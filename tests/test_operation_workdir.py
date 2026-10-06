"""호스트 훅에서 workdir가 누락돼도 명시한 보호 실행 경로를 확인한다."""
import os
import shlex
import unittest
from unittest.mock import patch

import test_relation_operations as shared


class OperationWorkdirTests(unittest.TestCase):
    def setUp(self):
        self.fixture = shared.RelationOperationTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        self.child = self.fixture.base / "child with spaces"
        self.fixture.git("worktree", "add", "-qb", "child", str(self.child))
        self.ops = self.fixture.module("git_operations")
        environment = patch.dict(os.environ, self.fixture.env, clear=True)
        environment.start()
        self.addCleanup(environment.stop)

    def test_literal_worktree_path_works_when_host_omits_workdir(self):
        for host in ("codex", "claude", "opencode"):
            with self.subTest(host=host):
                self.ops.reserve_write(self.root, {"session_id": "ended", "tool_call_id": host}, host, [self.child])
                pending = next(p for p in (self.ops.relations.directory(self.root) / "writes").glob("*.json")
                               if self.ops.state.read(p)["call"] == host)
                operation = self.ops.prepare_write_recovery(self.root, self.child, pending.stem, "명시적인 종료 결과 확인")
                direct = shlex.join(["python3", "-I", str(self.fixture.runtime / "git_operations.py"), "execute", operation["id"]])
                command = "cd -- " + shlex.quote(str(self.child)) + " && " + direct
                result = self.fixture.event("pre-tool", command, host=host)
                output = result.stdout + result.stderr
                self.assertIn("Git 작업 승인", output)
                self.assertNotIn("직접 실행", output)
                self.assertNotIn("실제 실행 위치와 다릅니다", output)
                if host != "claude":
                    self.fixture.event("user-prompt", host=host, prompt="명령 실행 승인")
                    result = self.fixture.event("pre-tool", command, host=host)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertNotIn('"deny"', result.stdout)
                # 테스트 runner에서 실제 승인한 복구만 실행한다. cwd=child이며 부모는 그대로다.
                self.ops.grant(self.root, operation, host, {"session_id": host + "-test"})
                self.assertEqual(self.ops.execute(self.root, operation["id"], self.child)["stage"], "done")

    def test_generated_command_carries_workdir_and_rejects_extra_shell(self):
        operation = self.ops.prepare_git(self.root, self.child, "git commit --allow-empty -m test", "codex", {})
        command = self.ops.command(operation)
        self.assertTrue(command.startswith("cd -- "), command)
        self.assertIn(shlex.quote(str(self.child)), command)
        for invalid in (command + " && git status", command.replace(" && ", " ; "),
                        command.replace(" && ", " || "), command + " > output.txt"):
            with self.subTest(invalid=invalid):
                result = self.fixture.event("pre-tool", invalid)
                self.assertIn('"deny"', result.stdout)

    def test_wrong_worktree_and_dynamic_cd_remain_blocked(self):
        operation = self.ops.prepare_git(self.root, self.child, "git commit --allow-empty -m test", "codex", {})
        direct = shlex.join(["python3", "-I", str(self.fixture.runtime / "git_operations.py"), "execute", operation["id"]])
        for location in (shlex.quote(str(self.root)), "$HOME"):
            result = self.fixture.event("pre-tool", "cd -- " + location + " && " + direct)
            self.assertIn('"deny"', result.stdout)


if __name__ == "__main__":
    unittest.main()
