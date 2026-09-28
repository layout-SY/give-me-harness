"""새 linked worktree의 프로젝트별 영속 저장 위치를 검증한다."""
from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path
from types import ModuleType

_path = Path(__file__).with_name("runtime_loader.py")
_loader = ModuleType("worktree_storage_loader")
_loader.__file__ = str(_path)
exec(compile(_path.read_bytes(), str(_path), "exec"), _loader.__dict__)
config = _loader.load("runtime_config")


def temporary_roots() -> tuple[Path, ...]:
    values = ["/tmp", "/private/tmp", "/var/tmp", "/private/var/tmp",
              "/var/folders", "/private/var/folders", tempfile.gettempdir()]
    values.extend(os.environ[key] for key in ("TMPDIR", "TMP", "TEMP") if os.environ.get(key))
    return tuple({Path(value).expanduser().resolve() for value in values})


def default_destination(branch: str) -> Path:
    prefix, separator, suffix = branch.partition("/")
    task = suffix if separator and prefix in {"task", "feature", "feat", "fix", "hotfix", "chore", "refactor", "docs", "test"} else branch
    name = re.sub(r"[^\w.-]+", "-", task).strip(".-_").lower()
    if not name:
        raise RuntimeError("작업 폴더 이름을 계산할 수 없습니다. --worktree로 경로를 명시하세요.")
    return config.WORKTREE_ROOT / name


def destination(root: Path, cwd: Path, raw: str) -> Path:
    if not raw.strip() or any(char in raw for char in "\0\n\r"):
        raise RuntimeError("새 worktree의 실제 경로를 명시하세요.")
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = cwd / path
    target = path.resolve()
    configured = config.WORKTREE_ROOT.expanduser()
    if not configured.is_absolute():
        raise RuntimeError("프로젝트 worktree_root 절대 경로가 필요합니다.")
    storage_root = configured.resolve()
    if any(target.is_relative_to(item) or storage_root.is_relative_to(item) for item in temporary_roots()):
        raise RuntimeError(f"임시 디렉토리에 작업용 worktree를 생성할 수 없습니다. 프로젝트 저장 위치: {configured}")
    if target.parent != storage_root:
        raise RuntimeError(f"새 worktree는 프로젝트 저장 위치의 작업 폴더로 생성하세요: {configured}/<작업명>")
    if path.is_symlink() or target.exists():
        raise RuntimeError(f"worktree 경로가 이미 존재합니다. 다른 작업명을 선택하세요: {target}")
    if _loader.load("project_boundary").foreign_repository(root, target):
        raise RuntimeError("다른 프로젝트 안에 linked worktree를 생성할 수 없습니다.")
    for entry in _loader.load("branch_relations").worktrees(root):
        existing = Path(entry["worktree"]).resolve()
        if target.is_relative_to(existing) or existing.is_relative_to(target):
            raise RuntimeError("등록된 worktree 경로와 겹칩니다. 사라진 경로도 복구 상태를 먼저 확인하세요.")
    return target


def git_destination(root: Path, cwd: Path, args: tuple[str, ...] | list[str]) -> Path | None:
    if len(args) < 2 or args[0] != "worktree":
        return None
    # Git은 subcommand 앞의 --도 허용한다.
    words = list(args[1:])
    if words[0] == "--":
        words.pop(0)
    if not words or words[0] != "add":
        return None
    flags = {"-f", "--force", "-d", "--detach", "--checkout", "--no-checkout",
             "--lock", "--orphan", "-q", "--quiet", "--track", "--no-track",
             "--guess-remote", "--no-guess-remote"}
    positionals: list[str] = []
    index = 1
    options = True
    while index < len(words):
        word = words[index]
        if options and word == "--":
            options = False
        elif options and word in {"-b", "-B", "--reason"}:
            index += 1
            if index >= len(words):
                raise RuntimeError("worktree add 옵션 값이 누락되었습니다.")
        elif options and (word in flags or word.startswith(("--reason=", "--track="))
                          or len(word) > 2 and word.startswith(("-b", "-B"))):
            pass
        elif options and word.startswith("-"):
            raise RuntimeError(f"worktree add 옵션을 확인할 수 없습니다: {word}. 옵션과 경로를 명시하세요.")
        else:
            positionals.append(word)
        index += 1
    if len(positionals) not in {1, 2}:
        raise RuntimeError("worktree add의 새 경로와 선택적 commit을 명시하세요.")
    return destination(root, cwd, positionals[0])
