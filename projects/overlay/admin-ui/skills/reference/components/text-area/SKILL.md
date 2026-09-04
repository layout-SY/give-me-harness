---
name: component-text-area
description: {{PROJECT_NAME}}의 공용 TextArea(src/shared/ui/text-area) 사용 및 수정 가이드. 여러 행 입력과 ref 전달을 다룰 때 사용.
---

# TextArea

## 대상

- `src/shared/ui/text-area/text-area.tsx`
- `src/shared/ui/text-area/text-area.css`

## 계약

`@heroui/react`의 `TextArea`를 감싼 얇은 래퍼다. `React.TextareaHTMLAttributes<HTMLTextAreaElement>`에서 `color`만 제외한 속성을 그대로 전달한다.

- `React.forwardRef`로 구현되어 `HTMLTextAreaElement` ref를 받는다. 포커스 제어와 폼 라이브러리 연동에 사용한다.
- 고정 클래스 `text-area-component`를 부여한다.
- `text-input`과 달리 지우기·표시 토글, `error` prop이 없다.

## 사용 기준

- 여러 행 입력에 사용한다. 단일 행은 `text-input`을 사용한다.
- 오류 상태 표기가 필요하면 소비처가 별도로 처리한다. 이 컴포넌트에는 `error` 계약이 없다.

## 수정 규칙

- `forwardRef`와 `displayName`을 유지한다. ref를 잃으면 폼 연동이 깨진다.
- 고정 클래스 `text-area-component`는 CSS 진입점이다. 이름을 바꾸지 않는다.
- `text-input`의 접미 버튼 기능을 이쪽으로 복제하지 않는다. 필요하면 사용자에게 요청한다.
