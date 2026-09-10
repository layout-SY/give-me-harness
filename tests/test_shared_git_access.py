"""V4 계약: 브랜치 권한 대신 사용자 Git 승인과 세션 기록 보호.

V3의 의도적인 차단 사례는 기존 테스트에서 보존한다. 이 모듈은 실제 최신
렌더 결과를 세 host와 독립 worktree에 적용해 새 허용/차단 경계를 검증한다.
"""
from __future__ import annotations

import hashlib
import json
import os
import shlex
from dataclasses import replace
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from agent_policy.core import load_project, render_project
from agent_policy.injection import prepare_injection


class SharedGitAccessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / "repo"
        self.root.mkdir()
        self.git("init", "-q", "-b", "sy-main")
        self.git("config", "user.name", "Policy Test")
        self.git("config", "user.email", "policy@example.test")
        (self.root / "src").mkdir()
        (self.root / "src/app.ts").write_text("export const value = 1;\n")
        self.git("add", "--", "src")
        self.git("commit", "-qm", "baseline")
        self.worktree = self.base / "other-worktree"
        self.git("worktree", "add", "-qb", "existing-without-contract", str(self.worktree))
        self.bundle = self.base / "bundle"
        for name, content in render_project(replace(load_project("user-ui"), path=self.root)).items():
            if name.startswith((".agent-policy/runtime/", ".agent-policy/common/contracts/")):
                path = self.bundle / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
        self.guard = self.bundle / ".agent-policy/runtime/managed_policy_guard.py"
        self.state = self.base / "state"
        self.call = 0

    def git(self, *args, root=None):
        return subprocess.check_output(["git", *args], cwd=root or self.root, text=True).strip()

    def run_event(self, host, mode, event, *, role="logic"):
        self.call += 1
        env = {k: v for k, v in os.environ.items() if not k.startswith("ASAN_")}
        env.update(ASAN_AGENT_POLICY_ROLE=role, ASAN_AGENT_POLICY_STATE_ROOT=str(self.state),
                   ASAN_SESSION_DIR=f".{host}/logs/sessions/shared-session",
                   ASAN_AGENT_POLICY_TASK="task/old-closed-task")
        result = subprocess.run([sys.executable, "-I", str(self.guard), mode, host],
            cwd=self.root, env=env, text=True, capture_output=True,
            input=json.dumps({"cwd": str(self.root), "session_id": f"{host}-session",
                              "tool_call_id": f"call-{self.call}", **event}))
        return result

    def pre(self, host, command, *, workdir=None, role="logic"):
        result = self.run_event(host, "pre-tool", {"tool_name": "Bash", "tool_input": {
            "command": command, "workdir": str(workdir or self.root)}}, role=role)
        # Native raw commands are now redirected to the actual execution lock.
        # Follow the emitted exact command, as a consumer agent does; the raw
        # denial itself is covered separately in test_relation_operations.
        output = result.stdout + result.stderr
        if result.stdout.startswith("{"):
            output = json.loads(result.stdout).get("hookSpecificOutput", {}).get("permissionDecisionReason", output)
        if "보호 실행: " in output:
            protected = output.split("보호 실행: ", 1)[1].strip()
            return self.run_event(host, "pre-tool", {"tool_name": "Bash", "tool_input": {
                "command": protected, "workdir": str(workdir or self.root)}}, role=role)
        return result

    def assert_allowed(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('"deny"', result.stdout, result.stdout)
        self.assertNotIn('"ask"', result.stdout, result.stdout)

    def assert_asks(self, result, host):
        output = result.stdout + result.stderr
        self.assertIn("승인", output, output)
        self.assertNotIn("소유자가 다른", output)
        self.assertNotIn("V3 계약", output)
        self.assertNotIn("구현 gate", output)
        self.assertNotIn("사용자 전용", output)
        if host == "claude":
            self.assertIn('"ask"', output)
        else:
            self.assertTrue(result.returncode != 0 or '"deny"' in output)

    def test_all_hosts_ask_for_git_on_any_worktree_without_contract_or_readiness(self):
        common = Path(self.git("rev-parse", "--absolute-git-dir"))
        repository = self.state / "repositories" / hashlib.sha256(str(common).encode()).hexdigest()
        claims = repository / "claims"
        claims.mkdir(parents=True)
        resource = "git:" + str(self.worktree.resolve())
        claim = claims / (hashlib.sha256(resource.encode()).hexdigest() + ".json")
        claim.write_text(json.dumps({"resource": resource, "owner": "retired-assignment"}))
        self.git("config", "branch.existing-without-contract.asan-state", "CLOSED")
        for host in ("codex", "claude", "opencode"):
            for location in (self.root, self.worktree):
                with self.subTest(host=host, location=location):
                    self.assert_asks(self.pre(host, "git commit -m '승인 대상'", workdir=location, role="review"), host)
        self.assertEqual(json.loads(claim.read_text())["owner"], "retired-assignment")

    def test_reads_and_local_validation_do_not_ask(self):
        for host in ("codex", "claude", "opencode"):
            for command in ("git status --short", "git branch --list", "git worktree list",
                            "git log -1", "git config --get user.name", "git config user.name",
                            "git config --show-origin user.name", "npm run lint",
                            "npm run test", "npm run build"):
                with self.subTest(host=host, command=command):
                    self.assert_allowed(self.pre(host, command, workdir=self.worktree))

    def test_creation_merge_and_former_user_only_commands_ask(self):
        for command in ("git switch -c plain-branch", "git branch -d old",
                        "git worktree add /tmp/new-worktree", "git push origin HEAD",
                        "git clean -fd", "git fetch origin",
                        "git restore -- src/app.ts", "git stash push", "git config user.name Name"):
            with self.subTest(command=command):
                self.assert_asks(self.pre("claude", command), "claude")

    def test_codex_batch_approval_is_single_use_and_bound_to_worktree(self):
        command = "git add -- src/app.ts && git commit -m '작업 단위'"
        self.assert_asks(self.pre("codex", command, workdir=self.worktree), "codex")
        self.run_event("codex", "user-prompt", {"prompt": "명령 실행 승인"})
        self.assert_allowed(self.pre("codex", command, workdir=self.worktree))
        self.assert_asks(self.pre("codex", command, workdir=self.worktree), "codex")
        self.run_event("codex", "user-prompt", {"prompt": "명령 실행 승인"})
        self.assert_asks(self.pre("codex", command, workdir=self.root), "codex")

    def test_source_approval_survives_worktree_switch_but_other_host_artifacts_are_read_only(self):
        for host in ("codex", "claude", "opencode"):
            for tool, arg in (("Skill", {"skill": "policy"}), ("Read", {"file_path": "src/app.ts"})):
                self.run_event(host, "post-tool", {"tool_name": tool, "tool_input": arg,
                                                     "tool_response": {"success": True}})
            self.run_event(host, "user-prompt", {"prompt": "진행"})
            self.assert_allowed(self.run_event(host, "pre-tool", {"tool_name": "Edit", "tool_input": {
                "file_path": str(self.worktree / "src/app.ts"), "old_string": "1", "new_string": "2"}}))
            other = "claude" if host != "claude" else "codex"
            denied = self.run_event(host, "pre-tool", {"tool_name": "Write", "tool_input": {
                "file_path": str(self.worktree / f".{other}/logs/sessions/someone/handoff.md"), "content": "변경"}})
            self.assertIn("읽기 전용", denied.stdout + denied.stderr)

    def test_unknown_existing_branch_needs_relation_only_for_completion(self):
        log = self.worktree / ".claude/logs/sessions/child-session/handoff.md"
        log.parent.mkdir(parents=True)
        log.write_text("자식 담당자의 실제 인계 기록\n")
        (self.worktree / "src/app.ts").write_text("export const value = 2;\n")
        self.git("add", "--", "src/app.ts", ".claude", root=self.worktree)
        self.git("commit", "-qm", "child", root=self.worktree)
        source = self.git("rev-parse", "HEAD", root=self.worktree)
        command = "git merge --ff-only existing-without-contract"
        denied = self.pre("codex", command)
        self.assertIn("직접 부모 관계", denied.stdout + denied.stderr)
        self.assert_allowed(self.pre("codex", "git status", workdir=self.worktree))
        self.assert_asks(self.pre("codex", "git commit --allow-empty -m next", workdir=self.worktree), "codex")
        self.assertEqual(self.git("rev-parse", "HEAD", root=self.worktree), source)
        self.assertFalse(list(self.state.glob("repositories/*/claims/*.json")))

    def test_state_change_revokes_pending_git_approval_without_affecting_source_approval(self):
        command = "git add -- src/app.ts && git commit -m 'reviewed'"
        self.assert_asks(self.pre("codex", command), "codex")
        self.run_event("codex", "user-prompt", {"prompt": "명령 실행 승인"})
        (self.root / "src/app.ts").write_text("export const value = 999;\n")
        self.assert_asks(self.pre("codex", command), "codex")

    def test_unrelated_host_log_change_does_not_require_reapproval(self):
        command = "git add -- src/app.ts && git commit -m 'source only'"
        (self.root / "src/app.ts").write_text("export const value = 2;\n")
        log = self.root / ".claude/logs/sessions/other/handoff.md"
        log.parent.mkdir(parents=True)
        log.write_text("다른 작업 진행 중\n")
        self.assert_asks(self.pre("codex", command), "codex")
        self.run_event("codex", "user-prompt", {"prompt": "명령 실행 승인"})
        log.write_text("다른 작업 진행 내용 추가\n")
        self.assert_allowed(self.pre("codex", command))

    def test_write_flags_on_read_commands_need_approval_and_cannot_overwrite_foreign_logs(self):
        self.assert_asks(self.pre("claude", "git fsck --lost-found"), "claude")
        self.assert_asks(self.pre("claude", "git config --show-origin user.name changed"), "claude")
        denied = self.pre("codex", "git diff --output=.claude/logs/sessions/other/handoff.md")
        self.assertIn("읽기 전용", denied.stdout + denied.stderr)

    def test_other_host_dirty_log_does_not_block_source_stage_but_cannot_be_staged(self):
        path = self.root / ".claude/logs/sessions/another/handoff.md"
        path.parent.mkdir(parents=True)
        path.write_text("다른 host의 미커밋 기록\n")
        (self.root / "src/app.ts").write_text("export const value = 2;\n")
        self.assert_asks(self.pre("codex", "git add -- src/app.ts"), "codex")
        denied = self.pre("codex", "git add -- .")
        self.assertIn("읽기 전용", denied.stdout + denied.stderr)

    def test_own_session_directory_can_be_staged_and_scoped_reset_ignores_foreign_logs(self):
        own = self.root / ".codex/logs/sessions/shared-session/final-summary.md"
        own.parent.mkdir(parents=True)
        own.write_text("자기 결과 기록\n")
        self.assert_asks(self.pre("codex", "git add -- .codex/logs/sessions/shared-session"), "codex")
        other = self.root / ".claude/logs/sessions/other/handoff.md"
        other.parent.mkdir(parents=True)
        other.write_text("다른 세션 기록\n")
        self.assert_asks(self.pre("codex", "git reset HEAD -- src/app.ts"), "codex")
        self.assert_asks(self.pre("codex", "git clean -fd -- src"), "codex")

    def test_retired_workflow_wrapper_cannot_avoid_git_approval(self):
        result = self.pre("codex", "python3 /tmp/old/skills/policy/git-branch-strategy/scripts/branch_workflow.py finish")
        self.assertIn("workflow", result.stdout + result.stderr)
        self.assertTrue(result.returncode != 0 or '"deny"' in result.stdout)

    def test_own_log_can_follow_worktrees_without_changing_other_session_records(self):
        for target in (self.root, self.worktree):
            event = {"tool_name": "Write", "tool_input": {"file_path": str(
                target / ".codex/logs/sessions/shared-session/final-summary.md"), "content": "실제 결과 기록"}}
            self.assert_allowed(self.run_event("codex", "pre-tool", event))
        other = self.run_event("codex", "pre-tool", {"tool_name": "Write", "tool_input": {
            "file_path": str(self.worktree / ".codex/logs/sessions/another/final-summary.md"), "content": "변경"}})
        self.assertIn("읽기 전용", other.stdout + other.stderr)

    def test_logging_in_another_worktree_keeps_the_approved_plan(self):
        def write_log(target, name, call):
            path = target / ".codex/logs/sessions/shared-session" / name
            event = {"tool_name": "Write", "tool_call_id": call,
                     "tool_input": {"file_path": str(path), "content": "현재 작업의 실제 기록"}}
            self.assert_allowed(self.run_event("codex", "pre-tool", event))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("현재 작업의 실제 기록\n")
            self.run_event("codex", "post-tool", {**event, "tool_response": {"success": True}})
        write_log(self.root, "plan.md", "plan-write")
        for tool, data in (("Skill", {"skill": "policy"}), ("Read", {"file_path": "src/app.ts"})):
            self.run_event("codex", "post-tool", {"tool_name": tool, "tool_input": data,
                "tool_response": {"success": True}})
        self.run_event("codex", "user-prompt", {"prompt": "진행"})
        write_log(self.worktree, "final-summary.md", "other-log")
        self.assert_allowed(self.run_event("codex", "pre-tool", {"tool_name": "Edit", "tool_input": {
            "file_path": str(self.worktree / "src/app.ts"), "old_string": "1", "new_string": "2"}}))

    def test_read_options_that_write_and_opencode_approval_are_not_bypasses(self):
        command = "git diff --output=report.txt"
        self.assert_asks(self.pre("opencode", command), "opencode")
        self.run_event("opencode", "user-prompt", {"prompt": "명령 실행 승인"})
        self.assert_allowed(self.pre("opencode", command))
        self.assert_asks(self.pre("opencode", command), "opencode")

    def test_other_repository_and_direct_git_file_edits_stay_protected(self):
        denied = self.run_event("codex", "pre-tool", {"tool_name": "Write", "tool_input": {
            "file_path": str(self.root / ".git/config"), "content": "overwrite"}})
        self.assertTrue(denied.returncode != 0 or '"deny"' in denied.stdout)
        elsewhere = self.base / "elsewhere"
        elsewhere.mkdir()
        self.git("init", "-q", root=elsewhere)
        denied = self.pre("codex", f"git -C {elsewhere} commit -m unrelated")
        self.assertIn("다른 Git 저장소", denied.stdout + denied.stderr)

    def test_real_inject_hook_paths_use_shared_access_for_all_hosts(self):
        project = replace(load_project("user-ui"), path=self.root)
        fake_home = self.base / "source-codex-home"
        fake_home.mkdir()
        (fake_home / "config.toml").write_text("")
        self.git("branch", "feature", "sy-main")
        self.git("branch", "child", "feature")
        for host in ("codex", "claude", "opencode"):
            with self.subTest(host=host):
                launch = prepare_injection(project, host, "logic", build_root=self.base / "launch-build",
                    state_root=self.base / "launch-state", source_codex_home=fake_home, task="새 작업 설명")
                if host == "codex":
                    hooks = json.loads((Path(launch.environment["CODEX_HOME"]) / "hooks.json").read_text())["hooks"]
                    command = shlex.split(hooks["PreToolUse"][0]["hooks"][0]["command"])
                elif host == "claude":
                    hooks = json.loads((launch.bundle_root / "plugin/hooks/hooks.json").read_text())["hooks"]
                    command = shlex.split(hooks["PreToolUse"][0]["hooks"][0]["command"])
                else:
                    runtime = launch.bundle_root / "opencode-home/runtime/managed_policy_guard.py"
                    command = [sys.executable, "-I", str(runtime), "pre-tool", host]
                    plugin = (launch.bundle_root / "opencode-home/plugins/agent-policy.js").read_text()
                    self.assertIn(str(runtime), plugin)
                common = Path(self.git("rev-parse", "--absolute-git-dir")).resolve()
                directory = Path(launch.environment["ASAN_AGENT_POLICY_STATE_ROOT"]) / "repositories" / hashlib.sha256(str(common).encode()).hexdigest() / "branch-relations/v1"
                directory.mkdir(parents=True, exist_ok=True)
                head = self.git("rev-parse", "HEAD")
                nodes = {name: {"id": name, "name": name, "parent": parent, "fork_commit": head,
                    "purpose": "native test", "revision": 1, "deleted": False, "resolution": None}
                    for name, parent in (("sy-main", None), ("feature", "sy-main"), ("child", "feature"))}
                (directory / "graph.json").write_text(json.dumps({"version": 1, "revision": 1, "nodes": nodes}))
                event = {"cwd": str(self.root), "session_id": f"native-{host}",
                         "tool_name": "exec_command" if host == "codex" else "bash",
                         "tool_input": {"cmd" if host == "codex" else "command": "git commit --allow-empty -m native",
                                        "workdir": str(self.root)}}
                env = {k: v for k, v in os.environ.items() if not k.startswith("ASAN_")}
                invalid = json.loads(json.dumps(event))
                invalid["tool_input"]["cmd" if host == "codex" else "command"] = "git merge --ff-only child"
                denied = subprocess.run(command, input=json.dumps(invalid), cwd=self.root,
                    env={**env, **launch.environment}, text=True, capture_output=True)
                self.assertIn("직접 부모", denied.stdout + denied.stderr)
                result = subprocess.run(command, input=json.dumps(event), cwd=self.root,
                    env={**env, **launch.environment}, text=True, capture_output=True)
                output = result.stdout + result.stderr
                if result.stdout.startswith("{"):
                    output = json.loads(result.stdout)["hookSpecificOutput"]["permissionDecisionReason"]
                self.assertIn("보호 실행: ", output)
                event["tool_input"]["cmd" if host == "codex" else "command"] = output.split("보호 실행: ", 1)[1].strip()
                result = subprocess.run(command, input=json.dumps(event), cwd=self.root,
                    env={**env, **launch.environment}, text=True, capture_output=True)
                self.assert_asks(result, host)
                if host != "claude":
                    approved = subprocess.run([*command[:-2], "user-prompt", host],
                        input=json.dumps({"cwd": str(self.root), "session_id": f"native-{host}", "prompt": "명령 실행 승인"}),
                        cwd=self.root, env={**env, **launch.environment}, text=True, capture_output=True)
                    self.assertEqual(approved.returncode, 0, approved.stderr)
                    allowed = subprocess.run(command, input=json.dumps(event), cwd=self.root,
                        env={**env, **launch.environment}, text=True, capture_output=True)
                    self.assert_allowed(allowed)
                # Simulate acceptance of Claude's native ask; other hosts consumed
                # the explicit prompt above. Execute the actual bundled runner.
                executed = subprocess.run(shlex.split(event["tool_input"]["cmd" if host == "codex" else "command"]),
                    cwd=self.root, env={**env, **launch.environment}, text=True, capture_output=True)
                self.assertEqual(executed.returncode, 0, executed.stderr)
                self.assertEqual(self.git("log", "-1", "--format=%s"), "native")

    def test_project_boundary_precedes_read_and_mutation_approval_for_all_hosts(self):
        other = self.base / "admin-ui"
        other.mkdir()
        self.git("init", "-q", root=other)
        alias = self.root / "admin-link"
        alias.symlink_to(other, target_is_directory=True)
        for host in ("codex", "claude", "opencode"):
            for command, cwd in (
                ("git status --short", other), ("npm run build", other),
                (f"git -C {other} status", self.root),
                (f"git -C {other} commit -m unrelated", self.root),
                (f"cd {other} && git status", self.root),
                (f"cd {other}\ngit commit -m unrelated", self.root),
                (f"npm --prefix {other} run build", self.root),
                (f"pnpm -C {other} test", self.root),
                (f"yarn --cwd={other} build", self.root),
                (f"env -C {other} git status", self.root),
                (f"sh -c 'cd {other} && pwd'", self.root),
                (f"git -C {alias} status", self.root),
                (f"git --git-dir={other}/.git --work-tree={other} status", self.root),
                (f"GIT_DIR={other}/.git git status", self.root),
                (f"git diff --output={other}/report.txt", self.root),
                (f"git config --file={other}/.git/config user.name Changed", self.root),
                (f"git worktree add {other}/nested", self.root),
                (f"git push {other} HEAD", self.root),
                (f"git clone {other} {self.base}/clone", self.root),
                (f"git init {other}", self.root),
                ("git config --global user.name Changed", self.root),
            ):
                with self.subTest(host=host, command=command, cwd=cwd):
                    result = self.pre(host, command, workdir=cwd)
                    output = result.stdout + result.stderr
                    self.assertTrue(result.returncode != 0 or '"deny"' in output, output)
                    self.assertNotIn('"ask"', output, output)
                    self.assertIn("프로젝트", output, output)

    def test_event_cwd_cannot_rebind_the_injected_project(self):
        other = self.base / "admin-ui"
        other.mkdir()
        self.git("init", "-q", root=other)
        for host in ("codex", "claude", "opencode"):
            for command in ("git status", "git commit -m unrelated", "npm run lint"):
                result = self.run_event(host, "pre-tool", {"cwd": str(other),
                    "tool_name": "Bash", "tool_input": {"command": command}})
                output = result.stdout + result.stderr
                self.assertTrue(result.returncode != 0 or '"deny"' in output, output)
                self.assertNotIn('"ask"', output, output)
                self.assertIn("프로젝트", output, output)
            result = self.run_event(host, "pre-tool", {"cwd": str(other),
                "tool_name": "Write", "tool_input": {
                    "file_path": f".{host}/logs/sessions/shared-session/final-summary.md", "content": "잘못된 위치"}})
            self.assertIn("프로젝트", result.stdout + result.stderr)

    def test_same_project_directories_and_new_linked_worktrees_remain_available(self):
        for host in ("codex", "claude", "opencode"):
            for command in (f"git -C {self.worktree} status", f"cd {self.worktree} && git status",
                            f"npm --prefix {self.worktree} run build", f"env -C {self.worktree} git status",
                            f"cd {self.worktree}\ngit status\ngit log -1"):
                self.assert_allowed(self.pre(host, command))
            self.assert_asks(self.pre(host, f"git worktree add {self.base}/new-linked"), host)
        command = f"cd {self.worktree} && git add -- src/app.ts && git commit -m reviewed"
        self.assert_asks(self.pre("codex", command), "codex")
        self.run_event("codex", "user-prompt", {"prompt": "명령 실행 승인"})
        self.assert_allowed(self.pre("codex", command))

    def test_approval_cannot_override_project_boundary_or_changed_local_remote(self):
        other = self.base / "admin-ui"
        other.mkdir()
        self.git("init", "-q", root=other)
        self.git("remote", "add", "origin", "https://example.test/user-ui.git")
        command = "git push origin HEAD"
        self.assert_asks(self.pre("codex", command), "codex")
        self.run_event("codex", "user-prompt", {"prompt": "진행"})
        self.git("remote", "set-url", "origin", str(other))
        result = self.pre("codex", command)
        self.assertIn("프로젝트", result.stdout + result.stderr)
        self.assertNotIn("이 작업 단위", result.stdout + result.stderr)

    def test_nested_repository_alias_and_default_remote_cannot_cross_the_boundary(self):
        other = self.root / "admin-ui"
        other.mkdir()
        self.git("init", "-q", root=other)
        self.git("config", "alias.other-status", f"!git -C {other} status")
        self.git("remote", "add", "admin", str(other))
        self.git("config", "remote.pushDefault", "admin")
        for command in ("git other-status", "git push", "git push --repo=admin HEAD",
                        "git worktree add admin-ui/nested", "git -C admin-ui status",
                        "npm --prefix admin-ui run build"):
            result = self.pre("claude", command)
            self.assertEqual(result.returncode, 2, f"{command}: {result.stdout} {result.stderr}")
            self.assertNotIn('"ask"', result.stdout)
            self.assertIn("프로젝트", result.stderr)

    def test_native_project_binding_survives_foreign_event_cwd_for_both_projects(self):
        other = self.base / "foreign-project"
        other.mkdir()
        self.git("init", "-q", root=other)
        home = self.base / "native-home"
        home.mkdir()
        (home / "config.toml").write_text("")
        for project_id in ("user-ui", "admin-ui"):
            for host in ("codex", "claude", "opencode"):
                with self.subTest(project=project_id, host=host):
                    launch = prepare_injection(replace(load_project(project_id), path=self.root), host, "logic",
                        build_root=self.base / "native-build", state_root=self.base / "native-state", source_codex_home=home)
                    if host == "codex":
                        hooks = json.loads((Path(launch.environment["CODEX_HOME"]) / "hooks.json").read_text())["hooks"]
                        command = shlex.split(hooks["PreToolUse"][0]["hooks"][0]["command"])
                    elif host == "claude":
                        hooks = json.loads((launch.bundle_root / "plugin/hooks/hooks.json").read_text())["hooks"]
                        command = shlex.split(hooks["PreToolUse"][0]["hooks"][0]["command"])
                    else:
                        command = [sys.executable, "-I", str(launch.bundle_root / "opencode-home/runtime/managed_policy_guard.py"), "pre-tool", host]
                    env = {k: v for k, v in os.environ.items() if not k.startswith("ASAN_")}
                    for location, expected in ((self.worktree, "allow"), (other, "deny")):
                        event = {"cwd": str(location), "session_id": f"{project_id}-{host}", "tool_name": "bash",
                                 "tool_input": {"command": "git status"}}
                        result = subprocess.run(command, cwd=location, text=True, capture_output=True,
                            env={**env, **launch.environment, "ASAN_AGENT_POLICY_PROJECT_PATH": str(location)}, input=json.dumps(event))
                        if expected == "allow":
                            self.assert_allowed(result)
                        else:
                            output = result.stdout + result.stderr
                            self.assertTrue(result.returncode != 0 or '"deny"' in output, output)
                            self.assertNotIn('"ask"', output)
                            self.assertIn("프로젝트", output)


if __name__ == "__main__":
    unittest.main()
