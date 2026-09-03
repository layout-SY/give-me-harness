---
name: component-search-state-bar
description: synthoria-admin-ui의 SearchStateBar/TableSortFilter 사용 가이드. 탭, 검색어, 정렬, 생성 액션이 있는 목록 상단 요구사항에서 사용.
---

# Search State Bar

## 대상

- `src/shared/ui/search-state-bar/searchStateBar.tsx`
- `src/shared/ui/search-state-bar/TableSortFilter.tsx`

## 언제 선택하나

- 목록 상단에 탭/검색/정렬/생성 버튼이 함께 필요한 경우

## 사용 핵심

- `tabs`, `keyword`, `onSubmit`, `onTabChange`, `onChangeKeyword`를 연결한다.
- 탭 항목이 없더라도 "전체" 탭은 구성한다.

## 주의

- `aria-label`/문구는 `mui` 기반으로 맞춘다.
- 화면별 레이아웃 미세 조정은 페이지 CSS에서 보강한다.
