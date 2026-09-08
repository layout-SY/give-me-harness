"""작업 브랜치 계보와 파일 범위를 검증하는 호스트 중립 guard."""

from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import re
import shlex
import subprocess
from pathlib import Path
from typing import NamedTuple

BASE_BRANCH = "{{BASE_BRANCH}}"
TASK_BRANCH_PATTERN = re.compile(r"^task/[a-z0-9]+(?:-[a-z0-9]+)*$")
FULL_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
INTEGRATOR_PATTERN = re.compile(r"^(?:codex|claude|opencode|user)$")


def _runtime_contract_path() -> Path:
    bundle_root = os.environ.get("ASAN_AGENT_POLICY_BUNDLE_ROOT", "").strip()
    source = Path(__file__).resolve()
    candidates = [
        source.parents[1] / "common/contracts/runtime-policy.json",
        *(
            (Path(bundle_root) / ".agent-policy/common/contracts/runtime-policy.json",)
            if bundle_root
            else ()
        ),
        Path.cwd() / ".agent-policy/common/contracts/runtime-policy.json",
        Path.cwd() / "policy/common/contracts/runtime-policy.json",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise RuntimeError("공통 runtime-policy.json을 찾을 수 없습니다. 정책을 다시 렌더링하세요.")


def _runtime_contract() -> dict[str, object]:
    source = _runtime_contract_path()
    try:
        value = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"공통 runtime 계약을 읽을 수 없습니다: {source}: {error}") from error
    if not isinstance(value, dict) or value.get("version") != 3:
        raise RuntimeError(f"지원하지 않는 공통 runtime 계약입니다: {source}")
    return value


RUNTIME_CONTRACT = _runtime_contract()
_HOSTS = RUNTIME_CONTRACT.get("hosts")
if not isinstance(_HOSTS, dict):
    raise RuntimeError("공통 runtime 계약의 hosts가 올바르지 않습니다.")
HOST_ARTIFACT_SESSION_ROOTS: dict[str, str] = {
    str(name): str(value["artifact_root"])
    for name, value in _HOSTS.items()
    if isinstance(value, dict) and isinstance(value.get("artifact_root"), str)
}
KNOWN_HOSTS: tuple[str, ...] = tuple(
    name for name in HOST_ARTIFACT_SESSION_ROOTS if name != "unknown"
)
ARTIFACT_PREFIXES: tuple[str, ...] = tuple(
    f"{root.rstrip('/')}/" for root in HOST_ARTIFACT_SESSION_ROOTS.values()
)
_ROLES = RUNTIME_CONTRACT.get("roles")
if not isinstance(_ROLES, dict):
    raise RuntimeError("공통 runtime 계약의 roles가 올바르지 않습니다.")
ROLE_ALIASES: dict[str, str] = {
    str(name): str(value["canonical"])
    for name, value in _ROLES.items()
    if isinstance(value, dict) and isinstance(value.get("canonical"), str)
}
_ARTIFACTS = RUNTIME_CONTRACT.get("artifacts")
if not isinstance(_ARTIFACTS, dict):
    raise RuntimeError("공통 runtime 계약의 artifacts가 올바르지 않습니다.")
REQUIRED_ARTIFACTS: tuple[str, ...] = tuple(
    str(name) for name in _ARTIFACTS.get("required", ()) if isinstance(name, str)
)
HANDOFF_ARTIFACT = str(_ARTIFACTS.get("handoff", "handoff.md"))
UNKNOWN_ARTIFACT_DIRECTORY = str(_ARTIFACTS.get("unknown_directory", "unknown"))
ARTIFACT_RESPONSIBILITIES: tuple[str, ...] = tuple(
    str(value)
    for value in _ARTIFACTS.get("responsibilities", ())
    if isinstance(value, str)
)
TASK_STATES: tuple[str, ...] = tuple(
    str(state) for state in RUNTIME_CONTRACT.get("task_states", ()) if isinstance(state, str)
)
_GIT_POLICY = RUNTIME_CONTRACT.get("git")
if not isinstance(_GIT_POLICY, dict):
    raise RuntimeError("공통 runtime 계약의 git 정책이 올바르지 않습니다.")
NEVER_AGENT_GIT_COMMANDS: tuple[str, ...] = tuple(
    str(command)
    for command in _GIT_POLICY.get("never_agent_commands", ())
    if isinstance(command, str)
)
ALLOWED_VALIDATION_COMMANDS: tuple[tuple[str, ...], ...] = tuple(
    tuple(shlex.split(command, posix=True))
    for command in _GIT_POLICY.get("validation_commands", ())
    if isinstance(command, str) and command.strip()
)
MAX_LINEAGE_DEPTH = 32
CONTRACT_VERSION = "3"
ALLOWED_ROLES: tuple[str, ...] = tuple(
    dict.fromkeys((*ROLE_ALIASES, *ROLE_ALIASES.values(), "documentation"))
)

REQUIRED_METADATA: tuple[str, ...] = (
    "purpose",
    "parent",
    "parent-head",
    "merge-target",
    "proposal",
)

V3_REQUIRED_METADATA: tuple[str, ...] = (
    *REQUIRED_METADATA,
    "reason",
    "contract-sha256",
    "git-integrator",
    "task-id",
    "state",
)
GIT_STATUS_UNAVAILABLE = "<git-status-unavailable>"


class GitInvocation(NamedTuple):
    """한 shell command 안의 Git 호출과 그 호출이 실제로 대상으로 삼는 worktree."""

    root: Path
    arguments: tuple[str, ...]
    unsafe_repository_options: tuple[str, ...] = ()


def _git(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ("git", *arguments),
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return subprocess.CompletedProcess(("git", *arguments), 1, "", "")


def _output(root: Path, *arguments: str) -> str:
    completed = _git(root, *arguments)
    return completed.stdout.strip() if completed.returncode == 0 else ""


def enabled(base_branch: str = BASE_BRANCH) -> bool:
    """대상별 기준 브랜치 토큰이 렌더링된 hook인지 확인한다."""

    return bool(base_branch and "{{" not in base_branch)


def current_branch(root: Path) -> str:
    return _output(root, "symbolic-ref", "--quiet", "--short", "HEAD")


def head(root: Path, revision: str = "HEAD") -> str:
    return _output(root, "rev-parse", revision)


def branch_exists(root: Path, branch: str) -> bool:
    return _git(root, "show-ref", "--verify", "--quiet", f"refs/heads/{branch}").returncode == 0


def is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    return _git(root, "merge-base", "--is-ancestor", ancestor, descendant).returncode == 0


def merge_base(root: Path, left: str, right: str) -> str:
    return _output(root, "merge-base", left, right)


def changed_paths(root: Path) -> tuple[str, ...]:
    completed = _git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    if completed.returncode != 0:
        return (GIT_STATUS_UNAVAILABLE,)
    paths: list[str] = []
    records = completed.stdout.split("\0")
    index = 0
    while index < len(records):
        record = records[index]
        index += 1
        if not record:
            continue
        if len(record) < 4:
            return (GIT_STATUS_UNAVAILABLE,)
        status = record[:2]
        entry = record[3:]
        if entry:
            paths.append(entry)
        if "R" in status or "C" in status:
            if index >= len(records) or not records[index]:
                return (GIT_STATUS_UNAVAILABLE,)
            paths.append(records[index])
            index += 1
    return tuple(dict.fromkeys(paths))


def staged_paths(root: Path) -> tuple[str, ...]:
    completed = _git(root, "diff", "--cached", "--name-only", "-z")
    if completed.returncode != 0:
        return (GIT_STATUS_UNAVAILABLE,)
    return tuple(path for path in completed.stdout.split("\0") if path)


def _config(root: Path, branch: str, field: str) -> str:
    return _output(root, "config", "--get", f"branch.{branch}.asan-{field}")


def _config_all(root: Path, branch: str, field: str) -> tuple[str, ...]:
    completed = _git(root, "config", "--get-all", f"branch.{branch}.asan-{field}")
    if completed.returncode != 0:
        return ()
    return tuple(line.strip() for line in completed.stdout.splitlines() if line.strip())


def metadata(root: Path, branch: str) -> dict[str, object]:
    values: dict[str, object] = {field: _config(root, branch, field) for field in REQUIRED_METADATA}
    values["scope"] = _config_all(root, branch, "scope")
    values["roles"] = _config_all(root, branch, "role")
    values["worktree"] = _config(root, branch, "worktree")
    values["git-integrator"] = _config(root, branch, "git-integrator")
    values["artifact-mode"] = _config(root, branch, "artifact-mode")
    values["contract-version"] = _config(root, branch, "contract-version")
    values["contract-sha256"] = _config(root, branch, "contract-sha256")
    values["reason"] = _config(root, branch, "reason")
    values["task-id"] = _config(root, branch, "task-id")
    values["state"] = _config(root, branch, "state")
    return values


def git_common_directory(root: Path) -> Path | None:
    raw = _output(root, "rev-parse", "--git-common-dir")
    if not raw:
        return None
    candidate = Path(raw)
    try:
        return (candidate if candidate.is_absolute() else root / candidate).resolve()
    except OSError:
        return None


def task_state(root: Path, branch: str) -> str:
    """존재하는 branch metadata 또는 삭제 후 closed record에서 task 상태를 읽는다."""

    if branch_exists(root, branch):
        return str(metadata(root, branch).get("state") or "")
    common = git_common_directory(root)
    if common is None or TASK_BRANCH_PATTERN.fullmatch(branch) is None:
        return ""
    source = common / "asan-agent-policy/closed" / f"{branch.removeprefix('task/')}.json"
    try:
        value = json.loads(source.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return ""
    if not isinstance(value, dict) or value.get("source") != branch:
        return ""
    return str(value.get("state") or "")


def _missing_metadata(values: dict[str, object]) -> tuple[str, ...]:
    missing = [field for field in V3_REQUIRED_METADATA if not values.get(field)]
    scope = values.get("scope")
    if not isinstance(scope, tuple) or not scope:
        missing.append("scope")
    roles = values.get("roles")
    if not isinstance(roles, tuple) or not roles:
        missing.append("role")
    return tuple(missing)


def _v3_contract_denial(branch: str, values: dict[str, object]) -> str | None:
    version = str(values.get("contract-version") or "")
    if version == CONTRACT_VERSION:
        return None
    legacy = f"V{version}" if version else "V1(무버전)"
    return (
        f"{branch}의 {legacy} branch 계약은 변경 권한을 부여하지 않습니다. "
        "branch_workflow.py proposal → create 절차로 V3 계약을 다시 승인받으세요."
    )


def canonical_contract(
    branch: str,
    purpose: str,
    parent: str,
    parent_head: str,
    merge_target: str,
    scopes: tuple[str, ...],
    reason: str,
    worktree: str = "",
    roles: tuple[str, ...] = (),
    git_integrator: str = "",
) -> dict[str, object]:
    """순서와 공백 차이를 제거한 V3 branch task 계약을 만든다."""

    return {
        "version": int(CONTRACT_VERSION),
        "task_id": branch.removeprefix("task/"),
        "branch": branch,
        "purpose": purpose.strip(),
        "parent": parent,
        "parent_head": parent_head,
        "merge_target": merge_target,
        "roles": sorted(dict.fromkeys(role.strip().casefold() for role in roles if role.strip())),
        "scopes": sorted(dict.fromkeys(scope.strip().strip("/") or "." for scope in scopes)),
        "git_integrator": git_integrator.strip().casefold(),
        "reason": reason.strip(),
        "worktree": worktree,
    }


def contract_bytes(contract: dict[str, object]) -> bytes:
    return json.dumps(
        contract,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def contract_sha256(contract: dict[str, object]) -> str:
    return hashlib.sha256(contract_bytes(contract)).hexdigest()


def proposal_id(
    branch: str,
    parent: str,
    parent_head: str,
    merge_target: str,
    worktree: str = "",
    roles: tuple[str, ...] = (),
    git_integrator: str = "",
    artifact_mode: str = "",
    purpose: str = "",
    scopes: tuple[str, ...] = (),
    reason: str = "",
) -> str:
    """승인 요청에 표시하고 hook이 재계산할 수 있는 분기 계약 식별자를 만든다."""

    if purpose or scopes or reason:
        contract = canonical_contract(
            branch,
            purpose,
            parent,
            parent_head,
            merge_target,
            scopes,
            reason,
            worktree,
            roles,
            git_integrator,
        )
        return f"asan-v3:{contract_sha256(contract)}"

    identifier = f"branch:{branch}|parent:{parent}@{parent_head}|merge:{merge_target}"
    normalized_roles = tuple(sorted(dict.fromkeys(roles)))
    if normalized_roles or git_integrator or artifact_mode:
        identifier += (
            f"|roles:{','.join(normalized_roles)}"
            f"|integrator:{git_integrator}"
            f"|artifacts:{artifact_mode}"
        )
    return f"{identifier}|worktree:{worktree}" if worktree else identifier


def branch_names(root: Path) -> tuple[str, ...]:
    output = _output(root, "for-each-ref", "--format=%(refname:short)", "refs/heads")
    return tuple(line.strip() for line in output.splitlines() if line.strip())


def unmerged_children(root: Path, parent: str) -> tuple[str, ...]:
    children: list[str] = []
    for branch in branch_names(root):
        values = metadata(root, branch)
        if values.get("parent") != parent:
            continue
        if not is_ancestor(root, branch, parent):
            children.append(branch)
    return tuple(sorted(children))


def _scope_allows(relative: str, scopes: tuple[str, ...]) -> bool:
    if _artifact_host(relative) is not None:
        return True
    normalized = relative.strip("/")
    for raw_scope in scopes:
        scope = raw_scope.strip().strip("/")
        if scope in {"", "."}:
            return True
        if any(character in scope for character in "*?["):
            if fnmatch.fnmatch(normalized, scope):
                return True
            continue
        if normalized == scope or normalized.startswith(f"{scope}/"):
            return True
    return False


def _artifact_host(relative: str) -> str | None:
    normalized = relative.removeprefix("./")
    for host, root in HOST_ARTIFACT_SESSION_ROOTS.items():
        prefix = f"{root.rstrip('/')}/"
        if normalized.startswith(prefix):
            return host
    return None


def artifact_write_denial(targets: tuple[str, ...], host: str) -> str | None:
    """다른 host의 세션 산출물은 읽을 수 있지만 수정할 수 없게 한다."""

    current_host = host if host in KNOWN_HOSTS else "unknown"
    for relative in targets:
        owner = _artifact_host(relative)
        if owner is not None and owner != current_host:
            return (
                f"다른 host({owner}) 세션의 산출물은 읽기 전용입니다: {relative}\n"
                f"현재 host({current_host})는 {HOST_ARTIFACT_SESSION_ROOTS[current_host]}/ 아래의 "
                "현재 세션 디렉터리에만 쓸 수 있습니다."
            )
    return None


def _lineage_denial(
    root: Path,
    branch: str,
    base_branch: str,
    *,
    allow_merged: bool = False,
    required_ancestor: str = "",
) -> str | None:
    seen: set[str] = set()
    cursor = branch
    ancestor_found = not required_ancestor
    for _ in range(MAX_LINEAGE_DEPTH):
        if cursor == required_ancestor:
            ancestor_found = True
        if cursor == base_branch:
            return (
                None
                if ancestor_found
                else f"{branch}는 assignment 권한 root {required_ancestor}의 V3 자손이 아닙니다."
            )
        if cursor in seen:
            return f"브랜치 계보가 순환합니다: {cursor}"
        seen.add(cursor)
        values = metadata(root, cursor)
        version_problem = _v3_contract_denial(cursor, values)
        if version_problem is not None:
            return version_problem
        missing = _missing_metadata(values)
        if missing:
            return f"{cursor} 브랜치 메타데이터가 없습니다: {', '.join(missing)}"
        parent = str(values["parent"])
        merge_target = str(values["merge-target"])
        parent_head = str(values["parent-head"])
        proposal = str(values["proposal"])
        worktree = str(values.get("worktree") or "")
        if parent != merge_target:
            return f"{cursor}의 분기 기준({parent})과 직접 merge 대상({merge_target})이 다릅니다."
        if FULL_SHA_PATTERN.fullmatch(parent_head) is None:
            return f"{cursor}의 부모 HEAD는 40자리 전체 SHA여야 합니다: {parent_head or '없음'}"
        roles = values.get("roles")
        git_integrator = str(values.get("git-integrator") or "")
        assert isinstance(roles, tuple)
        invalid_roles = tuple(role for role in roles if role not in ALLOWED_ROLES)
        if invalid_roles:
            return f"{cursor}의 역할 metadata가 올바르지 않습니다: {', '.join(invalid_roles)}"
        if INTEGRATOR_PATTERN.fullmatch(git_integrator) is None:
            return f"{cursor}의 Git 통합 담당자가 올바르지 않습니다: {git_integrator or '없음'}"
        scopes = values.get("scope")
        assert isinstance(scopes, tuple)
        reason = str(values.get("reason") or "")
        purpose = str(values.get("purpose") or "")
        expected_proposal = proposal_id(
            cursor,
            parent,
            parent_head,
            merge_target,
            worktree,
            roles,
            git_integrator,
            "",
            purpose,
            scopes,
            reason,
        )
        expected_sha = expected_proposal.removeprefix("asan-v3:")
        if values.get("contract-sha256") != expected_sha:
            return f"{cursor}의 branch 계약 SHA-256이 승인된 canonical 계약과 일치하지 않습니다."
        if values.get("task-id") != cursor.removeprefix("task/"):
            return f"{cursor}의 task id가 branch 이름과 일치하지 않습니다."
        state = str(values.get("state") or "")
        if state not in TASK_STATES:
            return f"{cursor}의 작업 상태가 올바르지 않습니다: {state or '없음'}"
        if proposal != expected_proposal:
            return f"{cursor}의 승인 요청 식별자가 분기 계약과 일치하지 않습니다."
        if not branch_exists(root, parent):
            return f"{cursor}의 부모 브랜치를 찾을 수 없습니다: {parent}"
        if not head(root, parent_head):
            return f"{cursor}에 기록된 부모 HEAD를 찾을 수 없습니다: {parent_head}"
        if not is_ancestor(root, parent_head, cursor):
            return f"{cursor}가 승인된 부모 HEAD {parent_head[:12]}를 포함하지 않습니다."
        actual_base = merge_base(root, cursor, parent)
        if actual_base != parent_head and not (
            allow_merged and is_ancestor(root, cursor, parent)
        ):
            return (
                f"{cursor}의 실제 분기점({actual_base[:12]})이 승인된 부모 HEAD"
                f"({parent_head[:12]})와 다릅니다."
            )
        cursor = parent
    return f"브랜치 계보가 {MAX_LINEAGE_DEPTH}단계를 초과했습니다."


def assignment_includes_branch(
    root: Path,
    assignment_root: str,
    branch: str,
    base_branch: str = BASE_BRANCH,
) -> bool:
    """동일 assignment root 또는 승인된 V3 자손인지 식별한다."""

    if assignment_root and assignment_root == branch:
        return True
    return not (
        TASK_BRANCH_PATTERN.fullmatch(assignment_root) is None
        or TASK_BRANCH_PATTERN.fullmatch(branch) is None
        or not branch_exists(root, assignment_root)
        or not branch_exists(root, branch)
        or _lineage_denial(
            root,
            branch,
            base_branch,
            allow_merged=True,
            required_ancestor=assignment_root,
        )
        is not None
    )


def assignment_allows_branch_mutation(
    root: Path,
    assignment_root: str,
    branch: str,
    base_branch: str = BASE_BRANCH,
) -> bool:
    """유효한 V3 계보에서만 source·Git 변경 권한을 활성화한다."""

    if not enabled(base_branch):
        return bool(assignment_root and assignment_root == branch)
    if not assignment_includes_branch(root, assignment_root, branch, base_branch):
        return False
    if _lineage_denial(
        root,
        branch,
        base_branch,
        allow_merged=True,
        required_ancestor=assignment_root,
    ) is not None:
        return False
    return branch == assignment_root or task_state(root, assignment_root) == "ACTIVE"


def active_branch_denial(
    root: Path,
    targets: tuple[str, ...] = (),
    base_branch: str = BASE_BRANCH,
    host: str = "",
) -> str | None:
    """현재 작업 브랜치가 승인된 계보와 범위를 만족하는지 판정한다."""

    if not enabled(base_branch):
        return None
    if host:
        artifact_denial = artifact_write_denial(targets, host)
        if artifact_denial is not None:
            return artifact_denial
    branch = current_branch(root)
    if not branch:
        return "detached HEAD에서는 저장소를 수정할 수 없습니다. 작업 브랜치를 먼저 승인받으세요."
    if branch == base_branch:
        return (
            f"기준 브랜치 {base_branch}에서 직접 수정할 수 없습니다. "
            "git-branch-strategy 스킬에 따라 새 작업 브랜치를 승인받으세요."
        )
    if TASK_BRANCH_PATTERN.fullmatch(branch) is None:
        return f"작업 브랜치명은 task/<ascii-kebab-summary> 형식이어야 합니다: {branch}"
    if not branch_exists(root, base_branch):
        return f"기준 브랜치를 찾을 수 없습니다: {base_branch}"
    lineage_problem = _lineage_denial(root, branch, base_branch)
    if lineage_problem is not None:
        return lineage_problem
    values = metadata(root, branch)
    state = str(values.get("state") or "")
    if state != "ACTIVE":
        return (
            f"V3 task {branch}는 ACTIVE 상태에서만 수정할 수 있습니다. 현재 상태: "
            f"{state or '없음'}"
        )
    approved_worktree = str(values.get("worktree") or "")
    if approved_worktree:
        try:
            actual_root = root.resolve()
            expected_root = Path(approved_worktree).expanduser().resolve()
        except (OSError, RuntimeError):
            return f"V3 task {branch}의 승인 worktree 경로를 확인할 수 없습니다."
        if actual_root != expected_root:
            return (
                f"V3 task {branch}의 변경 대상 worktree가 승인 계약과 다릅니다.\n"
                f"  승인: {expected_root}\n"
                f"  실제: {actual_root}"
            )
    scopes = values.get("scope")
    assert isinstance(scopes, tuple)
    changed = changed_paths(root)
    if GIT_STATUS_UNAVAILABLE in changed:
        return "Git 변경 상태를 확인할 수 없어 승인 scope 검증을 중단했습니다."
    for relative in tuple(dict.fromkeys((*targets, *changed))):
        normalized = relative.removeprefix("./").strip("/")
        if normalized == ".git" or normalized.startswith(".git/"):
            return (
                f"Git 제어 경로는 branch scope에 포함되어도 직접 수정할 수 없습니다: {relative}. "
                "승인된 Git 명령 또는 branch_workflow.py를 사용하세요."
            )
        if not _scope_allows(relative, scopes):
            return (
                f"승인된 작업 범위 밖의 경로입니다: {relative}\n"
                f"  브랜치: {branch}\n"
                f"  승인 범위: {', '.join(scopes)}\n"
                "범위를 임의 확장하지 말고 사용자에게 다시 승인받으세요."
            )
    return None


def git_integrator_denial(root: Path, branch: str, host: str) -> str | None:
    """V3 계약에서 AI 호스트의 Git 통합 담당자 일치를 확인한다."""

    if not enabled():
        return None
    if not branch or not host:
        return None
    values = metadata(root, branch)
    version_problem = _v3_contract_denial(branch, values)
    if version_problem is not None:
        return version_problem
    integrator = str(values.get("git-integrator") or "")
    if integrator == host:
        return None
    if integrator == "user":
        return "이 브랜치의 Git 통합 담당자는 사용자입니다. AI 호스트가 Git 상태를 변경할 수 없습니다."
    return (
        f"이 브랜치의 Git 통합 담당자는 {integrator or '등록되지 않음'}입니다. "
        f"현재 호스트({host})는 index, commit 또는 merge를 조작할 수 없습니다."
    )


def _git_commands(command: str) -> tuple[tuple[str, ...], ...]:
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|")
        lexer.whitespace_split = True
        lexer.commenters = ""
        tokens = list(lexer)
    except ValueError:
        return (("<unparsed>",),) if re.search(r"(?:^|\s)git(?:\s|$)", command) else ()
    commands: list[tuple[str, ...]] = []
    index = 0
    separators = {";", "&&", "||", "|", "&"}
    while index < len(tokens):
        if os.path.basename(tokens[index]) != "git":
            index += 1
            continue
        end = index + 1
        while end < len(tokens) and tokens[end] not in separators:
            end += 1
        commands.append(tuple(tokens[index + 1:end]))
        index = end + 1
    if not commands:
        nested_git = any(
            re.search(r"(?:^|[^A-Za-z0-9_-])git\s+", token) is not None
            for token in tokens
        ) or re.search(r"(?:\$\(|`)[^\n]*\bgit\s+", command) is not None
        if nested_git:
            return (("<unparsed>",),)
    return tuple(commands)


GIT_GLOBAL_VALUE_OPTIONS = frozenset(
    {
        "-C",
        "-c",
        "--config-env",
        "--exec-path",
        "--git-dir",
        "--namespace",
        "--super-prefix",
        "--work-tree",
    }
)
GIT_GLOBAL_FLAG_OPTIONS = frozenset(
    {
        "--bare",
        "--html-path",
        "--info-path",
        "--literal-pathspecs",
        "--man-path",
        "--no-lazy-fetch",
        "--no-optional-locks",
        "--no-pager",
        "--no-replace-objects",
        "--no-restrict-protocols",
        "--paginate",
        "--version",
    }
)


def _strip_git_global_options(arguments: tuple[str, ...]) -> tuple[str, ...] | None:
    """`git -C … <subcommand>` 형태에서 실제 subcommand부터 반환한다."""

    index = 0
    while index < len(arguments):
        value = arguments[index]
        if value in GIT_GLOBAL_VALUE_OPTIONS:
            if index + 1 >= len(arguments):
                return None
            configured = arguments[index + 1]
            if value in {"-c", "--config-env"} and configured.casefold().startswith("alias."):
                return None
            index += 2
            continue
        if any(
            value.startswith(prefix)
            for prefix in (
                "-C",
                "-c",
                "--config-env=",
                "--exec-path=",
                "--git-dir=",
                "--namespace=",
                "--super-prefix=",
                "--work-tree=",
            )
        ) and value not in {"-C", "-c"}:
            if value.casefold().startswith(("-calias.", "--config-env=alias.")):
                return None
            index += 1
            continue
        if value in GIT_GLOBAL_FLAG_OPTIONS:
            index += 1
            continue
        if value.startswith("-"):
            return None
        return arguments[index:]
    return ()


def _resolved_option_path(base: Path, raw_value: str) -> Path | None:
    if not raw_value or any(character in raw_value for character in ("\0", "\n", "\r")):
        return None
    try:
        candidate = Path(raw_value).expanduser()
        return (candidate if candidate.is_absolute() else base / candidate).resolve()
    except (OSError, RuntimeError):
        return None


def _git_top_level(
    working_directory: Path,
    git_directory: Path | None = None,
    work_tree: Path | None = None,
) -> Path | None:
    arguments = ["git"]
    if git_directory is not None:
        arguments.append(f"--git-dir={git_directory}")
    if work_tree is not None:
        arguments.append(f"--work-tree={work_tree}")
    arguments.extend(("rev-parse", "--show-toplevel"))
    try:
        completed = subprocess.run(
            arguments,
            cwd=working_directory,
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


def _absolute_git_directory(working_directory: Path) -> Path | None:
    raw = _output(working_directory, "rev-parse", "--absolute-git-dir")
    if not raw:
        return None
    try:
        return Path(raw).resolve()
    except (OSError, RuntimeError):
        return None


def _git_invocation(
    execution_cwd: Path,
    raw_arguments: tuple[str, ...],
) -> GitInvocation | None:
    """Git global option을 적용한 실제 worktree와 subcommand를 함께 해석한다."""

    working_directory = execution_cwd.resolve()
    git_directory: Path | None = None
    work_tree: Path | None = None
    unsafe: list[str] = []
    index = 0
    while index < len(raw_arguments):
        value = raw_arguments[index]
        if value == "-C":
            if index + 1 >= len(raw_arguments):
                return None
            resolved = _resolved_option_path(working_directory, raw_arguments[index + 1])
            if resolved is None or not resolved.is_dir():
                return None
            working_directory = resolved
            index += 2
            continue
        if value.startswith("-C") and value != "-C" and not value.startswith("-c"):
            resolved = _resolved_option_path(working_directory, value[2:])
            if resolved is None or not resolved.is_dir():
                return None
            working_directory = resolved
            index += 1
            continue
        if value in {"--git-dir", "--work-tree"}:
            if index + 1 >= len(raw_arguments):
                return None
            resolved = _resolved_option_path(working_directory, raw_arguments[index + 1])
            if resolved is None:
                return None
            if value == "--git-dir":
                git_directory = resolved
            else:
                work_tree = resolved
            index += 2
            continue
        if value.startswith("--git-dir=") or value.startswith("--work-tree="):
            option, raw_path = value.split("=", maxsplit=1)
            resolved = _resolved_option_path(working_directory, raw_path)
            if resolved is None:
                return None
            if option == "--git-dir":
                git_directory = resolved
            else:
                work_tree = resolved
            index += 1
            continue
        if value == "-c" or (value.startswith("-c") and value != "-C"):
            if value == "-c":
                if index + 1 >= len(raw_arguments):
                    return None
                configured = raw_arguments[index + 1]
                index += 2
            else:
                configured = value[2:]
                index += 1
            key = configured.split("=", maxsplit=1)[0].casefold()
            if key.startswith("alias."):
                return None
            if key in {"core.worktree", "core.bare"}:
                unsafe.append(f"-c {key}")
            continue
        if value == "--config-env" or value.startswith("--config-env="):
            if value == "--config-env":
                if index + 1 >= len(raw_arguments):
                    return None
                index += 2
            else:
                index += 1
            unsafe.append("--config-env")
            continue
        if value in {"--exec-path", "--namespace", "--super-prefix"}:
            if index + 1 >= len(raw_arguments):
                return None
            unsafe.append(value)
            index += 2
            continue
        if any(
            value.startswith(f"{option}=")
            for option in ("--exec-path", "--namespace", "--super-prefix")
        ):
            unsafe.append(value.split("=", maxsplit=1)[0])
            index += 1
            continue
        if value == "--bare":
            unsafe.append(value)
            index += 1
            continue
        if value in GIT_GLOBAL_FLAG_OPTIONS:
            index += 1
            continue
        if value.startswith("-"):
            return None
        break

    arguments = raw_arguments[index:]
    if arguments == ("<unparsed>",):
        return None
    if git_directory is not None and work_tree is None:
        unsafe.append("--git-dir without --work-tree")
    target_root = _git_top_level(working_directory, git_directory, work_tree)
    if target_root is None:
        return None
    effective_git_directory = git_directory or _absolute_git_directory(working_directory)
    expected_git_directory = _absolute_git_directory(target_root)
    if (
        effective_git_directory is None
        or expected_git_directory is None
        or effective_git_directory.resolve() != expected_git_directory.resolve()
    ):
        unsafe.append("Git directory/worktree mismatch")
    return GitInvocation(
        root=target_root,
        arguments=arguments,
        unsafe_repository_options=tuple(dict.fromkeys(unsafe)),
    )


def git_invocations(
    root: Path,
    command: str,
    execution_cwd: Path | None = None,
) -> tuple[GitInvocation, ...] | None:
    """shell 안의 모든 Git 호출을 대상 worktree 기준으로 해석한다."""

    cwd = (execution_cwd or root).resolve()
    invocations: list[GitInvocation] = []
    for raw_arguments in _git_commands(command):
        invocation = _git_invocation(cwd, raw_arguments)
        if invocation is None:
            return None
        invocations.append(invocation)
    return tuple(invocations)


def same_git_repository(left: Path, right: Path) -> bool:
    left_common = git_common_directory(left)
    right_common = git_common_directory(right)
    return left_common is not None and left_common == right_common


def _never_agent_git_denial(arguments: tuple[str, ...]) -> str | None:
    if not arguments:
        return None
    subcommand = arguments[0]
    hard_reset = subcommand == "reset" and any(
        option == "--hard" or option.startswith("--hard=") for option in arguments[1:]
    )
    blocked = (
        subcommand in NEVER_AGENT_GIT_COMMANDS
        or (hard_reset and "reset --hard" in NEVER_AGENT_GIT_COMMANDS)
    )
    if blocked:
        rendered = "git " + " ".join(arguments)
        return (
            f"{rendered} 명령은 에이전트가 실행할 수 없는 사용자 전용 작업입니다. "
            "승인으로 해제하거나 우회하지 말고, 필요한 이유·정확한 대상·예상 영향을 사용자에게 "
            "양도한 뒤 사용자가 직접 실행하도록 하세요."
        )
    return None


def _never_agent_git_text_denial(command: str) -> str | None:
    """중첩 shell·alias로 숨긴 사용자 전용 Git 명령도 승인 경로 전에 찾는다."""

    normalized = command.casefold()
    if re.search(r"\bgit\b", normalized) is None:
        return None
    critical = (
        ("push" in NEVER_AGENT_GIT_COMMANDS and re.search(r"\bpush\b", normalized))
        or (
            "reset --hard" in NEVER_AGENT_GIT_COMMANDS
            and re.search(r"\breset\b", normalized)
            and "--hard" in normalized
        )
        or ("clean" in NEVER_AGENT_GIT_COMMANDS and re.search(r"\bclean\b", normalized))
        or ("update-ref" in NEVER_AGENT_GIT_COMMANDS and "update-ref" in normalized)
    )
    if not critical:
        return None
    return (
        "숨겨지거나 중첩된 사용자 전용 Git 명령이 감지되었습니다. "
        "승인으로 해제하거나 우회하지 말고 정확한 명령·대상·영향을 사용자에게 양도하세요."
    )


READ_ONLY_GIT_SUBCOMMANDS = frozenset(
    {
        "blame",
        "cat-file",
        "count-objects",
        "describe",
        "diff",
        "diff-tree",
        "for-each-ref",
        "fsck",
        "grep",
        "help",
        "log",
        "ls-files",
        "ls-tree",
        "merge-base",
        "name-rev",
        "rev-list",
        "rev-parse",
        "shortlog",
        "show",
        "show-ref",
        "status",
        "version",
    }
)
SUPPORTED_MUTATING_GIT_SUBCOMMANDS = frozenset(
    {"add", "branch", "checkout", "commit", "fetch", "merge", "restore", "switch", "worktree"}
)


def _config_is_read_only(arguments: tuple[str, ...]) -> bool:
    return any(
        option in arguments
        for option in (
            "--get",
            "--get-all",
            "--get-regexp",
            "--get-urlmatch",
            "--list",
            "-l",
            "--show-origin",
            "--show-scope",
        )
    ) and not any(
        option in arguments
        for option in ("--add", "--unset", "--unset-all", "--rename-section", "--remove-section")
    )


def _remote_is_read_only(arguments: tuple[str, ...]) -> bool:
    positionals = tuple(value for value in arguments[1:] if not value.startswith("-"))
    return not positionals or positionals[0] in {"get-url", "show"}


def _argument_after(arguments: tuple[str, ...], *options: str) -> str:
    for index, value in enumerate(arguments):
        for option in options:
            if value == option:
                return arguments[index + 1] if index + 1 < len(arguments) else ""
            if option.startswith("--") and value.startswith(f"{option}="):
                return value.removeprefix(f"{option}=")
            if option.startswith("-") and not option.startswith("--") and value.startswith(option):
                attached = value[len(option):]
                if attached:
                    return attached
    return ""


def _has_option(arguments: tuple[str, ...], *options: str) -> bool:
    return any(
        value == option
        or (option.startswith("--") and value.startswith(f"{option}="))
        or (
            option.startswith("-")
            and not option.startswith("--")
            and value.startswith(option)
            and len(value) > len(option)
        )
        for value in arguments[1:]
        for option in options
    )


def _has_short_flag(
    arguments: tuple[str, ...],
    flags: frozenset[str],
    value_options: frozenset[str] = frozenset(),
) -> bool:
    """묶인 short option을 값 소비 option 전까지만 해석한다."""

    for value in arguments[1:]:
        if not value.startswith("-") or value.startswith("--"):
            continue
        for flag in value[1:]:
            if flag in flags:
                return True
            if flag in value_options:
                break
    return False


def _symbolic_ref_is_read_only(arguments: tuple[str, ...]) -> bool:
    """`git symbolic-ref <name>` 조회형만 허용하고 HEAD/ref 쓰기는 차단한다."""

    allowed_options = {"-q", "--quiet", "--short", "--no-recurse", "--recurse"}
    positionals: list[str] = []
    after_separator = False
    for value in arguments[1:]:
        if value == "--" and not after_separator:
            after_separator = True
            continue
        if not after_separator and value.startswith("-"):
            if value not in allowed_options:
                return False
            continue
        positionals.append(value)
    return len(positionals) == 1


def _branch_is_read_only(arguments: tuple[str, ...]) -> bool:
    """branch 목록·필터 조회와 ref 변경형을 보수적으로 구분한다."""

    mutating_options = (
        "-c",
        "-C",
        "--copy",
        "-d",
        "-D",
        "--delete",
        "-m",
        "-M",
        "--move",
        "-f",
        "--force",
        "-t",
        "--track",
        "--no-track",
        "-u",
        "--set-upstream-to",
        "--unset-upstream",
        "--edit-description",
        "--create-reflog",
        "--recurse-submodules",
    )
    if _has_option(arguments, *mutating_options) or _has_short_flag(
        arguments,
        frozenset({"c", "C", "d", "D", "m", "M", "f", "t", "u"}),
    ):
        return False

    flag_options = {
        "-a",
        "--all",
        "-r",
        "--remotes",
        "-v",
        "-vv",
        "--verbose",
        "-q",
        "--quiet",
        "-l",
        "--list",
        "-i",
        "--ignore-case",
        "--no-abbrev",
        "--omit-empty",
        "--show-current",
        "--no-color",
        "--no-column",
    }
    value_options = {
        "--abbrev",
        "--color",
        "--column",
        "--contains",
        "--no-contains",
        "--merged",
        "--no-merged",
        "--points-at",
        "--sort",
        "--format",
    }
    listing_options = {
        "-a",
        "--all",
        "-r",
        "--remotes",
        "-l",
        "--list",
        "--show-current",
        "--contains",
        "--no-contains",
        "--merged",
        "--no-merged",
        "--points-at",
    }
    listing_mode = False
    positionals: list[str] = []
    index = 1
    while index < len(arguments):
        value = arguments[index]
        if value == "--":
            positionals.extend(arguments[index + 1:])
            break
        if value in flag_options:
            listing_mode = listing_mode or value in listing_options
            index += 1
            continue
        if value in value_options:
            listing_mode = listing_mode or value in listing_options
            if index + 1 < len(arguments) and not arguments[index + 1].startswith("-"):
                index += 2
            else:
                index += 1
            continue
        if any(value.startswith(f"{option}=") for option in value_options):
            option = value.split("=", maxsplit=1)[0]
            listing_mode = listing_mode or option in listing_options
            index += 1
            continue
        if value.startswith("-") and not value.startswith("--"):
            flags = value[1:]
            if not flags or any(flag not in "arvqli" for flag in flags):
                return False
            listing_mode = listing_mode or any(flag in "arl" for flag in flags)
            index += 1
            continue
        if value.startswith("-"):
            return False
        positionals.append(value)
        index += 1
    return not positionals or listing_mode


def _worktree_is_read_only(arguments: tuple[str, ...]) -> bool:
    """worktree 자체 도움말과 list 조회만 읽기 전용으로 인정한다."""

    if len(arguments) == 1:
        return True
    if arguments[1] != "list":
        return False
    index = 2
    while index < len(arguments):
        value = arguments[index]
        if value in {"--porcelain", "-z", "-v", "--verbose"}:
            index += 1
            continue
        if value == "--expire":
            if index + 1 >= len(arguments):
                return False
            index += 2
            continue
        if value.startswith("--expire=") and value != "--expire=":
            index += 1
            continue
        return False
    return True


def git_arguments_are_read_only(arguments: tuple[str, ...]) -> bool:
    """global option을 제거한 한 Git 호출의 저장소 변경 여부를 판정한다."""

    if not arguments:
        return True
    subcommand = arguments[0]
    if subcommand in READ_ONLY_GIT_SUBCOMMANDS:
        return True
    if subcommand == "config":
        return _config_is_read_only(arguments)
    if subcommand == "remote":
        return _remote_is_read_only(arguments)
    if subcommand == "symbolic-ref":
        return _symbolic_ref_is_read_only(arguments)
    if subcommand == "branch":
        return _branch_is_read_only(arguments)
    if subcommand == "worktree":
        return _worktree_is_read_only(arguments)
    return False


def git_command_mutates(command: str) -> bool:
    """shell 문자열의 Git 호출 중 하나라도 변경형·미분류이면 True를 반환한다."""

    for raw_arguments in _git_commands(command):
        arguments = _strip_git_global_options(raw_arguments)
        if arguments is None or arguments == ("<unparsed>",):
            return True
        if not git_arguments_are_read_only(arguments):
            return True
    return False


def _fetch_denial(arguments: tuple[str, ...]) -> str | None:
    """일반 remote fetch는 허용하되 local ref 강제 갱신·삭제형은 거부한다."""

    dangerous_options = (
        "-f",
        "--force",
        "-p",
        "--prune",
        "--prune-tags",
        "--refmap",
        "--update-head-ok",
    )
    if _has_option(arguments, *dangerous_options) or _has_short_flag(
        arguments,
        frozenset({"f", "p"}),
        frozenset({"j", "o"}),
    ):
        return "raw git fetch의 강제 ref 갱신·삭제 옵션은 사용할 수 없습니다. 사용자에게 양도하세요."
    for value in arguments[1:]:
        if value.startswith("+") or ":" in value:
            return (
                "local ref를 직접 갱신할 수 있는 git fetch refspec은 사용할 수 없습니다. "
                "remote 또는 조회할 ref만 지정하세요."
            )
    return None


def _commit_has_pathspec(arguments: tuple[str, ...]) -> bool:
    """메시지 옵션 값과 실제 commit pathspec을 보수적으로 구분한다."""

    value_options = {
        "-m",
        "--message",
        "-F",
        "--file",
        "--author",
        "--date",
        "--cleanup",
        "--trailer",
        "-C",
        "--reuse-message",
        "-c",
        "--reedit-message",
        "--fixup",
        "--squash",
        "-t",
        "--template",
        "--untracked-files",
    }
    short_value_options = {"m", "F", "C", "c", "t"}
    index = 1
    while index < len(arguments):
        value = arguments[index]
        if value == "--":
            return bool(arguments[index + 1:])
        if not value.startswith("-"):
            return True
        if value in value_options:
            index += 2
            continue
        if value.startswith("--"):
            index += 1
            continue
        cluster = value[1:]
        consuming = next(
            (
                (offset, flag)
                for offset, flag in enumerate(cluster)
                if flag in short_value_options or flag == "S"
            ),
            None,
        )
        if consuming is not None and consuming[1] != "S" and consuming[0] == len(cluster) - 1:
            index += 2
        else:
            index += 1
    return False


def _last_positional(arguments: tuple[str, ...]) -> str:
    for value in reversed(arguments):
        if not value.startswith("-"):
            return value
    return ""


def _creation_denial(root: Path, arguments: tuple[str, ...]) -> str | None:
    subcommand = arguments[0]
    if subcommand == "switch":
        if _has_option(arguments, "-C", "--force-create"):
            return "기존 브랜치를 덮어쓰는 git switch -C는 금지합니다."
        branch = _argument_after(arguments, "-c", "--create")
    elif subcommand == "checkout":
        if _has_option(arguments, "-B"):
            return "기존 브랜치를 덮어쓰는 git checkout -B는 금지합니다."
        branch = _argument_after(arguments, "-b")
    else:
        branch = ""
    if not branch:
        return None
    denial = _new_branch_denial(root, branch)
    if denial is not None:
        return denial
    return "새 작업 브랜치는 승인 후 branch_workflow.py create 명령으로 생성하세요."


def _new_branch_denial(root: Path, branch: str) -> str | None:
    if changed_paths(root):
        return (
            "dirty worktree에서는 현재 작업 트리에 새 브랜치를 만들 수 없습니다. "
            "기존 변경을 임의로 commit, stash, reset, restore하지 마세요. "
            "관련 없는 작업은 branch_workflow.py proposal/create 승인 계약에 "
            "저장소 밖의 --worktree 경로를 포함하세요."
        )
    if TASK_BRANCH_PATTERN.fullmatch(branch) is None:
        return f"새 작업 브랜치명은 task/<ascii-kebab-summary> 형식이어야 합니다: {branch}"
    if branch_exists(root, branch):
        return f"이미 존재하는 브랜치입니다: {branch}"
    if task_state(root, branch) == "CLOSED":
        return f"감사 이력을 보존하기 위해 CLOSED 기록이 있는 task 이름을 재사용할 수 없습니다: {branch}"
    return None


def _is_checkout_path_operation(arguments: tuple[str, ...]) -> bool:
    return bool(arguments and arguments[0] == "checkout" and "--" in arguments)


def _switches_branch(arguments: tuple[str, ...]) -> bool:
    if not arguments:
        return False
    if arguments[0] == "switch":
        return True
    return arguments[0] == "checkout" and not _is_checkout_path_operation(arguments)


def _shell_repository_context_denial(command: str) -> str | None:
    """guard가 추적하지 못하는 shell cwd·Git 환경 우회를 fail-closed한다."""

    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|")
        lexer.whitespace_split = True
        lexer.commenters = ""
        tokens = list(lexer)
    except ValueError:
        return "shell 저장소 문맥을 안전하게 해석할 수 없습니다. 명령을 한 단계로 분리하세요."
    has_git = any(os.path.basename(token) == "git" for token in tokens)
    if not has_git:
        return None
    separators = {";", "&&", "||", "|", "&"}
    segments: list[list[str]] = [[]]
    for token in tokens:
        if token in separators:
            segments.append([])
        else:
            segments[-1].append(token)
    for segment in segments:
        if not segment:
            continue
        command_index = next(
            (
                index
                for index, token in enumerate(segment)
                if token not in {"command"}
                and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", token) is None
            ),
            None,
        )
        if command_index is not None and Path(segment[command_index]).name in {"cd", "pushd", "popd"}:
            return (
                "cd/pushd/popd와 Git 변경을 한 shell 명령에 섞을 수 없습니다. "
                "도구 workdir 또는 명시적인 git -C를 사용하세요."
            )
        git_index = next(
            (index for index, token in enumerate(segment) if os.path.basename(token) == "git"),
            None,
        )
        if git_index is None:
            continue
        prefixes = segment[:git_index]
        if any(
            re.fullmatch(r"(?:GIT_DIR|GIT_WORK_TREE)=.+", token) is not None
            for token in prefixes
        ):
            return (
                "GIT_DIR/GIT_WORK_TREE 환경 변수로 저장소 대상을 바꿀 수 없습니다. "
                "검증 가능한 git -C 또는 --git-dir/--work-tree 형식을 사용하세요."
            )
        if "env" in prefixes and any(
            token == "-C" or token.startswith("--chdir=") for token in prefixes
        ):
            return (
                "env -C로 Git 실행 위치를 숨길 수 없습니다. 도구 workdir 또는 git -C를 사용하세요."
            )
    return None


def branch_selection_denial(
    root: Path,
    branch: str,
    base_branch: str = BASE_BRANCH,
) -> str | None:
    """전환할 local branch가 승인된 계보인지 실제 전환 전에 확인한다."""

    if not branch or branch == base_branch:
        return None
    if TASK_BRANCH_PATTERN.fullmatch(branch) is None:
        return f"승인 계약이 없는 branch로 전환할 수 없습니다: {branch}"
    lineage_problem = _lineage_denial(root, branch, base_branch)
    if lineage_problem is not None:
        return lineage_problem
    values = metadata(root, branch)
    state = str(values.get("state") or "")
    if state != "ACTIVE":
        return f"V3 task {branch}는 ACTIVE 상태에서만 전환할 수 있습니다. 현재 상태: {state or '없음'}"
    approved_worktree = str(values.get("worktree") or "")
    if approved_worktree and Path(approved_worktree).expanduser().resolve() != root.resolve():
        return (
            f"V3 task {branch}는 승인된 격리 worktree에서만 사용할 수 있습니다: "
            f"{Path(approved_worktree).expanduser().resolve()}"
        )
    return None


def _pathspecs_after_separator(arguments: tuple[str, ...]) -> tuple[str, ...]:
    if "--" not in arguments:
        return ()
    start = arguments.index("--") + 1
    return tuple(value for value in arguments[start:] if value)


def _merge_denial(root: Path, arguments: tuple[str, ...], base_branch: str) -> str | None:
    if any(option in arguments for option in ("--abort", "--continue", "--quit")):
        return (
            "raw git merge의 abort/continue/quit는 승인된 V3 완료 상태를 우회할 수 있습니다. "
            "현재 merge 상태와 영향을 사용자에게 보고하고 다음 조치를 양도하세요."
        )
    source = _last_positional(arguments[1:])
    if not source or not branch_exists(root, source):
        return "merge할 source 작업 브랜치를 확인할 수 없습니다."
    values = metadata(root, source)
    version_problem = _v3_contract_denial(source, values)
    if version_problem is not None:
        return version_problem
    missing = _missing_metadata(values)
    if missing:
        return f"merge source {source}의 승인 메타데이터가 없습니다: {', '.join(missing)}"
    return (
        "V3 task branch는 raw git merge로 통합할 수 없습니다. "
        "승인된 branch_workflow.py finish → verify → close 절차를 사용하세요."
    )


def _deletion_denial(root: Path, arguments: tuple[str, ...]) -> str | None:
    if "-D" in arguments:
        return "작업 브랜치 강제 삭제(git branch -D)는 금지합니다."
    if "-d" not in arguments and "--delete" not in arguments:
        if any(option in arguments for option in ("-m", "-M", "--move")):
            return "승인 메타데이터와 이름이 분리되므로 작업 브랜치 rename은 금지합니다."
        return None
    option = "-d" if "-d" in arguments else "--delete"
    start = arguments.index(option) + 1
    candidates = tuple(value for value in arguments[start:] if not value.startswith("-"))
    for branch in candidates:
        values = metadata(root, branch)
        version_problem = _v3_contract_denial(branch, values)
        if version_problem is not None:
            return version_problem
        return "V3 task branch 정리는 승인된 branch_workflow.py close에서만 수행합니다."
    return None


def command_denial(
    root: Path,
    command: str,
    base_branch: str = BASE_BRANCH,
    host: str = "",
    execution_cwd: Path | None = None,
    expected_branch: str = "",
) -> str | None:
    """각 Git 호출의 실제 대상 worktree에서 계보·scope·소유권을 확인한다."""

    if not enabled(base_branch):
        return None
    hidden_never_denial = _never_agent_git_text_denial(command)
    if hidden_never_denial is not None:
        return hidden_never_denial
    invocations = git_invocations(root, command, execution_cwd)
    if invocations is None:
        return "Git 명령의 대상 저장소를 안전하게 해석할 수 없어 실행을 차단했습니다. 명령을 단순한 한 단계로 분리하세요."
    if invocations:
        context_denial = _shell_repository_context_denial(command)
        if context_denial is not None:
            return context_denial
    git_commands = tuple(invocation.arguments for invocation in invocations)
    if any(_switches_branch(arguments) for arguments in git_commands) and len(
        tuple(arguments for arguments in git_commands if arguments)
    ) > 1:
        return (
            "브랜치 전환과 다른 Git 작업을 한 복합 명령으로 실행할 수 없습니다. "
            "전환 결과와 실제 worktree를 확인한 뒤 다음 Git 작업을 별도 명령으로 실행하세요."
        )

    for invocation in invocations:
        arguments = invocation.arguments
        if not arguments:
            continue
        never_denial = _never_agent_git_denial(arguments)
        if never_denial is not None:
            return never_denial
        subcommand = arguments[0]
        if subcommand == "config":
            if not _config_is_read_only(arguments):
                return (
                    "raw git config 쓰기는 branch 계약을 변조할 수 있어 차단했습니다. "
                    "계약 metadata는 승인된 branch_workflow.py만 변경할 수 있습니다."
                )
            continue
        if subcommand == "remote":
            if not _remote_is_read_only(arguments):
                return "Git remote 설정 변경은 에이전트가 수행하지 않습니다. 사용자에게 양도하세요."
            continue
        if subcommand == "symbolic-ref":
            if not _symbolic_ref_is_read_only(arguments):
                return (
                    "git symbolic-ref 쓰기는 HEAD 또는 ref를 우회 변경할 수 있어 차단했습니다. "
                    "현재 branch 조회형만 사용할 수 있습니다."
                )
            continue
        if git_arguments_are_read_only(arguments):
            continue
        if subcommand not in READ_ONLY_GIT_SUBCOMMANDS | SUPPORTED_MUTATING_GIT_SUBCOMMANDS | {
            "config",
            "remote",
            "symbolic-ref",
            "reset",
            "stash",
            "rebase",
            "cherry-pick",
            "pull",
            "revert",
            "am",
            "apply",
        }:
            return (
                f"git {subcommand} 명령의 안전한 효과를 분류할 수 없어 차단했습니다. "
                "지원되는 단순 명령으로 분리하거나 사용자가 직접 실행하세요."
            )
        if subcommand in {"reset", "stash", "rebase", "cherry-pick", "pull", "revert", "am", "apply"}:
            return f"브랜치 계보를 임의 변경할 수 있어 git {subcommand} 명령을 차단했습니다."
        operation_root = invocation.root
        if invocation.unsafe_repository_options:
            return (
                "Git 저장소 대상을 우회할 수 있는 global option은 변경 명령에 사용할 수 없습니다: "
                + ", ".join(invocation.unsafe_repository_options)
            )
        if not same_git_repository(root, operation_root):
            return (
                "현재 소비자 프로젝트와 다른 Git 저장소를 변경할 수 없습니다.\n"
                f"  세션 저장소: {root.resolve()}\n"
                f"  명령 대상: {operation_root}"
            )
        if subcommand in {"add", "commit", "restore"} and expected_branch:
            actual_branch = current_branch(operation_root)
            if not assignment_allows_branch_mutation(
                operation_root,
                expected_branch,
                actual_branch,
                base_branch,
            ):
                lineage_problem = _lineage_denial(
                    operation_root,
                    actual_branch,
                    base_branch,
                    allow_merged=True,
                    required_ancestor=expected_branch,
                )
                if lineage_problem is not None:
                    return lineage_problem
                return (
                    "현재 세션의 assignment 권한 계보와 Git 변경 대상 branch가 다릅니다.\n"
                    f"  권한 root: {expected_branch}\n"
                    f"  명령 대상: {actual_branch or 'detached HEAD'} ({operation_root})"
                )
        if subcommand == "fetch":
            denial = _fetch_denial(arguments)
            if denial is not None:
                return denial
            continue
        if subcommand in {"switch", "checkout"}:
            unsafe_switch_options = (
                "--detach",
                "--discard-changes",
                "-f",
                "--force",
                "--orphan",
                "--merge",
                "-m",
                "--conflict",
                "--track",
                "-t",
                "--no-track",
                "--ignore-other-worktrees",
            )
            short_value_options = (
                frozenset({"c", "C"})
                if subcommand == "switch"
                else frozenset({"b", "B"})
            )
            combined_creation_option = any(
                value.startswith("-")
                and not value.startswith("--")
                and len(value) > 2
                and any(flag in value[1:] for flag in short_value_options)
                for value in arguments[1:]
            )
            if (
                _has_option(arguments, *unsafe_switch_options)
                or _has_short_flag(
                    arguments,
                    frozenset({"f", "m", "p", "t"}),
                    short_value_options,
                )
                or combined_creation_option
                or "-" in arguments[1:]
            ):
                return (
                    f"git {subcommand}의 detached/강제/암시적 생성·변경 병합 옵션은 사용할 수 없습니다. "
                    "명시적인 local branch만 전환하세요."
                )
            if subcommand == "checkout" and _has_option(arguments, "-p", "--patch"):
                return "파일 대화형 복원은 git checkout이 아니라 scope를 적은 git restore를 사용하세요."
            if _is_checkout_path_operation(arguments):
                return (
                    "git checkout -- <path>는 브랜치 전환과 구분하기 어렵습니다. "
                    "파일 복원은 git restore -- <path>를 사용하세요."
                )
            denial = _creation_denial(operation_root, arguments)
            if denial is not None:
                return denial
            target_branch = _last_positional(arguments[1:])
            if target_branch and not branch_exists(operation_root, target_branch):
                return f"전환 대상을 local branch로 확인할 수 없습니다: {target_branch}"
            denial = branch_selection_denial(operation_root, target_branch, base_branch)
            if denial is not None:
                return denial
            current = current_branch(operation_root)
            if (
                expected_branch
                and target_branch
                and not assignment_allows_branch_mutation(
                    operation_root,
                    expected_branch,
                    target_branch,
                    base_branch,
                )
                and task_state(operation_root, expected_branch) != "CLOSED"
            ):
                return (
                    f"현재 세션의 assignment 권한 root({expected_branch})가 CLOSED 상태가 아니므로 "
                    "권한 계보 밖의 branch로 전환할 수 없습니다."
                )
            integrator_branch = current
            if integrator_branch == base_branch and branch_exists(operation_root, target_branch):
                integrator_branch = target_branch
            denial = git_integrator_denial(operation_root, integrator_branch, host)
            if denial is not None:
                return denial
            if target_branch and target_branch != integrator_branch:
                denial = git_integrator_denial(operation_root, target_branch, host)
                if denial is not None:
                    return denial
            if not _argument_after(arguments, "-c", "--create", "-b") and changed_paths(operation_root):
                return "dirty worktree에서는 브랜치를 전환할 수 없습니다."
        elif subcommand == "branch":
            combined_branch_mutation = any(
                value.startswith("-")
                and not value.startswith("--")
                and len(value) > 2
                and any(flag in value[1:] for flag in "ftumMcdDC")
                for value in arguments[1:]
            )
            if combined_branch_mutation:
                return "묶이거나 값이 붙은 raw git branch 변경 옵션은 사용할 수 없습니다."
            unsupported_branch_options = {
                "--edit-description",
                "--set-upstream-to",
                "--set-upstream",
                "-u",
                "--unset-upstream",
                "--track",
                "-t",
                "--no-track",
                "--force",
                "-f",
                "--create-reflog",
                "--recurse-submodules",
            }
            if _has_option(arguments, *unsupported_branch_options):
                return "raw git branch metadata 변경은 승인된 branch workflow 밖에서 수행할 수 없습니다."
            denial = _deletion_denial(operation_root, arguments)
            if denial is not None:
                return denial
            if "-d" in arguments or "--delete" in arguments:
                option = "-d" if "-d" in arguments else "--delete"
                start = arguments.index(option) + 1
                for candidate in tuple(value for value in arguments[start:] if not value.startswith("-")):
                    denial = git_integrator_denial(operation_root, candidate, host)
                    if denial is not None:
                        return denial
            if any(option in arguments for option in ("-c", "-C", "--copy")):
                return "승인 메타데이터가 분리될 수 있어 git branch copy는 금지합니다."
            if len(arguments) > 1 and not arguments[1].startswith("-"):
                denial = _new_branch_denial(operation_root, arguments[1])
                if denial is not None:
                    return denial
                return "새 작업 브랜치는 승인 후 branch_workflow.py create 명령으로 생성하세요."
        elif subcommand == "worktree":
            operation = next((value for value in arguments[1:] if not value.startswith("-")), "")
            if operation == "add":
                return "격리 worktree는 승인 계약에 경로를 포함해 branch_workflow.py create로 생성하세요."
            if operation in {"remove", "prune"}:
                return "V3 worktree 정리는 승인된 branch_workflow.py close에서만 수행합니다."
            if operation not in {"", "list"}:
                return f"git worktree {operation}은 승인된 branch workflow 밖에서 수행할 수 없습니다."
            if "--force" in arguments or "-f" in arguments:
                return "worktree 강제 작업은 자동 복구가 어려워 금지합니다."
        elif subcommand == "restore":
            denial = git_integrator_denial(
                operation_root,
                current_branch(operation_root),
                host,
            )
            if denial is not None:
                return denial
            targets = _pathspecs_after_separator(arguments)
            if not targets:
                return "git restore는 대상 오인을 막기 위해 git restore ... -- <path> 형식으로 실행하세요."
            denial = active_branch_denial(operation_root, targets, base_branch, host)
            if denial is not None:
                return denial
        elif subcommand == "merge":
            source = _last_positional(arguments[1:])
            denial = git_integrator_denial(operation_root, source, host)
            if denial is not None:
                return denial
            denial = _merge_denial(operation_root, arguments, base_branch)
            if denial is not None:
                return denial
        elif subcommand in {"add", "commit"}:
            if subcommand == "add" and _has_option(
                arguments,
                "--pathspec-from-file",
                "--pathspec-file-nul",
            ):
                return "검사할 수 없는 git add pathspec 파일은 사용할 수 없습니다. `git add -- <path>`를 사용하세요."
            if subcommand == "add" and "--" not in arguments and any(
                not value.startswith("-") for value in arguments[1:]
            ):
                return "git add 대상은 오인을 막기 위해 `git add ... -- <path>` 형식으로 지정하세요."
            if subcommand == "commit" and any(
                option == "--amend" or option.startswith("--fixup=reword:")
                for option in arguments[1:]
            ):
                return "기존 commit을 다시 쓰는 git commit 옵션은 사용할 수 없습니다."
            if subcommand == "commit" and (
                _has_option(
                    arguments,
                    "-a",
                    "--all",
                    "-i",
                    "--include",
                    "-o",
                    "--only",
                    "--pathspec-from-file",
                    "--pathspec-file-nul",
                )
                or _has_short_flag(
                    arguments,
                    frozenset({"a", "i", "o"}),
                    frozenset({"m", "F", "C", "c", "t", "S"}),
                )
                or _commit_has_pathspec(arguments)
            ):
                return (
                    "git commit이 unstaged path를 암시적으로 포함하면 scope·산출물 소유권을 검증할 수 없습니다. "
                    "먼저 `git add -- <path>`로 stage한 뒤 pathspec 없는 commit을 사용하세요."
                )
            denial = git_integrator_denial(
                operation_root,
                current_branch(operation_root),
                host,
            )
            if denial is not None:
                return denial
            explicit_paths = _pathspecs_after_separator(arguments) if subcommand == "add" else ()
            ownership_paths = (
                tuple(dict.fromkeys((*changed_paths(operation_root), *explicit_paths)))
                if subcommand == "add"
                else staged_paths(operation_root)
            )
            if GIT_STATUS_UNAVAILABLE in ownership_paths:
                return "Git 변경 상태를 확인할 수 없어 artifact 소유권 검증을 중단했습니다."
            if host:
                denial = artifact_write_denial(ownership_paths, host)
                if denial is not None:
                    return denial
            denial = active_branch_denial(
                operation_root,
                explicit_paths,
                base_branch=base_branch,
                host=host,
            )
            if denial is not None:
                return denial
    return None


def pre_tool_denial(
    root: Path,
    command: str,
    targets: tuple[str, ...],
    shell_command: bool,
    base_branch: str = BASE_BRANCH,
    host: str = "",
    execution_cwd: Path | None = None,
    expected_branch: str = "",
) -> str | None:
    if shell_command and command:
        denial = command_denial(
            root,
            command,
            base_branch,
            host,
            execution_cwd,
            expected_branch,
        )
        if denial is not None:
            return denial
    if targets:
        return active_branch_denial(root, targets, base_branch, host)
    return None


def branch_context(root: Path, base_branch: str = BASE_BRANCH) -> str:
    """compact와 session resume 뒤 모델에 다시 넣을 최신 브랜치 컨텍스트를 만든다."""

    if not enabled(base_branch):
        return ""
    branch = current_branch(root)
    current_head = head(root)
    dirty = changed_paths(root)
    lines = [
        "[BRANCH_CONTEXT]",
        f"- 기준 브랜치: {base_branch}",
        f"- 현재 브랜치: {branch or 'detached HEAD'}",
        f"- 현재 HEAD: {current_head[:12] if current_head else '없음'}",
        f"- dirty 상태: {'있음' if dirty else '없음'}",
    ]
    if dirty:
        preview = ", ".join(dirty[:10])
        suffix = f" 외 {len(dirty) - 10}개" if len(dirty) > 10 else ""
        lines.append(f"- 변경 경로: {preview}{suffix}")
    if not branch or branch == base_branch:
        lines.extend(("- 작업 목적: 기준 브랜치", "- 직접 merge 대상: 없음", "- 다음 안전 조치: 변경 작업이면 새 작업 브랜치 승인을 요청"))
        return "\n".join(lines)

    values = metadata(root, branch)
    scopes = values.get("scope")
    roles = values.get("roles")
    contract_version = str(values.get("contract-version") or "")
    contract_label = f"V{contract_version}" if contract_version else "V1(무버전)"
    lines.extend(
        (
            f"- 작업 목적: {values.get('purpose') or '메타데이터 없음'}",
            f"- branch 계약: {contract_label}",
            f"- 확인된 역할: {', '.join(roles) if isinstance(roles, tuple) and roles else '기록 없음'}",
            f"- Git 통합 담당자: {values.get('git-integrator') or '기록 없음'}",
            (
                f"- task 상태: {values.get('state') or '메타데이터 없음'}"
                if contract_version == CONTRACT_VERSION
                else "- 변경 권한: 없음 (V3 계약 재승인 필요)"
            ),
            f"- 분기 기준: {values.get('parent') or '메타데이터 없음'}",
            f"- 승인 시점 부모 HEAD: {str(values.get('parent-head') or '없음')[:12]}",
            f"- 직접 merge 대상: {values.get('merge-target') or '메타데이터 없음'}",
            f"- 승인된 작업 경로: {', '.join(scopes) if isinstance(scopes, tuple) and scopes else '메타데이터 없음'}",
        )
    )
    target = str(values.get("merge-target") or "")
    approved_parent_head = str(values.get("parent-head") or "")
    branch_head = head(root, branch)
    merged = bool(
        target
        and branch_exists(root, target)
        and branch_head
        and branch_head != approved_parent_head
        and is_ancestor(root, branch, target)
    )
    lines.append(f"- merge 상태: {'merge됨' if merged else '미병합'}")
    worktree = str(values.get("worktree") or "")
    if worktree:
        lines.append(f"- 격리 worktree: {worktree}")
    children = unmerged_children(root, branch)
    lines.append(f"- 미병합 자식 브랜치: {', '.join(children) if children else '없음'}")
    lines.append("- 상위 브랜치 계보:")
    cursor = branch
    seen: set[str] = set()
    for _ in range(MAX_LINEAGE_DEPTH):
        if cursor == base_branch:
            lines.append(f"  - {base_branch}: 기준 브랜치")
            break
        if cursor in seen:
            lines.append(f"  - {cursor}: 계보 순환 감지")
            break
        seen.add(cursor)
        entry = metadata(root, cursor)
        lines.append(
            f"  - {cursor}: {entry.get('purpose') or '목적 없음'} / "
            f"추후 {entry.get('merge-target') or '대상 없음'}으로 merge"
        )
        parent = str(entry.get("parent") or "")
        if not parent:
            break
        cursor = parent
    lines.append(
        "- 다음 안전 조치: "
        + ("사후 검증 후 안전 삭제 검토" if merged else "현재 작업 완료 후 merge 승인 요청")
    )
    return "\n".join(lines)
