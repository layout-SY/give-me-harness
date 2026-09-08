from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from types import ModuleType

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from agent_policy.core import CENTRAL_ROOT, load_project, render_project

GUARD = CENTRAL_ROOT / "policy/guards/managed_policy_guard.py"


class GuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.session_id = str(uuid.uuid4())
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        manifest = self.root / ".agent-policy/manifest.json"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(
            json.dumps(
                {
                    "project_id": "test",
                    "managed_roots": [
                        "AGENTS.md",
                        ".agents/skills/",
                        ".opencode/plugins/",
                    ],
                    "managed_files": {"AGENTS.md": "unused"},
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def run_mode(
        self,
        mode: str,
        host: str,
        event: dict[str, object],
        environment: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        selected_environment = dict(os.environ)
        if environment:
            selected_environment.update(environment)
        return subprocess.run(
            ["python3", "-I", str(GUARD), mode, host],
            input=json.dumps({"cwd": str(self.root), "session_id": self.session_id, **event}),
            text=True,
            capture_output=True,
            cwd=self.root,
            env=selected_environment,
            check=False,
        )

    def run_guard(
        self,
        host: str,
        tool_name: str,
        tool_input: dict[str, object],
    ) -> subprocess.CompletedProcess[str]:
        return self.run_mode(
            "pre-tool",
            host,
            {"tool_name": tool_name, "tool_input": tool_input},
        )

    def record_common_readiness(
        self,
        host: str,
        contract_sha256: str = "",
    ) -> None:
        environment = {"ASAN_AGENT_POLICY_ROLE": "logic"}
        skill = self.run_mode(
            "post-tool",
            host,
            {"tool_name": "Skill", "tool_input": {"skill": "policy"}},
            environment,
        )
        exploration = self.run_mode(
            "post-tool",
            host,
            {"tool_name": "Read", "tool_input": {"file_path": "src/App.tsx"}},
            environment,
        )
        prompt = f"승인 {contract_sha256}" if contract_sha256 else "진행"
        approval = self.run_mode("user-prompt", host, {"prompt": prompt}, environment)
        self.assertEqual(skill.returncode, 0, skill.stderr)
        self.assertEqual(exploration.returncode, 0, exploration.stderr)
        self.assertEqual(approval.returncode, 0, approval.stderr)

    def rendered_guard(self) -> Path:
        rendered = render_project(load_project("user-ui"))
        bundle = self.root.parent / f"rendered-guard-{self.session_id}"
        runtime = bundle / ".agent-policy/runtime"
        runtime.mkdir(parents=True)
        managed = runtime / "managed_policy_guard.py"
        managed.write_bytes(rendered[".agent-policy/runtime/managed_policy_guard.py"])
        (runtime / "branch_guard.py").write_bytes(
            rendered[".agent-policy/runtime/branch_guard.py"]
        )
        contract = bundle / ".agent-policy/common/contracts/runtime-policy.json"
        contract.parent.mkdir(parents=True)
        contract.write_bytes(rendered[".agent-policy/common/contracts/runtime-policy.json"])
        return managed

    @staticmethod
    def write_complete_artifacts(session: Path) -> None:
        session.mkdir(parents=True, exist_ok=True)
        ordinary = (
            "plan.md",
            "exploration.md",
            "implementation-log.md",
            "review-log.md",
            "evaluation-log.md",
            "final-summary.md",
        )
        for name in ordinary:
            (session / name).write_text(
                f"# {name}\n\n검증 가능한 작업 근거를 충분히 기록했습니다.\n",
                encoding="utf-8",
            )
        (session / "grill-me-review.md").write_text(
            """# Grill Me 검토

## Method Guardrails

- neutral question-first 적용 여부: 예

## Neutral Question Flow

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer |
| --- | --- | --- | --- | --- |
| 계약 | 범위가 맞는가? | 예 | 테스트 | 현재 범위를 유지한다 |

## 결론

계약을 충족합니다.
""",
            encoding="utf-8",
        )
        (session / "portfolio-log.md").write_text(
            """# 이력서·포트폴리오 기록

## 사례 1 — 정책 검증

- 작업 유형: 테스트
- 관련 도메인/서비스: 중앙 정책
- 문제 출처: 회귀 테스트

### 문제 상황

정책 회귀를 막아야 했습니다.

### 고민과 선택

공통 검증을 선택했습니다.

### 적용

구조 검사를 적용했습니다.

### 사용 기술과 구체적 목적

Python unittest로 정책 계약을 검증했습니다.

### 결과

회귀를 자동 검출합니다.

### 이력서·포트폴리오 문구

중앙 정책 검증을 자동화했습니다.
""",
            encoding="utf-8",
        )

    @staticmethod
    def configure_v3_branch(
        root: Path,
        guard: ModuleType,
        branch: str,
        parent: str,
        *,
        scopes: tuple[str, ...] = ("src",),
        integrator: str = "claude",
        worktree: str = "",
    ) -> None:
        parent_head = guard.head(root, parent)
        subprocess.run(["git", "branch", branch, parent_head], cwd=root, check=True)
        roles = ("logic",)
        purpose = f"{branch} 세션 계보 검증"
        reason = f"{parent}의 승인된 하위 작업"
        contract = guard.canonical_contract(
            branch,
            purpose,
            parent,
            parent_head,
            parent,
            scopes,
            reason,
            worktree,
            roles,
            integrator,
        )
        digest = guard.contract_sha256(contract)
        for field, value in {
            "contract-version": "3",
            "task-id": branch.removeprefix("task/"),
            "purpose": purpose,
            "parent": parent,
            "parent-head": parent_head,
            "merge-target": parent,
            "proposal": f"asan-v3:{digest}",
            "contract-sha256": digest,
            "reason": reason,
            "git-integrator": integrator,
            "state": "ACTIVE",
            "worktree": worktree,
        }.items():
            subprocess.run(
                ["git", "config", f"branch.{branch}.asan-{field}", value],
                cwd=root,
                check=True,
            )
        for role in roles:
            subprocess.run(
                ["git", "config", "--add", f"branch.{branch}.asan-role", role],
                cwd=root,
                check=True,
            )
        for scope in scopes:
            subprocess.run(
                ["git", "config", "--add", f"branch.{branch}.asan-scope", scope],
                cwd=root,
                check=True,
            )

    def test_codex_apply_patch_uses_absolute_v3_worktree_without_shell_parsing(self) -> None:
        subprocess.run(["git", "branch", "-M", "sy-main"], cwd=self.root, check=True)
        subprocess.run(["git", "add", ".agent-policy/manifest.json"], cwd=self.root, check=True)
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
            cwd=self.root,
            check=True,
        )
        runtime_guard = self.rendered_guard()
        branch_source = (runtime_guard.parent / "branch_guard.py").read_bytes()
        rendered_branch_guard = ModuleType("codex_absolute_worktree_branch_guard")
        rendered_branch_guard.__file__ = str(runtime_guard.parent / "branch_guard.py")
        exec(
            compile(branch_source, rendered_branch_guard.__file__, "exec"),
            rendered_branch_guard.__dict__,
        )
        branch = "task/codex-absolute-worktree"
        worktree = self.root.parent / f"codex-worktree-{self.session_id}"
        self.configure_v3_branch(
            self.root,
            rendered_branch_guard,
            branch,
            "sy-main",
            scopes=("src/feature",),
            integrator="codex",
            worktree=str(worktree.resolve()),
        )
        subprocess.run(
            ["git", "worktree", "add", "-q", str(worktree), branch],
            cwd=self.root,
            check=True,
        )
        try:
            self.record_common_readiness("codex")
            environment = {
                **os.environ,
                "ASAN_AGENT_POLICY_MODE": "inject",
                "ASAN_AGENT_POLICY_PROJECT": "user-ui",
                "ASAN_AGENT_POLICY_BUNDLE_ROOT": str(runtime_guard.parents[2]),
                "ASAN_AGENT_POLICY_ROLE": "logic",
                "ASAN_AGENT_POLICY_TASK": branch,
            }

            def run_patch(target: Path) -> subprocess.CompletedProcess[str]:
                command = (
                    "*** Begin Patch\n"
                    f"*** Add File: {target}\n"
                    "+export const parse = () => {\n"
                    "+  return true;\n"
                    "+};\n"
                    "*** End Patch"
                )
                return subprocess.run(
                    ["python3", "-I", str(runtime_guard), "pre-tool", "codex"],
                    input=json.dumps(
                        {
                            "cwd": str(self.root),
                            "session_id": self.session_id,
                            "tool_name": "apply_patch",
                            "tool_input": {"command": command},
                        }
                    ),
                    text=True,
                    capture_output=True,
                    cwd=self.root,
                    env=environment,
                    check=False,
                )

            allowed = run_patch(worktree / "src/feature/parser.ts")
            self.assertEqual(allowed.returncode, 0, allowed.stderr)
            self.assertEqual(allowed.stdout, "")

            denied = run_patch(worktree / "src/outside.ts")
            self.assertEqual(denied.returncode, 0, denied.stderr)
            decision = json.loads(denied.stdout)["hookSpecificOutput"]
            self.assertEqual(decision["permissionDecision"], "deny")
            self.assertIn("승인된 작업 범위 밖", decision["permissionDecisionReason"])
        finally:
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(worktree)],
                cwd=self.root,
                check=False,
                capture_output=True,
            )

    def test_codex_returns_native_deny_shape(self) -> None:
        result = self.run_guard("codex", "Write", {"file_path": "AGENTS.md"})
        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_claude_and_opencode_exit_two(self) -> None:
        for host, tool_input in (
            ("claude", {"file_path": ".agents/skills/SKILL.md"}),
            ("opencode", {"filePath": ".opencode/plugins/new.js"}),
        ):
            with self.subTest(host=host):
                result = self.run_guard(host, "Write", tool_input)
                self.assertEqual(result.returncode, 2)
                self.assertIn("중앙 프로젝트", result.stderr)

    def test_apply_patch_add_update_delete_and_move_are_covered(self) -> None:
        for heading in (
            "*** Add File: AGENTS.md",
            "*** Update File: AGENTS.md",
            "*** Delete File: AGENTS.md",
            "*** Move to: .agents/skills/new/SKILL.md",
        ):
            with self.subTest(heading=heading):
                command = f"*** Begin Patch\n{heading}\n+x\n*** End Patch"
                result = self.run_guard("codex", "apply_patch", {"command": command})
                self.assertEqual(
                    json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"],
                    "deny",
                )

    def test_explicit_shell_writes_are_denied(self) -> None:
        for command in (
            "printf x > AGENTS.md",
            "rm AGENTS.md",
            "sed -i '' 's/a/b/' AGENTS.md",
            "git reset --hard",
        ):
            with self.subTest(command=command):
                result = self.run_guard("claude", "Bash", {"command": command})
                self.assertEqual(result.returncode, 2)

    def test_read_only_shell_is_allowed_and_application_edit_needs_common_readiness(self) -> None:
        read = self.run_guard("claude", "Bash", {"command": "sed -n '1,20p' AGENTS.md"})
        denied = self.run_guard("codex", "Write", {"file_path": "src/App.tsx"})
        self.record_common_readiness("codex")
        application = self.run_guard("codex", "Write", {"file_path": "src/App.tsx"})
        self.assertEqual(read.returncode, 0, read.stderr)
        self.assertEqual(
            json.loads(denied.stdout)["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )
        self.assertIn("사용자 구현 승인", denied.stdout)
        self.assertEqual(application.returncode, 0, application.stderr)
        self.assertEqual(application.stdout, "")

    def test_common_readiness_gate_applies_to_every_host(self) -> None:
        for host in ("codex", "claude", "opencode"):
            with self.subTest(host=host):
                denied = self.run_guard(host, "Write", {"file_path": "src/feature.ts"})
                if host == "codex":
                    self.assertEqual(
                        json.loads(denied.stdout)["hookSpecificOutput"]["permissionDecision"],
                        "deny",
                    )
                else:
                    self.assertEqual(denied.returncode, 2)
                    self.assertIn("공통 구현 gate", denied.stderr)
                self.record_common_readiness(host)
                allowed = self.run_guard(host, "Write", {"file_path": "src/feature.ts"})
                self.assertEqual(allowed.returncode, 0, allowed.stderr)
                self.assertEqual(allowed.stdout, "")

    def test_ui_readiness_requires_shared_ui_exploration(self) -> None:
        environment = {"ASAN_AGENT_POLICY_ROLE": "ui"}
        self.run_mode(
            "post-tool",
            "claude",
            {"tool_name": "Skill", "tool_input": {"skill": "project-ui"}},
            environment,
        )
        self.run_mode(
            "post-tool",
            "claude",
            {"tool_name": "Read", "tool_input": {"file_path": "src/App.tsx"}},
            environment,
        )
        self.run_mode("user-prompt", "claude", {"prompt": "작업 진행"}, environment)
        denied = self.run_mode(
            "pre-tool",
            "claude",
            {"tool_name": "Write", "tool_input": {"file_path": "src/feature.ts"}},
            environment,
        )
        self.assertEqual(denied.returncode, 2)
        self.assertIn("src/shared/ui", denied.stderr)

        self.run_mode(
            "post-tool",
            "claude",
            {
                "tool_name": "Glob",
                "tool_input": {"path": "src/shared/ui"},
            },
            environment,
        )
        allowed = self.run_mode(
            "pre-tool",
            "claude",
            {"tool_name": "Write", "tool_input": {"file_path": "src/feature.ts"}},
            environment,
        )
        self.assertEqual(allowed.returncode, 0, allowed.stderr)

    def test_exec_alias_is_governed_as_a_shell_tool(self) -> None:
        guard = self.rendered_guard()
        for host in ("codex", "claude", "opencode"):
            for command in ("git -C . reset --hard", "git -C . push origin HEAD"):
                with self.subTest(host=host, command=command):
                    completed = subprocess.run(
                        ["python3", "-I", str(guard), "pre-tool", host],
                        input=json.dumps(
                            {
                                "cwd": str(self.root),
                                "session_id": self.session_id,
                                "tool_name": "functions.exec",
                                "tool_input": {"command": command},
                            }
                        ),
                        text=True,
                        capture_output=True,
                        cwd=self.root,
                        check=False,
                    )
                    message = completed.stdout if host == "codex" else completed.stderr
                    self.assertIn("사용자 전용", message)
                    self.assertNotIn("명령 실행 승인", message)

    def test_non_git_shell_file_mutation_requires_structured_write_tool(self) -> None:
        self.record_common_readiness("claude")
        for command in (
            "touch src/unscoped.ts",
            "git status --short && touch src/unscoped.ts",
        ):
            with self.subTest(command=command):
                denied = self.run_guard(
                    "claude",
                    "functions.exec",
                    {"command": command},
                )
                self.assertEqual(denied.returncode, 2)
                self.assertIn("비구조적 파일 변경", denied.stderr)
                self.assertIn("apply_patch", denied.stderr)

    def test_harmless_stderr_redirects_do_not_count_as_policy_writes(self) -> None:
        commands = (
            "ls .agents/skills/policy/SKILL.md 2>&1",
            "ls .agents/skills/policy/SKILL.md 2>/dev/null",
            "ls .agents/skills/policy/SKILL.md 2>/tmp/asan-policy-errors.log",
            "ls .codex/logs/sessions/2026-09-02-task/handoff.md 2>&1",
            "ls .codex/logs/sessions/2026-09-02-task/handoff.md 2>/dev/null",
            "sed -n '1,20p' AGENTS.md >/dev/null",
            "sed -n '1,20p' AGENTS.md >& /dev/null",
        )
        for command in commands:
            with self.subTest(command=command):
                result = self.run_guard("claude", "Bash", {"command": command})
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "")

    def test_fd_duplication_does_not_hide_a_managed_file_redirect(self) -> None:
        for command in (
            "printf x > AGENTS.md 2>&1",
            "printf x >& AGENTS.md",
        ):
            with self.subTest(command=command):
                result = self.run_guard("claude", "Bash", {"command": command})
                self.assertEqual(result.returncode, 2)
                self.assertIn("AGENTS.md", result.stderr)

    def test_claude_asks_for_git_build_and_dev_commands(self) -> None:
        self.record_common_readiness("claude")
        for command, expected_category in (
            ("git fetch origin", "Git"),
            ("npm run build", "빌드"),
            ("vite build", "빌드"),
            ("npm run dev -- --host", "개발 서버"),
        ):
            with self.subTest(command=command):
                result = self.run_guard("claude", "Bash", {"command": command})
                output = json.loads(result.stdout)
                decision = output["hookSpecificOutput"]
                self.assertEqual(decision["permissionDecision"], "ask")
                self.assertIn(expected_category, decision["permissionDecisionReason"])
                self.assertIn(command, decision["permissionDecisionReason"])
                if command == "vite build":
                    self.assertNotIn("개발 서버", decision["permissionDecisionReason"])

    def test_lint_and_test_commands_do_not_require_operation_approval(self) -> None:
        for command in ("npm run lint", "npm run test"):
            with self.subTest(command=command):
                result = self.run_guard("claude", "Bash", {"command": command})
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "")

    def test_read_only_git_queries_need_neither_implementation_nor_command_approval(self) -> None:
        commands = (
            "git status --short --branch",
            "git diff --stat",
            "git log -1 --oneline",
            "git branch -a -vv --no-abbrev",
            "git worktree list --porcelain",
            "git -C . config --get user.name",
        )
        for host in ("codex", "claude"):
            for command in commands:
                with self.subTest(host=host, command=command):
                    result = self.run_guard(host, "Bash", {"command": command})
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout, "")

    def test_codex_approval_is_exact_and_one_shot(self) -> None:
        command = "git fetch origin"
        self.record_common_readiness("codex")
        first = self.run_guard("codex", "Bash", {"command": command})
        self.assertEqual(
            json.loads(first.stdout)["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )

        approval = self.run_mode(
            "user-prompt",
            "codex",
            {"prompt": "명령 실행 승인"},
        )
        self.assertIn("동일 명령", approval.stdout)

        allowed = self.run_guard("codex", "Bash", {"command": command})
        self.assertEqual(allowed.returncode, 0, allowed.stderr)
        self.assertEqual(allowed.stdout, "")

        second = self.run_guard("codex", "Bash", {"command": command})
        self.assertEqual(
            json.loads(second.stdout)["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )

    def test_codex_approval_does_not_apply_to_changed_command(self) -> None:
        self.run_guard("codex", "Bash", {"command": "npm run build"})
        self.run_mode("user-prompt", "codex", {"prompt": "명령 실행 승인"})

        changed = self.run_guard("codex", "Bash", {"command": "npm run build -- --mode host"})
        self.assertEqual(
            json.loads(changed.stdout)["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )

    def test_codex_approval_is_isolated_by_session(self) -> None:
        command = "git fetch origin"
        self.record_common_readiness("codex")
        first_session = self.session_id
        self.run_guard("codex", "Bash", {"command": command})
        self.run_mode("user-prompt", "codex", {"prompt": "명령 실행 승인"})

        self.session_id = str(uuid.uuid4())
        other_session = self.run_guard("codex", "Bash", {"command": command})
        self.assertEqual(
            json.loads(other_session.stdout)["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )

        self.session_id = first_session
        original_session = self.run_guard("codex", "Bash", {"command": command})
        self.assertEqual(original_session.stdout, "")

    def test_all_approval_phrases_only_satisfy_implementation_approval(self) -> None:
        for phrase in ("전부 승인", "모두 승인"):
            with self.subTest(phrase=phrase):
                self.session_id = str(uuid.uuid4())
                environment = {"ASAN_AGENT_POLICY_ROLE": "logic"}
                self.run_mode(
                    "post-tool",
                    "codex",
                    {"tool_name": "Skill", "tool_input": {"skill": "policy"}},
                    environment,
                )
                self.run_mode(
                    "post-tool",
                    "codex",
                    {"tool_name": "Read", "tool_input": {"file_path": "src/App.tsx"}},
                    environment,
                )
                self.run_mode("user-prompt", "codex", {"prompt": phrase}, environment)
                write = self.run_mode(
                    "pre-tool",
                    "codex",
                    {"tool_name": "Write", "tool_input": {"file_path": "src/feature.ts"}},
                    environment,
                )
                self.assertEqual(write.returncode, 0, write.stderr)
                self.assertEqual(write.stdout, "")

                build = self.run_mode(
                    "pre-tool",
                    "codex",
                    {"tool_name": "Bash", "tool_input": {"command": "npm run build"}},
                    environment,
                )
                decision = json.loads(build.stdout)["hookSpecificOutput"]
                self.assertEqual(decision["permissionDecision"], "deny")
                self.assertIn("명령 실행 승인", decision["permissionDecisionReason"])

    def test_codex_session_start_context_is_valid_json(self) -> None:
        result = self.run_mode("session-start", "codex", {})

        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        context = output["hookSpecificOutput"]
        self.assertEqual(context["hookEventName"], "SessionStart")
        self.assertIsInstance(context["additionalContext"], str)
        self.assertTrue(context["additionalContext"])

    def test_codex_approval_phrase_must_be_standalone(self) -> None:
        command = "npm run dev"
        self.run_guard("codex", "Bash", {"command": command})
        embedded = self.run_mode(
            "user-prompt",
            "codex",
            {"prompt": "이제 명령 실행 승인해줘"},
        )
        self.assertEqual(embedded.stdout, "")

        still_denied = self.run_guard("codex", "Bash", {"command": command})
        self.assertEqual(
            json.loads(still_denied.stdout)["hookSpecificOutput"]["permissionDecision"],
            "deny",
        )

    def test_conditional_implementation_approval_is_accepted_without_weakening_denial(self) -> None:
        environment = {"ASAN_AGENT_POLICY_ROLE": "logic"}
        for host in ("codex", "claude", "opencode"):
            for prompt, expected_allowed in (
                ("좋아. 회귀 테스트를 먼저 추가하는 조건으로 이 계획대로 진행해.", True),
                ("회귀 테스트는 추가하되 구현은 진행하지 마.", False),
            ):
                with self.subTest(host=host, prompt=prompt):
                    self.session_id = str(uuid.uuid4())
                    self.run_mode(
                        "post-tool",
                        host,
                        {"tool_name": "Skill", "tool_input": {"skill": "policy"}},
                        environment,
                    )
                    self.run_mode(
                        "post-tool",
                        host,
                        {"tool_name": "Read", "tool_input": {"file_path": "src/App.tsx"}},
                        environment,
                    )
                    self.run_mode("user-prompt", host, {"prompt": prompt}, environment)
                    write = self.run_mode(
                        "pre-tool",
                        host,
                        {"tool_name": "Write", "tool_input": {"file_path": "src/feature.ts"}},
                        environment,
                    )
                    if expected_allowed:
                        self.assertEqual(write.returncode, 0, write.stderr)
                        self.assertEqual(write.stdout, "")
                    elif host == "codex":
                        decision = json.loads(write.stdout)["hookSpecificOutput"]
                        self.assertEqual(decision["permissionDecision"], "deny")
                        self.assertIn("사용자 구현 승인", decision["permissionDecisionReason"])
                    else:
                        self.assertEqual(write.returncode, 2)
                        self.assertIn("사용자 구현 승인", write.stderr)

    def test_never_agent_git_commands_cannot_be_unlocked_by_codex_approval(self) -> None:
        guard = self.rendered_guard()

        def run(mode: str, command: str = "", prompt: str = "") -> subprocess.CompletedProcess[str]:
            event: dict[str, object] = {
                "cwd": str(self.root),
                "session_id": self.session_id,
            }
            if command:
                event.update({"tool_name": "Bash", "tool_input": {"command": command}})
            if prompt:
                event["prompt"] = prompt
            return subprocess.run(
                ["python3", "-I", str(guard), mode, "codex"],
                input=json.dumps(event),
                text=True,
                capture_output=True,
                cwd=self.root,
                check=False,
            )

        for command in ("git -C . reset --hard", "git push origin HEAD"):
            with self.subTest(command=command):
                first = run("pre-tool", command=command)
                first_reason = json.loads(first.stdout)["hookSpecificOutput"][
                    "permissionDecisionReason"
                ]
                self.assertIn("사용자 전용", first_reason)
                self.assertNotIn("명령 실행 승인", first_reason)
                _ = run("user-prompt", prompt="명령 실행 승인")
                second = run("pre-tool", command=command)
                second_reason = json.loads(second.stdout)["hookSpecificOutput"][
                    "permissionDecisionReason"
                ]
                self.assertIn("사용자 전용", second_reason)

    def test_artifact_reads_are_cross_host_but_writes_are_current_session_only(self) -> None:
        current = ".claude/logs/sessions/2026-09-03-current/plan.md"
        own_unknown = ".claude/logs/sessions/2026-09-03-current/unknown/notes.md"
        foreign = ".codex/logs/sessions/2026-09-03-foreign/plan.md"

        bound = self.run_guard("claude", "Write", {"file_path": current})
        self.assertEqual(bound.returncode, 0, bound.stderr)
        read = self.run_guard("claude", "Read", {"file_path": foreign})
        self.assertEqual(read.returncode, 0, read.stderr)
        foreign_write = self.run_guard("claude", "Write", {"file_path": foreign})
        self.assertEqual(foreign_write.returncode, 2)
        self.assertIn("읽기 전용", foreign_write.stderr)
        other_session = self.run_guard(
            "claude",
            "Write",
            {"file_path": ".claude/logs/sessions/2026-09-03-other/plan.md"},
        )
        self.assertEqual(other_session.returncode, 2)
        unknown = self.run_guard("claude", "Write", {"file_path": own_unknown})
        self.assertEqual(unknown.returncode, 0, unknown.stderr)
        misplaced = self.run_guard(
            "claude",
            "Write",
            {"file_path": ".claude/logs/sessions/2026-09-03-current/notes.md"},
        )
        self.assertEqual(misplaced.returncode, 2)
        self.assertIn("unknown/", misplaced.stderr)

    def test_artifact_write_without_session_identity_requires_declared_directory(self) -> None:
        event = {
            "cwd": str(self.root),
            "tool_name": "Write",
            "tool_input": {
                "file_path": ".opencode/logs/sessions/2026-09-03-task/plan.md"
            },
        }
        missing = subprocess.run(
            ["python3", "-I", str(GUARD), "pre-tool", "opencode"],
            input=json.dumps(event),
            text=True,
            capture_output=True,
            cwd=self.root,
            check=False,
        )
        self.assertEqual(missing.returncode, 2)
        self.assertIn("ASAN_SESSION_DIR", missing.stderr)

        environment = dict(os.environ)
        environment["ASAN_SESSION_DIR"] = ".opencode/logs/sessions/2026-09-03-task"
        declared = subprocess.run(
            ["python3", "-I", str(GUARD), "pre-tool", "opencode"],
            input=json.dumps(event),
            text=True,
            capture_output=True,
            cwd=self.root,
            env=environment,
            check=False,
        )
        self.assertEqual(declared.returncode, 0, declared.stderr)

    def test_opencode_operation_gate_is_delegated_to_native_permissions(self) -> None:
        result = self.run_guard("opencode", "bash", {"command": "git status"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_inject_ignores_stale_manifest_and_protects_central_bundle(self) -> None:
        bundle = self.root / "central-bundle"
        bundle.mkdir()
        environment = {
            "ASAN_AGENT_POLICY_MODE": "inject",
            "ASAN_AGENT_POLICY_PROJECT": "user-ui",
            "ASAN_AGENT_POLICY_BUNDLE_ROOT": str(bundle),
        }
        stale_manifest_target = self.run_mode(
            "pre-tool",
            "claude",
            {"tool_name": "Write", "tool_input": {"file_path": ".codex/config.toml"}},
            environment,
        )
        central_write = self.run_mode(
            "pre-tool",
            "claude",
            {"tool_name": "Write", "tool_input": {"file_path": str(bundle / "AGENTS.md")}},
            environment,
        )
        central_workdir = self.run_mode(
            "pre-tool",
            "opencode",
            {
                "tool_name": "bash",
                "tool_input": {"command": "touch output", "workdir": str(bundle)},
            },
            environment,
        )
        self.assertEqual(stale_manifest_target.returncode, 2)
        self.assertEqual(central_write.returncode, 2)
        self.assertEqual(central_workdir.returncode, 2)

    def test_inject_allows_trusted_branch_workflow_from_policy_snapshot(self) -> None:
        bundle = self.root / "central-bundle"
        script = (
            bundle
            / "policy/.agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py"
        )
        script.parent.mkdir(parents=True)
        script.write_text("# trusted test fixture\n", encoding="utf-8")
        environment = {
            "ASAN_AGENT_POLICY_MODE": "inject",
            "ASAN_AGENT_POLICY_PROJECT": "user-ui",
            "ASAN_AGENT_POLICY_BUNDLE_ROOT": str(bundle),
        }
        commands = (
            (
                f"python3 {script} proposal --branch task/icon-policy --purpose icon "
                "--parent sy-main --scope src --reason 'git restore . 오판 회귀'"
            ),
            f"python3 {script} scope-proposal --scope src --scope docs",
            (
                f"python3 {script} context 2>/dev/null"
            ),
        )
        for host in ("codex", "claude", "opencode"):
            for command in commands:
                with self.subTest(host=host, command=command):
                    result = self.run_mode(
                        "pre-tool",
                        host,
                        {"tool_name": "Bash", "tool_input": {"command": command}},
                        environment,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout, "")

        chained = self.run_mode(
            "pre-tool",
            "claude",
            {
                "tool_name": "Bash",
                "tool_input": {
                    "command": f"{commands[0]} && touch {bundle / 'modified'}",
                },
            },
            environment,
        )
        self.assertEqual(chained.returncode, 2)
        self.assertIn("중앙 프로젝트", chained.stderr)

    def test_trusted_create_still_enforces_the_contract_git_integrator(self) -> None:
        bundle = self.root / "central-bundle"
        script = (
            bundle
            / "policy/.agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py"
        )
        script.parent.mkdir(parents=True)
        script.write_text("# trusted test fixture\n", encoding="utf-8")
        proposal = self.root / "proposal.json"
        proposal.write_text(
            json.dumps({"branch": "task/next", "git_integrator": "codex"}),
            encoding="utf-8",
        )
        environment = {
            "ASAN_AGENT_POLICY_MODE": "inject",
            "ASAN_AGENT_POLICY_PROJECT": "user-ui",
            "ASAN_AGENT_POLICY_BUNDLE_ROOT": str(bundle),
        }
        command = (
            f"python3 {script} create --proposal-file {proposal} "
            f"--proposal-sha256 {'0' * 64}"
        )

        self.record_common_readiness("codex", "0" * 64)

        denied = self.run_mode(
            "pre-tool",
            "claude",
            {"tool_name": "Bash", "tool_input": {"command": command}},
            environment,
        )
        allowed = self.run_mode(
            "pre-tool",
            "codex",
            {"tool_name": "Bash", "tool_input": {"command": command}},
            environment,
        )
        active_environment = {
            **environment,
            "ASAN_AGENT_POLICY_TASK": "task/current",
        }
        active_task_denied = self.run_mode(
            "pre-tool",
            "codex",
            {"tool_name": "Bash", "tool_input": {"command": command}},
            active_environment,
        )

        self.assertEqual(denied.returncode, 2)
        self.assertIn("Git 통합 담당자는 codex", denied.stderr)
        self.assertEqual(allowed.returncode, 0, allowed.stderr)
        self.assertEqual(allowed.stdout, "")
        active_reason = json.loads(active_task_denied.stdout)["hookSpecificOutput"][
            "permissionDecisionReason"
        ]
        self.assertIn("권한 root", active_reason)
        self.assertIn("task/current", active_reason)

    def test_parent_assignment_can_create_descendants_but_not_unrelated_tasks(self) -> None:
        subprocess.run(["git", "branch", "-M", "sy-main"], cwd=self.root, check=True)
        subprocess.run(["git", "add", ".agent-policy/manifest.json"], cwd=self.root, check=True)
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
            cwd=self.root,
            check=True,
        )
        runtime_guard = self.rendered_guard()
        branch_source = (runtime_guard.parent / "branch_guard.py").read_bytes()
        rendered_branch_guard = ModuleType("descendant_assignment_branch_guard")
        rendered_branch_guard.__file__ = str(runtime_guard.parent / "branch_guard.py")
        exec(
            compile(branch_source, rendered_branch_guard.__file__, "exec"),
            rendered_branch_guard.__dict__,
        )
        parent = "task/meeting-reserve-ui"
        child = "task/reserve-option-lazy-load"
        unrelated = "task/unrelated-reserve"
        self.configure_v3_branch(self.root, rendered_branch_guard, parent, "sy-main")
        self.configure_v3_branch(
            self.root,
            rendered_branch_guard,
            child,
            parent,
            scopes=("src/child",),
        )
        self.configure_v3_branch(self.root, rendered_branch_guard, unrelated, "sy-main")
        subprocess.run(["git", "switch", "-q", child], cwd=self.root, check=True)

        bundle = runtime_guard.parents[2]
        script = (
            bundle
            / "policy/.agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py"
        )
        script.parent.mkdir(parents=True)
        script.write_text("# trusted test fixture\n", encoding="utf-8")
        proposal = self.root / "proposal.json"
        command = (
            f"python3 {script} create --proposal-file {proposal} "
            f"--proposal-sha256 {'0' * 64}"
        )
        environment = {
            "ASAN_AGENT_POLICY_MODE": "inject",
            "ASAN_AGENT_POLICY_PROJECT": "user-ui",
            "ASAN_AGENT_POLICY_BUNDLE_ROOT": str(bundle),
            "ASAN_AGENT_POLICY_ROLE": "logic",
            "ASAN_AGENT_POLICY_TASK": parent,
        }

        def run_create(parent_branch: str) -> subprocess.CompletedProcess[str]:
            proposal.write_text(
                json.dumps(
                    {
                        "branch": "task/reserve-option-child",
                        "parent": parent_branch,
                        "git_integrator": "claude",
                    }
                ),
                encoding="utf-8",
            )
            return subprocess.run(
                ["python3", "-I", str(runtime_guard), "pre-tool", "claude"],
                input=json.dumps(
                    {
                        "cwd": str(self.root),
                        "session_id": self.session_id,
                        "tool_name": "Bash",
                        "tool_input": {"command": command},
                    }
                ),
                text=True,
                capture_output=True,
                cwd=self.root,
                env={**os.environ, **environment},
                check=False,
            )

        self.record_common_readiness("claude", "0" * 64)
        allowed = run_create(child)
        denied = run_create(unrelated)

        self.assertEqual(allowed.returncode, 0, allowed.stderr)
        self.assertEqual(allowed.stdout, "")
        self.assertEqual(denied.returncode, 2)
        self.assertIn("권한 root", denied.stderr)
        self.assertIn(unrelated, denied.stderr)

        proposal.unlink()

        def run_tool(
            tool_name: str,
            tool_input: dict[str, object],
        ) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                ["python3", "-I", str(runtime_guard), "pre-tool", "claude"],
                input=json.dumps(
                    {
                        "cwd": str(self.root),
                        "session_id": self.session_id,
                        "tool_name": tool_name,
                        "tool_input": tool_input,
                    }
                ),
                text=True,
                capture_output=True,
                cwd=self.root,
                env={**os.environ, **environment},
                check=False,
            )

        source_relative = "src/child/feature.ts"
        child_write = run_tool("Write", {"file_path": source_relative})
        self.assertEqual(child_write.returncode, 0, child_write.stderr)
        repository_identity = rendered_branch_guard.git_common_directory(self.root)
        assert repository_identity is not None
        binding_digest = hashlib.sha256(
            f"{repository_identity}\0claude\0{self.session_id}".encode()
        ).hexdigest()
        binding_path = (
            Path(tempfile.gettempdir())
            / "asan-agent-policy-session-bindings"
            / f"{binding_digest}.txt"
        )
        child_binding = json.loads(binding_path.read_text(encoding="utf-8"))
        self.assertEqual(child_binding["task"], parent)
        self.assertEqual(child_binding["branch"], child)
        source = self.root / source_relative
        source.parent.mkdir(parents=True)
        source.write_text("export const child = true\n", encoding="utf-8")

        artifact_write = run_tool(
            "Write",
            {
                "file_path": (
                    ".claude/logs/sessions/2026-09-05-meeting-reserve-ui/plan.md"
                )
            },
        )
        self.assertEqual(artifact_write.returncode, 0, artifact_write.stderr)
        add = run_tool("Bash", {"command": f"git add -- {source_relative}"})
        self.assertEqual(add.returncode, 0, add.stderr)
        outside_child_scope = run_tool(
            "Write",
            {"file_path": "src/parent-only.ts"},
        )
        self.assertEqual(outside_child_scope.returncode, 2)
        self.assertIn("승인된 작업 범위 밖", outside_child_scope.stderr)

        subprocess.run(["git", "add", source_relative], cwd=self.root, check=True)
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Policy Test",
                "-c",
                "user.email=policy@example.com",
                "commit",
                "-qm",
                "child change",
            ],
            cwd=self.root,
            check=True,
        )
        subprocess.run(["git", "switch", "-q", parent], cwd=self.root, check=True)
        parent_write = run_tool("Write", {"file_path": "src/parent.ts"})
        self.assertEqual(parent_write.returncode, 0, parent_write.stderr)
        parent_binding = json.loads(binding_path.read_text(encoding="utf-8"))
        self.assertEqual(parent_binding["task"], parent)
        self.assertEqual(parent_binding["branch"], parent)

    def test_v3_codex_artifact_write_needs_no_proposal_reapproval(self) -> None:
        subprocess.run(["git", "branch", "-M", "sy-main"], cwd=self.root, check=True)
        subprocess.run(["git", "add", ".agent-policy/manifest.json"], cwd=self.root, check=True)
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
            cwd=self.root,
            check=True,
        )
        runtime_guard = self.rendered_guard()
        branch_source = (runtime_guard.parent / "branch_guard.py").read_bytes()
        rendered_branch_guard = ModuleType("codex_artifact_branch_guard")
        rendered_branch_guard.__file__ = str(runtime_guard.parent / "branch_guard.py")
        exec(
            compile(branch_source, rendered_branch_guard.__file__, "exec"),
            rendered_branch_guard.__dict__,
        )
        branch = "task/meeting-reservation-logic"
        self.configure_v3_branch(
            self.root,
            rendered_branch_guard,
            branch,
            "sy-main",
            integrator="codex",
        )
        subprocess.run(["git", "switch", "-q", branch], cwd=self.root, check=True)
        subprocess.run(
            [
                "git",
                "config",
                f"branch.{branch}.asan-proposal",
                f"asan-v3:{'0' * 64}",
            ],
            cwd=self.root,
            check=True,
        )
        session_dir = ".codex/logs/sessions/2026-09-07-meeting-reservation-logic"
        environment = {
            "ASAN_AGENT_POLICY_MODE": "inject",
            "ASAN_AGENT_POLICY_PROJECT": "user-ui",
            "ASAN_AGENT_POLICY_BUNDLE_ROOT": str(runtime_guard.parents[2]),
            "ASAN_AGENT_POLICY_ROLE": "logic",
            "ASAN_AGENT_POLICY_TASK": branch,
            "ASAN_ARTIFACT_RESPONSIBILITY": "owner",
            "ASAN_SESSION_DIR": session_dir,
        }

        result = subprocess.run(
            ["python3", "-I", str(runtime_guard), "pre-tool", "codex"],
            input=json.dumps(
                {
                    "cwd": str(self.root),
                    "session_id": self.session_id,
                    "tool_name": "Write",
                    "tool_input": {"file_path": f"{session_dir}/plan.md"},
                }
            ),
            text=True,
            capture_output=True,
            cwd=self.root,
            env={**os.environ, **environment},
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

        source_write = subprocess.run(
            ["python3", "-I", str(runtime_guard), "pre-tool", "codex"],
            input=json.dumps(
                {
                    "cwd": str(self.root),
                    "session_id": self.session_id,
                    "tool_name": "Write",
                    "tool_input": {"file_path": "src/blocked.ts"},
                }
            ),
            text=True,
            capture_output=True,
            cwd=self.root,
            env={**os.environ, **environment},
            check=False,
        )

        self.assertEqual(source_write.returncode, 0, source_write.stderr)
        source_decision = json.loads(source_write.stdout)["hookSpecificOutput"]
        self.assertEqual(source_decision["permissionDecision"], "deny")
        self.assertIn(
            "승인 요청 식별자가 분기 계약과 일치하지 않습니다",
            source_decision["permissionDecisionReason"],
        )

    def test_proposal_posttool_binds_user_approval_to_full_sha256(self) -> None:
        bundle = self.root / "central-bundle"
        script = (
            bundle
            / "policy/.agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py"
        )
        script.parent.mkdir(parents=True)
        script.write_text("# trusted test fixture\n", encoding="utf-8")
        proposal = self.root / "proposal.json"
        proposal.write_text(json.dumps({"git_integrator": "codex"}), encoding="utf-8")
        environment = {
            "ASAN_AGENT_POLICY_MODE": "inject",
            "ASAN_AGENT_POLICY_PROJECT": "user-ui",
            "ASAN_AGENT_POLICY_BUNDLE_ROOT": str(bundle),
        }
        digest = "a" * 64
        proposal_command = f"python3 {script} proposal --branch task/full-digest"
        create = (
            f"python3 {script} create --proposal-file {proposal} "
            f"--proposal-sha256 {digest}"
        )
        self.run_mode(
            "post-tool",
            "codex",
            {
                "tool_name": "Bash",
                "tool_input": {"command": proposal_command},
                "tool_output": f"proposal 파일: /tmp/{digest}.json\nproposal SHA-256: {digest}\n",
            },
            environment,
        )
        self.run_mode(
            "post-tool",
            "codex",
            {"tool_name": "Skill", "tool_input": {"skill": "git-branch-strategy"}},
            environment,
        )
        self.run_mode(
            "post-tool",
            "codex",
            {"tool_name": "Read", "tool_input": {"file_path": "src/App.tsx"}},
            environment,
        )
        self.run_mode("user-prompt", "codex", {"prompt": "승인"}, environment)

        allowed = self.run_mode(
            "pre-tool",
            "codex",
            {"tool_name": "Bash", "tool_input": {"command": create}},
            environment,
        )
        mismatch = self.run_mode(
            "pre-tool",
            "codex",
            {
                "tool_name": "Bash",
                "tool_input": {
                    "command": create.replace(digest, "b" * 64),
                },
            },
            environment,
        )

        self.assertEqual(allowed.returncode, 0, allowed.stderr)
        self.assertEqual(allowed.stdout, "")
        mismatch_reason = json.loads(mismatch.stdout)["hookSpecificOutput"][
            "permissionDecisionReason"
        ]
        self.assertIn("현재 proposal SHA-256", mismatch_reason)

    def test_preserve_requires_handoff_and_contributor_cannot_finish(self) -> None:
        bundle = self.root / "central-bundle"
        script = (
            bundle
            / "policy/.agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py"
        )
        script.parent.mkdir(parents=True)
        script.write_text("# trusted test fixture\n", encoding="utf-8")
        environment = {
            "ASAN_AGENT_POLICY_MODE": "inject",
            "ASAN_AGENT_POLICY_PROJECT": "user-ui",
            "ASAN_AGENT_POLICY_BUNDLE_ROOT": str(bundle),
            "ASAN_ARTIFACT_RESPONSIBILITY": "contributor",
            "ASAN_SESSION_DIR": ".claude/logs/sessions/2026-09-03-preserved",
        }
        preserve = f"python3 {script} preserve --reason handoff"
        missing = self.run_mode(
            "pre-tool",
            "claude",
            {"tool_name": "Bash", "tool_input": {"command": preserve}},
            environment,
        )
        self.assertEqual(missing.returncode, 2)
        self.assertIn("handoff", missing.stderr)

        relative = ".claude/logs/sessions/2026-09-03-preserved/handoff.md"
        binding = self.run_mode(
            "pre-tool",
            "claude",
            {"tool_name": "Write", "tool_input": {"file_path": relative}},
            environment,
        )
        self.assertEqual(binding.returncode, 0, binding.stderr)
        handoff = self.root / relative
        handoff.parent.mkdir(parents=True)
        handoff.write_text("다음 세션이 재개할 상태와 검증 결과를 기록했습니다.\n", encoding="utf-8")
        self.record_common_readiness("claude")
        allowed = self.run_mode(
            "pre-tool",
            "claude",
            {"tool_name": "Bash", "tool_input": {"command": preserve}},
            environment,
        )
        self.assertEqual(allowed.returncode, 0, allowed.stderr)

        finish_proposal = f"python3 {script} finish-proposal --verify-command 'npm run test'"
        contributor = self.run_mode(
            "pre-tool",
            "claude",
            {"tool_name": "Bash", "tool_input": {"command": finish_proposal}},
            environment,
        )
        self.assertEqual(contributor.returncode, 2)
        self.assertIn("owner assignment", contributor.stderr)

    def test_bash_artifact_write_is_rejected_without_structured_binding(self) -> None:
        command = (
            "cat <<'EOF' > .claude/logs/sessions/2026-09-02-task/handoff.md\n"
            "handoff content\nEOF"
        )

        result = self.run_guard("claude", "Bash", {"command": command})

        self.assertEqual(result.returncode, 2)
        self.assertIn("구조화된 파일 쓰기 도구", result.stderr)
        self.assertIn("귀속", result.stderr)

    def test_git_cannot_stage_another_host_or_session_artifact(self) -> None:
        current = ".claude/logs/sessions/2026-09-03-current/plan.md"
        self.assertEqual(
            self.run_guard("claude", "Write", {"file_path": current}).returncode,
            0,
        )
        targets = (
            ".codex/logs/sessions/2026-09-03-foreign/plan.md",
            ".claude/logs/sessions/2026-09-03-other/plan.md",
        )
        for relative in targets:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("다른 소유자의 산출물입니다.\n", encoding="utf-8")
            with self.subTest(relative=relative):
                denied = self.run_guard(
                    "claude",
                    "Bash",
                    {"command": f"git add -- {relative}"},
                )
                self.assertEqual(denied.returncode, 2)
                self.assertIn("산출물", denied.stderr)
            target.unlink()

    def test_same_session_uses_the_approved_isolated_worktree_as_mutation_boundary(self) -> None:
        subprocess.run(["git", "branch", "-M", "sy-main"], cwd=self.root, check=True)
        subprocess.run(["git", "add", ".agent-policy/manifest.json"], cwd=self.root, check=True)
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
            cwd=self.root,
            check=True,
        )
        runtime_guard = self.rendered_guard()
        branch_source = (runtime_guard.parent / "branch_guard.py").read_bytes()
        rendered_branch_guard = ModuleType("isolated_worktree_branch_guard")
        rendered_branch_guard.__file__ = str(runtime_guard.parent / "branch_guard.py")
        exec(
            compile(branch_source, rendered_branch_guard.__file__, "exec"),
            rendered_branch_guard.__dict__,
        )
        branch = "task/same-session-worktree"
        worktree = self.root.parent / f"approved-worktree-{self.session_id}"
        parent_head = rendered_branch_guard.head(self.root, "sy-main")
        subprocess.run(
            ["git", "worktree", "add", "-q", "-b", branch, str(worktree), parent_head],
            cwd=self.root,
            check=True,
        )
        second_worktree: Path | None = None
        try:
            roles = ("logic",)
            scopes = ("src",)
            purpose = "같은 세션의 격리 worktree 경계 검증"
            reason = "dirty 기준 폴더와 task index를 분리"
            contract = rendered_branch_guard.canonical_contract(
                branch,
                purpose,
                "sy-main",
                parent_head,
                "sy-main",
                scopes,
                reason,
                str(worktree.resolve()),
                roles,
                "opencode",
            )
            digest = rendered_branch_guard.contract_sha256(contract)
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
                "git-integrator": "opencode",
                "state": "ACTIVE",
                "worktree": str(worktree.resolve()),
            }.items():
                subprocess.run(
                    ["git", "config", f"branch.{branch}.asan-{field}", value],
                    cwd=self.root,
                    check=True,
                )
            for role in roles:
                subprocess.run(
                    ["git", "config", "--add", f"branch.{branch}.asan-role", role],
                    cwd=self.root,
                    check=True,
                )
            for scope in scopes:
                subprocess.run(
                    ["git", "config", "--add", f"branch.{branch}.asan-scope", scope],
                    cwd=self.root,
                    check=True,
                )

            environment = dict(os.environ)
            environment.update(
                {
                    "ASAN_AGENT_POLICY_MODE": "inject",
                    "ASAN_AGENT_POLICY_PROJECT": "user-ui",
                    "ASAN_AGENT_POLICY_BUNDLE_ROOT": str(runtime_guard.parents[2]),
                    "ASAN_AGENT_POLICY_ROLE": "logic",
                }
            )

            def run_rendered(
                event_root: Path,
                tool_name: str,
                tool_input: dict[str, object],
            ) -> subprocess.CompletedProcess[str]:
                return subprocess.run(
                    ["python3", "-I", str(runtime_guard), "pre-tool", "opencode"],
                    input=json.dumps(
                        {
                            "cwd": str(event_root),
                            "session_id": self.session_id,
                            "tool_name": tool_name,
                            "tool_input": tool_input,
                        }
                    ),
                    cwd=event_root,
                    env=environment,
                    text=True,
                    capture_output=True,
                    check=False,
                )

            source = worktree / "src/feature.ts"
            self.record_common_readiness("opencode")
            source_binding = run_rendered(
                self.root,
                "Write",
                {"file_path": str(source)},
            )
            self.assertEqual(source_binding.returncode, 0, source_binding.stderr)
            source.parent.mkdir(parents=True)
            source.write_text("export const feature = true\n", encoding="utf-8")

            artifact = worktree / ".opencode/logs/sessions/2026-09-03-isolated/plan.md"
            bound = run_rendered(self.root, "Write", {"file_path": str(artifact)})
            self.assertEqual(bound.returncode, 0, bound.stderr)
            allowed = run_rendered(
                self.root,
                "Bash",
                {"command": f"git -C {worktree} add -- src/feature.ts"},
            )
            self.assertEqual(allowed.returncode, 0, allowed.stderr)

            denied = run_rendered(
                worktree,
                "Bash",
                {"command": f"git -C {self.root} add -- .agent-policy/manifest.json"},
            )
            self.assertEqual(denied.returncode, 2)
            self.assertIn("assignment 권한", denied.stderr)

            self.write_complete_artifacts(artifact.parent)
            subprocess.run(["git", "add", "."], cwd=worktree, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=Policy Test",
                    "-c",
                    "user.email=policy@example.com",
                    "commit",
                    "-qm",
                    "first isolated task",
                ],
                cwd=worktree,
                check=True,
            )
            subprocess.run(["git", "merge", "-q", "--ff-only", branch], cwd=self.root, check=True)
            subprocess.run(
                ["git", "config", f"branch.{branch}.asan-state", "CLOSED"],
                cwd=self.root,
                check=True,
            )

            second_branch = "task/same-session-next"
            second_worktree = self.root.parent / f"next-worktree-{self.session_id}"
            second_parent_head = rendered_branch_guard.head(self.root, "sy-main")
            subprocess.run(
                [
                    "git",
                    "worktree",
                    "add",
                    "-q",
                    "-b",
                    second_branch,
                    str(second_worktree),
                    second_parent_head,
                ],
                cwd=self.root,
                check=True,
            )
            second_purpose = "CLOSED 뒤 같은 세션의 다음 task 검증"
            second_reason = "이전 task의 merge와 산출물 완료 확인"
            second_contract = rendered_branch_guard.canonical_contract(
                second_branch,
                second_purpose,
                "sy-main",
                second_parent_head,
                "sy-main",
                scopes,
                second_reason,
                str(second_worktree.resolve()),
                roles,
                "opencode",
            )
            second_digest = rendered_branch_guard.contract_sha256(second_contract)
            for field, value in {
                "contract-version": "3",
                "task-id": second_branch.removeprefix("task/"),
                "purpose": second_purpose,
                "parent": "sy-main",
                "parent-head": second_parent_head,
                "merge-target": "sy-main",
                "proposal": f"asan-v3:{second_digest}",
                "contract-sha256": second_digest,
                "reason": second_reason,
                "git-integrator": "opencode",
                "state": "ACTIVE",
                "worktree": str(second_worktree.resolve()),
            }.items():
                subprocess.run(
                    ["git", "config", f"branch.{second_branch}.asan-{field}", value],
                    cwd=self.root,
                    check=True,
                )
            for role in roles:
                subprocess.run(
                    ["git", "config", "--add", f"branch.{second_branch}.asan-role", role],
                    cwd=self.root,
                    check=True,
                )
            for scope in scopes:
                subprocess.run(
                    ["git", "config", "--add", f"branch.{second_branch}.asan-scope", scope],
                    cwd=self.root,
                    check=True,
                )
            next_artifact = (
                second_worktree
                / ".opencode/logs/sessions/2026-09-03-isolated-next/plan.md"
            )
            rebound = run_rendered(
                self.root,
                "Write",
                {"file_path": str(next_artifact)},
            )
            self.assertEqual(rebound.returncode, 0, rebound.stderr)
        finally:
            if second_worktree is not None:
                subprocess.run(
                    ["git", "worktree", "remove", "--force", str(second_worktree)],
                    cwd=self.root,
                    check=False,
                    capture_output=True,
                )
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(worktree)],
                cwd=self.root,
                check=False,
                capture_output=True,
            )

    def test_legacy_documentation_stop_never_blocks_committed_changes(self) -> None:
        subprocess.run(["git", "branch", "-M", "sy-main"], cwd=self.root, check=True)
        subprocess.run(["git", "add", ".agent-policy/manifest.json"], cwd=self.root, check=True)
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
            cwd=self.root,
            check=True,
        )
        parent_head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        subprocess.run(["git", "switch", "-qc", "task/committed-change"], cwd=self.root, check=True)
        subprocess.run(
            [
                "git",
                "config",
                "branch.task/committed-change.asan-parent-head",
                parent_head,
            ],
            cwd=self.root,
            check=True,
        )
        source = self.root / "src/committed.ts"
        source.parent.mkdir(parents=True)
        source.write_text("export const committed = true\n", encoding="utf-8")
        subprocess.run(["git", "add", "src/committed.ts"], cwd=self.root, check=True)
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Policy Test",
                "-c",
                "user.email=policy@example.com",
                "commit",
                "-qm",
                "committed change",
            ],
            cwd=self.root,
            check=True,
        )

        self.assertEqual(
            subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.root,
                capture_output=True,
                text=True,
                check=True,
            ).stdout,
            "",
        )
        for stop_hook_active in (False, True):
            with self.subTest(stop_hook_active=stop_hook_active):
                result = self.run_mode(
                    "documentation-stop",
                    "codex",
                    {"stop_hook_active": stop_hook_active},
                )
                self.assertEqual(json.loads(result.stdout), {})

    def test_active_session_directory_cannot_change_before_close(self) -> None:
        first = ".claude/logs/sessions/2026-09-01-first/handoff.md"
        second = ".claude/logs/sessions/2026-09-02-second/handoff.md"
        self.assertEqual(
            self.run_guard("claude", "Write", {"file_path": first}).returncode,
            0,
        )

        changed = self.run_guard("claude", "Write", {"file_path": second})

        self.assertEqual(changed.returncode, 2)
        self.assertIn("CLOSED", changed.stderr)
        self.assertIn("별도 worktree와 세션", changed.stderr)

    def test_claude_legacy_documentation_stop_is_nonblocking(self) -> None:
        source = self.root / "src/App.tsx"
        source.parent.mkdir(parents=True)
        source.write_text("export const App = () => null\n", encoding="utf-8")

        result = self.run_mode("documentation-stop", "claude", {"stop_hook_active": True})

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {})

    def test_completion_workflow_still_requires_full_owner_artifacts(self) -> None:
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        subprocess.run(
            ["git", "config", f"branch.{branch}.asan-contract-version", "2"],
            cwd=self.root,
            check=True,
        )
        subprocess.run(
            ["git", "config", f"branch.{branch}.asan-artifact-mode", "full"],
            cwd=self.root,
            check=True,
        )
        source = self.root / "src/App.tsx"
        source.parent.mkdir(parents=True)
        source.write_text("export const App = () => null\n", encoding="utf-8")
        bundle = self.root / "central-bundle"
        script = (
            bundle
            / "policy/.agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py"
        )
        script.parent.mkdir(parents=True)
        script.write_text("# trusted test fixture\n", encoding="utf-8")
        environment = {
            "ASAN_AGENT_POLICY_MODE": "inject",
            "ASAN_AGENT_POLICY_PROJECT": "user-ui",
            "ASAN_AGENT_POLICY_BUNDLE_ROOT": str(bundle),
            "ASAN_ARTIFACT_RESPONSIBILITY": "owner",
            "ASAN_SESSION_DIR": ".codex/logs/sessions/2026-09-02-full",
        }
        relative = ".codex/logs/sessions/2026-09-02-full/handoff.md"
        binding = self.run_mode(
            "pre-tool",
            "codex",
            {"tool_name": "Write", "tool_input": {"file_path": relative}},
            environment,
        )
        self.assertEqual(binding.returncode, 0, binding.stderr)
        session = (self.root / relative).parent
        session.mkdir(parents=True)
        (session / "handoff.md").write_text("부분 인계 내용이 충분히 있습니다.\n", encoding="utf-8")
        finish_proposal = f"python3 {script} finish-proposal --verify-command 'npm run test'"

        handoff_only = self.run_mode(
            "pre-tool",
            "codex",
            {"tool_name": "Bash", "tool_input": {"command": finish_proposal}},
            environment,
        )

        handoff_reason = json.loads(handoff_only.stdout)["hookSpecificOutput"][
            "permissionDecisionReason"
        ]
        self.assertIn("필수 산출물 8종", handoff_reason)
        self.write_complete_artifacts(session)
        self.record_common_readiness("codex")
        complete = self.run_mode(
            "pre-tool",
            "codex",
            {"tool_name": "Bash", "tool_input": {"command": finish_proposal}},
            environment,
        )
        self.assertEqual(complete.returncode, 0, complete.stderr)
        self.assertEqual(complete.stdout, "")

    def test_closed_merged_task_can_rebind_same_session_to_next_task(self) -> None:
        subprocess.run(["git", "checkout", "-qb", "sy-main"], cwd=self.root, check=True)
        subprocess.run(["git", "add", ".agent-policy/manifest.json"], cwd=self.root, check=True)
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
            cwd=self.root,
            check=True,
        )
        rendered = render_project(load_project("user-ui"))
        bundle = self.root.parent / f"runtime-{self.session_id}"
        runtime = bundle / ".agent-policy/runtime"
        runtime.mkdir(parents=True)
        runtime_guard = runtime / "managed_policy_guard.py"
        runtime_guard.write_bytes(rendered[".agent-policy/runtime/managed_policy_guard.py"])
        branch_source = rendered[".agent-policy/runtime/branch_guard.py"]
        (runtime / "branch_guard.py").write_bytes(branch_source)
        contract = bundle / ".agent-policy/common/contracts/runtime-policy.json"
        contract.parent.mkdir(parents=True)
        contract.write_bytes(rendered[".agent-policy/common/contracts/runtime-policy.json"])
        branch_guard = ModuleType("test_branch_guard")
        branch_guard.__file__ = str(runtime / "branch_guard.py")
        exec(compile(branch_source, branch_guard.__file__, "exec"), branch_guard.__dict__)

        def configure(branch: str, parent: str) -> None:
            parent_head = branch_guard.head(self.root, parent)
            roles = ("documentation", "logic")
            proposal = branch_guard.proposal_id(
                branch,
                parent,
                parent_head,
                parent,
                "",
                roles,
                "claude",
                "full",
            )
            for field, value in {
                "contract-version": "2",
                "purpose": branch,
                "parent": parent,
                "parent-head": parent_head,
                "merge-target": parent,
                "proposal": proposal,
                "git-integrator": "claude",
                "artifact-mode": "full",
            }.items():
                subprocess.run(
                    ["git", "config", f"branch.{branch}.asan-{field}", value],
                    cwd=self.root,
                    check=True,
                )
            for role in roles:
                subprocess.run(
                    ["git", "config", "--add", f"branch.{branch}.asan-role", role],
                    cwd=self.root,
                    check=True,
                )
            subprocess.run(
                ["git", "config", "--add", f"branch.{branch}.asan-scope", "src"],
                cwd=self.root,
                check=True,
            )

        def run_rendered(file_path: str) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                ["python3", "-I", str(runtime_guard), "pre-tool", "claude"],
                input=json.dumps(
                    {
                        "cwd": str(self.root),
                        "session_id": self.session_id,
                        "tool_name": "Write",
                        "tool_input": {"file_path": file_path},
                    }
                ),
                text=True,
                capture_output=True,
                cwd=self.root,
                check=False,
            )

        subprocess.run(["git", "switch", "-qc", "task/first"], cwd=self.root, check=True)
        configure("task/first", "sy-main")
        first_relative = ".claude/logs/sessions/2026-09-02-first/plan.md"
        first_binding = run_rendered(first_relative)
        self.assertEqual(first_binding.returncode, 0, first_binding.stderr)
        first_session = (self.root / first_relative).parent
        first_session.mkdir(parents=True)
        self.write_complete_artifacts(first_session)
        source = self.root / "src/first.ts"
        source.parent.mkdir(parents=True)
        source.write_text("export const first = true\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Policy Test",
                "-c",
                "user.email=policy@example.com",
                "commit",
                "-qm",
                "first",
            ],
            cwd=self.root,
            check=True,
        )
        subprocess.run(["git", "switch", "-q", "sy-main"], cwd=self.root, check=True)
        subprocess.run(["git", "merge", "-q", "--ff-only", "task/first"], cwd=self.root, check=True)
        subprocess.run(["git", "switch", "-qc", "task/second"], cwd=self.root, check=True)
        configure("task/second", "sy-main")

        second = run_rendered(".claude/logs/sessions/2026-09-02-second/plan.md")

        self.assertEqual(second.returncode, 0, second.stderr)
