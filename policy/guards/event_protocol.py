"""호스트 결과를 공통 성공/실패/미확인 상태로 정규화한다."""

from __future__ import annotations

import re
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any


def codex_plain_shell_result(event: dict) -> bool:
    return (event.get("policy_host") == "codex" and event.get("hook_event_name") == "PostToolUse"
            and str(event.get("tool_name", "")).rsplit(".", 1)[-1].casefold() in {"bash", "exec", "exec_command", "shell"}
            and isinstance(event.get("tool_response"), str))


def normalize_tool_result(event: dict) -> dict:
    if not codex_plain_shell_result(event):
        return event
    loader_path = Path(__file__).with_name("runtime_loader.py")
    loader = ModuleType("asan_codex_event_loader")
    loader.__file__ = str(loader_path)
    exec(compile(loader_path.read_bytes(), str(loader_path), "exec"), loader.__dict__)
    result = loader.load("codex_events").command_result(event)
    if result is None:
        return event
    return {**event, "tool_input": {**event["tool_input"], "workdir": result["workdir"]},
            "tool_response": {"exit_code": result["exit_code"], "output": event["tool_response"]}}


def tool_outcome(event: dict) -> bool | None:
    """빈 결과나 입력 경로만으로 성공을 추론하지 않는다."""
    responses = [event]
    for key in ("tool_response", "tool_output", "result", "output"):
        value = event.get(key)
        if isinstance(value, dict):
            responses.append(value)
    success = event.get("policy_host") == "claude" and event.get("hook_event_name") == "PostToolUse"
    for response in responses:
        if response.get("error") or response.get("isError") or response.get("is_error"):
            return False
        status = response.get("status")
        if response.get("success") is False or (isinstance(status, str) and status in {"error", "failed", "cancelled"}):
            return False
        for key in ("exit_code", "exitCode", "returncode"):
            code = response.get(key)
            if type(code) is int:
                if code != 0:
                    return False
                success = True
        if response.get("success") is True or (isinstance(status, str) and status in {"completed", "success"}):
            success = True
        # Claude Read/Skill의 성공 응답은 file/content, 실패는 error로 전달된다.
        if response is not event and any(response.get(key) for key in ("file", "content", "skill")):
            success = True
    for key in ("tool_response", "tool_output", "output"):
        # 현재 Codex Bash의 문자열은 stdout/stderr 본문이다. 본문의 상태 문구를 믿지 않는다.
        if codex_plain_shell_result(event):
            continue
        value = event.get(key)
        if not isinstance(value, str):
            continue
        # Codex Bash 도구 결과의 프로세스 상태. 실행 중 결과는 완료로 보지 않는다.
        match = re.search(r"(?:Process exited with code|exit code[: ]+)\s*(-?\d+)", value, re.I)
        if str(event.get("tool_name", "")).casefold() == "apply_patch" and value.startswith("Success. Updated the following files:"):
            success = True
        if match:
            if int(match.group(1)) != 0:
                return False
            success = True
    return True if success else None


def tool_succeeded(event: dict) -> bool:
    return tool_outcome(event) is True


def tool_call_id(event: dict) -> str:
    for key in ("tool_use_id", "tool_call_id", "call_id", "callID"):
        value = event.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def emit_stop_result(denial: str | None) -> None:
    if denial is None:
        print("{}")
        return
    json.dump({"decision": "block", "reason": denial}, sys.stdout, ensure_ascii=False)


def emit_operation_approval(host: str, message: str) -> None:
    if host in {"codex", "claude"}:
        decision = "deny" if host == "codex" else "ask"
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": decision,
                    "permissionDecisionReason": message,
                }
            },
            sys.stdout,
            ensure_ascii=False,
        )
        return
    print(message, file=sys.stderr)
    raise SystemExit(2)


def emit_denial(host: str, message: str) -> None:
    if host == "codex":
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": message,
                }
            },
            sys.stdout,
            ensure_ascii=False,
        )
        return
    print(message, file=sys.stderr)
    raise SystemExit(2)


def emit_session_context(host: str, message: str) -> None:
    if host == "codex":
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": message,
                }
            },
            sys.stdout,
            ensure_ascii=False,
        )
        return
    print(message)


def emit_notice(host: str, message: str) -> None:
    """A context hint is never a permission decision or a recurring blocker."""
    print(json.dumps({"decision": "allow", "hookSpecificOutput": {
        "hookEventName": "PreToolUse", "additionalContext": message}}, ensure_ascii=False))
