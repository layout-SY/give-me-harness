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
        plan = self.root / self.env.get("ASAN_SESSION_DIR", f".{host}/logs/sessions/shared-session") / "plan.md"
        if not plan.is_file():
            log = {"tool_name": "Write", "tool_call_id": f"plan-{self.calls}", "tool_input": {
                "file_path": str(plan), "content": "코드 변경과 공통 formatter 검증 계획"}}
            if session:
                log["session_id"] = session
            self.fixture.assert_allowed(self.hook("pre-tool", log, host=host))
            plan.parent.mkdir(parents=True, exist_ok=True)
            plan.write_text(log["tool_input"]["content"])
            self.fixture.assert_allowed(self.hook("post-tool", {**log, "tool_response": {"success": True}}, host=host))
        # Existing implementation approval remains independently required.
        for tool, args in (("Skill", {"skill": "policy"}), ("Read", {"file_path": "src/app.ts"})):
            self.hook("post-tool", {**({"session_id": session} if session else {}), "cwd": str(root or self.root), "tool_name": tool,
                "tool_input": args, "tool_response": {"success": True}}, host=host)
        self.hook("user-prompt", {**({"session_id": session} if session else {}), "prompt": "진행"}, host=host)
        self.fixture.assert_allowed(self.hook("pre-tool", event, host=host))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        self.fixture.assert_allowed(self.hook("post-tool", {**event, "tool_response": {"success": True}}, host=host))
        return path

    def test_permission_denial_releases_only_denied_call_and_keeps_later_save(self):
        path = self.write("src/denied.ts", "export const n={value:1};\n")
        denied = {"tool_name": "Write", "tool_call_id": "denied-before-execution",
                  "tool_input": {"file_path": str(path), "content": "never written"}}
        self.fixture.assert_allowed(self.hook("pre-tool", denied))
        path = self.write("src/denied.ts", "export const n={value:2};\n")
        waiting = {**denied, "tool_call_id": "still-waiting",
                   "tool_input": {"file_path": str(self.root / "src/waiting.ts"), "content": "pending"}}
        self.fixture.assert_allowed(self.hook("pre-tool", waiting))
        lookup = [sys.executable, "-I", str(self.fixture.guard.with_name("git_operations.py")), "writes"]
        self.fixture.assert_allowed(self.hook("pre-tool", {"tool_name": "Bash",
            "tool_input": {"command": shlex.join(lookup)}}))
        environment = {key: value for key, value in os.environ.items() if not key.startswith("ASAN_")}
        environment["ASAN_AGENT_POLICY_STATE_ROOT"] = str(self.fixture.state)
        listed = subprocess.run(lookup, cwd=self.root / "src", env=environment, text=True, capture_output=True, check=True)
        self.assertEqual({v["call"] for v in json.loads(listed.stdout)["writes"]},
                         {"denied-before-execution", "still-waiting"})
        response = self.hook("write-denied", {**denied, "hook_event_name": "PermissionDenied",
                                             "reason": "Classifier unavailable"})
        self.fixture.assert_allowed(response)
        self.assertNotIn("retry", response.stdout)
        # 중복/늦은 실패 callback도 후속 정상 저장을 unconfirmed로 되돌리지 않는다.
        self.fixture.assert_allowed(self.hook("post-tool", {**denied, "hook_event_name": "PostToolUseFailure",
                                                            "error": "denied before execution"}))
        writes = list(self.fixture.state.glob("repositories/*/branch-relations/v1/writes/*.json"))
        self.assertEqual([json.loads(p.read_text())["call"] for p in writes], ["still-waiting"])
        self.assertNotEqual(self.runner().returncode, 0)
        self.fixture.assert_allowed(self.hook("write-denied", {**waiting, "hook_event_name": "PermissionDenied"}))
        self.assertEqual(self.runner().returncode, 0)
        self.assertEqual(path.read_text(), "export const n = { value: 2 };\n")

    def test_permission_denial_restores_previous_writer_without_marking_new_file_successful(self):
        path = self.write("src/previous.ts", "export const n={value:1};\n")
        for target in (path, self.root / "src/never-created.ts"):
            denied = {"tool_name": "Write", "tool_call_id": "denied-" + target.name,
                      "tool_input": {"file_path": str(target), "content": "never written"}}
            self.fixture.assert_allowed(self.hook("pre-tool", denied))
            self.fixture.assert_allowed(self.hook("write-denied", {**denied, "hook_event_name": "PermissionDenied"}))
        self.assertEqual(self.runner().returncode, 0)
        self.assertFalse((self.root / "src/never-created.ts").exists())
        self.assertEqual(path.read_text(), "export const n = { value: 1 };\n")

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

    def runner(self, host="claude", root=None, path=None):
        args = [sys.executable, "-I", str(self.fixture.guard.with_name("formatting.py")), "apply",
                "--host", host, "--session", f"{host}-session"]
        env = {key: value for key, value in os.environ.items() if not key.startswith("ASAN_")}
        env.update(self.env, ASAN_AGENT_POLICY_STATE_ROOT=str(self.fixture.state))
        if path:
            env["PATH"] = path
        return subprocess.run(args, cwd=root or self.root, env=env, text=True, capture_output=True)

    def test_formatter_git_queries_do_not_grow_with_the_file_count(self):
        # 실제 orchest 세션: Stop 자동 포맷이 파일마다 Git을 여러 번 조회하며 events.lock을 쥐어
        # (36개 파일, 최대 17초) 하위 에이전트의 hook이 제한 시간을 넘겼다.
        shim = self.fixture.base / "git-shim"
        shim.mkdir()
        log = shim / "calls.log"
        (shim / "git").write_text(f"#!/bin/sh\nprintf '%s\\n' \"$*\" >> {shlex.quote(str(log))}\n"
                                  f"exec {shlex.quote(shutil.which('git'))} \"$@\"\n")
        (shim / "git").chmod(0o755)
        path = f"{shim}{os.pathsep}{os.environ['PATH']}"
        counts = []
        # 이전 포맷 완료 기록이 있으면 HEAD를 한 번 더 조회한다. 두 측정 모두 같은 조건에서 시작한다.
        self.write("src/count-warm.ts", "export const warm={value:0};\n")
        self.assertEqual(self.runner().returncode, 0)
        for files in (1, 4):
            for index in range(files):
                self.write(f"src/count-{files}-{index}.ts", f"export const n={{value:{index}}};\n")
            log.write_text("")
            result = self.runner(path=path)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(len(json.loads(result.stdout)["formatted"]), files, result.stdout)
            counts.append(len(log.read_text().splitlines()))
        self.assertEqual(counts[0], counts[1], counts)

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

    def test_conflicted_merge_defers_formatting_until_the_merge_commit(self):
        # user-ui의 origin/dev 병합에서 충돌 파일이 index에 올라 있어 포맷이 거부됐고,
        # 포맷 기록을 요구하는 검증·stage·commit과 Stop이 모두 막혀 사용자가 직접 실행해야 했다.
        git = self.fixture.git
        git("switch", "-qc", "incoming")
        (self.root / "src/app.ts").write_text("export const value = 2;\n")
        git("commit", "-qam", "incoming")
        git("switch", "-q", "sy-main")
        (self.root / "src/app.ts").write_text("export const value = 3;\n")
        git("commit", "-qam", "ours")
        merge = subprocess.run(["git", "merge", "incoming"], cwd=self.root, text=True, capture_output=True)
        self.assertNotEqual(merge.returncode, 0, "충돌하는 병합이어야 합니다.")
        resolved = "export const value={merged:1};\n"
        path = self.write("src/app.ts", resolved)

        def output(result):
            return result.stdout + result.stderr

        validation = {"tool_name": "Bash", "tool_call_id": "merge-lint", "tool_input": {"command": "npm run lint"}}
        self.fixture.assert_allowed(self.hook("pre-tool", validation))
        self.fixture.assert_allowed(self.hook("post-tool", {**validation, "tool_response": {"exit_code": 0}}))
        staging = output(self.hook("pre-tool", {"tool_name": "Bash", "tool_input": {"command": "git add -- src/app.ts"}}))
        self.assertNotIn("Prettier 적용이 확인되지 않은", staging)
        self.assertNotIn("stage된", staging)
        self.assertIn("보호 실행", staging)
        stop = self.hook("format-stop", {})
        self.fixture.assert_allowed(stop)
        self.assertNotIn('"block"', stop.stdout)
        explicit = self.runner()
        self.assertNotEqual(explicit.returncode, 0)
        self.assertIn("병합 commit 뒤", explicit.stderr)
        self.assertEqual(path.read_text(), resolved, "병합 중에는 파일을 다시 쓰지 않습니다.")

        git("add", "--", "src/app.ts")
        git("commit", "-qm", "merge")
        # 병합이 끝나면 미뤄 둔 포맷이 평소처럼 적용되고 다시 요구된다.
        commit = output(self.hook("pre-tool", {"tool_name": "Bash", "tool_input": {"command": "git commit --allow-empty -m next"}}))
        self.assertIn("Prettier 적용이 확인되지 않은", commit)
        applied = self.runner()
        self.assertEqual(applied.returncode, 0, applied.stderr)
        self.assertEqual(path.read_text(), "export const value = { merged: 1 };\n")

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
        first = self.hook("format-stop", {})
        self.assertEqual(json.loads(first.stdout)["decision"], "block")
        repeated = self.hook("format-stop", {"stop_hook_active": True})
        self.fixture.assert_allowed(repeated)
        self.assertNotIn('"block"', repeated.stdout)
        self.assertIn("심볼릭 링크", repeated.stdout)

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

    def test_recovered_call_stays_resolved_after_another_session_edits_and_commits(self):
        self.test_recovered_unknown_write_can_be_finished_by_a_successful_edit()
        self.write("src/unconfirmed.ts", "export const value={n:4};\n", session="next-session")
        validation = {"session_id": "next-session", "tool_call_id": "next-validation",
                      "tool_name": "Bash", "tool_input": {"command": "npm run lint"}}
        self.fixture.assert_allowed(self.hook("pre-tool", validation))
        self.hook("post-tool", {**validation, "tool_response": {"exit_code": 0}})
        self.fixture.git("add", "--", "src/unconfirmed.ts")
        self.fixture.git("commit", "-qm", "next session change")
        owned = self.write("src/msw.ts", "export const msw={enabled:true};\n")
        result = self.runner()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(owned.read_text(), "export const msw = { enabled: true };\n")

    def test_stop_persists_recovery_evidence_for_legacy_calls_even_without_pending_files(self):
        self.test_recovered_unknown_write_can_be_finished_by_a_successful_edit()
        legacy = next(self.fixture.state.glob("repositories/*/formatting/v1/calls/*.json"))
        value = json.loads(legacy.read_text())
        for item in value["files"]:
            item.pop("resolved_by", None)
        legacy.write_text(json.dumps(value))
        self.fixture.assert_allowed(self.hook("format-stop", {}))
        self.assertTrue(all(item.get("resolved_by") for item in json.loads(legacy.read_text())["files"]))

    def test_stop_runs_formatter_without_a_validation_command(self):
        for host in ("codex", "claude", "opencode"):
            with self.subTest(host=host):
                path = self.write(f"src/stop-{host}.ts", "export const value={n:1};\n", host=host)
                linked = self.write(f"src/stop-linked-{host}.ts", "export const linked={n:2};\n", host=host, root=self.worktree)
                result = self.hook("format-stop", {}, host=host)
                self.fixture.assert_allowed(result)
                self.assertNotIn('"block"', result.stdout)
                self.assertEqual(path.read_text(), "export const value = { n: 1 };\n")
                self.assertEqual(linked.read_text(), "export const linked = { n: 2 };\n")

    def test_stop_names_the_blocking_reservation_and_still_formats_other_worktrees(self):
        # 실제 user-ui orchest 세션: 기록이 없는 에이전트의 Bash 예약이 한 worktree에 남아 Stop 자동 포맷이
        # 매 턴 같은 오류로 멈췄다. 오류에 예약이 없어 원인을 찾기 어려웠고, 다른 worktree의 포맷도 함께 멈췄다.
        blocked = self.write("src/blocked.ts", "export const blocked={value:1};\n")
        linked = self.write("src/linked.ts", "export const linked={value:2};\n", root=self.worktree)
        ghost = {"tool_name": "Bash", "tool_call_id": "ghost-call", "agent_id": "ghost-agent",
                 "tool_input": {"command": "node --version"}}
        self.fixture.assert_allowed(self.hook("pre-tool", ghost))
        [reservation] = list(self.fixture.state.glob("repositories/*/branch-relations/v1/writes/*.json"))
        self.assertEqual(json.loads(reservation.read_text())["worktree"], str(self.root.resolve()))
        stopped = self.hook("format-stop", {})
        reason = json.loads(stopped.stdout)["reason"]
        for expected in (reservation.stem, "ghost-agent", "ghost-call", "write-recovery"):
            self.assertIn(expected, reason)
        self.assertEqual(blocked.read_text(), "export const blocked={value:1};\n")
        self.assertEqual(linked.read_text(), "export const linked = { value: 2 };\n")

    def test_reservation_of_an_agent_without_a_transcript_is_released_after_a_minute(self):
        # 10-23 user-ui, 10-27 admin-ui: 부모 Stop 2초 뒤 대화 기록이 없는 에이전트의 호출이 예약을 남겼다.
        # SubagentStop이 오지 않아 해소되지 않았고 Stop 자동 포맷이 매 턴 막혔다.
        transcript = self.fixture.base / "claude-projects" / "parent-session.jsonl"
        (transcript.with_suffix("") / "subagents").mkdir(parents=True)
        transcript.write_text("{}\n")
        (transcript.with_suffix("") / "subagents/agent-live-agent.jsonl").write_text("{}\n")
        pending = self.write("src/pending.ts", "export const pending={value:1};\n")
        writes = self.fixture.state.glob("repositories/*/branch-relations/v1/writes/*.json")
        for agent in ("ghost-agent", "live-agent"):
            self.fixture.assert_allowed(self.hook("pre-tool", {"tool_name": "Bash", "tool_call_id": agent + "-call",
                "agent_id": agent, "agent_type": "general-purpose", "transcript_path": str(transcript),
                "tool_input": {"command": "node --version"}}))
        records = {json.loads(path.read_text())["agent"]: path for path in writes}
        ghost = json.loads(records["ghost-agent"].read_text())
        self.assertEqual((ghost["tool"], ghost["command"], ghost["agent_type"], ghost["transcript"]),
                         ("Bash", "node --version", "general-purpose", str(transcript)))
        # 1분이 지나지 않은 예약과 대화 기록이 있는 에이전트의 예약은 그대로 막는다.
        self.assertIn("ghost-agent", json.loads(self.hook("format-stop", {"transcript_path": str(transcript)}).stdout)["reason"])
        for path in records.values():
            path.write_text(json.dumps({**json.loads(path.read_text()), "created_at": time.time() - 120}))
        reason = json.loads(self.hook("format-stop", {"transcript_path": str(transcript)}).stdout)["reason"]
        self.assertIn("live-agent", reason)
        self.assertNotIn("ghost-agent", reason)
        self.assertFalse(records["ghost-agent"].exists())
        [receipt] = [json.loads(path.read_text()) for path in
                     self.fixture.state.glob("repositories/*/branch-relations/v1/write-receipts/*.json")]
        self.assertEqual((receipt["outcome"], receipt["call"]), ("agent-transcript-missing", "ghost-agent-call"))
        records["live-agent"].unlink()
        self.hook("format-stop", {"transcript_path": str(transcript)})
        self.assertEqual(pending.read_text(), "export const pending = { value: 1 };\n")

    def test_duplicate_patch_targets_have_one_unknown_diagnostic_and_known_failure_releases_them(self):
        path = self.write("src/duplicate.ts", "export const value={n:1};\n", host="codex")
        event = {"tool_name": "apply_patch", "tool_call_id": "duplicate-patch", "tool_input": {"command":
            f"*** Begin Patch\n*** Update File: {path}\n@@\n-a\n+b\n*** Update File: {path}\n@@\n-b\n+c\n*** End Patch"}}
        self.fixture.assert_allowed(self.hook("pre-tool", event, host="codex"))
        stopped = self.hook("format-stop", {}, host="codex")
        self.assertEqual(json.loads(stopped.stdout)["reason"].count(str(path)), 1)
        self.hook("post-tool", {**event, "tool_response":
            "apply_patch verification failed: invalid patch: multiple operations target the same file"}, host="codex")
        result = self.runner("codex")
        self.assertEqual(result.returncode, 0, result.stderr)

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
                env = {key: value for key, value in os.environ.items()
                       if not key.startswith("ASAN_") and key != "CODEX_THREAD_ID"}
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
