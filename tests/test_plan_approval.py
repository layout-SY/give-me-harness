"""계획의 승인 범위와 진행 기록을 실제 source gate에서 구분한다."""
import unittest

import test_shared_git_access as shared


START = "<!-- asan-plan:approval:start:v1 -->"
END = "<!-- asan-plan:approval:end:v1 -->"


class PlanApprovalTests(unittest.TestCase):
    def setUp(self):
        self.fixture = shared.SharedGitAccessTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.plan = self.fixture.root / ".codex/logs/sessions/shared-session/plan.md"
        self.plan.parent.mkdir(parents=True, exist_ok=True)
        self.plan.write_text(f"# 계획\n{START}\n## 목표\n요청한 기능 구현\n{END}\n## 진행\n준비\n")

    def prepare(self):
        for tool, args in (("Skill", {"skill": "policy"}), ("Read", {"file_path": "src/app.ts"})):
            self.fixture.run_event("codex", "post-tool", {
                "tool_name": tool, "tool_input": args, "tool_response": {"success": True}})
        self.fixture.run_event("codex", "user-prompt", {"prompt": "Proceed"})

    def edit(self):
        return self.fixture.run_event("codex", "pre-tool", {"tool_name": "Edit", "tool_input": {
            "file_path": str(self.fixture.root / "src/app.ts"), "old_string": "1", "new_string": "2"}})

    def test_progress_updates_keep_approval_but_scope_changes_require_same_session_reapproval(self):
        self.prepare()
        self.plan.write_text(self.plan.read_text().replace("준비", "1단계 완료: 테스트 통과"))
        self.fixture.assert_allowed(self.edit())
        self.plan.write_text(self.plan.read_text().replace("요청한 기능 구현", "추가 API 계약 변경"))
        self.assertIn("사용자 구현 승인", self.edit().stdout)
        self.fixture.run_event("codex", "user-prompt", {"prompt": "Proceed"})
        self.fixture.assert_allowed(self.edit())

    def test_plan_is_required_even_when_all_three_preparation_events_succeed(self):
        self.plan.unlink()
        self.prepare()
        self.assertIn("plan.md", self.edit().stdout)

    def test_plan_created_after_approval_needs_approval_for_that_plan(self):
        content = self.plan.read_text()
        self.plan.unlink()
        self.prepare()
        self.plan.write_text(content)
        self.assertIn("사용자 구현 승인", self.edit().stdout)

    def test_malformed_or_empty_approval_region_cannot_be_approved(self):
        for content in (f"{START}\n범위\n", f"{END}\n범위\n{START}",
                        f"{START}\n{START}\n범위\n{END}", f"{START}\n \n{END}"):
            with self.subTest(content=content):
                self.plan.write_text(content)
                self.prepare()
                self.assertIn("승인 영역", self.edit().stdout)

    def test_legacy_plan_keeps_full_document_comparison(self):
        self.plan.write_text("기존 형식 계획")
        self.prepare()
        self.plan.write_text("기존 형식 계획 변경")
        self.assertIn("사용자 구현 승인", self.edit().stdout)


if __name__ == "__main__":
    unittest.main()
