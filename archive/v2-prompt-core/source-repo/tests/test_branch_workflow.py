"""브랜치 승인 요청과 생성 도구의 계약 고정을 검증한다."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BranchWorkflowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "repository"
        self.runtime = Path(self.temporary.name) / "runtime/common"
        self.root.mkdir()
        script = self.runtime / "skills/policy/git-branch-strategy/scripts/branch_workflow.py"
        guard = self.runtime / "hooks/branch_guard.py"
        script.parent.mkdir(parents=True)
        guard.parent.mkdir(parents=True)
        shutil.copyfile(
            ROOT / "source/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py",
            script,
        )
        guard_text = (ROOT / "source/common/hooks/branch_guard.py").read_text(encoding="utf-8")
        _ = guard.write_text(guard_text.replace("{{BASE_BRANCH}}", "main"), encoding="utf-8")
        self.script = script

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

    def workflow(self, *arguments: str, succeeds: bool = True) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run(
            ("python3", str(self.script), *arguments),
            cwd=self.root,
            capture_output=True,
            text=True,
            check=False,
        )
        if succeeds and completed.returncode != 0:
            self.fail(completed.stderr or completed.stdout)
        return completed

    def test_승인_요청과_동일한_계약으로_브랜치를_생성한다(self) -> None:
        parent_head = self.git("rev-parse", "main")
        proposal = (
            "branch:task/add-policy|parent:main@"
            f"{parent_head}|merge:main"
        )
        request = self.workflow(
            "proposal",
            "--branch",
            "task/add-policy",
            "--purpose",
            "브랜치 정책 추가",
            "--parent",
            "main",
            "--scope",
            "src/policy",
            "--reason",
            "독립 작업",
        )
        self.assertIn("[브랜치 생성 승인 요청]", request.stdout)
        self.assertIn(proposal, request.stdout)

        created = self.workflow(
            "create",
            "--branch",
            "task/add-policy",
            "--purpose",
            "브랜치 정책 추가",
            "--parent",
            "main",
            "--parent-head",
            parent_head,
            "--proposal",
            proposal,
            "--scope",
            "src/policy",
        )
        self.assertEqual(self.git("branch", "--show-current"), "task/add-policy")
        self.assertEqual(
            self.git("config", "--get", "branch.task/add-policy.asan-merge-target"),
            "main",
        )
        self.assertIn("[BRANCH_CONTEXT]", created.stdout)

    def test_승인_뒤_parent_head가_바뀌면_생성을_거부한다(self) -> None:
        approved_head = self.git("rev-parse", "main")
        _ = (self.root / "README.md").write_text("changed\n", encoding="utf-8")
        self.git("add", "README.md")
        self.git("commit", "-m", "advance parent")
        proposal = f"branch:task/stale|parent:main@{approved_head}|merge:main"
        completed = self.workflow(
            "create",
            "--branch",
            "task/stale",
            "--purpose",
            "오래된 승인",
            "--parent",
            "main",
            "--parent-head",
            approved_head,
            "--proposal",
            proposal,
            "--scope",
            "src",
            succeeds=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("부모 HEAD가 변경", completed.stderr)
        self.assertEqual(self.git("branch", "--show-current"), "main")


if __name__ == "__main__":
    unittest.main(verbosity=2)
