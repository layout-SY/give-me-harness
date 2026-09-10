from __future__ import annotations

import json
import sys
import tomllib
import unittest
import tempfile
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from agent_policy.core import (
    CENTRAL_ROOT,
    EXPECTED_REQUIRED_ARTIFACTS,
    audit_source_contract,
    load_project,
    render_project,
    source_digest,
)


class RenderingTests(unittest.TestCase):
    def test_reference_overlay_changes_digest_but_logs_do_not(self) -> None:
        import agent_policy.core as core
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            projects = root / "projects"
            reference = projects / "overlay/admin-ui/skills/reference/catalog.md"
            reference.parent.mkdir(parents=True)
            reference.write_text("original catalog\n")
            (projects / "admin-ui.json").write_text("{}")
            project = load_project("admin-ui")
            with patch.object(core, "CENTRAL_ROOT", root), patch.object(core, "PROJECTS_ROOT", projects):
                original = source_digest(project)
                reference.write_text("updated catalog\n")
                changed = source_digest(project)
                self.assertNotEqual(original, changed)
                log = root / "logs/projects/admin-ui/codex/sessions/test/plan.md"
                log.parent.mkdir(parents=True)
                log.write_text("session log\n")
                self.assertEqual(changed, source_digest(project))

    def test_project_metadata_is_rendered_without_cross_project_name(self) -> None:
        user = render_project(load_project("user-ui"))
        admin = render_project(load_project("admin-ui"))
        self.assertIn(b"asan-metaverse-user-ui", user["AGENTS.md"])
        self.assertNotIn(b"asan-metaverse-admin-ui", user["AGENTS.md"])
        self.assertIn(b"asan-metaverse-admin-ui", admin["AGENTS.md"])
        self.assertNotIn(b"asan-metaverse-user-ui", admin["AGENTS.md"])
        self.assertEqual(user["AGENTS.md"], user[".agent-policy/common/AGENT_POLICY.md"])

    def test_managed_outputs_have_no_legacy_central_reference_or_placeholder(self) -> None:
        for project_id in ("user-ui", "admin-ui"):
            with self.subTest(project=project_id):
                for path, content in render_project(load_project(project_id)).items():
                    self.assertNotIn(b"bin/sync.py deploy --target", content, path)
                    self.assertNotIn(
                        "이 프로젝트에서 직접 수정하지 마세요.\n     원본: source/hosts/".encode(),
                        content,
                        path,
                    )
                    self.assertNotIn(b"{{PROJECT_NAME}}", content, path)
                    self.assertNotIn(b"{{CENTRAL_ROOT}}", content, path)
                    self.assertNotIn(b"{{BASE_BRANCH}}", content, path)
                    self.assertNotIn(b"{{DEV_COMMAND}}", content, path)
                    self.assertNotIn(b"{{BUILD_COMMAND}}", content, path)
                    self.assertNotIn(b"{{PREVIEW_COMMAND}}", content, path)

    def test_runtime_cache_files_are_never_rendered_or_digested(self) -> None:
        rendered = render_project(load_project("user-ui"))
        self.assertFalse(any("__pycache__" in path for path in rendered))
        self.assertFalse(any(path.endswith((".pyc", ".pyo")) for path in rendered))

    def test_project_specific_reference_catalogs_are_conditional(self) -> None:
        rendered = render_project(load_project("user-ui"))
        self.assertNotIn(
            ".agents/skills/reference/components/COMMON_COMPONENTS.md",
            rendered,
        )
        hooks = rendered[".agent-policy/common/skills/reference/custom-hooks/SKILL.md"]
        self.assertIn(b"useApi", hooks)
        self.assertIn(b"meeting", hooks)
        self.assertIn("실제 경로와 사용처가 확인될 때만".encode(), hooks)
        self.assertIn("모든 소비자 프로젝트에 존재한다고 단정하지 않습니다".encode(), hooks)
        api_authoring = rendered[".agent-policy/common/skills/recipe/api-authoring/SKILL.md"]
        self.assertIn(b"useApi", api_authoring)
        self.assertIn("기존 범용 요청 hook".encode(), api_authoring)

    def test_claude_documentation_uses_claude_artifact_root(self) -> None:
        rendered = render_project(load_project("user-ui"))
        claude = rendered["CLAUDE.md"]
        documentation = rendered[
            ".agent-policy/common/skills/policy/documentation/SKILL.md"
        ]
        self.assertIn(b".claude/logs/sessions/", claude)
        self.assertIn(b".claude/logs/sessions/", documentation)
        for artifact in EXPECTED_REQUIRED_ARTIFACTS:
            self.assertIn(artifact.encode(), documentation)

    def test_entry_docs_do_not_identify_the_central_prompt_repository(self) -> None:
        central_root = str(CENTRAL_ROOT).encode()
        for project_id in ("user-ui", "admin-ui"):
            with self.subTest(project=project_id):
                rendered = render_project(load_project(project_id))
                agents = rendered["AGENTS.md"]
                claude = rendered["CLAUDE.md"]
                self.assertNotIn("중앙 시스템 프롬프트".encode(), agents)
                self.assertNotIn("중앙 시스템 프롬프트".encode(), claude)
                self.assertNotIn(central_root, agents)
                self.assertNotIn(central_root, claude)
                self.assertIn("## 4. 관리 정책 파일".encode(), claude)
                self.assertIn(b".agent-policy/common/AGENT_POLICY.md", claude)
                self.assertNotIn(b"AGENTS.md", claude)

    def test_codex_and_claude_hook_schemas_are_json_and_include_guard(self) -> None:
        rendered = render_project(load_project("user-ui"))
        codex = json.loads(rendered[".codex/hooks.json"])["hooks"]
        claude = json.loads(rendered[".claude/settings.json"])["hooks"]
        self.assertIn("SessionStart", codex)
        self.assertIn("UserPromptSubmit", codex)
        self.assertIn("PreToolUse", codex)
        self.assertIn("PostToolUse", codex)
        self.assertIn("Stop", codex)
        self.assertIn("SessionStart", claude)
        self.assertIn("UserPromptSubmit", claude)
        self.assertIn("PreToolUse", claude)
        self.assertIn("PostToolUse", claude)
        self.assertIn("Stop", claude)
        self.assertIn("managed_policy_guard.py", json.dumps(codex))
        self.assertIn("managed_policy_guard.py", json.dumps(claude))
        self.assertIn("collect-logs --project user-ui --channel codex", json.dumps(codex))
        self.assertIn("collect-logs --project user-ui --channel claude", json.dumps(claude))
        self.assertNotIn("documentation-stop", json.dumps(codex))
        self.assertNotIn("documentation-stop", json.dumps(claude))
        central_prompt_hook = next(
            item
            for item in codex["UserPromptSubmit"]
            if "user-prompt codex" in item["hooks"][0]["command"]
        )
        self.assertEqual(central_prompt_hook["hooks"][0]["timeout"], 10)

    def test_render_is_deterministic(self) -> None:
        project = load_project("user-ui")
        self.assertEqual(render_project(project), render_project(project))

    def test_codex_legacy_hooks_are_removed_in_favor_of_common_guard(self) -> None:
        rendered = render_project(load_project("user-ui"))
        hooks = json.loads(rendered[".codex/hooks.json"])["hooks"]
        post_commands = [
            hook["command"]
            for registration in hooks["PostToolUse"]
            for hook in registration["hooks"]
        ]
        self.assertTrue(all("managed_policy_guard.py" in command for command in post_commands))
        self.assertTrue(any("post-tool codex" in command for command in post_commands))
        self.assertFalse(any(path.startswith(".codex/hooks/") for path in rendered))
        self.assertNotIn(b"HOOK_SHA256", b"\n".join(rendered.values()))
        self.assertIn(b"hooks = true", rendered[".codex/config.toml"])
        self.assertNotIn(b"codex_hooks", rendered[".codex/config.toml"])

    def test_opencode_plugin_contract_is_rendered(self) -> None:
        rendered = render_project(load_project("user-ui"))
        plugin = rendered[".opencode/plugins/agent-policy.js"].decode()
        self.assertIn('"tool.execute.before"', plugin)
        self.assertIn('"tool.execute.after"', plugin)
        self.assertIn('"chat.message"', plugin)
        self.assertIn("output.args", plugin)
        self.assertIn("session_id: sessionId(input)", plugin)
        self.assertIn("session-start", plugin)
        self.assertIn('event.type !== "session.idle"', plugin)
        self.assertNotIn("documentation-stop", plugin)
        self.assertIn('"experimental.session.compacting"', plugin)
        self.assertIn('"branch-context"', plugin)
        self.assertIn('"collect-logs"', plugin)
        self.assertIn('"opencode"', plugin)
        self.assertIn('const PROJECT_ID = "user-ui"', plugin)
        self.assertIn("client.app", plugin)
        self.assertIn("client.tui.showToast", plugin)
        self.assertNotIn("process.stderr.write", plugin)

        config = json.loads(rendered["opencode.json"])
        bash = config["permission"]["bash"]
        self.assertEqual(bash["*"], "allow")
        for command in ("npm run dev", "vite *"):
            self.assertEqual(bash[command], "ask")
        # Git은 공통 guard의 실제 argv 분류/승인을 사용한다. build에는 중복 승인하지 않는다.
        for command in ("git", "git *", "npm run build"):
            self.assertNotIn(command, bash)
        self.assertEqual(bash["vite build"], "allow")

    def test_rendered_role_contract_is_host_neutral(self) -> None:
        rendered = render_project(load_project("user-ui"))
        managed_text = b"\n".join(rendered.values())
        self.assertNotIn(b"Hephaestus", managed_text)
        self.assertNotIn(b"hephasetus", managed_text.lower())
        self.assertNotIn("Logic Session".encode(), managed_text)
        self.assertNotIn("production UI 전담".encode(), managed_text)
        self.assertIn(
            ".agent-policy/common/skills/policy/task-role-routing/SKILL.md".encode(),
            rendered["AGENTS.md"],
        )
        self.assertIn(
            ".agent-policy/common/skills/policy/task-role-routing/references/ui.md".encode(),
            rendered[".claude/agents/publisher.md"],
        )
        planner = rendered[".claude/agents/planner.md"]
        evaluator = rendered[".claude/agents/evaluator.md"]
        self.assertIn("역할을 제안".encode(), planner)
        self.assertIn("모든 산출물은 한국어".encode(), rendered[".codex/agents/planner.toml"])
        self.assertIn("장기".encode(), evaluator)

    def test_codex_agent_toml_uses_supported_schema(self) -> None:
        rendered = render_project(load_project("user-ui"))
        agent_paths = sorted(
            path for path in rendered if path.startswith(".codex/agents/")
        )
        self.assertTrue(agent_paths)
        for path in agent_paths:
            with self.subTest(path=path):
                agent = tomllib.loads(rendered[path].decode("utf-8"))
                self.assertEqual(
                    set(agent),
                    {"name", "description", "developer_instructions"},
                )
                self.assertTrue(agent["developer_instructions"])

    def test_request_clarity_gate_is_rendered_for_every_project(self) -> None:
        for project_id in ("user-ui", "admin-ui"):
            with self.subTest(project=project_id):
                rendered = render_project(load_project(project_id))
                common = rendered[".agent-policy/common/AGENT_POLICY.md"]
                routing = rendered[
                    ".agent-policy/common/skills/policy/task-role-routing/SKILL.md"
                ]

                self.assertEqual(rendered["AGENTS.md"], common)
                self.assertIn("사용자 요청 명확성 게이트".encode(), common)
                self.assertIn("육하원칙".encode(), common)
                self.assertIn(b"can_proceed: false", common)
                self.assertIn("다음 파이프라인 호출은 시작하지 않는다".encode(), routing)
                self.assertIn(b"needs_clarification", routing)
                self.assertIn("사용자 답변이 올 때까지".encode(), routing)

    def test_policy_and_strategy_docs_have_no_fixed_host_role_assignment(self) -> None:
        forbidden = (
            "Logic Session",
            "production UI 전담",
            "Claude UI 구현",
            "UI_COMPLETE",
        )
        roots = (
            CENTRAL_ROOT / "AGENTS.md",
            CENTRAL_ROOT / "CLAUDE.md",
            CENTRAL_ROOT / "README.md",
            CENTRAL_ROOT / "policy/common",
            CENTRAL_ROOT / "adapters",
            CENTRAL_ROOT / "docs",
        )
        files = []
        for root in roots:
            files.extend((root,) if root.is_file() else root.rglob("*.md"))
        for path in files:
            text = path.read_text(encoding="utf-8")
            for phrase in forbidden:
                self.assertNotIn(phrase, text, str(path.relative_to(CENTRAL_ROOT)))

    def test_branch_contract_is_rendered_once_for_every_host(self) -> None:
        rendered = render_project(load_project("user-ui"))
        runtime = rendered[".agent-policy/runtime/branch_guard.py"]
        self.assertIn(b'BASE_BRANCH = "sy-main"', runtime)
        for path in (
            ".codex/hooks/branch_guard.py",
            ".claude/hooks/branch_guard.py",
            ".opencode/plugins/branch_guard.py",
        ):
            self.assertNotIn(path, rendered)
        self.assertIn(
            b"git-branch-strategy",
            rendered["AGENTS.md"],
        )
        self.assertIn(
            b"def proposal(",
            rendered[
                ".agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py"
            ],
        )
        self.assertIn(b"FULL_SHA_PATTERN", runtime)
        self.assertIn(b"ALLOWED_ROLES", runtime)
        self.assertIn(b"def assignment_includes_branch(", runtime)
        strategy = rendered[".agent-policy/common/skills/policy/git-branch-strategy/SKILL.md"]
        # 이전 실행/복구 구현은 보존하지만 새 주입 문서가 V3 권한을
        # 요구하면 안 된다. 실제 V4 허용/차단은 shared Git 통합 검사로 검증한다.
        self.assertIn("모든 host·role·session".encode(), strategy)
        self.assertNotIn(b"proposal-sha256", strategy)
        self.assertNotIn("assignment 권한 root".encode(), strategy)
        self.assertIn(".agent-policy/runtime/shared_git.py", rendered)
        self.assertEqual(json.loads(rendered[".agent-policy/common/contracts/runtime-policy.json"])["version"], 4)
        self.assertIn(
            b'git(root, "worktree", "add"',
            rendered[
                ".agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py"
            ],
        )

    def test_common_templates_are_identical_for_all_hosts(self) -> None:
        rendered = render_project(load_project("user-ui"))
        expected = (*EXPECTED_REQUIRED_ARTIFACTS, "handoff.md")
        for artifact in expected:
            stem = artifact.removesuffix(".md")
            for name in (artifact, f"{stem}.template.md"):
                common = rendered[f".agent-policy/common/templates/{name}"]
                for host in ("codex", "claude", "opencode"):
                    self.assertEqual(rendered[f".{host}/templates/{name}"], common)
        portfolio = rendered[".agent-policy/common/templates/portfolio-log.template.md"]
        for heading in (
            "문제 상황",
            "고민과 선택",
            "적용",
            "사용 기술과 구체적 목적",
            "결과",
            "이력서·포트폴리오 문구",
        ):
            self.assertIn(heading.encode(), portfolio)

    def test_central_source_contract_audit_passes(self) -> None:
        self.assertEqual(audit_source_contract(), ())

    def test_host_adapters_reference_neutral_common_contract(self) -> None:
        rendered = render_project(load_project("user-ui"))
        for path, content in rendered.items():
            if not path.startswith((".claude/", ".codex/agents/", ".opencode/agent/")):
                continue
            self.assertNotIn(b".agents/skills/policy/task-role-routing", content, path)
        self.assertNotIn(b"AGENTS.md", rendered["CLAUDE.md"])
        self.assertIn(
            b".agent-policy/common/AGENT_POLICY.md",
            rendered["CLAUDE.md"],
        )

    def test_project_overlay_renders_only_for_its_own_project(self) -> None:
        admin = render_project(load_project("admin-ui"))
        user = render_project(load_project("user-ui"))
        entry = "skills/reference/components/button/SKILL.md"
        for root in (".agents/", ".agent-policy/common/"):
            self.assertIn(f"{root}{entry}", admin)
            self.assertNotIn(f"{root}{entry}", user)

    def test_project_overlay_is_rendered_with_project_metadata(self) -> None:
        admin = render_project(load_project("admin-ui"))
        overlay_paths = tuple(
            path
            for path in admin
            if path.startswith(".agents/skills/reference/")
            and path.count("/") > 4
        )
        self.assertTrue(overlay_paths)
        for path in overlay_paths:
            content = admin[path]
            self.assertNotIn(b"{{", content, path)
            self.assertNotIn(b"synthoria", content.lower(), path)
            self.assertIn(b"asan-metaverse-admin-ui", content, path)

    def test_project_overlay_never_shadows_the_common_catalog_index(self) -> None:
        common_root = CENTRAL_ROOT / "policy/common/skills"
        overlay_root = CENTRAL_ROOT / "projects/overlay/admin-ui/skills"
        common = {path.relative_to(common_root) for path in common_root.rglob("*.md")}
        overlay = {path.relative_to(overlay_root) for path in overlay_root.rglob("*.md")}
        self.assertEqual(common & overlay, set())

    def test_source_digest_includes_project_metadata(self) -> None:
        self.assertNotEqual(
            source_digest(load_project("user-ui")),
            source_digest(load_project("admin-ui")),
        )
