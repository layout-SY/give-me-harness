#!/usr/bin/env python3
"""승인할 브랜치 계약을 출력하고 승인 후 동일한 계약으로 브랜치를 만든다."""

from __future__ import annotations

import argparse
import importlib.util
import subprocess
from pathlib import Path
from types import ModuleType


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


def load_guard(root: Path) -> ModuleType:
    candidates = (
        Path(__file__).resolve().parents[4] / "hooks/branch_guard.py",
        root / ".codex/hooks/branch_guard.py",
        root / ".claude/hooks/branch_guard.py",
        root / ".opencode/plugins/branch_guard.py",
    )
    source = next((candidate for candidate in candidates if candidate.is_file()), None)
    if source is None:
        raise SystemExit("중앙 branch_guard.py를 찾을 수 없습니다. 정책을 다시 동기화하세요.")
    specification = importlib.util.spec_from_file_location("asan_branch_guard", source)
    if specification is None or specification.loader is None:
        raise SystemExit(f"branch guard를 불러올 수 없습니다: {source}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


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
    parent = arguments.parent or guard.current_branch(root)
    if not parent or not guard.branch_exists(root, parent):
        raise SystemExit(f"분기 기준 브랜치를 찾을 수 없습니다: {parent or '없음'}")
    if guard.TASK_BRANCH_PATTERN.fullmatch(arguments.branch) is None:
        raise SystemExit("브랜치명은 task/<ascii-kebab-summary> 형식이어야 합니다.")
    if guard.branch_exists(root, arguments.branch):
        raise SystemExit(f"이미 존재하는 브랜치입니다: {arguments.branch}")
    dirty = guard.changed_paths(root)
    parent_head = guard.head(root, parent)
    merge_target = parent
    identifier = guard.proposal_id(arguments.branch, parent, parent_head, merge_target)
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
                f"- 승인 요청 식별자: {identifier}",
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
    if dirty:
        print("\n주의: dirty worktree이므로 현재 상태에서는 승인 후에도 브랜치를 생성할 수 없습니다.")
    return 0


def create(arguments: argparse.Namespace, guard: ModuleType, root: Path) -> int:
    if guard.changed_paths(root):
        raise SystemExit("dirty worktree에서는 브랜치를 생성할 수 없습니다.")
    if guard.TASK_BRANCH_PATTERN.fullmatch(arguments.branch) is None:
        raise SystemExit("브랜치명은 task/<ascii-kebab-summary> 형식이어야 합니다.")
    if guard.branch_exists(root, arguments.branch):
        raise SystemExit(f"이미 존재하는 브랜치입니다: {arguments.branch}")
    if not guard.branch_exists(root, arguments.parent):
        raise SystemExit(f"분기 기준 브랜치를 찾을 수 없습니다: {arguments.parent}")
    actual_parent_head = guard.head(root, arguments.parent)
    if actual_parent_head != arguments.parent_head:
        raise SystemExit(
            "승인 이후 부모 HEAD가 변경되었습니다.\n"
            f"  승인: {arguments.parent_head}\n"
            f"  현재: {actual_parent_head}\n"
            "새 계약으로 다시 승인받으세요."
        )
    expected = guard.proposal_id(
        arguments.branch,
        arguments.parent,
        arguments.parent_head,
        arguments.parent,
    )
    if arguments.proposal != expected:
        raise SystemExit("승인 요청 식별자가 현재 분기 계약과 일치하지 않습니다.")

    if guard.current_branch(root) != arguments.parent:
        _ = git(root, "switch", arguments.parent)
    _ = git(root, "switch", "-c", arguments.branch)
    for field, value in (
        ("purpose", arguments.purpose),
        ("parent", arguments.parent),
        ("parent-head", arguments.parent_head),
        ("merge-target", arguments.parent),
        ("proposal", arguments.proposal),
    ):
        _ = git(root, "config", f"branch.{arguments.branch}.asan-{field}", value)
    for scope in arguments.scope:
        _ = git(root, "config", "--add", f"branch.{arguments.branch}.asan-scope", scope)

    denial = guard.active_branch_denial(root, (), str(guard.BASE_BRANCH))
    if denial is not None:
        raise SystemExit(f"브랜치는 생성됐지만 계약 검증에 실패했습니다:\n{denial}")
    print(guard.branch_context(root, str(guard.BASE_BRANCH)))
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

    create_parser = subparsers.add_parser("create", help="승인된 계약과 동일할 때 브랜치를 생성")
    _ = create_parser.add_argument("--branch", required=True)
    _ = create_parser.add_argument("--purpose", required=True)
    _ = create_parser.add_argument("--parent", required=True)
    _ = create_parser.add_argument("--parent-head", required=True)
    _ = create_parser.add_argument("--proposal", required=True)
    _ = create_parser.add_argument("--scope", action="append", required=True)

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
    print(guard.branch_context(root, str(guard.BASE_BRANCH)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
