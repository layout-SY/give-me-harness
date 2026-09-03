from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from agent_policy.cli import active_project, build_parser, normalized_session_dir, run_start
from agent_policy.core import PolicyError, ProjectConfig, ProjectDiff, render_project
from agent_policy.injection import InjectionLaunch, prepare_injection


class InjectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.project_root = self.root / "consumer"
        self.project_root.mkdir()
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

    def test_bundle_reuse_repairs_invalid_snapshot_and_keeps_consumer_unchanged(self) -> None:
        before = self.consumer_snapshot()
        first = self.prepare("opencode", role="review")
        prompt = first.system_prompt
        prompt.write_text("tampered", encoding="utf-8")
        second = self.prepare("opencode", role="review")
        self.assertEqual(second.bundle_root, first.bundle_root)
        self.assertIn("중앙 정책 inject 실행 컨텍스트", prompt.read_text(encoding="utf-8"))
        self.assertEqual(self.consumer_snapshot(), before)

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

    def test_start_parser_defaults_to_sync_and_accepts_inject(self) -> None:
        default = build_parser().parse_args(
            ["start", "--project", "user-ui", "--host", "codex"]
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
        self.assertEqual(default.mode, "sync")
        self.assertEqual(injected.mode, "inject")
        self.assertEqual(injected.role, "logic")
        self.assertIsNone(default.role)
        self.assertIsNone(default.worktree)
        self.assertIsNone(default.branch)
        self.assertIsNone(default.session_dir)
        self.assertIsNone(default.task)
        self.assertEqual(default.responsibility, "owner")

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
        self.assertEqual(selected.policy_root, repository.resolve())
        with self.assertRaises(PolicyError):
            active_project(project, str(worktree), "task/other")

    def test_inject_drift_warns_but_sync_drift_still_blocks(self) -> None:
        difference = ProjectDiff(
            project=self.project,
            added=("CLAUDE.md",),
            changed=("AGENTS.md",),
            stale=(),
            legacy=(),
            manifest_issues=("manifest missing",),
        )
        launch = InjectionLaunch(
            project=self.project,
            host="codex",
            role="logic",
            bundle_root=self.build_root,
            system_prompt=self.build_root / "system-prompt.md",
            command=("codex",),
            environment={"CODEX_HOME": str(self.state_root)},
        )
        with (
            patch("agent_policy.cli.select_projects", return_value=(self.project,)),
            patch("agent_policy.cli.diff_project", return_value=difference),
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
                    "inject",
                    role="logic",
                )
            self.assertEqual(code, 0)
            self.assertIn("inject 번들로 세션을 계속", stderr.getvalue())
            self.assertIn("mode: inject", stdout.getvalue())

        with (
            patch("agent_policy.cli.select_projects", return_value=(self.project,)),
            patch("agent_policy.cli.diff_project", return_value=difference),
            self.assertRaises(PolicyError),
        ):
            with redirect_stdout(StringIO()):
                run_start("user-ui", "codex", None, True, "sync")


if __name__ == "__main__":
    unittest.main()
