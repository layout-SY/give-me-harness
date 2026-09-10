"""도구 입력·경로 정규화와 관리 정책 대상 판정."""
from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any


_loader_path = Path(__file__).resolve().with_name("runtime_loader.py")
_loader = ModuleType("asan_runtime_loader")
_loader.__file__ = str(_loader_path)
exec(compile(_loader_path.read_bytes(), str(_loader_path), "exec"), _loader.__dict__)
load_runtime_module = _loader.load

_runtime_config = load_runtime_module("runtime_config")
BRANCH_WORKFLOW_SUFFIX = _runtime_config.BRANCH_WORKFLOW_SUFFIX
BROAD_MUTATION_PATTERN = _runtime_config.BROAD_MUTATION_PATTERN
BUILD_COMMAND = _runtime_config.BUILD_COMMAND
CENTRAL_ROOT = _runtime_config.CENTRAL_ROOT
DEV_COMMAND = _runtime_config.DEV_COMMAND
INJECT_BUNDLE_ROOT_ENV = _runtime_config.INJECT_BUNDLE_ROOT_ENV
INJECT_MODE_ENV = _runtime_config.INJECT_MODE_ENV
MANAGED_POLICY_ROOTS = _runtime_config.MANAGED_POLICY_ROOTS
NON_PERSISTENT_REDIRECT_TARGETS = _runtime_config.NON_PERSISTENT_REDIRECT_TARGETS
PACKAGE_BUILD_PATTERN = _runtime_config.PACKAGE_BUILD_PATTERN
PACKAGE_DEV_PATTERN = _runtime_config.PACKAGE_DEV_PATTERN
PATCH_PATH_PATTERN = _runtime_config.PATCH_PATH_PATTERN
PATH_KEYS = _runtime_config.PATH_KEYS
PYTHON_COMMAND_PATTERN = _runtime_config.PYTHON_COMMAND_PATTERN
SHELL_IN_PLACE_PATTERN = _runtime_config.SHELL_IN_PLACE_PATTERN
SHELL_MUTATION_PATTERN = _runtime_config.SHELL_MUTATION_PATTERN
SHELL_PREFIX_PATTERN = _runtime_config.SHELL_PREFIX_PATTERN
SHELL_RUNTIME_WRITE_PATTERN = _runtime_config.SHELL_RUNTIME_WRITE_PATTERN
SHELL_SEGMENT_PATTERN = _runtime_config.SHELL_SEGMENT_PATTERN
SHELL_TOOLS = _runtime_config.SHELL_TOOLS
STRUCTURED_MUTATION_TOOLS = _runtime_config.STRUCTURED_MUTATION_TOOLS
UNKNOWN_REDIRECT_TARGET = _runtime_config.UNKNOWN_REDIRECT_TARGET
branch_guard = _runtime_config.branch_guard

def read_event() -> dict[str, Any]:
    try:
        value = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError) as error:
        raise ValueError("hook 입력을 JSON으로 읽을 수 없습니다.") from error
    if not isinstance(value, dict):
        raise ValueError("hook 입력은 JSON object여야 합니다.")
    tool_input = value.get("tool_input")
    if normalized_tool_name(value) in SHELL_TOOLS and isinstance(tool_input, dict) and "cmd" in tool_input:
        command = tool_input["cmd"]
        if not isinstance(command, str) or ("command" in tool_input and tool_input["command"] != command):
            raise ValueError("shell 입력의 cmd와 command가 올바르지 않거나 서로 다릅니다.")
        value = {**value, "tool_input": {**tool_input, "command": command}}
    return value


def normalized_tool_name(event: dict[str, Any]) -> str:
    return (
        str(event.get("tool_name", ""))
        .rsplit(".", maxsplit=1)[-1]
        .casefold()
        .replace("-", "_")
    )


def repository_root(event: dict[str, Any]) -> Path:
    if branch_guard.SHARED_GIT_ACCESS:
        # 도구 cwd나 변경 가능한 shell 환경으로 세션 프로젝트를 재지정하지 않는다.
        project = _runtime_config.PROJECT_ROOT
        if not project.is_absolute() or not project.is_dir():
            raise ValueError("세션 프로젝트 경로가 유효하지 않습니다. 중앙 launcher로 시작하세요.")
        return project.resolve()
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


def runtime_policy_root() -> Path:
    """현재 guard가 로드된 중앙 inject bundle을 반환한다."""

    bundle = os.environ.get(INJECT_BUNDLE_ROOT_ENV, "").strip()
    if bundle:
        return Path(bundle).resolve()
    return Path(__file__).resolve().parents[2]


def repository_relative(root: Path, raw_path: str) -> str | None:
    if not raw_path.strip():
        return None
    candidate = Path(raw_path.strip())
    target = candidate if candidate.is_absolute() else root / candidate
    try:
        return target.resolve().relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        return None


def git_top_level(directory: Path) -> Path | None:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0 or not completed.stdout.strip():
        return None
    try:
        return Path(completed.stdout.strip()).resolve()
    except (OSError, RuntimeError):
        return None


def repository_target(
    session_root: Path,
    raw_path: str,
    base: Path | None = None,
) -> tuple[Path, str] | None:
    """새 파일 경로도 가장 가까운 기존 부모에서 소속 worktree를 찾는다."""

    if not raw_path.strip():
        return None
    try:
        candidate = Path(raw_path.strip()).expanduser()
        target = (candidate if candidate.is_absolute() else (base or session_root) / candidate).resolve()
    except (OSError, RuntimeError):
        return None
    probe = target if target.is_dir() else target.parent
    while not probe.exists() and probe != probe.parent:
        probe = probe.parent
    target_root = git_top_level(probe)
    if target_root is None or not branch_guard.same_git_repository(session_root, target_root):
        return None
    try:
        relative = target.relative_to(target_root).as_posix()
    except ValueError:
        return None
    return target_root, relative


def inject_mode() -> bool:
    return os.environ.get(INJECT_MODE_ENV) == "inject"


def injected_policy_roots() -> tuple[Path, ...]:
    if not inject_mode():
        return ()
    roots: list[Path] = []
    if CENTRAL_ROOT.is_absolute():
        roots.append(CENTRAL_ROOT.resolve())
    bundle_value = os.environ.get(INJECT_BUNDLE_ROOT_ENV, "").strip()
    if bundle_value and Path(bundle_value).is_absolute():
        roots.append(Path(bundle_value).resolve())
    return tuple(dict.fromkeys(roots))


def injected_policy_target(root: Path, raw_path: str) -> Path | None:
    if not raw_path.strip():
        return None
    candidate = Path(raw_path.strip())
    try:
        target = (candidate if candidate.is_absolute() else root / candidate).resolve()
    except OSError:
        return None
    for policy_root in injected_policy_roots():
        try:
            target.relative_to(policy_root)
        except ValueError:
            continue
        return target
    return None


def shell_working_directory(root: Path, tool_input: dict[str, Any]) -> Path:
    value = tool_input.get("workdir")
    if not isinstance(value, str) or not value.strip():
        return root.resolve()
    candidate = Path(value.strip())
    try:
        return (candidate if candidate.is_absolute() else root / candidate).resolve()
    except OSError:
        return root.resolve()


def resolved_shell_target(
    root: Path,
    tool_input: dict[str, Any],
    raw_target: str,
) -> Path | None:
    if raw_target == UNKNOWN_REDIRECT_TARGET or any(
        marker in raw_target for marker in ("$", "`", "\n", "\r")
    ):
        return None
    try:
        candidate = Path(raw_target).expanduser()
        base = shell_working_directory(root, tool_input)
        return (candidate if candidate.is_absolute() else base / candidate).resolve()
    except (OSError, RuntimeError):
        return None


def relative_target(root: Path, target: Path) -> str | None:
    try:
        return target.relative_to(root.resolve()).as_posix()
    except ValueError:
        return None


def target_in_injected_policy(target: Path) -> Path | None:
    for policy_root in injected_policy_roots():
        try:
            target.relative_to(policy_root)
        except ValueError:
            continue
        return target
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


def _shell_word(command: str, start: int) -> tuple[str, int]:
    index = start
    quote = ""
    escaped = False
    while index < len(command):
        character = command[index]
        if escaped:
            escaped = False
            index += 1
            continue
        if character == "\\" and quote != "'":
            escaped = True
            index += 1
            continue
        if quote:
            if character == quote:
                quote = ""
            index += 1
            continue
        if character in {"'", '"'}:
            quote = character
            index += 1
            continue
        if character.isspace() or character in ";|&":
            break
        index += 1

    raw = command[start:index]
    if not raw:
        return "", index
    try:
        tokens = shlex.split(raw, posix=True)
    except ValueError:
        return UNKNOWN_REDIRECT_TARGET, index
    return (tokens[0] if len(tokens) == 1 else UNKNOWN_REDIRECT_TARGET), index


def shell_redirect_targets(command: str) -> tuple[str, ...]:
    """셸의 지속 파일 쓰기 리다이렉션 목적지만 반환한다."""

    targets: list[str] = []
    index = 0
    quote = ""
    escaped = False
    while index < len(command):
        character = command[index]
        if escaped:
            escaped = False
            index += 1
            continue
        if character == "\\" and quote != "'":
            escaped = True
            index += 1
            continue
        if quote:
            if character == quote:
                quote = ""
            index += 1
            continue
        if character in {"'", '"'}:
            quote = character
            index += 1
            continue
        if character != ">":
            index += 1
            continue

        target_start = index + 1
        if target_start < len(command) and command[target_start] == ">":
            target_start += 1
        if target_start < len(command) and command[target_start] == "|":
            target_start += 1
        while target_start < len(command) and command[target_start] in " \t":
            target_start += 1

        if target_start < len(command) and command[target_start] == "(":
            index = target_start + 1
            continue
        if target_start < len(command) and command[target_start] == "&":
            descriptor_end = target_start + 1
            while descriptor_end < len(command) and command[descriptor_end].isdigit():
                descriptor_end += 1
            if descriptor_end == target_start + 1 and descriptor_end < len(command):
                descriptor_end += int(command[descriptor_end] == "-")
            if descriptor_end > target_start + 1 and (
                descriptor_end == len(command)
                or command[descriptor_end].isspace()
                or command[descriptor_end] in ";|&<>"
            ):
                index = descriptor_end
                continue
            target_start += 1
            while target_start < len(command) and command[target_start] in " \t":
                target_start += 1

        target, target_end = _shell_word(command, target_start)
        if not target:
            targets.append(UNKNOWN_REDIRECT_TARGET)
        elif not (
            target in NON_PERSISTENT_REDIRECT_TARGETS
            or target.startswith("/dev/fd/")
        ):
            targets.append(target)
        index = max(target_end, target_start + 1)
    return tuple(targets)


def has_non_redirect_shell_mutation(command: str) -> bool:
    return bool(
        SHELL_MUTATION_PATTERN.search(command)
        or SHELL_IN_PLACE_PATTERN.search(command)
        or SHELL_RUNTIME_WRITE_PATTERN.search(command)
        or BROAD_MUTATION_PATTERN.search(command)
    )


def has_non_git_shell_mutation(command: str) -> bool:
    return bool(
        SHELL_MUTATION_PATTERN.search(command)
        or SHELL_IN_PLACE_PATTERN.search(command)
        or SHELL_RUNTIME_WRITE_PATTERN.search(command)
    )


def looks_like_shell_mutation(command: str) -> bool:
    return has_non_redirect_shell_mutation(command) or bool(shell_redirect_targets(command))


def trusted_branch_workflow_invocation(command: str, root: Path | None = None) -> bool:
    """inject 스냅샷의 승인 도구를 단일 Python 명령으로 실행하는지 확인한다."""

    if SHELL_SEGMENT_PATTERN.search(command) or shell_redirect_targets(command):
        return False
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        return False
    if not tokens:
        return False

    index = 0
    if tokens[index] == "env":
        index += 1
    while index < len(tokens) and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", tokens[index]):
        index += 1
    if index >= len(tokens) or PYTHON_COMMAND_PATTERN.fullmatch(Path(tokens[index]).name) is None:
        return False
    index += 1
    while index < len(tokens) and tokens[index] in {"-B", "-E", "-I", "-s", "-S", "-u"}:
        index += 1
    if index + 1 >= len(tokens):
        return False

    script = Path(tokens[index])
    if not script.is_absolute():
        return False
    try:
        resolved = script.resolve()
    except OSError:
        return False
    if tuple(resolved.parts[-len(BRANCH_WORKFLOW_SUFFIX):]) != BRANCH_WORKFLOW_SUFFIX:
        return False
    if not resolved.is_file():
        return False
    if tokens[index + 1] not in {
        "proposal",
        "create",
        "scope-proposal",
        "update-scope",
        "finish-proposal",
        "finish",
        "verify",
        "close",
        "preserve",
        "resume",
        "context",
    }:
        return False
    if inject_mode():
        return any(
            resolved == policy_root or resolved.is_relative_to(policy_root)
            for policy_root in injected_policy_roots()
        )
    if root is None:
        return False
    expected_roots = tuple(dict.fromkeys((root.resolve(), runtime_policy_root().resolve())))
    for expected_root in expected_roots:
        expected = expected_root / ".agent-policy/common" / Path(*BRANCH_WORKFLOW_SUFFIX)
        try:
            if resolved == expected.resolve():
                return True
        except OSError:
            continue
    return False


def trusted_branch_workflow_action(command: str, root: Path | None = None) -> str:
    arguments = trusted_branch_workflow_arguments(command, root)
    return arguments[0] if arguments else ""


def unsupported_workflow_invocation(command: str, root: Path) -> bool:
    """복합 shell 안의 workflow를 일반 읽기 명령으로 잘못 통과시키지 않는다."""
    if "branch_workflow.py" not in command or trusted_branch_workflow_invocation(command, root):
        return False
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()")
        lexer.whitespace_split = True
        return any(PYTHON_COMMAND_PATTERN.fullmatch(Path(token).name) for token in lexer)
    except ValueError:
        return True


def trusted_branch_workflow_arguments(
    command: str,
    root: Path | None = None,
) -> tuple[str, ...]:
    if not trusted_branch_workflow_invocation(command, root):
        return ()
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        return ()
    for index, token in enumerate(tokens[:-1]):
        if tuple(Path(token).parts[-len(BRANCH_WORKFLOW_SUFFIX):]) == BRANCH_WORKFLOW_SUFFIX:
            return tuple(tokens[index + 1:])
    return ()


def branch_workflow_option(arguments: tuple[str, ...], name: str) -> str:
    for index, value in enumerate(arguments):
        if value == name:
            return arguments[index + 1] if index + 1 < len(arguments) else ""
        if value.startswith(f"{name}="):
            return value.removeprefix(f"{name}=")
    return ""


def branch_workflow_contract(
    event: dict[str, Any],
    root: Path,
    arguments: tuple[str, ...],
) -> dict[str, Any]:
    raw_path = branch_workflow_option(arguments, "--proposal-file")
    if not raw_path:
        return {}
    candidate = Path(raw_path).expanduser()
    source = candidate if candidate.is_absolute() else shell_working_directory(root, event.get("tool_input", {})) / candidate
    try:
        value = json.loads(source.resolve().read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def shell_mentions_managed(command: str, files: set[str], roots: tuple[str, ...]) -> list[str]:
    if not branch_guard.SHARED_GIT_ACCESS and BROAD_MUTATION_PATTERN.search(command):
        return ["<repository-wide mutation>"]
    candidates = sorted(files | {root.rstrip("/") for root in roots}, key=len, reverse=True)
    return [candidate for candidate in candidates if candidate and candidate in command]


def denied_targets(event: dict[str, Any], root: Path) -> list[str]:
    files: set[str] = set()
    roots = MANAGED_POLICY_ROOTS
    tool_name = normalized_tool_name(event)
    raw_input = event.get("tool_input")
    tool_input = raw_input if isinstance(raw_input, dict) else {}
    structured_mutation = tool_name in STRUCTURED_MUTATION_TOOLS
    raw_targets = structured_targets(tool_input) if structured_mutation else []

    command_value = tool_input.get("command")
    command = command_value if isinstance(command_value, str) else ""
    shell_tool = tool_name in SHELL_TOOLS
    trusted_workflow = bool(
        shell_tool
        and command
        and trusted_branch_workflow_invocation(command, root)
    )
    if tool_name in {"apply_patch", "patch"}:
        raw_targets.extend(patch_targets(command))

    denied: set[str] = set()
    for raw_path in raw_targets:
        context = repository_target(root, raw_path)
        relative = context[1] if context is not None else repository_relative(root, raw_path)
        if relative is not None and is_managed(relative, files, roots):
            denied.add(relative)

    if shell_tool and command and not trusted_workflow:
        non_redirect_mutation = has_non_redirect_shell_mutation(command)
        redirect_targets = shell_redirect_targets(command)
        if non_redirect_mutation:
            denied.update(shell_mentions_managed(command, files, roots))
            workdir = tool_input.get("workdir")
            if isinstance(workdir, str):
                raw_targets.append(workdir)
        for raw_target in redirect_targets:
            target = resolved_shell_target(root, tool_input, raw_target)
            if target is None:
                denied.update(shell_mentions_managed(command, files, roots))
                workdir = tool_input.get("workdir")
                if isinstance(workdir, str):
                    raw_targets.append(workdir)
                continue
            context = repository_target(root, str(target))
            relative = context[1] if context is not None else relative_target(root, target)
            if relative is not None and is_managed(relative, files, roots):
                denied.add(relative)
            if injected_target := target_in_injected_policy(target):
                denied.add(str(injected_target))

    for raw_path in raw_targets:
        if target := injected_policy_target(root, raw_path):
            denied.add(str(target))
    if command and has_non_redirect_shell_mutation(command) and not trusted_workflow:
        for policy_root in injected_policy_roots():
            if str(policy_root) in command:
                denied.add(str(policy_root))
    return sorted(denied)


def denial_message(targets: list[str]) -> str:
    rendered_targets = ", ".join(targets)
    return (
        "중앙 시스템 프롬프트는 소비자 프로젝트에서 수정할 수 없습니다.\n"
        f"대상: {rendered_targets}\n"
        f"중앙 프로젝트: {CENTRAL_ROOT}\n"
        "중앙 프로젝트에서 원본과 회귀 테스트를 수정한 뒤 audit을 통과시키고, "
        "현재 작업을 handoff한 다음 중앙 launcher로 새 inject 세션을 시작해 주세요."
    )


def shell_segments(command: str) -> tuple[str, ...]:
    return tuple(
        normalized
        for raw_segment in SHELL_SEGMENT_PATTERN.split(command)
        if (normalized := " ".join(raw_segment.strip(" ()\t").casefold().split()))
    )


def strip_shell_prefix(segment: str) -> str:
    return SHELL_PREFIX_PATTERN.sub("", segment, count=1)


def command_matches(segment: str, expected: str) -> bool:
    normalized = " ".join(expected.casefold().split())
    return bool(normalized) and (segment == normalized or segment.startswith(f"{normalized} "))


def protected_operation_categories(command: str) -> tuple[str, ...]:
    categories: set[str] = set()
    git_commands = branch_guard._git_commands(command)
    if git_commands and (branch_guard.SHARED_GIT_ACCESS or git_commands != (("<unparsed>",),)) and git_command_mutates(command):
        categories.add("Git")
    for raw_segment in shell_segments(command):
        segment = strip_shell_prefix(raw_segment)
        is_build = bool(
            command_matches(segment, BUILD_COMMAND) or PACKAGE_BUILD_PATTERN.match(segment)
        )
        if is_build and not branch_guard.SHARED_GIT_ACCESS:
            categories.add("빌드")
        if not is_build and (
            command_matches(segment, DEV_COMMAND) or PACKAGE_DEV_PATTERN.match(segment)
        ):
            categories.add("개발 서버")
    return tuple(sorted(categories))


def event_session_id(event: dict[str, Any]) -> str:
    for key in ("session_id", "sessionID"):
        value = event.get(key)
        if isinstance(value, str) and value:
            return value
    return "missing-session-id"


def git_command_mutates(command: str) -> bool:
    return branch_guard.git_command_mutates(command)
