# 탐색

## 불러온 스킬

- policy/coding-convention, type-definition, data-fetch-layer, abstraction-strategy, refactoring, documentation, portfolio, harness, review-checklist
- recipe/api-authoring, data-dto

## 재사용 자산

- 투표 상세: `GetVoteDetailResponseDto` + `useVoteDetailQuery` + `parseVoteDetail`
- 제안 목록: `proposalAuthorSchema`, SUCCESS envelope
- 생성 Location: 이미 `/citizen/proposals/{id}`

## 확인한 사실

- 기존 제안 상세는 `ContentDetailDto`(string id, body/detail/effect/reference, authorName)
- 확정 예시는 number id, background/content/expectedEffect/referenceCase, author 객체 또는 null, updatedAt
- RESOURCE는 `/v1/api/citizen-participation/...` 이었다

## 선택

투표 상세와 같이 전용 DTO·훅을 두고, 화면용 `ProposalDetail`은 presentation에서만 번역한다. path는 시민참여 전송 모듈 전체를 `/citizen`으로 통일한다.
