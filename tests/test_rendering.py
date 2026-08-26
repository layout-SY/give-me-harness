from __future__ import annotations

import json
import hashlib
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from agent_policy.core import load_project, render_project, source_digest


class RenderingTests(unittest.TestCase):
    def test_project_metadata_is_rendered_without_cross_project_name(self) -> None:
        user = render_project(load_project("user-ui"))
        admin = render_project(load_project("admin-ui"))
        self.assertIn(b"asan-metaverse-user-ui", user["AGENTS.md"])
        self.assertNotIn(b"asan-metaverse-admin-ui", user["AGENTS.md"])
        self.assertIn(b"asan-metaverse-admin-ui", admin["AGENTS.md"])
        self.assertNotIn(b"asan-metaverse-user-ui", admin["AGENTS.md"])

    def test_managed_outputs_have_no_legacy_central_reference_or_placeholder(self) -> None:
        for project_id in ("user-ui", "admin-ui"):
            with self.subTest(project=project_id):
                for path, content in render_project(load_project(project_id)).items():
                    self.assertNotIn(b"asan-prompt-core", content, path)
                    self.assertNotIn(b"{{PROJECT_NAME}}", content, path)
                    self.assertNotIn(b"{{CENTRAL_ROOT}}", content, path)

    def test_project_specific_reference_catalogs_are_not_centralized(self) -> None:
        rendered = render_project(load_project("user-ui"))
        self.assertNotIn(
            ".agents/skills/reference/components/COMMON_COMPONENTS.md",
            rendered,
        )
        hooks = rendered[".agents/skills/reference/custom-hooks/SKILL.md"]
        self.assertNotIn(b"useApi", hooks)
        self.assertNotIn(b"meeting", hooks)

    def test_codex_and_claude_hook_schemas_are_json_and_include_guard(self) -> None:
        rendered = render_project(load_project("user-ui"))
        codex = json.loads(rendered[".codex/hooks.json"])["hooks"]
        claude = json.loads(rendered[".claude/settings.json"])["hooks"]
        self.assertIn("SessionStart", codex)
        self.assertIn("PreToolUse", codex)
        self.assertIn("SessionStart", claude)
        self.assertIn("PreToolUse", claude)
        self.assertIn("managed_policy_guard.py", json.dumps(codex))
        self.assertIn("managed_policy_guard.py", json.dumps(claude))

    def test_codex_baseline_hook_integrity_hashes_match_sources(self) -> None:
        rendered = render_project(load_project("user-ui"))
        hooks = json.loads(rendered[".codex/hooks.json"])["hooks"]
        for event_name in ("UserPromptSubmit", "PreToolUse", "PostToolUse", "Stop"):
            registration = next(
                item
                for item in hooks[event_name]
                if "HOOK_SHA256" in item["hooks"][0]["command"]
            )
            command = registration["hooks"][0]["command"]
            expected = re.search(r"HOOK_SHA256='([0-9a-f]{64})'", command)
            entry = re.search(r'"([a-z-]+\.py)" "\$HOOK_SHA256"', command)
            self.assertIsNotNone(expected)
            self.assertIsNotNone(entry)
            digest = hashlib.sha256(
                rendered[f".codex/hooks/{entry.group(1)}"]
                + b"\0"
                + rendered[".codex/hooks/hook_common.py"]
            ).hexdigest()
            self.assertEqual(expected.group(1), digest)

    def test_opencode_plugin_contract_is_rendered(self) -> None:
        plugin = render_project(load_project("user-ui"))[
            ".opencode/plugins/agent-policy.js"
        ].decode()
        self.assertIn('"tool.execute.before"', plugin)
        self.assertIn("output.args", plugin)
        self.assertIn("session-start", plugin)

    def test_source_digest_includes_project_metadata(self) -> None:
        self.assertNotEqual(
            source_digest(load_project("user-ui")),
            source_digest(load_project("admin-ui")),
        )
