from __future__ import annotations

import hashlib
import json
import os
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
    ".agent-policy/",
    ".agents/skills/",
    ".claude/agents/",
    ".claude/harness/",
    ".claude/multi-agent-spec.md",
    ".claude/multi-agent-spec/",
    ".claude/settings.json",
    ".claude/skills/",
    ".claude/templates/",
    ".claude/workflows/",
    ".codex/agents/",
    ".codex/config.toml",
    ".codex/harness/",
    ".codex/hooks.json",
    ".codex/hooks/",
    ".codex/multi-agent-spec.md",
    ".codex/multi-agent-spec/",
    ".codex/templates/",
    ".codex/workflows/",
    ".harness/roles/",
    ".opencode/agent/",
    ".opencode/plugins/",
    "opencode.json",
)
HOST_COMMANDS: Final = {
    "codex": ["codex"],
    "claude": ["claude"],
    "opencode": ["opencode"],
}


class PolicyError(RuntimeError):
    """운영자가 해결해야 하는 정책 오류."""


@dataclass(frozen=True)
class ProjectConfig:
    id: str
    name: str
    path: Path
    commands: dict[str, str]


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
    required_commands = ("dev", "build", "lint", "test")
    missing = [name for name in required_commands if name not in project.commands]
    if missing:
        raise PolicyError(f"{project.id} 명령이 누락되었습니다: {', '.join(missing)}")
    return {
        "{{PROJECT_ID}}": project.id,
        "{{PROJECT_NAME}}": project.name,
        "{{PROJECT_PATH}}": str(project.path),
        "{{CENTRAL_ROOT}}": str(CANONICAL_ROOT),
        "{{DEV_COMMAND}}": project.commands["dev"],
        "{{BUILD_COMMAND}}": project.commands["build"],
        "{{LINT_COMMAND}}": project.commands["lint"],
        "{{TEST_COMMAND}}": project.commands["test"],
    }


def render_content(content: bytes, project: ProjectConfig) -> bytes:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return content
    for marker, value in replacements(project).items():
        text = text.replace(marker, value)
    return text.encode("utf-8")


def add_tree(
    rendered: dict[str, bytes],
    source_root: Path,
    target_prefix: Path,
    project: ProjectConfig,
) -> None:
    for source in sorted(path for path in source_root.rglob("*") if path.is_file()):
        relative = (target_prefix / source.relative_to(source_root)).as_posix()
        if relative in rendered:
            raise PolicyError(f"중복 렌더 대상입니다: {relative}")
        rendered[relative] = render_content(source.read_bytes(), project)


def hook_command(mode: str, host: str) -> str:
    return (
        'ROOT="$(git rev-parse --show-toplevel)" || exit 2; '
        f'python3 -I "$ROOT/.agent-policy/runtime/managed_policy_guard.py" {mode} {host}'
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
                    "command": hook_command("session-start", "codex"),
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
                    "command": hook_command("user-prompt", "codex"),
                    "timeout": 10,
                    "statusMessage": "Recording one-shot command approval",
                }
            ],
        },
    )
    registrations.setdefault("PreToolUse", []).insert(
        0,
        {
            "matcher": "Bash|Edit|Write|apply_patch",
            "hooks": [
                {
                    "type": "command",
                    "command": hook_command("pre-tool", "codex"),
                    "timeout": 10,
                    "statusMessage": "Protecting central agent policy files",
                }
            ],
        },
    )
    return (json.dumps(hooks, ensure_ascii=False, indent=2) + "\n").encode()


def render_claude_settings(project: ProjectConfig) -> bytes:
    settings = read_json(CENTRAL_ROOT / "adapters/claude/settings.base.json")
    settings["hooks"] = {
        "SessionStart": [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": hook_command("session-start", "claude"),
                        "timeout": 15,
                    }
                ]
            }
        ],
        "PreToolUse": [
            {
                "matcher": "Bash|Edit|Write|MultiEdit|NotebookEdit",
                "hooks": [
                    {
                        "type": "command",
                        "command": hook_command("pre-tool", "claude"),
                        "timeout": 10,
                    }
                ],
            }
        ],
    }
    return (json.dumps(settings, ensure_ascii=False, indent=2) + "\n").encode()


def render_project(project: ProjectConfig) -> dict[str, bytes]:
    rendered: dict[str, bytes] = {}
    rendered["AGENTS.md"] = render_content(
        (CENTRAL_ROOT / "policy/common/AGENTS.template.md").read_bytes(), project
    )
    rendered["CLAUDE.md"] = render_content(
        (CENTRAL_ROOT / "adapters/claude/CLAUDE.template.md").read_bytes(), project
    )
    add_tree(rendered, CENTRAL_ROOT / "policy/common/skills", Path(".agents/skills"), project)
    for host in ("codex", "claude", "opencode"):
        add_tree(
            rendered,
            CENTRAL_ROOT / f"adapters/{host}/files",
            Path(),
            project,
        )
    rendered["opencode.json"] = render_opencode_config(project)
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
        files.extend(path for path in root.rglob("*") if path.is_file())
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
    return completed.returncode == 0 and not completed.stdout.strip()


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
        raise PolicyError("중앙 저장소에 commit되지 않은 변경이 있어 sync를 거부합니다.")
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
        if "{{PROJECT_" in text or "{{CENTRAL_ROOT}}" in text or "{{DEV_COMMAND}}" in text:
            issues.append(f"unresolved placeholder: {relative}")
    return tuple(issues)


def start_command(project: ProjectConfig, host: str, model: str | None) -> list[str]:
    if host not in HOST_COMMANDS:
        raise PolicyError(f"지원하지 않는 host입니다: {host}")
    command = list(HOST_COMMANDS[host])
    if model:
        command.extend(["--model", model])
    return command
