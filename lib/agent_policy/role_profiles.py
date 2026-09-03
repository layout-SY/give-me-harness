from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Final


CENTRAL_ROOT: Final = Path(__file__).resolve().parents[2]
RUNTIME_CONTRACT_PATH: Final = CENTRAL_ROOT / "policy/common/contracts/runtime-policy.json"


def _load_runtime_contract() -> dict[str, Any]:
    value = json.loads(RUNTIME_CONTRACT_PATH.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("version") != 3:
        raise RuntimeError(f"지원하지 않는 공통 runtime 계약입니다: {RUNTIME_CONTRACT_PATH}")
    return value


RUNTIME_CONTRACT: Final = _load_runtime_contract()


def _canonical_role(name: str) -> str:
    roles = RUNTIME_CONTRACT.get("roles")
    entry = roles.get(name) if isinstance(roles, dict) else None
    canonical = entry.get("canonical") if isinstance(entry, dict) else None
    if not isinstance(canonical, str) or not canonical:
        raise RuntimeError(f"공통 runtime 계약의 role이 올바르지 않습니다: {name}")
    return canonical


@dataclass(frozen=True)
class InjectRoleProfile:
    cli_name: str
    canonical_name: str
    summary: str
    role_references: tuple[str, ...]
    common_skill_prefixes: tuple[str, ...]
    native_agents: tuple[str, ...]


BASE_COMMON_SKILL_PREFIXES: Final = (
    ".agent-policy/common/skills/SKILL.md",
    ".agent-policy/common/skills/policy/SKILL.md",
    ".agent-policy/common/skills/policy/documentation/",
    ".agent-policy/common/skills/policy/git-branch-strategy/",
    ".agent-policy/common/skills/policy/task-role-routing/SKILL.md",
    ".agent-policy/common/skills/policy/task-role-routing/references/handoff-and-ownership.md",
    ".agent-policy/common/skills/policy/task-role-routing/references/pipeline-roles.md",
)


ROLE_PROFILES: Final[dict[str, InjectRoleProfile]] = {
    "logic": InjectRoleProfile(
        cli_name="logic",
        canonical_name=_canonical_role("logic"),
        summary="API, 데이터, 상태, hook과 업무 규칙을 구현한다.",
        role_references=("logic.md", "pipeline-roles.md"),
        common_skill_prefixes=(
            ".agent-policy/common/skills/policy/abstraction-strategy/",
            ".agent-policy/common/skills/policy/coding-convention/",
            ".agent-policy/common/skills/policy/data-fetch-layer/",
            ".agent-policy/common/skills/policy/implementation-quality/",
            ".agent-policy/common/skills/policy/refactoring/",
            ".agent-policy/common/skills/policy/type-definition/",
            ".agent-policy/common/skills/policy/validation/",
            ".agent-policy/common/skills/recipe/api-authoring/",
            ".agent-policy/common/skills/recipe/data-dto/",
            ".agent-policy/common/skills/recipe/data-fetch/",
            ".agent-policy/common/skills/reference/custom-hooks/",
        ),
        native_agents=("generator", "refactorer", "watcher"),
    ),
    "ui": InjectRoleProfile(
        cli_name="ui",
        canonical_name=_canonical_role("ui"),
        summary="화면 구조, 스타일, 접근성, 반응형 표현과 UI 계약을 구현한다.",
        role_references=("ui.md", "pipeline-roles.md"),
        common_skill_prefixes=(
            ".agent-policy/common/skills/policy/abstraction-strategy/",
            ".agent-policy/common/skills/policy/coding-convention/",
            ".agent-policy/common/skills/policy/implementation-quality/",
            ".agent-policy/common/skills/policy/refactoring/",
            ".agent-policy/common/skills/policy/styles/",
            ".agent-policy/common/skills/policy/ui-library/",
            ".agent-policy/common/skills/policy/validation/",
            ".agent-policy/common/skills/recipe/i18n/",
            ".agent-policy/common/skills/reference/components/",
        ),
        native_agents=("publisher", "generator", "refactorer", "watcher"),
    ),
    "orchest": InjectRoleProfile(
        cli_name="orchest",
        canonical_name=_canonical_role("orchest"),
        summary="요청 조사, 계획, 역할·소유권·승인과 완료 게이트를 조율한다.",
        role_references=(
            "orchestration.md",
            "pipeline-roles.md",
            "workflows.md",
        ),
        common_skill_prefixes=(
            ".agent-policy/common/skills/policy/harness/",
            ".agent-policy/common/skills/policy/review-checklist/",
        ),
        native_agents=("planner",),
    ),
    "review": InjectRoleProfile(
        cli_name="review",
        canonical_name=_canonical_role("review"),
        summary="구현을 변경하지 않고 현재 변경과 장기 개선점을 검토한다.",
        role_references=("pipeline-roles.md",),
        common_skill_prefixes=(
            ".agent-policy/common/skills/policy/implementation-quality/",
            ".agent-policy/common/skills/policy/review-checklist/",
            ".agent-policy/common/skills/policy/validation/",
        ),
        native_agents=("watcher", "evaluator"),
    ),
    "generate": InjectRoleProfile(
        cli_name="generate",
        canonical_name=_canonical_role("generate"),
        summary="승인된 handoff와 branch scope에 적힌 기본 역할을 구현한다.",
        role_references=(
            "logic.md",
            "ui.md",
            "pipeline-roles.md",
            "workflows.md",
        ),
        common_skill_prefixes=(".agent-policy/common/skills/",),
        native_agents=("publisher", "generator", "refactorer", "watcher"),
    ),
}

INJECT_ROLES: Final = tuple(ROLE_PROFILES)
_HOSTS = RUNTIME_CONTRACT.get("hosts")
if not isinstance(_HOSTS, dict):
    raise RuntimeError("공통 runtime 계약의 hosts가 object가 아닙니다.")
HOST_ARTIFACT_SESSION_ROOTS: Final = {
    name: str(value["artifact_root"])
    for name, value in _HOSTS.items()
    if isinstance(name, str)
    and isinstance(value, dict)
    and isinstance(value.get("artifact_root"), str)
}
_ARTIFACTS = RUNTIME_CONTRACT.get("artifacts")
if not isinstance(_ARTIFACTS, dict):
    raise RuntimeError("공통 runtime 계약의 artifacts가 object가 아닙니다.")
ARTIFACT_RESPONSIBILITIES: Final = tuple(
    value
    for value in _ARTIFACTS.get("responsibilities", ())
    if isinstance(value, str)
)


def role_profile(role: str) -> InjectRoleProfile:
    try:
        return ROLE_PROFILES[role]
    except KeyError as error:
        supported = ", ".join(INJECT_ROLES)
        raise ValueError(f"지원하지 않는 inject role입니다: {role} (지원: {supported})") from error


def artifact_session_root(host: str) -> str:
    try:
        return HOST_ARTIFACT_SESSION_ROOTS[host]
    except KeyError as error:
        supported = ", ".join(HOST_ARTIFACT_SESSION_ROOTS)
        raise ValueError(f"지원하지 않는 host입니다: {host} (지원: {supported})") from error


def path_matches(relative: str, selectors: tuple[str, ...]) -> bool:
    return any(
        relative.startswith(selector) if selector.endswith("/") else relative == selector
        for selector in selectors
    )


def common_skill_selected(relative: str, role: str) -> bool:
    profile = role_profile(role)
    role_references = tuple(
        f".agent-policy/common/skills/policy/task-role-routing/references/{name}"
        for name in profile.role_references
    )
    return path_matches(
        relative,
        BASE_COMMON_SKILL_PREFIXES + role_references + profile.common_skill_prefixes,
    )


def role_document_paths(host: str, role: str) -> tuple[str, ...]:
    profile = role_profile(role)
    _ = host
    root = ".agent-policy/common/skills/policy/task-role-routing"
    references = tuple(f"{root}/references/{name}" for name in profile.role_references)
    return (
        f"{root}/SKILL.md",
        f"{root}/references/handoff-and-ownership.md",
        *references,
    )
