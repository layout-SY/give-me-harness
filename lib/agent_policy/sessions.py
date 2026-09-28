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
from .session_diagnostics import diagnose_assignment, record_problem, transcript_catalog


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
        if not bundle.exists() and not bundle.is_symlink():
            from .bundle_store import restore_bundle
            return [str(restore_bundle(path, record))]
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
    bundle_cache = {}
    policy_cache = {}
    for path in paths:
        try:
            record = state.read(path)
            error = record_problem(record)
            if error:
                raise RuntimeError(error)
        except RuntimeError as error:
            rows.append({"assignment": path.parent.name, "project": project.id, "host": host or "unknown",
                         "role": "unknown", "task": "", "task_state": "", "pending_calls": [],
                         "native_session": "", "codex_home": None, "transcripts": [], "native_candidates": [],
                         "resume_command": "", "resumable": False, "last_activity": 0,
                         "bundle": {"valid": False, "error": "assignment를 읽을 수 없습니다."},
                         "reasons": [{"code": "record_invalid", "message": str(error)}]})
            continue
        if record.get("project") != project.id or (host and record.get("host") != host):
            continue
        binding = state.read(path.with_name("session-binding.json"))
        native = str(record.get("native_session") or "")
        assessment = diagnose_assignment(project, path, record, bundle_cache=bundle_cache)
        worktree = assessment["worktree"]
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
        current_calls = [value.get("call", "") for pending in
                         (repository / "branch-relations/v1/writes").glob("*.json")
                         if (value := state.read(pending)).get("session") == native and value.get("host") == record["host"]]
        receipts = []
        for reservation in (Path(record["repository"]) / "asan-agent-policy/integration-targets").glob("*.json"):
            value = state.read(reservation)
            if value.get("owner") == path.parent.name:
                receipts.append(value)
        bundle_key = record["bundle_root"]
        if bundle_key not in policy_cache:
            try:
                policy_cache[bundle_key] = compare_bundle_policy(project, Path(bundle_key))
            except (OSError, ValueError, PolicyError) as error:
                policy_cache[bundle_key] = {"status": "unknown", "message": str(error)}
        rows.append({**assessment, "assignment": path.parent.name, "project": project.id, "host": record["host"],
                     "role": record["role"], "task": task, "worktree": worktree, "native_session": native,
                     "task_state": task_state, "pending_calls": sorted(pending_calls),
                     "current_pending_calls": sorted(set(current_calls)),
                     "handed_off_to": record.get("handed_off_to"), "integration_reservations": receipts,
                     "policy_comparison": policy_cache[bundle_key],
                     "resume_command": shlex.join(command) if assessment["resumable"] else ""})
    return sorted(rows, key=lambda row: (-row["last_activity"], row["assignment"]))


def link_native_session(project: ProjectConfig, assignment: str, native: str,
                        state_root: Path | None = None) -> None:
    """사용자가 선택한, 현재 home에 실제로 존재하는 미연결 대화만 연결한다."""
    path, _ = assignment_record(project, assignment, state_root)
    state = load_runtime("runtime_state")
    with state.locked(path.parents[2] / "events.lock"):
        record = state.read(path)
        invalid = record_problem(record)
        if invalid:
            raise PolicyError(invalid)
        if record.get("host") != "codex" or record.get("handed_off_to") or record.get("native_session"):
            raise PolicyError("연결은 인계되지 않은 Codex 미연결 assignment에만 가능합니다.")
        entries, _ = transcript_catalog(Path(record["environment"]["CODEX_HOME"]))
        matches = [entry for entry in entries if entry["id"] == native]
        if len(matches) != 1:
            raise PolicyError("선택한 native ID의 실제 대화 원본을 하나로 확인할 수 없습니다.")
        original_cwd = Path(record["worktree"]).resolve()
        if Path(matches[0]["cwd"]).resolve() != original_cwd:
            raise PolicyError("대화의 최초 작업 경로가 assignment와 다릅니다. 임의로 연결하지 않습니다.")
        for other in path.parents[1].glob("*/assignment.json"):
            value = state.read(other)
            if other != path and value.get("native_session") == native and not value.get("handed_off_to"):
                raise PolicyError("이 native ID가 다른 assignment에 연결되어 있습니다. 기존 연결을 먼저 확인하세요.")
        state.write(path.with_name("native-link-backup.json"), record)
        record["native_session"] = native
        record["native_link_source"] = matches[0]["path"]
        state.write(path, record)
