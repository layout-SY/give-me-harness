# 최종 요약

## 제공 사항

- 투표 목록 전용 요청/응답 DTO와 `parseVoteList`
- `getVoteList`는 `page`/`size`를 항상 보내고 `status`/`sort`는 있을 때만 반복 키로 전송
- `VOTE_STATUS` `IN_PROGRESS`/`CLOSED`. 토론·설문·정책 status는 유지
- `useVoteListQuery`와 `VoteListRoute`가 새 목록 DTO를 직접 사용
- 진행 중 찬반 수는 `null`로 두고 비율을 숨김. 종료 시에만 비율 표시
- MSW vote list SUCCESS envelope와 숫자 id fixture

## 제외 사항

- `VoteListPage` 마크업, status/sort 필터 UI
- 투표 내 활동 응답 재설계
- 투표 상세 envelope 재설계
- 토론·설문·정책 목록 계약
- `UPCOMING`/`CANCELLED`

## 검증

| 명령어 | 결과 |
| --- | --- |
| `npx vitest run src/features/citizen-participation src/pages/citizen-participation` | 12 files / 61 passed |
| `npm run lint && npm run build` | 성공 |

## 산출물

`.codex/logs/sessions/2026-08-25-vote-list-api-contract/`의 plan, exploration, implementation-log, grill-me-review, review-log, evaluation-log, final-summary, portfolio-log

## 남은 제한 사항

- 투표 내 활동은 기존 content list DTO다.
- 투표 상세는 `ContentDetailDto`이며 목록의 `startsAt`/`endsAt`과 다르다.
- 클라이언트 목록 size는 10이다.
- MSW 목록 기간 필드는 상세 `createdAt`을 복사한다.

## 다음 단계

투표 내 활동 응답과 상세 envelope가 확정되면 같은 방식으로 DTO를 맞춘다. status/sort 필터 UI가 필요하면 이미 있는 query DTO에 연결한다.
