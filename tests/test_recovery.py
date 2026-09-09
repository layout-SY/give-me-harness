from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from test_remediation import WorkflowFixture
from agent_policy.core import PolicyError
from agent_policy.injection import prepare_injection
from agent_policy.recovery import recover_assignment, recover_integration, repository_state
from agent_policy.assignment import handoff
from agent_policy.runtime import load_runtime


class WorkflowRecoveryTests(WorkflowFixture):
    def prepared_finish(self, *, cleanup=False, worktree=False, logs=False):
        source = self.create_task("recovery", self.directory / "child" if worktree else None)
        self.commit(source, "recovery")
        if logs:
            document = source / ".claude/logs/sessions/cleanup/plan.md"
            document.parent.mkdir(parents=True)
            document.write_text("정리 전에 보존해야 할 계획 기록입니다.\n")
            self.git("add", ".claude/logs", root=source)
            self.git("commit", "-qm", "logs", root=source)
        proposal = self.workflow("finish-proposal", "--verify-command", self.project.commands["test"],
                                 *(["--cleanup"] if cleanup else []), root=source)
        self.assertEqual(proposal.returncode, 0, proposal.stderr)
        args = self.proposal_args(proposal.stdout, True)
        contract = json.loads(Path(args[1]).read_text())
        receipt = self.root / ".git/asan-agent-policy/integrations" / f"{args[-1]}.json"
        return source, args, contract, receipt

    def test_log_collection_failure_blocks_worktree_cleanup(self):
        source, args, _, receipt = self.prepared_finish(cleanup=True, worktree=True, logs=True)
        for action in ("finish", "verify"):
            result = self.workflow(action, *args)
            self.assertEqual(result.returncode, 0, result.stderr)
        workflow = self.module(self.snapshot / ".agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py")
        original = subprocess.run

        def fail_collection(command, **kwargs):
            if str(command[0]).endswith("/bin/agent-policy"):
                return subprocess.CompletedProcess(command, 1, "", "archive unavailable")
            return original(command, **kwargs)

        argv = workflow.build_parser().parse_args(["close", *args])
        with patch("subprocess.run", side_effect=fail_collection), self.assertRaises(SystemExit):
            workflow.close(argv, self.guard.branch_guard, self.root)
        self.assertTrue(source.exists())
        self.assertEqual(json.loads(receipt.read_text())["state"], "verified")

    def test_finish_recovers_merge_succeeded_before_receipt_write(self):
        source, args, _, receipt = self.prepared_finish()
        self.assertEqual(self.workflow("finish", *args, root=source).returncode, 0)
        record = json.loads(receipt.read_text())
        record.pop("integration_head")
        record["state"] = "merging"
        receipt.write_text(json.dumps(record))
        retry = self.workflow("finish", *args)
        self.assertEqual(retry.returncode, 0, retry.stderr)
        self.assertEqual(json.loads(receipt.read_text())["integration_head"], self.git("rev-parse", "HEAD"))

    def test_aborted_finish_can_retry_unchanged_approved_contract(self):
        _, args, _, receipt = self.prepared_finish()
        receipt.parent.mkdir(parents=True)
        receipt.write_text(json.dumps({"state": "aborted", "finish_sha256": args[-1], "owner": "manual"}))
        result = self.workflow("finish", *args)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_closed_cleanup_retry_passes_hook_without_deleted_source_metadata(self):
        launch = prepare_injection(self.project, "claude", "logic", build_root=self.directory / "build", state_root=self.directory / "state")
        self.env.update(launch.environment)
        self.snapshot = launch.bundle_root / "policy"
        self.runtime = self.snapshot / ".agent-policy/runtime"
        _, args, _, _ = self.prepared_finish(cleanup=True, worktree=True)
        for action in ("finish", "verify", "close"):
            result = self.workflow(action, *args)
            self.assertEqual(result.returncode, 0, result.stderr)
        script = self.snapshot / ".agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py"
        result = self.hook("pre-tool", tool_name="Bash", tool_input={"command": shlex.join([sys.executable, "-I", str(script), "close", *args])})
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_verify_and_close_are_retryable_after_cleanup(self):
        source, args, _, _ = self.prepared_finish(cleanup=True, worktree=True)
        for action in ("finish", "verify", "verify", "close", "close"):
            result = self.workflow(action, *args)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(source.exists())
        self.assertEqual(self.git("branch", "--list", "task/recovery"), "")

    def test_workflow_body_rechecks_integration_owner(self):
        _, args, _, _ = self.prepared_finish()
        self.assertEqual(self.workflow("finish", *args).returncode, 0)
        self.env["ASAN_AGENT_POLICY_ASSIGNMENT"] = "b" * 32
        result = self.workflow("verify", *args)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("assignment", result.stderr)

    def test_changed_head_never_reuses_finish_approval(self):
        source, args, _, receipt = self.prepared_finish()
        self.commit(source, "late")
        result = self.workflow("finish", *args)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(receipt.exists())
        self.assertEqual(self.git("config", "branch.task/recovery.asan-state"), "ACTIVE")

    def test_failed_verification_preserves_source_and_reservation(self):
        _, args, _, receipt = self.prepared_finish()
        self.assertEqual(self.workflow("finish", *args).returncode, 0)
        script = self.snapshot / ".agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py"
        workflow = self.module(script)
        argv = workflow.build_parser().parse_args(["verify", *args])
        original = subprocess.run

        def fail_validation(command, **kwargs):
            if tuple(command) == ("git", "status", "--porcelain") and kwargs.get("timeout") == 600:
                return subprocess.CompletedProcess(command, 1)
            return original(command, **kwargs)

        with patch("subprocess.run", side_effect=fail_validation), self.assertRaises(SystemExit):
            workflow.verify(argv, self.guard.branch_guard, self.root)
        self.assertEqual(self.git("config", "branch.task/recovery.asan-state"), "READY_TO_MERGE")
        self.assertEqual(json.loads(receipt.read_text())["state"], "merged")
        self.assertTrue(any((self.root / ".git/asan-agent-policy/integration-targets").glob("*.json")))


class InputRecoveryTests(WorkflowFixture):
    def test_child_scope_expansion_needs_implementation_approval(self):
        self.create_task("scope-root")
        self.hook("post-tool", tool_name="Skill", tool_input={"skill": "policy"}, tool_response={"success": True})
        self.hook("post-tool", tool_name="Read", tool_input={"file_path": "src/App.tsx"}, tool_response={"success": True})
        self.hook("user-prompt", prompt="proceed")
        parent_write = {"tool_name": "Write", "tool_input": {"file_path": "src/App.tsx"}, "tool_use_id": "parent"}
        self.assertEqual(self.hook("pre-tool", **parent_write).returncode, 0)
        self.hook("post-tool", **parent_write, tool_response={"success": True})
        child = self.directory / "expanded"
        proposed = self.workflow("proposal", "--branch", "task/expanded", "--parent", "task/scope-root",
                                 "--purpose", "추가 범위", "--scope", "extra", "--reason", "별도 구현 승인 필요",
                                 "--role", "logic", "--git-integrator", "claude", "--worktree", str(child))
        self.assertEqual(proposed.returncode, 0, proposed.stderr)
        args = self.proposal_args(proposed.stdout)
        self.hook("user-prompt", prompt="승인 " + args[-1])
        script = self.snapshot / ".agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py"
        event = {"tool_name": "Bash", "tool_input": {"command": shlex.join([sys.executable, "-I", str(script), "create", *args])}, "tool_use_id": "create-child"}
        self.assertEqual(self.hook("pre-tool", **event).returncode, 0)
        self.assertEqual(self.workflow("create", *args).returncode, 0)
        self.hook("post-tool", **event, tool_response={"exit_code": 0})
        result = self.hook("pre-tool", tool_name="Write", tool_input={"file_path": str(child / "extra/new.ts")})
        self.assertEqual(result.returncode, 2)
        self.assertIn("구현 승인", result.stderr)
        self.hook("user-prompt", prompt="proceed")
        result = self.hook("pre-tool", tool_name="Write", tool_input={"file_path": str(child / "extra/new.ts")})
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_owned_plan_change_revokes_only_implementation_approval(self):
        relative = ".claude/logs/sessions/plan-change/plan.md"
        event = {"tool_name": "Write", "tool_input": {"file_path": relative}, "tool_use_id": "plan"}
        self.assertEqual(self.hook("pre-tool", **event).returncode, 0)
        path = self.root / relative
        path.parent.mkdir(parents=True)
        path.write_text("승인할 구현 계획과 범위가 기록되어 있습니다.\n")
        self.hook("post-tool", **event, tool_response={"success": True})
        self.hook("user-prompt", prompt="proceed")
        self.hook("user-prompt", prompt="승인 " + "a" * 64)
        self.assertTrue(self.state()["implementation_approved"])
        path.write_text("이전과 다른 구현 계획 및 확장 범위입니다.\n")
        self.hook("user-prompt", prompt="진행 상황을 알려줘")
        self.assertFalse(self.state()["implementation_approved"])
        self.assertEqual(self.state()["approved_contracts"]["explicit"], "a" * 64)

    def test_command_approval_cannot_move_to_another_directory(self):
        tool = {"tool_name": "Bash", "tool_input": {"command": "npm run build", "workdir": str(self.root)}}
        self.hook("pre-tool", "codex", **tool)
        self.hook("user-prompt", "codex", prompt="명령 실행 승인")
        tool["tool_input"]["workdir"] = str(self.root / "src")
        result = self.hook("pre-tool", "codex", **tool)
        self.assertIn('"deny"', result.stdout)

    def test_merged_task_can_enter_diagnostic_launcher(self):
        from agent_policy.cli import task_start_denial
        from dataclasses import replace
        source = self.create_task("merged-entry", self.directory / "child")
        self.commit(source, "entry")
        result = self.workflow("finish-proposal", "--verify-command", self.project.commands["test"], root=source)
        args = self.proposal_args(result.stdout, True)
        self.assertEqual(self.workflow("finish", *args, root=source).returncode, 0)
        self.assertIsNone(task_start_denial(replace(self.project, path=source)))

    def test_multiple_pending_contracts_require_explicit_sha_selection(self):
        script = self.snapshot / ".agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py"
        events = []
        for index, action in enumerate(("proposal", "finish-proposal")):
            event = {"tool_name": "Bash", "tool_input": {"command": shlex.join([sys.executable, "-I", str(script), action])},
                     "tool_use_id": str(index), "tool_response": {"exit_code": 0, "stdout": "SHA-256: " + str(index + 1) * 64}}
            events.append(event)
            self.hook("post-tool", **event)
        self.hook("user-prompt", prompt="proceed")
        self.assertFalse(self.state().get("approved_contracts"))
        self.assertIsNot(self.state().get("implementation_approved"), True)
        self.hook("user-prompt", prompt="승인 " + "1" * 64)
        self.assertEqual(self.state()["approved_contracts"], {"proposal": "1" * 64})
        self.hook("post-tool", **events[0])
        self.assertEqual(self.state()["approved_contracts"], {"proposal": "1" * 64})

    def test_malformed_pretool_is_denied_on_every_host(self):
        for host in ("codex", "claude", "opencode"):
            for raw in ("{", "[]", '{"tool_name": "Write", "tool_input": null}'):
                result = subprocess.run([sys.executable, "-I", str(self.runtime / "managed_policy_guard.py"), "pre-tool", host],
                                        input=raw, text=True, capture_output=True,
                                        env={**os.environ, **self.env})
                self.assertTrue(result.returncode == 2 or '"deny"' in result.stdout, (host, raw, result))


class ExplicitRecoveryTests(WorkflowFixture):
    def test_concurrent_first_writes_have_one_artifact_owner(self):
        from concurrent.futures import ThreadPoolExecutor
        common_options = {"build_root": self.directory / "build", "state_root": self.directory / "state",
                          "session_dir": ".claude/logs/sessions/shared"}
        launches = [prepare_injection(self.project, "claude", "logic", **common_options) for _ in range(2)]

        def reserve(index):
            launch = launches[index]
            event = {"cwd": str(self.root), "session_id": f"native-{index}", "tool_name": "Write",
                     "tool_input": {"file_path": ".claude/logs/sessions/shared/plan.md"}, "tool_use_id": "first"}
            return subprocess.run([sys.executable, "-I", str(launch.bundle_root / "policy/.agent-policy/runtime/managed_policy_guard.py"), "pre-tool", "claude"],
                                  input=json.dumps(event), text=True, capture_output=True,
                                  env={**os.environ, **launch.environment}).returncode

        with ThreadPoolExecutor(max_workers=2) as executor:
            self.assertEqual(sorted(executor.map(reserve, (0, 1))), [0, 2])

    def test_handoff_is_exclusive_and_recovers_interrupted_transfer(self):
        options = {"build_root": self.directory / "build", "state_root": self.directory / "state"}
        first = prepare_injection(self.project, "claude", "logic", **options)
        second = prepare_injection(self.project, "claude", "logic", **options)
        source, target = [launch.environment["ASAN_AGENT_POLICY_ASSIGNMENT"] for launch in (first, second)]
        state = load_runtime("runtime_state")
        repository = repository_state(self.project, options["state_root"])
        resource = "git:" + str(self.root)
        claim_path = repository / "claims" / f"{state.digest(resource)}.json"
        state.write(claim_path, {"resource": resource, "owner": source})
        document = self.root / first.environment["ASAN_SESSION_DIR"] / "handoff.md"
        document.parent.mkdir(parents=True)
        document.write_text("현재 작업과 Git 소유권을 다음 담당 세션으로 인계합니다. 다음 조치는 검증입니다.\n")
        _, digest = handoff(self.project, source, target, document, state_root=options["state_root"])
        self.assertEqual(state.read(claim_path)["owner"], source)
        with self.assertRaises(PolicyError):
            handoff(self.project, source, target, document, "f" * 64, options["state_root"])
        original = state.write

        def crash_after_claim(path, value):
            original(path, value)
            if path == claim_path:
                raise OSError("simulated process interruption")

        with patch("agent_policy.assignment.load_runtime", return_value=state), patch.object(state, "write", side_effect=crash_after_claim), self.assertRaises(OSError):
            handoff(self.project, source, target, document, digest, options["state_root"])
        with patch.dict(os.environ, second.environment), self.assertRaises(RuntimeError):
            state.bind_native_session(self.root / ".git", "claude", "new-native")
        handoff(self.project, source, target, document, digest, options["state_root"])
        self.assertEqual(state.read(claim_path)["owner"], target)
        with patch.dict(os.environ, first.environment), self.assertRaises(RuntimeError):
            state.bind_native_session(self.root / ".git", "claude", "old-native")
        with patch.dict(os.environ, second.environment):
            state.bind_native_session(self.root / ".git", "claude", "new-native")
        self.assertFalse((repository / "assignments" / target / "session-binding.json").exists())

    def test_lost_post_tool_requires_reviewed_current_state(self):
        launch = prepare_injection(self.project, "claude", "logic", build_root=self.directory / "build",
                                   state_root=self.directory / "state")
        self.env.update(launch.environment)
        self.runtime = launch.bundle_root / "policy/.agent-policy/runtime"
        directory = self.root / self.env["ASAN_SESSION_DIR"]
        target = directory / "handoff.md"
        event = {"tool_name": "Write", "tool_input": {"file_path": str(target)}, "tool_use_id": "lost"}
        self.assertEqual(self.hook("pre-tool", **event).returncode, 0)
        directory.mkdir(parents=True)
        target.write_text("실행 직후 연결이 끊겼습니다. 다음 세션에 작업 상태를 인계합니다.\n")
        options = {"state_root": self.directory / "state"}
        assignment = self.env["ASAN_AGENT_POLICY_ASSIGNMENT"]
        path, digest = recover_assignment(self.project, assignment, "lost", "confirmed", **options)
        state = repository_state(self.project, options["state_root"]) / "assignments" / assignment
        self.assertFalse((state / "session-binding.json").exists())
        target.write_text(target.read_text() + "승인 전에 상태가 변경되었습니다.\n")
        with self.assertRaises(PolicyError):
            recover_assignment(self.project, assignment, "lost", "confirmed", digest, **options)
        _, digest = recover_assignment(self.project, assignment, "lost", "confirmed", **options)
        recover_assignment(self.project, assignment, "lost", "confirmed", digest, **options)
        self.assertEqual(json.loads((state / "session-binding.json").read_text())["directory"], self.env["ASAN_SESSION_DIR"])
        self.assertFalse(list((state / "pending-bindings").glob("*.json")))
        self.assertFalse((state / "harness.json").exists())

    def test_conflict_is_preserved_until_exact_abort_contract_approval(self):
        source = self.create_task("conflict", self.directory / "child")
        (source / "src/App.tsx").write_text("source change\n")
        self.git("commit", "-qam", "source", root=source)
        (self.root / "src/App.tsx").write_text("target change\n")
        self.git("commit", "-qam", "target")
        proposed = self.workflow("finish-proposal", "--merge-strategy", "merge-commit", "--verify-command",
                                 self.project.commands["test"], root=source)
        self.assertEqual(proposed.returncode, 0, proposed.stderr)
        args = self.proposal_args(proposed.stdout, True)
        failed = self.workflow("finish", *args, root=source)
        self.assertNotEqual(failed.returncode, 0)
        self.assertTrue((self.root / ".git/MERGE_HEAD").exists())
        self.assertNotEqual(self.workflow("close", *args).returncode, 0)
        options = {"state_root": self.directory / "state"}
        _, digest = recover_integration(self.project, Path(args[1]), args[-1], **options)
        self.assertTrue((self.root / ".git/MERGE_HEAD").exists())
        with self.assertRaises(PolicyError):
            recover_integration(self.project, Path(args[1]), args[-1], "0" * 64, **options)
        recover_integration(self.project, Path(args[1]), args[-1], digest, **options)
        self.assertFalse((self.root / ".git/MERGE_HEAD").exists())
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertEqual(self.git("config", "branch.task/conflict.asan-state"), "ACTIVE")
        self.assertTrue(source.exists())
