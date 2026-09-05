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

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from agent_policy.core import load_project, render_project


class BranchGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name) / "repository"
        self.root.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "sy-main"], cwd=self.root, check=True)
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
        self.rendered = render_project(load_project("user-ui"))
        source = self.rendered[".agent-policy/runtime/branch_guard.py"]
        self.guard = ModuleType("rendered_branch_guard")
        self.guard.__file__ = "rendered_branch_guard.py"
        exec(compile(source, self.guard.__file__, "exec"), self.guard.__dict__)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def configure_task_branch(self) -> str:
        parent_head = self.guard.head(self.root, "sy-main")
        branch = "task/render-policy"
        subprocess.run(["git", "switch", "-qc", branch], cwd=self.root, check=True)
        values = {
            "purpose": "중앙 정책 렌더링 검증",
            "parent": "sy-main",
            "parent-head": parent_head,
            "merge-target": "sy-main",
            "proposal": self.guard.proposal_id(branch, "sy-main", parent_head, "sy-main"),
        }
        for field, value in values.items():
            subprocess.run(
                ["git", "config", f"branch.{branch}.asan-{field}", value],
                cwd=self.root,
                check=True,
            )
        subprocess.run(
            ["git", "config", "--add", f"branch.{branch}.asan-scope", "src/shared/ui"],
            cwd=self.root,
            check=True,
        )
        return branch

    def configure_v3_isolated_task(self) -> tuple[str, Path]:
        branch = "task/isolated-context"
        worktree = Path(self.temporary_directory.name) / "approved-task-worktree"
        parent_head = self.guard.head(self.root, "sy-main")
        subprocess.run(
            ["git", "worktree", "add", "-q", "-b", branch, str(worktree), parent_head],
            cwd=self.root,
            check=True,
        )
        roles = ("logic",)
        scopes = ("src",)
        purpose = "실제 Git 대상 worktree 검증"
        reason = "기준 worktree와 task index를 분리"
        contract = self.guard.canonical_contract(
            branch,
            purpose,
            "sy-main",
            parent_head,
            "sy-main",
            scopes,
            reason,
            str(worktree.resolve()),
            roles,
            "codex",
        )
        digest = self.guard.contract_sha256(contract)
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
        return branch, worktree

    def configure_v3_task(
        self,
        branch: str,
        parent: str,
        scopes: tuple[str, ...] = ("src",),
    ) -> str:
        parent_head = self.guard.head(self.root, parent)
        subprocess.run(["git", "branch", branch, parent_head], cwd=self.root, check=True)
        roles = ("logic",)
        purpose = f"{branch} 계보 권한 검증"
        reason = f"{parent}에서 승인된 하위 작업 분리"
        contract = self.guard.canonical_contract(
            branch,
            purpose,
            parent,
            parent_head,
            parent,
            scopes,
            reason,
            "",
            roles,
            "codex",
        )
        digest = self.guard.contract_sha256(contract)
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
            "git-integrator": "codex",
            "state": "ACTIVE",
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
        return branch

    def install_workflow(self) -> Path:
        runtime_source = self.rendered[".agent-policy/runtime/branch_guard.py"]
        runtime = self.root / ".agent-policy/runtime/branch_guard.py"
        runtime.parent.mkdir(parents=True)
        runtime.write_bytes(runtime_source)
        contract = self.root / ".agent-policy/common/contracts/runtime-policy.json"
        contract.parent.mkdir(parents=True, exist_ok=True)
        contract.write_bytes(
            self.rendered[".agent-policy/common/contracts/runtime-policy.json"]
        )
        stale_guard = self.root / ".codex/hooks/branch_guard.py"
        stale_guard.parent.mkdir(parents=True)
        stale_guard.write_bytes(
            b"\n".join(
                line
                for line in runtime_source.splitlines()
                if not line.startswith(b"FULL_SHA_PATTERN =")
            )
            + b"\n"
        )
        workflow = (
            self.root
            / ".agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py"
        )
        workflow.parent.mkdir(parents=True)
        workflow.write_bytes(
            self.rendered[
                ".agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py"
            ]
        )
        return workflow

    def install_inject_workflow(self) -> Path:
        policy_root = Path(self.temporary_directory.name) / "bundle/policy"
        runtime = policy_root / ".agent-policy/runtime/branch_guard.py"
        runtime.parent.mkdir(parents=True)
        runtime.write_bytes(self.rendered[".agent-policy/runtime/branch_guard.py"])
        contract = policy_root / ".agent-policy/common/contracts/runtime-policy.json"
        contract.parent.mkdir(parents=True, exist_ok=True)
        contract.write_bytes(
            self.rendered[".agent-policy/common/contracts/runtime-policy.json"]
        )
        workflow = (
            policy_root
            / ".agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py"
        )
        workflow.parent.mkdir(parents=True)
        workflow.write_bytes(
            self.rendered[
                ".agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py"
            ]
        )
        return workflow

    def test_base_branch_rejects_repository_writes(self) -> None:
        denial = self.guard.active_branch_denial(self.root, ("src/App.tsx",))
        self.assertIsNotNone(denial)
        self.assertIn("기준 브랜치", denial)

    def test_approved_task_branch_enforces_scope_and_reports_context(self) -> None:
        branch = self.configure_task_branch()
        self.assertIsNone(
            self.guard.active_branch_denial(
                self.root,
                ("src/shared/ui/button/Button.tsx",),
            )
        )
        for artifact in (
            ".codex/logs/sessions/task/plan.md",
            ".claude/logs/sessions/task/plan.md",
            ".opencode/logs/sessions/task/plan.md",
        ):
            self.assertIsNone(self.guard.active_branch_denial(self.root, (artifact,)))
        denial = self.guard.active_branch_denial(self.root, ("src/App.tsx",))
        self.assertIsNotNone(denial)
        self.assertIn("승인된 작업 범위 밖", denial)

        context = self.guard.branch_context(self.root)
        self.assertIn(branch, context)
        self.assertIn("src/shared/ui", context)
        self.assertIn("sy-main", context)

    def test_parent_branch_can_advance_without_invalidating_approved_lineage(self) -> None:
        branch = self.configure_task_branch()
        subprocess.run(["git", "switch", "-q", "sy-main"], cwd=self.root, check=True)
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
                "base advances",
            ],
            cwd=self.root,
            check=True,
        )
        subprocess.run(["git", "switch", "-q", branch], cwd=self.root, check=True)

        self.assertIsNone(
            self.guard.active_branch_denial(
                self.root,
                ("src/shared/ui/button/Button.tsx",),
            )
        )

    def test_assignment_authority_is_inherited_only_by_v3_descendants(self) -> None:
        parent = self.configure_v3_task("task/meeting-reserve-ui", "sy-main")
        child = self.configure_v3_task("task/reserve-option-lazy-load", parent)
        grandchild = self.configure_v3_task("task/reserve-option-api", child)
        unrelated = self.configure_v3_task("task/unrelated-reserve", "sy-main")

        self.assertTrue(self.guard.assignment_includes_branch(self.root, parent, parent))
        self.assertTrue(self.guard.assignment_includes_branch(self.root, parent, child))
        self.assertTrue(self.guard.assignment_includes_branch(self.root, parent, grandchild))
        self.assertFalse(self.guard.assignment_includes_branch(self.root, child, parent))
        self.assertFalse(self.guard.assignment_includes_branch(self.root, child, unrelated))
        self.assertFalse(self.guard.assignment_includes_branch(self.root, parent, "sy-main"))

        subprocess.run(["git", "switch", "-q", child], cwd=self.root, check=True)
        source = self.root / "src/merged-child.ts"
        source.parent.mkdir(parents=True)
        source.write_text("export const mergedChild = true\n", encoding="utf-8")
        subprocess.run(["git", "add", "src/merged-child.ts"], cwd=self.root, check=True)
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
        subprocess.run(["git", "merge", "-q", "--ff-only", child], cwd=self.root, check=True)

        self.assertTrue(self.guard.assignment_includes_branch(self.root, parent, child))
        self.assertTrue(self.guard.assignment_includes_branch(self.root, parent, grandchild))

    def test_assignment_root_can_mutate_and_switch_within_descendant_family(self) -> None:
        parent = self.configure_v3_task("task/meeting-reserve-ui", "sy-main")
        child = self.configure_v3_task("task/reserve-option-lazy-load", parent)
        grandchild = self.configure_v3_task("task/reserve-option-api", child)
        unrelated = self.configure_v3_task("task/unrelated-reserve", "sy-main")
        subprocess.run(["git", "switch", "-q", child], cwd=self.root, check=True)
        source = self.root / "src/child.ts"
        source.parent.mkdir(parents=True)
        source.write_text("export const child = true\n", encoding="utf-8")

        self.assertIsNone(
            self.guard.command_denial(
                self.root,
                "git add -- src/child.ts",
                host="codex",
                expected_branch=parent,
            )
        )
        denied_mutation = self.guard.command_denial(
            self.root,
            "git add -- src/child.ts",
            host="codex",
            expected_branch=unrelated,
        )
        self.assertIsNotNone(denied_mutation)
        self.assertIn("권한 root", denied_mutation)

        source.unlink()
        subprocess.run(
            ["git", "config", f"branch.{parent}.asan-state", "PRESERVED"],
            cwd=self.root,
            check=True,
        )
        inactive_root_denial = self.guard.command_denial(
            self.root,
            "git add -- src/child.ts",
            host="codex",
            expected_branch=parent,
        )
        self.assertIsNotNone(inactive_root_denial)
        self.assertIn("권한 계보", inactive_root_denial)
        subprocess.run(
            ["git", "config", f"branch.{parent}.asan-state", "ACTIVE"],
            cwd=self.root,
            check=True,
        )
        self.assertIsNone(
            self.guard.command_denial(
                self.root,
                f"git switch {grandchild}",
                host="codex",
                expected_branch=parent,
            )
        )
        self.assertIsNone(
            self.guard.command_denial(
                self.root,
                f"git switch {parent}",
                host="codex",
                expected_branch=parent,
            )
        )
        for expected, target in (
            (parent, unrelated),
            (parent, "sy-main"),
            (child, parent),
        ):
            with self.subTest(expected=expected, target=target):
                denial = self.guard.command_denial(
                    self.root,
                    f"git switch {target}",
                    host="codex",
                    expected_branch=expected,
                )
                self.assertIsNotNone(denial)
                self.assertIn("권한 계보 밖", denial)

    def test_short_parent_sha_is_rejected_with_actionable_message(self) -> None:
        branch = self.configure_task_branch()
        short_head = self.guard.head(self.root, "sy-main")[:12]
        subprocess.run(
            ["git", "config", f"branch.{branch}.asan-parent-head", short_head],
            cwd=self.root,
            check=True,
        )
        subprocess.run(
            [
                "git",
                "config",
                f"branch.{branch}.asan-proposal",
                self.guard.proposal_id(branch, "sy-main", short_head, "sy-main"),
            ],
            cwd=self.root,
            check=True,
        )

        denial = self.guard.active_branch_denial(
            self.root,
            ("src/shared/ui/button/Button.tsx",),
        )

        self.assertIsNotNone(denial)
        self.assertIn("40자리 전체 SHA", denial)

    def test_uncommitted_task_branch_is_not_reported_as_merged(self) -> None:
        self.configure_task_branch()

        context = self.guard.branch_context(self.root)

        self.assertIn("- merge 상태: 미병합", context)

    def test_v2_contract_records_roles_and_limits_git_integrator(self) -> None:
        parent_head = self.guard.head(self.root, "sy-main")
        branch = "task/role-contract"
        roles = ("documentation", "logic")
        proposal = self.guard.proposal_id(
            branch,
            "sy-main",
            parent_head,
            "sy-main",
            "",
            roles,
            "codex",
            "full",
        )
        subprocess.run(["git", "switch", "-qc", branch], cwd=self.root, check=True)
        for field, value in {
            "contract-version": "2",
            "purpose": "역할 계약 검증",
            "parent": "sy-main",
            "parent-head": parent_head,
            "merge-target": "sy-main",
            "proposal": proposal,
            "git-integrator": "codex",
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

        denied = self.guard.command_denial(self.root, "git add -- src", host="claude")
        allowed = self.guard.command_denial(self.root, "git add -- src", host="codex")
        context = self.guard.branch_context(self.root)

        self.assertIn("Git 통합 담당자는 codex", denied)
        self.assertIsNone(allowed)
        self.assertIn("확인된 역할: documentation, logic", context)
        self.assertIn("산출물 모드: full", context)

    def test_checkout_path_restore_and_compound_merge_are_classified(self) -> None:
        self.configure_task_branch()
        target = self.root / "src/shared/ui/button/Button.tsx"
        target.parent.mkdir(parents=True)
        target.write_text("export const Button = () => null\n", encoding="utf-8")

        checkout_denial = self.guard.command_denial(
            self.root,
            "git checkout -- src/shared/ui/button/Button.tsx",
        )
        restore_denial = self.guard.command_denial(
            self.root,
            "git restore -- src/shared/ui/button/Button.tsx",
        )
        compound_denial = self.guard.command_denial(
            self.root,
            "git checkout sy-main && git merge task/render-policy",
        )

        self.assertIsNotNone(checkout_denial)
        self.assertIn("git restore", checkout_denial)
        self.assertIsNone(restore_denial)
        self.assertIsNotNone(compound_denial)
        self.assertIn("별도 명령", compound_denial)

    def test_git_c_targets_the_actual_approved_worktree_independent_of_session_cwd(self) -> None:
        branch, worktree = self.configure_v3_isolated_task()
        source = worktree / "src/feature.ts"
        source.parent.mkdir(parents=True)
        source.write_text("export const feature = true\n", encoding="utf-8")
        task_command = f"git -C {shlex.quote(str(worktree))} add -- src/feature.ts"
        primary_command = f"git -C {shlex.quote(str(self.root))} add -- src/feature.ts"

        self.assertIsNone(
            self.guard.command_denial(
                self.root,
                task_command,
                host="codex",
                expected_branch=branch,
            )
        )
        denied = self.guard.command_denial(
            worktree,
            primary_command,
            host="codex",
            expected_branch=branch,
        )
        self.assertIsNotNone(denied)
        self.assertIn("assignment 권한", denied)

        self.assertIsNone(
            self.guard.command_denial(
                self.root,
                "git add -- src/feature.ts",
                host="codex",
                execution_cwd=worktree,
                expected_branch=branch,
            )
        )
        denied_by_workdir = self.guard.command_denial(
            worktree,
            "git add -- src/feature.ts",
            host="codex",
            execution_cwd=self.root,
            expected_branch=branch,
        )
        self.assertIsNotNone(denied_by_workdir)

    def test_explicit_git_repository_options_are_resolved_or_fail_closed(self) -> None:
        branch, worktree = self.configure_v3_isolated_task()
        source = worktree / "src/feature.ts"
        source.parent.mkdir(parents=True)
        source.write_text("export const feature = true\n", encoding="utf-8")
        git_directory = subprocess.run(
            ["git", "rev-parse", "--absolute-git-dir"],
            cwd=worktree,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        explicit = (
            f"git --git-dir={shlex.quote(git_directory)} "
            f"--work-tree={shlex.quote(str(worktree))} add -- src/feature.ts"
        )
        self.assertIsNone(
            self.guard.command_denial(
                self.root,
                explicit,
                host="codex",
                expected_branch=branch,
            )
        )
        primary_git_directory = subprocess.run(
            ["git", "rev-parse", "--absolute-git-dir"],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        for command in (
            f"git --git-dir={shlex.quote(git_directory)} add -- src/feature.ts",
            (
                f"git --git-dir={shlex.quote(primary_git_directory)} "
                f"--work-tree={shlex.quote(str(worktree))} add -- src/feature.ts"
            ),
            f"GIT_DIR={shlex.quote(git_directory)} GIT_WORK_TREE={shlex.quote(str(worktree))} git add -- src/feature.ts",
            f"cd {shlex.quote(str(worktree))} && git add -- src/feature.ts",
            f"env -C {shlex.quote(str(worktree))} git add -- src/feature.ts",
        ):
            with self.subTest(command=command):
                denial = self.guard.command_denial(
                    self.root,
                    command,
                    host="codex",
                    expected_branch=branch,
                )
                self.assertIsNotNone(denial)

    def test_unapproved_branch_switch_and_compound_followup_are_rejected(self) -> None:
        self.configure_task_branch()
        subprocess.run(["git", "branch", "scratch"], cwd=self.root, check=True)

        single = self.guard.command_denial(self.root, "git switch scratch")
        compound = self.guard.command_denial(
            self.root,
            "git switch scratch && git commit --allow-empty -m bypass",
        )

        self.assertIsNotNone(single)
        self.assertIn("승인 계약", single)
        self.assertIsNotNone(compound)
        self.assertIn("복합 명령", compound)

    def test_git_control_files_are_never_in_branch_scope(self) -> None:
        branch = self.configure_task_branch()
        subprocess.run(
            ["git", "config", "--add", f"branch.{branch}.asan-scope", "."],
            cwd=self.root,
            check=True,
        )

        denial = self.guard.active_branch_denial(self.root, (".git/config",))

        self.assertIsNotNone(denial)
        self.assertIn("Git 제어 경로", denial)

    def test_dirty_repository_can_create_an_approved_isolated_worktree(self) -> None:
        workflow = self.install_workflow()
        worktree = Path(self.temporary_directory.name) / "isolated-worktree"
        (self.root / "existing-session.txt").write_text("dirty\n", encoding="utf-8")
        proposal = subprocess.run(
            [
                "python3",
                str(workflow),
                "proposal",
                "--branch",
                "task/isolated-policy",
                "--purpose",
                "격리 정책 검증",
                "--parent",
                "sy-main",
                "--scope",
                "src/shared/ui",
                "--reason",
                "다른 세션의 dirty 변경과 무관함",
                "--worktree",
                str(worktree),
                "--role",
                "ui",
                "--git-integrator",
                "claude",
            ],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proposal.returncode, 0, proposal.stderr)
        proposal_path = next(
            line.removeprefix("- canonical proposal 파일: ")
            for line in proposal.stdout.splitlines()
            if line.startswith("- canonical proposal 파일: ")
        )
        proposal_sha256 = next(
            line.removeprefix("- canonical proposal SHA-256: ")
            for line in proposal.stdout.splitlines()
            if line.startswith("- canonical proposal SHA-256: ")
        )

        created = subprocess.run(
            [
                "python3",
                str(workflow),
                "create",
                "--proposal-file",
                proposal_path,
                "--proposal-sha256",
                proposal_sha256,
            ],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(created.returncode, 0, created.stderr)
        self.assertEqual(self.guard.current_branch(self.root), "sy-main")
        self.assertEqual(self.guard.current_branch(worktree), "task/isolated-policy")
        contract = json.loads(Path(proposal_path).read_text(encoding="utf-8"))
        self.assertRegex(contract["parent_head"], r"^[0-9a-f]{40}$")
        self.assertEqual(contract["worktree"], str(worktree.resolve()))
        self.assertRegex(proposal_sha256, r"^[0-9a-f]{64}$")

    def test_inject_snapshot_uses_runtime_guard_instead_of_stale_consumer(self) -> None:
        _ = self.install_workflow()
        workflow = self.install_inject_workflow()
        environment = dict(os.environ)
        environment.update(
            {
                "ASAN_AGENT_POLICY_MODE": "inject",
                "ASAN_AGENT_POLICY_BUNDLE_ROOT": str(workflow.parents[5].parent),
                "ASAN_AGENT_POLICY_PROJECT": "user-ui",
            }
        )

        proposal = subprocess.run(
            [
                "python3",
                str(workflow),
                "proposal",
                "--branch",
                "task/snapshot-runtime",
                "--purpose",
                "정책 스냅샷 guard 검증",
                "--parent",
                "sy-main",
                "--scope",
                "src/shared/ui",
                "--reason",
                "stale 소비자 guard보다 스냅샷 runtime을 우선함",
                "--role",
                "orchestration",
                "--git-integrator",
                "codex",
            ],
            cwd=self.root,
            capture_output=True,
            text=True,
            env=environment,
            check=False,
        )

        self.assertEqual(proposal.returncode, 0, proposal.stderr)
        self.assertIn(self.guard.head(self.root, "sy-main"), proposal.stdout)
        self.assertNotIn("AttributeError", proposal.stderr)

    def test_inject_snapshot_does_not_fall_back_when_runtime_is_incompatible(self) -> None:
        _ = self.install_workflow()
        workflow = self.install_inject_workflow()
        runtime = workflow.parents[5] / "runtime/branch_guard.py"
        runtime.write_bytes(
            b"\n".join(
                line
                for line in runtime.read_bytes().splitlines()
                if not line.startswith(b"FULL_SHA_PATTERN =")
            )
            + b"\n"
        )
        environment = dict(os.environ)
        environment.update(
            {
                "ASAN_AGENT_POLICY_MODE": "inject",
                "ASAN_AGENT_POLICY_BUNDLE_ROOT": str(workflow.parents[6]),
                "ASAN_AGENT_POLICY_PROJECT": "user-ui",
            }
        )

        context = subprocess.run(
            ["python3", str(workflow), "context"],
            cwd=self.root,
            capture_output=True,
            text=True,
            env=environment,
            check=False,
        )

        self.assertNotEqual(context.returncode, 0)
        self.assertIn("정책 스냅샷", context.stderr)
        self.assertIn("FULL_SHA_PATTERN", context.stderr)
        self.assertNotIn("AttributeError", context.stderr)

    def test_dirty_direct_branch_creation_points_to_isolated_worktree(self) -> None:
        (self.root / "existing-session.txt").write_text("dirty\n", encoding="utf-8")

        denial = self.guard.command_denial(
            self.root,
            "git switch -c task/unrelated-ui sy-main",
        )

        self.assertIsNotNone(denial)
        self.assertIn("--worktree", denial)
        self.assertIn("임의로 commit", denial)

    def test_history_rewriting_git_commands_are_rejected(self) -> None:
        self.configure_task_branch()
        for command in (
            "git reset --hard",
            "git -C . reset --hard",
            "git push",
            "git -C . push origin HEAD",
            "sh -c 'git push origin HEAD'",
            "git -c alias.ship=push ship origin HEAD",
            "git rebase sy-main",
            "git stash",
        ):
            with self.subTest(command=command):
                denial = self.guard.command_denial(self.root, command)
                self.assertIsNotNone(denial)
                if "push" in command or "--hard" in command:
                    self.assertIn("사용자", denial)

    def test_ref_mutation_aliases_and_implicit_branch_creation_are_rejected(self) -> None:
        self.configure_task_branch()
        rejected = (
            "git symbolic-ref HEAD refs/heads/sy-main",
            "git branch --track task/tracked sy-main",
            "git branch -f task/render-policy sy-main",
            "git branch -vf task/render-policy sy-main",
            "git checkout --orphan task/new-root",
            "git checkout -qbtask/new-root sy-main",
            "git switch --orphan task/new-root",
            "git switch -qctask/new-root sy-main",
            "git fetch origin +main:refs/heads/sy-main",
            "git fetch --prune origin",
            "git fetch -vp origin",
            "git commit -am tracked-change",
            "git commit -qamtracked-change",
            "git commit -- src/shared/ui/button/Button.tsx",
            "git add src/shared/ui/button/Button.tsx",
            "git merge --abort",
            "git merge --continue",
            "git merge --quit",
        )
        for command in rejected:
            with self.subTest(command=command):
                self.assertIsNotNone(self.guard.command_denial(self.root, command))

        self.assertIsNone(
            self.guard.command_denial(self.root, "git symbolic-ref --quiet --short HEAD")
        )
        self.assertIsNone(self.guard.command_denial(self.root, "git fetch origin sy-main"))
        self.assertIsNone(
            self.guard.command_denial(
                self.root,
                "git add -- src/shared/ui/button/Button.tsx",
            )
        )
        self.assertIsNone(self.guard.command_denial(self.root, "git commit -qm 'safe message'"))

    def test_v3_proposal_digest_covers_all_mutable_contract_fields(self) -> None:
        parent_head = self.guard.head(self.root, "sy-main")
        base = {
            "branch": "task/contract-digest",
            "parent": "sy-main",
            "parent_head": parent_head,
            "merge_target": "sy-main",
            "worktree": "",
            "roles": ("logic",),
            "git_integrator": "codex",
            "purpose": "계약 digest 검증",
            "scopes": ("src",),
            "reason": "독립 기능 작업",
        }
        original = self.guard.proposal_id(**base)
        variants = (
            {"purpose": "다른 목적"},
            {"scopes": ("src", "tests")},
            {"reason": "다른 분기 근거"},
            {"roles": ("ui",)},
            {"git_integrator": "claude"},
            {"worktree": "/tmp/other-worktree"},
        )
        self.assertRegex(original, r"^asan-v3:[0-9a-f]{64}$")
        for changed in variants:
            with self.subTest(changed=changed):
                self.assertNotEqual(original, self.guard.proposal_id(**(base | changed)))

    def test_cross_host_artifact_write_is_read_only_and_unknown_is_scoped(self) -> None:
        self.configure_task_branch()
        own = ".claude/logs/sessions/2026-09-03-task/plan.md"
        foreign = ".codex/logs/sessions/2026-09-03-task/plan.md"
        unknown = ".agent-policy/logs/unknown/sessions/2026-09-03-task/unknown/note.md"

        self.assertIsNone(self.guard.active_branch_denial(self.root, (own,), host="claude"))
        self.assertIsNone(self.guard.active_branch_denial(self.root, (unknown,), host="unknown"))
        denial = self.guard.active_branch_denial(self.root, (foreign,), host="claude")
        self.assertIsNotNone(denial)
        self.assertIn("읽기 전용", denial)

    def test_child_workflow_requires_parent_to_remain_active(self) -> None:
        parent = self.configure_v3_task("task/meeting-reserve-ui", "sy-main")
        workflow = self.install_inject_workflow()
        environment = {
            **os.environ,
            "ASAN_AGENT_POLICY_MODE": "inject",
            "ASAN_AGENT_POLICY_BUNDLE_ROOT": str(workflow.parents[6]),
            "ASAN_AGENT_POLICY_PROJECT": "user-ui",
        }

        def run_workflow(*arguments: str) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                ["python3", str(workflow), *arguments],
                cwd=self.root,
                capture_output=True,
                text=True,
                env=environment,
                check=False,
            )

        proposed = run_workflow(
            "proposal",
            "--branch",
            "task/reserve-option-lazy-load",
            "--purpose",
            "예약 옵션 지연 로딩",
            "--parent",
            parent,
            "--scope",
            "src",
            "--reason",
            "parent 작업에서 분리된 후속 변경",
            "--role",
            "logic",
            "--git-integrator",
            "codex",
        )
        self.assertEqual(proposed.returncode, 0, proposed.stderr)
        proposal_path = next(
            line.removeprefix("- canonical proposal 파일: ")
            for line in proposed.stdout.splitlines()
            if line.startswith("- canonical proposal 파일: ")
        )
        proposal_sha = next(
            line.removeprefix("- canonical proposal SHA-256: ")
            for line in proposed.stdout.splitlines()
            if line.startswith("- canonical proposal SHA-256: ")
        )
        subprocess.run(
            ["git", "config", f"branch.{parent}.asan-state", "PRESERVED"],
            cwd=self.root,
            check=True,
        )

        stale_create = run_workflow(
            "create",
            "--proposal-file",
            proposal_path,
            "--proposal-sha256",
            proposal_sha,
        )
        new_proposal = run_workflow(
            "proposal",
            "--branch",
            "task/reserve-option-second",
            "--purpose",
            "두 번째 예약 옵션 작업",
            "--parent",
            parent,
            "--scope",
            "src",
            "--reason",
            "PRESERVED parent 차단 검증",
            "--role",
            "logic",
            "--git-integrator",
            "codex",
        )

        self.assertNotEqual(stale_create.returncode, 0)
        self.assertIn("ACTIVE", stale_create.stderr)
        self.assertNotEqual(new_proposal.returncode, 0)
        self.assertIn("ACTIVE", new_proposal.stderr)

    def test_v3_finish_verify_and_close_lifecycle(self) -> None:
        workflow = self.install_inject_workflow()
        base_environment = {
            "ASAN_AGENT_POLICY_MODE": "inject",
            "ASAN_AGENT_POLICY_BUNDLE_ROOT": str(workflow.parents[6]),
            "ASAN_AGENT_POLICY_PROJECT": "user-ui",
        }

        def run_workflow(*arguments: str, environment: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
            selected_environment = dict(os.environ)
            selected_environment.update(base_environment)
            if environment:
                selected_environment.update(environment)
            return subprocess.run(
                ["python3", str(workflow), *arguments],
                cwd=self.root,
                capture_output=True,
                text=True,
                env=selected_environment,
                check=False,
            )

        proposed = run_workflow(
            "proposal",
            "--branch",
            "task/finish-lifecycle",
            "--purpose",
            "완료 생명주기 검증",
            "--parent",
            "sy-main",
            "--scope",
            "src",
            "--reason",
            "독립 회귀 테스트",
            "--role",
            "logic",
            "--git-integrator",
            "codex",
        )
        self.assertEqual(proposed.returncode, 0, proposed.stderr)
        proposal_path = next(
            line.removeprefix("- canonical proposal 파일: ")
            for line in proposed.stdout.splitlines()
            if line.startswith("- canonical proposal 파일: ")
        )
        proposal_sha = next(
            line.removeprefix("- canonical proposal SHA-256: ")
            for line in proposed.stdout.splitlines()
            if line.startswith("- canonical proposal SHA-256: ")
        )
        created = run_workflow(
            "create",
            "--proposal-file",
            proposal_path,
            "--proposal-sha256",
            proposal_sha,
        )
        self.assertEqual(created.returncode, 0, created.stderr)

        source = self.root / "src/feature.ts"
        source.parent.mkdir(parents=True)
        source.write_text("export const feature = true\n", encoding="utf-8")
        subprocess.run(["git", "add", "src/feature.ts"], cwd=self.root, check=True)
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Policy Test",
                "-c",
                "user.email=policy@example.com",
                "commit",
                "-qm",
                "feature",
            ],
            cwd=self.root,
            check=True,
        )
        finish_proposed = run_workflow(
            "finish-proposal",
            "--source",
            "task/finish-lifecycle",
            "--verify-command",
            "npm run lint",
        )
        self.assertEqual(finish_proposed.returncode, 0, finish_proposed.stderr)
        finish_path = next(
            line.removeprefix("- finish proposal 파일: ")
            for line in finish_proposed.stdout.splitlines()
            if line.startswith("- finish proposal 파일: ")
        )
        finish_sha = next(
            line.removeprefix("- finish proposal SHA-256: ")
            for line in finish_proposed.stdout.splitlines()
            if line.startswith("- finish proposal SHA-256: ")
        )
        subprocess.run(["git", "switch", "-q", "sy-main"], cwd=self.root, check=True)
        finished = run_workflow(
            "finish",
            "--proposal-file",
            finish_path,
            "--proposal-sha256",
            finish_sha,
        )
        self.assertEqual(finished.returncode, 0, finished.stderr)

        executable_root = Path(self.temporary_directory.name) / "bin"
        executable_root.mkdir()
        npm = executable_root / "npm"
        npm.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        npm.chmod(0o755)
        environment = {"PATH": f"{executable_root}{os.pathsep}{os.environ.get('PATH', '')}"}
        verified = run_workflow(
            "verify",
            "--proposal-file",
            finish_path,
            "--proposal-sha256",
            finish_sha,
            environment=environment,
        )
        self.assertEqual(verified.returncode, 0, verified.stderr)
        closed = run_workflow(
            "close",
            "--proposal-file",
            finish_path,
            "--proposal-sha256",
            finish_sha,
        )
        self.assertEqual(closed.returncode, 0, closed.stderr)
        self.assertEqual(self.guard.task_state(self.root, "task/finish-lifecycle"), "CLOSED")

    def test_v3_preserve_blocks_writes_until_resume(self) -> None:
        workflow = self.install_inject_workflow()
        environment = dict(os.environ)
        environment.update(
            {
                "ASAN_AGENT_POLICY_MODE": "inject",
                "ASAN_AGENT_POLICY_BUNDLE_ROOT": str(workflow.parents[6]),
                "ASAN_AGENT_POLICY_PROJECT": "user-ui",
            }
        )

        def run_workflow(*arguments: str) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                ["python3", str(workflow), *arguments],
                cwd=self.root,
                capture_output=True,
                text=True,
                env=environment,
                check=False,
            )

        proposed = run_workflow(
            "proposal",
            "--branch",
            "task/preserve-lifecycle",
            "--purpose",
            "보존 상태 검증",
            "--parent",
            "sy-main",
            "--scope",
            "src",
            "--reason",
            "다른 독립 작업 전에 현재 상태 보존",
            "--role",
            "logic",
            "--git-integrator",
            "codex",
        )
        self.assertEqual(proposed.returncode, 0, proposed.stderr)
        proposal_path = next(
            line.removeprefix("- canonical proposal 파일: ")
            for line in proposed.stdout.splitlines()
            if line.startswith("- canonical proposal 파일: ")
        )
        proposal_sha = next(
            line.removeprefix("- canonical proposal SHA-256: ")
            for line in proposed.stdout.splitlines()
            if line.startswith("- canonical proposal SHA-256: ")
        )
        created = run_workflow(
            "create",
            "--proposal-file",
            proposal_path,
            "--proposal-sha256",
            proposal_sha,
        )
        self.assertEqual(created.returncode, 0, created.stderr)

        preserved = run_workflow("preserve", "--reason", "후속 세션에 handoff")
        self.assertEqual(preserved.returncode, 0, preserved.stderr)
        self.assertEqual(self.guard.task_state(self.root, "task/preserve-lifecycle"), "PRESERVED")
        denial = self.guard.active_branch_denial(self.root, ("src/feature.ts",))
        self.assertIsNotNone(denial)
        self.assertIn("ACTIVE", denial)

        resumed = run_workflow("resume")
        self.assertEqual(resumed.returncode, 0, resumed.stderr)
        self.assertEqual(self.guard.task_state(self.root, "task/preserve-lifecycle"), "ACTIVE")
        self.assertIsNone(self.guard.active_branch_denial(self.root, ("src/feature.ts",)))


if __name__ == "__main__":
    unittest.main()
