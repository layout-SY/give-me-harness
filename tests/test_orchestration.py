"""하위 에이전트 계약, 작업 현황판과 검토 지문의 회귀 검사."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from agent_policy.core import ProjectConfig, load_project, render_project
from agent_policy.injection import prepare_injection
from agent_policy.role_profiles import role_document_paths, role_profile

CHILDREN = ("planner", "publisher", "generator", "refactorer", "watcher")
CORE_RULES = ("미확정 결정은 부모에게 반환한다", "Git 변경은 요청만 반환한다", "재조사는 변경분만 한다")


class ChildContractTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.project_root = self.root / "consumer"
        self.project_root.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.project_root, check=True)
        self.source_codex_home = self.root / "user-codex"
        self.source_codex_home.mkdir()
        (self.source_codex_home / "auth.json").write_text('{"token":"test-only"}\n', encoding="utf-8")
        self.project = ProjectConfig(id="user-ui", name="temporary-user-ui", path=self.project_root,
            commands={"dev": "npm run dev", "build": "npm run build", "lint": "npm run lint",
                      "test": "npm run test", "preview": "npm run preview"})
        executable_lookup = shutil.which
        lookup = patch("shutil.which", side_effect=lambda command, *args, **kwargs:
                       sys.executable if command == "bunx" else executable_lookup(command, *args, **kwargs))
        lookup.start()
        self.addCleanup(lookup.stop)

    def child_definitions(self, host: str, role: str = "generate") -> tuple[Path, Path, dict[str, str]]:
        launch = prepare_injection(self.project, host, role, build_root=self.root / "build",
            state_root=self.root / "state", source_codex_home=self.source_codex_home)
        directory, suffix, runtime = {
            "claude": (launch.bundle_root / "plugin/agents", ".md", launch.bundle_root / "plugin/runtime"),
            "opencode": (launch.bundle_root / "opencode-home/agents", ".md", launch.bundle_root / "opencode-home/runtime"),
            "codex": (Path(launch.environment.get("CODEX_HOME", "")) / "agents", ".toml",
                      launch.bundle_root / "policy/.agent-policy/runtime"),
        }[host]
        texts = {}
        for name in role_profile(role).native_agents:
            raw = (directory / (name + suffix)).read_text(encoding="utf-8")
            texts[name] = tomllib.loads(raw)["developer_instructions"] if suffix == ".toml" else raw
        return launch.bundle_root / "policy", runtime, texts

    def test_every_child_receives_core_contract_in_its_own_prompt(self) -> None:
        # 부모의 system prompt는 하위 에이전트에 전달되지 않는다. 질문·Git·재조사 계약은
        # 참조가 아니라 자식이 실제로 받는 정의 본문에 있어야 한다.
        for host in ("codex", "claude", "opencode"):
            _, _, texts = self.child_definitions(host)
            for name, text in texts.items():
                with self.subTest(host=host, child=name):
                    for rule in CORE_RULES:
                        self.assertIn(rule, text)
                    self.assertNotIn("{{", text)

    def test_child_policy_and_runner_paths_resolve_outside_the_consumer(self) -> None:
        # inject 방식에서 소비자 cwd에는 .agent-policy가 없다. 상대 경로는 자식이 읽을 수 없다.
        for host in ("codex", "claude", "opencode"):
            policy, runtime, texts = self.child_definitions(host)
            for name, text in texts.items():
                with self.subTest(host=host, child=name):
                    self.assertNotIn(".agent-policy/", text.replace(str(policy) + "/.agent-policy/", ""),
                                     "정책 경로가 번들 절대 경로로 바인딩되지 않았습니다.")
                    documents = re.findall(re.escape(str(policy)) + r"/\.agent-policy/common/[\w./-]+?\.md", text)
                    self.assertTrue(documents)
                    for document in documents:
                        self.assertTrue(Path(document).is_file(), document)
                    self.assertIn(f"python3 -I {runtime}/git_operations.py board", text)
                    self.assertTrue((runtime / "git_operations.py").is_file())
                    self.assertTrue((runtime / "work_board.py").is_file())

    def test_role_bodies_come_from_one_source_for_every_host(self) -> None:
        # 역할 본문은 호스트마다 따로 적지 않는다. 같은 원본이 세 호스트에 그대로 들어간다.
        source = Path(__file__).resolve().parents[1] / "policy/common/agents"
        definitions = {host: self.child_definitions(host)[2] for host in ("codex", "claude", "opencode")}
        for name in CHILDREN:
            lines = [line for line in (source / f"{name}.md").read_text(encoding="utf-8").splitlines()
                     if line.startswith("- ") and ".agent-policy/" not in line]
            self.assertGreaterEqual(len(lines), 3, name)
            for host, texts in definitions.items():
                with self.subTest(host=host, child=name):
                    for line in lines:
                        self.assertIn(line, texts[name])
        adapters = Path(__file__).resolve().parents[1] / "adapters"
        for path in adapters.glob("*/files/.*/agent*/*"):
            with self.subTest(adapter=path.name):
                self.assertIn("{{AGENT_CONTRACT:" + path.stem + "}}", path.read_text(encoding="utf-8"))

    def test_generate_children_follow_existing_ui_and_logic_working_methods(self) -> None:
        for host in ("codex", "claude", "opencode"):
            policy, _, texts = self.child_definitions(host)
            references = f"{policy}/.agent-policy/common/skills/policy/task-role-routing/references"
            skills = f"{policy}/.agent-policy/common/skills"
            with self.subTest(host=host):
                self.assertIn("`ui` 역할", texts["publisher"])
                self.assertIn(f"{references}/ui.md", texts["publisher"])
                self.assertIn(f"{skills}/policy/styles/", texts["publisher"])
                self.assertIn(f"{skills}/policy/publishing/", texts["publisher"])
                self.assertIn("unknown/ui-asset-plan.md", texts["publisher"])
                self.assertNotIn(f"{references}/logic.md", texts["publisher"])
                for name in ("generator", "refactorer"):
                    self.assertIn("`logic` 역할", texts[name])
                    self.assertIn(f"{references}/logic.md", texts[name])
                    self.assertIn(f"{skills}/recipe/api-authoring/", texts[name])
                    self.assertIn(f"{skills}/policy/data-fetch-layer/", texts[name])
                    self.assertNotIn(f"{references}/ui.md", texts[name])
                self.assertIn("`review` 역할", texts["watcher"])
                self.assertIn(f"{skills}/policy/review-checklist/", texts["watcher"])
                self.assertIn("`orchest` 역할", texts["planner"])

    def test_work_items_are_assigned_by_change_kind_and_ui_logic_run_in_parallel_then_connect(self) -> None:
        # UI·스타일은 Publisher, 로직은 Generator·Refactorer. 생성뿐 아니라 수정·삭제도 같은 기준이다.
        for host in ("codex", "claude", "opencode"):
            _, _, texts = self.child_definitions(host)
            with self.subTest(host=host):
                self.assertIn("변경 종류(생성·수정·삭제), 대상 경로와 담당 하위 에이전트를 지정한다", texts["planner"])
                self.assertIn("스타일·디자인 토큰, 정적 자산, 접근성, 반응형 표현의 생성·수정·삭제와 이들의 리팩터링", texts["publisher"])
                self.assertIn("상태 전이와 controller의 생성·수정·삭제", texts["generator"])
                self.assertIn("동작을 바꾸지 않는 구조 정리", texts["refactorer"])
                for name in CHILDREN:
                    self.assertIn("역할 밖의 변경은 반환한다", texts[name])
                # 병렬 구간: 같은 계약에 각자 맞추고 포맷·검증은 미룬다. 연결은 Generator가 맡는다.
                self.assertIn("확정된 연결 계약의 props·callback만 사용해 화면을 구현한다", texts["publisher"])
                self.assertIn("UI 없는 controller까지 구현한다", texts["generator"])
                self.assertIn("최종 연결 단계를 맡는다", texts["generator"])
                for name in ("publisher", "generator"):
                    self.assertIn("병렬 구간이라고 알린 경우에는 포맷과 검증 명령을 실행하지 않고", texts[name])
        rendered = render_project(load_project("user-ui"))
        skills = ".agent-policy/common/skills"
        roles = rendered[f"{skills}/policy/task-role-routing/references/pipeline-roles.md"].decode()
        for expected in ("### 작업 항목 배정 기준", "### UI와 Logic의 병렬 구현과 최종 연결",
                         "생성·수정·삭제에 같은 기준을 적용한다", "두 에이전트의 수정 파일은 겹치지 않아야 한다"):
            self.assertIn(expected, roles)
        self.assertIn("`controller -> 계약 <- UI`",
                      rendered[f"{skills}/recipe/api-authoring/references/ui-controller.md"].decode())
        template = rendered[".agent-policy/common/templates/plan.template.md"].decode()
        self.assertIn("| 작업 항목 | 변경 종류(생성·수정·삭제) | 대상 경로 | 담당 역할·에이전트 |", template)
        self.assertIn("연결 계약이 확정되고 수정 파일이 겹치지 않는 Publisher와 Generator만 병렬로 호출한다",
                      rendered[f"{skills}/policy/task-role-routing/references/orchestration.md"].decode())

    def test_role_sessions_keep_their_own_working_method_for_children(self) -> None:
        # 매핑은 통합 구현 세션에만 적용한다. UI 세션의 Generator는 UI 방식으로 작업한다.
        policy, _, texts = self.child_definitions("claude", "ui")
        references = f"{policy}/.agent-policy/common/skills/policy/task-role-routing/references"
        for name in ("publisher", "generator", "refactorer"):
            with self.subTest(child=name):
                self.assertIn("세션 role은 `ui`이고, 이 에이전트에는 `ui` 역할", texts[name])
                self.assertIn(f"{references}/ui.md", texts[name])
                self.assertNotIn("logic.md", texts[name])
        _, _, logic = self.child_definitions("codex", "logic")
        self.assertIn("`logic` 역할", logic["generator"])

    def test_figma_mcp_reaches_only_the_claude_publisher(self) -> None:
        claude = prepare_injection(self.project, "claude", "generate", build_root=self.root / "build",
            state_root=self.root / "state", source_codex_home=self.source_codex_home)
        servers = json.loads((claude.bundle_root / "claude-mcp.json").read_text(encoding="utf-8"))["mcpServers"]
        self.assertEqual(set(servers), {"TalkToFigma"})
        publisher = (claude.bundle_root / "plugin/agents/publisher.md").read_text(encoding="utf-8")
        self.assertIn("tools: Read, Grep, Glob, Bash, Edit, Write, Skill, mcp__TalkToFigma\n", publisher)
        self.assertIn("TalkToFigma", publisher)
        for name in ("generator", "refactorer", "planner", "watcher"):
            self.assertNotIn("TalkToFigma", (claude.bundle_root / f"plugin/agents/{name}.md").read_text(encoding="utf-8"))
        for host in ("codex", "opencode"):
            launch = prepare_injection(self.project, host, "generate", build_root=self.root / "build",
                state_root=self.root / "state", source_codex_home=self.source_codex_home)
            self.assertNotIn("--mcp-config", launch.command)
            self.assertNotIn("Figma", self.child_definitions(host)[2]["publisher"])

    def test_generate_session_offers_planning_and_implementation_children(self) -> None:
        profile = role_profile("generate")
        self.assertEqual(set(profile.native_agents), set(CHILDREN))
        self.assertTrue(any(path.endswith("references/orchestration.md") for path in role_document_paths("claude", "generate")))
        # 기획 전용 세션은 구현 자식을 받지 않고 source도 쓰지 않는다.
        self.assertEqual(role_profile("orchest").native_agents, ("planner",))

    def test_parent_prompt_explains_board_commands_and_changed_only_replanning(self) -> None:
        for host in ("codex", "claude", "opencode"):
            with self.subTest(host=host):
                launch = prepare_injection(self.project, host, "generate", build_root=self.root / "build",
                    state_root=self.root / "state", source_codex_home=self.source_codex_home)
                prompt = launch.system_prompt.read_text(encoding="utf-8")
                for expected in ("git_operations.py board-set", "git_operations.py board-wait",
                                 "git_operations.py fingerprint", "변경 파일만 다시 조사",
                                 "하위 에이전트가 요청만 반환하고 부모가 사용자 승인 후 실행"):
                    self.assertIn(expected, prompt)

    def test_claude_watcher_can_write_its_review_document(self) -> None:
        rendered = render_project(load_project("user-ui"))[".claude/agents/watcher.md"].decode()
        self.assertIn("tools: Read, Grep, Glob, Bash, Write\n", rendered)


class WorkBoardTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.root = self.base / "repo"
        self.root.mkdir()
        self.git("init", "-q", "-b", "sy-main")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "policy@example.test")
        (self.root / "src/shared/ui").mkdir(parents=True)
        (self.root / "src/shared/ui/Button.tsx").write_text("export const Button = 1;\n")
        (self.root / "src/app.ts").write_text("export const value = 1;\n")
        self.git("add", "--", "src")
        self.git("commit", "-qm", "base")
        self.project = replace(load_project("user-ui"), path=self.root)
        self.runtime = self.base / "bundle/.agent-policy/runtime"
        for name, content in render_project(self.project).items():
            if name.startswith((".agent-policy/runtime/", ".agent-policy/common/contracts/")):
                target = self.base / "bundle" / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
        self.state = self.base / "state"
        self.env = {key: value for key, value in os.environ.items() if not key.startswith("ASAN_")}
        self.env.update(ASAN_AGENT_POLICY_STATE_ROOT=str(self.state), ASAN_AGENT_POLICY_ROLE="generate",
                        ASAN_SESSION_DIR=".claude/logs/sessions/current")
        self.repository = self.state / "repositories" / hashlib.sha256(str(self.root / ".git").encode()).hexdigest()
        self.calls = 0

    def git(self, *args, root=None) -> str:
        return subprocess.check_output(["git", *args], cwd=root or self.root, text=True).strip()

    def runner(self, *args, cwd=None, ok=True):
        result = subprocess.run([sys.executable, "-I", str(self.runtime / "git_operations.py"), *args],
            cwd=cwd or self.root, env=self.env, text=True, capture_output=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        return result.stderr

    def event(self, mode, command="", *, host="claude", prompt="", **extra):
        self.calls += 1
        event = {"cwd": str(self.root), "session_id": f"{host}-test", "tool_use_id": str(self.calls),
                 "tool_name": "Bash", "tool_input": {"command": command}, "prompt": prompt, **extra}
        return subprocess.run([sys.executable, "-I", str(self.runtime / "managed_policy_guard.py"), mode, host],
            input=json.dumps(event), cwd=self.root, env=self.env, text=True, capture_output=True)

    def branch(self, name: str, *files: str, parent: str = "sy-main") -> Path:
        tree = self.base / "trees" / name
        self.git("worktree", "add", "-q", "-b", name, str(tree), parent)
        for file in files:
            target = tree / file
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f"// {name}\nimport {{ Button }} from '@/shared/ui/Button';\n")
        return tree

    def commit(self, tree: Path, message: str = "work") -> str:
        self.git("add", "-A", root=tree)
        self.git("commit", "-qm", message, root=tree)
        return self.git("rev-parse", "HEAD", root=tree)

    def seed_relations(self, *pairs: tuple[str, str | None]) -> None:
        base = self.git("rev-parse", "sy-main")
        nodes = {name: {"id": name, "name": name, "parent": parent, "fork_commit": base, "purpose": name,
                        "revision": 1, "activity": 0, "deleted": False, "resolution": None}
                 for name, parent in pairs}
        directory = self.repository / "branch-relations/v1"
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "graph.json").write_text(json.dumps({"version": 1, "revision": 1, "nodes": nodes}))

    def test_overlapping_scope_is_reported_without_blocking_registration(self) -> None:
        first = self.runner("board-set", "--task", "A", "--title", "버튼 수정", "--stage", "planning",
                            "--scope", "src/shared/ui")
        self.assertEqual(first["overlaps"], [])
        second = self.runner("board-set", "--task", "B", "--title", "버튼 사용", "--stage", "planning",
                             "--scope", "src/app.ts", "--shared", "src/shared/ui/Button.tsx")
        self.assertEqual([(item["task"], item["paths"]) for item in second["overlaps"]],
                         [("A", ["src/shared/ui/Button.tsx"])])
        self.assertEqual(second["task"]["stage"], "planning")
        # 현황판 기록은 소유권·허용 파일 목록을 만들지 않는다.
        self.assertFalse((self.repository / "claims").exists())
        self.assertIn("새 작업은", self.runner("board-set", "--task", "C", "--stage", "planning", ok=False))
        self.assertIn("지원하는 단계", self.runner("board-set", "--task", "A", "--stage", "locked", ok=False))

    def test_git_result_stages_are_checked_against_the_repository(self) -> None:
        self.assertIn("실제로 존재하는 작업 branch",
                      self.runner("board-set", "--task", "A", "--title", "A", "--stage", "working", "--branch", "A1", ok=False))
        tree = self.branch("A1", "src/feature.ts")
        working = self.runner("board-set", "--task", "A", "--title", "A", "--stage", "working", "--branch", "A1")
        self.assertEqual(working["task"]["worktree"], str(tree))
        self.assertEqual(working["task"]["base_head"], self.git("rev-parse", "sy-main"))
        self.assertIn("커밋되지 않은 변경", self.runner("board-set", "--task", "A", "--stage", "committed", ok=False))
        head = self.commit(tree)
        self.assertEqual(self.runner("board-set", "--task", "A", "--stage", "committed")["task"]["head"], head)
        self.seed_relations(("sy-main", None), ("A1", "sy-main"))
        self.assertIn("병합된 사실을 확인할 수 없습니다", self.runner("board-set", "--task", "A", "--stage", "merged", ok=False))
        self.git("merge", "-q", "--ff-only", "A1")
        self.assertEqual(self.runner("board-set", "--task", "A", "--stage", "merged")["task"]["stage"], "merged")
        self.assertIn("아직 남아 있습니다", self.runner("board-set", "--task", "A", "--stage", "removed", ok=False))

    def test_waiting_task_is_released_at_commit_with_only_changed_overlap_files(self) -> None:
        tree = self.branch("A1")
        self.runner("board-set", "--task", "A", "--title", "A", "--stage", "working", "--branch", "A1",
                    "--scope", "src/shared/ui", "src/a-only.ts")
        waiting = self.runner("board-set", "--task", "B", "--title", "B", "--stage", "planning",
                              "--scope", "src/shared/ui", "src/b.ts", "--wait-for", "A")
        self.assertEqual(waiting["task"]["waiting_on"]["overlap"], ["src/shared/ui"])
        self.assertFalse(waiting["release"]["released"])
        blocked = self.runner("board-wait", "--task", "B", "--timeout", "0")
        self.assertEqual((blocked["released"], blocked["timed_out"]), (False, True))
        self.assertIn("기다리는 중", self.event("session-start").stdout)
        self.assertEqual(self.event("user-prompt", prompt="상태 알려줘").stdout, "")

        (tree / "src/shared/ui/Button.tsx").write_text("export const Button = 2;\n")
        (tree / "src/a-only.ts").write_text("export const only = 1;\n")
        # 미커밋 완료는 대기를 풀지 않는다. 사용자 검토에서 내용이 바뀔 수 있다.
        self.runner("board-set", "--task", "A", "--stage", "awaiting-user-review")
        self.assertFalse(self.runner("board-wait", "--task", "B", "--timeout", "0")["released"])
        head = self.commit(tree)
        self.runner("board-set", "--task", "A", "--stage", "committed")

        released = self.runner("board-wait", "--task", "B", "--timeout", "0")
        self.assertEqual((released["released"], released["timed_out"], released["to_head"]), (True, False, head))
        self.assertEqual(released["changed_files"], ["src/shared/ui/Button.tsx"])
        self.assertIn("이미 조사한 내용은 다시 조사하지 않습니다", released["instruction"])
        for host in ("claude", "codex"):
            self.assertIn("src/shared/ui/Button.tsx", self.event("session-start", host=host).stdout)
        notice = self.event("user-prompt", prompt="이어서 해줘").stdout
        self.assertIn("[WORK_BOARD]", notice)
        self.assertIn("src/shared/ui/Button.tsx", notice)
        self.assertNotIn("a-only.ts", notice)
        # 같은 해제는 사용자 입력마다 반복하지 않는다.
        self.assertEqual(self.event("user-prompt", prompt="계속").stdout, "")
        self.assertIsNone(self.runner("board-set", "--task", "B", "--clear-wait")["task"]["waiting_on"])
        self.assertEqual(self.event("session-start").stdout.count("[WORK_BOARD]"), 0)

    def test_mutual_waiting_is_rejected_and_reported(self) -> None:
        for name in ("A", "B"):
            self.runner("board-set", "--task", name, "--title", name, "--stage", "planning", "--scope", "src")
        self.runner("board-set", "--task", "B", "--wait-for", "A")
        self.assertIn("서로를 기다리게", self.runner("board-set", "--task", "A", "--wait-for", "B", ok=False))
        self.assertIn("현황판에 없는 선행 작업", self.runner("board-set", "--task", "A", "--wait-for", "none", ok=False))

    def test_view_lists_relations_children_first_merge_order_and_actual_state(self) -> None:
        self.branch("A1")
        tree = self.branch("B1", "src/b.ts", parent="A1")
        self.seed_relations(("sy-main", None), ("A1", "sy-main"), ("B1", "A1"))
        self.runner("board-set", "--task", "B", "--title", "B", "--stage", "working", "--branch", "B1")
        board = self.runner("board")
        self.assertEqual(board["merge_order"], ["B1 → A1", "A1 → sy-main"])
        self.assertEqual({item["branch"]: item["parent"] for item in board["branches"]},
                         {"sy-main": None, "A1": "sy-main", "B1": "A1"})
        task = board["tasks"][0]
        self.assertEqual((task["id"], task["stage_label"], task["actual"]["uncommitted"]),
                         ("B", "작업 중", {str(tree): ["src/b.ts"]}))
        self.assertTrue(all(item["registered"] for item in board["worktrees"]))

    def test_shared_item_check_reports_tasks_and_other_worktree_usage(self) -> None:
        tree = self.branch("A1", "src/pages/Home.tsx")
        self.runner("board-set", "--task", "A", "--title", "A", "--stage", "working", "--branch", "A1",
                    "--scope", "src/pages", "--shared", "src/shared/ui/Button.tsx")
        result = self.runner("board", "--check", "src/shared/ui/Button.tsx")
        self.assertEqual([(item["task"], item["paths"]) for item in result["tasks"]], [("A", ["src/shared/ui/Button.tsx"])])
        self.assertEqual(result["usage"][str(tree)]["references"]["src/shared/ui/Button.tsx"]["files"],
                         ["src/pages/Home.tsx"])
        self.assertEqual(self.runner("board", "--check", "src/app.ts")["usage"], {})

    def test_review_fingerprint_changes_only_with_reviewed_content(self) -> None:
        first = self.runner("fingerprint")
        self.assertEqual(self.runner("fingerprint")["fingerprint"], first["fingerprint"])
        review = self.root / ".claude/logs/sessions/current/review-log.md"
        review.parent.mkdir(parents=True)
        review.write_text("PASS\n")
        self.assertEqual(self.runner("fingerprint")["fingerprint"], first["fingerprint"],
                         "Watcher의 리뷰 문서는 검토 대상 버전을 바꾸지 않습니다.")
        (self.root / "src/new.ts").write_text("export {};\n")
        changed = self.runner("fingerprint")
        self.assertNotEqual(changed["fingerprint"], first["fingerprint"])
        self.assertEqual(changed["changed"], ["src/new.ts"])

    PLAN = "# 계획\n<!-- asan-plan:approval:start:v1 -->\n## 목표\n{goal}\n<!-- asan-plan:approval:end:v1 -->\n## 진행\n"

    def task(self, name: str, goal: str = "구현") -> tuple[Path, Path]:
        tree = self.branch(name + "1")
        (tree / "src").mkdir(exist_ok=True)
        (tree / "src/app.ts").write_text("export const value = 1;\n")
        plan = self.root / f".claude/logs/sessions/current/tasks/{name}/plan.md"
        plan.parent.mkdir(parents=True, exist_ok=True)
        plan.write_text(self.PLAN.format(goal=goal))
        self.runner("board-set", "--task", name, "--title", name, "--stage", "working", "--branch", name + "1",
                    "--plan", str(plan))
        for tool, args in (("Skill", {"skill": "policy"}), ("Read", {"file_path": str(tree / "src/app.ts")})):
            self.tool("post-tool", tool, args, cwd=tree, tool_response={"success": True})
        return tree, plan

    def tool(self, mode, name, data, *, cwd=None, **extra):
        self.calls += 1
        event = {"cwd": str(cwd or self.root), "session_id": "claude-test", "tool_use_id": str(self.calls),
                 "tool_name": name, "tool_input": data, **extra}
        return subprocess.run([sys.executable, "-I", str(self.runtime / "managed_policy_guard.py"), mode, "claude"],
            input=json.dumps(event), cwd=self.root, env=self.env, text=True, capture_output=True)

    def edit(self, tree: Path):
        return self.tool("pre-tool", "Edit", {"file_path": str(tree / "src/app.ts"), "old_string": "1", "new_string": "2"}, cwd=tree)

    def test_each_task_plan_is_approved_only_by_its_task_id(self) -> None:
        first, plan = self.task("A")
        second, _ = self.task("B")
        # 일반 승인은 아직 보지 않은 작업 계획까지 승인하지 않는다.
        self.event("user-prompt", prompt="진행")
        for tree, name in ((first, "A"), (second, "B")):
            self.assertIn(f"작업 {name}의 계획 승인(사용자 입력: `{name} 진행`)", self.edit(tree).stderr)
        self.assertIn("작업 A의 계획을 승인했습니다", self.event("user-prompt", prompt="A 진행").stdout)
        self.assertEqual(self.edit(first).returncode, 0, self.edit(first).stderr)
        self.assertIn("작업 B의 계획 승인", self.edit(second).stderr)
        # 승인한 뒤 계획의 승인 영역이 바뀌면 그 작업만 다시 승인받는다.
        plan.write_text(self.PLAN.format(goal="범위 확대"))
        self.assertIn("작업 A의 계획 승인", self.edit(first).stderr)
        self.assertIn("승인했습니다", self.event("user-prompt", prompt="작업 A B 진행").stdout)
        self.assertEqual(self.edit(first).returncode, 0)
        self.assertEqual(self.edit(second).returncode, 0)
        self.assertIn("취소했습니다", self.event("user-prompt", prompt="B 구현 승인 취소").stdout)
        self.assertEqual(self.edit(first).returncode, 0)
        self.assertIn("작업 B의 계획 승인", self.edit(second).stderr)

    def test_task_plan_must_be_a_session_plan_and_have_an_approval_region(self) -> None:
        self.branch("A1")
        outside = self.root / "src/plan.md"
        outside.write_text("계획")
        self.assertIn("세션 산출물 아래", self.runner("board-set", "--task", "A", "--title", "A", "--stage", "planning",
                                                    "--plan", str(outside), ok=False))
        tree, plan = self.task("C")
        plan.write_text("<!-- asan-plan:approval:start:v1 -->\n \n<!-- asan-plan:approval:end:v1 -->\n")
        self.assertIn("승인 영역", self.event("user-prompt", prompt="C 진행").stdout)
        self.assertIn("작업 C: plan.md 승인 영역", self.edit(tree).stderr)

    def test_worktree_without_board_task_keeps_session_plan_approval(self) -> None:
        plan = self.root / ".claude/logs/sessions/current/plan.md"
        plan.parent.mkdir(parents=True, exist_ok=True)
        plan.write_text(self.PLAN.format(goal="세션 작업"))
        for tool, args in (("Skill", {"skill": "policy"}), ("Read", {"file_path": str(self.root / "src/app.ts")})):
            self.tool("post-tool", tool, args, tool_response={"success": True})
        self.assertIn("사용자 구현 승인", self.edit(self.root).stderr)
        self.event("user-prompt", prompt="진행")
        self.assertEqual(self.edit(self.root).returncode, 0, self.edit(self.root).stderr)

    def test_task_artifacts_have_their_own_folder_and_are_mirrored(self) -> None:
        base = ".claude/logs/sessions/current"
        for relative, allowed in ((f"{base}/tasks/A/plan.md", True), (f"{base}/tasks/A/review-log.md", True),
                                  (f"{base}/tasks/A/unknown/notes.md", True), (f"{base}/tasks/A/random.md", False),
                                  (f"{base}/tasks/bad id/plan.md", False), (f"{base}/random.md", False)):
            with self.subTest(path=relative):
                result = self.tool("pre-tool", "Write", {"file_path": str(self.root / relative), "content": "x"})
                self.assertEqual(result.returncode == 0, allowed, result.stderr)
        from agent_policy.log_mirror import collect_project_logs
        target = self.root / base / "tasks/A/plan.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("계획")
        copied = collect_project_logs(self.project, "claude", logs_root=self.base / "central").copied
        self.assertIn("current/tasks/A/plan.md", copied)

    def test_another_session_finds_unfinished_tasks_and_must_reapprove(self) -> None:
        tree, _ = self.task("A")
        self.event("user-prompt", prompt="A 진행")
        self.assertEqual(self.edit(tree).returncode, 0)
        first = dict(self.env, ASAN_AGENT_POLICY_ASSIGNMENT="a" * 32)
        second = dict(self.env, ASAN_AGENT_POLICY_ASSIGNMENT="b" * 32)
        run = lambda env, *args: json.loads(subprocess.run(
            [sys.executable, "-I", str(self.runtime / "git_operations.py"), *args],
            cwd=self.root, env=env, text=True, capture_output=True, check=True).stdout)
        run(first, "board-set", "--task", "A", "--stage", "reviewing")
        board = run(second, "board")
        self.assertEqual([(item["task"], item["stage"], item["worktree"]) for item in board["resumable"]],
                         [("A", "리뷰 중", str(tree))])
        self.assertIn("다시 승인", board["resume"])
        self.assertEqual(run(first, "board")["resumable"], [])
        # 새 세션(다른 host session)은 이전 세션의 계획 승인을 승계하지 않는다.
        self.calls += 1
        fresh = subprocess.run([sys.executable, "-I", str(self.runtime / "managed_policy_guard.py"), "pre-tool", "claude"],
            input=json.dumps({"cwd": str(tree), "session_id": "claude-new", "tool_use_id": str(self.calls), "tool_name": "Edit",
                              "tool_input": {"file_path": str(tree / "src/app.ts"), "old_string": "1", "new_string": "2"}}),
            cwd=self.root, env=self.env, text=True, capture_output=True)
        self.assertIn("작업 A의 계획 승인", fresh.stderr)

    def test_child_agent_cannot_prepare_or_run_git_changes_where_host_identifies_it(self) -> None:
        runner = f"python3 -I {self.runtime / 'git_operations.py'}"
        operations = self.repository / "branch-relations/v1/operations"
        for command in ("git commit --allow-empty -m child", "git branch X",
                        f"{runner} board-set --task A --title A --stage planning",
                        f"{runner} relation --action register --name A1 --parent sy-main --fork HEAD --purpose p"):
            with self.subTest(command=command):
                result = self.event("pre-tool", command, agent_id="agent-1", agent_type="generator")
                self.assertEqual(result.returncode, 2)
                self.assertIn("하위 에이전트는 Git 변경과 현황판 갱신을 실행하지 않습니다", result.stderr)
        self.assertFalse(operations.exists() and any(operations.iterdir()), "자식의 요청으로 승인 대상을 준비하지 않습니다.")
        for command in ("git status --short", f"{runner} board", f"{runner} fingerprint"):
            with self.subTest(command=command):
                self.assertEqual(self.event("pre-tool", command, agent_id="agent-1").returncode, 0)
        # 부모의 같은 명령은 기존 승인 경로로 이어진다.
        parent = self.event("pre-tool", "git commit --allow-empty -m parent")
        self.assertIn("보호 실행", parent.stderr)
        self.assertEqual(self.event("pre-tool", f"{runner} board-set --task A --title A --stage planning").returncode, 0)


if __name__ == "__main__":
    unittest.main()
