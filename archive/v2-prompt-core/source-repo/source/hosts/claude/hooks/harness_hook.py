"""Claude Code 호스트 훅 진입점. production UI 범위에 맞춰 인계 문서만 요구한다."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import harness_core


def main() -> None:
    event_name = sys.argv[1] if len(sys.argv) > 1 else ""
    harness_core.run(
        event_name,
        (harness_core.HANDOFF_ARTIFACT,),
        harness_core.REQUIRED_ARTIFACTS,
    )


if __name__ == "__main__":
    main()
