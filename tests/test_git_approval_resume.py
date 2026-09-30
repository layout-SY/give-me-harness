"""Git이 시작되기 전 차단과 이미 시작된 실행의 재시도를 구분한다."""
import json
import os
import unittest
from unittest.mock import patch

import test_relation_operations as relations


class GitApprovalResumeTests(unittest.TestCase):
    def setUp(self):
        self.fixture = relations.RelationOperationTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.operations = self.fixture.module("git_operations")
        self.environment = patch.dict(os.environ, self.fixture.env, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def blocked_operation(self, host):
        f, ops = self.fixture, self.operations
        event = {"session_id": host + "-test", "tool_call_id": "pending-write"}
        operation = ops.prepare_git(f.root, f.root,
            "git commit --allow-empty -m resumed", host, event)
        command = ops.command(operation)
        f.event("pre-tool", command, host=host)
        if host != "claude":
            f.event("user-prompt", host=host, prompt="명령 실행 승인")
            f.event("pre-tool", command, host=host)
        ops.reserve_write(f.root, event, host, [f.root])
        before = f.git("rev-parse", "HEAD")
        with self.assertRaisesRegex(RuntimeError, "결과 미확인"):
            ops.execute(f.root, operation["id"])
        saved = ops.load(f.root, operation["id"])
        self.assertEqual(saved["stage"], "prepared")
        self.assertFalse(saved.get("results"))
        self.assertEqual(before, f.git("rev-parse", "HEAD"))
        ops.complete_write(f.root, {**event, "tool_response": {"success": True}}, host)
        return saved, event

    def test_preflight_failure_reuses_same_approval_once_for_all_hosts(self):
        for host in ("codex", "claude", "opencode"):
            with self.subTest(host=host):
                saved, _ = self.blocked_operation(host)
                retry = self.fixture.event("pre-tool", self.operations.command(saved), host=host)
                self.assertEqual(retry.returncode, 0, retry.stderr)
                self.assertNotIn('"ask"', retry.stdout)
                self.assertNotIn('"deny"', retry.stdout)
                if host == "claude":
                    self.assertEqual(json.loads(retry.stdout)["hookSpecificOutput"].get("permissionDecision"), "allow")
                result = self.operations.execute(self.fixture.root, saved["id"])
                self.assertEqual(result["stage"], "done")
                self.assertNotIn("reason", result)
                with self.assertRaisesRegex(RuntimeError, "승인"):
                    self.operations.execute(self.fixture.root, saved["id"])

    def test_resume_cannot_transfer_to_another_actor_or_an_executing_operation(self):
        saved, event = self.blocked_operation("codex")
        root, ops = self.fixture.root, self.operations
        self.assertTrue(ops.resumable(root, saved, "codex", event))
        self.assertFalse(ops.resumable(root, saved, "claude", event))
        self.assertFalse(ops.resumable(root, saved, "codex", {"session_id": "another"}))
        with patch.dict(os.environ, {"ASAN_AGENT_POLICY_ASSIGNMENT": "a" * 32}):
            self.assertFalse(ops.resumable(root, saved, "codex", event))
        self.assertFalse(ops.resumable(root, {**saved, "stage": "executing"}, "codex", event))
        self.assertFalse(ops.resumable(root, {**saved, "results": ["partial"]}, "codex", event))
        self.assertFalse(ops.resumable(root, {**saved, "authorized": {"fingerprint": saved["fingerprint"]}}, "codex", event))

    def test_revocation_invalidates_saved_consent_and_an_already_issued_ticket(self):
        saved, event = self.blocked_operation("codex")
        self.fixture.event("pre-tool", self.operations.command(saved))
        self.fixture.event("user-prompt", prompt="명령 실행 승인 취소")
        with self.assertRaisesRegex(RuntimeError, "취소|철회"):
            self.operations.execute(self.fixture.root, saved["id"])
        self.assertFalse(self.operations.resumable(self.fixture.root, saved, "codex", event))
        command = self.operations.command(saved)
        self.fixture.event("pre-tool", command)
        self.fixture.event("user-prompt", prompt="명령 실행 승인")
        self.fixture.event("pre-tool", command)
        self.assertEqual(self.operations.execute(self.fixture.root, saved["id"])["stage"], "done")

    def test_unexecuted_native_permission_request_is_not_durable_consent(self):
        f, ops = self.fixture, self.operations
        event = {"session_id": "claude-test"}
        operation = ops.prepare_git(f.root, f.root, "git commit --allow-empty -m requested", "claude", event)
        f.event("pre-tool", ops.command(operation), host="claude")
        self.assertFalse(ops.resumable(f.root, ops.load(f.root, operation["id"]), "claude", event))
        retry = f.event("pre-tool", ops.command(operation), host="claude")
        self.assertIn('"ask"', retry.stdout)

    def test_changed_contents_cannot_resume_even_with_saved_consent(self):
        saved, _ = self.blocked_operation("codex")
        self.fixture.git("commit", "--allow-empty", "-qm", "other change")
        retry = self.fixture.event("pre-tool", self.operations.command(saved))
        self.assertIn("변경", retry.stdout + retry.stderr)
        self.assertEqual(self.fixture.git("log", "-1", "--format=%s"), "other change")


if __name__ == "__main__":
    unittest.main()
