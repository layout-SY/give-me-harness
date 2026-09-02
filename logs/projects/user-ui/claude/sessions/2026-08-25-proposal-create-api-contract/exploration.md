# 탐색

## 요청

사용자는 제안하기 버튼의 POST 요청 body와 성공 계약을 기존 API에 반영하라고 했다. 성공은 201과 `Location: /citizen/proposals/{id}`이며, `referenceCase`만 선택 입력이고 생략하면 `null`로 저장된다.

## 대상 관련 사실

- 기존 `createProposalRequestSchema`는 `title`/`body`/`detail`/`effect`/`reference?`였다.
- `postProposal`은 요청 객체 전체를 보내고 `MutationResponseDto` `{ id: string, completed }`를 기대했다.
- 폼은 `title`/`background`/`detail`/`effect`/`reference`이며 `toCreateProposalRequest`가 `background`→`body`, 빈 `reference`는 키 생략으로 매핑했다.
- `ProposalWriteRoute`는 `onSuccess: ({ id }) => navigation.goToDetail("proposal", id)`로 상세로 이동한다. `goToDetail`은 `string` id를 받는다.
- 프로덕션 Axios interceptor는 `response.data`만 반환해 Location 헤더를 버린다. `toApiResult`는 `code === "SUCCESS"` 또는 `success === true`가 있어야 한다.
- MSW POST는 `mutationResponse`로 옛 envelope를 돌려줬고, 상세 저장은 `ContentDetailDto`의 `body`/`detail`/`effect`/`reference`를 쓴다.
- `ProposalWritePage`는 Claude Code 소유 UI다. 필드 id는 `proposal-detail` 등이다.

## 불러온 스킬

- `.agents/skills/SKILL.md`
- `policy/harness`, `policy/coding-convention`, `policy/type-definition`, `policy/data-fetch-layer`, `policy/documentation`, `policy/portfolio`, `policy/hook-extraction`, `policy/validation`, `policy/review-checklist`
- `recipe/api-authoring`, `recipe/data-dto`, `recipe/data-fetch`
- `reference/SKILL.md`, `reference/components`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| 공용 폼 컨트롤 | 제외 | 작성 페이지 마크업을 바꾸지 않는다. |
| DateRangePicker 등 | 제외 | 생성 POST와 무관하다. |

## 제약 조건 및 미확인 사항

- 201 JSON body 예시는 대화에 없었다. Location path의 `{id}`만 확정 응답이다.
- proposal 상세 GET 계약은 이번 지시 밖이다. 생성 후 조회는 기존 `ContentDetailDto`를 유지한다.
- OpenAPI Location 경로는 `/citizen/proposals/{id}`이고 앱 라우트는 `/citizen-participation/proposals/:id`다. 이동에는 path의 id만 쓴다.

## 결론

요청 DTO를 예시 JSON 필드명으로 바꾸고, 빈 `referenceCase`는 `null`로 보낸다. 성공 id는 201 Location에서 파싱한다. UI 필드명은 유지하고 매퍼만 바꾼다.
