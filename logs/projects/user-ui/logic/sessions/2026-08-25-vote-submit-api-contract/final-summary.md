# 최종 요약

## 제공 사항

- 투표 POST 요청 `{ choice }`만 전송
- `VOTE_CONFLICT_CODE`와 MSW 409 분기 (`ALREADY_VOTED`·`VOTE_NOT_STARTED`·`VOTE_CLOSED`·`VOTE_CANCELLED`)
- 문자열 오류 `code` 보존
- `parseVoteResponse`와 훅 연결
- 진행 중 1회 성공, 재투표 거절

## 제외 사항

- 200 응답 재설계
- POST URL 변경
- `VoteDetailPage` 409 안내 UI

## 검증

| 명령어 | 결과 |
| --- | --- |
| `npx vitest run src/features/citizen-participation src/pages/citizen-participation` | 12 files / 69 passed |
| `npm run lint && npm run build` | 성공 |

## 산출물

`.codex/logs/sessions/2026-08-25-vote-submit-api-contract/`

## 남은 제한 사항

- 성공 `data`는 기존 `{ id: string, completed, choice }`다.
- 409 코드는 클라이언트 타입·MSW에 있고 화면 문구는 없다.
- 라우트는 `IN_PROGRESS`가 아니면 POST하지 않는다.

## 다음 단계

성공 응답 JSON과 409 화면 안내가 확정되면 같은 방식으로 맞춘다.
