from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from agent_policy.core import CENTRAL_ROOT

GUARD = CENTRAL_ROOT / "policy/guards/managed_policy_guard.py"


class GuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.session_id = str(uuid.uuid4())
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

    def run_mode(
        self,
        mode: str,
        host: str,
        event: dict[str, object],
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", "-I", str(GUARD), mode, host],
            input=json.dumps({"cwd": str(self.root), "session_id": self.session_id, **event}),
            text=True,
            capture_output=True,
            cwd=self.root,
            check=False,
        )

    def run_guard(
        self,
        host: str,
        tool_name: str,
        tool_input: dict[str, object],
    ) -> subprocess.CompletedProcess[str]:
        return self.run_mode(
            "pre-tool",
            host,
            {"tool_name": tool_name, "tool_input": tool_input},
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

    def test_claude_asks_for_git_build_and_dev_commands(self) -> None:
        for command, expected_category in (
            ("git status --short", "Git"),
            ("npm run build", "빌드"),
            ("vite build", "빌드"),
            ("npm run dev -- --host", "개발 서버"),
        ):
            with self.subTest(command=command):
                result = self.run_guard("claude", "Bash", {"command": command})
                output = json.loads(result.stdout)
                decision = output["hookSpecificOutput"]
                self.assertEqual(decision["permissionDecision"], "ask")
                self.assertIn(expected_category, decision["permissionDecisionReason"])
                self.assertIn(command, decision["permissionDecisionReason"])
                if command == "vite build":
                    self.assertNotIn("개발 서버", decision["permissionDecisionReason"])

    def test_lint_and_test_commands_do_not_require_operation_approval(self) -> None:
        for command in ("npm run lint", "npm run test"):
            with self.subTest(command=command):
                result = self.run_guard("claude", "Bash", {"command": command})
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "")

    def test_codex_approval_is_exact_and_one_shot(self) -> None:
        command = "git status --short"
        first = self.run_guard("codex", "Bash", {"command": command})
        self.assertEqual(
            json.loads(first.stdout)["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )

        approval = self.run_mode(
            "user-prompt",
            "codex",
            {"prompt": "명령 실행 승인"},
        )
        self.assertIn("동일 명령", approval.stdout)

        allowed = self.run_guard("codex", "Bash", {"command": command})
        self.assertEqual(allowed.returncode, 0, allowed.stderr)
        self.assertEqual(allowed.stdout, "")

        second = self.run_guard("codex", "Bash", {"command": command})
        self.assertEqual(
            json.loads(second.stdout)["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )

    def test_codex_approval_does_not_apply_to_changed_command(self) -> None:
        self.run_guard("codex", "Bash", {"command": "npm run build"})
        self.run_mode("user-prompt", "codex", {"prompt": "명령 실행 승인"})

        changed = self.run_guard("codex", "Bash", {"command": "npm run build -- --mode host"})
        self.assertEqual(
            json.loads(changed.stdout)["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )

    def test_codex_approval_is_isolated_by_session(self) -> None:
        command = "git diff --stat"
        first_session = self.session_id
        self.run_guard("codex", "Bash", {"command": command})
        self.run_mode("user-prompt", "codex", {"prompt": "명령 실행 승인"})

        self.session_id = str(uuid.uuid4())
        other_session = self.run_guard("codex", "Bash", {"command": command})
        self.assertEqual(
            json.loads(other_session.stdout)["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )

        self.session_id = first_session
        original_session = self.run_guard("codex", "Bash", {"command": command})
        self.assertEqual(original_session.stdout, "")

    def test_codex_approval_phrase_must_be_standalone(self) -> None:
        command = "npm run dev"
        self.run_guard("codex", "Bash", {"command": command})
        embedded = self.run_mode(
            "user-prompt",
            "codex",
            {"prompt": "이제 명령 실행 승인해줘"},
        )
        self.assertEqual(embedded.stdout, "")

        still_denied = self.run_guard("codex", "Bash", {"command": command})
        self.assertEqual(
            json.loads(still_denied.stdout)["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )

    def test_opencode_operation_gate_is_delegated_to_native_permissions(self) -> None:
        result = self.run_guard("opencode", "bash", {"command": "git status"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
