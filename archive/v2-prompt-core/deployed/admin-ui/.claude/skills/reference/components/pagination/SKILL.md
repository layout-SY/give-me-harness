---
name: component-pagination
description: synthoria-admin-ui의 Pagination 컴포넌트 사용 가이드. 페이지 이동 가능한 목록 요구사항에서 사용.
---

# Pagination Component

## 대상

- `src/components/pagination/pagination.tsx`

## 언제 선택하나

- 목록 페이지에서 `page`, `pageCount` 기반 이동이 필요한 경우

## 사용 핵심

- `page`, `pageCount`, `handler`를 반드시 연결한다.
- 페이지 이동 시 쿼리 상태 갱신 + 재조회 트리거를 함께 처리한다.

## 주의

- 공용 Table과 함께 쓸 때 중복 페이지네이션 렌더 여부를 확인한다.

## 리팩토링

- Icon이 불필요하게 위치해 있다. 위치를 옮길 수 있으면 옮겨라.
