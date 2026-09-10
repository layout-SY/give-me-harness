"""세션 권한과 독립적인 관계·완료·Git 승인 회귀 검사."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from agent_policy.core import load_project, render_project


class RelationOperationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.root = self.base / "repo"
        self.root.mkdir()
        self.git("init", "-q", "-b", "sy-main")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "policy@example.test")
        (self.root / "src").mkdir()
        (self.root / "src/app.ts").write_text("export const value = 1;\n")
        self.git("add", "--", "src")
        self.git("commit", "-qm", "base")
        self.bundle = self.base / "bundle"
        self.project = replace(load_project("user-ui"), path=self.root,
            commands={"lint": "git status --porcelain", "test": "git status --short", "build": "git diff --check", "dev": "npm run dev", "preview": "npm run preview"})
        for name, content in render_project(self.project).items():
            if name.startswith((".agent-policy/runtime/", ".agent-policy/common/contracts/")):
                target = self.bundle / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
        self.runtime = self.bundle / ".agent-policy/runtime"
        self.state = self.base / "state"
        self.env = {key: value for key, value in os.environ.items() if not key.startswith("ASAN_")}
        self.env.update(ASAN_AGENT_POLICY_STATE_ROOT=str(self.state), ASAN_AGENT_POLICY_ROLE="logic",
                        ASAN_SESSION_DIR=".codex/logs/sessions/current")
        self.common = self.root / ".git"
        self.repository = self.state / "repositories" / hashlib.sha256(str(self.common).encode()).hexdigest()
        self.calls = 0

    def git(self, *args, root=None):
        return subprocess.check_output(["git", *args], cwd=root or self.root, text=True).strip()

    def module(self, name):
        spec = importlib.util.spec_from_file_location(f"test_{name}_{id(self)}", self.runtime / f"{name}.py")
        result = importlib.util.module_from_spec(spec)
        with patch.dict(os.environ, self.env, clear=True):
            spec.loader.exec_module(result)
        return result

    def event(self, mode, command="", *, host="codex", prompt="", cwd=None, data=None, tool="Bash"):
        self.calls += 1
        event = {"cwd": str(cwd or self.root), "session_id": f"{host}-test", "tool_call_id": str(self.calls),
                 "tool_name": tool, "tool_input": data or {"command": command}, "prompt": prompt}
        return subprocess.run([sys.executable, "-I", str(self.runtime / "managed_policy_guard.py"), mode, host],
            input=json.dumps(event), cwd=self.root, env=self.env, text=True, capture_output=True)

    def seed_tree(self):
        nodes = {}
        base = self.git("rev-parse", "HEAD")
        for name, parent in (("sy-main", None), ("A", "sy-main"), ("F", "A"), ("I", "F"), ("K", "A"), ("C", "sy-main")):
            if parent:
                self.git("branch", name, parent)
            nodes[name] = {"id": name, "name": name, "parent": parent, "fork_commit": base,
                           "purpose": name, "revision": 1, "activity": 0, "deleted": False, "resolution": None}
        directory = self.repository / "branch-relations/v1"
        directory.mkdir(parents=True)
        (directory / "graph.json").write_text(json.dumps({"version": 1, "revision": 1, "nodes": nodes}))
        return nodes

    def test_raw_merge_cannot_skip_parent_or_unfinished_equal_head_child(self):
        self.seed_tree()
        for source, target, expected in (("I", "A", "직접 부모"), ("F", "A", "하위 작업"), ("A", "sy-main", "하위 작업")):
            self.git("switch", "-q", target)
            result = self.event("pre-tool", f"git merge --ff-only {source}")
            self.assertIn(expected, result.stdout + result.stderr)

    def test_reset_separator_and_attached_force_options_cannot_bypass_relations(self):
        self.seed_tree()
        self.git("switch", "-q", "I")
        self.commit_file(self.root, "src/child.ts", "pending child\n")
        self.git("switch", "-q", "A")
        relations = self.module("branch_relations")
        with patch.dict(os.environ, self.env, clear=True):
            for args in (("reset", "--hard", "I", "--"), ("checkout", "-BA", "I"), ("switch", "-CA", "I")):
                with self.subTest(args=args):
                    self.assertIsNotNone(relations.integration_denial(self.root, args))
            self.assertIsNone(relations.integration_denial(self.root, ("reset", "HEAD", "--", "src/app.ts")))

    def test_restore_without_separator_and_path_commit_protect_foreign_logs(self):
        log = self.root / ".claude/logs/sessions/other/handoff.md"
        log.parent.mkdir(parents=True)
        log.write_text("original\n")
        self.git("add", "--", str(log))
        self.git("commit", "-qm", "log")
        log.write_text("another session is working\n")
        for command in ("git restore .claude/logs/sessions/other/handoff.md",
                        "git commit -m result .claude/logs/sessions/other/handoff.md"):
            with self.subTest(command=command):
                result = self.event("pre-tool", command)
                self.assertIn("읽기 전용", result.stdout + result.stderr)

    def test_implementation_proceed_does_not_approve_pending_git(self):
        self.event("pre-tool", "git commit -m pending")
        self.event("user-prompt", prompt="다른 구현은 이대로 진행해")
        result = self.event("pre-tool", "git commit -m pending")
        self.assertIn("승인", result.stdout + result.stderr)

    def test_push_refspec_tracks_the_source_branch(self):
        self.git("branch", "source")
        approval = self.module("approval_policy")
        with patch.dict(os.environ, self.env, clear=True):
            before = approval.operation_fingerprint(self.root, "git push origin source:target")
            tree = self.git("rev-parse", "HEAD^{tree}")
            commit = subprocess.check_output(["git", "commit-tree", tree, "-p", "HEAD"], cwd=self.root,
                input="source advances\n", text=True).strip()
            self.git("update-ref", "refs/heads/source", commit)
            after = approval.operation_fingerprint(self.root, "git push origin source:target")
        self.assertNotEqual(before, after)

    def test_review_includes_sibling_descendants_and_dirty_untracked(self):
        self.seed_tree()
        child = self.base / "child"
        self.git("worktree", "add", "-q", str(child), "I")
        (child / "src/new.ts").write_text("Button({onSelect: oldContract});\n")
        review = self.module("integration_review")
        with patch.dict(os.environ, self.env, clear=True):
            evidence = review.collect(self.root, "K", "A", "ff-only", ["npm run lint"], False)
        serialized = json.dumps(evidence)
        self.assertIn("src/new.ts", serialized)
        self.assertIn("oldContract", serialized)
        self.assertIn("I", evidence["participants"])
        self.assertIn("F", evidence["participants"])

    def test_review_snapshot_invalidated_by_new_child_but_not_session_log(self):
        self.seed_tree()
        review = self.module("integration_review")
        with patch.dict(os.environ, self.env, clear=True):
            before = review.snapshot(self.root, "K", "A")
            log = self.root / ".claude/logs/sessions/other/handoff.md"
            log.parent.mkdir(parents=True)
            log.write_text("unrelated log update")
            self.assertEqual(before, review.snapshot(self.root, "K", "A"))
            graph = review.relations.read(self.root)
            self.git("branch", "new-child", "K")
            review.relations.register(self.root, graph, "new-child", "K", self.git("rev-parse", "HEAD"), "new child")
            review.relations.save(self.root, graph)
            self.assertNotEqual(before, review.snapshot(self.root, "K", "A"))

    def test_pending_children_do_not_block_an_independent_sibling(self):
        self.seed_tree()
        relations = self.module("branch_relations")
        with patch.dict(os.environ, self.env, clear=True):
            child, parent = relations.completion_check(self.root, relations.read(self.root), "K", "A")
        self.assertEqual((child["name"], parent["name"]), ("K", "A"))

    def test_executor_rechecks_index_after_approval(self):
        operations = self.module("git_operations")
        (self.root / "src/app.ts").write_text("export const value = 2;\n")
        self.git("add", "--", "src/app.ts")
        with patch.dict(os.environ, self.env, clear=True):
            operation = operations.prepare_git(self.root, self.root, "git commit -m approved", "codex", {"session_id": "codex-test"})
            operations.grant(self.root, operation, "codex", {"session_id": "codex-test"})
            (self.root / "src/app.ts").write_text("export const value = 3;\n")
            self.git("add", "--", "src/app.ts")
            with self.assertRaisesRegex(RuntimeError, "변경|재검토"):
                operations.execute(self.root, operation["id"])
        self.assertEqual(self.git("log", "-1", "--format=%s"), "base")

    def test_short_execution_lock_does_not_become_a_session_claim(self):
        operations = self.module("git_operations")
        with patch.dict(os.environ, self.env, clear=True):
            for host in ("codex", "claude", "opencode"):
                event = {"session_id": host + "-test"}
                operation = operations.prepare_git(self.root, self.root, "git commit --allow-empty -m " + host, host, event)
                operations.grant(self.root, operation, host, event)
                operations.execute(self.root, operation["id"])
        self.assertEqual(self.git("log", "-1", "--format=%s"), "opencode")
        self.assertFalse((self.repository / "claims").exists())

    def completion(self, operations, source="K", target="A", strategy="ff-only", cleanup=False, cwd=None):
        evidence = operations.review.collect(self.root, source, target, strategy, ["git diff --check"], cleanup)
        report = {key: "실제 fixture 비교; 의미 검증은 이 검사 범위 밖" for key in operations.review.REPORT_FIELDS}
        report["evidence_digest"] = evidence["evidence_digest"]
        return operations.prepare_completion(self.root, cwd or self.root, evidence, report)

    def commit_file(self, root, name, value):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value)
        self.git("add", "--", name, root=root)
        self.git("commit", "-qm", name, root=root)
        return self.git("rev-parse", "HEAD", root=root)

    def test_real_completion_cleanup_and_deleted_sibling_history(self):
        self.seed_tree()
        self.git("switch", "-q", "A")
        child = self.base / "K"
        self.git("worktree", "add", "-q", str(child), "K")
        source_head = self.commit_file(child, "src/button.ts", "export const onSelect = (item: string) => item;\n")
        operations = self.module("git_operations")
        with patch.dict(os.environ, self.env, clear=True):
            operation = self.completion(operations, cleanup=True)
            operations.grant(self.root, operation, "claude", {"session_id": "claude-test"})
            result = operations.execute(self.root, operation["id"], self.root)
            self.assertEqual(result["stage"], "cleaned", result)
            self.assertFalse(child.exists())
            self.assertEqual(self.git("rev-parse", "A"), source_head)
            # Cancel I explicitly so F can complete, then compare with deleted K.
            graph = operations.relations.read(self.root)
            graph["nodes"]["I"]["resolution"] = {"kind": "cancelled", "snapshot": operations.relations.node_snapshot(self.root, graph["nodes"]["I"])}
            operations.relations.save(self.root, graph)
            evidence = operations.review.collect(self.root, "F", "A", "merge", ["git diff --check"], False)
            self.assertIn("onSelect", evidence["participants"]["K"]["committed"]["patch"])
            self.assertTrue(evidence["participants"]["K"]["deleted"])
            self.assertEqual(operations.recover(self.root, operation["id"], self.root)["stage"], "cleaned")

    def test_retained_branch_can_complete_new_work_without_losing_prior_results(self):
        self.seed_tree()
        self.git("switch", "-q", "A")
        child = self.base / "K"
        self.git("worktree", "add", "-q", str(child), "K")
        operations = self.module("git_operations")
        with patch.dict(os.environ, self.env, clear=True):
            previous = None
            for host, value in (("codex", "first"), ("claude", "second")):
                head = self.commit_file(child, "src/button.ts", value + "\n")
                operation = self.completion(operations)
                operations.grant(self.root, operation, host, {"session_id": host})
                result = operations.execute(self.root, operation["id"], self.root)
                self.assertEqual(result["stage"], "retained", result)
                self.assertEqual(self.git("rev-parse", "A"), head)
                if previous:
                    with self.assertRaisesRegex(RuntimeError, "실제 병합|완료.*기록"):
                        operations.verify_result(self.root, previous)
                previous = result
            node = operations.relations.read(self.root)["nodes"]["K"]
            self.assertEqual(len(node["integrations"]), 2)
            self.assertTrue(all(item["verification"] == "passed" for item in node["integrations"]))

    def test_reparented_completed_sibling_keeps_evidence_at_its_original_parent(self):
        self.seed_tree()
        self.git("switch", "-q", "A")
        child = self.base / "K"
        self.git("worktree", "add", "-q", str(child), "K")
        self.commit_file(child, "src/button.ts", "export const onSelect = (value: string) => value;\n")
        operations = self.module("git_operations")
        with patch.dict(os.environ, self.env, clear=True):
            operation = self.completion(operations)
            operations.grant(self.root, operation, "codex", {"session_id": "first"})
            operations.execute(self.root, operation["id"], self.root)
            graph = operations.relations.read(self.root)
            operations.relations.reparent(self.root, graph, graph["nodes"]["K"], graph["nodes"]["C"], self.git("rev-parse", "sy-main"))
            graph["nodes"]["I"]["resolution"] = {"kind": "cancelled", "snapshot": operations.relations.node_snapshot(self.root, graph["nodes"]["I"])}
            operations.relations.save(self.root, graph)
            evidence = operations.review.collect(self.root, "F", "A", "merge", ["git diff --check"], False)
            self.assertIn("K", evidence["participants"])
            self.assertIn("onSelect", evidence["participants"]["K"]["past_integrations"][0]["committed"]["patch"])

    def test_diverged_ff_failure_preserves_both_and_approved_merge_succeeds(self):
        self.seed_tree()
        self.git("switch", "-q", "A")
        self.commit_file(self.root, "src/parent.ts", "parent\n")
        child = self.base / "K"
        self.git("worktree", "add", "-q", str(child), "K")
        source_head = self.commit_file(child, "src/child.ts", "child\n")
        operations = self.module("git_operations")
        with patch.dict(os.environ, self.env, clear=True):
            operation = self.completion(operations)
            self.assertFalse(operation["evidence"]["text_preview"]["ff_only_possible"])
            self.assertFalse(operation["evidence"]["text_preview"]["text_conflicts"])
            operations.grant(self.root, operation, "codex", {"session_id": "one"})
            with self.assertRaises(RuntimeError):
                operations.execute(self.root, operation["id"], self.root)
            self.assertEqual(self.git("rev-parse", "K"), source_head)
            self.assertIsNone(operations.relations.read(self.root)["nodes"]["K"]["resolution"])
            second = self.completion(operations, strategy="merge")
            operations.grant(self.root, second, "opencode", {"session_id": "two"})
            result = operations.execute(self.root, second["id"], self.root)
            self.assertEqual(result["stage"], "retained", result)

    def test_new_child_between_approval_and_merge_is_not_integrated(self):
        self.seed_tree()
        self.git("switch", "-q", "A")
        operations = self.module("git_operations")
        with patch.dict(os.environ, self.env, clear=True):
            operation = self.completion(operations)
            operations.grant(self.root, operation, "codex", {"session_id": "one"})
            self.git("branch", "new-child", "K")
            graph = operations.relations.read(self.root)
            operations.relations.register(self.root, graph, "new-child", "K", self.git("rev-parse", "K"), "new work")
            operations.relations.save(self.root, graph)
            with self.assertRaisesRegex(RuntimeError, "변경|작업"):
                operations.execute(self.root, operation["id"], self.root)
            self.assertIsNone(operations.relations.read(self.root)["nodes"]["K"]["resolution"])

    def test_rename_reparent_cycle_cancel_and_name_reuse(self):
        self.seed_tree()
        operations = self.module("git_operations")
        with patch.dict(os.environ, self.env, clear=True):
            for action, name, parent, new in (("rename", "K", None, "renamed"), ("reparent", "renamed", "C", None), ("cancel", "renamed", None, None)):
                operation = operations.prepare_relation(self.root, self.root, action, name, parent, self.git("rev-parse", "HEAD"), new_name=new)
                operations.grant(self.root, operation, "codex", {"session_id": "one"})
                operations.execute(self.root, operation["id"], self.root)
            graph = operations.relations.read(self.root)
            self.assertEqual(graph["nodes"]["K"]["name"], "renamed")
            self.assertEqual(graph["nodes"]["K"]["parent"], "C")
            with self.assertRaisesRegex(RuntimeError, "순환"):
                operations.relations.reparent(self.root, graph, graph["nodes"]["C"], graph["nodes"]["K"], self.git("rev-parse", "HEAD"))
            self.git("branch", "K", "A")
            new = operations.relations.register(self.root, graph, "K", "A", self.git("rev-parse", "HEAD"), "new identity")
            self.assertNotEqual(new["id"], "K")

    def test_family_movement_is_only_a_single_notice(self):
        self.seed_tree()
        relations = self.module("branch_relations")
        with patch.dict(os.environ, self.env, clear=True):
            context = self.base / "context.json"
            self.git("switch", "-q", "A")
            self.assertEqual(relations.transition(self.root, context, self.root), "")
            self.git("switch", "-q", "C")
            self.assertIn("이어서", relations.transition(self.root, context, self.root))
            self.assertEqual(relations.transition(self.root, context, self.root), "")

    def test_parent_sync_never_records_completion(self):
        self.seed_tree()
        self.git("switch", "-q", "A")
        self.commit_file(self.root, "src/parent.ts", "parent\n")
        self.git("switch", "-q", "K")
        operations = self.module("git_operations")
        with patch.dict(os.environ, self.env, clear=True):
            operation = operations.prepare_git(self.root, self.root, "git merge --ff-only A", "codex", {"session_id": "one"})
            operations.grant(self.root, operation, "codex", {"session_id": "one"})
            operations.execute(self.root, operation["id"], self.root)
            graph = operations.relations.read(self.root)
            self.assertIsNone(graph["nodes"]["A"]["resolution"])
            self.assertFalse(graph["nodes"]["A"]["deleted"])

    def test_cleanup_failure_and_retry_never_remerge_or_lose_source(self):
        self.seed_tree()
        self.git("switch", "-q", "A")
        child = self.base / "K"
        self.git("worktree", "add", "-q", str(child), "K")
        tip = self.commit_file(child, "src/child.ts", "child\n")
        operations = self.module("git_operations")
        with patch.dict(os.environ, self.env, clear=True):
            operation = self.completion(operations, cleanup=True)
            operations.grant(self.root, operation, "codex", {"session_id": "one"})
            original = operations.run
            def fail_remove(root, args):
                if args[:2] == ["worktree", "remove"]:
                    raise RuntimeError("injected removal failure")
                return original(root, args)
            with patch.object(operations, "run", side_effect=fail_remove):
                result = operations.execute(self.root, operation["id"], self.root)
            self.assertEqual(result["stage"], "cleanup-deferred")
            self.assertTrue(child.exists())
            self.assertEqual(self.git("rev-parse", "A"), tip)
            result = operations.recover(self.root, operation["id"], self.root)
            self.assertEqual(result["stage"], "cleaned", result)
            self.assertEqual(self.git("rev-parse", "A"), tip)

    def test_verification_failure_and_log_failure_preserve_merge(self):
        self.seed_tree()
        self.git("switch", "-q", "A")
        child = self.base / "K"
        self.git("worktree", "add", "-q", str(child), "K")
        tip = self.commit_file(child, "src/child.ts", "trailing space \n")
        operations = self.module("git_operations")
        with patch.dict(os.environ, self.env, clear=True):
            operation = self.completion(operations, cleanup=True)
            operations.grant(self.root, operation, "codex", {"session_id": "one"})
            original = operations.subprocess.run
            def failed_check(args, **kwargs):
                if args == ["git", "diff", "--check"]:
                    return subprocess.CompletedProcess(args, 1, "existing validation failure", "")
                return original(args, **kwargs)
            with patch.object(operations.subprocess, "run", side_effect=failed_check):
                result = operations.execute(self.root, operation["id"], self.root)
            self.assertEqual(result["stage"], "cleanup-deferred")
            self.assertEqual(self.git("rev-parse", "A"), tip)
            self.assertTrue(child.exists())
            with patch.object(operations, "archive", side_effect=RuntimeError("log preservation failure")):
                result = operations.recover(self.root, operation["id"], self.root)
            self.assertEqual(result["stage"], "cleanup-deferred")
            self.assertIn("log preservation", result["reason"])
            self.assertTrue(child.exists())
            self.assertEqual(operations.recover(self.root, operation["id"], self.root)["stage"], "cleaned")

    def test_source_current_directory_and_new_commit_defer_cleanup(self):
        self.seed_tree()
        self.git("switch", "-q", "A")
        child = self.base / "K"
        self.git("worktree", "add", "-q", str(child), "K")
        self.commit_file(child, "src/child.ts", "child\n")
        operations = self.module("git_operations")
        with patch.dict(os.environ, self.env, clear=True):
            operation = self.completion(operations, cleanup=True, cwd=child)
            operations.grant(self.root, operation, "claude", {"session_id": "one"})
            result = operations.execute(self.root, operation["id"], child)
            self.assertEqual(result["stage"], "cleanup-deferred")
            self.assertIn("현재 실행 위치", result["reason"])
            tip = self.commit_file(child, "src/next.ts", "next\n")
            result = operations.recover(self.root, operation["id"], self.root)
            self.assertEqual(result["stage"], "cleanup-deferred")
            self.assertEqual(self.git("rev-parse", "K"), tip)
            self.assertTrue(child.exists())

    def test_recovery_never_validates_a_different_branch_in_the_target_worktree(self):
        self.seed_tree()
        self.git("switch", "-q", "A")
        child = self.base / "K"
        self.git("worktree", "add", "-q", str(child), "K")
        self.commit_file(child, "src/child.ts", "integrated\n")
        operations = self.module("git_operations")
        with patch.dict(os.environ, self.env, clear=True):
            operation = self.completion(operations, cleanup=True)
            operations.merge(self.root, operation)
            self.git("switch", "-q", "C")
            operations.finish(self.root, operation, self.root)
            self.assertEqual(operation["stage"], "cleanup-deferred", operation)
            self.assertFalse(operation.get("verification_passed"))
            self.assertTrue(child.exists())
            self.assertEqual(self.git("rev-parse", "A"), operation["result"])

    def test_unresolved_text_conflict_never_records_completion(self):
        self.seed_tree()
        self.git("switch", "-q", "A")
        self.commit_file(self.root, "src/app.ts", "parent\n")
        child = self.base / "K"
        self.git("worktree", "add", "-q", str(child), "K")
        self.commit_file(child, "src/app.ts", "child\n")
        operations = self.module("git_operations")
        with patch.dict(os.environ, self.env, clear=True):
            operation = self.completion(operations, strategy="merge")
            self.assertTrue(operation["evidence"]["text_preview"]["text_conflicts"])
            operations.grant(self.root, operation, "codex", {"session_id": "one"})
            with self.assertRaises(RuntimeError):
                operations.execute(self.root, operation["id"], self.root)
            self.assertTrue(self.git("ls-files", "-u"))
            self.assertIsNone(operations.relations.read(self.root)["nodes"]["K"]["resolution"])

    def test_native_hosts_redirect_mutations_and_keep_parent_checks(self):
        self.seed_tree()
        self.git("switch", "-q", "A")
        for host in ("codex", "claude", "opencode"):
            result = self.event("pre-tool", "git status\ngit merge --ff-only I", host=host)
            self.assertIn("직접 부모", result.stdout + result.stderr)
            for command in ("git status\ngit commit --allow-empty -m native", "git --unknown-flag status"):
                result = self.event("pre-tool", command, host=host)
                output = result.stdout + result.stderr
                self.assertTrue('"deny"' in output or result.returncode != 0)
            result = self.event("pre-tool", "git status", host=host)
            self.assertEqual(result.returncode, 0)
            self.assertNotIn('"deny"', result.stdout)

    def test_pending_write_blocks_completion_only_until_known_result(self):
        self.seed_tree()
        self.git("switch", "-q", "A")
        operations = self.module("git_operations")
        event = {"session_id": "one", "tool_call_id": "edit-one"}
        with patch.dict(os.environ, self.env, clear=True):
            operation = self.completion(operations)
            operations.reserve_write(self.root, event, "claude", [self.root])
            operations.grant(self.root, operation, "codex", {"session_id": "two"})
            with self.assertRaisesRegex(RuntimeError, "실행 중"):
                operations.execute(self.root, operation["id"], self.root)
            read = self.event("pre-tool", "git status")
            self.assertNotIn('"deny"', read.stdout)
            operations.complete_write(self.root, {**event, "tool_response": {"success": True}}, "claude")
            operation = self.completion(operations)
            operations.grant(self.root, operation, "codex", {"session_id": "two"})
            self.assertEqual(operations.execute(self.root, operation["id"], self.root)["stage"], "retained")

    def test_unknown_write_recovery_requires_a_reviewed_operation(self):
        operations = self.module("git_operations")
        event = {"session_id": "one", "tool_call_id": "edit-one"}
        with patch.dict(os.environ, self.env, clear=True):
            operations.reserve_write(self.root, event, "claude", [self.root])
            pending = next((operations.relations.directory(self.root) / "writes").glob("*.json"))
            operation = operations.prepare_write_recovery(self.root, self.root, pending.stem, "호스트에서 해당 도구가 종료됐음을 확인")
            with self.assertRaisesRegex(RuntimeError, "승인"):
                operations.execute(self.root, operation["id"], self.root)
            operations.grant(self.root, operation, "codex", {"session_id": "two"})
            operations.execute(self.root, operation["id"], self.root)
            self.assertFalse(pending.exists())

    def test_bundle_policy_difference_is_reported_without_replacement(self):
        from agent_policy.injection import compare_bundle_policy
        root = self.base / "old-bundle"
        contract = root / "policy/.agent-policy/common/contracts/runtime-policy.json"
        contract.parent.mkdir(parents=True)
        contract.write_text(json.dumps({"version": 4, "git": {"access": "shared-project"}}))
        (root / "manifest.json").write_text(json.dumps({"source_digest": "0" * 64}))
        before = contract.read_bytes()
        result = compare_bundle_policy(self.project, root)
        self.assertEqual(result["status"], "different")
        self.assertIsNone(result["original_integration"])
        self.assertEqual(result["current_integration"]["schema"], 1)
        self.assertEqual(contract.read_bytes(), before)

    def test_related_source_commit_ignores_unrelated_foreign_log_updates(self):
        log = self.root / ".claude/logs/sessions/other/handoff.md"
        log.parent.mkdir(parents=True)
        log.write_text("other log")
        operations = self.module("git_operations")
        self.commit_file(self.root, "src/other.ts", "other\n")
        (self.root / "src/app.ts").write_text("new\n")
        with patch.dict(os.environ, self.env, clear=True):
            operation = operations.prepare_git(self.root, self.root, "git commit -m source src/app.ts", "codex", {"session_id": "one"})
            operations.grant(self.root, operation, "codex", {"session_id": "one"})
            log.write_text("new unrelated log")
            operations.execute(self.root, operation["id"], self.root)
        self.assertEqual(log.read_text(), "new unrelated log")
        self.assertNotIn(".claude", self.git("show", "--name-only", "--format=", "HEAD"))

    def test_subdirectory_pathspec_cannot_stage_foreign_logs(self):
        path = self.root / ".claude/logs/sessions/other/handoff.md"
        path.parent.mkdir(parents=True)
        path.write_text("other")
        result = self.event("pre-tool", "git add -- ../.claude/logs/sessions/other/handoff.md", cwd=self.root / "src")
        self.assertIn("읽기 전용", result.stdout + result.stderr)

    def test_cleanup_preserves_ignored_local_work(self):
        self.seed_tree()
        self.git("switch", "-q", "A")
        child = self.base / "K"
        self.git("worktree", "add", "-q", str(child), "K")
        self.commit_file(child, ".gitignore", ".env.local\n")
        (child / ".env.local").write_text("LOCAL_CONFIG=preserve\n")
        operations = self.module("git_operations")
        with patch.dict(os.environ, self.env, clear=True):
            operation = self.completion(operations, cleanup=True)
            operations.grant(self.root, operation, "codex", {"session_id": "one"})
            result = operations.execute(self.root, operation["id"], self.root)
            self.assertEqual(result["stage"], "cleanup-deferred", result)
            self.assertEqual((child / ".env.local").read_text(), "LOCAL_CONFIG=preserve\n")

    def test_resolved_parent_cannot_hide_new_work_in_retained_descendants(self):
        self.seed_tree()
        relations = self.module("branch_relations")
        with patch.dict(os.environ, self.env, clear=True):
            graph = relations.read(self.root)
            head = self.git("rev-parse", "HEAD")
            graph["nodes"]["F"]["resolution"] = {"kind": "merged", "source_head": head}
            graph["nodes"]["F"]["deleted"] = True
            graph["nodes"]["I"]["resolution"] = {"kind": "merged", "source_head": head}
            self.git("branch", "-d", "F")
            self.git("switch", "-q", "I")
            self.commit_file(self.root, "src/new.ts", "new descendant work\n")
            self.assertFalse(relations.resolved(self.root, graph, graph["nodes"]["F"]))
            graph["nodes"]["K"]["resolution"] = {"kind": "cancelled", "snapshot": relations.node_snapshot(self.root, graph["nodes"]["K"])}
            self.git("branch", "new-child", "K")
            relations.register(self.root, graph, "new-child", "K", head, "new work")
            self.assertFalse(relations.resolved(self.root, graph, graph["nodes"]["K"]))


if __name__ == "__main__":
    unittest.main()
