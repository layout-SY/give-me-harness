"""세션 프로젝트에 고정된 명령 경계. 연결 worktree는 동일 Git 저장소다."""
from __future__ import annotations

from pathlib import Path
from types import ModuleType
from urllib.parse import unquote, urlparse

_loader_path = Path(__file__).resolve().with_name("runtime_loader.py")
_loader = ModuleType("asan_boundary_loader")
_loader.__file__ = str(_loader_path)
exec(compile(_loader_path.read_bytes(), str(_loader_path), "exec"), _loader.__dict__)
config = _loader.load("runtime_config")
branch = config.branch_guard


def denial(target: object) -> str:
    return f"현재 세션 프로젝트 밖의 명령 대상은 허용하지 않습니다: {target}. 해당 프로젝트의 별도 세션을 사용하세요."


def directory_denial(root: Path, target: Path) -> str | None:
    if not target.is_dir() or not branch.same_git_repository(root, target):
        return denial(target)
    return None


def resolve(base: Path, raw: str) -> Path | None:
    if not raw or any(char in raw for char in "$`*\0\n\r"):
        return None
    if raw.startswith("file://"):
        uri = urlparse(raw)
        if uri.netloc not in {"", "localhost"}:
            return None
        raw = unquote(uri.path)
    return branch._resolved_option_path(base, raw)


def foreign_repository(root: Path, target: Path) -> bool:
    probe = target if target.is_dir() else target.parent
    while not probe.exists() and probe != probe.parent:
        probe = probe.parent
    common = branch.git_common_directory(probe)
    return common is not None and common != branch.git_common_directory(root)


def command_denial(root: Path, command: str, cwd: Path, depth: int = 0) -> str | None:
    problem = directory_denial(root, cwd)
    if problem:
        return problem
    contexts = branch.shell_command_contexts(command, cwd)
    if contexts is None or depth > 3:
        return "프로젝트 명령의 실행 위치를 확인할 수 없습니다. 리터럴 경로와 workdir 또는 git -C를 명시하세요."
    for location, words in contexts:
        problem = directory_denial(root, location)
        if problem:
            return problem
        executable = Path(words[0]).name
        if executable in {"sh", "bash", "zsh", "dash"}:
            for index, word in enumerate(words[1:], 1):
                if word.startswith("-") and not word.startswith("--") and "c" in word:
                    if index + 1 >= len(words):
                        return denial("shell 실행 위치 미확인")
                    problem = command_denial(root, words[index + 1], location, depth + 1)
                    if problem:
                        return problem
        options = {
            "npm": {"--prefix"}, "npx": {"--prefix"}, "pnpm": {"-C", "--dir", "--prefix"},
            "yarn": {"--cwd"}, "bun": {"--cwd"}, "make": {"-C", "--directory"},
        }.get(executable, set())
        for index, word in enumerate(words[1:], 1):
            option = word.split("=", 1)[0]
            if option in options:
                raw = word.split("=", 1)[1] if "=" in word else words[index + 1] if index + 1 < len(words) else ""
                target = resolve(location, raw)
                if target is None:
                    return denial("명령 실행 경로 미확인")
                problem = directory_denial(root, target)
                if problem:
                    return problem
        # 절대·상대 경로 및 file://로 다른 저장소를 명시하는 경우도 검사한다.
        # 실행 파일·중앙 스킬 문서 같은 공용 자산의 위치를 worktree로 오인하지 않는다.
        for word in words:
            raw = word.split("=", 1)[1] if "=" in word else word
            if not raw.startswith(("/", "./", "../", "~/", "file://")) and (
                    ":" in raw or ("/" not in raw and not (location / raw).exists())):
                continue
            target = resolve(location, raw)
            if target is None:
                return denial("명령 대상 경로 미확인")
            if foreign_repository(root, target):
                if (executable in {"cat", "head", "tail", "sed", "rg", "ls"}
                        and config.CENTRAL_ROOT.is_absolute() and target.is_relative_to(config.CENTRAL_ROOT.resolve())):
                    continue
                return f"현재 프로젝트와 다른 Git 저장소의 명령 대상입니다: {target}. 해당 프로젝트의 별도 세션을 사용하세요."
    return None


def git_arguments_denial(root: Path, invocation) -> str | None:
    args = invocation.arguments
    if not args:
        return None
    if branch._output(invocation.root, "config", "--get", f"alias.{args[0]}"):
        return denial("Git alias의 실제 실행 대상; 원래 Git 명령을 명시하세요")
    if args[0] in {"clone", "init"}:
        return denial("별도 저장소 생성; 같은 프로젝트의 git worktree add를 사용하세요")
    if args[0] == "config" and any(value in {"--global", "--system"} for value in args[1:]):
        return denial("프로젝트 외 Git 설정")
    if args[0] in {"push", "pull", "fetch", "ls-remote"}:
        # 이름으로 지정한 remote도 로컬 다른 프로젝트를 가리킬 수 있다.
        names = [value for value in args[1:] if not value.startswith("-")]
        names.extend(value.split("=", 1)[1] for value in args[1:] if value.startswith("--repo="))
        if not names:
            current = branch.current_branch(invocation.root)
            keys = ([f"branch.{current}.pushRemote", "remote.pushDefault"] if args[0] == "push" else [])
            keys.append(f"branch.{current}.remote")
            names = [next((value for key in keys if (value := branch._output(invocation.root, "config", "--get", key))), "origin")]
        if "--all" in args and args[0] == "fetch":
            names = branch._output(invocation.root, "remote").splitlines()
        for name in names:
            options = ("--push",) if args[0] == "push" else ()
            urls = branch._output(invocation.root, "remote", "get-url", *options, "--all", name).splitlines()
            for value in urls or [name]:
                if ":" in value and not value.startswith("file://"):
                    continue  # HTTPS/SSH 등 프로젝트 원격 사용은 기존 승인 계약을 따른다.
                target = resolve(invocation.root, value)
                if target is not None and foreign_repository(root, target):
                    return denial(target)
    return None
