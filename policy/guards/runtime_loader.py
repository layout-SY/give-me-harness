"""격리 Python 실행에서도 동일 bundle 내부 모듈만 로드한다."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from types import ModuleType


def load(name: str) -> ModuleType:
    if not name.isidentifier():
        raise RuntimeError("올바르지 않은 runtime 모듈 이름")
    source = Path(__file__).resolve().with_name(f"{name}.py")
    # 원본 직접 실행에서도 호스트 형식은 adapter의 정본에서 읽는다.
    # 렌더된 bundle은 같은 runtime 디렉터리에 설치된 파일만 사용한다.
    if name == "codex_events" and source.parent.name == "guards" and source.parent.parent.name == "policy":
        source = source.parents[2] / "adapters/codex/files/.agent-policy/runtime/codex_events.py"
    key = "_asan_runtime_" + hashlib.sha256(str(source).encode()).hexdigest()
    if key in sys.modules:
        return sys.modules[key]
    module = ModuleType(key)
    module.__file__ = str(source)
    sys.modules[key] = module
    try:
        exec(compile(source.read_bytes(), str(source), "exec"), module.__dict__)
    except BaseException:
        sys.modules.pop(key, None)
        raise
    return module
