from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from dataclasses import replace
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import test_injection as injection_fixtures

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from agent_policy import injection, sessions
from agent_policy.core import PolicyError, sha256_bytes


class SessionResumeTests(unittest.TestCase):
    native = "00000000-0000-4000-8000-000000000001"

    def setUp(self):
        self.fixture = injection_fixtures.InjectionTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.addCleanup(self.fixture.tearDown)
        (self.fixture.project_root / "AGENTS.md").unlink()
        shutil.rmtree(self.fixture.project_root / ".agents")
        self.launch = self.fixture.prepare("codex")
        self.home = Path(self.launch.environment["CODEX_HOME"])
        self.record_path = self.home.parent / "assignment.json"
        self.record = json.loads(self.record_path.read_text())
        self.record["native_session"] = self.native
        self.save_record()
        self.transcript = self.home / "sessions/2026/09/14" / f"rollout-{self.native}.jsonl"
        self.transcript.parent.mkdir(parents=True)
        self.transcript.write_text(json.dumps({"type": "session_meta", "payload": {
            "id": self.native, "cwd": str(self.fixture.project_root)}}) + "\n")

    def save_record(self):
        self.record_path.write_text(json.dumps(self.record))

    def rows(self):
        return sessions.list_sessions(self.fixture.project, host="codex", state_root=self.fixture.state_root)

    def resume(self):
        return injection.resume_injection(self.fixture.project, "codex", "logic", self.record_path.parent.name,
                                          self.fixture.state_root, None, "owner")

    def test_missing_bundle_never_advertises_resume(self):
        self.launch.bundle_root.rename(self.launch.bundle_root.with_name("saved-bundle"))
        self.assertEqual(self.rows()[0]["resume_command"], "")
        with self.assertRaises(PolicyError):
            self.resume()

    def test_missing_transcript_is_rejected_before_host_launch(self):
        self.transcript.unlink()
        with self.assertRaises(PolicyError):
            self.resume()
        self.assertEqual(self.rows()[0]["resume_command"], "")

    def test_unbound_native_never_silently_starts_new_chat(self):
        self.record.pop("native_session")
        self.save_record()
        with self.assertRaises(PolicyError):
            self.resume()

    def test_unbound_native_still_lists_existing_transcript(self):
        self.record.pop("native_session")
        self.save_record()
        self.assertEqual(self.rows()[0]["transcripts"], [str(self.transcript)])

    def test_deleted_worktree_never_advertises_broken_command(self):
        self.record_path.with_name("session-binding.json").write_text(json.dumps({
            "worktree": str(self.fixture.root / "removed-worktree")}))
        self.assertEqual(self.rows()[0]["resume_command"], "")

    def test_modified_home_is_not_reported_as_resumable(self):
        target = self.home / "hooks.json"
        target.write_bytes(target.read_bytes() + b"\n ")
        self.assertEqual(self.rows()[0]["resume_command"], "")
        with self.assertRaises(PolicyError):
            self.resume()

    def test_healthy_resume_preserves_native_home_and_bundle(self):
        resumed = self.resume()
        self.assertEqual(resumed.command[1:3], ("resume", self.native))
        self.assertEqual(resumed.environment["CODEX_HOME"], str(self.home))
        self.assertEqual(resumed.bundle_root, self.launch.bundle_root)
        self.assertTrue(self.rows()[0]["resume_command"])

    def test_catalog_is_read_only_and_spans_homes(self):
        self.fixture.prepare("codex", role="ui")
        before = {str(p): p.read_bytes() for p in self.fixture.state_root.rglob("*") if p.is_file()}
        rows = self.rows()
        self.assertEqual(len(rows), 2)
        self.assertEqual({row["role"] for row in rows}, {"logic", "ui"})
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.fixture.state_root.rglob("*") if p.is_file()})

    def test_native_link_requires_metadata_and_preserves_record(self):
        self.record.pop("native_session")
        self.save_record()
        with self.assertRaises(PolicyError):
            sessions.link_native_session(self.fixture.project, self.record_path.parent.name,
                "00000000-0000-4000-8000-000000000099", self.fixture.state_root)
        sessions.link_native_session(self.fixture.project, self.record_path.parent.name, self.native, self.fixture.state_root)
        self.assertEqual(json.loads(self.record_path.with_name("native-link-backup.json").read_text()), self.record)
        self.assertEqual(self.resume().command[1:3], ("resume", self.native))

    def test_filename_without_matching_metadata_is_not_identity(self):
        self.transcript.write_text(json.dumps({"type": "session_meta", "payload": {
            "id": "00000000-0000-4000-8000-000000000099"}}) + "\n")
        with self.assertRaises(PolicyError):
            self.resume()

    def test_default_bundles_survive_build_cleanup(self):
        launch = injection.prepare_injection(self.fixture.project, "codex", "logic", state_root=self.fixture.state_root,
            source_codex_home=self.fixture.source_codex_home)
        self.assertTrue(launch.bundle_root.is_relative_to(self.fixture.state_root.resolve() / "bundles"))
        shutil.rmtree(self.fixture.build_root)
        self.assertTrue(injection.bundle_diagnostics(launch.bundle_root,
            json.loads((Path(launch.environment["CODEX_HOME"]).parent / "assignment.json").read_text())["bundle_digest"])["valid"])

    def test_original_bundle_backup_restores_exact_bytes_and_paths(self):
        from agent_policy.bundle_store import preserve_bundle
        original = {str(p.relative_to(self.launch.bundle_root)): p.read_bytes()
                    for p in self.launch.bundle_root.rglob("*") if p.is_file()}
        backup = preserve_bundle(self.record_path, self.record)
        self.assertEqual(preserve_bundle(self.record_path, self.record), backup)
        shutil.rmtree(self.launch.bundle_root)
        sessions.repair_bundle(self.fixture.project, self.record_path.parent.name, self.fixture.state_root)
        restored = {str(p.relative_to(self.launch.bundle_root)): p.read_bytes()
                    for p in self.launch.bundle_root.rglob("*") if p.is_file()}
        self.assertEqual(original, restored)
        self.assertEqual(self.resume().bundle_root, self.launch.bundle_root)

    def test_missing_bundle_without_backup_is_not_replaced_with_current_policy(self):
        shutil.rmtree(self.launch.bundle_root)
        with self.assertRaisesRegex(PolicyError, "백업"):
            sessions.repair_bundle(self.fixture.project, self.record_path.parent.name, self.fixture.state_root)
        self.assertFalse(self.launch.bundle_root.exists())

    def test_deleted_launch_worktree_does_not_delete_conversation_or_pin_guard(self):
        subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "--allow-empty", "-qm", "fixture"],
                       cwd=self.fixture.project_root, check=True)
        worktree = self.fixture.root / "child"
        subprocess.run(["git", "worktree", "add", "-qb", "child", str(worktree)], cwd=self.fixture.project_root, check=True)
        launched = injection.prepare_injection(replace(self.fixture.project, path=worktree), "codex", "logic",
            state_root=self.fixture.state_root, source_codex_home=self.fixture.source_codex_home)
        main = injection.prepare_injection(self.fixture.project, "codex", "logic", state_root=self.fixture.state_root,
            source_codex_home=self.fixture.source_codex_home)
        self.assertEqual(main.bundle_root, launched.bundle_root)
        home = Path(launched.environment["CODEX_HOME"])
        path = home.parent / "assignment.json"
        record = json.loads(path.read_text())
        record["native_session"] = self.native
        path.write_text(json.dumps(record))
        transcript = home / "sessions" / "conversation.jsonl"
        transcript.parent.mkdir()
        transcript.write_text(json.dumps({"type": "session_meta", "payload": {"id": self.native, "cwd": str(worktree)}}) + "\n")
        subprocess.run(["git", "worktree", "remove", str(worktree)], cwd=self.fixture.project_root, check=True)
        resumed = injection.resume_injection(self.fixture.project, "codex", "logic", path.parent.name,
            self.fixture.state_root, None, "owner")
        self.assertEqual(resumed.command[-2:], ("--cd", str(self.fixture.project_root.resolve())))
        hooks = json.loads((home / "hooks.json").read_text())["hooks"]
        command = shlex.split(hooks["PreToolUse"][0]["hooks"][0]["command"])
        event = {"session_id": self.native, "cwd": str(self.fixture.project_root), "tool_name": "exec_command",
                 "tool_input": {"cmd": "git status", "workdir": str(self.fixture.project_root)}}
        result = subprocess.run(command, input=json.dumps(event), cwd=self.fixture.project_root,
            env={**os.environ, **resumed.environment}, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn('"deny"', result.stdout)

    def test_cli_selection_uses_original_role_and_does_not_audit_current_source(self):
        from agent_policy.cli import run_resume
        with patch("agent_policy.cli.select_projects", return_value=[self.fixture.project]), \
             patch("agent_policy.injection.STATE_ROOT", self.fixture.state_root), \
             patch("agent_policy.recovery.CENTRAL_ROOT", self.fixture.root), \
             patch("agent_policy.cli.consumer_policy_sources", return_value=[]), \
             patch("agent_policy.cli.audit_source_contract", side_effect=AssertionError("current audit")), \
             redirect_stdout(StringIO()) as output:
            result = run_resume("user-ui", "codex", self.record_path.parent.name, None, True)
        self.assertEqual(result, 0)
        self.assertIn(self.native, output.getvalue())
        self.assertIn("role: logic", output.getvalue())

    def test_legacy_guard_anchor_is_checked_even_when_record_claims_valid_root(self):
        relative = "policy/.agent-policy/runtime/runtime_config.py"
        runtime = self.launch.bundle_root / relative
        runtime.write_text(runtime.read_text().replace(str(self.fixture.project_root.resolve()), str(self.fixture.root / "deleted")))
        manifest_path = self.launch.bundle_root / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["files"][relative] = sha256_bytes(runtime.read_bytes())
        manifest_path.write_text(json.dumps(manifest))
        self.assertIn("policy_anchor_missing", {reason["code"] for reason in self.rows()[0]["reasons"]})
        with self.assertRaisesRegex(PolicyError, "guard"):
            self.resume()

    def test_backup_tampering_and_duplicate_native_do_not_resume(self):
        from agent_policy.bundle_store import preserve_bundle
        backup = preserve_bundle(self.record_path, self.record)
        (backup / "system-prompt.md").write_text("changed")
        shutil.rmtree(self.launch.bundle_root)
        with self.assertRaises(PolicyError):
            sessions.repair_bundle(self.fixture.project, self.record_path.parent.name, self.fixture.state_root)
        self.assertFalse(self.launch.bundle_root.exists())
        duplicate = self.home / "archived_sessions/duplicate.jsonl"
        duplicate.parent.mkdir()
        duplicate.write_bytes(self.transcript.read_bytes())
        self.assertIn("transcript_ambiguous", {reason["code"] for reason in self.rows()[0]["reasons"]})

    def test_consumer_conflict_and_incomplete_record_are_not_advertised(self):
        (self.fixture.project_root / "AGENTS.md").write_text("conflicting policy")
        self.assertIn("consumer_policy_conflict", {reason["code"] for reason in self.rows()[0]["reasons"]})
        self.record.pop("command")
        self.save_record()
        self.assertEqual(self.rows()[0]["reasons"][0]["code"], "record_invalid")
        with self.assertRaises(PolicyError):
            self.resume()

    def test_interactive_picker_executes_selected_original_assignment(self):
        from agent_policy.cli import run_resume
        self.fixture.prepare("codex", role="ui")
        number = next(index for index, row in enumerate(self.rows(), 1) if row["assignment"] == self.record_path.parent.name)
        with patch("agent_policy.cli.select_projects", return_value=[self.fixture.project]), \
             patch("agent_policy.injection.STATE_ROOT", self.fixture.state_root), \
             patch("agent_policy.recovery.CENTRAL_ROOT", self.fixture.root), \
             patch("sys.stdin.isatty", return_value=True), patch("builtins.input", return_value=str(number)), \
             patch("agent_policy.cli.os.chdir") as chdir, patch("agent_policy.cli.os.execvpe") as execute, \
             redirect_stdout(StringIO()):
            self.assertEqual(run_resume("user-ui", "codex", None, None), 0)
        command, args, environment = execute.call_args.args
        self.assertEqual(command, "codex")
        self.assertEqual(args[1:3], ["resume", self.native])
        self.assertEqual(environment["CODEX_HOME"], str(self.home))
        self.assertEqual(environment["ASAN_AGENT_POLICY_ASSIGNMENT"], self.record_path.parent.name)
        self.assertEqual(environment["ASAN_AGENT_POLICY_ROLE"], "logic")
        chdir.assert_called_once_with(self.fixture.project_root.resolve())

    def test_cancelled_picker_creates_no_assignment(self):
        from agent_policy.cli import run_resume
        before = list(self.fixture.state_root.glob("repositories/*/assignments/*"))
        with patch("agent_policy.cli.select_projects", return_value=[self.fixture.project]), \
             patch("agent_policy.recovery.CENTRAL_ROOT", self.fixture.root), \
             patch("sys.stdin.isatty", return_value=True), patch("builtins.input", return_value=""), \
             patch("agent_policy.cli.os.execvpe") as execute, redirect_stdout(StringIO()):
            self.assertEqual(run_resume("user-ui", "codex", None, None), 0)
        execute.assert_not_called()
        self.assertEqual(before, list(self.fixture.state_root.glob("repositories/*/assignments/*")))
