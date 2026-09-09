from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from agent_policy.core import CENTRAL_ROOT, ProjectConfig, render_project
from agent_policy.injection import prepare_injection
from agent_policy.cli import task_start_denial
from agent_policy.log_mirror import assignment_log_sources, collect_project_logs


class RuntimeFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name).resolve()
        self.root = self.directory / "repo"
        self.root.mkdir()
        self.git("init", "-q", "-b", "sy-main")
        self.git("config", "user.name", "Policy Test")
        self.git("config", "user.email", "policy@example.invalid")
        (self.root / "src").mkdir()
        (self.root / "src/App.tsx").write_text("export const App = () => null;\n")
        self.git("add", "src")
        self.git("commit", "-qm", "initial")
        self.project = ProjectConfig("user-ui", "test", self.root, {
            "dev": "npm run dev", "build": "npm run build", "lint": "npm run lint",
            "test": "git status --porcelain", "preview": "npm run preview",
        })
        self.rendered = render_project(self.project)
        self.snapshot = self.directory / "snapshot"
        for relative, content in self.rendered.items():
            path = self.snapshot / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        self.runtime = self.snapshot / ".agent-policy/runtime"
        self.guard = self.module(self.runtime / "managed_policy_guard.py")
        self.env = {
            "ASAN_AGENT_POLICY_MODE": "inject",
            "ASAN_AGENT_POLICY_PROJECT": self.project.id,
            "ASAN_AGENT_POLICY_PROJECT_PATH": str(self.root),
            "ASAN_AGENT_POLICY_BUNDLE_ROOT": str(self.snapshot),
            "ASAN_AGENT_POLICY_ROLE": "logic",
            "ASAN_AGENT_POLICY_STATE_ROOT": str(self.directory / "state"),
        }
        self.event = {"cwd": str(self.root), "session_id": self.directory.name}

    @staticmethod
    def module(path: Path) -> ModuleType:
        module = ModuleType(path.stem)
        module.__file__ = str(path)
        exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
        return module

    def git(self, *args: str, root: Path | None = None) -> str:
        return subprocess.run(["git", *args], cwd=root or self.root, check=True,
                              capture_output=True, text=True).stdout.strip()

    def hook(self, mode: str, host: str = "claude", **event: object) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, "-I", str(self.runtime / "managed_policy_guard.py"), mode, host],
                              input=json.dumps({**self.event, **event}), text=True,
                              capture_output=True, env={**os.environ, **self.env}, check=False)

    def state(self, host: str = "claude") -> dict:
        with patch.dict(os.environ, self.env):
            return self.guard.load_json_state(self.guard.harness_state_path(self.event, self.root, host))


class EventRegressionTests(RuntimeFixture):
    def test_central_snapshot_reads_are_allowed_but_writes_are_denied(self) -> None:
        target = self.snapshot / ".agent-policy/common/skills/policy/SKILL.md"
        for host in ("codex", "claude", "opencode"):
            with self.subTest(host=host):
                read = self.hook("pre-tool", host, tool_name="Read", tool_input={"file_path": str(target)})
                self.assertEqual(read.returncode, 0, read.stderr)
                self.assertNotIn('"deny"', read.stdout)
                write = self.hook("pre-tool", host, tool_name="Write", tool_input={"file_path": str(target)})
                self.assertTrue(write.returncode != 0 or '"deny"' in write.stdout)

    def test_failed_and_unknown_reads_cannot_supply_readiness(self) -> None:
        for host in ("codex", "claude", "opencode"):
            for result in ({"success": False, "exit_code": 1}, {}):
                with self.subTest(host=host, result=result):
                    self.hook("post-tool", host, tool_name="Read", tool_input={"file_path": "src/App.tsx"},
                              tool_response=result)
                    self.assertIsNot(self.state(host).get("exploration_completed"), True)
            self.hook("post-tool", host, tool_name="Read", tool_input={"file_path": "src/App.tsx"},
                      tool_response={"success": True, "content": "export const App = () => null;"})
            self.assertTrue(self.state(host).get("exploration_completed"))

    def test_question_and_compact_preserve_implementation_approval(self) -> None:
        for host in ("codex", "claude", "opencode"):
            with self.subTest(host=host):
                self.hook("user-prompt", host, prompt="proceed")
                self.hook("user-prompt", host, prompt="현재 진행 상황을 설명해줘")
                self.assertTrue(self.state(host).get("implementation_approved"))
                self.hook("session-start", host, source="compact")
                self.assertTrue(self.state(host).get("implementation_approved"))
                self.hook("user-prompt", host, prompt="구현 승인 취소")
                self.assertIsNot(self.state(host).get("implementation_approved"), True)

    def test_contract_approval_does_not_create_implementation_approval(self) -> None:
        self.hook("user-prompt", prompt="승인 " + "a" * 64)
        self.assertIsNot(self.state().get("implementation_approved"), True)

    def test_denied_write_does_not_bind_assignment(self) -> None:
        guard = self.guard.branch_guard
        branch = "task/denied-write"
        self.git("switch", "-qc", branch)
        contract = guard.canonical_contract(branch, "검사", "sy-main", self.git("rev-parse", "sy-main"),
                                            "sy-main", ("src",), "검사", "", ("logic",), "claude")
        digest = guard.contract_sha256(contract)
        for key, value in {"contract-version": "3", "task-id": "denied-write", "purpose": "검사",
                           "parent": "sy-main", "parent-head": self.git("rev-parse", "sy-main"),
                           "merge-target": "sy-main", "proposal": f"asan-v3:{digest}",
                           "contract-sha256": digest, "reason": "검사", "worktree": "",
                           "role": "logic", "scope": "src", "git-integrator": "claude", "state": "ACTIVE"}.items():
            self.git("config", f"branch.{branch}.asan-{key}", value)
        denied = self.hook("pre-tool", tool_name="Write", tool_input={"file_path": "src/App.tsx"})
        self.assertNotEqual(denied.returncode, 0)
        with patch.dict(os.environ, self.env):
            self.assertEqual(self.guard.session_binding_record(self.event, self.root, "claude"), {})


class InjectionRegressionTests(RuntimeFixture):
    def launch(self, role: str):
        return prepare_injection(self.project, "codex", role, build_root=self.directory / "build",
                                 state_root=self.directory / "state", source_codex_home=self.directory / "user-home")

    def test_same_project_sessions_have_independent_codex_homes(self) -> None:
        first = self.launch("logic")
        first_home = Path(first.environment["CODEX_HOME"])
        before = (first_home / "hooks.json").read_bytes()
        second = self.launch("review")
        self.assertNotEqual(first_home, Path(second.environment["CODEX_HOME"]))
        self.assertEqual((first_home / "hooks.json").read_bytes(), before)
        self.assertTrue((first_home / "agents/generator.toml").is_file())

    def test_every_owner_role_can_read_portfolio_skill(self) -> None:
        for role in ("logic", "ui", "orchest", "review", "generate"):
            with self.subTest(role=role):
                launch = self.launch(role)
                self.assertTrue((launch.bundle_root / "policy/.agent-policy/common/skills/policy/portfolio/SKILL.md").is_file())


class OpenCodeFailureTests(unittest.TestCase):
    def test_runtime_failures_block_pretool(self) -> None:
        plugin = CENTRAL_ROOT / "adapters/opencode/files/.opencode/plugins/agent-policy.js"
        script = r'''
import fs from "node:fs";
const source = fs.readFileSync(process.argv[1], "utf8").replace(
  /import .* from "node:child_process"/, "const { spawnSync, execFile } = globalThis.fakeProcess");
for (const [index, [status, stdout, expectedBlocked]] of [
  [0, '', false], [0, '{"decision":"allow"}', false], [0, '{}', true], [0, 'invalid-json', true],
  [1, '', true], [2, '', true], [null, '', true],
].entries()) {
  globalThis.fakeProcess = {
    spawnSync: () => ({status, stdout, stderr: status ? 'failure' : '', error: status === null ? new Error('timeout') : undefined}),
    execFile: (_file, _args, _opts, done) => {
      const child = {stdin: {end: () => {}}, kill: () => {}};
      queueMicrotask(() => done(status === 0 ? null : Object.assign(new Error('failure'), {code: status, killed: status === null}), stdout, ''));
      return child;
    }
  };
  const {AgentPolicyPlugin} = await import('data:text/javascript,' + encodeURIComponent(source) + '#' + index);
  const plugin = await AgentPolicyPlugin({directory: '/tmp', client: {app: {log: async () => {}}, tui: {showToast: async () => {}}}});
  let blocked = false;
  try { await plugin['tool.execute.before']({tool: 'write', sessionID: 'test'}, {args: {file_path: 'src/a'}}); }
  catch { blocked = true; }
  if (blocked !== expectedBlocked) throw new Error(`status=${status}, stdout=${stdout}, blocked=${blocked}`);
}
'''
        result = subprocess.run(["node", "--input-type=module", "-e", script, str(plugin)],
                                text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)


class WorkflowFixture(RuntimeFixture):
    def workflow(self, *args: str, root: Path | None = None):
        script = self.snapshot / ".agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py"
        return subprocess.run([sys.executable, "-I", str(script), *args], cwd=root or self.root,
                              text=True, capture_output=True, env={**os.environ, **self.env}, check=False)

    def proposal_args(self, output: str, finish: bool = False) -> tuple[str, ...]:
        label = "finish proposal" if finish else "canonical proposal"
        lines = output.splitlines()
        path = next(line.split(": ", 1)[1] for line in lines if line.startswith(f"- {label} 파일:"))
        sha = next(line.split(": ", 1)[1] for line in lines if line.startswith(f"- {label} SHA-256:"))
        return ("--proposal-file", path, "--proposal-sha256", sha)

    def create_task(self, name: str, worktree: Path | None = None) -> Path:
        args = ["proposal", "--branch", f"task/{name}", "--parent", "sy-main", "--purpose", name,
                "--scope", "src", "--reason", "회귀 검사", "--role", "logic", "--git-integrator", "claude"]
        if worktree:
            args += ["--worktree", str(worktree)]
        proposed = self.workflow(*args)
        self.assertEqual(proposed.returncode, 0, proposed.stderr)
        created = self.workflow("create", *self.proposal_args(proposed.stdout))
        self.assertEqual(created.returncode, 0, created.stderr)
        return worktree or self.root

    def commit(self, root: Path, name: str) -> None:
        (root / f"src/{name}.tsx").write_text(f"export const {name} = 1;\n")
        self.git("add", "src", root=root)
        self.git("commit", "-qm", name, root=root)



class LifecycleRegressionTests(WorkflowFixture):
    def test_finish_from_source_completes_single_worktree(self) -> None:
        root = self.create_task("single")
        self.commit(root, "single")
        proposed = self.workflow("finish-proposal", "--verify-command", self.project.commands["test"])
        self.assertEqual(proposed.returncode, 0, proposed.stderr)
        args = self.proposal_args(proposed.stdout, True)
        for action in ("finish", "verify", "close"):
            result = self.workflow(action, *args)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git("branch", "--show-current"), "sy-main")

    def test_divergent_siblings_merge_and_verify_recorded_integration_head(self) -> None:
        left = self.create_task("left", self.directory / "left")
        right = self.create_task("right", self.directory / "right")
        self.commit(left, "left")
        self.commit(right, "right")
        for index, root in enumerate((left, right)):
            proposed = self.workflow("finish-proposal", "--merge-strategy", "ff-only" if index == 0 else "merge-commit",
                                     "--verify-command", self.project.commands["test"], root=root)
            self.assertEqual(proposed.returncode, 0, proposed.stderr)
            args = self.proposal_args(proposed.stdout, True)
            for action in ("finish", "verify", "close"):
                result = self.workflow(action, *args, root=root)
                self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.root / "src/left.tsx").exists())
        self.assertTrue((self.root / "src/right.tsx").exists())
        self.assertNotEqual(self.git("rev-parse", "sy-main"), self.git("rev-parse", "task/right"))

    def test_preserved_start_is_diagnostic_until_explicit_resume(self) -> None:
        self.create_task("preserved")
        preserved = self.workflow("preserve", "--reason", "인계")
        self.assertEqual(preserved.returncode, 0, preserved.stderr)
        self.assertIsNone(task_start_denial(self.project))
        self.assertIsNotNone(self.guard.branch_guard.active_branch_denial(self.root, ("src/App.tsx",)))


class FullHostLifecycleTests(WorkflowFixture):
    # 각 host는 별도의 fixture에서 실제 guard → 도구 → 결과 hook 순서를 통과한다.
    def run_flow(self, host: str, *, external: bool = False) -> None:
        import test_guard
        launch = prepare_injection(self.project, host, "logic", build_root=self.directory / "build",
                                   state_root=self.directory / "state", source_codex_home=self.directory / "user-home")
        self.env.update(launch.environment)
        self.snapshot = launch.bundle_root / "policy"
        self.runtime = self.snapshot / ".agent-policy/runtime"
        working_root = self.root
        counter = 0

        def run(command: list[str]):
            nonlocal counter
            counter += 1
            tool = {"tool_name": "Bash", "tool_input": {"command": shlex.join(command), "workdir": str(working_root)},
                    "tool_use_id": f"command-{counter}"}
            before = self.hook("pre-tool", host, **tool)
            if host == "codex" and '"deny"' in before.stdout and "명령 실행 승인" in before.stdout:
                self.hook("user-prompt", host, prompt="명령 실행 승인")
                before = self.hook("pre-tool", host, **tool)
            self.assertEqual(before.returncode, 0, before.stderr)
            self.assertNotIn('"deny"', before.stdout)
            # Claude ask는 fixture 사용자가 승인한 후에만 실제 명령을 실행한다.
            result = subprocess.run(command, cwd=working_root, text=True, capture_output=True,
                                    env={**os.environ, **self.env}, check=False)
            after = self.hook("post-tool", host, **tool, tool_response={"exit_code": result.returncode,
                                                                      "stdout": result.stdout, "stderr": result.stderr})
            self.assertEqual(after.returncode, 0, after.stderr)
            self.assertEqual(result.returncode, 0, result.stderr)
            return result

        def write(relative: str, content: str):
            nonlocal counter
            counter += 1
            tool = {"tool_name": "Write", "tool_input": {"file_path": str(working_root / relative), "content": content},
                    "tool_use_id": f"write-{counter}"}
            before = self.hook("pre-tool", host, **tool)
            self.assertEqual(before.returncode, 0, before.stderr)
            self.assertNotIn('"deny"', before.stdout)
            path = working_root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            after = self.hook("post-tool", host, **tool, tool_response={"success": True})
            self.assertEqual(after.returncode, 0, after.stderr)

        self.hook("post-tool", host, tool_name="Skill", tool_input={"skill": "git-branch-strategy"}, tool_response={"success": True})
        self.hook("post-tool", host, tool_name="Read", tool_input={"file_path": "src/App.tsx"}, tool_response={"success": True})
        self.hook("user-prompt", host, prompt="proceed")
        script = str(self.snapshot / ".agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py")
        prefix = [sys.executable, "-I", script]
        proposed = run([*prefix, "proposal", "--branch", "task/full-flow", "--parent", "sy-main", "--purpose", "전체 흐름",
                        "--scope", "src", "--reason", "회귀 검사", "--role", "logic", "--git-integrator", host,
                        *(["--worktree", str(self.directory / "child")] if external else [])])
        args = self.proposal_args(proposed.stdout)
        self.hook("user-prompt", host, prompt="승인 " + args[-1])
        run([*prefix, "create", *args])
        if external:
            working_root = self.directory / "child"
        self.hook("user-prompt", host, prompt="현재 상태를 설명해줘")
        self.hook("session-start", host, source="compact")
        write("src/flow.tsx", "export const flow = true;\n")
        docs = self.directory / "document-fixtures"
        test_guard.GuardTests.write_complete_artifacts(docs)
        session = self.env["ASAN_SESSION_DIR"]
        for path in docs.iterdir():
            write(f"{session}/{path.name}", path.read_text())
        if external:
            sources = assignment_log_sources(self.project, host, self.env["ASAN_AGENT_POLICY_ASSIGNMENT"], self.directory / "state")
            self.assertIn(working_root / session, sources)
            logs = self.directory / "collected"
            collect_project_logs(self.project, host, logs, sources)
            repeated = collect_project_logs(self.project, host, logs, sources)
            self.assertEqual(repeated.copied, ())
            self.assertEqual((logs / self.project.id / host / "sessions" / Path(session).name / "plan.md").read_bytes(), (docs / "plan.md").read_bytes())
        run(["git", "add", "--", "src/flow.tsx", session])
        run(["git", "commit", "-qm", "flow"])
        proposed = run([*prefix, "finish-proposal", "--verify-command", self.project.commands["test"]])
        args = self.proposal_args(proposed.stdout, True)
        self.hook("user-prompt", host, prompt="승인 " + args[-1])
        for action in ("finish", "verify", "close"):
            run([*prefix, action, *args])
        self.assertEqual(self.git("branch", "--show-current"), "sy-main")
        self.assertEqual(self.git("config", "branch.task/full-flow.asan-state"), "CLOSED")

    def test_codex_full_hook_lifecycle(self) -> None:
        self.run_flow("codex")

    def test_claude_full_hook_lifecycle(self) -> None:
        self.run_flow("claude")

    def test_opencode_full_hook_lifecycle(self) -> None:
        self.run_flow("opencode")

    def test_codex_full_hook_lifecycle_with_external_worktree(self) -> None:
        self.run_flow("codex", external=True)


class StateRegressionTests(WorkflowFixture):
    def prepare(self, host: str = "claude", role: str = "logic", **options):
        return prepare_injection(self.project, host, role, build_root=self.directory / "build",
                                 state_root=self.directory / "state", source_codex_home=self.directory / "user-home", **options)

    def record_artifact(self, relative: str, content: str, call: str, *, success: bool = True, root: Path | None = None):
        target = (root or self.root) / relative
        event = {"tool_name": "Write", "tool_input": {"file_path": str(target), "content": content}, "tool_use_id": call}
        before = self.hook("pre-tool", **event)
        self.assertEqual(before.returncode, 0, before.stderr)
        if success:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
        after = self.hook("post-tool", **event, tool_response={"success": success})
        self.assertEqual(after.returncode, 0, after.stderr)

    def test_resume_pins_native_session_bundle_and_codex_home(self) -> None:
        first = self.prepare("codex")
        self.env.update(first.environment)
        started = self.hook("session-start", "codex")
        self.assertEqual(started.returncode, 0, started.stderr)
        self.hook("user-prompt", "codex", prompt="proceed")
        second = self.prepare("codex", "review")
        resumed = self.prepare("codex", resume_assignment=first.environment["ASAN_AGENT_POLICY_ASSIGNMENT"])
        self.assertEqual(resumed.bundle_root, first.bundle_root)
        self.assertEqual(resumed.environment["CODEX_HOME"], first.environment["CODEX_HOME"])
        self.assertNotEqual(resumed.environment["CODEX_HOME"], second.environment["CODEX_HOME"])
        self.assertIn(self.event["session_id"], resumed.command)
        self.hook("session-start", "codex", source="resume")
        self.assertTrue(self.state("codex").get("implementation_approved"))

    def test_failed_initial_artifact_write_releases_its_reservation(self) -> None:
        session = ".claude/logs/sessions/2026-09-08-shared"
        first = self.prepare(session_dir=session)
        self.env.update(first.environment)
        self.record_artifact(session + "/plan.md", "실패해야 하는 도구 호출", "first", success=False)
        second = self.prepare(session_dir=session)
        self.env.update(second.environment)
        self.event["session_id"] = "second"
        self.record_artifact(session + "/plan.md", "두 번째 assignment의 정상 산출물", "second")

    def test_distinct_calls_keep_independent_pending_bindings(self) -> None:
        launch = self.prepare()
        self.env.update(launch.environment)
        directory = launch.environment["ASAN_SESSION_DIR"]
        events = [{"tool_name": "Write", "tool_input": {"file_path": f"{directory}/{name}"}, "tool_use_id": name}
                  for name in ("plan.md", "exploration.md")]
        for event in events:
            result = self.hook("pre-tool", **event)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.hook("post-tool", **events[0], tool_response={"success": True})
        self.hook("post-tool", **events[1], tool_response={"success": False})
        with patch.dict(os.environ, self.env):
            binding = self.guard.runtime_state.read(self.guard.session_binding_path(self.event, self.root, "claude"))
            self.assertEqual(binding["directory"], directory)

    def test_worktree_log_sources_are_collected_in_recorded_order(self) -> None:
        launch = self.prepare()
        self.env.update(launch.environment)
        relative = launch.environment["ASAN_SESSION_DIR"]
        self.record_artifact(relative + "/plan.md", "기준 폴더의 이전 계획", "old")
        worktree = self.create_task("log-move", self.directory / "log-worktree")
        # 실제 create 성공 후의 assignment 전이를 재생한다.
        with patch.dict(os.environ, self.env):
            path = self.guard.session_binding_path(self.event, self.root, "claude")
            binding = self.guard.runtime_state.read(path)
            binding.update({"branch": "task/log-move", "task": "task/log-move", "worktree": str(worktree)})
            self.guard.runtime_state.write(path, binding)
        self.record_artifact(relative + "/plan.md", "격리 worktree의 최신 계획", "new", root=worktree)
        sources = assignment_log_sources(self.project, "claude", launch.environment["ASAN_AGENT_POLICY_ASSIGNMENT"], self.directory / "state")
        self.assertEqual(len(sources), 2)
        logs = self.directory / "logs"
        collect_project_logs(self.project, "claude", logs, sources)
        target = logs / "user-ui/claude/sessions" / Path(relative).name / "plan.md"
        self.assertEqual(target.read_text(), "격리 worktree의 최신 계획")
        collect_project_logs(self.project, "claude", logs, sources)
        self.assertEqual(target.read_text(), "격리 worktree의 최신 계획")

    def test_another_session_of_same_host_cannot_claim_git_worktree(self) -> None:
        self.create_task("ownership")
        for index in range(2):
            self.event["session_id"] = f"owner-{index}"
            self.hook("post-tool", tool_name="Skill", tool_input={"skill": "policy"}, tool_response={"success": True})
            self.hook("post-tool", tool_name="Read", tool_input={"file_path": "src/App.tsx"}, tool_response={"success": True})
            self.hook("user-prompt", prompt="proceed")
            result = self.hook("pre-tool", tool_name="Bash", tool_input={"command": "git add -- src/App.tsx"})
            if index == 0:
                self.assertEqual(result.returncode, 0, result.stderr)
            else:
                self.assertEqual(result.returncode, 2)
                self.assertIn("다른 assignment", result.stderr)

    def test_review_and_orchestration_cannot_write_source(self) -> None:
        self.create_task("capability")
        for role in ("review", "orchest"):
            self.env["ASAN_AGENT_POLICY_ROLE"] = role
            result = self.hook("pre-tool", tool_name="Write", tool_input={"file_path": "src/App.tsx"})
            self.assertEqual(result.returncode, 2)
            self.assertIn("source", result.stderr)

    def test_echoed_paths_are_not_read_evidence(self) -> None:
        skill = self.snapshot / ".agent-policy/common/skills/policy/SKILL.md"
        self.hook("post-tool", tool_name="Bash", tool_input={"command": f"echo {skill} src/App.tsx"}, tool_response={"exit_code": 0})
        self.assertIsNot(self.state().get("skill_confirmed"), True)
        self.assertIsNot(self.state().get("exploration_completed"), True)

    def test_snapshot_does_not_cache_git_across_events(self) -> None:
        self.create_task("snapshot")
        guard = self.guard.branch_guard
        with patch.object(guard, "_git_uncached", wraps=guard._git_uncached) as calls:
            with guard.git_snapshot():
                self.assertIsNone(guard.active_branch_denial(self.root))
                count = calls.call_count
                self.assertIsNone(guard.active_branch_denial(self.root))
                self.assertEqual(calls.call_count, count)
            self.git("config", "branch.task/snapshot.asan-state", "PRESERVED")
            with guard.git_snapshot():
                self.assertIsNotNone(guard.active_branch_denial(self.root))

    def test_git_diff_output_option_is_not_a_read_only_query(self) -> None:
        guard = self.guard.branch_guard
        self.assertFalse(guard.git_arguments_are_read_only(("diff", "--output=src/overwrite.ts")))
        self.assertTrue(guard.git_arguments_are_read_only(("diff", "--stat")))
