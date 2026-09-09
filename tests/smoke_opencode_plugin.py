from __future__ import annotations

import subprocess
import os
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from agent_policy.core import ProjectConfig
from agent_policy.injection import prepare_injection


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary_directory:
        temporary = Path(temporary_directory).resolve()
        root = temporary / "consumer"
        root.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        project = ProjectConfig(
            id="user-ui",
            name="opencode-smoke",
            path=root,
            commands={
                "dev": "npm run dev",
                "build": "npm run build",
                "lint": "npm run lint",
                "test": "npm run test",
                "preview": "npm run preview",
            },
        )
        launch = prepare_injection(project, "opencode", "logic", build_root=temporary / "build", state_root=temporary / "state")
        environment = {**os.environ, **launch.environment}

        output_file = temporary / "effective-config.json"
        stream = output_file.open("w")
        completed = subprocess.run(
            [
                "opencode",
                "--print-logs",
                "--log-level",
                "DEBUG",
                "debug",
                "config",
            ],
            cwd=root,
            env=environment,
            stdout=stream,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30,
            check=False,
        )
        stream.close()
        effective_text = output_file.read_text()
        output = effective_text + completed.stderr
        if completed.returncode != 0:
            raise SystemExit(output)
        if "agent-policy.js" not in output and "AgentPolicyPlugin" not in output:
            raise SystemExit("OpenCode debug output에서 local agent-policy plugin load를 확인하지 못했습니다.\n" + output)
        effective = json.loads(effective_text)
        Path("/private/tmp/asan-opencode-effective.json").write_text(json.dumps(effective, ensure_ascii=False, indent=2))
        permission = effective.get("permission", {})
        if not isinstance(permission, dict) or not isinstance(permission.get("bash"), dict):
            raise SystemExit("Unexpected effective permission schema: " + json.dumps(permission, ensure_ascii=False))
        for command in ("git *", "npm run build", "npm run dev"):
            if permission["bash"].get(command) != "ask":
                raise SystemExit("OpenCode effective protected command permission mismatch: " + json.dumps(permission, ensure_ascii=False))
        if (root / ".agent-policy").exists() or (root / ".opencode").exists():
            raise SystemExit("inject smoke가 소비자에 정책 사본을 만들었습니다.")
        print("OpenCode actual inject config, plugin and protected command permissions: PASS")


if __name__ == "__main__":
    main()
