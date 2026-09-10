"""격리된 assignment 이력을 읽고, 원본 정책이 일치하는 생성 캐시만 격리한다."""

from __future__ import annotations

import hashlib
import re
import shlex
from pathlib import Path

from .core import PolicyError, ProjectConfig, atomic_write
from .injection import bundle_diagnostics, compare_bundle_policy
from .recovery import common_directory, git, repository_state
from .runtime import load_runtime


def assignment_record(project: ProjectConfig, assignment: str, state_root: Path | None = None) -> tuple[Path, dict]:
    if re.fullmatch(r"[a-f0-9]{32}", assignment) is None:
        raise PolicyError("32자리 assignment ID가 필요합니다.")
    path = repository_state(project, state_root) / "assignments" / assignment / "assignment.json"
    record = load_runtime("runtime_state").read(path)
    if record.get("project") != project.id or record.get("repository") != str(common_directory(project.path)):
        raise PolicyError("assignment의 프로젝트·저장소가 다릅니다.")
    return path, record


def repair_bundle(project: ProjectConfig, assignment: str, state_root: Path | None = None) -> list[str]:
    path, record = assignment_record(project, assignment, state_root)
    bundle, digest = Path(record["bundle_root"]), record["bundle_digest"]
    if re.fullmatch(r"[a-f0-9]{64}", str(digest)) is None:
        raise PolicyError("assignment bundle digest가 올바르지 않습니다.")
    state = load_runtime("runtime_state")
    repository = path.parents[2]
    with state.locked(repository / "bundle-repairs" / f"{digest}.lock"):
        diagnosis = bundle_diagnostics(bundle, digest)
        if diagnosis["valid"]:
            return []
        if (diagnosis["error"] or diagnosis["missing"] or diagnosis["changed"] or diagnosis["symlinks"]
                or not diagnosis["caches"] or diagnosis["unexpected"] != diagnosis["caches"]):
            raise PolicyError("정책 변조·누락·미상 파일은 캐시 복구로 처리할 수 없습니다: " + str(diagnosis))
        # 캐시 내용은 역직렬화하거나 실행하지 않는다. 먼저 모두 백업한 뒤 정확한 파일만 제거한다.
        payloads = {relative: (bundle / relative).read_bytes() for relative in diagnosis["caches"]}
        destinations = {}
        for relative, content in payloads.items():
            destination = repository / "bundle-repairs" / digest / hashlib.sha256(content).hexdigest() / relative
            atomic_write(destination, content)
            destinations[relative] = destination
        for relative, content in payloads.items():
            target = bundle / relative
            if target.is_symlink() or target.read_bytes() != content:
                raise PolicyError("격리 중 캐시가 바뀌었습니다. 다시 진단하세요.")
            target.unlink()
        if not bundle_diagnostics(bundle, digest)["valid"]:
            raise PolicyError("캐시 격리 뒤 bundle이 변경되었습니다. 원본을 다시 진단하세요.")
        state.write(repository / "bundle-repairs" / f"{digest}.json",
                    {"assignment": assignment, "bundle": str(bundle), "bundle_digest": digest,
                     "quarantined": {key: str(value) for key, value in destinations.items()}})
        return [str(value) for value in destinations.values()]


def list_sessions(project: ProjectConfig, host: str | None = None, assignment: str | None = None,
                  state_root: Path | None = None) -> list[dict]:
    state = load_runtime("runtime_state")
    repository = repository_state(project, state_root)
    paths = sorted((repository / "assignments").glob("*/assignment.json"))
    if assignment:
        selected, _ = assignment_record(project, assignment, state_root)
        paths = [selected]
    rows = []
    for path in paths:
        record = state.read(path)
        if record.get("project") != project.id or (host and record.get("host") != host):
            continue
        binding = state.read(path.with_name("session-binding.json"))
        native = str(record.get("native_session") or "")
        home = record.get("environment", {}).get("CODEX_HOME")
        transcripts = []
        if home and re.fullmatch(r"[a-f0-9-]{36}", native):
            for folder in ("sessions", "archived_sessions"):
                transcripts.extend(str(p) for p in Path(home).glob(f"{folder}/**/*{native}*.jsonl") if p.is_file())
        worktree = str(binding.get("worktree") or record.get("worktree") or project.path)
        command = ["bin/agent-policy", "start", "--project", project.id, "--host", record["host"],
                   "--role", record["role"], "--responsibility", record.get("responsibility", "owner"),
                   "--worktree", worktree, "--resume-assignment", path.parent.name]
        task = str(binding.get("task") or record.get("task") or "")
        task_state = ""
        if re.fullmatch(r"task/[a-z0-9]+(?:-[a-z0-9]+)*", task):
            try:
                task_state = git(project.path, "config", "--get", f"branch.{task}.asan-state")
            except PolicyError:
                task_state = state.read(Path(record["repository"]) / "asan-agent-policy/closed" / f"{task[5:]}.json").get("state", "UNKNOWN")
        pending_calls = [value.get("call", "") for pending_path in
                         (path.with_name("pending-binding.json"), *path.parent.glob("pending-bindings/*.json"))
                         if (value := state.read(pending_path))]
        receipts = []
        for reservation in (Path(record["repository"]) / "asan-agent-policy/integration-targets").glob("*.json"):
            value = state.read(reservation)
            if value.get("owner") == path.parent.name:
                receipts.append(value)
        rows.append({"assignment": path.parent.name, "project": project.id, "host": record["host"],
                     "role": record["role"], "task": task, "worktree": worktree, "native_session": native,
                     "task_state": task_state, "pending_calls": sorted(pending_calls),
                     "handed_off_to": record.get("handed_off_to"), "codex_home": home,
                     "transcripts": sorted(transcripts), "integration_reservations": receipts,
                     "bundle": bundle_diagnostics(Path(record["bundle_root"]), record["bundle_digest"]),
                     "policy_comparison": compare_bundle_policy(project, Path(record["bundle_root"])),
                     "resume_command": shlex.join(command) if native and not record.get("handed_off_to") else ""})
    return rows
