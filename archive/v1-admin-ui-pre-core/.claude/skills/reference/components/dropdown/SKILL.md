---
name: component-dropdown
description: synthoria-admin-ui의 공용 Dropdown 사용 가이드. 인덱스 기반 선택 UI와 필터/폼 선택 항목 요구사항에서 사용.
---

# Dropdown Component

## 대상

- `src/components/dropdown/dropdown.tsx`

## 언제 선택하나

- 셀렉트 박스/필터 선택이 필요한 경우

## 사용 핵심

- 현재 계약은 `onSelect(type, index)` 인덱스 기반이다.
- 화면 상태에서는 `index`와 `items`를 함께 관리한다.
- `placeholder`, `disabled`를 명확히 연결한다.

## 주의

- 값 직접 반환 구조로 임의 변경하지 않는다.
- 복잡한 라벨/아이콘 셀렉트는 페이지 전용 래퍼로 보강한다.
- 현재 해당 드롭다운은 items와 label만 별도로 받는 중복 props가 존재한다.
  - 또한, items라는 json 형태의 배열 인자를 기준으로 동작한다.
