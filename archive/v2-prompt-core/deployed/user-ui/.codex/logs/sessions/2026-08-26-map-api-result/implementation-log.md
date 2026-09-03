# 구현 기록

## 승인된 범위

성공 `ApiResult` data 변환을 공용 매퍼로 모으고 제안·투표 POST가 그걸 쓴다.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `src/shared/api/common/api-result/api-result.mapper.ts` | `mapApiResult` 추가. 실패는 통과, 성공은 `toApiResult({ code: "SUCCESS", data })` | 성공 envelope 생성은 `toApiResult` 한 곳 |
| `src/shared/api/common/api-result.ts` | `mapApiResult` export | 도메인 API가 barrel로 가져옴 |
| `api/proposal/proposal.api.ts` | `toCreatedProposalResult` 제거, `mapApiResult(..., parseCreatedProposalLocation)` | Location→id 변환만 도메인에 남음 |
| `api/vote/vote.api.ts` | `toVoteResponseResult` 제거, `mapApiResult(..., voteResponseSchema.parse)` | 스키마 파싱만 도메인에 남음 |

## 결정 사항

- 신규 이름은 `mapApiResult`. 기존 `toApiResult`는 unknown envelope 변환을 유지한다.
- 토론·댓글 like mutation은 unwrap 후 parse라 이번 범위에서 바꾸지 않는다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| `npx eslint` 변경 4파일 | 성공 |
| `npx tsc -b` | 성공 |
| `npx vitest run` citizenParticipation.api.test + pages | 7 files / 33 tests passed |
| `npx vitest run` handlers.test.ts (`all` 권한) | 18 tests passed. 샌드박스에서는 MSW `Invalid URL` |
