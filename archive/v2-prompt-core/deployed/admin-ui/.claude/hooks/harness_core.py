"""중앙 프롬프트 하네스의 호스트 중립 판정 로직.

호스트별 진입점은 이벤트를 읽어 이 모듈의 함수를 호출하고 종료 코드로만 응답한다.
차단은 종료 코드 2와 stderr 메시지로 표현하며, 호스트별 JSON 출력 규격에 의존하지 않는다.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

import branch_guard

CENTRAL_ROOT = "~/SynologyDrive/asan-prompt-core"

MANAGED_PREFIXES: tuple[str, ...] = (
    "AGENTS.md",
    "CLAUDE.md",
    ".agents/skills/",
    ".codex/agents/",
    ".codex/harness/",
    ".codex/workflows/",
    ".codex/templates/",
    ".codex/hooks/",
    ".codex/hooks.json",
    ".codex/config.toml",
    ".codex/multi-agent-spec.md",
    ".codex/multi-agent-spec/",
    ".claude/agents/",
    ".claude/harness/",
    ".claude/workflows/",
    ".claude/templates/",
    ".claude/hooks/",
    ".claude/skills/",
    ".claude/settings.json",
    ".claude/multi-agent-spec.md",
    ".claude/multi-agent-spec/",
    ".opencode/agent/",
    ".opencode/plugins/",
    ".harness/roles/",
)

CENTRAL_SOURCE_MAP: tuple[tuple[str, str], ...] = (
    (".agents/skills/", "source/common/skills/"),
    (".harness/roles/", "source/common/roles/"),
    (".codex/", "source/hosts/codex/"),
    (".claude/", "source/hosts/claude/"),
    (".opencode/", "source/hosts/opencode/"),
    ("AGENTS.md", "source/common/AGENTS.md"),
    ("CLAUDE.md", "source/common/CLAUDE.md"),
)

REQUIRED_ARTIFACTS: tuple[str, ...] = (
    "plan.md",
    "exploration.md",
    "implementation-log.md",
    "grill-me-review.md",
    "review-log.md",
    "evaluation-log.md",
    "final-summary.md",
    "portfolio-log.md",
)

HANDOFF_ARTIFACT = "handoff.md"

SESSIONS_RELATIVE = ".codex/logs/sessions"


def repository_root() -> Path | None:
    """현재 작업 디렉터리가 속한 Git 최상위 경로를 반환한다."""

    try:
        completed = subprocess.run(
            ("git", "rev-parse", "--show-toplevel"),
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0:
        return None
    return Path(completed.stdout.strip()).resolve()


def relative_path(root: Path, candidate: str) -> str | None:
    """도구가 대상으로 삼은 경로를 저장소 기준 상대 경로로 정규화한다."""

    if not candidate:
        return None
    path = Path(candidate)
    resolved = (path if path.is_absolute() else root / path).resolve()
    try:
        return resolved.relative_to(root).as_posix()
    except ValueError:
        return None


def central_source_for(relative: str) -> str:
    """프로젝트 경로에 대응하는 중앙 저장소 경로를 계산한다."""

    for project_prefix, central_prefix in CENTRAL_SOURCE_MAP:
        if relative == project_prefix:
            return f"{CENTRAL_ROOT}/{central_prefix}"
        if project_prefix.endswith("/") and relative.startswith(project_prefix):
            return f"{CENTRAL_ROOT}/{central_prefix}{relative[len(project_prefix):]}"
    return f"{CENTRAL_ROOT}/source/"


def is_managed(relative: str) -> bool:
    """중앙에서 배포되어 프로젝트에서 수정할 수 없는 경로인지 판정한다."""

    return any(
        relative == prefix or (prefix.endswith("/") and relative.startswith(prefix))
        for prefix in MANAGED_PREFIXES
    )


def managed_denial(relative: str) -> str:
    """편집이 차단된 경로에 대한 사용자 안내 메시지를 만든다."""

    return (
        "중앙 시스템 프롬프트는 이 프로젝트에서 수정할 수 없습니다.\n"
        f"  대상 : {relative}\n"
        f"  이동 : {central_source_for(relative)}\n\n"
        "중앙 저장소에서 수정한 뒤 다음을 실행하고 세션을 재시작해 주세요.\n"
        f"  python3 {CENTRAL_ROOT}/bin/sync.py deploy --target all\n\n"
        "이 세션 안에서 우회 수정하지 마세요. 필요한 변경 내용과 이유를 사용자에게 전달하세요."
    )


def central_root() -> Path:
    """사용자 홈을 확장한 중앙 저장소 경로를 반환한다."""

    return Path(CENTRAL_ROOT).expanduser().resolve()


def policy_drift(root: Path) -> str | None:
    """현재 프로젝트가 중앙 원본과 다르면 새 세션에 전달할 안내를 만든다."""

    checker = central_root() / "bin/sync.py"
    if not checker.is_file():
        return (
            "중앙 시스템 프롬프트 저장소를 찾을 수 없습니다.\n"
            f"  예상 위치: {central_root()}\n"
            "중앙 저장소를 확인한 뒤 세션을 다시 시작해 주세요."
        )
    try:
        completed = subprocess.run(
            (sys.executable, str(checker), "check", "--path", str(root)),
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        return f"중앙 시스템 프롬프트 정합성 검사를 실행하지 못했습니다: {error}"
    if completed.returncode == 0:
        return None
    detail = "\n".join(part.strip() for part in (completed.stdout, completed.stderr) if part.strip())
    return (
        "중앙 시스템 프롬프트와 현재 프로젝트가 일치하지 않습니다.\n"
        f"{detail}\n\n"
        f"`cd {central_root()}` 후 `python3 bin/sync.py deploy --target all`을 실행하고 세션을 재시작해 주세요."
    )


def is_deployed_hook(root: Path) -> bool:
    """hook 소스가 대상 프로젝트 내부에 배포된 형태인지 확인한다."""

    try:
        relative = Path(__file__).resolve().relative_to(root).as_posix()
    except ValueError:
        return False
    return relative in {
        ".codex/hooks/harness_core.py",
        ".claude/hooks/harness_core.py",
        ".opencode/plugins/harness_core.py",
    }


CENTRAL_WRITABLE: frozenset[str] = frozenset({"build"})


def central_denial(absolute: Path) -> str | None:
    """세션이 중앙 저장소 원본을 직접 고치려는 시도를 막는다.

    중앙에서 수정하더라도 실행 중인 세션에는 반영되지 않으므로, 사용자가 직접 수정하고
    세션을 재시작하는 흐름을 유지한다. 생성물 디렉터리는 예외로 둔다.
    """

    central = central_root()
    try:
        relative = absolute.relative_to(central)
    except ValueError:
        return None
    if relative.parts and relative.parts[0] in CENTRAL_WRITABLE:
        return None
    return (
        "중앙 시스템 프롬프트는 실행 중인 세션에서 수정할 수 없습니다.\n"
        f"  대상 : {central / relative}\n\n"
        "수정해도 이 세션에는 반영되지 않습니다. 필요한 변경 내용과 이유를 사용자에게 전달하고,\n"
        "사용자가 직접 수정한 뒤 세션을 재시작하도록 안내하세요."
    )


def changed_paths(root: Path) -> list[str]:
    """추적 대상과 미추적 파일을 포함한 변경 경로 목록을 반환한다."""

    try:
        completed = subprocess.run(
            ("git", "status", "--porcelain=v1", "--untracked-files=all"),
            capture_output=True,
            text=True,
            timeout=10,
            cwd=root,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if completed.returncode != 0:
        return []
    paths: list[str] = []
    for line in completed.stdout.splitlines():
        entry = line[3:].strip()
        if " -> " in entry:
            entry = entry.split(" -> ", 1)[1]
        if entry:
            paths.append(entry.strip('"'))
    return paths


def requires_artifacts(root: Path) -> bool:
    """산출물을 요구해야 하는 변경이 있었는지 판정한다."""

    for path in changed_paths(root):
        if path.startswith(SESSIONS_RELATIVE):
            continue
        if path.endswith(".DS_Store"):
            continue
        return True
    return False


SESSION_DIR_ENV = "ASAN_SESSION_DIR"
SESSION_ID_KEYS: tuple[str, ...] = ("session_id", "sessionId", "sessionID", "conversation_id")


def session_id(event: dict[str, object]) -> str:
    """호스트가 전달한 세션 식별자를 얻는다. 키 이름은 호스트마다 다르다."""

    for key in SESSION_ID_KEYS:
        value = event.get(key)
        if isinstance(value, str) and value.strip():
            return re.sub(r"[^A-Za-z0-9_-]", "_", value.strip())[:128]
    return ""


def _binding_path(identifier: str) -> Path:
    return central_root() / "state/session-bindings" / f"{identifier}.txt"


def bind_session(event: dict[str, object], root: Path, relative: str) -> None:
    """세션이 산출물 디렉터리에 쓰면 그 귀속을 자동으로 기록한다.

    사람이나 모델이 따로 선언하지 않아도 첫 산출물 작성 시점에 세션과 디렉터리가 묶인다.
    선언 규칙을 지키지 않아 판정이 어긋나는 경우를 없애기 위한 장치다.
    """

    identifier = session_id(event)
    prefix = f"{SESSIONS_RELATIVE}/"
    if not identifier or not relative.startswith(prefix):
        return
    slug = relative[len(prefix):].split("/", 1)[0]
    if not slug:
        return
    destination = _binding_path(identifier)
    payload = f"{root}\n{slug}\n"
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.is_file() and destination.read_text(encoding="utf-8") == payload:
            return
        _ = destination.write_text(payload, encoding="utf-8")
    except OSError:
        return


def bound_session(event: dict[str, object], root: Path) -> Path | None:
    """자동 기록된 귀속에서 이 세션의 산출물 디렉터리를 찾는다."""

    identifier = session_id(event)
    if not identifier:
        return None
    source = _binding_path(identifier)
    try:
        recorded = source.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    if len(recorded) < 2 or recorded[0] != str(root):
        return None
    candidate = root / SESSIONS_RELATIVE / recorded[1]
    return candidate if candidate.is_dir() else None


def declared_session(root: Path) -> Path | None:
    """세션이 자기 산출물 디렉터리를 명시했으면 그것을 사용한다."""

    declared = os.environ.get(SESSION_DIR_ENV)
    if not declared:
        return None
    candidate = Path(declared)
    resolved = (candidate if candidate.is_absolute() else root / candidate).resolve()
    return resolved if resolved.is_dir() else None


def active_sessions(root: Path) -> list[Path]:
    """이번 작업에서 파일이 변경된 세션 디렉터리를 모두 찾는다.

    날짜만으로 판정하면 자정을 넘긴 작업의 산출물을 놓치고, 같은 날 다른 세션이 만든
    디렉터리를 자기 것으로 오인한다. 실제 변경 기록을 근거로 삼는다.
    """

    sessions = root / SESSIONS_RELATIVE
    if not sessions.is_dir():
        return []
    prefix = f"{SESSIONS_RELATIVE}/"
    names: set[str] = set()
    for path in changed_paths(root):
        if not path.startswith(prefix):
            continue
        remainder = path[len(prefix):].split("/", 1)[0]
        if remainder:
            names.add(remainder)
    found = [sessions / name for name in sorted(names)]
    return [entry for entry in found if entry.is_dir()]


def latest_session(root: Path) -> Path | None:
    """가장 최근에 갱신된 세션 디렉터리를 찾는다. 날짜 접두사에 의존하지 않는다."""

    candidates = active_sessions(root)
    if not candidates:
        sessions = root / SESSIONS_RELATIVE
        if not sessions.is_dir():
            return None
        candidates = [entry for entry in sessions.iterdir() if entry.is_dir()]
    if not candidates:
        return None
    return max(candidates, key=lambda entry: entry.stat().st_mtime)


def missing_artifacts(session: Path, required: tuple[str, ...]) -> list[str]:
    """세션 디렉터리에서 비어 있거나 존재하지 않는 산출물을 반환한다."""

    missing: list[str] = []
    for name in required:
        artifact = session / name
        if not artifact.is_file() or len(artifact.read_text(encoding="utf-8").strip()) < 40:
            missing.append(name)
    return missing


def documentation_denial(root: Path, event: dict[str, object], *accepted: tuple[str, ...]) -> str | None:
    """허용되는 산출물 집합 중 하나도 충족하지 못하면 안내 메시지를 반환한다."""

    if not requires_artifacts(root):
        return None
    declared = declared_session(root) or bound_session(event, root)
    if declared is not None:
        candidates = [declared]
    else:
        candidates = active_sessions(root) or (
            [latest_session(root)] if latest_session(root) is not None else []
        )
    for candidate in candidates:
        if any(not missing_artifacts(candidate, names) for names in accepted):
            return None
    session = candidates[-1] if candidates else None
    if session is None:
        expected = " 또는 ".join(", ".join(names) for names in accepted)
        return (
            "변경 작업의 필수 산출물이 없습니다.\n"
            f"  생성할 위치 : {SESSIONS_RELATIVE}/{date.today().isoformat()}-{{task-slug}}/\n"
            f"  필요한 문서 : {expected}\n\n"
            "`.codex/templates/`의 템플릿을 사용해 한국어로 작성한 뒤 작업을 완료하세요."
        )
    shortfalls = [missing_artifacts(session, names) for names in accepted]
    closest = min(shortfalls, key=len)
    return (
        "필수 산출물이 누락되었거나 내용이 비어 있습니다.\n"
        f"  세션 : {session.relative_to(root).as_posix()}\n"
        f"  누락 : {', '.join(closest)}\n\n"
        "`.codex/templates/`의 템플릿을 사용해 한국어로 작성한 뒤 작업을 완료하세요."
    )


def trace(event_name: str, event: dict[str, object]) -> None:
    """진단용으로 수신한 훅 이벤트를 기록한다.

    호스트마다 도구 이름과 페이로드 형태가 달라, 차단이 걸리지 않을 때 실제 입력을 확인하기
    위해 사용한다. `ASAN_HOOK_TRACE` 가 설정된 경우에만 동작한다.
    """

    destination = os.environ.get("ASAN_HOOK_TRACE")
    if not destination:
        return
    record = {
        "event": event_name,
        "tool_name": event.get("tool_name"),
        "keys": sorted(event.keys()),
        "tool_input_keys": sorted(event["tool_input"].keys())
        if isinstance(event.get("tool_input"), dict)
        else None,
        "cwd": os.getcwd(),
    }
    try:
        with open(destination, "a", encoding="utf-8") as stream:
            _ = stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        return


def read_event() -> dict[str, object]:
    """표준 입력의 이벤트 JSON을 읽는다. 형식이 아니면 빈 이벤트로 취급한다."""

    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        event = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return event if isinstance(event, dict) else {}


SHELL_TOOLS: frozenset[str] = frozenset(
    {"shell", "bash", "Bash", "run", "exec", "local_shell", "run_command", "container.exec"}
)

# 셸 명령 중 파일을 실제로 변경하는 형태만 대상으로 삼는다. 조회 명령까지 편집으로 보면
# 정상 작업이 막히므로, 쓰기 의도가 드러나는 패턴만 수집한다.
SHELL_WRITE_PATTERNS: tuple[str, ...] = (
    r"^\*\*\* (?:Add|Update|Delete) File: (.+)$",
    r"^\*\*\* Move to: (.+)$",
    r">>?\s*([^\s|&;<>()]+)",
    r"\btee\s+(?:-a\s+)?([^\s|&;]+)",
    r"\b(?:cp|mv|install)\s+(?:-[^\s]+\s+)*[^\s]+\s+([^\s|&;]+)",
    r"\brm\s+(?:-[^\s]+\s+)*([^\s|&;]+)",
    r"\b(?:truncate|touch)\s+(?:-[^\s]+\s+)*([^\s|&;]+)",
)


def command_text(payload: dict[str, object]) -> str:
    """도구 입력에서 셸 명령 문자열을 얻는다. 호스트에 따라 배열로 오기도 한다."""

    command = payload.get("command")
    if isinstance(command, str):
        return command
    if isinstance(command, list):
        return " ".join(part for part in command if isinstance(part, str))
    return ""


INTERPRETERS: tuple[str, ...] = (
    "python3", "python", "node", "deno", "bun", "perl", "ruby", "php", "osascript",
)

# 인터프리터 인자 안에서 파일 쓰기를 나타내는 신호다. 읽기 전용 실행을 막지 않기 위해
# 쓰기 함수가 함께 나타날 때만 대상 경로를 수집한다.
INTERPRETER_WRITE_MARKERS: tuple[str, ...] = (
    "write_text", "write_bytes", "writeFile", "writeFileSync", "appendFile",
    "appendFileSync", "File.write", "shutil.copy", "shutil.move",
    "os.replace", "os.rename", "os.remove", "unlink(", "rmtree",
)
# `open()` 은 읽기에도 쓰이므로 쓰기 모드가 함께 지정된 경우만 신호로 본다.
OPEN_WRITE_PATTERN = r"""(?:open|fopen)\([^)]*['"][wax]"""


def _interpreter_targets(command: str) -> list[str]:
    """인터프리터를 통한 파일 쓰기의 대상 경로를 찾는다.

    `python3 -c "...write_text..."` 나 힙독처럼 셸 리다이렉션을 쓰지 않는 쓰기는
    일반 패턴으로 잡히지 않는다. 인터프리터 호출과 쓰기 신호가 함께 있을 때에 한해
    인자 안의 경로 문자열을 후보로 수집한다.
    """

    if not any(re.search(rf"(?:^|[\s|&;(]){name}\b", command) for name in INTERPRETERS):
        return []
    writes = any(marker in command for marker in INTERPRETER_WRITE_MARKERS) or bool(
        re.search(OPEN_WRITE_PATTERN, command)
    )
    if not writes:
        return []
    # 쓰기 함수 호출의 인자에서만 경로를 뽑는다. 명령 전체를 훑으면 실행 인자로
    # 넘어간 스크립트 경로까지 수정 대상으로 오인한다.
    found: list[str] = []
    for pattern in (
        r"""(?:open|fopen)\(\s*['"]([^'"]+)['"]\s*,\s*['"][wax]""",
        r"""Path\(\s*['"]([^'"]+)['"]\s*\)\s*\.\s*write_""",
        r"""(?:writeFileSync|writeFile|appendFileSync)\(\s*['"]([^'"]+)['"]""",
        r"""(?:os\.replace|os\.rename|shutil\.(?:copy\w*|move))\([^,]+,\s*['"]([^'"]+)['"]""",
        r"""(?:os\.remove|os\.unlink)\(\s*['"]([^'"]+)['"]""",
    ):
        for match in re.finditer(pattern, command):
            candidate = match.group(1)
            if candidate and not candidate.startswith("/dev/"):
                found.append(candidate)
    return found


def _inplace_edit_targets(command: str) -> list[str]:
    """`sed -i` 처럼 인자 구성이 가변적인 제자리 편집의 대상을 찾는다.

    옵션과 스크립트 위치가 플랫폼마다 달라 정규식으로 자리를 특정하기 어렵다.
    파이프와 명령 구분자로 나눈 뒤 해당 세그먼트의 마지막 토큰을 대상으로 본다.
    """

    found: list[str] = []
    for segment in re.split(r"[|&;]+", command):
        if not re.search(r"\bsed\b", segment):
            continue
        if not re.search(r"(?:^|\s)-i(?:\s|$|[^\s-])", segment):
            continue
        tokens = segment.split()
        if tokens:
            found.append(tokens[-1].strip("'\""))
    return found


def shell_targets(command: str) -> list[str]:
    """셸 명령에서 쓰기 대상 경로를 추출한다."""

    found: list[str] = _inplace_edit_targets(command) + _interpreter_targets(command)
    for pattern in SHELL_WRITE_PATTERNS:
        for match in re.finditer(pattern, command, flags=re.MULTILINE):
            candidate = match.group(1).strip().strip("'\"")
            if candidate and not candidate.startswith("/dev/"):
                found.append(candidate)
    return found


def tool_targets(event: dict[str, object]) -> tuple[str, ...]:
    """편집 계열 도구가 대상으로 삼은 모든 파일 경로를 추출한다."""

    payload = event.get("tool_input")
    if not isinstance(payload, dict):
        return ()
    targets: list[str] = []
    for key in ("file_path", "filePath", "path", "notebook_path", "notebookPath"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            targets.append(value)
    name = event.get("tool_name")
    command = command_text(payload)
    if command and (name == "apply_patch" or (isinstance(name, str) and name in SHELL_TOOLS)):
        targets.extend(shell_targets(command))
    return tuple(dict.fromkeys(targets))


def is_edit_tool(event: dict[str, object]) -> bool:
    """파일을 변경하는 도구인지 판정한다."""

    name = event.get("tool_name")
    if not isinstance(name, str):
        return False
    return name in {
        "Write",
        "Edit",
        "MultiEdit",
        "NotebookEdit",
        "apply_patch",
        "edit",
        "write",
    } or name in SHELL_TOOLS


def block(message: str) -> None:
    """차단 메시지를 출력하고 종료 코드 2로 종료한다."""

    print(message, file=sys.stderr)
    raise SystemExit(2)


def allow() -> None:
    """허용을 나타내는 종료 코드 0으로 종료한다."""

    raise SystemExit(0)


def run(event_name: str, *accepted: tuple[str, ...]) -> None:
    """호스트 진입점이 호출하는 공통 처리 흐름."""

    event = read_event()
    trace(event_name, event)
    root = repository_root()
    if root is None:
        allow()
    if event_name == "SessionStart":
        messages: list[str] = []
        if is_deployed_hook(root):
            warning = policy_drift(root)
            if warning is not None:
                messages.append(warning)
        context = branch_guard.branch_context(root)
        if context:
            messages.append(context)
        if messages:
            print("\n\n".join(messages))
        allow()
    if event_name == "BranchContext":
        context = branch_guard.branch_context(root)
        if context:
            print(context)
        allow()
    if event_name == "PreToolUse":
        if not is_edit_tool(event):
            allow()
        targets = tool_targets(event)
        relative_targets: list[str] = []
        for target in targets:
            candidate = Path(target)
            absolute = (candidate if candidate.is_absolute() else root / candidate).resolve()
            relative_target = relative_path(root, target)
            if relative_target is not None:
                relative_targets.append(relative_target)
                bind_session(event, root, relative_target)
            denial = central_denial(absolute)
            if denial is not None:
                block(denial)
            relative = relative_path(root, target)
            if relative is not None and is_managed(relative):
                block(managed_denial(relative))
        payload = event.get("tool_input")
        command = command_text(payload) if isinstance(payload, dict) else ""
        name = event.get("tool_name")
        denial = branch_guard.pre_tool_denial(
            root,
            command,
            tuple(relative_targets),
            isinstance(name, str) and name in SHELL_TOOLS,
        )
        if denial is not None:
            block(denial)
        allow()
    if event_name == "Stop":
        if event.get("stop_hook_active") is True:
            allow()
        denial = documentation_denial(root, event, *accepted)
        if denial is not None:
            block(denial)
        allow()
    allow()
