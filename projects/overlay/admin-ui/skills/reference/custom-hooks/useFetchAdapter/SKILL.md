---
name: hook-use-fetch-adapter
description: {{PROJECT_NAME}}의 useFetchAdapter 훅(src/shared/ui/table/hooks/useFetchAdapter.ts) 사용 및 수정 가이드. 목록 조회, 행 매핑, 페이지네이션·탭 카운트와 debounce·throttle을 다룰 때 사용.
---

# useFetchAdapter

## 대상

- `src/shared/ui/table/hooks/useFetchAdapter.ts`
- `src/shared/api/common/dto.ts` (`TableApiResponseDto`, `TablePagination`, `TableItemCountMap`)
- `src/shared/lib/utils/performance.util.ts` (`debounce`, `throttle`)

`shared/lib/hooks`가 아니라 **`table` 컴포넌트 하위에 있다.** 표 전용 조회 어댑터다. **명명 내보내기다.**

## 계약

```ts
const { isLoading, setIsLoading, rows, fetchedPagination, refetch, fetchedData, tabCount, totalItemCount } =
  useFetchAdapter({ mapRow, searchState, fetchApi, enabled, debounceMs, throttleMs });
```

| 인자 | 기본값 | 설명 |
| --- | --- | --- |
| `fetchApi` | 필수 | `(params: TQuery) => Promise<TableApiResponseDto<TItem, TKey>>` |
| `searchState` | 필수 | 질의 상태. **바뀌면 자동 재조회한다** |
| `mapRow` | 필수 | `(row: TItem) => TRow` 행 변환 |
| `enabled` | `true` | `false`면 조회하지 않는다 |
| `debounceMs` | `0` | `> 0`이면 debounce 적용 |
| `throttleMs` | `0` | `> 0`이면 throttle 적용. debounce가 우선한다 |

응답 `content`, `pagination`, `count`를 각각 `fetchedData`, `fetchedPagination`, `tabCount`/`totalItemCount`로 노출한다. `rows`는 `fetchedData`에 `mapRow`를 적용한 결과다.

동작에서 알아야 할 점은 다음과 같다.

- `searchState`가 바뀔 때마다 `useEffect`가 재조회한다. 별도 호출이 필요 없다.
- 자체 `requestSequenceRef`로 **마지막 요청만 반영한다.** `useApi`의 race 가드와 별개의 2차 방어다.
- `fetchedPagination` 기본값은 `{ page: 1, pageCount: 1 }`이다.
- `refetch()`는 debounce·throttle을 우회하고 즉시 조회한다.
- `mapRow`와 `fetchApi`가 `useCallback` 의존성에 들어간다. **인라인으로 새로 만들면 매 렌더 재조회된다.**

## 사용 기준

- 서버 페이징 목록은 이 훅과 `table`을 함께 사용한다. 조회 로직을 화면에 직접 작성하지 않는다.
- `fetchApi`와 `mapRow`는 컴포넌트 밖에 두거나 `useCallback`으로 고정한다.
- `searchState`도 참조가 안정적이어야 한다. 매 렌더 새 객체를 만들지 않는다.
- 검색어 입력 연동에는 `debounceMs`를 사용한다.
- 등록·삭제 후 갱신은 `refetch()`를 호출한다.
- 탭 카운트는 `tabCount`를 `search-state-bar`의 `tabs[].count`로 전달한다.

## 수정 규칙

- `requestSequenceRef` 검사를 제거하지 않는다. 이전 응답이 목록을 덮어쓴다.
- debounce가 throttle보다 우선하는 분기 순서를 바꾸지 않는다.
- 반환 키 이름은 여러 목록 화면의 계약이다. 이름을 바꾸면 호출부를 전수 확인한다.
- `setIsLoading`을 외부에 노출하는 현재 계약을 제거하려면 외부에서 로딩을 제어하는 화면이 있는지 먼저 확인한다.
