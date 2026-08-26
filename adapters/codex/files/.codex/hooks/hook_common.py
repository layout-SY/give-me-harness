#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import unicodedata
import uuid
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Final, TypeAlias

JsonValue: TypeAlias = None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]
Event: TypeAlias = dict[str, JsonValue]

ROOT = Path(__file__).resolve().parents[2]
STATE_ROOT = (
    Path(os.environ.get("TMPDIR", "/tmp")).resolve()
    / "codex-harness-state-v2"
    / hashlib.sha256(str(ROOT).encode("utf-8")).hexdigest()
)
IDENTIFIER_PATTERN: Final = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}")
TOOL_INPUT_KEYS: Final = ("tool_input", "arguments", "args", "input", "parameters")
PATH_KEYS: Final = ("file_path", "filePath", "path")


@dataclass(frozen=True, slots=True)
class EventIdentity:
    session_id: str
    task_id: str
    transcript_path: str

    @property
    def key(self) -> str:
        raw = f"{self.session_id}\0{self.task_id}\0{self.transcript_path}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class HarnessState:
    session_id: str
    task_id: str
    transcript_path: str
    approval: bool = False
    skill_confirmed: bool = False
    exploration_completed: bool = False
    source_mutated: bool = False
    active_session: str = ""


def read_event() -> Event:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        parsed: JsonValue = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    match parsed:
        case dict() as event:
            return event
        case _:
            return {}


def emit_user_prompt_allow() -> None:
    print("{}")


def emit_pretool_allow() -> None:
    print("{}")


def emit_pretool_deny(reason: str) -> None:
    output: Event = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    print(json.dumps(output, ensure_ascii=False))


def emit_posttool_allow() -> None:
    print("{}")


def emit_stop_allow() -> None:
    print("{}")


def emit_stop_block(reason: str) -> None:
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))


def prompt_text(event: Event) -> str:
    value = event.get("prompt")
    return unicodedata.normalize("NFKC", value) if isinstance(value, str) else ""


def tool_name(event: Event) -> str:
    value = event.get("tool_name")
    return value if isinstance(value, str) else ""


def tool_input(event: Event) -> dict[str, JsonValue]:
    for key in TOOL_INPUT_KEYS:
        value = event.get(key)
        if isinstance(value, dict):
            return value
    return {}


def command_text(event: Event) -> str:
    value = tool_input(event).get("command")
    return value if isinstance(value, str) else ""


def parse_identity(event: Event, expected_hook: str, *, require_tool: bool = False) -> EventIdentity | None:
    if event.get("hook_event_name") != expected_hook:
        return None
    session = event.get("session_id")
    task = event.get("task_id", "")
    transcript = event.get("transcript_path")
    cwd = event.get("cwd")
    if not isinstance(session, str) or IDENTIFIER_PATTERN.fullmatch(session) is None:
        return None
    if not isinstance(task, str) or (task and IDENTIFIER_PATTERN.fullmatch(task) is None):
        return None
    if not isinstance(cwd, str) or Path(cwd).resolve() != ROOT.resolve():
        return None
    if not isinstance(transcript, str):
        return None
    transcript_path = Path(transcript)
    if not transcript_path.is_absolute() or transcript_path.is_symlink() or not transcript_path.is_file():
        return None
    if require_tool:
        tool_use_id = event.get("tool_use_id")
        if not isinstance(tool_use_id, str) or IDENTIFIER_PATTERN.fullmatch(tool_use_id) is None:
            return None
    return EventIdentity(session, task, str(transcript_path.resolve()))


def _state_path(identity: EventIdentity) -> Path:
    return STATE_ROOT / identity.key / "state.json"


def _secure_directory(path: Path) -> bool:
    try:
        path.mkdir(parents=True, mode=0o700, exist_ok=True)
        if path.is_symlink() or not path.is_dir():
            return False
        path.chmod(0o700)
        return True
    except OSError:
        return False


def load_state(identity: EventIdentity) -> HarnessState:
    target = _state_path(identity)
    empty = HarnessState(identity.session_id, identity.task_id, identity.transcript_path)
    try:
        if STATE_ROOT.is_symlink() or target.parent.is_symlink():
            return empty
        metadata = target.lstat()
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
            return empty
        if hasattr(os, "getuid") and metadata.st_uid != os.getuid():
            return empty
        parsed: JsonValue = json.loads(target.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return empty
    if not isinstance(parsed, dict):
        return empty
    expected = {
        "session_id": identity.session_id,
        "task_id": identity.task_id,
        "transcript_path": identity.transcript_path,
    }
    if any(parsed.get(key) != value for key, value in expected.items()):
        return empty
    return HarnessState(
        identity.session_id,
        identity.task_id,
        identity.transcript_path,
        approval=parsed.get("approval") is True,
        skill_confirmed=parsed.get("skill_confirmed") is True,
        exploration_completed=parsed.get("exploration_completed") is True,
        source_mutated=parsed.get("source_mutated") is True,
        active_session=parsed.get("active_session") if isinstance(parsed.get("active_session"), str) else "",
    )


def update_state(identity: EventIdentity, **changes: bool | str) -> HarnessState:
    state = replace(load_state(identity), **changes)
    parent = _state_path(identity).parent
    if not _secure_directory(STATE_ROOT) or not _secure_directory(parent):
        return state
    temporary = parent / f".{uuid.uuid4().hex}.tmp"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(temporary, flags, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(asdict(state), handle, ensure_ascii=False, sort_keys=True)
        os.replace(temporary, _state_path(identity))
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
    return state


def clear_state(identity: EventIdentity) -> None:
    try:
        _state_path(identity).unlink()
    except FileNotFoundError:
        return


def changed_files() -> list[str]:
    if not (ROOT / ".git").exists():
        return []
    commands = (
        ("git", "diff", "--name-only", "-z"),
        ("git", "diff", "--cached", "--name-only", "-z"),
        ("git", "ls-files", "--others", "--exclude-standard", "-z"),
    )
    paths: set[str] = set()
    try:
        for command in commands:
            result = subprocess.run(
                command,
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            paths.update(path for path in result.stdout.split("\0") if path)
    except FileNotFoundError:
        return []
    return sorted(paths)


def is_protected_path(path: str) -> bool:
    normalized = path.removeprefix("./")
    if normalized.startswith(".codex/logs/sessions/"):
        return False
    return normalized.startswith(("src/", ".agents/", ".codex/", ".claude/", ".harness/", "docs/")) or normalized in {
        ".gitignore",
        ".env.template",
        "AGENTS.md",
        "CLAUDE.md",
        "package.json",
        "package-lock.json",
        "index.html",
    } or normalized.startswith((".env", "vite.config", "vitest.config", "tsconfig", "eslint.config"))
