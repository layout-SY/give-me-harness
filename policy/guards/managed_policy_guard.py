#!/usr/bin/env python3
"""중앙 inject 정책, 승인 범위와 보호 명령을 검사한다."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time
import unicodedata
from pathlib import Path
from types import ModuleType
from typing import Any, Final


def load_branch_guard() -> ModuleType:
    source = Path(__file__).resolve().with_name("branch_guard.py")
    module = ModuleType("branch_guard")
    module.__file__ = str(source)
    exec(compile(source.read_bytes(), str(source), "exec"), module.__dict__)
    return module


branch_guard = load_branch_guard()

CENTRAL_ROOT: Final = Path("{{CENTRAL_ROOT}}")
DEV_COMMAND: Final = "{{DEV_COMMAND}}"
BUILD_COMMAND: Final = "{{BUILD_COMMAND}}"
COMMAND_APPROVAL_PHRASE: Final = "명령 실행 승인"
APPROVAL_MAX_AGE_SECONDS: Final = 30 * 60
IMPLEMENTATION_APPROVAL_PHRASES: Final = frozenset(
    {
        "진행",
        "진행해",
        "진행해줘",
        "그대로 진행",
        "그대로 진행해",
        "이대로 진행",
        "이대로 진행해",
        "계획대로 진행",
        "계획대로 진행해",
        "작업 진행",
        "작업 진행해",
        "작업 진행해줘",
        "오케이 작업 진행",
        "오케이 이대로 진행",
        "좋아 진행",
        "승인",
        "승인합니다",
        "전부 승인",
        "모두 승인",
        "proceed",
        "approved",
        "go ahead",
    }
)
EMBEDDED_IMPLEMENTATION_APPROVAL_PHRASES: Final = frozenset(
    IMPLEMENTATION_APPROVAL_PHRASES - {"진행", "승인", "approved"}
)
APPROVAL_WORD_PATTERN: Final = re.compile(r"(?:승인|진행|proceed|approved|go\s+ahead)", re.I)
DENIAL_WORD_PATTERN: Final = re.compile(r"(?:취소|거부|보류|중단|하지\s*마|don't|do\s+not|cancel)", re.I)
CONTRACT_SHA256_PATTERN: Final = re.compile(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])", re.I)
HOST_ARTIFACT_SESSIONS_PREFIXES: Final = {
    host: f"{root.rstrip('/')}/"
    for host, root in branch_guard.HOST_ARTIFACT_SESSION_ROOTS.items()
}
ARTIFACT_SESSIONS_PREFIXES: Final = tuple(HOST_ARTIFACT_SESSIONS_PREFIXES.values())
SESSION_DIR_ENV: Final = "ASAN_SESSION_DIR"
TASK_ENV: Final = "ASAN_AGENT_POLICY_TASK"
ARTIFACT_RESPONSIBILITY_ENV: Final = "ASAN_ARTIFACT_RESPONSIBILITY"
INJECT_MODE_ENV: Final = "ASAN_AGENT_POLICY_MODE"
INJECT_PROJECT_ENV: Final = "ASAN_AGENT_POLICY_PROJECT"
INJECT_BUNDLE_ROOT_ENV: Final = "ASAN_AGENT_POLICY_BUNDLE_ROOT"
INJECT_ROLE_ENV: Final = "ASAN_AGENT_POLICY_ROLE"
REQUIRED_ARTIFACTS: Final = branch_guard.REQUIRED_ARTIFACTS
HANDOFF_ARTIFACT: Final = branch_guard.HANDOFF_ARTIFACT
UNKNOWN_ARTIFACT_DIRECTORY: Final = branch_guard.UNKNOWN_ARTIFACT_DIRECTORY
MANAGED_POLICY_ROOTS: Final = (
    "AGENTS.md",
    "CLAUDE.md",
    ".agent-policy/manifest.json",
    ".agent-policy/common/",
    ".agent-policy/runtime/",
    ".agents/skills/",
    ".claude/agents/",
    ".claude/hooks/",
    ".claude/settings.json",
    ".claude/skills/",
    ".claude/templates/",
    ".codex/agents/",
    ".codex/config.toml",
    ".codex/hooks.json",
    ".codex/hooks/",
    ".codex/templates/",
    ".opencode/agent/",
    ".opencode/plugins/",
    ".opencode/templates/",
    "opencode.json",
)
PATH_KEYS: Final = ("file_path", "filePath", "path", "paths", "notebook_path")
PATCH_PATH_PATTERN: Final = re.compile(
    r"^\*\*\* (?:(?:Add|Update|Delete) File|Move to): (.+)$", re.MULTILINE
)
SHELL_MUTATION_PATTERN: Final = re.compile(
    r"(?:^|[;&|]\s*)(?:rm|mv|cp|install|touch|mkdir|rmdir|truncate|tee|dd|ln|chmod|chown|patch)\b"
)
SHELL_IN_PLACE_PATTERN: Final = re.compile(r"\b(?:sed|perl)\b[^\n]*(?:\s-i(?:\s|$)|--in-place)")
SHELL_RUNTIME_WRITE_PATTERN: Final = re.compile(
    r"\b(?:python\d*|node|ruby)\b[^\n]*(?:writeFile|write_text|write_bytes|unlink|rename|replace|open\s*\([^\n]*['\"](?:w|a|x))"
)
BROAD_MUTATION_PATTERN: Final = re.compile(
    r"(?:git\s+(?:reset\s+--hard|clean\b|checkout\s+(?:--\s+)?\.|restore\s+\.)|rm\s+[^\n]*(?:\s|^)(?:\.|\./)(?:\s|$))"
)
SHELL_SEGMENT_PATTERN: Final = re.compile(r"(?:&&|\|\||[;|\n])")
SHELL_PREFIX_PATTERN: Final = re.compile(
    r"^(?:(?:[A-Za-z_][A-Za-z0-9_]*=\S+|command|env|sudo)\s+)*"
)
PACKAGE_BUILD_PATTERN: Final = re.compile(
    r"^(?:(?:npm|pnpm|yarn|bun)\s+(?:run\s+)?build(?:[:\s]|$)|"
    r"(?:npx\s+)?vite\s+build(?:\s|$)|tsc\s+-b(?:\s|$))"
)
PACKAGE_DEV_PATTERN: Final = re.compile(
    r"^(?:(?:npm|pnpm|yarn|bun)\s+(?:run\s+)?(?:dev|start|preview)(?:[:\s]|$)|"
    r"npm\s+start(?:\s|$)|(?:npx\s+)?vite(?:\s|$))"
)
BRANCH_WORKFLOW_SUFFIX: Final = (
    "skills",
    "policy",
    "git-branch-strategy",
    "scripts",
    "branch_workflow.py",
)
PYTHON_COMMAND_PATTERN: Final = re.compile(r"^python\d*(?:\.\d+)?$")
UNKNOWN_REDIRECT_TARGET: Final = "<unresolved-shell-redirect>"
NON_PERSISTENT_REDIRECT_TARGETS: Final = frozenset(
    {
        "/dev/null",
        "/dev/stderr",
        "/dev/stdout",
        "/dev/tty",
    }
)
TABLE_SEPARATOR: Final = re.compile(r"\|\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?")
PORTFOLIO_CASE: Final = re.compile(r"^##\s+사례\b.*$", re.MULTILINE)
PORTFOLIO_HEADINGS: Final = (
    "문제 상황",
    "고민과 선택",
    "적용",
    "사용 기술과 구체적 목적",
    "결과",
    "이력서·포트폴리오 문구",
)
PORTFOLIO_FIELDS: Final = ("작업 유형", "관련 도메인/서비스", "문제 출처")
SESSION_NAME_PATTERN: Final = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{1,127}")
READ_EVIDENCE_TOOLS: Final = frozenset(
    {"glob", "grep", "read", "search", "skill", "webfetch", "websearch"}
)
STRUCTURED_MUTATION_TOOLS: Final = frozenset(
    {"apply_patch", "edit", "multiedit", "notebookedit", "patch", "write"}
)
SHELL_TOOLS: Final = frozenset({"bash", "exec", "exec_command", "shell"})


def read_event() -> dict[str, Any]:
    try:
        value = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return {}
    return value if isinstance(value, dict) else {}


def normalized_tool_name(event: dict[str, Any]) -> str:
    return (
        str(event.get("tool_name", ""))
        .rsplit(".", maxsplit=1)[-1]
        .casefold()
        .replace("-", "_")
    )


def repository_root(event: dict[str, Any]) -> Path:
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


def branch_workflow_integrator_denial(
    event: dict[str, Any],
    root: Path,
    host: str,
    command: str,
) -> str | None:
    """승인 workflow도 계약에 기록된 단일 Git 통합 담당자만 실행하게 한다."""

    arguments = trusted_branch_workflow_arguments(command, root)
    if not arguments:
        return None
    action = arguments[0]
    assignment_root = active_assignment_branch(event, root, host)
    if action == "create":
        contract = branch_workflow_contract(event, root, arguments)
        requested_branch = contract.get("branch")
        parent_value = contract.get("parent")
        parent = parent_value if isinstance(parent_value, str) else ""
        if assignment_root:
            if not branch_guard.assignment_allows_branch_mutation(
                root,
                assignment_root,
                parent,
            ):
                return (
                    f"현재 세션의 assignment 권한 root({assignment_root}) 밖에서 "
                    f"task({requested_branch or '확인 불가'})를 생성할 수 없습니다.\n"
                    f"  요청 parent: {parent or '확인 불가'}"
                )
            if branch_guard.task_state(root, parent) != "ACTIVE":
                return f"ACTIVE 상태의 권한 계보 branch에서만 자식 task를 생성할 수 있습니다: {parent}"
        integrator = contract.get("git_integrator")
        if not isinstance(integrator, str) or not integrator:
            return "branch create proposal에서 Git 통합 담당자를 확인할 수 없습니다."
        if integrator == host:
            return None
        if integrator == "user":
            return "이 branch 계약의 Git 통합 담당자는 사용자입니다. AI 호스트가 create를 실행할 수 없습니다."
        return (
            f"이 branch 계약의 Git 통합 담당자는 {integrator}입니다. "
            f"현재 호스트({host})는 create를 실행할 수 없습니다."
        )
    if action in {"finish", "verify", "close"}:
        contract = branch_workflow_contract(event, root, arguments)
        source_value = contract.get("source")
        source = source_value if isinstance(source_value, str) else ""
    elif action == "update-scope":
        contract = branch_workflow_contract(event, root, arguments)
        source_value = contract.get("branch")
        source = source_value if isinstance(source_value, str) else ""
    elif action in {"preserve", "resume"}:
        source = branch_guard.current_branch(root)
    else:
        return None
    if not source:
        return f"branch_workflow.py {action}의 source task를 확인할 수 없습니다."
    if assignment_root and not branch_guard.assignment_allows_branch_mutation(
        root,
        assignment_root,
        source,
    ):
        return (
            f"현재 세션의 assignment 권한 root({assignment_root}) 밖의 "
            f"task({source})에 {action}을 실행할 수 없습니다."
        )
    return branch_guard.git_integrator_denial(root, source, host)


def shell_mentions_managed(command: str, files: set[str], roots: tuple[str, ...]) -> list[str]:
    if BROAD_MUTATION_PATTERN.search(command):
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


def branch_denial(event: dict[str, Any], root: Path, host: str) -> str | None:
    tool_name = normalized_tool_name(event)
    raw_input = event.get("tool_input")
    tool_input = raw_input if isinstance(raw_input, dict) else {}
    command_value = tool_input.get("command")
    command = command_value if isinstance(command_value, str) else ""
    shell_cwd = shell_working_directory(root, tool_input)
    shell_root = git_top_level(shell_cwd)
    if shell_root is None or not branch_guard.same_git_repository(root, shell_root):
        shell_root = root
    if command and trusted_branch_workflow_invocation(command, root):
        return branch_workflow_integrator_denial(event, shell_root, host, command)

    raw_targets = structured_targets(tool_input)
    if tool_name in {"apply_patch", "patch"}:
        raw_targets.extend(patch_targets(command))
    target_contexts: list[tuple[Path, str]] = []
    for raw_target in raw_targets:
        context = repository_target(root, raw_target)
        if context is None:
            return (
                "구조화된 변경 대상이 현재 소비자 Git 저장소의 승인된 worktree에 속하지 않습니다: "
                f"{raw_target}"
            )
        target_contexts.append(context)
    edit_tool = tool_name in STRUCTURED_MUTATION_TOOLS
    shell_tool = tool_name in SHELL_TOOLS
    if not edit_tool and not shell_tool:
        return None
    if edit_tool and target_contexts and all(
        relative.startswith(ARTIFACT_SESSIONS_PREFIXES)
        for _, relative in target_contexts
    ):
        # bind_artifact_session이 바로 앞에서 host·session·layout·assignment 귀속을
        # 검증했다. 진단·handoff 문서는 손상된 branch 계약을 복구하는 데도 필요하므로
        # artifact-only 구조화 쓰기를 source branch 유효성 검사와 결합하지 않는다.
        return None
    if shell_tool:
        for raw_target in shell_redirect_targets(command):
            target = resolved_shell_target(root, tool_input, raw_target)
            if target is None:
                return "shell redirect 대상을 안전하게 해석할 수 없어 실행을 차단했습니다."
            context = repository_target(root, str(target))
            if context is not None:
                target_contexts.append(context)
        if has_non_git_shell_mutation(command):
            return (
                "shell 명령의 비구조적 파일 변경은 branch scope와 소유권을 안전하게 확인할 수 없습니다. "
                "파일 경로를 구조적으로 전달하는 Edit/Write/apply_patch 도구를 사용하세요."
            )
        denial = branch_guard.command_denial(
            root,
            command,
            host=host,
            execution_cwd=shell_cwd,
            expected_branch=active_assignment_branch(event, root, host),
        )
        if denial is not None:
            return denial
    grouped: dict[Path, list[str]] = {}
    for target_root, relative in target_contexts:
        grouped.setdefault(target_root, []).append(relative)
    expected_branch = active_assignment_branch(event, root, host)
    for target_root, relatives in grouped.items():
        actual_branch = branch_guard.current_branch(target_root)
        if expected_branch and not branch_guard.assignment_allows_branch_mutation(
            target_root,
            expected_branch,
            actual_branch,
        ):
            contract_denial = branch_guard.active_branch_denial(
                target_root,
                tuple(dict.fromkeys(relatives)),
                host=host,
            )
            if contract_denial is not None:
                return contract_denial
            return (
                "현재 세션의 assignment 권한 계보와 구조화된 변경 대상 branch가 다릅니다.\n"
                f"  권한 root: {expected_branch}\n"
                f"  변경 대상: {actual_branch or 'detached HEAD'} ({target_root})"
            )
        denial = branch_guard.active_branch_denial(
            target_root,
            tuple(dict.fromkeys(relatives)),
            host=host,
        )
        if denial is not None:
            return denial
    return None


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
    if git_commands and git_commands != (("<unparsed>",),) and git_command_mutates(command):
        categories.add("Git")
    for raw_segment in shell_segments(command):
        segment = strip_shell_prefix(raw_segment)
        is_build = bool(
            command_matches(segment, BUILD_COMMAND) or PACKAGE_BUILD_PATTERN.match(segment)
        )
        if is_build:
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


def session_binding_path(event: dict[str, Any], root: Path, host: str) -> Path | None:
    session = event_session_id(event)
    if session == "missing-session-id":
        return None
    repository_identity = branch_guard.git_common_directory(root) or root.resolve()
    identity = f"{repository_identity}\0{host}\0{session}"
    digest = hashlib.sha256(identity.encode()).hexdigest()
    state_root = Path(tempfile.gettempdir()) / "asan-agent-policy-session-bindings"
    state_root.mkdir(mode=0o700, parents=True, exist_ok=True)
    return state_root / f"{digest}.txt"


def artifact_sessions_prefix(host: str) -> str:
    return HOST_ARTIFACT_SESSIONS_PREFIXES.get(
        host,
        HOST_ARTIFACT_SESSIONS_PREFIXES["unknown"],
    )


def artifact_session_directory(root: Path, raw_path: str, host: str) -> Path | None:
    prefix = artifact_sessions_prefix(host)
    relative = repository_relative(root, raw_path)
    if relative is None or not relative.startswith(prefix):
        return None
    remainder = relative.removeprefix(prefix)
    parts = Path(remainder).parts
    if len(parts) < 2 or SESSION_NAME_PATTERN.fullmatch(parts[0]) is None:
        return None
    candidate = root / prefix / parts[0]
    try:
        candidate.resolve().relative_to((root / prefix).resolve())
    except (OSError, ValueError):
        return None
    return candidate


def artifact_layout_denial(root: Path, raw_path: str, host: str) -> str | None:
    """알려진 문서는 session root, 그 외 문서는 unknown/ 아래에만 둔다."""

    prefix = artifact_sessions_prefix(host)
    relative = repository_relative(root, raw_path)
    if relative is None or not relative.startswith(prefix):
        return None
    parts = Path(relative.removeprefix(prefix)).parts
    if len(parts) < 2 or SESSION_NAME_PATTERN.fullmatch(parts[0]) is None:
        return f"세션 산출물 경로가 올바르지 않습니다: {relative}"
    artifact_parts = parts[1:]
    known = {*REQUIRED_ARTIFACTS, HANDOFF_ARTIFACT}
    if len(artifact_parts) == 1 and artifact_parts[0] in known:
        return None
    if len(artifact_parts) >= 2 and artifact_parts[0] == UNKNOWN_ARTIFACT_DIRECTORY:
        return None
    return (
        f"정의되지 않은 산출물은 현재 세션의 {UNKNOWN_ARTIFACT_DIRECTORY}/ 아래에 작성해야 합니다: "
        f"{relative}"
    )


def declared_session_directory(root: Path, host: str) -> Path | None:
    prefix = artifact_sessions_prefix(host)
    value = os.environ.get(SESSION_DIR_ENV, "").strip()
    if not value:
        return None
    candidate = Path(value)
    target = candidate if candidate.is_absolute() else root / candidate
    try:
        relative = target.resolve().relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        return None
    if not relative.startswith(prefix):
        return None
    remainder = relative.removeprefix(prefix)
    parts = Path(remainder).parts
    if len(parts) != 1 or SESSION_NAME_PATTERN.fullmatch(parts[0]) is None:
        return None
    return target


def session_binding_record(event: dict[str, Any], root: Path, host: str) -> dict[str, str]:
    path = session_binding_path(event, root, host)
    if path is None:
        return {}
    try:
        value = path.read_text(encoding="utf-8").strip()
    except (FileNotFoundError, OSError):
        return {}
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        parsed = None
    if isinstance(parsed, dict) and isinstance(parsed.get("directory"), str):
        return {
            key: str(parsed.get(key, ""))
            for key in (
                "directory",
                "branch",
                "merge_target",
                "task",
                "responsibility",
                "contract_version",
                "worktree",
            )
        }
    return {
        "directory": value,
        "branch": "",
        "merge_target": "",
        "task": "",
        "responsibility": "",
        "contract_version": "",
        "worktree": "",
    }


def binding_worktree(root: Path, record: dict[str, str]) -> Path:
    raw = record.get("worktree", "")
    if not raw:
        return root.resolve()
    try:
        candidate = Path(raw).resolve()
    except (OSError, RuntimeError):
        return root.resolve()
    if branch_guard.same_git_repository(root, candidate):
        return candidate
    return root.resolve()


def active_assignment_branch(event: dict[str, Any], root: Path, host: str) -> str:
    """CLOSED 전까지 같은 세션이 소유하는 assignment 권한 root를 반환한다."""

    record = session_binding_record(event, root, host)
    branch = (
        record.get("task", "")
        or os.environ.get(TASK_ENV, "").strip()
        or record.get("branch", "")
    )
    if not branch:
        return ""
    lookup_root = binding_worktree(root, record)
    if branch_guard.task_state(lookup_root, branch) == "CLOSED":
        return ""
    return branch


def bound_session_directory(event: dict[str, Any], root: Path, host: str) -> Path | None:
    record = session_binding_record(event, root, host)
    value = record.get("directory", "")
    if value:
        record_root = binding_worktree(root, record)
        candidate = artifact_session_directory(
            record_root,
            f"{value}/{HANDOFF_ARTIFACT}",
            host,
        )
        if candidate is not None:
            return candidate
    return declared_session_directory(root, host)


def bind_artifact_session(event: dict[str, Any], root: Path, host: str) -> str | None:
    raw_input = event.get("tool_input")
    tool_input = raw_input if isinstance(raw_input, dict) else {}
    tool_name = normalized_tool_name(event)
    if tool_name not in STRUCTURED_MUTATION_TOOLS | SHELL_TOOLS:
        return None
    raw_targets = structured_targets(tool_input)
    command_value = tool_input.get("command")
    command = command_value if isinstance(command_value, str) else ""
    if tool_name in {"apply_patch", "patch"}:
        raw_targets.extend(patch_targets(command))
    resolved_redirects = tuple(
        target
        for raw_target in shell_redirect_targets(command)
        if (target := resolved_shell_target(root, tool_input, raw_target)) is not None
    )
    target_contexts = tuple(
        context
        for raw_target in raw_targets
        if (context := repository_target(root, raw_target)) is not None
    )
    redirect_contexts = tuple(
        context
        for target in resolved_redirects
        if (context := repository_target(root, str(target))) is not None
    )
    artifact_contexts = tuple(
        (target_root, relative)
        for target_root, relative in (*target_contexts, *redirect_contexts)
        if relative.startswith(ARTIFACT_SESSIONS_PREFIXES)
    )
    artifact_relative_targets = tuple(
        dict.fromkeys(relative for _, relative in artifact_contexts)
    )
    cross_host_denial = branch_guard.artifact_write_denial(
        tuple(dict.fromkeys(artifact_relative_targets)),
        host,
    )
    if cross_host_denial is not None:
        return cross_host_denial
    for target_root, relative in artifact_contexts:
        layout_denial = artifact_layout_denial(target_root, relative, host)
        if layout_denial is not None:
            return layout_denial
    current_prefix = artifact_sessions_prefix(host)
    if has_non_redirect_shell_mutation(command):
        current_host = host if host in HOST_ARTIFACT_SESSIONS_PREFIXES else "unknown"
        for owner, prefix in HOST_ARTIFACT_SESSIONS_PREFIXES.items():
            if owner != current_host and prefix in command:
                return (
                    f"다른 host({owner}) 세션의 산출물은 읽기 전용입니다. "
                    f"현재 host({current_host})의 구조화된 쓰기 도구를 사용하세요."
                )
    redirect_writes_artifact = any(
        relative.startswith(ARTIFACT_SESSIONS_PREFIXES)
        for _, relative in redirect_contexts
    )
    command_writes_artifact = bool(
        has_non_redirect_shell_mutation(command)
        and current_prefix in command
    )
    if (
        tool_name in SHELL_TOOLS
        and command
        and (redirect_writes_artifact or command_writes_artifact)
        and not trusted_branch_workflow_invocation(command, root)
    ):
        return (
            "Bash heredoc·리다이렉션으로 만든 세션 산출물은 세션 귀속을 기록할 수 없습니다. "
            "현재 호스트의 구조화된 파일 쓰기 도구를 사용하세요."
        )
    candidates = tuple(
        (target_root, candidate)
        for target_root, relative in target_contexts
        if (candidate := artifact_session_directory(target_root, relative, host)) is not None
    )
    if not candidates:
        return None
    requested_root, requested = candidates[0]
    if any(candidate.resolve() != requested.resolve() for _, candidate in candidates[1:]):
        return "한 번의 작업에서 서로 다른 세션 산출물 디렉터리를 수정할 수 없습니다."
    path = session_binding_path(event, root, host)
    record = session_binding_record(event, root, host)
    relative = requested.resolve().relative_to(requested_root.resolve()).as_posix()
    branch = branch_guard.current_branch(requested_root)
    values = branch_guard.metadata(requested_root, branch) if branch else {}
    assignment_root = active_assignment_branch(event, root, host)
    in_assignment = bool(
        assignment_root
        and branch
        and branch_guard.assignment_includes_branch(
            requested_root,
            assignment_root,
            branch,
        )
    )
    existing = (
        bound_session_directory(event, root, host)
        if record
        else declared_session_directory(requested_root, host)
    )
    if path is None and existing is None:
        return (
            "호스트 이벤트에 session id가 없으므로 산출물 소유권을 자동 귀속할 수 없습니다. "
            f"세션 시작 시 ASAN_SESSION_DIR={requested.resolve().relative_to(requested_root.resolve()).as_posix()}를 "
            "지정하세요."
        )
    can_rebind = False
    declared_session = os.environ.get(SESSION_DIR_ENV, "").strip().strip("/")
    logical_session = record.get("directory", "") or declared_session
    lineage_worktree_move = bool(in_assignment and logical_session == relative)
    if existing is not None and existing.resolve() != requested.resolve():
        if not lineage_worktree_move:
            can_rebind = session_rebind_allowed(requested_root, existing, record)
        if not can_rebind and not lineage_worktree_move:
            return (
                "현재 세션의 기존 작업이 CLOSED 상태가 아니므로 다른 산출물 디렉터리로 전환할 수 없습니다. "
                "기존 작업을 완료·merge·검증하거나 handoff 후 별도 worktree와 세션을 사용하세요."
            )
    if assignment_root and branch and not (in_assignment or can_rebind):
        return (
            "현재 세션의 assignment 권한 계보와 산출물 대상 branch가 다릅니다.\n"
            f"  권한 root: {assignment_root}\n"
            f"  산출물 대상: {branch} ({requested_root})"
        )
    if record.get("branch") and record["branch"] != branch and not (can_rebind or in_assignment):
        return (
            "현재 세션의 assignment 권한 계보 밖 branch에 같은 산출물 디렉터리를 사용할 수 없습니다. "
            "독립 task는 이전 task를 CLOSED로 만든 뒤 새 산출물 디렉터리에 바인딩하세요."
        )
    declared_task = os.environ.get(TASK_ENV, "").strip()
    declared_includes_branch = bool(
        declared_task
        and branch
        and branch_guard.assignment_includes_branch(
            requested_root,
            declared_task,
            branch,
        )
    )
    if declared_task and declared_task != branch and not (can_rebind or declared_includes_branch):
        return (
            f"session assignment 권한 계보와 현재 branch가 다릅니다: "
            f"root={declared_task}, branch={branch or 'detached HEAD'}"
        )
    task = (
        (branch or declared_task)
        if can_rebind
        else assignment_root or declared_task or branch
    )
    responsibility = (
        os.environ.get(ARTIFACT_RESPONSIBILITY_ENV, "").strip().casefold()
        or record.get("responsibility", "").casefold()
        or "owner"
    )
    if responsibility not in tuple(branch_guard.ARTIFACT_RESPONSIBILITIES):
        return f"지원하지 않는 산출물 책임입니다: {responsibility}"
    if path is None:
        return None
    binding = {
        "directory": relative,
        "branch": branch,
        "merge_target": str(values.get("merge-target") or ""),
        "task": task,
        "responsibility": responsibility,
        "contract_version": str(values.get("contract-version") or ""),
        "worktree": str(requested_root.resolve()),
    }
    temporary = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(binding, ensure_ascii=False), encoding="utf-8")
    temporary.chmod(0o600)
    temporary.replace(path)
    return None


def bind_task_assignment(event: dict[str, Any], root: Path, host: str) -> str | None:
    """source/Git mutation에서 권한 root를 보존하고 현재 branch 초점을 갱신한다."""

    path = session_binding_path(event, root, host)
    if path is None:
        return None
    raw_input = event.get("tool_input")
    tool_input = raw_input if isinstance(raw_input, dict) else {}
    tool_name = normalized_tool_name(event)
    command_value = tool_input.get("command")
    command = command_value if isinstance(command_value, str) else ""
    target_roots: list[Path] = []
    if tool_name in STRUCTURED_MUTATION_TOOLS:
        raw_targets = structured_targets(tool_input)
        if tool_name in {"apply_patch", "patch"}:
            raw_targets.extend(patch_targets(command))
        target_roots.extend(
            target_root
            for raw_target in raw_targets
            if (context := repository_target(root, raw_target)) is not None
            for target_root in (context[0],)
        )
    elif tool_name in SHELL_TOOLS and command and git_command_mutates(command):
        invocations = branch_guard.git_invocations(
            root,
            command,
            shell_working_directory(root, tool_input),
        )
        if invocations is not None:
            target_roots.extend(invocation.root for invocation in invocations)
    unique_roots = tuple(dict.fromkeys(target.resolve() for target in target_roots))
    roots_by_branch: dict[str, Path] = {}
    for target_root in unique_roots:
        target_branch = branch_guard.current_branch(target_root)
        if target_branch and target_branch != str(branch_guard.BASE_BRANCH):
            roots_by_branch.setdefault(target_branch, target_root)
    branches = tuple(roots_by_branch)
    if not branches:
        return None
    if len(branches) != 1:
        return "한 번의 mutation을 서로 다른 task branch에 귀속할 수 없습니다. 명령을 분리하세요."
    branch = branches[0]
    target_root = roots_by_branch[branch]
    record = session_binding_record(event, root, host)
    previous = record.get("branch", "")
    assignment_root = active_assignment_branch(event, root, host)
    in_assignment = bool(
        assignment_root
        and branch_guard.assignment_allows_branch_mutation(
            target_root,
            assignment_root,
            branch,
        )
    )
    if previous and previous != branch and not in_assignment:
        if branch_guard.task_state(binding_worktree(root, record), previous) != "CLOSED":
            return (
                f"현재 세션의 assignment 권한 root({assignment_root or previous}) 밖인 "
                f"task({branch})로 전환할 수 없습니다."
            )
        return (
            "CLOSED 뒤 다음 독립 task를 시작하려면 먼저 새 task의 새 산출물 디렉터리를 "
            "구조화된 Write 도구로 바인딩하세요."
        )
    if previous == branch:
        return None
    values = branch_guard.metadata(target_root, branch)
    responsibility = (
        os.environ.get(ARTIFACT_RESPONSIBILITY_ENV, "").strip().casefold()
        or record.get("responsibility", "").casefold()
        or "owner"
    )
    if responsibility not in tuple(branch_guard.ARTIFACT_RESPONSIBILITIES):
        return f"지원하지 않는 산출물 책임입니다: {responsibility}"
    binding = {
        "directory": record.get("directory", ""),
        "branch": branch,
        "merge_target": str(values.get("merge-target") or ""),
        "task": assignment_root or branch,
        "responsibility": responsibility,
        "contract_version": str(values.get("contract-version") or ""),
        "worktree": str(target_root),
    }
    temporary = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(binding, ensure_ascii=False), encoding="utf-8")
    temporary.chmod(0o600)
    temporary.replace(path)
    return None


def _committed_paths(root: Path, branch: str) -> tuple[str, ...] | None:
    if not branch or not branch_guard.branch_exists(root, branch):
        return ()
    values = branch_guard.metadata(root, branch)
    parent_head = str(values.get("parent-head") or "")
    if branch_guard.FULL_SHA_PATTERN.fullmatch(parent_head) is None:
        return ()
    completed = subprocess.run(
        ["git", "diff", "--name-only", "-z", f"{parent_head}..{branch}"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return None
    return tuple(path for path in completed.stdout.split("\0") if path)


def changed_non_artifact_paths(root: Path, branch: str = "") -> tuple[str, ...] | None:
    working = branch_guard.changed_paths(root)
    if getattr(branch_guard, "GIT_STATUS_UNAVAILABLE", "") in working:
        return None
    selected_branch = branch or branch_guard.current_branch(root)
    committed = _committed_paths(root, selected_branch)
    if committed is None:
        return None
    return tuple(
        dict.fromkeys(
            path
            for path in (*working, *committed)
            if path and not path.startswith(ARTIFACT_SESSIONS_PREFIXES)
        )
    )


def git_artifact_ownership_denial(
    event: dict[str, Any],
    root: Path,
    host: str,
) -> str | None:
    """Git staging·commit도 현재 host·session의 산출물만 포함하게 한다."""

    tool_name = normalized_tool_name(event)
    raw_input = event.get("tool_input")
    tool_input = raw_input if isinstance(raw_input, dict) else {}
    command_value = tool_input.get("command")
    command = command_value if isinstance(command_value, str) else ""
    if tool_name not in SHELL_TOOLS or not command or trusted_branch_workflow_invocation(command, root):
        return None

    invocations = branch_guard.git_invocations(
        root,
        command,
        shell_working_directory(root, tool_input),
    )
    if invocations is None:
        return None
    affected: list[tuple[Path, str]] = []
    for invocation in invocations:
        arguments = invocation.arguments
        if not arguments:
            continue
        if arguments[0] == "add":
            affected.extend(
                (invocation.root, path)
                for path in branch_guard.changed_paths(invocation.root)
            )
            affected.extend(
                (invocation.root, path)
                for path in branch_guard._pathspecs_after_separator(arguments)
            )
        elif arguments[0] == "commit":
            affected.extend(
                (invocation.root, path)
                for path in branch_guard.staged_paths(invocation.root)
            )
    if any(path == branch_guard.GIT_STATUS_UNAVAILABLE for _, path in affected):
        return "Git 산출물 변경 상태를 확인할 수 없어 소유권 검증을 중단했습니다."

    artifact_paths = tuple(
        dict.fromkeys(
            (target_root, path)
            for target_root, path in affected
            if path.startswith(ARTIFACT_SESSIONS_PREFIXES)
        )
    )
    if not artifact_paths:
        return None
    denial = branch_guard.artifact_write_denial(
        tuple(path for _, path in artifact_paths),
        host,
    )
    if denial is not None:
        return denial
    current = bound_session_directory(event, root, host)
    if current is None:
        return "Git에 포함할 산출물이 현재 host·session에 귀속되지 않았습니다."
    for target_root, relative in artifact_paths:
        layout_denial = artifact_layout_denial(target_root, relative, host)
        if layout_denial is not None:
            return layout_denial
        session = artifact_session_directory(target_root, relative, host)
        if session is None or session.resolve() != current.resolve():
            return f"다른 세션의 산출물은 Git에 포함할 수 없습니다: {relative}"
    return None


def artifact_has_content(path: Path) -> bool:
    if path.is_symlink() or not path.is_file():
        return False
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return False
    table_rows = 0
    separator_seen = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("#", "<!--")):
            continue
        if TABLE_SEPARATOR.fullmatch(line):
            separator_seen = True
            continue
        if line.startswith("|"):
            if separator_seen:
                cells = [cell.strip() for cell in line.strip("|").split("|")]
                if any(cells):
                    table_rows += 1
            continue
        normalized = re.sub(r"^[\-*+>\d.()\s]+", "", line).strip()
        if len(normalized) >= 8 and re.search(r"\w", normalized):
            return True
    return table_rows > 0


def _has_grill_data_row(text: str) -> bool:
    match = re.search(r"##\s*neutral question flow\s*(.*?)(?:\n##\s+|\Z)", text, re.S | re.I)
    if match is None:
        return False
    separator_seen = False
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if TABLE_SEPARATOR.fullmatch(line):
            separator_seen = True
            continue
        if separator_seen and line.startswith("|"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) >= 5 and all(cells[:5]):
                return True
    return False


def _portfolio_issues(text: str) -> list[str]:
    matches = list(PORTFOLIO_CASE.finditer(text))
    if not matches:
        return ["portfolio-log.md: 사례가 없음"]
    issues: list[str] = []
    for index, match in enumerate(matches, start=1):
        end = matches[index].start() if index < len(matches) else len(text)
        section = text[match.end():end]
        headings = set(re.findall(r"^###\s+(.+?)\s*$", section, re.MULTILINE))
        missing_headings = [heading for heading in PORTFOLIO_HEADINGS if heading not in headings]
        missing_fields = [
            field
            for field in PORTFOLIO_FIELDS
            if re.search(rf"^-\s*{re.escape(field)}\s*:", section, re.MULTILINE) is None
        ]
        if missing_headings or missing_fields:
            missing = ", ".join((*missing_fields, *missing_headings))
            issues.append(f"portfolio-log.md: 사례 {index} 필수 구조 누락({missing})")
    return issues


def artifact_issues(session: Path) -> tuple[str, ...]:
    issues: list[str] = []
    texts: dict[str, str] = {}
    for name in REQUIRED_ARTIFACTS:
        target = session / name
        if target.is_symlink() or not target.is_file():
            issues.append(f"{name}: 없거나 symlink")
            continue
        try:
            text = target.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            issues.append(f"{name}: 읽을 수 없음")
            continue
        texts[name] = text
        if not artifact_has_content(target):
            issues.append(f"{name}: 제목·placeholder만 있거나 내용 없음")
    grill = texts.get("grill-me-review.md")
    if grill is not None:
        normalized = grill.casefold()
        if "## method guardrails" not in normalized:
            issues.append("grill-me-review.md: Method Guardrails 누락")
        if "neutral question-first 적용 여부" not in normalized:
            issues.append("grill-me-review.md: neutral question-first 확인 누락")
        if "recommended answer" not in normalized:
            issues.append("grill-me-review.md: Recommended Answer 열 누락")
        if not _has_grill_data_row(grill):
            issues.append("grill-me-review.md: 실제 질문·답변 데이터 행 누락")
    portfolio = texts.get("portfolio-log.md")
    if portfolio is not None:
        issues.extend(_portfolio_issues(portfolio))
    return tuple(issues)


def session_rebind_allowed(root: Path, session: Path, record: dict[str, str]) -> bool:
    """완료·merge된 이전 작업 뒤 같은 프로세스의 순차 작업 전환만 허용한다."""

    if artifact_issues(session):
        return False
    if changed_non_artifact_paths(root) != ():
        return False
    previous_branch = record.get("branch", "")
    previous_target = record.get("merge_target", "")
    current = branch_guard.current_branch(root)
    if not previous_branch or not previous_target or not current:
        return current == str(branch_guard.BASE_BRANCH)
    previous_values = (
        branch_guard.metadata(root, previous_branch)
        if branch_guard.branch_exists(root, previous_branch)
        else {}
    )
    previous_version = str(
        previous_values.get("contract-version") or record.get("contract_version", "")
    )
    if previous_version == str(branch_guard.CONTRACT_VERSION):
        if branch_guard.task_state(root, previous_branch) != "CLOSED":
            return False
    if not branch_guard.branch_exists(root, previous_target):
        return False
    if branch_guard.branch_exists(root, previous_branch) and not branch_guard.is_ancestor(
        root, previous_branch, previous_target
    ):
        return False
    if current == previous_target:
        return True
    current_values = branch_guard.metadata(root, current)
    return current_values.get("parent") == previous_target


def documentation_denial(event: dict[str, Any], root: Path, host: str) -> str | None:
    record = session_binding_record(event, root, host)
    changed = changed_non_artifact_paths(root, record.get("branch", ""))
    if changed == ():
        return None
    if changed is None:
        return "변경 상태를 확인할 수 없어 필수 산출물 검증을 완료하지 못했습니다."
    session = bound_session_directory(event, root, host)
    if session is None:
        prefix = artifact_sessions_prefix(host)
        return (
            "현재 세션에 귀속된 산출물 디렉터리가 없습니다. "
            f"{prefix}{{YYYY-MM-DD-task-slug}}/에 인계 문서를 작성하세요."
        )
    handoff_complete = artifact_has_content(session / HANDOFF_ARTIFACT)
    full_issues = artifact_issues(session)
    full_complete = not full_issues
    branch = record.get("branch", "") or branch_guard.current_branch(root)
    values = branch_guard.metadata(root, branch) if branch else {}
    artifact_mode = str(values.get("artifact-mode") or "")
    contract_version = str(values.get("contract-version") or "")
    responsibility = (
        os.environ.get(ARTIFACT_RESPONSIBILITY_ENV, "").strip().casefold()
        or record.get("responsibility", "").casefold()
        or "owner"
    )
    if responsibility not in tuple(branch_guard.ARTIFACT_RESPONSIBILITIES):
        return f"지원하지 않는 산출물 책임이라 완료할 수 없습니다: {responsibility}"
    assigned_task = record.get("task", "") or os.environ.get(TASK_ENV, "").strip()
    if assigned_task and branch and not branch_guard.assignment_includes_branch(
        root,
        assigned_task,
        branch,
    ):
        return (
            "session assignment 권한 계보와 산출물 branch가 다릅니다: "
            f"root={assigned_task}, branch={branch}"
        )
    if contract_version == str(branch_guard.CONTRACT_VERSION):
        if responsibility == "owner" and full_complete:
            return None
        if responsibility == "contributor" and handoff_complete:
            return None
        if responsibility == "contributor":
            return "부분 기여자는 현재 세션 디렉터리에 내용이 있는 handoff.md를 작성해야 합니다."
        return (
            "전체 작업 책임자는 현재 세션 디렉터리에 구조를 갖춘 필수 산출물 8종을 모두 작성해야 합니다. "
            f"확인 필요: {'; '.join(full_issues)}"
        )
    if artifact_mode == "full" and full_complete:
        return None
    if artifact_mode == "handoff" and handoff_complete:
        return None
    if not artifact_mode and (handoff_complete or full_complete):
        return None
    if artifact_mode == "full":
        return (
            "전체 작업 책임자는 현재 세션 디렉터리에 구조를 갖춘 필수 산출물 8종을 모두 작성해야 합니다. "
            f"확인 필요: {'; '.join(full_issues)}"
        )
    if artifact_mode == "handoff":
        return "부분 역할 기여자는 현재 세션 디렉터리에 내용이 있는 handoff.md를 작성해야 합니다."
    detail = f" 확인 필요: {'; '.join(full_issues)}" if full_issues else ""
    return (
        "legacy branch 계약의 변경을 완료하려면 현재 세션 디렉터리에 내용이 있는 handoff.md를 작성하거나 "
        f"필수 산출물 8종을 모두 작성해야 합니다.{detail}"
    )


def assignment_responsibility(event: dict[str, Any], root: Path, host: str) -> str:
    record = session_binding_record(event, root, host)
    return (
        os.environ.get(ARTIFACT_RESPONSIBILITY_ENV, "").strip().casefold()
        or record.get("responsibility", "").casefold()
        or "owner"
    )


def preservation_documentation_denial(
    event: dict[str, Any],
    root: Path,
    host: str,
) -> str | None:
    session = bound_session_directory(event, root, host)
    if session is None:
        return "작업을 PRESERVED로 전환하려면 현재 세션에 귀속된 산출물 디렉터리가 필요합니다."
    if not artifact_has_content(session / HANDOFF_ARTIFACT):
        return "작업을 PRESERVED로 전환하기 전에 현재 세션 디렉터리에 handoff.md를 작성해야 합니다."
    return None


def completion_assignment_denial(
    event: dict[str, Any],
    root: Path,
    host: str,
) -> str | None:
    responsibility = assignment_responsibility(event, root, host)
    if responsibility == "owner":
        return None
    return (
        "contributor assignment는 handoff까지만 수행할 수 있습니다. "
        "필수 산출물 8종을 책임지는 owner assignment가 finish·verify·close를 수행해야 합니다."
    )


def emit_stop_result(denial: str | None) -> None:
    if denial is None:
        print("{}")
        return
    json.dump({"decision": "block", "reason": denial}, sys.stdout, ensure_ascii=False)


def transient_state_path(
    event: dict[str, Any],
    root: Path,
    host: str,
    namespace: str,
) -> Path | None:
    session_id = event_session_id(event)
    if session_id == "missing-session-id":
        return None
    repository_identity = branch_guard.git_common_directory(root) or root.resolve()
    identity = f"{repository_identity}\0{host}\0{event_session_id(event)}"
    digest = hashlib.sha256(identity.encode()).hexdigest()
    state_root = Path(tempfile.gettempdir()) / f"asan-agent-policy-{namespace}"
    state_root.mkdir(mode=0o700, parents=True, exist_ok=True)
    return state_root / f"{digest}.json"


def approval_state_path(event: dict[str, Any], root: Path, host: str) -> Path | None:
    return transient_state_path(event, root, host, "command-approvals")


def harness_state_path(event: dict[str, Any], root: Path, host: str) -> Path | None:
    return transient_state_path(event, root, host, "harness-state-v3")


def load_json_state(path: Path | None, *, max_age: int | None = None) -> dict[str, Any]:
    if path is None:
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    if not isinstance(value, dict):
        return {}
    if max_age is not None:
        created_at = value.get("created_at")
        if not isinstance(created_at, (int, float)) or time.time() - created_at > max_age:
            path.unlink(missing_ok=True)
            return {}
    return value


def write_json_state(path: Path | None, state: dict[str, Any]) -> None:
    if path is None:
        return
    temporary = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
    temporary.chmod(0o600)
    temporary.replace(path)


def load_approval_state(path: Path | None) -> dict[str, Any]:
    return load_json_state(path, max_age=APPROVAL_MAX_AGE_SECONDS)


def write_approval_state(path: Path | None, state: dict[str, Any]) -> None:
    write_json_state(path, state)


def normalize_prompt(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).casefold()
    normalized = re.sub(r"[.,!?。！？]+", " ", normalized)
    return " ".join(normalized.split())


def prompt_contract_sha256(text: str) -> str:
    matches = tuple(dict.fromkeys(match.casefold() for match in CONTRACT_SHA256_PATTERN.findall(text)))
    if len(matches) != 1 or DENIAL_WORD_PATTERN.search(text):
        return ""
    return matches[0] if APPROVAL_WORD_PATTERN.search(text) else ""


def is_implementation_approval(text: str) -> bool:
    normalized = normalize_prompt(text)
    if DENIAL_WORD_PATTERN.search(normalized):
        return False
    if normalized in IMPLEMENTATION_APPROVAL_PHRASES:
        return True
    padded = f" {normalized} "
    return any(f" {phrase} " in padded for phrase in EMBEDDED_IMPLEMENTATION_APPROVAL_PHRASES)


def event_output_text(event: dict[str, Any]) -> str:
    values: list[str] = []
    for key in ("tool_output", "tool_response", "result", "output", "stdout"):
        value = event.get(key)
        if isinstance(value, str):
            values.append(value)
        elif isinstance(value, dict):
            values.extend(item for item in value.values() if isinstance(item, str))
    return "\n".join(values)


def resolved_evidence_targets(
    event: dict[str, Any],
    root: Path,
) -> tuple[Path, ...]:
    raw_input = event.get("tool_input")
    tool_input = raw_input if isinstance(raw_input, dict) else {}
    targets: list[Path] = []
    for raw_path in structured_targets(tool_input):
        candidate = Path(raw_path).expanduser()
        try:
            target = (candidate if candidate.is_absolute() else root / candidate).resolve()
        except (OSError, RuntimeError):
            continue
        targets.append(target)
    if normalized_tool_name(event) in SHELL_TOOLS:
        command_value = tool_input.get("command")
        command = command_value if isinstance(command_value, str) else ""
        try:
            tokens = shlex.split(command, posix=True)
        except ValueError:
            tokens = []
        for token in tokens:
            if token.startswith("-") or not (
                "/" in token or token in {"src", ".agents", ".agent-policy"}
            ):
                continue
            candidate = Path(token).expanduser()
            try:
                target = (candidate if candidate.is_absolute() else root / candidate).resolve()
            except (OSError, RuntimeError):
                continue
            targets.append(target)
    return tuple(dict.fromkeys(targets))


def is_skill_evidence(event: dict[str, Any], root: Path) -> bool:
    tool_name = normalized_tool_name(event)
    raw_input = event.get("tool_input")
    tool_input = raw_input if isinstance(raw_input, dict) else {}
    if tool_name == "skill":
        skill = tool_input.get("skill") or tool_input.get("name")
        return isinstance(skill, str) and bool(skill.strip())
    if tool_name not in READ_EVIDENCE_TOOLS | SHELL_TOOLS:
        return False
    for target in resolved_evidence_targets(event, root):
        if target.name != "SKILL.md":
            continue
        allowed_roots = (
            root / ".agent-policy/common/skills",
            root / ".agents/skills",
            root / ".claude/skills",
            root / ".codex/skills",
            root / ".opencode/skills",
            *injected_policy_roots(),
        )
        if any(target == allowed.resolve() or target.is_relative_to(allowed.resolve()) for allowed in allowed_roots):
            return True
    return False


def is_exploration_evidence(event: dict[str, Any], root: Path) -> bool:
    tool_name = normalized_tool_name(event)
    if tool_name not in READ_EVIDENCE_TOOLS | SHELL_TOOLS:
        return False
    for target in resolved_evidence_targets(event, root):
        try:
            relative = target.relative_to(root.resolve()).as_posix()
        except ValueError:
            relative = ""
        if relative == "src" or relative.startswith("src/"):
            return True
        if "reference/" in target.as_posix():
            return True
    return False


def is_ui_exploration_evidence(event: dict[str, Any], root: Path) -> bool:
    tool_name = normalized_tool_name(event)
    if tool_name not in READ_EVIDENCE_TOOLS | SHELL_TOOLS:
        return False
    for target in resolved_evidence_targets(event, root):
        try:
            relative = target.relative_to(root.resolve()).as_posix()
        except ValueError:
            relative = ""
        if relative == "src/shared/ui" or relative.startswith("src/shared/ui/"):
            return True
        if "reference/components" in target.as_posix():
            return True
    return False


def requires_ui_exploration(root: Path) -> bool:
    selected_role = os.environ.get(INJECT_ROLE_ENV, "").strip().casefold()
    if selected_role == "ui":
        return True
    branch = branch_guard.current_branch(root)
    values = branch_guard.metadata(root, branch) if branch else {}
    roles = values.get("roles")
    return isinstance(roles, tuple) and "ui" in roles


def record_post_tool(event: dict[str, Any], root: Path, host: str) -> None:
    path = harness_state_path(event, root, host)
    if path is None:
        return
    state = load_json_state(path)
    if is_skill_evidence(event, root):
        state["skill_confirmed"] = True
    if is_exploration_evidence(event, root):
        state["exploration_completed"] = True
    if is_ui_exploration_evidence(event, root):
        state["ui_exploration_completed"] = True

    raw_input = event.get("tool_input")
    tool_input = raw_input if isinstance(raw_input, dict) else {}
    command_value = tool_input.get("command")
    command = command_value if isinstance(command_value, str) else ""
    if trusted_branch_workflow_action(command, root) in {
        "proposal",
        "scope-proposal",
        "finish-proposal",
    }:
        digests = tuple(
            dict.fromkeys(
                match.casefold()
                for match in CONTRACT_SHA256_PATTERN.findall(event_output_text(event))
            )
        )
        if len(digests) == 1:
            state["pending_contract_sha256"] = digests[0]
            state.pop("approved_contract_sha256", None)
    if state:
        write_json_state(path, state)


def command_digest(command: str) -> str:
    return hashlib.sha256(command.encode()).hexdigest()


def codex_operation_allowed(event: dict[str, Any], root: Path, command: str) -> bool:
    path = approval_state_path(event, root, "codex")
    if path is None:
        return False
    state = load_approval_state(path)
    digest = command_digest(command)
    if state.get("approved") is True and state.get("command_sha256") == digest:
        path.unlink(missing_ok=True)
        return True

    write_approval_state(
        path,
        {
            "approved": False,
            "categories": list(protected_operation_categories(command)),
            "command_sha256": digest,
            "created_at": time.time(),
        },
    )
    return False


def record_user_prompt(event: dict[str, Any], root: Path, host: str) -> None:
    prompt = event.get("prompt")
    if not isinstance(prompt, str):
        return

    harness_path = harness_state_path(event, root, host)
    harness_state = load_json_state(harness_path)
    if prompt.strip() != COMMAND_APPROVAL_PHRASE:
        approved_digest = prompt_contract_sha256(prompt)
        approved = is_implementation_approval(prompt) or bool(approved_digest)
        harness_state["implementation_approved"] = approved
        if approved_digest:
            harness_state["approved_contract_sha256"] = approved_digest
        elif approved and isinstance(harness_state.get("pending_contract_sha256"), str):
            harness_state["approved_contract_sha256"] = harness_state[
                "pending_contract_sha256"
            ]
        else:
            harness_state.pop("approved_contract_sha256", None)
        write_json_state(harness_path, harness_state)
        return

    if host != "codex":
        return

    path = approval_state_path(event, root, host)
    state = load_approval_state(path)
    if not state or state.get("approved") is not False:
        return
    state["approved"] = True
    state["created_at"] = time.time()
    write_approval_state(path, state)
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": "직전에 차단된 동일 명령을 1회 실행할 수 있습니다. 명령을 변경하면 다시 승인을 요청하세요.",
            }
        },
        sys.stdout,
        ensure_ascii=False,
    )


def git_command_mutates(command: str) -> bool:
    return branch_guard.git_command_mutates(command)


def implementation_gate_required(event: dict[str, Any], root: Path) -> bool:
    tool_name = normalized_tool_name(event)
    raw_input = event.get("tool_input")
    tool_input = raw_input if isinstance(raw_input, dict) else {}
    command_value = tool_input.get("command")
    command = command_value if isinstance(command_value, str) else ""
    if tool_name in STRUCTURED_MUTATION_TOOLS:
        raw_targets = structured_targets(tool_input)
        if tool_name in {"apply_patch", "patch"}:
            raw_targets.extend(patch_targets(command))
        if not raw_targets:
            return True
        relatives = tuple(
            context[1] if (context := repository_target(root, raw_path)) is not None else None
            for raw_path in raw_targets
        )
        return any(
            relative is None or not relative.startswith(ARTIFACT_SESSIONS_PREFIXES)
            for relative in relatives
        )
    if tool_name not in SHELL_TOOLS or not command:
        return False
    action = trusted_branch_workflow_action(command, root)
    if action:
        return action in {
            "create",
            "update-scope",
            "finish",
            "verify",
            "close",
            "preserve",
            "resume",
        }
    if git_command_mutates(command) or has_non_redirect_shell_mutation(command):
        return True
    for raw_target in shell_redirect_targets(command):
        target = resolved_shell_target(root, tool_input, raw_target)
        if target is None or target_in_injected_policy(target) is not None:
            return True
        context = repository_target(root, str(target))
        relative = context[1] if context is not None else relative_target(root, target)
        if relative is not None and not relative.startswith(ARTIFACT_SESSIONS_PREFIXES):
            return True
    return False


def implementation_gate_denial(
    event: dict[str, Any],
    root: Path,
    host: str,
) -> str | None:
    if not implementation_gate_required(event, root):
        return None
    state = load_json_state(harness_state_path(event, root, host))
    missing: list[str] = []
    if state.get("implementation_approved") is not True:
        missing.append("사용자 구현 승인")
    if state.get("skill_confirmed") is not True:
        missing.append("관련 SKILL.md 확인")
    exploration_key = (
        "ui_exploration_completed" if requires_ui_exploration(root) else "exploration_completed"
    )
    if state.get(exploration_key) is not True:
        missing.append(
            "src/shared/ui 재사용 자산 탐색"
            if exploration_key == "ui_exploration_completed"
            else "역할별 재사용 자산·인접 구현 탐색"
        )

    raw_input = event.get("tool_input")
    tool_input = raw_input if isinstance(raw_input, dict) else {}
    command_value = tool_input.get("command")
    command = command_value if isinstance(command_value, str) else ""
    action = trusted_branch_workflow_action(command, root)
    if action in {"create", "update-scope", "finish", "verify", "close"}:
        arguments = trusted_branch_workflow_arguments(command, root)
        proposed_digest = branch_workflow_option(arguments, "--proposal-sha256").casefold()
        approved_digest = str(state.get("approved_contract_sha256") or "").casefold()
        if CONTRACT_SHA256_PATTERN.fullmatch(proposed_digest) is None:
            missing.append("64자리 proposal SHA-256")
        elif approved_digest != proposed_digest:
            missing.append("현재 proposal SHA-256에 대한 사용자 승인")
    if not missing:
        return None
    return (
        "공통 구현 gate의 필수 조건이 누락되었습니다: "
        + ", ".join(dict.fromkeys(missing))
        + ". 계획·역할·branch proposal을 보고하고 사용자 승인을 받은 뒤, 관련 스킬과 "
        "재사용 가능 자산 또는 인접 구현을 실제 도구로 확인하세요."
    )


def operation_approval_message(command: str, categories: tuple[str, ...], host: str) -> str:
    category_text = ", ".join(categories)
    if host == "codex":
        action = (
            f"실행하려면 사용자가 `{COMMAND_APPROVAL_PHRASE}`만 독립된 메시지로 보내야 합니다. "
            "승인은 아래의 완전히 동일한 명령에 한해 1회만 유효합니다."
        )
    else:
        action = "호스트가 표시하는 권한 요청에서 사용자가 직접 실행 여부를 결정해야 합니다."
    return (
        f"{category_text} 명령은 사용자 승인 전에 실행할 수 없습니다.\n"
        f"명령: {command}\n"
        f"{action}"
    )


def emit_operation_approval(host: str, message: str) -> None:
    if host in {"codex", "claude"}:
        decision = "deny" if host == "codex" else "ask"
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": decision,
                    "permissionDecisionReason": message,
                }
            },
            sys.stdout,
            ensure_ascii=False,
        )
        return
    print(message, file=sys.stderr)
    raise SystemExit(2)


def emit_denial(host: str, message: str) -> None:
    if host == "codex":
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": message,
                }
            },
            sys.stdout,
            ensure_ascii=False,
        )
        return
    print(message, file=sys.stderr)
    raise SystemExit(2)


def emit_session_context(host: str, message: str) -> None:
    if host == "codex":
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": message,
                }
            },
            sys.stdout,
            ensure_ascii=False,
        )
        return
    print(message)


def check_session(event: dict[str, Any], host: str) -> None:
    root = repository_root(event)
    messages: list[str] = []
    project_id = os.environ.get(INJECT_PROJECT_ENV, "").strip()
    bundle_root = os.environ.get(INJECT_BUNDLE_ROOT_ENV, "").strip()
    if not inject_mode() or not project_id or not bundle_root:
        messages.append(
            "중앙 inject 실행 컨텍스트가 완전하지 않습니다. "
            "중앙 launcher로 새 세션을 시작해 주세요."
        )

    context = branch_guard.branch_context(root)
    if context:
        messages.append(context)
    if messages:
        emit_session_context(host, "\n\n".join(messages))


def check_operation(event: dict[str, Any], root: Path, host: str) -> None:
    if host == "opencode":
        return
    tool_name = normalized_tool_name(event)
    raw_input = event.get("tool_input")
    tool_input = raw_input if isinstance(raw_input, dict) else {}
    command_value = tool_input.get("command")
    command = command_value if isinstance(command_value, str) else ""
    if tool_name not in SHELL_TOOLS or not command:
        return

    categories = protected_operation_categories(command)
    if not categories:
        return
    if host == "codex" and codex_operation_allowed(event, root, command):
        return
    emit_operation_approval(host, operation_approval_message(command, categories, host))


def operation_repository_root(event: dict[str, Any], root: Path) -> Path:
    raw_input = event.get("tool_input")
    tool_input = raw_input if isinstance(raw_input, dict) else {}
    candidate = git_top_level(shell_working_directory(root, tool_input))
    if candidate is not None and branch_guard.same_git_repository(root, candidate):
        return candidate
    return root


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    host = sys.argv[2] if len(sys.argv) > 2 else ""
    event = read_event()

    if mode == "session-start":
        root = repository_root(event)
        for path in (
            approval_state_path(event, root, host),
            harness_state_path(event, root, host),
        ):
            if path is not None:
                path.unlink(missing_ok=True)
        check_session(event, host)
        return
    if mode == "branch-context":
        context = branch_guard.branch_context(repository_root(event))
        if context:
            print(context)
        return
    if mode == "documentation-stop":
        # 구버전 adapter가 이 mode를 계속 호출해도 대화 종료를 재차단하지 않는다.
        # 산출물 계약은 명시적 finish/verify/close와 preserve PreToolUse에서 검증한다.
        emit_stop_result(None)
        return
    if mode == "user-prompt":
        record_user_prompt(event, repository_root(event), host)
        return
    if mode == "post-tool":
        record_post_tool(event, repository_root(event), host)
        return
    if mode != "pre-tool":
        raise SystemExit("지원하지 않는 guard mode입니다.")

    root = repository_root(event)
    targets = denied_targets(event, root)
    if targets:
        emit_denial(host, denial_message(targets))
        return
    binding_denial = bind_artifact_session(event, root, host)
    if binding_denial is not None:
        emit_denial(host, binding_denial)
        return
    git_artifact_denial = git_artifact_ownership_denial(event, root, host)
    if git_artifact_denial is not None:
        emit_denial(host, git_artifact_denial)
        return
    raw_input = event.get("tool_input")
    tool_input = raw_input if isinstance(raw_input, dict) else {}
    command_value = tool_input.get("command")
    command = command_value if isinstance(command_value, str) else ""
    workflow_action = trusted_branch_workflow_action(command, root)
    operation_root = operation_repository_root(event, root)
    if workflow_action == "preserve":
        preservation_denial = preservation_documentation_denial(event, operation_root, host)
        if preservation_denial is not None:
            emit_denial(host, preservation_denial)
            return
    if workflow_action in {"finish-proposal", "finish", "verify", "close"}:
        assignment_denial = completion_assignment_denial(event, operation_root, host)
        if assignment_denial is not None:
            emit_denial(host, assignment_denial)
            return
        completion_denial = documentation_denial(event, operation_root, host)
        if completion_denial is not None:
            emit_denial(host, completion_denial)
            return
    denial = branch_denial(event, root, host)
    if denial is not None:
        emit_denial(host, denial)
        return
    assignment_binding_denial = bind_task_assignment(event, root, host)
    if assignment_binding_denial is not None:
        emit_denial(host, assignment_binding_denial)
        return
    readiness_denial = implementation_gate_denial(event, operation_root, host)
    if readiness_denial is not None:
        emit_denial(host, readiness_denial)
        return
    check_operation(event, operation_root, host)


if __name__ == "__main__":
    main()
