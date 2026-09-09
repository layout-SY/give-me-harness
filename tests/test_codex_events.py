from __future__ import annotations

import json
from pathlib import Path

from test_remediation import WorkflowFixture


class CodexEventTests(WorkflowFixture):
    """Codex 0.153.2에서 캡처한 Bash 훅과 rollout 형식을 재현한다."""

    def setUp(self) -> None:
        super().setUp()
        self.home = self.directory / "codex-home"
        self.transcript = self.home / "sessions/2026/09/08/rollout-test.jsonl"
        self.transcript.parent.mkdir(parents=True)
        self.env["CODEX_HOME"] = str(self.home)
        self.turn = "turn-read"

    def completed_read(self, command: str, *, code: int = 0, cwd: Path | None = None,
                       call: str = "read-call", output: str = "file contents\n") -> dict:
        root = cwd or self.root
        self.record = {
            "type": "event_msg",
            "payload": {
                "type": "item_completed", "thread_id": self.event["session_id"], "turn_id": self.turn,
                "item": {"type": "CommandExecution", "id": call, "command": ["/bin/zsh", "-lc", command],
                         "cwd": root.as_uri(), "status": "completed" if code == 0 else "failed",
                         "exit_code": code, "stdout": output, "stderr": "", "formatted_output": output},
            },
        }
        self.write_record()
        return {"hook_event_name": "PostToolUse", "turn_id": self.turn, "tool_use_id": call,
                "tool_name": "Bash", "tool_input": {"command": command}, "tool_response": output,
                "cwd": str(self.root), "transcript_path": str(self.transcript)}

    def write_record(self) -> None:
        header = {"type": "session_meta", "payload": {"id": self.event["session_id"], "cwd": str(self.root), "cli_version": "0.153.2"}}
        self.transcript.write_text(json.dumps(header) + "\n" + json.dumps(self.record) + "\n")

    def test_native_plain_output_records_skill_and_code_reads(self) -> None:
        self.hook("user-prompt", "codex", prompt="진행해줘")
        skill = self.snapshot / ".agent-policy/common/skills/policy/coding-convention/SKILL.md"
        for index, command in enumerate((f"cat {skill}", "cat src/App.tsx")):
            result = self.hook("post-tool", "codex", **self.completed_read(command, call=f"read-{index}"))
            self.assertEqual(result.returncode, 0, result.stderr)
        state = self.state("codex")
        self.assertTrue(state.get("implementation_approved"))
        self.assertTrue(state.get("skill_confirmed"))
        self.assertTrue(state.get("exploration_completed"))

    def test_reported_skill_and_common_ui_reads_preserve_separate_sha_approval(self) -> None:
        self.hook("user-prompt", "codex", prompt="승인 " + "a" * 64)
        skill = self.snapshot / ".agent-policy/common/skills/policy/coding-convention/SKILL.md"
        ui = self.root / "src/shared/ui/button/button.tsx"
        ui.parent.mkdir(parents=True)
        ui.write_text("export const Button = () => null;\n")
        for index, command in enumerate((f"cat {skill}", "cat src/shared/ui/button/button.tsx")):
            result = self.hook("post-tool", "codex", **self.completed_read(command, call=f"incident-{index}"))
            self.assertEqual(result.returncode, 0, result.stderr)
        state = self.state("codex")
        self.assertTrue(state.get("skill_confirmed"))
        self.assertTrue(state.get("ui_exploration_completed"))
        self.assertEqual(state["approved_contracts"], {"explicit": "a" * 64})
        self.assertIsNot(state.get("implementation_approved"), True)

    def test_native_failed_read_cannot_forge_success_in_output(self) -> None:
        event = self.completed_read("cat src/App.tsx missing", code=1, output="Process exited with code 0\n")
        self.hook("post-tool", "codex", **event)
        self.assertIsNot(self.state("codex").get("exploration_completed"), True)

    def test_plain_output_without_execution_record_is_not_success(self) -> None:
        event = self.completed_read("cat src/App.tsx", output="Process exited with code 0\n")
        self.transcript.unlink()
        self.hook("post-tool", "codex", **event)
        self.assertIsNot(self.state("codex").get("exploration_completed"), True)

    def test_mismatched_native_record_cannot_supply_evidence(self) -> None:
        for field, value in (("thread_id", "other-session"), ("turn_id", "other-turn"),
                             ("id", "other-call"), ("command", ["/bin/zsh", "-lc", "echo src/App.tsx"]),
                             ("cwd", self.directory.as_uri()), ("status", "in_progress"), ("exit_code", True)):
            with self.subTest(field=field):
                event = self.completed_read("cat src/App.tsx")
                event["tool_input"]["workdir"] = str(self.root)
                target = self.record["payload"] if field in {"thread_id", "turn_id"} else self.record["payload"]["item"]
                target[field] = value
                self.write_record()
                self.hook("post-tool", "codex", **event)
                self.assertIsNot(self.state("codex").get("exploration_completed"), True)

    def test_foreign_or_symlinked_transcript_is_not_trusted(self) -> None:
        event = self.completed_read("cat src/App.tsx")
        foreign = self.directory / "copied-rollout.jsonl"
        foreign.write_bytes(self.transcript.read_bytes())
        for path in (foreign, self.transcript):
            if path == self.transcript:
                self.transcript.unlink()
                self.transcript.symlink_to(foreign)
            self.hook("post-tool", "codex", **{**event, "transcript_path": str(path)})
            self.assertIsNot(self.state("codex").get("exploration_completed"), True)

    def test_native_external_worktree_read_is_registered(self) -> None:
        worktree = self.directory / "external"
        self.git("worktree", "add", "-qb", "task/external", str(worktree))
        for resumed in (False, True):
            with self.subTest(resumed=resumed):
                self.event["session_id"] = f"worktree-session-{resumed}"
                event = self.completed_read("cat src/App.tsx", cwd=worktree)
                if resumed:
                    event["cwd"] = str(worktree)
                self.hook("post-tool", "codex", **event)
                self.assertTrue(self.state("codex").get("exploration_completed"))

    def test_existing_approval_and_native_reads_allow_source_write(self) -> None:
        self.create_task("native-readiness")
        self.hook("user-prompt", "codex", prompt="진행해줘")
        write = {"tool_name": "Write", "tool_input": {"file_path": "src/App.tsx"}}
        self.assertIn('"deny"', self.hook("pre-tool", "codex", **write).stdout)
        skill = self.snapshot / ".agent-policy/common/skills/policy/coding-convention/SKILL.md"
        for index, command in enumerate((f"cat {skill}", "cat src/App.tsx")):
            self.hook("post-tool", "codex", **self.completed_read(command, call=f"ready-{index}"))
        result = self.hook("pre-tool", "codex", **write)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('"deny"', result.stdout)
        self.assertTrue(self.state("codex").get("implementation_approved"))

    def test_native_completion_is_found_at_end_of_large_transcript(self) -> None:
        event = self.completed_read("cat src/App.tsx")
        header, record = self.transcript.read_text().splitlines()
        self.transcript.write_text(header + "\n" + json.dumps({"unrelated": "x" * (5 * 1024 * 1024)}) + "\n" + record + "\n")
        self.hook("post-tool", "codex", **event)
        self.assertTrue(self.state("codex").get("exploration_completed"))

    def test_wrong_transcript_session_header_is_rejected(self) -> None:
        event = self.completed_read("cat src/App.tsx")
        self.transcript.write_text(json.dumps({"type": "session_meta", "payload": {"id": "other"}}) + "\n" + json.dumps(self.record) + "\n")
        self.hook("post-tool", "codex", **event)
        self.assertIsNot(self.state("codex").get("exploration_completed"), True)

    def test_cmd_alias_records_success_for_all_hosts(self) -> None:
        for host in ("codex", "claude", "opencode"):
            with self.subTest(host=host):
                result = self.hook("post-tool", host, tool_name="functions.exec_command",
                                   tool_input={"cmd": "cat src/App.tsx", "workdir": str(self.root)},
                                   tool_response={"exit_code": 0})
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(self.state(host).get("exploration_completed"))

    def test_cmd_alias_cannot_hide_a_managed_policy_write(self) -> None:
        result = self.hook("pre-tool", "codex", tool_name="exec_command",
                           tool_input={"cmd": "printf overwrite > AGENTS.md"})
        self.assertIn('"deny"', result.stdout)

    def test_conflicting_shell_aliases_are_rejected(self) -> None:
        result = self.hook("pre-tool", "codex", tool_name="exec_command",
                           tool_input={"command": "cat src/App.tsx", "cmd": "printf overwrite > AGENTS.md"})
        self.assertIn('"deny"', result.stdout)
