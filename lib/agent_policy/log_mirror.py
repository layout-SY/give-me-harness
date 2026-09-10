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
COLLECTED_ARTIFACTS: Final = REQUIRED_ARTIFACTS + tuple(
    str(name) for name in _ARTIFACT_CONTRACT.get("optional", ()) if isinstance(name, str)
)
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
    session_sources: tuple[Path, ...] | None = None,
) -> LogMirrorResult:
    if channel not in CHANNEL_SOURCES:
        raise PolicyError(f"지원하지 않는 로그 채널입니다: {channel}")

    source_root = project.path / CHANNEL_SOURCES[channel]
    target_root = (logs_root or CENTRAL_ROOT / "logs/projects").resolve()
    if session_sources is None and not source_root.exists():
        return LogMirrorResult(project.id, channel, (), 0, True)
    if session_sources is None and (source_root.is_symlink() or not source_root.is_dir()):
        raise PolicyError(f"안전한 로그 디렉터리가 아닙니다: {source_root}")

    copied: list[str] = []
    unchanged = 0
    try:
        sessions = session_sources if session_sources is not None else tuple(sorted(source_root.iterdir(), key=lambda path: path.name))
        preferred = {session.name: session for session in sessions}
        seen: set[Path] = set()
        for session in reversed(sessions):
            if session.is_symlink() or not session.is_dir():
                continue
            current_source_root = session.parent if session_sources is not None else source_root
            sources = [session / artifact_name for artifact_name in COLLECTED_ARTIFACTS]
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
                source.resolve().relative_to(current_source_root.resolve())

                relative = Path(session.name) / source.relative_to(session)
                if relative in seen:
                    continue
                seen.add(relative)
                target = target_root / project.id / channel / "sessions" / relative
                target.parent.resolve().relative_to(target_root)
                # 활성 위치에서 제거된 파일도 이전 worktree의 사본으로 되돌리지 않는다.
                if session != preferred[session.name] and target.exists():
                    unchanged += 1
                    continue
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


def assignment_log_sources(project: ProjectConfig, channel: str, assignment: str, state_root: Path) -> tuple[Path, ...]:
    """기록된 이동 순서대로 수집하여 현재 위치가 마지막으로 반영되게 한다."""
    import hashlib
    import subprocess
    from .runtime import load_runtime
    runtime = load_runtime("runtime_state")
    completed = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=project.path,
                               text=True, capture_output=True, check=True)
    raw = Path(completed.stdout.strip())
    common = (raw if raw.is_absolute() else project.path / raw).resolve()
    if len(assignment) != 32 or any(value not in "0123456789abcdef" for value in assignment):
        raise PolicyError("로그 수집 assignment ID가 올바르지 않습니다.")
    directory = state_root / "repositories" / hashlib.sha256(str(common).encode()).hexdigest() / "assignments" / assignment
    record = runtime.read(directory / "assignment.json")
    if record.get("repository") != str(common) or record.get("project") != project.id or record.get("host") != channel:
        raise PolicyError("로그 수집 assignment의 repository/project/host가 다릅니다.")
    source_record = runtime.read(directory / "artifact-sources.json")
    sources = source_record.get("sources", [])
    if not sources:
        declared = record.get("environment", {}).get("ASAN_SESSION_DIR")
        sources = [str(Path(record["worktree"]) / declared)] if declared else []
    active = source_record.get("active")
    ordered = [source for source in sources if source != active] + ([active] if active else [])
    result: list[Path] = []
    prefix = CHANNEL_SOURCES[channel]
    for source in ordered:
        path = Path(source)
        archived = source_record.get("archived", {})
        if source in archived and not path.exists():
            continue
        if active in archived and not Path(active).exists() and path.name == Path(active).name:
            continue
        if path.is_symlink() or any(parent.is_symlink() for parent in path.parents):
            raise PolicyError(f"산출물 출처가 심볼릭 링크입니다: {path}")
        path = path.resolve()
        worktree = path.parents[len(prefix.parts)]
        if path.parent != worktree / prefix:
            raise PolicyError(f"산출물 출처의 host 경로가 올바르지 않습니다: {path}")
        if not worktree.exists():
            raise PolicyError(f"수집할 worktree가 먼저 제거되었습니다: {worktree}")
        actual = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=worktree,
                                text=True, capture_output=True, check=True).stdout.strip()
        actual_path = Path(actual)
        if (actual_path if actual_path.is_absolute() else worktree / actual_path).resolve() != common:
            raise PolicyError(f"다른 Git 저장소의 산출물을 수집할 수 없습니다: {path}")
        result.append(path)
    return tuple(result)
