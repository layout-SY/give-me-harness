from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Sequence

from .core import (
    CANONICAL_ROOT,
    CENTRAL_ROOT,
    PolicyError,
    ProjectDiff,
    audit_project,
    central_is_clean,
    diff_project,
    load_manifest,
    render_project,
    select_projects,
    start_command,
    sync_project,
    verify_safe_removals,
)
from .log_mirror import collect_project_logs, selected_channels


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

    start = subparsers.add_parser("start", help="정합성 확인 후 선택한 host 세션을 시작합니다.")
    start.add_argument("--project", required=True, choices=("user-ui", "admin-ui"))
    start.add_argument("--host", required=True, choices=("codex", "claude", "opencode"))
    start.add_argument("--model", help="host에 전달할 model 이름")
    start.add_argument(
        "--print-only",
        action="store_true",
        help="실행하지 않고 cwd와 명령만 출력합니다.",
    )

    collect_logs = subparsers.add_parser(
        "collect-logs",
        help="프로젝트의 필수 세션 산출물을 중앙 로그로 복사합니다.",
    )
    project_argument(collect_logs)
    collect_logs.add_argument(
        "--channel",
        default="all",
        choices=("all", "logic", "claude"),
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
    issue_count = 0
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


def run_start(project_id: str, host: str, model: str | None, print_only: bool) -> int:
    project = select_projects(project_id)[0]
    result = diff_project(project)
    if not result.current:
        print_diff(result)
        raise PolicyError(
            "세션 시작을 중단했습니다. 중앙 프로젝트에서 diff와 승인된 sync를 완료하고 다시 실행하세요."
        )
    command = start_command(project, host, model)
    if print_only:
        print(f"cwd: {project.path}")
        print("command: " + " ".join(command))
        return 0
    os.chdir(project.path)
    os.execvp(command[0], command)
    return 0


def run_collect_logs(selector: str, channel: str, quiet: bool) -> int:
    for project in select_projects(selector):
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
