"""Native /resume must see project history without sharing policy or approvals."""
from __future__ import annotations

import json
import os
import subprocess
import unittest
from io import StringIO
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import test_injection
from agent_policy.runtime import load_runtime
from agent_policy.session_diagnostics import transcript_catalog
from agent_policy.core import PolicyError


class CodexHistoryTests(unittest.TestCase):
    first_id = "11111111-1111-4111-8111-111111111111"
    second_id = "22222222-2222-4222-8222-222222222222"

    def setUp(self):
        self.fixture = test_injection.InjectionTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.tearDown)
        self.addCleanup(self.fixture.doCleanups)

    def transcript(self, home, native, cwd=None):
        path = home / "sessions/2026/09/07" / f"rollout-2026-09-07T06-25-42-{native}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"timestamp": "2026-09-07T06:25:42.235Z", "type": "session_meta", "payload": {
            "id": native, "cwd": str(cwd or self.fixture.project_root),
            "timestamp": "2026-09-07T06:25:42.235Z", "source": "cli",
            "originator": "codex_cli_rs", "model_provider": "openai", "cli_version": "0.160.0"}}) + "\n")
        return path

    def test_new_launch_sees_previous_conversation_but_has_its_own_hooks(self):
        first = self.fixture.prepare("codex")
        first_home = Path(first.environment["CODEX_HOME"])
        original_hooks = (first_home / "hooks.json").read_bytes()
        self.transcript(first_home, self.first_id)
        second = self.fixture.prepare("codex", role="review")
        second_home = Path(second.environment["CODEX_HOME"])
        self.assertNotEqual(first_home, second_home)
        self.assertEqual((first_home / "hooks.json").read_bytes(), original_hooks)
        entries, errors = transcript_catalog(second_home)
        self.assertEqual(errors, [])
        self.assertEqual([row["id"] for row in entries], [self.first_id])
        self.assertEqual((first_home / "sessions").resolve(), (second_home / "sessions").resolve())

    def test_legacy_history_import_preserves_original_and_filters_project(self):
        legacy = self.fixture.state_root / "user-ui/codex-home"
        source = self.transcript(legacy, self.first_id)
        os.utime(source, (1788762342, 1788762342))
        self.transcript(legacy, self.second_id, self.fixture.root / "other-project")
        original = source.read_bytes()
        launch = self.fixture.prepare("codex")
        entries, errors = transcript_catalog(Path(launch.environment["CODEX_HOME"]))
        self.assertEqual(errors, [])
        self.assertEqual([row["id"] for row in entries], [self.first_id])
        self.assertEqual(source.read_bytes(), original)
        self.assertEqual(Path(entries[0]["path"]).stat().st_mtime_ns, source.stat().st_mtime_ns)

    def test_resume_switch_isolates_state_and_can_switch_back(self):
        launch = self.fixture.prepare("codex")
        home = Path(launch.environment["CODEX_HOME"])
        self.transcript(home, self.first_id)
        self.transcript(home, self.second_id)
        common = self.fixture.project_root / ".git"
        state = load_runtime("runtime_state")
        with patch.dict(os.environ, launch.environment):
            state.bind_native_session(common, "codex", self.first_id)
            first = state.session_path(common, "codex", self.first_id, "harness-state-v3")
            state.write(first, {"implementation_approved": True})
            state.bind_native_session(common, "codex", self.second_id)
            second = state.session_path(common, "codex", self.second_id, "harness-state-v3")
            self.assertNotEqual(first, second)
            self.assertEqual(state.read(second), {})
            state.bind_native_session(common, "codex", self.first_id)
            self.assertEqual(state.read(first), {"implementation_approved": True})

    def test_projects_do_not_share_history_even_with_same_project_id(self):
        first = self.fixture.prepare("codex")
        self.transcript(Path(first.environment["CODEX_HOME"]), self.first_id)
        other = self.fixture.root / "other-project"
        other.mkdir()
        subprocess.run(["git", "init", "-q", str(other)], check=True)
        self.fixture.project = replace(self.fixture.project, path=other)
        second = self.fixture.prepare("codex")
        entries, errors = transcript_catalog(Path(second.environment["CODEX_HOME"]))
        self.assertEqual((entries, errors), ([], []))

    def test_arbitrary_transcript_symlink_is_not_trusted(self):
        launch = self.fixture.prepare("codex")
        home = Path(launch.environment["CODEX_HOME"])
        (home / "sessions").unlink()
        (home / "sessions").symlink_to(self.fixture.source_codex_home)
        entries, errors = transcript_catalog(home)
        self.assertEqual(entries, [])
        self.assertTrue(errors)

    def test_repeated_import_keeps_new_canonical_turns_and_original_bytes(self):
        source = self.transcript(self.fixture.state_root / "user-ui/codex-home", self.first_id)
        original = source.read_bytes()
        first = self.fixture.prepare("codex")
        entries, _ = transcript_catalog(Path(first.environment["CODEX_HOME"]))
        canonical = Path(entries[0]["path"])
        with canonical.open("a") as stream:
            stream.write('{"type":"event_msg","payload":{}}\n')
        updated = canonical.read_bytes()
        second = self.fixture.prepare("codex")
        entries, _ = transcript_catalog(Path(second.environment["CODEX_HOME"]))
        self.assertEqual(Path(entries[0]["path"]).read_bytes(), updated)
        self.assertEqual(source.read_bytes(), original)

    def test_legacy_names_are_project_filtered_and_shared(self):
        legacy = self.fixture.state_root / "user-ui/codex-home"
        self.transcript(legacy, self.first_id)
        self.transcript(legacy, self.second_id, self.fixture.root / "other-project")
        (legacy / "session_index.jsonl").write_text("\n".join(json.dumps({
            "id": native, "thread_name": native, "updated_at": "2026-09-07T06:25:42Z"})
            for native in (self.first_id, self.second_id)) + "\n")
        first = self.fixture.prepare("codex")
        second = self.fixture.prepare("codex")
        first_home = Path(first.environment["CODEX_HOME"])
        second_home = Path(second.environment["CODEX_HOME"])
        rows = [json.loads(line) for line in (second_home / "session_index.jsonl").read_text().splitlines()]
        self.assertEqual([row["id"] for row in rows], [self.first_id])
        self.assertEqual((first_home / "thread-writer-locks").resolve(), (second_home / "thread-writer-locks").resolve())

    def test_conflicting_legacy_transcripts_are_not_overwritten(self):
        self.transcript(self.fixture.state_root / "user-ui/codex-home", self.first_id)
        conflicting = self.transcript(self.fixture.source_codex_home, self.first_id)
        with conflicting.open("a") as stream:
            stream.write('{"type":"event_msg","payload":{"type":"different"}}\n')
        with self.assertRaises(PolicyError):
            self.fixture.prepare("codex")

    def test_resume_hooks_accept_switch_and_preserve_current_role(self):
        launch = self.fixture.prepare("codex", role="review")
        guard = launch.bundle_root / "policy/.agent-policy/runtime/managed_policy_guard.py"
        for native in (self.first_id, self.second_id, self.first_id):
            result = subprocess.run(["python3", "-I", str(guard), "session-start", "codex"],
                input=json.dumps({"session_id": native, "cwd": str(self.fixture.project_root),
                                  "hook_event_name": "SessionStart", "source": "resume"}),
                capture_output=True, text=True, env={**os.environ, **launch.environment})
            self.assertEqual(result.returncode, 0, result.stderr)
        state = load_runtime("runtime_state")
        with patch.dict(os.environ, launch.environment):
            record = state.read(state.session_path(self.fixture.project_root / ".git", "codex", self.second_id, "assignment"))
        self.assertEqual(record["role"], "review")
        self.assertEqual(record["bundle_root"], str(launch.bundle_root))

    def test_stop_collection_uses_selected_conversation(self):
        from agent_policy.cli import run_collect_logs
        launch = self.fixture.prepare("codex")
        state = load_runtime("runtime_state")
        common = self.fixture.project_root / ".git"
        with patch.dict(os.environ, launch.environment):
            state.bind_native_session(common, "codex", self.first_id)
            state.bind_native_session(common, "codex", self.second_id)
            expected = state.effective_assignment("codex", self.second_id)
            with patch("agent_policy.cli.select_projects", return_value=[self.fixture.project]), \
                 patch("agent_policy.cli.active_project", return_value=self.fixture.project), \
                 patch("agent_policy.cli.assignment_log_sources", return_value=()) as sources, \
                 patch("agent_policy.cli.collect_project_logs"), \
                 patch("sys.stdin", StringIO(json.dumps({"session_id": self.second_id}))):
                run_collect_logs("user-ui", "codex", True, hook_event=True)
            self.assertEqual(sources.call_args.args[2], expected)
            self.assertNotEqual(expected, launch.environment["ASAN_AGENT_POLICY_ASSIGNMENT"])

    def test_formatter_uses_native_thread_after_resume(self):
        launch = self.fixture.prepare("codex")
        state = load_runtime("runtime_state")
        with patch.dict(os.environ, launch.environment):
            for native in (self.first_id, self.second_id):
                state.bind_native_session(self.fixture.project_root / ".git", "codex", native)
        formatter = launch.bundle_root / "policy/.agent-policy/runtime/formatting.py"
        result = subprocess.run(["python3", "-I", str(formatter), "check"], cwd=self.fixture.project_root,
            env={**os.environ, **launch.environment, "CODEX_THREAD_ID": self.second_id},
            text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
