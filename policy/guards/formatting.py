"""성공한 코드 쓰기를 기록하고 검증 전에 실제 Prettier로 포맷한다.

Node는 결과만 계산한다. events/Git 잠금 밖에서 계산하고, 다시 잠근 뒤
내용·설정·작성자·진행 중인 쓰기를 확인하여 원본 파일에 반영한다.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from types import ModuleType

_path = Path(__file__).with_name("runtime_loader.py")
_loader = ModuleType("formatting_loader")
_loader.__file__ = str(_path)
exec(compile(_path.read_bytes(), str(_path), "exec"), _loader.__dict__)
config = _loader.load("runtime_config")
paths = _loader.load("tool_paths")
protocol = _loader.load("event_protocol")
git, state = config.branch_guard, config.runtime_state
SETTINGS = git.RUNTIME_CONTRACT.get("formatting", {})
EXCLUDED = {".git", ".agent-policy", ".codex", ".claude", ".opencode", "node_modules", "dist", "build"}
CONFIG_NAMES = ("package.json", "package.yaml", ".editorconfig", ".prettierrc",
    *(".prettierrc." + suffix for suffix in ("json", "json5", "yml", "yaml", "toml", "js", "cjs", "mjs", "ts", "cts", "mts")),
    *("prettier.config." + suffix for suffix in ("js", "cjs", "mjs", "ts", "cts", "mts")))


class FormattingRequired(RuntimeError):
    def __init__(self, worktree: Path):
        self.worktree = worktree
        super().__init__("검증 전에 Prettier 실행이 필요합니다.")


def enabled() -> bool:
    return git.SHARED_GIT_ACCESS and os.environ.get("ASAN_FORMATTER") == "prettier-v1"


def directory(root: Path) -> Path:
    return state.repository_state(git.git_common_directory(root) or root) / "formatting/v1"


def session_path(root: Path, event: dict, host: str) -> Path:
    value = state.session_path(git.git_common_directory(root) or root, host, paths.event_session_id(event), "formatting", create=False)
    if value is None:
        raise RuntimeError("포맷 기록에 실제 session ID가 필요합니다.")
    return value


def call_path(root: Path, event: dict, host: str) -> Path:
    return directory(root) / "calls" / (state.digest(state.owner_id(host, paths.event_session_id(event)) + ":" + protocol.tool_call_id(event)) + ".json")


def writer_path(root: Path, path: Path) -> Path:
    return directory(root) / "writers" / (state.digest(str(path)) + ".json")


def safe_path(root: Path, worktree: Path, raw: str) -> Path:
    if not git.same_git_repository(root, worktree):
        raise RuntimeError(f"다른 프로젝트의 포맷 대상입니다: {worktree}")
    path = Path(raw)
    if not path.is_absolute() or not path.is_relative_to(worktree) or any(part in EXCLUDED for part in path.relative_to(worktree).parts):
        raise RuntimeError(f"포맷할 수 없는 경로입니다: {path}")
    if path.is_symlink() or any(parent.is_symlink() for parent in path.parents if parent.is_relative_to(worktree)):
        raise RuntimeError(f"심볼릭 링크는 포맷하지 않습니다: {path}")
    if path.resolve() != path:
        raise RuntimeError(f"포맷 대상의 실제 경로가 다릅니다: {path}")
    return path


def file_hash(path: Path) -> str | None:
    if not path.exists():
        return None
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"일반 코드 파일이 아닙니다: {path}")
    if path.stat().st_size > 2 * 1024 * 1024:
        raise RuntimeError(f"자동 포맷 파일 크기 한도를 초과했습니다: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def configuration_hash(worktree: Path, path: Path) -> str:
    files = {worktree / ".prettierignore", worktree / ".gitignore"}
    for parent in (path.parent, *path.parent.parents):
        if not parent.is_relative_to(worktree):
            break
        files.update(parent / name for name in CONFIG_NAMES)
    values = []
    for candidate in sorted(files):
        if candidate.is_symlink():
            raise RuntimeError(f"심볼릭 링크 설정은 포맷에 사용하지 않습니다: {candidate}")
        values.append((str(candidate), file_hash(candidate)))
    return state.digest(json.dumps(values))


def record_before(root: Path, event: dict, host: str, contexts: list) -> None:
    if not enabled():
        return
    selected = []
    for worktree, relative in contexts:
        if Path(relative).suffix.casefold() not in SETTINGS["extensions"] or any(part in EXCLUDED for part in Path(relative).parts):
            continue
        path = safe_path(root, worktree.resolve(), str(worktree / relative))
        token = uuid.uuid4().hex
        value = {"path": str(path), "worktree": str(worktree.resolve()), "token": token,
                 "owner": state.owner_id(host, paths.event_session_id(event)), "call": protocol.tool_call_id(event),
                 "before_sha256": file_hash(path), "previous_writer": state.read(writer_path(root, path))}
        state.write(writer_path(root, path), {key: value[key] for key in ("path", "worktree", "token", "owner", "call")})
        selected.append(value)
    if selected:
        state.write(call_path(root, event, host), {"files": selected})


def record_after(root: Path, event: dict, host: str) -> None:
    if not enabled() or protocol.tool_outcome(event) is None:
        return
    pending = call_path(root, event, host)
    source = state.read(pending)
    if not source:
        return
    record_path = session_path(root, event, host)
    record = state.read(record_path)
    files = record.setdefault("files", {})
    for item in source["files"]:
        path = safe_path(root, Path(item["worktree"]), item["path"])
        current = file_hash(path)
        if protocol.tool_outcome(event) is True:
            if current is None:
                files.pop(str(path), None)
            else:
                files[str(path)] = {**item, "sha256": current, "status": "pending"}
        elif current != item.get("before_sha256"):
            files[str(path)] = {**item, "sha256": current, "status": "unconfirmed"}
        elif state.read(writer_path(root, path)).get("token") == item["token"]:
            if item.get("previous_writer"):
                state.write(writer_path(root, path), item["previous_writer"])
            else:
                writer_path(root, path).unlink(missing_ok=True)
    state.write(record_path, record)
    pending.unlink(missing_ok=True)


def pending_files(root: Path, event: dict, host: str, worktree: Path | None = None) -> list[dict]:
    if not enabled():
        return []
    record = state.read(session_path(root, event, host))
    result = []
    revisions = {}
    for item in record.get("files", {}).values():
        location = Path(item["worktree"])
        if worktree and location != worktree.resolve():
            continue
        if not location.exists() and not location.is_symlink():
            continue  # 정리된 worktree의 과거 기록은 다음 작업을 구속하지 않는다.
        path = safe_path(root, location, item["path"])
        if item.get("status") in {"formatted", "ignored"} and item.get("head"):
            if location not in revisions:
                revisions[location] = git.head(location)
            if item["head"] != revisions[location]:
                continue  # 완료한 커밋·다른 branch의 코드를 이전 세션 기록으로 재포맷하지 않는다.
        current = file_hash(path)
        if current is None:
            continue  # 삭제한 파일을 다시 만들지 않는다.
        if (item.get("status") not in {"formatted", "ignored"} or current != item["sha256"]
                or item.get("config_sha256") != configuration_hash(location, path)):
            result.append(item)
    return result


def command(event: dict, host: str, action: str = "apply") -> str:
    return shlex.join([sys.executable, "-I", str(Path(__file__).resolve()), action,
                      "--host", host, "--session", paths.event_session_id(event)])


def require_before_validation(root: Path, event: dict, host: str, command_text: str, cwd: Path) -> None:
    if not enabled():
        return
    contexts = git.shell_command_contexts(command_text, cwd)
    allowed = [shlex.split(value) for value in git.RUNTIME_CONTRACT["git"]["validation_commands"]]
    for location, words in contexts or ():
        if any(list(words[:len(expected)]) == expected for expected in allowed):
            target = paths.git_top_level(location)
            if target and unconfirmed_calls(root, event, host, target):
                raise RuntimeError("결과 미확인 코드 쓰기를 확인한 뒤 포맷·검증하세요.")
            if target and pending_files(root, event, host, target):
                raise FormattingRequired(target)


def invocation(value: str, event: dict, host: str, cwd: Path) -> tuple[Path, str] | None:
    if "formatting.py" not in value:
        return None
    try:
        lexer = shlex.shlex(value.strip(), posix=True, punctuation_chars=";&|()<>\n")
        lexer.whitespace = " \t\r"
        lexer.whitespace_split = True
        lexer.commenters = ""
        words = list(lexer)
    except ValueError:
        return None
    if words and words[0] == "cd":
        prefix_length = 3 if len(words) > 1 and words[1] == "--" else 2
        formatter_words = words[prefix_length + 1:]
        if not formatter_words or not Path(formatter_words[0]).name.startswith("python"):
            return None
        contexts = git.shell_command_contexts(value, cwd)
        if (words[prefix_length] != "&&" or contexts is None or len(contexts) != 2
                or contexts[0][1] != tuple(words[:prefix_length])
                or contexts[1][1] != tuple(formatter_words)):
            raise RuntimeError("포맷 실행은 리터럴 cd 경로 뒤에 &&로 공통 포맷 명령 하나만 연결하세요.")
        cwd, words = contexts[1][0], formatter_words
    if not words or not Path(words[0]).name.startswith("python"):
        return None
    expected = [shlex.split(command(event, host, action))[3:] for action in ("apply", "check")]
    if os.environ.get("ASAN_AGENT_POLICY_ASSIGNMENT") and os.environ.get("ASAN_AGENT_POLICY_HOST") == host:
        expected.extend([["apply"], ["check"]])
    if (len(words) < 4 or words[1] != "-I" or Path(words[2]).resolve() != Path(__file__).resolve()
            or words[3:] not in expected):
        raise RuntimeError("현재 세션의 공통 포맷 실행기를 사용하세요: " + command(event, host))
    return cwd, words[3]


def require_for_trigger(root: Path, event: dict, host: str, action: str, cwd: Path) -> None:
    target = paths.git_top_level(cwd)
    if target and action == "apply" and check(root, event, host, target):
        raise FormattingRequired(target)


def unconfirmed_calls(root: Path, event: dict, host: str, worktree: Path | None = None) -> list[str]:
    if not enabled():
        return []
    owner = state.owner_id(host, paths.event_session_id(event))
    confirmed = state.read(session_path(root, event, host)).get("files", {})
    relations = _loader.load("branch_relations")
    active = {path.stem for path in (relations.directory(root) / "writes").glob("*.json")}
    unresolved = []
    for path in (directory(root) / "calls").glob("*.json"):
        for item in state.read(path).get("files", []):
            if item.get("owner") != owner or (worktree and item["worktree"] != str(worktree.resolve())):
                continue
            identifier = relations.digest([host, paths.event_session_id(event), item["call"], item["worktree"]])
            latest = confirmed.get(item["path"], {})
            # write-recovery로 이전 프로세스 종료를 확인하고 정상 수정 도구로
            # 마무리했을 때만 이전 미확인 기록을 대체한다. 단순 재시도로 우회하지 않는다.
            if (identifier not in active and latest.get("status") in {"pending", "formatted", "ignored"}
                    and latest.get("token") != item["token"]
                    and state.read(writer_path(root, Path(item["path"]))).get("token") == latest.get("token")):
                continue
            unresolved.append(item["path"])
    return unresolved


def check(root: Path, event: dict, host: str, worktree: Path | None = None) -> str | None:
    uncertain = unconfirmed_calls(root, event, host, worktree)
    if uncertain:
        return "코드 쓰기의 결과가 미확인되어 포맷 완료로 처리할 수 없습니다:\n" + "\n".join(uncertain)
    items = pending_files(root, event, host, worktree)
    if not items:
        return None
    return ("Prettier 적용이 확인되지 않은 파일이 있습니다:\n" + "\n".join(item["path"] for item in items)
            + "\n해당 worktree에서 실행한 뒤 lint·test·build를 진행하세요:\n" + command(event, host))


def apply(root: Path, event: dict, host: str, worktree: Path) -> dict:
    common = git.git_common_directory(root) or root
    events_lock = state.repository_state(common) / "events.lock"
    relations = _loader.load("branch_relations")
    reservation = relations.directory(root) / "writes" / (state.digest("formatter:" + uuid.uuid4().hex) + ".json")
    snapshot = []

    def verify(item: dict) -> Path:
        path = safe_path(root, Path(item["worktree"]), item["path"])
        if item.get("status") == "unconfirmed":
            raise RuntimeError(f"실패한 쓰기의 부분 변경을 확인한 뒤 수정 도구로 작업을 마무리하세요: {path}")
        if file_hash(path) != item["sha256"]:
            raise RuntimeError(f"기록 후 파일 내용이 변경되어 포맷을 중단합니다. 현재 내용을 다시 확인하세요: {path}")
        if state.read(writer_path(root, path)).get("token") != item["token"]:
            raise RuntimeError(f"다른 쓰기가 발생한 파일은 포맷하지 않습니다: {path}")
        staged = git.staged_paths(Path(item["worktree"]))
        if git.GIT_STATUS_UNAVAILABLE in staged:
            raise RuntimeError("포맷 전 staged 상태를 확인할 수 없습니다.")
        if path.relative_to(Path(item["worktree"])).as_posix() in staged:
            raise RuntimeError(f"이미 stage된 파일은 자동 포맷하지 않습니다. 포맷을 stage보다 먼저 수행하세요: {path}")
        return path

    def ensure_idle() -> None:
        for path in (relations.directory(root) / "writes").glob("*.json"):
            if path == reservation:
                continue
            value = state.read(path)
            if value.get("worktree") == str(worktree.resolve()):
                raise RuntimeError("같은 worktree에 실행 결과가 확인되지 않은 쓰기가 있습니다. 완료 후 포맷을 다시 실행하세요.")

    try:
        with state.locked(events_lock), state.locked(relations.directory(root) / "locks/git.lock"):
            state.bind_native_session(common, host, paths.event_session_id(event))
            if unconfirmed_calls(root, event, host, worktree):
                raise RuntimeError("결과 미확인 코드 쓰기를 먼저 확인한 뒤 포맷하세요.")
            items = pending_files(root, event, host, worktree)
            if not items:
                return {"formatted": [], "ignored": []}
            ensure_idle()
            revision = git.head(worktree)
            for item in items:
                path = verify(item)
                snapshot.append({**item, "content": path.read_bytes().decode("utf-8"),
                                 "config_sha256": configuration_hash(worktree, path)})
            state.write(reservation, {"host": host, "session": paths.event_session_id(event),
                "call": reservation.stem, "worktree": str(worktree.resolve()), "formatter": True, "pid": os.getpid()})
        package = config.CENTRAL_ROOT / "state/tools/prettier" / SETTINGS["version"] / "node_modules/prettier"
        if not package.is_dir() or package.is_symlink():
            raise RuntimeError("공용 Prettier가 없습니다. 중앙 저장소에서 bin/agent-policy formatter-install을 실행하세요.")
        if not shutil.which("node"):
            raise RuntimeError("Prettier 실행에 Node.js가 필요합니다.")
        result = subprocess.run([shutil.which("node"), str(Path(__file__).with_name("prettier_runner.mjs"))],
            input=json.dumps({"package": str(package), "version": SETTINGS["version"], "files": snapshot}),
            text=True, capture_output=True, cwd=worktree, timeout=40)
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or "Prettier 실행 실패")
        output = json.loads(result.stdout)["files"]
        if [item["path"] for item in output] != [item["path"] for item in snapshot]:
            raise RuntimeError("Prettier 결과의 파일 목록이 요청과 다릅니다.")
        report = {"formatted": [], "ignored": []}
        with state.locked(events_lock), state.locked(relations.directory(root) / "locks/git.lock"):
            ensure_idle()
            if git.head(worktree) != revision:
                raise RuntimeError("포맷 중 Git HEAD가 변경되었습니다. 현재 작업을 확인한 뒤 다시 실행하세요.")
            for item in snapshot:
                verify(item)
                if configuration_hash(worktree, Path(item["path"])) != item["config_sha256"]:
                    raise RuntimeError("포맷 중 Prettier 설정이 변경되었습니다. 다시 실행하세요.")
            record_path = session_path(root, event, host)
            record = state.read(record_path)
            for item, outcome in zip(snapshot, output, strict=True):
                path = Path(item["path"])
                if outcome["status"] == "formatted":
                    content = outcome["content"].encode("utf-8")
                    if content != path.read_bytes():
                        descriptor, temporary = tempfile.mkstemp(prefix=".prettier-", dir=path.parent)
                        try:
                            os.fchmod(descriptor, stat.S_IMODE(path.stat().st_mode))
                            with os.fdopen(descriptor, "wb") as stream:
                                stream.write(content)
                            verify(item)
                            os.replace(temporary, path)
                        finally:
                            Path(temporary).unlink(missing_ok=True)
                    report["formatted"].append(str(path))
                elif outcome["status"] == "ignored":
                    report["ignored"].append(str(path))
                else:
                    raise RuntimeError("Prettier 결과 상태가 올바르지 않습니다.")
                record["files"][str(path)] = {**record["files"][str(path)], "sha256": file_hash(path),
                    "status": outcome["status"], "config_sha256": item["config_sha256"], "version": SETTINGS["version"], "head": revision}
                state.write(record_path, record)
            record.setdefault("reports", {})[str(worktree.resolve())] = {"head": revision, "result": report}
            state.write(record_path, record)
        return report
    finally:
        with state.locked(events_lock):
            reservation.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="현재 세션이 수정한 코드에 프로젝트 Prettier 설정을 적용합니다.")
    parser.add_argument("action", choices=("apply", "check"))
    parser.add_argument("--host", default=os.environ.get("ASAN_AGENT_POLICY_HOST"), choices=("codex", "claude", "opencode"))
    parser.add_argument("--session")
    args = parser.parse_args()
    try:
        if not enabled():
            raise RuntimeError("포맷 자동화가 활성화된 새 inject 세션에서 실행하세요.")
        event = {"session_id": args.session or "missing-session-id", "cwd": str(Path.cwd())}
        root = paths.repository_root(event)
        if not args.host:
            raise RuntimeError("실행 host를 확인할 수 없습니다.")
        if not args.session and os.environ.get("ASAN_AGENT_POLICY_ASSIGNMENT"):
            assignment_path = state.session_path(git.git_common_directory(root), args.host, "launcher", "assignment", create=False)
            args.session = state.read(assignment_path).get("native_session")
        if not args.session:
            raise RuntimeError("실행 중인 native session을 확인할 수 없습니다.")
        event["session_id"] = args.session
        worktree = paths.git_top_level(Path.cwd())
        if worktree is None or not git.same_git_repository(root, worktree):
            raise RuntimeError("같은 프로젝트의 실제 worktree에서 포맷하세요.")
        state.bind_native_session(git.git_common_directory(root), args.host, args.session, read_only=True)
        message = check(root, event, args.host, worktree)
        if args.action == "check":
            if message:
                raise RuntimeError(message)
            print("Prettier 확인 완료")
        elif not message:
            # 실제 launcher에서는 PreToolUse가 포맷을 마쳤다. sandbox 안의
            # 명령은 중앙 state 쓰기 권한 없이 현재 결과만 읽어 확인한다.
            record = state.read(session_path(root, event, args.host))
            receipt = record.get("reports", {}).get(str(worktree.resolve()), {})
            report = receipt.get("result") if receipt.get("head") == git.head(worktree) else None
            print(json.dumps(report or {"formatted": [], "ignored": []}, ensure_ascii=False))
        else:
            print(json.dumps(apply(root, event, args.host, worktree), ensure_ascii=False))
    except (RuntimeError, OSError, ValueError, subprocess.TimeoutExpired) as error:
        print(f"포맷 미완료: {error}", file=sys.stderr)
        raise SystemExit(2) from error


if __name__ == "__main__":
    main()
