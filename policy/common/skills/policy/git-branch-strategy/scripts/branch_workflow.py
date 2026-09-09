#!/usr/bin/env python3
"""승인할 브랜치 계약을 출력하고 승인 후 동일한 계약으로 브랜치를 만든다."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import subprocess
import tempfile
from pathlib import Path
from types import ModuleType


INJECT_MODE_ENV = "ASAN_AGENT_POLICY_MODE"
REQUIRED_GUARD_ATTRIBUTES = (
    "ALLOWED_VALIDATION_COMMANDS",
    "ALLOWED_ROLES",
    "BASE_BRANCH",
    "CONTRACT_VERSION",
    "INTEGRATOR_PATTERN",
    "TASK_BRANCH_PATTERN",
    "FULL_SHA_PATTERN",
    "MAX_LINEAGE_DEPTH",
    "RUNTIME_CONTRACT",
)
REQUIRED_GUARD_CALLABLES = (
    "active_branch_denial",
    "assignment_allows_branch_mutation",
    "branch_context",
    "branch_exists",
    "changed_paths",
    "current_branch",
    "enabled",
    "head",
    "metadata",
    "proposal_id",
    "task_state",
    "canonical_contract",
    "contract_bytes",
    "contract_sha256",
    "is_ancestor",
    "unmerged_children",
)


def repository_root() -> Path:
    completed = subprocess.run(
        ("git", "rev-parse", "--show-toplevel"),
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise SystemExit("Git 저장소에서 실행해야 합니다.")
    return Path(completed.stdout.strip()).resolve()


def snapshot_guard_candidates() -> tuple[Path, ...]:
    """현재 세션에 주입된 중앙 정책 번들의 guard 경로만 반환한다."""

    if os.environ.get(INJECT_MODE_ENV) != "inject":
        return ()
    bundle_root = os.environ.get("ASAN_AGENT_POLICY_BUNDLE_ROOT", "").strip()
    if not bundle_root:
        return ()
    return (Path(bundle_root).resolve() / ".agent-policy/runtime/branch_guard.py",)


def guard_contract_issues(module: ModuleType) -> tuple[str, ...]:
    issues: list[str] = []
    for name in REQUIRED_GUARD_ATTRIBUTES:
        if not hasattr(module, name):
            issues.append(name)
    for name in ("TASK_BRANCH_PATTERN", "FULL_SHA_PATTERN"):
        value = getattr(module, name, None)
        if value is not None and not callable(getattr(value, "fullmatch", None)):
            issues.append(name)
    if hasattr(module, "BASE_BRANCH") and not isinstance(module.BASE_BRANCH, str):
        issues.append("BASE_BRANCH")
    if hasattr(module, "MAX_LINEAGE_DEPTH") and not isinstance(module.MAX_LINEAGE_DEPTH, int):
        issues.append("MAX_LINEAGE_DEPTH")
    for name in REQUIRED_GUARD_CALLABLES:
        if not callable(getattr(module, name, None)):
            issues.append(name)
    return tuple(issues)


def import_guard(source: Path) -> ModuleType:
    # runtime_loader와 동일하게 원본만 읽는다. immutable bundle에 pyc를 만들거나 읽지 않는다.
    module = ModuleType("asan_branch_guard")
    module.__file__ = str(source)
    exec(compile(source.read_bytes(), str(source), "exec"), module.__dict__)
    return module


def load_guard(root: Path) -> ModuleType:
    del root
    snapshot_candidates = snapshot_guard_candidates()
    diagnostics: list[str] = []
    for source in snapshot_candidates:
        if not source.is_file():
            diagnostics.append(f"- 없음: {source}")
            continue
        try:
            module = import_guard(source)
        except Exception as error:  # pragma: no cover - 구체 오류는 실행 환경에 따라 다름
            diagnostics.append(f"- 로드 실패: {source} ({type(error).__name__}: {error})")
            break
        issues = guard_contract_issues(module)
        if not issues:
            return module
        diagnostics.append(f"- 호환되지 않음: {source} (계약 오류: {', '.join(issues)})")
        break

    detail = "\n".join(diagnostics) if diagnostics else "- 중앙 inject 번들 환경이 없습니다."
    raise SystemExit(
        "중앙 inject 정책 스냅샷에서 호환되는 branch_guard.py를 찾을 수 없습니다.\n"
        f"{detail}\n"
        "중앙 agent-policy start로 새 inject 세션을 시작하세요. 소비자 정책 파일로 fallback하지 않습니다."
    )


def git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ("git", *arguments),
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = "\n".join(part.strip() for part in (completed.stdout, completed.stderr) if part.strip())
        raise SystemExit(detail or f"git {' '.join(arguments)} 실행에 실패했습니다.")
    return completed.stdout.strip()


def git_common_directory(root: Path) -> Path:
    raw = git(root, "rev-parse", "--git-common-dir")
    candidate = Path(raw)
    return (candidate if candidate.is_absolute() else root / candidate).resolve()


def workflow_state_root(root: Path) -> Path:
    return git_common_directory(root) / "asan-agent-policy"


def proposal_file(root: Path, digest: str) -> Path:
    return workflow_state_root(root) / "proposals" / f"{digest}.json"


def finish_proposal_file(root: Path, digest: str) -> Path:
    return workflow_state_root(root) / "finish-proposals" / f"{digest}.json"


def write_immutable_contract(
    destination: Path,
    contract: dict[str, object],
    guard: ModuleType,
    temporary_prefix: str,
) -> tuple[Path, str]:
    payload = guard.contract_bytes(contract)
    digest = hashlib.sha256(payload).hexdigest()
    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if destination.exists():
        if destination.is_symlink() or not destination.is_file() or destination.read_bytes() != payload:
            raise SystemExit(f"동일 SHA의 proposal 파일이 안전하지 않습니다: {destination}")
        return destination, digest
    descriptor, temporary_name = tempfile.mkstemp(prefix=temporary_prefix, dir=destination.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.chmod(0o600)
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)
    return destination, digest


def write_immutable_proposal(root: Path, contract: dict[str, object], guard: ModuleType) -> tuple[Path, str]:
    digest = guard.contract_sha256(contract)
    return write_immutable_contract(proposal_file(root, digest), contract, guard, ".proposal-")


def write_immutable_finish_proposal(
    root: Path,
    contract: dict[str, object],
    guard: ModuleType,
) -> tuple[Path, str]:
    digest = guard.contract_sha256(contract)
    return write_immutable_contract(
        finish_proposal_file(root, digest),
        contract,
        guard,
        ".finish-",
    )


def load_approved_proposal(
    root: Path,
    raw_path: str,
    expected_digest: str,
    guard: ModuleType,
) -> dict[str, object]:
    if not re_full_sha256(expected_digest):
        raise SystemExit("--proposal-sha256에는 64자리 전체 SHA-256을 사용해야 합니다.")
    source = Path(raw_path).expanduser().resolve()
    expected = proposal_file(root, expected_digest).resolve()
    if source != expected:
        raise SystemExit(f"proposal 파일은 Git 공용 상태의 승인 경로여야 합니다: {expected}")
    if source.is_symlink() or not source.is_file():
        raise SystemExit(f"승인 proposal 파일을 찾을 수 없습니다: {source}")
    payload = source.read_bytes()
    actual_digest = hashlib.sha256(payload).hexdigest()
    if actual_digest != expected_digest:
        raise SystemExit(
            "승인 proposal SHA-256이 파일 내용과 일치하지 않습니다.\n"
            f"  승인: {expected_digest}\n"
            f"  현재: {actual_digest}"
        )
    try:
        value = json.loads(payload)
    except json.JSONDecodeError as error:
        raise SystemExit(f"proposal JSON을 읽을 수 없습니다: {error}") from error
    if not isinstance(value, dict) or value.get("version") != int(guard.CONTRACT_VERSION):
        raise SystemExit("지원하지 않는 branch proposal 계약입니다.")
    if guard.contract_bytes(value) != payload:
        raise SystemExit("proposal JSON이 canonical 직렬화 형식과 일치하지 않습니다.")
    if guard.contract_sha256(value) != expected_digest:
        raise SystemExit("proposal 계약 digest를 재계산할 수 없습니다.")
    return value


def load_finish_proposal(
    root: Path,
    raw_path: str,
    expected_digest: str,
    guard: ModuleType,
) -> dict[str, object]:
    if not re_full_sha256(expected_digest):
        raise SystemExit("--proposal-sha256에는 64자리 전체 SHA-256을 사용해야 합니다.")
    source = Path(raw_path).expanduser().resolve()
    expected = finish_proposal_file(root, expected_digest).resolve()
    if source != expected or source.is_symlink() or not source.is_file():
        raise SystemExit(f"승인 finish proposal 파일을 찾을 수 없습니다: {expected}")
    payload = source.read_bytes()
    actual = hashlib.sha256(payload).hexdigest()
    if actual != expected_digest:
        raise SystemExit(f"finish proposal SHA-256 불일치: 승인={expected_digest}, 현재={actual}")
    try:
        value = json.loads(payload)
    except json.JSONDecodeError as error:
        raise SystemExit(f"finish proposal JSON을 읽을 수 없습니다: {error}") from error
    if (
        not isinstance(value, dict)
        or value.get("version") != int(guard.CONTRACT_VERSION)
        or value.get("kind") != "finish"
        or guard.contract_bytes(value) != payload
    ):
        raise SystemExit("finish proposal canonical 계약이 올바르지 않습니다.")
    return value


def re_full_sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def branch_worktrees(root: Path, branch: str) -> tuple[Path, ...]:
    output = git(root, "worktree", "list", "--porcelain")
    paths: list[Path] = []
    current_path: Path | None = None
    for line in (*output.splitlines(), ""):
        if line.startswith("worktree "):
            current_path = Path(line.removeprefix("worktree ")).resolve()
        elif line == f"branch refs/heads/{branch}" and current_path is not None:
            paths.append(current_path)
        elif not line:
            current_path = None
    return tuple(paths)


def dirty_branch_worktrees(root: Path, branch: str) -> tuple[Path, ...]:
    dirty: list[Path] = []
    for worktree in branch_worktrees(root, branch):
        completed = subprocess.run(
            ("git", "status", "--porcelain=v1", "-z", "--untracked-files=all"),
            cwd=worktree,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            raise SystemExit(f"parent worktree 상태를 확인할 수 없습니다: {worktree}")
        if completed.stdout:
            dirty.append(worktree)
    return tuple(dirty)


def normalized_worktree(root: Path, raw_path: str | None) -> str:
    if not raw_path:
        return ""
    candidate = Path(raw_path)
    target = (candidate if candidate.is_absolute() else root / candidate).resolve()
    if any(character in str(target) for character in ("\n", "\r", "|")):
        raise SystemExit("격리 worktree 경로에는 줄바꿈이나 | 문자를 사용할 수 없습니다.")
    try:
        target.relative_to(root)
    except ValueError:
        pass
    else:
        raise SystemExit("격리 worktree는 현재 저장소 작업 트리 밖의 경로여야 합니다.")
    if target.exists():
        raise SystemExit(f"격리 worktree 대상 경로가 이미 존재합니다: {target}")
    return str(target)


def normalized_roles(guard: ModuleType, raw_roles: list[str]) -> tuple[str, ...]:
    roles = tuple(sorted(dict.fromkeys(role.strip().casefold() for role in raw_roles if role.strip())))
    if not roles:
        raise SystemExit("하나 이상의 --role을 지정해야 합니다.")
    invalid = tuple(role for role in roles if role not in tuple(guard.ALLOWED_ROLES))
    if invalid:
        raise SystemExit(f"지원하지 않는 역할입니다: {', '.join(invalid)}")
    return roles


def validate_role_contract(arguments: argparse.Namespace, guard: ModuleType) -> tuple[tuple[str, ...], str]:
    roles = normalized_roles(guard, arguments.role)
    integrator = arguments.git_integrator.strip().casefold()
    if guard.INTEGRATOR_PATTERN.fullmatch(integrator) is None:
        raise SystemExit("--git-integrator는 codex, claude, opencode 또는 user여야 합니다.")
    return roles, integrator


def lineage(guard: ModuleType, root: Path, branch: str) -> tuple[str, ...]:
    base_branch = str(guard.BASE_BRANCH)
    lines: list[str] = []
    cursor = branch
    seen: set[str] = set()
    for _ in range(int(guard.MAX_LINEAGE_DEPTH)):
        if cursor == base_branch:
            lines.append(f"  - {base_branch}: 기준 브랜치")
            break
        if cursor in seen:
            lines.append(f"  - {cursor}: 계보 순환 감지")
            break
        seen.add(cursor)
        values = guard.metadata(root, cursor)
        lines.append(
            f"  - {cursor}: {values.get('purpose') or '등록된 목적 없음'}, "
            f"추후 {values.get('merge-target') or '등록된 대상 없음'}으로 merge"
        )
        parent = str(values.get("parent") or "")
        if not parent:
            break
        cursor = parent
    return tuple(lines)


def proposal(arguments: argparse.Namespace, guard: ModuleType, root: Path) -> int:
    if not arguments.purpose.strip():
        raise SystemExit("--purpose는 공백이 아닌 작업 목적이어야 합니다.")
    if not arguments.reason.strip():
        raise SystemExit("--reason은 공백이 아닌 분기 판단 근거여야 합니다.")
    if any(not scope.strip() for scope in arguments.scope):
        raise SystemExit("--scope에는 공백이 아닌 상대 경로를 지정해야 합니다.")
    parent = arguments.parent or guard.current_branch(root)
    if not parent or not guard.branch_exists(root, parent):
        raise SystemExit(f"분기 기준 브랜치를 찾을 수 없습니다: {parent or '없음'}")
    if guard.TASK_BRANCH_PATTERN.fullmatch(arguments.branch) is None:
        raise SystemExit("브랜치명은 task/<ascii-kebab-summary> 형식이어야 합니다.")
    if guard.branch_exists(root, arguments.branch):
        raise SystemExit(f"이미 존재하는 브랜치입니다: {arguments.branch}")
    if guard.task_state(root, arguments.branch) == "CLOSED":
        raise SystemExit(
            f"이미 CLOSED 기록이 있는 task 이름은 재사용할 수 없습니다: {arguments.branch}"
        )
    dirty = guard.changed_paths(root)
    if getattr(guard, "GIT_STATUS_UNAVAILABLE", "") in dirty:
        raise SystemExit("Git 변경 상태를 확인할 수 없어 branch proposal을 만들 수 없습니다.")
    parent_head = guard.head(root, parent)
    if guard.FULL_SHA_PATTERN.fullmatch(parent_head) is None:
        raise SystemExit(f"분기 기준 HEAD를 40자리 전체 SHA로 확인할 수 없습니다: {parent_head or '없음'}")
    worktree = normalized_worktree(root, arguments.worktree)
    roles, integrator = validate_role_contract(arguments, guard)
    dirty_parent_worktrees = dirty_branch_worktrees(root, parent)
    if parent != str(guard.BASE_BRANCH) and dirty_parent_worktrees:
        rendered = ", ".join(str(path) for path in dirty_parent_worktrees)
        raise SystemExit(
            "task parent에 commit되지 않은 변경이 있어 child branch 기준을 확정할 수 없습니다.\n"
            f"  parent: {parent}\n"
            f"  dirty worktree: {rendered}\n"
            "변경 소유자가 parent 작업을 commit하거나 handoff로 보존한 뒤 다시 proposal 하세요."
        )
    if parent != str(guard.BASE_BRANCH) and guard.task_state(root, parent) != "ACTIVE":
        raise SystemExit(
            "ACTIVE 상태의 task parent에서만 child branch를 제안할 수 있습니다.\n"
            f"  parent: {parent}\n"
            f"  현재 상태: {guard.task_state(root, parent) or '없음'}"
        )
    merge_target = parent
    contract = guard.canonical_contract(
        arguments.branch,
        arguments.purpose,
        parent,
        parent_head,
        merge_target,
        tuple(arguments.scope),
        arguments.reason,
        worktree,
        roles,
        integrator,
    )
    proposal_path, digest = write_immutable_proposal(root, contract, guard)
    identifier = f"asan-v3:{digest}"
    current = guard.current_branch(root) or "detached HEAD"
    scope_lines = "\n".join(f"  - {scope}" for scope in arguments.scope)
    ancestry = "\n".join(lineage(guard, root, parent))
    print(
        "\n".join(
            (
                "[브랜치 생성 승인 요청]",
                f"- 작업 목적: {arguments.purpose}",
                f"- 분기 기준: {parent}",
                f"- 분기 기준 HEAD: {parent_head}",
                f"- 새 브랜치: {arguments.branch}",
                f"- 직접 merge 대상: {merge_target}",
                f"- 확인된 역할: {', '.join(roles)}",
                f"- Git 통합 담당자: {integrator}",
                "- 산출물 책임: branch가 아닌 start 시 session assignment에서 owner/contributor로 지정",
                f"- 생성 방식: {'격리 worktree' if worktree else '현재 worktree 전환'}",
                f"- 격리 worktree 경로: {worktree or '없음'}",
                f"- 승인 요청 식별자: {identifier}",
                f"- canonical proposal 파일: {proposal_path}",
                f"- canonical proposal SHA-256: {digest}",
                "- 예정 작업 경로:",
                scope_lines,
                "- 상위 브랜치 계보:",
                ancestry,
                f"- 분기 판단 근거: {arguments.reason}",
                f"- 현재 상태: {current}, dirty={'있음' if dirty else '없음'}",
                "",
                "이 계약으로 브랜치를 생성해도 될까요?",
            )
        )
    )
    if dirty and worktree:
        print("\n현재 worktree의 기존 변경은 건드리지 않고 승인된 경로에 격리 worktree를 생성합니다.")
    elif dirty:
        print(
            "\n주의: dirty worktree에서는 현재 작업 트리를 전환할 수 없습니다. "
            "저장소 밖의 승인할 경로를 --worktree로 지정해 다시 proposal 하세요."
        )
    return 0


def create(arguments: argparse.Namespace, guard: ModuleType, root: Path) -> int:
    contract = load_approved_proposal(
        root,
        arguments.proposal_file,
        arguments.proposal_sha256,
        guard,
    )
    try:
        branch = str(contract["branch"])
        purpose = str(contract["purpose"])
        parent = str(contract["parent"])
        parent_head = str(contract["parent_head"])
        merge_target = str(contract["merge_target"])
        reason = str(contract["reason"])
        worktree_value = str(contract.get("worktree") or "")
        roles_value = contract["roles"]
        scopes_value = contract["scopes"]
        integrator = str(contract["git_integrator"])
    except KeyError as error:
        raise SystemExit(f"proposal 필드가 누락되었습니다: {error}") from error
    if not isinstance(roles_value, list) or not all(isinstance(role, str) for role in roles_value):
        raise SystemExit("proposal roles가 올바르지 않습니다.")
    if not isinstance(scopes_value, list) or not all(isinstance(scope, str) for scope in scopes_value):
        raise SystemExit("proposal scopes가 올바르지 않습니다.")
    roles = normalized_roles(guard, list(roles_value))
    scopes = tuple(scopes_value)
    if guard.INTEGRATOR_PATTERN.fullmatch(integrator) is None:
        raise SystemExit("proposal Git 통합 담당자가 올바르지 않습니다.")
    worktree = normalized_worktree(root, worktree_value or None)
    canonical = guard.canonical_contract(
        branch,
        purpose,
        parent,
        parent_head,
        merge_target,
        scopes,
        reason,
        worktree,
        roles,
        integrator,
    )
    if canonical != contract:
        raise SystemExit("proposal 필드가 canonical branch 계약과 일치하지 않습니다.")
    assert_creation_owner(root, Path(worktree) if worktree else root, guard)
    changed = guard.changed_paths(root)
    if getattr(guard, "GIT_STATUS_UNAVAILABLE", "") in changed:
        raise SystemExit("Git 변경 상태를 확인할 수 없어 branch 생성을 중단했습니다.")
    if changed and not worktree:
        raise SystemExit(
            "dirty worktree에서는 현재 작업 트리를 전환할 수 없습니다. "
            "승인 계약에 격리 --worktree 경로를 포함하세요."
        )
    if guard.TASK_BRANCH_PATTERN.fullmatch(branch) is None:
        raise SystemExit("브랜치명은 task/<ascii-kebab-summary> 형식이어야 합니다.")
    if guard.branch_exists(root, branch):
        raise SystemExit(f"이미 존재하는 브랜치입니다: {branch}")
    if guard.task_state(root, branch) == "CLOSED":
        raise SystemExit(f"승인 뒤 CLOSED 기록이 확인되어 task 이름을 재사용할 수 없습니다: {branch}")
    if parent != merge_target:
        raise SystemExit("proposal의 parent와 직접 merge 대상이 다릅니다.")
    if not guard.branch_exists(root, parent):
        raise SystemExit(f"분기 기준 브랜치를 찾을 수 없습니다: {parent}")
    if guard.FULL_SHA_PATTERN.fullmatch(parent_head) is None:
        raise SystemExit("--parent-head에는 40자리 전체 SHA를 사용해야 합니다.")
    actual_parent_head = guard.head(root, parent)
    if actual_parent_head != parent_head:
        raise SystemExit(
            "승인 이후 부모 HEAD가 변경되었습니다.\n"
            f"  승인: {parent_head}\n"
            f"  현재: {actual_parent_head}\n"
            "새 계약으로 다시 승인받으세요."
        )
    dirty_parent_worktrees = dirty_branch_worktrees(root, parent)
    if parent != str(guard.BASE_BRANCH) and dirty_parent_worktrees:
        raise SystemExit("승인 후 task parent worktree가 dirty 상태가 되어 branch 생성을 중단했습니다.")
    if parent != str(guard.BASE_BRANCH) and guard.task_state(root, parent) != "ACTIVE":
        raise SystemExit(
            "승인 후 task parent가 ACTIVE 상태가 아니어서 child branch 생성을 중단했습니다.\n"
            f"  parent: {parent}\n"
            f"  현재 상태: {guard.task_state(root, parent) or '없음'}"
        )

    active_root = root
    if worktree:
        _ = git(root, "worktree", "add", "-b", branch, worktree, parent_head)
        active_root = Path(worktree)
    else:
        _ = git(root, "switch", "-c", branch, parent_head)
    for field, value in (
        ("contract-version", str(guard.CONTRACT_VERSION)),
        ("task-id", branch.removeprefix("task/")),
        ("purpose", purpose),
        ("parent", parent),
        ("parent-head", parent_head),
        ("merge-target", merge_target),
        ("proposal", f"asan-v3:{arguments.proposal_sha256}"),
        ("contract-sha256", arguments.proposal_sha256),
        ("reason", reason),
        ("git-integrator", integrator),
        ("state", "ACTIVE"),
    ):
        _ = git(root, "config", f"branch.{branch}.asan-{field}", value)
    if worktree:
        _ = git(root, "config", f"branch.{branch}.asan-worktree", worktree)
    for role in roles:
        _ = git(root, "config", "--add", f"branch.{branch}.asan-role", role)
    for scope in scopes:
        _ = git(root, "config", "--add", f"branch.{branch}.asan-scope", scope)

    denial = guard.active_branch_denial(active_root, (), str(guard.BASE_BRANCH))
    if denial is not None:
        raise SystemExit(f"브랜치는 생성됐지만 계약 검증에 실패했습니다:\n{denial}")
    if worktree:
        print(
            "격리 worktree가 생성되었습니다. 현재 session assignment의 권한 root 또는 "
            "그 V3 자손에서 만든 branch라면 "
            f"도구 workdir 또는 git -C 대상으로 이 경로를 사용해 계속 진행하세요: {worktree}\n"
            "권한 계보 밖의 독립 task를 병행하거나 담당자를 인계할 때만 handoff 후 새 세션을 시작합니다.\n"
        )
    print(guard.branch_context(active_root, str(guard.BASE_BRANCH)))
    return 0


def _active_branch_contract(
    guard: ModuleType,
    root: Path,
) -> tuple[str, dict[str, object], dict[str, object]]:
    branch = guard.current_branch(root)
    if not branch or guard.TASK_BRANCH_PATTERN.fullmatch(branch) is None:
        raise SystemExit("scope 변경은 현재 V3 task branch에서 실행해야 합니다.")
    values = guard.metadata(root, branch)
    if values.get("contract-version") != str(guard.CONTRACT_VERSION):
        raise SystemExit("scope 변경은 V3 task branch에서만 사용할 수 있습니다.")
    if values.get("state") != "ACTIVE":
        raise SystemExit(
            f"ACTIVE task의 scope만 변경할 수 있습니다: {values.get('state') or '없음'}"
        )
    roles_value = values.get("roles")
    scopes_value = values.get("scope")
    if not isinstance(roles_value, tuple) or not roles_value:
        raise SystemExit("현재 branch의 승인 역할을 확인할 수 없습니다.")
    if not isinstance(scopes_value, tuple) or not scopes_value:
        raise SystemExit("현재 branch의 승인 scope를 확인할 수 없습니다.")
    if not guard.assignment_allows_branch_mutation(root, branch, branch, str(guard.BASE_BRANCH)):
        raise SystemExit("현재 branch의 V3 계보 계약이 유효하지 않습니다.")
    approved_worktree = str(values.get("worktree") or "")
    if approved_worktree and Path(approved_worktree).expanduser().resolve() != root.resolve():
        raise SystemExit(f"scope 변경은 승인된 worktree에서 실행해야 합니다: {approved_worktree}")

    contract = guard.canonical_contract(
        branch,
        str(values.get("purpose") or ""),
        str(values.get("parent") or ""),
        str(values.get("parent-head") or ""),
        str(values.get("merge-target") or ""),
        scopes_value,
        str(values.get("reason") or ""),
        approved_worktree,
        roles_value,
        str(values.get("git-integrator") or ""),
    )
    digest = guard.contract_sha256(contract)
    if values.get("contract-sha256") != digest or values.get("proposal") != f"asan-v3:{digest}":
        raise SystemExit("현재 branch metadata가 승인된 canonical V3 계약과 일치하지 않습니다.")
    return branch, values, contract


def scope_proposal(arguments: argparse.Namespace, guard: ModuleType, root: Path) -> int:
    if any(not scope.strip() for scope in arguments.scope):
        raise SystemExit("--scope에는 공백이 아닌 상대 경로를 지정해야 합니다.")
    branch, _, current = _active_branch_contract(guard, root)
    proposed = guard.canonical_contract(
        branch,
        str(current["purpose"]),
        str(current["parent"]),
        str(current["parent_head"]),
        str(current["merge_target"]),
        tuple(arguments.scope),
        str(current["reason"]),
        str(current.get("worktree") or ""),
        tuple(str(role) for role in current["roles"]),
        str(current["git_integrator"]),
    )
    if proposed["scopes"] == current["scopes"]:
        raise SystemExit("요청 scope가 현재 승인 scope와 같습니다.")
    proposal_path, digest = write_immutable_proposal(root, proposed, guard)
    current_lines = "\n".join(f"  - {scope}" for scope in current["scopes"])
    proposed_lines = "\n".join(f"  - {scope}" for scope in proposed["scopes"])
    print(
        "\n".join(
            (
                "[브랜치 scope 변경 승인 요청]",
                f"- 브랜치: {branch}",
                "- 현재 승인 scope:",
                current_lines,
                "- 변경할 승인 scope:",
                proposed_lines,
                f"- 승인 요청 식별자: asan-v3:{digest}",
                f"- canonical proposal 파일: {proposal_path}",
                f"- canonical proposal SHA-256: {digest}",
                "",
                "이 scope 계약 변경을 적용해도 될까요?",
            )
        )
    )
    return 0


def _replace_config_values(root: Path, key: str, values: tuple[str, ...]) -> None:
    completed = subprocess.run(
        ("git", "config", "--unset-all", key),
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode not in {0, 5}:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise SystemExit(detail or f"Git config를 초기화할 수 없습니다: {key}")
    for value in values:
        _ = git(root, "config", "--add", key, value)


def update_scope(arguments: argparse.Namespace, guard: ModuleType, root: Path) -> int:
    proposed = load_approved_proposal(
        root,
        arguments.proposal_file,
        arguments.proposal_sha256,
        guard,
    )
    branch, values, current = _active_branch_contract(guard, root)
    if proposed.get("branch") != branch:
        raise SystemExit(
            f"scope proposal branch와 현재 branch가 다릅니다: {proposed.get('branch')} != {branch}"
        )
    for key, value in current.items():
        if key != "scopes" and proposed.get(key) != value:
            raise SystemExit(f"scope 변경 proposal이 기존 branch 계약의 {key} 필드를 변경합니다.")
    if set(proposed) != set(current):
        raise SystemExit("scope 변경 proposal의 canonical 필드 구성이 기존 branch 계약과 다릅니다.")
    proposed_scopes_value = proposed.get("scopes")
    if not isinstance(proposed_scopes_value, list) or not all(
        isinstance(scope, str) and scope for scope in proposed_scopes_value
    ):
        raise SystemExit("scope 변경 proposal의 scopes가 올바르지 않습니다.")
    proposed_scopes = tuple(proposed_scopes_value)
    old_scopes = tuple(str(scope) for scope in current["scopes"])
    if proposed_scopes == old_scopes:
        raise SystemExit("scope 변경 proposal이 현재 계약과 같습니다.")

    scope_key = f"branch.{branch}.asan-scope"
    old_proposal = str(values.get("proposal") or "")
    old_digest = str(values.get("contract-sha256") or "")
    try:
        _replace_config_values(root, scope_key, proposed_scopes)
        _ = git(root, "config", f"branch.{branch}.asan-proposal", f"asan-v3:{arguments.proposal_sha256}")
        _ = git(root, "config", f"branch.{branch}.asan-contract-sha256", arguments.proposal_sha256)
        denial = guard.active_branch_denial(root, (), str(guard.BASE_BRANCH))
        if denial is not None:
            raise SystemExit(f"변경할 scope가 현재 branch 상태를 승인하지 못합니다:\n{denial}")
    except BaseException:
        _replace_config_values(root, scope_key, old_scopes)
        _ = git(root, "config", f"branch.{branch}.asan-proposal", old_proposal)
        _ = git(root, "config", f"branch.{branch}.asan-contract-sha256", old_digest)
        raise

    print(f"{branch}의 승인 scope를 갱신했습니다: {', '.join(proposed_scopes)}")
    return 0


def _clean_worktree(guard: ModuleType, root: Path) -> None:
    changed = guard.changed_paths(root)
    unavailable = getattr(guard, "GIT_STATUS_UNAVAILABLE", "")
    if unavailable in changed:
        raise SystemExit(f"Git 변경 상태를 확인할 수 없습니다: {root}")
    if changed:
        preview = ", ".join(changed[:10])
        raise SystemExit(f"dirty worktree에서는 완료 작업을 진행할 수 없습니다: {preview}")


def _validation_argv(
    raw_commands: list[str],
    guard: ModuleType,
) -> tuple[tuple[str, ...], ...]:
    commands: list[tuple[str, ...]] = []
    for raw in raw_commands:
        try:
            tokens = tuple(shlex.split(raw, posix=True))
        except ValueError as error:
            raise SystemExit(f"검증 명령을 해석할 수 없습니다: {raw}: {error}") from error
        if not tokens:
            raise SystemExit("빈 --verify-command는 사용할 수 없습니다.")
        if tokens not in tuple(guard.ALLOWED_VALIDATION_COMMANDS):
            allowed = ", ".join(shlex.join(command) for command in guard.ALLOWED_VALIDATION_COMMANDS)
            raise SystemExit(
                "검증 명령은 프로젝트 공통 계약에 등록된 정확한 argv만 사용할 수 있습니다.\n"
                f"  요청: {shlex.join(tokens)}\n"
                f"  허용: {allowed or '없음'}"
            )
        commands.append(tokens)
    if not commands:
        raise SystemExit("하나 이상의 --verify-command를 지정해야 합니다.")
    return tuple(commands)


def validate_cleanup_layout(contract: dict[str, object]) -> None:
    worktree = str(contract.get("worktree") or "")
    integration = str(contract.get("integration_worktree") or "")
    if contract.get("cleanup") is True and worktree and integration and Path(worktree).resolve() == Path(integration).resolve():
        raise SystemExit(
            "통합 worktree를 cleanup 대상으로 함께 지정할 수 없습니다. "
            "별도 target worktree를 준비하거나 --cleanup 없이 완료 계약을 제안하세요. "
            "이미 MERGED_VERIFIED인 계약은 중앙 close-recover로 정리 보류를 검토하세요."
        )


def finish_proposal(arguments: argparse.Namespace, guard: ModuleType, root: Path) -> int:
    source = arguments.source or guard.current_branch(root)
    if not source or not guard.branch_exists(root, source):
        raise SystemExit(f"완료할 source branch를 찾을 수 없습니다: {source or '없음'}")
    values = guard.metadata(root, source)
    if values.get("contract-version") != str(guard.CONTRACT_VERSION):
        raise SystemExit("finish workflow는 V3 branch 계약에서만 사용할 수 있습니다.")
    if values.get("state") != "ACTIVE":
        raise SystemExit(f"ACTIVE task만 완료 제안할 수 있습니다. 현재 상태: {values.get('state') or '없음'}")
    if guard.current_branch(root) != source:
        raise SystemExit(f"finish proposal은 source worktree에서 실행해야 합니다: {source}")
    _clean_worktree(guard, root)
    lineage_denial = guard.active_branch_denial(root, (), str(guard.BASE_BRANCH))
    if lineage_denial is not None:
        raise SystemExit(lineage_denial)
    target = str(values.get("merge-target") or "")
    if not target or not guard.branch_exists(root, target):
        raise SystemExit(f"직접 merge 대상을 찾을 수 없습니다: {target or '없음'}")
    source_head = guard.head(root, source)
    parent_head = str(values.get("parent-head") or "")
    if source_head == parent_head:
        raise SystemExit("source branch에 완료할 commit이 없습니다.")
    children = guard.unmerged_children(root, source)
    if children:
        raise SystemExit(f"미병합 자식 branch를 먼저 처리해야 합니다: {', '.join(children)}")
    validation = _validation_argv(arguments.verify_command, guard)
    contract: dict[str, object] = {
        "version": int(guard.CONTRACT_VERSION),
        "kind": "finish",
        "source": source,
        "source_head": source_head,
        "target": target,
        "target_head": guard.head(root, target),
        "finish_schema": 1,
        "merge_strategy": arguments.merge_strategy,
        "integration_worktree": str((branch_worktrees(root, target) or (root.resolve(),))[0]),
        "source_worktree": str(root.resolve()),
        "validation_commands": [list(command) for command in validation],
        "cleanup": bool(arguments.cleanup),
        "worktree": str(values.get("worktree") or ""),
        "branch_contract_sha256": str(values.get("contract-sha256") or ""),
    }
    validate_cleanup_layout(contract)
    path, digest = write_immutable_finish_proposal(root, contract, guard)
    print(
        "\n".join(
            (
                "[브랜치 완료 승인 요청]",
                f"- source: {source}@{source_head}",
                f"- target: {target}@{contract['target_head']}",
                f"- merge 방식: {contract.get('merge_strategy')}",
                f"- 통합 worktree: {contract.get('integration_worktree')}",
                "- 검증 명령:",
                *(f"  - {shlex.join(command)}" for command in validation),
                f"- merge 후 local cleanup: {'수행' if arguments.cleanup else '보존'}",
                f"- finish proposal 파일: {path}",
                f"- finish proposal SHA-256: {digest}",
                "",
                "이 계약으로 merge, 사후 검증과 close를 진행해도 될까요?",
            )
        )
    )
    return 0


def _finish_fields(contract: dict[str, object]) -> tuple[str, str, str, str]:
    try:
        return (
            str(contract["source"]),
            str(contract["source_head"]),
            str(contract["target"]),
            str(contract["target_head"]),
        )
    except KeyError as error:
        raise SystemExit(f"finish proposal 필드가 누락되었습니다: {error}") from error


def integration_state(guard: ModuleType) -> ModuleType:
    return import_guard(Path(guard.__file__).with_name("runtime_state.py"))


def assert_creation_owner(root: Path, destination: Path, guard: ModuleType) -> None:
    state = integration_state(guard)
    common = git_common_directory(root)
    owner = os.environ.get("ASAN_AGENT_POLICY_ASSIGNMENT", "manual")
    resource = "git:" + str(destination.resolve())
    with state.locked(state.repository_state(common) / "events.lock"):
        claim = state.read(state.repository_state(common) / "claims" / f"{state.digest(resource)}.json")
        if claim and claim.get("owner") != owner:
            raise SystemExit("Git worktree의 통합 소유자가 다른 assignment입니다. 인계 또는 별도 worktree가 필요합니다.")
        for path in (workflow_state_root(root) / "integration-targets").glob("*.json"):
            if state.read(path).get("worktree") == str(destination.resolve()):
                raise SystemExit("이 worktree의 병합 검증·close가 미완료입니다. 먼저 완료 또는 명시적 복구를 수행하세요.")
        if os.environ.get("ASAN_AGENT_POLICY_ASSIGNMENT"):
            state.claim(common, resource, owner)


def integration_record_path(root: Path, contract: dict[str, object], guard: ModuleType) -> Path:
    return workflow_state_root(root) / "integrations" / f"{guard.contract_sha256(contract)}.json"


def integration_root(root: Path, contract: dict[str, object], guard: ModuleType) -> Path:
    selected = Path(str(contract.get("integration_worktree") or root)).resolve()
    if not selected.is_dir() or git_common_directory(selected) != git_common_directory(root):
        raise SystemExit("승인된 통합 worktree가 같은 Git 저장소에 존재하지 않습니다.")
    if Path(git(selected, "rev-parse", "--show-toplevel")).resolve() != selected:
        raise SystemExit("통합 실행 위치가 worktree root가 아닙니다.")
    return selected


def target_reservation(root: Path, contract: dict[str, object], guard: ModuleType) -> Path:
    return workflow_state_root(root) / "integration-targets" / f"{guard.contract_sha256({'target': contract['target']})}.json"


def integration_head(root: Path, contract: dict[str, object], guard: ModuleType) -> str:
    state = integration_state(guard)
    record = state.read(integration_record_path(root, contract, guard))
    if not record and not contract.get("finish_schema"):
        # 구형 ff-only 승인 계약의 호환 경로.
        return str(contract["source_head"])
    if record.get("finish_sha256") != guard.contract_sha256(contract):
        raise SystemExit("승인된 완료 계약의 병합 실행 기록이 없습니다.")
    result = str(record.get("integration_head") or "")
    if not guard.FULL_SHA_PATTERN.fullmatch(result):
        raise SystemExit("병합 결과 HEAD를 확인할 수 없습니다. 통합 복구가 필요합니다.")
    return result


def assert_integration_owner(root: Path, contract: dict[str, object], guard: ModuleType) -> None:
    state = integration_state(guard)
    reservation = state.read(target_reservation(root, contract, guard))
    owner = os.environ.get("ASAN_AGENT_POLICY_ASSIGNMENT", "manual")
    if reservation and (reservation.get("owner") != owner or reservation.get("finish_sha256") != guard.contract_sha256(contract)):
        raise SystemExit("통합 예약을 소유한 assignment만 finish/verify/close를 실행할 수 있습니다.")
    receipt = state.read(integration_record_path(root, contract, guard))
    if contract.get("finish_schema") and receipt and not reservation and receipt.get("state") not in {"closed", "aborted"}:
        raise SystemExit("통합 예약이 없습니다. 실행 기록을 복구한 뒤 재개하세요.")
    claim = state.read(state.repository_state(git_common_directory(root)) / "claims" / f"{state.digest('git:' + str(root.resolve()))}.json")
    if os.environ.get("ASAN_AGENT_POLICY_ASSIGNMENT") and claim and claim.get("owner") != owner:
        raise SystemExit("다른 assignment가 Git worktree를 소유하고 있습니다.")


def expected_merge_result(root: Path, contract: dict[str, object], guard: ModuleType) -> bool:
    result = guard.head(root, str(contract["target"]))
    if contract.get("merge_strategy") == "ff-only":
        return result == contract["source_head"]
    parents = git(root, "rev-list", "--parents", "-n", "1", result).split()[1:]
    return parents == [contract["target_head"], contract["source_head"]]


def collect_before_cleanup(root: Path, candidate: Path, contract: dict[str, object], guard: ModuleType) -> None:
    """worktree를 제거하기 전에 모든 host의 세션 로그를 중앙으로 수집한다."""
    prefixes = [value["artifact_root"] for value in guard.RUNTIME_CONTRACT["hosts"].values()]
    if not any((candidate / prefix).is_dir() for prefix in prefixes):
        return
    environment = dict(os.environ)
    environment.pop("ASAN_AGENT_POLICY_ASSIGNMENT", None)
    environment["ASAN_AGENT_POLICY_PROJECT_PATH"] = str(candidate)
    try:
        result = subprocess.run(["{{CENTRAL_ROOT}}/bin/agent-policy", "collect-logs", "--project", "{{PROJECT_ID}}",
                                 "--channel", "all", "--quiet"], env=environment, cwd=root,
                                capture_output=True, text=True, timeout=60, check=False)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise SystemExit(f"정리 전 로그 수집 실패: {error}") from error
    if result.returncode:
        raise SystemExit("정리 전 로그 수집 실패. worktree를 보존합니다.\n" + result.stderr)
    state = integration_state(guard)
    # 다른 assignment의 로그도 정리 전 수집되었다는 출처 기록을 보존한다.
    with state.locked(state.repository_state(git_common_directory(root)) / "events.lock"):
        for path in (state.repository_state(git_common_directory(root)) / "assignments").glob("*/artifact-sources.json"):
            record = state.read(path)
            archived = record.setdefault("archived", {})
            for source in record.get("sources", []):
                if Path(source).is_relative_to(candidate):
                    archived[source] = {"finish_sha256": guard.contract_sha256(contract)}
            state.write(path, record)


def release_closed_git_claims(root: Path, contract: dict[str, object], guard: ModuleType) -> None:
    owner = os.environ.get("ASAN_AGENT_POLICY_ASSIGNMENT")
    if not owner:
        return
    state = integration_state(guard)
    common = git_common_directory(root)
    source_root = Path(str(contract.get("source_worktree") or contract.get("worktree") or root)).resolve()
    candidates = {source_root, root.resolve()}
    with state.locked(state.repository_state(common) / "events.lock"):
        for candidate in candidates:
            current = guard.current_branch(candidate) if candidate.exists() else ""
            if current.startswith("task/") and guard.task_state(root, current) not in {"CLOSED", ""}:
                continue
            resource = "git:" + str(candidate)
            path = state.repository_state(common) / "claims" / f"{state.digest(resource)}.json"
            if state.read(path).get("owner") == owner:
                path.unlink()


def finish(arguments: argparse.Namespace, guard: ModuleType, root: Path) -> int:
    contract = load_finish_proposal(root, arguments.proposal_file, arguments.proposal_sha256, guard)
    source, source_head, target, target_head = _finish_fields(contract)
    root = integration_root(root, contract, guard)
    state = integration_state(guard)
    receipt_path = integration_record_path(root, contract, guard)
    reservation = target_reservation(root, contract, guard)
    owner = os.environ.get("ASAN_AGENT_POLICY_ASSIGNMENT", "manual")
    previous = state.read(reservation)
    assert_integration_owner(root, contract, guard)
    if previous and (previous.get("finish_sha256") != arguments.proposal_sha256 or previous.get("owner") != owner):
        raise SystemExit("target에 다른 assignment의 완료 작업이 진행 중입니다. 인계 또는 close가 필요합니다.")
    receipt = state.read(receipt_path)
    if receipt.get("integration_head") and guard.head(root, target) == receipt["integration_head"] and guard.head(root, source) == source_head:
        print("이미 기록된 병합입니다. verify를 실행하세요.")
        return 0
    _clean_worktree(guard, root)
    if (receipt.get("state") == "merging" and previous and guard.current_branch(root) == target
            and guard.head(root, source) == source_head and expected_merge_result(root, contract, guard)):
        receipt.update({"integration_head": guard.head(root, target), "state": "merged",
                        "strategy": contract["merge_strategy"], "worktree": str(root)})
        state.write(receipt_path, receipt)
        git(root, "config", f"branch.{source}.asan-state", "READY_TO_MERGE")
        print("실제 Git 결과와 승인 계약을 대조하여 병합 실행 기록을 복구했습니다. verify를 실행하세요.")
        return 0
    validate_cleanup_layout(contract)
    if guard.head(root, source) != source_head or guard.head(root, target) != target_head:
        raise SystemExit("승인 후 source 또는 target HEAD가 변경되었습니다. 새 finish proposal이 필요합니다.")
    values = guard.metadata(root, source)
    if values.get("contract-sha256") != contract.get("branch_contract_sha256"):
        raise SystemExit("source branch 계약이 finish proposal과 일치하지 않습니다.")
    if values.get("state") not in {"ACTIVE", "READY_TO_MERGE"}:
        raise SystemExit(f"finish를 실행할 수 없는 task 상태입니다: {values.get('state') or '없음'}")
    strategy = contract.get("merge_strategy")
    if strategy not in {"ff-only", "merge-commit"} or (strategy == "merge-commit" and contract.get("finish_schema") != 1):
        raise SystemExit("승인 계약의 merge 방식을 지원하지 않습니다.")
    current = guard.current_branch(root)
    if current != target and (current != source or not contract.get("finish_schema") or branch_worktrees(root, target)):
        raise SystemExit(f"승인된 target 전환을 수행할 수 없습니다: {target}")
    if strategy == "merge-commit" and guard.is_ancestor(root, source_head, target_head):
        raise SystemExit("이미 target에 포함된 source입니다. 추가 merge commit을 만들 수 없습니다.")
    state.write(reservation, {"finish_sha256": arguments.proposal_sha256, "owner": owner, "source": source,
                              "target": target, "worktree": str(root)})
    state.write(receipt_path, {"finish_sha256": arguments.proposal_sha256, "owner": owner,
                               "source_head": source_head, "target_head": target_head, "state": "merging"})
    if current != target:
        git(root, "switch", target)
    git(root, "config", f"branch.{source}.asan-state", "READY_TO_MERGE")
    try:
        if strategy == "ff-only":
            git(root, "merge", "--ff-only", source_head)
        else:
            git(root, "merge", "--no-ff", "--no-edit", source_head)
    except SystemExit as error:
        raise SystemExit("merge 실패: source·worktree·통합 예약을 보존했습니다. 충돌 해결 또는 승인된 복구가 필요합니다.\n" + str(error)) from error
    receipt = state.read(receipt_path)
    receipt.update({"integration_head": guard.head(root, target), "state": "merged", "strategy": strategy,
                    "worktree": str(root)})
    state.write(receipt_path, receipt)
    print(f"{source}를 {target}에 {strategy} merge했습니다. verify를 별도 실행하세요.")
    return 0


def record_verification_failure(root: Path, contract: dict[str, object], guard: ModuleType,
                                command: list[str], exit_code: int | None, error: str = "") -> None:
    state = integration_state(guard)
    path = integration_record_path(root, contract, guard)
    receipt = state.read(path)
    receipt["state"] = "merged"
    receipt["verification"] = {"status": "failed", "head": guard.head(root, str(contract["target"])),
                               "command": command, "exit_code": exit_code, "error": error}
    state.write(path, receipt)
    git(root, "config", f"branch.{contract['source']}.asan-state", "READY_TO_MERGE")


def verify(arguments: argparse.Namespace, guard: ModuleType, root: Path) -> int:
    contract = load_finish_proposal(root, arguments.proposal_file, arguments.proposal_sha256, guard)
    source, source_head, target, _ = _finish_fields(contract)
    root = integration_root(root, contract, guard)
    assert_integration_owner(root, contract, guard)
    result_head = integration_head(root, contract, guard)
    if guard.current_branch(root) != target:
        raise SystemExit(f"verify는 target worktree에서 실행해야 합니다: target={target}")
    _clean_worktree(guard, root)
    if (
        guard.head(root, source) != source_head
        or guard.head(root, target) != result_head
        or not guard.is_ancestor(root, source, target)
    ):
        raise SystemExit(
            "승인된 source 또는 기록된 병합 결과 HEAD와 현재 상태가 달라 verify할 수 없습니다."
        )
    values = guard.metadata(root, source)
    if values.get("state") not in {"READY_TO_MERGE", "MERGED_VERIFIED"}:
        raise SystemExit(f"병합 후 상태에서만 verify할 수 있습니다: {values.get('state') or '없음'}")
    if contract.get("merge_strategy") == "merge-commit":
        parents = git(root, "rev-list", "--parents", "-n", "1", result_head).split()[1:]
        if parents != [str(contract["target_head"]), source_head]:
            raise SystemExit("merge commit의 부모가 승인된 target/source HEAD와 다릅니다.")
    raw_commands = contract.get("validation_commands")
    if not isinstance(raw_commands, list) or not raw_commands:
        raise SystemExit("finish proposal의 validation_commands가 올바르지 않습니다.")
    for raw in raw_commands:
        if not isinstance(raw, list) or not raw or not all(isinstance(token, str) for token in raw):
            raise SystemExit("finish proposal의 검증 명령이 올바르지 않습니다.")
        if tuple(raw) not in tuple(guard.ALLOWED_VALIDATION_COMMANDS):
            raise SystemExit("실행할 검증 argv가 공통 계약의 허용 목록과 다릅니다.")
        try:
            completed = subprocess.run(tuple(raw), cwd=root, check=False, timeout=600)
        except (OSError, subprocess.TimeoutExpired) as error:
            record_verification_failure(root, contract, guard, raw, None, str(error))
            raise SystemExit(
                "사후 검증을 실행하지 못했습니다. source와 worktree를 보존합니다.\n"
                f"  명령: {shlex.join(raw)}\n"
                f"  오류: {error}"
            ) from error
        if completed.returncode != 0:
            record_verification_failure(root, contract, guard, raw, completed.returncode)
            raise SystemExit(
                "사후 검증이 실패했습니다. 자동 rollback·삭제 없이 source와 worktree를 보존합니다.\n"
                f"  명령: {shlex.join(raw)}\n"
                f"  exit: {completed.returncode}"
            )
    if guard.head(root, target) != result_head:
        record_verification_failure(root, contract, guard, [], None, "검증 중 target HEAD 변경")
        raise SystemExit("검증 중 target HEAD가 변경되었습니다.")
    try:
        _clean_worktree(guard, root)
    except SystemExit as error:
        record_verification_failure(root, contract, guard, [], None, str(error))
        raise
    state = integration_state(guard)
    receipt_path = integration_record_path(root, contract, guard)
    receipt = state.read(receipt_path)
    receipt.update({"finish_sha256": guard.contract_sha256(contract), "integration_head": result_head,
                    "state": "verified", "validation_commands": raw_commands,
                    "verification": {"status": "passed", "head": result_head}})
    state.write(receipt_path, receipt)
    _ = git(root, "config", f"branch.{source}.asan-state", "MERGED_VERIFIED")
    print(f"{target}에서 사후 검증이 통과했습니다. close를 별도 실행하세요.")
    return 0


def _write_closed_record(root: Path, contract: dict[str, object], guard: ModuleType) -> Path:
    source = str(contract["source"])
    record = {
        "version": int(guard.CONTRACT_VERSION),
        "source": source,
        "source_head": contract["source_head"],
        "target": contract["target"],
        "state": "CLOSED",
        "finish_sha256": guard.contract_sha256(contract),
    }
    destination = workflow_state_root(root) / "closed" / f"{source.removeprefix('task/')}.json"
    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    payload = guard.contract_bytes(record)
    descriptor, temporary_name = tempfile.mkstemp(prefix=".closed-", dir=destination.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.chmod(0o600)
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)
    return destination


def close(arguments: argparse.Namespace, guard: ModuleType, root: Path) -> int:
    contract = load_finish_proposal(root, arguments.proposal_file, arguments.proposal_sha256, guard)
    source, source_head, target, _ = _finish_fields(contract)
    root = integration_root(root, contract, guard)
    assert_integration_owner(root, contract, guard)
    result_head = integration_head(root, contract, guard)
    if guard.current_branch(root) != target:
        raise SystemExit(f"close는 target worktree에서 실행해야 합니다: target={target}")
    _clean_worktree(guard, root)
    if guard.head(root, target) != result_head or not guard.is_ancestor(root, source_head, target):
        raise SystemExit(
            "검증 뒤 target HEAD가 변경되었거나 승인된 source HEAD와 달라 close할 수 없습니다."
        )
    state = integration_state(guard)
    receipt_path = integration_record_path(root, contract, guard)
    receipt = state.read(receipt_path)
    values = guard.metadata(root, source)
    if receipt.get("verification", {}).get("status") == "failed":
        raise SystemExit("최근 사후 검증이 실패했습니다. verify 통과 후 close를 실행하세요.")
    if receipt.get("state") == "closed":
        release_closed_git_claims(root, contract, guard)
        print("이미 CLOSED로 기록된 동일 완료 계약입니다.")
        return 0
    validate_cleanup_layout(contract)
    if receipt.get("state") not in {"verified", "closing"} and values.get("state") != "MERGED_VERIFIED":
        raise SystemExit("MERGED_VERIFIED 상태가 아니므로 close할 수 없습니다. verify를 먼저 실행하세요.")
    if guard.branch_exists(root, source) and guard.head(root, source) != source_head:
        raise SystemExit("검증 뒤 source HEAD가 변경되었습니다.")
    if not guard.branch_exists(root, source) and receipt.get("state") != "closing":
        raise SystemExit("정리 시작 기록 없이 source branch가 사라졌습니다.")
    if contract.get("cleanup") is True:
        worktree = str(contract.get("worktree") or "")
        candidate = Path(worktree).resolve() if worktree else None
        if candidate is not None and candidate.exists():
            if candidate not in branch_worktrees(root, source):
                raise SystemExit("정리할 worktree가 승인된 source branch에 연결되어 있지 않습니다.")
            _clean_worktree(guard, candidate)
            collect_before_cleanup(root, candidate, contract, guard)
        receipt["state"] = "closing"
        state.write(receipt_path, receipt)
        if candidate is not None and candidate.exists():
            git(root, "worktree", "remove", str(candidate))
        if guard.branch_exists(root, source):
            git(root, "branch", "-d", source)
    else:
        git(root, "config", f"branch.{source}.asan-state", "CLOSED")
    record = _write_closed_record(root, contract, guard)
    receipt["state"] = "closed"
    state.write(receipt_path, receipt)
    target_reservation(root, contract, guard).unlink(missing_ok=True)
    release_closed_git_claims(root, contract, guard)
    print(f"작업을 CLOSED로 기록했습니다: {record}")
    return 0


def preserve(arguments: argparse.Namespace, guard: ModuleType, root: Path) -> int:
    branch = guard.current_branch(root)
    if not branch or not guard.branch_exists(root, branch):
        raise SystemExit("보존할 현재 task branch를 확인할 수 없습니다.")
    values = guard.metadata(root, branch)
    if values.get("contract-version") != str(guard.CONTRACT_VERSION):
        raise SystemExit("preserve는 V3 task branch에서만 사용할 수 있습니다.")
    if values.get("state") != "ACTIVE":
        raise SystemExit(f"ACTIVE task만 PRESERVED로 전환할 수 있습니다: {values.get('state') or '없음'}")
    reason = arguments.reason.strip()
    if not reason:
        raise SystemExit("--reason에는 보존·인계 이유를 기록해야 합니다.")
    _ = git(root, "config", f"branch.{branch}.asan-preserve-reason", reason)
    _ = git(root, "config", f"branch.{branch}.asan-state", "PRESERVED")
    print(
        f"{branch}를 PRESERVED로 기록했습니다. 이 worktree는 그대로 보존하고 "
        "다른 작업은 별도 worktree·세션에서 시작하세요."
    )
    return 0


def resume(arguments: argparse.Namespace, guard: ModuleType, root: Path) -> int:
    _ = arguments
    branch = guard.current_branch(root)
    if not branch or not guard.branch_exists(root, branch):
        raise SystemExit("재개할 현재 task branch를 확인할 수 없습니다.")
    values = guard.metadata(root, branch)
    if values.get("contract-version") != str(guard.CONTRACT_VERSION):
        raise SystemExit("resume은 V3 task branch에서만 사용할 수 있습니다.")
    if values.get("state") != "PRESERVED":
        raise SystemExit(f"PRESERVED task만 ACTIVE로 재개할 수 있습니다: {values.get('state') or '없음'}")
    _ = git(root, "config", "--unset-all", f"branch.{branch}.asan-preserve-reason")
    _ = git(root, "config", f"branch.{branch}.asan-state", "ACTIVE")
    print(f"{branch}를 ACTIVE로 재개했습니다. 새 session assignment를 확인하세요.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="승인 기반 작업 브랜치 계약 도구")
    subparsers = parser.add_subparsers(dest="command", required=True)

    proposal_parser = subparsers.add_parser("proposal", help="사용자에게 제시할 분기 계약을 출력")
    _ = proposal_parser.add_argument("--branch", required=True)
    _ = proposal_parser.add_argument("--purpose", required=True)
    _ = proposal_parser.add_argument("--parent")
    _ = proposal_parser.add_argument("--scope", action="append", required=True)
    _ = proposal_parser.add_argument("--reason", required=True)
    _ = proposal_parser.add_argument("--worktree")
    _ = proposal_parser.add_argument("--role", action="append", required=True)
    _ = proposal_parser.add_argument("--git-integrator", required=True)

    create_parser = subparsers.add_parser("create", help="승인된 계약과 동일할 때 브랜치를 생성")
    _ = create_parser.add_argument("--proposal-file", required=True)
    _ = create_parser.add_argument("--proposal-sha256", required=True)

    scope_proposal_parser = subparsers.add_parser(
        "scope-proposal",
        help="현재 V3 branch의 새 전체 scope 계약을 승인 요청",
    )
    _ = scope_proposal_parser.add_argument("--scope", action="append", required=True)

    update_scope_parser = subparsers.add_parser(
        "update-scope",
        help="승인된 전체 SHA-256 계약으로 현재 V3 branch scope를 변경",
    )
    _ = update_scope_parser.add_argument("--proposal-file", required=True)
    _ = update_scope_parser.add_argument("--proposal-sha256", required=True)

    finish_proposal_parser = subparsers.add_parser(
        "finish-proposal",
        help="commit된 source를 merge·검증·close할 immutable 계약 출력",
    )
    _ = finish_proposal_parser.add_argument("--source")
    _ = finish_proposal_parser.add_argument("--merge-strategy", choices=("ff-only", "merge-commit"), default="ff-only")
    _ = finish_proposal_parser.add_argument("--verify-command", action="append", required=True)
    _ = finish_proposal_parser.add_argument("--cleanup", action="store_true")

    preserve_parser = subparsers.add_parser(
        "preserve",
        help="handoff한 미완료 task와 worktree를 PRESERVED로 기록",
    )
    _ = preserve_parser.add_argument("--reason", required=True)
    _ = subparsers.add_parser("resume", help="현재 PRESERVED task를 ACTIVE로 재개")

    for command_name, help_text in (
        ("finish", "승인된 방식으로 target에 merge"),
        ("verify", "target에서 승인된 사후 검증 실행"),
        ("close", "검증된 task를 CLOSED로 기록하고 승인된 경우 local 정리"),
    ):
        command_parser = subparsers.add_parser(command_name, help=help_text)
        _ = command_parser.add_argument("--proposal-file", required=True)
        _ = command_parser.add_argument("--proposal-sha256", required=True)

    _ = subparsers.add_parser("context", help="현재 브랜치 계보와 다음 안전 조치를 출력")
    return parser


def main() -> int:
    parser = build_parser()
    arguments = parser.parse_args()
    root = repository_root()
    guard = load_guard(root)
    if not guard.enabled(str(guard.BASE_BRANCH)):
        raise SystemExit("기준 브랜치 토큰이 렌더링되지 않았습니다. 중앙 agent-policy start로 새 inject 세션을 시작하세요.")
    actions = {"proposal": proposal, "create": create, "scope-proposal": scope_proposal,
               "update-scope": update_scope, "finish-proposal": finish_proposal, "finish": finish,
               "verify": verify, "close": close, "preserve": preserve, "resume": resume}
    if arguments.command not in actions:
        print(guard.branch_context(root, str(guard.BASE_BRANCH)))
        return 0
    state = integration_state(guard)
    execution_root = root
    if arguments.command in {"finish", "verify", "close"}:
        contract = load_finish_proposal(root, arguments.proposal_file, arguments.proposal_sha256, guard)
        execution_root = integration_root(root, contract, guard)
    lock = workflow_state_root(root) / "locks" / f"{state.digest(str(execution_root))}.lock"
    with state.locked(lock):
        return actions[arguments.command](arguments, guard, root)


if __name__ == "__main__":
    raise SystemExit(main())
