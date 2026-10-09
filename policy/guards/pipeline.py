"""Pipeline gates of an orchestration session.

The parent coordinates and children implement. Where the host identifies a
child call, only implementer children may change source. Each stage leaves its
document before the next one starts, and a commit needs a Watcher PASS for the
exact content being committed.
"""
from __future__ import annotations

import hashlib
import os
import time
from pathlib import Path
from types import ModuleType

_path = Path(__file__).with_name("runtime_loader.py")
_loader = ModuleType("pipeline_loader")
_loader.__file__ = str(_path)
exec(compile(_path.read_bytes(), str(_path), "exec"), _loader.__dict__)
board = _loader.load("work_board")
relations = board.relations
config = relations.config
git, state = relations.git, relations.state
paths = _loader.load("tool_paths")

ORCHESTRATION = board.ORCHESTRATION
CONTRACT = ORCHESTRATION.get("pipeline") or {}
ROLES = frozenset(ORCHESTRATION.get("roles") or ())
RUNNER_ACTIONS = frozenset(ORCHESTRATION.get("runner_actions") or ())
TASK_DIRECTORY = (ORCHESTRATION.get("artifacts") or {}).get("task_directory") or ""
IMPLEMENTERS = frozenset(CONTRACT.get("implementers") or ())
REVIEWER = CONTRACT.get("reviewer") or ""
IDENTIFYING_HOSTS = frozenset(CONTRACT.get("child_identifying_hosts") or ())
DIRECT_EDIT_PHRASE = CONTRACT.get("direct_edit_phrase") or ""
DOCUMENTS: dict[str, list[str]] = CONTRACT.get("documents") or {}
PARENT_DENIAL = ("오케스트레이션 세션의 부모는 source를 직접 수정하지 않습니다. 계획의 배정대로 Publisher·Generator·Refactorer를 "
                 f"호출하세요. 사용자가 `{DIRECT_EDIT_PHRASE}`을 입력하면 다음 사용자 입력 전까지만 직접 수정할 수 있습니다.")


def active() -> bool:
    return os.environ.get(config.INJECT_ROLE_ENV, "") in ROLES


def agent(event: dict) -> tuple[str, str]:
    """(agent id, role name). The id exists only inside a child call on identifying hosts."""
    identifier = event.get("agent_id")
    kind = str(event.get("agent_type") or "").rsplit(":", 1)[-1].casefold()
    return (identifier if isinstance(identifier, str) else ""), kind


def state_path(event: dict, root: Path, host: str) -> Path | None:
    return state.session_path(git.git_common_directory(root), host, paths.event_session_id(event), "pipeline")


def record_prompt(event: dict, root: Path, host: str) -> None:
    """The direct-edit exception lasts for one response: any next user input ends it."""
    prompt = event.get("prompt")
    if not active() or not isinstance(prompt, str):
        return
    normalize = _loader.load("approval_policy").normalize_prompt
    allowed = normalize(prompt) == normalize(DIRECT_EDIT_PHRASE)
    path = state_path(event, root, host)
    if allowed or state.read(path).get("direct_edit"):
        state.write(path, {"direct_edit": allowed, "at": time.time()})
    if allowed:
        print("이번 응답 동안 부모 세션의 source 직접 수정을 허용합니다. 다음 사용자 입력에서 다시 막힙니다. "
              "계획 승인, 단계별 문서와 커밋 전 Watcher 검토는 그대로 적용합니다.")


def document_directory(event: dict, root: Path, host: str, tree: Path) -> Path | None:
    task = board.task_for(root, tree)
    if task:
        return Path(task["plan"]).parent
    return _loader.load("artifact_policy").bound_session_directory(event, root, host)


def missing_documents(directory: Path | None, stage: str) -> list[str]:
    names = DOCUMENTS[stage]
    if directory is None:
        return list(names)
    return [name for name in names
            if not ((path := directory / name).is_file() and not path.is_symlink()
                    and path.read_text(encoding="utf-8", errors="ignore").strip())]


def source_denial(event: dict, root: Path, host: str, trees) -> str | None:
    if not active():
        return None
    identifier, kind = agent(event)
    if host in IDENTIFYING_HOSTS:
        if identifier and kind not in IMPLEMENTERS:
            return (f"{kind or '이'} 하위 에이전트는 source를 수정하지 않습니다. 구현은 Publisher·Generator·Refactorer가 맡습니다. "
                    "필요한 변경은 부모에게 반환하세요.")
        if not identifier and not state.read(state_path(event, root, host)).get("direct_edit"):
            return PARENT_DENIAL
    for tree in trees:
        directory = document_directory(event, root, host, tree)
        missing = missing_documents(directory, "source")
        if missing:
            return (f"source를 수정하기 전에 Planner의 문서가 필요합니다: {', '.join(missing)} "
                    f"(위치: {directory or '세션 산출물 폴더 미정'}). Planner를 호출해 작성하세요.")
    return None


def review_path(root: Path, tree: Path) -> Path:
    return board.directory(root) / "reviews" / (hashlib.sha256(str(tree.resolve()).encode()).hexdigest() + ".json")


def record_verdict(root: Path, cwd: Path, result: str, start: str) -> dict:
    current = board.fingerprint(root, cwd)
    if start != current["fingerprint"]:
        raise RuntimeError("검토 시작 지문과 현재 지문이 다릅니다. 검토 중 대상이 바뀌었으므로 바뀐 부분을 다시 검토한 뒤 "
                           f"현재 지문을 시작 지문으로 기록하세요: {current['fingerprint']}")
    record = {**current, "result": result, "session": board.session(), "at": time.time()}
    state.write(review_path(root, Path(current["worktree"])), record)
    return {"verdict": record}


def verdict_denial(event: dict, root: Path, host: str, cwd: Path) -> str | None:
    if not active():
        return None
    if host in IDENTIFYING_HOSTS and agent(event)[1] != REVIEWER:
        return "검토 판정은 Watcher 하위 에이전트만 기록합니다. Watcher를 호출해 검토하세요."
    tree = paths.git_top_level(cwd)
    if tree is None:
        return "검토한 worktree에서 판정을 기록하세요."
    directory = document_directory(event, root, host, tree)
    missing = missing_documents(directory, "verdict")
    if missing:
        return (f"판정을 기록하기 전에 필요한 문서가 없습니다: {', '.join(missing)} (위치: {directory or '세션 산출물 폴더 미정'}). "
                "implementation-log.md는 구현 에이전트가, review-log.md는 Watcher가 작성합니다.")
    return None


def commit_denial(root: Path, invocations) -> str | None:
    """invocations: (worktree, git arguments). Only content that is not a session log needs review."""
    if not active():
        return None
    for tree, arguments in invocations:
        if not arguments or arguments[0] != "commit":
            continue
        tree = Path(tree)
        changed = [name for name in git.changed_paths(tree) if not name.startswith(config.ARTIFACT_SESSIONS_PREFIXES)]
        if not changed:
            continue
        record = state.read(review_path(root, tree))
        if record.get("result") != "PASS":
            return (f"커밋 전에 Watcher의 PASS 판정이 필요합니다 ({tree}). 포맷과 검증을 마친 뒤 Watcher를 호출해 검토하고 "
                    "판정을 기록하세요." + (" 마지막 판정은 FAIL입니다. 수정 요구를 반영한 뒤 다시 검토받으세요."
                                           if record.get("result") == "FAIL" else ""))
        if record.get("fingerprint") != board.fingerprint(root, tree)["fingerprint"]:
            return (f"Watcher가 검토한 뒤 내용이 바뀌었습니다 ({tree}). 포맷이나 수정을 한 뒤에는 다시 검토받아야 커밋할 수 있습니다.")
    return None


def merge_denial(event: dict, root: Path, host: str, review_id: str) -> str | None:
    if not active():
        return None
    evidence = state.read(relations.directory(root) / "reviews" / (review_id + ".json"))
    source = evidence.get("source") or ""
    trees = relations.branch_worktrees(root, source) if source else []
    directories = [document_directory(event, root, host, tree) for tree in trees] or [
        _loader.load("artifact_policy").bound_session_directory(event, root, host)]
    for directory in directories:
        missing = missing_documents(directory, "merge")
        if missing:
            return (f"병합을 준비하기 전에 작업 결과 문서가 필요합니다: {', '.join(missing)} "
                    f"(위치: {directory or '세션 산출물 폴더 미정'}).")
    return None
