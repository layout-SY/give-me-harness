from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

from .core import CENTRAL_ROOT, PolicyError, ProjectConfig, atomic_write
from .role_profiles import HOST_ARTIFACT_SESSION_ROOTS, RUNTIME_CONTRACT

ACTIVE_CHANNELS: Final = ("codex", "claude", "opencode", "unknown")
_ARTIFACT_CONTRACT = RUNTIME_CONTRACT.get("artifacts")
if not isinstance(_ARTIFACT_CONTRACT, dict):
    raise RuntimeError("공통 runtime 계약의 artifacts가 object가 아닙니다.")
REQUIRED_ARTIFACTS: Final = tuple(
    str(name)
    for name in _ARTIFACT_CONTRACT.get("required", ())
    if isinstance(name, str)
) + (str(_ARTIFACT_CONTRACT.get("handoff", "handoff.md")),)
UNKNOWN_DIRECTORY: Final = str(
    _ARTIFACT_CONTRACT.get("unknown_directory", "unknown")
)
CHANNEL_SOURCES: Final = {
    channel: Path(relative)
    for channel, relative in HOST_ARTIFACT_SESSION_ROOTS.items()
} | {
    # 2026-09-02 이전 수동 수집 명령과 중앙 archive를 위한 호환 alias.
    "logic": Path(".codex/logs/sessions"),
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
        return ACTIVE_CHANNELS
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
            sources = [session / artifact_name for artifact_name in REQUIRED_ARTIFACTS]
            unknown_root = session / UNKNOWN_DIRECTORY
            if unknown_root.is_dir() and not unknown_root.is_symlink():
                sources.extend(
                    source
                    for source in sorted(unknown_root.rglob("*"))
                    if source.is_file() and not source.is_symlink()
                )
            for source in sources:
                if source.is_symlink() or not source.is_file():
                    continue
                source.resolve().relative_to(source_root.resolve())

                relative = Path(session.name) / source.relative_to(session)
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
