"""Codex의 종료 코드 없는 Bash 결과를 같은 호출의 완료 기록으로 보완한다."""
from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.parse import unquote, urlsplit


MAX_TRANSCRIPT_BYTES = 4 * 1024 * 1024


def command_result(event: dict) -> dict | None:
    """기록이 없거나 형식·귀속이 다르면 성공을 추정하지 않는다."""
    session = event.get("session_id")
    turn = event.get("turn_id")
    call = event.get("tool_use_id") or event.get("tool_call_id") or event.get("call_id")
    transcript = event.get("transcript_path")
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        return None
    command = tool_input.get("command")
    cwd = event.get("cwd")
    if not all(isinstance(value, str) and value for value in (session, turn, call, transcript, command, cwd)):
        return None
    try:
        home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).expanduser().resolve()
        path = Path(transcript)
        if not path.is_absolute() or path.is_symlink() or not path.resolve().is_relative_to((home / "sessions").resolve()):
            return None
        expected_root = None
        workdir = tool_input.get("workdir")
        if isinstance(workdir, str) and workdir:
            expected_root = (Path(cwd) / Path(workdir).expanduser()).resolve()
        with path.open("rb") as stream:
            header = json.loads(stream.readline(64 * 1024))
            if not isinstance(header, dict) or header.get("type") != "session_meta":
                return None
            metadata = header.get("payload")
            if not isinstance(metadata, dict) or metadata.get("id") != session:
                return None
            # session_meta.cwd는 최초 위치다. 같은 native 세션을 다른 worktree에서
            # 재개할 수 있으므로 경로는 아래의 해당 호출 완료 기록으로 판정한다.
            size = stream.seek(0, 2)
            start = max(0, size - MAX_TRANSCRIPT_BYTES)
            stream.seek(start)
            if start:
                stream.readline(MAX_TRANSCRIPT_BYTES)
            tail = stream.read(MAX_TRANSCRIPT_BYTES)
        for line in reversed(tail.splitlines()):
            if b'"item_completed"' not in line:
                continue
            try:
                record = json.loads(line)
            except (ValueError, UnicodeError):
                continue
            if not isinstance(record, dict) or record.get("type") != "event_msg":
                continue
            payload = record.get("payload")
            if not isinstance(payload, dict) or payload.get("type") != "item_completed":
                continue
            item = payload.get("item")
            if not isinstance(item, dict) or item.get("type") != "CommandExecution" or item.get("id") != call:
                continue
            if payload.get("thread_id") != session or payload.get("turn_id") != turn:
                return None
            arguments = item.get("command")
            if (not isinstance(arguments, list) or len(arguments) != 3
                    or not isinstance(arguments[0], str)
                    or Path(arguments[0]).name not in {"sh", "bash", "zsh", "fish", "dash", "ksh"}
                    or arguments[1] not in {"-c", "-lc"} or arguments[2] != command):
                return None
            location = item.get("cwd")
            if not isinstance(location, str):
                return None
            parsed = urlsplit(location)
            if parsed.scheme != "file" or parsed.netloc not in {"", "localhost"} or parsed.query or parsed.fragment:
                return None
            actual_root = Path(unquote(parsed.path))
            if not actual_root.is_absolute():
                return None
            actual_root = actual_root.resolve()
            if expected_root is not None and actual_root != expected_root:
                return None
            code = item.get("exit_code")
            status = item.get("status")
            if type(code) is not int or status not in {"completed", "failed"}:
                return None
            if status == "failed" and code == 0:
                return None
            # Codex Bash hook은 exec_command.workdir도 생략한다. 완료 기록의 실제 경로를 사용한다.
            return {"exit_code": code, "workdir": str(actual_root)}
    except (OSError, RuntimeError, ValueError, UnicodeError):
        return None
    return None
