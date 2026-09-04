from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Final, Iterable

CENTRAL_ROOT: Final = Path(__file__).resolve().parents[2]
CANONICAL_ROOT: Final = Path("/Users/okand/SynologyDrive/asan-agent-policy")
PROJECTS_ROOT: Final = CENTRAL_ROOT / "projects"
MANIFEST_RELATIVE: Final = Path(".agent-policy/manifest.json")
MANAGED_ROOTS: Final = (
    "AGENTS.md",
    "CLAUDE.md",
    ".agent-policy/common/",
    ".agent-policy/runtime/",
    ".agents/skills/",
    ".claude/agents/",
    ".claude/hooks/",
    ".claude/settings.json",
    ".claude/skills/",
    ".claude/templates/",
    ".codex/agents/",
    ".codex/config.toml",
    ".codex/hooks.json",
    ".codex/hooks/",
    ".codex/templates/",
    ".opencode/agent/",
    ".opencode/plugins/",
    ".opencode/templates/",
    "opencode.json",
)
HOST_COMMANDS: Final = {
    "codex": ["codex"],
    "claude": ["claude"],
    "opencode": ["opencode"],
}
EXPECTED_REQUIRED_ARTIFACTS: Final = (
    "plan.md",
    "exploration.md",
    "implementation-log.md",
    "grill-me-review.md",
    "review-log.md",
    "evaluation-log.md",
    "final-summary.md",
    "portfolio-log.md",
)


class PolicyError(RuntimeError):
    """운영자가 해결해야 하는 정책 오류."""


@dataclass(frozen=True)
class ProjectConfig:
    id: str
    name: str
    path: Path
    commands: dict[str, str]
    base_branch: str = "sy-main"
    policy_path: Path | None = None

    @property
    def policy_root(self) -> Path:
        """sync 정책 파일이 배포된 소비자 기본 checkout을 반환한다."""

        return (self.policy_path or self.path).resolve()


@dataclass(frozen=True)
class LegacyTrace:
    path: str
    expected_sha256: str
    actual_sha256: str

    @property
    def matches(self) -> bool:
        return self.expected_sha256 == self.actual_sha256


@dataclass(frozen=True)
class ProjectDiff:
    project: ProjectConfig
    added: tuple[str, ...]
    changed: tuple[str, ...]
    stale: tuple[str, ...]
    legacy: tuple[LegacyTrace, ...]
    manifest_issues: tuple[str, ...]

    @property
    def current(self) -> bool:
        return not (
            self.added
            or self.changed
            or self.stale
            or self.legacy
            or self.manifest_issues
        )


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError) as error:
        raise PolicyError(f"JSON을 읽을 수 없습니다: {path}: {error}") from error
    if not isinstance(value, dict):
        raise PolicyError(f"JSON object가 필요합니다: {path}")
    return value


def project_ids() -> tuple[str, ...]:
    return tuple(sorted(path.stem for path in PROJECTS_ROOT.glob("*.json")))


def load_project(project_id: str) -> ProjectConfig:
    raw = read_json(PROJECTS_ROOT / f"{project_id}.json")
    commands = raw.get("commands")
    if not isinstance(commands, dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in commands.items()
    ):
        raise PolicyError(f"commands 계약이 올바르지 않습니다: {project_id}")
    try:
        return ProjectConfig(
            id=str(raw["id"]),
            name=str(raw["name"]),
            path=Path(str(raw["path"])).resolve(),
            commands=dict(commands),
            base_branch=str(raw["base_branch"]),
            policy_path=Path(str(raw["path"])).resolve(),
        )
    except KeyError as error:
        raise PolicyError(f"프로젝트 필드가 누락되었습니다: {project_id}: {error}") from error


def select_projects(selector: str) -> tuple[ProjectConfig, ...]:
    ids = project_ids() if selector == "all" else (selector,)
    projects = tuple(load_project(project_id) for project_id in ids)
    if any(project.id != project_id for project, project_id in zip(projects, ids, strict=True)):
        raise PolicyError("프로젝트 파일명과 id가 일치하지 않습니다.")
    return projects


def replacements(project: ProjectConfig) -> dict[str, str]:
    required_commands = ("dev", "build", "lint", "test", "preview")
    missing = [name for name in required_commands if name not in project.commands]
    if missing:
        raise PolicyError(f"{project.id} 명령이 누락되었습니다: {', '.join(missing)}")
    return {
        "{{PROJECT_ID}}": project.id,
        "{{PROJECT_NAME}}": project.name,
        "{{PROJECT_PATH}}": str(project.path),
        "{{CENTRAL_ROOT}}": str(CANONICAL_ROOT),
        "{{BASE_BRANCH}}": project.base_branch,
        "{{DEV_COMMAND}}": project.commands["dev"],
        "{{BUILD_COMMAND}}": project.commands["build"],
        "{{LINT_COMMAND}}": project.commands["lint"],
        "{{TEST_COMMAND}}": project.commands["test"],
        "{{PREVIEW_COMMAND}}": project.commands["preview"],
    }


def render_content(content: bytes, project: ProjectConfig) -> bytes:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return content
    for marker, value in replacements(project).items():
        text = text.replace(marker, value)
    return text.encode("utf-8")


def is_policy_source_file(path: Path, root: Path) -> bool:
    if not path.is_file():
        return False
    relative = path.relative_to(root)
    return (
        "__pycache__" not in relative.parts
        and path.suffix not in {".pyc", ".pyo"}
        and path.name != ".DS_Store"
    )


def add_tree(
    rendered: dict[str, bytes],
    source_root: Path,
    target_prefix: Path,
    project: ProjectConfig,
) -> None:
    for source in sorted(
        path for path in source_root.rglob("*") if is_policy_source_file(path, source_root)
    ):
        relative = (target_prefix / source.relative_to(source_root)).as_posix()
        if relative in rendered:
            raise PolicyError(f"중복 렌더 대상입니다: {relative}")
        rendered[relative] = render_content(source.read_bytes(), project)


def project_overlay_root(project: ProjectConfig) -> Path:
    """프로젝트 전용 자산 카탈로그의 중앙 원본 경로를 반환한다."""

    return CENTRAL_ROOT / "projects/overlay" / project.id


def hook_command(project: ProjectConfig, mode: str, host: str) -> str:
    """cwd와 무관한 sync runtime 절대 경로로 hook 명령을 렌더한다."""

    guard = project.policy_root / ".agent-policy/runtime/managed_policy_guard.py"
    return shlex.join(("python3", "-I", str(guard), mode, host))


def log_collection_command(project: ProjectConfig, channel: str) -> str:
    return (
        f'python3 "{CANONICAL_ROOT / "bin/agent-policy"}" collect-logs '
        f"--project {project.id} --channel {channel} --quiet"
    )


def render_opencode_config(project: ProjectConfig) -> bytes:
    config = read_json(CENTRAL_ROOT / "adapters/opencode/opencode.base.json")
    permission = config.get("permission")
    bash = permission.get("bash") if isinstance(permission, dict) else None
    if not isinstance(bash, dict):
        raise PolicyError("OpenCode config의 permission.bash가 object가 아닙니다.")
    for command_name in ("build", "dev"):
        command = project.commands[command_name]
        bash[command] = "ask"
        bash[f"{command} *"] = "ask"
    return (json.dumps(config, ensure_ascii=False, indent=2) + "\n").encode()


def render_codex_hooks(project: ProjectConfig) -> bytes:
    hooks = read_json(CENTRAL_ROOT / "adapters/codex/hooks.base.json")
    registrations = hooks.setdefault("hooks", {})
    if not isinstance(registrations, dict):
        raise PolicyError("Codex hooks base의 hooks가 object가 아닙니다.")
    registrations.setdefault("SessionStart", []).insert(
        0,
        {
            "matcher": "startup|resume|clear|compact",
            "hooks": [
                {
                    "type": "command",
                    "command": hook_command(project, "session-start", "codex"),
                    "timeout": 15,
                    "statusMessage": "Checking central agent policy drift",
                    "additionalContextLimit": 1200,
                }
            ],
        },
    )
    registrations.setdefault("UserPromptSubmit", []).insert(
        0,
        {
            "hooks": [
                {
                    "type": "command",
                    "command": hook_command(project, "user-prompt", "codex"),
                    "timeout": 10,
                    "statusMessage": "Recording common harness approval",
                }
            ],
        },
    )
    registrations.setdefault("PreToolUse", []).insert(
        0,
        {
            "hooks": [
                {
                    "type": "command",
                    "command": hook_command(project, "pre-tool", "codex"),
                    "timeout": 10,
                    "statusMessage": "Protecting central agent policy files",
                }
            ],
        },
    )
    registrations.setdefault("PostToolUse", []).insert(
        0,
        {
            "hooks": [
                {
                    "type": "command",
                    "command": hook_command(project, "post-tool", "codex"),
                    "timeout": 10,
                    "statusMessage": "Recording common harness evidence",
                }
            ],
        },
    )
    registrations["Stop"] = [
        {
            "hooks": [
                {
                    "type": "command",
                    "command": hook_command(project, "documentation-stop", "codex"),
                    "timeout": 10,
                    "statusMessage": "Checking role-based task artifacts",
                },
                {
                    "type": "command",
                    "command": log_collection_command(project, "codex"),
                    "timeout": 30,
                    "statusMessage": "Mirroring required artifacts to central logs",
                }
            ],
        }
    ]
    return (json.dumps(hooks, ensure_ascii=False, indent=2) + "\n").encode()


def render_claude_settings(project: ProjectConfig) -> bytes:
    settings = read_json(CENTRAL_ROOT / "adapters/claude/settings.base.json")
    settings["hooks"] = {
        "SessionStart": [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": hook_command(project, "session-start", "claude"),
                        "timeout": 15,
                    }
                ]
            }
        ],
        "UserPromptSubmit": [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": hook_command(project, "user-prompt", "claude"),
                        "timeout": 10,
                    }
                ]
            }
        ],
        "PreToolUse": [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": hook_command(project, "pre-tool", "claude"),
                        "timeout": 10,
                    }
                ],
            }
        ],
        "PostToolUse": [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": hook_command(project, "post-tool", "claude"),
                        "timeout": 10,
                    }
                ]
            }
        ],
        "Stop": [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": hook_command(project, "documentation-stop", "claude"),
                        "timeout": 10,
                    },
                    {
                        "type": "command",
                        "command": log_collection_command(project, "claude"),
                        "timeout": 30,
                    }
                ]
            }
        ],
    }
    return (json.dumps(settings, ensure_ascii=False, indent=2) + "\n").encode()


def render_project(project: ProjectConfig) -> dict[str, bytes]:
    rendered: dict[str, bytes] = {}
    common_contract = render_content(
        (CENTRAL_ROOT / "policy/common/AGENT_POLICY.template.md").read_bytes(), project
    )
    rendered["AGENTS.md"] = common_contract
    rendered[".agent-policy/common/AGENT_POLICY.md"] = common_contract
    rendered["CLAUDE.md"] = render_content(
        (CENTRAL_ROOT / "adapters/claude/CLAUDE.template.md").read_bytes(), project
    )
    add_tree(rendered, CENTRAL_ROOT / "policy/common/skills", Path(".agents/skills"), project)
    add_tree(
        rendered,
        CENTRAL_ROOT / "policy/common/skills",
        Path(".agent-policy/common/skills"),
        project,
    )
    overlay_skills = project_overlay_root(project) / "skills"
    if overlay_skills.is_dir():
        add_tree(rendered, overlay_skills, Path(".agents/skills"), project)
        add_tree(rendered, overlay_skills, Path(".agent-policy/common/skills"), project)
    add_tree(
        rendered,
        CENTRAL_ROOT / "policy/common/contracts",
        Path(".agent-policy/common/contracts"),
        project,
    )
    add_tree(
        rendered,
        CENTRAL_ROOT / "policy/common/templates",
        Path(".agent-policy/common/templates"),
        project,
    )
    for template_root in (
        Path(".codex/templates"),
        Path(".claude/templates"),
        Path(".opencode/templates"),
    ):
        add_tree(
            rendered,
            CENTRAL_ROOT / "policy/common/templates",
            template_root,
            project,
        )
    for host in ("codex", "claude", "opencode"):
        add_tree(
            rendered,
            CENTRAL_ROOT / f"adapters/{host}/files",
            Path(),
            project,
        )
    rendered["opencode.json"] = render_opencode_config(project)
    branch_guard = render_content(
        (CENTRAL_ROOT / "policy/guards/branch_guard.py").read_bytes(), project
    )
    rendered[".agent-policy/runtime/branch_guard.py"] = branch_guard
    rendered[".agent-policy/runtime/managed_policy_guard.py"] = render_content(
        (CENTRAL_ROOT / "policy/guards/managed_policy_guard.py").read_bytes(), project
    )
    rendered[".codex/hooks.json"] = render_codex_hooks(project)
    rendered[".claude/settings.json"] = render_claude_settings(project)
    return dict(sorted(rendered.items()))


def source_files(project: ProjectConfig) -> tuple[Path, ...]:
    roots = (
        CENTRAL_ROOT / "policy/common",
        CENTRAL_ROOT / "policy/guards",
        CENTRAL_ROOT / "adapters/codex",
        CENTRAL_ROOT / "adapters/claude",
        CENTRAL_ROOT / "adapters/opencode",
    )
    files: list[Path] = []
    for root in roots:
        files.extend(path for path in root.rglob("*") if is_policy_source_file(path, root))
    files.append(PROJECTS_ROOT / f"{project.id}.json")
    return tuple(sorted(set(files)))


def source_digest(project: ProjectConfig) -> str:
    digest = hashlib.sha256()
    for path in source_files(project):
        digest.update(path.relative_to(CENTRAL_ROOT).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def central_commit() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=CENTRAL_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else "uncommitted"


def central_is_clean() -> bool:
    completed = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=CENTRAL_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return False
    entries = tuple(line for line in completed.stdout.splitlines() if line.strip())
    return all(central_status_entry_is_log_only(entry) for entry in entries)


def central_status_entry_is_log_only(entry: str) -> bool:
    if len(entry) < 4:
        return False
    paths = tuple(path.strip() for path in entry[3:].split(" -> "))
    return bool(paths) and all(path == "logs" or path.startswith("logs/") for path in paths)


def load_manifest(project: ProjectConfig) -> dict[str, Any]:
    path = project.path / MANIFEST_RELATIVE
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"_invalid": True}
    return value if isinstance(value, dict) else {"_invalid": True}


def manifest_payload(project: ProjectConfig, rendered: dict[str, bytes]) -> dict[str, Any]:
    return {
        "version": 1,
        "project_id": project.id,
        "project_name": project.name,
        "central_root": str(CANONICAL_ROOT),
        "central_commit": central_commit(),
        "source_digest": source_digest(project),
        "managed_roots": list(MANAGED_ROOTS),
        "managed_files": {
            path: sha256_bytes(content) for path, content in sorted(rendered.items())
        },
        "synced_at": datetime.now(timezone.utc).isoformat(),
    }


def legacy_entries(project: ProjectConfig) -> tuple[dict[str, str], ...]:
    path = PROJECTS_ROOT / "legacy" / f"{project.id}.json"
    if not path.is_file():
        return ()
    raw_entries = read_json(path).get("entries", [])
    if not isinstance(raw_entries, list):
        raise PolicyError(f"legacy entries가 list가 아닙니다: {path}")
    entries: list[dict[str, str]] = []
    for entry in raw_entries:
        if not isinstance(entry, dict):
            raise PolicyError(f"legacy entry가 object가 아닙니다: {path}")
        relative = entry.get("path")
        digest = entry.get("sha256")
        if not isinstance(relative, str) or not isinstance(digest, str):
            raise PolicyError(f"legacy entry 필드가 잘못되었습니다: {path}")
        entries.append({"path": relative, "sha256": digest})
    return tuple(entries)


def existing_legacy(project: ProjectConfig, expected: Iterable[str]) -> tuple[LegacyTrace, ...]:
    expected_set = set(expected)
    traces: list[LegacyTrace] = []
    for entry in legacy_entries(project):
        relative = entry["path"]
        if relative in expected_set:
            continue
        target = safe_target(project.path, relative)
        if target.is_file():
            traces.append(
                LegacyTrace(
                    path=relative,
                    expected_sha256=entry["sha256"],
                    actual_sha256=sha256_file(target),
                )
            )
    return tuple(sorted(traces, key=lambda trace: trace.path))


def safe_target(root: Path, relative: str) -> Path:
    candidate = root / relative
    try:
        candidate.resolve().relative_to(root.resolve())
    except (OSError, ValueError) as error:
        raise PolicyError(f"프로젝트 밖의 경로는 사용할 수 없습니다: {relative}") from error
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise PolicyError(f"안전하지 않은 상대 경로입니다: {relative}")
    return candidate


def diff_project(project: ProjectConfig) -> ProjectDiff:
    rendered = render_project(project)
    manifest = load_manifest(project)
    managed_value = manifest.get("managed_files")
    prior_managed = set(managed_value) if isinstance(managed_value, dict) else set()
    added: list[str] = []
    changed: list[str] = []
    for relative, content in rendered.items():
        target = safe_target(project.path, relative)
        if not target.is_file():
            added.append(relative)
        elif target.read_bytes() != content:
            changed.append(relative)
    stale = sorted(prior_managed - set(rendered))

    issues: list[str] = []
    if not manifest:
        issues.append("manifest missing")
    elif manifest.get("_invalid"):
        issues.append("manifest invalid")
    else:
        if manifest.get("project_id") != project.id:
            issues.append("manifest project_id mismatch")
        if manifest.get("central_root") != str(CANONICAL_ROOT):
            issues.append("manifest central_root mismatch")
        if manifest.get("source_digest") != source_digest(project):
            issues.append("central source digest changed")
        expected_hashes = {path: sha256_bytes(content) for path, content in rendered.items()}
        if managed_value != expected_hashes:
            issues.append("manifest managed_files mismatch")

    return ProjectDiff(
        project=project,
        added=tuple(sorted(added)),
        changed=tuple(sorted(changed)),
        stale=tuple(stale),
        legacy=existing_legacy(project, rendered),
        manifest_issues=tuple(issues),
    )


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(file_descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def verify_safe_removals(
    project: ProjectConfig,
    rendered: dict[str, bytes],
    manifest: dict[str, Any],
    retire_legacy: bool,
) -> tuple[Path, ...]:
    removals: list[Path] = []
    managed_value = manifest.get("managed_files")
    if isinstance(managed_value, dict):
        for relative, expected_hash in managed_value.items():
            if relative in rendered:
                continue
            target = safe_target(project.path, relative)
            if not target.exists():
                continue
            if not target.is_file() or sha256_file(target) != expected_hash:
                raise PolicyError(f"수정된 이전 managed 파일은 삭제하지 않습니다: {project.id}:{relative}")
            removals.append(target)

    legacy = existing_legacy(project, rendered)
    if legacy and not retire_legacy:
        raise PolicyError(
            f"{project.id}에 legacy 파일 {len(legacy)}개가 남아 있습니다. "
            "diff를 검토하고 승인 후 --retire-legacy를 명시하세요."
        )
    for trace in legacy:
        if not trace.matches:
            raise PolicyError(f"감사 후 변경된 legacy 파일은 삭제하지 않습니다: {project.id}:{trace.path}")
        removals.append(safe_target(project.path, trace.path))
    return tuple(sorted(set(removals)))


def sync_project(project: ProjectConfig, retire_legacy: bool = False) -> int:
    if not central_is_clean():
        raise PolicyError("중앙 정책 소스에 commit되지 않은 변경이 있어 sync를 거부합니다.")
    if not project.path.is_dir():
        raise PolicyError(f"대상 프로젝트를 찾을 수 없습니다: {project.path}")

    rendered = render_project(project)
    manifest = load_manifest(project)
    removals = verify_safe_removals(project, rendered, manifest, retire_legacy)
    for relative, content in rendered.items():
        atomic_write(safe_target(project.path, relative), content)
    for target in removals:
        target.unlink()
    payload = manifest_payload(project, rendered)
    atomic_write(
        project.path / MANIFEST_RELATIVE,
        (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode(),
    )
    return len(rendered)


def audit_project(project: ProjectConfig) -> tuple[str, ...]:
    issues: list[str] = []
    if not project.path.is_dir():
        issues.append(f"project path missing: {project.path}")
        return tuple(issues)
    rendered = render_project(project)
    for relative, content in rendered.items():
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            continue
        if "asan-prompt-core" in text:
            issues.append(f"forbidden legacy reference: {relative}")
        unresolved = (
            "{{PROJECT_",
            "{{CENTRAL_ROOT}}",
            "{{BASE_BRANCH}}",
            "{{DEV_COMMAND}}",
            "{{BUILD_COMMAND}}",
            "{{LINT_COMMAND}}",
            "{{TEST_COMMAND}}",
            "{{PREVIEW_COMMAND}}",
        )
        if any(marker in text for marker in unresolved):
            issues.append(f"unresolved placeholder: {relative}")
    return tuple(issues)


def audit_source_contract() -> tuple[str, ...]:
    """공통 정본·adapter·runtime이 하나의 호스트 중립 계약인지 검사한다."""

    issues: list[str] = []
    contract_path = CENTRAL_ROOT / "policy/common/contracts/runtime-policy.json"
    try:
        contract = read_json(contract_path)
    except PolicyError as error:
        return (str(error),)

    if contract.get("version") != 3:
        issues.append("runtime contract version mismatch")
    roles = contract.get("roles")
    expected_roles = {
        "logic": {"canonical": "logic"},
        "ui": {"canonical": "ui"},
        "orchest": {"canonical": "orchestration"},
        "review": {"canonical": "review"},
        "generate": {"canonical": "integrated"},
    }
    if roles != expected_roles:
        issues.append("runtime role registry mismatch")
    hosts = contract.get("hosts")
    expected_hosts = {
        "codex": {"artifact_root": ".codex/logs/sessions"},
        "claude": {"artifact_root": ".claude/logs/sessions"},
        "opencode": {"artifact_root": ".opencode/logs/sessions"},
        "unknown": {"artifact_root": ".agent-policy/logs/unknown/sessions"},
    }
    if hosts != expected_hosts:
        issues.append("runtime host registry mismatch")
    artifacts = contract.get("artifacts")
    required = artifacts.get("required") if isinstance(artifacts, dict) else None
    if required != list(EXPECTED_REQUIRED_ARTIFACTS):
        issues.append("OpenCode-origin required artifact registry mismatch")
    if not isinstance(artifacts, dict) or artifacts.get("responsibilities") != [
        "owner",
        "contributor",
    ]:
        issues.append("artifact responsibility registry mismatch")
    if not isinstance(artifacts, dict) or artifacts.get("unknown_directory") != "unknown":
        issues.append("unknown artifact directory registry mismatch")
    if not isinstance(artifacts, dict) or artifacts.get("handoff") != "handoff.md":
        issues.append("handoff artifact registry mismatch")
    if contract.get("task_states") != [
        "IDLE",
        "ACTIVE",
        "READY_TO_MERGE",
        "MERGED_VERIFIED",
        "CLOSED",
        "PRESERVED",
    ]:
        issues.append("task state registry mismatch")

    git_policy = contract.get("git")
    never_agent = git_policy.get("never_agent_commands") if isinstance(git_policy, dict) else None
    if never_agent != ["push", "reset --hard", "clean", "update-ref"]:
        issues.append("never-agent Git command registry mismatch")
    validation = git_policy.get("validation_commands") if isinstance(git_policy, dict) else None
    if validation != ["{{LINT_COMMAND}}", "{{TEST_COMMAND}}", "{{BUILD_COMMAND}}"]:
        issues.append("validation command registry mismatch")

    template_root = CENTRAL_ROOT / "policy/common/templates"
    expected_templates = {
        "README.md",
        "agent-output-schema.yaml",
        "handoff.md",
        "handoff.template.md",
        *(name for artifact in EXPECTED_REQUIRED_ARTIFACTS for name in (artifact, f"{artifact.removesuffix('.md')}.template.md")),
    }
    actual_templates = {
        path.name for path in template_root.iterdir() if path.is_file()
    } if template_root.is_dir() else set()
    if actual_templates != expected_templates:
        missing = sorted(expected_templates - actual_templates)
        extra = sorted(actual_templates - expected_templates)
        issues.append(f"common template set mismatch: missing={missing}, extra={extra}")

    portfolio = template_root / "portfolio-log.template.md"
    if portfolio.is_file():
        text = portfolio.read_text(encoding="utf-8")
        required_portfolio_sections = (
            "### 문제 상황",
            "### 고민과 선택",
            "### 적용",
            "### 사용 기술과 구체적 목적",
            "### 결과",
            "### 이력서·포트폴리오 문구",
        )
        if any(section not in text for section in required_portfolio_sections):
            issues.append("Claude-origin portfolio prompt structure mismatch")
    else:
        issues.append("portfolio template missing")

    agent_schema = template_root / "agent-output-schema.yaml"
    if agent_schema.is_file():
        schema_text = agent_schema.read_text(encoding="utf-8")
        harness_fields = (
            "can_proceed",
            "missing_requirements",
            "role_violation_detected",
            "approval_status",
            "retry_count",
            "escalation_signal",
        )
        if any(f"  {field}:" not in schema_text for field in harness_fields):
            issues.append("common agent output schema is missing Harness fields")
        claude_role_fields = (
            "work_type",
            "reusable_components_found",
            "implementation_summary",
            "refactor_targets",
            "repeat_issue_detected",
            "diagnosis_report",
            "recommended_backlog",
        )
        if any(f"    - {field}" not in schema_text for field in claude_role_fields):
            issues.append("common agent output schema lost Claude role-specific fields")
    else:
        issues.append("common agent output schema missing")

    legacy_codex_hooks = CENTRAL_ROOT / "adapters/codex/files/.codex/hooks"
    if legacy_codex_hooks.is_dir() and any(path.is_file() for path in legacy_codex_hooks.rglob("*")):
        issues.append("legacy Codex Python hooks remain")
    hooks_base = read_json(CENTRAL_ROOT / "adapters/codex/hooks.base.json")
    if hooks_base != {"hooks": {}}:
        issues.append("Codex adapter still registers legacy hooks")
    common_guard = CENTRAL_ROOT / "policy/guards/managed_policy_guard.py"
    common_guard_text = common_guard.read_text(encoding="utf-8")
    required_common_guard_markers = (
        "def record_user_prompt(",
        "def record_post_tool(",
        "def implementation_gate_denial(",
        '"post-tool"',
    )
    if any(marker not in common_guard_text for marker in required_common_guard_markers):
        issues.append("common guard does not supersede Codex approval/evidence hooks")
    codex_config = (CENTRAL_ROOT / "adapters/codex/files/.codex/config.toml").read_text(
        encoding="utf-8"
    )
    if re.search(r"^\s*codex_hooks\s*=", codex_config, re.MULTILINE):
        issues.append("deprecated Codex codex_hooks feature remains")

    scanned_roots = (
        CENTRAL_ROOT / "policy",
        CENTRAL_ROOT / "adapters",
        CENTRAL_ROOT / "lib",
    )
    stale_markers = (
        "HOOK_SHA256",
        "features.codex_hooks",
        ".codex/hooks/branch_guard.py",
        ".claude/hooks/branch_guard.py",
        ".opencode/plugins/branch_guard.py",
    )
    for root in scanned_roots:
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in {".py", ".js", ".json", ".toml", ".md"}:
                continue
            if path.resolve() == Path(__file__).resolve():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeError:
                continue
            for marker in stale_markers:
                if marker in text:
                    issues.append(f"stale host-specific guard marker {marker}: {path.relative_to(CENTRAL_ROOT)}")

    forbidden_role_phrases = (
        "Logic Session",
        "production UI 전담",
        "Claude UI 구현",
        "UI_COMPLETE",
        "Hephaestus",
    )
    for root in (CENTRAL_ROOT / "policy/common", CENTRAL_ROOT / "adapters"):
        for path in root.rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            for phrase in forbidden_role_phrases:
                if phrase.casefold() in text.casefold():
                    issues.append(f"fixed host-role phrase {phrase}: {path.relative_to(CENTRAL_ROOT)}")

    for project_id in project_ids():
        project = load_project(project_id)
        overlay_root = project_overlay_root(project)
        if overlay_root.is_dir():
            for path in sorted(overlay_root.rglob("*.md")):
                relative = path.relative_to(CENTRAL_ROOT)
                text = path.read_text(encoding="utf-8")
                if "synthoria" in text.casefold():
                    issues.append(f"{project_id}: overlay keeps a stale project name: {relative}")
                # overlay가 주장하는 소비자 경로는 실제로 존재해야 한다.
                # 이 검사가 V1 카탈로그를 낡게 만든 원인을 재발시키지 않는다.
                if not project.path.is_dir():
                    continue
                for reference in sorted(set(re.findall(r"`(src/[A-Za-z0-9/_.\-]+)`", text))):
                    if not (project.path / reference).exists():
                        issues.append(
                            f"{project_id}: overlay references a missing path: {relative} -> {reference}"
                        )

    for project_id in project_ids():
        rendered = render_project(load_project(project_id))
        cache_outputs = tuple(
            path
            for path in rendered
            if "__pycache__" in Path(path).parts or path.endswith((".pyc", ".pyo"))
        )
        if cache_outputs:
            issues.append(f"{project_id}: runtime cache files rendered: {cache_outputs}")
        runtime_guard_paths = tuple(path for path in rendered if path.endswith("/branch_guard.py"))
        if runtime_guard_paths != (".agent-policy/runtime/branch_guard.py",):
            issues.append(f"{project_id}: branch guard is not single common runtime: {runtime_guard_paths}")
        codex_hooks = json.loads(rendered[".codex/hooks.json"])["hooks"]
        claude_hooks = json.loads(rendered[".claude/settings.json"])["hooks"]
        for host, registrations in (("codex", codex_hooks), ("claude", claude_hooks)):
            for event, mode in (
                ("UserPromptSubmit", "user-prompt"),
                ("PreToolUse", "pre-tool"),
                ("PostToolUse", "post-tool"),
                ("Stop", "documentation-stop"),
            ):
                serialized = json.dumps(registrations.get(event, ()), ensure_ascii=False)
                if "managed_policy_guard.py" not in serialized or f"{mode} {host}" not in serialized:
                    issues.append(f"{project_id}: {host} common guard registration missing: {event}")
        opencode_plugin = rendered[".opencode/plugins/agent-policy.js"].decode("utf-8")
        for marker in ('"chat.message"', '"tool.execute.before"', '"tool.execute.after"'):
            if marker not in opencode_plugin:
                issues.append(f"{project_id}: OpenCode common guard event missing: {marker}")
        for template_name in expected_templates:
            common_path = f".agent-policy/common/templates/{template_name}"
            if common_path not in rendered:
                issues.append(f"{project_id}: missing rendered common template {template_name}")
                continue
            for host_root in (".codex/templates", ".claude/templates", ".opencode/templates"):
                host_path = f"{host_root}/{template_name}"
                if rendered.get(host_path) != rendered[common_path]:
                    issues.append(f"{project_id}: template adapter drift {host_path}")

        common_paths = set(rendered)
        for relative, content in rendered.items():
            if not relative.startswith(("CLAUDE.md", ".claude/", ".codex/agents/", ".opencode/agent/")):
                continue
            try:
                text = content.decode("utf-8")
            except UnicodeDecodeError:
                continue
            for reference in re.findall(r"`(\.agent-policy/common/[^`]+)`", text):
                normalized = reference.rstrip("/.,:;)")
                if normalized.endswith("/**"):
                    normalized = normalized.removesuffix("**")
                if normalized.endswith("/"):
                    if not any(path.startswith(normalized) for path in common_paths):
                        issues.append(f"{project_id}: unresolved common reference {relative} -> {reference}")
                elif normalized not in common_paths:
                    issues.append(f"{project_id}: unresolved common reference {relative} -> {reference}")
    return tuple(dict.fromkeys(issues))


def start_command(project: ProjectConfig, host: str, model: str | None) -> list[str]:
    if host not in HOST_COMMANDS:
        raise PolicyError(f"지원하지 않는 host입니다: {host}")
    command = list(HOST_COMMANDS[host])
    if model:
        command.extend(["--model", model])
    return command
