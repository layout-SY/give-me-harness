from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import shutil
import tempfile
import tomllib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Final, Mapping

from . import role_profiles as role_profiles_module
from .core import (
    CENTRAL_ROOT,
    HOST_COMMANDS,
    PolicyError,
    ProjectConfig,
    atomic_write,
    central_commit,
    central_is_clean,
    render_project,
    sha256_bytes,
    source_digest,
)
from .role_profiles import (
    ARTIFACT_RESPONSIBILITIES,
    artifact_session_root,
    common_skill_selected,
    role_document_paths,
    role_profile,
)

BUILD_ROOT: Final = CENTRAL_ROOT / "build"
STATE_ROOT: Final = CENTRAL_ROOT / "state"
INJECT_MODE_ENV: Final = "ASAN_AGENT_POLICY_MODE"
INJECT_PROJECT_ENV: Final = "ASAN_AGENT_POLICY_PROJECT"
INJECT_PROJECT_PATH_ENV: Final = "ASAN_AGENT_POLICY_PROJECT_PATH"
INJECT_BUNDLE_ROOT_ENV: Final = "ASAN_AGENT_POLICY_BUNDLE_ROOT"
INJECT_ROLE_ENV: Final = "ASAN_AGENT_POLICY_ROLE"
INJECT_TASK_ENV: Final = "ASAN_AGENT_POLICY_TASK"
ARTIFACT_RESPONSIBILITY_ENV: Final = "ASAN_ARTIFACT_RESPONSIBILITY"
BUNDLE_MANIFEST: Final = "manifest.json"
CODEX_STATE_MANIFEST: Final = ".asan-agent-policy-inject.json"
OPENCODE_RUNTIME_FILES: Final[frozenset[str]] = frozenset(
    {
        "opencode-home/.gitignore",
        "opencode-home/bun.lock",
        "opencode-home/package-lock.json",
        "opencode-home/package.json",
    }
)
OPENCODE_NODE_MODULES: Final = "opencode-home/node_modules"


@dataclass(frozen=True)
class InjectionLaunch:
    project: ProjectConfig
    host: str
    role: str
    bundle_root: Path
    system_prompt: Path
    command: tuple[str, ...]
    environment: dict[str, str]


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def _bundle_digest(
    rendered: Mapping[str, bytes],
    host: str,
    role: str,
    project_path: Path,
) -> str:
    digest = hashlib.sha256()
    digest.update(host.encode())
    digest.update(b"\0")
    digest.update(role.encode())
    digest.update(b"\0")
    digest.update(str(project_path.resolve()).encode())
    digest.update(b"\0")
    for relative, content in sorted(rendered.items()):
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(content)
        digest.update(b"\0")
    digest.update(Path(__file__).read_bytes())
    digest.update(Path(str(role_profiles_module.__file__)).read_bytes())
    return digest.hexdigest()


def _injection_preamble(
    project: ProjectConfig,
    host: str,
    role: str,
    policy_root: Path,
) -> str:
    profile = role_profile(role)
    documents = "\n".join(f"  - `{path}`" for path in role_document_paths(host, role))
    artifact_root = artifact_session_root(host)
    return f"""# 중앙 정책 inject 실행 컨텍스트

이 세션은 소비자 저장소에 배포된 정책 파일이 아니라 중앙 정책 번들을 사용한다.

- 작업 프로젝트 루트: `{project.path}`
- 읽기 전용 정책 스냅샷: `{policy_root}`
- 실행 호스트: `{host}`
- 선택된 role: `{role}` (`{profile.canonical_name}`)
- 역할 목적: {profile.summary}
- 아래에 바인딩된 정책 상대 경로는 읽을 때 정책 스냅샷 아래에서 해석한다.
- 애플리케이션 경로와 `{artifact_root}/**` 산출물 경로는 작업 프로젝트 루트에서 해석한다.
- 정책 스냅샷과 중앙 저장소는 세션에서 직접 수정하지 않는다. 정책 변경은 중앙 저장소의 승인 절차를 따른다.
- 소비자 저장소의 기존 `AGENTS.md`, `CLAUDE.md`, `.codex/**`, `.claude/**`,
  `.opencode/**`는 이 inject 세션의 정책 원본이 아니다.

## Role 계약

`--role {role}`은 이 inject 세션의 역할 확인을 대신한다. 범위 안의 새 요청마다 같은 역할을 다시 묻지 않는다.
다른 역할이 필요하면 현재 역할을 확장하지 말고 사용자에게 이유를 보고한 뒤 새 `--role` 세션으로 시작한다.
이 경계는 현재 system prompt의 운영 계약이며 별도 role 감시 hook으로 강제하지 않는다.

바인딩된 역할 문서:

{documents}
"""


def _system_prompt(
    project: ProjectConfig,
    host: str,
    role: str,
    rendered: Mapping[str, bytes],
    policy_root: Path,
) -> bytes:
    entry = "CLAUDE.md" if host == "claude" else "AGENTS.md"
    sections = [
        _injection_preamble(project, host, role, policy_root),
    ]
    if host == "claude":
        sections.append(rendered[".agent-policy/common/AGENT_POLICY.md"].decode("utf-8"))
    sections.append(rendered[entry].decode("utf-8"))
    return ("\n\n---\n\n".join(section.rstrip() for section in sections) + "\n").encode()


def _agent_selected(relative: str, prefix: str, names: tuple[str, ...]) -> bool:
    if not relative.startswith(prefix):
        return False
    name = Path(relative).stem
    return name in names


def _role_selected_rendered(
    rendered: Mapping[str, bytes],
    host: str,
    role: str,
) -> dict[str, bytes]:
    profile = role_profile(role)
    selected: dict[str, bytes] = {}

    for relative, content in rendered.items():
        include = relative.startswith(".agent-policy/runtime/")
        include = include or relative == ".agent-policy/common/AGENT_POLICY.md"
        include = include or relative.startswith(".agent-policy/common/contracts/")
        include = include or relative.startswith(".agent-policy/common/templates/")
        if host == "claude":
            include = include or relative == "CLAUDE.md"
        else:
            include = include or relative == "AGENTS.md"

        if relative.startswith(".agent-policy/common/skills/"):
            include = common_skill_selected(relative, role)

        if host == "codex":
            include = include or relative in {".codex/config.toml", ".codex/hooks.json"}
            include = include or relative.startswith(".codex/hooks/")
            include = include or relative.startswith(".codex/templates/")
            include = include or _agent_selected(
                relative, ".codex/agents/", profile.native_agents
            )

        elif host == "claude":
            include = include or relative in {
                ".claude/settings.json",
                ".claude/hookify.require-documentation.local.md",
            }
            include = include or relative.startswith(".claude/hooks/")
            include = include or relative.startswith(".claude/templates/")
            include = include or relative.startswith(".claude/skills/project-role/")
            include = include or _agent_selected(
                relative, ".claude/agents/", profile.native_agents
            )
            if role in {"ui", "generate"}:
                include = include or relative.startswith(".claude/skills/project-ui/")

        elif host == "opencode":
            include = include or relative == "opencode.json"
            include = include or relative.startswith(".opencode/plugins/")
            include = include or relative.startswith(".opencode/templates/")
            include = include or _agent_selected(
                relative, ".opencode/agent/", profile.native_agents
            )

        if include:
            selected[relative] = content

    entry = "CLAUDE.md" if host == "claude" else "AGENTS.md"
    missing = [
        entry,
        ".agent-policy/common/AGENT_POLICY.md",
        ".agent-policy/runtime/managed_policy_guard.py",
        ".agent-policy/runtime/branch_guard.py",
    ]
    absent = [relative for relative in missing if relative not in selected]
    if absent:
        raise PolicyError(f"inject role 필수 문서가 누락되었습니다: {', '.join(absent)}")
    return dict(sorted(selected.items()))


def _guard_command(runtime: Path, mode: str, host: str) -> str:
    return f"python3 -I {shlex.quote(str(runtime))} {mode} {host}"


def _replace_guard_commands(value: object, runtime: Path, host: str) -> object:
    if isinstance(value, list):
        return [_replace_guard_commands(item, runtime, host) for item in value]
    if isinstance(value, dict):
        return {
            key: _replace_guard_commands(item, runtime, host)
            for key, item in value.items()
        }
    if not isinstance(value, str) or ".agent-policy/runtime/managed_policy_guard.py" not in value:
        return value
    for mode in (
        "session-start",
        "user-prompt",
        "pre-tool",
        "post-tool",
        "documentation-stop",
    ):
        if value.endswith(f" {mode} {host}"):
            return _guard_command(runtime, mode, host)
    raise PolicyError(f"inject guard 명령을 해석할 수 없습니다: {host}: {value}")


def _render_claude_files(
    rendered: Mapping[str, bytes],
    bundle_root: Path,
) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    plugin = bundle_root / "plugin"
    runtime = plugin / "runtime/managed_policy_guard.py"
    files["plugin/.claude-plugin/plugin.json"] = _json_bytes(
        {
            "$schema": "https://anthropic.com/claude-code/plugin.schema.json",
            "name": "asan-agent-policy",
            "version": "1.0.0",
            "description": "중앙 asan agent policy inject bundle",
            "author": {"name": "asan-agent-policy maintainers"},
            "skills": ["./skills"],
        }
    )
    for relative, content in rendered.items():
        if relative.startswith(".agent-policy/common/skills/"):
            target = "plugin/skills/" + relative.removeprefix(
                ".agent-policy/common/skills/"
            )
            files[target] = content
        elif relative.startswith(".claude/skills/"):
            target = "plugin/skills/" + relative.removeprefix(".claude/skills/")
            if target in files:
                raise PolicyError(f"Claude inject skill 경로가 중복됩니다: {target}")
            files[target] = content
        elif relative.startswith(".claude/agents/"):
            files["plugin/agents/" + relative.removeprefix(".claude/agents/")] = content

    files["plugin/runtime/managed_policy_guard.py"] = rendered[
        ".agent-policy/runtime/managed_policy_guard.py"
    ]
    files["plugin/runtime/branch_guard.py"] = rendered[
        ".agent-policy/runtime/branch_guard.py"
    ]
    settings = json.loads(rendered[".claude/settings.json"])
    hooks = settings.pop("hooks", {})
    files["plugin/hooks/hooks.json"] = _json_bytes(
        {"hooks": _replace_guard_commands(hooks, runtime, "claude")}
    )
    files["claude-settings.json"] = _json_bytes(settings)
    return files


def _render_opencode_files(
    rendered: Mapping[str, bytes],
    bundle_root: Path,
) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    home = bundle_root / "opencode-home"
    runtime = home / "runtime/managed_policy_guard.py"
    system_prompt = bundle_root / "system-prompt.md"
    skills = home / "skills"

    config = json.loads(rendered["opencode.json"])
    config["instructions"] = [str(system_prompt)]
    config["skills"] = [str(skills)]
    files["opencode-home/opencode.json"] = _json_bytes(config)
    for relative, content in rendered.items():
        if relative.startswith(".agent-policy/common/skills/"):
            files[
                "opencode-home/skills/"
                + relative.removeprefix(".agent-policy/common/skills/")
            ] = content
        elif relative.startswith(".opencode/agent/"):
            files["opencode-home/agents/" + relative.removeprefix(".opencode/agent/")] = content
        elif relative.startswith(".opencode/plugins/"):
            target = "opencode-home/plugins/" + relative.removeprefix(".opencode/plugins/")
            files[target] = content

    plugin_path = "opencode-home/plugins/agent-policy.js"
    plugin = files[plugin_path].decode("utf-8")
    original = 'join(directory, ".agent-policy/runtime/managed_policy_guard.py")'
    replacement = json.dumps(str(runtime), ensure_ascii=False)
    if plugin.count(original) != 1:
        raise PolicyError("OpenCode inject plugin의 guard 경로 계약이 변경되었습니다.")
    files[plugin_path] = plugin.replace(original, replacement).encode()
    files["opencode-home/runtime/managed_policy_guard.py"] = rendered[
        ".agent-policy/runtime/managed_policy_guard.py"
    ]
    files["opencode-home/runtime/branch_guard.py"] = rendered[
        ".agent-policy/runtime/branch_guard.py"
    ]
    return files


def _render_bundle_files(
    project: ProjectConfig,
    host: str,
    role: str,
    rendered: Mapping[str, bytes],
    bundle_root: Path,
) -> dict[str, bytes]:
    files = {f"policy/{relative}": content for relative, content in rendered.items()}
    files["system-prompt.md"] = _system_prompt(
        project,
        host,
        role,
        rendered,
        bundle_root / "policy",
    )
    if host == "claude":
        files.update(_render_claude_files(rendered, bundle_root))
    elif host == "opencode":
        files.update(_render_opencode_files(rendered, bundle_root))
    elif host != "codex":
        raise PolicyError(f"지원하지 않는 inject host입니다: {host}")
    return dict(sorted(files.items()))


def _manifest_payload(
    project: ProjectConfig,
    host: str,
    role: str,
    digest: str,
    files: Mapping[str, bytes],
) -> dict[str, object]:
    return {
        "version": 2,
        "mode": "inject",
        "project_id": project.id,
        "host": host,
        "role": role,
        "central_root": str(CENTRAL_ROOT),
        "central_commit": central_commit(),
        "central_clean": central_is_clean(),
        "source_digest": source_digest(project),
        "bundle_digest": digest,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "files": {relative: sha256_bytes(content) for relative, content in files.items()},
    }


def _bundle_is_valid(bundle_root: Path, digest: str) -> bool:
    if bundle_root.is_symlink() or not bundle_root.is_dir():
        return False
    try:
        manifest = json.loads((bundle_root / BUNDLE_MANIFEST).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return False
    expected = manifest.get("files")
    if manifest.get("bundle_digest") != digest or not isinstance(expected, dict):
        return False
    actual_files: set[str] = set()
    for path in bundle_root.rglob("*"):
        relative = path.relative_to(bundle_root).as_posix()
        if relative in OPENCODE_RUNTIME_FILES or relative.startswith(
            f"{OPENCODE_NODE_MODULES}/"
        ):
            continue
        if path.is_symlink():
            return False
        if not path.is_file():
            continue
        if relative == BUNDLE_MANIFEST:
            continue
        actual_files.add(relative)
        expected_digest = expected.get(relative)
        if not isinstance(expected_digest, str) or sha256_bytes(path.read_bytes()) != expected_digest:
            return False
    return actual_files == set(expected)


def _install_bundle(
    bundle_root: Path,
    project: ProjectConfig,
    host: str,
    role: str,
    digest: str,
    files: Mapping[str, bytes],
) -> None:
    if _bundle_is_valid(bundle_root, digest):
        return
    parent = bundle_root.parent
    parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{bundle_root.name}.", dir=parent))
    previous: Path | None = None
    try:
        for relative, content in files.items():
            atomic_write(staging / relative, content)
        atomic_write(
            staging / BUNDLE_MANIFEST,
            _json_bytes(_manifest_payload(project, host, role, digest, files)),
        )
        if bundle_root.exists() or bundle_root.is_symlink():
            if bundle_root.is_symlink() or not bundle_root.is_dir():
                raise PolicyError(f"inject bundle 대상이 안전한 디렉터리가 아닙니다: {bundle_root}")
            previous = parent / f".{bundle_root.name}.previous-{os.getpid()}"
            if previous.exists():
                raise PolicyError(f"inject bundle 교체 임시 경로가 이미 존재합니다: {previous}")
            os.replace(bundle_root, previous)
        try:
            os.replace(staging, bundle_root)
        except OSError:
            if previous is not None and not bundle_root.exists():
                os.replace(previous, bundle_root)
                previous = None
            raise
        if previous is not None:
            shutil.rmtree(previous)
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def _read_state_manifest(root: Path) -> dict[str, str]:
    try:
        value = json.loads((root / CODEX_STATE_MANIFEST).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    files = value.get("files") if isinstance(value, dict) else None
    return {
        relative: digest
        for relative, digest in files.items()
        if isinstance(relative, str) and isinstance(digest, str)
    } if isinstance(files, dict) else {}


def _safe_state_target(root: Path, relative: str) -> Path:
    target = root / relative
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise PolicyError(f"안전하지 않은 Codex inject state 경로입니다: {relative}")
    try:
        target.resolve(strict=False).relative_to(root.resolve())
    except (OSError, ValueError) as error:
        raise PolicyError(f"Codex inject state 밖의 경로입니다: {relative}") from error
    return target


def _sync_state_files(root: Path, files: Mapping[str, bytes]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    previous = _read_state_manifest(root)
    for relative, expected_digest in previous.items():
        if relative in files:
            continue
        target = _safe_state_target(root, relative)
        if not target.exists():
            continue
        if target.is_symlink() or not target.is_file() or sha256_bytes(target.read_bytes()) != expected_digest:
            raise PolicyError(f"수정된 Codex inject state 파일은 삭제하지 않습니다: {target}")
        target.unlink()
    for relative, content in files.items():
        target = _safe_state_target(root, relative)
        if target.is_symlink():
            raise PolicyError(f"Codex inject state managed 파일이 심볼릭 링크입니다: {target}")
        atomic_write(target, content)
    atomic_write(
        root / CODEX_STATE_MANIFEST,
        _json_bytes(
            {
                "version": 1,
                "files": {
                    relative: sha256_bytes(content)
                    for relative, content in sorted(files.items())
                },
            }
        ),
    )


def _transform_codex_hooks(
    rendered: Mapping[str, bytes],
    runtime: Path,
) -> bytes:
    hooks = json.loads(rendered[".codex/hooks.json"])
    return _json_bytes(_replace_guard_commands(hooks, runtime, "codex"))


def _toml_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, list):
        return "[" + ", ".join(_toml_value(item) for item in value) + "]"
    if isinstance(value, dict):
        entries = ", ".join(
            f"{key} = {_toml_value(item)}" for key, item in value.items()
        )
        return "{ " + entries + " }"
    raise PolicyError(f"Codex inject config 값을 CLI override로 변환할 수 없습니다: {value!r}")


def _flatten_toml(value: Mapping[str, Any], prefix: str = "") -> tuple[str, ...]:
    entries: list[str] = []
    for key, item in value.items():
        dotted = f"{prefix}.{key}" if prefix else key
        if isinstance(item, dict):
            entries.extend(_flatten_toml(item, dotted))
        else:
            entries.append(f"{dotted}={_toml_value(item)}")
    return tuple(entries)


def _link_codex_user_file(source: Path, target: Path) -> None:
    if not source.is_file() or source.resolve() == target.resolve(strict=False):
        return
    if target.is_symlink():
        if target.resolve(strict=False) == source.resolve():
            return
        target.unlink()
    elif target.exists():
        return
    temporary = target.with_name(f".{target.name}.{os.getpid()}.link")
    temporary.unlink(missing_ok=True)
    temporary.symlink_to(source)
    os.replace(temporary, target)


def _remove_stale_codex_user_link(source: Path, target: Path) -> None:
    if source.is_file() or not target.is_symlink():
        return
    if target.resolve(strict=False) == source.resolve(strict=False):
        target.unlink()


def _consumer_skill_paths(project: ProjectConfig) -> tuple[Path, ...]:
    roots = (
        project.path / ".agents/skills",
        project.path / ".claude/skills",
        project.path / ".codex/skills",
    )
    paths: set[Path] = set()
    for root in roots:
        if root.is_symlink() or not root.is_dir():
            continue
        for path in root.rglob("SKILL.md"):
            if path.is_symlink() or not path.is_file():
                continue
            try:
                path.resolve().relative_to(root.resolve())
            except (OSError, ValueError):
                continue
            paths.add(path.resolve())
    return tuple(sorted(paths))


def _skill_config_override(
    user_config: Mapping[str, Any],
    project: ProjectConfig,
) -> str | None:
    skills = user_config.get("skills")
    configured = skills.get("config") if isinstance(skills, dict) else None
    entries: list[dict[str, object]] = []
    if isinstance(configured, list):
        for item in configured:
            if not isinstance(item, dict):
                continue
            path = item.get("path")
            enabled = item.get("enabled")
            if isinstance(path, str) and isinstance(enabled, bool):
                entries.append({"path": path, "enabled": enabled})
    positions = {
        str(item.get("path")): index
        for index, item in enumerate(entries)
        if isinstance(item.get("path"), str)
    }
    for path in _consumer_skill_paths(project):
        entry = {"path": str(path), "enabled": False}
        key = str(path)
        if key in positions:
            entries[positions[key]] = entry
        else:
            positions[key] = len(entries)
            entries.append(entry)
    return f"skills.config={_toml_value(entries)}" if entries else None


def _prepare_codex_home(
    project: ProjectConfig,
    rendered: Mapping[str, bytes],
    bundle_root: Path,
    state_root: Path,
    source_codex_home: Path,
) -> tuple[Path, tuple[str, ...]]:
    codex_home = state_root / project.id / "codex-home"
    user_config_content = (
        (source_codex_home / "config.toml").read_bytes()
        if (source_codex_home / "config.toml").is_file()
        else b""
    )
    try:
        user_config = tomllib.loads(user_config_content.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
        raise PolicyError(f"사용자 Codex config.toml을 읽을 수 없습니다: {error}") from error
    files: dict[str, bytes] = {"AGENTS.md": b""}
    if not (source_codex_home / "config.toml").is_file():
        files["config.toml"] = b""
    for relative, content in rendered.items():
        if relative.startswith(".agent-policy/common/skills/"):
            files[
                "skills/" + relative.removeprefix(".agent-policy/common/skills/")
            ] = content
        elif relative.startswith(".codex/agents/"):
            files["agents/" + relative.removeprefix(".codex/agents/")] = content
    runtime = bundle_root / "policy/.agent-policy/runtime/managed_policy_guard.py"
    files["hooks.json"] = _transform_codex_hooks(
        rendered,
        runtime,
    )
    _remove_stale_codex_user_link(
        source_codex_home / "config.toml",
        codex_home / "config.toml",
    )
    _remove_stale_codex_user_link(
        source_codex_home / "auth.json",
        codex_home / "auth.json",
    )
    _sync_state_files(codex_home, files)
    _link_codex_user_file(source_codex_home / "config.toml", codex_home / "config.toml")
    _link_codex_user_file(source_codex_home / "auth.json", codex_home / "auth.json")
    policy_config = tomllib.loads(rendered[".codex/config.toml"].decode("utf-8"))
    overrides = list(_flatten_toml(policy_config))
    project_key = json.dumps(str(project.path), ensure_ascii=False)
    overrides.append(f"projects.{project_key}.trust_level=\"untrusted\"")
    skill_override = _skill_config_override(user_config, project)
    if skill_override is not None:
        overrides.append(skill_override)
    return codex_home, tuple(overrides)


def _host_command(
    host: str,
    model: str | None,
    bundle_root: Path,
    prompt: str,
    codex_overrides: tuple[str, ...] = (),
) -> tuple[str, ...]:
    command = list(HOST_COMMANDS[host])
    if host == "codex":
        for override in codex_overrides:
            command.extend(("--config", override))
        command.extend(("--config", "project_doc_max_bytes=0"))
        command.extend(
            (
                "--config",
                f"developer_instructions={json.dumps(prompt, ensure_ascii=False)}",
            )
        )
    elif host == "claude":
        command.extend(
            (
                "--setting-sources",
                "user",
                "--settings",
                str(bundle_root / "claude-settings.json"),
                "--plugin-dir",
                str(bundle_root / "plugin"),
                "--append-system-prompt-file",
                str(bundle_root / "system-prompt.md"),
            )
        )
    if model:
        command.extend(("--model", model))
    return tuple(command)


def prepare_injection(
    project: ProjectConfig,
    host: str,
    role: str,
    model: str | None = None,
    *,
    build_root: Path | None = None,
    state_root: Path | None = None,
    source_codex_home: Path | None = None,
    task: str | None = None,
    responsibility: str = "owner",
) -> InjectionLaunch:
    if host not in HOST_COMMANDS:
        raise PolicyError(f"지원하지 않는 inject host입니다: {host}")
    if responsibility not in ARTIFACT_RESPONSIBILITIES:
        raise PolicyError(f"지원하지 않는 산출물 책임입니다: {responsibility}")
    if task is not None and re.fullmatch(r"task/[a-z0-9]+(?:-[a-z0-9]+)*", task) is None:
        raise PolicyError("--task는 task/<ascii-kebab-summary> 형식이어야 합니다.")
    try:
        role_profile(role)
    except ValueError as error:
        raise PolicyError(str(error)) from error
    if not project.path.is_dir():
        raise PolicyError(f"대상 프로젝트를 찾을 수 없습니다: {project.path}")

    rendered = _role_selected_rendered(render_project(project), host, role)
    digest = _bundle_digest(rendered, host, role, project.path)
    selected_build_root = (build_root or BUILD_ROOT).resolve()
    bundle_root = selected_build_root / project.id / f"{host}-{role}-{digest[:16]}"
    files = _render_bundle_files(project, host, role, rendered, bundle_root)
    _install_bundle(bundle_root, project, host, role, digest, files)

    selected_state_root = (state_root or STATE_ROOT).resolve()
    selected_source_home = (
        source_codex_home
        or Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    ).resolve()
    codex_overrides: tuple[str, ...] = ()
    environment = {
        INJECT_MODE_ENV: "inject",
        INJECT_PROJECT_ENV: project.id,
        INJECT_PROJECT_PATH_ENV: str(project.path),
        INJECT_BUNDLE_ROOT_ENV: str(bundle_root / "policy"),
        INJECT_ROLE_ENV: role,
        ARTIFACT_RESPONSIBILITY_ENV: responsibility,
    }
    if task is not None:
        environment[INJECT_TASK_ENV] = task
    if host == "codex":
        codex_home, codex_overrides = _prepare_codex_home(
            project,
            rendered,
            bundle_root,
            selected_state_root,
            selected_source_home,
        )
        environment["CODEX_HOME"] = str(codex_home)
    elif host == "opencode":
        environment["OPENCODE_CONFIG_DIR"] = str(bundle_root / "opencode-home")
        environment["OPENCODE_DISABLE_PROJECT_CONFIG"] = "1"
        environment["OPENCODE_DISABLE_EXTERNAL_SKILLS"] = "1"

    prompt_path = bundle_root / "system-prompt.md"
    prompt = prompt_path.read_text(encoding="utf-8")
    command = _host_command(host, model, bundle_root, prompt, codex_overrides)
    return InjectionLaunch(
        project=project,
        host=host,
        role=role,
        bundle_root=bundle_root,
        system_prompt=prompt_path,
        command=command,
        environment=environment,
    )
