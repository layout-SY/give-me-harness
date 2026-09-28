"""Launcher와 주입 runtime이 공유하는 산출물 폴더 이름 규칙."""
from __future__ import annotations

import unicodedata


def name_key(value: str) -> str:
    """macOS의 Unicode 정규화·대소문자 별칭도 같은 이름으로 보호한다."""
    return unicodedata.normalize("NFC", value).casefold()


def valid_session_name(value: str) -> bool:
    name = unicodedata.normalize("NFC", value)
    return (1 <= len(name) <= 128 and len(name.encode("utf-8")) <= 255
            and name[0].isalnum()
            and all(char.isalnum() or char in "._-" for char in name))
