"""호스트 이벤트를 공통 정책 판정과 실행 예약에 연결하는 진입점."""
from __future__ import annotations

import os
import json
import signal
import sys
from pathlib import Path
from types import ModuleType
from typing import Any


try:
    _loader_path = Path(__file__).resolve().with_name("runtime_loader.py")
    _loader = ModuleType("asan_runtime_loader")
    _loader.__file__ = str(_loader_path)
    exec(compile(_loader_path.read_bytes(), str(_loader_path), "exec"), _loader.__dict__)
    load_runtime_module = _loader.load

    _runtime_config = load_runtime_module("runtime_config")
    ARTIFACT_SESSIONS_PREFIXES = _runtime_config.ARTIFACT_SESSIONS_PREFIXES
    COMMAND_APPROVAL_PHRASE = _runtime_config.COMMAND_APPROVAL_PHRASE
    INJECT_BUNDLE_ROOT_ENV = _runtime_config.INJECT_BUNDLE_ROOT_ENV
    INJECT_PROJECT_ENV = _runtime_config.INJECT_PROJECT_ENV
    INJECT_ROLE_ENV = _runtime_config.INJECT_ROLE_ENV
    SHELL_TOOLS = _runtime_config.SHELL_TOOLS
    STRUCTURED_MUTATION_TOOLS = _runtime_config.STRUCTURED_MUTATION_TOOLS
    branch_guard = _runtime_config.branch_guard
    runtime_state = _runtime_config.runtime_state
    load_json_state = _runtime_config.load_json_state

    _artifact_policy = load_runtime_module("artifact_policy")
    _child_completion = load_runtime_module("child_completion")
    active_assignment_branch = _artifact_policy.active_assignment_branch
    bind_artifact_session = _artifact_policy.bind_artifact_session
    bind_task_assignment = _artifact_policy.bind_task_assignment
    complete_binding = _artifact_policy.complete_binding
    completion_assignment_denial = _artifact_policy.completion_assignment_denial
    documentation_denial = _artifact_policy.documentation_denial
    git_artifact_ownership_denial = _artifact_policy.git_artifact_ownership_denial
    preservation_documentation_denial = _artifact_policy.preservation_documentation_denial
    reserve_binding = _artifact_policy.reserve_binding
    session_binding_path = _artifact_policy.session_binding_path
    session_binding_record = _artifact_policy.session_binding_record

    _tool_paths = load_runtime_module("tool_paths")
    branch_workflow_contract = _tool_paths.branch_workflow_contract
    denial_message = _tool_paths.denial_message
    denied_targets = _tool_paths.denied_targets
    event_session_id = _tool_paths.event_session_id
    git_command_mutates = _tool_paths.git_command_mutates
    git_top_level = _tool_paths.git_top_level
    has_non_git_shell_mutation = _tool_paths.has_non_git_shell_mutation
    inject_mode = _tool_paths.inject_mode
    normalized_tool_name = _tool_paths.normalized_tool_name
    patch_targets = _tool_paths.patch_targets
    protected_operation_categories = _tool_paths.protected_operation_categories
    read_event = _tool_paths.read_event
    repository_root = _tool_paths.repository_root
    repository_target = _tool_paths.repository_target
    resolved_shell_target = _tool_paths.resolved_shell_target
    shell_redirect_targets = _tool_paths.shell_redirect_targets
    shell_working_directory = _tool_paths.shell_working_directory
    structured_targets = _tool_paths.structured_targets
    trusted_branch_workflow_action = _tool_paths.trusted_branch_workflow_action
    trusted_branch_workflow_arguments = _tool_paths.trusted_branch_workflow_arguments
    trusted_branch_workflow_invocation = _tool_paths.trusted_branch_workflow_invocation

    _approval_policy = load_runtime_module("approval_policy")
    codex_operation_allowed = _approval_policy.codex_operation_allowed
    harness_state_path = _approval_policy.harness_state_path
    implementation_gate_denial = _approval_policy.implementation_gate_denial
    implementation_gate_required = _approval_policy.implementation_gate_required
    record_post_tool = _approval_policy.record_post_tool
    record_user_prompt = _approval_policy.record_user_prompt

    _event_protocol = load_runtime_module("event_protocol")
    emit_denial = _event_protocol.emit_denial
    emit_operation_approval = _event_protocol.emit_operation_approval
    emit_session_context = _event_protocol.emit_session_context
    emit_stop_result = _event_protocol.emit_stop_result
except Exception as error:
    # 진입점 의존성 자체의 손상도 host가 일반 종료 오류로 무시하지 않게 한다.
    if len(sys.argv) > 2 and sys.argv[1:3] == ["pre-tool", "codex"]:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                         "permissionDecision": "deny", "permissionDecisionReason": f"정책 로드 오류: {error}"}}, ensure_ascii=False))
        raise SystemExit(0) from error
    print(f"정책 로드 오류: {error}", file=sys.stderr)
    raise SystemExit(2) from error


def branch_workflow_integrator_denial(
    event: dict[str, Any],
    root: Path,
    host: str,
    command: str,
) -> str | None:
    """승인 workflow도 계약에 기록된 단일 Git 통합 담당자만 실행하게 한다."""

    arguments = trusted_branch_workflow_arguments(command, root)
    if not arguments:
        return None
    action = arguments[0]
    assignment_root = active_assignment_branch(event, root, host)
    if action == "create":
        contract = branch_workflow_contract(event, root, arguments)
        requested_branch = contract.get("branch")
        parent_value = contract.get("parent")
        parent = parent_value if isinstance(parent_value, str) else ""
        if assignment_root:
            if not branch_guard.assignment_allows_branch_mutation(
                root,
                assignment_root,
                parent,
            ):
                return (
                    f"현재 세션의 assignment 권한 root({assignment_root}) 밖에서 "
                    f"task({requested_branch or '확인 불가'})를 생성할 수 없습니다.\n"
                    f"  요청 parent: {parent or '확인 불가'}"
                )
            if branch_guard.task_state(root, parent) != "ACTIVE":
                return f"ACTIVE 상태의 권한 계보 branch에서만 자식 task를 생성할 수 있습니다: {parent}"
        integrator = contract.get("git_integrator")
        if not isinstance(integrator, str) or not integrator:
            return "branch create proposal에서 Git 통합 담당자를 확인할 수 없습니다."
        if integrator == host:
            return None
        if integrator == "user":
            return "이 branch 계약의 Git 통합 담당자는 사용자입니다. AI 호스트가 create를 실행할 수 없습니다."
        return (
            f"이 branch 계약의 Git 통합 담당자는 {integrator}입니다. "
            f"현재 호스트({host})는 create를 실행할 수 없습니다."
        )
    if action in {"finish", "verify", "close"}:
        contract = branch_workflow_contract(event, root, arguments)
        if "completion_authority" in contract:
            try:
                _child_completion.validate(root, contract, action=action, host=host)
            except ValueError as error:
                return str(error)
            return None
        source_value = contract.get("source")
        source = source_value if isinstance(source_value, str) else ""
    elif action == "update-scope":
        contract = branch_workflow_contract(event, root, arguments)
        source_value = contract.get("branch")
        source = source_value if isinstance(source_value, str) else ""
    elif action in {"preserve", "resume"}:
        source = branch_guard.current_branch(root)
    else:
        return None
    if not source:
        return f"branch_workflow.py {action}의 source task를 확인할 수 없습니다."
    if assignment_root and not branch_guard.assignment_allows_branch_mutation(
        root,
        assignment_root,
        source,
    ):
        return (
            f"현재 세션의 assignment 권한 root({assignment_root}) 밖의 "
            f"task({source})에 {action}을 실행할 수 없습니다."
        )
    return branch_guard.git_integrator_denial(root, source, host)


def completion_documentation_denial(event: dict[str, Any], root: Path, host: str, command: str) -> str | None:
    """자식 병합에서는 자식 owner의 산출물을 검사하고 부모의 미완료 산출물과 구분한다."""
    arguments = trusted_branch_workflow_arguments(command, root)
    action = arguments[0] if arguments else ""
    try:
        if action == "finish-proposal":
            source = _tool_paths.branch_workflow_option(arguments, "--source")
            if source and source != branch_guard.current_branch(root):
                _child_completion.proposal(root, source, cleanup="--cleanup" in arguments, host=host)
                return None
        elif action in {"finish", "verify", "close"}:
            contract = branch_workflow_contract(event, root, arguments)
            if "completion_authority" in contract:
                # 바로 다음 branch_workflow_integrator_denial이 권한과 자식 산출물을 함께 검사한다.
                return None
    except ValueError as error:
        return str(error)
    return documentation_denial(event, root, host)


def branch_denial(event: dict[str, Any], root: Path, host: str) -> str | None:
    tool_name = normalized_tool_name(event)
    raw_input = event.get("tool_input")
    tool_input = raw_input if isinstance(raw_input, dict) else {}
    command_value = tool_input.get("command")
    command = command_value if isinstance(command_value, str) else ""
    shell_cwd = shell_working_directory(root, tool_input)
    shell_root = git_top_level(shell_cwd)
    if shell_root is None or not branch_guard.same_git_repository(root, shell_root):
        shell_root = root
    if command and trusted_branch_workflow_invocation(command, root):
        return branch_workflow_integrator_denial(event, shell_root, host, command)

    if tool_name not in STRUCTURED_MUTATION_TOOLS | SHELL_TOOLS:
        return None

    raw_targets = structured_targets(tool_input)
    if tool_name in {"apply_patch", "patch"}:
        raw_targets.extend(patch_targets(command))
    target_contexts: list[tuple[Path, str]] = []
    for raw_target in raw_targets:
        context = repository_target(root, raw_target)
        if context is None:
            return (
                "구조화된 변경 대상이 현재 소비자 Git 저장소의 승인된 worktree에 속하지 않습니다: "
                f"{raw_target}"
            )
        target_contexts.append(context)
    edit_tool = tool_name in STRUCTURED_MUTATION_TOOLS
    shell_tool = tool_name in SHELL_TOOLS
    if not edit_tool and not shell_tool:
        return None
    if edit_tool and target_contexts and all(
        relative.startswith(ARTIFACT_SESSIONS_PREFIXES)
        for _, relative in target_contexts
    ):
        # bind_artifact_session이 바로 앞에서 host·session·layout·assignment 귀속을
        # 검증했다. 진단·handoff 문서는 손상된 branch 계약을 복구하는 데도 필요하므로
        # artifact-only 구조화 쓰기를 source branch 유효성 검사와 결합하지 않는다.
        return None
    if shell_tool:
        for raw_target in shell_redirect_targets(command):
            target = resolved_shell_target(root, tool_input, raw_target)
            if target is None:
                return "shell redirect 대상을 안전하게 해석할 수 없어 실행을 차단했습니다."
            context = repository_target(root, str(target))
            if context is not None:
                target_contexts.append(context)
        if has_non_git_shell_mutation(command):
            return (
                "shell 명령의 비구조적 파일 변경은 branch scope와 소유권을 안전하게 확인할 수 없습니다. "
                "파일 경로를 구조적으로 전달하는 Edit/Write/apply_patch 도구를 사용하세요."
            )
        denial = branch_guard.command_denial(
            root,
            command,
            host=host,
            execution_cwd=shell_cwd,
            expected_branch=active_assignment_branch(event, root, host),
        )
        if denial is not None:
            return denial
    grouped: dict[Path, list[str]] = {}
    for target_root, relative in target_contexts:
        grouped.setdefault(target_root, []).append(relative)
    expected_branch = active_assignment_branch(event, root, host)
    for target_root, relatives in grouped.items():
        actual_branch = branch_guard.current_branch(target_root)
        if expected_branch and not branch_guard.assignment_allows_branch_mutation(
            target_root,
            expected_branch,
            actual_branch,
        ):
            contract_denial = branch_guard.active_branch_denial(
                target_root,
                tuple(dict.fromkeys(relatives)),
                host=host,
            )
            if contract_denial is not None:
                return contract_denial
            return (
                "현재 세션의 assignment 권한 계보와 구조화된 변경 대상 branch가 다릅니다.\n"
                f"  권한 root: {expected_branch}\n"
                f"  변경 대상: {actual_branch or 'detached HEAD'} ({target_root})"
            )
        denial = branch_guard.active_branch_denial(
            target_root,
            tuple(dict.fromkeys(relatives)),
            host=host,
        )
        if denial is not None:
            return denial
    return None


def operation_approval_message(command: str, categories: tuple[str, ...], host: str) -> str:
    category_text = ", ".join(categories)
    if host == "codex":
        action = (
            f"실행하려면 사용자가 `{COMMAND_APPROVAL_PHRASE}`만 독립된 메시지로 보내야 합니다. "
            "승인은 아래의 완전히 동일한 명령에 한해 1회만 유효합니다."
        )
    else:
        action = "호스트가 표시하는 권한 요청에서 사용자가 직접 실행 여부를 결정해야 합니다."
    return (
        f"{category_text} 명령은 사용자 승인 전에 실행할 수 없습니다.\n"
        f"명령: {command}\n"
        f"{action}"
    )


def check_session(event: dict[str, Any], host: str) -> None:
    root = repository_root(event)
    messages: list[str] = []
    project_id = os.environ.get(INJECT_PROJECT_ENV, "").strip()
    bundle_root = os.environ.get(INJECT_BUNDLE_ROOT_ENV, "").strip()
    if not inject_mode() or not project_id or not bundle_root:
        messages.append(
            "중앙 inject 실행 컨텍스트가 완전하지 않습니다. "
            "중앙 launcher로 새 세션을 시작해 주세요."
        )

    record = session_binding_record(event, root, host)
    focus = _artifact_policy.binding_worktree(root, record)
    if branch_guard.SHARED_GIT_ACCESS:
        messages.append(_artifact_policy.session_directory_context(event, root, host))
    messages.append(_approval_policy.readiness_context(event, focus if focus.is_dir() else root, host))
    context = branch_guard.branch_context(focus if focus.is_dir() else root)
    if context:
        messages.append(context)
    if messages:
        emit_session_context(host, "\n\n".join(messages))


def check_operation(event: dict[str, Any], root: Path, host: str) -> bool:
    if host == "opencode":
        return True
    tool_name = normalized_tool_name(event)
    raw_input = event.get("tool_input")
    tool_input = raw_input if isinstance(raw_input, dict) else {}
    command_value = tool_input.get("command")
    command = command_value if isinstance(command_value, str) else ""
    if tool_name not in SHELL_TOOLS or not command:
        return True

    categories = protected_operation_categories(command)
    if not categories:
        return True
    if host == "codex" and codex_operation_allowed(event, shell_working_directory(root, tool_input), command):
        return True
    if host == "claude":
        git_ownership(event, root, host, reserve=True)
        reserve_binding(event, root, host)
    emit_operation_approval(host, operation_approval_message(command, categories, host))

    return False


def operation_repository_root(event: dict[str, Any], root: Path) -> Path:
    raw_input = event.get("tool_input")
    tool_input = raw_input if isinstance(raw_input, dict) else {}
    candidate = git_top_level(shell_working_directory(root, tool_input))
    if candidate is not None and branch_guard.same_git_repository(root, candidate):
        return candidate
    return root


def completed_close_retry(event: dict[str, Any], root: Path, host: str) -> bool:
    """삭제된 source metadata 대신 같은 소유자의 완료 영수증으로 무변경 재시도를 판정한다."""
    if normalized_tool_name(event) not in SHELL_TOOLS:
        return False
    command = str(event.get("tool_input", {}).get("command") or "")
    arguments = trusted_branch_workflow_arguments(command, root)
    if not arguments or arguments[0] != "close":
        return False
    contract = branch_workflow_contract(event, root, arguments)
    digest = _tool_paths.branch_workflow_option(arguments, "--proposal-sha256")
    if contract.get("kind") != "finish" or branch_guard.contract_sha256(contract) != digest:
        return False
    common = branch_guard.git_common_directory(root)
    if common is None:
        return False
    receipt = runtime_state.read(common / "asan-agent-policy/integrations" / f"{digest}.json")
    if receipt.get("state") != "closed" or receipt.get("owner") != runtime_state.owner_id(host, event_session_id(event)):
        return False
    selected = Path(str(contract.get("integration_worktree") or root)).resolve()
    return (selected.is_dir() and branch_guard.same_git_repository(root, selected)
            and branch_guard.current_branch(selected) == contract.get("target")
            and branch_guard.head(selected, str(contract["target"])) == receipt.get("integration_head")
            and branch_guard.changed_paths(selected) == ())


def dispatch(mode: str, host: str, event: dict[str, Any]) -> None:
    # 입력 parsing과 transaction lock은 main이 맡는다.

    if mode == "session-start":
        root = repository_root(event)
        check_session(event, host)
        return
    if mode == "branch-context":
        root = repository_root(event)
        focus = _artifact_policy.binding_worktree(root, session_binding_record(event, root, host))
        if branch_guard.SHARED_GIT_ACCESS:
            print(_artifact_policy.session_directory_context(event, root, host))
        print(_approval_policy.readiness_context(event, focus if focus.is_dir() else root, host))
        context = branch_guard.branch_context(focus if focus.is_dir() else root)
        if context:
            print(context)
        return
    if mode == "format-stop":
        message = load_runtime_module("formatting").check(repository_root(event), event, host)
        if host == "opencode":
            if message:
                print(message, file=sys.stderr)
                raise SystemExit(2)
        elif event.get("stop_hook_active"):
            # 같은 오류로 종료를 무한 반복시키지 않고 미완료 결과를 보고하게 한다.
            print(json.dumps({"systemMessage": message} if message else {}, ensure_ascii=False))
        else:
            emit_stop_result(message)
        return
    if mode == "documentation-stop":
        # 구버전 adapter가 이 mode를 계속 호출해도 대화 종료를 재차단하지 않는다.
        # 산출물 계약은 명시적 finish/verify/close와 preserve PreToolUse에서 검증한다.
        emit_stop_result(None)
        return
    if mode == "user-prompt":
        record_user_prompt(event, repository_root(event), host)
        return
    if mode == "post-tool":
        load_runtime_module("formatting").record_after(repository_root(event), event, host)
        complete_binding(event, repository_root(event), host)
        record_post_tool(event, repository_root(event), host)
        if branch_guard.SHARED_GIT_ACCESS:
            load_runtime_module("git_operations").complete_write(repository_root(event), event, host)
        return
    if mode != "pre-tool":
        raise SystemExit("지원하지 않는 guard mode입니다.")

    root = repository_root(event)
    if branch_guard.SHARED_GIT_ACCESS:
        load_runtime_module("shared_git").pre_tool(event, root, host)
        return
    raw_input = event.get("tool_input")
    command = str(raw_input.get("command") or "") if isinstance(raw_input, dict) else ""
    if normalized_tool_name(event) in SHELL_TOOLS and _tool_paths.unsupported_workflow_invocation(command, root):
        emit_denial(host, "workflow는 단일 Python 명령으로 실행하세요. cd·개행·&&·리다이렉션을 분리하고 workdir로 위치를 지정하세요.")
        return
    targets = denied_targets(event, root)
    if targets:
        emit_denial(host, denial_message(targets))
        return
    if completed_close_retry(event, root, host):
        return
    binding_denial = bind_artifact_session(event, root, host)
    if binding_denial is not None:
        emit_denial(host, binding_denial)
        return
    git_artifact_denial = git_artifact_ownership_denial(event, root, host)
    if git_artifact_denial is not None:
        emit_denial(host, git_artifact_denial)
        return
    raw_input = event.get("tool_input")
    tool_input = raw_input if isinstance(raw_input, dict) else {}
    command_value = tool_input.get("command")
    command = command_value if isinstance(command_value, str) else ""
    workflow_action = trusted_branch_workflow_action(command, root)
    operation_root = operation_repository_root(event, root)
    if workflow_action == "preserve":
        preservation_denial = preservation_documentation_denial(event, operation_root, host)
        if preservation_denial is not None:
            emit_denial(host, preservation_denial)
            return
    if workflow_action in {"finish-proposal", "finish", "verify", "close"}:
        assignment_denial = completion_assignment_denial(event, operation_root, host)
        if assignment_denial is not None:
            emit_denial(host, assignment_denial)
            return
        completion_denial = completion_documentation_denial(event, operation_root, host, command)
        if completion_denial is not None:
            emit_denial(host, completion_denial)
            return
    denial = branch_denial(event, root, host)
    if denial is not None:
        emit_denial(host, denial)
        return
    assignment_binding_denial = bind_task_assignment(event, root, host)
    if assignment_binding_denial is not None:
        emit_denial(host, assignment_binding_denial)
        return
    role = os.environ.get(INJECT_ROLE_ENV, "")
    source_roles = branch_guard.RUNTIME_CONTRACT.get("capabilities", {}).get("source_write", [])
    if role and role not in source_roles and not workflow_action and normalized_tool_name(event) in STRUCTURED_MUTATION_TOOLS and implementation_gate_required(event, operation_root):
        emit_denial(host, f"{role} 역할은 source를 변경할 수 없습니다. 자기 산출물과 읽기 전용 조사를 사용하세요.")
        return
    ownership_denial = git_ownership(event, root, host, reserve=False)
    if ownership_denial:
        emit_denial(host, ownership_denial)
        return
    readiness_denial = implementation_gate_denial(event, operation_root, host)
    if readiness_denial is not None:
        emit_denial(host, readiness_denial)
        return
    if not check_operation(event, operation_root, host):
        return
    git_ownership(event, root, host, reserve=True)
    reserve_binding(event, root, host)


def git_ownership(event: dict[str, Any], root: Path, host: str, *, reserve: bool) -> str | None:
    raw_input = event.get("tool_input")
    tool_input = raw_input if isinstance(raw_input, dict) else {}
    command = str(tool_input.get("command") or "")
    action = trusted_branch_workflow_action(command, root)
    if normalized_tool_name(event) not in SHELL_TOOLS:
        return None
    operation_root = operation_repository_root(event, root)
    if action in {"proposal", "scope-proposal", "finish-proposal", "context"}:
        return None
    if action:
        contract = branch_workflow_contract(event, root, trusted_branch_workflow_arguments(command, root))
        if action == "create":
            operation_root = Path(str(contract.get("worktree") or operation_root)).resolve()
        elif action in {"finish", "verify", "close"}:
            operation_root = Path(str(contract.get("integration_worktree") or operation_root)).resolve()
        roots = (operation_root,)
    elif git_command_mutates(command):
        invocations = branch_guard.git_invocations(root, command, shell_working_directory(root, tool_input))
        roots = tuple(dict.fromkeys(item.root for item in (invocations or ()) if not branch_guard.git_arguments_are_read_only(item.arguments)))
    else:
        return None
    common = branch_guard.git_common_directory(root) or root.resolve()
    owner = runtime_state.owner_id(host, event_session_id(event))
    for selected in roots:
        resource = "git:" + str(selected.resolve())
        path = runtime_state.repository_state(common) / "claims" / f"{runtime_state.digest(resource)}.json"
        claim = runtime_state.read(path)
        if claim and claim.get("owner") != owner:
            return f"Git worktree의 통합 소유자가 다른 assignment입니다: {selected} (owner={claim.get('owner')})"
        reservations = common / "asan-agent-policy/integration-targets"
        for reservation in reservations.glob("*.json"):
            value = runtime_state.read(reservation)
            if value.get("worktree") == str(selected.resolve()) and (
                action not in {"finish", "verify", "close"}
                or value.get("finish_sha256") != branch_guard.contract_sha256(contract)
                or value.get("owner") != owner
            ):
                return "이 worktree의 다른 병합 검증·close 예약이 진행 중입니다. 완료 또는 명시적 복구 후 변경하세요."
        if reserve:
            runtime_state.claim(common, resource, owner)
    return None


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    host = sys.argv[2] if len(sys.argv) > 2 else ""
    time_limit = 8
    def timeout(_signum, _frame):
        raise RuntimeError(f"정책 검사가 제한 시간 {time_limit}초를 초과했습니다.")

    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(8)
    try:
        event = read_event()
        event["policy_host"] = host
        if mode == "post-tool":
            event = _event_protocol.normalize_tool_result(event)
        if mode == "pre-tool" and (not event.get("tool_name") or not isinstance(event.get("tool_input"), dict)):
            raise ValueError("PreToolUse에는 tool_name과 object 형식 tool_input이 필요합니다.")
        if (os.environ.get("ASAN_AGENT_POLICY_ASSIGNMENT") and mode in {"pre-tool", "post-tool", "user-prompt"}
                and event_session_id(event) == "missing-session-id"):
            raise ValueError("launcher assignment의 실제 host session ID가 필요합니다.")
        root = repository_root(event)
        common = branch_guard.git_common_directory(root) or root.resolve()
        formatting = load_runtime_module("formatting")
        for attempt in range(3):
            try:
                with runtime_state.locked(runtime_state.repository_state(common) / "events.lock"):
                    runtime_state.bind_native_session(common, host, event_session_id(event))
                    with branch_guard.git_snapshot():
                        dispatch(mode, host, event)
                break
            except formatting.FormattingRequired as request:
                if attempt == 2:
                    raise RuntimeError("포맷 중 변경이 반복되었습니다. 진행 중인 쓰기가 끝난 뒤 검증하세요.")
                time_limit = 50
                signal.alarm(time_limit)
                formatting.apply(root, event, host, request.worktree)
                time_limit = 8
                signal.alarm(time_limit)
    except Exception as error:
        if mode == "pre-tool":
            emit_denial(host, f"중앙 정책 검사 오류: {error}")
        else:
            print(f"중앙 정책 상태 오류: {error}", file=sys.stderr)
            raise SystemExit(2) from error
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()
