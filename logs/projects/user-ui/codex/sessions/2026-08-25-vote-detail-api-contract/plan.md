# 계획

## 목표

확정된 투표 상세 API(`GET /v1/api/citizen-participation/votes/{voteId}`)를 전용 응답 DTO·parser·훅·MSW·상세 사용처에 반영한다. 인증 없이 조회하고, 임시저장은 404이며, 목록에 없는 시작 전·중단 투표도 상세에서 파싱한다.

## 범위

- `GetVoteDetailResponseDto` / `parseVoteDetail` / `getVoteDetail` 반환 타입
- `VOTE_STATUS`에 상세용 `UPCOMING`/`CANCELLED` 추가, 목록 필터는 `VOTE_LIST_STATUS`만
- `useVoteDetailQuery`와 `VoteDetailRoute`가 상세 DTO를 직접 사용
- `myChoice: VoteChoice | null`. 미투표·무토큰은 `null`이며 재투표는 409 `ALREADY_VOTED`
- `agreeCount`/`disagreeCount`는 `CLOSED`만 값, 그 외 `null`
- 의견 목록은 기존 comments 요청 유지

## 제외 사항

- `VoteDetailPage` 마크업·뱃지 상태값 확장
- 댓글 URL을 OpenAPI 표기 `/citizen/votes/{voteId}/comments`로 변경
- 투표 목록 요청에 `UPCOMING`/`CANCELLED` 전송
- 투표 POST 응답 DTO 재설계
- 토론·제안 상세 계약 변경

## 제약 조건

- 명시 승인 후 구현. 사용자 지시: `작업 진행`
- 임시저장(DRAFT)은 성공 스키마에 넣지 않는다
- Claude Code 소유 `VoteDetailPage`는 읽기 전용. 사용처 연결은 `CitizenParticipationDetailRoutes.tsx`만 최소 수정

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| DTO/parser | Hephaestus | recipe-api-authoring, recipe-data-dto, type-definition | 확정 JSON과 같은 상세 계약 |
| API/훅 | Hephaestus | data-fetch-layer, hook-extraction | 전용 detail 훅과 공용 content detail 분리 |
| 매퍼/라우트 | Hephaestus | coding-convention | myChoice null과 기간 안내 매핑 |
| MSW/테스트 | Hephaestus | recipe-api-authoring | SUCCESS/404/409와 Axios 경로 검증 |
| 문서 | Hephaestus | documentation, portfolio | 세션 산출물 8종 |

## 검증

`npx vitest run src/features/citizen-participation src/pages/citizen-participation`, `npm run lint`, `npm run build`

## 위험 요소 및 결정 사항

- `myChoice: null`을 `undefined`로 취급하면 미투표를 이미 투표한 것으로 본다.
- 시작 전·중단 투표를 목록 fixture에 넣으면 내 활동 건수가 늘어난다. 상세 전용 fixture로 분리한다.
- 기존 `VoteDetail` UI는 `ongoing`/`closed`만 있으므로 시작 전·중단은 투표 불가로 매핑하고 이유를 `period`에 넣는다.

## 승인

- 상태: approved
- 승인 문구: `작업 진행`
