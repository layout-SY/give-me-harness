# 탐색

## 요청

사용자는 확정된 proposal list 응답을 반영하되, 요청은 `page`/`size`만 추가하고 내 활동 같은 필터는 `?content=proposal|vote`와 `page`/`size`를 가진 별도 API로 받도록 수정하라고 지시했다.

## 대상 관련 사실

- 기존 `getProposalList`는 공용 `ContentListQueryDto`/`ContentListResponseDto`를 썼다. 아이템에 `type`·`summary`·`authorName`이 있고 페이지네이션은 `pageSize`/`itemCount`/`pageCount`였다.
- 확정 목록 아이템은 `id: number`, `title`, `status`, `author.nickname`, `createdAt`이며 페이지네이션은 `total`/`page`/`size`다.
- 확정 envelope는 `{ code: "SUCCESS", message, data }`다. 공용 `toApiResult`는 기존에 `success === true`만 성공으로 봤다.
- 목록 화면의 `내 활동만`은 query `myActivity=true`를 같은 list endpoint에 붙이고 있었다.
- `/v1/api/citizen-participation/me/activity`가 이미 있었고 query는 `type`이었다.
- `ProposalListPage`는 `summary`를 필수로 렌더한다. 확정 목록 응답에는 summary가 없다.
- `src/shared/ui/`의 Pagination, StatusBadge, NoResults, Loading는 기존 목록 UI가 이미 사용 중이다.

## 불러온 스킬

- `.agents/skills/SKILL.md`
- `policy/harness`, `policy/coding-convention`, `policy/type-definition`, `policy/data-fetch-layer`, `policy/documentation`, `policy/portfolio`, `policy/hook-extraction`, `policy/abstraction-strategy`, `policy/codex-native-quality`, `policy/review-checklist`
- `recipe/api-authoring`, `recipe/data-dto`, `recipe/data-fetch`
- `reference/SKILL.md`, `reference/custom-hooks`, `reference/components`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| Pagination | 재사용 | 목록 페이지가 이미 `page`/`pageCount`로 연결한다. `total`/`size`는 사용처에서 `pageCount`로 환산한다. |
| StatusBadge | 재사용 | 기존 제안 상태 뱃지 계약을 유지한다. |
| Table / useFetchAdapter | 제외 | 시민참여 목록은 카드 리스트이며 공용 Table 계약이 아니다. |
| useApi | 제외 | 이미 TanStack Query + `ApiClient` 경로가 있다. |

## 제약 조건 및 미확인 사항

- activity API의 응답 본문 형태는 이번 지시에서 확정되지 않았다. 요청만 `content`/`page`/`size`로 맞추고 응답은 기존 스키마를 유지했다.
- proposal 상세 API는 미확정이라 fixture/상세 경로는 문자열 id(`"59"`)를 유지한다.
- `REJECTED`는 API 상태값에 있으나 기존 UI 매퍼는 숨긴다.

## 결론

proposal list는 전용 DTO가 단일 계약이 되어야 하고, 내 활동은 list query에 섞지 않고 `/me/activity`로 보낸다. 공용 content list DTO는 다른 타입에 남겨 둔다.
