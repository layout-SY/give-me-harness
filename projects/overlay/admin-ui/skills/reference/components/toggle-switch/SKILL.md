---
name: component-toggle-switch
description: {{PROJECT_NAME}}의 공용 ToggleSwitch(src/shared/ui/toggle-switch) 사용 및 수정 가이드. 켬/끔 상태 전환 UI를 다룰 때 사용.
---

# ToggleSwitch

## 대상

- `src/shared/ui/toggle-switch/toggle-switch.tsx`
- `src/shared/ui/toggle-switch/toggle-switch.css`

## 계약

`@heroui/react`의 `Switch`를 감싼 제어 컴포넌트다.

| prop | 기본값 | 설명 |
| --- | --- | --- |
| `checked` | 필수 | HeroUI `isSelected`로 전달된다 |
| `onChange` | 필수 | `(checked: boolean) => void` |
| `disabled` | `false` | HeroUI `isDisabled`로 전달된다 |
| `className` | 없음 | `Switch`에 그대로 전달된다 |

`Switch.Content > Switch.Control > Switch.Thumb` 구조를 고정으로 사용하고, 바깥을 `toggle-switch-wrapper` div로 감싼다.

## 사용 기준

- 완전 제어 컴포넌트다. 소비처가 `checked` 상태를 보관한다. 내부 상태는 없다.
- 즉시 반영이 아니라 저장 버튼이 필요한 화면이라면 소비처가 임시 상태를 따로 관리한다.

## 수정 규칙

- `toggle-switch-wrapper` 래퍼 div와 HeroUI 하위 구조는 CSS가 전제한다. 계층을 바꾸지 않는다.
- 비제어 모드를 추가하지 않는다.
- 라벨이 필요하면 소비처에서 배치한다. 컴포넌트에 문구를 넣지 않는다.
