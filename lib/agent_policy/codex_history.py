"""Project transcripts are shared; hooks, skills and approvals remain isolated."""
from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

from .core import PolicyError, ProjectConfig, atomic_write, sha256_bytes
from .runtime import load_runtime

NATIVE_ID = re.compile(r"[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}")


def name_records(path: Path) -> dict[str, dict]:
    latest = {}
    for line in path.read_text().splitlines():
        try:
            value = json.loads(line)
            if (not isinstance(value, dict) or not isinstance(value.get("id"), str)
                    or not isinstance(value.get("thread_name"), str) or not isinstance(value.get("updated_at"), str)):
                continue
            timestamp = datetime.fromisoformat(value["updated_at"].replace("Z", "+00:00")).timestamp()
        except (ValueError, TypeError):
            continue
        if timestamp >= latest.get(value["id"], {}).get("timestamp", float("-inf")):
            latest[value["id"]] = {"timestamp": timestamp, "line": line}
    return latest


def prepare_history(project: ProjectConfig, home: Path, state_root: Path, source_home: Path) -> Path:
    repository = home.parents[2]
    history = repository / "codex-history"
    state = load_runtime("runtime_state")
    with state.locked(repository / "codex-history.lock"):
        if history.is_symlink():
            raise PolicyError("프로젝트 대화 저장소는 symlink일 수 없습니다.")
        history.mkdir(exist_ok=True)
        for name in ("sessions", "archived_sessions", "thread-writer-locks"):
            directory = history / name
            if directory.is_symlink():
                raise PolicyError("프로젝트 대화 디렉터리는 symlink일 수 없습니다.")
            directory.mkdir(exist_ok=True)
        listing = subprocess.run(["git", "worktree", "list", "--porcelain", "-z"], cwd=project.path,
                                 capture_output=True, text=True, check=True).stdout
        roots = {str(Path(item[9:]).resolve()) for item in listing.split("\0") if item.startswith("worktree ")}
        sources = {state_root / project.id / "codex-home", source_home}
        current = json.loads((home.parent / "assignment.json").read_text())
        for path in (repository / "assignments").glob("*/assignment.json"):
            record = state.read(path)
            if (record.get("project") != project.id or record.get("host") != "codex"
                    or record.get("repository") != current["repository"]):
                continue
            roots.add(str(Path(record["worktree"]).resolve()))
            binding = state.read(path.with_name("session-binding.json"))
            if binding.get("worktree"):
                roots.add(str(Path(binding["worktree"]).resolve()))
            raw = record.get("environment", {}).get("CODEX_HOME")
            if raw:
                sources.add(Path(raw))
        imports_path = history / "imports.json"
        imported = state.read(imports_path)
        index_path = history / "session_index.jsonl"
        if index_path.is_symlink():
            raise PolicyError("프로젝트 대화 index는 symlink일 수 없습니다.")
        if not index_path.exists():
            atomic_write(index_path, b"")
        names = name_records(index_path)
        for source in sorted(sources):
            if source == home or source.is_symlink():
                continue
            for name in ("sessions", "archived_sessions"):
                directory = source / name
                # New launches already point to the common store. Never re-import it.
                if directory.is_symlink():
                    continue
                for path in sorted(directory.glob("**/*.jsonl")):
                    if path.is_symlink() or not path.resolve().is_relative_to(directory.resolve()):
                        continue
                    if str(path) in imported:
                        continue
                    try:
                        with path.open() as stream:
                            meta = json.loads(stream.readline(1024 * 1024))
                        payload = meta.get("payload", {})
                        native = payload.get("id", "")
                        if (meta.get("type") != "session_meta" or not isinstance(native, str)
                                or not NATIVE_ID.fullmatch(native) or not isinstance(payload.get("cwd"), str)
                                or str(Path(payload["cwd"]).resolve()) not in roots):
                            continue
                        before = path.stat()
                        content = path.read_bytes()
                        after = path.stat()
                        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                            raise PolicyError(f"대화가 기록 중입니다. 기존 세션을 종료한 뒤 다시 시작하세요: {path}")
                    except (OSError, ValueError, AttributeError):
                        continue
                    # One canonical rollout per native ID; originals remain intact.
                    try:
                        timestamp = datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00"))
                    except (KeyError, TypeError, ValueError):
                        raise PolicyError(f"대화 생성 시각을 확인할 수 없습니다: {path}")
                    relative = Path(timestamp.strftime("%Y/%m/%d")) if name == "sessions" else Path()
                    target = history / name / relative / f"rollout-{timestamp:%Y-%m-%dT%H-%M-%S}-{native}.jsonl"
                    existing = list((history / "sessions").glob(f"**/*{native}*.jsonl")) + list(
                        (history / "archived_sessions").glob(f"**/*{native}*.jsonl"))
                    if existing:
                        target = existing[0]
                        previous = target.read_bytes()
                        if len(existing) != 1 or not previous.startswith(content):
                            raise PolicyError(f"같은 native ID의 대화가 서로 다릅니다. 원본 확인이 필요합니다: {path}")
                    else:
                        atomic_write(target, content)
                        os.utime(target, ns=(before.st_atime_ns, before.st_mtime_ns))
                    imported[str(path)] = {"sha256": sha256_bytes(content), "target": str(target)}
            source_index = source / "session_index.jsonl"
            if source_index.is_file() and not source_index.is_symlink() and str(source_index) not in imported:
                known = {Path(item["target"]).stem[-36:] for item in imported.values() if item.get("target")}
                selected = []
                for native, value in name_records(source_index).items():
                    if native in known and value["timestamp"] > names.get(native, {}).get("timestamp", float("-inf")):
                        selected.append(value["line"])
                        names[native] = value
                if selected:
                    with index_path.open("a") as stream:
                        stream.write("\n".join(selected) + "\n")
                imported[str(source_index)] = {"sha256": sha256_bytes(source_index.read_bytes())}
        state.write(imports_path, imported)
        for name in ("sessions", "archived_sessions", "thread-writer-locks", "session_index.jsonl"):
            link = home / name
            if link.exists() or link.is_symlink():
                if not link.is_symlink() or link.resolve() != (history / name).resolve():
                    raise PolicyError(f"Codex 이력 연결 대상이 이미 존재합니다: {link}")
            else:
                link.symlink_to(history / name, target_is_directory=name != "session_index.jsonl")
        atomic_write(home / ".asan-project-history.json", (json.dumps(
            {"version": 1, "root": str(history.resolve())}) + "\n").encode())
    return history
