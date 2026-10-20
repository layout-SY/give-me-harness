"""지속 상태, 프로세스 lock과 tool 실행 예약. 정책 판정은 호출자가 맡는다."""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path

STATE_ROOT_ENV = "ASAN_AGENT_POLICY_STATE_ROOT"
ASSIGNMENT_ENV = "ASAN_AGENT_POLICY_ASSIGNMENT"


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def state_root() -> Path:
    return Path(os.environ.get(STATE_ROOT_ENV) or Path(tempfile.gettempdir()) / "asan-agent-policy-state").resolve()


def repository_state(common: Path) -> Path:
    return state_root() / "repositories" / digest(str(common.resolve()))


# 같은 hook 프로세스 안에서 대화별 재개 판단을 한 번만 한다.
_RESUMES: dict[tuple[str, str], tuple[str, str, str]] = {}
RESUME_KEYS = ("host", "repository", "project", "role", "responsibility")


def _assignment_record(launch: str) -> tuple[Path | None, dict]:
    for path in (state_root() / "repositories").glob(f"*/assignments/{launch}/assignment.json"):
        return path.parents[2], read(path)
    return None, {}


def native_index(repository: Path, host: str, session: str) -> Path:
    return repository / "native-sessions" / (digest(host + "\0" + session) + ".json")


def _conversation_owner(repository: Path, host: str, session: str) -> str:
    """이 대화를 처음 연결한 assignment. 색인이 없던 이전 기록은 assignment 기록을 훑어 찾는다."""
    indexed = read(native_index(repository, host, session)).get("assignment", "")
    if indexed and read(repository / "assignments" / indexed / "assignment.json").get("native_session") == session:
        return indexed
    owners = []
    for path in (repository / "assignments").glob("*/assignment.json"):
        record = read(path)
        if record.get("host") == host and record.get("native_session") == session and not record.get("resumed_from_launch"):
            owners.append((str(record.get("created_at", "")), path.parent.name))
    return min(owners)[1] if owners else ""


def claude_resume(launch: str, session: str) -> tuple[str, str, str]:
    """(사용할 assignment, 사유, 원래 assignment). 사유: ''(launch 그대로) | reconnected | policy-changed.

    Claude의 세션 안 /resume은 launcher가 만든 assignment를 그대로 둔 채 다른 대화의 ID로 이벤트를 보낸다.
    그 대화를 소유한 assignment가 같은 계약·같은 정책 번들이면 그 assignment에 다시 연결해 승인과 근거를 잇는다.
    정책 번들이 다르면 이전 정책의 승인을 쓰지 않도록 launch에서 파생한 새 assignment로 시작한다.
    """
    key = (launch, session)
    if key in _RESUMES:
        return _RESUMES[key]
    result = (launch, "", "")
    repository, record = _assignment_record(launch)
    if repository is not None and record.get("native_session") not in (None, "", session):
        derived = digest(f"{launch}\0{session}")[:32]
        owner = _conversation_owner(repository, "claude", session)
        original = read(repository / "assignments" / owner / "assignment.json") if owner else {}
        if (repository / "assignments" / derived / "assignment.json").is_file():
            result = (derived, "policy-changed", read(repository / "assignments" / derived / "assignment.json")
                      .get("resumed_owner", owner))
        elif (owner and owner != launch and not original.get("handed_off_to")
              and all(original.get(name) == record.get(name) for name in RESUME_KEYS)):
            same_policy = original.get("bundle_digest") == record.get("bundle_digest")
            result = (owner, "reconnected", owner) if same_policy else (derived, "policy-changed", owner)
    _RESUMES[key] = result
    return result


def resume_notice(host: str, session: str) -> str:
    launch = os.environ.get(ASSIGNMENT_ENV, "")
    if host != "claude" or not re.fullmatch(r"[a-f0-9]{32}", launch):
        return ""
    assignment, reason, original = claude_resume(launch, session)
    if reason == "reconnected":
        return (f"[SESSION_RESUME] 이 대화를 원래 assignment {assignment[:8]}…에 다시 연결했습니다. "
                "그 assignment의 승인·준비 근거와 세션 산출물 폴더를 이어 씁니다.")
    if reason == "policy-changed":
        project = os.environ.get("ASAN_AGENT_POLICY_PROJECT", "<프로젝트>")
        return (f"[SESSION_RESUME] 이 대화를 시작할 때와 정책 번들이 달라 새 assignment {assignment[:8]}…로 시작합니다. "
                "대화는 이어지지만 승인·준비 근거는 현재 정책으로 다시 받습니다. 이전 정책 그대로 이어 쓰려면 이 세션을 닫고 "
                f"`bin/agent-policy resume --project {project} --host claude --assignment {original}`로 재개하세요.")
    return ""


def effective_assignment(host: str, session: str) -> str:
    assignment = os.environ.get(ASSIGNMENT_ENV, "")
    if host == "claude" and re.fullmatch(r"[a-f0-9]{32}", assignment) and session and session != "missing-session-id":
        return claude_resume(assignment, session)[0]
    if (host != "codex" or os.environ.get("ASAN_CODEX_PROJECT_HISTORY") != "1"
            or not re.fullmatch(r"[a-f0-9]{32}", assignment)
            or not re.fullmatch(r"[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}", session)):
        return assignment
    home = Path(os.environ["CODEX_HOME"])
    record = read(home.parents[2] / "assignments" / assignment / "assignment.json")
    previous = record.get("native_session")
    return digest(f"{assignment}\0{session}")[:32] if previous and previous != session else assignment


def session_path(common: Path, host: str, session: str, namespace: str, *, create: bool = True) -> Path | None:
    if not session or session == "missing-session-id":
        return None
    assignment = effective_assignment(host, session)
    if assignment:
        if len(assignment) != 32 or any(c not in "0123456789abcdef" for c in assignment):
            raise RuntimeError("assignment ID가 올바르지 않습니다.")
        root = repository_state(common) / "assignments" / assignment
    else:
        root = repository_state(common) / "sessions" / digest(f"{host}\0{session}")
    if create:
        root.mkdir(mode=0o700, parents=True, exist_ok=True)
    return root / f"{namespace}.json"


def read(path: Path | None, *, max_age: int | None = None) -> dict:
    if path is None:
        return {}
    try:
        if path.is_symlink():
            raise RuntimeError(f"상태 파일이 심볼릭 링크입니다: {path}")
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except (OSError, ValueError) as error:
        raise RuntimeError(f"상태 파일을 확인할 수 없습니다: {path}: {error}") from error
    if not isinstance(value, dict):
        raise RuntimeError(f"상태 파일은 JSON object여야 합니다: {path}")
    if max_age is not None:
        created = value.get("created_at")
        if not isinstance(created, (float, int)) or not 0 <= time.time() - created <= max_age:
            return {}
    return value


def write(path: Path | None, value: dict) -> None:
    if path is None:
        return
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.is_symlink():
        raise RuntimeError(f"상태 파일이 심볼릭 링크입니다: {path}")
    descriptor, temporary_name = tempfile.mkstemp(prefix=".state-", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


@contextmanager
def locked(path: Path):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def bind_native_session(common: Path, host: str, session: str, *, read_only: bool = False) -> None:
    if not os.environ.get(ASSIGNMENT_ENV) or session == "missing-session-id":
        return
    path = session_path(common, host, session, "assignment", create=not read_only)
    record = read(path)
    launch_assignment = os.environ[ASSIGNMENT_ENV]
    if not record and path.parent.name != launch_assignment and not read_only:
        original = read(repository_state(common) / "assignments" / launch_assignment / "assignment.json")
        if (not original or original.get("host") != host
                or original.get("repository") != str(common.resolve()) or original.get("handed_off_to")):
            raise RuntimeError("내장 resume의 원래 launcher 계약을 확인할 수 없습니다.")
        # Copy execution metadata only. Approval/binding/write state lives in separate files.
        record = {key: value for key, value in original.items() if key not in {
            "native_session", "native_link_source", "handed_off_to"}}
        record.update({"id": path.parent.name, "native_session": session,
                       "created_at": time.time(), "resumed_from_launch": launch_assignment})
        if host == "claude":
            record["resumed_owner"] = claude_resume(launch_assignment, session)[2]
        environment = dict(record["environment"])
        environment[ASSIGNMENT_ENV] = path.parent.name
        if environment.get("ASAN_SESSION_DIR_MODE") == "suggested":
            environment["ASAN_SESSION_DIR"] = environment["ASAN_SESSION_DIR"] + "-" + session[:8]
        record["environment"] = environment
    if not record or record.get("host") != host or record.get("repository") != str(common.resolve()):
        raise RuntimeError("launcher의 assignment와 현재 host/repository가 다릅니다.")
    for key, variable in (("role", "ASAN_AGENT_POLICY_ROLE"), ("responsibility", "ASAN_ARTIFACT_RESPONSIBILITY")):
        if os.environ.get(variable) and record.get(key) != os.environ[variable]:
            raise RuntimeError(f"launcher assignment의 {key}와 현재 실행 설정이 다릅니다.")
    if record.get("handed_off_to"):
        raise RuntimeError("이미 다른 assignment로 인계한 세션입니다.")
    assignment = os.environ.get(ASSIGNMENT_ENV)
    for transaction in (repository_state(common) / "handoffs").glob("*.transaction.json"):
        value = read(transaction)
        if value.get("state") == "applying" and {assignment, path.parent.name} & {value.get("source"), value.get("target")}:
            raise RuntimeError("중단된 assignment handoff가 있습니다. 승인한 동일 계약으로 인계를 재실행하세요.")
    previous = record.get("native_session")
    if previous and previous != session:
        guidance = (" 이전 대화를 이어 쓰려면 이 세션을 닫고 `bin/agent-policy resume --project "
                    f"{os.environ.get('ASAN_AGENT_POLICY_PROJECT', '<프로젝트>')} --host claude`로 재개하세요."
                    if host == "claude" else "")
        raise RuntimeError("다른 native session이 소유한 assignment입니다. 새 세션 또는 명시적 handoff를 사용하세요." + guidance)
    if read_only:
        if previous != session:
            raise RuntimeError("native session의 훅이 먼저 assignment를 확인해야 합니다.")
        return
    record["native_session"] = session
    write(path, record)
    index = native_index(repository_state(common), host, session)
    if read(index).get("assignment") != path.parent.name and not record.get("resumed_from_launch"):
        write(index, {"assignment": path.parent.name, "host": host})
    # Hook processes are short-lived; never alter another conversation's environment/state.
    for variable in ("ASAN_SESSION_DIR", "ASAN_SESSION_DIR_MODE"):
        if variable in record.get("environment", {}):
            os.environ[variable] = record["environment"][variable]


def owner_id(host: str, session: str) -> str:
    return effective_assignment(host, session) or digest(f"{host}\0{session}")


def claim(common: Path, resource: str, owner: str) -> str | None:
    path = repository_state(common) / "claims" / f"{digest(resource)}.json"
    record = read(path)
    if record and record.get("owner") != owner:
        return f"다른 assignment가 소유한 작업 대상입니다: {resource} (owner={record.get('owner')}). 명시적으로 인계하세요."
    write(path, {"resource": resource, "owner": owner})
    return None
