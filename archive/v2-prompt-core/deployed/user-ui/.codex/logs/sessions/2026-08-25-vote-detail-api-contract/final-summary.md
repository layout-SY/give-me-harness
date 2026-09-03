# 최종 요약

## 제공 사항

- 투표 상세 전용 응답 DTO와 `parseVoteDetail`
- `useVoteDetailQuery`와 `VoteDetailRoute`가 새 상세 DTO를 직접 사용
- `myChoice` null을 미투표로 처리. 재투표 MSW 409 `ALREADY_VOTED`
- 임시저장 id 404. 시작 전·중단은 상세에서만 조회
- 찬반 수는 `CLOSED`만 값. 댓글은 기존 분리 요청 유지
- 목록 필터는 `VOTE_LIST_STATUS`(`IN_PROGRESS`/`CLOSED`)만

## 제외 사항

- `VoteDetailPage` 마크업
- 댓글 URL 변경
- 투표 목록에 시작 전·중단 포함
- 투표 POST 응답 재설계

## 검증

| 명령어 | 결과 |
| --- | --- |
| `npx vitest run src/features/citizen-participation src/pages/citizen-participation` | 12 files / 66 passed |
| `npm run lint && npm run build` | 성공 |

## 산출물

`.codex/logs/sessions/2026-08-25-vote-detail-api-contract/`의 plan, exploration, implementation-log, grill-me-review, review-log, evaluation-log, final-summary, portfolio-log

## 남은 제한 사항

- 시작 전·중단은 UI `closed` + `period` 안내로만 구분된다.
- 댓글 경로는 기존 시민참여 prefix를 유지한다.
- 작성자 필드는 상세 API에 없어 빈 문자열이다.

## 다음 단계

예정/중단 전용 상세 UI와 comments URL이 확정되면 같은 방식으로 맞춘다.
