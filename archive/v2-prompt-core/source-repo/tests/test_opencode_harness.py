"""OpenCode hook이 실제 shell 실행 workdir를 검사하는지 검증한다."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_SOURCE = ROOT / "source/hosts/opencode/plugins/harness.js"


class OpenCodeWorkdirTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.session = self.root / "session-worktree"
        self.logic = self.root / "logic-worktree"
        self.session.mkdir()
        self.logic.mkdir()
        self.plugin = self.root / "harness.mjs"
        shutil.copyfile(PLUGIN_SOURCE, self.plugin)
        (self.root / "harness_hook.py").write_text(
            "import os\nimport sys\nprint(os.getcwd(), file=sys.stderr)\nraise SystemExit(2)\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def invoke(self, workdir: object = None, *, include_workdir: bool = True) -> str:
        arguments: dict[str, object] = {"command": "git commit -m test"}
        if include_workdir:
            arguments["workdir"] = workdir
        script = "\n".join(
            (
                f"const module = await import({json.dumps(self.plugin.as_uri())})",
                f"const plugin = await module.HarnessPlugin({{ directory: {json.dumps(str(self.session))} }})",
                "try {",
                "  await plugin['tool.execute.before'](",
                "    { tool: 'bash' },",
                f"    {{ args: {json.dumps(arguments)} }},",
                "  )",
                "} catch (error) {",
                "  process.stdout.write(error.message)",
                "}",
            )
        )
        completed = subprocess.run(
            ["node", "--input-type=module", "--eval", script],
            cwd=self.session,
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip()

    def test_절대_workdir를_guard_실행_위치로_사용한다(self) -> None:
        self.assertEqual(Path(self.invoke(str(self.logic))).resolve(), self.logic.resolve())

    def test_상대_workdir를_session_directory_기준으로_해석한다(self) -> None:
        self.assertEqual(Path(self.invoke("../logic-worktree")).resolve(), self.logic.resolve())

    def test_workdir가_없으면_session_directory를_사용한다(self) -> None:
        self.assertEqual(Path(self.invoke(include_workdir=False)).resolve(), self.session.resolve())

    def test_유효하지_않은_workdir는_session_directory로_fallback한다(self) -> None:
        missing = self.root / "missing-worktree"
        self.assertEqual(Path(self.invoke(str(missing))).resolve(), self.session.resolve())
        file_path = self.root / "not-a-directory"
        file_path.write_text("file", encoding="utf-8")
        self.assertEqual(Path(self.invoke(str(file_path))).resolve(), self.session.resolve())


if __name__ == "__main__":
    unittest.main()
