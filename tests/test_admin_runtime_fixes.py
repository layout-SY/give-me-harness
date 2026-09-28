from __future__ import annotations

import json
import os
import py_compile
import shlex
import sys
from pathlib import Path
from unittest.mock import patch

from test_remediation import WorkflowFixture
from agent_policy import injection
from agent_policy.core import PolicyError
from agent_policy.runtime import load_runtime


class AdminRuntimeTests(WorkflowFixture):
    def launch(self, host="codex"):
        launch = injection.prepare_injection(self.project, host, "logic", build_root=self.directory / "build",
                                             state_root=self.directory / "state", source_codex_home=self.directory / "personal")
        self.env.update(launch.environment)
        self.snapshot = launch.bundle_root / "policy"
        self.runtime = self.snapshot / ".agent-policy/runtime"
        self.guard = self.module(self.runtime / "managed_policy_guard.py")
        self.launch_record = launch
        self.assignment = launch.environment["ASAN_AGENT_POLICY_ASSIGNMENT"]
        self.state_api = load_runtime("runtime_state")
        with patch.dict(os.environ, self.env):
            self.repository = self.state_api.repository_state(self.root / ".git")
        self.assignment_path = self.repository / "assignments" / self.assignment / "assignment.json"
        record = self.state_api.read(self.assignment_path)
        record["native_session"] = "12345678-1234-1234-1234-123456789012"
        self.state_api.write(self.assignment_path, record)
        self.event["session_id"] = record["native_session"]
        if host == "codex":
            log = Path(launch.environment["CODEX_HOME"]) / "sessions" / f"rollout-{record['native_session']}.jsonl"
            log.parent.mkdir(exist_ok=True)
            log.write_text(json.dumps({"type": "session_meta", "payload": {
                "id": record["native_session"], "cwd": str(self.root)}}) + "\n")
        return launch

    def test_actual_workflow_keeps_bundle_resumable_on_both_hosts(self):
        for host in ("codex", "claude"):
            with self.subTest(host=host):
                launch = self.launch(host)
                result = self.workflow("context")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertFalse(list(launch.bundle_root.rglob("*.pyc")), "읽기 명령이 immutable bundle을 오염시켰습니다.")
                resumed = injection.resume_injection(self.project, host, "logic", self.assignment,
                                                      self.directory / "state", None, "owner")
                self.assertEqual(resumed.bundle_root, launch.bundle_root)
                self.assertEqual(resumed.environment, launch.environment)
                self.assertIn(self.event["session_id"], resumed.command)

    def test_diagnostics_and_cache_repair_preserve_original_policy(self):
        from agent_policy import sessions
        launch = self.launch()
        source = self.runtime / "branch_guard.py"
        py_compile.compile(str(source), doraise=True)
        record = self.state_api.read(self.assignment_path)
        issue = injection.bundle_diagnostics(launch.bundle_root, record["bundle_digest"])
        self.assertFalse(issue["valid"])
        self.assertEqual(len(issue["caches"]), 1)
        original = source.read_bytes()
        with self.assertRaisesRegex(PolicyError, "__pycache__"):
            injection.resume_injection(self.project, "codex", "logic", self.assignment, self.directory / "state", None, "owner")
        quarantined = sessions.repair_bundle(self.project, self.assignment, state_root=self.directory / "state")
        self.assertEqual(len(quarantined), 1)
        self.assertTrue(Path(quarantined[0]).is_file())
        self.assertEqual(source.read_bytes(), original)
        self.assertTrue(injection._bundle_is_valid(launch.bundle_root, record["bundle_digest"]))
        self.assertEqual(sessions.repair_bundle(self.project, self.assignment, state_root=self.directory / "state"), [])

    def test_repair_rejects_source_changes_unknown_files_and_symlinks(self):
        from agent_policy import sessions
        self.launch()
        source = self.runtime / "branch_guard.py"
        original = source.read_bytes()
        py_compile.compile(str(source), doraise=True)
        source.write_bytes(original + b"\n# changed\n")
        with self.assertRaises(PolicyError):
            sessions.repair_bundle(self.project, self.assignment, state_root=self.directory / "state")
        source.write_bytes(original)
        extra = self.launch_record.bundle_root / "unexpected.py"
        extra.write_text("unrecognized")
        with self.assertRaises(PolicyError):
            sessions.repair_bundle(self.project, self.assignment, state_root=self.directory / "state")
        extra.unlink()
        extra.symlink_to(source)
        with self.assertRaises(PolicyError):
            sessions.repair_bundle(self.project, self.assignment, state_root=self.directory / "state")
        self.assertTrue(list(self.launch_record.bundle_root.rglob("*.pyc")))

    def test_session_catalog_spans_isolated_homes_without_writing_them(self):
        from agent_policy import sessions
        launches = [self.launch(), self.launch()]
        for launch in launches:
            home = Path(launch.environment["CODEX_HOME"])
            log = home / "sessions/rollout-12345678-1234-1234-1234-123456789012.jsonl"
            log.write_text(json.dumps({"type": "session_meta", "payload": {
                "id": "12345678-1234-1234-1234-123456789012", "cwd": str(self.root)}}) + "\n")
        before = {str(p): p.read_bytes() for launch in launches for p in Path(launch.environment["CODEX_HOME"]).rglob("*") if p.is_file()}
        rows = sessions.list_sessions(self.project, host="codex", state_root=self.directory / "state")
        self.assertEqual(len(rows), 2)
        self.assertEqual(len({r["codex_home"] for r in rows}), 2)
        self.assertTrue(all(r["transcripts"] and r["bundle"]["valid"] for r in rows))
        self.assertTrue(all("--resume-assignment" in r["resume_command"] for r in rows))
        self.assertEqual(before, {name: Path(name).read_bytes() for name in before})

    def test_wrapped_workflow_is_rejected_before_ownership_can_be_skipped(self):
        self.launch("claude")
        script = self.snapshot / ".agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py"
        command = shlex.join([sys.executable, str(script), "context"])
        for prefix in (f"cd {self.root}\n", f"cd {self.root} && ", f"cd {self.root}; "):
            with self.subTest(prefix=prefix):
                denied = self.hook("pre-tool", tool_name="Bash", tool_input={"command": prefix + command})
                self.assertNotEqual(denied.returncode, 0, denied.stdout)
                self.assertIn("단일", denied.stderr + denied.stdout)
        read = self.hook("pre-tool", tool_name="Bash", tool_input={"command": shlex.join(["cat", str(script)])})
        self.assertEqual(read.returncode, 0, read.stderr)

    def test_create_body_checks_foreign_git_claim_and_target_reservation(self):
        self.launch()
        proposed = self.workflow("proposal", "--branch", "task/owned", "--parent", "sy-main", "--purpose", "owned",
                                 "--scope", "src", "--reason", "test", "--role", "logic", "--git-integrator", "codex")
        self.assertEqual(proposed.returncode, 0, proposed.stderr)
        args = self.proposal_args(proposed.stdout)
        claim = self.repository / "claims" / (self.state_api.digest("git:" + str(self.root)) + ".json")
        self.state_api.write(claim, {"owner": "b" * 32, "resource": "git:" + str(self.root)})
        denied = self.workflow("create", *args)
        self.assertNotEqual(denied.returncode, 0)
        self.assertEqual(self.git("branch", "--show-current"), "sy-main")
        self.assertEqual(self.git("branch", "--list", "task/owned"), "")
        claim.unlink()
        reservation = self.root / ".git/asan-agent-policy/integration-targets/other.json"
        self.state_api.write(reservation, {"owner": self.assignment, "worktree": str(self.root)})
        self.assertNotEqual(self.workflow("create", *args).returncode, 0)

    def test_post_merge_owner_can_record_logs_without_rebinding_to_target(self):
        self.launch("claude")
        self.create_task("logs")
        self.commit(self.root, "logs")
        directory = self.env["ASAN_SESSION_DIR"]
        binding_path = self.assignment_path.with_name("session-binding.json")
        binding = {"task": "task/logs", "branch": "task/logs", "worktree": str(self.root), "directory": directory,
                   "merge_target": "sy-main", "responsibility": "owner", "contract_version": "3"}
        self.state_api.write(binding_path, binding)
        proposal = self.workflow("finish-proposal", "--verify-command", self.project.commands["test"])
        self.assertEqual(proposal.returncode, 0, proposal.stderr)
        args = self.proposal_args(proposal.stdout, True)
        self.assertEqual(self.workflow("finish", *args).returncode, 0)
        target = str(self.root / directory / "handoff.md")
        result = self.hook("pre-tool", tool_name="Write", tool_input={"file_path": target, "content": "병합 후 검증 미완료 기록"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.hook("post-tool", tool_name="Write", tool_input={"file_path": target}, tool_response={"success": True})
        self.assertEqual(self.state_api.read(binding_path), binding)
        for target in (str(self.root / ".claude/logs/sessions/another/handoff.md"), str(self.root / "src/App.tsx")):
            denied = self.hook("pre-tool", tool_name="Write", tool_input={"file_path": target, "content": "denied"})
            self.assertNotEqual(denied.returncode, 0)
