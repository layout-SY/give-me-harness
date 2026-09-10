"""Approve immutable operations, then recheck under a short execution lock.

Hosts do not need to rewrite tool input: raw Git mutations are prepared by the
hook and executed via this exact bundled entrypoint. No shell is evaluated here.
The lock exists only while a process is changing Git, never for a session's life.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import time
import uuid
from pathlib import Path
from types import ModuleType

_path = Path(__file__).with_name("runtime_loader.py")
_loader = ModuleType("operations_loader")
_loader.__file__ = str(_path)
exec(compile(_path.read_bytes(), str(_path), "exec"), _loader.__dict__)
relations = _loader.load("branch_relations")
review = _loader.load("integration_review")
config = relations.config
git, state = relations.git, relations.state


def operation_path(root: Path, identifier: str) -> Path:
    if not re.fullmatch(r"[a-f0-9]{32}", identifier):
        raise RuntimeError("올바르지 않은 실행 기록 ID입니다.")
    return relations.directory(root) / "operations" / (identifier + ".json")


def load(root: Path, identifier: str) -> dict:
    value = state.read(operation_path(root, identifier))
    if not value or value.get("repository") != str(git.git_common_directory(root)):
        raise RuntimeError("현재 프로젝트의 실행 기록이 아닙니다.")
    return value


def save(root: Path, operation: dict) -> dict:
    state.write(operation_path(root, operation["id"]), operation)
    return operation


def base(root: Path, cwd: Path, kind: str) -> dict:
    if not git.same_git_repository(root, cwd):
        raise RuntimeError("현재 프로젝트 밖에서 Git 작업을 준비할 수 없습니다.")
    return {"version": 1, "id": uuid.uuid4().hex, "repository": str(git.git_common_directory(root)),
            "cwd": str(cwd.resolve()), "kind": kind, "created_at": time.time(), "stage": "prepared"}


def command(operation: dict) -> str:
    return shlex.join([sys.executable, "-I", str(Path(__file__).resolve()), "execute", operation["id"]])


def invocation(value: str) -> list[str] | None:
    try:
        words = shlex.split(value)
    except ValueError:
        return None
    if len(words) >= 4 and Path(words[0]).name.startswith("python") and words[1] == "-I" and Path(words[2]).resolve() == Path(__file__).resolve():
        if any(word in {";", "&&", "||", "|"} for word in words):
            raise RuntimeError("보호 실행기는 단일 명령으로 호출하세요.")
        return words[3:]
    if "git_operations.py" in value:
        raise RuntimeError("현재 bundle의 git_operations.py를 python -I로 직접 실행하세요.")
    return None


def prepare_git(root: Path, cwd: Path, value: str, host: str, event: dict) -> dict:
    boundary = _loader.load("project_boundary")
    denial = boundary.command_denial(root, value, cwd)
    if denial:
        raise RuntimeError(denial)
    contexts = git.shell_command_contexts(value, cwd)
    invocations = git.git_invocations(root, value, cwd)
    if not invocations or contexts is None or any(Path(words[0]).name not in {"git", "cd"} for _, words in contexts):
        raise RuntimeError("실행할 Git 명령만 명시하세요. 셸 스크립트·동적 wrapper는 지원하지 않습니다.")
    lexer = shlex.shlex(value, posix=True, punctuation_chars=";&|<>")
    lexer.whitespace_split = True
    if any(word in {";", "||", "|", "&", ">", "<", ">>", "<<"} for word in lexer):
        raise RuntimeError("Git 실행은 단일 명령 또는 순서가 명확한 &&·개행 목록으로 준비하세요.")
    denial = _loader.load("shared_git").git_denial(event, root, host, value, cwd)
    if denial:
        raise RuntimeError(denial)
    for item in invocations:
        args = item.arguments
        if args[0] == "worktree" and len(args) > 1 and args[1] in {"remove", "prune", "repair", "move", "lock", "unlock"}:
            raise RuntimeError("worktree 삭제·이동은 경로와 보존 조건을 확인하는 완료 정리 절차를 사용하세요.")
        if args[0] == "push" and any(arg in {"--all", "--mirror", "--tags"} or "*" in arg for arg in args):
            raise RuntimeError("승인할 push source:target refspec을 각각 명시하세요.")
        if args[0] in {"commit", "add"} and any(arg.startswith("--pathspec-from-file") for arg in args):
            raise RuntimeError("stage·commit 경로를 간접 파일 대신 직접 명시하세요.")
    operation = base(root, cwd, "git")
    operation.update(command=value, invocations=[{"root": str(item.root), "cwd": str(item.working_directory or item.root), "args": list(item.arguments)} for item in invocations],
        fingerprint=_loader.load("approval_policy").operation_fingerprint(cwd, value))
    # Repeated preparation of the same still-pending operation does not create
    # another approval question. Completed operations get a fresh execution ID.
    operation["id"] = relations.digest([operation["repository"], str(cwd), operation["fingerprint"]])[:32]
    previous = state.read(operation_path(root, operation["id"]))
    if previous and previous.get("stage") == "prepared":
        return previous
    if previous:
        operation["id"] = uuid.uuid4().hex
    return save(root, operation)


def reserve_write(root: Path, event: dict, host: str, locations: list[Path]) -> None:
    protocol = _loader.load("event_protocol")
    call = protocol.tool_call_id(event)
    if not call:
        raise RuntimeError("변경 도구의 실행 ID를 확인할 수 없습니다.")
    with state.locked(relations.directory(root) / "locks/git.lock"):
        for location in set(locations):
            identifier = relations.digest([host, event.get("session_id"), call, str(location)])
            state.write(relations.directory(root) / "writes" / (identifier + ".json"),
                {"host": host, "session": event.get("session_id"), "call": call, "worktree": str(location), "created_at": time.time()})


def complete_write(root: Path, event: dict, host: str) -> None:
    protocol = _loader.load("event_protocol")
    if protocol.tool_outcome(event) is None:
        return  # Unknown is not success; recovery explicitly verifies it.
    call = protocol.tool_call_id(event)
    for path in (relations.directory(root) / "writes").glob("*.json"):
        pending = state.read(path)
        if pending.get("host") == host and pending.get("session") == event.get("session_id") and pending.get("call") == call:
            path.unlink(missing_ok=True)


def prepare_write_recovery(root: Path, cwd: Path, identifier: str, reason: str) -> dict:
    if not re.fullmatch(r"[a-f0-9]{64}", identifier) or not reason.strip():
        raise RuntimeError("결과 미확인 도구 ID와 실제 종료를 확인한 근거를 명시하세요.")
    pending = state.read(relations.directory(root) / "writes" / (identifier + ".json"))
    if not pending:
        raise RuntimeError("미확인 도구 실행 기록이 없습니다.")
    location = Path(pending["worktree"])
    if not git.same_git_repository(root, location):
        raise RuntimeError("다른 프로젝트의 실행 기록입니다.")
    operation = base(root, cwd, "write-recovery")
    operation.update(write_id=identifier, pending=pending, reason=reason,
                     snapshot={"head": git.head(location), "changes": relations.content_snapshot(location, logs=True)})
    operation["fingerprint"] = relations.digest(operation)
    return save(root, operation)


def prepare_completion(root: Path, cwd: Path, evidence: dict, report: dict) -> dict:
    review.require_report(evidence, report)
    if evidence["repository"] != str(git.git_common_directory(root)) or not review.current(root, evidence):
        raise RuntimeError("검토한 저장소 또는 변경이 달라졌습니다. 재검토하세요.")
    allowed = set(git.RUNTIME_CONTRACT["git"]["validation_commands"])
    if any(value not in allowed for value in evidence["verification"]):
        raise RuntimeError("프로젝트에 등록된 검증 명령을 사용하세요.")
    targets = relations.branch_worktrees(root, evidence["target"])
    sources = relations.branch_worktrees(root, evidence["source"])
    if len(targets) > 1 or len(sources) > 1:
        raise RuntimeError("source·target이 여러 worktree에 checkout되어 있습니다. 실제 실행 위치를 정리하세요.")
    target = targets[0] if targets else cwd
    operation = base(root, cwd, "completion")
    operation.update(evidence=evidence, report=report, target_worktree=str(target),
                     source_worktree=str(sources[0]) if sources else None,
                     fingerprint=relations.digest([evidence, report, str(target), [str(item) for item in sources]]))
    operation["target_before"] = {"branch": git.current_branch(target), "head": git.head(target),
                                  "changes": relations.content_snapshot(target)}
    operation["fingerprint"] = relations.digest([operation["fingerprint"], operation["target_before"]])
    return save(root, operation)


def prepare_relation(root: Path, cwd: Path, action: str, name: str, parent: str | None, fork: str | None,
                     purpose: str = "", new_name: str | None = None, worktree: str | None = None) -> dict:
    if action not in {"register", "create", "rename", "reparent", "cancel", "retire"}:
        raise RuntimeError("지원하지 않는 관계 변경입니다.")
    graph = relations.read(root)
    operation = base(root, cwd, "relation")
    operation.update(action=action, name=name, parent=parent, fork=fork, purpose=purpose,
                     new_name=new_name, worktree=worktree, graph=graph,
                     refs={item["name"]: relations.oid(root, item["name"]) for item in graph["nodes"].values() if not item.get("deleted")})
    # Include unregistered branches too. User confirms parentage based on these
    # exact commits, not on a stale session assignment or branch naming scheme.
    operation["refs"].update({ref: relations.oid(root, ref) for ref in (name, parent) if ref})
    operation["fingerprint"] = relations.digest(operation)
    return save(root, operation)


def validate(root: Path, operation: dict) -> None:
    if operation["kind"] == "git":
        actual = _loader.load("approval_policy").operation_fingerprint(Path(operation["cwd"]), operation["command"])
        if actual != operation["fingerprint"]:
            raise RuntimeError("승인 후 관련 Git 변경이 달라졌습니다. 재검토·재승인이 필요합니다.")
    elif operation["kind"] == "completion":
        if not review.current(root, operation["evidence"]):
            raise RuntimeError("승인 후 관련 HEAD·변경·하위 작업이 달라졌습니다. 형제 검토를 갱신하세요.")
        relations.completion_check(root, relations.read(root), operation["evidence"]["source"], operation["evidence"]["target"])
        target = Path(operation["target_worktree"])
        if operation["target_before"] != {"branch": git.current_branch(target), "head": git.head(target), "changes": relations.content_snapshot(target)}:
            raise RuntimeError("승인 후 통합 worktree의 실제 변경이 달라졌습니다.")
    elif operation["kind"] == "relation":
        if relations.read(root) != operation["graph"] or any(relations.oid(root, ref) != head for ref, head in operation["refs"].items()):
            raise RuntimeError("승인 후 브랜치 관계 또는 commit이 변경되었습니다.")
    elif operation["kind"] == "write-recovery":
        pending = state.read(relations.directory(root) / "writes" / (operation["write_id"] + ".json"))
        location = Path(operation["pending"]["worktree"])
        if pending != operation["pending"] or operation["snapshot"] != {"head": git.head(location), "changes": relations.content_snapshot(location, logs=True)}:
            raise RuntimeError("종료 확인 후 도구 기록 또는 변경이 달라졌습니다. 복구 근거를 재검토하세요.")


def grant(root: Path, operation: dict, host: str, event: dict) -> None:
    # This is an operation execution reservation, not a branch owner/claim.
    state.write(operation_path(root, operation["id"]).with_suffix(".grant.json"),
        {"fingerprint": operation["fingerprint"], "host": host, "event": event,
         "assignment": os.environ.get("ASAN_AGENT_POLICY_ASSIGNMENT", ""),
         "created_at": time.time(), "cwd": operation["cwd"]})


def run(root: Path, args: list[str]) -> subprocess.CompletedProcess:
    result = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"Git 실패: {result.returncode}")
    return result


def pin(root: Path, operation: dict, label: str, head: str) -> None:
    ref = f"refs/asan-policy/integrations/{operation['id']}/{label}"
    existing = git._output(root, "rev-parse", "--verify", ref)
    if existing and existing != head:
        raise RuntimeError("보존 ref가 다른 commit을 가리킵니다. 실행 기록을 확인하세요.")
    if not existing:
        run(root, ["update-ref", ref, head, "0" * len(head)])


def apply_relation(root: Path, operation: dict) -> None:
    graph = relations.read(root)
    action, name = operation["action"], operation["name"]
    node = relations.named(graph, name)
    if action == "create":
        parent = relations.named(graph, operation["parent"] or "")
        if not parent or relations.oid(root, name):
            raise RuntimeError("등록된 직접 부모와 사용하지 않는 새 브랜치 이름이 필요합니다.")
        if operation["fork"] != relations.require_live(root, parent):
            raise RuntimeError("새 작업은 승인한 부모의 현재 commit에서 분기하세요.")
        candidate = operation.get("worktree")
        if not candidate:
            raise RuntimeError("병렬 작업 생성에는 별도 linked worktree 경로를 명시하세요.")
        destination = Path(candidate).resolve()
        if _loader.load("project_boundary").foreign_repository(root, destination):
            raise RuntimeError("다른 프로젝트 안에 linked worktree를 생성할 수 없습니다.")
        if destination.exists() or destination == root or any(destination.is_relative_to(Path(item["worktree"])) for item in relations.worktrees(root)):
            raise RuntimeError("새 linked worktree는 기존 작업 경로와 겹치지 않아야 합니다.")
        run(root, ["worktree", "add", "-b", name, str(destination), operation["fork"]])
    if action in {"create", "register"}:
        node = relations.register(root, graph, name, operation["parent"], operation["fork"], operation["purpose"])
        pin(root, operation, "fork", node["fork_commit"])
    else:
        if not node:
            raise RuntimeError("등록된 브랜치를 확인할 수 없습니다.")
        if action == "retire":
            if relations.oid(root, name) or not node.get("resolution") or relations.unfinished(root, graph, node["id"]):
                raise RuntimeError("삭제가 확인되고 완료·취소 기록과 미처리 자식이 없는 브랜치만 퇴역할 수 있습니다.")
            node["deleted"] = True
        else:
            relations.require_live(root, node)
        if action == "rename":
            new_name = operation["new_name"]
            if not new_name or relations.named(graph, new_name) or relations.oid(root, new_name):
                raise RuntimeError("이미 사용 중이거나 잘못된 새 브랜치 이름입니다.")
            run(root, ["branch", "-m", name, new_name])
            node.setdefault("history", []).append({"kind": "rename", "name": name, "at": time.time()})
            node.update(name=new_name, birth=relations.birth(root, new_name), revision=node["revision"] + 1)
        elif action == "reparent":
            parent = relations.named(graph, operation["parent"] or "")
            if not parent:
                raise RuntimeError("새 직접 부모를 등록하세요.")
            relations.reparent(root, graph, node, parent, operation["fork"])
        elif action == "cancel":
            if relations.unfinished(root, graph, node["id"]):
                raise RuntimeError("미처리 하위 작업을 먼저 취소·보존하거나 부모를 변경하세요.")
            snapshot = relations.node_snapshot(root, node)
            pin(root, operation, "preserved", snapshot["head"])
            # Preserve all dirty evidence, including untracked contents, before
            # removing this task as a dependency. Branch and worktree stay intact.
            operation["preserved"] = {str(path): archive(root, path, operation) for path in relations.branch_worktrees(root, name)}
            node["resolution"] = {"kind": "cancelled", "snapshot": snapshot, "operation": operation["id"]}
    relations.save(root, graph)


def assert_idle(root: Path, locations: list[Path]) -> None:
    for path in (relations.directory(root) / "writes").glob("*.json"):
        pending = state.read(path)
        if any(Path(pending["worktree"]) == location for location in locations):
            raise RuntimeError("해당 worktree에 실행 중이거나 결과 미확인인 변경 도구가 있습니다: " + path.stem)


def merge(root: Path, operation: dict) -> None:
    evidence = operation["evidence"]
    source, target = evidence["source"], evidence["target"]
    target_path = Path(operation["target_worktree"])
    source_paths = relations.branch_worktrees(root, source)
    assert_idle(root, [target_path, *source_paths])
    for path in [target_path, *source_paths]:
        if relations.content_snapshot(path)["files"]:
            raise RuntimeError("source 또는 target에 미커밋 변경이 있습니다. 다른 작업을 stage·commit하지 않고 병합을 보류합니다.")
    if git._output(target_path, "ls-files", "-u"):
        raise RuntimeError("미해결 Git 충돌이 있습니다.")
    if git.current_branch(target_path) != target:
        run(target_path, ["switch", target])
    for label in ("source", "target"):
        pin(root, operation, label, evidence[label + "_head"])
    operation["stage"] = "merging"
    save(root, operation)
    args = ["merge", "--ff-only", evidence["source_head"]] if evidence["strategy"] == "ff-only" else [
        "merge", "--no-ff", "--no-edit", "-m", f"merge: {source} 작업을 {target}에 통합", evidence["source_head"]]
    run(target_path, args)
    verify_result(root, operation)


def verify_result(root: Path, operation: dict) -> None:
    evidence = operation["evidence"]
    result = relations.oid(root, evidence["target"])
    target_path = Path(operation["target_worktree"])
    if git._output(target_path, "ls-files", "-u") or not git.is_ancestor(root, evidence["source_head"], result):
        raise RuntimeError("실제 통합 결과를 확인할 수 없습니다. 병합을 되돌리지 않고 기록을 보존합니다.")
    parents = git._output(root, "rev-list", "--parents", "-n", "1", result).split()[1:]
    expected = result == evidence["source_head"] if evidence["strategy"] == "ff-only" else parents == [evidence["target_head"], evidence["source_head"]]
    # Already contained but explicitly completed children still need a durable
    # completion request; an unchanged target is a verified no-op integration.
    expected = expected or result == evidence["target_head"] and git.is_ancestor(root, evidence["source_head"], evidence["target_head"])
    if not expected:
        raise RuntimeError("실제 병합 commit이 승인한 source·target·전략과 다릅니다.")
    operation.update(stage="merged", result=result)
    pin(root, operation, "result", result)
    graph = relations.read(root)
    node = graph["nodes"][evidence["source_id"]]
    if node.get("resolution") and node["resolution"].get("operation") != operation["id"]:
        reviewed = evidence["snapshot"][node["id"]]["relation"].get("resolution")
        if node["resolution"] != reviewed:
            raise RuntimeError("검토 이후의 다른 완료·취소 기록을 덮어쓸 수 없습니다. 이 실행 결과를 별도로 대조하세요.")
    node["resolution"] = {"kind": "merged", "source_head": evidence["source_head"], "target_head": evidence["target_head"],
                          "result": result, "operation": operation["id"], "verification": "pending",
                          "target_id": evidence["target_id"], "fork_commit": node["fork_commit"],
                          "source_name": evidence["source"], "target_name": evidence["target"]}
    integrations = node.setdefault("integrations", [])
    if not any(item["operation"] == operation["id"] for item in integrations):
        integrations.append(dict(node["resolution"]))
    relations.save(root, graph)
    save(root, operation)


def archive(root: Path, candidate: Path, operation: dict, *, mirror: bool = True) -> dict:
    """Immutable operation evidence plus the existing non-deleting log mirror."""
    files = set(relations.content_snapshot(candidate, logs=True)["files"])
    for host in git.RUNTIME_CONTRACT["hosts"].values():
        log_root = candidate / host["artifact_root"]
        if log_root.is_symlink():
            raise RuntimeError("로그 보존 대상이 심볼릭 링크입니다.")
        if log_root.exists():
            files.update(str(path.relative_to(candidate)) for path in log_root.rglob("*") if path.is_file() or path.is_symlink())
    manifest = {}
    import hashlib
    for relative in sorted(files):
        path = candidate / relative
        if path.is_symlink() or not path.resolve().is_relative_to(candidate.resolve()):
            raise RuntimeError("보존할 파일이 외부 경로를 가리킵니다: " + relative)
        content = path.read_bytes() if path.is_file() else b"<absent>"
        checksum = hashlib.sha256(content).hexdigest()
        destination = relations.directory(root) / "archives" / operation["id"] / "objects" / checksum
        if not destination.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("xb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
        if destination.read_bytes() != content:
            raise RuntimeError("보존된 파일 검증에 실패했습니다.")
        manifest[relative] = checksum
    # Reuse the central collector; no deletion/staging/committing of central logs.
    if mirror and any(name.startswith(config.ARTIFACT_SESSIONS_PREFIXES) for name in files):
        environment = dict(os.environ)
        environment.pop("ASAN_AGENT_POLICY_ASSIGNMENT", None)
        environment["ASAN_AGENT_POLICY_PROJECT_PATH"] = str(candidate)
        result = subprocess.run(["{{CENTRAL_ROOT}}/bin/agent-policy", "collect-logs", "--project", "{{PROJECT_ID}}", "--channel", "all", "--quiet"],
            cwd=root, env=environment, text=True, capture_output=True, timeout=60)
        if result.returncode:
            raise RuntimeError("중앙 로그 보존 실패: " + result.stderr)
    return {"files": manifest, "changes": relations.content_snapshot(candidate, logs=True)}


def verify_and_archive(root: Path, operation: dict) -> None:
    target = Path(operation["target_worktree"])
    event = {"session_id": operation["id"], "tool_call_id": "verification"}
    reserve_write(root, event, "runtime", [target])
    try:
        _verify_and_archive(root, operation)
    finally:
        complete_write(root, {**event, "tool_response": {"success": True}}, "runtime")


def _verify_and_archive(root: Path, operation: dict) -> None:
    target = Path(operation["target_worktree"])
    if (git.current_branch(target) != operation["evidence"]["target"] or
            git.head(target) != operation["result"]):
        operation["verification_passed"] = False
        raise RuntimeError("검증 위치가 승인한 target 브랜치·병합 결과와 다릅니다. 병합은 보존하고 정리를 보류합니다.")
    before = {"head": git.head(target), "changes": relations.content_snapshot(target)}
    operation["verification_results"] = []
    for command_value in operation["evidence"]["verification"]:
        result = subprocess.run(shlex.split(command_value), cwd=target, text=True, capture_output=True)
        operation["verification_results"].append({"command": command_value, "exit_code": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr})
        save(root, operation)
    success = all(item["exit_code"] == 0 for item in operation["verification_results"])
    if (relations.oid(root, operation["evidence"]["target"]) != operation["result"] or
            before != {"head": git.head(target), "changes": relations.content_snapshot(target)}):
        success = False
        operation["reason"] = "검증 중 target commit이 바뀌었습니다. 검증 결과를 현재 commit의 성공으로 사용하지 않습니다."
    operation["stage"] = "verified" if success else "verification-failed"
    operation["verification_passed"] = success
    with state.locked(relations.directory(root) / "locks/git.lock"):
        graph = relations.read(root)
        resolution = graph["nodes"][operation["evidence"]["source_id"]].get("resolution") or {}
        if resolution.get("operation") == operation["id"]:
            resolution["verification"] = "passed" if success else "failed"
            for item in graph["nodes"][operation["evidence"]["source_id"]].get("integrations", []):
                if item["operation"] == operation["id"]:
                    item["verification"] = resolution["verification"]
            relations.save(root, graph)
        save(root, operation)
    candidates = [target]
    if operation.get("source_worktree"):
        candidates.append(Path(operation["source_worktree"]))
    operation["archives"] = {str(path): archive(root, path, operation) for path in set(candidates) if path.exists()}
    save(root, operation)


def cleanup(root: Path, operation: dict, execution_cwd: Path) -> None:
    evidence = operation["evidence"]
    if not evidence["cleanup"]:
        operation["stage"] = "retained"
        return
    if operation.get("stage") not in {"verified", "cleanup-deferred"} or not operation.get("verification_passed"):
        raise RuntimeError("승인한 검증이 성공하지 않아 정리를 보류합니다.")
    graph = relations.read(root)
    child = graph["nodes"][evidence["source_id"]]
    if relations.oid(root, evidence["source"]) != evidence["source_head"] or not git.is_ancestor(root, evidence["source_head"], relations.oid(root, evidence["target"])):
        raise RuntimeError("source의 추가 commit 또는 통합 결과 변경으로 정리를 보류합니다.")
    if relations.unfinished(root, graph, child["id"]):
        raise RuntimeError("새로운 미처리 자식이 있어 정리를 보류합니다.")
    candidate = Path(operation["source_worktree"]) if operation.get("source_worktree") else None
    if candidate and candidate.exists():
        entries = relations.worktrees(root)
        exact = [item for item in entries if Path(item["worktree"]).resolve() == candidate.resolve()]
        if len(exact) != 1 or exact[0].get("branch") != "refs/heads/" + evidence["source"]:
            raise RuntimeError("삭제 대상이 승인한 source의 linked worktree가 아닙니다.")
        if candidate.resolve() == Path(entries[0]["worktree"]).resolve() or not (candidate / ".git").is_file():
            raise RuntimeError("기본 worktree는 자동 삭제하지 않습니다.")
        if (execution_cwd.resolve().is_relative_to(candidate.resolve()) or
                config.PROJECT_ROOT.resolve().is_relative_to(candidate.resolve())):
            raise RuntimeError("현재 실행 위치를 보존합니다. 다른 안전한 workdir에서 같은 완료 정리를 재시도하세요.")
        assert_idle(root, [candidate])
        if relations.content_snapshot(candidate, logs=True)["files"]:
            raise RuntimeError("미커밋 로그 또는 작업 변경이 있어 worktree 정리만 보류합니다.")
        ignored = git._git(candidate, "ls-files", "--others", "--ignored", "--exclude-standard", "--directory", "-z")
        if ignored.returncode:
            raise RuntimeError("ignored 로컬 파일의 보존 여부를 확인할 수 없습니다.")
        generated = tuple(evidence.get("generated_cleanup_roots", []))
        unpreserved = [name for name in ignored.stdout.split("\0") if name and not name.startswith(generated)]
        if unpreserved:
            raise RuntimeError("미보존 ignored 로컬 파일이 있어 정리를 보류합니다: " + ", ".join(unpreserved[:10]))
        archived = operation.get("archives", {}).get(str(candidate))
        if archived is None or archived != archive(root, candidate, operation, mirror=False):
            raise RuntimeError("로그 보존 이후 변경이 발생했습니다. 정리를 보류합니다.")
        run(root, ["worktree", "remove", str(candidate)])
        operation["worktree_removed"] = True
        save(root, operation)
    elif candidate and not operation.get("worktree_removed"):
        raise RuntimeError("삭제 대상 worktree가 외부에서 사라졌습니다. 자동 삭제 결과로 기록하지 않습니다.")
    if relations.branch_worktrees(root, evidence["source"]):
        raise RuntimeError("source가 다른 worktree에서 사용 중입니다. 브랜치 삭제를 보류합니다.")
    run(Path(operation["target_worktree"]), ["branch", "-d", evidence["source"]])
    child["deleted"] = True
    relations.save(root, graph)
    operation["stage"] = "cleaned"


def execute(root: Path, identifier: str, execution_cwd: Path | None = None) -> dict:
    operation_path(root, identifier)
    with state.locked(relations.directory(root) / "locks" / ("operation-" + identifier + ".lock")):
        return _execute(root, identifier, execution_cwd)


def _execute(root: Path, identifier: str, execution_cwd: Path | None = None) -> dict:
    operation = load(root, identifier)
    execution_cwd = execution_cwd or Path(operation["cwd"])
    if not git.same_git_repository(root, execution_cwd):
        raise RuntimeError("현재 프로젝트 밖에서는 실행할 수 없습니다.")
    grant_path = operation_path(root, identifier).with_suffix(".grant.json")
    ticket = state.read(grant_path, max_age=120)
    if not ticket or ticket.get("fingerprint") != operation["fingerprint"]:
        raise RuntimeError("이 작업의 사용자 승인과 도구 실행 예약이 필요합니다.")
    # Credentials for this one tool invocation; never branch/worktree ownership.
    current_host = os.environ.get("ASAN_AGENT_POLICY_HOST")
    if (current_host and ticket.get("host") != current_host or
            ticket.get("assignment", "") != os.environ.get("ASAN_AGENT_POLICY_ASSIGNMENT", "")):
        raise RuntimeError("다른 도구 실행의 승인 예약입니다. 현재 호스트의 execute 요청으로 예약하세요.")
    grant_path.unlink()
    with state.locked(relations.directory(root) / "locks/git.lock"):
        operation = load(root, identifier)
        if operation["stage"] in {"cleaned", "done", "retained"}:
            return operation
        if operation["stage"] != "prepared":
            raise RuntimeError("중단된 실행 기록입니다. 같은 operation ID로 recover를 사용하세요. 새 commit을 다시 실행하지 않습니다.")
        validate(root, operation)
        operation["authorized"] = {"at": time.time(), "fingerprint": operation["fingerprint"]}
        try:
            if operation["kind"] == "git":
                denial = _loader.load("shared_git").git_denial(ticket["event"], root, ticket["host"], operation["command"], Path(operation["cwd"]))
                if denial:
                    raise RuntimeError(denial)
                assert_idle(root, [Path(item["root"]) for item in operation["invocations"]])
                operation["stage"] = "executing"
                save(root, operation)
                operation["results"] = []
                for item in operation["invocations"]:
                    operation["results"].append(run(Path(item["cwd"]), item["args"]).stdout)
                    save(root, operation)
                operation["stage"] = "done"
            elif operation["kind"] == "relation":
                operation["stage"] = "executing"
                save(root, operation)
                apply_relation(root, operation)
                operation["stage"] = "done"
            elif operation["kind"] == "write-recovery":
                (relations.directory(root) / "writes" / (operation["write_id"] + ".json")).unlink()
                operation["stage"] = "done"
            else:
                merge(root, operation)
            save(root, operation)
        except BaseException as error:
            operation["reason"] = str(error)
            save(root, operation)
            raise
    if operation["kind"] == "completion":
        finish(root, operation, execution_cwd)
    return operation


def finish(root: Path, operation: dict, execution_cwd: Path) -> None:
    try:
        verify_and_archive(root, operation)
        with state.locked(relations.directory(root) / "locks/git.lock"):
            cleanup(root, operation, execution_cwd)
    except (RuntimeError, OSError, subprocess.SubprocessError) as error:
        operation["stage"] = "cleanup-deferred"
        operation["reason"] = str(error)
    save(root, operation)


def recover(root: Path, identifier: str, execution_cwd: Path) -> dict:
    operation_path(root, identifier)
    with state.locked(relations.directory(root) / "locks" / ("operation-" + identifier + ".lock")):
        return _recover(root, identifier, execution_cwd)


def _recover(root: Path, identifier: str, execution_cwd: Path) -> dict:
    operation = load(root, identifier)
    if operation["kind"] != "completion":
        raise RuntimeError("일반 Git·관계 변경은 결과를 조회해 대조하세요. 중단된 명령을 자동 반복하지 않습니다.")
    if not operation.get("authorized"):
        raise RuntimeError("사용자 승인 후 시작한 완료 작업만 복구할 수 있습니다.")
    if not git.same_git_repository(root, execution_cwd):
        raise RuntimeError("현재 프로젝트 밖에서 완료 작업을 복구할 수 없습니다.")
    for path in (relations.directory(root) / "writes").glob("*.json"):
        pending = state.read(path)
        if pending.get("host") == "runtime" and pending.get("session") == identifier:
            raise RuntimeError("이전 검증 프로세스의 종료를 확인하고 write-recovery로 미확인 실행을 정리하세요: " + path.stem)
    with state.locked(relations.directory(root) / "locks/git.lock"):
        if operation["stage"] in {"cleaned", "retained"}:
            return operation
        verify_result(root, operation)
    finish(root, operation, execution_cwd)
    return operation


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("--command", required=True)
    prepare.add_argument("--host", choices=git.KNOWN_HOSTS, required=True)
    evidence = commands.add_parser("review")
    evidence.add_argument("--source", required=True)
    evidence.add_argument("--target", required=True)
    evidence.add_argument("--strategy", choices=("ff-only", "merge"), required=True)
    evidence.add_argument("--verify-command", action="append", required=True)
    evidence.add_argument("--cleanup", action="store_true")
    complete = commands.add_parser("complete")
    complete.add_argument("--review", required=True)
    complete.add_argument("--report", type=Path, required=True)
    relation = commands.add_parser("relation")
    relation.add_argument("--action", dest="relation_action", choices=("register", "create", "rename", "reparent", "cancel", "retire"), required=True)
    relation.add_argument("--name", required=True)
    for name in ("parent", "fork", "purpose", "new-name", "worktree"):
        relation.add_argument("--" + name)
    for name in ("execute", "recover", "show"):
        commands.add_parser(name).add_argument("id")
    commands.add_parser("graph")
    recovery = commands.add_parser("write-recovery")
    recovery.add_argument("--id", required=True)
    recovery.add_argument("--reason", required=True)
    args = parser.parse_args()
    cwd = Path.cwd().resolve()
    root = config.PROJECT_ROOT.resolve()
    if not git.same_git_repository(root, cwd):
        raise RuntimeError("현재 세션 프로젝트 밖에서 명령을 실행할 수 없습니다.")
    if args.action == "prepare":
        result = prepare_git(root, cwd, args.command, args.host, {"session_id": "prepare"})
    elif args.action == "review":
        result = review.collect(root, args.source, args.target, args.strategy, args.verify_command, args.cleanup)
        state.write(relations.directory(root) / "reviews" / (result["id"] + ".json"), result)
    elif args.action == "complete":
        if not re.fullmatch(r"[a-f0-9]{32}", args.review) or not git.same_git_repository(root, args.report.resolve().parent):
            raise RuntimeError("현재 프로젝트의 검토 보고와 review ID를 명시하세요.")
        result = prepare_completion(root, cwd, state.read(relations.directory(root) / "reviews" / (args.review + ".json")), json.loads(args.report.read_text()))
    elif args.action == "relation":
        result = prepare_relation(root, cwd, args.relation_action, args.name, args.parent, args.fork,
                                  args.purpose or "", args.new_name, args.worktree)
    elif args.action == "graph":
        result = relations.read(root)
    elif args.action == "write-recovery":
        result = prepare_write_recovery(root, cwd, args.id, args.reason)
    elif args.action == "show":
        result = load(root, args.id)
    elif args.action == "execute":
        result = execute(root, args.id, cwd)
    else:
        result = recover(root, args.id, cwd)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get("stage") == "prepared":
        print("승인·실행: " + command(result))


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, ValueError) as error:
        print(f"Git 작업: {error}", file=sys.stderr)
        raise SystemExit(2)
