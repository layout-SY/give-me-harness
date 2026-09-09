"""부모 owner가 직접 자식의 확정된 변경을 받아들이는 완료 권한 계약."""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from types import ModuleType

_loader_path = Path(__file__).resolve().with_name("runtime_loader.py")
_loader = ModuleType("asan_runtime_loader")
_loader.__file__ = str(_loader_path)
exec(compile(_loader_path.read_bytes(), str(_loader_path), "exec"), _loader.__dict__)
guard = _loader.load("branch_guard")
state = _loader.load("runtime_state")
artifacts = _loader.load("artifact_policy")


def checked(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def claim_path(common: Path, root: Path) -> Path:
    return state.repository_state(common) / "claims" / f"{state.digest('git:' + str(root.resolve()))}.json"


def assignment(common: Path, owner: str, root: Path, branch: str) -> tuple[dict, dict]:
    checked(re.fullmatch(r"[a-f0-9]{32}", owner) is not None, "자식 완료에는 launcher assignment가 필요합니다.")
    directory = state.repository_state(common) / "assignments" / owner
    record = state.read(directory / "assignment.json")
    binding = state.read(directory / "session-binding.json")
    checked(record.get("id") == owner and record.get("repository") == str(common)
            and record.get("responsibility") == "owner" and not record.get("handed_off_to"),
            "자식 완료의 assignment 저장소·owner 책임·인계 상태가 올바르지 않습니다.")
    checked(binding.get("branch") == branch and binding.get("worktree") == str(root.resolve())
            and binding.get("responsibility") == "owner"
            and guard.assignment_allows_branch_mutation(root, str(binding.get("task") or record.get("task") or ""), branch),
            "자식 완료의 assignment가 승인 branch·worktree에 귀속되지 않습니다.")
    for path in (state.repository_state(common) / "handoffs").glob("*.transaction.json"):
        transaction = state.read(path)
        checked(not (transaction.get("state") == "applying" and owner in {transaction.get("source"), transaction.get("target")}),
                "진행 중인 assignment 인계를 먼저 완료해야 합니다.")
    return record, binding


def source_worktree(root: Path, source: str) -> Path:
    result = subprocess.run(["git", "worktree", "list", "--porcelain"], cwd=root,
                            capture_output=True, text=True, check=False, timeout=10)
    checked(result.returncode == 0, "자식 worktree 목록을 확인할 수 없습니다.")
    paths = []
    for block in result.stdout.split("\n\n"):
        lines = block.splitlines()
        if f"branch refs/heads/{source}" in lines:
            paths.extend(Path(line.removeprefix("worktree ")).resolve() for line in lines if line.startswith("worktree "))
    checked(len(paths) == 1, "자식 source가 checkout된 단일 worktree가 필요합니다.")
    return paths[0]


def proposal(root: Path, source: str, *, cleanup: bool = False, host: str = "") -> dict:
    """부모 cwd에서 제안할 계약의 귀속을 읽는다. claim이나 branch 상태는 바꾸지 않는다."""
    with guard.git_snapshot():
        return _proposal(root, source, cleanup=cleanup, host=host)


def _proposal(root: Path, source: str, *, cleanup: bool, host: str) -> dict:
    target = guard.current_branch(root)
    values = guard.metadata(root, source)
    checked(source != target and values.get("parent") == target and values.get("merge-target") == target,
            "부모 worktree에서는 직접 자식 branch의 완료 계약만 제안할 수 있습니다.")
    common = guard.git_common_directory(root)
    checked(common is not None, "Git 공용 상태를 확인할 수 없습니다.")
    source_root = source_worktree(root, source)
    target_owner = os.environ.get("ASAN_AGENT_POLICY_ASSIGNMENT", "")
    source_owner = str(state.read(claim_path(common, source_root)).get("owner") or "")
    target_record, _ = assignment(common, target_owner, root, target)
    source_record, source_binding = assignment(common, source_owner, source_root, source)
    authority = {"mode": "parent", "target_assignment": target_owner, "target_host": target_record.get("host"),
                 "target_contract_sha256": guard.metadata(root, target).get("contract-sha256"),
                 "source_assignment": source_owner, "source_host": source_record.get("host"),
                 "source_session_directory": source_binding.get("directory")}
    contract = {"kind": "finish", "version": int(guard.CONTRACT_VERSION), "finish_schema": 1,
                "source": source, "source_head": guard.head(root, source), "target": target,
                "target_head": guard.head(root, target), "source_worktree": str(source_root),
                "integration_worktree": str(root.resolve()), "branch_contract_sha256": values.get("contract-sha256"),
                "cleanup": cleanup, "completion_authority": authority}
    _validate(root, contract, action="finish-proposal", host=host)
    return contract


def validate(root: Path, contract: dict, *, action: str, host: str = "") -> None:
    """hook과 workflow 본문이 동일한 부모 실행 권한·자식 근거를 재검사한다."""
    with guard.git_snapshot():
        _validate(root, contract, action=action, host=host)


def _validate(root: Path, contract: dict, *, action: str, host: str) -> None:
    authority = contract.get("completion_authority")
    checked(isinstance(authority, dict) and set(authority) == {
        "mode", "target_assignment", "target_host", "target_contract_sha256",
        "source_assignment", "source_host", "source_session_directory",
    } and authority.get("mode") == "parent", "부모 완료 권한 계약이 올바르지 않습니다.")
    checked(all(isinstance(value, str) and value for value in authority.values())
            and authority["target_host"] in guard.KNOWN_HOSTS and authority["source_host"] in guard.KNOWN_HOSTS,
            "부모 완료 권한의 host·assignment·산출물 필드가 올바르지 않습니다.")
    checked(contract.get("kind") == "finish" and contract.get("version") == int(guard.CONTRACT_VERSION)
            and contract.get("finish_schema") == 1, "지원하지 않는 부모 완료 계약입니다.")
    checked(contract.get("cleanup") is False, "부모가 받는 자식 완료는 --cleanup 없이 branch·worktree를 보존해야 합니다.")
    checked(os.environ.get("ASAN_AGENT_POLICY_ASSIGNMENT") == authority["target_assignment"],
            "승인된 부모 assignment만 자식 완료 계약을 실행할 수 있습니다.")
    checked(not host or host == authority["target_host"], "승인된 부모 host와 실행 host가 다릅니다.")
    checked(str(root.resolve()) == contract.get("integration_worktree"), "부모 완료 계약은 승인된 부모 worktree에서 실행해야 합니다.")
    common = guard.git_common_directory(root)
    checked(common is not None, "Git 공용 상태를 확인할 수 없습니다.")
    source, target = str(contract.get("source") or ""), str(contract.get("target") or "")
    checked(guard.current_branch(root) == target, "부모 worktree의 checkout branch가 승인 target과 다릅니다.")
    checked(state.read(claim_path(common, root)).get("owner") == authority["target_assignment"],
            "부모 Git 소유권이 승인된 assignment와 다릅니다.")
    target_record, _ = assignment(common, authority["target_assignment"], root, target)
    checked(target_record.get("host") == authority["target_host"], "부모 assignment의 host가 변경되었습니다.")
    denial = guard.active_branch_denial(root) or guard.git_integrator_denial(root, target, authority["target_host"])
    checked(denial is None, denial or "")
    checked(guard.metadata(root, target).get("contract-sha256") == authority["target_contract_sha256"],
            "부모 branch 계약이 변경되었습니다. 새 완료 계약이 필요합니다.")
    digest = guard.contract_sha256(contract)
    receipt = state.read(common / "asan-agent-policy/integrations" / f"{digest}.json")
    # CLOSED 재시도에는 이미 해제한 자식 claim을 다시 요구하거나 만들지 않는다.
    if action == "close" and receipt.get("state") == "closed" and receipt.get("owner") == authority["target_assignment"]:
        return
    source_root = Path(str(contract.get("source_worktree") or "")).resolve()
    checked(source_root != root.resolve() and source_root.is_dir() and guard.same_git_repository(root, source_root)
            and guard.current_branch(source_root) == source, "승인된 자식 worktree의 저장소·branch가 다릅니다.")
    checked(state.read(claim_path(common, source_root)).get("owner") == authority["source_assignment"],
            "자식 Git 소유권이 변경되었습니다. 새 완료 계약이 필요합니다.")
    source_record, binding = assignment(common, authority["source_assignment"], source_root, source)
    checked(source_record.get("host") == authority["source_host"] and binding.get("directory") == authority["source_session_directory"],
            "자식 assignment의 host 또는 산출물 귀속이 변경되었습니다.")
    values = guard.metadata(root, source)
    checked(values.get("parent") == target and values.get("merge-target") == target
            and values.get("contract-sha256") == contract.get("branch_contract_sha256"),
            "승인된 직접 자식 branch 계약과 다릅니다.")
    states = ("ACTIVE",) if action == "finish-proposal" else ("ACTIVE", "READY_TO_MERGE", "MERGED_VERIFIED")
    if action == "close" and receipt.get("state") == "closing" and receipt.get("owner") == authority["target_assignment"]:
        states += ("CLOSED",)
    denial = (guard.active_branch_denial(source_root, allowed_states=states)
              or guard.git_integrator_denial(source_root, source, authority["source_host"]))
    checked(denial is None, denial or "")
    checked(guard.head(root, source) == contract.get("source_head"), "승인 후 자식 HEAD가 변경되었습니다. 새 완료 계약이 필요합니다.")
    checked(not guard.unmerged_children(root, source), "자식의 미병합 하위 branch를 먼저 완료해야 합니다.")
    checked(guard.changed_paths(source_root) == (), "dirty 자식 worktree는 완료할 수 없습니다.")
    for label, owner in (("부모", authority["target_assignment"]), ("자식", authority["source_assignment"])):
        pending = state.repository_state(common) / "assignments" / owner
        checked(not state.read(pending / "pending-binding.json") and not any((pending / "pending-bindings").glob("*.json")),
                f"{label} assignment에 결과 미확인 도구 예약이 있습니다. 먼저 결과를 확인하세요.")
    directory = artifacts.artifact_session_directory(source_root, str(binding.get("directory") or "") + "/handoff.md", authority["source_host"])
    checked(directory is not None, "자식 assignment의 산출물 디렉터리가 올바르지 않습니다.")
    issues = artifacts.artifact_issues(directory)
    checked(not issues, "자식 owner의 필수 산출물을 확인하세요: " + "; ".join(issues))


def release_source_claim(root: Path, contract: dict) -> None:
    """승인된 자식이 CLOSED가 된 뒤 해당 자식 claim만 해제한다."""
    authority = contract["completion_authority"]
    source_root = Path(contract["source_worktree"]).resolve()
    common = guard.git_common_directory(root)
    with state.locked(state.repository_state(common) / "events.lock"):
        path = claim_path(common, source_root)
        claim = state.read(path)
        if (guard.task_state(root, contract["source"]) == "CLOSED"
                and guard.current_branch(source_root) == contract["source"]
                and guard.head(root, contract["source"]) == contract["source_head"]
                and claim.get("owner") == authority["source_assignment"]):
            path.unlink()
