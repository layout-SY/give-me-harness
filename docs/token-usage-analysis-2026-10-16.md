# 오케스트레이션 세션의 토큰 사용량 분석

## 배경

2026-10-15 admin-ui의 `orchest` 세션 `swagger-api-명세-대조`에서 사용자 요청으로 토큰 사용량 보고서를 만들었다. 보고서는 `unknown/token-usage-report-swagger-api-명세-대조.md`이고, 세션이 직접 쓴 집계 스크립트는 `unknown/token-usage-analysis.py`다. 이 보고서가 하위 에이전트 재개, 단계 연속 처리, 문서 재작성 같은 비용 원인을 찾아냈다. 그래서 같은 분석을 다른 세션에서도 같은 기준으로 반복할 수 있게 중앙 스킬로 승격했다.

## 사용자 결정 (2026-10-16)

| 항목 | 결정 |
| --- | --- |
| 요청 | 사용자가 `토큰 분석`을 입력한다. `토큰 분석 취소`로 거둔다 |
| 시점 | 작업 병합 뒤, branch·worktree 정리 전. guard가 확인한다 |
| 대상 host | Claude Code, Codex, OpenCode |
| 집계 | 중앙 스킬에 공용 스크립트를 둔다 |
| 적용 role | `orchest` 세션만 |

## 구성

| 파일 | 내용 |
| --- | --- |
| `policy/common/skills/policy/token-usage/SKILL.md` | 적용 조건, 집계 기준, 절차, host별 기록 위치와 차이 |
| `policy/common/skills/policy/token-usage/references/report.md` | 보고서 0~9절 구조와 절별 필수 항목 |
| `policy/common/skills/policy/token-usage/scripts/token_usage.py` | 읽기 전용 집계 스크립트(`sessions`, `summary`, `overview`, `parent`, `agents`, `inputs`, `prompts`, `versions`, `docs`) |
| `policy/common/contracts/orchestration-policy.json` | `token_analysis`: 요청·취소 문구, 보고서 경로, 스킬 경로 |
| `policy/guards/pipeline.py` | 요청 기록(`record_prompt`)과 정리 전 확인(`token_report_denial`) |
| `policy/guards/shared_git.py` | `complete`·`cleanup`·`execute` 준비·실행 시점의 확인 연결 |

## guard 동작

요청이 있는 `orchest` 세션에서만 동작한다.

- `review --cleanup`으로 준비한 완료(병합과 정리를 한 번에)는 준비와 실행 모두 막는다. `--cleanup` 없이 병합만 완료하게 한다.
- `cleanup --source <branch> --target <직접 부모>`는 세션 산출물 폴더의 `unknown/token-usage-report.md`가 있고, 그 수정 시각이 직접 부모의 마지막 commit 시각보다 늦을 때만 준비·실행된다.
- 요청은 세션 상태에 남아 다른 입력이 와도 유지된다.

## 스크립트 검증

- Claude: admin 세션(`57834b6b…`)을 보고서와 같은 종료 시각(`2026-10-15T05:40:00Z`)으로 집계했다. 부모 9.33M, 하위 에이전트 27.98M, 합계 37.31M, 역할별 묶음, Planner F·Generator F의 수치와 재개 재기록이 보고서와 같았다.
- Codex: `~/.codex/sessions/2026/07/22`의 부모·하위 rollout을 집계했다. 입력·캐시 읽기·출력 합이 각 rollout의 마지막 `total_token_usage`와 같았다.
- OpenCode: `opencode.db`의 user-ui 세션 1건을 집계했다. assistant 메시지 합이 `session.tokens_*`와 같았다.
- 단위 테스트: `tests/test_token_usage.py`(합성 기록), `tests/test_orchestration.py`(요청·정리 전 확인, 번들 범위).

## 확인하지 못한 것

- 실제 `orchest` 세션에서 `토큰 분석`부터 정리까지의 종단 실행
- 10-08 이후 이 프로젝트의 inject Codex 세션과 inject OpenCode 세션은 기록이 없어 실제 데이터로 확인하지 못했다. Codex는 0.153 이상 형식(`token_usage_record`)을 다른 세션의 기록으로, 이전 형식을 07-22 기록으로 확인했다.
- Codex는 thread 삭제 시 rollout도 사라진다(10-07 사례). 분석은 정리 직전에 해야 한다.
