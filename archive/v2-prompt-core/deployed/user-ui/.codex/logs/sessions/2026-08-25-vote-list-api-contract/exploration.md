# 탐색

## 요청

사용자는 투표 목록 응답 JSON을 확정했고, `GET /v1/api/citizen-participation/votes`의 `page`/`size`(항상), optional `status` 배열(`IN_PROGRESS`|`CLOSED`), optional `sort` 배열을 클라이언트 계약으로 맞추라고 했다. 구현 승인은 `작업 진행`이다.

## 대상 관련 사실

- 기존 투표 목록은 공용 `ContentListQueryDto`/`ContentListResponseDto`와 `useCitizenContentListQuery("vote")`를 썼다. status는 토론과 같은 `scheduled`/`open`/`closed`였다.
- 확정 목록 아이템은 숫자 `id`, `title`, `summary`, `IN_PROGRESS`|`CLOSED`, `startsAt`/`endsAt`, `commentCount`, nullable `agreeCount`/`disagreeCount`, `createdAt`이다. 페이지네이션은 `{ items, total, page, size }`다.
- 확정 envelope는 `{ code: "SUCCESS", message, data }`다.
- `VoteListPage`는 `state: "ongoing" | "closed"`와 선택적 찬반 비율을 받는다. 작성자 필드는 API에 없다.
- proposal list는 이미 전용 DTO·훅·MSW SUCCESS envelope를 쓰고 있어 같은 분리 패턴을 재사용할 수 있다.
- `src/shared/ui/`의 Pagination, StatusBadge, NoResults, Loading는 기존 투표 목록 UI가 이미 사용 중이다.

## 불러온 스킬

- `.agents/skills/SKILL.md`
- `policy/harness`, `policy/coding-convention`, `policy/type-definition`, `policy/data-fetch-layer`, `policy/documentation`, `policy/portfolio`, `policy/hook-extraction`, `policy/abstraction-strategy`, `policy/codex-native-quality`, `policy/review-checklist`
- `recipe/api-authoring`, `recipe/data-dto`, `recipe/data-fetch`
- `reference/SKILL.md`, `reference/custom-hooks`, `reference/components`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| Pagination | 재사용 | 목록 페이지가 이미 `page`/`pageCount`로 연결한다. `total`/`size`는 사용처에서 `pageCount`로 환산한다. |
| StatusBadge | 재사용 | 기존 투표 상태 뱃지 계약을 유지한다. |
| Table / useFetchAdapter | 제외 | 시민참여 목록은 카드 리스트이며 공용 Table 계약이 아니다. |
| useApi | 제외 | 이미 TanStack Query + `ApiClient` 경로가 있다. |

## 제약 조건 및 미확인 사항

- 투표 내 활동 응답 본문은 이번 지시에서 확정되지 않았다. 목록만 전용 DTO로 바꾸고 activity는 기존 content list를 유지한다.
- 투표 상세는 여전히 `ContentDetailDto`다. 목록의 `startsAt`/`endsAt`을 상세에 이식하지 않는다.
- MSW 목록의 `startsAt`/`endsAt`은 상세 fixture에 해당 필드가 없어 `createdAt`을 복사한다.
- 클라이언트 목록 page size는 라우트 `PAGE_SIZE` 10이다. OpenAPI 기본 20과 다르다.

## 결론

투표 목록은 proposal과 같이 전용 DTO가 단일 계약이어야 하고, `VOTE_STATUS`는 토론·설문·정책 status와 섞지 않는다. 첫 화면은 `page`/`size`만 보내며 status/sort UI는 추가하지 않는다.
