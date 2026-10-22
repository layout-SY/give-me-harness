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
import time
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

    def child_definitions(self, host: str, role: str = "orchest") -> tuple[Path, Path, dict[str, str]]:
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

    def test_orchest_children_follow_existing_ui_and_logic_working_methods(self) -> None:
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
        roles = rendered[f"{skills}/policy/task-role-routing/references/orchestration.md"].decode()
        for expected in ("### 작업 항목 배정 기준", "### UI와 Logic의 병렬 구현과 최종 연결",
                         "생성·수정·삭제에 같은 기준을 적용한다", "두 에이전트의 수정 파일은 겹치지 않아야 한다"):
            self.assertIn(expected, roles)
        # 기존 세션이 함께 쓰는 문서에는 오케스트레이션 계약을 넣지 않는다.
        self.assertNotIn("작업 항목 배정 기준",
                         rendered[f"{skills}/policy/task-role-routing/references/pipeline-roles.md"].decode())
        self.assertIn("연결 계약이 확정되고 수정 파일이 겹치지 않는 Publisher와 Generator만 병렬로 호출한다",
                      rendered[f"{skills}/policy/task-role-routing/references/orchestration.md"].decode())

    def test_other_role_sessions_keep_their_original_prompts_and_children(self) -> None:
        # 오케스트레이션 계약은 orchest 세션에만 적용한다. 기존 logic·ui·review·generate 세션은 그대로 둔다.
        rendered = render_project(self.project)
        source = {"claude": ".claude/agents/", "opencode": ".opencode/agent/", "codex": ".codex/agents/"}
        for host in ("codex", "claude", "opencode"):
            for role in ("logic", "ui", "review", "generate"):
                with self.subTest(host=host, role=role):
                    launch = prepare_injection(self.project, host, role, build_root=self.root / "build",
                        state_root=self.root / "state", source_codex_home=self.source_codex_home)
                    directory = {"claude": launch.bundle_root / "plugin/agents",
                                 "opencode": launch.bundle_root / "opencode-home/agents",
                                 "codex": Path(launch.environment.get("CODEX_HOME", "")) / "agents"}[host]
                    installed = sorted(directory.iterdir())
                    self.assertEqual({path.stem for path in installed}, set(role_profile(role).native_agents))
                    for path in installed:
                        self.assertEqual(path.read_bytes(), rendered[source[host] + path.name],
                                         "기존 세션의 하위 에이전트 정의는 adapter 원본 그대로여야 합니다.")
                        self.assertNotIn("세션 바인딩", path.read_text(encoding="utf-8"))
                    prompt = launch.system_prompt.read_text(encoding="utf-8")
                    for absent in ("파이프라인 계약", "현황판", "board-set", "verdict", "직접 수정 승인", "파이프라인 게이트"):
                        self.assertNotIn(absent, prompt)
                    # 오케스트레이션 계약은 그 세션의 번들에만 들어가고, 공통 runtime 계약은 그대로다.
                    contracts = launch.bundle_root / "policy/.agent-policy/common/contracts"
                    self.assertFalse((contracts / "orchestration-policy.json").exists())
                    self.assertEqual((contracts / "runtime-policy.json").read_bytes(),
                                     rendered[".agent-policy/common/contracts/runtime-policy.json"])
                    self.assertNotIn(b"work_board", (contracts / "runtime-policy.json").read_bytes())
        ui = prepare_injection(self.project, "claude", "ui", build_root=self.root / "build",
            state_root=self.root / "state", source_codex_home=self.source_codex_home)
        skill = (ui.bundle_root / "plugin/skills/project-ui/SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("orchest", skill)
        codex = prepare_injection(self.project, "codex", "logic", build_root=self.root / "build",
            state_root=self.root / "state", source_codex_home=self.source_codex_home)
        rule = (Path(codex.environment["CODEX_HOME"]) / "rules/asan-git-operations.rules").read_text(encoding="utf-8")
        for action in ("board", "verdict", "fingerprint"):
            self.assertNotIn(f'"{action}"', rule)

    def test_orchest_bundle_carries_its_own_contract_and_runner_actions(self) -> None:
        for host in ("codex", "claude", "opencode"):
            launch = prepare_injection(self.project, host, "orchest", build_root=self.root / "build",
                state_root=self.root / "state", source_codex_home=self.source_codex_home)
            contract = json.loads((launch.bundle_root / "policy/.agent-policy/common/contracts/orchestration-policy.json").read_text())
            self.assertEqual(contract["roles"], ["orchest"])
            self.assertIn("이 절이 우선한다", launch.system_prompt.read_text(encoding="utf-8"))
        rule = (Path(launch.environment.get("CODEX_HOME", "")) / "rules/asan-git-operations.rules")
        codex = prepare_injection(self.project, "codex", "orchest", build_root=self.root / "build",
            state_root=self.root / "state", source_codex_home=self.source_codex_home)
        rule = (Path(codex.environment["CODEX_HOME"]) / "rules/asan-git-operations.rules").read_text(encoding="utf-8")
        for action in ("board", "board-set", "board-wait", "fingerprint", "verdict", "execute"):
            self.assertIn(f'"{action}"', rule)
        self.assertEqual(role_profile("generate").native_agents, ("publisher", "generator", "refactorer", "watcher"))
        self.assertEqual(role_profile("generate").summary, "승인된 handoff와 branch scope에 적힌 기본 역할을 구현한다.")
    def test_figma_mcp_reaches_only_the_claude_publisher(self) -> None:
        claude = prepare_injection(self.project, "claude", "orchest", build_root=self.root / "build",
            state_root=self.root / "state", source_codex_home=self.source_codex_home)
        servers = json.loads((claude.bundle_root / "claude-mcp.json").read_text(encoding="utf-8"))["mcpServers"]
        self.assertEqual(set(servers), {"TalkToFigma"})
        publisher = (claude.bundle_root / "plugin/agents/publisher.md").read_text(encoding="utf-8")
        self.assertIn("tools: Read, Grep, Glob, Bash, Edit, Write, Skill, mcp__TalkToFigma\n", publisher)
        self.assertIn("TalkToFigma", publisher)
        for name in ("generator", "refactorer", "planner", "watcher"):
            self.assertNotIn("TalkToFigma", (claude.bundle_root / f"plugin/agents/{name}.md").read_text(encoding="utf-8"))
        for host in ("codex", "opencode"):
            launch = prepare_injection(self.project, host, "orchest", build_root=self.root / "build",
                state_root=self.root / "state", source_codex_home=self.source_codex_home)
            self.assertNotIn("--mcp-config", launch.command)
            self.assertNotIn("Figma", self.child_definitions(host)[2]["publisher"])
        generate = prepare_injection(self.project, "claude", "generate", build_root=self.root / "build",
            state_root=self.root / "state", source_codex_home=self.source_codex_home)
        self.assertNotIn("--mcp-config", generate.command)

    def test_orchest_session_offers_planning_implementation_and_review_children(self) -> None:
        profile = role_profile("orchest")
        self.assertEqual(set(profile.native_agents), set(CHILDREN))
        documents = role_document_paths("claude", "orchest")
        for name in ("orchestration.md", "logic.md", "ui.md"):
            self.assertTrue(any(path.endswith("references/" + name) for path in documents), name)
    def test_parent_prompt_explains_board_commands_and_changed_only_replanning(self) -> None:
        for host in ("codex", "claude", "opencode"):
            with self.subTest(host=host):
                launch = prepare_injection(self.project, host, "orchest", build_root=self.root / "build",
                    state_root=self.root / "state", source_codex_home=self.source_codex_home)
                prompt = launch.system_prompt.read_text(encoding="utf-8")
                for expected in ("git_operations.py board-set", "git_operations.py board-wait",
                                 "git_operations.py fingerprint", "변경 파일만 다시 조사",
                                 "하위 에이전트가 요청만 반환하고 부모가 사용자 승인 후 실행"):
                    self.assertIn(expected, prompt)

    def test_unrequested_design_decisions_are_offered_as_options_before_acting(self) -> None:
        # 요청에 없는 설계·운영 결정을 임의로 정해 구현한 뒤 사후 보고하지 않는다.
        rule = "문제 상황과 둘 이상의 방안, 각 방안의 장단점·영향과 권장안을 제시하고 사용자가 선택한 뒤 진행한다"
        for host in ("codex", "claude", "opencode"):
            for role in ("logic", "ui", "orchest", "review", "generate"):
                with self.subTest(host=host, role=role):
                    launch = prepare_injection(self.project, host, role, build_root=self.root / "build",
                        state_root=self.root / "state", source_codex_home=self.source_codex_home)
                    prompt = launch.system_prompt.read_text(encoding="utf-8")
                    self.assertIn(rule, prompt)
                    self.assertIn("먼저 구현하고 사후에 보고하는 것으로 대신하지 않는다", prompt)
                    self.assertNotIn("권장안을 함께 제시할 수 있지만", prompt)
            for name, text in self.child_definitions(host)[2].items():
                with self.subTest(host=host, child=name):
                    self.assertIn("설계 선택(구현 구조, 작업 순서, 담당 등)을 임의로 정하지 않는다", text)
                    self.assertIn("둘 이상의 방안과 각 방안의 장단점·영향, 권장안을 정리해 반환", text)
        central = Path(__file__).resolve().parents[1]
        for name in ("CLAUDE.md", "AGENTS.md"):
            self.assertIn(rule, (central / name).read_text(encoding="utf-8"), name)

    def test_token_usage_skill_is_bundled_only_for_orchestration(self) -> None:
        skill = ".agent-policy/common/skills/policy/token-usage"
        for host in ("codex", "claude", "opencode"):
            with self.subTest(host=host):
                policy, _, _ = self.child_definitions(host)
                for name in ("SKILL.md", "references/report.md", "scripts/token_usage.py"):
                    self.assertTrue((policy / skill / name).is_file(), name)
                launch = prepare_injection(self.project, host, "orchest", build_root=self.root / "build",
                    state_root=self.root / "state", source_codex_home=self.source_codex_home)
                prompt = launch.system_prompt.read_text(encoding="utf-8")
                for expected in ("### 토큰 사용량 분석", "`토큰 분석`", "policy/token-usage/SKILL.md",
                                 "`unknown/token-usage-report.md`", "`review`를 `--cleanup` 없이"):
                    self.assertIn(expected, prompt)
                for role in ("logic", "ui"):
                    other = prepare_injection(self.project, host, role, build_root=self.root / "build",
                        state_root=self.root / "state", source_codex_home=self.source_codex_home)
                    self.assertFalse((other.bundle_root / "policy" / skill).exists(), role)
                    self.assertNotIn("토큰 분석", other.system_prompt.read_text(encoding="utf-8"))

    def test_claude_pipeline_planner_and_watcher_can_write_their_documents(self) -> None:
        launch = prepare_injection(self.project, "claude", "orchest", build_root=self.root / "build",
            state_root=self.root / "state", source_codex_home=self.source_codex_home)
        for name in ("watcher", "planner"):
            text = (launch.bundle_root / f"plugin/agents/{name}.md").read_text(encoding="utf-8")
            self.assertIn("tools: Read, Grep, Glob, Bash, Write\n", text)
        # 하위 에이전트 종료 시 쓰기 예약을 정리하는 훅이 실제 번들에 설치된다.
        hooks = json.loads((launch.bundle_root / "plugin/hooks/hooks.json").read_text(encoding="utf-8"))["hooks"]
        stop = [hook["command"] for entry in hooks["SubagentStop"] for hook in entry["hooks"]]
        self.assertEqual(len(stop), 1)
        self.assertTrue(stop[0].endswith("managed_policy_guard.py subagent-stop claude"), stop)
        # 기존 세션이 쓰는 adapter 원본의 도구 목록은 바꾸지 않는다.
        rendered = render_project(load_project("user-ui"))
        self.assertIn("tools: Read, Grep, Glob, Bash\n", rendered[".claude/agents/watcher.md"].decode())
    def test_orchest_parent_prompt_mandates_the_pipeline_and_children_know_their_documents(self) -> None:
        # 부모 프롬프트가 "기본 역할을 구현한다"고만 해서 부모가 하위 에이전트 없이 전부 구현했다.
        for host in ("codex", "claude", "opencode"):
            with self.subTest(host=host):
                launch = prepare_injection(self.project, host, "orchest", build_root=self.root / "build",
                    state_root=self.root / "state", source_codex_home=self.source_codex_home)
                prompt = launch.system_prompt.read_text(encoding="utf-8")
                for expected in ("## 파이프라인 계약 (필수)", "source를 직접 수정하지 않고 아래 순서대로 하위 에이전트를 호출한다",
                                 "부모는 source를 직접 수정하지 않는다", "git_operations.py verdict --result PASS|FAIL",
                                 "`직접 수정 승인`", "작은 수정이라도 하위 에이전트 호출을 생략하지 않는다",
                                 "`plan.md`를 작성하게 한다", "`exploration.md`를 작성한다", "`implementation-log.md`", "`review-log.md`",
                                 "`final-summary.md`"):
                    self.assertIn(expected, prompt)
                # 계획 뒤에 만든 작업 worktree 안에서 근거를 읽도록 순서를 명시한다.
                for expected in ("**Planner(1차)**", "**Planner(2차)**", "그 worktree 안에서 읽은 것만 인정된다"):
                    self.assertIn(expected, prompt)
                _, runtime, texts = self.child_definitions(host)
                self.assertIn("**2차(상세 탐색)**는 작업 worktree가 만들어진 뒤다", texts["planner"])
                self.assertIn("`exploration.md`는 탐색을 마친 뒤 한 번에 작성한다", texts["planner"])
                for name in CHILDREN:
                    self.assertIn("작업 worktree로 옮긴 뒤 읽는다", texts[name])
                    self.assertIn("`cd <worktree 절대 경로>`를 단독 명령으로 실행한다", texts[name])
                for name in ("publisher", "generator", "refactorer"):
                    self.assertIn("`implementation-log.md`에 변경 경로", texts[name])
                self.assertIn(f"python3 -I {runtime}/git_operations.py verdict --result PASS|FAIL --start", texts["watcher"])
                self.assertIn("구현 에이전트가 보고한 결과를 그대로 믿지 않는다", texts["watcher"])
                logic = prepare_injection(self.project, host, "logic", build_root=self.root / "build",
                    state_root=self.root / "state", source_codex_home=self.source_codex_home)
                self.assertNotIn("## 파이프라인 계약", logic.system_prompt.read_text(encoding="utf-8"))

    def test_orchest_contract_keeps_child_calls_from_being_blocked_or_repeated(self) -> None:
        # 실제 orchest 세션의 비용 분석: 근거 부족·셸 rm으로 차단된 하위 호출, 계획을 다시 풀어 쓴 지시,
        # 큰 컨텍스트 재개, 문서를 여러 번 고쳐 쓴 Planner 2차, 전체 검증을 반복한 Watcher가 비용의 대부분이었다.
        for host in ("codex", "claude", "opencode"):
            with self.subTest(host=host):
                launch = prepare_injection(self.project, host, "orchest", build_root=self.root / "build",
                    state_root=self.root / "state", source_codex_home=self.source_codex_home)
                prompt = launch.system_prompt.read_text(encoding="utf-8")
                for expected in ("### 하위 에이전트 호출 비용", "부모가 그 worktree에서 근거를 먼저 기록한다",
                                 "`git rm -- <경로>`", "절 번호로 가리킨다", "새 하위 에이전트를 호출한다",
                                 "검증 결과와 그때의 지문을 Watcher에 전달한다", "새 하위 에이전트를 호출하지 않는다"):
                    self.assertIn(expected, prompt)
                policy, _, texts = self.child_definitions(host)
                contract = (policy / ".agent-policy/common/skills/policy/task-role-routing/references/orchestration.md").read_text(encoding="utf-8")
                self.assertIn("### 하위 에이전트 호출 비용", contract)
                for name in CHILDREN:
                    self.assertIn("파일 삭제는 요청으로 반환한다", texts[name])
                    self.assertIn("문서에 적은 내용은 경로와 절로 가리키고 다시 풀어 쓰지 않는다", texts[name])
                self.assertIn("삭제 항목은 부모의 Git 작업(`git rm`)으로 계획한다", texts["planner"])
                self.assertIn("`exploration.md`는 탐색을 마친 뒤 한 번에 작성한다", texts["planner"])
                self.assertIn("부모가 전달한 검증 결과의 지문이 시작 지문과 같으면", texts["watcher"])
                self.assertIn("구현 에이전트가 보고한 결과를 그대로 믿지 않는다", texts["watcher"])


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
        self.env.update(ASAN_AGENT_POLICY_STATE_ROOT=str(self.state), ASAN_AGENT_POLICY_ROLE="orchest",
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
        (plan.parent / "exploration.md").write_text("탐색 결과\n")
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

    GENERATOR = {"agent_id": "agent-g", "agent_type": "asan-agent-policy:generator"}
    WATCHER = {"agent_id": "agent-w", "agent_type": "asan-agent-policy:watcher"}

    def edit(self, tree: Path, **who):
        # 통합 구현 세션의 구현은 하위 에이전트가 한다. 기본값은 Generator의 호출이다.
        return self.tool("pre-tool", "Edit", {"file_path": str(tree / "src/app.ts"), "old_string": "1", "new_string": "2"},
                         cwd=tree, **(who or self.GENERATOR))

    def session_documents(self, *names: str) -> Path:
        directory = self.root / ".claude/logs/sessions/current"
        directory.mkdir(parents=True, exist_ok=True)
        for name in names:
            (directory / name).write_text(self.PLAN.format(goal="세션 작업") if name == "plan.md" else f"{name} 내용\n")
        return directory

    def ready(self, tree: Path | None = None) -> None:
        self.session_documents("plan.md", "exploration.md")
        for tool, args in (("Skill", {"skill": "policy"}), ("Read", {"file_path": str((tree or self.root) / "src/app.ts")})):
            self.tool("post-tool", tool, args, cwd=tree, tool_response={"success": True})
        self.event("user-prompt", prompt="진행")

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

    def test_evidence_must_be_read_inside_the_task_worktree_created_after_planning(self) -> None:
        # 기본 checkout에서 계획한 뒤 새 worktree를 만들고 그곳의 구현을 Generator에 맡기자,
        # 스킬 근거가 기본 checkout에만 쌓여 "관련 SKILL.md 확인"으로 7번 차단됐다.
        # 1차 계획: 기본 checkout에서 가볍게 조사하고 계획을 승인받는다.
        self.tool("post-tool", "Skill", {"skill": "policy"}, tool_response={"success": True})
        self.tool("post-tool", "Read", {"file_path": str(self.root / "src/app.ts")}, tool_response={"success": True})
        tree = self.branch("A1")
        (tree / "src").mkdir(exist_ok=True)
        (tree / "src/app.ts").write_text("export const value = 1;\n")
        plan = self.root / ".claude/logs/sessions/current/tasks/A/plan.md"
        plan.parent.mkdir(parents=True, exist_ok=True)
        plan.write_text(self.PLAN.format(goal="구현"))
        (plan.parent / "exploration.md").write_text("탐색 결과\n")
        self.runner("board-set", "--task", "A", "--title", "A", "--stage", "working", "--branch", "A1", "--plan", str(plan))
        self.event("user-prompt", prompt="A 진행")
        skill = tree / ".agent-policy/common/skills/policy/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("정책 색인\n")
        # 기본 checkout에서 읽은 근거는 새 worktree의 근거가 아니다. 어디서 읽어야 하는지 알려 준다.
        denied = self.edit(tree).stderr
        self.assertIn("관련 SKILL.md 확인", denied)
        self.assertIn(f"`cd {tree}`", denied)
        self.assertIn("이어 쓴 명령은 근거로 인정하지 않습니다", denied)
        # 작업 위치를 옮기지 않고 한 줄로 이어 쓴 읽기는 인정하지 않는다.
        self.tool("post-tool", "Bash", {"command": f"cd {tree} && cat {skill}"}, tool_response={"exit_code": 0})
        self.assertIn("관련 SKILL.md 확인", self.edit(tree).stderr)
        # 2차 탐색: 작업 worktree로 위치를 옮긴 뒤 스킬과 코드를 읽으면 그 worktree의 근거가 된다.
        self.tool("post-tool", "Read", {"file_path": str(skill)}, cwd=tree, tool_response={"success": True})
        self.assertIn("역할별 재사용 자산·인접 구현 탐색", self.edit(tree).stderr)
        self.tool("post-tool", "Read", {"file_path": str(tree / "src/app.ts")}, cwd=tree, tool_response={"success": True})
        self.assertEqual(self.edit(tree).returncode, 0, self.edit(tree).stderr)

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
        self.session_documents("plan.md", "exploration.md")
        for tool, args in (("Skill", {"skill": "policy"}), ("Read", {"file_path": str(self.root / "src/app.ts")})):
            self.tool("post-tool", tool, args, tool_response={"success": True})
        self.assertIn("사용자 구현 승인", self.edit(self.root).stderr)
        self.event("user-prompt", prompt="진행")
        self.assertEqual(self.edit(self.root).returncode, 0, self.edit(self.root).stderr)

    def test_parent_cannot_implement_and_only_implementer_children_change_source(self) -> None:
        # 실제 generate 세션에서 부모가 하위 에이전트를 한 번도 호출하지 않고 22개 파일을 직접 구현했다.
        self.ready()
        parent = self.tool("pre-tool", "Edit", {"file_path": str(self.root / "src/app.ts"), "old_string": "1", "new_string": "2"})
        self.assertEqual(parent.returncode, 2)
        self.assertIn("부모는 source를 직접 수정하지 않습니다", parent.stderr)
        self.assertIn("직접 수정 승인", parent.stderr)
        self.assertEqual(self.edit(self.root).returncode, 0, self.edit(self.root).stderr)
        for kind in ("planner", "watcher"):
            denied = self.edit(self.root, agent_id="agent-x", agent_type=f"asan-agent-policy:{kind}")
            self.assertIn("하위 에이전트는 source를 수정하지 않습니다", denied.stderr)
        # 부모와 Planner·Watcher도 자기 산출물은 쓴다.
        artifact = self.tool("pre-tool", "Write", {"file_path": str(self.root / ".claude/logs/sessions/current/review-log.md"),
                                                   "content": "PASS"}, **self.WATCHER)
        self.assertEqual(artifact.returncode, 0, artifact.stderr)

    def test_direct_edit_exception_lasts_until_the_next_user_input(self) -> None:
        self.ready()
        parent = lambda: self.tool("pre-tool", "Edit", {"file_path": str(self.root / "src/app.ts"), "old_string": "1", "new_string": "2"})
        self.assertEqual(parent().returncode, 2)
        self.assertIn("다음 사용자 입력에서 다시 막힙니다", self.event("user-prompt", prompt="직접 수정 승인").stdout)
        self.assertEqual(parent().returncode, 0, parent().stderr)
        self.assertEqual(parent().returncode, 0, "같은 응답 안에서는 여러 번 수정할 수 있습니다.")
        self.event("user-prompt", prompt="이제 다음 작업 해줘")
        self.assertIn("부모는 source를 직접 수정하지 않습니다", parent().stderr)

    def test_source_change_needs_planner_documents(self) -> None:
        directory = self.session_documents("plan.md")
        for tool, args in (("Skill", {"skill": "policy"}), ("Read", {"file_path": str(self.root / "src/app.ts")})):
            self.tool("post-tool", tool, args, tool_response={"success": True})
        self.event("user-prompt", prompt="진행")
        self.assertIn("Planner의 문서가 필요합니다: exploration.md", self.edit(self.root).stderr)
        (directory / "exploration.md").write_text("  \n")
        self.assertIn("exploration.md", self.edit(self.root).stderr, "빈 문서는 작성한 것으로 보지 않습니다.")
        (directory / "exploration.md").write_text("탐색 결과\n")
        self.assertEqual(self.edit(self.root).returncode, 0, self.edit(self.root).stderr)

    def test_hosts_that_cannot_identify_children_keep_documents_but_not_the_parent_block(self) -> None:
        directory = self.root / ".codex/logs/sessions/current"
        directory.mkdir(parents=True)
        (directory / "plan.md").write_text(self.PLAN.format(goal="세션 작업"))
        env = dict(self.env, ASAN_SESSION_DIR=".codex/logs/sessions/current")
        def codex(mode, name, data, **extra):
            self.calls += 1
            event = {"cwd": str(self.root), "session_id": "codex-test", "tool_call_id": str(self.calls),
                     "tool_name": name, "tool_input": data, **extra}
            return subprocess.run([sys.executable, "-I", str(self.runtime / "managed_policy_guard.py"), mode, "codex"],
                input=json.dumps(event), cwd=self.root, env=env, text=True, capture_output=True)
        for tool, args in (("Skill", {"skill": "policy"}), ("Read", {"file_path": str(self.root / "src/app.ts")})):
            codex("post-tool", tool, args, tool_response={"success": True})
        codex("user-prompt", "Bash", {}, prompt="Proceed")
        change = {"file_path": str(self.root / "src/app.ts"), "old_string": "1", "new_string": "2"}
        self.assertIn("exploration.md", codex("pre-tool", "Edit", change).stdout)
        (directory / "exploration.md").write_text("탐색 결과\n")
        allowed = codex("pre-tool", "Edit", change)
        self.assertNotIn('"deny"', allowed.stdout, "Codex는 부모와 하위 에이전트를 구분할 수 없어 부모 차단을 적용하지 않습니다.")

    def test_other_roles_are_not_pipeline_sessions(self) -> None:
        self.env["ASAN_AGENT_POLICY_ROLE"] = "logic"
        self.session_documents("plan.md")
        for tool, args in (("Skill", {"skill": "policy"}), ("Read", {"file_path": str(self.root / "src/app.ts")})):
            self.tool("post-tool", tool, args, tool_response={"success": True})
        self.event("user-prompt", prompt="진행")
        parent = self.tool("pre-tool", "Edit", {"file_path": str(self.root / "src/app.ts"), "old_string": "1", "new_string": "2"})
        self.assertEqual(parent.returncode, 0, parent.stderr)
        commit = self.event("pre-tool", "git commit -am work")
        self.assertIn("보호 실행", commit.stderr)
        # 하위 에이전트의 Git 제한과 현황판 안내도 오케스트레이션 세션에만 적용한다.
        child = self.event("pre-tool", "git commit -am work", agent_id="agent-1", agent_type="generator")
        self.assertIn("보호 실행", child.stderr)
        self.runner("board-set", "--task", "A", "--title", "A", "--stage", "planning", "--scope", "src")
        self.runner("board-set", "--task", "B", "--title", "B", "--stage", "planning", "--scope", "src", "--wait-for", "A")
        self.assertNotIn("[WORK_BOARD]", self.event("session-start").stdout)
        # 현황판·지문·판정 명령과 작업별 산출물 폴더도 오케스트레이션 세션 전용이다.
        runner = f"python3 -I {self.runtime / 'git_operations.py'}"
        for action in ("board", "fingerprint", "board-set --task A --stage planning"):
            self.assertIn("오케스트레이션(orchest) 세션 전용 명령입니다", self.event("pre-tool", f"{runner} {action}").stderr)
        self.assertEqual(self.event("pre-tool", f"{runner} graph").returncode, 0)
        nested = self.tool("pre-tool", "Write", {"file_path": str(self.root / ".claude/logs/sessions/current/tasks/A/plan.md"), "content": "x"})
        self.assertIn("unknown/", nested.stderr)

    def test_commit_needs_a_watcher_pass_for_exactly_the_reviewed_content(self) -> None:
        directory = self.session_documents("plan.md", "exploration.md")
        runner = f"python3 -I {self.runtime / 'git_operations.py'}"
        (self.root / "src/app.ts").write_text("export const value = 2;\n")
        commit = lambda: self.event("pre-tool", "git commit -am work").stderr
        self.assertIn("Watcher의 PASS 판정이 필요합니다", commit())
        start = self.runner("fingerprint")["fingerprint"]
        verdict = lambda result, who: self.event("pre-tool", f"{runner} verdict --result {result} --start {start}", **who)
        self.assertIn("Watcher 하위 에이전트만 기록합니다", verdict("PASS", {}).stderr)
        self.assertIn("Watcher 하위 에이전트만 기록합니다", verdict("PASS", self.GENERATOR).stderr)
        self.assertIn("implementation-log.md, review-log.md", verdict("PASS", self.WATCHER).stderr)
        self.session_documents("implementation-log.md", "review-log.md")
        self.assertEqual(verdict("FAIL", self.WATCHER).returncode, 0)
        self.runner("verdict", "--result", "FAIL", "--start", start)
        self.assertIn("마지막 판정은 FAIL입니다", commit())
        self.assertEqual(self.runner("verdict", "--result", "PASS", "--start", start)["verdict"]["result"], "PASS")
        self.assertIn("보호 실행", commit())
        # stage는 검토한 내용을 바꾸지 않는다. 세션 문서를 더 써도 마찬가지다.
        self.git("add", "--", "src/app.ts")
        (directory / "final-summary.md").write_text("요약\n")
        self.assertIn("보호 실행", commit())
        # 검토 뒤의 수정·포맷은 다시 검토받아야 한다.
        (self.root / "src/app.ts").write_text("export const value = 3;\n")
        self.assertIn("Watcher가 검토한 뒤 내용이 바뀌었습니다", commit())
        self.assertIn("검토 시작 지문과 현재 지문이 다릅니다", self.runner("verdict", "--result", "PASS", "--start", start, ok=False))
        # 세션 기록만 커밋할 때는 검토할 source가 없다.
        self.git("checkout", "-q", "HEAD", "--", "src/app.ts")
        self.assertNotIn("Watcher", self.event("pre-tool", "git commit -m logs -- .claude").stderr)

    def test_merge_preparation_needs_the_final_summary(self) -> None:
        self.branch("A1")
        self.session_documents("plan.md")
        reviews = self.repository / "branch-relations/v1/reviews"
        reviews.mkdir(parents=True)
        (reviews / ("a" * 32 + ".json")).write_text(json.dumps({"id": "a" * 32, "source": "A1", "target": "sy-main"}))
        runner = f"python3 -I {self.runtime / 'git_operations.py'}"
        complete = lambda: self.event("pre-tool", f"{runner} complete --review {'a' * 32} --report-json {{}}")
        self.assertIn("작업 결과 문서가 필요합니다: final-summary.md", complete().stderr)
        self.session_documents("final-summary.md")
        self.assertEqual(complete().returncode, 0, complete().stderr)

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
            input=json.dumps({"cwd": str(tree), "session_id": "claude-new", "tool_use_id": str(self.calls), "tool_name": "Edit", **self.GENERATOR,
                              "tool_input": {"file_path": str(tree / "src/app.ts"), "old_string": "1", "new_string": "2"}}),
            cwd=self.root, env=self.env, text=True, capture_output=True)
        self.assertIn("작업 A의 계획 승인", fresh.stderr)

    def test_git_check_ignore_is_a_read_only_query(self) -> None:
        # 실제 orchest 세션에서 Watcher의 `git check-ignore` 조회가 Git 변경으로 분류되어 차단됐다.
        command = f"git -C {self.root} check-ignore -v dist node_modules/.tmp"
        child = self.event("pre-tool", command, **self.WATCHER)
        self.assertEqual(child.returncode, 0, child.stderr)
        self.assertEqual(self.event("pre-tool", command).returncode, 0)

    def test_reservation_of_a_call_missing_from_the_finished_child_transcript_is_released(self) -> None:
        # 실제 orchest 세션: Watcher의 병렬 호출 하나가 PreToolUse에서 쓰기 예약만 남기고 대화 기록에도,
        # PostToolUse에도 나타나지 않았다. 그 예약이 commit 실행을 막았다.
        self.ready()
        writes = lambda: {item["call"]: item for item in self.runner("writes")["writes"]}
        self.assertEqual(self.event("pre-tool", "npx tsc -b", **self.WATCHER).returncode, 0)
        orphan = str(self.calls)
        self.assertEqual(self.event("pre-tool", "npm run test", **self.WATCHER).returncode, 0)
        unfinished = str(self.calls)
        self.assertEqual(writes()[orphan]["agent"], "agent-w")
        transcript = self.base / "subagents/agent-agent-w.jsonl"
        transcript.parent.mkdir()
        transcript.write_text(json.dumps({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "id": unfinished, "name": "Bash", "input": {"command": "npm run test"}}]}}) + "\n")
        stop = lambda **extra: self.event("subagent-stop", hook_event_name="SubagentStop", agent_type="asan-agent-policy:watcher",
                                          agent_transcript_path=str(transcript), **extra)
        # 다른 하위 에이전트의 종료나 기록 경로가 없는 종료는 예약을 정리하지 않는다.
        self.assertEqual(stop(agent_id="agent-g").returncode, 0)
        self.assertEqual(set(writes()), {orphan, unfinished})
        self.assertEqual(self.event("subagent-stop", hook_event_name="SubagentStop", agent_id="agent-w").returncode, 0)
        self.assertEqual(set(writes()), {orphan, unfinished})
        result = stop(agent_id="agent-w")
        self.assertEqual(result.returncode, 0, result.stderr)
        # 기록에 있으나 결과가 확인되지 않은 호출은 실제 종료를 확인해야 하므로 남긴다.
        self.assertEqual(set(writes()), {unfinished})
        receipts = list((self.repository / "branch-relations/v1/write-receipts").glob("*.json"))
        self.assertEqual([json.loads(path.read_text())["outcome"] for path in receipts], ["not-recorded"])
        # Claude 하위 에이전트의 종료 이벤트가 이 정리를 호출한다.
        events = json.loads((Path(__file__).resolve().parents[1] / "adapters/claude/events.json").read_text())
        self.assertEqual([hook["command"] for entry in events["SubagentStop"] for hook in entry["hooks"]], ["subagent-stop"])

    def test_hash_and_byte_queries_do_not_reserve_a_write(self) -> None:
        # 실제 orchest 세션: Publisher의 `shasum …; tail -c 1 … | xxd` 조회가 쓰기로 예약됐고, 그 PostToolUse가
        # 제한 시간을 넘겨 예약이 남았다. 남은 예약이 Stop 자동 포맷과 검증 명령을 막았다.
        self.ready()
        target = self.root / "src/app.ts"
        for command in (f"shasum {target}; tail -c 1 {target} | xxd", f"sha256sum {target}", f"md5 {target}",
                        f"xxd -g 1 {target}", f"od -c {target}", f"cmp {target} {target}", f"stat {target}"):
            with self.subTest(command=command):
                self.assertEqual(self.event("pre-tool", command, **self.WATCHER).returncode, 0)
        self.assertEqual(self.runner("writes")["writes"], [])
        # 출력 파일을 받는 xxd와 조회가 아닌 명령은 그대로 예약한다.
        for command in (f"xxd {target} {self.base / 'dump.txt'}", f"xxd -r {target}", "npx tsc -b"):
            self.assertEqual(self.event("pre-tool", command, **self.WATCHER).returncode, 0)
        self.assertEqual(len(self.runner("writes")["writes"]), 3)

    def test_write_completion_waits_for_the_events_lock_beyond_the_old_limit(self) -> None:
        # 실제 orchest 세션: 부모의 Stop 자동 포맷이 events.lock을 오래 쥐는 동안 하위 에이전트의 PostToolUse가
        # 8초 제한에 걸려 쓰기 완료를 기록하지 못했다.
        import fcntl
        self.ready()
        self.assertEqual(self.event("pre-tool", "npx tsc -b", **self.WATCHER).returncode, 0)
        self.assertEqual(len(self.runner("writes")["writes"]), 1)
        event = {"cwd": str(self.root), "session_id": "claude-test", "tool_use_id": str(self.calls), "tool_name": "Bash",
                 "tool_input": {"command": "npx tsc -b"}, "hook_event_name": "PostToolUse",
                 "tool_response": {"success": True}, **self.WATCHER}
        with open(self.repository / "events.lock", "a+") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            process = subprocess.Popen([sys.executable, "-I", str(self.runtime / "managed_policy_guard.py"), "post-tool", "claude"],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.root, env=self.env, text=True)
            process.stdin.write(json.dumps(event))
            process.stdin.close()
            time.sleep(9)
            fcntl.flock(lock, fcntl.LOCK_UN)
        stderr = process.stderr.read()
        self.assertEqual(process.wait(timeout=30), 0, stderr)
        self.assertEqual(self.runner("writes")["writes"], [])
        # host가 내부 제한보다 먼저 hook을 끝내지 않는다.
        adapters = Path(__file__).resolve().parents[1] / "adapters"
        claude = json.loads((adapters / "claude/events.json").read_text())
        codex = json.loads((adapters / "codex/events.json").read_text())
        for events, names in ((claude, ("PostToolUse", "PostToolUseFailure")), (codex, ("PostToolUse",))):
            for name in names:
                self.assertEqual([hook["timeout"] for entry in events[name] for hook in entry["hooks"]], [30])
        self.assertIn('mode === "post-tool" ? 30000', (adapters / "opencode/files/.opencode/plugins/agent-policy.js").read_text())

    def test_reservation_of_a_finished_child_call_with_a_result_is_released_as_unconfirmed(self) -> None:
        # 실제 orchest 세션: 하위 에이전트의 호출은 결과까지 기록됐지만 PostToolUse가 제한 시간을 넘겨
        # 쓰기 예약이 남았다. 하위 에이전트가 끝난 뒤에도 그 예약이 부모의 포맷·검증을 막았다.
        self.env["ASAN_FORMATTER"] = "prettier-v1"
        tree, _ = self.task("A")
        self.event("user-prompt", prompt="A 진행")
        self.assertEqual(self.edit(tree).returncode, 0)
        edited = str(self.calls)
        (tree / "src/app.ts").write_text("export const value = 2;\n")
        self.assertEqual(self.event("pre-tool", "npx tsc -b", **self.GENERATOR).returncode, 0)
        built = str(self.calls)
        self.assertEqual(self.event("pre-tool", "npm run test", **self.GENERATOR).returncode, 0)
        unfinished = str(self.calls)
        # Edit은 작업 worktree, 명령은 저장소 worktree의 예약이다.
        writes = lambda: {json.loads(path.read_text())["call"] for path in (self.repository / "branch-relations/v1/writes").glob("*.json")}
        self.assertEqual(writes(), {edited, built, unfinished})
        transcript = self.base / "subagents/agent-agent-g.jsonl"
        transcript.parent.mkdir()
        rows = [{"type": "assistant", "message": {"content": [{"type": "tool_use", "id": call, "name": "Bash", "input": {}}]}}
                for call in (edited, built, unfinished)]
        rows += [{"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": call, "content": "ok"}]}}
                 for call in (edited, built)]
        transcript.write_text("".join(json.dumps(row) + "\n" for row in rows))
        result = self.event("subagent-stop", hook_event_name="SubagentStop", agent_transcript_path=str(transcript), **self.GENERATOR)
        self.assertEqual(result.returncode, 0, result.stderr)
        # 결과가 없는 호출은 실제 종료를 확인해야 하므로 남긴다.
        self.assertEqual(writes(), {unfinished})
        receipts = [json.loads(path.read_text()) for path in (self.repository / "branch-relations/v1/write-receipts").glob("*.json")]
        self.assertEqual({(item["call"], item["outcome"]) for item in receipts},
                         {(built, "post-tool-missing"), (edited, "post-tool-missing")})
        # 실행 결과를 확인하지 못했으므로 바뀐 파일은 성공한 쓰기가 아니라 결과 미확인으로 남긴다.
        records = [json.loads(path.read_text()) for path in self.repository.rglob("formatting.json")]
        statuses = {name: item["status"] for record in records for name, item in record.get("files", {}).items()}
        self.assertEqual(statuses, {str(tree / "src/app.ts"): "unconfirmed"})

    def test_child_stop_does_not_release_reservations_outside_orchestration(self) -> None:
        self.env["ASAN_AGENT_POLICY_ROLE"] = "logic"
        self.ready()
        self.event("pre-tool", "npx tsc -b", agent_id="agent-w", agent_type="watcher")
        transcript = self.base / "subagents/agent-agent-w.jsonl"
        transcript.parent.mkdir()
        transcript.write_text("")
        result = self.event("subagent-stop", hook_event_name="SubagentStop", agent_id="agent-w",
                            agent_transcript_path=str(transcript))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(self.runner("writes")["writes"]), 1)

    def token_review(self, identifier: str, cleanup: bool) -> None:
        reviews = self.repository / "branch-relations/v1/reviews"
        reviews.mkdir(parents=True, exist_ok=True)
        (reviews / f"{identifier}.json").write_text(json.dumps({"id": identifier, "source": "A1", "target": "sy-main",
                                                                "cleanup": cleanup}))

    def test_token_analysis_request_puts_the_report_between_merge_and_cleanup(self) -> None:
        runner = f"python3 -I {self.runtime / 'git_operations.py'}"
        directory = self.session_documents("plan.md", "final-summary.md")
        cleanup = lambda: self.event("pre-tool", f"{runner} cleanup --source A1 --target sy-main").stderr
        merged_with_cleanup, merge_only = "c" * 32, "d" * 32
        self.token_review(merged_with_cleanup, True)
        self.token_review(merge_only, False)
        complete = lambda review: self.event("pre-tool", f"{runner} complete --review {review} --report-json '{{}}'").stderr
        # 요청이 없으면 기존 흐름(병합과 정리를 한 번에)을 그대로 쓴다.
        self.assertNotIn("토큰 분석", complete(merged_with_cleanup) + cleanup())
        notice = self.event("user-prompt", prompt="토큰 분석").stdout
        self.assertIn("토큰 분석을 요청했습니다", notice)
        self.assertIn("policy/token-usage/SKILL.md", notice)
        # 병합과 정리를 함께 하는 완료는 막고, 병합만 하는 완료는 보고서 없이 진행한다.
        self.assertIn("병합과 branch·worktree 정리를 나누어 실행합니다", complete(merged_with_cleanup))
        self.assertNotIn("토큰 분석", complete(merge_only))
        # 요청은 다른 사용자 입력이 와도 유지된다.
        self.event("user-prompt", prompt="병합 진행")
        self.assertIn("정리 전에 보고서가 필요합니다", cleanup())
        report = directory / "unknown/token-usage-report.md"
        report.parent.mkdir(parents=True)
        report.write_text("# 토큰 사용량 보고\n")
        merged_at = int(self.git("log", "-1", "--format=%ct", "sy-main"))
        os.utime(report, (merged_at - 60, merged_at - 60))
        self.assertIn("마지막 commit보다 먼저 작성됐습니다", cleanup())
        os.utime(report, (merged_at + 60, merged_at + 60))
        self.assertNotIn("토큰 분석", cleanup())
        report.unlink()
        self.assertIn("토큰 분석 요청을 취소했습니다", self.event("user-prompt", prompt="토큰 분석 취소").stdout)
        self.assertNotIn("토큰 분석", complete(merged_with_cleanup) + cleanup())

    def test_token_analysis_request_is_ignored_outside_orchestration(self) -> None:
        self.env["ASAN_AGENT_POLICY_ROLE"] = "logic"
        runner = f"python3 -I {self.runtime / 'git_operations.py'}"
        self.token_review("e" * 32, True)
        self.assertNotIn("토큰 분석", self.event("user-prompt", prompt="토큰 분석").stdout)
        self.assertNotIn("토큰 분석", self.event("pre-tool", f"{runner} complete --review {'e' * 32} --report-json '{{}}'").stderr)
        self.assertNotIn("토큰 분석", self.event("pre-tool", f"{runner} cleanup --source A1 --target sy-main").stderr)

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
