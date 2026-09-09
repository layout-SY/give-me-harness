from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from test_remediation import WorkflowFixture
from agent_policy import recovery
from agent_policy.core import PolicyError
from agent_policy.runtime import load_runtime


class IntegrationPreserveTests(WorkflowFixture):
    def prepared(self):
        self.owner = "a" * 32
        self.env["ASAN_AGENT_POLICY_ASSIGNMENT"] = self.owner
        self.api = load_runtime("runtime_state")
        self.repository = recovery.repository_state(self.project, self.directory / "state")
        self.api.write(self.repository / "assignments" / self.owner / "assignment.json",
                       {"project": self.project.id, "repository": str(self.root / ".git"), "host": "codex", "role": "logic"})
        self.create_task("debt")
        self.commit(self.root, "debt")
        proposed = self.workflow("finish-proposal", "--verify-command", self.project.commands["test"])
        self.assertEqual(proposed.returncode, 0, proposed.stderr)
        self.args = self.proposal_args(proposed.stdout, True)
        self.file, self.sha = Path(self.args[1]), self.args[-1]
        self.contract = json.loads(self.file.read_text())
        self.assertEqual(self.workflow("finish", *self.args).returncode, 0)
        self.receipt = self.root / ".git/asan-agent-policy/integrations" / f"{self.sha}.json"
        self.reservation = next((self.root / ".git/asan-agent-policy/integration-targets").glob("*.json"))
        self.claim = self.repository / "claims" / f"{self.api.digest('git:' + str(self.root))}.json"
        # 통합 예약이 남은 채 사용자가 직접 수행한 후속 commit을 재현한다.
        self.commit(self.root, "later")

    def preserve(self, approved=None):
        return recovery.preserve_integration(self.project, self.file, self.sha, "lint 실패를 보존하고 후속 처리를 분리",
                                             approved_sha256=approved, state_root=self.directory / "state")

    def test_preserves_unverified_merge_at_reviewed_current_head(self):
        self.prepared()
        head = self.git("rev-parse", "HEAD")
        path, digest = self.preserve()
        plan = json.loads(path.read_text())
        self.assertEqual(plan["current"]["head"], head)
        self.assertEqual(self.api.read(self.receipt)["state"], "merged")
        with self.assertRaises(PolicyError):
            self.preserve("0" * 64)
        self.preserve(digest)
        self.assertEqual(self.git("rev-parse", "HEAD"), head)
        self.assertEqual(self.git("config", "branch.task/debt.asan-state"), "PRESERVED")
        self.assertEqual(self.api.read(self.receipt)["state"], "preserved")
        self.assertFalse(self.claim.exists())
        self.assertFalse(self.reservation.exists())
        self.assertFalse((self.root / ".git/asan-agent-policy/closed/debt.json").exists())
        self.assertEqual(self.preserve(digest), (path, digest))

    def test_stale_head_dirty_or_other_owner_cannot_release_reservation(self):
        self.prepared()
        _, digest = self.preserve()
        before = self.claim.read_bytes()
        record = self.api.read(self.claim)
        record["owner"] = "b" * 32
        self.api.write(self.claim, record)
        with self.assertRaises(PolicyError):
            self.preserve(digest)
        self.claim.write_bytes(before)
        (self.root / "src/dirty.tsx").write_text("dirty")
        with self.assertRaises(PolicyError):
            self.preserve(digest)
        (self.root / "src/dirty.tsx").unlink()
        self.commit(self.root, "newer")
        with self.assertRaises(PolicyError):
            self.preserve(digest)
        self.assertTrue(self.reservation.exists())
        self.assertEqual(self.api.read(self.receipt)["state"], "merged")

    def test_interrupted_preservation_reuses_original_review(self):
        self.prepared()
        path, digest = self.preserve()
        write = self.api.write

        def interrupted(destination, value):
            if destination == self.receipt and value.get("state") == "preserved":
                raise OSError("simulated receipt write failure")
            write(destination, value)

        with patch.object(recovery, "load_runtime", return_value=self.api), patch.object(self.api, "write", side_effect=interrupted):
            with self.assertRaises(OSError):
                self.preserve(digest)
        self.assertTrue(self.reservation.exists())
        self.assertEqual(self.preserve(digest), (path, digest))
        self.assertFalse(self.reservation.exists())

    def test_related_manual_merge_is_preserved_with_its_owner_in_review(self):
        self.prepared()
        self.git("branch", "task/manual-ui", "HEAD")
        for key, value in {"state": "ACTIVE", "contract-version": "3", "contract-sha256": "d" * 64, "merge-target": "sy-main"}.items():
            self.git("config", f"branch.task/manual-ui.asan-{key}", value)
        other = self.repository / "assignments" / ("b" * 32)
        self.api.write(other / "assignment.json", {"project": self.project.id, "repository": str(self.root / ".git"),
                       "host": "claude", "role": "ui", "task": "task/manual-ui"})
        args = (self.project, self.file, self.sha, "검증 미완료 및 수동 병합 보존", ("task/manual-ui",))
        path, digest = recovery.preserve_integration(*args, state_root=self.directory / "state")
        self.assertIn("b" * 32, json.loads(path.read_text())["participants"])
        self.api.write(other / "pending-bindings/tool.json", {"call": "pending"})
        with self.assertRaises(PolicyError):
            recovery.preserve_integration(*args, approved_sha256=digest, state_root=self.directory / "state")
        (other / "pending-bindings/tool.json").unlink()
        recovery.preserve_integration(*args, approved_sha256=digest, state_root=self.directory / "state")
        self.assertEqual(self.git("config", "branch.task/manual-ui.asan-state"), "PRESERVED")

    def test_failed_pending_calls_require_explicit_review_before_cancellation(self):
        self.prepared()
        pending = self.repository / "assignments" / self.owner / "pending-bindings/tool.json"
        self.api.write(pending, {"call": "failed-patch", "new_claim": "", "binding": {"worktree": str(self.root), "task": "task/debt"}})
        with self.assertRaises(PolicyError):
            self.preserve()
        args = (self.project, self.file, self.sha, "실패한 patch 예약을 취소하고 보존")
        path, digest = recovery.preserve_integration(*args, state_root=self.directory / "state", cancel_calls=("failed-patch",))
        self.assertTrue(pending.exists())
        self.assertEqual(json.loads(path.read_text())["cancel_calls"], ["failed-patch"])
        recovery.preserve_integration(*args, approved_sha256=digest, state_root=self.directory / "state", cancel_calls=("failed-patch",))
        self.assertFalse(pending.exists())
