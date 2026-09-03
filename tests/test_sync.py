from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from agent_policy.core import (
    MANIFEST_RELATIVE,
    ProjectConfig,
    central_is_clean,
    diff_project,
    render_project,
    sync_project,
    verify_safe_removals,
)


class SyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        self.project = ProjectConfig(
            id="user-ui",
            name="temporary-user-ui",
            path=self.root,
            commands={
                "dev": "npm run dev",
                "build": "npm run build",
                "lint": "npm run lint",
                "test": "npm run test",
                "preview": "npm run preview",
            },
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    @patch("agent_policy.core.central_is_clean", return_value=True)
    def test_sync_writes_manifest_and_detects_consumer_mutation(self, _clean: object) -> None:
        count = sync_project(self.project)
        manifest = json.loads((self.root / MANIFEST_RELATIVE).read_text(encoding="utf-8"))
        self.assertEqual(count, len(manifest["managed_files"]))
        self.assertTrue(diff_project(self.project).current)

        agents = self.root / "AGENTS.md"
        agents.write_text(agents.read_text(encoding="utf-8") + "\nlocal drift\n", encoding="utf-8")
        self.assertIn("AGENTS.md", diff_project(self.project).changed)

    @patch("agent_policy.core.central_is_clean", return_value=True)
    def test_central_source_digest_change_is_detected(self, _clean: object) -> None:
        sync_project(self.project)
        with patch("agent_policy.core.source_digest", return_value="changed-source"):
            self.assertIn(
                "central source digest changed",
                diff_project(self.project).manifest_issues,
            )

    def test_previous_manifest_file_is_removed_only_when_hash_matches(self) -> None:
        obsolete = self.root / "obsolete.md"
        obsolete.write_text("old", encoding="utf-8")
        digest = hashlib.sha256(b"old").hexdigest()
        manifest = {"managed_files": {"obsolete.md": digest}}
        removals = verify_safe_removals(self.project, {}, manifest, retire_legacy=False)
        self.assertEqual(removals, (obsolete,))

        obsolete.write_text("user change", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "수정된 이전 managed"):
            verify_safe_removals(self.project, {}, manifest, retire_legacy=False)

    def test_render_is_deterministic(self) -> None:
        self.assertEqual(render_project(self.project), render_project(self.project))

    @patch("agent_policy.core.subprocess.run")
    def test_central_clean_check_ignores_only_central_logs(self, run: object) -> None:
        run.return_value.returncode = 0
        run.return_value.stdout = "?? logs/projects/user-ui/logic/sessions/task/plan.md\n"
        self.assertTrue(central_is_clean())

        run.return_value.stdout = " M policy/common/AGENT_POLICY.template.md\n"
        self.assertFalse(central_is_clean())

        run.return_value.stdout = "R  policy/old.md -> logs/old.md\n"
        self.assertFalse(central_is_clean())

    @patch("agent_policy.core.central_is_clean", return_value=True)
    def test_rendered_consumer_common_guard_blocks_never_agent_git(self, _clean: object) -> None:
        sync_project(self.project)
        completed = subprocess.run(
            [
                "python3",
                "-I",
                ".agent-policy/runtime/managed_policy_guard.py",
                "pre-tool",
                "codex",
            ],
            input=json.dumps(
                {
                    "cwd": str(self.root),
                    "session_id": "session-test",
                    "tool_name": "Bash",
                    "tool_input": {"command": "git -C . reset --hard"},
                }
            ),
            cwd=self.root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        output = json.loads(completed.stdout)["hookSpecificOutput"]
        self.assertEqual(output["permissionDecision"], "deny")
        self.assertIn("사용자 전용", output["permissionDecisionReason"])

    @patch("agent_policy.core.central_is_clean", return_value=True)
    def test_rendered_codex_common_hook_registration_executes(self, _clean: object) -> None:
        sync_project(self.project)
        hooks = json.loads((self.root / ".codex/hooks.json").read_text(encoding="utf-8"))["hooks"]
        command = next(
            item["hooks"][0]["command"]
            for item in hooks["UserPromptSubmit"]
            if "managed_policy_guard.py" in item["hooks"][0]["command"]
        )
        self.assertNotIn("HOOK_SHA256", command)
        environment = os.environ.copy()
        environment["TMPDIR"] = str(self.root)
        completed = subprocess.run(
            command,
            input=json.dumps(
                {
                    "session_id": "session-test",
                    "cwd": str(self.root),
                    "prompt": "일반 사용자 요청",
                }
            ),
            cwd=self.root,
            env=environment,
            shell=True,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, "")
