from __future__ import annotations

import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "bin/sync.py"
SPEC = importlib.util.spec_from_file_location("prompt_sync", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("sync.py를 불러올 수 없습니다.")
prompt_sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prompt_sync)


class SyncTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        self.user = self.root / "user-ui"
        self.admin = self.root / "admin-ui"
        self.user.mkdir()
        self.admin.mkdir()
        (self.source / "common").mkdir(parents=True)
        (self.source / "hosts/codex").mkdir(parents=True)
        (self.source / "common/AGENTS.md").write_text(
            "# {{PROJECT_NAME}}\n\n기준: {{BASE_BRANCH}}\n\n## 명령어\n\n{{PROJECT_COMMANDS}}\n",
            encoding="utf-8",
        )
        (self.source / "hosts/codex/config.toml").write_text('approval_policy = "on-request"\n', encoding="utf-8")
        self.targets_path = self.root / "targets.json"
        self.manifest_path = self.root / "MANIFEST.json"
        self.targets_path.write_text(
            json.dumps(
                {
                    "targets": [
                        {
                            "id": "user-ui",
                            "name": "user-project",
                            "path": str(self.user),
                            "base_branch": "user-main",
                            "hosts": ["codex"],
                            "commands": [{"label": "테스트", "command": "npm run test"}],
                        },
                        {
                            "id": "admin-ui",
                            "name": "admin-project",
                            "path": str(self.admin),
                            "base_branch": "admin-main",
                            "hosts": ["codex"],
                            "commands": [{"label": "린트", "command": "npm run lint"}],
                        },
                    ]
                }
            ),
            encoding="utf-8",
        )
        self.manifest_path.write_text('{"schema_version": 1, "targets": {}}\n', encoding="utf-8")
        self.originals = (
            prompt_sync.SOURCE,
            prompt_sync.TARGETS_PATH,
            prompt_sync.MANIFEST_PATH,
        )
        prompt_sync.SOURCE = self.source
        prompt_sync.TARGETS_PATH = self.targets_path
        prompt_sync.MANIFEST_PATH = self.manifest_path

    def tearDown(self) -> None:
        prompt_sync.SOURCE, prompt_sync.TARGETS_PATH, prompt_sync.MANIFEST_PATH = self.originals
        self.temporary.cleanup()

    def deploy(self) -> None:
        with redirect_stdout(io.StringIO()):
            self.assertEqual(prompt_sync.deploy("all"), 0)

    def test_프로젝트별_이름과_명령어를_렌더링한다(self) -> None:
        self.deploy()
        user_agents = (self.user / "AGENTS.md").read_text(encoding="utf-8")
        admin_agents = (self.admin / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("user-project", user_agents)
        self.assertIn("기준: user-main", user_agents)
        self.assertIn("npm run test", user_agents)
        self.assertNotIn("npm run test", admin_agents)
        self.assertIn("admin-project", admin_agents)
        self.assertIn("기준: admin-main", admin_agents)

    def test_중앙_원본만_수정해도_check가_탐지한다(self) -> None:
        self.deploy()
        (self.source / "common/AGENTS.md").write_text("# 변경된 {{PROJECT_NAME}}\n", encoding="utf-8")
        with redirect_stdout(io.StringIO()):
            self.assertEqual(prompt_sync.check("all"), 1)

    def test_dry_run은_대상_파일을_수정하지_않는다(self) -> None:
        self.deploy()
        before = (self.user / "AGENTS.md").read_bytes()
        (self.source / "common/AGENTS.md").write_text("# dry-run {{PROJECT_NAME}}\n", encoding="utf-8")
        with redirect_stdout(io.StringIO()):
            self.assertEqual(prompt_sync.deploy("user-ui", dry_run=True), 0)
        self.assertEqual((self.user / "AGENTS.md").read_bytes(), before)

    def test_중앙에서_삭제한_이전_관리_파일을_회수한다(self) -> None:
        retired_source = self.source / "hosts/codex/retired.toml"
        retired_source.write_text("enabled = true\n", encoding="utf-8")
        self.deploy()
        retired_target = self.user / ".codex/retired.toml"
        self.assertTrue(retired_target.is_file())
        retired_source.unlink()
        self.deploy()
        self.assertFalse(retired_target.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)



class CollectTest(unittest.TestCase):
    """프로젝트 세션 산출물의 중앙 미러링 동작을 검증한다."""

    def test_프로젝트_로그가_중앙으로_복사된다(self) -> None:
        _ = prompt_sync.collect("all", quiet=True)
        for target in prompt_sync.load_targets():
            target_id = str(target["id"])
            source = Path(str(target["path"])) / prompt_sync.PROJECT_SESSIONS
            if not source.is_dir():
                continue
            mirror = prompt_sync.LOGS / target_id / "sessions"
            self.assertTrue(mirror.is_dir(), f"{target_id} 사본이 없다")
            names = {entry.name for entry in source.iterdir() if entry.is_dir()}
            copied = {entry.name for entry in mirror.iterdir() if entry.is_dir()}
            self.assertTrue(names.issubset(copied), f"{target_id} 세션 일부가 누락되었다")

    def test_대상별로_분리되어_충돌하지_않는다(self) -> None:
        _ = prompt_sync.collect("all", quiet=True)
        identifiers = [str(target["id"]) for target in prompt_sync.load_targets()]
        for target_id in identifiers:
            self.assertTrue((prompt_sync.LOGS / target_id).is_dir())

    def test_중앙에만_있는_기록은_삭제하지_않는다(self) -> None:
        _ = prompt_sync.collect("all", quiet=True)
        archived = prompt_sync.LOGS / "user-ui/sessions/9999-01-01-archived-only"
        archived.mkdir(parents=True, exist_ok=True)
        keeper = archived / "final-summary.md"
        _ = keeper.write_text("보관 전용 기록", encoding="utf-8")

        _ = prompt_sync.collect("all", quiet=True)

        self.assertTrue(keeper.is_file(), "프로젝트에 없는 중앙 보관 기록이 삭제되었다")
        keeper.unlink()
        archived.rmdir()

    def test_복사는_단방향이다(self) -> None:
        _ = prompt_sync.collect("all", quiet=True)
        target = prompt_sync.select_targets("user-ui")[0]
        source = Path(str(target["path"])) / prompt_sync.PROJECT_SESSIONS
        before = sorted(path.name for path in source.iterdir())

        injected = prompt_sync.LOGS / "user-ui/sessions/9999-01-02-central-only"
        injected.mkdir(parents=True, exist_ok=True)
        _ = prompt_sync.collect("all", quiet=True)

        after = sorted(path.name for path in source.iterdir())
        self.assertEqual(before, after, "중앙 기록이 프로젝트로 역류했다")
        injected.rmdir()
