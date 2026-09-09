"""실제 Claude CLI에서 중앙 MCP 주입과 도구 탐색을 검증한다.

임시 개인 설정·소비자·stdio MCP만 사용하며 사용자 prompt나 모델 요청은 보내지 않는다.
실행: python3 tests/smoke_claude_mcp.py [--output-dir /private/tmp/claude-mcp-smoke]
Control protocol: anthropics/claude-agent-sdk-python의 initialize, mcp_status 계약.
"""
from __future__ import annotations

import argparse
import json
import os
import queue
import shutil
import subprocess
import sys
import threading
import time
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch


def serve_fixture() -> None:
    for line in sys.stdin:
        message = json.loads(line)
        if "id" not in message:
            continue
        method = message.get("method")
        if method == "initialize":
            result = {
                "protocolVersion": message["params"]["protocolVersion"],
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "asan-test-fixture", "version": "1.0.0"},
            }
        elif method == "tools/list":
            result = {"tools": [{
                "name": "fixture_read", "description": "Read-only MCP discovery fixture",
                "inputSchema": {"type": "object", "properties": {}},
                "annotations": {"readOnlyHint": True},
            }]}
        else:
            result = {}
        print(json.dumps({"jsonrpc": "2.0", "id": message["id"], "result": result}), flush=True)


def mcp_status(command: list[str], cwd: Path, environment: dict[str, str], directory: Path,
               personal_config: dict | None = None) -> dict:
    directory.mkdir(parents=True)
    environment = dict(environment, CLAUDE_CONFIG_DIR=str(directory / "claude-home"))
    home = Path(environment["CLAUDE_CONFIG_DIR"])
    home.mkdir()
    (home / ".claude.json").write_text(json.dumps(personal_config or {"mcpServers": {}, "projects": {}}))
    messages: queue.Queue[str] = queue.Queue()
    with (directory / "stderr.log").open("w") as error_log:
        process = subprocess.Popen(
            command + ["--print", "--input-format", "stream-json", "--output-format", "stream-json",
                       "--verbose", "--no-session-persistence"],
            cwd=cwd, env=environment, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=error_log, text=True,
        )
        assert process.stdout is not None and process.stdin is not None

        def receive() -> None:
            for line in process.stdout:
                messages.put(line)
            messages.put("")

        reader = threading.Thread(target=receive, daemon=True)
        reader.start()
        transcript: list[dict] = []

        def request(subtype: str) -> dict:
            request_id = f"request-{len(transcript)}-{subtype}"
            process.stdin.write(json.dumps({"type": "control_request", "request_id": request_id,
                                           "request": {"subtype": subtype}}) + "\n")
            process.stdin.flush()
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                line = messages.get(timeout=max(0.1, deadline - time.monotonic()))
                assert line, f"Claude exited: {directory / 'stderr.log'}"
                message = json.loads(line)
                transcript.append(message)
                response = message.get("response", {})
                if message.get("type") == "control_response" and response.get("request_id") == request_id:
                    assert response.get("subtype") == "success", response
                    return response.get("response", {})
            raise AssertionError(f"Claude control timeout: {subtype}")

        try:
            request("initialize")
            deadline = time.monotonic() + 20
            status = request("mcp_status")
            while any(server["status"] == "pending" for server in status.get("mcpServers", [])):
                assert time.monotonic() < deadline, status
                time.sleep(0.1)
                status = request("mcp_status")
            return status
        finally:
            process.stdin.close()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.terminate()
                process.wait(timeout=5)
            reader.join(timeout=2)
            process.stdout.close()
            (directory / "control.json").write_text(json.dumps(transcript, ensure_ascii=False, indent=2))


def run(output_dir: Path | None) -> None:
    from test_injection import InjectionTests

    executable = shutil.which("claude")
    if executable is None:
        raise SystemExit("Claude CLI가 필요합니다.")
    fixture = InjectionTests()
    fixture.setUp()
    try:
        defaults = fixture.root / "mcp.defaults.json"
        defaults.write_text(json.dumps({
            "projects": ["user-ui", "admin-ui"], "roles": ["ui"],
            "mcpServers": {"TalkToFigma": {"type": "stdio", "command": sys.executable,
                           "args": ["-I", str(Path(__file__).resolve()), "--serve-mcp"]}},
        }))
        environment = {key: os.environ[key] for key in ("PATH", "HOME", "TMPDIR", "LANG") if key in os.environ}
        environment.update({
            "ANTHROPIC_API_KEY": "fixture-only", "ANTHROPIC_BASE_URL": "http://127.0.0.1:1",
            "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1", "DISABLE_AUTOUPDATER": "1",
            "DISABLE_TELEMETRY": "1", "DISABLE_ERROR_REPORTING": "1",
        })
        result_root = output_dir or fixture.root / "results"
        results = {}
        with patch("agent_policy.injection.CLAUDE_MCP_DEFAULTS", defaults):
            for project_id in ("user-ui", "admin-ui"):
                fixture.project = replace(fixture.project, id=project_id)
                launch = fixture.prepare("claude", role="ui")
                command = [executable, *launch.command[1:]]
                for enabled in (False, True):
                    arguments = list(command)
                    if not enabled:
                        index = arguments.index("--mcp-config")
                        del arguments[index:index + 2]
                    label = f"{project_id}-{'injected' if enabled else 'legacy'}"
                    status = mcp_status(arguments, fixture.project_root,
                                        {**environment, **launch.environment}, result_root / label)
                    servers = {server["name"]: server for server in status.get("mcpServers", [])}
                    results[label] = status
                    if enabled:
                        assert servers["TalkToFigma"]["status"] == "connected", status
                        assert any("fixture_read" in tool["name"] for tool in servers["TalkToFigma"]["tools"]), status
                    else:
                        assert "TalkToFigma" not in servers, status
                launch = fixture.prepare("claude", role="logic")
                label = f"{project_id}-logic"
                status = mcp_status([executable, *launch.command[1:]], fixture.project_root,
                                    {**environment, **launch.environment}, result_root / label)
                results[label] = status
                assert all(server["name"] != "TalkToFigma" for server in status.get("mcpServers", [])), status
            # Reproduce the reported local-scope registration: normal sources
            # load it, --setting-sources user hides it, explicit injection restores it.
            fixture.project = replace(fixture.project, id="user-ui")
            launch = fixture.prepare("claude", role="ui")
            personal_config = {"mcpServers": {}, "projects": {
                str(fixture.project_root.resolve()): {
                    "hasTrustDialogAccepted": True,
                    "mcpServers": json.loads(defaults.read_bytes())["mcpServers"],
                },
            }}
            for sources, injected in (("user", False), ("user,project,local", False), ("user", True)):
                command = [executable, *launch.command[1:]]
                command[command.index("--setting-sources") + 1] = sources
                if not injected:
                    index = command.index("--mcp-config")
                    del command[index:index + 2]
                label = f"local-scope-{sources}-{'injected' if injected else 'legacy'}"
                status = mcp_status(command, fixture.project_root, {**environment, **launch.environment},
                                    result_root / label, personal_config)
                results[label] = status
                connected = any(server["name"] == "TalkToFigma" and server["status"] == "connected"
                                for server in status.get("mcpServers", []))
                assert connected == (injected or sources != "user"), status
        (result_root / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2))
        version = subprocess.check_output([executable, "--version"], text=True).strip()
        print(f"PASS: {version}; both UI projects connected, tools discovered; "
              "legacy and Logic excluded; reported local-scope failure reproduced and resolved")
    finally:
        fixture.doCleanups()
        fixture.tearDown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--serve-mcp", action="store_true")
    arguments = parser.parse_args()
    if arguments.serve_mcp:
        serve_fixture()
    else:
        run(arguments.output_dir)
