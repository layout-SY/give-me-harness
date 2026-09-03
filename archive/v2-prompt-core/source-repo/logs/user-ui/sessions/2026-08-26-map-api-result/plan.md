# 계획

## 목표

`toCreatedProposalResult`처럼 성공 `ApiResult`의 data만 변환하는 로직을 공용 매퍼 한 곳으로 모으고, 같은 패턴의 도메인 API가 그걸 쓰게 한다.

## 범위

- `src/shared/api/common/api-result/api-result.mapper.ts`에 `mapApiResult` 추가
- `src/shared/api/common/api-result.ts`에서 export
- `proposal.api.ts`의 `toCreatedProposalResult` 제거 후 `mapApiResult` 사용
- `vote.api.ts`의 `toVoteResponseResult` 제거 후 `mapApiResult` 사용

## 제외 사항

- Location path 파서(`parseCreatedProposalLocation`) 자체는 제안 계약으로 유지
- 훅의 `unwrapApiResult` 패턴 변경
- 토론·댓글 like처럼 이미 unwrap 후 schema.parse 하는 mutation

## 제약 조건

- 사용자 지시: `toCreatedProposalResult` 역할을 전역 코드로 가져다 쓰는 패턴으로 전체 수정
- 실패 `ApiResult`는 그대로 통과시키고, 성공 data만 변환

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 공용 매퍼 | Hephaestus | type-definition, abstraction-strategy, recipe-api-authoring | `mapApiResult`가 성공 data만 변환 |
| API 교체 | Hephaestus | data-fetch-layer, refactoring | 제안·투표 POST가 공용 매퍼 사용 |
| 검증 | Hephaestus | documentation | eslint·vitest·tsc 통과 |
| 문서 | Hephaestus | documentation, portfolio | 세션 산출물 8종 |

## 검증

대상 파일 eslint, 시민참여 API·페이지·MSW 테스트, `tsc -b`

## 위험 요소 및 결정 사항

- 저장소에 동일 이름 헬퍼는 없었다. 성공 envelope 생성은 `toApiResult`가 이미 담당하므로 `mapApiResult`가 그걸 호출한다.
- 사용처가 제안·투표 두 곳이라 공용 추출 근거가 있다.

## 승인

- 상태: approved
- 승인 문구: `그거 가져다 쓰는 패턴으로 전체 수정해`
