"""실제 사고의 native 거절 형식과 중앙 복구 경계를 검증한다."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from agent_policy.core import load_project, PolicyError
from agent_policy.recovery import assignment_writes, repository_state
from agent_policy.runtime import load_runtime


class WriteReceiptTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.project = replace(load_project("admin-ui"), path=self.base / "repo")
        self.project.path.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.project.path, check=True)
        self.state_root = self.base / "state"
        self.repository = repository_state(self.project, self.state_root)
        self.owner, self.session = "a" * 32, "12345678-1234-1234-1234-123456789abc"
        self.receipts = load_runtime("write_receipts")
        self.state = load_runtime("runtime_state")
        self.transcript = self.base / ".claude/projects/encoded" / (self.session + ".jsonl")
        self.transcript.parent.mkdir(parents=True)
        self.target = str(self.project.path / "src/denied.ts")
        self.state.write(self.repository / "assignments" / self.owner / "assignment.json", {
            "project": "admin-ui", "repository": str(self.project.path / ".git"), "host": "claude",
            "native_session": self.session, "environment": {"CLAUDE_CONFIG_DIR": str(self.base / ".claude")}})
        self.seed("denied", self.owner, self.session)
        self.seed("other", "b" * 32, "another-session")
        self.rows = [
            {"type": "assistant", "sessionId": self.session, "uuid": "assistant-id", "message": {"content": [
                {"type": "tool_use", "id": "denied", "name": "Write", "input": {"file_path": self.target}}]}},
            {"type": "user", "sessionId": self.session, "uuid": "result-id", "sourceToolAssistantUUID": "assistant-id",
             "toolDenialKind": "automode-unavailable", "message": {"content": [{"type": "tool_result",
                 "tool_use_id": "denied", "is_error": True,
                 "content": "The server-side auto mode classifier gave no verdict (error), so auto mode cannot determine the safety of Write."}]}}]

    def seed(self, call, owner, session):
        record = {"host": "claude", "session": session, "call": call, "worktree": str(self.project.path), "created_at": 1}
        identifier = hashlib.sha256(json.dumps(["claude", session, call, str(self.project.path)]).encode()).hexdigest()
        self.state.write(self.repository / "branch-relations/v1/writes" / (identifier + ".json"), record)
        self.state.write(self.receipts.call_path(self.repository, owner, call), {"files": [{
            "owner": owner, "call": call, "path": self.target, "worktree": str(self.project.path),
            "token": call, "previous_writer": {}}]})

    def run_recovery(self, reconcile=True):
        self.transcript.write_text("\n".join(json.dumps(row) for row in self.rows) + "\n")
        return assignment_writes(self.project, self.owner, reconcile=reconcile, state_root=self.state_root)

    def test_lookup_exposes_id_and_only_matching_native_denial_is_reconciled(self):
        before = self.run_recovery(False)
        self.assertEqual(len(before["writes"]), 1)
        self.assertEqual(before["writes"][0]["paths"], [self.target])
        self.assertTrue(before["writes"][0]["denial_confirmed"])
        self.assertEqual(before["recovered"], [])
        after = self.run_recovery()
        self.assertEqual(after["recovered"], [before["writes"][0]["id"]])
        self.assertEqual(after["remaining"], [])
        self.assertEqual([v["call"] for v in self.receipts.pending_writes(self.repository)], ["other"])
        self.assertFalse(Path(self.target).exists())
        self.assertEqual(self.run_recovery()["recovered"], [])
        saved = list((self.repository / "branch-relations/v1/write-receipts").glob("*.json"))
        self.assertEqual(json.loads(saved[0].read_text())["outcome"], "not-executed")

    def test_generic_error_wrong_session_wrong_call_source_and_wrong_path_remain_pending(self):
        original = json.dumps(self.rows)
        for change in ("generic", "session", "source", "path", "success", "ambiguous", "sidechain"):
            with self.subTest(change=change):
                self.rows = json.loads(original)
                if change == "generic": self.rows[1].pop("toolDenialKind")
                if change == "session": self.rows[1]["sessionId"] = "another-session"
                if change == "source": self.rows[1]["sourceToolAssistantUUID"] = "another-call"
                if change == "path": self.rows[0]["message"]["content"][0]["input"]["file_path"] += ".other"
                if change == "success": self.rows[1]["message"]["content"][0]["is_error"] = False
                if change == "ambiguous": self.rows.append(self.rows[1])
                if change == "sidechain": self.rows[1]["isSidechain"] = True
                result = self.run_recovery()
                self.assertEqual(result["recovered"], [])
                self.assertEqual(len(result["remaining"]), 1)

    def test_denied_validation_shell_without_formatting_call_is_not_left_running(self):
        self.receipts.call_path(self.repository, self.owner, "denied").unlink()
        self.rows[0]["message"]["content"][0].update(name="Bash", input={"command": "npm run build"})
        result = self.run_recovery()
        self.assertEqual(len(result["recovered"]), 1)
        self.assertEqual(result["remaining"], [])

    def test_other_project_assignment_and_symlink_transcript_are_rejected(self):
        self.run_recovery(False)
        self.transcript.rename(self.base / "copy.jsonl")
        self.transcript.symlink_to(self.base / "copy.jsonl")
        with self.assertRaises(PolicyError):
            assignment_writes(self.project, self.owner, reconcile=True, state_root=self.state_root)
        with self.assertRaises(PolicyError):
            assignment_writes(replace(self.project, id="user-ui"), self.owner, state_root=self.state_root)

    def test_cancelled_writer_chain_is_restored_even_when_denials_arrive_out_of_order(self):
        writer = self.repository / "formatting/v1/writers" / (self.state.digest(self.target) + ".json")
        previous = {"token": "successful", "owner": self.owner, "call": "successful"}
        for call in ("first", "second"):
            self.state.write(self.receipts.call_path(self.repository, self.owner, call), {"files": [{
                "path": self.target, "owner": self.owner, "call": call, "token": call,
                "previous_writer": previous}]})
            previous = {"token": call, "owner": self.owner, "call": call}
        self.state.write(writer, previous)
        for call in ("first", "second"):
            self.receipts.cancel_unexecuted(self.repository, "claude", self.session, self.owner, call, {"event": "PermissionDenied"})
        self.assertEqual(self.state.read(writer)["token"], "successful")


if __name__ == "__main__":
    unittest.main()
