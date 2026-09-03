---
name: component-button
description: synthoria-admin-ui의 공용 Button 컴포넌트(src/shared/ui/button) 사용 및 수정 가이드. 기본 액션 버튼 UI, 로딩 상태 처리, 클래스 규칙을 다룰 때 사용.
---

# Button Component

## 대상

- `src/shared/ui/button/button.tsx`
- `src/shared/ui/button/button.css`

## 사용 기준

- 페이지 액션 버튼은 먼저 `Button` 재사용을 우선한다.
- 로딩 상태가 필요하면 `isLoading` 패턴을 유지한다.
- 텍스트는 하드코딩하지 말고 `mui` 키와 함께 사용한다.

## 수정(or 리팩토링) 규칙

- 기존 `className` 계약을 깨지 않는다.
- `type`, `disabled`, `onClick` 등 기본 버튼 속성 호환을 유지한다.
- 기능/스타일 관련 확장이 필요한 경우 사용자에게 요청한다.
