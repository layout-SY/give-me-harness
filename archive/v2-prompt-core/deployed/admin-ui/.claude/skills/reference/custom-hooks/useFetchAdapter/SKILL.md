---
name: hook-use-fetch-adapter
description: synthoria-admin-ui의 useFetchAdapter 훅(src/components/table/hooks/useFetchAdapter.ts) 사용 가이드. 공용 Table + 검색·페이지네이션 화면에서 fetch 트리거 플래그 기반으로 데이터를 바인딩할 때 사용.
---

# useFetchAdapter Hook (synthoria-admin-ui)

## 언제 이 스킬을 사용하나요?

- `src/components/table` 공용 Table을 사용하는 목록 화면을 새로 만들거나 수정할 때
- 검색 조건(`searchState`) + 페이지네이션이 필요한 화면을 만들 때
- 모달 작업 후 목록을 다시 불러오는 흐름을 추가할 때 (`setRequestSearch(true)` + `refresh-*` pubsub 연동)
- 다중 카운트(예: 총 개수, 활성/비활성 카운트)를 함께 표시해야 하는 테이블

## 0) 작업 시작 전 필수 확인

1. 화면이 정말 공용 `Table` 패턴인지 확인한다.
   - 공용 Table 사용 페이지: `src/pages/manage/users/index.tsx`, `src/pages/dao/proposal-manage/index.tsx`, `src/pages/dao/pass-management/**`, `src/pages/dao/discuss-posts-management/**` 등
   - 수동 `<table>` 패턴 페이지: `src/pages/manage/items/index.tsx` (이 경우 `useFetchAdapter` 미사용)
2. API 응답 형태가 `TableApiResponseDto<TItem, TCount>` (`{ content, pagination, count }`)와 호환되는지 확인한다.
3. 행(row) 인터페이스가 `src/components/table/interface/apiTableRowInterface.ts`에 정의되어 있는지 확인하고, 없다면 추가한다.

---

## 1) 훅 시그니처

```ts
useFetchAdapter<TQuery, TItem, TRow, TCount = TableItemAmountCountDto>({
  mapRow,
  searchState,
  fetchApi,
  enabled = true,
})
```

### 1-1. 입력

- `mapRow(row: TItem) => TRow`: API 응답 한 건을 테이블 행 모델로 변환
- `searchState: TQuery`: 검색/필터/정렬/페이지 입력 객체 (페이지 컴포넌트 state)
- `fetchApi(params: TQuery) => Promise<TableApiResponseDto<TItem, TCount>>`: 도메인 API 함수
- `enabled?: boolean`: false면 자동 fetch가 일어나지 않음 (조건부 활성화에 사용)

### 1-2. 출력

- `rows: TRow[]` — `mapRow`로 변환된 행 배열
- `fetchedPagination: PaginationDto` — 응답의 `pagination` 그대로
- `fetchedCount: TCount | undefined` — 응답의 `count` 그대로
- `totalItemCount: number` — `resolveTableTotalItemCount`로 정규화된 총 개수
- `fetchedData: TItem[]` — 변환 전 원본 응답 콘텐츠
- `isLoading: boolean`, `setIsLoading` — 로딩 상태와 setter
- `setRequestSearch: (boolean) => void` — **다음 fetch 트리거 플래그**

---

## 2) 트리거 모델 — 가장 흔한 함정

`useFetchAdapter`는 `searchState`가 변해도 **자동 재요청하지 않는다.**
모든 fetch는 `requestSearch` 플래그가 true일 때만 일어난다.

- 초기 1회: `requestSearch` 기본값 true → 마운트 직후 자동 1회 fetch
- 이후 fetch: 검색/필터 변경 시 `setRequestSearch(true)`를 **반드시 호출**
- pubsub 리프레시: `refresh-*` 이벤트 핸들러에서도 `setRequestSearch(true)` 호출

### 2-1. 트리거가 필요한 시점 체크리스트

- 검색 폼 submit
- 필터 변경 (드롭다운, 토글)
- 페이지 이동 (`Pagination` `handler`)
- 정렬 변경 (`TableSortFilter`)
- 페이지 사이즈 변경
- pubsub `refresh-*` 수신
- 모달 작업 완료 후

---

## 3) 사용 패턴

### 3-1. 기본 구성

```tsx
const { api } = useApi();
const { pubsub } = usePubSub();

const [searchState, setSearchState] = useState<GetUserListDto>(_initSearchState);

const { rows, fetchedPagination, setRequestSearch, isLoading, totalItemCount } = useFetchAdapter<
  GetUserListDto,
  GetUsersResponseDto,
  ManageUsersTableRow
>({
  mapRow: (row) => ({
    id: row.id,
    user_id: row.id,
    user_name: `${row.firstName} ${row.lastName}`,
    user_email: row.email,
    user_status: row.status as USER_STATUS,
    user_created_at: row.createdAt,
  }),
  searchState,
  fetchApi: api.users.getUsers,
});
```

### 3-2. 검색 submit

```tsx
const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault();
  setSearchState((prev) => ({ ...prev, page: 1 }));
  setRequestSearch(true);
};
```

### 3-3. 페이지/필터 변경

```tsx
<Pagination
  page={fetchedPagination.page}
  pageCount={fetchedPagination.pageCount}
  handler={(page) => {
    setSearchState((prev) => ({ ...prev, page }));
    setRequestSearch(true);
  }}
/>
```

### 3-4. pubsub 리프레시 연동

```tsx
useEffect(() => {
  const off = pubsub.subscribe("refresh-users", () => setRequestSearch(true));
  return () => off();
}, []);
```

### 3-5. 카운트 분기 사용

```tsx
const { fetchedCount } = useFetchAdapter<GetXxxQuery, XxxItem, XxxRow, XxxCount>({
  mapRow: ...,
  searchState,
  fetchApi: api.xxx.getXxxList,
});

return <span>{fetchedCount?.activeCount ?? 0}</span>;
```

> 기본 `TCount`는 `TableItemAmountCountDto`. 도메인별로 다른 카운트가 필요하면 명시적으로 제네릭을 지정한다.

---

## 4) 공용 Table과의 결합

- `Table` 컴포넌트는 항상 내부에 `Pagination`을 렌더한다 (`handler` 미전달 시 동작은 no-op).
- `rows`, `isLoading`, `fetchedPagination`을 그대로 Table에 넘기는 것이 표준이다.
- 정렬/필터 UI: `src/components/search-state-bar/TableSortFilter.tsx`와 함께 사용 가능. 정렬/필터 콜백에서 `searchState` 갱신 후 `setRequestSearch(true)`를 호출한다.
- 빈 상태/스켈레톤은 `Table` 자체 처리에 위임한다. 페이지 측에서 별도 분기를 추가하지 않는다.

---

## 5) 구현 시 주의사항

- **트리거 누락**: `searchState`만 바꾸고 `setRequestSearch(true)`를 잊으면 화면이 정지한다 → 가장 흔한 버그.
- **fetchApi 안정성**: `useCallback` 의존성 배열에 `fetchApi`가 들어 있다. 매 렌더 새로 만들어지는 인라인 함수 사용 시 무한 루프 위험. `api.<domain>.<method>` 같은 안정 참조나 `useCallback` 메모이즈된 함수만 사용한다.
- **응답 키 가정**: 응답은 반드시 `{ content, pagination, count }` 구조여야 한다. 도메인 API가 다른 형태를 반환하면 어댑터를 직접 사용하지 말고 도메인 API 레이어에서 형태를 맞춰준다.
- **enabled 사용처**: 권한/사전 데이터 로드 후에만 fetch가 필요할 때 `enabled` 플래그를 사용한다. 단, false→true 전환 시점에 자동 fetch가 발생한다.
- **mapRow 의존성**: `mapRow` 함수 참조가 매 렌더 바뀌면 `rows` 메모이즈가 무효화된다. 큰 리스트라면 `useCallback`으로 묶는다.
- **로컬 isLoading**: 일반적으로 `useFetchAdapter`의 `isLoading`만 사용해도 충분하다. 화면에서 추가 비동기 흐름이 있으면 `setIsLoading`을 함께 사용해 통합 관리할 수 있다.
- **에러 처리**: 내부에서 `useApi().execute`를 사용하므로 기본 에러 Dialog가 자동으로 뜬다. 별도 에러 핸들링이 필요하면 어댑터 호출을 `useApi`로 풀어 대체한다.
- **수동 테이블에 끼우지 말 것**: 수동 `<table>` 패턴(`src/pages/manage/items/index.tsx`)은 `useApi` + 로컬 state 패턴이다. 일관성을 위해 그 패턴 안에서 작업한다.

---

## 6) 빠른 템플릿

### 6-1. 페이지 구성

```tsx
const ListPage = () => {
  const { api } = useApi();
  const { pubsub } = usePubSub();

  const [searchState, setSearchState] = useState<GetFooListDto>(_initSearchState);

  const { rows, fetchedPagination, setRequestSearch, isLoading, totalItemCount } = useFetchAdapter<
    GetFooListDto,
    FooItemDto,
    FooTableRow
  >({
    mapRow: (row) => ({
      id: row.fooId,
      name: row.name,
      createdAt: row.createdAt,
    }),
    searchState,
    fetchApi: api.foo.getFooList,
  });

  useEffect(() => {
    const off = pubsub.subscribe("refresh-foos", () => setRequestSearch(true));
    return () => off();
  }, []);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setSearchState((prev) => ({ ...prev, page: 1 }));
    setRequestSearch(true);
  };

  return (
    <>
      <SearchStateBar onSubmit={handleSubmit} />
      <Table
        columns={columns}
        rows={rows}
        isLoading={isLoading}
        pagination={fetchedPagination}
        totalItemCount={totalItemCount}
        onPageChange={(page) => {
          setSearchState((prev) => ({ ...prev, page }));
          setRequestSearch(true);
        }}
      />
    </>
  );
};
```

### 6-2. 카운트가 다른 경우

```tsx
type FooCount = { totalCount: number; activeCount: number };

const { fetchedCount } = useFetchAdapter<GetFooListDto, FooItemDto, FooTableRow, FooCount>({
  mapRow: ...,
  searchState,
  fetchApi: api.foo.getFooList,
});
```
