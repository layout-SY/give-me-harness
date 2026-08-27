from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

from .core import CENTRAL_ROOT, PolicyError, ProjectConfig, atomic_write

REQUIRED_ARTIFACTS: Final = (
    "plan.md",
    "exploration.md",
    "implementation-log.md",
    "grill-me-review.md",
    "review-log.md",
    "evaluation-log.md",
    "final-summary.md",
    "portfolio-log.md",
)
CHANNEL_SOURCES: Final = {
    "logic": Path(".codex/logs/sessions"),
    "claude": Path(".claude/logs/sessions"),
}


@dataclass(frozen=True)
class LogMirrorResult:
    project_id: str
    channel: str
    copied: tuple[str, ...]
    unchanged: int
    source_missing: bool


def selected_channels(selector: str) -> tuple[str, ...]:
    if selector == "all":
        return tuple(CHANNEL_SOURCES)
    if selector not in CHANNEL_SOURCES:
        raise PolicyError(f"지원하지 않는 로그 채널입니다: {selector}")
    return (selector,)


def collect_project_logs(
    project: ProjectConfig,
    channel: str,
    logs_root: Path | None = None,
) -> LogMirrorResult:
    if channel not in CHANNEL_SOURCES:
        raise PolicyError(f"지원하지 않는 로그 채널입니다: {channel}")

    source_root = project.path / CHANNEL_SOURCES[channel]
    target_root = (logs_root or CENTRAL_ROOT / "logs/projects").resolve()
    if not source_root.exists():
        return LogMirrorResult(project.id, channel, (), 0, True)
    if source_root.is_symlink() or not source_root.is_dir():
        raise PolicyError(f"안전한 로그 디렉터리가 아닙니다: {source_root}")

    copied: list[str] = []
    unchanged = 0
    try:
        sessions = sorted(source_root.iterdir(), key=lambda path: path.name)
        for session in sessions:
            if session.is_symlink() or not session.is_dir():
                continue
            for artifact_name in REQUIRED_ARTIFACTS:
                source = session / artifact_name
                if source.is_symlink() or not source.is_file():
                    continue
                source.resolve().relative_to(source_root.resolve())

                relative = Path(session.name) / artifact_name
                target = target_root / project.id / channel / "sessions" / relative
                target.parent.resolve().relative_to(target_root)
                content = source.read_bytes()
                if target.is_file() and not target.is_symlink() and target.read_bytes() == content:
                    unchanged += 1
                    continue
                if target.is_symlink():
                    raise PolicyError(f"중앙 로그 대상이 심볼릭 링크입니다: {target}")
                atomic_write(target, content)
                copied.append(relative.as_posix())
    except (OSError, ValueError) as error:
        raise PolicyError(
            f"필수 산출물 로그를 수집할 수 없습니다: {project.id}:{channel}: {error}"
        ) from error

    return LogMirrorResult(
        project_id=project.id,
        channel=channel,
        copied=tuple(copied),
        unchanged=unchanged,
        source_missing=False,
    )
