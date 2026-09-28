"""실제 수정 훅과 Prettier를 연결하는 회귀 검증. 소비자 소스는 임시 저장소만 사용한다."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import shlex
import time
import unittest
from pathlib import Path

import test_shared_git_access as shared


class FormattingTests(unittest.TestCase):
    def setUp(self):
        self.fixture = shared.SharedGitAccessTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        self.worktree = self.fixture.worktree
        for root in (self.root, self.worktree):
            (root / ".prettierrc").write_text('{"semi":true,"tabWidth":2,"printWidth":160,"arrowParens":"always"}')
            (root / ".prettierignore").write_text("src/ignored.ts\n")
        self.env = {"ASAN_FORMATTER": "prettier-v1"}
        self.calls = 0

    def hook(self, mode, event, *, host="claude", environment=None):
        return self.fixture.run_event(host, mode, event, environment={**self.env, **(environment or {})})

    def write(self, relative, content, *, root=None, host="claude", session=None):
        self.calls += 1
        path = (root or self.root) / relative
        event = {"tool_name": "Write", "tool_call_id": f"format-write-{self.calls}",
                 "tool_input": {"file_path": str(path), "content": content}}
        if session:
            event["session_id"] = session
        # Existing implementation approval remains independently required.
        for tool, args in (("Skill", {"skill": "policy"}), ("Read", {"file_path": "src/app.ts"})):
            self.hook("post-tool", {**({"session_id": session} if session else {}), "tool_name": tool,
                "tool_input": args, "tool_response": {"success": True}}, host=host)
        self.hook("user-prompt", {**({"session_id": session} if session else {}), "prompt": "진행"}, host=host)
        self.fixture.assert_allowed(self.hook("pre-tool", event, host=host))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        self.fixture.assert_allowed(self.hook("post-tool", {**event, "tool_response": {"success": True}}, host=host))
        return path

    def test_validation_trigger_formats_only_successfully_modified_files(self):
        owned = self.write("src/owned.ts", "export const owned={value:1};\n")
        untouched = self.root / "src/other.ts"
        untouched.write_text("export const other={value:2};\n")
        result = self.hook("pre-tool", {"tool_name": "Bash", "tool_input": {"command": "npm run lint"}})
        self.fixture.assert_allowed(result)
        self.assertEqual(owned.read_text(), "export const owned = { value: 1 };\n")
        self.assertEqual(untouched.read_text(), "export const other={value:2};\n")

    def test_codex_patch_move_and_delete_track_only_surviving_code(self):
        old = self.write("src/old.ts", "export const moved={value:1};\n", host="codex")
        removed = self.write("src/removed.ts", "export const removed=1;\n", host="codex")
        moved = self.root / "src/moved.ts"
        patch = f"*** Begin Patch\n*** Update File: {old}\n*** Move to: {moved}\n@@\n-export const moved={{value:1}};\n+export const moved={{value:2}};\n*** Delete File: {removed}\n*** End Patch"
        event = {"tool_name": "apply_patch", "tool_call_id": "native-patch", "tool_input": {"command": patch}}
        self.fixture.assert_allowed(self.hook("pre-tool", event, host="codex"))
        old.rename(moved)
        moved.write_text("export const moved={value:2};\n")
        removed.unlink()
        self.fixture.assert_allowed(self.hook("post-tool", {**event,
            "tool_response": "Success. Updated the following files:\nM src/moved.ts\nD src/removed.ts\n"}, host="codex"))
        result = self.runner("codex")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(moved.read_text(), "export const moved = { value: 2 };\n")
        self.assertFalse(old.exists())
        self.assertFalse(removed.exists())

    def test_changed_file_is_not_overwritten_by_automatic_formatting(self):
        path = self.write("src/owned.ts", "export const owned={value:1};\n")
        path.write_text("export const anotherSession={value:9};\n")
        result = self.hook("pre-tool", {"tool_name": "Bash", "tool_input": {"command": "npm run test"}})
        self.assertTrue(result.returncode != 0 or '"deny"' in result.stdout)
        self.assertIn("변경", result.stdout + result.stderr)
        self.assertEqual(path.read_text(), "export const anotherSession={value:9};\n")

    def runner(self, host="claude", root=None):
        args = [sys.executable, "-I", str(self.fixture.guard.with_name("formatting.py")), "apply",
                "--host", host, "--session", f"{host}-session"]
        env = {key: value for key, value in os.environ.items() if not key.startswith("ASAN_")}
        env.update(self.env, ASAN_AGENT_POLICY_STATE_ROOT=str(self.fixture.state))
        return subprocess.run(args, cwd=root or self.root, env=env, text=True, capture_output=True)

    def test_explicit_trigger_uses_current_worktree_and_preserves_mode_and_index(self):
        first = self.write("src/first.ts", "export const first={value:1};\n")
        second = self.write("src/second.ts", "export const second={value:2};\n", root=self.worktree)
        second.chmod(0o755)
        before = self.fixture.git("ls-files", "--stage", root=self.worktree)
        result = self.runner(root=self.worktree)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(first.read_text(), "export const first={value:1};\n")
        self.assertEqual(second.read_text(), "export const second = { value: 2 };\n")
        self.assertEqual(second.stat().st_mode & 0o777, 0o755)
        self.assertEqual(self.fixture.git("ls-files", "--stage", root=self.worktree), before)

    def test_cd_trigger_formats_linked_worktree_and_updates_its_receipt_on_all_hosts(self):
        # The injected runtime belongs to the central repository, not the consumer.
        self.fixture.git("init", "-q", root=self.fixture.bundle)
        for host in ("claude", "codex", "opencode"):
            with self.subTest(host=host):
                primary = self.write(f"src/primary-{host}.ts", "export const primary={value:1};\n", host=host)
                linked = self.write(f"src/linked-{host}.ts", "export const linked={value:2};\n",
                                    root=self.worktree, host=host)
                command = shlex.join([sys.executable, "-I", str(self.fixture.guard.with_name("formatting.py")),
                                      "apply", "--host", host, "--session", f"{host}-session"])
                wrapped = f"\ncd {shlex.quote(str(self.worktree))} && {command}\n"
                before = self.fixture.git("ls-files", "--stage", root=self.worktree)
                result = self.hook("pre-tool", {"tool_name": "Bash", "tool_input": {"command": wrapped}}, host=host)
                self.fixture.assert_allowed(result)
                self.assertEqual(linked.read_text(), "export const linked = { value: 2 };\n")
                self.assertEqual(primary.read_text(), "export const primary={value:1};\n")
                self.assertEqual(self.fixture.git("ls-files", "--stage", root=self.worktree), before)
                receipt = self.runner(host, root=self.worktree)
                self.assertEqual(receipt.returncode, 0, receipt.stderr)
                self.assertEqual(json.loads(receipt.stdout)["formatted"], [str(linked.resolve())])
                self.fixture.assert_allowed(self.hook("pre-tool", {"tool_name": "Bash", "tool_input": {
                    "command": command.replace(" apply ", " check "), "workdir": str(self.worktree)}}, host=host))

    def test_cd_trigger_preserves_repository_session_and_shell_boundaries(self):
        self.fixture.git("init", "-q", root=self.fixture.bundle)
        foreign = self.fixture.base / "foreign"
        foreign.mkdir()
        self.fixture.git("init", "-q", root=foreign)
        other_runtime = self.fixture.base / "other-runtime"
        other_runtime.mkdir()
        shutil.copy2(self.fixture.guard.with_name("formatting.py"), other_runtime / "formatting.py")
        for host in ("claude", "codex", "opencode"):
            linked = self.write(f"src/protected-{host}.ts", "export const protectedValue={value:1};\n",
                                root=self.worktree, host=host)
            command = shlex.join([sys.executable, "-I", str(self.fixture.guard.with_name("formatting.py")),
                                  "apply", "--host", host, "--session", f"{host}-session"])
            prefix = f"cd {shlex.quote(str(self.worktree))}"
            commands = (
                f"cd {shlex.quote(str(foreign))} && {command}",
                f"{prefix} && {command.replace(f'{host}-session', 'other-session')}",
                f"{prefix} && {command.replace(str(self.fixture.guard.parent), str(other_runtime))}",
                f"{prefix} && {command} && git commit -am bypass",
                f"{prefix}; {command}",
                f"{prefix} || {command}",
                f"{prefix} && {command} > receipt.json",
            )
            for candidate in commands:
                with self.subTest(host=host, command=candidate):
                    result = self.hook("pre-tool", {"tool_name": "Bash", "tool_input": {"command": candidate}}, host=host)
                    self.assertTrue(result.returncode != 0 or '"deny"' in result.stdout, result.stdout + result.stderr)
                    self.assertEqual(linked.read_text(), "export const protectedValue={value:1};\n")

    def test_all_hosts_honor_ignore_and_format_again_after_an_edit(self):
        for host in ("claude", "codex", "opencode"):
            with self.subTest(host=host):
                ignored = self.write("src/ignored.ts", "export const ignored={value:1};\n", host=host)
                own = self.write(f"src/{host}.tsx", "export const View=()=>{return <div>hello</div>};\n", host=host)
                result = self.runner(host)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("export const View = () =>", own.read_text())
                self.assertEqual(ignored.read_text(), "export const ignored={value:1};\n")
                self.fixture.assert_allowed(self.hook("format-stop", {}, host=host))
                own = self.write(f"src/{host}.tsx", "export const View=()=>{return <div>next</div>};\n", host=host)
                self.assertEqual(self.runner(host).returncode, 0)
                self.assertIn("export const View = () =>", own.read_text())

    def test_syntax_error_preserves_all_files_and_keeps_pending_status(self):
        good = self.write("src/good.ts", "export const good={value:1};\n")
        broken = self.write("src/broken.ts", "export const broken = {\n")
        result = self.runner()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Prettier 실행 실패", result.stderr)
        self.assertEqual(good.read_text(), "export const good={value:1};\n")
        self.assertEqual(broken.read_text(), "export const broken = {\n")
        stopped = self.hook("format-stop", {})
        self.assertEqual(json.loads(stopped.stdout)["decision"], "block")
        repeated = self.hook("format-stop", {"stop_hook_active": True})
        self.assertNotIn('"block"', repeated.stdout)
        self.assertIn("Prettier", repeated.stdout)
        self.assertFalse(list(self.fixture.state.glob("repositories/*/branch-relations/v1/writes/*.json")))

    def test_staged_file_is_not_rewritten(self):
        path = self.write("src/staged.ts", "export const staged={value:1};\n")
        self.fixture.git("add", "--", "src/staged.ts")
        before = self.fixture.git("diff", "--cached")
        result = self.runner()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("stage", result.stderr)
        self.assertEqual(path.read_text(), "export const staged={value:1};\n")
        self.assertEqual(self.fixture.git("diff", "--cached"), before)

    def test_another_session_write_with_same_bytes_prevents_adoption(self):
        self.write("src/shared.ts", "export const shared={value:1};\n")
        self.write("src/shared.ts", "export const shared={value:1};\n", session="other-session")
        result = self.runner()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("다른 쓰기", result.stderr)

    def test_concurrent_change_during_prettier_computation_is_preserved(self):
        path = self.write("src/race.ts", "export const race={value:1};\n")
        runner = self.fixture.guard.with_name("prettier_runner.mjs")
        marker = self.fixture.base / "started"
        runner.write_text('import markerFs from "node:fs";\nmarkerFs.writeFileSync(' + json.dumps(str(marker)) + ', "ready");\n'
            + 'await new Promise((resolve) => setTimeout(resolve, 600));\n' + runner.read_text())
        env = {key: value for key, value in os.environ.items() if not key.startswith("ASAN_")}
        env.update(self.env, ASAN_AGENT_POLICY_STATE_ROOT=str(self.fixture.state))
        process = subprocess.Popen([sys.executable, "-I", str(self.fixture.guard.with_name("formatting.py")),
            "apply", "--host", "claude", "--session", "claude-session"], cwd=self.root,
            env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(lambda: process.kill() if process.poll() is None else None)
        deadline = time.monotonic() + 5
        while not marker.exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertTrue(marker.exists())
        path.write_text("export const newer={value:9};\n")
        _, stderr = process.communicate(timeout=10)
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("변경", stderr)
        self.assertEqual(path.read_text(), "export const newer={value:9};\n")

    def test_missing_formatter_does_not_download_or_silently_pass(self):
        self.write("src/owned.ts", "export const owned={value:1};\n")
        configuration = self.fixture.guard.with_name("runtime_config.py")
        configuration.write_text("\n".join(
            f"CENTRAL_ROOT: Final = Path({str(self.fixture.base / 'empty-central')!r})"
            if line.startswith("CENTRAL_ROOT: Final =") else line for line in configuration.read_text().splitlines()) + "\n")
        result = self.runner()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("formatter-install", result.stderr)
        self.assertFalse((self.fixture.base / "empty-central").exists())

    def test_no_code_commit_only_session_has_no_format_or_artifact_requirement(self):
        self.fixture.assert_allowed(self.hook("format-stop", {}))
        result = self.hook("pre-tool", {"tool_name": "Bash", "tool_input": {"command": "git commit --allow-empty -m existing"}})
        self.assertNotIn("Prettier", result.stdout + result.stderr)
        self.assertFalse((self.root / ".claude/logs/sessions").exists())
        self.write("src/pending.ts", "export const pending={value:1};\n")
        for operation in ("merge", "rebase"):
            for action in ("--abort", "--quit"):
                result = self.hook("pre-tool", {"tool_name": "Bash", "tool_input": {
                    "command": f"git {operation} {action}"}})
                self.assertNotIn("Prettier", result.stdout + result.stderr)

    def test_configuration_change_invalidates_format_receipt(self):
        (self.root / ".prettierrc").write_text('{"endOfLine":"auto"}')
        windows = self.write("src/windows.ts", "export const windows={value:1};\r\n")
        self.assertEqual(self.runner().returncode, 0)
        self.assertEqual(windows.read_bytes(), b"export const windows = { value: 1 };\r\n")
        path = self.write("src/owned.ts", "export const owned={value:1};\n")
        self.assertEqual(self.runner().returncode, 0)
        (self.root / ".prettierrc").write_text('{"semi":false}')
        self.assertEqual(self.runner().returncode, 0)
        self.assertEqual(path.read_text(), "export const owned = { value: 1 }\n")

    def test_symlink_replacement_is_not_followed(self):
        path = self.write("src/owned.ts", "export const owned={value:1};\n")
        outside = self.fixture.base / "outside.ts"
        outside.write_text("export const privateValue={value:7};\n")
        path.unlink()
        path.symlink_to(outside)
        result = self.runner()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("심볼릭 링크", result.stderr)
        self.assertEqual(outside.read_text(), "export const privateValue={value:7};\n")

    def assert_unconfirmed_write_is_not_formatted(self, response):
        path = self.write("src/unconfirmed.ts", "export const value={n:1};\n")
        event = {"tool_name": "Write", "tool_call_id": "uncertain", "tool_input": {
            "file_path": str(path), "content": "export const value={n:2};\n"}}
        self.fixture.assert_allowed(self.hook("pre-tool", event))
        path.write_text("export const value={n:2};\n")
        self.hook("post-tool", {**event, "tool_response": response})
        result = self.runner()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(path.read_text(), "export const value={n:2};\n")
        stopped = self.hook("format-stop", {})
        self.assertEqual(json.loads(stopped.stdout)["decision"], "block")

    def test_unknown_write_is_not_formatted_as_success(self):
        self.assert_unconfirmed_write_is_not_formatted({})

    def test_failed_partial_write_is_not_formatted_as_success(self):
        self.assert_unconfirmed_write_is_not_formatted({"success": False})

    def test_removed_worktree_does_not_block_session_stop(self):
        self.write("src/completed.ts", "export const completed={value:1};\n", root=self.worktree)
        self.assertEqual(self.runner(root=self.worktree).returncode, 0)
        shutil.rmtree(self.worktree)
        self.fixture.assert_allowed(self.hook("format-stop", {}))

    def test_completed_format_receipt_does_not_bind_a_session_to_the_previous_branch(self):
        path = self.write("src/branch.ts", "export const previous={value:1};\n")
        self.assertEqual(self.runner().returncode, 0)
        self.fixture.git("add", "--", "src/branch.ts")
        self.fixture.git("commit", "-qm", "formatted task")
        self.fixture.git("switch", "-qc", "another-task")
        path.write_text("export const anotherTask={value:2};\n")
        self.fixture.git("add", "--", "src/branch.ts")
        self.fixture.git("commit", "-qm", "another task content")
        result = self.runner()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(path.read_text(), "export const anotherTask={value:2};\n")
        self.fixture.assert_allowed(self.hook("format-stop", {}))
        self.write("src/branch.ts", "export const next={value:3};\n")
        self.assertEqual(self.runner().returncode, 0)
        self.assertEqual(path.read_text(), "export const next = { value: 3 };\n")

    def test_recovered_unknown_write_can_be_finished_by_a_successful_edit(self):
        self.assert_unconfirmed_write_is_not_formatted({})
        # The existing approved write-recovery operation removes this reservation
        # after the caller checks that the unknown process actually terminated.
        for path in self.fixture.state.glob("repositories/*/branch-relations/v1/writes/*.json"):
            path.unlink()
        owned = self.write("src/unconfirmed.ts", "export const value={n:3};\n")
        result = self.runner()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(owned.read_text(), "export const value = { n: 3 };\n")

    def test_native_launcher_prompt_has_an_executable_formatter_trigger_for_each_host(self):
        from dataclasses import replace
        from agent_policy.core import load_project
        from agent_policy.injection import prepare_injection
        fake_home = self.fixture.base / "source-home"
        fake_home.mkdir()
        (fake_home / "config.toml").write_text("")
        for host in ("claude", "codex", "opencode"):
            with self.subTest(host=host):
                launch = prepare_injection(replace(load_project("user-ui"), path=self.root), host, "logic",
                    build_root=self.fixture.base / "launch-build", state_root=self.fixture.base / "launch-state",
                    source_codex_home=fake_home)
                runtime = {"claude": launch.bundle_root / "plugin/runtime",
                           "codex": launch.bundle_root / "policy/.agent-policy/runtime",
                           "opencode": launch.bundle_root / "opencode-home/runtime"}[host]
                self.fixture.guard = runtime / "managed_policy_guard.py"
                self.fixture.state = self.fixture.base / "launch-state"
                self.env = launch.environment
                path = self.write(f"src/native-{host}.ts", "export const native={value:1};\n", host=host)
                command = shlex.join(["python3", "-I", str(runtime / "formatting.py"), "apply"])
                self.assertIn(command, launch.system_prompt.read_text())
                event = {"tool_name": "Bash", "tool_input": {"command": command}}
                self.fixture.assert_allowed(self.hook("pre-tool", event, host=host))
                self.assertEqual(path.read_text(), "export const native = { value: 1 };\n")
                env = {key: value for key, value in os.environ.items() if not key.startswith("ASAN_")}
                # The native command only confirms the hook's result. Simulate
                # a sandbox that permits reading central state but no writes.
                modes = [(entry, entry.stat().st_mode & 0o777) for entry in
                         [self.fixture.state, *self.fixture.state.rglob("*")] if not entry.is_symlink()]
                try:
                    for entry, mode in modes:
                        entry.chmod(mode & ~0o222)
                    result = subprocess.run(shlex.split(command), cwd=self.root, env={**env, **launch.environment},
                                            text=True, capture_output=True)
                finally:
                    for entry, mode in modes:
                        entry.chmod(mode)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(path.read_text(), "export const native = { value: 1 };\n")
                linked = self.write(f"src/native-linked-{host}.ts", "export const linked={value:2};\n",
                                    root=self.worktree, host=host)
                wrapped = f"cd -- {shlex.quote(str(self.worktree))} && {command}"
                self.fixture.assert_allowed(self.hook("pre-tool", {
                    "tool_name": "Bash", "tool_input": {"command": wrapped}}, host=host))
                self.assertEqual(linked.read_text(), "export const linked = { value: 2 };\n")
                result = subprocess.run(shlex.split(command), cwd=self.worktree, env={**env, **launch.environment},
                                        text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)["formatted"], [str(linked.resolve())])


if __name__ == "__main__":
    unittest.main()
