from __future__ import annotations

import json
import os
import shlex
import sys
from pathlib import Path
from unittest.mock import patch

import test_guard
from test_remediation import WorkflowFixture
from agent_policy.core import ProjectConfig, render_project


class ChildCompletionTests(WorkflowFixture):
    def pair(self, project="user-ui", parent="reservation-detail-ui", child="reservation-mock-logic",
             parent_host="claude", child_host="codex"):
        self.project = ProjectConfig(project, "test", self.root, self.project.commands)
        for relative, content in render_project(self.project).items():
            path = self.snapshot / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        self.guard = self.module(self.runtime / "managed_policy_guard.py")
        self.api = self.guard.runtime_state
        self.parent = "task/" + parent
        self.child = "task/" + child
        self.source = self.directory / child
        (self.root / "src/shared/ui").mkdir(parents=True)
        (self.root / "src/shared/ui/Button.tsx").write_text("export const Button = () => null;\n")
        self.git("add", "src/shared/ui")
        self.git("commit", "-qm", "shared fixture")
        proposed = self.workflow("proposal", "--branch", self.parent, "--parent", "sy-main",
                                 "--purpose", parent, "--scope", "src", "--reason", "부모 통합 회귀",
                                 "--role", "ui", "--git-integrator", parent_host)
        self.assertEqual(proposed.returncode, 0, proposed.stderr)
        created = self.workflow("create", *self.proposal_args(proposed.stdout))
        self.assertEqual(created.returncode, 0, created.stderr)
        proposed = self.workflow("proposal", "--branch", self.child, "--parent", self.parent,
                                 "--purpose", child, "--scope", "src", "--reason", "자식 통합 회귀",
                                 "--role", "logic", "--git-integrator", child_host, "--worktree", str(self.source))
        self.assertEqual(proposed.returncode, 0, proposed.stderr)
        self.assertEqual(self.workflow("create", *self.proposal_args(proposed.stdout)).returncode, 0)
        self.commit(self.source, "child_result")
        self.source_head = self.git("rev-parse", self.child)
        self.parent_head = self.git("rev-parse", self.parent)
        self.parent_id, self.child_id = "a" * 32, "b" * 32
        with patch.dict(os.environ, self.env):
            self.repository = self.api.repository_state(self.root / ".git")
        self.claims = {}
        self.sessions = {}
        for aid, host, role, root, branch in (
            (self.parent_id, parent_host, "ui", self.root, self.parent),
            (self.child_id, child_host, "logic", self.source, self.child),
        ):
            directory = f".{host}/logs/sessions/2026-09-09-{role}-{aid[:8]}"
            record = {"id": aid, "project": project, "repository": str(self.root / ".git"),
                      "host": host, "role": role, "responsibility": "owner", "worktree": str(root),
                      "task": self.parent, "native_session": aid}
            assignment = self.repository / "assignments" / aid
            self.api.write(assignment / "assignment.json", record)
            self.api.write(assignment / "session-binding.json", {
                "task": self.parent, "branch": branch, "worktree": str(root), "directory": directory,
                "responsibility": "owner", "contract_version": "3", "merge_target": self.parent if root == self.source else "sy-main",
            })
            resource = "git:" + str(root)
            claim = self.repository / "claims" / (self.api.digest(resource) + ".json")
            self.api.write(claim, {"resource": resource, "owner": aid})
            self.claims[aid] = claim
            self.sessions[aid] = root / directory
        # Production session logs can be ignored; the source binding, not Git tracking, proves provenance.
        (self.root / ".git/info/exclude").write_text(".codex/logs/\n.claude/logs/\n")
        test_guard.GuardTests.write_complete_artifacts(self.sessions[self.child_id])
        # Parent work is still ongoing and does not need a duplicate completed child artifact set.
        self.sessions[self.parent_id].mkdir(parents=True)
        (self.sessions[self.parent_id] / "handoff.md").write_text("부모 UI 구현 진행 중, 자식 Logic 변경 통합 예정\n")
        self.env.update({"ASAN_AGENT_POLICY_ASSIGNMENT": self.parent_id, "ASAN_AGENT_POLICY_ROLE": "ui",
                         "ASAN_AGENT_POLICY_PROJECT": project, "ASAN_ARTIFACT_RESPONSIBILITY": "owner",
                         "ASAN_SESSION_DIR": str(self.sessions[self.parent_id].relative_to(self.root))})
        self.event["session_id"] = self.parent_id

    def propose(self, *extra):
        result = self.workflow("finish-proposal", "--source", self.child,
                               "--verify-command", self.project.commands["test"], *extra)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.args = self.proposal_args(result.stdout, True)
        self.contract = json.loads(Path(self.args[1]).read_text())
        return result

    def tool(self, action, *args):
        script = self.snapshot / ".agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py"
        return {"tool_name": "Bash", "tool_input": {"command": shlex.join([sys.executable, "-I", str(script), action, *args])},
                "tool_use_id": action}

    def approve(self, proposed):
        self.hook("post-tool", tool_name="Skill", tool_input={"skill": "git-branch-strategy"}, tool_response={"success": True})
        self.hook("post-tool", tool_name="Read", tool_input={"file_path": "src/App.tsx"}, tool_response={"success": True})
        self.hook("post-tool", tool_name="Read", tool_input={"file_path": "src/shared/ui/Button.tsx"}, tool_response={"success": True})
        self.hook("user-prompt", prompt="proceed")
        self.hook("post-tool", **self.tool("finish-proposal", "--source", self.child,
                                            "--verify-command", self.project.commands["test"]),
                  tool_response={"exit_code": 0, "stdout": proposed.stdout})
        self.hook("user-prompt", prompt="승인 " + self.args[-1])

    def assert_allowed(self, result):
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertNotIn('"deny"', result.stdout)

    def run_parent_lifecycle(self, **pair):
        self.pair(**pair)
        proposal_tool = self.tool("finish-proposal", "--source", self.child,
                                  "--verify-command", self.project.commands["test"])
        self.assert_allowed(self.hook("pre-tool", **proposal_tool))
        proposed = self.propose()
        self.assertEqual(self.contract["integration_worktree"], str(self.root))
        self.assertEqual(self.contract["source_worktree"], str(self.source))
        self.approve(proposed)
        for action in ("finish", "verify", "close"):
            tool = self.tool(action, *self.args)
            self.assert_allowed(self.hook("pre-tool", **tool))
            result = self.workflow(action, *self.args)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assert_allowed(self.hook("post-tool", **tool, tool_response={"exit_code": 0, "stdout": result.stdout}))
        self.assertEqual(self.git("rev-parse", self.parent), self.source_head)
        self.assertEqual(self.git("config", f"branch.{self.child}.asan-state"), "CLOSED")
        self.assertEqual(self.git("config", f"branch.{self.parent}.asan-state"), "ACTIVE")
        self.assertEqual(self.api.read(self.claims[self.parent_id])["owner"], self.parent_id)
        self.assertFalse(self.claims[self.child_id].exists())
        self.assertTrue(self.source.is_dir())
        binding = self.api.read(self.repository / "assignments" / self.parent_id / "session-binding.json")
        self.assertEqual(binding["branch"], self.parent)
        self.assertEqual(self.git("config", f"branch.{self.child}.asan-git-integrator"), "codex")
        self.assert_allowed(self.hook("pre-tool", **self.tool("close", *self.args)))
        self.assertEqual(self.workflow("close", *self.args).returncode, 0)

    def test_user_reservation_parent_accepts_codex_child_without_releasing_parent(self):
        self.run_parent_lifecycle()

    def test_admin_news_parent_accepts_codex_child_without_releasing_parent(self):
        self.run_parent_lifecycle(project="admin-ui", parent="news-management-ui", child="news-management-logic")

    def test_parent_cannot_reuse_legacy_source_finish_approval(self):
        self.pair()
        old = self.workflow("finish-proposal", "--source", self.child,
                            "--verify-command", self.project.commands["test"], root=self.source)
        self.assertEqual(old.returncode, 0, old.stderr)
        old_args = self.proposal_args(old.stdout, True)
        denied = self.hook("pre-tool", **self.tool("finish", *old_args))
        self.assertTrue(denied.returncode or '"deny"' in denied.stdout)
        proposed = self.propose()
        self.assertNotEqual(self.args[-1], old_args[-1])
        self.assertIn("부모", proposed.stdout)

    def test_parent_acceptance_does_not_authorize_raw_child_git(self):
        self.pair()
        self.propose()
        denied = self.hook("pre-tool", tool_name="Bash", tool_input={"command": shlex.join([
            "git", "-C", str(self.source), "commit", "-m", "unauthorized",
        ])})
        self.assertTrue(denied.returncode or '"deny"' in denied.stdout)

    def test_source_or_target_head_changes_require_new_proposal(self):
        self.pair()
        self.propose()
        self.commit(self.source, "later")
        result = self.workflow("finish", *self.args)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.git("rev-parse", self.parent), self.parent_head)
        self.propose()
        self.commit(self.root, "parent_later")
        expected = self.git("rev-parse", self.parent)
        self.assertNotEqual(self.workflow("finish", *self.args).returncode, 0)
        self.assertEqual(self.git("rev-parse", self.parent), expected)

    def test_dirty_source_and_missing_source_artifacts_block_acceptance(self):
        self.pair()
        self.propose()
        (self.source / "src/App.tsx").write_text("uncommitted source\n")
        result = self.workflow("finish", *self.args)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.git("rev-parse", self.parent), self.parent_head)
        self.git("restore", "--", "src/App.tsx", root=self.source)
        (self.sessions[self.child_id] / "grill-me-review.md").unlink()
        self.assertNotEqual(self.workflow("finish", *self.args).returncode, 0)
        self.assertEqual(self.git("rev-parse", self.parent), self.parent_head)

    def test_changed_source_owner_or_target_contract_cannot_reuse_acceptance(self):
        self.pair()
        self.propose()
        claim = self.api.read(self.claims[self.child_id])
        self.api.write(self.claims[self.child_id], {**claim, "owner": "c" * 32})
        self.assertNotEqual(self.workflow("finish", *self.args).returncode, 0)
        self.api.write(self.claims[self.child_id], claim)
        self.git("config", f"branch.{self.parent}.asan-contract-sha256", "0" * 64)
        self.assertNotEqual(self.workflow("finish", *self.args).returncode, 0)
        self.assertEqual(self.git("rev-parse", self.parent), self.parent_head)

    def test_child_owner_cannot_execute_parent_acceptance_contract(self):
        self.pair()
        self.propose()
        self.env.update({"ASAN_AGENT_POLICY_ASSIGNMENT": self.child_id, "ASAN_AGENT_POLICY_ROLE": "logic"})
        result = self.workflow("finish", *self.args, root=self.source)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.git("rev-parse", self.parent), self.parent_head)

    def test_acceptance_keeps_failed_verification_open_and_ownership_reserved(self):
        self.pair()
        self.propose()
        self.assertEqual(self.workflow("finish", *self.args).returncode, 0)
        workflow = self.module(self.snapshot / ".agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py")
        # Fail only the registered validation command; all Git checks remain real.
        original = workflow.subprocess.run
        def run(command, *args, **kwargs):
            if tuple(command) == tuple(self.contract["validation_commands"][0]):
                import subprocess
                return subprocess.CompletedProcess(command, 1)
            return original(command, *args, **kwargs)
        with patch.dict(os.environ, self.env), patch.object(workflow.subprocess, "run", side_effect=run):
            with self.assertRaisesRegex(SystemExit, "사후 검증이 실패"):
                workflow.verify(workflow.build_parser().parse_args(["verify", *self.args]), self.guard.branch_guard, self.root)
        self.assertNotEqual(self.workflow("close", *self.args).returncode, 0)
        self.assertEqual(self.git("config", f"branch.{self.child}.asan-state"), "READY_TO_MERGE")
        self.assertEqual(self.api.read(self.claims[self.child_id])["owner"], self.child_id)
        self.assertEqual(self.api.read(self.claims[self.parent_id])["owner"], self.parent_id)

    def test_acceptance_rejects_cleanup_of_other_assignments_worktree(self):
        self.pair()
        self.propose()
        denied = self.workflow("finish-proposal", "--source", self.child, "--cleanup",
                               "--verify-command", self.project.commands["test"])
        self.assertNotEqual(denied.returncode, 0)
        self.assertIn("cleanup", denied.stderr)

    def test_parent_acceptance_requires_its_own_new_sha_approval(self):
        self.pair()
        proposed = self.propose()
        self.approve(proposed)
        # A different approved contract cannot authorize this executor-bound proposal.
        with patch.dict(os.environ, self.env):
            path = self.guard.harness_state_path(self.event, self.root, "claude")
        state = self.api.read(path)
        state["approved_contracts"] = {"finish-proposal": "f" * 64}
        self.api.write(path, state)
        denied = self.hook("pre-tool", **self.tool("finish", *self.args))
        self.assertTrue(denied.returncode or '"deny"' in denied.stdout)
        self.assertIn("SHA-256", denied.stderr + denied.stdout)
        self.assertEqual(self.git("rev-parse", self.parent), self.parent_head)

    def test_pending_source_mutation_and_contributor_cannot_complete_child(self):
        self.pair()
        self.propose()
        for owner in (self.parent_id, self.child_id):
            pending = self.repository / "assignments" / owner / "pending-bindings/write.json"
            self.api.write(pending, {"call": "in-flight-write"})
            result = self.workflow("finish", *self.args)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("결과 미확인", result.stderr)
            pending.unlink()
        path = self.repository / "assignments" / self.parent_id / "assignment.json"
        self.api.write(path, {**self.api.read(path), "responsibility": "contributor"})
        self.assertNotEqual(self.workflow("finish", *self.args).returncode, 0)
        self.assertEqual(self.git("rev-parse", self.parent), self.parent_head)

    def test_source_owner_still_cannot_mutate_parent_with_legacy_contract(self):
        self.pair()
        self.env.update({"ASAN_AGENT_POLICY_ASSIGNMENT": self.child_id, "ASAN_AGENT_POLICY_ROLE": "logic",
                         "ASAN_SESSION_DIR": str(self.sessions[self.child_id].relative_to(self.source))})
        self.event["session_id"] = self.child_id
        proposed = self.workflow("finish-proposal", "--verify-command", self.project.commands["test"], root=self.source)
        self.assertEqual(proposed.returncode, 0, proposed.stderr)
        args = self.proposal_args(proposed.stdout, True)
        tool = self.tool("finish", *args)
        tool["tool_input"]["workdir"] = str(self.source)
        denied = self.hook("pre-tool", "codex", **tool)
        self.assertTrue(denied.returncode or '"deny"' in denied.stdout)
        self.assertIn("소유자가 다른 assignment", denied.stderr + denied.stdout)
        self.assertNotEqual(self.workflow("finish", *args, root=self.source).returncode, 0)
        self.assertEqual(self.git("rev-parse", self.parent), self.parent_head)

    def test_parent_authority_is_independent_of_host_and_role_pairing(self):
        self.pair(parent_host="codex", child_host="claude")
        self.propose()
        tool = self.tool("finish", *self.args)
        with patch.dict(os.environ, self.env):
            self.assertIsNone(self.guard.branch_workflow_integrator_denial(
                {**self.event, **tool}, self.root, "codex", tool["tool_input"]["command"]))
        for action in ("finish", "verify", "close"):
            result = self.workflow(action, *self.args)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.api.read(self.claims[self.parent_id])["owner"], self.parent_id)
        self.assertFalse(self.claims[self.child_id].exists())

    def test_close_resumes_after_closed_metadata_write_was_interrupted(self):
        self.pair()
        self.propose()
        for action in ("finish", "verify"):
            self.assertEqual(self.workflow(action, *self.args).returncode, 0)
        workflow = self.module(self.snapshot / ".agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py")
        with patch.dict(os.environ, self.env), patch.object(workflow, "_write_closed_record", side_effect=RuntimeError("interrupted")):
            with self.assertRaisesRegex(RuntimeError, "interrupted"):
                workflow.close(workflow.build_parser().parse_args(["close", *self.args]), self.guard.branch_guard, self.root)
        self.assertEqual(self.git("config", f"branch.{self.child}.asan-state"), "CLOSED")
        self.assertTrue(self.claims[self.child_id].exists())
        result = self.workflow("close", *self.args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.claims[self.child_id].exists())
        self.assertEqual(self.api.read(self.claims[self.parent_id])["owner"], self.parent_id)

    def test_source_write_started_during_finish_validation_is_not_merged(self):
        self.pair()
        self.propose()
        workflow = self.module(self.snapshot / ".agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py")
        check = workflow.assert_integration_owner
        pending = self.repository / "assignments" / self.child_id / "pending-bindings/new-write.json"
        def concurrent_source_write(*args, **kwargs):
            check(*args, **kwargs)
            self.api.write(pending, {"call": "source-write-started-after-initial-check"})
        with patch.dict(os.environ, self.env), patch.object(workflow, "assert_integration_owner", side_effect=concurrent_source_write):
            with self.assertRaisesRegex(SystemExit, "결과 미확인"):
                workflow.finish(workflow.build_parser().parse_args(["finish", *self.args]), self.guard.branch_guard, self.root)
        self.assertEqual(self.git("rev-parse", self.parent), self.parent_head)
        self.assertEqual(self.git("config", f"branch.{self.child}.asan-state"), "ACTIVE")

    def test_parent_cannot_start_next_merge_before_child_verify_and_close(self):
        self.pair()
        self.propose()
        self.assertEqual(self.workflow("finish", *self.args).returncode, 0)
        proposed = self.workflow("finish-proposal", "--verify-command", self.project.commands["test"])
        self.assertEqual(proposed.returncode, 0, proposed.stderr)
        parent_args = self.proposal_args(proposed.stdout, True)
        before = self.git("rev-parse", "sy-main")
        with patch.dict(os.environ, self.env):
            denial = self.guard.git_ownership({**self.event, **self.tool("finish", *parent_args)}, self.root, "claude", reserve=False)
        self.assertIsNotNone(denial)
        self.assertIn("예약", denial)
        denied = self.workflow("finish", *parent_args)
        self.assertNotEqual(denied.returncode, 0, "자식 close 전에 같은 worktree의 다음 병합이 시작되었습니다.")
        self.assertIn("예약", denied.stderr)
        self.assertEqual(self.git("rev-parse", "sy-main"), before)
        for action in ("verify", "close"):
            self.assertEqual(self.workflow(action, *self.args).returncode, 0)
        self.assertEqual(self.workflow("finish", *parent_args).returncode, 0)

    def test_in_progress_parent_completion_cannot_be_orphaned_by_assignment_handoff(self):
        from agent_policy.assignment import handoff
        from agent_policy.core import PolicyError
        self.pair()
        self.propose()
        self.assertEqual(self.workflow("finish", *self.args).returncode, 0)
        original_path = self.repository / "assignments" / self.parent_id / "assignment.json"
        original = self.api.read(original_path)
        target_id = "c" * 32
        self.api.write(self.repository / "assignments" / target_id / "assignment.json", {
            **original, "id": target_id, "native_session": None, "environment": {},
        })
        with self.assertRaisesRegex(PolicyError, "부모 완료 계약"):
            handoff(self.project, self.parent_id, target_id, self.sessions[self.parent_id] / "handoff.md",
                    state_root=self.directory / "state")
        self.assertEqual(self.api.read(original_path), original)
        self.assertEqual(self.api.read(self.claims[self.parent_id])["owner"], self.parent_id)
        for action in ("verify", "close"):
            self.assertEqual(self.workflow(action, *self.args).returncode, 0)
