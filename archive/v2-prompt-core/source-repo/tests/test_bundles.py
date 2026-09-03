"""주입 번들 생성 동작을 검증한다."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))

import bundles
import sync


class BundleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.target = sync.select_targets("user-ui")[0]
        self.bundle = bundles.build(self.target, sync.render_tokens)

    def test_플러그인_매니페스트가_유효한_구조를_갖는다(self) -> None:
        manifest = json.loads((self.bundle / "plugin/.claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "asan-prompt-core")
        self.assertEqual(manifest["skills"], ["./skills"])

    def test_시스템_프롬프트에_프로젝트_토큰이_남지_않는다(self) -> None:
        prompt = (self.bundle / "system-prompt.md").read_text(encoding="utf-8")
        self.assertNotIn("{{PROJECT_", prompt)
        self.assertIn(str(self.target["name"]), prompt)

    def test_스킬_참조가_번들_절대경로로_바뀐다(self) -> None:
        prompt = (self.bundle / "system-prompt.md").read_text(encoding="utf-8")
        self.assertNotIn(".agents/skills", prompt)
        self.assertIn(str(self.bundle / "plugin/skills"), prompt)

    def test_참조된_스킬_파일이_번들에_실제로_존재한다(self) -> None:
        self.assertTrue((self.bundle / "plugin/skills/policy/harness/SKILL.md").is_file())
        self.assertTrue((self.bundle / "plugin/skills/project-ui/SKILL.md").is_file())

    def test_opencode_번들이_설정과_역할과_플러그인을_갖춘다(self) -> None:
        home = self.bundle / "opencode-home"
        config = json.loads((home / "opencode.json").read_text(encoding="utf-8"))
        self.assertEqual(config["instructions"], [str(home / "AGENTS.md")])
        for role in ("planner", "publisher", "generator", "refactorer", "watcher", "evaluator"):
            self.assertTrue((home / f"agent/{role}.md").is_file(), f"{role} 역할이 없다")
        self.assertTrue((home / "plugin/harness.js").is_file())
        self.assertTrue((home / "plugin/harness_core.py").is_file())

    def test_opencode_지침에_프로젝트_토큰이_남지_않는다(self) -> None:
        text = (self.bundle / "opencode-home/AGENTS.md").read_text(encoding="utf-8")
        self.assertNotIn("{{PROJECT_", text)
        self.assertIn(str(self.target["name"]), text)

    def test_호스트별_훅이_등록된다(self) -> None:
        home = bundles.STATE / self.bundle.name / "codex-home"
        for path in (self.bundle / "plugin/hooks/hooks.json", home / "hooks.json"):
            document = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(set(document["hooks"]), set(bundles.INJECT_EVENTS))

    def test_주입_번들은_compact_브랜치_컨텍스트를_위해_session_start를_등록한다(self) -> None:
        document = json.loads((self.bundle / "plugin/hooks/hooks.json").read_text(encoding="utf-8"))
        self.assertIn("SessionStart", document["hooks"])

    def test_주입_hook에_기준_브랜치_토큰이_렌더링된다(self) -> None:
        for path in (
            self.bundle / "plugin/hooks/branch_guard.py",
            bundles.STATE / self.bundle.name / "codex-home/hooks/branch_guard.py",
        ):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("{{BASE_BRANCH}}", text)
            self.assertIn(str(self.target["base_branch"]), text)

    def test_opencode가_shell과_compact_브랜치_guard를_연결한다(self) -> None:
        text = (self.bundle / "opencode-home/plugin/harness.js").read_text(encoding="utf-8")
        self.assertIn('"bash"', text)
        self.assertIn("executionDirectory(directory, toolInput.workdir)", text)
        self.assertIn('"experimental.session.compacting"', text)

    def test_주입_인자가_프로젝트_경로를_참조하지_않는다(self) -> None:
        command, environment = bundles_command("claude", self.bundle)
        joined = " ".join(command)
        self.assertNotIn(str(self.target["path"]), joined)
        self.assertIn("--setting-sources", command)
        self.assertEqual(command[command.index("--setting-sources") + 1], "user")
        self.assertEqual(environment, {})

    def test_codex_는_전용_홈을_환경변수로_전달한다(self) -> None:
        _, environment = bundles_command("codex", self.bundle)
        self.assertEqual(environment["CODEX_HOME"], str(bundles.STATE / self.bundle.name / "codex-home"))

    def test_opencode_는_설정_디렉터리와_프로젝트_배제를_전달한다(self) -> None:
        _, environment = bundles_command("opencode", self.bundle)
        self.assertEqual(
            environment["OPENCODE_CONFIG_DIR"], str(self.bundle / "opencode-home")
        )
        self.assertEqual(environment["OPENCODE_DISABLE_PROJECT_CONFIG"], "1")

    def test_알_수_없는_호스트는_거부한다(self) -> None:
        with self.assertRaises(SystemExit):
            _ = bundles_command("unknown-host", self.bundle)


class CodexHomePreservationTest(unittest.TestCase):
    def test_런타임_상태는_build_밖에_저장된다(self) -> None:
        target = sync.select_targets("user-ui")[0]
        bundle = bundles.build(target, sync.render_tokens)
        home = bundles.STATE / str(target["id"]) / "codex-home"
        self.assertTrue(home.is_dir())
        self.assertFalse((bundle / "codex-home").exists(), "런타임 상태가 build/ 안에 남아 있다")

    def test_재빌드가_코덱스_런타임_상태를_지우지_않는다(self) -> None:
        target = sync.select_targets("user-ui")[0]
        _ = bundles.build(target, sync.render_tokens)
        home = bundles.STATE / str(target["id"]) / "codex-home"
        runtime = home / "sessions"
        runtime.mkdir(parents=True, exist_ok=True)
        canary = runtime / "canary.jsonl"
        _ = canary.write_text("keep me", encoding="utf-8")

        _ = bundles.build(target, sync.render_tokens)

        self.assertTrue(canary.is_file(), "세션 이력이 재빌드에서 삭제되었다")
        canary.unlink()

    def test_build_전체를_지워도_이력이_남는다(self) -> None:
        import shutil

        target = sync.select_targets("user-ui")[0]
        _ = bundles.build(target, sync.render_tokens)
        home = bundles.STATE / str(target["id"]) / "codex-home"
        canary = home / "sessions" / "canary2.jsonl"
        canary.parent.mkdir(parents=True, exist_ok=True)
        _ = canary.write_text("survive rm -rf build", encoding="utf-8")

        shutil.rmtree(bundles.BUILD / str(target["id"]))
        _ = bundles.build(target, sync.render_tokens)

        self.assertTrue(canary.is_file(), "build/ 삭제로 세션 이력이 사라졌다")
        canary.unlink()


class ConcurrentSessionTest(unittest.TestCase):
    def test_재빌드_중에도_훅과_스킬_파일이_사라지지_않는다(self) -> None:
        import threading
        import time

        target = sync.select_targets("user-ui")[0]
        bundle = bundles.build(target, sync.render_tokens)
        probes = [
            bundle / "plugin/hooks/harness_hook.py",
            bundle / "plugin/skills/policy/harness/SKILL.md",
            bundle / "system-prompt.md",
        ]
        state = {"missing": 0, "stop": False}

        def watch() -> None:
            while not state["stop"]:
                if not all(path.exists() for path in probes):
                    state["missing"] += 1
                time.sleep(0.001)

        thread = threading.Thread(target=watch)
        thread.start()
        try:
            for _ in range(2):
                _ = bundles.build(target, sync.render_tokens)
        finally:
            state["stop"] = True
            thread.join()

        self.assertEqual(state["missing"], 0, "재빌드 중 실행 세션이 참조하는 파일이 사라졌다")

    def test_동시_빌드가_충돌하지_않는다(self) -> None:
        import threading

        errors: list[str] = []

        def build(target_id: str) -> None:
            try:
                for _ in range(2):
                    _ = bundles.build(sync.select_targets(target_id)[0], sync.render_tokens)
            except Exception as error:  # noqa: BLE001 - 실패 원인을 그대로 보고한다
                errors.append(f"{target_id}: {error!r}")

        threads = [
            threading.Thread(target=build, args=(target_id,))
            for target_id in ("user-ui", "admin-ui", "user-ui")
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(errors, [])


class HookTrustTest(unittest.TestCase):
    def test_승인된_훅_신뢰_기록이_재빌드에서_보존된다(self) -> None:
        target = sync.select_targets("user-ui")[0]
        _ = bundles.build(target, sync.render_tokens)
        config = bundles.STATE / str(target["id"]) / "codex-home/config.toml"
        marker = '[hooks.state."asan-test:hooks/hooks.json:pre_tool_use:0:0"]\ntrusted = true\n'
        _ = config.write_text(config.read_text(encoding="utf-8") + "\n" + marker, encoding="utf-8")

        _ = bundles.build(target, sync.render_tokens)

        self.assertIn("asan-test:hooks/hooks.json", config.read_text(encoding="utf-8"))

    def test_보존_후에도_유효한_TOML_이다(self) -> None:
        import tomllib

        target = sync.select_targets("user-ui")[0]
        _ = bundles.build(target, sync.render_tokens)
        config = bundles.STATE / str(target["id"]) / "codex-home/config.toml"
        _ = tomllib.loads(config.read_text(encoding="utf-8"))


class CodexConfigTest(unittest.TestCase):
    def test_사용자_설정을_유지하고_중앙_항목만_추가한다(self) -> None:
        merged = bundles.merged_codex_config('personality = "x"\n\n[features]\ncodex_hooks = true\n')
        if not bundles.CODEX_USER_CONFIG.is_file():
            self.skipTest("사용자 Codex 설정이 없다")
        user = bundles.CODEX_USER_CONFIG.read_text(encoding="utf-8")
        self.assertTrue(merged.startswith(user.rstrip("\n")))
        self.assertIn("codex_hooks = true", merged)

    def test_병합_결과가_유효한_TOML_이다(self) -> None:
        import tomllib

        target = sync.select_targets("user-ui")[0]
        _ = bundles.build(target, sync.render_tokens)
        home = bundles.STATE / str(target["id"]) / "codex-home"
        document = tomllib.loads((home / "config.toml").read_text(encoding="utf-8"))
        self.assertTrue(document.get("features", {}).get("codex_hooks"))


def bundles_command(host: str, bundle: Path):
    return sync.inject_command(bundle, host)


if __name__ == "__main__":
    unittest.main(verbosity=2)
