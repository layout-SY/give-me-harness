# 최종 요약

## 제공 사항

`useVoteMutation`이 parser를 `.then`하지 않는다. `postVote`가 `voteResponseSchema`로 응답을 파싱한 뒤 `{ id, completed, choice }`를 돌려준다.

## 제외 사항

- 투표 JSON 계약 변경, `VoteDetailPage`, parser 함수 삭제

## 검증

| 명령어 | 결과 |
| --- | --- |
| ReadLints 훅·vote.api | 오류 없음 |
| `npx eslint` 변경 파일 | 성공 |
| `npx vitest run` citizen-participation | 12 files / 71 tests passed |

## 산출물

`.codex/logs/sessions/2026-08-25-fix-vote-mutation-parser-types/`

## 남은 제한 사항

훅이 다시 `citizenParticipation.parser`를 `.then`하면 같은 오류가 난다.

## 다음 단계

mutation 파싱은 feature API/DTO에 둔다.
