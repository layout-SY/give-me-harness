"""작업용 worktree의 영속 경로와 생성 시점 검증."""
from __future__ import annotations

import os
import shlex
import unittest
from unittest.mock import patch

import test_relation_operations as fixtures


class WorktreeStorageTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.RelationOperationTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.seed_tree()
        self.operations = self.fixture.module("git_operations")
        self.environment = patch.dict(os.environ, self.fixture.env, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def test_relation_rejects_temporary_destination_before_approval(self):
        f = self.fixture
        with self.assertRaisesRegex(RuntimeError, "임시"):
            self.operations.prepare_relation(f.root, f.root, "create", "task/new", "A",
                f.git("rev-parse", "A"), worktree="/tmp/asan-worktree-storage-regression")

    def test_raw_git_rejects_temporary_destination_before_approval(self):
        f = self.fixture
        with self.assertRaisesRegex(RuntimeError, "임시"):
            self.operations.prepare_git(f.root, f.root,
                "git worktree add -b task/new /private/tmp/asan-worktree-storage-regression A",
                "codex", {"session_id": "codex-test"})

    def test_relation_execution_rechecks_temporary_destination(self):
        f = self.fixture
        operation = {"action": "create", "name": "task/new", "parent": "A",
                     "fork": f.git("rev-parse", "A"), "purpose": "regression",
                     "worktree": str(f.base / "unsafe"), "cwd": str(f.root)}
        # 실행 대신 기록하여 수정 전에도 실제 worktree를 생성하지 않는다.
        with patch.object(self.operations, "run") as run:
            with self.assertRaisesRegex(RuntimeError, "임시"):
                self.operations.apply_relation(f.root, operation)
            run.assert_not_called()

    def durable_storage(self):
        # 테스트 저장소만 임시 sandbox에 둔다. production에는 우회 옵션이 없다.
        storage = self.fixture.base / "asan-worktrees" / "asan-metaverse-user-ui-worktree"
        for context in (patch.object(self.operations.config, "WORKTREE_ROOT", storage),
                        patch.object(self.operations.storage, "temporary_roots",
                                     return_value=(self.fixture.base / "volatile",))):
            context.start()
            self.addCleanup(context.stop)
        return storage

    def prepare(self, worktree=None):
        f = self.fixture
        return self.operations.prepare_relation(f.root, f.root, "create", "task/reservation/media", "A",
            f.git("rev-parse", "A"), "작업 저장 위치 검증", worktree=worktree)

    def execute(self, operation):
        f = self.fixture
        self.operations.grant(f.root, operation, "codex", {"session_id": "codex-test"})
        return self.operations.execute(f.root, operation["id"], f.root)

    def test_default_path_is_previewed_then_created_after_approval(self):
        storage = self.durable_storage()
        operation = self.prepare()
        target = storage / "reservation-media"
        self.assertEqual(operation["worktree"], str(target))
        self.assertFalse(storage.exists(), "승인 준비 중에는 폴더를 생성하지 않는다")
        self.assertEqual(self.execute(operation)["stage"], "done")
        self.assertEqual(self.fixture.git("branch", "--show-current", root=target), "task/reservation/media")
        self.assertEqual(self.fixture.git("rev-parse", "HEAD", root=target), self.fixture.git("rev-parse", "A"))

    def test_raw_git_uses_effective_cwd_and_supports_quoted_paths(self):
        storage = self.durable_storage()
        target = storage / "task with spaces"
        f = self.fixture
        nested = f.root / "src"
        relative = os.path.relpath(target, nested)
        command = shlex.join(["git", "-C", str(nested), "worktree", "add", "-b", "task/quoted", "--", relative, "A"])
        operation = self.operations.prepare_git(f.root, f.root, command, "codex", {"session_id": "codex-test"})
        self.assertEqual(operation["worktree_destinations"], [str(target)])
        self.assertEqual(self.execute(operation)["stage"], "done")
        self.assertEqual(f.git("branch", "--show-current", root=target), "task/quoted")

    def test_rejects_other_projects_nested_tasks_and_existing_paths(self):
        storage = self.durable_storage()
        f = self.fixture
        for target in (storage.parent / "asan-metaverse-admin-ui-worktree" / "task",
                       storage / "nested" / "task", storage, storage / ".." / "escape"):
            with self.subTest(target=target), self.assertRaisesRegex(RuntimeError, "프로젝트 저장 위치"):
                self.prepare(str(target))
        existing = storage / "reservation-media"
        existing.mkdir(parents=True)
        (existing / "uncommitted.txt").write_text("preserve")
        with self.assertRaisesRegex(RuntimeError, "이미 존재"):
            self.prepare()
        self.assertEqual((existing / "uncommitted.txt").read_text(), "preserve")

    def test_missing_registered_worktree_is_not_reused(self):
        storage = self.durable_storage()
        target = storage / "reservation-media"
        self.fixture.git("worktree", "add", "-q", str(target), "K")
        moved = storage / "unregistered-location"
        target.rename(moved)
        with self.assertRaisesRegex(RuntimeError, "등록된 worktree"):
            self.prepare()
        self.assertTrue((moved / "src/app.ts").is_file())

    def test_temporary_aliases_environment_and_symlinks_are_rejected(self):
        f = self.fixture
        link = f.base / "tmp-alias"
        link.symlink_to("/tmp", target_is_directory=True)
        for target in ("/tmp/unsafe", "/private/tmp/unsafe", "/var/tmp/unsafe",
                       "/private/var/folders/unsafe", str(link / "unsafe")):
            with self.subTest(target=target), self.assertRaisesRegex(RuntimeError, "임시"):
                self.prepare(target)
        # 존재하지 않는 TMPDIR도 경로 분류에 포함한다.
        custom = f.root / "custom-temporary"
        with patch.dict(os.environ, {"TMPDIR": str(custom)}):
            self.assertIn(custom.resolve(), self.operations.storage.temporary_roots())

    def test_symlink_change_after_approval_blocks_relation_and_raw_git(self):
        storage = self.durable_storage()
        f = self.fixture
        for raw in (False, True):
            with self.subTest(raw=raw):
                if raw:
                    command = shlex.join(["git", "worktree", "add", "-b", "task/new", str(storage / "raw-task"), "A"])
                    operation = self.operations.prepare_git(f.root, f.root, command, "codex", {"session_id": "codex-test"})
                else:
                    operation = self.prepare()
                volatile = f.base / "volatile"
                volatile.mkdir(exist_ok=True)
                storage.parent.mkdir(parents=True, exist_ok=True)
                storage.symlink_to(volatile, target_is_directory=True)
                with self.assertRaisesRegex(RuntimeError, "임시"):
                    self.execute(operation)
                self.assertEqual(list(volatile.iterdir()), [])
                storage.unlink()

    def test_existing_destination_after_approval_is_preserved(self):
        storage = self.durable_storage()
        operation = self.prepare()
        target = storage / "reservation-media"
        target.mkdir(parents=True)
        marker = target / "preserve.txt"
        marker.write_text("another task")
        with self.assertRaisesRegex(RuntimeError, "이미 존재"):
            self.execute(operation)
        self.assertEqual(marker.read_text(), "another task")

    def test_changed_durable_target_can_be_prepared_again_with_a_new_approval(self):
        storage = self.durable_storage()
        f = self.fixture
        command = shlex.join(["git", "worktree", "add", "-b", "task/new", str(storage / "new-task"), "A"])
        before = self.operations.prepare_git(f.root, f.root, command, "codex", {"session_id": "codex-test"})
        replacement = f.base / "replacement-storage"
        replacement.mkdir()
        storage.parent.mkdir(parents=True)
        storage.symlink_to(replacement, target_is_directory=True)
        with self.assertRaisesRegex(RuntimeError, "변경"):
            self.execute(before)
        after = self.operations.prepare_git(f.root, f.root, command, "codex", {"session_id": "codex-test"})
        repeated = self.operations.prepare_git(f.root, f.root, command, "codex", {"session_id": "codex-test"})
        self.assertNotEqual(before["id"], after["id"])
        self.assertEqual(after["id"], repeated["id"])
        self.assertEqual(after["worktree_destinations"], [str(replacement / "new-task")])
        self.assertEqual(self.execute(after)["stage"], "done")

    def test_raw_git_options_cannot_hide_temporary_destination(self):
        f = self.fixture
        for args in (("-bnew", "/tmp/unsafe"), ("--lock", "--reason", "storage", "/tmp/unsafe"),
                     ("--track=direct", "--", "/tmp/unsafe", "A"), ("/tmp/unsafe", "-f", "A")):
            with self.subTest(args=args), self.assertRaisesRegex(RuntimeError, "임시"):
                self.operations.prepare_git(f.root, f.root, shlex.join(["git", "worktree", "add", *args]),
                    "codex", {"session_id": "codex-test"})
        with self.assertRaisesRegex(RuntimeError, "옵션"):
            self.operations.storage.git_destination(f.root, f.root, ("worktree", "add", "--unknown", "/tmp/unsafe"))
