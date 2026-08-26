#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUARD = ROOT / ".agent-policy/runtime/managed_policy_guard.py"


class ManagedPolicyGuardTests(unittest.TestCase):
    def run_guard(self, host: str, tool_name: str, tool_input: dict[str, object]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", "-I", str(GUARD), "pre-tool", host],
            input=json.dumps(
                {
                    "cwd": str(ROOT),
                    "tool_name": tool_name,
                    "tool_input": tool_input,
                }
            ),
            text=True,
            capture_output=True,
            cwd=ROOT,
            check=False,
        )

    def test_codex_denies_managed_write(self) -> None:
        result = self.run_guard("codex", "Write", {"file_path": "AGENTS.md"})
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(
            output["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )

    def test_claude_denies_managed_edit(self) -> None:
        result = self.run_guard("claude", "Edit", {"file_path": ".agents/skills/SKILL.md"})
        self.assertEqual(result.returncode, 2)
        self.assertIn("중앙 프로젝트", result.stderr)

    def test_opencode_denies_file_path(self) -> None:
        result = self.run_guard(
            "opencode",
            "write",
            {"filePath": ".opencode/plugins/extra.js"},
        )
        self.assertEqual(result.returncode, 2)

    def test_apply_patch_move_and_delete_are_denied(self) -> None:
        command = (
            "*** Begin Patch\n"
            "*** Update File: AGENTS.md\n"
            "*** Move to: docs/old-agents.md\n"
            "@@\n-old\n+new\n"
            "*** End Patch"
        )
        result = self.run_guard("codex", "apply_patch", {"command": command})
        output = json.loads(result.stdout)
        self.assertEqual(output["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_shell_write_is_denied_but_read_is_allowed(self) -> None:
        denied = self.run_guard("claude", "Bash", {"command": "printf x > AGENTS.md"})
        allowed = self.run_guard("claude", "Bash", {"command": "sed -n '1,20p' AGENTS.md"})
        self.assertEqual(denied.returncode, 2)
        self.assertEqual(allowed.returncode, 0, allowed.stderr)

    def test_application_edit_is_allowed(self) -> None:
        result = self.run_guard("codex", "Write", {"file_path": "src/App.tsx"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")


class HostContractTests(unittest.TestCase):
    def test_codex_and_claude_register_session_and_pretool_hooks(self) -> None:
        codex = json.loads((ROOT / ".codex/hooks.json").read_text(encoding="utf-8"))["hooks"]
        claude = json.loads((ROOT / ".claude/settings.json").read_text(encoding="utf-8"))["hooks"]
        self.assertIn("SessionStart", codex)
        self.assertIn("PreToolUse", codex)
        self.assertIn("SessionStart", claude)
        self.assertIn("PreToolUse", claude)

    def test_opencode_plugin_uses_supported_before_hook(self) -> None:
        plugin = (ROOT / ".opencode/plugins/agent-policy.js").read_text(encoding="utf-8")
        self.assertIn('"tool.execute.before"', plugin)
        self.assertIn("output.args", plugin)


if __name__ == "__main__":
    unittest.main()
