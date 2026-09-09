# 구현 로그

## 승인된 범위

투표 mutation의 parser `.then` error 유형 인자를 제거한다. 동작은 유지한다.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `api/vote/vote.api.ts` | `toVoteResponseResult`가 `voteResponseSchema.parse` | 응답 파싱이 vote 모듈 안에 있음 |
| `hook/useCitizenParticipationMutations.ts` | `parseVoteResponse` import·`.then` 제거 | 훅이 parser 순환에 묶이지 않음 |
| `citizenParticipation.api.test.ts` | `result.data`를 직접 단언 | 이중 파싱 제거 |

## 결정 사항

- parser 단언으로 막지 않았다. 생성 POST와 같이 API가 파싱한다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| ReadLints 대상 훅·vote.api | 오류 없음 |
| `npx eslint` 변경 파일 | 성공 |
| `npx vitest run` citizen-participation | 12 files / 71 tests passed |

## Watcher 인계

현재 변경은 투표 POST 파싱 위치다. UI 시각 QA는 없다.
