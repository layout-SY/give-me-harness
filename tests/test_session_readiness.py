from __future__ import annotations

import json
import shlex
import sys
import uuid
from pathlib import Path
from unittest.mock import patch

from test_remediation import WorkflowFixture
from agent_policy.injection import prepare_injection


class SessionReadinessTests(WorkflowFixture):
    def start(self, host: str = "claude", **options):
        launch = prepare_injection(self.project, host, "logic", build_root=self.directory / "build",
                                   state_root=self.directory / "state", source_codex_home=self.directory / "user-home",
                                   **options)
        self.env.update(launch.environment)
        self.snapshot = launch.bundle_root / "policy"
        self.runtime = self.snapshot / ".agent-policy/runtime"
        self.guard = self.module(self.runtime / "managed_policy_guard.py")
        self.event["session_id"] = launch.environment["ASAN_AGENT_POLICY_ASSIGNMENT"]
        if host == "codex":
            self.event["session_id"] = str(uuid.UUID(self.event["session_id"]))
        return launch

    def read_prerequisites(self, host: str = "claude") -> None:
        skill = self.snapshot / ".agent-policy/common/skills/policy/coding-convention/SKILL.md"
        for target in (str(skill), "src/App.tsx"):
            result = self.hook("post-tool", host, tool_name="Read", tool_input={"file_path": target},
                               tool_response={"success": True, "content": "confirmed read"})
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_existing_branch_new_assignment_reports_missing_readiness_before_first_write(self) -> None:
        self.create_task("existing")
        for host in ("codex", "claude", "opencode"):
            with self.subTest(host=host):
                self.start(host, task="task/existing")
                started = self.hook("session-start", host)
                self.assertEqual(started.returncode, 0, started.stderr)
                self.assertIn("[SESSION_READINESS]", started.stdout)
                self.assertIn("implementation_approved: false", started.stdout)
                self.assertIn("skill_confirmed: false", started.stdout)
                self.assertIn("branch_creation_required: false", started.stdout)
                self.read_prerequisites(host)
                write = {"tool_name": "Write", "tool_input": {"file_path": "src/App.tsx"}}
                missing = self.hook("pre-tool", host, **write)
                self.assertTrue(missing.returncode != 0 or '"deny"' in missing.stdout)
                self.assertNotIn("branch proposal", missing.stdout + missing.stderr)
                self.hook("user-prompt", host, prompt="Proceed")
                allowed = self.hook("pre-tool", host, **write)
                self.assertEqual(allowed.returncode, 0, allowed.stderr)
                self.assertNotIn('"deny"', allowed.stdout)
                self.assertEqual(self.git("branch", "--show-current"), "task/existing")
                self.assertFalse(self.state(host).get("approved_contracts"))

    def test_undeclared_existing_task_is_scoped_before_mutation_and_cannot_leak_approval(self) -> None:
        self.create_task("first")
        self.git("switch", "-q", "sy-main")
        self.create_task("second")
        self.git("switch", "-q", "task/first")
        self.start()
        self.hook("user-prompt", prompt="Proceed")
        self.read_prerequisites()
        self.assertEqual(self.state()["implementation_scope"]["task"], "task/first")
        self.git("switch", "-q", "task/second")
        self.hook("user-prompt", prompt="현재 상태를 알려줘")
        self.assertIsNot(self.state().get("implementation_approved"), True)
        self.assertIsNot(self.state().get("skill_confirmed"), True)

    def test_closed_ui_branch_does_not_supply_scope_or_ui_requirement_to_new_logic_task(self) -> None:
        self.create_task("closed-ui")
        self.git("config", "branch.task/closed-ui.asan-role", "ui")
        self.git("config", "branch.task/closed-ui.asan-state", "CLOSED")
        self.start()
        self.hook("user-prompt", prompt="Proceed")
        self.read_prerequisites()
        state = self.state()
        self.assertEqual(state["implementation_scope"]["source_scopes"], [])
        proposed = self.workflow("proposal", "--branch", "task/new-logic", "--parent", "sy-main",
                                 "--purpose", "새 Logic 작업", "--scope", "src", "--reason", "종료 작업과 독립",
                                 "--role", "logic", "--git-integrator", "claude",
                                 "--worktree", str(self.directory / "new-logic"))
        self.assertEqual(proposed.returncode, 0, proposed.stderr)
        args = self.proposal_args(proposed.stdout)
        self.hook("user-prompt", prompt="승인 " + args[-1])
        script = self.snapshot / ".agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py"
        event = {"tool_name": "Bash", "tool_input": {"command": shlex.join([sys.executable, "-I", str(script), "create", *args])}}
        allowed = self.hook("pre-tool", **event)
        self.assertEqual(allowed.returncode, 0, allowed.stderr)
        self.assertNotIn("src/shared/ui", allowed.stdout)
        self.assertEqual(self.workflow("create", *args).returncode, 0)
        self.hook("post-tool", **event, tool_response={"exit_code": 0})
        self.assertTrue(self.state().get("implementation_approved"))
        self.assertEqual(self.state()["implementation_scope"]["source_scopes"], ["src"])

    def test_create_uses_proposed_ui_role_even_from_logic_base(self) -> None:
        self.start()
        self.hook("user-prompt", prompt="Proceed")
        self.read_prerequisites()
        proposed = self.workflow("proposal", "--branch", "task/new-ui", "--parent", "sy-main",
                                 "--purpose", "UI 구현", "--scope", "src", "--reason", "UI 계약",
                                 "--role", "ui", "--git-integrator", "claude")
        self.assertEqual(proposed.returncode, 0, proposed.stderr)
        args = self.proposal_args(proposed.stdout)
        self.hook("user-prompt", prompt="승인 " + args[-1])
        script = self.snapshot / ".agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py"
        event = {"tool_name": "Bash", "tool_input": {"command": shlex.join([sys.executable, "-I", str(script), "create", *args])}}
        denied = self.hook("pre-tool", **event)
        self.assertIn("src/shared/ui", denied.stderr)
        self.assertNotEqual(denied.returncode, 0)

    def test_same_assignment_resume_preserves_readiness_but_new_assignment_starts_empty(self) -> None:
        self.create_task("continued")
        first = self.start("codex", task="task/continued")
        self.hook("session-start", "codex")
        self.hook("user-prompt", "codex", prompt="Proceed")
        self.read_prerequisites("codex")
        ready = self.hook("session-start", "codex", source="resume")
        self.assertIn("implementation_approved: true", ready.stdout)
        self.assertIn("skill_confirmed: true", ready.stdout)
        self.start("codex", task="task/continued")
        self.assertNotEqual(self.env["ASAN_AGENT_POLICY_ASSIGNMENT"], first.environment["ASAN_AGENT_POLICY_ASSIGNMENT"])
        started = self.hook("session-start", "codex")
        self.assertIn("implementation_approved: false", started.stdout)
        self.assertIn("skill_confirmed: false", started.stdout)
        self.assertIsNot(self.state("codex").get("implementation_approved"), True)

    def test_sha_approval_is_reported_separately_from_missing_implementation_approval(self) -> None:
        self.start()
        self.hook("user-prompt", prompt="승인 " + "a" * 64)
        started = self.hook("session-start")
        self.assertIn("implementation_approved: false", started.stdout)
        self.assertIn("a" * 64, started.stdout)
        self.assertIsNot(self.state().get("implementation_approved"), True)

    def test_new_start_uses_updated_runtime_while_resume_pins_original_bundle(self) -> None:
        self.event["session_id"] = "12345678-1234-1234-1234-123456789012"
        first = self.start("codex")
        transcript = Path(first.environment["CODEX_HOME"]) / "sessions/rollout.jsonl"
        transcript.parent.mkdir()
        transcript.write_text(json.dumps({"type": "session_meta", "payload": {
            "id": self.event["session_id"], "cwd": str(self.root)}}) + "\n")
        self.hook("session-start", "codex")
        self.hook("user-prompt", "codex", prompt="Proceed")
        from agent_policy import injection
        rendered = injection.render_project(self.project)
        runtime_path = ".agent-policy/runtime/approval_policy.py"
        updated = {**rendered, runtime_path: rendered[runtime_path] + b"\n# updated central policy\n"}
        with patch.object(injection, "render_project", return_value=updated):
            second = self.start("codex")
            self.assertNotEqual(first.bundle_root, second.bundle_root)
            self.assertEqual((second.bundle_root / "policy" / runtime_path).read_bytes(), updated[runtime_path])
            resumed = self.start("codex", resume_assignment=first.environment["ASAN_AGENT_POLICY_ASSIGNMENT"])
        self.assertEqual(resumed.bundle_root, first.bundle_root)
        self.assertEqual((resumed.bundle_root / "policy" / runtime_path).read_bytes(), rendered[runtime_path])
        self.assertTrue(self.state("codex").get("implementation_approved"))

    def test_readiness_query_does_not_record_reads_or_change_pending_approval(self) -> None:
        self.start()
        script = self.snapshot / ".agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py"
        self.hook("post-tool", tool_name="Bash", tool_input={"command": shlex.join([sys.executable, str(script), "proposal"])},
                  tool_response={"exit_code": 0, "output": "SHA-256: " + "b" * 64})
        before = self.state()
        context = self.hook("branch-context")
        self.assertEqual(context.returncode, 0, context.stderr)
        self.assertIn("[SESSION_READINESS]", context.stdout)
        self.assertIn("b" * 64, context.stdout)
        self.assertEqual(self.state(), before)
