"""실행 전 거절된 호출만 종료한다. 코드·성공 receipt·승인 상태는 변경하지 않는다."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import ModuleType

_source = Path(__file__).with_name("runtime_state.py")
state = ModuleType("write_receipt_state")
state.__file__ = str(_source)
exec(compile(_source.read_bytes(), str(_source), "exec"), state.__dict__)


def call_path(repository: Path, owner: str, call: str) -> Path:
    return repository / "formatting/v1/calls" / (state.digest(owner + ":" + call) + ".json")


def pending_writes(repository: Path, host: str | None = None, session: str | None = None) -> list[dict]:
    result = []
    for path in sorted((repository / "branch-relations/v1/writes").glob("*.json")):
        value = state.read(path)
        if (host is None or value.get("host") == host) and (session is None or value.get("session") == session):
            result.append({**value, "id": path.stem})
    return result


def cancel_unexecuted(repository: Path, host: str, session: str, owner: str, call: str, evidence: dict,
                      outcome: str = "not-executed", reason: str = "permission-denied-before-execution") -> list[str]:
    """호출자는 native 거절 근거를 검증하고 events.lock을 보유해야 한다."""
    if not call or host != "claude" or not session:
        raise RuntimeError("실행 전 거절된 Claude 호출 식별자가 필요합니다.")
    directory = repository / "branch-relations/v1"
    with state.locked(directory / "locks/git.lock"):
        writes = [item for item in pending_writes(repository, host, session) if item.get("call") == call]
        source = call_path(repository, owner, call)
        record = state.read(source)
        files = record.get("files", [])
        if any(item.get("owner") != owner or item.get("call") != call for item in files):
            raise RuntimeError("쓰기 호출의 소유자와 포맷 기록이 다릅니다.")
        if not writes and not files:
            return []
        # 삭제 전에 근거와 원본을 보존한다. 중단 후 같은 호출의 재처리는 멱등이다.
        receipt = directory / "write-receipts" / (state.digest(host + ":" + session + ":" + call) + ".json")
        if not receipt.exists():
            state.write(receipt, {"outcome": outcome, "host": host, "session": session,
                                 "owner": owner, "call": call, "writes": writes, "formatting": record,
                                 "evidence": evidence})
        if files:
            record["not_executed"] = True
            for item in files:
                item["resolved_by"] = {"reason": reason, "receipt": str(receipt)}
            state.write(source, record)
            for item in files:
                writer = repository / "formatting/v1/writers" / (state.digest(item["path"]) + ".json")
                if state.read(writer).get("token") != item["token"]:
                    continue  # 후속 쓰기 또는 다른 세션의 소유권을 덮어쓰지 않는다.
                previous = item.get("previous_writer", {})
                visited = set()
                while previous.get("token") and previous["token"] not in visited:
                    visited.add(previous["token"])
                    prior = state.read(call_path(repository, previous["owner"], previous["call"]))
                    if not prior.get("not_executed"):
                        break
                    match = next((v for v in prior.get("files", []) if v.get("token") == previous["token"]), {})
                    previous = match.get("previous_writer", {})
                if previous:
                    state.write(writer, previous)
                else:
                    writer.unlink(missing_ok=True)
        for item in writes:
            (directory / "writes" / (item["id"] + ".json")).unlink(missing_ok=True)
        return [item["id"] for item in writes]


def agent_transcript_calls(agent: str, transcript: Path) -> tuple[set[str], set[str]] | None:
    """끝난 하위 에이전트 대화 기록의 (호출 ID, 결과가 기록된 호출 ID). 확인할 수 없으면 None."""
    if not agent or transcript.name != f"agent-{agent}.jsonl" or not transcript.is_file():
        return None
    if transcript.stat().st_size > 32 * 1024 * 1024:
        return None
    recorded, results = set(), set()
    with transcript.open() as stream:
        for line in stream:
            try:
                content = json.loads(line).get("message", {}).get("content")
            except (json.JSONDecodeError, AttributeError):
                continue
            for block in content if isinstance(content, list) else ():
                if isinstance(block, dict):
                    recorded.update(value for value in (block.get("id"), block.get("tool_use_id")) if isinstance(value, str))
                    if block.get("type") == "tool_result" and isinstance(block.get("tool_use_id"), str):
                        results.add(block["tool_use_id"])
    return recorded, results


def release_unrecorded(repository: Path, host: str, session: str, owner: str, agent: str, transcript: Path) -> list[str]:
    """끝난 하위 에이전트의 대화 기록에 없는 호출의 예약만 해소한다. 호출자는 events.lock을 보유해야 한다.

    병렬 호출이 취소되면 PreToolUse만 실행되고 대화 기록과 PostToolUse가 남지 않는다. 하위 에이전트가
    끝났으므로 그 호출은 더 실행되지 않는다. 기록에 있으나 결과가 확인되지 않은 호출은 남긴다.
    """
    calls = agent_transcript_calls(agent, transcript) if host == "claude" and session else None
    if calls is None:
        return []
    recorded = calls[0]
    released = []
    for item in pending_writes(repository, host, session):
        if item.get("agent") == agent and item.get("call") and item["call"] not in recorded:
            released += cancel_unexecuted(repository, host, session, owner, item["call"],
                {"event": "SubagentStop", "agent": agent, "transcript": str(transcript), "recorded_calls": len(recorded)},
                outcome="not-recorded", reason="call-missing-from-finished-agent-transcript")
    return released


def finished_calls(repository: Path, host: str, session: str, agent: str, transcript: Path) -> list[str]:
    """끝난 하위 에이전트의 호출 중 결과는 기록됐지만 PostToolUse가 예약을 끝내지 못한 호출."""
    calls = agent_transcript_calls(agent, transcript) if host == "claude" and session else None
    if calls is None:
        return []
    return list(dict.fromkeys(item["call"] for item in pending_writes(repository, host, session)
                              if item.get("agent") == agent and item.get("call") in calls[1]))


def release_finished(repository: Path, host: str, session: str, owner: str, call: str, evidence: dict) -> list[str]:
    """결과가 기록된 호출의 예약을 수령증과 함께 해소한다. 호출자는 events.lock을 보유하고 포맷 기록을
    결과 미확인으로 먼저 정리해야 한다."""
    directory = repository / "branch-relations/v1"
    with state.locked(directory / "locks/git.lock"):
        writes = [item for item in pending_writes(repository, host, session) if item.get("call") == call]
        if not writes:
            return []
        receipt = directory / "write-receipts" / (state.digest(host + ":" + session + ":" + call) + ".json")
        if not receipt.exists():
            state.write(receipt, {"outcome": "post-tool-missing", "host": host, "session": session,
                                 "owner": owner, "call": call, "writes": writes, "evidence": evidence})
        for item in writes:
            (directory / "writes" / (item["id"] + ".json")).unlink(missing_ok=True)
        return [item["id"] for item in writes]


def denied_transcript_calls(path: Path, session: str) -> dict[str, dict]:
    """native JSONL의 실행 전 classifier 거절만 인정한다. 일반 tool 오류는 제외한다."""
    if path.stat().st_size > 32 * 1024 * 1024:
        raise RuntimeError("대화 원본이 자동 대조 크기 한도를 초과했습니다. 개별 write-recovery를 사용하세요.")
    uses, results, ambiguous = {}, {}, set()
    with path.open() as stream:
        for number, line in enumerate(stream, 1):
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue  # 기록 중인 마지막 줄은 종료 근거로 사용하지 않는다.
            if row.get("sessionId") != session or row.get("isSidechain"):
                continue
            content = row.get("message", {}).get("content")
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict):
                    continue
                call = block.get("id") or block.get("tool_use_id")
                if not call:
                    continue
                if row.get("type") == "assistant" and block.get("type") == "tool_use":
                    value = {"uuid": row.get("uuid"), "name": block.get("name"), "input": block.get("input", {})}
                    if call in uses and uses[call] != value:
                        ambiguous.add(call)
                    uses[call] = value
                elif row.get("type") == "user" and block.get("type") == "tool_result":
                    if call in results:
                        ambiguous.add(call)
                    results[call] = {"line": number, "source": row.get("sourceToolAssistantUUID"),
                        "kind": row.get("toolDenialKind"), "error": block.get("is_error"),
                        "text": block.get("content"), "uuid": row.get("uuid")}
    confirmed = {}
    for call, result in results.items():
        use = uses.get(call, {})
        if (call not in ambiguous and use.get("name") in {"Write", "Edit", "Bash"}
                and use.get("uuid") and result["source"] == use["uuid"]
                and result["kind"] == "automode-unavailable" and result["error"] is True
                and isinstance(result["text"], str)
                and result["text"].startswith("The server-side auto mode classifier gave no verdict")):
            confirmed[call] = {"path": use["input"].get("file_path"), "tool": use["name"],
                               "input_sha256": hashlib.sha256(json.dumps(use["input"], sort_keys=True).encode()).hexdigest(),
                               "transcript": str(path),
                               "line": result["line"], "uuid": result["uuid"], "kind": result["kind"]}
    return confirmed
