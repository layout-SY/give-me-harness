---
name: component-modal
description: {{PROJECT_NAME}}의 공용 Modal(src/shared/ui/modal) 사용 및 수정 가이드. 중앙 다이얼로그 열기·닫기 계약을 다룰 때 사용.
---

# Modal

## 대상

- `src/shared/ui/modal/modal.tsx`
- `src/shared/ui/modal/index.ts`

## 계약

`@heroui/react`의 `Modal`을 감싼 래퍼다. 내보내는 이름은 `CustomModal`이다.

| prop | 설명 |
| --- | --- |
| `open` | HeroUI `isOpen`으로 전달된다 |
| `close` | `onOpenChange(false)`일 때 호출된다 |
| `children` | `Modal.Dialog`의 내용이다 |
| `className` | `Modal.Dialog`에 전달된다 |

구조는 `Modal.Root > Modal.Backdrop > Modal.Container > Modal.Dialog`로 고정이다. **ESC와 백드롭 클릭 닫힘은 HeroUI 기본 동작이므로 따로 구현하지 않는다.**

## 사용 기준

- 중앙 다이얼로그에 사용한다. 우측 패널은 `side-modal`, 애니메이션이 필요한 자체 dialog는 `popup`을 사용한다.
- `open`/`close`는 소비처가 보관한다. 내부 상태는 없다.
- 닫기 버튼과 헤더는 `children`에서 구성한다. 컴포넌트가 제공하지 않는다.

## 수정 규칙

- HeroUI 하위 구조 계층을 바꾸지 않는다.
- ESC·백드롭 닫힘을 자체 이벤트 리스너로 다시 구현하지 않는다. 중복 호출이 된다.
- `popup`과 계약(`open`/`close`)이 같지만 구현이 전혀 다르다. 한쪽 변경을 다른 쪽에 그대로 옮기지 않는다.
