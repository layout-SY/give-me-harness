"""사용자가 검토한 현재 상태의 SHA로만 미확인 도구·실패 병합을 복구한다."""

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
