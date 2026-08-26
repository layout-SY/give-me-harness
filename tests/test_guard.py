from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from agent_policy.core import CENTRAL_ROOT

GUARD = CENTRAL_ROOT / "policy/guards/managed_policy_guard.py"


class GuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        manifest = self.root / ".agent-policy/manifest.json"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(
            json.dumps(
                {
                    "project_id": "test",
                    "managed_roots": [
                        "AGENTS.md",
                        ".agents/skills/",
                        ".opencode/plugins/",
                    ],
                    "managed_files": {"AGENTS.md": "unused"},
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def run_guard(self, host: str, tool_name: str, tool_input: dict[str, object]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", "-I", str(GUARD), "pre-tool", host],
            input=json.dumps(
                {
                    "cwd": str(self.root),
                    "tool_name": tool_name,
                    "tool_input": tool_input,
                }
            ),
            text=True,
            capture_output=True,
            cwd=self.root,
            check=False,
        )

    def test_codex_returns_native_deny_shape(self) -> None:
        result = self.run_guard("codex", "Write", {"file_path": "AGENTS.md"})
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_claude_and_opencode_exit_two(self) -> None:
        for host, tool_input in (
            ("claude", {"file_path": ".agents/skills/SKILL.md"}),
            ("opencode", {"filePath": ".opencode/plugins/new.js"}),
        ):
            with self.subTest(host=host):
                result = self.run_guard(host, "Write", tool_input)
                self.assertEqual(result.returncode, 2)
                self.assertIn("중앙 프로젝트", result.stderr)

    def test_apply_patch_add_update_delete_and_move_are_covered(self) -> None:
        for heading in (
            "*** Add File: AGENTS.md",
            "*** Update File: AGENTS.md",
            "*** Delete File: AGENTS.md",
            "*** Move to: .agents/skills/new/SKILL.md",
        ):
            with self.subTest(heading=heading):
                command = f"*** Begin Patch\n{heading}\n+x\n*** End Patch"
                result = self.run_guard("codex", "apply_patch", {"command": command})
                self.assertEqual(
                    json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"],
                    "deny",
                )

    def test_explicit_shell_writes_are_denied(self) -> None:
        for command in (
            "printf x > AGENTS.md",
            "rm AGENTS.md",
            "sed -i '' 's/a/b/' AGENTS.md",
            "git reset --hard",
        ):
            with self.subTest(command=command):
                result = self.run_guard("claude", "Bash", {"command": command})
                self.assertEqual(result.returncode, 2)

    def test_read_only_shell_and_application_edit_are_allowed(self) -> None:
        read = self.run_guard("claude", "Bash", {"command": "sed -n '1,20p' AGENTS.md"})
        application = self.run_guard("codex", "Write", {"file_path": "src/App.tsx"})
        self.assertEqual(read.returncode, 0, read.stderr)
        self.assertEqual(application.returncode, 0, application.stderr)
        self.assertEqual(application.stdout, "")
