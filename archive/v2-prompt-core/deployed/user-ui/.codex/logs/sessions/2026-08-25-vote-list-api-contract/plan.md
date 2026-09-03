# 계획

## 목표

확정된 투표 목록 API(`GET /v1/api/citizen-participation/votes`)를 전용 요청/응답 DTO·parser·훅·MSW·목록 사용처에 반영한다. 투표 status는 `IN_PROGRESS`/`CLOSED`만 쓰고, 토론·설문·정책의 `PARTICIPATION_STATUS`는 유지한다.

## 범위

- `VOTE_STATUS`와 `GetVoteListQueryDto` / `GetVoteListResponseDto` / `parseVoteList`
- `voteApi.getVoteList`가 `page`/`size`를 항상 보내고 `status`/`sort`는 값이 있을 때만 반복 키로 전송
- `useVoteListQuery`와 `VoteListRoute`가 목록 DTO를 직접 사용
- `IN_PROGRESS` → UI `ongoing`, `CLOSED` → `closed` 매핑. 진행 중 찬반 비율 숨김
- MSW vote list SUCCESS envelope, 숫자 id fixture, 상세 status 분기

## 제외 사항

- `VoteListPage` 마크업 변경, status/sort 필터 UI 추가
- 투표 내 활동 응답을 목록 DTO로 재설계 (`useMyActivityQuery` + 기존 content list 유지)
- 투표 상세 envelope를 목록 형태(`startsAt`/`endsAt`)로 재설계
- 토론·설문·정책 목록 계약 변경
- `UPCOMING`/`CANCELLED` 상태값 도입

## 제약 조건

- 명시 승인 후 구현. 사용자 지시: `작업 진행`
- 클라이언트는 유효하지 않은 status를 보내지 않는다. 생략은 양쪽 OR, 둘 다 보내면 OR
- `page`/`size` 외 query는 optional/`undefined`이며 미설정 시 params에서 생략
- Claude Code 소유 `VoteListPage`는 읽기 전용. 사용처 연결은 `CitizenListRoutes.tsx`만 최소 수정

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| DTO/parser | Hephaestus | recipe-api-authoring, recipe-data-dto, type-definition | 확정 JSON과 같은 목록 계약 |
| API/훅 | Hephaestus | data-fetch-layer, hook-extraction | 반복 query 키와 전용 list 훅 |
| 매퍼/상세 | Hephaestus | coding-convention | UI 상태·제출 가드가 새 status를 사용 |
| MSW/테스트 | Hephaestus | recipe-api-authoring | Axios 경로로 계약 검증 |
| 문서 | Hephaestus | documentation, portfolio | 세션 산출물 8종 |

## 검증

`npx vitest run src/features/citizen-participation src/pages/citizen-participation`, `npm run lint`, `npm run build`

## 위험 요소 및 결정 사항

- Axios 기본 배열 직렬화(`status[]`)는 `URLSearchParams.getAll("status")`와 맞지 않으므로 `URLSearchParams.append`를 사용한다.
- 첫 화면은 `page`+`size`만 보낸다. `PAGE_SIZE`는 라우트 상태 10이며 OpenAPI 기본 20과 다를 수 있다.
- 투표 내 활동은 옛 activity DTO를 유지한다.

## 승인

- 상태: approved
- 승인 문구: `작업 진행`
