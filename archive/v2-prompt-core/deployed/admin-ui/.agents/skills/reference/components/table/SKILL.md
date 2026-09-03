---
name: component-table
description: synthoria-admin-ui의 공용 Table 컴포넌트(src/shared/ui/table) 사용 가이드. 목록/컬럼 렌더링, pagination, useFetchAdapter 연동이 필요한 요구사항에서 사용.
---

# Table Component

## 대상

- `src/shared/ui/table/table.tsx`
- `src/shared/ui/table/hooks/useFetchAdapter.ts`

## 언제 선택하나

- 표 형태 목록 + 페이지네이션 + 공통 셀 렌더 규칙이 필요한 경우
- DAO/유저 관리형 리스트처럼 `TableColumnDef` 기반 구성이 필요한 경우

## 사용 핵심

- 컬럼은 `TableColumnDef`로 선언한다. API 응답과의 1:1 매칭은 필수는 아니지만, 권고한다.
- 데이터 fetch는 가능하면 `useFetchAdapter`와 함께 사용한다.
- `searchState` 변경 뒤 `setRequestSearch(true)` 호출이 필요하다.

## 주의

- `Table`은 하단 `Pagination`을 기본 렌더한다.
- 화면 요구가 더 복잡하면 페이지에서 래핑 스타일/보조 로직을 추가한다.

## 수정(or 리팩토링) 주의

- 리팩토링 시 TanStack-Query Table 라이브러리를 참고하여 리팩토링을 진행한다.
