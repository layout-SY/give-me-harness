# 계획

## 목표

- CP 도메인의 입력 날짜 검증, unknown key 거부, board bulk-hide 응답 파싱 위치를 기존 계층 규칙에 맞춘다.
- 응답 호환성, React Query cache 동작, UI 파일을 변경하지 않은 채 독립 검증과 문서화를 완료한다.

## 범위

- `src/shared/lib/validation/index.ts`
- discussion, vote, comment, proposal, board, report의 승인된 API DTO 경로
- `src/entities/cp-board/api/`와 `src/entities/cp-board/hook/use-cp-board-bulk-hide-mutation.ts`
- `tests/*.test.mjs` 4개와 이 세션의 8종 문서

## 제외 사항

- `src/**/ui/**`, CSS, assets, `src/shared/ui/**`
- 응답 DTO 계약, cache key 및 cache update/invalidation 동작
- `package.json`, lockfile, ESLint 설정과 기존 lint 오류
- 계획의 UI Todo 5~7

## 제약 조건

- 브랜치 계약: `task/domain-pattern-alignment-logic` → `sy-main@3f5b4d4b31992d421a02bc44b97276e6863ee05e`.
- 현재 logic 작업은 GPT-5.6 Sol 기반 Hephaestus가 수행하며 Claude Code를 사용하지 않는다. UI Todo 5~7은 별도 브랜치 승인 전 보류한다.
- commit, merge, 사후 검증, 로컬 브랜치 삭제는 별도 승인 전 수행하지 않는다.
- 전체 `npm run lint`의 범위 밖 기존 오류와 `npm run test` script 부재는 사용자 승인에 따라 baseline 위험으로 분리한다.

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 탐색·계획 | Hephaestus | `skill-index`, `policy-index`, `reference-index`, `recipe-index` | 최소 변경 범위와 불변 계약 확정 |
| 날짜 입력 | Generator | `policy-validation`, `policy-type-definition`, `policy-coding-convention` | 실제 달력 날짜 검증 |
| strict 입력 | Generator | `recipe-data-dto`, `policy-validation`, `policy-type-definition` | 여섯 입력 schema의 unknown key 거부 |
| API parser | Generator | `recipe-api-authoring`, `policy-data-fetch-layer`, `policy-tanstack-query` | parser 책임을 API 경계로 이동 |
| 독립 판정 | Watcher | `policy-review-checklist`, `policy-harness` | baseline-aware gate PASS/FAIL |
| 장기 평가 | Evaluator | `policy-documentation`, `policy-abstraction-strategy` | 현 결함과 장기 제안 분리 |

## 검증

- Vite `ssrLoadModule` 기반 `node --test` 4개 파일, 총 13개 테스트.
- `npm run build`.
- 변경 TypeScript 10개 대상 ESLint.
- `GIT_MASTER=1 git diff --check`와 최신 diff 범위 확인.
- 전체 `npm run lint`와 `npm run test` 결과는 baseline 한계로 별도 기록.

## 위험 요소 및 결정 사항

- 단순 regex 날짜는 `2026-02-31`을 허용하므로 Zod의 실제 ISO 날짜 검증을 공용 schema로 사용했다.
- `.strict()`는 입력 schema에만 적용해 comment/proposal 응답의 extra-key 호환성을 유지했다.
- hook 내부 local parser를 제거하되 API 호출 → unwrap → parser → cache callback 순서는 유지했다.
- 최초 Watcher FAIL은 branch 결함이 아니라 실행 불가능한 계획 gate였으며, 사용자가 baseline-aware 기준을 승인했다.

## 승인

- 구현 승인: 완료
- 브랜치 생성 승인: 완료
- baseline-aware 검증 기준 승인: 완료
- Watcher 판정: PASS
- commit·merge 승인: 완료
- 실행 상태: 5개 atomic commit을 `sy-main@5aa158a42669aef832f0031790ba964a164c88ff`에 ff-only merge하고 사후 필수 gate를 모두 통과한 뒤 source branch와 두 linked worktree를 안전 제거했다.
- 다음 승인: logic 작업은 완료됐으며 UI Todo 5~7은 별도 GPT Sol 브랜치 계약 전까지 시작하지 않는다.
