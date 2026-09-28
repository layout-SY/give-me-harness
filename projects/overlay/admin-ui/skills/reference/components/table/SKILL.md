---
name: component-table
description: {{PROJECT_NAME}}의 공용 Table(src/shared/ui/table) 사용 및 수정 가이드. 컬럼 정의, 행 선택, 순번 열, sticky 열과 내장 페이지네이션을 다룰 때 사용.
---

# Table

## 대상

- `src/shared/ui/table/table.tsx`
- `src/shared/ui/table/table.css`
- `src/shared/ui/table/index.ts`
- `src/shared/ui/table/interface/columnDef.ts`
<!-- 비활성 참조: src/shared/ui/table/hooks/useFetchAdapter.ts (사용처 없는 훅으로 제거됨) -->
- `src/shared/ui/table/utils/commonCell.tsx`
- `src/shared/ui/table/utils/resolveRowNumber.ts`

## 계약

제네릭 `TRow`를 받는 목록 표다.

| prop | 기본값 | 설명 |
| --- | --- | --- |
| `columns` | 필수 | `TableColumnDef<TRow>[]` |
| `rows` | 필수 | 표시할 행 |
| `isLoading` | 없음 | 로딩 중에는 빈 상태를 표시하지 않는다 |
| `emptyContent` | 없음 | 행이 없을 때 표 본문에 넣을 내용 |
| `showRowNumber` | `true` | 좌측 순번 열 표시 여부 |
| `getRowClassName` | 없음 | `(row, rowIndex) => string \| undefined` |
| `isRowSelected` | 없음 | 선택 행 표시. `aria-selected`로 반영된다 |
| `onRowClick` | 없음 | 전달하면 행이 클릭·키보드 조작 가능해진다 |
| `page`, `itemCount`, `pageSize`, `pageCount`, `handler` | 없음 | 페이지네이션과 순번 계산에 쓰인다 |

컬럼은 `kind`로 분기한다.

- `accessor`: `accessor({ row, rowIndex })` 값을 `commonCell`이 `type`에 맞게 렌더링한다.
- `action`: `commonCell`이 `type`과 `onOpenDetail`로 액션을 렌더링한다.
- `custom`: `cell(context)`를 직접 호출한다. `context`에 `row`, `rowIndex`, `column`, `itemCount`, `page`, `pageSize`, `rowsLength`가 담긴다.

동작에서 반드시 알아야 할 점은 다음과 같다.

- **페이지네이션이 내장이다.** 표 아래에 `Pagination`이 항상 렌더링되며 값이 없으면 `page=1`, `pageCount=1`, 빈 핸들러로 동작한다. 별도로 페이지네이션을 붙이지 않는다.
- **빈 상태도 내장이다.** `isLoading`이 아니고 행이 없으면 `NoResults`가 렌더링된다. `emptyContent`는 그와 별개로 표 본문 행에 들어간다. 둘을 같이 쓰면 두 개가 함께 보인다.
- 순번 열 값은 `resolveRowNumber`가 `page`, `pageSize`, `itemCount`, `rowsLength`로 계산한다. 페이지를 넘겨도 이어지는 번호를 만들기 위함이다.
- `onRowClick`이 있을 때만 `tabIndex=0`, `aria-selected`, Enter·Space 키 처리가 활성화된다.
- `sticky: "right"` 컬럼이 둘 이상이면 마지막에서 두 번째에 `is-sticky-right-secondary`가 붙는다.
- `column.dimAsId`는 `is-id-column` 클래스를 붙인다.
- `action` + `type === "open_detail"` 컬럼은 `is-open-detail-action-column`을 받는다.

## 사용 기준

- 목록 화면은 이 컴포넌트를 재사용한다. 표 마크업을 직접 작성하지 않는다.
- 화면정의서에 순번 열이 없으면 `showRowNumber={false}`를 전달한다.
<!-- useFetchAdapter가 실제로 존재하는 브랜치에서만 서버 페이징에 함께 사용한다. -->
- 셀 표현이 `commonCell`의 `type`으로 표현되면 `custom` 대신 `accessor`를 쓴다.

## 수정 규칙

- 내장 페이지네이션과 내장 `NoResults`를 제거하면 모든 목록 화면이 함께 깨진다. 변경 전 호출부를 전수 확인한다.
- 행 `key`가 `rowIndex`다. 정렬·필터로 순서가 바뀌는 화면에서 입력 상태를 셀에 보관하지 않는다.
- `resolveRowNumber`의 인자 조합을 바꾸면 페이지 간 순번이 어긋난다.
- sticky 보조 클래스 계산 규칙은 CSS와 짝이다. 한쪽만 바꾸지 않는다.
