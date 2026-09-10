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
from types import ModuleType
from typing import Sequence

from .core import (
    CANONICAL_ROOT,
    CENTRAL_ROOT,
    PolicyError,
    ProjectConfig,
    audit_project,
    audit_source_contract,
    render_project,
    select_projects,
)
from .injection import (
    ARTIFACT_RESPONSIBILITY_ENV,
    INJECT_PROJECT_PATH_ENV,
    INJECT_TASK_ENV,
    InjectionLaunch,
    consumer_policy_sources,
    is_consumer_policy_path,
    prepare_injection,
)
from .log_mirror import assignment_log_sources, collect_project_logs, selected_channels
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

    start = subparsers.add_parser("start", help="중앙 inject 정책으로 host 세션을 시작합니다.")
    start.add_argument("--project", required=True, choices=("user-ui", "admin-ui"))
    start.add_argument("--host", required=True, choices=("codex", "claude", "opencode"))
    start.add_argument(
        "--mode",
        default="inject",
        choices=("inject",),
        help="기존 명령 호환용 옵션입니다. 중앙 정책은 inject 방식만 지원합니다.",
    )
    start.add_argument("--model", help="host에 전달할 model 이름")
    start.add_argument("--resume-assignment", help="원래 native session·bundle·승인을 유지할 assignment ID")
    start.add_argument(
        "--role",
        choices=INJECT_ROLES,
        help="inject 세션에 바인딩할 역할 (logic, ui, orchest, review, generate)",
    )
    start.add_argument("--worktree", help="세션 cwd로 사용할 같은 저장소의 worktree 절대 또는 상대 경로")
    start.add_argument("--branch", help="worktree에서 확인해야 할 현재 branch 이름")
    start.add_argument(
        "--task",
        help="현재 작업을 설명하는 문구. branch/worktree 소유권이나 접근 범위를 부여하지 않습니다.",
    )
    start.add_argument(
        "--responsibility",
        choices=("owner", "contributor"),
        default="owner",
        help="owner는 plan.md·final-summary.md, contributor는 handoff.md를 기록합니다.",
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

    handoff_parser = subparsers.add_parser("assignment-handoff", help="동일 host·role의 담당 assignment 교체 계약을 출력하거나 적용합니다.")
    handoff_parser.add_argument("--project", required=True, choices=("user-ui", "admin-ui"))
    handoff_parser.add_argument("--from-assignment", required=True)
    handoff_parser.add_argument("--to-assignment", required=True)
    handoff_parser.add_argument("--handoff-file", required=True)
    handoff_parser.add_argument("--approved-sha256")

    sessions = subparsers.add_parser("sessions", help="격리된 assignment의 이력 위치·bundle 상태·재개 명령을 조회합니다.")
    sessions.add_argument("--project", required=True, choices=("user-ui", "admin-ui"))
    sessions.add_argument("--host", choices=("codex", "claude", "opencode"))
    sessions.add_argument("--assignment")
    sessions.add_argument("--json", action="store_true")
    bundle_repair = subparsers.add_parser("bundle-repair", help="원본 정책이 모두 일치할 때 생성된 Python 캐시만 백업·격리합니다.")
    bundle_repair.add_argument("--project", required=True, choices=("user-ui", "admin-ui"))
    bundle_repair.add_argument("--assignment", required=True)

    recovery = subparsers.add_parser("assignment-recover", help="미확인 tool 결과의 현재 상태를 검토한 뒤 귀속 예약만 복구합니다.")
    recovery.add_argument("--project", required=True, choices=("user-ui", "admin-ui"))
    recovery.add_argument("--assignment", required=True)
    recovery.add_argument("--call-id", default="")
    recovery.add_argument("--outcome", choices=("confirmed", "cancelled"), required=True)
    recovery.add_argument("--approved-sha256")
    integration = subparsers.add_parser("integration-recover", help="실패한 병합의 정확한 상태를 검토한 뒤 merge --abort합니다.")
    integration.add_argument("--project", required=True, choices=("user-ui", "admin-ui"))
    integration.add_argument("--finish-file", required=True)
    integration.add_argument("--finish-sha256", required=True)
    integration.add_argument("--approved-sha256")

    integration_preserve = subparsers.add_parser("integration-preserve", help="검증 미완료 병합을 보존하고 검토한 worktree 예약만 해제합니다.")
    integration_preserve.add_argument("--project", required=True, choices=("user-ui", "admin-ui"))
    integration_preserve.add_argument("--finish-file", required=True)
    integration_preserve.add_argument("--finish-sha256", required=True)
    integration_preserve.add_argument("--reason", required=True)
    integration_preserve.add_argument("--related-task", action="append", default=[])
    integration_preserve.add_argument("--cancel-call", action="append", default=[], help="실패 근거를 확인한 원래 assignment의 미확인 도구 예약 ID")
    integration_preserve.add_argument("--approved-sha256")

    close_recovery = subparsers.add_parser("close-recover", help="검증된 동일 worktree cleanup 결함의 정리를 보류하고 CLOSED 기록만 복구합니다.")
    close_recovery.add_argument("--project", required=True, choices=("user-ui", "admin-ui"))
    close_recovery.add_argument("--finish-file", required=True)
    close_recovery.add_argument("--finish-sha256", required=True)
    close_recovery.add_argument("--approved-sha256")

    maintenance_plan = subparsers.add_parser("maintenance-plan", help="정책 퇴역의 정확한 diff와 새 V3 worktree 계약을 제안합니다.")
    maintenance_plan.add_argument("--project", required=True, choices=("user-ui", "admin-ui"))
    maintenance_plan.add_argument("--branch", required=True)
    maintenance_plan.add_argument("--worktree", required=True)
    maintenance_plan.add_argument("--host", required=True, choices=("codex", "claude", "opencode", "user"))
    maintenance_apply = subparsers.add_parser("maintenance-apply", help="승인된 퇴역 manifest만 새 V3 worktree에 적용합니다.")
    maintenance_apply.add_argument("--project", required=True, choices=("user-ui", "admin-ui"))
    maintenance_apply.add_argument("--plan-file", required=True)
    maintenance_apply.add_argument("--approved-sha256", required=True)

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
        issues = list(audit_project(project))
        conflicting_sources = consumer_policy_sources(project)
        if conflicting_sources:
            preview = ", ".join(conflicting_sources[:10])
            remainder = len(conflicting_sources) - 10
            suffix = f" 외 {remainder}개" if remainder > 0 else ""
            issues.append(
                f"consumer policy sources remain ({len(conflicting_sources)}): "
                f"{preview}{suffix}"
            )
        rendered_count = len(render_project(project))
        if issues:
            issue_count += len(issues)
            print(f"[{project.id}] FAIL ({rendered_count} bundle files)")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"[{project.id}] PASS ({rendered_count} bundle files)")
    if CENTRAL_ROOT.resolve() != CANONICAL_ROOT.resolve():
        print(f"[info] staging root: {CENTRAL_ROOT}; canonical root: {CANONICAL_ROOT}")
    return 1 if issue_count else 0


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


def task_start_denial(project: ProjectConfig) -> str | None:
    """host 실행 전에 선택 task의 실제 V3 계약과 dirty scope를 검증한다."""

    source = render_project(project)[".agent-policy/runtime/branch_guard.py"]
    guard = ModuleType(f"{project.id.replace('-', '_')}_start_branch_guard")
    guard.__file__ = str(CENTRAL_ROOT / "policy/guards/branch_guard.py")
    try:
        exec(compile(source, guard.__file__, "exec"), guard.__dict__)
        if guard.SHARED_GIT_ACCESS:
            return None
        denial = guard.active_branch_denial(project.path, allowed_states=("ACTIVE", "PRESERVED", "READY_TO_MERGE", "MERGED_VERIFIED"))
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise PolicyError(f"task branch 계약 검사기를 불러올 수 없습니다: {error}") from error
    if denial is not None and not isinstance(denial, str):
        raise PolicyError("task branch 계약 검사 결과가 올바르지 않습니다.")
    return denial


def pending_policy_retirements(project: ProjectConfig) -> tuple[str, ...]:
    """현재 branch에 아직 통합되지 않은 tracked 소비자 정책 삭제를 찾는다."""

    completed = subprocess.run(
        ("git", "status", "--porcelain=v1", "-z", "--untracked-files=no"),
        cwd=project.path,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise PolicyError(detail or f"Git 변경 상태를 확인할 수 없습니다: {project.path}")
    deleted: list[str] = []
    records = completed.stdout.split("\0")
    index = 0
    while index < len(records):
        record = records[index]
        index += 1
        if not record or len(record) < 4:
            continue
        status = record[:2]
        relative = record[3:]
        if "R" in status or "C" in status:
            index += 1
        if "D" in status and is_consumer_policy_path(relative):
            deleted.append(relative)
    return tuple(dict.fromkeys(deleted))


def run_start(
    project_id: str,
    host: str,
    model: str | None,
    print_only: bool,
    mode: str = "inject",
    worktree: str | None = None,
    expected_branch: str | None = None,
    session_dir: str | None = None,
    role: str | None = None,
    task: str | None = None,
    responsibility: str = "owner",
    resume_assignment: str | None = None,
) -> int:
    if responsibility not in ARTIFACT_RESPONSIBILITIES:
        raise PolicyError(f"지원하지 않는 산출물 책임입니다: {responsibility}")
    configured_project = select_projects(project_id)[0]
    project = (
        active_project(configured_project, worktree, expected_branch)
        if worktree is not None or expected_branch is not None
        else configured_project
    )
    conflicting_sources = consumer_policy_sources(project)
    if conflicting_sources:
        listed = ", ".join(conflicting_sources)
        raise PolicyError(
            "inject 세션은 소비자 저장소의 정책·프롬프트·훅을 함께 로드하지 않습니다. "
            f"선택된 worktree에서 중앙 history와 대조 후 제거해야 할 경로: {listed}"
        )
    if mode != "inject":
        raise PolicyError(f"지원하지 않는 start mode입니다: {mode}")
    if role is None:
        raise PolicyError("inject 모드는 --role logic|ui|orchest|review|generate 중 하나가 필요합니다.")
    selected_session_dir = normalized_session_dir(session_dir, host)
    issues = tuple((*audit_source_contract(), *audit_project(project)))
    if issues:
        raise PolicyError("중앙 정책 audit 실패: " + "; ".join(issues))
    if task is not None:
        branch_denial = task_start_denial(project)
        retirements = pending_policy_retirements(project)
        if branch_denial is not None and retirements and "승인된 작업 범위 밖" in branch_denial:
            raise PolicyError(
                "선택 task에 소비자 정책 사본 퇴역 삭제가 아직 Git에 통합되지 않았습니다. "
                "feature scope를 확장하거나 기능 commit에 섞지 말고, 별도 승인된 V3 maintenance "
                "branch에서 기준 branch에 통합한 뒤 현재 task를 갱신하세요. 경로: "
                + ", ".join(retirements)
            )
        if branch_denial is not None:
            raise PolicyError(f"task 세션 시작 거부: {branch_denial}")
    launch = prepare_injection(
        project,
        host,
        role,
        model,
        task=task,
        responsibility=responsibility,
        session_dir=selected_session_dir,
        resume_assignment=resume_assignment,
    )
    if launch.policy_comparison:
        print("policy-comparison: " + json.dumps(launch.policy_comparison, ensure_ascii=False), flush=True)
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
            assignment = os.environ.get("ASAN_AGENT_POLICY_ASSIGNMENT")
            state_root = os.environ.get("ASAN_AGENT_POLICY_STATE_ROOT")
            sources = None
            if assignment and state_root:
                if selected_channel != os.environ.get("ASAN_AGENT_POLICY_HOST", selected_channel):
                    continue
                sources = assignment_log_sources(project, selected_channel, assignment, Path(state_root))
            result = collect_project_logs(project, selected_channel, session_sources=sources)
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
                arguments.resume_assignment,
            )
        elif arguments.command == "sessions":
            from .sessions import list_sessions
            rows = list_sessions(select_projects(arguments.project)[0], arguments.host, arguments.assignment)
            if arguments.json:
                print(json.dumps(rows, ensure_ascii=False, indent=2))
            else:
                for row in rows:
                    status = "정상" if row["bundle"]["valid"] else "검사 실패: " + json.dumps(row["bundle"], ensure_ascii=False)
                    print(f"{row['assignment']}  {row['host']}/{row['role']}  {row['task'] or '(task 미지정)'}  {row['task_state']}\n  bundle: {status}")
                    if row["pending_calls"]:
                        print("  미확인 도구: " + ", ".join(row["pending_calls"]))
                    print(f"  native session: {row['native_session'] or '(시작 전)'}\n  CODEX_HOME: {row['codex_home'] or '(해당 없음)'}")
                    for transcript in row["transcripts"]:
                        print(f"  대화: {transcript}")
                    print(f"  재개: {row['resume_command'] or '(시작 전 또는 인계됨)'}")
            code = 0
        elif arguments.command == "bundle-repair":
            from .sessions import repair_bundle
            paths = repair_bundle(select_projects(arguments.project)[0], arguments.assignment)
            print(f"원본 bundle 확인 완료. 생성 캐시 {len(paths)}개 격리.")
            for path in paths:
                print(f"  백업: {path}")
            code = 0
        elif arguments.command == "assignment-recover":
            from .recovery import recover_assignment
            path, digest = recover_assignment(select_projects(arguments.project)[0], arguments.assignment,
                                               arguments.call_id, arguments.outcome, arguments.approved_sha256)
            print(f"tool 복구 계약: {path}\n복구 SHA-256: {digest}")
            code = 0
        elif arguments.command == "integration-recover":
            from .recovery import recover_integration
            path, digest = recover_integration(select_projects(arguments.project)[0], Path(arguments.finish_file),
                                                arguments.finish_sha256, arguments.approved_sha256)
            print(f"병합 중단 복구 계약: {path}\n복구 SHA-256: {digest}")
            code = 0
        elif arguments.command == "integration-preserve":
            from .recovery import preserve_integration
            path, digest = preserve_integration(select_projects(arguments.project)[0], Path(arguments.finish_file),
                                                arguments.finish_sha256, arguments.reason, tuple(arguments.related_task),
                                                arguments.approved_sha256, cancel_calls=tuple(arguments.cancel_call))
            print(f"통합 보존 계약: {path}\n보존 SHA-256: {digest}")
            print("PRESERVED 기록과 예약 해제 완료. 검증은 미완료로 유지합니다." if arguments.approved_sha256
                  else "계약 승인 후 같은 명령에 --approved-sha256을 지정하세요.")
            code = 0
        elif arguments.command == "close-recover":
            from .recovery import recover_close
            path, digest = recover_close(select_projects(arguments.project)[0], Path(arguments.finish_file),
                                         arguments.finish_sha256, arguments.approved_sha256)
            print(f"close 복구 계약: {path}\n복구 SHA-256: {digest}")
            print("CLOSED 복구 완료. branch·worktree 정리는 보류했습니다." if arguments.approved_sha256
                  else "계약 승인 후 같은 명령에 --approved-sha256을 지정하세요.")
            code = 0
        elif arguments.command == "assignment-handoff":
            from .assignment import handoff
            path, digest = handoff(select_projects(arguments.project)[0], arguments.from_assignment,
                                   arguments.to_assignment, Path(arguments.handoff_file), arguments.approved_sha256)
            print(f"handoff 계약: {path}\nhandoff SHA-256: {digest}")
            print("소유권 이전 완료" if arguments.approved_sha256 else "계약 승인 후 같은 명령에 --approved-sha256을 지정하세요.")
            code = 0
        elif arguments.command == "maintenance-plan":
            from .maintenance import preview
            path, digest, diff = preview(select_projects(arguments.project)[0], arguments.branch,
                                         Path(arguments.worktree), arguments.host)
            print(diff)
            print(f"유지보수 계약 파일: {path}\n유지보수 SHA-256: {digest}")
            print("이 diff와 새 V3 worktree 생성만 승인한 뒤 maintenance-apply를 실행하세요.")
            code = 0
        elif arguments.command == "maintenance-apply":
            from .maintenance import apply
            target = apply(select_projects(arguments.project)[0], Path(arguments.plan_file), arguments.approved_sha256)
            print(f"검토·검증할 V3 유지보수 worktree: {target}")
            code = 0
        elif arguments.command == "collect-logs":
            code = run_collect_logs(arguments.project, arguments.channel, arguments.quiet)
        else:
            raise PolicyError(f"지원하지 않는 command입니다: {arguments.command}")
    except PolicyError as error:
        print(f"agent-policy: {error}", file=sys.stderr)
        exit_code = 1 if arguments.command == "collect-logs" else 2
        raise SystemExit(exit_code) from error
    raise SystemExit(code)
