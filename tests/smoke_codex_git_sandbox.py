"""실제 Codex의 중앙 Git runner 예외와 승인 경계를 로컬 응답 fixture로 검증한다.

외부 모델·실제 소비자 저장소를 사용하지 않는다. macOS에서는 중첩 sandbox 밖에서 실행한다.
python3 tests/smoke_codex_git_sandbox.py --output-dir /private/tmp/codex-git-sandbox
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
import tempfile
from dataclasses import replace
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from unittest.mock import patch

from test_relation_operations import RelationOperationTests
from agent_policy.core import CENTRAL_ROOT, render_project
from agent_policy.injection import _prepare_codex_home


def native_run(executable, fixture, home, steps, *, ignore_rules=False, hooks=True):
    class Handler(BaseHTTPRequestHandler):
        calls = 0
        errors = []
        tool_results = []

        def log_message(self, *_args):
            pass

        def do_POST(self):
            request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            Handler.tool_results.extend(item for item in request.get("input", [])
                                        if item.get("type") == "function_call_output")
            number = Handler.calls
            Handler.calls += 1
            try:
                if number < len(steps):
                    assert "exec_command" in {tool.get("name") for tool in request.get("tools", [])}, request.get("tools")
                    command = steps[number]()
                    item = {"type": "function_call", "id": f"fc_{number}", "call_id": f"call_{number}",
                            "name": "exec_command", "arguments": json.dumps({"cmd": command,
                            "workdir": str(fixture.root), "max_output_tokens": 2000})}
                else:
                    item = {"type": "message", "id": "done", "role": "assistant", "status": "completed",
                            "content": [{"type": "output_text", "text": "Fixture complete."}]}
                events = [{"type": "response.output_item.done", "output_index": 0, "item": item},
                          {"type": "response.completed", "response": {"id": f"resp_{number}", "object": "response",
                           "status": "completed", "output": [item],
                           "usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}}}]
                payload = "".join("event: " + event["type"] + "\ndata: " + json.dumps(event) + "\n\n" for event in events).encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            except Exception as error:
                Handler.errors.append(repr(error))
                self.send_error(500, "fixture failed")

    server = HTTPServer(("127.0.0.1", 0), Handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        command = [executable, "exec", "--skip-git-repo-check", "--json",
                   "--dangerously-bypass-hook-trust", "-C", str(fixture.root)]
        # Explicit read-only fixture root avoids macOS's writable temporary directory exception.
        profile = 'permissions.fixture={extends=":workspace",filesystem={' + json.dumps(str(fixture.base)) + '="read",' + json.dumps(str(fixture.root)) + '="write"}}'
        for value in (profile, 'default_permissions="fixture"', 'approval_policy="never"',
                      f'features.hooks={str(hooks).lower()}', 'features.apps=false', 'features.code_mode=false',
                      'project_doc_max_bytes=0', 'model_provider="fixture"', 'model="fixture"',
                      'model_providers.fixture.name="Fixture"',
                      f'model_providers.fixture.base_url="http://127.0.0.1:{server.server_port}/v1"',
                      'model_providers.fixture.wire_api="responses"', 'model_providers.fixture.requires_openai_auth=false'):
            command.extend(("-c", value))
        if ignore_rules:
            command.append("--ignore-rules")
        command.append("Run the fixture commands, then stop.")
        environment = {key: value for key, value in fixture.env.items() if key not in {"CODEX_THREAD_ID", "CODEX_HOME"}}
        environment["CODEX_HOME"] = str(home)
        result = subprocess.run(command, input="", text=True, capture_output=True, env=environment, timeout=90)
        assert not Handler.errors, Handler.errors
        assert result.returncode == 0, result.stderr
        assert Handler.calls == len(steps) + 1, (Handler.calls, result.stdout, result.stderr)
        return {"stdout": result.stdout, "stderr": result.stderr, "tool_results": Handler.tool_results}
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)


def run(output_dir: Path):
    executable = shutil.which("codex")
    assert executable, "Codex CLI가 필요합니다."
    fixture = RelationOperationTests()
    # Real worktree policy forbids /tmp: keep the synthetic repository in ignored
    # central state, and remove only this fixture via its TemporaryDirectory.
    fixture_root = CENTRAL_ROOT / "state/native-smoke"
    fixture_root.mkdir(parents=True, exist_ok=True)
    temporary_directory = tempfile.TemporaryDirectory
    with patch("test_relation_operations.tempfile.TemporaryDirectory",
               side_effect=lambda: temporary_directory(dir=fixture_root)):
        fixture.setUp()
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        fixture.project = replace(fixture.project, worktree_root=fixture.base / "worktrees")
        fixture.project.worktree_root.mkdir()
        # The fixture lives under central Git only for cleanup convenience;
        # prevent Git discovery above its isolated synthetic repository layout.
        fixture.env["GIT_CEILING_DIRECTORIES"] = str(fixture.base)
        rendered = render_project(fixture.project)
        for relative, content in rendered.items():
            target = fixture.base / "policy" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        fixture.seed_tree()
        fixture.runtime = fixture.base / "policy/.agent-policy/runtime"
        source = fixture.base / "empty-user-home"
        source.mkdir()
        (source / "config.toml").write_text("# Synthetic user config; no credentials or external provider.\n")
        home, _ = _prepare_codex_home(fixture.project, rendered, fixture.base,
                                      fixture.base / "assignment", source)
        assert (home / "config.toml").is_symlink()
        event_log = fixture.base / "events.jsonl"
        recorder = fixture.base / "record.py"
        guard = fixture.runtime / "managed_policy_guard.py"
        recorder.write_text("import json,subprocess,sys\nfrom pathlib import Path\n"
            "event=json.load(sys.stdin)\n"
            f"with Path({str(event_log)!r}).open('a') as out: out.write(json.dumps(event)+'\\n')\n"
            f"result=subprocess.run([sys.executable,'-I',{str(guard)!r},'pre-tool','codex'],input=json.dumps(event),text=True)\n"
            "sys.exit(result.returncode)\n")
        # Only the real pre-tool hook is needed; fixture approval is supplied explicitly below.
        (home / "hooks.json").write_text(json.dumps({"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{
            "type": "command", "timeout": 30, "command": shlex.join([sys.executable, str(recorder)])}]}]}}))
        runner = [sys.executable, "-I", str(fixture.runtime / "git_operations.py")]
        worktree = fixture.project.worktree_root / "native-sandbox"
        prepare = shlex.join([*runner, "relation", "--action", "create", "--name", "task/native-sandbox",
                              "--parent", "sy-main", "--fork", fixture.git("rev-parse", "HEAD"),
                              "--worktree", str(worktree), "--purpose", "sandbox fixture"])
        operations = fixture.repository / "branch-relations/v1/operations"

        def operation():
            records = [path for path in operations.glob("*.json") if not path.name.endswith(".grant.json")]
            assert len(records) == 1, records
            return json.loads(records[0].read_text())

        def execute():
            assert operation()["stage"] == "prepared"
            return "cd -- " + shlex.quote(str(fixture.root)) + " && " + shlex.join([*runner, "execute", operation()["id"]])

        baseline = native_run(executable, fixture, home, [lambda: prepare], ignore_rules=True)
        (output_dir / "before.json").write_text(json.dumps(baseline, ensure_ascii=False, indent=2))
        assert "Operation not permitted" in baseline["stdout"] or "Permission denied" in baseline["stdout"], baseline
        assert not list(operations.glob("*.json"))

        def approve_and_execute():
            assert operation()["stage"] == "prepared", "승인 전에 실행됨"
            assert not worktree.exists(), "승인 전에 worktree가 생성됨"
            event = json.loads(event_log.read_text().splitlines()[-1])
            event["prompt"] = "명령 실행 승인"
            approved = subprocess.run([sys.executable, "-I", str(guard), "user-prompt", "codex"],
                input=json.dumps(event), text=True, capture_output=True, env=fixture.env, cwd=fixture.root)
            assert approved.returncode == 0, approved.stderr
            return execute()

        fixed = native_run(executable, fixture, home, [lambda: prepare, execute, approve_and_execute])
        (output_dir / "after.json").write_text(json.dumps(fixed, ensure_ascii=False, indent=2))
        assert "명령 실행 승인" in fixed["stdout"] + fixed["stderr"], fixed
        assert operation()["stage"] == "done", fixed
        assert (worktree / ".git").is_file(), fixed
        assert fixture.git("branch", "--show-current", root=worktree) == "task/native-sandbox"

        sentinel = fixture.state / "unauthorized.txt"
        probe = shlex.join([sys.executable, "-c", f"from pathlib import Path; Path({str(sentinel)!r}).write_text('forbidden')"])
        # Disable hooks only for this negative probe: native sandbox itself must deny the direct write.
        blocked = native_run(executable, fixture, home,
            [lambda: probe, lambda: "cd -- " + shlex.quote(str(fixture.root)) + " && " + probe], hooks=False)
        (output_dir / "direct-write.json").write_text(json.dumps(blocked, ensure_ascii=False, indent=2))
        assert not sentinel.exists(), blocked
        denials = {item["call_id"]: str(item["output"]) for item in blocked["tool_results"]}
        assert len(denials) == 2, blocked
        assert all("Operation not permitted" in value or "Permission denied" in value
                   for value in denials.values()), blocked

        rule = home / "rules/asan-git-operations.rules"
        checks = []
        for argv, allowed in (([*runner, "relation"], True), ([*runner, "execute", "a" * 32], True),
                              (["python3", *runner[1:], "writes"], True),
                              ([sys.executable, runner[2], "relation"], False),
                              ([sys.executable, "-c", "pass"], False),
                              ([sys.executable, "-I", str(fixture.bundle / ".agent-policy/runtime/git_operations.py"), "relation"], False),
                              ([*runner, "unsupported"], False)):
            result = subprocess.run([executable, "execpolicy", "check", "--rules", str(rule), "--", *argv],
                                    capture_output=True, text=True, check=True)
            value = json.loads(result.stdout)
            assert (value.get("decision") == "allow") == allowed, (argv, value)
            checks.append({"command": argv, "expected_allow": allowed, "result": value})
        (output_dir / "rules.json").write_text(json.dumps(checks, indent=2))
        version = subprocess.check_output([executable, "--version"], text=True).strip()
        print(f"PASS: {version}; baseline denied; preparation allowed; unapproved execute denied; approved worktree created; direct state write denied; 7 rule checks")
    finally:
        fixture.doCleanups()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    run(parser.parse_args().output_dir)
