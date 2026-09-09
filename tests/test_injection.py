from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import replace
from io import StringIO
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from agent_policy.cli import active_project, build_parser, normalized_session_dir, run_start
from agent_policy.core import CENTRAL_ROOT, PolicyError, ProjectConfig, render_project
from agent_policy.injection import (
    InjectionLaunch,
    consumer_policy_sources,
    prepare_injection,
)


class InjectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.project_root = self.root / "consumer"
        self.project_root.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.project_root, check=True)
        (self.project_root / "AGENTS.md").write_text("consumer drift\n", encoding="utf-8")
        local_skill = self.project_root / ".agents/skills/local/SKILL.md"
        local_skill.parent.mkdir(parents=True)
        local_skill.write_text("---\nname: local\ndescription: local\n---\n", encoding="utf-8")
        self.build_root = self.root / "build"
        self.state_root = self.root / "state"
        self.source_codex_home = self.root / "user-codex"
        self.source_codex_home.mkdir()
        (self.source_codex_home / "config.toml").write_text(
            'model_reasoning_effort = "high"\n',
            encoding="utf-8",
        )
        (self.source_codex_home / "auth.json").write_text(
            '{"token":"test-only"}\n',
            encoding="utf-8",
        )
        self.project = ProjectConfig(
            id="user-ui",
            name="temporary-user-ui",
            path=self.project_root,
            commands={
                "dev": "npm run dev",
                "build": "npm run build",
                "lint": "npm run lint",
                "test": "npm run test",
                "preview": "npm run preview",
            },
        )
        # Unit tests never require Bun or launch a real MCP process.
        executable_lookup = shutil.which
        lookup = patch("shutil.which", side_effect=lambda command, *args, **kwargs:
                       sys.executable if command == "bunx" else executable_lookup(command, *args, **kwargs))
        lookup.start()
        self.addCleanup(lookup.stop)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def consumer_snapshot(self) -> dict[str, bytes]:
        return {
            path.relative_to(self.project_root).as_posix(): path.read_bytes()
            for path in self.project_root.rglob("*")
            if path.is_file()
        }

    def prepare(
        self,
        host: str,
        model: str | None = None,
        role: str = "logic",
        task: str | None = None,
        responsibility: str = "owner",
    ) -> InjectionLaunch:
        return prepare_injection(
            self.project,
            host,
            role,
            model,
            build_root=self.build_root,
            state_root=self.state_root,
            source_codex_home=self.source_codex_home,
            task=task,
            responsibility=responsibility,
        )

    @staticmethod
    def command_strings(value: object) -> list[str]:
        if isinstance(value, dict):
            return [
                command
                for item in value.values()
                for command in InjectionTests.command_strings(item)
            ]
        if isinstance(value, list):
            return [
                command
                for item in value
                for command in InjectionTests.command_strings(item)
            ]
        return [value] if isinstance(value, str) else []

    def assert_policy_snapshot_is_renderer_subset(self, launch: InjectionLaunch) -> None:
        rendered = render_project(self.project)
        policy_root = launch.bundle_root / "policy"
        for path in policy_root.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(policy_root).as_posix()
            self.assertIn(relative, rendered)
            self.assertEqual(path.read_bytes(), rendered[relative])

    def test_all_hosts_build_from_renderer_without_mutating_consumer(self) -> None:
        before = self.consumer_snapshot()
        for host in ("codex", "claude", "opencode"):
            with self.subTest(host=host):
                launch = self.prepare(host)
                self.assert_policy_snapshot_is_renderer_subset(launch)
                self.assertTrue(
                    (
                        launch.bundle_root
                        / "policy/.agent-policy/common/AGENT_POLICY.md"
                    ).is_file()
                )
                self.assertEqual(launch.environment["ASAN_AGENT_POLICY_MODE"], "inject")
                self.assertEqual(launch.environment["ASAN_AGENT_POLICY_ROLE"], "logic")
                self.assertEqual(
                    launch.environment["ASAN_AGENT_POLICY_PROJECT_PATH"],
                    str(self.project_root),
                )
                manifest = json.loads(
                    (launch.bundle_root / "manifest.json").read_text(encoding="utf-8")
                )
                self.assertEqual(manifest["mode"], "inject")
                self.assertEqual(manifest["project_id"], "user-ui")
                self.assertEqual(manifest["host"], host)
                self.assertEqual(manifest["role"], "logic")
                self.assertEqual(launch.role, "logic")
                self.assertRegex(manifest["source_digest"], r"^[0-9a-f]{64}$")
                self.assertRegex(manifest["bundle_digest"], r"^[0-9a-f]{64}$")
                policy = launch.bundle_root / "policy"
                foreign_roots = {
                    "codex": (".claude", ".opencode"),
                    "claude": (".codex", ".opencode"),
                    "opencode": (".codex", ".claude"),
                }
                for foreign in foreign_roots[host]:
                    self.assertFalse((policy / foreign).exists())
        self.assertEqual(self.consumer_snapshot(), before)

    def test_all_host_system_prompts_require_incident_regression_tests(self) -> None:
        required_contract = (
            "사용자 보고 또는 실행 로그로 확인된 정책·훅·세션 실행 결함을 수정할 때는 "
            "그 실패 상황을 재현하는 자동 회귀 테스트를 함께 작성한다."
        )
        runtime_contract = (
            "명령 문자열이나 생성 파일의 존재만 확인하지 않고 실제로 적용되는 "
            "프롬프트·설정·훅 출처를 검증한다."
        )
        no_weakening_contract = (
            "기존 회귀 테스트를 삭제하거나 검증을 약화해 통과시켜서는 안 된다."
        )
        loop_contract = "동일 원인의 훅 차단을 무한히 재시도하지 않는다."
        v3_contract = (
            "V1·V2·무버전 branch metadata는 읽기 전용 history로만 취급하며 "
            "source·Git 변경 권한을 부여하지 않는다."
        )

        for host in ("codex", "claude", "opencode"):
            with self.subTest(host=host):
                prompt = self.prepare(host).system_prompt.read_text(encoding="utf-8")
                self.assertIn(required_contract, prompt)
                self.assertIn(runtime_contract, prompt)
                self.assertIn(no_weakening_contract, prompt)
                self.assertIn(loop_contract, prompt)
                self.assertIn(v3_contract, prompt)

    def test_opencode_uses_isolated_config_prompt_skills_and_absolute_guard(self) -> None:
        launch = self.prepare("opencode", "provider/model")
        home = launch.bundle_root / "opencode-home"
        config = json.loads((home / "opencode.json").read_text(encoding="utf-8"))
        self.assertEqual(config["instructions"], [str(launch.system_prompt)])
        self.assertEqual(config["skills"], [str(home / "skills")])
        self.assertTrue((home / "skills/policy/SKILL.md").is_file())
        self.assertTrue((home / "agents/generator.md").is_file())
        self.assertFalse((home / "agents/planner.md").exists())
        self.assertTrue((home / "runtime/branch_guard.py").is_file())
        plugin = (home / "plugins/agent-policy.js").read_text(encoding="utf-8")
        self.assertIn(str(home / "runtime/managed_policy_guard.py"), plugin)
        self.assertNotIn('join(directory, ".agent-policy/runtime', plugin)
        self.assertEqual(launch.environment["OPENCODE_CONFIG_DIR"], str(home))
        self.assertEqual(launch.environment["OPENCODE_DISABLE_PROJECT_CONFIG"], "1")
        self.assertEqual(launch.environment["OPENCODE_DISABLE_EXTERNAL_SKILLS"], "1")
        self.assertEqual(launch.command[-2:], ("--model", "provider/model"))

    def test_claude_uses_plugin_settings_and_injected_prompt(self) -> None:
        launch = self.prepare("claude", role="ui")
        plugin = launch.bundle_root / "plugin"
        settings = json.loads(
            (launch.bundle_root / "claude-settings.json").read_text(encoding="utf-8")
        )
        hooks = json.loads((plugin / "hooks/hooks.json").read_text(encoding="utf-8"))
        self.assertNotIn("hooks", settings)
        self.assertIn("enabledPlugins", settings)
        self.assertTrue((plugin / "skills/project-ui/SKILL.md").is_file())
        self.assertTrue((plugin / "agents/publisher.md").is_file())
        self.assertFalse((plugin / "agents/planner.md").exists())
        self.assertFalse((launch.bundle_root / "policy/AGENTS.md").exists())
        self.assertFalse((launch.bundle_root / "policy/.codex").exists())
        prompt = launch.system_prompt.read_text(encoding="utf-8")
        self.assertIn("선택된 role: `ui`", prompt)
        self.assertIn(".agent-policy/common/AGENT_POLICY.md", prompt)
        self.assertTrue((plugin / "runtime/branch_guard.py").is_file())
        commands = [
            value
            for value in self.command_strings(hooks)
            if "managed_policy_guard.py" in value
        ]
        self.assertTrue(commands)
        self.assertTrue(all("${CLAUDE_PLUGIN_ROOT}" not in value for value in commands))
        self.assertTrue(all(str(plugin / "runtime") in value for value in commands))
        self.assertIn("--setting-sources", launch.command)
        self.assertIn("--plugin-dir", launch.command)
        self.assertIn("--append-system-prompt-file", launch.command)
        prompt_index = launch.command.index("--append-system-prompt-file")
        self.assertEqual(launch.command[prompt_index + 1], str(launch.system_prompt))

    def test_claude_ui_mcp_defaults_work_without_personal_registration(self) -> None:
        home = self.root / "empty-claude-home"
        home.mkdir()
        config = home / ".claude.json"
        config.write_text('{"mcpServers": {}, "projects": {}}\n')
        before = self.consumer_snapshot()
        with patch("pathlib.Path.home", return_value=home):
            for project_id in ("user-ui", "admin-ui"):
                with self.subTest(project=project_id):
                    self.project = replace(self.project, id=project_id)
                    launch = self.prepare("claude", role="ui")
                    self.assertIn("--mcp-config", launch.command)
                    index = launch.command.index("--mcp-config")
                    mcp_path = Path(launch.command[index + 1])
                    self.assertEqual(mcp_path, launch.bundle_root / "claude-mcp.json")
                    servers = json.loads(mcp_path.read_bytes())["mcpServers"]
                    self.assertEqual(set(servers), {"TalkToFigma"})
                    server = servers["TalkToFigma"]
                    self.assertEqual(server["type"], "stdio")
                    self.assertTrue(Path(server["command"]).is_absolute())
                    self.assertEqual(server["args"], ["cursor-talk-to-figma-mcp@latest"])
                    self.assertEqual(launch.command[launch.command.index("--setting-sources") + 1], "user")
                    self.assertNotIn("--strict-mcp-config", launch.command)
                    manifest = json.loads((launch.bundle_root / "manifest.json").read_bytes())
                    self.assertIn("claude-mcp.json", manifest["files"])
        self.assertEqual(config.read_text(), '{"mcpServers": {}, "projects": {}}\n')
        self.assertEqual(self.consumer_snapshot(), before)

    def test_claude_mcp_defaults_are_scoped_to_projects_host_and_ui_role(self) -> None:
        for project_id in ("user-ui", "admin-ui"):
            self.project = replace(self.project, id=project_id)
            for host in ("codex", "claude", "opencode"):
                for role in ("logic", "ui", "orchest", "review", "generate"):
                    if (host, role) == ("claude", "ui"):
                        continue
                    with self.subTest(project=project_id, host=host, role=role):
                        launch = self.prepare(host, role=role)
                        self.assertNotIn("--mcp-config", launch.command)
                        self.assertFalse((launch.bundle_root / "claude-mcp.json").exists())
        self.project = replace(self.project, id="unrelated")
        # Unknown projects are not launchable through the public CLI; isolate the
        # selection boundary without needing a projects/unrelated.json fixture.
        with patch("agent_policy.injection.source_digest", return_value="0" * 64):
            launch = self.prepare("claude", role="ui")
        self.assertNotIn("--mcp-config", launch.command)
        self.assertFalse((launch.bundle_root / "claude-mcp.json").exists())

    def test_claude_mcp_definition_change_creates_new_bundle_and_resume_preserves_old(self) -> None:
        defaults = self.root / "mcp.defaults.json"
        definition = {
            "projects": ["user-ui", "admin-ui"], "roles": ["ui"],
            "mcpServers": {"TalkToFigma": {
                "type": "stdio", "command": sys.executable, "args": ["fixture-v1"],
            }},
        }
        defaults.write_text(json.dumps(definition))
        with patch("agent_policy.injection.CLAUDE_MCP_DEFAULTS", defaults, create=True):
            first = self.prepare("claude", role="ui")
            self.assertIn("--mcp-config", first.command)
            original = (first.bundle_root / "claude-mcp.json").read_bytes()
            definition["mcpServers"]["TalkToFigma"]["args"] = ["fixture-v2"]
            defaults.write_text(json.dumps(definition))
            second = self.prepare("claude", role="ui")
            self.assertNotEqual(first.bundle_root, second.bundle_root)
            self.assertIn("fixture-v2", (second.bundle_root / "claude-mcp.json").read_text())
            resumed = prepare_injection(
                self.project, "claude", "ui", state_root=self.state_root,
                resume_assignment=first.environment["ASAN_AGENT_POLICY_ASSIGNMENT"],
            )
        self.assertEqual(resumed.bundle_root, first.bundle_root)
        self.assertEqual(resumed.command, first.command)
        self.assertEqual((first.bundle_root / "claude-mcp.json").read_bytes(), original)

    def test_claude_ui_mcp_resolves_bunx_fallback_and_rejects_missing_executable(self) -> None:
        home = self.root / "home with spaces"
        bunx = home / ".bun/bin/bunx"
        bunx.parent.mkdir(parents=True)
        bun = bunx.with_name("bun")
        bun.write_text("#!/bin/sh\nexit 0\n")
        bun.chmod(0o700)
        bunx.symlink_to(bun)
        with patch("pathlib.Path.home", return_value=home), patch("shutil.which", return_value=None):
            launch = self.prepare("claude", role="ui")
            self.assertIn("--mcp-config", launch.command)
            config = json.loads((launch.bundle_root / "claude-mcp.json").read_bytes())
            self.assertEqual(config["mcpServers"]["TalkToFigma"]["command"], str(bunx))
            bunx.unlink()
            with self.assertRaisesRegex(PolicyError, "TalkToFigma.*bunx"):
                self.prepare("claude", role="ui")
            # Other roles must not depend on the UI integration's executable.
            self.prepare("claude", role="logic")

    def test_claude_mcp_upgrade_preserves_legacy_resume(self) -> None:
        with patch("agent_policy.injection._claude_mcp_config", return_value=None):
            legacy = self.prepare("claude", role="ui")
        current = self.prepare("claude", role="ui")
        self.assertNotEqual(legacy.bundle_root, current.bundle_root)
        self.assertIn("--mcp-config", current.command)
        resumed = prepare_injection(
            self.project, "claude", "ui", state_root=self.state_root,
            resume_assignment=legacy.environment["ASAN_AGENT_POLICY_ASSIGNMENT"],
        )
        self.assertEqual(resumed.bundle_root, legacy.bundle_root)
        self.assertEqual(resumed.command, legacy.command)
        self.assertNotIn("--mcp-config", resumed.command)

    def test_claude_mcp_executable_change_creates_new_bundle(self) -> None:
        with patch("shutil.which", return_value="/fixture/first/bunx"):
            first = self.prepare("claude", role="ui")
        with patch("shutil.which", return_value="/fixture/second/bunx"):
            second = self.prepare("claude", role="ui")
        self.assertNotEqual(first.bundle_root, second.bundle_root)
        for launch, expected in ((first, "/fixture/first/bunx"), (second, "/fixture/second/bunx")):
            servers = json.loads((launch.bundle_root / "claude-mcp.json").read_bytes())["mcpServers"]
            self.assertEqual(servers["TalkToFigma"]["command"], expected)

    def test_codex_preserves_user_config_and_auth_while_overriding_policy(self) -> None:
        launch = self.prepare("codex", "gpt-test")
        codex_home = Path(launch.environment["CODEX_HOME"])
        self.assertEqual(
            (codex_home / "config.toml").read_bytes(),
            (self.source_codex_home / "config.toml").read_bytes(),
        )
        self.assertTrue((codex_home / "config.toml").is_symlink())
        self.assertTrue((codex_home / "auth.json").is_symlink())
        self.assertEqual(
            (codex_home / "auth.json").resolve(),
            (self.source_codex_home / "auth.json").resolve(),
        )
        self.assertTrue((codex_home / "skills/policy/SKILL.md").is_file())
        self.assertTrue((codex_home / "agents/generator.toml").is_file())
        self.assertFalse((codex_home / "agents/planner.toml").exists())
        self.assertFalse((codex_home / "hooks/branch_guard.py").exists())
        self.assertEqual((codex_home / "AGENTS.md").read_bytes(), b"")
        command = list(launch.command)
        self.assertIn("personality=\"pragmatic\"", command)
        self.assertIn("features.hooks=true", command)
        self.assertIn("project_doc_max_bytes=0", command)
        self.assertIn(
            f'projects."{self.project_root}".trust_level="untrusted"',
            command,
        )
        skill_override = next(item for item in command if item.startswith("skills.config="))
        self.assertIn(str(self.project_root / ".agents/skills/local/SKILL.md"), skill_override)
        self.assertIn("enabled = false", skill_override)
        self.assertTrue(any(item.startswith("developer_instructions=") for item in command))
        self.assertEqual(command[-2:], ["--model", "gpt-test"])

        self.assertFalse((codex_home / ".codex/hooks").exists())
        hooks = json.loads((codex_home / "hooks.json").read_text(encoding="utf-8"))
        commands = self.command_strings(hooks)
        self.assertFalse(any("git rev-parse --show-toplevel" in value for value in commands))
        self.assertFalse(any("HOOK_SHA256" in value for value in commands))
        self.assertTrue(
            any(
                str(launch.bundle_root / "policy/.agent-policy/runtime") in value
                for value in commands
            )
        )
        baseline = next(value for value in commands if "pre-tool codex" in value)
        environment = dict(os.environ)
        environment.update(launch.environment)
        executed = subprocess.run(
            ["/bin/sh", "-c", baseline],
            input=json.dumps(
                {
                    "cwd": str(self.project_root),
                    "session_id": "session-test",
                    "tool_name": "Bash",
                    "tool_input": {"command": "pwd"},
                }
            ),
            text=True,
            capture_output=True,
            cwd=self.project_root,
            env=environment,
            check=False,
        )
        self.assertEqual(executed.returncode, 0, executed.stderr)
        self.assertEqual(executed.stdout, "")

    def test_consumer_policy_inventory_detects_all_host_sources_but_not_logs(self) -> None:
        root = self.root / "policy-inventory"
        root.mkdir()
        project = ProjectConfig(
            id="user-ui",
            name="temporary-user-ui",
            path=root,
            commands=self.project.commands,
        )
        policy_files = (
            "AGENTS.md",
            "AGENTS.override.md",
            "CLAUDE.md",
            "CLAUDE.local.md",
            "opencode.json",
            "package.json",
            "README.md",
            ".agent-policy/manifest.json",
            ".agents/skills/policy/SKILL.md",
            ".harness/roles/ui.md",
            ".codex/hooks/__pycache__/branch_guard.cpython-314.pyc",
            ".codex/hooks.json",
            ".claude/hooks/harness_hook.py",
            ".opencode/plugins/branch_guard.py",
        )
        for relative in policy_files:
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("legacy policy\n", encoding="utf-8")
        (root / "package.json").write_text(
            '{"scripts":{"test":"python3 -I .codex/hooks/test_governance_hooks.py"}}\n',
            encoding="utf-8",
        )
        (root / "README.md").write_text(
            "정책 훅은 `.codex/hooks/`에서 실행한다.\n",
            encoding="utf-8",
        )
        preserved = (
            ".codex/logs/sessions/task/plan.md",
            ".claude/logs/sessions/task/handoff.md",
            ".opencode/logs/sessions/task/final-summary.md",
            ".agent-policy/logs/unknown/sessions/task/note.md",
            ".claude/settings.local.json",
            ".opencode/node_modules/example/index.js",
            ".opencode/package.json",
        )
        for relative in preserved:
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("{}\n", encoding="utf-8")

        self.assertEqual(consumer_policy_sources(project), policy_files)

    def test_start_rejects_stale_consumer_policy_for_every_host(self) -> None:
        stale_by_host = {
            "codex": ".codex/hooks/branch_guard.py",
            "claude": ".claude/hooks/harness_hook.py",
            "opencode": ".opencode/plugins/branch_guard.py",
        }
        root = self.root / "selected-worktree"
        root.mkdir()
        project = ProjectConfig(
            id="user-ui",
            name="temporary-user-ui",
            path=root,
            commands=self.project.commands,
        )

        for host, relative in stale_by_host.items():
            with self.subTest(host=host):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("legacy guard\n", encoding="utf-8")
                with (
                    patch("agent_policy.cli.select_projects", return_value=(project,)),
                    self.assertRaisesRegex(PolicyError, relative),
                ):
                    run_start("user-ui", host, None, True, role="logic")
                target.unlink()

    def test_selected_external_worktree_is_checked_for_consumer_policy(self) -> None:
        repository = self.root / "policy-source-repository"
        repository.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "sy-main"], cwd=repository, check=True)
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Policy Test",
                "-c",
                "user.email=policy@example.com",
                "commit",
                "--allow-empty",
                "-qm",
                "baseline",
            ],
            cwd=repository,
            check=True,
        )
        worktree = self.root / "policy-source-worktree"
        subprocess.run(
            ["git", "worktree", "add", "-q", "-b", "task/external", str(worktree)],
            cwd=repository,
            check=True,
        )
        stale = worktree / ".codex/hooks/branch_guard.py"
        stale.parent.mkdir(parents=True)
        stale.write_text("legacy guard\n", encoding="utf-8")
        project = ProjectConfig(
            id="user-ui",
            name="temporary-user-ui",
            path=repository,
            commands=self.project.commands,
        )

        selected = active_project(project, str(worktree), "task/external")

        self.assertEqual(
            consumer_policy_sources(selected),
            (".codex/hooks/branch_guard.py",),
        )

    def test_inject_only_sources_have_no_consumer_deployment_entry_points(self) -> None:
        cli = (CENTRAL_ROOT / "lib/agent_policy/cli.py").read_text(encoding="utf-8")
        core = (CENTRAL_ROOT / "lib/agent_policy/core.py").read_text(encoding="utf-8")
        guard = (CENTRAL_ROOT / "policy/guards/managed_policy_guard.py").read_text(
            encoding="utf-8"
        )
        for marker in (
            'add_parser("sync"',
            'add_parser("diff"',
            'add_parser("check"',
            "def run_sync(",
            "--retire-legacy",
        ):
            self.assertNotIn(marker, cli)
        for marker in (
            "def sync_project(",
            "def diff_project(",
            "class ProjectDiff",
            "class LegacyTrace",
        ):
            self.assertNotIn(marker, core)
        for marker in (
            "def load_manifest(",
            '"check", "--project"',
            "sync한 뒤",
        ):
            self.assertNotIn(marker, guard)
        self.assertFalse(any((CENTRAL_ROOT / "projects/legacy").glob("*.json")))

    def test_all_host_stop_paths_are_nonblocking_log_collection_only(self) -> None:
        codex = self.prepare("codex")
        codex_hooks = json.loads(
            (Path(codex.environment["CODEX_HOME"]) / "hooks.json").read_text(
                encoding="utf-8"
            )
        )["hooks"]
        codex_stop = [
            handler["command"]
            for group in codex_hooks["Stop"]
            for handler in group["hooks"]
        ]
        self.assertTrue(codex_stop)
        self.assertTrue(all("collect-logs" in command for command in codex_stop))

        claude = self.prepare("claude")
        claude_hooks = json.loads(
            (claude.bundle_root / "plugin/hooks/hooks.json").read_text(encoding="utf-8")
        )["hooks"]
        claude_stop = [
            handler["command"]
            for group in claude_hooks["Stop"]
            for handler in group["hooks"]
        ]
        self.assertTrue(claude_stop)
        self.assertTrue(all("collect-logs" in command for command in claude_stop))

        opencode = self.prepare("opencode")
        plugin = (opencode.bundle_root / "opencode-home/plugins/agent-policy.js").read_text(
            encoding="utf-8"
        )
        self.assertIn('event.type !== "session.idle"', plugin)
        self.assertIn('"collect-logs"', plugin)
        self.assertNotIn("documentation-stop", plugin)

    def test_codex_command_has_no_consumer_hook_disable_workaround(self) -> None:
        launch = self.prepare("codex")
        command = list(launch.command)
        self.assertFalse(any(value.startswith("hooks.state.") for value in command))

        central_hooks = Path(launch.environment["CODEX_HOME"]) / "hooks.json"
        central_commands = self.command_strings(
            json.loads(central_hooks.read_text(encoding="utf-8"))
        )
        self.assertTrue(
            any("managed_policy_guard.py" in value for value in central_commands)
        )

    def test_bundle_reuse_repairs_invalid_snapshot_and_keeps_consumer_unchanged(self) -> None:
        before = self.consumer_snapshot()
        first = self.prepare("opencode", role="review")
        prompt = first.system_prompt
        prompt.write_text("tampered", encoding="utf-8")
        second = self.prepare("opencode", role="review")
        self.assertEqual(second.bundle_root, first.bundle_root)
        self.assertIn("중앙 정책 inject 실행 컨텍스트", prompt.read_text(encoding="utf-8"))
        self.assertEqual(self.consumer_snapshot(), before)

    def test_opencode_runtime_dependencies_do_not_invalidate_bundle(self) -> None:
        first = self.prepare("opencode", role="review")
        home = first.bundle_root / "opencode-home"
        (home / ".gitignore").write_text("node_modules\n", encoding="utf-8")
        (home / "package.json").write_text('{"dependencies": {}}\n', encoding="utf-8")
        (home / "package-lock.json").write_text('{"lockfileVersion": 3}\n', encoding="utf-8")
        dependency = home / "node_modules/@opencode-ai/plugin/index.js"
        dependency.parent.mkdir(parents=True)
        dependency.write_text("export default {}\n", encoding="utf-8")
        executable = home / "node_modules/.bin/opencode-plugin"
        executable.parent.mkdir(parents=True)
        executable.symlink_to(dependency)

        second = self.prepare("opencode", role="review")

        self.assertEqual(second.bundle_root, first.bundle_root)
        self.assertTrue(dependency.is_file())
        self.assertTrue(executable.is_symlink())

        unexpected = home / "unexpected.txt"
        unexpected.write_text("not managed by OpenCode\n", encoding="utf-8")
        third = self.prepare("opencode", role="review")

        self.assertEqual(third.bundle_root, first.bundle_root)
        self.assertFalse(dependency.exists())
        self.assertFalse(unexpected.exists())

    def test_role_profiles_create_distinct_scoped_bundles(self) -> None:
        logic = self.prepare("claude", role="logic")
        ui = self.prepare("claude", role="ui")

        self.assertNotEqual(logic.bundle_root, ui.bundle_root)
        self.assertTrue((logic.bundle_root / "plugin/agents/generator.md").is_file())
        self.assertFalse((logic.bundle_root / "plugin/agents/publisher.md").exists())
        self.assertTrue((ui.bundle_root / "plugin/agents/publisher.md").is_file())
        self.assertFalse(
            (
                logic.bundle_root
                / "policy/.agent-policy/common/skills/policy/task-role-routing/references/ui.md"
            ).exists()
        )
        self.assertFalse(
            (
                ui.bundle_root
                / "policy/.agent-policy/common/skills/policy/task-role-routing/references/logic.md"
            ).exists()
        )

    def test_inject_requires_role_and_session_dir_matches_host(self) -> None:
        with (
            patch("agent_policy.cli.select_projects", return_value=(self.project,)),
            self.assertRaises(PolicyError),
        ):
            run_start("user-ui", "claude", None, True, "inject")

        self.assertEqual(
            normalized_session_dir(
                ".claude/logs/sessions/2026-09-03-task",
                "claude",
            ),
            ".claude/logs/sessions/2026-09-03-task",
        )
        with self.assertRaises(PolicyError):
            normalized_session_dir(
                ".codex/logs/sessions/2026-09-03-task",
                "claude",
            )
        assigned = self.prepare(
            "claude",
            task="task/assigned-work",
            responsibility="contributor",
        )
        self.assertEqual(
            assigned.environment["ASAN_AGENT_POLICY_TASK"],
            "task/assigned-work",
        )
        self.assertEqual(
            assigned.environment["ASAN_ARTIFACT_RESPONSIBILITY"],
            "contributor",
        )
        with self.assertRaises(PolicyError):
            self.prepare("claude", task="invalid-task")

    def test_start_parser_is_inject_only_and_sync_commands_are_absent(self) -> None:
        default = build_parser().parse_args(
            [
                "start",
                "--project",
                "user-ui",
                "--host",
                "codex",
                "--role",
                "logic",
            ]
        )
        injected = build_parser().parse_args(
            [
                "start",
                "--project",
                "user-ui",
                "--host",
                "codex",
                "--mode",
                "inject",
                "--role",
                "logic",
            ]
        )
        self.assertEqual(default.mode, "inject")
        self.assertEqual(injected.mode, "inject")
        self.assertEqual(injected.role, "logic")
        self.assertEqual(default.role, "logic")
        self.assertIsNone(default.worktree)
        self.assertIsNone(default.branch)
        self.assertIsNone(default.session_dir)
        self.assertIsNone(default.task)
        self.assertEqual(default.responsibility, "owner")

        for removed in ("sync", "diff", "check"):
            with self.subTest(command=removed), redirect_stderr(StringIO()):
                with self.assertRaises(SystemExit):
                    build_parser().parse_args([removed, "--project", "user-ui"])
        with redirect_stderr(StringIO()):
            with self.assertRaises(SystemExit):
                build_parser().parse_args(
                    [
                        "start",
                        "--project",
                        "user-ui",
                        "--host",
                        "codex",
                        "--mode",
                        "sync",
                        "--role",
                        "logic",
                    ]
                )

    def test_start_worktree_must_match_repository_and_branch(self) -> None:
        repository = self.root / "repository"
        repository.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "sy-main"], cwd=repository, check=True)
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Policy Test",
                "-c",
                "user.email=policy@example.com",
                "commit",
                "--allow-empty",
                "-qm",
                "baseline",
            ],
            cwd=repository,
            check=True,
        )
        worktree = self.root / "isolated"
        subprocess.run(
            ["git", "worktree", "add", "-q", "-b", "task/isolated", str(worktree)],
            cwd=repository,
            check=True,
        )
        project = ProjectConfig(
            id="user-ui",
            name="temporary-user-ui",
            path=repository,
            commands=self.project.commands,
        )

        selected = active_project(project, str(worktree), "task/isolated")

        self.assertEqual(selected.path, worktree.resolve())
        launch = prepare_injection(
            selected,
            "codex",
            "logic",
            build_root=self.build_root,
            state_root=self.state_root,
            source_codex_home=self.source_codex_home,
        )
        self.assertEqual(
            launch.environment["ASAN_AGENT_POLICY_PROJECT_PATH"],
            str(worktree.resolve()),
        )
        self.assertIn(
            f'projects."{worktree.resolve()}".trust_level="untrusted"',
            launch.command,
        )
        with self.assertRaises(PolicyError):
            active_project(project, str(worktree), "task/other")

    def test_start_uses_only_central_audit_and_injection(self) -> None:
        root = self.root / "clean-consumer"
        root.mkdir()
        project = ProjectConfig(
            id="user-ui",
            name="temporary-user-ui",
            path=root,
            commands=self.project.commands,
        )
        launch = InjectionLaunch(
            project=project,
            host="codex",
            role="logic",
            bundle_root=self.build_root,
            system_prompt=self.build_root / "system-prompt.md",
            command=("codex",),
            environment={"CODEX_HOME": str(self.state_root)},
        )
        with (
            patch("agent_policy.cli.select_projects", return_value=(project,)),
            patch("agent_policy.cli.audit_project", return_value=()),
            patch("agent_policy.cli.prepare_injection", return_value=launch),
        ):
            stdout = StringIO()
            stderr = StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = run_start(
                    "user-ui",
                    "codex",
                    None,
                    True,
                    role="logic",
                )
            self.assertEqual(code, 0)
            self.assertEqual(stderr.getvalue(), "")
            self.assertIn("mode: inject", stdout.getvalue())

    def test_task_start_rejects_legacy_branch_before_host_launch(self) -> None:
        repository = self.root / "legacy-task-repository"
        repository.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "sy-main"], cwd=repository, check=True)
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Policy Test",
                "-c",
                "user.email=policy@example.com",
                "commit",
                "--allow-empty",
                "-qm",
                "baseline",
            ],
            cwd=repository,
            check=True,
        )
        branch = "task/legacy-start"
        subprocess.run(["git", "switch", "-qc", branch], cwd=repository, check=True)
        parent_head = subprocess.run(
            ["git", "rev-parse", "sy-main"],
            cwd=repository,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        for field, value in {
            "purpose": "구형 task 시작 차단",
            "parent": "sy-main",
            "parent-head": parent_head,
            "merge-target": "sy-main",
            "proposal": f"branch:{branch}|parent:sy-main@{parent_head}|merge:sy-main",
        }.items():
            subprocess.run(
                ["git", "config", f"branch.{branch}.asan-{field}", value],
                cwd=repository,
                check=True,
            )
        subprocess.run(
            ["git", "config", "--add", f"branch.{branch}.asan-scope", "src"],
            cwd=repository,
            check=True,
        )
        project = ProjectConfig(
            id="user-ui",
            name="temporary-user-ui",
            path=repository,
            commands=self.project.commands,
        )

        with (
            patch("agent_policy.cli.select_projects", return_value=(project,)),
            patch("agent_policy.cli.audit_project", return_value=()),
            patch("agent_policy.cli.prepare_injection") as prepare,
            self.assertRaisesRegex(PolicyError, "V3 계약을 다시 승인"),
        ):
            run_start("user-ui", "codex", None, True, role="logic", task=branch)
        prepare.assert_not_called()

    def test_task_start_rejects_pending_policy_retirement_outside_scope(self) -> None:
        repository = self.root / "retirement-task-repository"
        repository.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "sy-main"], cwd=repository, check=True)
        retired_prompt = repository / "AGENTS.md"
        retired_prompt.write_text("retired consumer prompt\n", encoding="utf-8")
        subprocess.run(["git", "add", "AGENTS.md"], cwd=repository, check=True)
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Policy Test",
                "-c",
                "user.email=policy@example.com",
                "commit",
                "-qm",
                "baseline",
            ],
            cwd=repository,
            check=True,
        )
        branch = "task/pending-retirement"
        subprocess.run(["git", "switch", "-qc", branch], cwd=repository, check=True)
        project = ProjectConfig(
            id="user-ui",
            name="temporary-user-ui",
            path=repository,
            commands=self.project.commands,
        )
        source = render_project(project)[".agent-policy/runtime/branch_guard.py"]
        guard = ModuleType("retirement_branch_guard")
        guard.__file__ = str(CENTRAL_ROOT / "policy/guards/branch_guard.py")
        exec(compile(source, guard.__file__, "exec"), guard.__dict__)
        parent_head = guard.head(repository, "sy-main")
        roles = ("logic",)
        scopes = ("src",)
        purpose = "소비자 정책 퇴역 완료 검증"
        reason = "정책 사본 삭제를 기능 작업과 분리"
        contract = guard.canonical_contract(
            branch,
            purpose,
            "sy-main",
            parent_head,
            "sy-main",
            scopes,
            reason,
            "",
            roles,
            "codex",
        )
        digest = guard.contract_sha256(contract)
        for field, value in {
            "contract-version": "3",
            "task-id": branch.removeprefix("task/"),
            "purpose": purpose,
            "parent": "sy-main",
            "parent-head": parent_head,
            "merge-target": "sy-main",
            "proposal": f"asan-v3:{digest}",
            "contract-sha256": digest,
            "reason": reason,
            "git-integrator": "codex",
            "state": "ACTIVE",
        }.items():
            subprocess.run(
                ["git", "config", f"branch.{branch}.asan-{field}", value],
                cwd=repository,
                check=True,
            )
        subprocess.run(
            ["git", "config", "--add", f"branch.{branch}.asan-role", "logic"],
            cwd=repository,
            check=True,
        )
        subprocess.run(
            ["git", "config", "--add", f"branch.{branch}.asan-scope", "src"],
            cwd=repository,
            check=True,
        )
        retired_prompt.unlink()

        with (
            patch("agent_policy.cli.select_projects", return_value=(project,)),
            patch("agent_policy.cli.audit_project", return_value=()),
            patch("agent_policy.cli.prepare_injection") as prepare,
            self.assertRaisesRegex(PolicyError, "정책 사본 퇴역 삭제가 아직 Git에 통합되지 않았습니다"),
        ):
            run_start("user-ui", "codex", None, True, role="logic", task=branch)
        prepare.assert_not_called()

        maintenance_scopes = ("AGENTS.md",)
        maintenance_contract = guard.canonical_contract(
            branch,
            purpose,
            "sy-main",
            parent_head,
            "sy-main",
            maintenance_scopes,
            reason,
            "",
            roles,
            "codex",
        )
        maintenance_digest = guard.contract_sha256(maintenance_contract)
        subprocess.run(
            ["git", "config", "--unset-all", f"branch.{branch}.asan-scope"],
            cwd=repository,
            check=True,
        )
        subprocess.run(
            ["git", "config", "--add", f"branch.{branch}.asan-scope", "AGENTS.md"],
            cwd=repository,
            check=True,
        )
        for field, value in {
            "proposal": f"asan-v3:{maintenance_digest}",
            "contract-sha256": maintenance_digest,
        }.items():
            subprocess.run(
                ["git", "config", f"branch.{branch}.asan-{field}", value],
                cwd=repository,
                check=True,
            )

        with (
            patch("agent_policy.cli.select_projects", return_value=(project,)),
            patch("agent_policy.cli.audit_project", return_value=()),
            patch("agent_policy.cli.prepare_injection") as prepare,
            redirect_stdout(StringIO()),
        ):
            result = run_start("user-ui", "codex", None, True, role="logic", task=branch)
        self.assertEqual(result, 0)
        prepare.assert_called_once()


if __name__ == "__main__":
    unittest.main()
