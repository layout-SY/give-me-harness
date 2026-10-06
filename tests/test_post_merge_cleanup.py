"""병합 완료 후 부모의 진행 작업과 독립된 정리·보존 회귀 검사."""
import os
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

import test_relation_operations as shared


class PostMergeCleanupTests(unittest.TestCase):
    def setUp(self):
        self.fixture = shared.RelationOperationTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.seed_tree()
        self.fixture.git("switch", "-q", "A")
        self.root = self.fixture.root
        self.child = self.fixture.base / "K"
        self.fixture.git("worktree", "add", "-q", str(self.child), "K")
        self.head = self.fixture.commit_file(self.child, "src/child.ts", "export const child = 1;\n")
        self.env = patch.dict(os.environ, self.fixture.env, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)
        self.ops = self.fixture.module("git_operations")
        operation = self.fixture.completion(self.ops)
        self.ops.grant(self.root, operation, "codex", {"session_id": "one"})
        self.completed = self.ops.execute(self.root, operation["id"], self.root)
        self.assertEqual(self.completed["stage"], "retained")

    def prepare(self):
        return self.ops.prepare_cleanup(self.root, self.root, "K", "A")

    def execute(self, operation):
        self.ops.grant(self.root, operation, "codex", {"session_id": "one"})
        return self.ops.execute(self.root, operation["id"], self.root)

    def test_retained_cleanup_preserves_parent_dirty_index_and_archives_ignored_configuration(self):
        (self.root / "README.md").write_text("another task\n")
        self.fixture.git("add", "README.md")
        (self.root / "README.md").write_text("another task unstaged\n")
        self.fixture.git("config", "core.excludesFile", str(self.fixture.base / "global-ignore"))
        (self.fixture.base / "global-ignore").write_text(".env\n.env.development.local\ndist/\nnode_modules/\n")
        (self.child / ".env").write_text("LOCAL_SECRET=preserve-only\n")
        (self.child / ".env.development.local").write_text("VITE_MSW=true\n")
        (self.child / "dist").mkdir()
        (self.child / "dist/result.js").write_text("generated\n")
        before = self.ops.relations.content_snapshot(self.root, logs=True)
        prepared = self.prepare()
        self.assertTrue(self.child.exists())
        result = self.execute(prepared)
        self.assertEqual(result["stage"], "cleaned", result)
        self.assertFalse(self.child.exists())
        self.assertEqual(self.ops.relations.content_snapshot(self.root, logs=True), before)
        self.assertEqual(self.fixture.git("rev-parse", "A"), self.head)
        self.assertEqual(self.fixture.git("branch", "--list", "K"), "")
        self.assertTrue(self.ops.relations.read(self.root)["nodes"]["K"]["deleted"])
        manifest = result["archive"]["files"]
        self.assertNotIn("dist/result.js", manifest)
        saved = Path(result["archive"]["directory"]) / "objects" / manifest[".env"]["sha256"]
        self.assertEqual(saved.read_text(), "LOCAL_SECRET=preserve-only\n")
        self.assertEqual(saved.stat().st_mode & 0o777, 0o600)

    def test_source_change_or_config_change_after_preparation_prevents_cleanup(self):
        prepared = self.prepare()
        (self.child / "src/child.ts").write_text("new work\n")
        with self.assertRaisesRegex(RuntimeError, "변경|미커밋"):
            self.execute(prepared)
        self.assertTrue(self.child.exists())
        self.assertTrue(self.fixture.git("branch", "--list", "K"))

    def test_pending_write_and_current_source_directory_prevent_cleanup(self):
        with self.assertRaisesRegex(RuntimeError, "실행 위치|현재"):
            self.ops.prepare_cleanup(self.root, self.child, "K", "A")
        self.ops.reserve_write(self.root, {"session_id": "other", "tool_call_id": "unfinished"}, "claude", [self.child])
        with self.assertRaisesRegex(RuntimeError, "미확인|실행 중"):
            self.prepare()

    def test_parent_must_be_direct_and_source_commit_must_be_contained(self):
        with self.assertRaisesRegex(RuntimeError, "직접 부모"):
            self.ops.prepare_cleanup(self.root, self.root, "K", "sy-main")
        self.fixture.commit_file(self.child, "src/new.ts", "unmerged\n")
        with self.assertRaisesRegex(RuntimeError, "포함|병합"):
            self.prepare()

    def test_external_merge_without_verification_can_be_cleaned_without_claiming_pass(self):
        graph = self.ops.relations.read(self.root)
        graph["nodes"]["K"]["resolution"] = None
        graph["nodes"]["K"]["integrations"] = []
        self.ops.relations.save(self.root, graph)
        prepared = self.prepare()
        self.assertEqual(prepared["cleanup"]["verification"]["status"], "unknown")
        result = self.execute(prepared)
        self.assertNotIn("verification_passed", result)
        resolution = self.ops.relations.read(self.root)["nodes"]["K"]["resolution"]
        self.assertEqual(resolution["verification"], "unknown")
        self.assertEqual(result["stage"], "cleaned")

    def test_ignored_file_change_and_unfinished_child_block_cleanup(self):
        (self.child / ".gitignore").write_text(".env\n")
        self.fixture.git("add", ".gitignore", root=self.child)
        self.fixture.git("commit", "-qm", "ignore", root=self.child)
        self.fixture.git("merge", "--ff-only", "K")
        (self.child / ".env").write_text("before")
        prepared = self.prepare()
        (self.child / ".env").write_text("after")
        with self.assertRaisesRegex(RuntimeError, "보존 파일|변경"):
            self.execute(prepared)
        self.fixture.git("branch", "new-child", "K")
        graph = self.ops.relations.read(self.root)
        graph["nodes"]["new-child"] = {**graph["nodes"]["K"], "id": "new-child",
            "name": "new-child", "parent": "K", "resolution": None,
            "birth": self.ops.relations.birth(self.root, "new-child")}
        self.ops.relations.save(self.root, graph)
        with self.assertRaisesRegex(RuntimeError, "미처리 하위"):
            self.prepare()

    def test_crash_after_worktree_delete_recovers_remaining_branch_only(self):
        prepared = self.prepare()
        implementation = self.ops._loader.load("post_merge_cleanup")
        original = implementation.ops.run
        def crash(root, args):
            result = original(root, args)
            if args[:2] == ["worktree", "remove"]:
                raise RuntimeError("crash after successful deletion")
            return result
        with patch.object(implementation.ops, "run", side_effect=crash):
            with self.assertRaisesRegex(RuntimeError, "crash"):
                self.execute(prepared)
        self.assertFalse(self.child.exists())
        self.assertTrue(self.fixture.git("branch", "--list", "K"))
        result = self.ops.recover(self.root, prepared["id"], self.root)
        self.assertEqual(result["stage"], "cleaned")
        self.assertEqual(self.fixture.git("rev-parse", "A"), self.head)

    def test_crash_after_branch_delete_recovers_relation_and_is_idempotent(self):
        prepared = self.prepare()
        implementation = self.ops._loader.load("post_merge_cleanup")
        original = implementation.ops.run
        def crash(root, args):
            result = original(root, args)
            if args[:2] == ["branch", "-D"]:
                raise RuntimeError("crash after branch deletion")
            return result
        with patch.object(implementation.ops, "run", side_effect=crash):
            with self.assertRaisesRegex(RuntimeError, "crash"):
                self.execute(prepared)
        self.assertFalse(self.ops.relations.read(self.root)["nodes"]["K"]["deleted"])
        result = self.ops.recover(self.root, prepared["id"], self.root)
        self.assertEqual(result["stage"], "cleaned")
        self.assertTrue(self.ops.relations.read(self.root)["nodes"]["K"]["deleted"])
        self.assertEqual(self.ops.recover(self.root, prepared["id"], self.root)["stage"], "cleaned")

    def test_dirty_session_logs_are_preserved_and_collected_before_deletion(self):
        log = self.child / ".claude/logs/sessions/other/handoff.md"
        log.parent.mkdir(parents=True)
        log.write_text("handoff remains recoverable\n")
        implementation = self.ops._loader.load("post_merge_cleanup")
        original = implementation.ops.subprocess.run
        collected = []
        def collect(args, **kwargs):
            if "collect-logs" in args:
                collected.append(args)
                return subprocess.CompletedProcess(args, 0, "", "")
            return original(args, **kwargs)
        with patch.object(implementation.ops.subprocess, "run", side_effect=collect):
            result = self.execute(self.prepare())
        entry = result["archive"]["files"][str(log.relative_to(self.child))]
        saved = Path(result["archive"]["directory"]) / "objects" / entry["sha256"]
        self.assertEqual(saved.read_text(), "handoff remains recoverable\n")
        self.assertEqual(len(collected), 1)

    def test_archive_failure_keeps_worktree_and_corruption_prevents_recovery(self):
        ignore = self.fixture.base / "ignore"
        ignore.write_text(".env\n")
        self.fixture.git("config", "core.excludesFile", str(ignore))
        (self.child / ".env").write_text("local config")
        implementation = self.ops._loader.load("post_merge_cleanup")
        prepared = self.prepare()
        with patch.object(implementation.ops, "archive", side_effect=RuntimeError("collection failure")):
            with self.assertRaisesRegex(RuntimeError, "collection failure"):
                self.execute(prepared)
        self.assertTrue(self.child.exists())
        original = implementation.ops.run
        def stop(root, args):
            if args[:2] == ["branch", "-D"]:
                raise RuntimeError("stop before branch removal")
            return original(root, args)
        with patch.object(implementation.ops, "run", side_effect=stop):
            with self.assertRaisesRegex(RuntimeError, "stop before"):
                self.ops.recover(self.root, prepared["id"], self.root)
        operation = self.ops.load(self.root, prepared["id"])
        entry = operation["archive"]["files"][".env"]
        (Path(operation["archive"]["directory"]) / "objects" / entry["sha256"]).write_text("corrupt")
        with self.assertRaisesRegex(RuntimeError, "손상"):
            self.ops.recover(self.root, prepared["id"], self.root)
        self.assertTrue(self.fixture.git("branch", "--list", "K"))

    def test_recovery_rejects_new_actor_and_revoked_consent(self):
        implementation = self.ops._loader.load("post_merge_cleanup")
        prepared = self.prepare()
        with patch.object(implementation, "preserve", side_effect=RuntimeError("stop")):
            with self.assertRaisesRegex(RuntimeError, "stop"):
                self.execute(prepared)
        operation = self.ops.load(self.root, prepared["id"])
        with self.assertRaisesRegex(RuntimeError, "같은 주체"):
            implementation.require_consent(self.root, operation, "codex", {"session_id": "another"})
        self.ops.revoke_consent(self.root, "codex", {"session_id": "one"})
        with self.assertRaisesRegex(RuntimeError, "철회"):
            self.ops.recover(self.root, prepared["id"], self.root)

    def test_symlink_nested_repository_and_hidden_index_changes_are_rejected(self):
        ignore = self.fixture.base / "ignore"
        ignore.write_text("local/\n")
        self.fixture.git("config", "core.excludesFile", str(ignore))
        local = self.child / "local"
        local.mkdir()
        (local / "secret").symlink_to(self.root / "src/app.ts")
        with self.assertRaisesRegex(RuntimeError, "링크"):
            self.prepare()
        (local / "secret").unlink()
        (local / ".git").write_text("gitdir: /somewhere")
        with self.assertRaisesRegex(RuntimeError, "중첩"):
            self.prepare()
        (local / ".git").unlink()
        self.fixture.git("update-index", "--assume-unchanged", "src/child.ts", root=self.child)
        (self.child / "src/child.ts").write_text("hidden local work")
        with self.assertRaisesRegex(RuntimeError, "assume-unchanged"):
            self.prepare()

    def test_in_progress_git_and_branch_recreation_after_interruption_block_cleanup(self):
        marker = Path(self.fixture.git("rev-parse", "--git-path", "rebase-merge", root=self.child))
        marker.mkdir()
        with self.assertRaisesRegex(RuntimeError, "진행 중인 Git"):
            self.prepare()
        marker.rmdir()
        implementation = self.ops._loader.load("post_merge_cleanup")
        original = implementation.ops.run
        def crash(root, args):
            result = original(root, args)
            if args[:2] == ["branch", "-D"]:
                raise RuntimeError("crash")
            return result
        prepared = self.prepare()
        with patch.object(implementation.ops, "run", side_effect=crash):
            with self.assertRaisesRegex(RuntimeError, "crash"):
                self.execute(prepared)
        # 같은 HEAD로 재생성된 branch에도 과거 삭제 승인을 재사용하지 않는다.
        self.fixture.git("branch", "K", "A")
        with self.assertRaisesRegex(RuntimeError, "재생성|reflog|브랜치 식별"):
            self.ops.recover(self.root, prepared["id"], self.root)
        self.assertTrue(self.fixture.git("branch", "--list", "K"))


if __name__ == "__main__":
    unittest.main()
