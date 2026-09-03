#!/usr/bin/env python3
"""승인할 브랜치 계약을 출력하고 승인 후 동일한 계약으로 브랜치를 만든다."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
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
    "ARTIFACT_MODES",
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
    """실행 중인 deploy·inject 스냅샷과 함께 렌더링된 guard 경로를 찾는다."""

    script = Path(__file__).resolve()
    candidates: list[Path] = []
    bundle_root = os.environ.get("ASAN_AGENT_POLICY_BUNDLE_ROOT", "").strip()
    if bundle_root:
        candidates.append(Path(bundle_root).resolve() / ".agent-policy/runtime/branch_guard.py")
    for ancestor in script.parents:
        if ancestor.name == "common" and ancestor.parent.name == ".agent-policy":
            candidates.append(ancestor.parent / "runtime/branch_guard.py")
            break
        if ancestor.name == ".agents":
            candidates.append(ancestor.parent / ".agent-policy/runtime/branch_guard.py")
            break
        if ancestor.name == "plugin":
            candidates.append(ancestor / "runtime/branch_guard.py")
            break
        if ancestor.name == "opencode-home":
            candidates.append(ancestor / "runtime/branch_guard.py")
            break
    return tuple(candidates)


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
    specification = importlib.util.spec_from_file_location("asan_branch_guard", source)
    if specification is None or specification.loader is None:
        raise SystemExit(f"branch guard를 불러올 수 없습니다: {source}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def load_guard(root: Path) -> ModuleType:
    snapshot_candidates = snapshot_guard_candidates()
    inject = os.environ.get(INJECT_MODE_ENV) == "inject"
    fallback_candidates = (root / ".agent-policy/runtime/branch_guard.py",)
    candidates = snapshot_candidates if inject else snapshot_candidates + fallback_candidates
    authoritative = set(snapshot_candidates) | {fallback_candidates[0]}
    diagnostics: list[str] = []
    for source in dict.fromkeys(candidates):
        if not source.is_file():
            diagnostics.append(f"- 없음: {source}")
            continue
        try:
            module = import_guard(source)
        except Exception as error:  # pragma: no cover - 구체 오류는 실행 환경에 따라 다름
            diagnostics.append(f"- 로드 실패: {source} ({type(error).__name__}: {error})")
            if source in authoritative:
                break
            continue
        issues = guard_contract_issues(module)
        if not issues:
            return module
        diagnostics.append(f"- 호환되지 않음: {source} (계약 오류: {', '.join(issues)})")
        if source in authoritative:
            break

    location = "정책 스냅샷" if inject else "현재 정책 배치"
    detail = "\n".join(diagnostics) if diagnostics else "- 검사할 guard 후보 경로가 없습니다."
    raise SystemExit(
        f"{location}에서 호환되는 branch_guard.py를 찾을 수 없습니다.\n"
        f"{detail}\n"
        "정책 diff를 확인하고 별도 승인 후 동기화한 다음 새 세션을 시작하세요."
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
            "격리 worktree가 생성되었습니다. 현재 세션의 활성 task가 이 작업 하나라면 "
            f"도구 workdir 또는 git -C 대상으로 이 경로를 사용해 계속 진행하세요: {worktree}\n"
            "미완료 task를 병행하거나 담당자를 인계할 때만 handoff 후 새 세션을 시작합니다.\n"
        )
    print(guard.branch_context(active_root, str(guard.BASE_BRANCH)))
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
        "merge_strategy": "ff-only",
        "validation_commands": [list(command) for command in validation],
        "cleanup": bool(arguments.cleanup),
        "worktree": str(values.get("worktree") or ""),
        "branch_contract_sha256": str(values.get("contract-sha256") or ""),
    }
    path, digest = write_immutable_finish_proposal(root, contract, guard)
    print(
        "\n".join(
            (
                "[브랜치 완료 승인 요청]",
                f"- source: {source}@{source_head}",
                f"- target: {target}@{contract['target_head']}",
                "- merge 방식: ff-only",
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


def finish(arguments: argparse.Namespace, guard: ModuleType, root: Path) -> int:
    contract = load_finish_proposal(root, arguments.proposal_file, arguments.proposal_sha256, guard)
    source, source_head, target, target_head = _finish_fields(contract)
    if guard.current_branch(root) != target:
        raise SystemExit(f"finish는 target worktree에서 실행해야 합니다: target={target}")
    _clean_worktree(guard, root)
    if guard.head(root, source) != source_head or guard.head(root, target) != target_head:
        raise SystemExit("승인 후 source 또는 target HEAD가 변경되었습니다. 새 finish proposal이 필요합니다.")
    values = guard.metadata(root, source)
    if values.get("contract-sha256") != contract.get("branch_contract_sha256"):
        raise SystemExit("source branch 계약이 finish proposal과 일치하지 않습니다.")
    if values.get("state") not in {"ACTIVE", "READY_TO_MERGE"}:
        raise SystemExit(f"finish를 실행할 수 없는 task 상태입니다: {values.get('state') or '없음'}")
    _ = git(root, "config", f"branch.{source}.asan-state", "READY_TO_MERGE")
    try:
        _ = git(root, "merge", "--ff-only", source)
    except SystemExit as error:
        raise SystemExit(
            "merge에 실패했습니다. 자동 rollback·rebase·삭제를 하지 않고 source와 worktree를 보존합니다.\n"
            f"{error}"
        ) from error
    print(f"{source}를 {target}에 ff-only merge했습니다. verify를 별도 실행하세요.")
    return 0


def verify(arguments: argparse.Namespace, guard: ModuleType, root: Path) -> int:
    contract = load_finish_proposal(root, arguments.proposal_file, arguments.proposal_sha256, guard)
    source, source_head, target, _ = _finish_fields(contract)
    if guard.current_branch(root) != target:
        raise SystemExit(f"verify는 target worktree에서 실행해야 합니다: target={target}")
    _clean_worktree(guard, root)
    if (
        guard.head(root, source) != source_head
        or guard.head(root, target) != source_head
        or not guard.is_ancestor(root, source, target)
    ):
        raise SystemExit(
            "승인된 source HEAD만 target의 현재 HEAD인 상태가 아니어서 verify할 수 없습니다."
        )
    values = guard.metadata(root, source)
    if values.get("state") != "READY_TO_MERGE":
        raise SystemExit(f"READY_TO_MERGE 상태에서만 verify할 수 있습니다: {values.get('state') or '없음'}")
    raw_commands = contract.get("validation_commands")
    if not isinstance(raw_commands, list):
        raise SystemExit("finish proposal의 validation_commands가 올바르지 않습니다.")
    for raw in raw_commands:
        if not isinstance(raw, list) or not raw or not all(isinstance(token, str) for token in raw):
            raise SystemExit("finish proposal의 검증 명령이 올바르지 않습니다.")
        try:
            completed = subprocess.run(tuple(raw), cwd=root, check=False, timeout=600)
        except (OSError, subprocess.TimeoutExpired) as error:
            _ = git(root, "config", f"branch.{source}.asan-state", "READY_TO_MERGE")
            raise SystemExit(
                "사후 검증을 실행하지 못했습니다. source와 worktree를 보존합니다.\n"
                f"  명령: {shlex.join(raw)}\n"
                f"  오류: {error}"
            ) from error
        if completed.returncode != 0:
            _ = git(root, "config", f"branch.{source}.asan-state", "READY_TO_MERGE")
            raise SystemExit(
                "사후 검증이 실패했습니다. 자동 rollback·삭제 없이 source와 worktree를 보존합니다.\n"
                f"  명령: {shlex.join(raw)}\n"
                f"  exit: {completed.returncode}"
            )
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
    if guard.current_branch(root) != target:
        raise SystemExit(f"close는 target worktree에서 실행해야 합니다: target={target}")
    _clean_worktree(guard, root)
    if guard.head(root, target) != source_head or not guard.is_ancestor(root, source_head, target):
        raise SystemExit(
            "검증 뒤 target HEAD가 변경되었거나 승인된 source HEAD와 달라 close할 수 없습니다."
        )
    values = guard.metadata(root, source)
    if values.get("state") != "MERGED_VERIFIED":
        raise SystemExit("MERGED_VERIFIED 상태가 아니므로 close할 수 없습니다. verify를 먼저 실행하세요.")
    record = _write_closed_record(root, contract, guard)
    if contract.get("cleanup") is True:
        worktree = str(contract.get("worktree") or "")
        if worktree:
            candidate = Path(worktree).resolve()
            if candidate in branch_worktrees(root, source):
                _clean_worktree(guard, candidate)
                _ = git(root, "worktree", "remove", str(candidate))
        _ = git(root, "branch", "-d", source)
    else:
        _ = git(root, "config", f"branch.{source}.asan-state", "CLOSED")
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

    finish_proposal_parser = subparsers.add_parser(
        "finish-proposal",
        help="commit된 source를 merge·검증·close할 immutable 계약 출력",
    )
    _ = finish_proposal_parser.add_argument("--source")
    _ = finish_proposal_parser.add_argument("--verify-command", action="append", required=True)
    _ = finish_proposal_parser.add_argument("--cleanup", action="store_true")

    preserve_parser = subparsers.add_parser(
        "preserve",
        help="handoff한 미완료 task와 worktree를 PRESERVED로 기록",
    )
    _ = preserve_parser.add_argument("--reason", required=True)
    _ = subparsers.add_parser("resume", help="현재 PRESERVED task를 ACTIVE로 재개")

    for command_name, help_text in (
        ("finish", "승인된 계약으로 target에 ff-only merge"),
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
        raise SystemExit("기준 브랜치 토큰이 렌더링되지 않았습니다. 중앙 정책을 다시 동기화하세요.")
    if arguments.command == "proposal":
        return proposal(arguments, guard, root)
    if arguments.command == "create":
        return create(arguments, guard, root)
    if arguments.command == "finish-proposal":
        return finish_proposal(arguments, guard, root)
    if arguments.command == "finish":
        return finish(arguments, guard, root)
    if arguments.command == "verify":
        return verify(arguments, guard, root)
    if arguments.command == "close":
        return close(arguments, guard, root)
    if arguments.command == "preserve":
        return preserve(arguments, guard, root)
    if arguments.command == "resume":
        return resume(arguments, guard, root)
    print(guard.branch_context(root, str(guard.BASE_BRANCH)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
