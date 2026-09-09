"""차단된 소비자의 정책 퇴역을 정확한 diff와 새 V3 worktree로 복구한다."""

from __future__ import annotations

import argparse
import base64
import difflib
import hashlib
import json
import re
import subprocess
from pathlib import Path
from types import ModuleType

from .core import CENTRAL_ROOT, PolicyError, ProjectConfig, atomic_write, render_project
from .injection import CONSUMER_POLICY_REFERENCE_MARKERS, is_consumer_policy_path
from .runtime import load_runtime


def git(root: Path, *arguments: str) -> bytes:
    result = subprocess.run(["git", *arguments], cwd=root, capture_output=True, check=False)
    if result.returncode:
        raise PolicyError(result.stderr.decode(errors="replace").strip())
    return result.stdout


def canonical(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def replacement(path: str, before: bytes) -> bytes | None:
    if is_consumer_policy_path(path):
        return None
    if path == "package.json":
        value = json.loads(before)
        scripts = value.get("scripts", {})
        command = scripts.get("test")
        if isinstance(command, str):
            scripts["test"] = re.sub(
                r"\s*&&\s*python3?\s+(?:-I\s+)?\.codex/hooks/test_governance_hooks\.py\s*$", "", command)
            if scripts["test"] != command and scripts["test"].strip():
                return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()
        return before
    if path == "README.md":
        text = before.decode()
        lines = text.splitlines()
        retained = [line for line in lines if not any(marker in line for marker in CONSUMER_POLICY_REFERENCE_MARKERS)]
        if retained != lines:
            retained.extend(["", "AI 정책은 asan-agent-policy 중앙 저장소에서 관리합니다.",
                             "중앙 저장소의 `bin/agent-policy start --project user-ui|admin-ui --host <host> --role <role>`로 inject 세션을 시작합니다."])
            return ("\n".join(retained).rstrip() + "\n").encode()
        return before
    raise PolicyError(f"유지보수에서 허용하지 않는 파일입니다: {path}")


def preview(project: ProjectConfig, branch: str, worktree: Path, host: str,
            state_root: Path | None = None) -> tuple[Path, str, str]:
    if re.fullmatch(r"task/[a-z0-9]+(?:-[a-z0-9]+)*", branch) is None:
        raise PolicyError("유지보수 branch는 task/<ascii-kebab-summary>여야 합니다.")
    if host not in {"codex", "claude", "opencode", "user"}:
        raise PolicyError("지원하지 않는 Git 통합 담당자입니다.")
    worktree = worktree.expanduser().resolve()
    if worktree.exists() or worktree.is_relative_to(project.path.resolve()):
        raise PolicyError("유지보수 worktree는 기존 작업 폴더 밖의 새 경로여야 합니다.")
    head = git(project.path, "rev-parse", project.base_branch).decode().strip()
    existing = subprocess.run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], cwd=project.path)
    if existing.returncode == 0:
        raise PolicyError("유지보수 branch가 이미 존재합니다. 새 이름을 지정하세요.")
    entries = git(project.path, "ls-tree", "-r", "--name-only", "-z", head).decode().split("\0")
    changes: list[dict] = []
    diff: list[str] = []
    for relative in entries:
        if not relative or not (is_consumer_policy_path(relative) or relative in {"package.json", "README.md"}):
            continue
        before = git(project.path, "show", f"{head}:{relative}")
        after = replacement(relative, before)
        if after == before:
            continue
        changes.append({"path": relative, "before_sha256": hashlib.sha256(before).hexdigest(),
                        "after": base64.b64encode(after).decode() if after is not None else None})
        diff.extend(difflib.unified_diff(before.decode(errors="replace").splitlines(True),
                                        (after or b"").decode(errors="replace").splitlines(True),
                                        fromfile=f"a/{relative}", tofile=f"b/{relative}" if after is not None else "/dev/null"))
    if not changes:
        raise PolicyError("기준 branch에서 자동 제안 가능한 퇴역 정책 변경이 없습니다.")
    common = git(project.path, "rev-parse", "--git-common-dir").decode().strip()
    common_path = (Path(common) if Path(common).is_absolute() else project.path / common).resolve()
    plan = {"version": 1, "kind": "policy-retirement", "project": project.id,
            "repository": str(common_path), "base": project.base_branch, "base_head": head,
            "branch": branch, "worktree": str(worktree), "integrator": host, "changes": changes}
    payload = canonical(plan)
    digest = hashlib.sha256(payload).hexdigest()
    destination = (state_root or CENTRAL_ROOT / "state") / "maintenance" / f"{digest}.json"
    if destination.exists() and destination.read_bytes() != payload:
        raise PolicyError("기존 유지보수 계약 파일이 변경되었습니다.")
    atomic_write(destination, payload)
    return destination, digest, "".join(diff)


def apply(project: ProjectConfig, plan_file: Path, approved_sha256: str) -> Path:
    if re.fullmatch(r"[a-f0-9]{64}", approved_sha256) is None or plan_file.is_symlink():
        raise PolicyError("승인된 유지보수 계약 파일과 전체 SHA-256이 필요합니다.")
    payload = plan_file.read_bytes()
    if hashlib.sha256(payload).hexdigest() != approved_sha256:
        raise PolicyError("유지보수 계약의 승인 SHA-256이 파일과 다릅니다.")
    plan = json.loads(payload)
    if canonical(plan) != payload or plan.get("kind") != "policy-retirement" or plan.get("version") != 1:
        raise PolicyError("유지보수 canonical 계약 형식이 올바르지 않습니다.")
    common_raw = git(project.path, "rev-parse", "--git-common-dir").decode().strip()
    common = (Path(common_raw) if Path(common_raw).is_absolute() else project.path / common_raw).resolve()
    if plan.get("repository") != str(common) or plan.get("project") != project.id or plan.get("base") != project.base_branch:
        raise PolicyError("유지보수 계약의 저장소·프로젝트·기준 branch가 다릅니다.")
    state = load_runtime("runtime_state")
    with state.locked(common / "asan-agent-policy/maintenance.lock"):
        if git(project.path, "rev-parse", project.base_branch).decode().strip() != plan["base_head"]:
            raise PolicyError("승인 후 기준 HEAD가 변경되었습니다. 새 유지보수 계획이 필요합니다.")
        target = Path(plan["worktree"])
        if target.exists() or target.resolve() != target or target.is_relative_to(project.path.resolve()):
            raise PolicyError("승인된 새 유지보수 worktree 위치를 사용할 수 없습니다.")
        changes = plan.get("changes")
        if not isinstance(changes, list) or not changes:
            raise PolicyError("유지보수 변경 목록이 비어 있습니다.")
        prepared: list[tuple[str, bytes | None]] = []
        for change in changes:
            relative = change["path"]
            if Path(relative).is_absolute() or ".." in Path(relative).parts:
                raise PolicyError("유지보수 경로가 저장소 밖입니다.")
            before = git(project.path, "show", f"{plan['base_head']}:{relative}")
            after = base64.b64decode(change["after"], validate=True) if change["after"] is not None else None
            if hashlib.sha256(before).hexdigest() != change["before_sha256"] or replacement(relative, before) != after:
                raise PolicyError(f"허용된 퇴역 변경과 계약 diff가 다릅니다: {relative}")
            prepared.append((relative, after))
        rendered = render_project(project)
        guard = ModuleType("maintenance_branch_guard")
        guard.__file__ = str(CENTRAL_ROOT / "policy/guards/branch_guard.py")
        exec(compile(rendered[".agent-policy/runtime/branch_guard.py"], guard.__file__, "exec"), guard.__dict__)
        workflow_path = CENTRAL_ROOT / "policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py"
        workflow = ModuleType("maintenance_branch_workflow")
        workflow.__file__ = str(workflow_path)
        exec(compile(workflow_path.read_bytes(), str(workflow_path), "exec"), workflow.__dict__)
        contract = guard.canonical_contract(plan["branch"], "소비자 정책 사본·참조 퇴역", plan["base"],
            plan["base_head"], plan["base"], tuple(relative for relative, _ in prepared),
            f"승인된 유지보수 manifest {approved_sha256}", str(target), ("integrated",), plan["integrator"])
        destination = workflow.proposal_file(project.path, guard.contract_sha256(contract))
        proposal, digest = workflow.write_immutable_contract(destination, contract, guard, ".maintenance-")
        workflow.create(argparse.Namespace(proposal_file=str(proposal), proposal_sha256=digest), guard, project.path)
        for relative, after in prepared:
            path = target / relative
            if after is None:
                path.unlink()
            else:
                if path.is_symlink() or any(parent.is_symlink() for parent in path.parents):
                    raise PolicyError(f"유지보수 수정 경로가 심볼릭 링크입니다: {path}")
                atomic_write(path, after)
        # 검토·테스트·commit·통합은 생성된 V3 작업에서 별도로 수행한다.
        return target
