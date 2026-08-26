#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Final

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hook_common import emit_user_prompt_allow, parse_identity, prompt_text, read_event, update_state

APPROVAL_PHRASES: Final = frozenset(
    {
        "진행",
        "진행해줘",
        "작업 진행",
        "승인",
        "proceed",
        "approved",
        "go ahead",
    }
)


def normalize_approval_text(text: str) -> str:
    return " ".join(text.casefold().split())


def has_explicit_approval(text: str) -> bool:
    return normalize_approval_text(text) in APPROVAL_PHRASES


def main() -> None:
    event = read_event()
    identity = parse_identity(event, "UserPromptSubmit")
    if identity is None:
        emit_user_prompt_allow()
        return
    approved = has_explicit_approval(prompt_text(event))
    update_state(identity, approval=approved)
    emit_user_prompt_allow()


if __name__ == "__main__":
    main()
