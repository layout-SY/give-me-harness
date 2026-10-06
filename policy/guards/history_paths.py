"""Validate the project-only transcript links created by the central launcher."""
from __future__ import annotations

import json
from pathlib import Path


def shared_history(home: Path) -> Path | None:
    marker = home / ".asan-project-history.json"
    if not marker.exists():
        return None
    expected = home.parents[2] / "codex-history"
    if (home.name != "codex-home" or home.parent.parent.name != "assignments"
            or home.is_symlink() or marker.is_symlink() or expected.is_symlink()):
        raise ValueError("Codex 프로젝트 이력 경로가 올바르지 않습니다.")
    record = json.loads(marker.read_text())
    if record != {"version": 1, "root": str(expected.resolve())}:
        raise ValueError("Codex 프로젝트 이력 manifest가 일치하지 않습니다.")
    for name in ("sessions", "archived_sessions"):
        target = expected / name
        link = home / name
        if target.is_symlink() or not target.is_dir() or not link.is_symlink() or link.resolve() != target.resolve():
            raise ValueError("Codex 프로젝트 대화 연결이 변경되었습니다.")
    return expected.resolve()


def transcript_roots(home: Path) -> tuple[Path, Path]:
    shared = shared_history(home)
    return tuple((shared or home) / name for name in ("sessions", "archived_sessions"))
