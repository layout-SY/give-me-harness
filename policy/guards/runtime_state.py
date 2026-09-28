"""지속 상태, 프로세스 lock과 tool 실행 예약. 정책 판정은 호출자가 맡는다."""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
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


def session_path(common: Path, host: str, session: str, namespace: str, *, create: bool = True) -> Path | None:
    if not session or session == "missing-session-id":
        return None
    assignment = os.environ.get(ASSIGNMENT_ENV, "")
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
        if value.get("state") == "applying" and assignment in {value.get("source"), value.get("target")}:
            raise RuntimeError("중단된 assignment handoff가 있습니다. 승인한 동일 계약으로 인계를 재실행하세요.")
    previous = record.get("native_session")
    if previous and previous != session:
        raise RuntimeError("다른 native session이 소유한 assignment입니다. 새 세션 또는 명시적 handoff를 사용하세요.")
    if read_only:
        if previous != session:
            raise RuntimeError("native session의 훅이 먼저 assignment를 확인해야 합니다.")
        return
    record["native_session"] = session
    write(path, record)


def owner_id(host: str, session: str) -> str:
    return os.environ.get(ASSIGNMENT_ENV) or digest(f"{host}\0{session}")


def claim(common: Path, resource: str, owner: str) -> str | None:
    path = repository_state(common) / "claims" / f"{digest(resource)}.json"
    record = read(path)
    if record and record.get("owner") != owner:
        return f"다른 assignment가 소유한 작업 대상입니다: {resource} (owner={record.get('owner')}). 명시적으로 인계하세요."
    write(path, {"resource": resource, "owner": owner})
    return None
