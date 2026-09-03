---
name: component-icon-button
description: synthoria-admin-ui의 공용 IconButton 사용 가이드. 툴바/테이블/모달 액션 아이콘 버튼 요구사항에서 사용.
---

# IconButton Component

## 대상
- `src/components/icon-button/icon-button.tsx`

## 언제 선택하나
- 아이콘 중심 액션 버튼이 필요한 경우

## 사용 핵심
- `type="button"`을 명시하고 클릭 핸들러를 전달한다.
- 상태에 따라 `className`으로 시맨틱(`primary`, `warn`, `error`, `success`)을 적용한다.

## 주의
- 아이콘만 있는 경우 `title` 또는 `aria-label`을 넣는다.
- 스타일 부족분은 페이지 class를 추가해 보강한다.
