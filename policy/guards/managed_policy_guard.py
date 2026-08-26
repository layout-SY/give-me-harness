#!/usr/bin/env python3
"""소비자 프로젝트의 중앙 관리 파일 변경과 drift를 검사한다."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Final

CENTRAL_ROOT: Final = Path("{{CENTRAL_ROOT}}")
MANIFEST_PATH: Final = ".agent-policy/manifest.json"
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


def read_event() -> dict[str, Any]:
    try:
        value = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return {}
    return value if isinstance(value, dict) else {}


def repository_root(event: dict[str, Any]) -> Path:
    cwd_value = event.get("cwd")
    cwd = Path(cwd_value) if isinstance(cwd_value, str) and cwd_value else Path.cwd()
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


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    host = sys.argv[2] if len(sys.argv) > 2 else ""
    event = read_event()

    if mode == "session-start":
        check_session(event)
        return
    if mode != "pre-tool":
        raise SystemExit("지원하지 않는 guard mode입니다.")

    root = repository_root(event)
    targets = denied_targets(event, root, load_manifest(root))
    if targets:
        emit_denial(host, denial_message(targets))


if __name__ == "__main__":
    main()
