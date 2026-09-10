"""작업 범위별 승인·탐색 근거와 구현 gate."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import sys
import time
import unicodedata
from pathlib import Path
from types import ModuleType
from typing import Any


_loader_path = Path(__file__).resolve().with_name("runtime_loader.py")
_loader = ModuleType("asan_runtime_loader")
_loader.__file__ = str(_loader_path)
exec(compile(_loader_path.read_bytes(), str(_loader_path), "exec"), _loader.__dict__)
load_runtime_module = _loader.load

_runtime_config = load_runtime_module("runtime_config")
APPROVAL_MAX_AGE_SECONDS = _runtime_config.APPROVAL_MAX_AGE_SECONDS
APPROVAL_WORD_PATTERN = _runtime_config.APPROVAL_WORD_PATTERN
ARTIFACT_SESSIONS_PREFIXES = _runtime_config.ARTIFACT_SESSIONS_PREFIXES
COMMAND_APPROVAL_PHRASE = _runtime_config.COMMAND_APPROVAL_PHRASE
CONTRACT_SHA256_PATTERN = _runtime_config.CONTRACT_SHA256_PATTERN
DENIAL_WORD_PATTERN = _runtime_config.DENIAL_WORD_PATTERN
EMBEDDED_IMPLEMENTATION_APPROVAL_PHRASES = _runtime_config.EMBEDDED_IMPLEMENTATION_APPROVAL_PHRASES
IMPLEMENTATION_APPROVAL_PHRASES = _runtime_config.IMPLEMENTATION_APPROVAL_PHRASES
INJECT_ROLE_ENV = _runtime_config.INJECT_ROLE_ENV
READ_EVIDENCE_TOOLS = _runtime_config.READ_EVIDENCE_TOOLS
SHELL_TOOLS = _runtime_config.SHELL_TOOLS
STRUCTURED_MUTATION_TOOLS = _runtime_config.STRUCTURED_MUTATION_TOOLS
branch_guard = _runtime_config.branch_guard
event_protocol = _runtime_config.event_protocol
load_json_state = _runtime_config.load_json_state
write_json_state = _runtime_config.write_json_state

_artifact_policy = load_runtime_module("artifact_policy")
active_assignment_branch = _artifact_policy.active_assignment_branch
transient_state_path = _artifact_policy.transient_state_path

_tool_paths = load_runtime_module("tool_paths")
branch_workflow_option = _tool_paths.branch_workflow_option
git_command_mutates = _tool_paths.git_command_mutates
has_non_redirect_shell_mutation = _tool_paths.has_non_redirect_shell_mutation
injected_policy_roots = _tool_paths.injected_policy_roots
normalized_tool_name = _tool_paths.normalized_tool_name
patch_targets = _tool_paths.patch_targets
protected_operation_categories = _tool_paths.protected_operation_categories
relative_target = _tool_paths.relative_target
repository_target = _tool_paths.repository_target
resolved_shell_target = _tool_paths.resolved_shell_target
shell_redirect_targets = _tool_paths.shell_redirect_targets
structured_targets = _tool_paths.structured_targets
shell_working_directory = _tool_paths.shell_working_directory
target_in_injected_policy = _tool_paths.target_in_injected_policy
trusted_branch_workflow_action = _tool_paths.trusted_branch_workflow_action
trusted_branch_workflow_arguments = _tool_paths.trusted_branch_workflow_arguments

def approval_state_path(event: dict[str, Any], root: Path, host: str) -> Path | None:
    return transient_state_path(event, root, host, "command-approvals")


def harness_state_path(event: dict[str, Any], root: Path, host: str) -> Path | None:
    return transient_state_path(event, root, host, "harness-state-v3")


def load_approval_state(path: Path | None) -> dict[str, Any]:
    return load_json_state(path, max_age=APPROVAL_MAX_AGE_SECONDS)


def write_approval_state(path: Path | None, state: dict[str, Any]) -> None:
    write_json_state(path, state)


def normalize_prompt(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).casefold()
    normalized = re.sub(r"[.,!?。！？]+", " ", normalized)
    return " ".join(normalized.split())


def prompt_contract_sha256(text: str) -> str:
    matches = tuple(dict.fromkeys(match.casefold() for match in CONTRACT_SHA256_PATTERN.findall(text)))
    if len(matches) != 1 or DENIAL_WORD_PATTERN.search(text):
        return ""
    return matches[0] if APPROVAL_WORD_PATTERN.search(text) else ""


def is_implementation_approval(text: str) -> bool:
    normalized = normalize_prompt(text)
    if DENIAL_WORD_PATTERN.search(normalized):
        return False
    if normalized in IMPLEMENTATION_APPROVAL_PHRASES:
        return True
    padded = f" {normalized} "
    return any(f" {phrase} " in padded for phrase in EMBEDDED_IMPLEMENTATION_APPROVAL_PHRASES)


def event_output_text(event: dict[str, Any]) -> str:
    values: list[str] = []
    for key in ("tool_output", "tool_response", "result", "output", "stdout"):
        value = event.get(key)
        if isinstance(value, str):
            values.append(value)
        elif isinstance(value, dict):
            values.extend(item for item in value.values() if isinstance(item, str))
    return "\n".join(values)


def resolved_evidence_targets(
    event: dict[str, Any],
    root: Path,
) -> tuple[Path, ...]:
    raw_input = event.get("tool_input")
    tool_input = raw_input if isinstance(raw_input, dict) else {}
    targets: list[Path] = []
    execution_root = shell_working_directory(root, tool_input)
    for raw_path in structured_targets(tool_input):
        candidate = Path(raw_path).expanduser()
        try:
            target = (candidate if candidate.is_absolute() else execution_root / candidate).resolve()
        except (OSError, RuntimeError):
            continue
        targets.append(target)
    if normalized_tool_name(event) in SHELL_TOOLS:
        command_value = tool_input.get("command")
        command = command_value if isinstance(command_value, str) else ""
        try:
            tokens = shlex.split(command, posix=True)
        except ValueError:
            tokens = []
        if not tokens or Path(tokens[0]).name not in {"cat", "sed", "head", "tail", "rg", "grep", "ls", "find"} or any(token in {";", "&&", "||", "|"} for token in tokens):
            return tuple(targets)
        for token in tokens:
            if token.startswith("-") or not (
                "/" in token or token in {"src", ".agents", ".agent-policy"}
            ):
                continue
            candidate = Path(token).expanduser()
            try:
                target = (candidate if candidate.is_absolute() else execution_root / candidate).resolve()
            except (OSError, RuntimeError):
                continue
            targets.append(target)
    return tuple(dict.fromkeys(targets))


def is_skill_evidence(event: dict[str, Any], root: Path) -> bool:
    tool_name = normalized_tool_name(event)
    raw_input = event.get("tool_input")
    tool_input = raw_input if isinstance(raw_input, dict) else {}
    if tool_name == "skill":
        skill = tool_input.get("skill") or tool_input.get("name")
        return isinstance(skill, str) and bool(skill.strip())
    if tool_name not in READ_EVIDENCE_TOOLS | SHELL_TOOLS:
        return False
    if tool_name in SHELL_TOOLS:
        tokens = shlex.split(str(tool_input.get("command") or ""))
        if not tokens or Path(tokens[0]).name not in {"cat", "sed", "head", "tail"}:
            return False
    for target in resolved_evidence_targets(event, root):
        if target.name != "SKILL.md":
            continue
        allowed_roots = (
            root / ".agent-policy/common/skills",
            root / ".agents/skills",
            root / ".claude/skills",
            root / ".codex/skills",
            root / ".opencode/skills",
            *injected_policy_roots(),
        )
        if any(target == allowed.resolve() or target.is_relative_to(allowed.resolve()) for allowed in allowed_roots):
            return True
    return False


def is_exploration_evidence(event: dict[str, Any], root: Path) -> bool:
    tool_name = normalized_tool_name(event)
    if tool_name not in READ_EVIDENCE_TOOLS | SHELL_TOOLS:
        return False
    for target in resolved_evidence_targets(event, root):
        try:
            context = repository_target(root, str(target))
            relative = context[1] if context else target.relative_to(root.resolve()).as_posix()
        except ValueError:
            relative = ""
        if relative == "src" or relative.startswith("src/"):
            return True
        if "reference/" in target.as_posix():
            return True
    return False


def is_ui_exploration_evidence(event: dict[str, Any], root: Path) -> bool:
    tool_name = normalized_tool_name(event)
    if tool_name not in READ_EVIDENCE_TOOLS | SHELL_TOOLS:
        return False
    for target in resolved_evidence_targets(event, root):
        try:
            context = repository_target(root, str(target))
            relative = context[1] if context else target.relative_to(root.resolve()).as_posix()
        except ValueError:
            relative = ""
        if relative == "src/shared/ui" or relative.startswith("src/shared/ui/"):
            return True
        if "reference/components" in target.as_posix():
            return True
    return False


def task_context(event: dict[str, Any], root: Path, host: str) -> dict[str, Any]:
    """아직 쓰지 않은 기존 task도 식별하되 종료된 branch의 문맥은 제외한다."""
    if branch_guard.SHARED_GIT_ACCESS:
        return {"task": os.environ.get("ASAN_AGENT_POLICY_TASK", ""),
                "branch": branch_guard.current_branch(root), "task_values": {}, "values": {}}
    binding = _artifact_policy.session_binding_record(event, root, host)
    task = active_assignment_branch(event, root, host)
    if binding.get("_action") == "create":
        # 생성 예약은 아직 branch 계약이 아니다. 생성 전 승인의 범위는 확정된
        # 초점에 두고, 성공 PostTool 이후 처음 생성된 task에 연결한다.
        binding = load_json_state(_artifact_policy.session_binding_path(event, root, host))
    focus = binding.get("branch") or branch_guard.current_branch(root)

    def active_values(branch: str) -> dict[str, Any]:
        values = branch_guard.metadata(root, branch) if branch else {}
        if values.get("contract-version") != branch_guard.CONTRACT_VERSION or values.get("state") == "CLOSED":
            return {}
        return values

    focus_values = active_values(focus)
    task_values = active_values(task)
    if not task_values:
        task = focus if focus_values else ""
        task_values = focus_values
    return {"task": task, "branch": focus if focus_values else "",
            "task_values": task_values, "values": focus_values}


def requires_ui_exploration(event: dict[str, Any], root: Path, host: str) -> bool:
    if os.environ.get(INJECT_ROLE_ENV, "").strip().casefold() == "ui":
        return True
    if branch_guard.SHARED_GIT_ACCESS:
        return False
    tool_input = event.get("tool_input") or {}
    command = str(tool_input.get("command") or "")
    if trusted_branch_workflow_action(command, root) == "create":
        arguments = trusted_branch_workflow_arguments(command, root)
        contract = _tool_paths.branch_workflow_contract(event, root, arguments)
        if branch_guard.contract_sha256(contract) == branch_workflow_option(arguments, "--proposal-sha256"):
            return "ui" in contract.get("roles", [])
    return "ui" in task_context(event, root, host)["values"].get("roles", ())


def approval_scope(event: dict[str, Any], root: Path, host: str) -> dict[str, Any]:
    context = task_context(event, root, host)
    directory = _artifact_policy.bound_session_directory(event, root, host)
    plan = directory / "plan.md" if directory else None
    if branch_guard.SHARED_GIT_ACCESS and (plan is None or not plan.is_file()):
        # 다른 worktree에 결과 로그를 쓰더라도 승인한 원래 계획은 유지한다.
        # 그 위치에 새 plan.md를 작성하거나 원래 계획을 바꾸면 내용 비교로
        # 정상적으로 구현 재승인을 요구한다.
        previous = load_json_state(harness_state_path(event, root, host)).get("implementation_scope", {})
        raw = previous.get("plan_path", "")
        context = _tool_paths.repository_target(root, raw) if raw else None
        if context and context[1].startswith(_artifact_policy.artifact_sessions_prefix(host)):
            plan = Path(raw)
    plan_digest = hashlib.sha256(plan.read_bytes()).hexdigest() if plan and plan.is_file() and not plan.is_symlink() else ""
    if branch_guard.SHARED_GIT_ACCESS:
        return {"task": "session", "role": os.environ.get(INJECT_ROLE_ENV, ""),
                "contract": "", "plan": plan_digest, "plan_path": str(plan) if plan else "", "source_scopes": []}
    return {"task": context["task"], "role": os.environ.get(INJECT_ROLE_ENV, ""),
            "contract": str(context["task_values"].get("contract-sha256") or ""), "plan": plan_digest,
            "source_scopes": list(context["values"].get("scope") or context["task_values"].get("scope") or ())}


def load_harness_state(event: dict[str, Any], root: Path, host: str) -> dict[str, Any]:
    state = load_json_state(harness_state_path(event, root, host))
    scope = approval_scope(event, root, host)
    previous = state.get("assignment_scope")
    if isinstance(previous, dict) and previous.get("task"):
        changed = previous.get("task") != scope["task"] or previous.get("role") != scope["role"]
        changed = changed or bool(previous.get("contract") and scope["contract"] and previous["contract"] != scope["contract"])
        if changed:
            state = {}
    state["assignment_scope"] = scope
    approved_scope = state.get("implementation_scope", {})
    if approved_scope.get("plan") and approved_scope["plan"] != scope["plan"]:
        state["implementation_approved"] = False
    approved_sources = approved_scope.get("source_scopes", [])
    if state.get("implementation_approved") and not approved_sources and scope["source_scopes"]:
        # 최초 branch 생성 전에 받은 구현 승인을 첫 승인 branch 범위에 연결한다.
        approved_scope["source_scopes"] = scope["source_scopes"]
        state["implementation_scope"] = approved_scope
    elif approved_sources and any(not any(
        parent == "." or candidate == parent or (not any(token in parent for token in "*?[") and candidate.startswith(parent.rstrip("/") + "/"))
        for parent in approved_sources) for candidate in scope["source_scopes"]):
        state["implementation_approved"] = False
    return state


def readiness_requirements(event: dict[str, Any], root: Path, host: str) -> dict[str, str]:
    exploration = ("ui_exploration_completed", "src/shared/ui 재사용 자산 탐색") if requires_ui_exploration(event, root, host) else (
        "exploration_completed", "역할별 재사용 자산·인접 구현 탐색")
    return {"implementation_approved": "사용자 구현 승인", "skill_confirmed": "관련 SKILL.md 확인",
            exploration[0]: exploration[1]}


def readiness_context(event: dict[str, Any], root: Path, host: str) -> str:
    """조회용 상태와 다음 조치. 읽기나 사용자 승인을 생성하지 않는다."""
    state = load_harness_state(event, root, host)
    context = task_context(event, root, host)
    requirements = readiness_requirements(event, root, host)
    missing = [label for key, label in requirements.items() if state.get(key) is not True]
    if branch_guard.SHARED_GIT_ACCESS:
        return "\n".join([
            "[SESSION_READINESS]", "- git_access: shared-project",
            "- branch_creation_required: false",
            f"- role: {os.environ.get(INJECT_ROLE_ENV, '') or '미지정'}",
            *(f"- {key}: {str(state.get(key) is True).lower()}" for key in requirements),
            f"- 소스 구현 준비: {', '.join(missing) or '완료'}",
            "- 모든 branch/worktree에서 Git 변경은 사용자 승인, 조회는 자유입니다.",
            "- Git에는 구현 준비·branch 계약·소유권·CLOSED 검사를 적용하지 않습니다.",
        ])
    lines = ["[SESSION_READINESS]", f"- task: {context['task'] or '미지정'}",
             f"- role: {os.environ.get(INJECT_ROLE_ENV, '') or '미지정'}",
             f"- branch_creation_required: {str(not bool(context['branch'])).lower()}"]
    lines.extend(f"- {key}: {str(state.get(key) is True).lower()}" for key in requirements)
    lines.extend((f"- approved_contracts: {json.dumps(state.get('approved_contracts', {}), ensure_ascii=False)}",
                  f"- pending_contracts: {json.dumps(state.get('pending_contracts', {}), ensure_ascii=False)}",
                  f"- 미충족: {', '.join(missing) or '없음'}"))
    if context["branch"]:
        lines.append("- 기존 V3 task를 이어갈 때 branch 생성 승인은 필요하지 않습니다. 현재 계약·경로·소유권 검사는 적용됩니다.")
        if context["values"].get("state") == "PRESERVED":
            lines.append("- PRESERVED task는 준비 조건 확인 후 명시적 resume으로 ACTIVE를 복원하세요.")
    else:
        lines.append("- 변경 작업이면 계획·구현 승인 뒤 새 branch proposal의 SHA 승인을 별도로 확인하세요.")
    if missing:
        lines.append("- 첫 변경 전에 위 미충족 조건을 확인하세요. 구현 승인은 계획·역할 보고 후 Proceed로 기록하며, SHA 승인과 별개입니다.")
        if state.get("pending_contracts"):
            lines.append("- 이미 대기 중인 계약은 전체 SHA로 먼저 승인한 뒤 구현 승인을 별도로 기록하세요.")
    lines.append("- 읽기 전용 조사는 가능합니다. 이 상태는 명령 실행 승인이나 변경 권한을 대신하지 않습니다.")
    return "\n".join(lines)


def record_post_tool(event: dict[str, Any], root: Path, host: str) -> None:
    path = harness_state_path(event, root, host)
    if path is None:
        return
    if not event_protocol.tool_succeeded(event):
        return
    state = load_harness_state(event, root, host)
    call = event_protocol.tool_call_id(event)
    processed = state.setdefault("processed_calls", [])
    if call and call in processed:
        return
    if call:
        state["processed_calls"] = (processed + [call])[-256:]
    if is_skill_evidence(event, root):
        state["skill_confirmed"] = True
    if is_exploration_evidence(event, root):
        state["exploration_completed"] = True
    if is_ui_exploration_evidence(event, root):
        state["ui_exploration_completed"] = True

    raw_input = event.get("tool_input")
    tool_input = raw_input if isinstance(raw_input, dict) else {}
    command_value = tool_input.get("command")
    command = command_value if isinstance(command_value, str) else ""
    if trusted_branch_workflow_action(command, root) in {
        "proposal",
        "scope-proposal",
        "finish-proposal",
    }:
        digests = tuple(
            dict.fromkeys(
                match.casefold()
                for match in CONTRACT_SHA256_PATTERN.findall(event_output_text(event))
            )
        )
        if len(digests) == 1:
            state["pending_contract_sha256"] = digests[0]
            state["pending_contract_kind"] = trusted_branch_workflow_action(command, root)
            state.setdefault("pending_contracts", {})[digests[0]] = state["pending_contract_kind"]
            state.pop("approved_contract_sha256", None)
    if state:
        write_json_state(path, state)


def command_digest(command: str) -> str:
    return hashlib.sha256(command.encode()).hexdigest()


def operation_fingerprint(root: Path, command: str) -> str:
    """사용자가 확인한 작업 위치, 명령, ref와 실제 변경 내용을 함께 고정한다."""
    invocations = branch_guard.git_invocations(root, command, root) or ()
    snapshots = []
    for invocation in invocations:
        target, args = invocation.root, invocation.arguments
        if not args or branch_guard.git_arguments_are_read_only(args):
            continue
        snapshots.append([str(target), branch_guard.current_branch(target), branch_guard.head(target)])
        selected: tuple[str, ...] = ()
        if args[0] == "add":
            files = branch_guard._git(target, "ls-files", "-c", "-o", "--exclude-standard", "-z", "--",
                                      *branch_guard._pathspecs_after_separator(args))
            if files.returncode:
                raise RuntimeError("승인할 stage 경로를 확인할 수 없습니다.")
            selected = tuple(sorted(set(filter(None, files.stdout.split("\0")))))
        elif args[0] == "commit":
            # commit은 index의 실제 내용을 고정한다. 타 세션의 unstaged
            # 로그 갱신은 이 작업의 재승인 사유가 아니다.
            snapshots.append(["index", branch_guard._output(target, "diff", "--cached", "--binary")])
            if any(value in {"--all", "--only", "--include"} or re.fullmatch(r"-[A-Za-z]*[aio][A-Za-z]*", value)
                   for value in args[1:]):
                selected = branch_guard.changed_paths(target)
        else:
            selected = tuple(name for name in branch_guard.changed_paths(target)
                             if not name.startswith(ARTIFACT_SESSIONS_PREFIXES))
            for value in args[1:]:
                if not value.startswith("-"):
                    resolved = branch_guard._output(target, "rev-parse", "--verify", "--end-of-options", value + "^{object}")
                    if resolved:
                        snapshots.append([value, resolved])
            if args[0] in {"push", "pull", "fetch", "remote"}:
                snapshots.append(["remotes", branch_guard._output(target, "remote", "-v")])
        for relative in selected:
            file = target / relative
            content = (os.readlink(file).encode() if file.is_symlink() else
                       file.read_bytes() if file.is_file() else b"<absent>")
            snapshots.append([relative, hashlib.sha256(content).hexdigest()])
    return command_digest(json.dumps([str(root.resolve()), command, snapshots], ensure_ascii=False))


def operation_allowed(event: dict[str, Any], root: Path, host: str, command: str) -> bool:
    path = approval_state_path(event, root, host)
    if path is None:
        return False
    current = operation_fingerprint(root, command)
    previous = load_approval_state(path)
    if previous.get("approved") is True and previous.get("command_sha256") == current:
        path.unlink(missing_ok=True)
        return True
    write_approval_state(path, {"approved": False, "command_sha256": current,
                              "command": command, "worktree": str(root.resolve()),
                              "created_at": time.time()})
    return False


def codex_operation_allowed(event: dict[str, Any], root: Path, command: str) -> bool:
    path = approval_state_path(event, root, "codex")
    if path is None:
        return False
    state = load_approval_state(path)
    digest = command_digest(str(root.resolve()) + "\0" + command)
    if state.get("approved") is True and state.get("command_sha256") == digest:
        path.unlink(missing_ok=True)
        return True

    write_approval_state(
        path,
        {
            "approved": False,
            "categories": list(protected_operation_categories(command)),
            "command_sha256": digest,
            "created_at": time.time(),
        },
    )
    return False


def record_user_prompt(event: dict[str, Any], root: Path, host: str) -> None:
    prompt = event.get("prompt")
    if not isinstance(prompt, str):
        return

    if branch_guard.SHARED_GIT_ACCESS:
        path = approval_state_path(event, root, host)
        pending = load_approval_state(path)
        explicit = prompt.strip() == COMMAND_APPROVAL_PHRASE or is_implementation_approval(prompt)
        if pending and explicit and not DENIAL_WORD_PATTERN.search(prompt):
            pending["approved"] = True
            pending["created_at"] = time.time()
            write_approval_state(path, pending)
            print("보고한 동일 Git 작업 단위를 한 번 실행하도록 승인했습니다.")
            return
        if pending and DENIAL_WORD_PATTERN.search(prompt):
            path.unlink(missing_ok=True)
        harness_path = harness_state_path(event, root, host)
        harness = load_harness_state(event, root, host)
        if explicit and prompt.strip() != COMMAND_APPROVAL_PHRASE:
            harness["implementation_approved"] = True
            harness["implementation_scope"] = approval_scope(event, root, host)
        elif normalize_prompt(prompt) in {"구현 승인 취소", "구현 중단", "cancel implementation"}:
            harness["implementation_approved"] = False
        write_json_state(harness_path, harness)
        return

    harness_path = harness_state_path(event, root, host)
    harness_state = load_harness_state(event, root, host)
    if prompt.strip() != COMMAND_APPROVAL_PHRASE:
        approved_digest = prompt_contract_sha256(prompt)
        approved = is_implementation_approval(prompt)
        pending = harness_state.get("pending_contract_sha256")
        pending_contracts = harness_state.setdefault("pending_contracts", {})
        if pending and pending not in pending_contracts:
            pending_contracts[pending] = str(harness_state.get("pending_contract_kind") or "explicit")
        if normalize_prompt(prompt) in {"구현 승인 취소", "구현 중단", "cancel implementation", "revoke implementation approval"}:
            harness_state["implementation_approved"] = False
        elif approved and not approved_digest and len(pending_contracts) > 1:
            print("승인 대기 계약이 여러 개입니다. 승인할 전체 SHA-256을 명시해야 합니다.")
        elif approved_digest or (approved and pending_contracts):
            digest = approved_digest or next(iter(pending_contracts))
            harness_state["approved_contract_sha256"] = digest
            kind = pending_contracts.pop(digest, "explicit")
            contracts = harness_state.setdefault("approved_contracts", {})
            contracts[kind] = digest
            harness_state.pop("pending_contract_sha256", None)
            harness_state.pop("pending_contract_kind", None)
        elif approved:
            harness_state["implementation_approved"] = True
            scope = approval_scope(event, root, host)
            previous = harness_state.get("implementation_scope", {}).get("source_scopes", [])
            scope["source_scopes"] = sorted(set(previous + scope["source_scopes"]))
            harness_state["implementation_scope"] = scope
        write_json_state(harness_path, harness_state)
        return

    if host != "codex":
        return

    path = approval_state_path(event, root, host)
    state = load_approval_state(path)
    if not state or state.get("approved") is not False:
        return
    state["approved"] = True
    state["created_at"] = time.time()
    write_approval_state(path, state)
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": "직전에 차단된 동일 명령을 1회 실행할 수 있습니다. 명령을 변경하면 다시 승인을 요청하세요.",
            }
        },
        sys.stdout,
        ensure_ascii=False,
    )


def implementation_gate_required(event: dict[str, Any], root: Path) -> bool:
    tool_name = normalized_tool_name(event)
    raw_input = event.get("tool_input")
    tool_input = raw_input if isinstance(raw_input, dict) else {}
    command_value = tool_input.get("command")
    command = command_value if isinstance(command_value, str) else ""
    if tool_name in STRUCTURED_MUTATION_TOOLS:
        raw_targets = structured_targets(tool_input)
        if tool_name in {"apply_patch", "patch"}:
            raw_targets.extend(patch_targets(command))
        if not raw_targets:
            return True
        relatives = tuple(
            context[1] if (context := repository_target(root, raw_path)) is not None else None
            for raw_path in raw_targets
        )
        return any(
            relative is None or not relative.startswith(ARTIFACT_SESSIONS_PREFIXES)
            for relative in relatives
        )
    if tool_name not in SHELL_TOOLS or not command:
        return False
    action = trusted_branch_workflow_action(command, root)
    if action:
        return action in {
            "create",
            "update-scope",
            "finish",
            "verify",
            "close",
            "preserve",
            "resume",
        }
    if git_command_mutates(command) or has_non_redirect_shell_mutation(command):
        return True
    for raw_target in shell_redirect_targets(command):
        target = resolved_shell_target(root, tool_input, raw_target)
        if target is None or target_in_injected_policy(target) is not None:
            return True
        context = repository_target(root, str(target))
        relative = context[1] if context is not None else relative_target(root, target)
        if relative is not None and not relative.startswith(ARTIFACT_SESSIONS_PREFIXES):
            return True
    return False


def implementation_gate_denial(
    event: dict[str, Any],
    root: Path,
    host: str,
) -> str | None:
    if not implementation_gate_required(event, root):
        return None
    state = load_harness_state(event, root, host)
    missing = [label for key, label in readiness_requirements(event, root, host).items()
               if state.get(key) is not True]

    raw_input = event.get("tool_input")
    tool_input = raw_input if isinstance(raw_input, dict) else {}
    command_value = tool_input.get("command")
    command = command_value if isinstance(command_value, str) else ""
    action = trusted_branch_workflow_action(command, root)
    if action in {"create", "update-scope", "finish", "verify", "close"}:
        arguments = trusted_branch_workflow_arguments(command, root)
        proposed_digest = branch_workflow_option(arguments, "--proposal-sha256").casefold()
        kind = {"create": "proposal", "update-scope": "scope-proposal", "finish": "finish-proposal", "verify": "finish-proposal", "close": "finish-proposal"}[action]
        contracts = state.get("approved_contracts", {})
        approved_digest = str(contracts.get(kind) or contracts.get("explicit") or "").casefold()
        if CONTRACT_SHA256_PATTERN.fullmatch(proposed_digest) is None:
            missing.append("64자리 proposal SHA-256")
        elif approved_digest != proposed_digest:
            missing.append("현재 proposal SHA-256에 대한 사용자 승인")
    if not missing:
        return None
    if branch_guard.SHARED_GIT_ACCESS:
        return ("소스 구현 준비가 필요합니다: " + ", ".join(dict.fromkeys(missing))
                + ". 승인한 계획과 성공한 스킬·탐색 근거를 확인하세요. Git 변경 승인은 별도로 처리합니다.")
    return (
        "공통 구현 gate의 필수 조건이 누락되었습니다: "
        + ", ".join(dict.fromkeys(missing))
        + ". 미충족 구현 승인은 계획·역할 보고 후 Proceed로 기록하고, 관련 스킬과 "
        "재사용 자산·인접 구현은 실제 성공한 읽기로 확인하세요. SHA 승인은 구현 승인을 대신하지 않습니다."
    )
