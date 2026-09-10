"""V4: 프로젝트 전체 접근, Git 변경 승인, host/session 기록 보호.

이 모듈은 branch 계약, Git claim, 완료 예약을 권한으로 읽거나 쓰지 않는다.
과거 V3 실행·복구 코드는 별도 경로에 남으며 새 세션에서는 사용하지 않는다.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from types import ModuleType

_loader_path = Path(__file__).resolve().with_name("runtime_loader.py")
_loader = ModuleType("asan_shared_loader")
_loader.__file__ = str(_loader_path)
exec(compile(_loader_path.read_bytes(), str(_loader_path), "exec"), _loader.__dict__)
config = _loader.load("runtime_config")
paths = _loader.load("tool_paths")
artifacts = _loader.load("artifact_policy")
approval = _loader.load("approval_policy")
protocol = _loader.load("event_protocol")
branch = config.branch_guard
state = config.runtime_state


def protected_path(root: Path, relative: str, host: str, event: dict) -> str | None:
    """소스 위치와 독립된 host/session 경계. Git 병합은 기존 기록 전달만 허용한다."""
    parts = Path(relative).parts
    if not parts:
        return None
    if parts[0] == ".git":
        return ".git 내부 파일은 직접 편집하지 않고 승인된 Git 명령으로 관리하세요."
    for other in branch.KNOWN_HOSTS:
        if parts[0] == f".{other}" and other != host:
            return f"다른 host({other})의 설정·세션 산출물은 읽기 전용입니다: {relative}"
    prefix = artifacts.artifact_sessions_prefix(host)
    if relative.startswith(prefix):
        record = artifacts.session_binding_record(event, root, host)
        directory = record.get("directory") or os.environ.get(config.SESSION_DIR_ENV, "").strip("/")
        if directory and relative != directory and not relative.startswith(directory.rstrip("/") + "/"):
            return f"다른 세션의 산출물은 읽기 전용입니다: {relative}"
    return None


def bind_artifacts(event: dict, root: Path, host: str, contexts: list) -> str | None:
    """동일 세션의 논리적 로그 경로만 유지하고 branch/worktree 이동은 허용한다."""
    selected = [(target, relative) for target, relative in contexts
                if relative.startswith(artifacts.artifact_sessions_prefix(host))]
    if not selected:
        return None
    target, relative = selected[0]
    directory = artifacts.artifact_session_directory(target, relative, host)
    if directory is None:
        return "세션 산출물 경로를 확인할 수 없습니다."
    logical = directory.relative_to(target).as_posix()
    if any(artifacts.artifact_session_directory(other, name, host) != directory for other, name in selected):
        return "한 번의 쓰기에서는 한 세션 산출물 위치를 사용하세요."
    binding_path = artifacts.session_binding_path(event, root, host)
    if binding_path is None:
        return "세션 산출물을 기록하려면 실제 session ID가 필요합니다."
    common = branch.git_common_directory(root) or root
    resource = "artifact:" + host + ":" + logical
    existing = state.read(state.repository_state(common) / "claims" / (state.digest(resource) + ".json"))
    if existing and existing.get("owner") != state.owner_id(host, paths.event_session_id(event)):
        return f"다른 세션의 산출물은 읽기 전용입니다: {logical}"
    artifacts._BINDING_DRAFT[binding_path] = {
        "directory": logical, "worktree": str(target), "branch": "", "task": "",
        "contract_version": "4", "merge_target": "",
        "responsibility": os.environ.get(config.ARTIFACT_RESPONSIBILITY_ENV, "owner"),
    }
    return None


def git_denial(event: dict, root: Path, host: str, command: str, cwd: Path) -> str | None:
    invocations = branch.git_invocations(root, command, cwd)
    if invocations is None:
        return "Git 대상과 변경 범위를 확인할 수 없습니다. 실제 Git 명령과 workdir 또는 git -C를 명시하세요."
    for invocation in invocations:
        if branch.git_arguments_are_read_only(invocation.arguments):
            continue
        if not branch.same_git_repository(root, invocation.root):
            return f"현재 프로젝트와 다른 Git 저장소입니다: {invocation.root}"
        if invocation.unsafe_repository_options:
            return "Git 대상 경로가 모호합니다. 실제 worktree를 workdir 또는 git -C로 지정하세요."
        args = invocation.arguments
        if not args:
            continue
        # Git의 --output/--file 역시 파일 쓰기다. 명령 이름이 조회형이어도
        # 다른 host 기록·중앙 정책·.git을 출력 대상으로 삼을 수 없다.
        for index, arg in enumerate(args):
            raw = args[index + 1] if arg in {"--output", "--file", "-f"} and index + 1 < len(args) and (
                arg != "-f" or args[0] == "config") else (
                    arg.split("=", 1)[1] if arg.startswith(("--output=", "--file=")) else "")
            if raw:
                target = (invocation.root / raw).resolve()
                if paths.target_in_injected_policy(target):
                    return "중앙 정책 스냅샷을 Git의 파일 출력 대상으로 사용할 수 없습니다."
                context = paths.repository_target(root, raw, invocation.root)
                if context:
                    denial = protected_path(*context, host, event)
                    if denial:
                        return denial
                    if paths.is_managed(context[1], set(), config.MANAGED_POLICY_ROOTS):
                        return "관리 정책 파일은 중앙 원본에서 수정하세요."
        # stage/commit은 실제 포함할 변경만 검사한다. 다른 host의 dirty 파일이
        # worktree에 있다는 이유만으로 관련 없는 source commit을 막지 않는다.
        affected: tuple[str, ...] = ()
        if args[0] == "add":
            explicit = branch._pathspecs_after_separator(args)
            if not explicit:
                return "commit할 파일을 확인할 수 있도록 git add -- <경로>를 명시하세요."
            changed = branch.changed_paths(invocation.root)
            matching = branch._git(invocation.root, "ls-files", "-c", "-o", "--exclude-standard", "-z", "--", *explicit)
            if matching.returncode:
                return "stage할 Git 경로를 확인할 수 없습니다."
            selected = set(matching.stdout.split("\0"))
            # 삭제한 파일도 ls-files의 cached 목록에 남으므로 검증한다.
            affected = tuple(name for name in changed if name in selected)
            for value in explicit:
                context = paths.repository_target(root, value, invocation.root)
                if context:
                    denial = protected_path(*context, host, event)
                    if denial:
                        return denial
        elif args[0] == "commit":
            affected = branch.staged_paths(invocation.root)
            if any(value in {"--all", "--only", "--include"} or re.fullmatch(r"-[A-Za-z]*[aio][A-Za-z]*", value)
                   for value in args[1:]):
                affected = tuple(set(affected) | set(branch.changed_paths(invocation.root)))
        elif args[0] in {"restore", "checkout"} and "--" in args:
            selected = branch._git(invocation.root, "ls-files", "-z", "--", *branch._pathspecs_after_separator(args))
            if selected.returncode:
                return "복원할 Git 경로를 확인할 수 없습니다."
            affected = tuple(filter(None, selected.stdout.split("\0")))
        elif args[0] == "clean":
            options = () if any(value == "-x" or value.startswith("-") and not value.startswith("--") and "x" in value
                                for value in args[1:]) else ("--exclude-standard",)
            result = branch._git(invocation.root, "ls-files", "--others", *options, "-z", "--",
                                 *(branch._pathspecs_after_separator(args) or tuple(f".{value}" for value in branch.KNOWN_HOSTS)))
            if result.returncode:
                return "삭제될 세션 기록을 확인할 수 없습니다."
            affected = tuple(filter(None, result.stdout.split("\0")))
        elif args[0] in {"reset", "stash"}:
            # 일반 source 동작은 승인할 수 있지만 타 세션 로그의 직접
            # 복원·삭제·stash는 읽기 전용 경계를 넘는다.
            affected = branch.changed_paths(invocation.root)
            if "--" in args:
                result = branch._git(invocation.root, "ls-files", "-c", "-o", "--exclude-standard", "-z", "--",
                                     *branch._pathspecs_after_separator(args))
                if result.returncode:
                    return "변경할 경로를 확인할 수 없습니다."
                selected = set(result.stdout.split("\0"))
                affected = tuple(name for name in affected if name in selected)
        if branch.GIT_STATUS_UNAVAILABLE in affected:
            return "Git 변경 상태를 확인할 수 없습니다."
        for relative in affected:
            denial = protected_path(invocation.root, relative, host, event)
            if denial:
                return denial
    return None


def pre_tool(event: dict, root: Path, host: str) -> None:
    tool = paths.normalized_tool_name(event)
    data = event.get("tool_input") or {}
    command = str(data.get("command") or "")
    shell = tool in config.SHELL_TOOLS
    cwd = paths.shell_working_directory(root, data)
    if shell and paths.unsupported_workflow_invocation(command, root):
        protocol.emit_denial(host, "이전 branch workflow로 Git 승인을 우회할 수 없습니다. 일반 Git 명령을 사용하세요.")
        return
    if shell and paths.trusted_branch_workflow_action(command, root):
        protocol.emit_denial(host, "V4에서는 branch workflow 계약을 사용하지 않습니다. 일반 Git 명령의 대상·영향을 보고하고 승인받으세요.")
        return
    denied = paths.denied_targets(event, root)
    if denied:
        protocol.emit_denial(host, paths.denial_message(denied))
        return
    contexts = []
    raw_targets = paths.structured_targets(data) if tool in config.STRUCTURED_MUTATION_TOOLS else []
    if tool in {"apply_patch", "patch"}:
        raw_targets.extend(paths.patch_targets(command))
    for raw in raw_targets:
        context = paths.repository_target(root, raw, cwd)
        if context is None:
            protocol.emit_denial(host, f"현재 프로젝트의 worktree 밖에 있는 변경 대상입니다: {raw}")
            return
        denial = protected_path(*context, host, event)
        if not denial and context[1].startswith(artifacts.artifact_sessions_prefix(host)):
            denial = artifacts.artifact_layout_denial(*context, host)
        if denial:
            protocol.emit_denial(host, denial)
            return
        contexts.append(context)
    if shell:
        if paths.has_non_git_shell_mutation(command):
            protocol.emit_denial(host, "파일 변경은 대상이 명확한 Edit/Write/apply_patch 도구를 사용하세요.")
            return
        for raw in paths.shell_redirect_targets(command):
            target = paths.resolved_shell_target(root, data, raw)
            if target is None:
                protocol.emit_denial(host, "리다이렉션 대상이 명확하지 않습니다.")
                return
            context = paths.repository_target(root, str(target))
            if context:
                protocol.emit_denial(host, protected_path(*context, host, event) or "파일 변경은 구조화된 쓰기 도구를 사용하세요.")
                return
        if branch._git_commands(command):
            denial = git_denial(event, root, host, command, cwd)
            if denial:
                protocol.emit_denial(host, denial)
                return
    denial = bind_artifacts(event, root, host, contexts)
    if denial:
        protocol.emit_denial(host, denial)
        return
    if tool in config.STRUCTURED_MUTATION_TOOLS and approval.implementation_gate_required(event, root):
        role = os.environ.get(config.INJECT_ROLE_ENV, "")
        if role and role not in branch.RUNTIME_CONTRACT["capabilities"]["source_write"]:
            protocol.emit_denial(host, f"{role} 역할은 source를 변경할 수 없습니다. Git 변경 권한과 구현 역할은 별개입니다.")
            return
        denial = approval.implementation_gate_denial(event, root, host)
        if denial:
            protocol.emit_denial(host, denial)
            return
    categories = paths.protected_operation_categories(command) if shell else ()
    if categories:
        if host != "claude" and approval.operation_allowed(event, cwd, host, command):
            return
        message = f"{', '.join(categories)} 변경 실행 전에 사용자 승인이 필요합니다.\n작업 위치: {cwd}\n명령: {command}\n"
        message += ("호스트 권한 요청에서 승인하세요." if host == "claude" else
                    "이 작업 단위의 대상과 영향을 확인한 뒤 진행 또는 명령 실행 승인으로 답하세요. 승인은 동일 위치·상태·명령에 한 번만 사용합니다.")
        protocol.emit_operation_approval(host, message)
        return
    artifacts.reserve_binding(event, root, host)
