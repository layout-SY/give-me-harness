"""읽기 참조와 다른 worktree의 구현 준비를 혼동하지 않는다."""
import unittest

import test_shared_git_access as shared


class WorktreeReadinessTests(unittest.TestCase):
    def setUp(self):
        self.fixture = shared.SharedGitAccessTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        for host in ("codex", "claude", "opencode"):
            plan = self.fixture.root / f".{host}/logs/sessions/shared-session/plan.md"
            plan.parent.mkdir(parents=True)
            plan.write_text("두 worktree에서 같은 작업을 수행하는 승인 계획\n")
        for location in (self.fixture.root, self.fixture.worktree):
            skill = location / ".agents/skills/policy/SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("현재 작업의 정책 스킬\n")

    def evidence(self, host, location, *, skill=True, source=True):
        tools = []
        if skill:
            tools.append(("Bash", {"command": "cat .agents/skills/policy/SKILL.md", "workdir": str(location)}))
        if source:
            tools.append(("Read", {"file_path": str(location / "src/app.ts")}))
        for tool, data in tools:
            self.fixture.run_event(host, "post-tool", {
                "tool_name": tool, "tool_input": data, "tool_response": {"success": True}})

    def edit(self, host, location):
        return self.fixture.run_event(host, "pre-tool", {"tool_name": "Edit", "tool_input": {
            "file_path": str(location / "src/app.ts"), "old_string": "1", "new_string": "2"}})

    def test_each_worktree_needs_its_own_evidence_but_can_reuse_the_approved_plan(self):
        f = self.fixture
        for host in ("codex", "claude", "opencode"):
            with self.subTest(host=host):
                self.evidence(host, f.root)
                f.run_event(host, "user-prompt", {"prompt": "Proceed"})
                f.assert_allowed(self.edit(host, f.root))
                blocked = self.edit(host, f.worktree)
                self.assertIn("소스 구현 준비", blocked.stdout + blocked.stderr)
                self.assertIn(str(f.worktree.resolve()), blocked.stdout + blocked.stderr)
                self.evidence(host, f.worktree, source=False)
                blocked = self.edit(host, f.worktree)
                self.assertIn("탐색", blocked.stdout + blocked.stderr)
                self.evidence(host, f.worktree, skill=False)
                f.assert_allowed(self.edit(host, f.worktree))
                # 다른 위치의 탐색은 기존 worktree 준비를 덮어쓰지 않는다.
                f.assert_allowed(self.edit(host, f.root))

    def test_checkout_or_head_change_requires_fresh_target_exploration(self):
        f = self.fixture
        self.evidence("codex", f.root)
        f.run_event("codex", "user-prompt", {"prompt": "Proceed"})
        f.git("switch", "-qc", "different-branch")
        self.assertIn("탐색", self.edit("codex", f.root).stdout)
        self.evidence("codex", f.root)
        f.assert_allowed(self.edit("codex", f.root))
        f.git("commit", "--allow-empty", "-qm", "changed HEAD")
        self.assertIn("탐색", self.edit("codex", f.root).stdout)

    def test_patch_cannot_borrow_preparation_from_the_first_worktree(self):
        f = self.fixture
        self.evidence("codex", f.root)
        f.run_event("codex", "user-prompt", {"prompt": "Proceed"})
        patch = "*** Begin Patch\n" + "".join(
            f"*** Update File: {location / 'src/app.ts'}\n@@\n-export const value = 1;\n+export const value = 2;\n"
            for location in (f.root, f.worktree)) + "*** End Patch"
        result = f.run_event("codex", "pre-tool", {"tool_name": "apply_patch", "tool_input": {"command": patch}})
        self.assertIn("소스 구현 준비", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
