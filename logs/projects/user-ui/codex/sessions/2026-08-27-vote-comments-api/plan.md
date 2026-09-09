# 계획

## 목표

`GET /citizen/votes/{voteId}/comments`의 요청·응답 계약을 시민참여 도메인에 반영하고 기존 댓글 UI 소비 계약을 유지한다.

## 범위

- vote 댓글 query·response DTO와 Zod 스키마
- Axios API 직렬화와 TanStack Query 연결
- 공용 댓글 모델 정규화와 query key
- MSW fixture·handler와 API·parser 회귀 테스트
- 공개 feature export

## 제외 사항

- production UI 마크업·스타일 변경
- backend 구현
- 기존 meeting API 보안 테스트 실패 수정
- commit, merge, push

## 제약 조건

- 작성자는 `authorName`만 사용한다.
- 정렬 속성은 `createdAt`, `id`만 허용하고 기본값은 `createdAt,desc`다.
- 투표 상태와 무관하게 조회하며 mock의 임시저장 투표 `99`만 404로 처리한다.
- `AGENTS.md`, `package.json`의 선행 변경을 수정하거나 되돌리지 않는다.
- 현재 브랜치는 `sy-main`이며 작업 시작 전 별도 브랜치가 생성되지 않은 운영 편차가 있다. dirty worktree에서 checkout·stash·commit은 수행하지 않는다.

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 탐색·계획 | Hephaestus | `skill-index`, `reference-index`, `recipe-api-authoring` | 기존 댓글 흐름과 재사용 경계 확인 |
| 구현 | Hephaestus | `programming`, `policy-coding-convention`, `policy-type-definition`, `policy-data-fetch-layer` | typed API와 정규화 경계 구현 |
| 검토 | Watcher | `policy-review-checklist` | 현재 변경 PASS/FAIL 판정 |
| 평가 | Evaluator | `policy-documentation`, `policy-portfolio` | 비차단 장기 개선 사항 기록 |

## 검증

- 신규 테스트를 먼저 실패시킨 뒤 구현한다.
- 대상 Vitest, `npm run build`, `npm run lint`, `npm test`를 실행한다.
- Axios와 MSW를 통한 실제 API client 표면에서 endpoint, query, 응답 정규화를 확인한다.

## 위험 요소 및 결정 사항

- 신규 응답에는 좋아요 필드가 없으므로 공용 모델에서는 선택형으로 표현하고 vote UI에서는 좋아요 제어를 렌더링하지 않는다.
- 숫자 댓글 ID는 parser에서 branded string ID로 정규화해 기존 신고·렌더링 계약을 유지한다.
- 원본 응답 DTO와 화면용 페이지 모델을 분리한다.

## 승인

- 상태: implementation continued by explicit continuation directive
- 구현 계획은 사용자에게 보고되었고 후속 continuation 지시로 실행했다.

## 추가 작업 — nullable 제안 작성자 목록 복구

### 목표

실제 제안 목록 응답의 `author: null` 항목 때문에 전체 목록 파싱이 실패하고 화면이 빈 결과로 보이는 문제를 수정한다.

### 범위

- `proposalListItemSchema`와 `GetProposalListItemDto`의 nullable 작성자 계약
- `toProposalListItem`의 null-safe 작성자 매핑
- parser·presentation 회귀 테스트
- 기존 8종 세션 문서 갱신

### 분기 계약

- 브랜치: `task/fix-proposal-list-null-author`
- 분기 기준·직접 merge 대상: `sy-main`
- 승인 시점 부모 HEAD: `586908c0e941da8f423cd3689884e25e64416fce`
- 원 dirty worktree를 보존하기 위해 승인된 예외 방식으로 linked worktree를 생성했다.

### 승인

- 사용자가 구현 진행과 linked worktree 예외 분기를 각각 명시적으로 승인했다.
