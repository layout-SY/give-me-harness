# 계획

## 결론
- 승인된 `cp-admin-api-remediation` Todo 4~6 중 Comment tranche만 수행하고, Todo 6에서 Todo 4 구현 및 Todo 5 독립 검증의 사실을 문서로 폐쇄한다.
- Vote(Todo 7 이후)는 시작하지 않는다.

## 요청 요약
- Comment 목록/처리 수직 slice의 구현 결과, 검증 이력, 잔여 위험을 동일 slug의 필수 문서 6개와 portfolio 1개에 기록한다.
- Watcher attempt 1·2의 `needs-fix`는 제품 동작 실패가 아니라 root QA 산출물 정리 실패로, attempt 3의 최종 결과는 `confirmed`로 기록한다.

## 작업 유형
- hybrid 구현 tranche의 documentation closure

## 범위
- 제품 결과: typed DTO, Zod parser, `ApiClient<unknown>`, list query, process mutation, stateful MSW, 응답 기반 KPI 5개, 필터, POST/cache 흐름, 400/404/500 처리.
- 품질 결과: 변경 TS/TSX 15개 모두 pure LOC 250 이하, scoped ESLint·TypeScript build·Vite build 통과, LSP unavailable.
- 문서 경로: `.codex/logs/sessions/2026-08-20-cp-t01-comment-api/`, 동일 slug portfolio, T01 closure evidence.

## 제외 범위
- 제품 코드, 원계획, Boulder/todos/ledger, Git 상태의 변경.
- Vote tranche 시작 또는 장기 Evaluator 판정.
- 백엔드 미확정 계약을 확정 사실로 표현하거나 측정하지 않은 효과를 주장하는 일.

## 섹션
1. Generator 근거 정리 — Todo 4 제품 결과와 브라우저 발견 결함을 기록.
2. Watcher 근거 정리 — Todo 5의 세 차례 독립 판정과 cleanup을 기록.
3. Closure — 필수 문서·portfolio·receipt·DoneClaim 및 링크/범위 검사.

## 필요 에이전트
- Generator: Todo 4 제품 구현 및 근거 소유자.
- Watcher: Todo 5 독립 검증 및 최종 `confirmed` 소유자.
- Closure fallback: Todo 6 문서·portfolio·receipt 작성만 담당.

## 필요 스킬
- `policy-documentation`: 결론 중심 필수 산출물과 근거 링크.
- `policy-portfolio`: 문제·선택지·실제 before/after·검증·잔여 위험만 기록.
- `policy-harness`, `policy-review-checklist`: 최종 `confirmed` 전에는 완료로 쓰지 않고 재시도 원인을 제품과 분리.

## 리스크 / 가정
- GET/POST DTO와 KPI/count 의미는 MSW 기반 provisional contract이며 실제 백엔드 계약 확인이 남아 있다.
- build 성공과 별개로 기존 bundle `>500 kB` warning이 남아 있다.
- TypeScript LSP는 미설치이고 기존 사용자 거절 상태여서 diagnostics를 확보하지 못했다.

## 근거
- [원계획 Todo 4~6](../../../../.omo/plans/cp-admin-api-remediation.md)
- [Generator 계약 및 파일](../../../../.omo/evidence/cp-admin-api-remediation/t01/generator/contracts-and-files.md)
- [Watcher attempt 3 verdict](../../../../.omo/evidence/cp-admin-api-remediation/t01/watcher/attempt-3/verdict.json)

## 승인 상태
- Todo 4 구현과 Todo 5 Watcher attempt 3는 선행 오케스트레이터에서 확인되었고, 본 작업은 요청받은 Todo 6 fallback closure만 수행한다.
