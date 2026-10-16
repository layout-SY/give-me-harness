"""토큰 사용량 집계 스크립트의 회귀 검사. 기준은 admin-ui 세션 보고서의 집계 방식이다."""
from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "policy/common/skills/policy/token-usage/scripts/token_usage.py"


def assistant(ts: str, message: str, usage: dict, *blocks: dict) -> list[dict]:
    """한 응답을 블록마다 한 줄씩, 같은 usage로 기록한다(Claude transcript 형식)."""
    return [{"type": "assistant", "timestamp": ts, "version": "2.1.295",
             "message": {"id": message, "role": "assistant", "model": "claude-opus-5-5", "usage": usage, "content": [block]}}
            for block in blocks]


def usage(inp: int, cc: int, cr: int, out: int) -> dict:
    return {"input_tokens": inp, "cache_creation_input_tokens": cc, "cache_read_input_tokens": cr, "output_tokens": out}


class ClaudeTokenUsageTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.project = self.base / "consumer"
        self.project.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.project, check=True)
        self.home = self.base / "claude"
        folder = self.home / "projects/-consumer"
        folder.mkdir(parents=True)
        self.session = "11111111-2222-3333-4444-555555555555"
        rows = [
            {"type": "user", "timestamp": "2026-10-10T00:00:00Z", "cwd": str(self.project),
             "message": {"role": "user", "content": "작업을 시작해"}},
            *assistant("2026-10-10T00:00:05Z", "m1", usage(10, 1000, 0, 40),
                       {"type": "text", "text": "확인합니다"},
                       {"type": "tool_use", "id": "t1", "name": "Read", "input": {"file_path": str(self.project / "src/app.ts")}}),
            {"type": "user", "timestamp": "2026-10-10T00:00:06Z",
             "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t1", "content": "x" * 500}]}},
            *assistant("2026-10-10T00:00:10Z", "m2", usage(5, 200, 1000, 30),
                       {"type": "tool_use", "id": "t2", "name": "Agent",
                        "input": {"description": "검토", "subagent_type": "asan-agent-policy:watcher", "prompt": "검토해 주세요"}}),
            {"type": "user", "timestamp": "2026-10-10T00:00:11Z",
             "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t2", "content": "launched"}]}},
            {"type": "user", "timestamp": "2026-10-10T01:00:00Z", "message": {"role": "user", "content": "토큰 분석"}},
            *assistant("2026-10-10T01:00:05Z", "m3", usage(1, 5000, 1200, 900), {"type": "text", "text": "분석합니다"}),
        ]
        self.transcript = folder / f"{self.session}.jsonl"
        self.transcript.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
        agents = folder / self.session / "subagents"
        agents.mkdir(parents=True)
        (agents / "agent-abc123.meta.json").write_text(json.dumps({"agentType": "asan-agent-policy:watcher", "description": "검토"}))
        child = [
            {"type": "user", "timestamp": "2026-10-10T00:00:12Z", "message": {"role": "user", "content": "검토해 주세요"}},
            *assistant("2026-10-10T00:00:20Z", "c1", usage(3, 20000, 0, 100),
                       {"type": "tool_use", "id": "c-t1", "name": "Bash", "input": {"command": "grep -rn foo src"}}),
            {"type": "user", "timestamp": "2026-10-10T00:00:21Z",
             "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "c-t1", "content": "y" * 900}]}},
            # 10분 뒤 재개: 컨텍스트 전체를 캐시에 다시 기록한다.
            {"type": "user", "timestamp": "2026-10-10T00:10:00Z", "message": {"role": "user", "content": "후속 지시"}},
            *assistant("2026-10-10T00:10:30Z", "c2", usage(2, 21000, 0, 50), {"type": "text", "text": "PASS"}),
        ]
        (agents / "agent-abc123.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in child),
                                                   encoding="utf-8")

    def run_script(self, *args: str):
        result = subprocess.run([sys.executable, "-I", str(SCRIPT), "claude", *args, "--home", str(self.home)],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_each_response_is_counted_once_and_the_analysis_itself_is_excluded(self) -> None:
        summary = self.run_script("summary", "--session", self.session, "--until", "2026-10-10T10:00:00+09:00")
        # m1은 두 줄에 같은 usage가 있지만 한 번만 센다. 분석 요청(01:00 UTC) 뒤의 m3는 뺀다.
        self.assertEqual(summary["parent"]["responses"], 2)
        self.assertEqual(summary["parent"]["usage"]["cc"], 1200)
        self.assertEqual(summary["parent"]["usage"]["cr"], 1000)
        self.assertEqual(summary["agents"]["count"], 1)
        self.assertEqual(summary["agents"]["usage"]["cc"], 41000)
        expected = 1200 * 1.25 + 1000 * 0.1 + 15 + summary["parent"]["usage"]["out"] * 5
        self.assertAlmostEqual(summary["parent"]["cost"], expected, delta=1)
        self.assertEqual(list(summary["by_role"]), ["watcher"])
        everything = self.run_script("summary", "--session", self.session)
        self.assertEqual(everything["parent"]["responses"], 3)

    def test_output_is_a_lower_bound_from_recorded_and_generated_text(self) -> None:
        parent = self.run_script("parent", "--session", self.session, "--until", "2026-10-10T00:30:00Z")
        # 기록된 출력이 생성 문자 추정보다 크면 기록값을 쓴다.
        self.assertEqual(parent["usage"]["out_recorded"], 70)
        self.assertGreaterEqual(parent["usage"]["out"], 70)
        self.assertEqual([segment["input"] for segment in parent["segments"]], ["작업을 시작해"])

    def test_resume_with_a_full_cache_rewrite_is_reported_per_agent(self) -> None:
        [profile] = self.run_script("agents", "--session", self.session, "--agent", "abc")
        self.assertEqual(profile["kind"], "asan-agent-policy:watcher")
        self.assertEqual(len(profile["resumes"]), 1)
        self.assertTrue(profile["resumes"][0]["full_rewrite"])
        self.assertEqual(profile["rewrite_tokens"], 21000)
        self.assertEqual([item[2] for item in profile["later_inputs"]], ["후속 지시"])
        self.assertEqual(profile["searches"][0]["files_only"], False)
        brief = self.run_script("agents", "--session", self.session)
        self.assertEqual(brief["-"][0]["resumes"], 1)
        # 목록 출력은 호출별 목록 대신 개수만 낸다.
        self.assertEqual(brief["-"][0]["searches"]["count"], 1)

    def test_tasks_file_assigns_parent_responses_and_agents_to_work_periods(self) -> None:
        tasks = self.base / "tasks.json"
        tasks.write_text(json.dumps({"tasks": [{"id": "A", "label": "조사", "start": "2026-10-10T09:00:00+09:00"},
                                               {"id": "B", "label": "구현", "start": "2026-10-10T09:00:08+09:00"}]}))
        summary = self.run_script("summary", "--session", self.session, "--until", "2026-10-10T00:30:00Z", "--tasks", str(tasks))
        self.assertEqual(summary["by_task"]["A"]["agent_count"], 0)
        self.assertEqual(summary["by_task"]["B"]["agent_count"], 1)
        self.assertGreater(summary["by_task"]["A"]["parent"], 0)

    def test_sessions_lists_only_this_project_with_first_and_last_requests(self) -> None:
        [row] = self.run_script("sessions", "--project", str(self.project))
        self.assertEqual(row["session"], self.session)
        self.assertEqual((row["first"], row["last"]), ("작업을 시작해", "토큰 분석"))
        self.assertEqual(row["agents"], 1)
        other = self.base / "other"
        other.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=other, check=True)
        self.assertEqual(self.run_script("sessions", "--project", str(other)), [])


def lines(rows: list[dict]) -> str:
    return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)


class CodexTokenUsageTests(unittest.TestCase):
    PARENT = "01a10000-0000-7000-8000-000000000001"
    CHILD = "01a10000-0000-7000-8000-000000000002"

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.project = self.base / "consumer"
        self.project.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.project, check=True)
        self.home = self.base / "codex-home"
        folder = self.home / "sessions/2026/10/10"
        folder.mkdir(parents=True)
        record = lambda ts, response, inp, cached, out: {"timestamp": ts, "type": "token_usage_record", "payload": {
            "response_id": response, "session_id": self.PARENT,
            "usage": {"input_tokens": inp, "cached_input_tokens": cached, "cache_write_input_tokens": 0,
                      "output_tokens": out, "reasoning_output_tokens": 3, "total_tokens": inp + out}}}
        count = lambda ts, total: {"timestamp": ts, "type": "event_msg", "payload": {"type": "token_count", "info": {
            "total_token_usage": {"total_tokens": total}, "last_token_usage": {"input_tokens": 999, "output_tokens": 1}}}}
        parent = [
            {"timestamp": "2026-10-10T00:00:00Z", "type": "session_meta", "payload": {
                "id": self.PARENT, "session_id": self.PARENT, "parent_thread_id": None, "cwd": str(self.project),
                "cli_version": "0.160.0", "source": "cli"}},
            {"timestamp": "2026-10-10T00:00:01Z", "type": "turn_context", "payload": {"model": "gpt-6"}},
            {"timestamp": "2026-10-10T00:00:02Z", "type": "event_msg", "payload": {"type": "user_message", "message": "작업 시작"}},
            {"timestamp": "2026-10-10T00:00:03Z", "type": "response_item", "payload": {
                "type": "function_call", "name": "shell", "call_id": "c1", "arguments": json.dumps({"command": "rg -l foo src"})}},
            {"timestamp": "2026-10-10T00:00:04Z", "type": "response_item", "payload": {
                "type": "function_call_output", "call_id": "c1", "output": "src/a.ts"}},
            record("2026-10-10T00:00:05Z", "r1", 1000, 0, 50),
            count("2026-10-10T00:00:05Z", 1050),
            {"timestamp": "2026-10-10T00:00:06Z", "type": "compacted", "payload": {
                "latest_token_usage_record": record("2026-10-10T00:00:05Z", "r1", 1000, 0, 50)["payload"]}},
            record("2026-10-10T00:00:09Z", "r2", 1200, 900, 20),
        ]
        child = [
            {"timestamp": "2026-10-10T00:00:07Z", "type": "session_meta", "payload": {
                "id": self.CHILD, "session_id": self.PARENT, "parent_thread_id": self.PARENT, "cwd": str(self.project),
                "cli_version": "0.160.0", "thread_source": "subagent",
                "source": {"subagent": {"thread_spawn": {"parent_thread_id": self.PARENT, "agent_role": "watcher",
                                                         "agent_nickname": "Dalton", "agent_path": "/root/review"}}}}},
            record("2026-10-10T00:00:08Z", "r3", 500, 400, 10),
        ]
        (folder / f"rollout-2026-10-10T00-00-00-{self.PARENT}.jsonl").write_text(lines(parent), encoding="utf-8")
        (folder / f"rollout-2026-10-10T00-00-07-{self.CHILD}.jsonl").write_text(lines(child), encoding="utf-8")

    def run_script(self, *args: str):
        result = subprocess.run([sys.executable, "-I", str(SCRIPT), "codex", *args, "--home", str(self.home)],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_usage_records_are_counted_once_and_cached_input_is_split(self) -> None:
        summary = self.run_script("summary", "--session", self.PARENT)
        # token_count와 압축 기록 안의 사본은 세지 않는다. 캐시 읽기는 입력에서 뺀다.
        self.assertEqual(summary["parent"]["responses"], 2)
        self.assertEqual(summary["parent"]["usage"]["in"], 1000 + 300)
        self.assertEqual(summary["parent"]["usage"]["cr"], 900)
        self.assertEqual(summary["parent"]["usage"]["out_recorded"], 70)
        self.assertEqual(summary["agents"]["count"], 1)
        self.assertEqual(list(summary["by_role"]), ["watcher"])
        [agent] = self.run_script("agents", "--session", self.PARENT, "--agent", self.CHILD[:12])
        self.assertEqual((agent["kind"], agent["description"]), ("watcher", "Dalton /root/review"))
        parent = self.run_script("parent", "--session", self.PARENT)
        self.assertEqual(parent["compaction_events"], ["10-10 09:00"])
        self.assertEqual(parent["segments"][0]["calls"], 1)

    def test_older_rollouts_fall_back_to_changed_token_counts(self) -> None:
        folder = self.home / "sessions/2026/10/11"
        folder.mkdir(parents=True)
        identifier = "01a10000-0000-7000-8000-000000000003"
        event = lambda ts, total, last: {"timestamp": ts, "type": "event_msg", "payload": {"type": "token_count", "info": {
            "total_token_usage": {"total_tokens": total}, "last_token_usage": last}}}
        rows = [{"timestamp": "2026-10-11T00:00:00Z", "type": "session_meta", "payload": {
                    "id": identifier, "session_id": identifier, "cwd": str(self.project), "cli_version": "0.145.0"}},
                event("2026-10-11T00:00:01Z", 110, {"input_tokens": 100, "cached_input_tokens": 40, "output_tokens": 10}),
                event("2026-10-11T00:00:02Z", 110, {"input_tokens": 100, "cached_input_tokens": 40, "output_tokens": 10}),
                event("2026-10-11T00:00:03Z", 230, {"input_tokens": 110, "cached_input_tokens": 100, "output_tokens": 10})]
        (folder / f"rollout-2026-10-11T00-00-00-{identifier}.jsonl").write_text(lines(rows), encoding="utf-8")
        summary = self.run_script("summary", "--session", identifier)
        self.assertEqual(summary["parent"]["responses"], 2)
        self.assertEqual(summary["parent"]["usage"]["cr"], 140)
        self.assertEqual(summary["parent"]["usage"]["in"], 70)
        [listed] = [row for row in self.run_script("sessions", "--project", str(self.project)) if row["session"] == self.PARENT]
        self.assertEqual((listed["first"], listed["agents"]), ("작업 시작", 1))


class OpenCodeTokenUsageTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.project = self.base / "consumer"
        self.project.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.project, check=True)
        self.data = self.base / "opencode"
        self.data.mkdir()
        connection = sqlite3.connect(self.data / "opencode.db")
        connection.executescript("""
            create table session (id text, parent_id text, directory text, title text, agent text, version text,
                                  time_created integer, time_updated integer);
            create table message (id text, session_id text, time_created integer, data text);
            create table part (id text, message_id text, session_id text, time_created integer, data text);
        """)
        connection.execute("insert into session values ('ses_p', null, ?, '작업', 'build', '1.0.0', 1791590400000, 1791590500000)",
                           (str(self.project),))
        connection.execute("insert into session values ('ses_c', 'ses_p', ?, '검토', 'explore', '1.0.0', 1791590410000, 1791590420000)",
                           (str(self.project),))
        tokens = lambda inp, out, reasoning, read, write: {"input": inp, "output": out, "reasoning": reasoning,
                                                          "cache": {"read": read, "write": write}}
        rows = [("m1", "ses_p", 1791590400000, {"role": "user"}), ("m2", "ses_p", 1791590401000,
                 {"role": "assistant", "modelID": "gpt-6", "tokens": tokens(100, 20, 5, 0, 300)}),
                ("m3", "ses_c", 1791590411000, {"role": "assistant", "modelID": "gpt-6", "tokens": tokens(10, 4, 1, 50, 0)})]
        for identifier, session, created, data in rows:
            connection.execute("insert into message values (?, ?, ?, ?)", (identifier, session, created, json.dumps(data)))
        parts = [("p1", "m1", "ses_p", {"type": "text", "text": "작업 시작"}),
                 ("p2", "m2", "ses_p", {"type": "tool", "tool": "task", "callID": "k1",
                                        "state": {"status": "completed", "input": {"description": "검토"}, "output": "done"}})]
        for identifier, message, session, data in parts:
            connection.execute("insert into part values (?, ?, ?, 0, ?)", (identifier, message, session, json.dumps(data)))
        connection.commit()
        connection.close()

    def run_script(self, *args: str):
        result = subprocess.run([sys.executable, "-I", str(SCRIPT), "opencode", *args, "--home", str(self.data)],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_messages_are_responses_and_child_sessions_are_agents(self) -> None:
        summary = self.run_script("summary", "--session", "ses_p")
        # 입력에는 캐시가 들어 있지 않고, 출력은 추론을 더해 기록한다.
        self.assertEqual(summary["parent"]["usage"], {"in": 100, "cc": 300, "cr": 0, "out": 25, "out_recorded": 25})
        self.assertEqual(summary["agents"]["count"], 1)
        self.assertEqual(list(summary["by_role"]), ["explore"])
        parent = self.run_script("parent", "--session", "ses_p")
        self.assertEqual(parent["segments"][0]["input"], "작업 시작")
        self.assertEqual(parent["tasks"][0]["prompts"], 1)
        [row] = self.run_script("sessions", "--project", str(self.project))
        self.assertEqual((row["session"], row["agents"], row["first"]), ("ses_p", 1, "작업 시작"))


if __name__ == "__main__":
    unittest.main()
