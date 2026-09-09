"""설치된 Codex와 로컬 응답 fixture로 실제 Bash 훅 계약을 검증한다.

실제 모델·외부 API·소비자 저장소를 사용하지 않는다.
실행: python3 tests/smoke_codex_hooks.py [--output-dir /private/tmp/codex-hook-smoke]
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from test_remediation import RuntimeFixture


def run(output_dir: Path | None) -> None:
    executable = shutil.which("codex")
    if executable is None:
        raise SystemExit("Codex CLI가 필요합니다.")
    fixture = RuntimeFixture()
    fixture.setUp()
    server = None
    try:
        home = fixture.directory / "codex-home"
        home.mkdir()
        worktree = fixture.directory / "external"
        fixture.git("worktree", "add", "-qb", "task/external", str(worktree))
        event_log = fixture.directory / "hook-events.jsonl"
        recorder = fixture.directory / "record-hook.py"
        recorder.write_text(
            "import json, os, subprocess, sys\nfrom pathlib import Path\n"
            "event=json.load(sys.stdin)\n"
            f"result=subprocess.run([sys.executable,'-I',{str(fixture.runtime / 'managed_policy_guard.py')!r},sys.argv[1],'codex'],input=json.dumps(event),text=True,capture_output=True)\n"
            "states=list(Path(os.environ['ASAN_AGENT_POLICY_STATE_ROOT']).rglob('harness-state-v3.json'))\n"
            "state=json.loads(states[0].read_text()) if len(states)==1 else {}\n"
            f"with Path({str(event_log)!r}).open('a') as out: out.write(json.dumps({{'event':event,'state':state,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr}})+'\\n')\n"
            "sys.stdout.write(result.stdout)\nsys.stderr.write(result.stderr)\nsys.exit(result.returncode)\n"
        )
        registrations = {}
        for event, mode in (("PreToolUse", "pre-tool"), ("PostToolUse", "post-tool")):
            registrations[event] = [{"matcher": "Bash", "hooks": [{"type": "command", "timeout": 15,
                                   "command": shlex.join((sys.executable, str(recorder), mode))}]}]
        (home / "hooks.json").write_text(json.dumps({"hooks": registrations}))
        skill = fixture.snapshot / ".agent-policy/common/skills/policy/coding-convention/SKILL.md"
        steps = [(f"cat {shlex.quote(str(skill))}", fixture.root),
                 ("cat src/missing.tsx", fixture.root), ("cat src/App.tsx", worktree)]

        class Handler(BaseHTTPRequestHandler):
            calls = 0

            def log_message(self, *_args):
                pass

            def do_POST(self):
                request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                number = Handler.calls
                Handler.calls += 1
                if number < len(steps):
                    names = {tool.get("name") for tool in request.get("tools", [])}
                    if "exec_command" not in names:
                        self.send_error(500, "fixture requires exec_command")
                        return
                    command, root = steps[number]
                    item = {"type": "function_call", "id": f"fc_{number}", "call_id": f"call_{number}",
                            "name": "exec_command", "arguments": json.dumps({"cmd": command, "workdir": str(root), "max_output_tokens": 1000})}
                else:
                    item = {"type": "message", "id": "msg_done", "role": "assistant", "status": "completed",
                            "content": [{"type": "output_text", "text": "Fixture complete."}]}
                events = [{"type": "response.output_item.done", "output_index": 0, "item": item},
                          {"type": "response.completed", "response": {"id": f"resp_{number}", "object": "response", "status": "completed", "output": [item],
                           "usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}}}]
                payload = "".join("event: " + event["type"] + "\ndata: " + json.dumps(event) + "\n\n" for event in events).encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

        server = HTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        command = [executable, "exec", "--ignore-user-config", "--skip-git-repo-check", "--sandbox", "read-only",
                   "--dangerously-bypass-hook-trust", "--json", "-C", str(fixture.root)]
        # hook trust 예외는 위에서 생성한 임시 recorder에만 적용한다. 프로젝트·개인 설정은 로드하지 않는다.
        for value in ("features.hooks=true", "project_doc_max_bytes=0", 'model_provider="fixture"', 'model="fixture"',
                      'model_providers.fixture.name="Fixture"', f'model_providers.fixture.base_url="http://127.0.0.1:{server.server_port}/v1"',
                      'model_providers.fixture.wire_api="responses"', "model_providers.fixture.requires_openai_auth=false"):
            command.extend(("-c", value))
        command.append("Run the fixture reads, then stop.")
        environment = {key: value for key, value in os.environ.items() if not key.startswith("ASAN_")}
        environment.update(fixture.env)
        environment["CODEX_HOME"] = str(home)
        result = subprocess.run(command, input="", text=True, capture_output=True, env=environment, timeout=60)
        captured = [json.loads(line) for line in event_log.read_text().splitlines()] if event_log.exists() else []
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "hook-events.json").write_text(json.dumps(captured, ensure_ascii=False, indent=2))
            (output_dir / "stdout.log").write_text(result.stdout)
            (output_dir / "stderr.log").write_text(result.stderr)
        assert result.returncode == 0, result.stderr
        assert all(entry["returncode"] == 0 and '"deny"' not in entry["stdout"] for entry in captured), captured
        completed = [entry for entry in captured if entry["event"]["hook_event_name"] == "PostToolUse"]
        assert len(completed) == 3, captured
        assert completed[0]["state"].get("skill_confirmed") is True, completed[0]
        assert completed[1]["state"].get("exploration_completed") is not True, completed[1]
        assert completed[2]["state"].get("exploration_completed") is True, completed[2]
        # 실제 Codex 훅은 외부 worktree 명령에도 session cwd를 보내며 workdir를 생략한다.
        assert completed[2]["event"]["cwd"] == str(fixture.root), completed[2]["event"]
        version = subprocess.check_output((executable, "--version"), text=True).strip()
        print(f"PASS: {version}; native skill read, failed read, external worktree read")
    finally:
        if server:
            server.shutdown()
            server.server_close()
        fixture.doCleanups()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    run(parser.parse_args().output_dir)
