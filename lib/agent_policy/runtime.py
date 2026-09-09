"""중앙 CLI가 사용하는 동일 runtime 구현을 명시적 경로로 로드한다."""

from pathlib import Path
from types import ModuleType


def load_runtime(name: str) -> ModuleType:
    if name not in {"runtime_state", "event_protocol"}:
        raise ValueError(f"지원하지 않는 runtime 모듈: {name}")
    source = Path(__file__).resolve().parents[2] / "policy/guards" / f"{name}.py"
    module = ModuleType(name)
    module.__file__ = str(source)
    exec(compile(source.read_bytes(), str(source), "exec"), module.__dict__)
    return module
