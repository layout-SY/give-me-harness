#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hook_common import JsonValue, ROOT, emit_posttool_allow, parse_identity, read_event, tool_input, tool_name, update_state


def repository_path(raw: str) -> Path | None:
    candidate = Path(raw)
    target = (candidate if candidate.is_absolute() else ROOT / candidate).resolve()
    try:
        target.relative_to(ROOT.resolve())
    except ValueError:
        return None
    return target


def is_skill_evidence(name: str, values: dict[str, JsonValue]) -> bool:
    if name.casefold() == "skill":
        skill = values.get("skill") or values.get("name")
        return isinstance(skill, str) and bool(skill.strip())
    if name.casefold() != "read":
        return False
    raw = values.get("file_path") or values.get("filePath")
    if not isinstance(raw, str):
        return False
    target = repository_path(raw)
    skills = (ROOT / ".agents" / "skills").resolve()
    return target is not None and target.name == "SKILL.md" and target.is_relative_to(skills)


def is_exploration_evidence(name: str, values: dict[str, JsonValue]) -> bool:
    if name.casefold() not in {"read", "glob", "grep"}:
        return False
    raw = values.get("file_path") or values.get("filePath") or values.get("path")
    if not isinstance(raw, str):
        return False
    target = repository_path(raw)
    if target is None:
        return False
    allowed = (
        (ROOT / "src" / "shared" / "ui").resolve(),
        (ROOT / ".agents" / "skills" / "reference" / "components").resolve(),
        (ROOT / ".codex" / "memory" / "reusable-assets.md").resolve(),
    )
    return any(target == base or target.is_relative_to(base) for base in allowed)


def main() -> None:
    event = read_event()
    identity = parse_identity(event, "PostToolUse", require_tool=True)
    if identity is None:
        emit_posttool_allow()
        return
    name = tool_name(event)
    values = tool_input(event)
    skill = is_skill_evidence(name, values)
    exploration = is_exploration_evidence(name, values)
    if skill:
        update_state(identity, skill_confirmed=True)
    if exploration:
        update_state(identity, exploration_completed=True)
    emit_posttool_allow()


if __name__ == "__main__":
    main()
