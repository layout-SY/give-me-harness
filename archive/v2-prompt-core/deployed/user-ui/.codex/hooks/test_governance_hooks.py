"""중앙 프롬프트 하네스 훅의 판정 로직을 검증한다."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    import harness_core
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "common/hooks"))
    import harness_core


class ManagedPathTest(unittest.TestCase):
    def test_중앙_관리_경로를_식별한다(self) -> None:
        for relative in (
            "AGENTS.md",
            "CLAUDE.md",
            ".agents/skills/policy/SKILL.md",
            ".codex/agents/watcher.toml",
            ".claude/hooks/harness_hook.py",
            ".opencode/agent/planner.md",
            ".harness/roles/orchestration.md",
        ):
            with self.subTest(relative=relative):
                self.assertTrue(harness_core.is_managed(relative))

    def test_프로젝트_소유_경로는_허용한다(self) -> None:
        for relative in (
            "src/shared/ui/Button.tsx",
            "package.json",
            ".codex/logs/sessions/2026-08-26-task/plan.md",
            ".codex/memory/reusable-assets.md",
            "DESIGN.md",
        ):
            with self.subTest(relative=relative):
                self.assertFalse(harness_core.is_managed(relative))

    def test_중앙_대응_경로를_계산한다(self) -> None:
        self.assertTrue(
            harness_core.central_source_for(".agents/skills/policy/SKILL.md").endswith(
                "source/common/skills/policy/SKILL.md"
            )
        )
        self.assertTrue(
            harness_core.central_source_for(".codex/agents/watcher.toml").endswith(
                "source/hosts/codex/agents/watcher.toml"
            )
        )
        self.assertTrue(harness_core.central_source_for("AGENTS.md").endswith("source/common/AGENTS.md"))

    def test_차단_메시지가_대상과_이동_경로를_포함한다(self) -> None:
        message = harness_core.managed_denial(".agents/skills/policy/SKILL.md")
        self.assertIn(".agents/skills/policy/SKILL.md", message)
        self.assertIn("asan-prompt-core", message)
        self.assertIn("세션을 재시작", message)


class EditToolTest(unittest.TestCase):
    def test_편집_도구를_식별한다(self) -> None:
        for name in ("Write", "Edit", "MultiEdit", "apply_patch"):
            self.assertTrue(harness_core.is_edit_tool({"tool_name": name}))

    def test_읽기_도구는_대상이_아니다(self) -> None:
        for name in ("Read", "Grep"):
            self.assertFalse(harness_core.is_edit_tool({"tool_name": name}))

    def test_도구_입력에서_대상_경로를_추출한다(self) -> None:
        self.assertEqual(
            harness_core.tool_targets({"tool_input": {"file_path": "AGENTS.md"}}),
            ("AGENTS.md",),
        )
        self.assertEqual(
            harness_core.tool_targets({"tool_input": {"filePath": ".opencode/plugins/harness.js"}}),
            (".opencode/plugins/harness.js",),
        )
        self.assertEqual(harness_core.tool_targets({"tool_input": {}}), ())
        self.assertEqual(harness_core.tool_targets({}), ())

    def test_apply_patch의_모든_대상_경로를_추출한다(self) -> None:
        event = {
            "tool_name": "apply_patch",
            "tool_input": {
                "command": "*** Begin Patch\n*** Update File: AGENTS.md\n*** Add File: src/new.ts\n*** End Patch"
            },
        }
        self.assertEqual(harness_core.tool_targets(event), ("AGENTS.md", "src/new.ts"))


class ShellEditTest(unittest.TestCase):
    """셸 명령을 통한 파일 변경도 편집으로 인식하는지 검증한다."""

    def _targets(self, command: str, name: str = "shell") -> tuple[str, ...]:
        return harness_core.tool_targets({"tool_name": name, "tool_input": {"command": command}})

    def test_apply_patch_힙독의_대상을_추출한다(self) -> None:
        command = "apply_patch <<'EOF'\n*** Update File: AGENTS.md\n*** Add File: .agents/skills/x/SKILL.md\nEOF"
        targets = self._targets(command)
        self.assertIn("AGENTS.md", targets)
        self.assertIn(".agents/skills/x/SKILL.md", targets)

    def test_리다이렉션_대상을_추출한다(self) -> None:
        self.assertIn("AGENTS.md", self._targets("echo hi > AGENTS.md"))
        self.assertIn("CLAUDE.md", self._targets("cat x >> CLAUDE.md"))

    def test_sed_와_tee_대상을_추출한다(self) -> None:
        self.assertIn("AGENTS.md", self._targets("sed -i '' 's/a/b/' AGENTS.md"))
        self.assertIn("CLAUDE.md", self._targets("echo x | tee CLAUDE.md"))

    def test_이동과_삭제_대상을_추출한다(self) -> None:
        self.assertIn("AGENTS.md", self._targets("mv tmp.md AGENTS.md"))
        self.assertIn("CLAUDE.md", self._targets("rm -f CLAUDE.md"))

    def test_조회_명령은_대상을_만들지_않는다(self) -> None:
        for command in (
            "ls -la .agents/skills",
            "cat AGENTS.md",
            "grep -rn foo .codex",
            "git status --short",
            "npm run lint",
        ):
            with self.subTest(command=command):
                self.assertEqual(self._targets(command), ())

    def test_dev_null_은_무시한다(self) -> None:
        self.assertEqual(self._targets("git status > /dev/null"), ())

    def test_배열로_전달된_명령도_처리한다(self) -> None:
        targets = harness_core.tool_targets(
            {"tool_name": "shell", "tool_input": {"command": ["bash", "-lc", "echo x > AGENTS.md"]}}
        )
        self.assertIn("AGENTS.md", targets)

    def test_셸_도구가_편집_도구로_인식된다(self) -> None:
        self.assertTrue(harness_core.is_edit_tool({"tool_name": "shell"}))
        self.assertTrue(harness_core.is_edit_tool({"tool_name": "local_shell"}))


class ArtifactTest(unittest.TestCase):
    def test_비어_있는_산출물을_누락으로_판정한다(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            session = Path(directory)
            _ = (session / "plan.md").write_text("짧음", encoding="utf-8")
            _ = (session / "exploration.md").write_text("가" * 60, encoding="utf-8")
            missing = harness_core.missing_artifacts(session, ("plan.md", "exploration.md", "review-log.md"))
            self.assertIn("plan.md", missing)
            self.assertIn("review-log.md", missing)
            self.assertNotIn("exploration.md", missing)

    def test_필수_산출물_목록이_여덟_종이다(self) -> None:
        self.assertEqual(len(harness_core.REQUIRED_ARTIFACTS), 8)
        self.assertIn("portfolio-log.md", harness_core.REQUIRED_ARTIFACTS)
        self.assertIn("grill-me-review.md", harness_core.REQUIRED_ARTIFACTS)


class AcceptedSetTest(unittest.TestCase):
    def test_허용_집합_중_하나만_충족해도_통과한다(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            session = root / harness_core.SESSIONS_RELATIVE / "2026-08-26-task"
            session.mkdir(parents=True)
            _ = (session / harness_core.HANDOFF_ARTIFACT).write_text("가" * 60, encoding="utf-8")
            shortfalls = [
                harness_core.missing_artifacts(session, (harness_core.HANDOFF_ARTIFACT,)),
                harness_core.missing_artifacts(session, harness_core.REQUIRED_ARTIFACTS),
            ]
            self.assertTrue(any(not missing for missing in shortfalls))

    def test_어느_집합도_충족하지_못하면_가장_가까운_누락을_보고한다(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            session = Path(directory)
            _ = (session / "plan.md").write_text("가" * 60, encoding="utf-8")
            shortfalls = [
                harness_core.missing_artifacts(session, (harness_core.HANDOFF_ARTIFACT,)),
                harness_core.missing_artifacts(session, harness_core.REQUIRED_ARTIFACTS),
            ]
            self.assertTrue(all(missing for missing in shortfalls))
            self.assertEqual(min(shortfalls, key=len), [harness_core.HANDOFF_ARTIFACT])


if __name__ == "__main__":
    unittest.main(verbosity=2)
