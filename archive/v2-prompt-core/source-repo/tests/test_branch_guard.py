"""공통 작업 브랜치 guard의 Git 계보 판정을 검증한다."""

from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "source/common/hooks/branch_guard.py"
SPEC = importlib.util.spec_from_file_location("branch_guard", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("branch_guard.py를 불러올 수 없습니다.")
branch_guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(branch_guard)


class BranchGuardTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Test User")
        self.git("config", "user.email", "test@example.com")
        _ = (self.root / "README.md").write_text("baseline\n", encoding="utf-8")
        self.git("add", "README.md")
        self.git("commit", "-m", "baseline")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def git(self, *arguments: str) -> str:
        completed = subprocess.run(
            ("git", *arguments),
            cwd=self.root,
            capture_output=True,
            text=True,
            check=True,
        )
        return completed.stdout.strip()

    def create_task(self, name: str = "task/add-branch-policy", scope: str = "src/policy") -> str:
        parent_head = self.git("rev-parse", "main")
        self.git("switch", "-c", name)
        for field, value in (
            ("purpose", "브랜치 정책 추가"),
            ("parent", "main"),
            ("parent-head", parent_head),
            ("merge-target", "main"),
            (
                "proposal",
                branch_guard.proposal_id(name, "main", parent_head, "main"),
            ),
        ):
            self.git("config", f"branch.{name}.asan-{field}", value)
        self.git("config", "--add", f"branch.{name}.asan-scope", scope)
        return parent_head

    def test_기준_브랜치의_직접_수정을_차단한다(self) -> None:
        denial = branch_guard.active_branch_denial(self.root, ("src/policy/rule.ts",), "main")
        self.assertIsNotNone(denial)
        self.assertIn("기준 브랜치 main", str(denial))

    def test_승인된_작업_브랜치와_범위를_허용한다(self) -> None:
        _ = self.create_task()
        denial = branch_guard.active_branch_denial(self.root, ("src/policy/rule.ts",), "main")
        self.assertIsNone(denial)

    def test_승인된_범위_밖의_수정을_차단한다(self) -> None:
        _ = self.create_task()
        denial = branch_guard.active_branch_denial(self.root, ("src/ui/Page.tsx",), "main")
        self.assertIsNotNone(denial)
        self.assertIn("승인된 작업 범위 밖", str(denial))

    def test_메타데이터가_없는_작업_브랜치를_차단한다(self) -> None:
        self.git("switch", "-c", "task/missing-metadata")
        denial = branch_guard.active_branch_denial(self.root, ("src/policy/rule.ts",), "main")
        self.assertIsNotNone(denial)
        self.assertIn("메타데이터", str(denial))

    def test_dirty_worktree의_새_브랜치_생성을_차단한다(self) -> None:
        _ = (self.root / "README.md").write_text("changed\n", encoding="utf-8")
        denial = branch_guard.command_denial(self.root, "git switch -c task/another-task", "main")
        self.assertIsNotNone(denial)
        self.assertIn("dirty worktree", str(denial))

    def test_merge는_기록된_target에서만_허용한다(self) -> None:
        _ = self.create_task()
        source = self.root / "src/policy/rule.ts"
        source.parent.mkdir(parents=True)
        _ = source.write_text("export {}\n", encoding="utf-8")
        self.git("add", "src/policy/rule.ts")
        self.git("commit", "-m", "add policy")

        wrong_target = branch_guard.command_denial(self.root, "git merge task/add-branch-policy", "main")
        self.assertIsNotNone(wrong_target)
        self.assertIn("main에서만 merge", str(wrong_target))

        self.git("switch", "main")
        allowed = branch_guard.command_denial(self.root, "git merge --ff-only task/add-branch-policy", "main")
        self.assertIsNone(allowed)

    def test_merge된_브랜치만_안전_삭제를_허용한다(self) -> None:
        _ = self.create_task()
        source = self.root / "src/policy/rule.ts"
        source.parent.mkdir(parents=True)
        _ = source.write_text("export {}\n", encoding="utf-8")
        self.git("add", "src/policy/rule.ts")
        self.git("commit", "-m", "add policy")
        self.git("switch", "main")

        before_merge = branch_guard.command_denial(
            self.root, "git branch -d task/add-branch-policy", "main"
        )
        self.assertIsNotNone(before_merge)
        self.git("merge", "--ff-only", "task/add-branch-policy")
        after_merge = branch_guard.command_denial(
            self.root, "git branch -d task/add-branch-policy", "main"
        )
        self.assertIsNone(after_merge)
        force = branch_guard.command_denial(self.root, "git branch -D task/add-branch-policy", "main")
        self.assertIsNotNone(force)

    def test_compact_context가_브랜치_계보를_포함한다(self) -> None:
        parent_head = self.create_task()
        context = branch_guard.branch_context(self.root, "main")
        self.assertIn("[BRANCH_CONTEXT]", context)
        self.assertIn("task/add-branch-policy", context)
        self.assertIn(parent_head[:12], context)
        self.assertIn("추후 main으로 merge", context)

    def test_승인_식별자가_계약과_다르면_차단한다(self) -> None:
        _ = self.create_task()
        self.git("config", "branch.task/add-branch-policy.asan-proposal", "tampered")
        denial = branch_guard.active_branch_denial(self.root, ("src/policy/rule.ts",), "main")
        self.assertIsNotNone(denial)
        self.assertIn("승인 요청 식별자", str(denial))

    def test_git_branch_방식의_이름과_dirty_상태도_검사한다(self) -> None:
        invalid = branch_guard.command_denial(self.root, "git branch feature/invalid", "main")
        self.assertIsNotNone(invalid)
        _ = (self.root / "README.md").write_text("changed\n", encoding="utf-8")
        dirty = branch_guard.command_denial(self.root, "git branch task/valid-name", "main")
        self.assertIsNotNone(dirty)
        self.assertIn("dirty worktree", str(dirty))


if __name__ == "__main__":
    unittest.main(verbosity=2)
