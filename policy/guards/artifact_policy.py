"""산출물·assignment 귀속, 문서 gate와 실행 예약."""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from types import ModuleType
from typing import Any


_loader_path = Path(__file__).resolve().with_name("runtime_loader.py")
_loader = ModuleType("asan_runtime_loader")
_loader.__file__ = str(_loader_path)
exec(compile(_loader_path.read_bytes(), str(_loader_path), "exec"), _loader.__dict__)
load_runtime_module = _loader.load

_runtime_config = load_runtime_module("runtime_config")
ARTIFACT_RESPONSIBILITY_ENV = _runtime_config.ARTIFACT_RESPONSIBILITY_ENV
ARTIFACT_SESSIONS_PREFIXES = _runtime_config.ARTIFACT_SESSIONS_PREFIXES
HANDOFF_ARTIFACT = _runtime_config.HANDOFF_ARTIFACT
HOST_ARTIFACT_SESSIONS_PREFIXES = _runtime_config.HOST_ARTIFACT_SESSIONS_PREFIXES
PORTFOLIO_CASE = _runtime_config.PORTFOLIO_CASE
PORTFOLIO_FIELDS = _runtime_config.PORTFOLIO_FIELDS
PORTFOLIO_HEADINGS = _runtime_config.PORTFOLIO_HEADINGS
REQUIRED_ARTIFACTS = _runtime_config.REQUIRED_ARTIFACTS
SESSION_DIR_ENV = _runtime_config.SESSION_DIR_ENV
valid_session_name = load_runtime_module("artifact_names").valid_session_name
SHELL_TOOLS = _runtime_config.SHELL_TOOLS
STRUCTURED_MUTATION_TOOLS = _runtime_config.STRUCTURED_MUTATION_TOOLS
TABLE_SEPARATOR = _runtime_config.TABLE_SEPARATOR
TASK_ENV = _runtime_config.TASK_ENV
UNKNOWN_ARTIFACT_DIRECTORY = _runtime_config.UNKNOWN_ARTIFACT_DIRECTORY
branch_guard = _runtime_config.branch_guard
event_protocol = _runtime_config.event_protocol
load_json_state = _runtime_config.load_json_state
runtime_state = _runtime_config.runtime_state
write_json_state = _runtime_config.write_json_state

_tool_paths = load_runtime_module("tool_paths")
branch_workflow_contract = _tool_paths.branch_workflow_contract
event_session_id = _tool_paths.event_session_id
git_command_mutates = _tool_paths.git_command_mutates
has_non_redirect_shell_mutation = _tool_paths.has_non_redirect_shell_mutation
normalized_tool_name = _tool_paths.normalized_tool_name
patch_targets = _tool_paths.patch_targets
repository_relative = _tool_paths.repository_relative
repository_target = _tool_paths.repository_target
resolved_shell_target = _tool_paths.resolved_shell_target
shell_redirect_targets = _tool_paths.shell_redirect_targets
shell_working_directory = _tool_paths.shell_working_directory
structured_targets = _tool_paths.structured_targets
trusted_branch_workflow_action = _tool_paths.trusted_branch_workflow_action
trusted_branch_workflow_arguments = _tool_paths.trusted_branch_workflow_arguments
trusted_branch_workflow_invocation = _tool_paths.trusted_branch_workflow_invocation

_event_protocol = load_runtime_module("event_protocol")
emit_denial = _event_protocol.emit_denial

_BINDING_DRAFT: dict[Path, dict[str, str]] = {}

def session_binding_path(event: dict[str, Any], root: Path, host: str) -> Path | None:
    return transient_state_path(event, root, host, "session-binding")


def artifact_sessions_prefix(host: str) -> str:
    return HOST_ARTIFACT_SESSIONS_PREFIXES.get(
        host,
        HOST_ARTIFACT_SESSIONS_PREFIXES["unknown"],
    )


def artifact_session_directory(root: Path, raw_path: str, host: str) -> Path | None:
    prefix = artifact_sessions_prefix(host)
    relative = repository_relative(root, raw_path)
    if relative is None or not relative.startswith(prefix):
        return None
    remainder = relative.removeprefix(prefix)
    parts = Path(remainder).parts
    if len(parts) < 2 or not valid_session_name(parts[0]):
        return None
    candidate = root / prefix / parts[0]
    try:
        candidate.resolve().relative_to((root / prefix).resolve())
    except (OSError, ValueError):
        return None
    return candidate


def artifact_layout_denial(root: Path, raw_path: str, host: str) -> str | None:
    """알려진 문서는 session root, 그 외 문서는 unknown/ 아래에만 둔다."""

    prefix = artifact_sessions_prefix(host)
    relative = repository_relative(root, raw_path)
    if relative is None or not relative.startswith(prefix):
        return None
    parts = Path(relative.removeprefix(prefix)).parts
    if len(parts) < 2 or not valid_session_name(parts[0]):
        return f"세션 산출물 경로가 올바르지 않습니다: {relative}"
    artifact_parts = parts[1:]
    known = {*REQUIRED_ARTIFACTS, HANDOFF_ARTIFACT, *branch_guard.RUNTIME_CONTRACT["artifacts"].get("optional", [])}
    if len(artifact_parts) == 1 and artifact_parts[0] in known:
        return None
    if len(artifact_parts) >= 2 and artifact_parts[0] == UNKNOWN_ARTIFACT_DIRECTORY:
        return None
    return (
        f"정의되지 않은 산출물은 현재 세션의 {UNKNOWN_ARTIFACT_DIRECTORY}/ 아래에 작성해야 합니다: "
        f"{relative}"
    )


def declared_session_directory(root: Path, host: str) -> Path | None:
    prefix = artifact_sessions_prefix(host)
    value = os.environ.get(SESSION_DIR_ENV, "").strip()
    if not value:
        return None
    candidate = Path(value)
    target = candidate if candidate.is_absolute() else root / candidate
    try:
        relative = target.resolve().relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        return None
    if not relative.startswith(prefix):
        return None
    remainder = relative.removeprefix(prefix)
    parts = Path(remainder).parts
    if len(parts) != 1 or not valid_session_name(parts[0]):
        return None
    return target


def session_binding_record(event: dict[str, Any], root: Path, host: str) -> dict[str, str]:
    path = session_binding_path(event, root, host)
    if path is None:
        return {}
    if path in _BINDING_DRAFT:
        return dict(_BINDING_DRAFT[path])
    # 예약도 같은 세션의 다음 쓰기에 소유권 경계로 적용한다. 실패 post는 해제한다.
    pending_records = pending_bindings(path)
    for _, pending in pending_records:
        if isinstance(pending.get("binding"), dict) and pending["binding"].get("_action") != "create":
            return dict(pending["binding"])
    try:
        value = path.read_text(encoding="utf-8").strip()
    except (FileNotFoundError, OSError):
        return {}
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        parsed = None
    if isinstance(parsed, dict) and isinstance(parsed.get("directory"), str):
        return {
            key: str(parsed.get(key, ""))
            for key in (
                "directory",
                "branch",
                "merge_target",
                "task",
                "responsibility",
                "contract_version",
                "worktree",
            )
        }
    return {
        "directory": value,
        "branch": "",
        "merge_target": "",
        "task": "",
        "responsibility": "",
        "contract_version": "",
        "worktree": "",
    }


def binding_worktree(root: Path, record: dict[str, str]) -> Path:
    raw = record.get("worktree", "")
    if not raw:
        return root.resolve()
    try:
        candidate = Path(raw).resolve()
    except (OSError, RuntimeError):
        return root.resolve()
    if branch_guard.same_git_repository(root, candidate):
        return candidate
    return root.resolve()


def active_assignment_branch(event: dict[str, Any], root: Path, host: str) -> str:
    """CLOSED 전까지 같은 세션이 소유하는 assignment 권한 root를 반환한다."""

    if branch_guard.SHARED_GIT_ACCESS:
        return ""
    record = session_binding_record(event, root, host)
    declared = os.environ.get(TASK_ENV, "").strip()
    recorded = record.get("task", "")
    if declared and recorded and declared != recorded and branch_guard.task_state(root, declared) != "CLOSED":
        raise RuntimeError(f"assignment 권한 root({recorded})와 실행 인자의 task({declared})가 다릅니다.")
    branch = (
        record.get("task", "")
        or os.environ.get(TASK_ENV, "").strip()
        or record.get("branch", "")
    )
    if not branch:
        return ""
    lookup_root = binding_worktree(root, record)
    if branch_guard.task_state(lookup_root, branch) == "CLOSED":
        return ""
    return branch


def bound_session_directory(event: dict[str, Any], root: Path, host: str) -> Path | None:
    record = session_binding_record(event, root, host)
    value = record.get("directory", "")
    if value:
        record_root = binding_worktree(root, record)
        candidate = artifact_session_directory(
            record_root,
            f"{value}/{HANDOFF_ARTIFACT}",
            host,
        )
        if candidate is not None:
            return candidate
    return declared_session_directory(root, host)


def session_directory_context(event: dict[str, Any], root: Path, host: str) -> str:
    record = session_binding_record(event, root, host)
    if record.get("directory"):
        return (f"세션 산출물 경로: {record['directory']}\n"
                f"마지막 기록 위치: {binding_worktree(root, record)}\n"
                "재개·압축·worktree 이동 후에도 이 폴더 이름을 유지하세요.")
    declared = os.environ.get(SESSION_DIR_ENV, "")
    if os.environ.get(_runtime_config.SESSION_DIR_MODE_ENV) == "suggested":
        return (f"세션 산출물 이름은 아직 선택하지 않았습니다. 산출물을 작성할 때 {artifact_sessions_prefix(host)} 아래에 "
                "작업을 설명하는 새 폴더 이름을 선택할 수 있습니다. "
                f"자동 추천 경로: {declared}. 날짜·일련번호는 필수가 아닙니다.")
    return f"지정된 세션 산출물 경로: {declared}" if declared else ""


def integrated_artifact_owner(event: dict[str, Any], root: Path, host: str, record: dict,
                              requested: Path, targets: list) -> bool:
    """target 전환 후에도 원래 source assignment의 자기 로그 귀속을 유지한다."""
    if not record.get("directory") or binding_worktree(root, record) != root.resolve():
        return False
    if requested.resolve() != (root / record["directory"]).resolve():
        return False
    if not targets or not all(target_root == root and (target_root / relative).resolve().is_relative_to(requested.resolve())
                              for target_root, relative in targets):
        return False
    common = branch_guard.git_common_directory(root)
    if common is None:
        return False
    owner = runtime_state.owner_id(host, event_session_id(event))
    for path in (common / "asan-agent-policy/integrations").glob("*.json"):
        receipt = runtime_state.read(path)
        digest = receipt.get("finish_sha256", "")
        if (re.fullmatch(r"[a-f0-9]{64}", str(digest)) is None or receipt.get("owner") != owner
                or receipt.get("state") not in {"merged", "verified", "closed", "preserved"}
                or receipt.get("worktree") != str(root.resolve())):
            continue
        contract = runtime_state.read(common / "asan-agent-policy/finish-proposals" / f"{digest}.json")
        if (path.stem == digest and branch_guard.contract_sha256(contract) == digest and contract.get("source") == record.get("branch")
                and contract.get("target") == branch_guard.current_branch(root)
                and contract.get("source_head") == receipt.get("source_head")
                and str(contract.get("integration_worktree") or root) == str(root.resolve())
                and branch_guard.is_ancestor(root, str(contract.get("source_head")), str(contract.get("target")))):
            return True
    return False


def bind_artifact_session(event: dict[str, Any], root: Path, host: str) -> str | None:
    raw_input = event.get("tool_input")
    tool_input = raw_input if isinstance(raw_input, dict) else {}
    tool_name = normalized_tool_name(event)
    if tool_name not in STRUCTURED_MUTATION_TOOLS | SHELL_TOOLS:
        return None
    raw_targets = structured_targets(tool_input)
    command_value = tool_input.get("command")
    command = command_value if isinstance(command_value, str) else ""
    if tool_name in {"apply_patch", "patch"}:
        raw_targets.extend(patch_targets(command))
    resolved_redirects = tuple(
        target
        for raw_target in shell_redirect_targets(command)
        if (target := resolved_shell_target(root, tool_input, raw_target)) is not None
    )
    target_contexts = tuple(
        context
        for raw_target in raw_targets
        if (context := repository_target(root, raw_target)) is not None
    )
    redirect_contexts = tuple(
        context
        for target in resolved_redirects
        if (context := repository_target(root, str(target))) is not None
    )
    artifact_contexts = tuple(
        (target_root, relative)
        for target_root, relative in (*target_contexts, *redirect_contexts)
        if relative.startswith(ARTIFACT_SESSIONS_PREFIXES)
    )
    artifact_relative_targets = tuple(
        dict.fromkeys(relative for _, relative in artifact_contexts)
    )
    cross_host_denial = branch_guard.artifact_write_denial(
        tuple(dict.fromkeys(artifact_relative_targets)),
        host,
    )
    if cross_host_denial is not None:
        return cross_host_denial
    for target_root, relative in artifact_contexts:
        layout_denial = artifact_layout_denial(target_root, relative, host)
        if layout_denial is not None:
            return layout_denial
    current_prefix = artifact_sessions_prefix(host)
    if has_non_redirect_shell_mutation(command):
        current_host = host if host in HOST_ARTIFACT_SESSIONS_PREFIXES else "unknown"
        for owner, prefix in HOST_ARTIFACT_SESSIONS_PREFIXES.items():
            if owner != current_host and prefix in command:
                return (
                    f"다른 host({owner}) 세션의 산출물은 읽기 전용입니다. "
                    f"현재 host({current_host})의 구조화된 쓰기 도구를 사용하세요."
                )
    redirect_writes_artifact = any(
        relative.startswith(ARTIFACT_SESSIONS_PREFIXES)
        for _, relative in redirect_contexts
    )
    command_writes_artifact = bool(
        has_non_redirect_shell_mutation(command)
        and current_prefix in command
    )
    if (
        tool_name in SHELL_TOOLS
        and command
        and (redirect_writes_artifact or command_writes_artifact)
        and not trusted_branch_workflow_invocation(command, root)
    ):
        return (
            "Bash heredoc·리다이렉션으로 만든 세션 산출물은 세션 귀속을 기록할 수 없습니다. "
            "현재 호스트의 구조화된 파일 쓰기 도구를 사용하세요."
        )
    candidates = tuple(
        (target_root, candidate)
        for target_root, relative in target_contexts
        if (candidate := artifact_session_directory(target_root, relative, host)) is not None
    )
    if not candidates:
        return None
    requested_root, requested = candidates[0]
    if any(candidate.resolve() != requested.resolve() for _, candidate in candidates[1:]):
        return "한 번의 작업에서 서로 다른 세션 산출물 디렉터리를 수정할 수 없습니다."
    path = session_binding_path(event, root, host)
    record = session_binding_record(event, root, host)
    relative = requested.resolve().relative_to(requested_root.resolve()).as_posix()
    branch = branch_guard.current_branch(requested_root)
    values = branch_guard.metadata(requested_root, branch) if branch else {}
    assignment_root = active_assignment_branch(event, root, host)
    in_assignment = bool(
        assignment_root
        and branch
        and branch_guard.assignment_includes_branch(
            requested_root,
            assignment_root,
            branch,
        )
    )
    existing = (
        bound_session_directory(event, root, host)
        if record
        else declared_session_directory(requested_root, host)
    )
    if path is not None and integrated_artifact_owner(event, requested_root, host, record, requested, target_contexts):
        _BINDING_DRAFT[path] = record
        return None
    if path is None and existing is None:
        return (
            "호스트 이벤트에 session id가 없으므로 산출물 소유권을 자동 귀속할 수 없습니다. "
            f"세션 시작 시 ASAN_SESSION_DIR={requested.resolve().relative_to(requested_root.resolve()).as_posix()}를 "
            "지정하세요."
        )
    can_rebind = False
    declared_session = os.environ.get(SESSION_DIR_ENV, "").strip().strip("/")
    logical_session = record.get("directory", "") or declared_session
    lineage_worktree_move = bool(in_assignment and logical_session == relative)
    if existing is not None and existing.resolve() != requested.resolve():
        if not lineage_worktree_move:
            can_rebind = session_rebind_allowed(requested_root, existing, record)
        if not can_rebind and not lineage_worktree_move:
            return (
                "현재 세션의 기존 작업이 CLOSED 상태가 아니므로 다른 산출물 디렉터리로 전환할 수 없습니다. "
                "기존 작업을 완료·merge·검증하거나 handoff 후 별도 worktree와 세션을 사용하세요."
            )
    if assignment_root and branch and not (in_assignment or can_rebind):
        return (
            "현재 세션의 assignment 권한 계보와 산출물 대상 branch가 다릅니다.\n"
            f"  권한 root: {assignment_root}\n"
            f"  산출물 대상: {branch} ({requested_root})"
        )
    if record.get("branch") and record["branch"] != branch and not (can_rebind or in_assignment):
        return (
            "현재 세션의 assignment 권한 계보 밖 branch에 같은 산출물 디렉터리를 사용할 수 없습니다. "
            "독립 task는 이전 task를 CLOSED로 만든 뒤 새 산출물 디렉터리에 바인딩하세요."
        )
    declared_task = os.environ.get(TASK_ENV, "").strip()
    declared_includes_branch = bool(
        declared_task
        and branch
        and branch_guard.assignment_includes_branch(
            requested_root,
            declared_task,
            branch,
        )
    )
    if declared_task and declared_task != branch and not (can_rebind or declared_includes_branch):
        return (
            f"session assignment 권한 계보와 현재 branch가 다릅니다: "
            f"root={declared_task}, branch={branch or 'detached HEAD'}"
        )
    task = (
        (branch or declared_task)
        if can_rebind
        else assignment_root or declared_task or branch
    )
    if task and branch_guard.TASK_BRANCH_PATTERN.fullmatch(task) is None:
        task = ""
    responsibility = (
        os.environ.get(ARTIFACT_RESPONSIBILITY_ENV, "").strip().casefold()
        or record.get("responsibility", "").casefold()
        or "owner"
    )
    if responsibility not in tuple(branch_guard.ARTIFACT_RESPONSIBILITIES):
        return f"지원하지 않는 산출물 책임입니다: {responsibility}"
    if path is None:
        return None
    binding = {
        "directory": relative,
        "branch": branch,
        "merge_target": str(values.get("merge-target") or ""),
        "task": task,
        "responsibility": responsibility,
        "contract_version": str(values.get("contract-version") or ""),
        "worktree": str(requested_root.resolve()),
    }
    _BINDING_DRAFT[path] = binding
    return None


def bind_task_assignment(event: dict[str, Any], root: Path, host: str) -> str | None:
    """source/Git mutation에서 권한 root를 보존하고 현재 branch 초점을 갱신한다."""

    path = session_binding_path(event, root, host)
    if path is None:
        return None
    raw_input = event.get("tool_input")
    tool_input = raw_input if isinstance(raw_input, dict) else {}
    tool_name = normalized_tool_name(event)
    command_value = tool_input.get("command")
    command = command_value if isinstance(command_value, str) else ""
    if trusted_branch_workflow_action(command, root) == "create":
        contract = branch_workflow_contract(event, root, trusted_branch_workflow_arguments(command, root))
        branch = str(contract.get("branch") or "")
        if not branch:
            return "create의 branch 계약을 확인할 수 없습니다."
        record = session_binding_record(event, root, host)
        _BINDING_DRAFT[path] = {"_action": "create", "directory": record.get("directory", "") or os.environ.get(SESSION_DIR_ENV, ""),
            "branch": branch, "task": active_assignment_branch(event, root, host) or branch,
            "worktree": str(contract.get("worktree") or root.resolve()),
            "merge_target": str(contract.get("merge_target") or contract.get("parent") or ""),
            "responsibility": os.environ.get(ARTIFACT_RESPONSIBILITY_ENV, "owner"), "contract_version": "3"}
        return None
    target_roots: list[Path] = []
    if tool_name in STRUCTURED_MUTATION_TOOLS:
        raw_targets = structured_targets(tool_input)
        if tool_name in {"apply_patch", "patch"}:
            raw_targets.extend(patch_targets(command))
        target_roots.extend(
            target_root
            for raw_target in raw_targets
            if (context := repository_target(root, raw_target)) is not None
            for target_root in (context[0],)
        )
    elif tool_name in SHELL_TOOLS and command and git_command_mutates(command):
        invocations = branch_guard.git_invocations(
            root,
            command,
            shell_working_directory(root, tool_input),
        )
        if invocations is not None:
            target_roots.extend(invocation.root for invocation in invocations)
    unique_roots = tuple(dict.fromkeys(target.resolve() for target in target_roots))
    roots_by_branch: dict[str, Path] = {}
    for target_root in unique_roots:
        target_branch = branch_guard.current_branch(target_root)
        if target_branch and target_branch != str(branch_guard.BASE_BRANCH):
            roots_by_branch.setdefault(target_branch, target_root)
    branches = tuple(roots_by_branch)
    if not branches:
        return None
    if len(branches) != 1:
        return "한 번의 mutation을 서로 다른 task branch에 귀속할 수 없습니다. 명령을 분리하세요."
    branch = branches[0]
    target_root = roots_by_branch[branch]
    record = session_binding_record(event, root, host)
    previous = record.get("branch", "")
    assignment_root = active_assignment_branch(event, root, host)
    in_assignment = bool(
        assignment_root
        and branch_guard.assignment_allows_branch_mutation(
            target_root,
            assignment_root,
            branch,
        )
    )
    if previous and previous != branch and not in_assignment:
        if branch_guard.task_state(binding_worktree(root, record), previous) != "CLOSED":
            return (
                f"현재 세션의 assignment 권한 root({assignment_root or previous}) 밖인 "
                f"task({branch})로 전환할 수 없습니다."
            )
        return (
            "CLOSED 뒤 다음 독립 task를 시작하려면 먼저 새 task의 새 산출물 디렉터리를 "
            "구조화된 Write 도구로 바인딩하세요."
        )
    if previous == branch:
        _BINDING_DRAFT[path] = record
        return None
    values = branch_guard.metadata(target_root, branch)
    responsibility = (
        os.environ.get(ARTIFACT_RESPONSIBILITY_ENV, "").strip().casefold()
        or record.get("responsibility", "").casefold()
        or "owner"
    )
    if responsibility not in tuple(branch_guard.ARTIFACT_RESPONSIBILITIES):
        return f"지원하지 않는 산출물 책임입니다: {responsibility}"
    binding = {
        "directory": record.get("directory", ""),
        "branch": branch,
        "merge_target": str(values.get("merge-target") or ""),
        "task": assignment_root or branch,
        "responsibility": responsibility,
        "contract_version": str(values.get("contract-version") or ""),
        "worktree": str(target_root),
    }
    _BINDING_DRAFT[path] = binding
    return None


def _committed_paths(root: Path, branch: str) -> tuple[str, ...] | None:
    if not branch or not branch_guard.branch_exists(root, branch):
        return ()
    values = branch_guard.metadata(root, branch)
    parent_head = str(values.get("parent-head") or "")
    if branch_guard.FULL_SHA_PATTERN.fullmatch(parent_head) is None:
        return ()
    completed = subprocess.run(
        ["git", "diff", "--name-only", "-z", f"{parent_head}..{branch}"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return None
    return tuple(path for path in completed.stdout.split("\0") if path)


def changed_non_artifact_paths(root: Path, branch: str = "") -> tuple[str, ...] | None:
    working = branch_guard.changed_paths(root)
    if getattr(branch_guard, "GIT_STATUS_UNAVAILABLE", "") in working:
        return None
    selected_branch = branch or branch_guard.current_branch(root)
    committed = _committed_paths(root, selected_branch)
    if committed is None:
        return None
    return tuple(
        dict.fromkeys(
            path
            for path in (*working, *committed)
            if path and not path.startswith(ARTIFACT_SESSIONS_PREFIXES)
        )
    )


def git_artifact_ownership_denial(
    event: dict[str, Any],
    root: Path,
    host: str,
) -> str | None:
    """Git staging·commit도 현재 host·session의 산출물만 포함하게 한다."""

    tool_name = normalized_tool_name(event)
    raw_input = event.get("tool_input")
    tool_input = raw_input if isinstance(raw_input, dict) else {}
    command_value = tool_input.get("command")
    command = command_value if isinstance(command_value, str) else ""
    if tool_name not in SHELL_TOOLS or not command or trusted_branch_workflow_invocation(command, root):
        return None

    invocations = branch_guard.git_invocations(
        root,
        command,
        shell_working_directory(root, tool_input),
    )
    if invocations is None:
        return None
    affected: list[tuple[Path, str]] = []
    for invocation in invocations:
        arguments = invocation.arguments
        if not arguments:
            continue
        if arguments[0] == "add":
            affected.extend(
                (invocation.root, path)
                for path in branch_guard.changed_paths(invocation.root)
            )
            affected.extend(
                (invocation.root, path)
                for path in branch_guard._pathspecs_after_separator(arguments)
            )
        elif arguments[0] == "commit":
            affected.extend(
                (invocation.root, path)
                for path in branch_guard.staged_paths(invocation.root)
            )
    if any(path == branch_guard.GIT_STATUS_UNAVAILABLE for _, path in affected):
        return "Git 산출물 변경 상태를 확인할 수 없어 소유권 검증을 중단했습니다."

    artifact_paths = tuple(
        dict.fromkeys(
            (target_root, path)
            for target_root, path in affected
            if path.startswith(ARTIFACT_SESSIONS_PREFIXES)
        )
    )
    if not artifact_paths:
        return None
    denial = branch_guard.artifact_write_denial(
        tuple(path for _, path in artifact_paths),
        host,
    )
    if denial is not None:
        return denial
    current = bound_session_directory(event, root, host)
    if current is None:
        return "Git에 포함할 산출물이 현재 host·session에 귀속되지 않았습니다."
    for target_root, relative in artifact_paths:
        candidate = target_root / relative
        if candidate.is_dir() and not candidate.is_symlink() and candidate.resolve() == current.resolve():
            continue
        layout_denial = artifact_layout_denial(target_root, relative, host)
        if layout_denial is not None:
            return layout_denial
        session = artifact_session_directory(target_root, relative, host)
        if session is None or session.resolve() != current.resolve():
            return f"다른 세션의 산출물은 Git에 포함할 수 없습니다: {relative}"
    return None


def artifact_has_content(path: Path) -> bool:
    if path.is_symlink() or not path.is_file():
        return False
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return False
    table_rows = 0
    separator_seen = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("#", "<!--")):
            continue
        if TABLE_SEPARATOR.fullmatch(line):
            separator_seen = True
            continue
        if line.startswith("|"):
            if separator_seen:
                cells = [cell.strip() for cell in line.strip("|").split("|")]
                if any(cells):
                    table_rows += 1
            continue
        normalized = re.sub(r"^[\-*+>\d.()\s]+", "", line).strip()
        if len(normalized) >= 8 and re.search(r"\w", normalized):
            return True
    return table_rows > 0


def _has_grill_data_row(text: str) -> bool:
    match = re.search(r"##\s*neutral question flow\s*(.*?)(?:\n##\s+|\Z)", text, re.S | re.I)
    if match is None:
        return False
    separator_seen = False
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if TABLE_SEPARATOR.fullmatch(line):
            separator_seen = True
            continue
        if separator_seen and line.startswith("|"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) >= 5 and all(cells[:5]):
                return True
    return False


def _portfolio_issues(text: str) -> list[str]:
    matches = list(PORTFOLIO_CASE.finditer(text))
    if not matches:
        return ["portfolio-log.md: 사례가 없음"]
    issues: list[str] = []
    for index, match in enumerate(matches, start=1):
        end = matches[index].start() if index < len(matches) else len(text)
        section = text[match.end():end]
        headings = set(re.findall(r"^###\s+(.+?)\s*$", section, re.MULTILINE))
        missing_headings = [heading for heading in PORTFOLIO_HEADINGS if heading not in headings]
        missing_fields = [
            field
            for field in PORTFOLIO_FIELDS
            if re.search(rf"^-\s*{re.escape(field)}\s*:", section, re.MULTILINE) is None
        ]
        if missing_headings or missing_fields:
            missing = ", ".join((*missing_fields, *missing_headings))
            issues.append(f"portfolio-log.md: 사례 {index} 필수 구조 누락({missing})")
    return issues


def artifact_issues(session: Path) -> tuple[str, ...]:
    issues: list[str] = []
    texts: dict[str, str] = {}
    for name in REQUIRED_ARTIFACTS:
        target = session / name
        if target.is_symlink() or not target.is_file():
            issues.append(f"{name}: 없거나 symlink")
            continue
        try:
            text = target.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            issues.append(f"{name}: 읽을 수 없음")
            continue
        texts[name] = text
        if not artifact_has_content(target):
            issues.append(f"{name}: 제목·placeholder만 있거나 내용 없음")
    grill = texts.get("grill-me-review.md")
    if grill is not None:
        normalized = grill.casefold()
        if "## method guardrails" not in normalized:
            issues.append("grill-me-review.md: Method Guardrails 누락")
        if "neutral question-first 적용 여부" not in normalized:
            issues.append("grill-me-review.md: neutral question-first 확인 누락")
        if "recommended answer" not in normalized:
            issues.append("grill-me-review.md: Recommended Answer 열 누락")
        if not _has_grill_data_row(grill):
            issues.append("grill-me-review.md: 실제 질문·답변 데이터 행 누락")
    portfolio = texts.get("portfolio-log.md")
    if portfolio is not None:
        issues.extend(_portfolio_issues(portfolio))
    return tuple(issues)


def session_rebind_allowed(root: Path, session: Path, record: dict[str, str]) -> bool:
    """완료·merge된 이전 작업 뒤 같은 프로세스의 순차 작업 전환만 허용한다."""

    if artifact_issues(session):
        return False
    if changed_non_artifact_paths(root) != ():
        return False
    previous_branch = record.get("branch", "")
    previous_target = record.get("merge_target", "")
    current = branch_guard.current_branch(root)
    if not previous_branch or not previous_target or not current:
        return current == str(branch_guard.BASE_BRANCH)
    previous_values = (
        branch_guard.metadata(root, previous_branch)
        if branch_guard.branch_exists(root, previous_branch)
        else {}
    )
    previous_version = str(
        previous_values.get("contract-version") or record.get("contract_version", "")
    )
    if previous_version == str(branch_guard.CONTRACT_VERSION):
        if branch_guard.task_state(root, previous_branch) != "CLOSED":
            return False
    if not branch_guard.branch_exists(root, previous_target):
        return False
    if branch_guard.branch_exists(root, previous_branch) and not branch_guard.is_ancestor(
        root, previous_branch, previous_target
    ):
        return False
    if current == previous_target:
        return True
    current_values = branch_guard.metadata(root, current)
    return current_values.get("parent") == previous_target


def documentation_denial(event: dict[str, Any], root: Path, host: str) -> str | None:
    record = session_binding_record(event, root, host)
    changed = changed_non_artifact_paths(root, record.get("branch", ""))
    if changed == ():
        return None
    if changed is None:
        return "변경 상태를 확인할 수 없어 필수 산출물 검증을 완료하지 못했습니다."
    session = bound_session_directory(event, root, host)
    if session is None:
        prefix = artifact_sessions_prefix(host)
        return (
            "현재 세션에 귀속된 산출물 디렉터리가 없습니다. "
            f"{prefix}{{session-name}}/에 인계 문서를 작성하세요."
        )
    handoff_complete = artifact_has_content(session / HANDOFF_ARTIFACT)
    full_issues = artifact_issues(session)
    full_complete = not full_issues
    branch = record.get("branch", "") or branch_guard.current_branch(root)
    values = branch_guard.metadata(root, branch) if branch else {}
    artifact_mode = str(values.get("artifact-mode") or "")
    contract_version = str(values.get("contract-version") or "")
    responsibility = (
        os.environ.get(ARTIFACT_RESPONSIBILITY_ENV, "").strip().casefold()
        or record.get("responsibility", "").casefold()
        or "owner"
    )
    if responsibility not in tuple(branch_guard.ARTIFACT_RESPONSIBILITIES):
        return f"지원하지 않는 산출물 책임이라 완료할 수 없습니다: {responsibility}"
    assigned_task = record.get("task", "") or os.environ.get(TASK_ENV, "").strip()
    if assigned_task and branch and not branch_guard.assignment_includes_branch(
        root,
        assigned_task,
        branch,
    ):
        return (
            "session assignment 권한 계보와 산출물 branch가 다릅니다: "
            f"root={assigned_task}, branch={branch}"
        )
    if contract_version == str(branch_guard.CONTRACT_VERSION):
        if responsibility == "owner" and full_complete:
            return None
        if responsibility == "contributor" and handoff_complete:
            return None
        if responsibility == "contributor":
            return "부분 기여자는 현재 세션 디렉터리에 내용이 있는 handoff.md를 작성해야 합니다."
        return (
            "전체 작업 책임자는 현재 세션 디렉터리에 구조를 갖춘 필수 산출물 8종을 모두 작성해야 합니다. "
            f"확인 필요: {'; '.join(full_issues)}"
        )
    if artifact_mode == "full" and full_complete:
        return None
    if artifact_mode == "handoff" and handoff_complete:
        return None
    if not artifact_mode and (handoff_complete or full_complete):
        return None
    if artifact_mode == "full":
        return (
            "전체 작업 책임자는 현재 세션 디렉터리에 구조를 갖춘 필수 산출물 8종을 모두 작성해야 합니다. "
            f"확인 필요: {'; '.join(full_issues)}"
        )
    if artifact_mode == "handoff":
        return "부분 역할 기여자는 현재 세션 디렉터리에 내용이 있는 handoff.md를 작성해야 합니다."
    detail = f" 확인 필요: {'; '.join(full_issues)}" if full_issues else ""
    return (
        "legacy branch 계약의 변경을 완료하려면 현재 세션 디렉터리에 내용이 있는 handoff.md를 작성하거나 "
        f"필수 산출물 8종을 모두 작성해야 합니다.{detail}"
    )


def assignment_responsibility(event: dict[str, Any], root: Path, host: str) -> str:
    record = session_binding_record(event, root, host)
    return (
        os.environ.get(ARTIFACT_RESPONSIBILITY_ENV, "").strip().casefold()
        or record.get("responsibility", "").casefold()
        or "owner"
    )


def preservation_documentation_denial(
    event: dict[str, Any],
    root: Path,
    host: str,
) -> str | None:
    session = bound_session_directory(event, root, host)
    if session is None:
        return "작업을 PRESERVED로 전환하려면 현재 세션에 귀속된 산출물 디렉터리가 필요합니다."
    if not artifact_has_content(session / HANDOFF_ARTIFACT):
        return "작업을 PRESERVED로 전환하기 전에 현재 세션 디렉터리에 handoff.md를 작성해야 합니다."
    return None


def completion_assignment_denial(
    event: dict[str, Any],
    root: Path,
    host: str,
) -> str | None:
    responsibility = assignment_responsibility(event, root, host)
    if responsibility == "owner":
        return None
    return (
        "contributor assignment는 handoff까지만 수행할 수 있습니다. "
        "필수 산출물 8종을 책임지는 owner assignment가 finish·verify·close를 수행해야 합니다."
    )


def transient_state_path(
    event: dict[str, Any],
    root: Path,
    host: str,
    namespace: str,
) -> Path | None:
    common = branch_guard.git_common_directory(root) or root.resolve()
    return runtime_state.session_path(common, host, event_session_id(event), namespace)


def pending_binding_path(path: Path, event: dict[str, Any]) -> Path:
    call = event_protocol.tool_call_id(event)
    if not call:
        return path.with_name("pending-binding.json")
    return path.parent / "pending-bindings" / f"{runtime_state.digest(call)}.json"


def pending_bindings(path: Path) -> list[tuple[Path, dict]]:
    candidates = [path.with_name("pending-binding.json"), *sorted((path.parent / "pending-bindings").glob("*.json"))]
    return [(candidate, record) for candidate in candidates if (record := load_json_state(candidate))]


def reserve_binding(event: dict[str, Any], root: Path, host: str) -> None:
    if not _BINDING_DRAFT:
        return
    common = branch_guard.git_common_directory(root) or root.resolve()
    owner = runtime_state.owner_id(host, event_session_id(event))
    for path, binding in _BINDING_DRAFT.items():
        pending = pending_binding_path(path, event)
        for other_path, other in pending_bindings(path):
            if other_path == pending:
                continue
            proposed = other.get("binding", {})
            if any(proposed.get(key) != binding.get(key) for key in (("directory",) if branch_guard.SHARED_GIT_ACCESS else ("branch", "worktree", "directory"))):
                raise RuntimeError("실행 결과가 확인되지 않은 다른 branch/worktree의 도구 예약이 있습니다. 먼저 결과를 확인하세요.")
        directory = binding.get("directory")
        resource = "artifact:" + host + ":" + directory if directory else ""
        new_claim = False
        if resource:
            claim_path = runtime_state.repository_state(common) / "claims" / f"{runtime_state.digest(resource)}.json"
            new_claim = not load_json_state(claim_path)
            denial = runtime_state.claim(common, resource, owner)
            if denial:
                raise RuntimeError(denial)
        write_json_state(pending, {"call": event_protocol.tool_call_id(event), "binding": binding,
                                   "event": {key: event[key] for key in ("tool_name", "tool_input", "cwd") if key in event},
                                   "new_claim": resource if new_claim else ""})


def complete_binding(event: dict[str, Any], root: Path, host: str) -> None:
    path = session_binding_path(event, root, host)
    if path is None:
        return
    pending_path = pending_binding_path(path, event)
    pending = load_json_state(pending_path)
    call = event_protocol.tool_call_id(event)
    if not pending or pending.get("call", "") != call:
        return
    outcome = event_protocol.tool_outcome(event)
    if outcome is None:
        return
    binding = pending.get("binding")
    if outcome is True and isinstance(binding, dict):
        binding.pop("_action", None)
        write_json_state(path, binding)
        sources_path = path.with_name("artifact-sources.json")
        sources = load_json_state(sources_path)
        directory = binding.get("directory")
        worktree = binding.get("worktree")
        if directory and worktree:
            key = str(Path(worktree) / directory)
            sources["active"] = key
            roots = sources.setdefault("sources", [])
            if key not in roots:
                roots.append(key)
            write_json_state(sources_path, sources)
    release_resource = pending.get("new_claim")
    if outcome is False and branch_guard.SHARED_GIT_ACCESS and isinstance(binding, dict):
        logical = binding.get("directory")
        remaining = any(other_path != pending_path and other.get("binding", {}).get("directory") == logical
                        for other_path, other in pending_bindings(path))
        committed = load_json_state(path).get("directory") == logical
        # 마지막 실패 결과에서 해제한다. 다른 진행 중인 쓰기와 성공한 binding이
        # 사용하는 이름은 파일이 아직 보이지 않아도 보호한다.
        release_resource = "artifact:" + host + ":" + logical if logical and not remaining and not committed else ""
    if outcome is False and release_resource and isinstance(binding, dict):
        directory = Path(binding.get("worktree", str(root))) / binding.get("directory", "")
        if not directory.exists():
            common = branch_guard.git_common_directory(root) or root.resolve()
            claim_path = runtime_state.repository_state(common) / "claims" / f"{runtime_state.digest(release_resource)}.json"
            claim = load_json_state(claim_path)
            if claim.get("owner") == runtime_state.owner_id(host, event_session_id(event)):
                claim_path.unlink(missing_ok=True)
    pending_path.unlink(missing_ok=True)
