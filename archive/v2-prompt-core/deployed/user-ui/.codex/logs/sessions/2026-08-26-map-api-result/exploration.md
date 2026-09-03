# 탐색

## 불러온 스킬

- policy/coding-convention, type-definition, data-fetch-layer, abstraction-strategy, refactoring, documentation, portfolio, harness
- recipe/api-authoring, data-dto

## 재사용 자산

- `toApiResult` (`src/shared/api/common/api-result/api-result.mapper.ts`): 서버 envelope → `ApiResult`
- `unwrapApiResult` (`src/features/citizen-participation/model/apiResult.ts`): 실패 시 throw, 훅에서 data를 꺼냄
- 로컬 복제: `toCreatedProposalResult`, `toVoteResponseResult`

## 확인한 사실

- `toCreatedProposalResult`는 실패를 통과시키고 성공 시 Location을 `{ id }`로 바꾼 뒤 `{ success: true, data, error: null }`를 만든다.
- `toVoteResponseResult`는 같은 실패 통과 + 성공 data `voteResponseSchema.parse`다.
- `mapApiResult`/`mapSuccess` 이름의 기존 함수는 저장소에 없었다.
- 훅 쪽 discussion/like는 `unwrapApiResult` 후 parse라 `ApiResult` envelope를 유지하지 않는다.

## 선택

실패를 throw하지 않고 envelope를 유지해야 API 테스트의 `result.success`/`result.data` 단언이 그대로다. 그래서 `unwrapApiResult` 대신 `toApiResult`를 쓰는 `mapApiResult`를 공용으로 둔다.
