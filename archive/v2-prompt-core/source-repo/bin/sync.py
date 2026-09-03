#!/usr/bin/env python3
"""중앙 에이전트 정책을 대상 프로젝트로 배포하고 정합성을 검사한다."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bundles

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
MANIFEST_PATH = ROOT / "MANIFEST.json"
TARGETS_PATH = ROOT / "targets.json"

HOST_DIRECTORIES: dict[str, str] = {
    "codex": ".codex",
    "claude": ".claude",
    "opencode": ".opencode",
}

HOOK_DESTINATIONS: dict[str, str] = {
    "codex": ".codex/hooks",
    "claude": ".claude/hooks",
    "opencode": ".opencode/plugins",
}

HOST_COMMANDS: dict[str, str] = {
    "codex": "codex",
    "claude": "claude",
    "opencode": "opencode",
}

COMMON_MAP: tuple[tuple[str, str], ...] = (
    ("common/AGENTS.md", "AGENTS.md"),
    ("common/CLAUDE.md", "CLAUDE.md"),
    ("common/skills", ".agents/skills"),
    ("common/roles", ".harness/roles"),
)

BANNER_TEMPLATE = (
    "<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.\n"
    "     원본: {origin}\n"
    "     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤"
    " `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->\n"
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_targets() -> list[dict[str, object]]:
    document = json.loads(TARGETS_PATH.read_text(encoding="utf-8"))
    targets = document.get("targets")
    if not isinstance(targets, list):
        raise SystemExit("targets.json의 targets는 배열이어야 합니다.")
    return [dict(target) for target in targets if isinstance(target, dict)]


def select_targets(selector: str | None = None, path: str | None = None) -> list[dict[str, object]]:
    targets = load_targets()
    if path is not None:
        requested = Path(path).expanduser().resolve()
        chosen = [target for target in targets if Path(str(target["path"])).expanduser().resolve() == requested]
        if not chosen:
            raise SystemExit(f"등록되지 않은 프로젝트 경로입니다: {requested}")
        return chosen
    if selector == "all":
        return targets
    chosen = [target for target in targets if target.get("id") == selector]
    if not chosen:
        known = ", ".join(str(target.get("id")) for target in targets)
        raise SystemExit(f"알 수 없는 대상입니다: {selector} (등록된 대상: {known})")
    return chosen


def source_files(relative: str) -> list[tuple[Path, str]]:
    origin = SOURCE / relative
    if origin.is_file():
        return [(origin, relative)]
    if not origin.is_dir():
        return []
    return [
        (path, path.relative_to(SOURCE).as_posix())
        for path in sorted(origin.rglob("*"))
        if path.is_file() and path.name != ".DS_Store" and "__pycache__" not in path.parts
    ]


def plan_for(target: dict[str, object]) -> list[tuple[Path, str, str]]:
    entries: list[tuple[Path, str, str]] = []
    hosts = [str(host) for host in target.get("hosts", [])]

    for source_relative, project_relative in COMMON_MAP:
        for path, origin in source_files(source_relative):
            suffix = origin[len(source_relative):].lstrip("/")
            destination = f"{project_relative}/{suffix}" if suffix else project_relative
            entries.append((path, origin, destination))

    for host in hosts:
        if host not in HOST_DIRECTORIES:
            raise SystemExit(f"지원하지 않는 호스트입니다: {host}")
        host_root = f"hosts/{host}"
        for path, origin in source_files(host_root):
            suffix = origin[len(host_root):].lstrip("/")
            entries.append((path, origin, f"{HOST_DIRECTORIES[host]}/{suffix}"))
        for path, origin in source_files("common/hooks"):
            suffix = origin[len("common/hooks"):].lstrip("/")
            entries.append((path, origin, f"{HOOK_DESTINATIONS[host]}/{suffix}"))

    destinations = [destination for _, _, destination in entries]
    duplicates = sorted({destination for destination in destinations if destinations.count(destination) > 1})
    if duplicates:
        raise SystemExit(f"중복 배포 경로가 있습니다: {', '.join(duplicates)}")
    return entries


def project_commands(target: dict[str, object]) -> str:
    commands = target.get("commands")
    if not isinstance(commands, list) or not commands:
        return "- 실행 명령은 대상 프로젝트의 `package.json` scripts를 확인한다."
    lines: list[str] = []
    for item in commands:
        if not isinstance(item, dict):
            continue
        label = str(item.get("label", "실행"))
        command = str(item.get("command", "")).strip()
        if command:
            lines.append(f"- {label}: `{command}`")
    return "\n".join(lines)


def render_tokens(text: str, target: dict[str, object]) -> str:
    rendered = text.replace("{{PROJECT_NAME}}", str(target.get("name", target.get("id", "project"))))
    rendered = rendered.replace("{{PROJECT_COMMANDS}}", project_commands(target))
    base_branch = str(target.get("base_branch", "")).strip()
    if not base_branch:
        raise SystemExit(f"{target.get('id', 'target')}의 base_branch가 없습니다.")
    rendered = rendered.replace("{{BASE_BRANCH}}", base_branch)
    if "{{PROJECT_" in rendered or "{{BASE_BRANCH}}" in rendered:
        raise SystemExit("해결되지 않은 프로젝트 템플릿 토큰이 있습니다.")
    return rendered


def rendered_bytes(path: Path, origin: str, target: dict[str, object]) -> bytes:
    data = path.read_bytes()
    try:
        text = render_tokens(data.decode("utf-8"), target)
    except UnicodeDecodeError:
        return data
    if path.suffix != ".md" or path.name.endswith(".template.md"):
        return text.encode("utf-8")
    banner = BANNER_TEMPLATE.format(origin=f"source/{origin}")
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            boundary = end + len("\n---\n")
            return (text[:boundary] + "\n" + banner + "\n" + text[boundary:].lstrip("\n")).encode("utf-8")
    return (banner + "\n" + text).encode("utf-8")


def expected_files(target: dict[str, object]) -> dict[str, tuple[str, bytes]]:
    return {
        destination: (origin, rendered_bytes(path, origin, target))
        for path, origin, destination in plan_for(target)
    }


def read_manifest() -> dict[str, dict[str, object]]:
    if not MANIFEST_PATH.is_file():
        return {"targets": {}}
    document = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    targets = document.get("targets", {})
    return {"targets": targets if isinstance(targets, dict) else {}}


def write_manifest(manifest: dict[str, dict[str, object]]) -> None:
    payload = {"schema_version": 1, "targets": manifest["targets"]}
    temporary = MANIFEST_PATH.with_name(f".{MANIFEST_PATH.name}.sync.tmp")
    _ = temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    shutil.move(str(temporary), str(MANIFEST_PATH))


def recorded_files(manifest: dict[str, dict[str, object]], target_id: str) -> dict[str, str]:
    record = manifest["targets"].get(target_id)
    if not isinstance(record, dict):
        return {}
    files = record.get("files")
    return {str(path): str(value) for path, value in files.items()} if isinstance(files, dict) else {}


def target_changes(target: dict[str, object], manifest: dict[str, dict[str, object]]) -> dict[str, list[str]]:
    target_id = str(target["id"])
    root = Path(str(target["path"])).expanduser().resolve()
    expected = expected_files(target)
    recorded = recorded_files(manifest, target_id)
    created: list[str] = []
    updated: list[str] = []
    unchanged: list[str] = []
    for destination, (_, payload) in expected.items():
        output = root / destination
        if not output.is_file():
            created.append(destination)
        elif output.read_bytes() != payload:
            updated.append(destination)
        else:
            unchanged.append(destination)
    retired = sorted(path for path in set(recorded) - set(expected) if (root / path).is_file())
    manifest_stale = sorted(
        destination
        for destination, (_, payload) in expected.items()
        if recorded.get(destination) != digest(payload)
    )
    return {
        "created": sorted(created),
        "updated": sorted(updated),
        "retired": retired,
        "unchanged": sorted(unchanged),
        "manifest_stale": manifest_stale,
    }


def print_diff(target: dict[str, object], manifest: dict[str, dict[str, object]]) -> bool:
    target_id = str(target["id"])
    root = Path(str(target["path"])).expanduser().resolve()
    expected = expected_files(target)
    changes = target_changes(target, manifest)
    changed = bool(changes["created"] or changes["updated"] or changes["retired"] or changes["manifest_stale"])
    print(
        f"[{target_id}] 생성 {len(changes['created'])}, 갱신 {len(changes['updated'])}, "
        f"회수 {len(changes['retired'])}, 동일 {len(changes['unchanged'])}"
    )
    for destination in changes["created"] + changes["updated"]:
        old = (root / destination).read_text(encoding="utf-8", errors="replace").splitlines(keepends=True) if (root / destination).is_file() else []
        new = expected[destination][1].decode("utf-8", errors="replace").splitlines(keepends=True)
        sys.stdout.writelines(
            difflib.unified_diff(old, new, fromfile=f"{target_id}/{destination}", tofile=f"central/{destination}")
        )
    for destination in changes["retired"]:
        print(f"[{target_id}] 중앙 관리에서 회수: {destination}")
    if changes["manifest_stale"] and not (changes["created"] or changes["updated"] or changes["retired"]):
        print(f"[{target_id}] 파일은 최신이지만 MANIFEST 갱신이 필요합니다.")
    return changed


def deploy(selector: str, dry_run: bool = False) -> int:
    manifest = read_manifest()
    targets = select_targets(selector)
    if dry_run:
        for target in targets:
            _ = print_diff(target, manifest)
        return 0

    for target in targets:
        target_id = str(target["id"])
        root = Path(str(target["path"])).expanduser().resolve()
        if not root.is_dir():
            print(f"[{target_id}] 경로를 찾을 수 없습니다: {root}", file=sys.stderr)
            return 1
        expected = expected_files(target)
        previous = recorded_files(manifest, target_id)
        for destination, (_, payload) in expected.items():
            output = root / destination
            output.parent.mkdir(parents=True, exist_ok=True)
            temporary = output.with_name(f".{output.name}.sync.tmp")
            _ = temporary.write_bytes(payload)
            shutil.move(str(temporary), str(output))
        retired: list[str] = []
        for destination in sorted(set(previous) - set(expected)):
            output = (root / destination).resolve()
            try:
                _ = output.relative_to(root)
            except ValueError:
                raise SystemExit(f"프로젝트 밖의 회수 경로를 거부합니다: {output}")
            if output.is_file():
                output.unlink()
                retired.append(destination)
        manifest["targets"][target_id] = {
            "files": {destination: digest(payload) for destination, (_, payload) in expected.items()}
        }
        print(f"[{target_id}] {len(expected)}개 파일 배포, {len(retired)}개 이전 파일 회수")
    write_manifest(manifest)
    return 0


def check(selector: str | None = None, path: str | None = None) -> int:
    manifest = read_manifest()
    status = 0
    for target in select_targets(selector, path):
        target_id = str(target["id"])
        changes = target_changes(target, manifest)
        if not (changes["created"] or changes["updated"] or changes["retired"] or changes["manifest_stale"]):
            print(f"[{target_id}] 중앙 원본과 정합 ({len(changes['unchanged'])}개 파일)")
            continue
        status = 1
        for destination in changes["created"]:
            print(f"[{target_id}] 누락됨: {destination}")
        for destination in changes["updated"]:
            print(f"[{target_id}] 중앙 원본과 다름: {destination}")
        for destination in changes["retired"]:
            print(f"[{target_id}] 중앙 관리에서 회수 예정: {destination}")
        if changes["manifest_stale"]:
            print(f"[{target_id}] MANIFEST 갱신 필요: {len(changes['manifest_stale'])}개")
    if status != 0:
        print("\n중앙 저장소에서 `python3 bin/sync.py deploy --target all`을 실행한 뒤 세션을 재시작하세요.")
    return status


LOGS = ROOT / "logs"
PROJECT_SESSIONS = ".codex/logs/sessions"


def collect(selector: str, quiet: bool = False) -> int:
    """대상 프로젝트의 세션 산출물을 중앙 `logs/` 로 단방향 복사한다.

    프로젝트가 정본이고 중앙 사본은 조회 전용 아카이브다. 중앙에서 프로젝트로 되돌려
    쓰지 않으며, 프로젝트에서 사라진 기록도 중앙에서 지우지 않는다.
    """

    copied = 0
    for target in select_targets(selector):
        target_id = str(target["id"])
        source = Path(str(target["path"])).expanduser().resolve() / PROJECT_SESSIONS
        if not source.is_dir():
            continue
        destination = LOGS / target_id / "sessions"
        for path in sorted(source.rglob("*")):
            if not path.is_file() or path.name == ".DS_Store":
                continue
            mirror = destination / path.relative_to(source)
            payload = path.read_bytes()
            if mirror.is_file() and mirror.read_bytes() == payload:
                continue
            mirror.parent.mkdir(parents=True, exist_ok=True)
            temporary = mirror.with_name(f".{mirror.name}.collect.tmp")
            _ = temporary.write_bytes(payload)
            os.replace(temporary, mirror)
            copied += 1
        if not quiet:
            sessions = len([entry for entry in destination.iterdir() if entry.is_dir()])
            print(f"[{target_id}] 세션 {sessions}개 보관, 이번에 갱신 {copied}개 파일")
            copied = 0
    return 0


def show_status() -> int:
    manifest = read_manifest()
    status = 0
    for target in load_targets():
        changes = target_changes(target, manifest)
        pending = len(changes["created"]) + len(changes["updated"]) + len(changes["retired"])
        label = "정합" if pending == 0 and not changes["manifest_stale"] else "동기화 필요"
        print(f"{str(target['id']):10s} {label} / 원본 {len(expected_files(target))}개 / 변경 {pending}개")
        if label != "정합":
            status = 1
    return status


INJECT_SUPPORTED: tuple[str, ...] = ("claude", "codex", "opencode")


def inject_command(bundle: Path, host: str) -> tuple[list[str], dict[str, str]]:
    """대상 프로젝트에 파일을 두지 않고 중앙 정책을 주입하는 실행 인자를 만든다."""

    if host == "claude":
        prompt = (bundle / "system-prompt.md").read_text(encoding="utf-8")
        return (
            [
                "claude",
                "--setting-sources",
                "user",
                "--plugin-dir",
                str(bundle / "plugin"),
                "--add-dir",
                str(ROOT),
                "--append-system-prompt",
                prompt,
            ],
            {},
        )
    if host == "codex":
        home = bundles.STATE / bundle.name / "codex-home"
        return (["codex"], {"CODEX_HOME": str(home)})
    if host == "opencode":
        return (
            ["opencode"],
            {
                "OPENCODE_CONFIG_DIR": str(bundle / "opencode-home"),
                "OPENCODE_DISABLE_PROJECT_CONFIG": "1",
            },
        )
    raise SystemExit(
        f"주입 방식을 지원하지 않는 호스트입니다: {host}\n"
        f"  지원: {', '.join(INJECT_SUPPORTED)}\n"
        "  다른 호스트는 `deploy` 후 호스트를 직접 실행하세요."
    )


def launch(
    target_id: str,
    host: str,
    model: str | None,
    extra: list[str],
    dry_run: bool,
    mode: str = "inject",
) -> int:
    target = select_targets(target_id)[0]
    hosts = [str(item) for item in target.get("hosts", [])]
    if host not in hosts or host not in HOST_COMMANDS:
        raise SystemExit(f"{target_id}에서 지원하지 않는 호스트입니다: {host}")
    root = Path(str(target["path"])).expanduser().resolve()
    environment = dict(os.environ)

    if mode == "deploy":
        result = deploy(target_id, dry_run=dry_run)
        if result != 0 or dry_run:
            return result
        command = [HOST_COMMANDS[host]]
    else:
        _ = collect(target_id, quiet=True)
        bundle = bundles.build(target, render_tokens)
        command, overrides = inject_command(bundle, host)
        environment.update(overrides)
        if dry_run:
            print(f"[{target_id}] 번들: {bundle}")
            print(f"[{target_id}] 실행: {' '.join(command[:6])} ...")
            for key, value in overrides.items():
                print(f"[{target_id}] 환경: {key}={value}")
            return 0

    if model:
        command.extend(("--model", model))
    command.extend(argument for argument in extra if argument != "--")
    os.chdir(root)
    os.execvpe(command[0], command, environment)
    return 1


def add_target_arguments(parser: argparse.ArgumentParser, allow_path: bool = False) -> None:
    _ = parser.add_argument("--target", default=None if allow_path else "all")
    if allow_path:
        _ = parser.add_argument("--path")


def main() -> None:
    parser = argparse.ArgumentParser(description="중앙 에이전트 정책 동기화")
    subparsers = parser.add_subparsers(dest="command", required=True)

    deploy_parser = subparsers.add_parser("deploy", help="중앙 원본을 대상 프로젝트로 배포")
    add_target_arguments(deploy_parser)
    _ = deploy_parser.add_argument("--dry-run", action="store_true")

    check_parser = subparsers.add_parser("check", help="현재 중앙 원본과 프로젝트 정합성 검사")
    add_target_arguments(check_parser, allow_path=True)

    _ = subparsers.add_parser("status", help="대상별 배포 상태 확인")

    collect_parser = subparsers.add_parser("collect", help="프로젝트 세션 산출물을 중앙으로 복사")
    _ = collect_parser.add_argument("--target", default="all")

    start_parser = subparsers.add_parser("start", help="동기화 후 선택한 호스트로 새 세션 시작")
    _ = start_parser.add_argument("--target", required=True)
    _ = start_parser.add_argument("--host", required=True, choices=tuple(HOST_COMMANDS))
    _ = start_parser.add_argument("--model")
    _ = start_parser.add_argument("--dry-run", action="store_true")
    _ = start_parser.add_argument("--mode", choices=("inject", "deploy"), default="inject")
    _ = start_parser.add_argument("extra", nargs=argparse.REMAINDER)

    arguments = parser.parse_args()
    if arguments.command == "deploy":
        raise SystemExit(deploy(arguments.target, arguments.dry_run))
    if arguments.command == "collect":
        raise SystemExit(collect(arguments.target))
    if arguments.command == "check":
        if arguments.target is None and arguments.path is None:
            parser.error("check에는 --target 또는 --path가 필요합니다.")
        raise SystemExit(check(arguments.target, arguments.path))
    if arguments.command == "start":
        raise SystemExit(
            launch(
                arguments.target,
                arguments.host,
                arguments.model,
                arguments.extra,
                arguments.dry_run,
                arguments.mode,
            )
        )
    raise SystemExit(show_status())


if __name__ == "__main__":
    main()
