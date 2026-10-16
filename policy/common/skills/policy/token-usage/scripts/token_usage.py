#!/usr/bin/env python3
"""세션 토큰 사용량 집계(읽기 전용). 부모 세션과 하위 에이전트를 응답 단위로 센다.

- usage는 API 응답 1개당 한 번만 센다. 응답 하나가 여러 줄에 같은 usage로 기록되는 host가 있다.
- 출력은 응답마다 max(기록값, 생성 문자 추정)으로 잡은 하한이다. 저장되지 않는 추론 본문이 있다.
- 비용 환산 = 캐시 신규 × 1.25 + 캐시 읽기 × 0.1 + 비캐시 입력 × 1 + 출력 × 5.
  청구액이 아니라 같은 기준으로 비교하기 위한 토큰 가중치다.

사용법: python3 -I token_usage.py <host> <명령> [옵션]
  host: claude | codex | opencode
  명령: sessions | overview | parent | agents | inputs | prompts | versions | docs | summary
  sessions 외에는 --session <native session ID>가 필요하다. 옵션은 --help로 확인한다.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sqlite3
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

WEIGHTS = {"cc": 1.25, "cr": 0.1, "in": 1.0, "out": 5.0}
KST = timezone(timedelta(hours=9))
RESUME_GAP = 240  # 초. 하위 에이전트에서 이보다 긴 공백 뒤의 응답을 재개로 본다.
REWRITE_RATIO = 0.8  # 재개 응답의 캐시 신규가 컨텍스트의 이 비율 이상이면 전체 재기록으로 본다.
LARGE_REWRITE = 40_000  # 부모에서 이보다 큰 캐시 신규는 만료·압축 재기록 후보로 보고한다.
VERIFY = ("node --test", "run lint", "run build", "run test", "formatting", "prettier", "npm ci", "npm install",
          "tsc", "vitest", "eslint")
SEARCH = re.compile(r"(?:^|[\s;&|(])(?:grep|rg|git\s+grep|ls-files|find)\b")
FILES_ONLY = re.compile(r"\s-(?:[a-zA-Z]*l[a-zA-Z]*|c|-count|-files-with-matches)\b")


# ---------------------------------------------------------------- 공통 모델

@dataclass
class Response:
    ts: str
    key: str
    model: str
    inp: int = 0  # 비캐시 입력
    cc: int = 0   # 캐시 신규 기록
    cr: int = 0   # 캐시 읽기
    out_recorded: int = 0
    generated: str = ""
    tools: list = field(default_factory=list)  # (call id, name, input dict)

    @property
    def context(self) -> int:
        return self.inp + self.cc + self.cr

    @property
    def out(self) -> float:
        return max(self.out_recorded, estimate_tokens(self.generated))


@dataclass
class Transcript:
    responses: list
    results: dict  # call id -> (chars, error, head)
    inputs: list   # (ts, chars, kind, text). kind: user | notice | handback | compact
    events: list   # (ts, kind, detail)
    versions: collections.Counter = field(default_factory=collections.Counter)


@dataclass
class Agent:
    identifier: str
    kind: str
    description: str
    transcript: Transcript
    parent_call: str = ""


def estimate_tokens(text: str) -> float:
    ascii_count = sum(1 for ch in text if ord(ch) < 128)
    return ascii_count / 3.8 + (len(text) - ascii_count) / 1.1


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def kst(value: str) -> str:
    try:
        return parse_ts(value).astimezone(KST).strftime("%m-%d %H:%M")
    except (ValueError, AttributeError):
        return str(value)[:16]


def iso(value: float) -> str:
    """epoch 초 또는 밀리초를 UTC ISO 문자열로 바꾼다."""
    if value > 1e12:
        value /= 1000
    return datetime.fromtimestamp(value, timezone.utc).isoformat().replace("+00:00", "Z")


def total(responses) -> dict:
    result = {"in": 0, "cc": 0, "cr": 0, "out": 0.0, "out_recorded": 0}
    for item in responses:
        result["in"] += item.inp
        result["cc"] += item.cc
        result["cr"] += item.cr
        result["out"] += item.out
        result["out_recorded"] += item.out_recorded
    return result


def cost(usage: dict) -> float:
    return usage["cc"] * WEIGHTS["cc"] + usage["cr"] * WEIGHTS["cr"] + usage["in"] * WEIGHTS["in"] + usage["out"] * WEIGHTS["out"]


def fmt(value: float) -> str:
    return f"{value / 1e6:.2f}M" if value >= 1e6 else f"{value / 1e3:.0f}K"


def text_of(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(text_of(item.get("text", item.get("content", ""))) if isinstance(item, dict) else str(item)
                       for item in content)
    if isinstance(content, dict):
        return text_of(content.get("text", content.get("content", "")))
    return "" if content is None else str(content)


def clip(text: str, size: int) -> str:
    return re.sub(r"\s+", " ", text)[:size]


# ---------------------------------------------------------------- Claude Code

class ClaudeHost:
    """~/.claude/projects/<cwd slug>/<session>.jsonl 과 <session>/subagents/agent-<id>.jsonl·.meta.json."""

    name = "claude"

    def __init__(self, home: Path | None = None):
        self.root = (home or Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")) / "projects"

    def sessions(self, project: Path) -> list[dict]:
        rows = []
        for path in self.root.glob("*/*.jsonl"):
            cwd, first, last, start, end = "", "", "", "", ""
            for line in path.open(encoding="utf-8", errors="ignore"):
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                cwd = cwd or row.get("cwd", "")
                ts = row.get("timestamp", "")
                start = start or ts
                end = ts or end
                message = row.get("message") or {}
                if row.get("type") == "user" and isinstance(message, dict) and message.get("role") == "user":
                    text = text_of(message.get("content"))
                    if text and not text.lstrip().startswith(("<", "Another Claude session")) and not row.get("isMeta"):
                        first = first or text
                        last = text
            if cwd and inside(project, cwd):
                rows.append({"session": path.stem, "path": str(path), "cwd": cwd, "start": start, "end": end,
                             "first": first, "last": last, "agents": len(list((path.with_suffix("") / "subagents").glob("*.jsonl")))})
        return rows

    def locate(self, session: str) -> Path:
        found = sorted(self.root.glob(f"*/{session}.jsonl"))
        if not found:
            raise SystemExit(f"Claude 세션 기록을 찾지 못했습니다: {session} (위치: {self.root})")
        return found[0]

    def load(self, path: Path, until: str = "") -> Transcript:
        responses = collections.OrderedDict()
        results, inputs, events, versions = {}, [], [], collections.Counter()
        for line in path.open(encoding="utf-8", errors="ignore"):
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = row.get("timestamp", "")
            if until and ts and ts >= until:
                continue
            if row.get("version"):
                versions[row["version"]] += 1
            if row.get("isCompactSummary") or row.get("subtype") == "compact_boundary":
                events.append((ts, "compact", ""))
            message = row.get("message") or {}
            if not isinstance(message, dict):
                continue
            content = message.get("content")
            if message.get("role") == "assistant":
                key = message.get("id") or row.get("uuid")
                item = responses.setdefault(key, Response(ts, key, message.get("model", "")))
                usage = message.get("usage")
                if usage:
                    item.inp = usage.get("input_tokens", 0) or 0
                    item.cc = usage.get("cache_creation_input_tokens", 0) or 0
                    item.cr = usage.get("cache_read_input_tokens", 0) or 0
                    item.out_recorded = usage.get("output_tokens", 0) or 0
                for block in content if isinstance(content, list) else ():
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") == "tool_use":
                        item.tools.append((block.get("id"), block.get("name"), block.get("input") or {}))
                        item.generated += json.dumps(block.get("input") or {}, ensure_ascii=False)
                    elif block.get("type") == "text":
                        item.generated += block.get("text", "")
                    elif block.get("type") == "thinking":
                        item.generated += block.get("thinking", "")
            elif message.get("role") == "user":
                texts = []
                for block in content if isinstance(content, list) else ():
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        value = text_of(block.get("content"))
                        results[block.get("tool_use_id")] = (len(value), bool(block.get("is_error")), clip(value, 200))
                    elif isinstance(block, dict) and block.get("type") == "text":
                        texts.append(block.get("text", ""))
                if isinstance(content, str):
                    texts.append(content)
                for value in texts:
                    if row.get("isCompactSummary"):
                        kind = "compact"
                    elif "<task-notification>" in value:
                        kind = "notice"
                    elif value.startswith("Another Claude session") or "[Subagent hand-back]" in value:
                        kind = "handback"
                    elif value.lstrip().startswith("<") or row.get("isMeta"):
                        kind = "notice"
                    else:
                        kind = "user"
                    inputs.append((ts, len(value), kind, value))
        kept = [item for item in responses.values() if item.context or item.out_recorded]
        return Transcript(kept, results, inputs, events, versions)

    def agents(self, path: Path, until: str = "") -> list[Agent]:
        directory = path.with_suffix("") / "subagents"
        found = []
        for transcript in sorted(directory.glob("agent-*.jsonl")):
            identifier = transcript.stem.removeprefix("agent-")
            try:
                meta = json.loads(transcript.with_suffix(".meta.json").read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                meta = {}
            loaded = self.load(transcript, until)
            if loaded.responses:
                found.append(Agent(identifier, meta.get("agentType", "?"), meta.get("description", ""), loaded,
                                   meta.get("toolUseId", "")))
        return sorted(found, key=lambda agent: agent.transcript.responses[0].ts)


def inside(project: Path, cwd: str) -> bool:
    """세션 cwd가 이 프로젝트의 기본 checkout이나 연결 worktree인지 본다."""
    try:
        target = Path(cwd).resolve()
    except OSError:
        return False
    roots = {project.resolve()}
    try:
        listing = subprocess.run(["git", "-C", str(project), "worktree", "list", "--porcelain"],
                                 capture_output=True, text=True, check=False).stdout
        roots.update(Path(line[9:]).resolve() for line in listing.splitlines() if line.startswith("worktree "))
    except OSError:
        pass
    return any(target == root or root in target.parents for root in roots)


# ---------------------------------------------------------------- Codex

class CodexHost:
    """$CODEX_HOME/sessions/**/rollout-*-<thread id>.jsonl. 하위 에이전트는 별도 rollout이다.

    - usage: cli 0.153 이상은 `token_usage_record`(response_id당 1회, 압축 호출 포함)를 쓴다. 그 이전은
      `event_msg/token_count`의 `last_token_usage`를 쓰되 `total_token_usage`가 직전과 같은 반복 이벤트는 버린다.
      `compacted.payload.latest_token_usage_record`는 직전 기록의 사본이라 세지 않는다.
    - input_tokens는 캐시 읽기(cached_input_tokens)와 캐시 기록을 포함하고, output_tokens는 추론 출력을 포함한다.
    - 하위 에이전트는 session_meta의 parent_thread_id로 부모에 연결된다.
    """

    name = "codex"

    def __init__(self, home: Path | None = None):
        homes = [home] if home else [Path(os.environ["CODEX_HOME"])] if os.environ.get("CODEX_HOME") else []
        self.homes = [*homes, *([Path.home() / ".codex"] if not home else [])]

    def files(self) -> dict[str, Path]:
        """thread id → 가장 큰 rollout. 같은 thread가 assignment home과 공용 이력에 함께 있을 수 있다."""
        found: dict[str, Path] = {}
        for home in self.homes:
            for folder in ("sessions", "archived_sessions"):
                for path in (home / folder).glob("**/rollout-*.jsonl"):
                    identifier = path.stem[-36:]
                    if identifier not in found or path.stat().st_size > found[identifier].stat().st_size:
                        found[identifier] = path
        return found

    @staticmethod
    def meta(path: Path) -> dict:
        with path.open(encoding="utf-8", errors="ignore") as stream:
            for line in stream:
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if row.get("type") == "session_meta":
                    return row.get("payload") or {}
        return {}

    def sessions(self, project: Path) -> list[dict]:
        rows = []
        for identifier, path in self.files().items():
            meta = self.meta(path)
            if meta.get("parent_thread_id") or not inside(project, meta.get("cwd", "")):
                continue
            loaded = self.load(path)
            users = [text for _, _, kind, text in loaded.inputs if kind == "user"]
            stamps = [item.ts for item in loaded.responses]
            rows.append({"session": identifier, "path": str(path), "cwd": meta.get("cwd", ""),
                         "start": stamps[0] if stamps else meta.get("timestamp", ""), "end": stamps[-1] if stamps else "",
                         "first": users[0] if users else "", "last": users[-1] if users else "",
                         "agents": len(self.children(identifier))})
        return rows

    def locate(self, session: str) -> Path:
        path = self.files().get(session)
        if path is None:
            raise SystemExit(f"Codex 세션 기록을 찾지 못했습니다: {session} (위치: {', '.join(map(str, self.homes))})")
        return path

    def children(self, session: str) -> list[tuple[str, Path, dict]]:
        result = []
        for identifier, path in self.files().items():
            meta = self.meta(path)
            if identifier != session and (meta.get("parent_thread_id") == session or
                                          meta.get("session_id") == session and meta.get("parent_thread_id")):
                result.append((identifier, path, meta))
        return result

    def load(self, path: Path, until: str = "") -> Transcript:
        rows = []
        for line in path.open(encoding="utf-8", errors="ignore"):
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        records = any(row.get("type") == "token_usage_record" for row in rows)
        responses, results, inputs, events, versions = [], {}, [], [], collections.Counter()
        pending = Response("", "", "")
        model, previous_total = "", None
        for row in rows:
            ts, kind, payload = row.get("timestamp", ""), row.get("type"), row.get("payload") or {}
            if until and ts and ts >= until:
                continue
            item_type = payload.get("type") if isinstance(payload, dict) else None
            if kind == "session_meta" and payload.get("cli_version"):
                versions[payload["cli_version"]] += 1
            elif kind == "turn_context":
                model = payload.get("model") or model
            elif kind == "compacted":
                events.append((ts, "compact", ""))
            elif kind == "event_msg" and item_type == "user_message":
                text = text_of(payload.get("message"))
                inputs.append((ts, len(text), "notice" if text.lstrip().startswith("<") else "user", text))
            elif kind == "response_item" and item_type == "message" and payload.get("role") == "assistant":
                pending.generated += text_of(payload.get("content"))
            elif kind == "response_item" and item_type == "reasoning":
                pending.generated += text_of(payload.get("summary")) + text_of(payload.get("content"))
            elif kind == "response_item" and item_type in {"function_call", "custom_tool_call"}:
                raw = payload.get("arguments") if item_type == "function_call" else payload.get("input")
                try:
                    data = json.loads(raw) if isinstance(raw, str) and raw.lstrip().startswith("{") else {"input": raw}
                except json.JSONDecodeError:
                    data = {"input": raw}
                if not isinstance(data, dict):
                    data = {"input": data}
                pending.tools.append((payload.get("call_id"), payload.get("name"), data))
                pending.generated += raw if isinstance(raw, str) else json.dumps(raw, ensure_ascii=False)
            elif kind == "response_item" and item_type in {"function_call_output", "custom_tool_call_output"}:
                value = text_of(payload.get("output"))
                error = bool(re.search(r"(?:exit code|Exit code|exit_code\"?:\s*)[1-9]", value[:400]))
                results[payload.get("call_id")] = (len(value), error, clip(value, 200))
            elif kind == "event_msg" and item_type == "item_completed":
                item = payload.get("item") or {}
                if item.get("type") == "CommandExecution":
                    call = item.get("id") or f"exec-{len(results)}"
                    output = text_of(item.get("aggregated_output"))
                    pending.tools.append((call, "exec_command", {"command": text_of(item.get("command")), "cwd": item.get("cwd", "")}))
                    results[call] = (len(output), (item.get("exit_code") or 0) != 0, clip(output, 200))
            usage = None
            if kind == "token_usage_record":
                usage, key = payload.get("usage") or {}, payload.get("response_id") or ts
            elif kind == "event_msg" and item_type == "token_count" and not records:
                info = payload.get("info") or {}
                current = (info.get("total_token_usage") or {}).get("total_tokens")
                if info.get("last_token_usage") and current != previous_total:
                    usage, key = info["last_token_usage"], ts
                previous_total = current if current is not None else previous_total
            if usage is not None:
                cached, written = usage.get("cached_input_tokens", 0) or 0, usage.get("cache_write_input_tokens", 0) or 0
                pending.ts, pending.key, pending.model = ts, key, model
                pending.cr, pending.cc = cached, written
                pending.inp = max((usage.get("input_tokens", 0) or 0) - cached - written, 0)
                pending.out_recorded = usage.get("output_tokens", 0) or 0
                responses.append(pending)
                pending = Response("", "", "")
        return Transcript(responses, results, inputs, events, versions)

    def agents(self, path: Path, until: str = "") -> list[Agent]:
        session = self.meta(path).get("id") or path.stem[-36:]
        found = []
        for identifier, child, meta in self.children(session):
            source = meta.get("source") if isinstance(meta.get("source"), dict) else {}
            subagent = source.get("subagent") or {}
            spawn = subagent.get("thread_spawn") if isinstance(subagent, dict) else None
            kind = (spawn or {}).get("agent_role") or (subagent.get("other") if isinstance(subagent, dict) else "") \
                or meta.get("thread_source") or "?"
            description = " ".join(str(value) for value in ((spawn or {}).get("agent_nickname"), (spawn or {}).get("agent_path")) if value)
            loaded = self.load(child, until)
            if loaded.responses:
                found.append(Agent(identifier, kind, description, loaded))
        return sorted(found, key=lambda agent: agent.transcript.responses[0].ts)


# ---------------------------------------------------------------- OpenCode

class OpenCodeHost:
    """$XDG_DATA_HOME/opencode/opencode.db (기본 ~/.local/share/opencode). 하위 에이전트는 parent_id가 있는 session이다.

    - assistant message의 data.tokens{input, output, reasoning, cache{read, write}}가 응답 1개의 usage다.
      input에는 캐시가, output에는 추론이 포함되지 않는다. event 테이블은 갱신마다 반복되므로 쓰지 않는다.
    - 압축은 summary가 true인 assistant message로 남고 그 usage도 집계한다.
    """

    name = "opencode"

    def __init__(self, home: Path | None = None):
        base = home or Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share") / "opencode"
        self.database = base / "opencode.db" if base.is_dir() or not base.suffix else base

    def connect(self) -> sqlite3.Connection:
        if not self.database.is_file():
            raise SystemExit(f"OpenCode 기록을 찾지 못했습니다: {self.database}")
        try:
            connection = sqlite3.connect(f"file:{self.database}?mode=ro", uri=True)
            connection.execute("select 1 from session limit 1")
        except sqlite3.Error:
            connection = sqlite3.connect(f"file:{self.database}?mode=ro&immutable=1", uri=True)
        return connection

    def sessions(self, project: Path) -> list[dict]:
        rows = []
        with self.connect() as connection:
            for identifier, directory, created, updated in connection.execute(
                    "select id, directory, time_created, time_updated from session where parent_id is null"):
                if not inside(project, directory or ""):
                    continue
                users = self.user_texts(connection, identifier)
                count = connection.execute("select count(*) from session where parent_id = ?", (identifier,)).fetchone()[0]
                rows.append({"session": identifier, "path": str(self.database), "cwd": directory, "start": iso(created),
                             "end": iso(updated), "first": users[0] if users else "", "last": users[-1] if users else "",
                             "agents": count})
        return rows

    @staticmethod
    def user_texts(connection: sqlite3.Connection, session: str) -> list[str]:
        texts = []
        for message, data in connection.execute("select id, data from message where session_id = ? order by time_created", (session,)):
            if json.loads(data).get("role") != "user":
                continue
            parts = [json.loads(value) for (value,) in connection.execute(
                "select data from part where message_id = ? order by time_created", (message,))]
            text = "".join(part.get("text", "") for part in parts if part.get("type") == "text" and not part.get("synthetic"))
            if text:
                texts.append(text)
        return texts

    def locate(self, session: str) -> Path:
        with self.connect() as connection:
            if not connection.execute("select 1 from session where id = ?", (session,)).fetchone():
                raise SystemExit(f"OpenCode 세션을 찾지 못했습니다: {session} (위치: {self.database})")
        return Path(session)

    def load_session(self, connection: sqlite3.Connection, session: str, until: str = "") -> Transcript:
        responses, results, inputs, events = [], {}, [], []
        versions = collections.Counter(value for (value,) in connection.execute("select version from session where id = ?", (session,)) if value)
        for message, created, data in connection.execute(
                "select id, time_created, data from message where session_id = ? order by time_created", (session,)):
            ts = iso(created)
            if until and ts >= until:
                continue
            value = json.loads(data)
            parts = [json.loads(part) for (part,) in connection.execute(
                "select data from part where message_id = ? order by time_created", (message,))]
            if value.get("role") == "user":
                if any(part.get("type") == "compaction" for part in parts):
                    events.append((ts, "compact", ""))
                text = "".join(part.get("text", "") for part in parts if part.get("type") == "text" and not part.get("synthetic"))
                if text:
                    inputs.append((ts, len(text), "notice" if text.lstrip().startswith("<") else "user", text))
                continue
            tokens = value.get("tokens") or {}
            cache = tokens.get("cache") or {}
            item = Response(ts, message, value.get("modelID", ""), inp=tokens.get("input", 0) or 0, cc=cache.get("write", 0) or 0,
                            cr=cache.get("read", 0) or 0, out_recorded=(tokens.get("output", 0) or 0) + (tokens.get("reasoning", 0) or 0))
            for part in parts:
                if part.get("type") in {"text", "reasoning"}:
                    item.generated += part.get("text", "")
                elif part.get("type") == "tool":
                    state = part.get("state") or {}
                    data_in = state.get("input") if isinstance(state.get("input"), dict) else {"input": state.get("input")}
                    item.tools.append((part.get("callID"), part.get("tool"), data_in))
                    item.generated += json.dumps(data_in, ensure_ascii=False)
                    output = text_of(state.get("output") or state.get("error") or "")
                    results[part.get("callID")] = (len(output), state.get("status") == "error", clip(output, 200))
            if value.get("summary") is True:
                events.append((ts, "compact", "summary"))
            if item.context or item.out_recorded:
                responses.append(item)
        return Transcript(responses, results, inputs, events, versions)

    def load(self, path: Path, until: str = "") -> Transcript:
        with self.connect() as connection:
            return self.load_session(connection, str(path), until)

    def agents(self, path: Path, until: str = "") -> list[Agent]:
        found = []
        with self.connect() as connection:
            queue = [str(path)]
            while queue:
                parent = queue.pop()
                for identifier, agent, title in connection.execute(
                        "select id, agent, title from session where parent_id = ?", (parent,)):
                    queue.append(identifier)
                    loaded = self.load_session(connection, identifier, until)
                    if loaded.responses:
                        found.append(Agent(identifier, agent or "?", title or "", loaded))
        return sorted(found, key=lambda agent: agent.transcript.responses[0].ts)


HOSTS = {"claude": ClaudeHost, "codex": CodexHost, "opencode": OpenCodeHost}


# ---------------------------------------------------------------- 분류

def category(name: str, data: dict, session_directory: str) -> str:
    path = str(data.get("file_path") or data.get("filePath") or data.get("path") or data.get("command")
               or data.get("cmd") or data.get("pattern") or "")
    if session_directory:
        path = path.replace(session_directory, "SESSION")
    lowered = (name or "").lower()
    if lowered in {"write", "create"}:
        return "Write(전체)"
    if lowered in {"edit", "multiedit", "apply_patch", "patch"}:
        return "Edit(부분)"
    if lowered in {"grep", "glob", "search"}:
        return "검색"
    if lowered == "skill" or (".agent-policy/" in path or "asan-agent-policy" in path) and "git_operations" not in path \
            and (lowered == "read" or re.search(r"\b(cat|sed|head|tail|nl)\b", path)):
        return "정책·스킬"
    if ("SESSION" in path or "/logs/sessions/" in path) and (lowered == "read" or re.search(r"\b(cat|sed|head)\b", path)):
        return "세션 문서"
    if lowered == "read" and re.search(r"(^|/)tests?/|\.test\.", path):
        return "테스트 읽기"
    if lowered == "read":
        return "소스 읽기"
    if lowered in {"agent", "task", "spawn_agent", "sendmessage", "send_input"}:
        return "하위 에이전트"
    if SEARCH.search(path):
        return "검색"
    if any(word in path for word in VERIFY):
        return "검증 실행"
    if "git_operations" in path:
        return "보호 실행기"
    if re.search(r"\b(cat|sed|head|tail|nl)\b", path):
        return "셸 파일 읽기"
    return "기타"


# ---------------------------------------------------------------- 작업 구간

def load_tasks(path: str | None) -> tuple[list, dict]:
    """[{"id","label","start"(ISO, 시간대 포함)}] 과 {"agents": {id 앞부분: 작업 id}}."""
    if not path:
        return [], {}
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    tasks = sorted(({**item, "start_utc": parse_ts(item["start"]).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")}
                    for item in value.get("tasks", [])), key=lambda item: item["start_utc"])
    return tasks, value.get("agents", {})


def task_of(ts: str, tasks: list) -> str:
    current = "-"
    for item in tasks:
        if ts >= item["start_utc"]:
            current = item["id"]
    return current


def agent_task(agent: Agent, tasks: list, overrides: dict) -> str:
    for prefix, task in overrides.items():
        if agent.identifier.startswith(prefix):
            return task
    return task_of(agent.transcript.responses[0].ts, tasks)


# ---------------------------------------------------------------- 분석

def agent_profile(agent: Agent, session_directory: str) -> dict:
    responses = agent.transcript.responses
    results = agent.transcript.results
    usage = total(responses)
    categories = collections.defaultdict(lambda: [0, 0.0])  # 호출 수, 귀속 토큰
    growth, resumes, errors, writes, searches = 0, [], [], [], []
    reads = collections.Counter()
    documents = collections.defaultdict(lambda: [0, 0, 0])  # chars, 횟수, 부분 읽기
    for index, item in enumerate(responses):
        if index:
            gap = (parse_ts(item.ts) - parse_ts(responses[index - 1].ts)).total_seconds()
            if gap > RESUME_GAP:
                resumes.append({"at": kst(item.ts), "gap_min": round(gap / 60), "context": item.context, "cache_write": item.cc,
                                "full_rewrite": item.cc >= item.context * REWRITE_RATIO})
        delta = responses[index + 1].context - item.context if index + 1 < len(responses) else 0
        sizes = []
        for call, name, data in item.tools:
            chars, error, head = results.get(call, (0, False, ""))
            kind = category(name, data, session_directory)
            sizes.append((kind, len(json.dumps(data, ensure_ascii=False)) + chars))
            path = str(data.get("file_path") or data.get("filePath") or data.get("path") or "")
            command = str(data.get("command") or data.get("cmd") or "")
            if error:
                errors.append({"tool": name, "target": clip(command or path, 90), "result": head[:120]})
            if (name or "").lower() == "read":
                reads[path] += 1
                if kind == "세션 문서":
                    entry = documents[os.path.basename(path)]
                    entry[0] += chars
                    entry[1] += 1
                    entry[2] += 1 if ("offset" in data or "limit" in data) else 0
            if kind in {"Write(전체)", "Edit(부분)"}:
                writes.append({"tool": name, "file": os.path.basename(path),
                               "chars": len(str(data.get("content") or data.get("new_string") or data.get("patch") or ""))})
            if kind == "검색":
                files_only = ((name or "").lower() in {"grep", "glob"} and data.get("output_mode") in (None, "files_with_matches", "count")) \
                    or bool(FILES_ONLY.search(command))
                searches.append({"chars": chars, "files_only": files_only, "command": clip(command or str(data.get("pattern", "")), 90)})
        if delta > 0:
            growth += delta
            weight = sum(size for _, size in sizes) or 1
            if not sizes:
                categories["도구 없는 응답·알림"][1] += delta
            for kind, size in sizes:
                categories[kind][0] += 1
                categories[kind][1] += delta * size / weight
    calls = sum(len(item.tools) for item in responses)
    later = [(kst(ts), chars, clip(text, 160)) for ts, chars, kind, text in agent.transcript.inputs[1:] if kind == "user"]
    return {
        "id": agent.identifier, "kind": agent.kind, "description": agent.description,
        "start": responses[0].ts, "end": responses[-1].ts, "responses": len(responses), "calls": calls,
        "calls_per_response": round(calls / len(responses), 1), "context_start": responses[0].context,
        "context_max": max(item.context for item in responses),
        "context_mean": round(sum(item.context for item in responses) / len(responses)),
        "usage": {key: round(value) for key, value in usage.items()}, "cost": round(cost(usage)),
        "prompt_chars": agent.transcript.inputs[0][1] if agent.transcript.inputs else 0,
        "growth": growth, "categories": {kind: {"calls": value[0], "share": round(value[1] / (growth or 1) * 100)}
                                         for kind, value in sorted(categories.items(), key=lambda kv: -kv[1][1])},
        "resumes": resumes, "rewrite_tokens": sum(item["cache_write"] for item in resumes if item["full_rewrite"]),
        "later_inputs": later, "documents": {name: {"chars": v[0], "reads": v[1], "partial": v[2]} for name, v in documents.items()},
        "rereads": {os.path.basename(path): count for path, count in reads.items() if count > 1},
        "writes": writes, "searches": searches, "errors": errors,
        "models": dict(collections.Counter(item.model for item in responses)),
        "versions": dict(agent.transcript.versions),
    }


def parent_profile(transcript: Transcript, tasks: list, session_directory: str) -> dict:
    responses, results = transcript.responses, transcript.results
    real = [(ts, chars, text) for ts, chars, kind, text in transcript.inputs if kind == "user"]
    bounds = [ts for ts, _, _ in real] + ["9999"]
    segments = []
    for index, (ts, chars, text) in enumerate(real):
        part = [item for item in responses if ts <= item.ts < bounds[index + 1]]
        if part:
            usage = total(part)
            segments.append({"at": kst(ts), "task": task_of(ts, tasks), "input": clip(text, 40), "input_chars": chars,
                             "responses": len(part), "calls": sum(len(item.tools) for item in part),
                             "context": [part[0].context, max(item.context for item in part)], "cost": round(cost(usage))})
    by_task = collections.OrderedDict()
    for item in responses:
        by_task.setdefault(task_of(item.ts, tasks), []).append(item)
    task_rows = []
    for task, part in by_task.items():
        usage = total(part)
        prompts, categories, errors = [], collections.Counter(), 0
        for item in part:
            for call, name, data in item.tools:
                chars, error, _ = results.get(call, (0, False, ""))
                categories[category(name, data, session_directory)] += chars
                errors += error
                if (name or "").lower() in {"agent", "task", "sendmessage", "spawn_agent", "send_input"}:
                    prompts.append((name, len(str(data.get("prompt") or data.get("message") or data.get("input") or ""))))
        replies = [chars for ts, chars, kind, _ in transcript.inputs if kind == "handback" and task_of(ts, tasks) == task]
        task_rows.append({"task": task, "responses": len(part), "calls": sum(len(item.tools) for item in part),
                          "context": [part[0].context, max(item.context for item in part)],
                          "usage": {key: round(value) for key, value in usage.items()}, "cost": round(cost(usage)),
                          "errors": errors, "prompts": len(prompts), "prompt_chars": sum(size for _, size in prompts),
                          "replies": len(replies), "reply_chars": sum(replies),
                          "result_chars_by_category": dict(categories.most_common())})
    rewrites, previous = [], None
    for item in responses:
        if item.cc > LARGE_REWRITE:
            gap = round((parse_ts(item.ts) - parse_ts(previous.ts)).total_seconds() / 60) if previous else None
            rewrites.append({"at": kst(item.ts), "task": task_of(item.ts, tasks), "cache_write": item.cc,
                             "context": item.context, "gap_min": gap})
        previous = item
    drops = [{"at": kst(b.ts), "before": a.context, "after": b.context, "cache_write": b.cc}
             for a, b in zip(responses, responses[1:]) if a.context > 100_000 and b.context < a.context * 0.6]
    large = sorted(((results.get(call, (0, False, ""))[0], kst(item.ts), name,
                     clip(str(data.get("command") or data.get("file_path") or data.get("description") or ""), 70))
                    for item in responses for call, name, data in item.tools), reverse=True)[:12]
    errors = [{"at": kst(item.ts), "task": task_of(item.ts, tasks), "tool": name,
               "target": clip(str(data.get("command") or data.get("file_path") or ""), 70), "result": results[call][2][:110]}
              for item in responses for call, name, data in item.tools if results.get(call, (0, False, ""))[1]]
    usage = total(responses)
    return {"responses": len(responses), "calls": sum(len(item.tools) for item in responses),
            "usage": {key: round(value) for key, value in usage.items()}, "cost": round(cost(usage)),
            "context_mean": round(sum(item.context for item in responses) / max(len(responses), 1)),
            "first": responses[0].ts if responses else "", "last": responses[-1].ts if responses else "",
            "segments": segments, "tasks": task_rows, "rewrites": rewrites, "compactions": drops,
            "compaction_events": [kst(ts) for ts, kind, _ in transcript.events if kind == "compact"],
            "large_results": large, "errors": errors, "models": dict(collections.Counter(item.model for item in responses)),
            "versions": dict(transcript.versions)}


def calls_by_period(agents: list[Agent], tasks: list, overrides: dict) -> list:
    rows = collections.OrderedDict()
    for agent in agents:
        task = agent_task(agent, tasks, overrides)
        entry = rows.setdefault(task, {"task": task, "responses": 0, "calls": 0, "models": collections.Counter()})
        entry["responses"] += len(agent.transcript.responses)
        entry["calls"] += sum(len(item.tools) for item in agent.transcript.responses)
        entry["models"].update(item.model for item in agent.transcript.responses)
    return [{**entry, "calls_per_response": round(entry["calls"] / max(entry["responses"], 1), 1),
             "models": dict(entry["models"])} for entry in rows.values()]


# ---------------------------------------------------------------- 출력

def brief(profile: dict) -> dict:
    """에이전트 목록용 요약. 호출별 목록은 --agent로 한 에이전트를 지정할 때만 낸다."""
    searches, writes = profile["searches"], profile["writes"]
    return {**{key: profile[key] for key in ("id", "kind", "description", "responses", "calls", "calls_per_response",
                                            "context_start", "context_max", "context_mean", "usage", "cost", "prompt_chars",
                                            "rewrite_tokens", "documents", "models")},
            "period": f"{kst(profile['start'])}~{kst(profile['end'])}",
            "categories": dict(list(profile["categories"].items())[:6]),
            "resumes": len(profile["resumes"]), "later_inputs": len(profile["later_inputs"]),
            "rereads": dict(sorted(profile["rereads"].items(), key=lambda kv: -kv[1])[:5]),
            "writes": {"Write": sum(1 for w in writes if w["tool"].lower() in {"write", "create"}),
                       "chars": sum(w["chars"] for w in writes), "largest": sorted(writes, key=lambda w: -w["chars"])[:3]},
            "searches": {"count": len(searches), "chars": sum(s["chars"] for s in searches),
                         "files_only": sum(1 for s in searches if s["files_only"]),
                         "largest": max(searches, key=lambda s: s["chars"]) if searches else None},
            "errors": len(profile["errors"])}


def emit(value) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=1, default=str))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("host", choices=sorted(HOSTS))
    parser.add_argument("command", choices=("sessions", "overview", "parent", "agents", "inputs", "prompts", "versions",
                                            "docs", "summary"))
    parser.add_argument("--project", default=os.getcwd(), help="sessions: 프로젝트 기본 checkout 또는 worktree 경로")
    parser.add_argument("--session", help="native session ID")
    parser.add_argument("--until", default="", help="이 시각(ISO, 시간대 포함) 이후는 집계하지 않는다. 분석 시작 시각을 넣는다")
    parser.add_argument("--tasks", help="작업 구간 JSON: {\"tasks\": [{\"id\",\"label\",\"start\"}], \"agents\": {\"id 앞부분\": \"작업 id\"}}")
    parser.add_argument("--session-directory", default="", help="세션 산출물 폴더. 문서 범주 판정과 docs에 쓴다")
    parser.add_argument("--home", help="host 데이터 위치를 직접 지정한다(기본값은 host 기본 위치)")
    parser.add_argument("--limit", type=int, default=20, help="sessions: 최근 순으로 보여 줄 개수")
    parser.add_argument("--agent", help="agents: 이 ID로 시작하는 하위 에이전트의 호출별 상세(재개, 쓰기, 검색, 오류)")
    args = parser.parse_args()
    host = HOSTS[args.host](Path(args.home)) if args.home else HOSTS[args.host]()
    until = parse_ts(args.until).astimezone(timezone.utc).isoformat().replace("+00:00", "Z") if args.until else ""

    if args.command == "sessions":
        rows = sorted(host.sessions(Path(args.project)), key=lambda row: row["end"], reverse=True)[: args.limit]
        emit([{**row, "start": kst(row["start"]), "end": kst(row["end"]), "first": clip(row["first"], 80),
               "last": clip(row["last"], 80)} for row in rows])
        return
    if args.command == "docs":
        directory = Path(args.session_directory)
        emit({str(path.relative_to(directory)): len(path.read_text(encoding="utf-8", errors="ignore"))
              for path in sorted(directory.rglob("*.md"))})
        return
    if not args.session:
        raise SystemExit("--session <native session ID>가 필요합니다. sessions 명령으로 찾습니다.")
    path = host.locate(args.session)
    tasks, overrides = load_tasks(args.tasks)
    parent = host.load(path, until)
    agents = host.agents(path, until)
    directory = args.session_directory

    if args.command == "overview":
        emit({"session": args.session, "transcript": str(path), "tasks": tasks,
              "parent": {key: value for key, value in parent_profile(parent, tasks, directory).items()
                         if key in {"responses", "calls", "usage", "cost", "first", "last", "compaction_events", "compactions",
                                    "models", "versions"}},
              "inputs": [(kst(ts), chars, clip(text, 110)) for ts, chars, kind, text in parent.inputs if kind == "user"],
              "agents": [{"id": agent.identifier, "task": agent_task(agent, tasks, overrides), "kind": agent.kind,
                          "description": agent.description, "start": kst(agent.transcript.responses[0].ts),
                          "end": kst(agent.transcript.responses[-1].ts), "responses": len(agent.transcript.responses),
                          "cost": round(cost(total(agent.transcript.responses)))} for agent in agents]})
    elif args.command == "parent":
        emit(parent_profile(parent, tasks, directory))
    elif args.command == "agents":
        if args.agent:
            emit([agent_profile(agent, directory) for agent in agents if agent.identifier.startswith(args.agent)])
            return
        groups = collections.OrderedDict()
        for agent in agents:
            groups.setdefault(agent_task(agent, tasks, overrides), []).append(brief(agent_profile(agent, directory)))
        emit(groups)
    elif args.command == "inputs":
        emit({agent.identifier: [(kst(ts), chars, clip(text, 200)) for ts, chars, kind, text in agent.transcript.inputs[1:]
                                 if kind == "user"] for agent in agents})
    elif args.command == "prompts":
        keys = {"묶음": r"묶|한 응답|병렬로 호출", "읽을 범위": r"읽을 것|절만|offset|limit|§|\d+\.\d+절",
                "반복 차단 중단": r"2회|두 번", "-l": r"-l\b|파일 목록만"}
        rows = []
        for item in parent.responses:
            for _, name, data in item.tools:
                if (name or "").lower() not in {"agent", "task", "sendmessage", "spawn_agent", "send_input"}:
                    continue
                text = str(data.get("prompt") or data.get("message") or data.get("input") or "")
                rows.append({"at": kst(item.ts), "task": task_of(item.ts, tasks), "tool": name,
                             "target": str(data.get("description") or data.get("to") or data.get("subagent_type") or "")[:40],
                             "chars": len(text), "has": [key for key, pattern in keys.items() if re.search(pattern, text)]})
        emit(rows)
    elif args.command == "versions":
        emit({"parent": dict(parent.versions), "parent_models": dict(collections.Counter(item.model for item in parent.responses)),
              "agents": {agent.identifier: {"versions": dict(agent.transcript.versions),
                                            "models": dict(collections.Counter(item.model for item in agent.transcript.responses))}
                         for agent in agents},
              "calls_by_task": calls_by_period(agents, tasks, overrides)})
    else:  # summary
        parent_usage = total(parent.responses)
        agent_usage = total(response for agent in agents for response in agent.transcript.responses)
        overall = {key: parent_usage[key] + agent_usage[key] for key in parent_usage}
        share = lambda part: round(part / (cost(overall) or 1) * 100)
        by_role = collections.OrderedDict()
        for agent in agents:
            entry = by_role.setdefault(agent.kind.rsplit(":", 1)[-1], {"agents": 0, "responses": 0, "calls": 0, "cost": 0})
            entry["agents"] += 1
            entry["responses"] += len(agent.transcript.responses)
            entry["calls"] += sum(len(item.tools) for item in agent.transcript.responses)
            entry["cost"] += round(cost(total(agent.transcript.responses)))
        by_task = collections.OrderedDict((item["id"], {"label": item.get("label", ""), "parent": 0, "agents": 0, "agent_count": 0})
                                          for item in tasks)
        for item in parent.responses:
            by_task.setdefault(task_of(item.ts, tasks), {"label": "", "parent": 0, "agents": 0, "agent_count": 0})["parent"] += cost(total([item]))
        for agent in agents:
            entry = by_task.setdefault(agent_task(agent, tasks, overrides), {"label": "", "parent": 0, "agents": 0, "agent_count": 0})
            entry["agents"] += cost(total(agent.transcript.responses))
            entry["agent_count"] += 1
        emit({"weights": WEIGHTS,
              "parent": {"responses": len(parent.responses), "calls": sum(len(i.tools) for i in parent.responses),
                         "usage": {k: round(v) for k, v in parent_usage.items()}, "cost": round(cost(parent_usage)),
                         "share": share(cost(parent_usage))},
              "agents": {"count": len(agents), "responses": sum(len(a.transcript.responses) for a in agents),
                         "calls": sum(len(i.tools) for a in agents for i in a.transcript.responses),
                         "usage": {k: round(v) for k, v in agent_usage.items()}, "cost": round(cost(agent_usage)),
                         "share": share(cost(agent_usage))},
              "total": {"usage": {k: round(v) for k, v in overall.items()}, "cost": round(cost(overall))},
              "cost_parts": {part: {"parent": round(parent_usage[part] * WEIGHTS[part]), "agents": round(agent_usage[part] * WEIGHTS[part])}
                             for part in ("cr", "cc", "out", "in")},
              "by_role": by_role,
              "by_task": {task: {**value, "parent": round(value["parent"]), "agents": round(value["agents"]),
                                 "total": round(value["parent"] + value["agents"]), "share": share(value["parent"] + value["agents"])}
                          for task, value in by_task.items()}})


if __name__ == "__main__":
    main()
