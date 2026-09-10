"""Session-independent branch identities and integration dependencies.

No record in this module grants access. Resolution describes a specific Git
result, never permission to work on a branch. V3 assignments are not consulted.
"""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from pathlib import Path
from types import ModuleType

_path = Path(__file__).with_name("runtime_loader.py")
_loader = ModuleType("relations_loader")
_loader.__file__ = str(_path)
exec(compile(_path.read_bytes(), str(_path), "exec"), _loader.__dict__)
config = _loader.load("runtime_config")
git = config.branch_guard
state = config.runtime_state


def directory(root: Path) -> Path:
    common = git.git_common_directory(root)
    if common is None:
        raise RuntimeError("Git common directory를 확인할 수 없습니다.")
    return state.repository_state(common) / "branch-relations" / "v1"


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def read(root: Path) -> dict:
    graph = state.read(directory(root) / "graph.json") or {"version": 1, "revision": 0, "nodes": {}}
    if graph.get("version") != 1 or not isinstance(graph.get("nodes"), dict):
        raise RuntimeError("지원하지 않는 브랜치 관계 기록입니다.")
    for identifier, node in graph["nodes"].items():
        if node.get("id") != identifier or any(key in node for key in ("owner", "assignment", "allowed_files")):
            raise RuntimeError("브랜치 관계에 잘못된 식별자 또는 소유권 필드가 있습니다.")
        seen = {identifier}
        parent = node.get("parent")
        while parent:
            if parent in seen or parent not in graph["nodes"]:
                raise RuntimeError("브랜치 관계에 순환 또는 누락된 부모가 있습니다.")
            seen.add(parent)
            parent = graph["nodes"][parent].get("parent")
    return graph


def save(root: Path, graph: dict) -> None:
    graph["revision"] += 1
    state.write(directory(root) / "graph.json", graph)


def named(graph: dict, name: str) -> dict | None:
    matches = [node for node in graph["nodes"].values() if node["name"] == name and not node.get("deleted")]
    if len(matches) > 1:
        raise RuntimeError("같은 이름의 활성 브랜치 식별자가 둘 이상입니다.")
    return matches[0] if matches else None


def oid(root: Path, name: str) -> str:
    return git._output(root, "rev-parse", "--verify", "--end-of-options", f"refs/heads/{name}^{{commit}}")


def birth(root: Path, name: str) -> str:
    """Detect unmediated delete/recreate, without treating ancestry as parentage.

    Reflog expiry is intentionally an identity uncertainty, requiring explicit
    reconciliation; it must not silently attach a new ref to an old task.
    """
    common = git.git_common_directory(root)
    path = common / "logs/refs/heads" / name
    if path.is_symlink():
        raise RuntimeError("브랜치 reflog가 심볼릭 링크입니다.")
    try:
        with path.open("rb") as stream:
            return hashlib.sha256(stream.readline()).hexdigest()
    except FileNotFoundError:
        return ""


def require_live(root: Path, node: dict) -> str:
    value = oid(root, node["name"])
    if node.get("deleted") or not value:
        raise RuntimeError(f"브랜치가 삭제되었거나 이름이 바뀌었습니다. 관계를 확인하세요: {node['name']}")
    if "birth" in node and node["birth"] != birth(root, node["name"]):
        raise RuntimeError(f"브랜치 재생성 또는 reflog 변경으로 식별을 재확인해야 합니다: {node['name']}")
    return value


def worktrees(root: Path) -> list[dict]:
    result = git._git(root, "worktree", "list", "--porcelain", "-z")
    if result.returncode:
        raise RuntimeError("linked worktree 목록을 확인할 수 없습니다.")
    entries, current = [], {}
    for field in result.stdout.split("\0"):
        if not field:
            if current:
                entries.append(current)
                current = {}
        elif " " in field:
            key, value = field.split(" ", 1)
            current[key] = value
        else:
            current[field] = True
    if current:
        entries.append(current)
    return entries


def branch_worktrees(root: Path, name: str) -> list[Path]:
    return [Path(item["worktree"]).resolve() for item in worktrees(root)
            if item.get("branch") == "refs/heads/" + name]


def content_snapshot(root: Path, *, logs: bool = False) -> dict:
    """Staged, unstaged and untracked evidence; no staging or restoration."""
    paths = git.changed_paths(root)
    if git.GIT_STATUS_UNAVAILABLE in paths:
        raise RuntimeError(f"변경 상태를 확인할 수 없습니다: {root}")
    selected = sorted(name for name in paths if logs or not name.startswith(config.ARTIFACT_SESSIONS_PREFIXES))
    files = {}
    for name in selected:
        file = root / name
        data = (str(file.readlink()).encode() if file.is_symlink() else
                file.read_bytes() if file.is_file() else b"<absent>")
        files[name] = hashlib.sha256(data).hexdigest()
    args = ("--", *selected) if selected else ("--", ":(exclude)*")
    return {"files": files,
            "index": git._output(root, "diff", "--cached", "--binary", *args),
            "unstaged": git._output(root, "diff", "--binary", *args)}


def node_snapshot(root: Path, node: dict) -> dict:
    head = require_live(root, node)
    return {"id": node["id"], "name": node["name"], "head": head,
            "revision": node["revision"], "activity": node.get("activity", 0),
            "worktrees": {str(path): content_snapshot(path) for path in branch_worktrees(root, node["name"])}}


def descendants(graph: dict, identifier: str) -> list[dict]:
    result = []
    for node in graph["nodes"].values():
        if node.get("parent") == identifier:
            result.append(node)
            result.extend(descendants(graph, node["id"]))
    return result


def resolved(root: Path, graph: dict, node: dict) -> bool:
    resolution = node.get("resolution")
    if not resolution:
        return False
    # A tombstone or cancellation settles only the recorded task. Descendants
    # that were retained may acquire new work later; do not hide that dependency.
    if any(not resolved(root, graph, child) for child in graph["nodes"].values() if child.get("parent") == node["id"]):
        return False
    if node.get("deleted"):
        return resolution.get("kind") in {"merged", "cancelled"}
    if resolution.get("kind") == "cancelled":
        return resolution.get("snapshot") == node_snapshot(root, node)
    if resolution.get("kind") != "merged" or require_live(root, node) != resolution.get("source_head"):
        return False
    if any(content_snapshot(path)["files"] for path in branch_worktrees(root, node["name"])):
        return False
    return True


def unfinished(root: Path, graph: dict, identifier: str) -> list[str]:
    return [node["name"] for node in graph["nodes"].values()
            if node.get("parent") == identifier and not resolved(root, graph, node)]


def completion_check(root: Path, graph: dict, source: str, target: str) -> tuple[dict, dict]:
    child, parent = named(graph, source), named(graph, target)
    if not child or not parent:
        raise RuntimeError("완료 병합 전에 사용자와 확인한 직접 부모 관계를 등록하세요. 조회·일반 작업은 가능합니다.")
    require_live(root, child)
    require_live(root, parent)
    if child.get("parent") != parent["id"]:
        raise RuntimeError(f"완료 병합은 직접 부모로만 가능합니다: {source} → {target}")
    pending = unfinished(root, graph, child["id"])
    if pending:
        raise RuntimeError("미처리 하위 작업이 있습니다: " + ", ".join(pending))
    return child, parent


def family(graph: dict, node: dict | None) -> str:
    if not node:
        return ""
    while node.get("parent"):
        parent = graph["nodes"][node["parent"]]
        if parent["name"] == "sy-main":
            return node["id"]
        node = parent
    return node["id"]


def transition(root: Path, context_path: Path, worktree: Path) -> str:
    graph = read(root)
    current = named(graph, git.current_branch(worktree))
    selected = family(graph, current)
    if not selected:
        return ""
    previous = state.read(context_path)
    state.write(context_path, {"family": selected, "worktree": str(worktree)})
    if previous.get("family") and previous["family"] != selected:
        name = graph["nodes"][selected]["name"]
        return f"{name} 계열의 {worktree}에서 이어서 작업할 수 있습니다. 문맥 분리가 필요하면 별도 세션도 가능합니다."
    return ""


def register(root: Path, graph: dict, name: str, parent: str | None, fork: str, purpose: str) -> dict:
    if named(graph, name):
        raise RuntimeError("이미 등록된 브랜치입니다. 이름 변경·부모 변경 절차를 사용하세요.")
    parent_node = named(graph, parent) if parent else None
    if name != "sy-main" and not parent_node or name == "sy-main" and parent:
        raise RuntimeError("sy-main 외의 브랜치는 등록된 직접 부모가 필요합니다.")
    head = oid(root, name)
    if not head or not fork or not purpose.strip():
        raise RuntimeError("현재 브랜치, 분기 commit과 작업 목적을 명시하세요.")
    if not git.is_ancestor(root, fork, head) or parent_node and not git.is_ancestor(root, fork, require_live(root, parent_node)):
        raise RuntimeError("분기 commit이 현재 source·parent 이력에 없습니다. 현재 Git 이력을 다시 확인하세요.")
    identifier = uuid.uuid4().hex
    node = {"id": identifier, "name": name, "parent": parent_node["id"] if parent_node else None,
            "fork_commit": fork, "purpose": purpose.strip(), "revision": 1, "activity": 0,
            "birth": birth(root, name), "deleted": False, "resolution": None, "history": []}
    graph["nodes"][identifier] = node
    return node


def reparent(root: Path, graph: dict, node: dict, parent: dict, fork: str) -> None:
    if node["name"] == "sy-main" or parent["id"] == node["id"] or parent in descendants(graph, node["id"]):
        raise RuntimeError("잘못된 순환 부모 관계입니다.")
    if not git.is_ancestor(root, fork, require_live(root, node)) or not git.is_ancestor(root, fork, require_live(root, parent)):
        raise RuntimeError("새 분기 commit이 source·parent 이력에 없습니다.")
    node.setdefault("history", []).append({"kind": "reparent", "parent": node["parent"], "fork_commit": node["fork_commit"], "at": time.time()})
    node.update(parent=parent["id"], fork_commit=fork, revision=node["revision"] + 1, resolution=None)


def integration_denial(root: Path, arguments: tuple[str, ...]) -> str | None:
    """Raw commands cannot bypass completion via a different host/tool/ref command."""
    if not arguments:
        return None
    command = arguments[0]
    if command not in {"merge", "rebase", "cherry-pick", "am", "update-ref", "replace", "filter-branch", "fast-import", "read-tree", "pull", "fetch", "push", "reset", "branch", "switch", "checkout"}:
        return None
    graph = read(root)
    if command == "merge":
        if any(arg in {"--abort", "--quit"} for arg in arguments):
            return None
        refs = [arg for arg in arguments[1:] if not arg.startswith("-")]
        if len(refs) != 1 or any(arg in {"--squash", "--no-commit"} for arg in arguments):
            return "완료 병합 source와 전략을 명시하세요. squash·다중 source 병합은 자동 완료로 인정하지 않습니다."
        source, target = named(graph, refs[0].removeprefix("refs/heads/")), named(graph, git.current_branch(root))
        if source and target and target.get("parent") == source["id"]:
            return None  # parent -> child synchronization, never completion
        try:
            completion_check(root, graph, refs[0].removeprefix("refs/heads/"), git.current_branch(root))
        except RuntimeError as error:
            return str(error)
        return "직접 부모·하위 작업 검사를 통과했습니다. 형제 변경 검토를 포함한 완료 작업을 준비하고 승인받으세요."
    if command in {"rebase", "cherry-pick", "am", "update-ref", "replace", "filter-branch", "fast-import", "read-tree"}:
        if any(arg in {"--abort", "--quit"} for arg in arguments):
            return None
        return "이력 재작성·ref 직접 갱신은 완료 관계 검사를 대신할 수 없습니다. 초기 완료 경로는 승인된 일반 merge를 사용하세요."
    if command in {"pull", "fetch"}:
        if command == "pull" or any(":" in arg for arg in arguments[1:]):
            return "자동 ref 통합 대신 fetch 조회 후 명시적인 source·target을 검토하세요."
    if command == "push":
        for arg in arguments[1:]:
            if arg.startswith("-") or ":" not in arg or arg.startswith(("https:", "ssh:", "file:")):
                continue
            source, target = arg.lstrip("+").split(":", 1)
            if not source:
                continue  # Remote deletion needs its own approval; never cleanup.
            source = git.current_branch(root) if source == "HEAD" else source.removeprefix("refs/heads/")
            target = target.removeprefix("refs/heads/")
            if source != target and graph["nodes"]:
                source_node, target_node = named(graph, source), named(graph, target)
                if (not source_node or not target_node or not resolved(root, graph, source_node)
                        or not git.is_ancestor(root, oid(root, source), oid(root, target))):
                    return "push refspec으로 완료 순서를 우회할 수 없습니다. 먼저 로컬 직접 부모 통합을 검증하세요."
    if command == "reset":
        options = arguments[1:arguments.index("--")] if "--" in arguments else arguments[1:]
        for arg in options:
            if not arg.startswith("-"):
                target = git._output(root, "rev-parse", "--verify", "--end-of-options", arg + "^{commit}")
                if target and target != git.head(root):
                    return "다른 commit으로 branch를 옮기는 reset은 완료 순서를 우회할 수 있습니다. 복구 대상과 관계를 별도로 확인하세요."
    if command == "branch" and any(arg in {"-m", "-M", "--move", "-d", "-D", "--delete", "-f", "--force", "-c", "-C", "--copy"} for arg in arguments):
        values = [value for value in arguments[1:] if not value.startswith("-")]
        if any(named(graph, value) for value in values) or len(values) <= 1 and named(graph, git.current_branch(root)):
            return "브랜치 식별자를 보존하도록 관계 명령의 rename 또는 안전한 완료 정리를 사용하세요."
    if command in {"switch", "checkout"} and any(arg.startswith(("-C", "-B", "--force-create", "--orphan")) for arg in arguments[1:]):
        return "branch를 강제로 교체하면 관계 식별자가 섞일 수 있습니다. 일반 생성·전환 또는 관계 복구를 사용하세요."
    return None
