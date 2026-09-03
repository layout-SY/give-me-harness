# 구현 로그

## 승인된 범위

투표 POST 요청을 `{ choice }`로 고정하고, 진행 중이 아니거나 이미 투표한 경우 409 코드를 구분한다. 성공 응답 JSON은 바꾸지 않는다.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `src/features/citizen-participation/model/constants.ts` | `VOTE_CONFLICT_CODE` 추가 | 409 코드가 도메인 상수 |
| `src/features/citizen-participation/api/vote/vote.dto.ts` | request/response handwritten DTO | `z.infer` 순환을 피함 |
| `src/features/citizen-participation/api/vote/vote.api.ts` | `{ choice: request.choice }`만 전송 | 요청 body가 확정 필드만 |
| `src/features/citizen-participation/api/http/citizenParticipation.parser.ts` | `parseVoteResponse` | submit 응답을 좁힘 |
| `src/features/citizen-participation/hook/useCitizenParticipationMutations.ts` | parseVoteResponse 사용 | 훅이 전용 parser를 탐 |
| `src/shared/api/common/api-result/types.ts` / `server-response.ts` / `custom.exception.ts` | `code`를 `number \| string`으로 보존 | 문자열 409가 0으로 떨어지지 않음 |
| `src/features/citizen-participation/mocks/handlers.ts` | status·재투표별 409, SUCCESS envelope | 로컬이 확정 오류 계약을 재현 |

## 결정 사항

- 200 `data`는 `{ id, completed, choice }`를 유지했다.
- `VoteDetailPage`에 409 문구를 넣지 않았다. 라우트는 `IN_PROGRESS`만 POST한다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| `npx vitest run src/features/citizen-participation src/pages/citizen-participation` | 12 files / 69 passed |
| `npm run lint && npm run build` | exit 0 |

구현 중 수정한 실패: handlers.test에서 `error.response.data.code`가 `any`라 eslint 4건 → `isRecord`로 좁힘.

## Watcher 인계

POST 계약과 409 구분이다. UI 시각 QA는 하지 않았다.
