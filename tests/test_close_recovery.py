from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

from test_remediation import WorkflowFixture
from agent_policy import recovery
from agent_policy.core import PolicyError
from agent_policy.runtime import load_runtime


class CloseRecoveryTests(WorkflowFixture):
    def isolated_source(self):
        source = self.create_task("close", self.directory / "child")
        self.git("switch", "-qc", "other-task")
        (self.root / "src/App.tsx").write_text("unrelated dirty work\n")
        self.commit(source, "close")
        return source

    def legacy_contract(self):
        source = self.isolated_source()
        proposal = self.workflow("finish-proposal", "--verify-command", self.project.commands["test"], root=source)
        self.assertEqual(proposal.returncode, 0, proposal.stderr)
        args = self.proposal_args(proposal.stdout, True)
        contract = json.loads(Path(args[1]).read_text())
        contract["cleanup"] = True
        guard = self.guard.branch_guard
        digest = guard.contract_sha256(contract)
        path = Path(args[1]).with_name(digest + ".json")
        path.write_bytes(guard.contract_bytes(contract))
        self.finish_file, self.finish_sha = path, digest
        self.args = ("--proposal-file", str(path), "--proposal-sha256", digest)
        self.source, self.contract = source, contract
        self.state = load_runtime("runtime_state")
        self.repository = recovery.repository_state(self.project, self.directory / "state")
        self.owner = "a" * 32
        self.env["ASAN_AGENT_POLICY_ASSIGNMENT"] = self.owner
        self.assignment_path = self.repository / "assignments" / self.owner / "assignment.json"
        self.state.write(self.assignment_path, {"project": self.project.id, "repository": str(self.root / ".git")})
        self.claim = self.repository / "claims" / (self.state.digest("git:" + str(source)) + ".json")
        self.state.write(self.claim, {"owner": self.owner, "resource": "git:" + str(source)})
        self.receipt = self.root / ".git/asan-agent-policy/integrations" / (digest + ".json")
        self.reservation = self.root / ".git/asan-agent-policy/integration-targets" / (guard.contract_sha256({"target": "sy-main"}) + ".json")
        self.closed = self.root / ".git/asan-agent-policy/closed/close.json"
        return source

    def verified_legacy(self):
        source = self.legacy_contract()
        workflow = self.module(self.snapshot / ".agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py")
        # 과거 launcher가 허용한 계약으로 실제 Git 병합과 검증을 재현한다.
        with patch.dict(os.environ, self.env), patch.object(workflow, "validate_cleanup_layout", create=True):
            workflow.finish(workflow.build_parser().parse_args(["finish", *self.args]), self.guard.branch_guard, source)
        verified = self.workflow("verify", *self.args, root=source)
        self.assertEqual(verified.returncode, 0, verified.stderr)
        failed = self.workflow("close", *self.args, root=source)
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual(self.state.read(self.receipt)["state"], "verified")
        return source

    def recover(self, approved=None):
        return recovery.recover_close(self.project, self.finish_file, self.finish_sha, approved,
                                      state_root=self.directory / "state")

    def test_rejects_same_integration_cleanup_before_proposal(self):
        source = self.isolated_source()
        result = self.workflow("finish-proposal", "--cleanup", "--verify-command", self.project.commands["test"], root=source)
        self.assertNotEqual(result.returncode, 0, "현재 구현이 모순된 cleanup 계약을 승인 대상으로 만들었습니다.")
        self.assertIn("통합 worktree", result.stderr)
        self.assertEqual(self.git("branch", "--show-current", root=source), "task/close")
        self.assertFalse(list((self.root / ".git/asan-agent-policy/finish-proposals").glob("*.json")))

    def test_rejects_legacy_bad_contract_before_switch_or_reservation(self):
        source = self.legacy_contract()
        before = self.git("rev-parse", "sy-main")
        result = self.workflow("finish", *self.args, root=source)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.git("rev-parse", "sy-main"), before)
        self.assertEqual(self.git("branch", "--show-current", root=source), "task/close")
        self.assertFalse(self.receipt.exists())
        self.assertFalse(self.reservation.exists())

    def test_preview_then_close_preserves_verified_git_result_and_logs(self):
        source = self.verified_legacy()
        head = self.git("rev-parse", "HEAD", root=source)
        old_receipt = self.receipt.read_bytes()
        path, digest = self.recover()
        self.assertEqual(self.receipt.read_bytes(), old_receipt)
        self.assertFalse(self.closed.exists())
        self.assertEqual(json.loads(path.read_text())["effect"]["cleanup"], "deferred")
        with self.assertRaises(PolicyError):
            self.recover("0" * 64)
        self.recover(digest)
        self.assertTrue(source.is_dir())
        self.assertEqual(self.git("rev-parse", "HEAD", root=source), head)
        self.assertEqual(self.git("rev-parse", "task/close"), head)
        self.assertEqual(self.git("config", "branch.task/close.asan-state"), "CLOSED")
        self.assertEqual(self.state.read(self.closed)["finish_sha256"], self.finish_sha)
        self.assertEqual(self.state.read(self.receipt)["validation_commands"], self.contract["validation_commands"])
        self.assertFalse(self.reservation.exists())
        self.assertFalse(self.claim.exists())
        self.assertEqual((self.root / "src/App.tsx").read_text(), "unrelated dirty work\n")
        self.assertEqual(self.recover(digest), (path, digest))

    def test_changed_state_invalidates_preview_without_writes(self):
        self.verified_legacy()
        _, digest = self.recover()
        original = self.receipt.read_bytes()
        for path, field, value in ((self.reservation, "owner", "b" * 32),
                                   (self.receipt, "state", "merged"),
                                   (self.claim, "owner", "b" * 32),
                                   (self.assignment_path, "handed_off_to", "b" * 32)):
            with self.subTest(field=field, path=path.name):
                before = path.read_bytes()
                record = json.loads(before)
                record[field] = value
                path.write_text(json.dumps(record))
                with self.assertRaises(PolicyError):
                    self.recover(digest)
                path.write_bytes(before)
                self.assertFalse(self.closed.exists())
        (self.source / "src/dirty.tsx").write_text("dirty")
        with self.assertRaises(PolicyError):
            self.recover(digest)
        self.assertEqual(self.receipt.read_bytes(), original)
        self.assertTrue(self.reservation.exists())

    def test_partial_finalization_resumes_same_approval(self):
        self.verified_legacy()
        path, digest = self.recover()
        original = self.state.write

        def interrupted(destination, value):
            if destination == self.receipt and value.get("state") == "closed":
                raise OSError("simulated crash after CLOSED record")
            original(destination, value)

        with patch.object(recovery, "load_runtime", return_value=self.state), patch.object(self.state, "write", side_effect=interrupted):
            with self.assertRaises(OSError):
                self.recover(digest)
        self.assertEqual(self.git("config", "branch.task/close.asan-state"), "CLOSED")
        self.assertTrue(self.reservation.exists())
        self.assertEqual(self.recover(digest), (path, digest))
        self.assertEqual(self.state.read(self.receipt)["state"], "closed")
        self.assertFalse(self.reservation.exists())

    def test_recovery_cannot_finalize_unverified_merge(self):
        self.verified_legacy()
        record = self.state.read(self.receipt)
        record["state"] = "merged"
        self.state.write(self.receipt, record)
        with self.assertRaises(PolicyError):
            self.recover()
        self.assertFalse(self.closed.exists())

    def test_changed_source_or_target_head_rejects_approval(self):
        self.verified_legacy()
        _, digest = self.recover()
        self.git("branch", "-f", "task/close", self.contract["target_head"])
        with self.assertRaises(PolicyError):
            self.recover(digest)
        self.git("branch", "-f", "task/close", self.contract["source_head"])
        self.commit(self.source, "later")
        with self.assertRaises(PolicyError):
            self.recover(digest)
        self.assertFalse(self.closed.exists())
        self.assertEqual(self.state.read(self.receipt)["state"], "verified")

    def test_final_journal_retry_preserves_later_owners(self):
        self.verified_legacy()
        path, digest = self.recover()
        original = self.state.write

        def interrupted(destination, value):
            if destination == path.with_suffix(".transaction.json") and value.get("state") == "complete":
                raise OSError("simulated crash after reservation release")
            original(destination, value)

        with patch.object(recovery, "load_runtime", return_value=self.state), patch.object(self.state, "write", side_effect=interrupted):
            with self.assertRaises(OSError):
                self.recover(digest)
        self.assertFalse(self.reservation.exists())
        later_reservation = {"owner": "b" * 32, "finish_sha256": "c" * 64}
        later_claim = {"owner": "b" * 32, "resource": "git:" + str(self.source)}
        self.state.write(self.reservation, later_reservation)
        self.state.write(self.claim, later_claim)
        for _ in range(2):
            self.assertEqual(self.recover(digest), (path, digest))
            self.assertEqual(self.state.read(self.reservation), later_reservation)
            self.assertEqual(self.state.read(self.claim), later_claim)

    def test_contract_tampering_and_other_cleanup_layout_are_rejected(self):
        self.verified_legacy()
        original = self.finish_file.read_bytes()
        self.finish_file.write_text("{}")
        with self.assertRaises(PolicyError):
            self.recover()
        self.finish_file.write_bytes(original)
        contract = {**self.contract, "worktree": str(self.root)}
        guard = self.guard.branch_guard
        digest = guard.contract_sha256(contract)
        path = self.finish_file.with_name(digest + ".json")
        path.write_bytes(guard.contract_bytes(contract))
        with self.assertRaises(PolicyError):
            recovery.recover_close(self.project, path, digest, state_root=self.directory / "state")
        self.assertFalse(self.closed.exists())
