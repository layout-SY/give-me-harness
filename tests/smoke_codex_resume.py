"""Check native Codex thread/list and thread/resume without sending a model turn."""
from __future__ import annotations

import json
import os
import argparse
import fcntl
import pty
import re
import select
import selectors
import shutil
import signal
import struct
import subprocess
import termios
import tempfile
import time
from pathlib import Path

from test_codex_history import CodexHistoryTests


FIXTURE_CONFIG = ('model_provider="fixture"', 'model="fixture"', 'features.apps=false',
                  'model_providers.fixture.name="Fixture"',
                  'model_providers.fixture.base_url="http://127.0.0.1:1/v1"',
                  'model_providers.fixture.wire_api="responses"',
                  'model_providers.fixture.requires_openai_auth=false')


class NativeClient:
    def __init__(self, launch):
        command = [shutil.which("codex"), "app-server", "--stdio"]
        for index, argument in enumerate(launch.command):
            if argument == "--config":
                command.extend([argument, launch.command[index + 1]])
        for value in FIXTURE_CONFIG:
            command.extend(["--config", value])
        self.stderr = tempfile.TemporaryFile(mode="w+")
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=self.stderr, env={**os.environ, **launch.environment},
                                        cwd=launch.project.path)
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.process.stdout, selectors.EVENT_READ)
        self.sequence = 0
        self.buffer = b""
        self.call("initialize", {"clientInfo": {"name": "asan-resume-smoke", "version": "1.0"},
                                 "capabilities": {"experimentalApi": True}})

    def call(self, method, params):
        self.sequence += 1
        self.process.stdin.write((json.dumps({"id": self.sequence, "method": method, "params": params}) + "\n").encode())
        self.process.stdin.flush()
        deadline = time.monotonic() + 25
        while time.monotonic() < deadline:
            if b"\n" in self.buffer:
                line, self.buffer = self.buffer.split(b"\n", 1)
                response = json.loads(line)
                if response.get("id") == self.sequence:
                    if "error" in response:
                        raise AssertionError(response)
                    return response["result"]
                continue
            if self.selector.select(timeout=1):
                content = os.read(self.process.stdout.fileno(), 65536)
                if not content:
                    break
                self.buffer += content
        self.stderr.seek(0)
        raise AssertionError(f"Native request timed out: {method}: {self.stderr.read()[-2000:]}")

    def close(self):
        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()
        self.selector.close()
        self.process.stdin.close()
        self.process.stdout.close()
        self.stderr.close()


def tui_resume(launch, native):
    command = list(launch.command) + ["--no-daemon", "--no-alt-screen", "--dangerously-bypass-hook-trust"]
    # This exception trusts only hooks rendered into the synthetic fixture's temporary home.
    for value in FIXTURE_CONFIG:
        command.extend(["--config", value])
    pid, descriptor = pty.fork()
    if pid == 0:
        os.chdir(launch.project.path)
        os.execvpe(command[0], command, {**os.environ, **launch.environment, "TERM": "xterm-256color"})
    output = b""
    requested = selected = False
    last_trust = 0
    submit_at = 0
    try:
        fcntl.ioctl(descriptor, termios.TIOCSWINSZ, struct.pack("HHHH", 36, 140, 0, 0))
        deadline = time.monotonic() + 35
        while time.monotonic() < deadline:
            if select.select([descriptor], [], [], 0.2)[0]:
                chunk = os.read(descriptor, 65536)
                output += chunk
                if b"\x1b[6n" in chunk:
                    os.write(descriptor, b"\x1b[1;1R")
                if b"\x1b]11;?" in chunk:
                    os.write(descriptor, b"\x1b]11;rgb:0000/0000/0000\x1b\\")
            plain = re.sub(rb"\x1b\[[0-9;?]*[a-zA-Z]", b"", output)
            folder = plain.rfind(b"Folder access")
            ready = plain.rfind(b"Ask Codex to do anything")
            if folder > ready and time.monotonic() - last_trust > 2:
                os.write(descriptor, b"\r")
                last_trust = time.monotonic()
            if ready > folder >= 0 and time.monotonic() - last_trust > 2 and not requested:
                os.write(descriptor, b"/resume")
                submit_at = time.monotonic() + 1
                requested = True
            if submit_at and time.monotonic() >= submit_at:
                os.write(descriptor, b"\r")
                submit_at = 0
            if b"Resume smoke fixture" in plain and requested and not selected:
                os.write(descriptor, b"\r")
                selected = True
            if selected and plain.rfind(b"Ask Codex to do anything") > plain.rfind(b"Resume a previous session") >= 0:
                print("PASS: native TUI /resume displays the fixture and opens its conversation after selection")
                return
        raise AssertionError("TUI /resume did not select the fixture; inspect /private/tmp/asan-resume-tui.log")
    finally:
        Path("/private/tmp/asan-resume-tui.log").write_bytes(output)
        try:
            os.kill(pid, signal.SIGTERM)
            os.waitpid(pid, 0)
        except ProcessLookupError:
            pass
        os.close(descriptor)


def run(tui=False):
    fixture = CodexHistoryTests()
    fixture.setUp()
    client = None
    try:
        legacy = fixture.fixture.state_root / "user-ui/codex-home"
        path = fixture.transcript(legacy, fixture.first_id)
        path.write_text(path.read_text().replace('"model_provider": "openai"', '"model_provider": "fixture"'))
        with path.open("a") as stream:
            stream.write(json.dumps({"timestamp": "2026-09-07T06:25:43.000Z", "type": "event_msg", "payload": {
                "type": "user_message", "message": "Resume smoke fixture", "images": [], "local_images": []}}) + "\n")
            stream.write(json.dumps({"timestamp": "2026-09-07T06:25:43.000Z", "type": "response_item", "payload": {
                "type": "message", "role": "user", "content": [{"type": "input_text", "text": "Resume smoke fixture"}]}}) + "\n")
        fixture.fixture.prepare("codex")
        second = fixture.fixture.prepare("codex")
        client = NativeClient(second)
        rows = client.call("thread/list", {"cwd": str(fixture.fixture.project_root), "modelProviders": [], "limit": 100})
        assert fixture.first_id in [row["id"] for row in rows["data"]], rows
        resumed = client.call("thread/resume", {"threadId": fixture.first_id, "cwd": str(fixture.fixture.project_root),
                                                "excludeTurns": True})
        assert resumed["thread"]["id"] == fixture.first_id, resumed
        print("PASS: native Codex lists and resumes legacy project history from a different isolated home")
        client.close()
        client = None
        if tui:
            tui_resume(fixture.fixture.prepare("codex"), fixture.first_id)
    finally:
        if client:
            client.close()
        fixture.doCleanups()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tui", action="store_true", help="Also exercise the actual /resume picker in a temporary PTY")
    run(parser.parse_args().tui)
