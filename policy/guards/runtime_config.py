"""runtime의 공통 계약 상수와 중앙 snapshot 의존성."""
from __future__ import annotations

import re
from pathlib import Path
from types import ModuleType
from typing import Final


_loader_path = Path(__file__).resolve().with_name("runtime_loader.py")
_loader = ModuleType("asan_runtime_loader")
_loader.__file__ = str(_loader_path)
exec(compile(_loader_path.read_bytes(), str(_loader_path), "exec"), _loader.__dict__)
load_runtime_module = _loader.load

branch_guard = load_runtime_module("branch_guard")
event_protocol = load_runtime_module("event_protocol")
runtime_state = load_runtime_module("runtime_state")
CENTRAL_ROOT: Final = Path("{{CENTRAL_ROOT}}")
PROJECT_ROOT: Final = Path("{{PROJECT_PATH}}")
DEV_COMMAND: Final = "{{DEV_COMMAND}}"
BUILD_COMMAND: Final = "{{BUILD_COMMAND}}"
COMMAND_APPROVAL_PHRASE: Final = "명령 실행 승인"
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
SESSION_DIR_MODE_ENV: Final = "ASAN_SESSION_DIR_MODE"
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
READ_EVIDENCE_TOOLS: Final = frozenset(
    {"glob", "grep", "read", "search", "skill", "webfetch", "websearch"}
)
STRUCTURED_MUTATION_TOOLS: Final = frozenset(
    {"apply_patch", "edit", "multiedit", "notebookedit", "patch", "write"}
)
SHELL_TOOLS: Final = frozenset({"bash", "exec", "exec_command", "shell"})

load_json_state = runtime_state.read
write_json_state = runtime_state.write
