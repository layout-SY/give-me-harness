"""사용자가 검토한 현재 상태의 SHA로 미확인 도구·실패 병합·검증된 close를 복구한다."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType

from .core import CENTRAL_ROOT, PolicyError, ProjectConfig, atomic_write
from .runtime import load_runtime


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)
    if result.returncode:
        raise PolicyError(result.stderr.strip() or "Git 상태를 조회하지 못했습니다.")
    return result.stdout.strip()


def common_directory(root: Path) -> Path:
    path = Path(git(root, "rev-parse", "--git-common-dir"))
    return (path if path.is_absolute() else root / path).resolve()


def repository_state(project: ProjectConfig, state_root: Path | None = None) -> Path:
    return (state_root or CENTRAL_ROOT / "state").resolve() / "repositories" / hashlib.sha256(str(common_directory(project.path)).encode()).hexdigest()


@contextmanager
def assignment_environment(environment: dict[str, str]):
    original = {key: os.environ.get(key) for key in environment}
    os.environ.update(environment)
    try:
        yield
    finally:
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def reviewed_plan(directory: Path, plan: dict, approved: str | None) -> tuple[Path, str]:
    payload = (json.dumps(plan, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
    digest = hashlib.sha256(payload).hexdigest()
    path = directory / f"{digest}.json"
    atomic_write(path, payload)
    if approved is not None and approved != digest:
        raise PolicyError("검토한 복구 계약과 현재 상태가 다릅니다. 새 diff·HEAD·SHA를 확인하세요.")
    return path, digest


def worktree_snapshot(root: Path) -> dict:
    changes = git(root, "status", "--porcelain=v1", "--untracked-files=all")
    # -z 출력을 별도로 해석하여 공백·한글 경로와 rename을 정확히 기록한다.
    raw = subprocess.run(["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
                         cwd=root, capture_output=True, check=True).stdout.decode().split("\0")
    files = {}
    index = 0
    while index < len(raw):
        entry = raw[index]
        index += 1
        if not entry:
            continue
        relative = entry[3:]
        if entry[:2].strip().startswith(("R", "C")):
            index += 1
        path = root / relative
        if path.is_symlink():
            value = "symlink:" + os.readlink(path)
        elif path.is_file():
            value = hashlib.sha256(path.read_bytes()).hexdigest()
        else:
            value = "missing"
        files[relative] = value
    return {"worktree": str(root), "head": git(root, "rev-parse", "HEAD"),
            "branch": git(root, "branch", "--show-current"), "status": changes, "files": files}


def recover_assignment(project: ProjectConfig, assignment: str, call_id: str, outcome: str,
                       approved_sha256: str | None = None, state_root: Path | None = None) -> tuple[Path, str]:
    if re.fullmatch(r"[a-f0-9]{32}", assignment) is None or outcome not in {"confirmed", "cancelled"}:
        raise PolicyError("유효한 assignment와 confirmed/cancelled 결과가 필요합니다.")
    state = load_runtime("runtime_state")
    repository = repository_state(project, state_root)
    with state.locked(repository / "events.lock"):
        directory = repository / "assignments" / assignment
        record = state.read(directory / "assignment.json")
        if (record.get("repository") != str(common_directory(project.path)) or record.get("project") != project.id
                or record.get("handed_off_to")):
            raise PolicyError("복구할 assignment의 저장소·프로젝트·소유권을 확인할 수 없습니다.")
        pending_path = directory / "pending-bindings" / f"{state.digest(call_id)}.json" if call_id else directory / "pending-binding.json"
        pending = state.read(pending_path)
        if not pending or pending.get("call", "") != call_id:
            raise PolicyError("해당 tool call의 미확인 예약이 없습니다.")
        binding = pending["binding"]
        worktree = Path(binding.get("worktree") or record["worktree"])
        if not worktree.exists():
            closed = state.read(common_directory(project.path) / "asan-agent-policy/closed" / f"{str(binding.get('branch', '')).removeprefix('task/')}.json")
            receipt = state.read(common_directory(project.path) / "asan-agent-policy/integrations" / f"{closed.get('finish_sha256', '')}.json")
            if outcome == "confirmed" and (closed.get("state") != "CLOSED" or receipt.get("state") != "closed"):
                raise PolicyError("존재하지 않는 worktree의 실행을 성공으로 확정할 수 없습니다.")
            worktree = project.path
        if common_directory(worktree) != common_directory(project.path):
            raise PolicyError("다른 저장소의 실행 결과를 복구할 수 없습니다.")
        if outcome == "confirmed" and binding.get("_action") == "create":
            if git(worktree, "branch", "--show-current") != binding.get("branch"):
                raise PolicyError("create 결과 branch가 예약과 다릅니다.")
        plan = {"version": 1, "kind": "assignment-recovery", "assignment": assignment, "call": call_id,
                "outcome": outcome, "pending": pending, "current": worktree_snapshot(worktree)}
        result = reviewed_plan(repository / "recoveries", plan, approved_sha256)
        if approved_sha256 is None:
            return result
        # 원래 bundle의 귀속 상태 전이만 재생한다. 탐색·구현 승인 근거는 만들지 않는다.
        from .injection import _bundle_is_valid
        if not _bundle_is_valid(Path(record["bundle_root"]), record["bundle_digest"]):
            raise PolicyError("원래 assignment bundle의 무결성 검사에 실패했습니다.")
        source = Path(record["bundle_root"]) / "policy/.agent-policy/runtime/artifact_policy.py"
        module = ModuleType("asan_recovery_artifact")
        module.__file__ = str(source)
        with assignment_environment(record["environment"]):
            exec(compile(source.read_bytes(), str(source), "exec"), module.__dict__)
            event = {"session_id": record.get("native_session", "recovery"), "tool_use_id": call_id,
                     "tool_response": {"success": outcome == "confirmed"}}
            module.complete_binding(event, project.path, record["host"])
        return result


def recover_integration(project: ProjectConfig, finish_file: Path, finish_sha256: str,
                        approved_sha256: str | None = None, state_root: Path | None = None) -> tuple[Path, str]:
    """실패한 병합을 승인 당시 target으로 merge --abort하고 source를 ACTIVE로 돌린다."""
    if re.fullmatch(r"[a-f0-9]{64}", finish_sha256) is None:
        raise PolicyError("finish 계약의 전체 SHA-256이 필요합니다.")
    state = load_runtime("runtime_state")
    common = common_directory(project.path)
    expected = common / "asan-agent-policy/finish-proposals" / f"{finish_sha256}.json"
    if finish_file.is_symlink() or finish_file.resolve() != expected.resolve():
        raise PolicyError("Git 공통 상태의 원본 finish proposal 경로가 필요합니다.")
    contract = state.read(expected)
    payload = (json.dumps(contract, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
    # workflow contract_bytes는 개행을 포함하지 않는다.
    if hashlib.sha256(payload.rstrip(b"\n")).hexdigest() != finish_sha256:
        raise PolicyError("finish proposal SHA가 올바르지 않습니다.")
    root = Path(str(contract.get("integration_worktree") or project.path)).resolve()
    if common_directory(root) != common:
        raise PolicyError("통합 worktree가 다른 저장소입니다.")
    repository = repository_state(project, state_root)
    lock = common / "asan-agent-policy/locks" / f"{state.digest(str(root))}.lock"
    # workflow와 동일한 lock 순서: 실행 worktree → 이벤트 상태.
    with state.locked(lock), state.locked(repository / "events.lock"):
        reservation_paths = list((common / "asan-agent-policy/integration-targets").glob("*.json"))
        selected = [(path, state.read(path)) for path in reservation_paths if state.read(path).get("finish_sha256") == finish_sha256]
        if len(selected) != 1:
            raise PolicyError("복구할 통합 예약을 하나로 확인할 수 없습니다.")
        reservation_path, reservation = selected[0]
        snapshot = worktree_snapshot(root)
        if snapshot["branch"] != contract["target"] or snapshot["head"] != contract["target_head"]:
            raise PolicyError("target HEAD가 승인 당시와 다릅니다. 기존 finish 재실행으로 결과 기록을 먼저 복구하세요.")
        if git(root, "rev-parse", contract["source"]) != contract["source_head"]:
            raise PolicyError("source HEAD가 변경되어 이 복구 계약을 사용할 수 없습니다.")
        merge_path = Path(git(root, "rev-parse", "--git-path", "MERGE_HEAD"))
        merge_path = merge_path if merge_path.is_absolute() else root / merge_path
        merge_head = merge_path.read_text().strip() if merge_path.is_file() else ""
        if merge_head and merge_head != contract["source_head"]:
            raise PolicyError("다른 source의 병합이 진행 중입니다.")
        if not merge_head and snapshot["status"]:
            raise PolicyError("실행 중인 병합 없이 dirty 변경이 있어 복구할 수 없습니다.")
        plan = {"version": 1, "kind": "integration-abort", "finish_sha256": finish_sha256,
                "reservation": reservation, "current": snapshot, "merge_head": merge_head,
                "effect": "merge --abort; source ACTIVE; integration reservation released"}
        result = reviewed_plan(repository / "recoveries", plan, approved_sha256)
        if approved_sha256 is None:
            return result
        if merge_head:
            git(root, "merge", "--abort")
        if git(root, "rev-parse", "HEAD") != contract["target_head"] or git(root, "status", "--porcelain"):
            raise PolicyError("복구 후 target이 clean한 승인 HEAD와 다릅니다. 예약을 보존합니다.")
        git(root, "config", f"branch.{contract['source']}.asan-state", "ACTIVE")
        receipt_path = common / "asan-agent-policy/integrations" / f"{finish_sha256}.json"
        receipt = state.read(receipt_path)
        receipt.update({"state": "aborted", "recovery_sha256": result[1]})
        state.write(receipt_path, receipt)
        reservation_path.unlink()
        return result


def recover_close(project: ProjectConfig, finish_file: Path, finish_sha256: str,
                  approved_sha256: str | None = None, state_root: Path | None = None) -> tuple[Path, str]:
    """동일 통합/정리 worktree의 검증된 구형 계약만 삭제를 보류하여 종료한다.

    병합 계약과 검증 receipt는 유지한다. Git 변경은 source의 CLOSED metadata뿐이며,
    durable journal로 부분 기록 후에도 동일 승인 SHA를 재사용한다.
    """
    for digest in (finish_sha256, approved_sha256):
        if digest is not None and re.fullmatch(r"[a-f0-9]{64}", digest) is None:
            raise PolicyError("계약의 전체 SHA-256이 필요합니다.")
    state = load_runtime("runtime_state")
    common = common_directory(project.path)
    workflow = common / "asan-agent-policy"
    expected = workflow / "finish-proposals" / f"{finish_sha256}.json"
    if finish_file.is_symlink() or finish_file.resolve() != expected.resolve():
        raise PolicyError("Git 공통 상태의 원본 finish proposal 경로가 필요합니다.")
    contract = state.read(expected)
    canonical = json.dumps(contract, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if hashlib.sha256(canonical.encode()).hexdigest() != finish_sha256:
        raise PolicyError("finish proposal SHA가 올바르지 않습니다.")
    source, target = contract.get("source", ""), contract.get("target", "")
    if (contract.get("version") != 3 or contract.get("finish_schema") != 1 or contract.get("kind") != "finish"
            or contract.get("cleanup") is not True or not isinstance(source, str)
            or re.fullmatch(r"task/[a-z0-9]+(?:-[a-z0-9]+)*", source) is None
            or not isinstance(target, str) or not target or source == target):
        raise PolicyError("close 복구는 V3 동일 worktree cleanup 계약에서만 지원합니다.")
    git(project.path, "check-ref-format", "--branch", target)
    roots = [contract.get(key) for key in ("integration_worktree", "source_worktree", "worktree")]
    if not all(isinstance(value, str) and Path(value).is_absolute() for value in roots):
        raise PolicyError("통합·source·정리 worktree의 절대 경로가 필요합니다.")
    root = Path(roots[0]).resolve()
    if (any(Path(value).resolve() != root for value in roots) or common_directory(root) != common
            or Path(git(root, "rev-parse", "--show-toplevel")).resolve() != root):
        raise PolicyError("통합·source·정리 worktree가 같은 저장소의 동일 root여야 합니다.")
    repository = repository_state(project, state_root)
    recoveries = repository / "recoveries"
    receipt_path = workflow / "integrations" / f"{finish_sha256}.json"
    target_hash = hashlib.sha256(json.dumps({"target": target}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    reservation_path = workflow / "integration-targets" / f"{target_hash}.json"
    closed_path = workflow / "closed" / f"{source.removeprefix('task/')}.json"
    claim_path = repository / "claims" / f"{state.digest('git:' + str(root))}.json"
    with state.locked(workflow / "locks" / f"{state.digest(str(root))}.lock"), state.locked(repository / "events.lock"):
        destination = recoveries / f"{approved_sha256}.json" if approved_sha256 else None
        journal_path = destination.with_suffix(".transaction.json") if destination else None
        journal = state.read(journal_path)
        receipt, reservation = state.read(receipt_path), state.read(reservation_path)
        closed, claim = state.read(closed_path), state.read(claim_path)
        if journal:
            plan = state.read(destination)
            payload = (json.dumps(plan, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
            if (hashlib.sha256(payload).hexdigest() != approved_sha256 or plan.get("kind") != "close-recovery"
                    or plan.get("finish_sha256") != finish_sha256 or plan.get("project") != project.id
                    or plan.get("repository") != str(common) or journal.get("finish_sha256") != finish_sha256
                    or journal.get("state") not in {"applying", "complete"}):
                raise PolicyError("close 복구 journal과 승인 계약이 일치하지 않습니다.")
            final_receipt = {**plan["receipt"], "state": "closed", "cleanup_deferred": True,
                             "close_recovery_sha256": approved_sha256}
            final_closed = {"version": 3, "source": source, "source_head": contract["source_head"], "target": target,
                            "state": "CLOSED", "finish_sha256": finish_sha256, "cleanup_deferred": True,
                            "close_recovery_sha256": approved_sha256}
            finalized = receipt == final_receipt and closed == final_closed
            # 정리 예약 해제 직후 중단되었거나 완료된 재호출은 이후 작업의 소유권을 건드리지 않는다.
            if finalized and (journal["state"] == "complete" or
                              (reservation != plan["reservation"] and (not claim or claim != plan["claim"]))):
                state.write(journal_path, {"state": "complete", "finish_sha256": finish_sha256})
                return destination, approved_sha256
            if journal["state"] == "complete":
                raise PolicyError("완료한 close 복구 기록이 변경되었습니다.")
        else:
            plan = None

        snapshot = worktree_snapshot(root)
        for operation in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply"):
            operation_path = Path(git(root, "rev-parse", "--git-path", operation))
            if (operation_path if operation_path.is_absolute() else root / operation_path).exists():
                raise PolicyError("진행 중인 Git 작업이 있어 close를 복구할 수 없습니다.")
        if f"branch refs/heads/{source}" in git(root, "worktree", "list", "--porcelain").splitlines():
            raise PolicyError("source branch를 사용하는 worktree가 있어 close를 복구할 수 없습니다.")
        source_head = git(root, "rev-parse", f"refs/heads/{source}")
        metadata = {key: git(root, "config", "--get", f"branch.{source}.asan-{key}")
                    for key in ("state", "contract-version", "contract-sha256", "merge-target", "worktree")}
        owner = receipt.get("owner", "")
        if not isinstance(owner, str) or re.fullmatch(r"[a-f0-9]{32}", owner) is None:
            raise PolicyError("검증 기록의 assignment 소유자를 확인할 수 없습니다.")
        assignment = state.read(repository / "assignments" / owner / "assignment.json")
        identity = {key: assignment.get(key) for key in ("project", "repository", "host", "role", "task", "native_session", "handed_off_to")}
        if (identity["project"] != project.id or identity["repository"] != str(common) or identity["handed_off_to"]):
            raise PolicyError("검증한 assignment의 저장소·프로젝트·소유권이 변경되었습니다.")
        if (snapshot["branch"] != target or snapshot["status"] or snapshot["head"] != receipt.get("integration_head")
                or source_head != contract.get("source_head") or metadata["contract-version"] != "3"
                or metadata["contract-sha256"] != contract.get("branch_contract_sha256")
                or metadata["merge-target"] != target or Path(metadata["worktree"]).resolve() != root):
            raise PolicyError("검증 뒤 worktree·HEAD·branch 계약이 변경되어 close를 복구할 수 없습니다.")
        git(root, "merge-base", "--is-ancestor", source_head, snapshot["head"])
        strategy = contract.get("merge_strategy")
        if strategy == "ff-only":
            valid_result = snapshot["head"] == source_head
        else:
            valid_result = strategy == "merge-commit" and git(root, "rev-list", "--parents", "-n", "1", snapshot["head"]).split()[1:] == [contract["target_head"], source_head]
        if (not valid_result or receipt.get("finish_sha256") != finish_sha256
                or receipt.get("source_head") != source_head or receipt.get("target_head") != contract.get("target_head")
                or receipt.get("strategy") != strategy or receipt.get("worktree") != str(root)
                or not contract.get("validation_commands") or receipt.get("validation_commands") != contract["validation_commands"]):
            raise PolicyError("원래 완료 계약의 병합·사후 검증 근거가 일치하지 않습니다.")
        current = {"version": 1, "kind": "close-recovery", "project": project.id, "repository": str(common),
                   "finish_sha256": finish_sha256, "current": snapshot, "source_head": source_head,
                   "metadata": metadata, "assignment": identity, "receipt": receipt,
                   "reservation": reservation, "claim": claim,
                   "effect": {"state": "CLOSED", "cleanup": "deferred", "preserve": [source, str(root)],
                              "release": ["integration reservation", "owned Git worktree claim"]}}
        if plan is None:
            if (receipt.get("state") != "verified" or metadata["state"] != "MERGED_VERIFIED" or closed
                    or reservation != {"finish_sha256": finish_sha256, "owner": owner, "source": source, "target": target, "worktree": str(root)}
                    or (claim and claim != {"owner": owner, "resource": "git:" + str(root)})):
                raise PolicyError("MERGED_VERIFIED 기록과 동일 소유자의 통합 예약·Git 소유권이 필요합니다.")
            destination, digest = reviewed_plan(recoveries, current, approved_sha256)
            if approved_sha256 is None:
                return destination, digest
            plan = current
            journal_path = destination.with_suffix(".transaction.json")
            final_receipt = {**receipt, "state": "closed", "cleanup_deferred": True, "close_recovery_sha256": digest}
            final_closed = {"version": 3, "source": source, "source_head": source_head, "target": target,
                            "state": "CLOSED", "finish_sha256": finish_sha256, "cleanup_deferred": True,
                            "close_recovery_sha256": digest}
        else:
            # 승인 이후 자신의 부분 기록만 허용한다. HEAD·검증·소유권 변경은 재승인 대상이다.
            original_metadata = {**metadata, "state": plan["metadata"]["state"]}
            normalized = {**current, "metadata": original_metadata, "receipt": plan["receipt"],
                          "reservation": plan["reservation"], "claim": plan["claim"]}
            if (normalized != plan or metadata["state"] not in {"MERGED_VERIFIED", "CLOSED"}
                    or receipt not in (plan["receipt"], final_receipt) or closed not in ({}, final_closed)
                    or reservation != plan["reservation"] or claim not in (plan["claim"], {})
                    or (claim != plan["claim"] and not finalized)):
                raise PolicyError("중단된 close 복구 이후 상태가 바뀌었습니다. 예약을 보존합니다.")
        state.write(journal_path, {"state": "applying", "finish_sha256": finish_sha256})
        git(root, "config", f"branch.{source}.asan-state", "CLOSED")
        state.write(closed_path, final_closed)
        state.write(receipt_path, final_receipt)
        claim_path.unlink(missing_ok=True)
        reservation_path.unlink()
        state.write(journal_path, {"state": "complete", "finish_sha256": finish_sha256})
        return destination, approved_sha256
