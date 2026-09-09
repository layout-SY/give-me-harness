from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from agent_policy.core import PolicyError, ProjectConfig
from agent_policy.maintenance import apply, preview


class MaintenanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name).resolve()
        self.root = self.directory / "repo"
        self.root.mkdir()
        self.git("init", "-q", "-b", "sy-main")
        self.git("config", "user.name", "Policy Test")
        self.git("config", "user.email", "policy@example.invalid")
        (self.root / "package.json").write_text(json.dumps({"scripts": {"test": "vitest run && python3 -I .codex/hooks/test_governance_hooks.py"}}))
        (self.root / "README.md").write_text("# Project\n\nApplication guide\n.codex/hooks/old.py\n")
        (self.root / ".codex/hooks").mkdir(parents=True)
        (self.root / ".codex/hooks/old.py").write_text("# retired\n")
        self.git("add", ".")
        self.git("commit", "-qm", "initial")
        self.project = ProjectConfig("user-ui", "test", self.root, {"dev": "npm run dev", "build": "npm run build",
            "lint": "npm run lint", "test": "npm run test", "preview": "npm run preview"})

    def git(self, *args: str) -> str:
        return subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True, check=True).stdout.strip()

    def plan(self):
        return preview(self.project, "task/policy-retirement", self.directory / "maintenance", "codex", self.directory / "state")

    def test_preview_and_apply_preserve_active_checkout_and_make_v3_worktree(self) -> None:
        self.git("switch", "-qc", "task/legacy")
        (self.root / "feature.txt").write_text("in progress")
        before = self.git("status", "--porcelain")
        plan, sha, diff = self.plan()
        self.assertIn("test_governance_hooks.py", diff)
        self.assertFalse((self.directory / "maintenance").exists())
        target = apply(self.project, plan, sha)
        self.assertEqual(self.git("status", "--porcelain"), before)
        self.assertEqual(self.git("branch", "--show-current"), "task/legacy")
        self.assertEqual(json.loads((target / "package.json").read_text())["scripts"]["test"], "vitest run")
        self.assertFalse((target / ".codex/hooks/old.py").exists())
        self.assertEqual(self.git("config", "branch.task/policy-retirement.asan-contract-version"), "3")

    def test_modified_contract_or_base_head_cannot_apply(self) -> None:
        plan, sha, _ = self.plan()
        with self.assertRaises(PolicyError):
            apply(self.project, plan, "0" * 64)
        self.git("commit", "--allow-empty", "-qm", "base changed")
        with self.assertRaisesRegex(PolicyError, "HEAD"):
            apply(self.project, plan, sha)
        self.assertFalse((self.directory / "maintenance").exists())
