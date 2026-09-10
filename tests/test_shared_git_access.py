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
        for name, content in render_project(load_project("user-ui")).items():
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
        return self.run_event(host, "pre-tool", {"tool_name": "Bash", "tool_input": {
            "command": command, "workdir": str(workdir or self.root)}}, role=role)

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
        for command in ("git switch -c plain-branch", "git branch -d old", "git merge --ff-only sy-main",
                        "git worktree add /tmp/new-worktree", "git push origin HEAD", "git reset --hard HEAD",
                        "git clean -fd", "git update-ref refs/heads/local HEAD", "git fetch origin",
                        "git restore -- src/app.ts", "git stash push", "git config user.name Name"):
            with self.subTest(command=command):
                self.assert_asks(self.pre("claude", command), "claude")

    def test_codex_batch_approval_is_single_use_and_bound_to_worktree(self):
        command = "git add -- src/app.ts && git commit -m '작업 단위'"
        self.assert_asks(self.pre("codex", command, workdir=self.worktree), "codex")
        self.run_event("codex", "user-prompt", {"prompt": "진행"})
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

    def test_approved_merge_really_transfers_child_and_committed_foreign_logs(self):
        log = self.worktree / ".claude/logs/sessions/child-session/handoff.md"
        log.parent.mkdir(parents=True)
        log.write_text("자식 담당자의 실제 인계 기록\n")
        (self.worktree / "src/app.ts").write_text("export const value = 2;\n")
        self.git("add", "--", "src/app.ts", ".claude", root=self.worktree)
        self.git("commit", "-qm", "child", root=self.worktree)
        source = self.git("rev-parse", "HEAD", root=self.worktree)
        command = "git merge --ff-only existing-without-contract"
        self.assert_asks(self.pre("codex", command), "codex")
        self.run_event("codex", "user-prompt", {"prompt": "진행"})
        self.assert_allowed(self.pre("codex", command))
        self.git("merge", "--ff-only", "existing-without-contract")
        self.assertEqual(self.git("rev-parse", "HEAD"), source)
        self.assertEqual((self.root / log.relative_to(self.worktree)).read_bytes(), log.read_bytes())
        self.assertEqual(self.git("status", "--porcelain"), "")
        self.assertFalse(list(self.state.glob("repositories/*/claims/*.json")))

    def test_state_change_revokes_pending_git_approval_without_affecting_source_approval(self):
        command = "git add -- src/app.ts && git commit -m 'reviewed'"
        self.assert_asks(self.pre("codex", command), "codex")
        self.run_event("codex", "user-prompt", {"prompt": "승인"})
        (self.root / "src/app.ts").write_text("export const value = 999;\n")
        self.assert_asks(self.pre("codex", command), "codex")

    def test_unrelated_host_log_change_does_not_require_reapproval(self):
        command = "git add -- src/app.ts && git commit -m 'source only'"
        (self.root / "src/app.ts").write_text("export const value = 2;\n")
        log = self.root / ".claude/logs/sessions/other/handoff.md"
        log.parent.mkdir(parents=True)
        log.write_text("다른 작업 진행 중\n")
        self.assert_asks(self.pre("codex", command), "codex")
        self.run_event("codex", "user-prompt", {"prompt": "진행"})
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
        self.run_event("opencode", "user-prompt", {"prompt": "진행"})
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
                event = {"cwd": str(self.root), "session_id": f"native-{host}",
                         "tool_name": "exec_command" if host == "codex" else "bash",
                         "tool_input": {"cmd" if host == "codex" else "command": "git merge --ff-only existing-without-contract",
                                        "workdir": str(self.root)}}
                env = {k: v for k, v in os.environ.items() if not k.startswith("ASAN_")}
                result = subprocess.run(command, input=json.dumps(event), cwd=self.root,
                    env={**env, **launch.environment}, text=True, capture_output=True)
                self.assert_asks(result, host)


if __name__ == "__main__":
    unittest.main()
