"""세션 목록과 실행이 공유하는 읽기 전용 재개 진단."""

from __future__ import annotations

import ast
import json
import re
import subprocess
from dataclasses import replace
from pathlib import Path

from .core import PolicyError, ProjectConfig, sha256_bytes
from .injection import CODEX_STATE_MANIFEST, _read_state_manifest, _safe_state_target, bundle_diagnostics, consumer_policy_sources
from .runtime import load_runtime

NATIVE_ID = re.compile(r"[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}")


def record_problem(record: dict) -> str | None:
    fields = ("project", "repository", "host", "role", "worktree", "bundle_root", "bundle_digest", "system_prompt")
    if any(not isinstance(record.get(key), str) or not record[key] for key in fields):
        return "assignment의 필수 실행 설정이 누락되었거나 형식이 잘못되었습니다."
    environment, command = record.get("environment"), record.get("command")
    if not isinstance(environment, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in environment.items()):
        return "assignment의 실행 환경이 올바르지 않습니다."
    if not isinstance(command, list) or not command or any(not isinstance(arg, str) for arg in command):
        return "assignment의 원래 실행 명령이 없습니다."
    if not Path(record["bundle_root"]).is_absolute() or re.fullmatch(r"[a-f0-9]{64}", record["bundle_digest"]) is None:
        return "assignment의 bundle 경로 또는 해시가 올바르지 않습니다."
    if Path(record["system_prompt"]) != Path(record["bundle_root"]) / "system-prompt.md":
        return "assignment의 prompt가 원래 bundle과 다릅니다."
    return None


def git_common(root: Path) -> str:
    result = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=root,
                            text=True, capture_output=True, check=False)
    if result.returncode:
        return ""
    raw = Path(result.stdout.strip())
    return str((raw if raw.is_absolute() else root / raw).resolve())


def transcript_catalog(home: Path) -> tuple[list[dict], list[str]]:
    """대화 본문은 읽지 않고 session_meta만 확인한다. 파일명은 ID의 근거가 아니다."""
    entries, errors = [], []
    if home.is_symlink():
        return [], [f"대화 home이 symlink입니다: {home}"]
    for folder in ("sessions", "archived_sessions"):
        directory = home / folder
        if directory.is_symlink():
            errors.append(f"대화 디렉터리가 symlink입니다: {directory}")
            continue
        for path in sorted(directory.glob("**/*.jsonl")):
            try:
                if path.is_symlink() or not path.resolve().is_relative_to(home.resolve()):
                    raise ValueError("대화 경로가 home 밖이거나 symlink입니다.")
                with path.open(encoding="utf-8") as stream:
                    line = stream.readline(1024 * 1024)
                value = json.loads(line)
                payload = value.get("payload", {})
                native = payload.get("id", "")
                if value.get("type") != "session_meta" or not isinstance(native, str) or not NATIVE_ID.fullmatch(native):
                    raise ValueError("유효한 session_meta.id가 없습니다.")
                if not isinstance(payload.get("cwd", ""), str):
                    raise ValueError("session_meta.cwd 형식이 잘못되었습니다.")
                entries.append({"id": native, "path": str(path), "cwd": payload.get("cwd", ""),
                                "modified_at": path.stat().st_mtime})
            except (OSError, ValueError, AttributeError) as error:
                errors.append(f"{path}: {error}")
    return entries, errors


def home_diagnostics(home: Path) -> str | None:
    try:
        if home.is_symlink() or not home.is_dir() or (home / CODEX_STATE_MANIFEST).is_symlink():
            return "원래 Codex home 또는 정책 manifest가 없거나 symlink입니다."
        manifest = _read_state_manifest(home)
        if not manifest:
            return "원래 Codex home의 정책 manifest가 없습니다."
        for relative, digest in manifest.items():
            target = _safe_state_target(home, relative)
            if target.is_symlink() or not target.is_file() or sha256_bytes(target.read_bytes()) != digest:
                return f"원래 Codex home의 정책 파일 검증에 실패했습니다: {relative}"
    except (OSError, PolicyError) as error:
        return str(error)
    return None


def policy_anchor(bundle: Path) -> Path | None:
    """검증한 정책의 실제 기준 경로를 파싱한다. 과거 runtime 코드는 실행하지 않는다."""
    contract = json.loads((bundle / "policy/.agent-policy/common/contracts/runtime-policy.json").read_bytes())
    if contract.get("version") != 4:
        return None
    tree = ast.parse((bundle / "policy/.agent-policy/runtime/runtime_config.py").read_text())
    for node in tree.body:
        if (isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "PROJECT_ROOT"
                and isinstance(node.value, ast.Call) and len(node.value.args) == 1
                and isinstance(node.value.args[0], ast.Constant) and isinstance(node.value.args[0].value, str)):
            return Path(node.value.args[0].value)
    raise ValueError("원래 guard의 프로젝트 기준 경로를 확인할 수 없습니다.")


def diagnose_assignment(project: ProjectConfig, path: Path, record: dict,
                        worktree: Path | None = None, bundle_cache: dict | None = None) -> dict:
    state = load_runtime("runtime_state")
    reasons = []

    def problem(code: str, message: str):
        reasons.append({"code": code, "message": message})

    binding = state.read(path.with_name("session-binding.json"))
    selected = worktree or Path(binding.get("worktree") or record.get("worktree") or project.path)
    common = record.get("repository", "")
    if record.get("project") != project.id or common != git_common(project.path):
        problem("repository_mismatch", "assignment의 프로젝트·저장소가 다릅니다.")
    if not selected.is_dir():
        problem("worktree_missing", f"실행 worktree가 없습니다. 같은 저장소의 기존 경로를 선택하세요: {selected}")
    elif git_common(selected) != common:
        problem("worktree_repository_mismatch", f"선택 경로가 원래 Git 저장소와 다릅니다: {selected}")
    else:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=selected,
                             text=True, capture_output=True, check=False)
        if top.returncode or Path(top.stdout.strip()).resolve() != selected.resolve():
            problem("worktree_not_root", "실행 위치에는 Git worktree 루트를 지정하세요.")
        conflicts = consumer_policy_sources(replace(project, path=selected))
        if conflicts:
            problem("consumer_policy_conflict", "선택 worktree에 소비자 정책 출처가 남아 있습니다: " + ", ".join(conflicts))
    bundle = Path(record.get("bundle_root", ""))
    key = (str(bundle), record.get("bundle_digest", ""))
    cache = bundle_cache if bundle_cache is not None else {}
    if key not in cache:
        cache[key] = bundle_diagnostics(bundle, key[1])
    diagnosis = cache[key]
    if not diagnosis["valid"]:
        problem("bundle_invalid", "원래 세션의 bundle 검증에 실패했습니다: " + json.dumps(diagnosis, ensure_ascii=False))
    else:
        try:
            anchor = policy_anchor(bundle)
            if anchor is not None and (not anchor.is_absolute() or not anchor.is_dir() or git_common(anchor) != common):
                problem("policy_anchor_missing", "원래 guard의 프로젝트 기준 경로가 없습니다. 원본 복구 또는 새 정책으로 기록 인계가 필요합니다.")
        except (OSError, ValueError, SyntaxError) as error:
            problem("policy_anchor_unknown", str(error))
    native = record.get("native_session", "")
    if not native:
        problem("native_unbound", "native session ID가 연결되지 않았습니다. 실제 대화 메타데이터를 확인하세요.")
    if record.get("handed_off_to"):
        problem("handed_off", "이미 인계한 assignment입니다. 인계 대상에서 이어가세요.")
    for transaction in (path.parents[2] / "handoffs").glob("*.transaction.json"):
        value = state.read(transaction)
        if value.get("state") == "applying" and path.parent.name in (value.get("source"), value.get("target")):
            problem("handoff_incomplete", "중단된 assignment 인계가 있습니다. 기존 인계를 먼저 복구하세요.")
    entries, transcript_errors, home = [], [], record.get("environment", {}).get("CODEX_HOME")
    if record.get("host") == "codex":
        if not home:
            problem("home_invalid", "원래 CODEX_HOME이 없습니다.")
        else:
            issue = home_diagnostics(Path(home))
            if issue:
                problem("home_invalid", issue)
            entries, transcript_errors = transcript_catalog(Path(home))
        if native and (not isinstance(native, str) or not NATIVE_ID.fullmatch(native)):
            problem("native_invalid", "native session ID 형식이 잘못되었습니다.")
        matches = [entry for entry in entries if entry["id"] == native]
        if native and not matches:
            problem("transcript_missing", "원래 CODEX_HOME에서 native ID와 일치하는 대화 메타데이터를 찾지 못했습니다.")
        if len(matches) > 1:
            problem("transcript_ambiguous", "동일 native ID의 대화 파일이 여러 개입니다. 원본을 확인하세요.")
    else:
        matches = []
    visible = matches if native else entries
    for entry in entries:
        entry["linkable"] = bool(not native and not record.get("handed_off_to") and entry["cwd"]
            and Path(entry["cwd"]).resolve() == Path(record["worktree"]).resolve()
            and sum(candidate["id"] == entry["id"] for candidate in entries) == 1)
    return {"resumable": not reasons, "reasons": reasons, "bundle": diagnosis, "worktree": str(selected),
            "codex_home": home, "transcripts": [entry["path"] for entry in visible],
            "native_candidates": entries if not native else [], "transcript_errors": transcript_errors,
            "last_activity": max((entry["modified_at"] for entry in visible), default=path.stat().st_mtime)}
