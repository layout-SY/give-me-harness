#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Final

sys.path.insert(0, str(Path(__file__).resolve().parent))

import hook_common as common

REQUIRED_ARTIFACTS: Final = (
    "plan.md",
    "exploration.md",
    "implementation-log.md",
    "grill-me-review.md",
    "review-log.md",
    "evaluation-log.md",
    "final-summary.md",
    "portfolio-log.md",
)
TABLE_SEPARATOR: Final = re.compile(r"\|\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?")
PORTFOLIO_CASE: Final = re.compile(r"^##\s+사례\b.*$", re.MULTILINE)
PORTFOLIO_HEADINGS: Final = (
    "문제 상황",
    "고민과 선택",
    "적용",
    "사용 기술과 구체적 목적",
    "결과",
    "이력서·포트폴리오 문구",
)
PORTFOLIO_FIELDS: Final = ("작업 유형", "관련 도메인/서비스", "문제 출처")


def is_bound_session(path: Path) -> bool:
    sessions = (common.ROOT / ".codex" / "logs" / "sessions").resolve()
    if path.is_symlink():
        return False
    try:
        resolved = path.resolve()
        relative = resolved.relative_to(sessions)
    except (OSError, ValueError):
        return False
    return len(relative.parts) == 1 and resolved.is_dir()


def has_substantive_content(text: str) -> bool:
    table_rows = 0
    separator_seen = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("<!--"):
            continue
        if TABLE_SEPARATOR.fullmatch(line):
            separator_seen = True
            continue
        if line.startswith("|"):
            if separator_seen:
                table_rows += 1
            continue
        normalized = re.sub(r"^[\-*+>\d.()\s]+", "", line).strip()
        if len(normalized) >= 8 and re.search(r"\w", normalized):
            return True
    return table_rows > 0


def has_flow_data_row(section: str) -> bool:
    separator_seen = False
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if TABLE_SEPARATOR.fullmatch(line):
            separator_seen = True
            continue
        if not separator_seen or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) >= 5 and all(cells[:5]):
            return True
    return False


def portfolio_issues(text: str) -> list[str]:
    matches = list(PORTFOLIO_CASE.finditer(text))
    if not matches:
        return ["portfolio-log.md: missing case"]
    issues: list[str] = []
    for index, match in enumerate(matches, start=1):
        end = matches[index].start() if index < len(matches) else len(text)
        section = text[match.end():end]
        headings = set(re.findall(r"^###\s+(.+?)\s*$", section, re.MULTILINE))
        missing_headings = [heading for heading in PORTFOLIO_HEADINGS if heading not in headings]
        missing_fields = [
            field
            for field in PORTFOLIO_FIELDS
            if re.search(rf"^-\s*{re.escape(field)}\s*:", section, re.MULTILINE) is None
        ]
        if missing_headings or missing_fields:
            missing = ", ".join((*missing_fields, *missing_headings))
            issues.append(f"portfolio-log.md: incomplete case {index} ({missing})")
    return issues


def artifact_issues(session: Path) -> list[str]:
    issues: list[str] = []
    artifact_texts: dict[str, str] = {}
    for name in REQUIRED_ARTIFACTS:
        target = session / name
        if target.is_symlink() or not target.is_file():
            issues.append(f"{name}: missing or symlinked")
            continue
        try:
            text = target.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            issues.append(f"{name}: unreadable")
            continue
        artifact_texts[name] = text
        if not has_substantive_content(text):
            issues.append(f"{name}: empty or header-only")
    grill = session / "grill-me-review.md"
    if grill.is_file() and not grill.is_symlink():
        text = grill.read_text(encoding="utf-8")
        normalized = text.casefold()
        if "## method guardrails" not in normalized:
            issues.append("grill-me-review.md: missing Method Guardrails")
        if "neutral question-first 적용 여부" not in normalized:
            issues.append("grill-me-review.md: missing neutral question-first check")
        match = re.search(r"##\s*neutral question flow\s*(.*?)(?:\n##\s+|\Z)", text, re.S | re.I)
        if match is None or not has_flow_data_row(match.group(1)):
            issues.append("grill-me-review.md: missing Q/A data row")
        if "recommended answer" not in normalized:
            issues.append("grill-me-review.md: missing recommended answer column")
    portfolio = artifact_texts.get("portfolio-log.md")
    if portfolio is not None:
        issues.extend(portfolio_issues(portfolio))
    return issues


def evaluate_stop(event: common.Event) -> tuple[bool, str]:
    identity = common.parse_identity(event, "Stop")
    if identity is None or not isinstance(event.get("stop_hook_active"), bool):
        return False, "harness event identity/provenance is missing"
    state = common.load_state(identity)
    protected_change = state.source_mutated or any(
        common.is_protected_path(path) for path in common.changed_files()
    )
    if not protected_change:
        common.clear_state(identity)
        return True, "Harness gates checked"
    if not state.active_session:
        return False, "current session has no explicitly bound task artifact directory"
    session = Path(state.active_session)
    if not is_bound_session(session):
        return False, "bound task artifact directory is invalid or symlinked"
    issues = artifact_issues(session)
    if issues:
        return False, "artifact validation failed: " + "; ".join(issues)
    common.clear_state(identity)
    return True, "Harness gates checked"


def main() -> None:
    allowed, message = evaluate_stop(common.read_event())
    if allowed:
        common.emit_stop_allow()
        return
    common.emit_stop_block(f"[Codex Hook][Stop][Blocked] {message}.")


if __name__ == "__main__":
    main()
