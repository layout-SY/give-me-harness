# 계획

## 목표

- 관리자 시민투표 목록·상세를 `GET /citizen/votes`, `GET /citizen/votes/{voteId}` 실제 계약에 연결한다.
- 외부 응답을 Zod 경계에서 파싱하고 page/size/sort, 실제 5개 상태, 집계 필드를 손실 없이 화면 상태까지 전달한다.

## 범위

- `src/entities/cp-vote`: 실제 query·응답 DTO, parser, API client, 조회 query hook, read model.
- `src/pages/cp-vote`: 실제 조회 모델을 소비하는 hook·controller·표시 설정. production UI는 Claude Code 소유권 계약에 따라 별도 인계 후 연결한다.
- `src/mocks/cp-vote.handlers.ts`: 실제 공개 endpoint, pagination, sort, 성공·400·404 envelope.
- `tests/citizen-votes-contract.test.mjs`, `tests/citizen-votes-msw.test.mjs`: Node 기반 contract·wire 검증.
- `.codex/logs/sessions/2026-09-02-citizen-votes-api`: 필수 작업 산출물.

## 제외 사항

- 명세가 없는 투표 상태·종료일·공개 기준 mutation 구현 또는 legacy mutation 추정.
- 실제 조회 API가 지원하지 않는 status/author/title/date 검색 조건 전송.
- 실제 응답에 없는 작성자·댓글·처리 이력·공개 정책 데이터를 parser에서 임의 생성.
- 브라우저 실행, 이미지 캡처, 시각 QA, 실제 인증 backend 호출.

## 제약 조건

- 브랜치 계약: `task/connect-citizen-votes-api`, parent/merge target `sy-main`, parent HEAD `e26b263afe2478cbabd3e34fdc82306e0715d059`.
- Hephaestus는 API·DTO·parser·hook·controller·test를 소유하고 `src/pages/cp-vote/ui/**`는 수정하지 않는다.
- UI에 새 controller 계약을 연결하기 전 사용자에게 `Claude Code의 UI 작업이 완료되었나요?`라고 확인한다.
- QA는 테스트 코드와 정적 검증으로만 수행한다.

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 계약 탐색·계획 | Hephaestus | `skill-index`, `policy-git-branch-strategy`, `policy-harness`, `reference-components`, `reference-custom-hooks` | 실제 계약과 파일 소유권이 확정된다. |
| DTO·API·parser | Hephaestus | `programming`, `policy-type-definition`, `policy-data-fetch-layer`, `recipe-api-authoring`, `recipe-data-dto` | 외부 응답이 Zod를 거쳐 typed read model로 변환된다. |
| query·controller | Hephaestus | `policy-tanstack-query`, `recipe-data-fetch`, `policy-coding-convention` | AbortSignal과 query key가 실제 요청 의존값을 반영한다. |
| production UI | Claude Code | `project-ui`, `reference-components` | unsupported filter와 legacy 처리 UI가 실제 조회 모델에 맞게 정리된다. |
| 검증·문서화 | Watcher·Evaluator·Hephaestus | `policy-review-checklist`, `policy-documentation`, `policy-portfolio` | PASS/FAIL 판정, 장기 권고, 8종 산출물이 남는다. |

## 검증

- RED/GREEN: `node --test tests/citizen-votes-contract.test.mjs`, `node --test tests/citizen-votes-msw.test.mjs`.
- 회귀: `node --test tests/*.test.mjs`.
- 정적 검증: 변경 파일 ESLint, `npm run build`, `npm run lint`, `git diff --check`.
- 사용자 표면: MSW server를 통한 정상 목록·빈 목록·정렬 오류·상세·404 HTTP 요청을 Node 테스트로 직접 실행한다.

## 위험 요소 및 결정 사항

- 실제 목록 응답에는 상태별 count가 없으므로 현재 페이지 항목으로 전체 KPI를 계산하지 않는다.
- 실제 query에는 검색 조건이 없으므로 기존 검색 UI를 무동작 상태로 유지하지 않고 Claude Code UI 범위에서 제거 또는 조회 전용 구조로 바꾼다.
- 실제 상세 응답에는 작성자·댓글·처리 이력·공개 정책이 없으므로 placeholder를 도메인 데이터처럼 만들지 않는다.
- mutation 명세가 없으므로 legacy `/v1/cp/votes/{voteId}/process`는 실제 조회 화면에서 노출하지 않는 방향으로 UI 계약을 분리한다.

## 승인

- 상태: approved
- 구현 승인: 사용자의 `일단 목록/상세 연결만 해. 그리고 다른 부분들은 실제 조회를 기준으로 작업하면 돼`.
- 브랜치 승인: 사용자의 `승인`.
- 승인 요청 식별자: `branch:task/connect-citizen-votes-api|parent:sy-main@e26b263afe2478cbabd3e34fdc82306e0715d059|merge:sy-main`.
