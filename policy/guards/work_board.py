"""Work board: task stage, scope and waiting records beside branch relations.

A record coordinates work; it never grants access, locks files or assigns
ownership. Stage changes that describe Git results are checked against the
actual repository before they are stored.
"""
from __future__ import annotations

import os
import posixpath
import re
import time
from pathlib import Path, PurePosixPath
from types import ModuleType

_path = Path(__file__).with_name("runtime_loader.py")
_loader = ModuleType("board_loader")
_loader.__file__ = str(_path)
exec(compile(_path.read_bytes(), str(_path), "exec"), _loader.__dict__)
relations = _loader.load("branch_relations")
config = relations.config
git, state = relations.git, relations.state

CONTRACT = git.RUNTIME_CONTRACT["work_board"]
STAGES: dict[str, str] = dict(CONTRACT["stages"])
RELEASE = frozenset(CONTRACT["release_stages"])
CLOSED = frozenset(CONTRACT["closed_stages"])
LOCATED = frozenset(CONTRACT["located_stages"])
TASK_ID = re.compile(r"[0-9A-Za-z가-힣][0-9A-Za-z가-힣._-]{0,79}")
NOTE = "현황판은 조율 기록입니다. 접근 권한·쓰기 잠금·소유권을 만들지 않으며 실제 Git 상태로 다시 확인하세요."
RESUME = ("다른 세션이 기록한 미완료 작업입니다. 실제 worktree·diff와 작업의 plan.md를 확인하고 사용자에게 확인받은 뒤 "
          "해당 단계부터 이어가세요. 이전 세션의 계획 승인은 승계되지 않으므로 `<작업 ID> 진행`으로 다시 승인받습니다.")
REPLAN = ("변경된 파일만 다시 조사해 계획을 갱신하세요. 이미 조사한 내용은 다시 조사하지 않습니다. "
          "구현은 갱신한 계획의 승인 후 진행하고, 재계획을 마치면 board-set --clear-wait로 대기를 해제하세요.")


def directory(root: Path) -> Path:
    common = git.git_common_directory(root)
    if common is None:
        raise RuntimeError("Git common directory를 확인할 수 없습니다.")
    return state.repository_state(common) / "work-board" / "v1"


def read(root: Path) -> dict:
    board = state.read(directory(root) / "board.json") or {"version": 1, "revision": 0, "tasks": {}}
    if board.get("version") != 1 or not isinstance(board.get("tasks"), dict):
        raise RuntimeError("지원하지 않는 작업 현황판 기록입니다.")
    return board


def session() -> str:
    """Identifies who last updated a record. It is not an owner or a permission."""
    return os.environ.get(state.ASSIGNMENT_ENV, "")


def normalize(root: Path, values) -> list[str]:
    trees = [Path(item["worktree"]).resolve() for item in relations.worktrees(root)]
    result = []
    for value in values or ():
        path = Path(value)
        if path.is_absolute():
            resolved = path.resolve()
            base = next((tree for tree in sorted(trees, key=lambda item: -len(str(item)))
                         if resolved == tree or resolved.is_relative_to(tree)), None)
            if base is None:
                raise RuntimeError(f"현재 프로젝트의 worktree 밖에 있는 경로입니다: {value}")
            relative = resolved.relative_to(base).as_posix()
        else:
            relative = posixpath.normpath(value.replace("\\", "/"))
        if relative.startswith("../") or relative == "..":
            raise RuntimeError(f"저장소 기준 상대 경로를 지정하세요: {value}")
        result.append(relative)
    return sorted(set(result))


def overlaps(left, right) -> list[str]:
    found = set()
    for first in left:
        for second in right:
            if "." in (first, second):
                found.add(second if first == "." else first)
            elif first == second or first.startswith(second.rstrip("/") + "/"):
                found.add(first)
            elif second.startswith(first.rstrip("/") + "/"):
                found.add(second)
    return sorted(found)


def open_tasks(root: Path) -> list[dict]:
    if not (directory(root) / "board.json").is_file():
        return []
    return [task for task in read(root)["tasks"].values() if task["stage"] not in CLOSED]


def task_for(root: Path, tree: Path) -> dict | None:
    """The one open task whose plan governs source changes in this worktree."""
    target = tree.resolve()
    found = [task for task in open_tasks(root)
             if task["plan"] and task["worktree"] and Path(task["worktree"]).resolve() == target]
    return found[0] if len(found) == 1 else None


def plan_path(root: Path, value: str) -> str:
    path = Path(value)
    context = _loader.load("tool_paths").repository_target(root, str(path)) if path.is_absolute() else None
    if (context is None or path.name != "plan.md" or not path.is_file() or path.is_symlink()
            or not context[1].startswith(config.ARTIFACT_SESSIONS_PREFIXES)):
        raise RuntimeError(f"작업의 plan은 세션 산출물 아래에 실제로 있는 plan.md의 절대 경로여야 합니다: {value}")
    return str(path.resolve())


def actual(root: Path, task: dict) -> dict:
    """Current Git facts for a record; the board alone never proves a result."""
    branch = task.get("branch") or ""
    head = relations.oid(root, branch) if branch else ""
    trees = relations.branch_worktrees(root, branch) if head else []
    uncommitted = {}
    for tree in trees:
        changed = git.changed_paths(tree)
        if git.GIT_STATUS_UNAVAILABLE in changed:
            raise RuntimeError(f"변경 상태를 확인할 수 없습니다: {tree}")
        names = sorted(name for name in changed if not name.startswith(config.ARTIFACT_SESSIONS_PREFIXES))
        if names:
            uncommitted[str(tree)] = names
    return {"branch_exists": bool(head), "head": head, "worktrees": [str(tree) for tree in trees],
            "uncommitted": uncommitted}


def verify(root: Path, task: dict, stage: str) -> dict:
    facts = actual(root, task)
    branch = task.get("branch") or ""
    if stage in LOCATED and not facts["branch_exists"]:
        raise RuntimeError(f"{STAGES[stage]} 단계는 실제로 존재하는 작업 branch가 필요합니다: {branch or '미지정'}")
    if stage == "committed" and facts["uncommitted"]:
        raise RuntimeError("커밋되지 않은 변경이 남아 있어 커밋됨으로 기록할 수 없습니다: "
                           + "; ".join(f"{tree}: {', '.join(names)}" for tree, names in facts["uncommitted"].items()))
    if stage == "merged":
        graph = relations.read(root)
        if facts["branch_exists"]:
            node = relations.named(graph, branch)
            parent = graph["nodes"].get(node.get("parent") or "") if node else None
            if not parent or not git.is_ancestor(root, facts["head"], relations.oid(root, parent["name"])):
                raise RuntimeError(f"등록된 직접 부모에 병합된 사실을 확인할 수 없습니다: {branch}")
        elif not any(node["name"] == branch and (node.get("resolution") or {}).get("kind") == "merged"
                     for node in graph["nodes"].values()):
            raise RuntimeError(f"병합 완료 기록을 확인할 수 없습니다: {branch or '미지정'}")
    if stage == "removed" and facts["branch_exists"]:
        raise RuntimeError(f"branch가 아직 남아 있습니다: {branch}")
    return facts


def conflicts(board: dict, task: dict) -> list[dict]:
    mine = task["scope"] + task["shared"]
    result = []
    for other in board["tasks"].values():
        if other["id"] == task["id"] or other["stage"] in CLOSED:
            continue
        paths = overlaps(mine, other["scope"] + other["shared"])
        if paths:
            result.append({"task": other["id"], "title": other["title"], "stage": other["stage"],
                           "branch": other["branch"], "worktree": other["worktree"], "paths": paths})
    return result


def release(root: Path, board: dict, task: dict) -> dict | None:
    """Whether a waiting task may re-plan, and exactly which files changed."""
    wait = task.get("waiting_on")
    if not wait:
        return None
    previous = board["tasks"].get(wait["task"])
    result = {"task": task["id"], "waiting_on": wait["task"], "overlap": wait["overlap"],
              "predecessor_stage": previous["stage"] if previous else None,
              "released": not previous or previous["stage"] in RELEASE}
    if not result["released"]:
        return result
    start, end = wait.get("seen_head") or "", (previous or {}).get("head") or ""
    changed = None
    if start and end:
        found = git._git(root, "diff", "--name-only", "-z", start, end, "--", *(wait["overlap"] or ["."]))
        if found.returncode == 0:
            changed = sorted(filter(None, found.stdout.split("\0")))
    result.update(from_head=start, to_head=end, changed_files=changed, instruction=REPLAN)
    return result


def update(root: Path, identifier: str, *, stage: str | None = None, title: str | None = None,
           branch: str | None = None, worktree: str | None = None, scope=None, shared=None,
           plan: str | None = None, wait_for: str | None = None, overlap=None, clear_wait: bool = False) -> dict:
    if not TASK_ID.fullmatch(identifier):
        raise RuntimeError("작업 ID는 문자·숫자로 시작하는 80자 이내의 이름(문자, 숫자, `.`, `_`, `-`)이어야 합니다.")
    if stage is not None and stage not in STAGES:
        raise RuntimeError("지원하는 단계: " + ", ".join(f"{key}({label})" for key, label in STAGES.items()))
    if worktree is not None and worktree and not Path(worktree).is_absolute():
        raise RuntimeError("worktree는 절대 경로로 지정하세요.")
    now = time.time()
    with state.locked(directory(root) / "board.lock"):
        board = read(root)
        task = board["tasks"].get(identifier)
        if task is None:
            if not stage or not (title or "").strip():
                raise RuntimeError("새 작업은 --title과 --stage를 함께 지정하세요.")
            task = {"id": identifier, "title": "", "stage": "", "branch": "", "worktree": "", "base_head": "",
                    "head": "", "scope": [], "shared": [], "plan": "", "session": "", "waiting_on": None,
                    "history": [], "created_at": now}
        for key, value in (("title", title), ("branch", branch), ("worktree", worktree)):
            if value is not None:
                task[key] = value.strip()
        if plan is not None:
            task["plan"] = plan_path(root, plan.strip()) if plan.strip() else ""
        if scope is not None:
            task["scope"] = normalize(root, scope)
        if shared is not None:
            task["shared"] = normalize(root, shared)
        if stage is not None:
            facts = verify(root, task, stage)
            if facts["branch_exists"]:
                task["head"] = facts["head"]
                task["base_head"] = task["base_head"] or facts["head"]
                if not task["worktree"] and facts["worktrees"]:
                    task["worktree"] = facts["worktrees"][0]
            task["stage"] = stage
            task["history"].append({"stage": stage, "head": task["head"], "session": session(), "at": now})
        if clear_wait:
            task["waiting_on"] = None
        if wait_for is not None:
            previous, seen = board["tasks"].get(wait_for), {identifier}
            if previous is None:
                raise RuntimeError(f"현황판에 없는 선행 작업입니다: {wait_for}")
            cursor = previous
            while cursor:
                if cursor["id"] in seen:
                    raise RuntimeError("작업들이 서로를 기다리게 됩니다. 의존 관계와 대기 이유를 사용자에게 보고하세요.")
                seen.add(cursor["id"])
                cursor = board["tasks"].get((cursor.get("waiting_on") or {}).get("task") or "")
            selected = normalize(root, overlap) if overlap else overlaps(
                task["scope"] + task["shared"], previous["scope"] + previous["shared"])
            task["waiting_on"] = {"task": wait_for, "overlap": selected, "registered_at": now, "notified": False,
                                  "seen_head": actual(root, previous)["head"] or previous["head"] or previous["base_head"]}
        if session() and task["session"] != session():
            if task["session"]:
                task["history"].append({"session_changed": task["session"], "session": session(), "at": now})
            task["session"] = session()
        task["updated_at"] = now
        board["tasks"][identifier] = task
        board["revision"] += 1
        state.write(directory(root) / "board.json", board)
        return {"task": task, "overlaps": conflicts(board, task), "release": release(root, board, task), "note": NOTE}


def wait(root: Path, identifier: str, timeout: float, interval: float = 5.0) -> dict:
    deadline = time.monotonic() + max(0.0, timeout)
    while True:
        board = read(root)
        task = board["tasks"].get(identifier)
        if task is None:
            raise RuntimeError(f"현황판에 없는 작업입니다: {identifier}")
        result = release(root, board, task)
        if result is None:
            raise RuntimeError("대기 중인 선행 작업이 없습니다. board-set --wait-for로 먼저 등록하세요.")
        if result["released"] or time.monotonic() >= deadline:
            result["timed_out"] = not result["released"]
            return result
        time.sleep(interval)


def view(root: Path) -> dict:
    board, graph, mine = read(root), relations.read(root), session()
    live = {key: node for key, node in graph["nodes"].items() if not node.get("deleted")}

    def pending(node: dict) -> bool:
        try:
            return not relations.resolved(root, graph, node)
        except RuntimeError:
            return True  # 식별을 재확인해야 하는 branch는 처리된 것으로 보지 않는다.

    state_of = {key: pending(node) for key, node in live.items()}
    children: dict[str | None, list[dict]] = {}
    for node in sorted(live.values(), key=lambda item: item["name"]):
        children.setdefault(node.get("parent") if node.get("parent") in live else None, []).append(node)
    order: list[str] = []

    def walk(node: dict) -> None:
        for child in children.get(node["id"], []):
            walk(child)
        parent = live.get(node.get("parent") or "")
        if parent and state_of[node["id"]]:
            order.append(f"{node['name']} → {parent['name']}")

    for node in children.get(None, []):
        walk(node)
    registered = {node["name"] for node in live.values()}
    trees = [{"worktree": item["worktree"], "branch": str(item.get("branch", "")).removeprefix("refs/heads/"),
              "registered": str(item.get("branch", "")).removeprefix("refs/heads/") in registered}
             for item in relations.worktrees(root) if "worktree" in item]
    tasks = []
    for task in sorted(board["tasks"].values(), key=lambda item: item.get("updated_at", 0)):
        entry = {key: value for key, value in task.items() if key != "history"}
        entry.update(stage_label=STAGES.get(task["stage"], task["stage"]), closed=task["stage"] in CLOSED,
                     other_session=bool(mine and task["session"] and task["session"] != mine),
                     actual=actual(root, task), release=release(root, board, task))
        tasks.append(entry)
    resumable = [{"task": task["id"], "stage": task["stage_label"], "branch": task["branch"],
                  "worktree": task["worktree"], "plan": task["plan"], "actual": task["actual"]}
                 for task in tasks if not task["closed"] and (task["other_session"] or not task["session"])]
    return {"note": NOTE, "stages": STAGES, "resumable": resumable,
            "resume": RESUME if resumable else "",
            "branches": [{"branch": node["name"], "parent": (live.get(node.get("parent") or "") or {}).get("name"),
                          "purpose": node.get("purpose"), "fork_commit": node.get("fork_commit"),
                          "pending": state_of[node["id"]],
                          "tasks": [task["id"] for task in board["tasks"].values() if task["branch"] == node["name"]]}
                         for node in sorted(live.values(), key=lambda item: item["name"])],
            "merge_order": order, "worktrees": trees, "tasks": tasks}


def needle(path: str) -> str:
    pure = PurePosixPath(path)
    while pure.suffix:
        pure = pure.with_suffix("")
    if pure.name == "index":
        pure = pure.parent
    parts = pure.parts[1:] if len(pure.parts) > 1 and pure.parts[0] == "src" else pure.parts
    return "/".join(parts)


def check(root: Path, cwd: Path, values) -> dict:
    """Shared-item impact: declared scopes plus literal import candidates in other worktrees."""
    selected = normalize(root, values)
    if not selected:
        raise RuntimeError("확인할 경로를 하나 이상 지정하세요.")
    board = read(root)
    tasks = []
    for task in board["tasks"].values():
        paths = overlaps(selected, task["scope"] + task["shared"])
        if paths and task["stage"] not in CLOSED:
            tasks.append({"task": task["id"], "title": task["title"], "stage": task["stage"],
                          "branch": task["branch"], "worktree": task["worktree"], "paths": paths})
    current = _loader.load("tool_paths").git_top_level(cwd)
    excluded = tuple(f":(exclude){prefix}**" for prefix in config.ARTIFACT_SESSIONS_PREFIXES)
    usage, unknown = {}, []
    for item in relations.worktrees(root):
        tree = Path(str(item.get("worktree", ""))).resolve()
        if not item.get("worktree") or item.get("bare") or tree == current or not tree.is_dir():
            continue
        references = {}
        for path in selected:
            text = needle(path)
            if not text:
                continue
            found = git._git(tree, "grep", "-l", "-z", "--untracked", "-F", "-e", text, "--", ".", *excluded)
            if found.returncode > 1:
                unknown.append(str(tree))
                break
            files = sorted(name for name in filter(None, found.stdout.split("\0")) if name != path)
            if files:
                references[path] = {"files": files[:50], "truncated": len(files) > 50}
        if references:
            usage[str(tree)] = {"branch": str(item.get("branch", "")).removeprefix("refs/heads/"),
                                "references": references}
    return {"paths": selected, "tasks": tasks, "usage": usage, "unknown_worktrees": unknown, "note": NOTE,
            "limits": "usage는 경로 문자열 참조 후보입니다. 같은 폴더의 상대 import와 타입·props·API 의미는 직접 확인하세요."}


def fingerprint(root: Path, cwd: Path) -> dict:
    """Review identity of a worktree: HEAD plus staged, unstaged and untracked content."""
    tree = _loader.load("tool_paths").git_top_level(cwd)
    if tree is None or not git.same_git_repository(root, tree):
        raise RuntimeError("현재 프로젝트의 worktree에서 실행하세요.")
    changes, head = relations.content_snapshot(tree), git.head(tree)
    return {"worktree": str(tree), "branch": git.current_branch(tree), "head": head,
            "changed": sorted(changes["files"]), "fingerprint": relations.digest({"head": head, "changes": changes})}


def context(root: Path, identities, *, once: bool = False) -> str:
    """Hook hint for waiting tasks. A hint never blocks and never approves work."""
    try:
        if not (directory(root) / "board.json").is_file():
            return ""
        with state.locked(directory(root) / "board.lock"):
            board = read(root)
            lines, changed = [], False
            for task in board["tasks"].values():
                wait_record = task.get("waiting_on")
                if not wait_record or task["stage"] in CLOSED:
                    continue
                if identities and task["session"] and task["session"] not in identities:
                    continue
                result = release(root, board, task)
                if not result["released"]:
                    if not once:
                        lines.append(f"- {task['id']}: 선행 작업 {wait_record['task']}"
                                     f"({STAGES.get(result['predecessor_stage'], '미확인')})을 기다리는 중입니다.")
                    continue
                if once and wait_record.get("notified"):
                    continue
                files = result["changed_files"]
                detail = ("변경 범위를 계산할 수 없습니다. 선행 작업의 commit을 직접 비교하세요." if files is None else
                          "접점 경로에 변경된 파일이 없습니다. 기존 계획을 그대로 쓸 수 있는지 확인하세요." if not files else
                          f"접점 경로에서 변경된 파일 {len(files)}개: " + ", ".join(files[:40])
                          + (" 외" if len(files) > 40 else ""))
                lines.append(f"- {task['id']}: 선행 작업 {wait_record['task']}의 대기가 풀렸습니다 "
                             f"({result['from_head'][:12] or '?'} → {result['to_head'][:12] or '?'}). {detail} {REPLAN}")
                if once:
                    wait_record["notified"] = changed = True
            if changed:
                state.write(directory(root) / "board.json", board)
            if not once and identities:
                others = [task for task in board["tasks"].values() if task["stage"] not in CLOSED
                          and task["session"] and task["session"] not in identities]
                if others:
                    names = ", ".join(f"{task['id']}({STAGES.get(task['stage'], task['stage'])})" for task in others[:10])
                    lines.append(f"- 다른 세션이 기록한 미완료 작업 {len(others)}개: {names}. "
                                 "이어받으려면 board로 실제 상태를 확인하고 사용자에게 확인받으세요.")
        return "\n".join(["[WORK_BOARD]", *lines]) if lines else ""
    except Exception:
        return ""  # 안내 실패가 훅의 판정이나 사용자 입력을 막지 않는다.
