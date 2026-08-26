#!/usr/bin/env python3
from __future__ import annotations

import re
import shlex
import sys
from pathlib import Path
from typing import Final

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hook_common import (
    ROOT,
    Event,
    EventIdentity,
    command_text,
    emit_pretool_allow,
    emit_pretool_deny,
    load_state,
    parse_identity,
    read_event,
    tool_input,
    tool_name,
    update_state,
)

MUTATION_TOOLS: Final = {"apply_patch", "edit", "write", "multiedit", "notebookedit"}
READ_ONLY_TOOLS: Final = {
    "glob",
    "grep",
    "list_mcp_resource_templates",
    "list_mcp_resources",
    "look_at",
    "lsp_diagnostics",
    "lsp_find_references",
    "lsp_goto_definition",
    "lsp_status",
    "lsp_symbols",
    "question",
    "read",
    "read_mcp_resource",
    "skill",
    "todowrite",
    "webfetch",
    "websearch",
}
ARTIFACT_NAMES: Final = {
    "plan.md",
    "exploration.md",
    "implementation-log.md",
    "grill-me-review.md",
    "review-log.md",
    "evaluation-log.md",
    "final-summary.md",
}
SESSION_PATTERN: Final = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{1,127}")
PATCH_PATH_PATTERN: Final = re.compile(
    r"^\*\*\* (?:(?:Add|Update|Delete) File|Move to): (.+)$", re.MULTILINE
)
SHELL_METACHARACTERS: Final = re.compile(r"[\n\r;&|><`$(){}\[\]*?!~\\'\"]")


def normalized_tool_name(name: str) -> str:
    return name.rsplit(".", maxsplit=1)[-1].casefold().replace("-", "_")


def safe_repository_path(raw: str) -> Path | None:
    candidate = Path(raw)
    target = candidate if candidate.is_absolute() else ROOT / candidate
    try:
        resolved_root = ROOT.resolve()
        resolved_target = target.resolve()
        resolved_target.relative_to(resolved_root)
    except (OSError, ValueError):
        return None
    return resolved_target


def mutation_targets(event: Event, name: str) -> list[Path]:
    values = tool_input(event)
    raw_paths: list[str] = []
    for key in ("file_path", "filePath", "path"):
        value = values.get(key)
        if isinstance(value, str):
            raw_paths.append(value)
    if name == "apply_patch":
        patch = (
            values.get("command")
            or values.get("patchText")
            or values.get("patch_text")
            or values.get("patch")
        )
        if isinstance(patch, str):
            raw_paths.extend(PATCH_PATH_PATTERN.findall(patch))
    targets = [safe_repository_path(raw) for raw in raw_paths]
    if any(target is None for target in targets):
        return []
    return [target for target in targets if target is not None]


def planning_session(target: Path) -> Path | None:
    sessions = (ROOT / ".codex" / "logs" / "sessions").resolve()
    try:
        relative = target.relative_to(sessions)
    except ValueError:
        return None
    if len(relative.parts) != 2:
        return None
    session_name, artifact = relative.parts
    if SESSION_PATTERN.fullmatch(session_name) is None or artifact not in ARTIFACT_NAMES:
        return None
    return sessions / session_name


def is_safe_argument_path(token: str) -> bool:
    if token.startswith("-"):
        return False
    return safe_repository_path(token) is not None


def is_read_only_bash(command: str) -> bool:
    if not command or SHELL_METACHARACTERS.search(command):
        return False
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        return False
    if tokens == ["pwd"]:
        return True
    if tokens and tokens[0] == "ls":
        return all(token in {"-a", "-l", "-la", "-al"} or is_safe_argument_path(token) for token in tokens[1:])
    if len(tokens) < 2 or tokens[0] != "git":
        return False
    offset = 2 if tokens[1] == "--no-pager" else 1
    if len(tokens) <= offset:
        return False
    subcommand = tokens[offset]
    arguments = tokens[offset + 1 :]
    if subcommand == "status":
        return all(argument in {"--short", "--branch", "--porcelain", "--untracked-files=all"} for argument in arguments)
    if tokens[1] != "--no-pager":
        return False
    if subcommand == "diff":
        allowed = {"--no-ext-diff", "--no-textconv", "--name-only", "--stat", "--cached", "--staged"}
        return {"--no-ext-diff", "--no-textconv"}.issubset(arguments) and all(
            argument in allowed or is_safe_argument_path(argument) for argument in arguments
        )
    if subcommand == "log":
        return all(
            argument in {"--oneline", "--decorate", "--stat", "--no-ext-diff"}
            or re.fullmatch(r"-[0-9]+", argument) is not None
            for argument in arguments
        )
    if subcommand == "ls-files":
        return all(argument in {"--cached", "--others", "--exclude-standard"} for argument in arguments)
    return False


def missing_prerequisites(identity: EventIdentity) -> list[str]:
    state = load_state(identity)
    missing: list[str] = []
    if not state.approval:
        missing.append("사용자 승인")
    if not state.skill_confirmed:
        missing.append("관련 SKILL.md 확인")
    if not state.exploration_completed:
        missing.append("재사용 자산 탐색")
    return missing


def main() -> None:
    event = read_event()
    name = normalized_tool_name(tool_name(event))
    identity = parse_identity(event, "PreToolUse", require_tool=True)
    if identity is None:
        emit_pretool_deny("[Codex Hook][PreToolUse][Blocked] harness event identity/provenance is missing.")
        return
    if name in READ_ONLY_TOOLS:
        emit_pretool_allow()
        return
    governed = name == "bash" or name in MUTATION_TOOLS
    if not governed:
        missing = missing_prerequisites(identity)
        if missing:
            emit_pretool_deny(
                "[Codex Hook][PreToolUse][Blocked] unclassified tool default-deny: "
                + ", ".join(missing)
            )
            return
        update_state(identity, source_mutated=True)
        emit_pretool_allow()
        return
    state = load_state(identity)
    if name == "bash":
        if is_read_only_bash(command_text(event)):
            emit_pretool_allow()
            return
        missing = missing_prerequisites(identity)
        if missing:
            emit_pretool_deny("[Codex Hook][PreToolUse][Blocked] Bash default-deny: " + ", ".join(missing))
            return
        update_state(identity, source_mutated=True)
        emit_pretool_allow()
        return
    targets = mutation_targets(event, name)
    if not targets:
        emit_pretool_deny("[Codex Hook][PreToolUse][Blocked] mutation target is missing or outside repository.")
        return
    sessions = [planning_session(target) for target in targets]
    if not state.approval:
        if any(session is None for session in sessions) or len(set(sessions)) != 1:
            emit_pretool_deny("[Codex Hook][PreToolUse][Blocked] pre-approval writes are limited to one task session's artifacts.")
            return
        update_state(identity, active_session=str(sessions[0]))
        emit_pretool_allow()
        return
    missing = missing_prerequisites(identity)
    if missing:
        emit_pretool_deny("[Codex Hook][PreToolUse][Blocked] 필수 조건 누락: " + ", ".join(missing))
        return
    changes: dict[str, bool | str] = {"source_mutated": True}
    bound_sessions = {session for session in sessions if session is not None}
    if len(bound_sessions) == 1:
        changes["active_session"] = str(bound_sessions.pop())
    update_state(identity, **changes)
    emit_pretool_allow()


if __name__ == "__main__":
    main()
