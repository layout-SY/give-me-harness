#!/usr/bin/env python3
"""소비자 프로젝트의 중앙 관리 파일, drift와 보호 명령을 검사한다."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Final

CENTRAL_ROOT: Final = Path("{{CENTRAL_ROOT}}")
DEV_COMMAND: Final = "{{DEV_COMMAND}}"
BUILD_COMMAND: Final = "{{BUILD_COMMAND}}"
MANIFEST_PATH: Final = ".agent-policy/manifest.json"
COMMAND_APPROVAL_PHRASE: Final = "명령 실행 승인"
APPROVAL_MAX_AGE_SECONDS: Final = 30 * 60
FALLBACK_MANAGED_ROOTS: Final = (
    "AGENTS.md",
    "CLAUDE.md",
    ".agent-policy/",
    ".agents/skills/",
    ".claude/agents/",
    ".claude/harness/",
    ".claude/hooks/",
    ".claude/multi-agent-spec.md",
    ".claude/multi-agent-spec/",
    ".claude/settings.json",
    ".claude/skills/",
    ".claude/templates/",
    ".claude/workflows/",
    ".codex/agents/",
    ".codex/config.toml",
    ".codex/harness/",
    ".codex/hooks.json",
    ".codex/hooks/",
    ".codex/multi-agent-spec.md",
    ".codex/multi-agent-spec/",
    ".codex/templates/",
    ".codex/workflows/",
    ".harness/roles/",
    ".opencode/agent/",
    ".opencode/plugins/",
    "opencode.json",
)
PATH_KEYS: Final = ("file_path", "filePath", "path", "paths", "notebook_path")
PATCH_PATH_PATTERN: Final = re.compile(
    r"^\*\*\* (?:(?:Add|Update|Delete) File|Move to): (.+)$", re.MULTILINE
)
SHELL_MUTATION_PATTERN: Final = re.compile(
    r"(?:^|[;&|]\s*)(?:rm|mv|cp|install|touch|mkdir|rmdir|truncate|tee|dd|ln|chmod|chown|patch)\b"
)
SHELL_REDIRECT_PATTERN: Final = re.compile(r"(?:^|[^<])>{1,2}(?!=)")
SHELL_IN_PLACE_PATTERN: Final = re.compile(r"\b(?:sed|perl)\b[^\n]*(?:\s-i(?:\s|$)|--in-place)")
SHELL_RUNTIME_WRITE_PATTERN: Final = re.compile(
    r"\b(?:python\d*|node|ruby)\b[^\n]*(?:writeFile|write_text|write_bytes|unlink|rename|replace|open\s*\([^\n]*['\"](?:w|a|x))"
)
BROAD_MUTATION_PATTERN: Final = re.compile(
    r"(?:git\s+(?:reset\s+--hard|clean\b|checkout\s+(?:--\s+)?\.|restore\s+\.)|rm\s+[^\n]*(?:\s|^)(?:\.|\./)(?:\s|$))"
)
SHELL_SEGMENT_PATTERN: Final = re.compile(r"(?:&&|\|\||[;|\n])")
SHELL_PREFIX_PATTERN: Final = re.compile(
    r"^(?:(?:[A-Za-z_][A-Za-z0-9_]*=\S+|command|env|sudo)\s+)*"
)
PACKAGE_BUILD_PATTERN: Final = re.compile(
    r"^(?:(?:npm|pnpm|yarn|bun)\s+(?:run\s+)?build(?:[:\s]|$)|"
    r"(?:npx\s+)?vite\s+build(?:\s|$)|tsc\s+-b(?:\s|$))"
)
PACKAGE_DEV_PATTERN: Final = re.compile(
    r"^(?:(?:npm|pnpm|yarn|bun)\s+(?:run\s+)?(?:dev|start|preview)(?:[:\s]|$)|"
    r"npm\s+start(?:\s|$)|(?:npx\s+)?vite(?:\s|$))"
)


def read_event() -> dict[str, Any]:
    try:
        value = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return {}
    return value if isinstance(value, dict) else {}


def repository_root(event: dict[str, Any]) -> Path:
    cwd_value = event.get("cwd")
    cwd = Path(cwd_value) if isinstance(cwd_value, str) and cwd_value else Path.cwd()
    for candidate in (cwd, *cwd.parents):
        if (candidate / MANIFEST_PATH).is_file():
            return candidate.resolve()

    completed = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode == 0 and completed.stdout.strip():
        return Path(completed.stdout.strip()).resolve()
    return cwd.resolve()


def load_manifest(root: Path) -> dict[str, Any]:
    try:
        value = json.loads((root / MANIFEST_PATH).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    return value if isinstance(value, dict) else {}


def managed_contract(manifest: dict[str, Any]) -> tuple[set[str], tuple[str, ...]]:
    managed = manifest.get("managed_files")
    files = set(managed) if isinstance(managed, dict) else set()
    files.add(MANIFEST_PATH)

    roots_value = manifest.get("managed_roots")
    roots = tuple(item for item in roots_value if isinstance(item, str)) if isinstance(roots_value, list) else ()
    return files, roots or FALLBACK_MANAGED_ROOTS


def repository_relative(root: Path, raw_path: str) -> str | None:
    if not raw_path.strip():
        return None
    candidate = Path(raw_path.strip())
    target = candidate if candidate.is_absolute() else root / candidate
    try:
        return target.resolve().relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        return None


def is_managed(relative: str, files: set[str], roots: tuple[str, ...]) -> bool:
    if relative in files:
        return True
    return any(
        relative == prefix.rstrip("/") or relative.startswith(prefix)
        for prefix in roots
    )


def collect_path_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    return []


def structured_targets(tool_input: dict[str, Any]) -> list[str]:
    targets: list[str] = []
    for key in PATH_KEYS:
        targets.extend(collect_path_values(tool_input.get(key)))
    return targets


def patch_targets(command: str) -> list[str]:
    return [match.strip() for match in PATCH_PATH_PATTERN.findall(command)]


def looks_like_shell_mutation(command: str) -> bool:
    return bool(
        SHELL_MUTATION_PATTERN.search(command)
        or SHELL_REDIRECT_PATTERN.search(command)
        or SHELL_IN_PLACE_PATTERN.search(command)
        or SHELL_RUNTIME_WRITE_PATTERN.search(command)
        or BROAD_MUTATION_PATTERN.search(command)
    )


def shell_mentions_managed(command: str, files: set[str], roots: tuple[str, ...]) -> list[str]:
    if BROAD_MUTATION_PATTERN.search(command):
        return ["<repository-wide mutation>"]
    candidates = sorted(files | {root.rstrip("/") for root in roots}, key=len, reverse=True)
    return [candidate for candidate in candidates if candidate and candidate in command]


def denied_targets(event: dict[str, Any], root: Path, manifest: dict[str, Any]) -> list[str]:
    files, roots = managed_contract(manifest)
    tool_name = str(event.get("tool_name", "")).rsplit(".", maxsplit=1)[-1].casefold()
    raw_input = event.get("tool_input")
    tool_input = raw_input if isinstance(raw_input, dict) else {}
    raw_targets = structured_targets(tool_input)

    command_value = tool_input.get("command")
    command = command_value if isinstance(command_value, str) else ""
    if tool_name in {"apply_patch", "patch"}:
        raw_targets.extend(patch_targets(command))

    denied: set[str] = set()
    for raw_path in raw_targets:
        relative = repository_relative(root, raw_path)
        if relative is not None and is_managed(relative, files, roots):
            denied.add(relative)

    if tool_name in {"bash", "shell"} and command and looks_like_shell_mutation(command):
        denied.update(shell_mentions_managed(command, files, roots))
    return sorted(denied)


def denial_message(targets: list[str]) -> str:
    rendered_targets = ", ".join(targets)
    return (
        "중앙 시스템 프롬프트는 소비자 프로젝트에서 수정할 수 없습니다.\n"
        f"대상: {rendered_targets}\n"
        f"중앙 프로젝트: {CENTRAL_ROOT}\n"
        "중앙 프로젝트에서 원본을 수정한 뒤 `bin/agent-policy diff --project all`을 확인하고 "
        "승인된 `bin/agent-policy sync --project all`을 실행하세요. "
        "그 다음 현재 작업을 handoff하고 세션을 재시작해 주세요."
    )


def shell_segments(command: str) -> tuple[str, ...]:
    return tuple(
        normalized
        for raw_segment in SHELL_SEGMENT_PATTERN.split(command)
        if (normalized := " ".join(raw_segment.strip(" ()\t").casefold().split()))
    )


def strip_shell_prefix(segment: str) -> str:
    return SHELL_PREFIX_PATTERN.sub("", segment, count=1)


def command_matches(segment: str, expected: str) -> bool:
    normalized = " ".join(expected.casefold().split())
    return bool(normalized) and (segment == normalized or segment.startswith(f"{normalized} "))


def protected_operation_categories(command: str) -> tuple[str, ...]:
    categories: set[str] = set()
    for raw_segment in shell_segments(command):
        segment = strip_shell_prefix(raw_segment)
        if segment == "git" or segment.startswith("git "):
            categories.add("Git")
        is_build = bool(
            command_matches(segment, BUILD_COMMAND) or PACKAGE_BUILD_PATTERN.match(segment)
        )
        if is_build:
            categories.add("빌드")
        if not is_build and (
            command_matches(segment, DEV_COMMAND) or PACKAGE_DEV_PATTERN.match(segment)
        ):
            categories.add("개발 서버")
    return tuple(sorted(categories))


def event_session_id(event: dict[str, Any]) -> str:
    for key in ("session_id", "sessionID"):
        value = event.get(key)
        if isinstance(value, str) and value:
            return value
    return "missing-session-id"


def approval_state_path(event: dict[str, Any], root: Path, host: str) -> Path:
    identity = f"{root.resolve()}\0{host}\0{event_session_id(event)}"
    digest = hashlib.sha256(identity.encode()).hexdigest()
    state_root = Path(tempfile.gettempdir()) / "asan-agent-policy-command-approvals"
    state_root.mkdir(mode=0o700, parents=True, exist_ok=True)
    return state_root / f"{digest}.json"


def load_approval_state(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    if not isinstance(value, dict):
        return {}
    created_at = value.get("created_at")
    if not isinstance(created_at, (int, float)) or time.time() - created_at > APPROVAL_MAX_AGE_SECONDS:
        path.unlink(missing_ok=True)
        return {}
    return value


def write_approval_state(path: Path, state: dict[str, Any]) -> None:
    temporary = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
    temporary.chmod(0o600)
    temporary.replace(path)


def command_digest(command: str) -> str:
    return hashlib.sha256(command.encode()).hexdigest()


def codex_operation_allowed(event: dict[str, Any], root: Path, command: str) -> bool:
    path = approval_state_path(event, root, "codex")
    state = load_approval_state(path)
    digest = command_digest(command)
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


def record_codex_approval(event: dict[str, Any], root: Path) -> None:
    prompt = event.get("prompt")
    if not isinstance(prompt, str) or prompt.strip() != COMMAND_APPROVAL_PHRASE:
        return

    path = approval_state_path(event, root, "codex")
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


def emit_operation_approval(host: str, message: str) -> None:
    if host in {"codex", "claude"}:
        decision = "deny" if host == "codex" else "ask"
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": decision,
                    "permissionDecisionReason": message,
                }
            },
            sys.stdout,
            ensure_ascii=False,
        )
        return
    print(message, file=sys.stderr)
    raise SystemExit(2)


def emit_denial(host: str, message: str) -> None:
    if host == "codex":
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": message,
                }
            },
            sys.stdout,
            ensure_ascii=False,
        )
        return
    print(message, file=sys.stderr)
    raise SystemExit(2)


def check_session(event: dict[str, Any]) -> None:
    root = repository_root(event)
    manifest = load_manifest(root)
    project_id = manifest.get("project_id")
    central_value = manifest.get("central_root")
    central = Path(central_value) if isinstance(central_value, str) else CENTRAL_ROOT
    cli = central / "bin/agent-policy"

    if not isinstance(project_id, str) or not cli.is_file():
        print(
            "중앙 정책 manifest 또는 CLI를 찾을 수 없습니다. "
            f"{CENTRAL_ROOT}에서 sync한 뒤 세션을 재시작해 주세요."
        )
        return

    completed = subprocess.run(
        [sys.executable, str(cli), "check", "--project", project_id, "--quiet"],
        cwd=central,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode == 0:
        return

    detail = completed.stderr.strip() or completed.stdout.strip()
    print(
        "중앙 시스템 프롬프트가 변경되었거나 소비자 파일에 drift가 있습니다. "
        f"{central}에서 diff와 sync를 확인하고 현재 작업을 handoff한 뒤 세션을 재시작해 주세요."
    )
    if detail:
        print(detail)


def check_operation(event: dict[str, Any], root: Path, host: str) -> None:
    if host == "opencode":
        return
    tool_name = str(event.get("tool_name", "")).rsplit(".", maxsplit=1)[-1].casefold()
    raw_input = event.get("tool_input")
    tool_input = raw_input if isinstance(raw_input, dict) else {}
    command_value = tool_input.get("command")
    command = command_value if isinstance(command_value, str) else ""
    if tool_name not in {"bash", "shell"} or not command:
        return

    categories = protected_operation_categories(command)
    if not categories:
        return
    if host == "codex" and codex_operation_allowed(event, root, command):
        return
    emit_operation_approval(host, operation_approval_message(command, categories, host))


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    host = sys.argv[2] if len(sys.argv) > 2 else ""
    event = read_event()

    if mode == "session-start":
        approval_state_path(event, repository_root(event), host).unlink(missing_ok=True)
        check_session(event)
        return
    if mode == "user-prompt" and host == "codex":
        record_codex_approval(event, repository_root(event))
        return
    if mode != "pre-tool":
        raise SystemExit("지원하지 않는 guard mode입니다.")

    root = repository_root(event)
    targets = denied_targets(event, root, load_manifest(root))
    if targets:
        emit_denial(host, denial_message(targets))
        return
    check_operation(event, root, host)


if __name__ == "__main__":
    main()
