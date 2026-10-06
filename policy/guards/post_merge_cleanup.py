"""이미 통합된 source만 보존·정리한다. 부모 index·작업 파일·검증 명령은 건드리지 않는다."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import stat
from types import ModuleType

_path = Path(__file__).with_name("runtime_loader.py")
_loader = ModuleType("cleanup_loader")
_loader.__file__ = str(_path)
exec(compile(_path.read_bytes(), str(_path), "exec"), _loader.__dict__)
ops = _loader.load("git_operations")
relations, git, state = ops.relations, ops.git, ops.state


def inventory(root: Path, candidate: Path) -> dict:
    for marker in ("index.lock", "HEAD.lock", "MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD",
                   "BISECT_START", "rebase-merge", "rebase-apply", "sequencer"):
        result = git._git(candidate, "rev-parse", "--git-path", marker)
        if result.returncode or not result.stdout.strip():
            raise RuntimeError("worktree의 Git 실행 상태를 확인할 수 없습니다.")
        path = candidate / result.stdout.strip()
        if path.exists() or path.is_symlink():
            raise RuntimeError("진행 중인 Git 상태가 있어 정리를 보류합니다: " + marker)
    changes = relations.content_snapshot(candidate, logs=True)
    source_changes = relations.content_snapshot(candidate)["files"]
    if source_changes:
        raise RuntimeError("source에 미커밋 작업이 있어 정리를 보류합니다: " + ", ".join(source_changes))
    generated = tuple(git.RUNTIME_CONTRACT["git"]["integration"].get("generated_cleanup_roots", []))
    args = ["--", ".", *(f":(exclude){name}**" for name in generated)]
    ignored = git._git(candidate, "ls-files", "--others", "--ignored", "--exclude-standard", "-z", *args)
    if ignored.returncode:
        raise RuntimeError("ignored 파일 목록을 확인할 수 없습니다.")
    files = set(changes["files"]) | set(filter(None, ignored.stdout.split("\0")))
    for host in git.RUNTIME_CONTRACT["hosts"].values():
        logs = candidate / host["artifact_root"]
        if logs.is_symlink():
            raise RuntimeError("세션 로그 경로가 심볼릭 링크입니다.")
        if logs.exists():
            files.update(str(p.relative_to(candidate)) for p in logs.rglob("*") if p.is_file() or p.is_symlink())
    # Git이 다른 저장소·submodule을 함께 지우거나 경로 밖 파일을 보존했다고 간주하지 않는다.
    tracked = git._output(candidate, "ls-files", "--stage")
    if tracked.startswith("160000 ") or "\n160000 " in tracked:
        raise RuntimeError("submodule이 있는 worktree는 별도 보존 검토가 필요합니다.")
    flags = git._git(candidate, "ls-files", "-v", "-z")
    if flags.returncode or any(item and (item[0].islower() or item[0] == "S") for item in flags.stdout.split("\0")):
        raise RuntimeError("assume-unchanged·skip-worktree 표시가 있어 실제 파일 변경을 확인할 수 없습니다.")
    for directory, names, _files in os.walk(candidate, followlinks=False):
        relative = Path(directory).relative_to(candidate)
        names[:] = [name for name in names if not any((relative / name).as_posix() + "/" == prefix for prefix in generated)]
        if ".git" in names or relative != Path(".") and ".git" in _files:
            raise RuntimeError("중첩 저장소가 있어 정리를 보류합니다.")
    manifest = {}
    for relative in sorted(files):
        path = candidate / relative
        if path.is_symlink() or path.resolve() != path or not path.is_relative_to(candidate):
            raise RuntimeError("보존 대상에 심볼릭 링크·외부 경로가 있습니다: " + relative)
        if not path.exists():
            manifest[relative] = {"absent": True}
        elif not path.is_file():
            raise RuntimeError("일반 파일이 아닌 보존 대상입니다: " + relative)
        else:
            manifest[relative] = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                                  "mode": stat.S_IMODE(path.stat().st_mode)}
    return {"files": manifest, "changes": changes, "generated_cleanup_roots": list(generated)}


def verification(root: Path, child: dict, parent: dict, source_head: str, target_head: str) -> dict:
    resolution = child.get("resolution") or {}
    if resolution.get("kind") != "merged" or resolution.get("source_head") != source_head or resolution.get("target_id") != parent["id"]:
        return {"status": "unknown", "reason": "현재 source·직접 부모에 대응하는 중앙 검증 기록 없음"}
    try:
        previous = ops.load(root, resolution.get("operation", ""))
    except RuntimeError:
        return {"status": "unknown", "reason": "중앙 검증 실행 기록을 확인할 수 없음"}
    evidence = previous.get("evidence", {})
    if (previous.get("kind") != "completion" or not previous.get("verification_passed")
            or evidence.get("source_head") != source_head or evidence.get("source_id") != child["id"]
            or evidence.get("target_id") != parent["id"]
            or not previous.get("result") or not git.is_ancestor(root, previous["result"], target_head)):
        return {"status": "failed" if previous.get("verification_passed") is False else "unknown",
                "operation": previous["id"], "commit": previous.get("result")}
    return {"status": "passed", "operation": previous["id"], "commit": previous["result"]}


def context(root: Path, cwd: Path, source: str, target: str, *, removed: bool = False) -> dict:
    graph = relations.read(root)
    child, parent = relations.completion_check(root, graph, source, target)
    source_head, target_head = relations.require_live(root, child), relations.require_live(root, parent)
    births = {"source_birth": relations.birth(root, source), "target_birth": relations.birth(root, target)}
    if not all(births.values()):
        raise RuntimeError("브랜치 reflog 식별 근거가 없습니다. 관계를 재확인하세요.")
    if not git.is_ancestor(root, source_head, target_head):
        raise RuntimeError("source의 최종 commit이 직접 부모에 포함되지 않았습니다. 정리 대신 병합을 검토하세요.")
    locations = relations.branch_worktrees(root, source)
    if len(locations) > 1 or removed and locations:
        raise RuntimeError("source의 worktree 등록이 변경됐습니다.")
    candidate = locations[0] if locations else None
    if candidate:
        entries = relations.worktrees(root)
        entry = next(item for item in entries if Path(item["worktree"]).resolve() == candidate)
        if (candidate == Path(entries[0]["worktree"]).resolve() or not (candidate / ".git").is_file()
                or (candidate / ".git").is_symlink() or "locked" in entry or "prunable" in entry):
            raise RuntimeError("기본·잠긴·복구가 필요한 worktree는 자동 정리하지 않습니다.")
        if cwd.resolve().is_relative_to(candidate) or ops.config.PROJECT_ROOT.resolve().is_relative_to(candidate):
            raise RuntimeError("현재 실행 위치는 삭제할 수 없습니다. 다른 workdir에서 정리를 준비하세요.")
        ops.assert_idle(root, [candidate])
    return {"source": source, "target": target, "source_id": child["id"], "target_id": parent["id"], **births,
            "source_head": source_head, "target_head": target_head, "relation": child,
            "verification": verification(root, child, parent, source_head, target_head),
            "worktree": str(candidate) if candidate else None,
            "inventory": inventory(root, candidate) if candidate else None}


def prepare(root: Path, cwd: Path, source: str, target: str) -> dict:
    operation = ops.base(root, cwd, "cleanup")
    with state.locked(relations.directory(root) / "locks/git.lock"):
        operation["cleanup"] = context(root, cwd, source, target)
        operation["fingerprint"] = relations.digest(operation["cleanup"])
        return ops.save(root, operation)


def validate(root: Path, operation: dict) -> None:
    expected = operation["cleanup"]
    current = context(root, Path(operation["cwd"]), expected["source"], expected["target"],
                      removed=bool(operation.get("worktree_removed")))
    if operation.get("worktree_removed"):
        expected = {**expected, "worktree": None, "inventory": None}
    if current != expected:
        raise RuntimeError("정리 승인 후 source·부모 HEAD·브랜치 식별·관계·보존 파일이 변경됐습니다. 새 정리 계획을 검토하세요.")


def preserve(root: Path, operation: dict) -> dict:
    expected = operation["cleanup"]
    candidate = Path(expected["worktree"])
    directory = relations.directory(root) / "cleanup-archives" / operation["id"]
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    directory.chmod(0o700)
    objects = directory / "objects"
    objects.mkdir(exist_ok=True, mode=0o700)
    objects.chmod(0o700)
    for relative, entry in expected["inventory"]["files"].items():
        if entry.get("absent"):
            continue
        path = candidate / relative
        content = path.read_bytes()
        if hashlib.sha256(content).hexdigest() != entry["sha256"]:
            raise RuntimeError("보존 중 파일이 변경됐습니다: " + relative)
        destination = objects / entry["sha256"]
        if not destination.exists():
            descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
        if destination.is_symlink() or destination.read_bytes() != content:
            raise RuntimeError("보존 객체의 검증에 실패했습니다: " + relative)
        destination.chmod(0o600)
    # 로그는 기존 중앙 수집기를 사용한다. 환경설정은 Git 제외 private archive에만 둔다.
    ops.archive(root, candidate, operation)
    result = {"directory": str(directory), "files": expected["inventory"]["files"],
              "changes": expected["inventory"]["changes"], "source_head": expected["source_head"]}
    state.write(directory / "manifest.json", result)
    operation["archive"] = result
    ops.save(root, operation)
    return result


def require_archive(root: Path, operation: dict) -> None:
    expected = operation["cleanup"]
    if not expected["worktree"]:
        return
    directory = relations.directory(root) / "cleanup-archives" / operation["id"]
    archive = operation.get("archive")
    if (not archive or archive.get("directory") != str(directory)
            or archive.get("files") != expected["inventory"]["files"]
            or archive.get("source_head") != expected["source_head"]
            or state.read(directory / "manifest.json") != archive):
        raise RuntimeError("승인한 파일 보존 기록이 없어 정리·복구를 보류합니다.")
    for relative, entry in archive["files"].items():
        if entry.get("absent"):
            continue
        path = directory / "objects" / entry["sha256"]
        if (path.resolve() != path or not path.is_file()
                or hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]):
            raise RuntimeError("보존 파일이 없거나 손상됐습니다: " + relative)


def finalize(root: Path, operation: dict) -> dict:
    """삭제 직전 의도와 실제 ref·경로 부재가 일치할 때만 관계를 퇴역한다."""
    data = operation["cleanup"]
    graph = relations.read(root)
    child, parent = graph["nodes"].get(data["source_id"]), graph["nodes"].get(data["target_id"])
    if (not child or not parent or relations.require_live(root, parent) != data["target_head"]
            or relations.birth(root, data["target"]) != data["target_birth"]
            or relations.oid(root, data["source"]) or relations.branch_worktrees(root, data["source"])
            or relations.unfinished(root, graph, data["source_id"])
            or child.get("parent") != parent["id"]):
        raise RuntimeError("삭제 결과·직접 부모·하위 작업이 승인 당시와 달라 관계 정리를 보류합니다.")
    if data["worktree"] and (Path(data["worktree"]).exists() or Path(data["worktree"]).is_symlink()):
        raise RuntimeError("삭제 대상 경로에 파일이 남아 있어 완료 처리하지 않습니다.")
    require_archive(root, operation)
    if child.get("deleted") and child.get("cleanup_operation") == operation["id"]:
        operation["stage"] = "cleaned"
        return ops.save(root, operation)
    if child != data["relation"]:
        raise RuntimeError("다른 작업에서 관계 기록을 변경했습니다. 덮어쓰지 않습니다.")
    resolution = child.get("resolution") or {}
    if (resolution.get("kind") != "merged" or resolution.get("source_head") != data["source_head"]
            or resolution.get("target_id") != data["target_id"]):
        child["resolution"] = {"kind": "merged", "source_head": data["source_head"],
            "target_head": data["target_head"], "target_id": data["target_id"], "result": data["target_head"],
            "operation": operation["id"], "verification": data["verification"]["status"],
            "fork_commit": child["fork_commit"], "source_name": data["source"], "target_name": data["target"],
            "evidence": "ancestry-only-cleanup"}
        child.setdefault("integrations", []).append(dict(child["resolution"]))
    child["deleted"] = True
    child["cleanup_operation"] = operation["id"]
    relations.save(root, graph)
    operation["stage"] = "cleaned"
    return ops.save(root, operation)


def require_consent(root: Path, operation: dict, host: str, event: dict) -> None:
    authorized = operation.get("authorized", {})
    if (authorized.get("fingerprint") != operation["fingerprint"]
            or authorized.get("consent") != ops.consent_context(root, host, event)):
        raise RuntimeError("같은 주체의 철회되지 않은 정리 승인만 재개할 수 있습니다. 새 정리 계획을 승인받으세요.")


def recover(root: Path, operation: dict, execution_cwd: Path) -> dict:
    consent = operation.get("authorized", {}).get("consent", {})
    require_consent(root, operation, os.environ.get("ASAN_AGENT_POLICY_HOST") or consent.get("host", ""),
                    {"session_id": consent.get("session", "")})
    data = operation["cleanup"]
    if operation["stage"] == "cleaned":
        return operation
    if operation["stage"] not in {"prepared", "preserving", "removing-worktree", "removing-branch"}:
        raise RuntimeError("지원하지 않는 정리 단계입니다. 실행 기록을 확인하세요.")
    if operation["stage"] in {"removing-worktree", "removing-branch"}:
        require_archive(root, operation)
        for label in ("source", "target"):
            if git._output(root, "rev-parse", "--verify", f"refs/asan-policy/integrations/{operation['id']}/{label}") != data[label + "_head"]:
                raise RuntimeError("승인한 commit 보존 ref가 없습니다. 정리 복구를 보류합니다.")
        if data["worktree"] and not Path(data["worktree"]).exists() and not Path(data["worktree"]).is_symlink():
            if relations.branch_worktrees(root, data["source"]):
                raise RuntimeError("worktree 등록이 남아 있습니다. 삭제 성공으로 추정하지 않습니다.")
            operation["worktree_removed"] = True
            ops.save(root, operation)
        if not relations.oid(root, data["source"]):
            if operation["stage"] != "removing-branch":
                raise RuntimeError("branch 삭제 의도 기록 없이 ref가 사라졌습니다.")
            return finalize(root, operation)
    return execute(root, operation, execution_cwd)


def execute(root: Path, operation: dict, execution_cwd: Path) -> dict:
    validate(root, operation)
    data = operation["cleanup"]
    candidate = Path(data["worktree"]) if data["worktree"] else None
    if candidate and execution_cwd.resolve().is_relative_to(candidate):
        raise RuntimeError("현재 실행 위치를 정리할 수 없습니다.")
    operation["stage"] = "preserving"
    ops.save(root, operation)
    ops.pin(root, operation, "source", data["source_head"])
    ops.pin(root, operation, "target", data["target_head"])
    if candidate and not operation.get("worktree_removed"):
        preserve(root, operation)
        validate(root, operation)  # 보존 뒤 최종 검사. 부모의 dirty/index는 제외한다.
        require_archive(root, operation)
        operation["stage"] = "removing-worktree"
        ops.save(root, operation)
        # --force는 미커밋 로그·ignored 자료를 전부 보존한 이 정확한 경로에만 허용한다.
        # 잠긴 worktree, 미커밋 source, 중첩 저장소, 미확인 쓰기는 위에서 거부한다.
        ops.run(root, ["worktree", "remove", "--force", str(candidate)])
        operation["worktree_removed"] = True
        ops.save(root, operation)
    operation["stage"] = "removing-branch"
    ops.save(root, operation)
    validate(root, operation)
    require_archive(root, operation)
    # source는 명시한 직접 부모와 보존 ref에 포함된다. 실행 cwd의 HEAD/upstream에 의존하지 않는다.
    ops.run(root, ["branch", "-D", "--", data["source"]])
    return finalize(root, operation)
