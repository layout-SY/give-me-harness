# 포트폴리오 경험 기록 — Codex 프롬프트 경량화

## 작업 개요

실제 FSD 구조와 다른 재사용 탐색 경로, 반복되는 browser QA, 실행 불가능한 Watcher 호출 규칙을 현재 환경에 맞게 정렬한 AI 하네스 개선 작업이다.

## 문제 상황

- **문제 출처:** 사용자 피드백과 실행시간 audit
- **대상 도메인·서비스:** admin Codex agent/workflow/harness/skill/OMO plan
- **기존 문제:** 존재하지 않는 `src/components`·`src/hooks` 탐색이 runtime marker와 문서에 남아 있었고, non-UI API 검증도 fresh browser 준비를 반복했다. Claude Code API가 없는데도 Watcher가 정상 단계처럼 dispatch됐다.

## 요구사항 및 의사결정

- **사용자 요구:** 재사용 탐색 경로를 전부 정리하고 fresh browser QA를 없애며, 도메인 순서를 Planner→Generator→Watcher→Closure로 유지하되 현재 Watcher는 실행하지 않는다.
- **선택:** browser 검증을 없애되 API/parser/state 검증은 Node driver로 유지하고, Watcher 비가용을 반려가 아닌 pause 상태로 모델링했다.

| 접근법 | 장점 | 단점 | 선택 여부와 이유 |
|---|---|---|---|
| browser QA를 전부 삭제하고 대체 검증도 제거 | 가장 빠름 | API/parser/state 회귀를 놓침 | 미채택 — 품질 경계가 사라짐 |
| Node API/module·HTTP driver로 대체 | browser 비용 제거, 서버 계약 검증 유지 | UI 동작은 확인하지 않음 | 채택 — UI는 Claude 소유이며 non-UI 검증에 적합 |
| Watcher 없이 Closure 진행 | 즉시 종료 가능 | 독립 품질 게이트를 우회 | 미채택 — 사용자 요청의 순서를 위반 |
| Watcher 비가용 상태에서 pause | 산출물 보존, 거짓 pass 방지 | API 복구 전 완료 불가 | 채택 — 외부 의존성과 품질 실패를 분리 |

## 사용 기술과 구체적 목적

| 기술/패턴/아키텍처 | 해결하려는 문제 | 적용 위치와 목적 | 미채택 대안/이유 |
|---|---|---|---|
| Python Codex hook | 실제 탐색 marker 불일치 | `track-posttooluse.py`에서 새 source root 인식 | 문서만 수정 — runtime 차단이 계속됨 |
| 상태 전이 모델 | API 비가용과 반려 혼동 | `watcher_unavailable`, `paused_after_generator` | retry 사용 — 외부 장애가 반려 횟수를 소모 |
| Node API/module driver | browser 준비 비용 | OMO API 검증 계약 | Playwright — non-UI 검증에 불필요 |

## 적용 내용

- 운영 prompt와 reference/recipe의 탐색 경로를 실제 source 구조로 교체했다.
- browser QA 요구를 비브라우저 API contract 검증으로 전환했다.
- Watcher 비가용 시 dispatch·retry·Closure를 차단하는 규칙을 agent/workflow/harness/plan에 반영했다.
- hook marker 회귀 테스트를 추가했다.

## 결과 및 성과

- governing prompt 범위의 stale 탐색 경로 검색 결과: 0건
- positive browser QA mandate 검색 결과: 0건
- 실제 source mapping 검사: 33개 경로 모두 존재
- hook regression, Python syntax, TOML parse, whitespace 검사: 모두 통과
- Watcher는 사용자 지시대로 실행하지 않았고 Closure confirmed를 주장하지 않았다.

## 회고

- 프롬프트 문구와 executable hook을 함께 바꾸지 않으면 문서상 수정이 실제 차단 해소로 이어지지 않는다.
- 외부 검토 서비스 부재는 품질 실패가 아니므로 retry와 분리된 상태가 필요하다.
- 브라우저 QA를 제거할 때도 해당 표면이 보장하던 API·parser·state observable은 더 저렴한 driver로 보존해야 한다.
