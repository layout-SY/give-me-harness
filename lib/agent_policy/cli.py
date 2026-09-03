from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from typing import Sequence

from .core import (
    CANONICAL_ROOT,
    CENTRAL_ROOT,
    PolicyError,
    ProjectDiff,
    ProjectConfig,
    audit_project,
    audit_source_contract,
    central_is_clean,
    diff_project,
    load_manifest,
    render_project,
    select_projects,
    start_command,
    sync_project,
    verify_safe_removals,
)
from .injection import (
    ARTIFACT_RESPONSIBILITY_ENV,
    INJECT_PROJECT_PATH_ENV,
    INJECT_TASK_ENV,
    InjectionLaunch,
    prepare_injection,
)
from .log_mirror import collect_project_logs, selected_channels
from .role_profiles import ARTIFACT_RESPONSIBILITIES, INJECT_ROLES, artifact_session_root


def project_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--project",
        default="all",
        choices=("all", "user-ui", "admin-ui"),
        help="대상 프로젝트",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-policy",
        description="중앙 AI 정책과 세션 산출물을 관리하고 host 세션을 시작합니다.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit = subparsers.add_parser("audit", help="중앙 소스와 대상 메타데이터를 검사합니다.")
    project_argument(audit)

    diff = subparsers.add_parser("diff", help="소비자 프로젝트 변경 예정 목록을 출력합니다.")
    project_argument(diff)
    diff.add_argument("--json", action="store_true", help="기계 판독 가능한 JSON 출력")

    check = subparsers.add_parser("check", help="manifest, 중앙 소스와 소비자 파일의 정합성을 검사합니다.")
    project_argument(check)
    check.add_argument("--quiet", action="store_true", help="정상 결과 출력을 생략합니다.")

    sync = subparsers.add_parser("sync", help="승인된 중앙 정책을 소비자 프로젝트에 배포합니다.")
    project_argument(sync)
    sync.add_argument(
        "--retire-legacy",
        action="store_true",
        help="감사 SHA-256이 일치하는 이전 중앙화 잔여 파일을 퇴역합니다.",
    )

    start = subparsers.add_parser("start", help="선택한 정책 모드와 host로 세션을 시작합니다.")
    start.add_argument("--project", required=True, choices=("user-ui", "admin-ui"))
    start.add_argument("--host", required=True, choices=("codex", "claude", "opencode"))
    start.add_argument(
        "--mode",
        default="sync",
        choices=("sync", "inject"),
        help="sync는 소비자 정합성을 요구하고, inject는 중앙 번들을 직접 주입합니다. (기본: sync)",
    )
    start.add_argument("--model", help="host에 전달할 model 이름")
    start.add_argument(
        "--role",
        choices=INJECT_ROLES,
        help="inject 세션에 바인딩할 역할 (logic, ui, orchest, review, generate)",
    )
    start.add_argument("--worktree", help="세션 cwd로 사용할 같은 저장소의 worktree 절대 또는 상대 경로")
    start.add_argument("--branch", help="worktree에서 확인해야 할 현재 branch 이름")
    start.add_argument(
        "--task",
        help="현재 세션에 배정할 승인된 task branch. 현재 worktree branch와 일치해야 합니다.",
    )
    start.add_argument(
        "--responsibility",
        choices=("owner", "contributor"),
        default="owner",
        help="owner는 8종 산출물, contributor는 handoff.md를 책임집니다.",
    )
    start.add_argument(
        "--session-dir",
        help="선택한 host의 세션 산출물 디렉터리(.<host>/logs/sessions/<task>)",
    )
    start.add_argument(
        "--print-only",
        action="store_true",
        help="inject 번들은 준비하되 host를 실행하지 않고 cwd, 환경과 명령만 출력합니다.",
    )

    collect_logs = subparsers.add_parser(
        "collect-logs",
        help="프로젝트의 필수 세션 산출물을 중앙 로그로 복사합니다.",
    )
    project_argument(collect_logs)
    collect_logs.add_argument(
        "--channel",
        default="all",
        choices=("all", "codex", "claude", "opencode", "unknown", "logic"),
        help="수집할 세션 로그 채널",
    )
    collect_logs.add_argument("--quiet", action="store_true", help="정상 결과 출력을 생략합니다.")
    return parser


def serialize_diff(result: ProjectDiff) -> dict[str, object]:
    return {
        "project": result.project.id,
        "path": str(result.project.path),
        "current": result.current,
        "added": list(result.added),
        "changed": list(result.changed),
        "stale": list(result.stale),
        "legacy": [
            {
                "path": trace.path,
                "sha256_matches_audit": trace.matches,
            }
            for trace in result.legacy
        ],
        "manifest_issues": list(result.manifest_issues),
    }


def print_diff(result: ProjectDiff) -> None:
    print(
        f"[{result.project.id}] current={str(result.current).lower()} "
        f"add={len(result.added)} change={len(result.changed)} "
        f"stale={len(result.stale)} legacy={len(result.legacy)}"
    )
    for label, paths in (
        ("A", result.added),
        ("M", result.changed),
        ("D", result.stale),
    ):
        for path in paths:
            print(f"  {label} {path}")
    for trace in result.legacy:
        status = "sha256-ok" if trace.matches else "sha256-mismatch"
        print(f"  L {trace.path} ({status})")
    for issue in result.manifest_issues:
        print(f"  ! {issue}")


def run_audit(selector: str) -> int:
    source_issues = audit_source_contract()
    issue_count = len(source_issues)
    if source_issues:
        print("[central-contract] FAIL")
        for issue in source_issues:
            print(f"  - {issue}")
    else:
        print("[central-contract] PASS")
    for project in select_projects(selector):
        issues = audit_project(project)
        rendered_count = len(render_project(project))
        if issues:
            issue_count += len(issues)
            print(f"[{project.id}] FAIL ({rendered_count} managed files)")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"[{project.id}] PASS ({rendered_count} managed files)")
    if CENTRAL_ROOT.resolve() != CANONICAL_ROOT.resolve():
        print(f"[info] staging root: {CENTRAL_ROOT}; canonical root: {CANONICAL_ROOT}")
    return 1 if issue_count else 0


def run_diff(selector: str, json_output: bool) -> int:
    results = [diff_project(project) for project in select_projects(selector)]
    if json_output:
        print(json.dumps([serialize_diff(result) for result in results], ensure_ascii=False, indent=2))
    else:
        for result in results:
            print_diff(result)
    return 0


def run_check(selector: str, quiet: bool) -> int:
    results = [diff_project(project) for project in select_projects(selector)]
    failed = [result for result in results if not result.current]
    if failed:
        for result in failed:
            if quiet:
                print(
                    f"{result.project.id}: 중앙 정책 또는 소비자 파일 drift가 있습니다.",
                    file=sys.stderr,
                )
            else:
                print_diff(result)
        return 1
    if not quiet:
        for result in results:
            print(f"[{result.project.id}] PASS")
    return 0


def run_sync(selector: str, retire_legacy: bool) -> int:
    projects = select_projects(selector)
    if not central_is_clean():
        raise PolicyError("중앙 정책 소스 변경을 commit한 뒤 sync해 주세요.")

    for project in projects:
        rendered = render_project(project)
        verify_safe_removals(
            project,
            rendered,
            load_manifest(project),
            retire_legacy,
        )
    for project in projects:
        count = sync_project(project, retire_legacy=retire_legacy)
        print(f"[{project.id}] synced {count} managed files")
    return 0


def display_injection_command(launch: InjectionLaunch) -> str:
    displayed: list[str] = []
    redact_next_prompt = False
    for argument in launch.command:
        if redact_next_prompt:
            displayed.append(f"@{launch.system_prompt}")
            redact_next_prompt = False
        elif argument == "--append-system-prompt":
            displayed.append(argument)
            redact_next_prompt = True
        elif argument.startswith("developer_instructions="):
            displayed.append(f"developer_instructions=@{launch.system_prompt}")
        elif argument.startswith("skills.config="):
            displayed.append("skills.config=<consumer project skills disabled>")
        else:
            displayed.append(argument)
    return shlex.join(displayed)


def git_output(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ("git", *arguments),
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise PolicyError(detail or f"Git 상태를 확인할 수 없습니다: {root}")
    return completed.stdout.strip()


def git_common_directory(root: Path) -> Path:
    raw = git_output(root, "rev-parse", "--git-common-dir")
    candidate = Path(raw)
    return (candidate if candidate.is_absolute() else root / candidate).resolve()


def active_project(
    project: ProjectConfig,
    worktree: str | None,
    expected_branch: str | None,
) -> ProjectConfig:
    configured_path = Path(str(project.path)).resolve()
    target = Path(worktree).expanduser().resolve() if worktree else configured_path
    if not target.is_dir():
        raise PolicyError(f"세션 worktree를 찾을 수 없습니다: {target}")
    top_level = Path(git_output(target, "rev-parse", "--show-toplevel")).resolve()
    if top_level != target:
        raise PolicyError(f"worktree 루트 경로를 지정해야 합니다: {target} (실제 루트: {top_level})")
    if git_common_directory(configured_path) != git_common_directory(target):
        raise PolicyError(f"대상 프로젝트와 다른 Git 저장소입니다: {target}")
    current_branch = git_output(target, "branch", "--show-current")
    if expected_branch and current_branch != expected_branch:
        raise PolicyError(
            f"요청한 branch와 worktree의 현재 branch가 다릅니다: "
            f"요청={expected_branch}, 현재={current_branch or 'detached HEAD'}"
        )
    return replace(project, path=target)


def normalized_session_dir(value: str | None, host: str) -> str | None:
    if value is None:
        return None
    path = Path(value)
    root = Path(artifact_session_root(host))
    expected_length = len(root.parts) + 1
    if (
        path.is_absolute()
        or len(path.parts) != expected_length
        or path.parts[: len(root.parts)] != root.parts
    ):
        raise PolicyError(
            f"--session-dir는 {root.as_posix()}/<task> 형식의 상대 경로여야 합니다."
        )
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{1,127}", path.parts[-1]) is None:
        raise PolicyError("--session-dir 작업 이름이 올바르지 않습니다.")
    return path.as_posix()


def run_start(
    project_id: str,
    host: str,
    model: str | None,
    print_only: bool,
    mode: str = "sync",
    worktree: str | None = None,
    expected_branch: str | None = None,
    session_dir: str | None = None,
    role: str | None = None,
    task: str | None = None,
    responsibility: str = "owner",
) -> int:
    if responsibility not in ARTIFACT_RESPONSIBILITIES:
        raise PolicyError(f"지원하지 않는 산출물 책임입니다: {responsibility}")
    if task is not None and re.fullmatch(r"task/[a-z0-9]+(?:-[a-z0-9]+)*", task) is None:
        raise PolicyError("--task는 task/<ascii-kebab-summary> 형식이어야 합니다.")
    configured_project = select_projects(project_id)[0]
    project = (
        active_project(configured_project, worktree, expected_branch)
        if worktree is not None or expected_branch is not None
        else configured_project
    )
    current_branch = ""
    if task is not None or expected_branch is not None:
        current_branch = git_output(project.path, "branch", "--show-current")
        if task is not None and current_branch != task:
            raise PolicyError(
                f"--task와 worktree의 현재 branch가 다릅니다: task={task}, 현재={current_branch or 'detached HEAD'}"
            )
    if expected_branch is not None and task is not None and expected_branch != task:
        raise PolicyError(f"--branch와 --task가 다릅니다: {expected_branch} != {task}")
    if mode == "inject" and role is None:
        raise PolicyError("inject 모드는 --role logic|ui|orchest|review|generate 중 하나가 필요합니다.")
    if mode == "sync" and role is not None:
        raise PolicyError("--role은 --mode inject에서만 사용할 수 있습니다.")
    selected_session_dir = normalized_session_dir(session_dir, host)
    result = diff_project(project)
    if mode == "sync":
        if not result.current:
            print_diff(result)
            raise PolicyError(
                "세션 시작을 중단했습니다. 중앙 프로젝트에서 diff와 승인된 sync를 완료하고 다시 실행하세요."
            )
        command = start_command(project, host, model)
        if print_only:
            print(f"mode: sync")
            print(f"responsibility: {responsibility}")
            if task is not None:
                print(f"task: {task}")
            print(f"cwd: {project.path}")
            print("command: " + " ".join(command))
            return 0
        environment = dict(os.environ)
        environment[INJECT_PROJECT_PATH_ENV] = str(project.path)
        environment[ARTIFACT_RESPONSIBILITY_ENV] = responsibility
        if task is not None:
            environment[INJECT_TASK_ENV] = task
        if selected_session_dir is not None:
            environment["ASAN_SESSION_DIR"] = selected_session_dir
        os.chdir(project.path)
        os.execvpe(command[0], list(command), environment)
        return 0

    if mode != "inject":
        raise PolicyError(f"지원하지 않는 start mode입니다: {mode}")
    issues = audit_project(project)
    if issues:
        raise PolicyError("중앙 정책 audit 실패: " + "; ".join(issues))
    if not result.current:
        print(
            f"[{project.id}] 소비자 정책 drift가 있습니다 "
            f"(add={len(result.added)} change={len(result.changed)} "
            f"stale={len(result.stale)} legacy={len(result.legacy)}). "
            "inject 번들로 세션을 계속합니다.",
            file=sys.stderr,
        )
    launch = prepare_injection(
        project,
        host,
        role,
        model,
        task=task,
        responsibility=responsibility,
    )
    if print_only:
        print("mode: inject")
        print(f"role: {launch.role}")
        print(f"responsibility: {responsibility}")
        if task is not None:
            print(f"task: {task}")
        print(f"cwd: {project.path}")
        print(f"bundle: {launch.bundle_root}")
        print(f"system-prompt: {launch.system_prompt}")
        for name, value in sorted(launch.environment.items()):
            print(f"env: {name}={value}")
        print("command: " + display_injection_command(launch))
        return 0
    environment = dict(os.environ)
    environment.update(launch.environment)
    if selected_session_dir is not None:
        environment["ASAN_SESSION_DIR"] = selected_session_dir
    os.chdir(project.path)
    os.execvpe(launch.command[0], list(launch.command), environment)
    return 0


def run_collect_logs(selector: str, channel: str, quiet: bool) -> int:
    for project in select_projects(selector):
        runtime_path = os.environ.get(INJECT_PROJECT_PATH_ENV)
        if runtime_path:
            project = active_project(project, runtime_path, None)
        for selected_channel in selected_channels(channel):
            result = collect_project_logs(project, selected_channel)
            if quiet:
                continue
            state = "source-missing" if result.source_missing else "ok"
            print(
                f"[{result.project_id}:{result.channel}] {state} "
                f"copied={len(result.copied)} unchanged={result.unchanged}"
            )
    return 0


def main(argv: Sequence[str] | None = None) -> None:
    arguments = build_parser().parse_args(argv)
    try:
        if arguments.command == "audit":
            code = run_audit(arguments.project)
        elif arguments.command == "diff":
            code = run_diff(arguments.project, arguments.json)
        elif arguments.command == "check":
            code = run_check(arguments.project, arguments.quiet)
        elif arguments.command == "sync":
            code = run_sync(arguments.project, arguments.retire_legacy)
        elif arguments.command == "start":
            code = run_start(
                arguments.project,
                arguments.host,
                arguments.model,
                arguments.print_only,
                arguments.mode,
                arguments.worktree,
                arguments.branch,
                arguments.session_dir,
                arguments.role,
                arguments.task,
                arguments.responsibility,
            )
        elif arguments.command == "collect-logs":
            code = run_collect_logs(arguments.project, arguments.channel, arguments.quiet)
        else:
            raise PolicyError(f"지원하지 않는 command입니다: {arguments.command}")
    except PolicyError as error:
        print(f"agent-policy: {error}", file=sys.stderr)
        exit_code = 1 if arguments.command == "collect-logs" else 2
        raise SystemExit(exit_code) from error
    raise SystemExit(code)
