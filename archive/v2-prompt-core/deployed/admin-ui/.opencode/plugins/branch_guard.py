"""작업 브랜치 계보와 파일 범위를 검증하는 호스트 중립 guard."""

from __future__ import annotations

import fnmatch
import os
import re
import shlex
import subprocess
from pathlib import Path

BASE_BRANCH = "sy-main"
TASK_BRANCH_PATTERN = re.compile(r"^task/[a-z0-9]+(?:-[a-z0-9]+)*$")
ARTIFACT_PREFIX = ".codex/logs/sessions/"
MAX_LINEAGE_DEPTH = 32

REQUIRED_METADATA: tuple[str, ...] = (
    "purpose",
    "parent",
    "parent-head",
    "merge-target",
    "proposal",
)


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
    completed = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if completed.returncode != 0:
        return ()
    paths: list[str] = []
    for line in completed.stdout.splitlines():
        entry = line[3:].strip()
        if " -> " in entry:
            entry = entry.split(" -> ", 1)[1]
        if entry:
            paths.append(entry.strip('"'))
    return tuple(dict.fromkeys(paths))


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
    return values


def _missing_metadata(values: dict[str, object]) -> tuple[str, ...]:
    missing = [field for field in REQUIRED_METADATA if not values.get(field)]
    scope = values.get("scope")
    if not isinstance(scope, tuple) or not scope:
        missing.append("scope")
    return tuple(missing)


def proposal_id(branch: str, parent: str, parent_head: str, merge_target: str) -> str:
    """승인 요청에 표시하고 hook이 재계산할 수 있는 분기 계약 식별자를 만든다."""

    return f"branch:{branch}|parent:{parent}@{parent_head}|merge:{merge_target}"


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
    if relative.startswith(ARTIFACT_PREFIX):
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


def _lineage_denial(root: Path, branch: str, base_branch: str) -> str | None:
    seen: set[str] = set()
    cursor = branch
    for _ in range(MAX_LINEAGE_DEPTH):
        if cursor == base_branch:
            return None
        if cursor in seen:
            return f"브랜치 계보가 순환합니다: {cursor}"
        seen.add(cursor)
        values = metadata(root, cursor)
        missing = _missing_metadata(values)
        if missing:
            return f"{cursor} 브랜치 메타데이터가 없습니다: {', '.join(missing)}"
        parent = str(values["parent"])
        merge_target = str(values["merge-target"])
        parent_head = str(values["parent-head"])
        proposal = str(values["proposal"])
        if parent != merge_target:
            return f"{cursor}의 분기 기준({parent})과 직접 merge 대상({merge_target})이 다릅니다."
        expected_proposal = proposal_id(cursor, parent, parent_head, merge_target)
        if proposal != expected_proposal:
            return f"{cursor}의 승인 요청 식별자가 분기 계약과 일치하지 않습니다."
        if not branch_exists(root, parent):
            return f"{cursor}의 부모 브랜치를 찾을 수 없습니다: {parent}"
        if not head(root, parent_head):
            return f"{cursor}에 기록된 부모 HEAD를 찾을 수 없습니다: {parent_head}"
        if not is_ancestor(root, parent_head, cursor):
            return f"{cursor}가 승인된 부모 HEAD {parent_head[:12]}를 포함하지 않습니다."
        actual_base = merge_base(root, cursor, parent)
        if actual_base != parent_head:
            return (
                f"{cursor}의 실제 분기점({actual_base[:12]})이 승인된 부모 HEAD"
                f"({parent_head[:12]})와 다릅니다."
            )
        cursor = parent
    return f"브랜치 계보가 {MAX_LINEAGE_DEPTH}단계를 초과했습니다."


def active_branch_denial(
    root: Path,
    targets: tuple[str, ...] = (),
    base_branch: str = BASE_BRANCH,
) -> str | None:
    """현재 작업 브랜치가 승인된 계보와 범위를 만족하는지 판정한다."""

    if not enabled(base_branch):
        return None
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
    if not is_ancestor(root, base_branch, branch):
        return f"{branch}가 기준 브랜치 {base_branch}의 계보에 속하지 않습니다."
    lineage_problem = _lineage_denial(root, branch, base_branch)
    if lineage_problem is not None:
        return lineage_problem
    values = metadata(root, branch)
    scopes = values.get("scope")
    assert isinstance(scopes, tuple)
    for relative in tuple(dict.fromkeys((*targets, *changed_paths(root)))):
        if not _scope_allows(relative, scopes):
            return (
                f"승인된 작업 범위 밖의 경로입니다: {relative}\n"
                f"  브랜치: {branch}\n"
                f"  승인 범위: {', '.join(scopes)}\n"
                "범위를 임의 확장하지 말고 사용자에게 다시 승인받으세요."
            )
    return None


def _git_commands(command: str) -> tuple[tuple[str, ...], ...]:
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|")
        lexer.whitespace_split = True
        lexer.commenters = ""
        tokens = list(lexer)
    except ValueError:
        return ()
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
    return tuple(commands)


def _argument_after(arguments: tuple[str, ...], *options: str) -> str:
    for option in options:
        if option not in arguments:
            continue
        index = arguments.index(option) + 1
        return arguments[index] if index < len(arguments) else ""
    return ""


def _last_positional(arguments: tuple[str, ...]) -> str:
    for value in reversed(arguments):
        if not value.startswith("-"):
            return value
    return ""


def _creation_denial(root: Path, arguments: tuple[str, ...]) -> str | None:
    subcommand = arguments[0]
    if subcommand == "switch":
        if "-C" in arguments or "--force-create" in arguments:
            return "기존 브랜치를 덮어쓰는 git switch -C는 금지합니다."
        branch = _argument_after(arguments, "-c", "--create")
    elif subcommand == "checkout":
        if "-B" in arguments:
            return "기존 브랜치를 덮어쓰는 git checkout -B는 금지합니다."
        branch = _argument_after(arguments, "-b")
    else:
        branch = ""
    if not branch:
        return None
    return _new_branch_denial(root, branch)


def _new_branch_denial(root: Path, branch: str) -> str | None:
    if changed_paths(root):
        return "dirty worktree에서는 새 브랜치를 만들 수 없습니다. 기존 변경의 소유권을 먼저 확인하세요."
    if TASK_BRANCH_PATTERN.fullmatch(branch) is None:
        return f"새 작업 브랜치명은 task/<ascii-kebab-summary> 형식이어야 합니다: {branch}"
    if branch_exists(root, branch):
        return f"이미 존재하는 브랜치입니다: {branch}"
    return None


def _merge_denial(root: Path, arguments: tuple[str, ...], base_branch: str) -> str | None:
    if any(option in arguments for option in ("--abort", "--continue", "--quit")):
        return None
    source = _last_positional(arguments[1:])
    if not source or not branch_exists(root, source):
        return "merge할 source 작업 브랜치를 확인할 수 없습니다."
    values = metadata(root, source)
    missing = _missing_metadata(values)
    if missing:
        return f"merge source {source}의 승인 메타데이터가 없습니다: {', '.join(missing)}"
    target = str(values["merge-target"])
    current = current_branch(root)
    if current != target:
        return f"{source}는 {target}에서만 merge할 수 있습니다. 현재 브랜치: {current or 'detached HEAD'}"
    if changed_paths(root):
        return "dirty worktree에서는 merge할 수 없습니다. 승인된 작업의 commit 상태를 먼저 확인하세요."
    lineage_problem = _lineage_denial(root, source, base_branch)
    if lineage_problem is not None:
        return lineage_problem
    children = unmerged_children(root, source)
    if children:
        return f"미병합 자식 브랜치를 먼저 처리해야 합니다: {', '.join(children)}"
    return None


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
        target = str(values.get("merge-target", ""))
        if not target or not branch_exists(root, target):
            return f"{branch}의 직접 merge 대상을 확인할 수 없어 삭제할 수 없습니다."
        if current_branch(root) == branch:
            return f"현재 체크아웃한 브랜치는 삭제할 수 없습니다: {branch}"
        if not is_ancestor(root, branch, target):
            return f"{branch}가 {target}에 완전히 merge되지 않아 삭제할 수 없습니다."
        children = unmerged_children(root, branch)
        if children:
            return f"{branch}에 미병합 자식 브랜치가 있습니다: {', '.join(children)}"
    return None


def command_denial(root: Path, command: str, base_branch: str = BASE_BRANCH) -> str | None:
    """브랜치 계보를 바꾸는 Git 명령의 기계적 안전 조건을 확인한다."""

    if not enabled(base_branch):
        return None
    for arguments in _git_commands(command):
        if not arguments:
            continue
        subcommand = arguments[0]
        if subcommand in {"reset", "clean", "stash", "rebase", "cherry-pick"}:
            return f"브랜치 계보를 임의 변경할 수 있어 git {subcommand} 명령을 차단했습니다."
        if subcommand in {"switch", "checkout"}:
            denial = _creation_denial(root, arguments)
            if denial is not None:
                return denial
            if not _argument_after(arguments, "-c", "--create", "-b") and changed_paths(root):
                return "dirty worktree에서는 브랜치를 전환할 수 없습니다."
        elif subcommand == "branch":
            denial = _deletion_denial(root, arguments)
            if denial is not None:
                return denial
            if any(option in arguments for option in ("-c", "-C", "--copy")):
                return "승인 메타데이터가 분리될 수 있어 git branch copy는 금지합니다."
            if len(arguments) > 1 and not arguments[1].startswith("-"):
                denial = _new_branch_denial(root, arguments[1])
                if denial is not None:
                    return denial
        elif subcommand == "merge":
            denial = _merge_denial(root, arguments, base_branch)
            if denial is not None:
                return denial
        elif subcommand in {"add", "commit"}:
            denial = active_branch_denial(root, base_branch=base_branch)
            if denial is not None:
                return denial
    return None


def pre_tool_denial(
    root: Path,
    command: str,
    targets: tuple[str, ...],
    shell_command: bool,
    base_branch: str = BASE_BRANCH,
) -> str | None:
    if shell_command and command:
        denial = command_denial(root, command, base_branch)
        if denial is not None:
            return denial
    if targets:
        return active_branch_denial(root, targets, base_branch)
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
    lines.extend(
        (
            f"- 작업 목적: {values.get('purpose') or '메타데이터 없음'}",
            f"- 분기 기준: {values.get('parent') or '메타데이터 없음'}",
            f"- 승인 시점 부모 HEAD: {str(values.get('parent-head') or '없음')[:12]}",
            f"- 직접 merge 대상: {values.get('merge-target') or '메타데이터 없음'}",
            f"- 승인된 작업 경로: {', '.join(scopes) if isinstance(scopes, tuple) and scopes else '메타데이터 없음'}",
        )
    )
    target = str(values.get("merge-target") or "")
    merged = bool(target and branch_exists(root, target) and is_ancestor(root, branch, target))
    lines.append(f"- merge 상태: {'merge됨' if merged else '미병합'}")
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
