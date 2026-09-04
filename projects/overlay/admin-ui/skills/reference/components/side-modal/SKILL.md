---
name: component-side-modal
description: {{PROJECT_NAME}}의 공용 SideModal(src/shared/ui/side-modal) 사용 및 수정 가이드. 우측 드로어 패널을 다룰 때 사용.
---

# SideModal

## 대상

- `src/shared/ui/side-modal/side-modal.tsx`

## 계약

`@heroui/react`의 `Drawer`를 감싼 래퍼다. `modal`과 prop 계약이 동일하다.

| prop | 설명 |
| --- | --- |
| `open` | HeroUI `isOpen`으로 전달된다 |
| `close` | `onOpenChange(false)`일 때 호출된다 |
| `children` | `Drawer.Dialog`의 내용이다 |
| `className` | `Drawer.Dialog`에 전달된다 |

구조는 `Drawer.Root > Drawer.Backdrop > Drawer.Content > Drawer.Dialog`이며 `placement="right"` 고정이다. `Drawer.Handle`이 내용보다 먼저 렌더링된다. ESC와 백드롭 클릭 닫힘은 HeroUI 기본 동작이다.

## 사용 기준

- 목록 옆에서 상세를 여는 패널에 사용한다. 중앙 정렬이 필요하면 `modal`을 사용한다.
- 배치는 우측 고정이다. 좌측 패널이 필요하면 사용자에게 요청한다.

## 수정 규칙

- `placement="right"`와 `Drawer.Handle` 배치를 임의로 바꾸지 않는다.
- `modal`과 계약이 같다고 해서 구현을 공유 컴포넌트로 합치지 않는다. HeroUI 기반 요소가 다르다.
