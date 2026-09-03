"""주입 방식 세션을 위한 호스트 번들을 중앙 저장소 안에 생성한다.

대상 프로젝트에 파일을 배포하지 않고, 호스트가 실행 인자로 읽어갈 산출물만 만든다.
Claude Code 는 플러그인 디렉터리와 시스템 프롬프트 파일을, Codex 는 전용 홈 디렉터리를 사용한다.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
BUILD = ROOT / "build"
# 호스트가 세션 이력, 메모리, 큐를 쌓는 위치다. 재생성 가능한 build/ 와 분리해 두어
# build 를 지우는 일상적인 조작으로 이력이 사라지지 않게 한다.
STATE = ROOT / "state"

PROJECT_SKILLS_PREFIX = ".agents/skills"
CODEX_AUTH = Path.home() / ".codex/auth.json"
CODEX_USER_CONFIG = Path.home() / ".codex/config.toml"

# 주입 모드의 SessionStart 는 배포 정합성 대신 현재 브랜치 컨텍스트를 공급한다.
INJECT_EVENTS: tuple[str, ...] = ("SessionStart", "PreToolUse", "Stop")


def _write(target: Path, payload: bytes, mode: int) -> None:
    """내용이 같으면 건드리지 않고, 다르면 원자적으로 교체한다.

    실행 중인 세션이 같은 경로의 훅과 스킬을 계속 읽으므로 파일이 잠시라도 사라지면
    그 세션의 훅 호출이 실패한다. 삭제 후 재작성 대신 임시 파일 교체를 사용한다.
    """

    if target.is_file() and target.read_bytes() == payload:
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.build.tmp")
    _ = temporary.write_bytes(payload)
    temporary.chmod(mode)
    os.replace(temporary, target)


def _prune(root: Path, keep: set[Path]) -> None:
    """중앙이 더 이상 생성하지 않는 파일만 제거한다."""

    if not root.is_dir():
        return
    for path in sorted(root.rglob("*"), reverse=True):
        if path.is_file() and path not in keep:
            path.unlink()
        elif path.is_dir() and not any(path.iterdir()):
            path.rmdir()


def _skills_root(bundle: Path) -> Path:
    return bundle / "plugin/skills"


def _rewrite_skill_paths(text: str, skills_root: Path) -> str:
    """프로젝트 상대 경로로 적힌 스킬 참조를 번들 절대 경로로 바꾼다."""

    return text.replace(PROJECT_SKILLS_PREFIX, str(skills_root))


def _copy_tree(source: Path, destination: Path, transform, written: set[Path]) -> None:
    for path in sorted(source.rglob("*")):
        if not path.is_file() or path.name == ".DS_Store" or "__pycache__" in path.parts:
            continue
        target = destination / path.relative_to(source)
        if path.suffix in {".md", ".toml", ".json", ".py", ".js"}:
            payload = transform(path.read_text(encoding="utf-8")).encode("utf-8")
        else:
            payload = path.read_bytes()
        _write(target, payload, path.stat().st_mode & 0o777)
        written.add(target)


def _toml_top_level_keys(text: str) -> set[str]:
    """최상위 키와 테이블 이름을 모은다. 중복 정의로 인한 파싱 실패를 피하기 위한 최소 판별이다."""

    keys: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("["):
            keys.add(stripped.strip("[]").split(".", 1)[0].strip('"'))
        elif "=" in stripped:
            keys.add(stripped.split("=", 1)[0].strip())
    return keys


def _hook_trust_blocks(text: str) -> dict[str, str]:
    """`[hooks.state.*]` 블록을 키별로 모은다. 훅 신뢰 승인이 이 형식으로 기록된다."""

    blocks: dict[str, str] = {}
    key: str | None = None
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("["):
            if key is not None:
                blocks[key] = "\n".join(lines)
            key = stripped.strip("[]") if stripped.startswith("[hooks.state.") else None
            lines = [line] if key is not None else []
            continue
        if key is not None:
            lines.append(line)
    if key is not None:
        blocks[key] = "\n".join(lines)
    return blocks


def preserved_hook_trust(existing: Path, generated: str) -> str:
    """이전 번들에서 승인된 훅 신뢰 기록을 새 설정에 이어 붙인다.

    Codex 는 훅 승인 결과를 `config.toml` 에 적는다. 재빌드가 설정을 덮어쓰면 사용자가
    매 실행마다 다시 승인해야 하므로, 생성본에 없는 신뢰 블록만 보존한다.
    """

    if not existing.is_file():
        return generated
    previous = _hook_trust_blocks(existing.read_text(encoding="utf-8"))
    current = set(_hook_trust_blocks(generated))
    carried = [block for key, block in previous.items() if key not in current]
    if not carried:
        return generated
    return (
        generated.rstrip("\n")
        + "\n\n# 이전 세션에서 승인된 훅 신뢰 기록이다.\n"
        + "\n".join(carried).strip()
        + "\n"
    )


def merged_codex_config(central: str) -> str:
    """사용자의 Codex 설정을 유지한 채 중앙 정책 설정을 덧붙인다.

    `CODEX_HOME` 을 바꾸면 사용자의 모델·플러그인 설정이 함께 가려지므로, 원본을 먼저 싣고
    사용자가 정의하지 않은 중앙 항목만 추가한다. 이미 정의된 키는 사용자 설정을 우선한다.
    """

    if not CODEX_USER_CONFIG.is_file():
        return central
    user = CODEX_USER_CONFIG.read_text(encoding="utf-8")
    existing = _toml_top_level_keys(user)
    kept: list[str] = []
    skipped: list[str] = []
    block: list[str] = []
    block_key: str | None = None

    def flush() -> None:
        if not block:
            return
        if block_key is not None and block_key in existing:
            skipped.append(block_key)
        else:
            kept.extend(block)

    for line in central.splitlines():
        stripped = line.strip()
        if stripped.startswith("["):
            flush()
            block = [line]
            block_key = stripped.strip("[]").split(".", 1)[0].strip('"')
            continue
        if block_key is None and "=" in stripped and not stripped.startswith("#"):
            key = stripped.split("=", 1)[0].strip()
            if key in existing:
                skipped.append(key)
            else:
                kept.append(line)
            continue
        block.append(line) if block_key is not None else kept.append(line)
    flush()

    note = "\n# 아래는 asan-prompt-core 중앙 정책에서 추가된 설정이다.\n"
    addition = "\n".join(part for part in kept if part.strip())
    if skipped:
        note += f"# 사용자 설정이 우선하여 제외된 항목: {', '.join(sorted(set(skipped)))}\n"
    return user.rstrip("\n") + "\n" + note + (addition + "\n" if addition else "")


def build(target: dict[str, object], render) -> Path:
    """대상 프로젝트용 번들을 만들고 번들 루트를 반환한다.

    `render` 는 프로젝트 토큰을 치환하는 호출 가능 객체다.
    """

    bundle = BUILD / str(target["id"])
    bundle.mkdir(parents=True, exist_ok=True)
    # 실행 중인 다른 세션이 같은 번들을 읽고 있을 수 있으므로 통째로 지우지 않는다.
    # 바뀐 파일만 원자적으로 교체하고, 중앙이 더 이상 생성하지 않는 파일만 제거한다.
    written: set[Path] = set()
    skills_root = _skills_root(bundle)

    def transform(text: str) -> str:
        return _rewrite_skill_paths(render(text, target), skills_root)

    plugin = bundle / "plugin"
    _copy_tree(SOURCE / "common/skills", skills_root, transform, written)
    _copy_tree(SOURCE / "hosts/claude/skills", skills_root, transform, written)
    _copy_tree(SOURCE / "hosts/claude/agents", plugin / "agents", transform, written)
    _copy_tree(SOURCE / "common/hooks", plugin / "hooks", transform, written)
    _copy_tree(SOURCE / "hosts/claude/hooks", plugin / "hooks", transform, written)

    manifest = {
        "$schema": "https://anthropic.com/claude-code/plugin.schema.json",
        "name": "asan-prompt-core",
        "version": "0.1.0",
        "description": f"{target.get('name', target['id'])}의 중앙 시스템 프롬프트",
        "skills": ["./skills"],
    }
    manifest_path = plugin / ".claude-plugin/plugin.json"
    _write(manifest_path, (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8"), 0o644)
    written.add(manifest_path)

    hooks = {
        "hooks": {
            event: [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"python3 -I ${{CLAUDE_PLUGIN_ROOT}}/hooks/harness_hook.py {event}",
                            "timeout": 20,
                        }
                    ]
                }
            ]
            for event in INJECT_EVENTS
        }
    }
    hooks_path = plugin / "hooks/hooks.json"
    _write(hooks_path, (json.dumps(hooks, ensure_ascii=False, indent=2) + "\n").encode("utf-8"), 0o644)
    written.add(hooks_path)
    _prune(plugin, written)

    system_prompt = "\n\n".join(
        transform((SOURCE / "common" / name).read_text(encoding="utf-8"))
        for name in ("AGENTS.md", "CLAUDE.md")
    )
    _write(bundle / "system-prompt.md", system_prompt.encode("utf-8"), 0o644)

    codex_home = STATE / str(target["id"]) / "codex-home"
    codex_home.mkdir(parents=True, exist_ok=True)
    _write(
        codex_home / "AGENTS.md",
        transform((SOURCE / "common/AGENTS.md").read_text(encoding="utf-8")).encode("utf-8"),
        0o644,
    )
    codex_written: set[Path] = set()
    _copy_tree(SOURCE / "common/hooks", codex_home / "hooks", transform, codex_written)
    _copy_tree(SOURCE / "hosts/codex/hooks", codex_home / "hooks", transform, codex_written)
    _copy_tree(SOURCE / "hosts/codex/agents", codex_home / "agents", transform, codex_written)
    _prune(codex_home / "hooks", codex_written)
    _prune(codex_home / "agents", codex_written)
    config = SOURCE / "hosts/codex/config.toml"
    if config.is_file():
        destination = codex_home / "config.toml"
        _write(
            destination,
            preserved_hook_trust(
                destination, merged_codex_config(transform(config.read_text(encoding="utf-8")))
            ).encode("utf-8"),
            0o600,
        )
    codex_hooks = {
        "hooks": {
            event: [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"python3 -I {codex_home}/hooks/harness_hook.py {event}",
                            "timeout": 20,
                        }
                    ]
                }
            ]
            for event in INJECT_EVENTS
        }
    }
    _write(
        codex_home / "hooks.json",
        (json.dumps(codex_hooks, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        0o644,
    )
    auth_link = codex_home / "auth.json"
    if CODEX_AUTH.is_file() and not auth_link.exists():
        auth_link.symlink_to(CODEX_AUTH)

    opencode_home = bundle / "opencode-home"
    opencode_written: set[Path] = set()
    agents_root = opencode_home / "agent"
    plugin_root = opencode_home / "plugin"
    _copy_tree(SOURCE / "hosts/opencode/agent", agents_root, transform, opencode_written)
    for source in ("hosts/opencode/plugins", "common/hooks"):
        _copy_tree(SOURCE / source, plugin_root, transform, opencode_written)
    instructions = opencode_home / "AGENTS.md"
    _write(instructions, system_prompt.encode("utf-8"), 0o644)
    opencode_written.add(instructions)
    opencode_config = opencode_home / "opencode.json"
    _write(
        opencode_config,
        (
            json.dumps(
                {
                    "$schema": "https://opencode.ai/config.json",
                    "instructions": [str(instructions)],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n"
        ).encode("utf-8"),
        0o644,
    )
    opencode_written.add(opencode_config)
    _prune(opencode_home, opencode_written)

    return bundle
