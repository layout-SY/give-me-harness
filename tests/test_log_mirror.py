from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from agent_policy.core import ProjectConfig
from agent_policy.log_mirror import REQUIRED_ARTIFACTS, collect_project_logs, selected_channels


class LogMirrorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.project_root = self.root / "project"
        self.logs_root = self.root / "central"
        self.project = ProjectConfig(
            id="user-ui",
            name="temporary-user-ui",
            path=self.project_root,
            commands={},
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_artifact(self, channel_root: str, session: str, name: str, content: bytes) -> Path:
        target = self.project_root / channel_root / session / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return target

    def test_only_required_regular_files_are_copied_byte_for_byte(self) -> None:
        source = self.write_artifact(
            ".codex/logs/sessions",
            "2026-08-27-task",
            REQUIRED_ARTIFACTS[0],
            b"required\x00content",
        )
        self.write_artifact(
            ".codex/logs/sessions",
            "2026-08-27-task",
            "transcript.md",
            b"excluded",
        )
        symlink = source.parent / REQUIRED_ARTIFACTS[1]
        symlink.symlink_to(source)

        result = collect_project_logs(self.project, "codex", self.logs_root)

        target_session = self.logs_root / "user-ui/codex/sessions/2026-08-27-task"
        self.assertEqual(result.copied, ("2026-08-27-task/plan.md",))
        self.assertEqual((target_session / "plan.md").read_bytes(), b"required\x00content")
        self.assertFalse((target_session / "transcript.md").exists())
        self.assertFalse((target_session / "exploration.md").exists())

    def test_collection_is_incremental_and_never_deletes_central_copy(self) -> None:
        source = self.write_artifact(
            ".codex/logs/sessions",
            "task",
            "plan.md",
            b"first",
        )
        first = collect_project_logs(self.project, "codex", self.logs_root)
        second = collect_project_logs(self.project, "codex", self.logs_root)
        self.assertEqual(len(first.copied), 1)
        self.assertEqual(second.copied, ())
        self.assertEqual(second.unchanged, 1)

        source.write_bytes(b"updated")
        updated = collect_project_logs(self.project, "codex", self.logs_root)
        target = self.logs_root / "user-ui/codex/sessions/task/plan.md"
        self.assertEqual(updated.copied, ("task/plan.md",))
        self.assertEqual(target.read_bytes(), b"updated")

        source.unlink()
        collect_project_logs(self.project, "codex", self.logs_root)
        self.assertEqual(target.read_bytes(), b"updated")

    def test_missing_source_is_nonfatal_and_channels_are_separated(self) -> None:
        missing = collect_project_logs(self.project, "codex", self.logs_root)
        self.assertTrue(missing.source_missing)

        self.write_artifact(
            ".claude/logs/sessions",
            "ui-task",
            "handoff.md",
            b"claude",
        )
        result = collect_project_logs(self.project, "claude", self.logs_root)
        self.assertFalse(result.source_missing)
        self.assertTrue(
            (self.logs_root / "user-ui/claude/sessions/ui-task/handoff.md").is_file()
        )
        self.assertFalse((self.logs_root / "user-ui/codex/sessions/ui-task").exists())

        self.write_artifact(
            ".opencode/logs/sessions",
            "review-task",
            "review-log.md",
            b"opencode",
        )
        opencode = collect_project_logs(self.project, "opencode", self.logs_root)
        self.assertEqual(opencode.copied, ("review-task/review-log.md",))

    def test_legacy_logic_channel_remains_explicitly_readable(self) -> None:
        self.write_artifact(".codex/logs/sessions", "legacy", "plan.md", b"legacy")

        result = collect_project_logs(self.project, "logic", self.logs_root)

        self.assertEqual(result.copied, ("legacy/plan.md",))
        self.assertTrue((self.logs_root / "user-ui/logic/sessions/legacy/plan.md").is_file())

    def test_all_selects_only_current_host_channels(self) -> None:
        self.assertEqual(
            selected_channels("all"),
            ("codex", "claude", "opencode", "unknown"),
        )

    def test_unknown_documents_are_collected_only_from_unknown_directories(self) -> None:
        self.write_artifact(
            ".claude/logs/sessions",
            "task/unknown",
            "decision-note.md",
            b"auxiliary",
        )
        self.write_artifact(
            ".agent-policy/logs/unknown/sessions",
            "runtime-task/unknown",
            "runtime-note.md",
            b"unknown-host",
        )

        claude = collect_project_logs(self.project, "claude", self.logs_root)
        unknown = collect_project_logs(self.project, "unknown", self.logs_root)

        self.assertEqual(claude.copied, ("task/unknown/decision-note.md",))
        self.assertEqual(unknown.copied, ("runtime-task/unknown/runtime-note.md",))
