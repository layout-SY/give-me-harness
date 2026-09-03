# 탐색

## 요청

사용자는 `GET /citizen/proposals` 계약을 제시했다. `mine=true`면 토큰 사용자가 등록한 제안만 내려가고, 목록에는 본문 4필드(`background`·`content`·`expectedEffect`·`referenceCase`)가 없으며 상세에서만 내려간다. `sort`는 `createdAt`·`id`만 허용하고 기본값은 `createdAt,desc`다. 제안 목록에 「내활동만 보기」 필터를 추가하라고 지시했다.

## 대상 관련 사실

- 직전 계약에서 `getProposalList`는 `page`/`size`만 보냈고, 제안 목록의 내 활동은 `useMyProposalActivityQuery`가 `/me/activity?content=proposal`를 쳤다.
- 화면 URL 필터는 기존 `?myActivity=true`다. `useContentListRouteState().myActivityOnly`가 토글 상태를 소유한다.
- `ProposalListPage` 헤더에 `MyActivityToggle`이 이미 있고 기본 라벨은 「내 활동 보기」였다.
- 목록 아이템 스키마는 `id`/`title`/`status`/`author`/`createdAt`이며 본문 4필드는 상세 스키마에만 있다.
- MSW fixture 59는 `mine: true`, 58은 기본 `false`다. 상세 매퍼 `toProposalDetailResponse`가 본문 4필드를 채운다.
- 투표 목록은 여전히 `useMyActivityQuery("vote")`를 쓴다.

## 불러온 스킬

- `.agents/skills/SKILL.md`
- `policy/harness`, `policy/coding-convention`, `policy/type-definition`, `policy/data-fetch-layer`, `policy/documentation`, `policy/portfolio`, `policy/hook-extraction`, `policy/abstraction-strategy`, `policy/codex-native-quality`, `policy/review-checklist`, `policy/publishing`, `policy/styles`
- `recipe/api-authoring`, `recipe/data-dto`, `recipe/data-fetch`
- `reference/SKILL.md`, `reference/custom-hooks`, `reference/components`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| Pagination | 재사용 | 목록 페이지가 이미 `page`/`pageCount`로 연결한다. |
| StatusBadge | 재사용 | 기존 제안 상태 뱃지 계약을 유지한다. |
| 새 필터 컴포넌트 | 제외 | `MyActivityToggle`이 이미 같은 헤더 슬롯을 차지한다. 라벨만 바꾼다. |
| useApi / useFetchAdapter | 제외 | 이미 TanStack Query + `ApiClient` 경로가 있다. |

## 제약 조건 및 미확인 사항

- 정렬 UI는 이번 지시에 없다. 전송 기본값만 맞춘다.
- 투표·토론의 `mine` 계약은 제시되지 않았다. `/me/activity`를 유지한다.
- 내 활동 페이지는 이번 범위가 아니다. `useMyProposalActivityQuery`를 유지한다.
- 목록 `summary`는 응답에 없어 빈 문자열 매핑을 유지한다.

## 결론

제안 목록의 내 활동은 별도 activity API가 아니라 `GET /citizen/proposals?mine=true`다. 같은 목록 DTO를 쓰고, 화면 토글은 기존 `myActivity` 쿼리를 `mine` 전송으로 옮긴다.
