---
name: domain-hook-use-dao-keyword-sort-query-state
description: DAO 목록 화면에서 page/size + keyword/by draft + required sort 구조를 공유할 때 사용하는 도메인 전용 query state hook. 전역 searchState 공용화 여부를 판단하거나 discussion/proposal 계열 DAO 목록 query 상태를 정리할 때 사용. (policy: hook-extraction, abstraction-strategy)
---

# useDaoKeywordSortQueryState

## 책임

- DAO 도메인 안에서 `page`, `size`, `keyword`, `by`, `sort`를 함께 쓰는 목록 query state를 관리한다.
- 검색 입력 draft와 실제 요청 query를 분리한다.
- 검색 submit, sort 변경, page/size 변경 시 page reset/patch 규칙을 캡슐화한다.

## 사용 핵심

- 위치: `src/pages/dao/hooks/useDaoKeywordSortQueryState.ts`
- 적용 범위: DAO 도메인 전용. `src/shared/lib/hooks` 공용 훅으로 승격하지 않는다.
- 현재 계약은 `keyword/by/sort/page/size` 전용이다. `search` 필드, status/category/date range 중심 화면에는 억지로 맞추지 않는다.
- `sort`는 required로 취급한다. optional sort 화면이면 별도 도메인 hook을 만들거나 계약을 새로 정의한다.

## 반환값

```ts
{
  queryState,
  draft,
  patchQueryState,
  handlePageChange,
  handleSizeChange,
  resetQueryState,
  handleSortChange,
  handleSubmitQuery,
  handleDraftChange,
  handleDraftReset,
}
```

## 사용 예시

```ts
type DiscussionQueryState = GetDaoDiscussionPostsQueryDto & {
  page: number;
  size: number;
};

const _initQueryState: DiscussionQueryState = {
  sort: DAO_DISCUSSION_SORT.LATEST,
  keyword: null,
  by: "TITLE",
  page: 1,
  size: 10,
};

const {
  queryState,
  draft,
  resetQueryState,
  handleSortChange,
  handlePageChange,
  handleSubmitQuery,
  handleDraftChange,
  handleDraftReset,
} = useDaoKeywordSortQueryState<DaoSearchBy, DaoDiscussionSort>(_initQueryState);
```

## 주의

- `useFetchAdapter` 호출이나 `refetch` 트리거를 이 hook에 넣지 않는다. query state와 fetch 책임을 분리한다.
- API DTO 조합 타입을 그대로 전역 UI state 계약으로 승격하지 않는다. DTO는 transport, 이 hook은 DAO UI query state primitive다.
- DAO 안에서도 query shape가 다르면 별도 도메인 hook을 만든다. 예: `search` 필드를 쓰는 proposal 목록, status/category tab 중심 목록.
