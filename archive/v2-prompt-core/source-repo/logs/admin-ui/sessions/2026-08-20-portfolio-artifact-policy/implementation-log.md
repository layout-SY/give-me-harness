# 구현 로그

## 작업 요약
- portfolio 경험 기록을 정책 문서에서 실행 가능한 완료 gate로 확장했다.
- 정책·template·agent·workflow·multi-agent spec·hook 문서를 동일 규칙으로 정렬했다.
- Python Stop hook이 source/config/harness와 untracked 변경을 감지하고 동일 slug portfolio의 필수 7개 섹션을 검사하도록 변경했다.

## 재사용 자산
- 기존 `policy-portfolio`
- 기존 `.codex/logs/portfolio/` 경로
- 기존 session slug와 Stop hook
- 기존 `grill-me-review.md` validator 구조

## 신규 파일 / 수정 파일
- 신규: `.codex/templates/portfolio-entry.template.md`
- 신규: `.codex/hooks/test_portfolio_gate.py`
- 수정: `AGENTS.md`, portfolio/documentation/harness/review policy
- 수정: agent·workflow·multi-agent spec·hook·harness 문서
- 수정: `.codex/hooks/hook_common.py`, `.codex/hooks/require-documentation-stop.py`

## 핵심 로직
- `changed_files()`가 tracked unstaged, staged, untracked 파일을 합산한다.
- `requires_completion_artifacts()`가 application/tooling과 AI harness 변경을 판정하고 `.codex/logs/**`·Python cache를 제외한다.
- PostToolUse가 현재 작업의 session slug를 runtime marker에 기록하고 Stop hook은 그 slug만 검사한다.
- portfolio 문서의 작업 개요, 문제 상황, 의사결정, 기술 목적, 적용, 결과, 회고 섹션을 검증한다.

## 검증 / 요청 처리
- RED: 기존 hook은 source 변경 후 portfolio가 없어도 통과했다.
- GREEN: source·harness·root config·untracked·active-session 우회·PostToolUse marker·필수 섹션·정상 통과·log-only 9개 시나리오가 통과했다.
- `uv`와 pytest가 환경에 없어 외부 dependency 없는 `python3` 회귀 스크립트로 전환했다.
- Python 구문 검사, strict no-excuse 검사, `hooks.json` JSON parse가 통과했다.
- active marker 없는 Stop은 차단되고, PostToolUse로 현재 slug를 기록한 뒤 Stop은 `continue: true`를 반환했다.

## 리스크
- portfolio 내용의 사실성은 구조 검사만으로 완전히 증명할 수 없어 Watcher evidence 검토가 필요하다.
- 동일 저장소에서 두 작업이 동시에 같은 runtime state marker를 갱신하는 실행 모델은 지원하지 않는다.

## 핸드오프 메모
- 1차 대체 Watcher가 root config와 mtime 세션 선택을 반려했고 두 항목을 수정했다.
- 대체 Evaluator의 orchestrator 책임 혼재 지적을 반영해 Planner는 evidence 반환, Codex orchestrator는 문서 작성으로 정렬했다.
- 보정 후 새 대체 Watcher가 최종 PASS했다.
