from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from agent_policy.core import ProjectConfig, render_project


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary_directory:
        root = Path(temporary_directory)
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
        for relative, content in render_project(project).items():
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)

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
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        output = completed.stdout + completed.stderr
        if completed.returncode != 0:
            raise SystemExit(output)
        if "agent-policy.js" not in output and "AgentPolicyPlugin" not in output:
            raise SystemExit("OpenCode debug output에서 local agent-policy plugin load를 확인하지 못했습니다.\n" + output)
        for permission_fragment in (
            '"git *": "ask"',
            '"npm run build": "ask"',
            '"npm run dev": "ask"',
        ):
            if permission_fragment not in output:
                raise SystemExit(
                    "OpenCode effective config에서 보호 명령 권한을 확인하지 못했습니다: "
                    f"{permission_fragment}\n{output}"
                )
        print("OpenCode local plugin and protected command permissions: PASS")


if __name__ == "__main__":
    main()
