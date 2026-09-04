---
name: component-dropdown
description: {{PROJECT_NAME}}의 공용 Dropdown(src/shared/ui/dropdown) 사용 및 수정 가이드. index 기반 선택 계약과 동일 항목 재선택 해제 동작을 다룰 때 사용.
---

# Dropdown

## 대상

- `src/shared/ui/dropdown/dropdown.tsx`

## 계약

`@heroui/react`의 `Select`와 `ListBox`를 감싼 제네릭 래퍼다. 타입 파라미터 `TType`은 `string | number`다.

| prop | 설명 |
| --- | --- |
| `type` | 선택 그룹 식별자. 콜백 첫 인자로 되돌아온다 |
| `index` | 현재 선택 인덱스. 미선택은 `-1` |
| `items` | `{ label: string; value: unknown }[]` |
| `onSelect` | `(type, index) => void` |
| `id`, `ariaLabel`, `label`, `placeholder`, `disabled` | 선택 사항 |

동작에서 반드시 알아야 할 두 가지가 있다.

- **값이 아니라 인덱스로 통신한다.** `items[i].value`는 컴포넌트가 해석하지 않는다. 소비처가 인덱스로 조회한다.
- **같은 항목을 다시 고르면 해제된다.** 재선택 시 `onSelect(type, -1)`이 호출된다. 단일 선택 토글로 동작한다.

`items`가 비어 있으면 `disabled` 값과 무관하게 비활성이다. `aria-label`은 `ariaLabel → label → placeholder → "선택"` 순서로 결정된다.

## 사용 기준

- 선택 상태는 소비처가 인덱스로 보관한다. 미선택은 `-1`로 표현한다.
- 해제가 허용되지 않는 화면이라면 `-1` 수신 시 소비처가 이전 값을 유지해야 한다. 컴포넌트는 해제를 막지 않는다.

## 수정 규칙

- index 기반 계약과 재선택 해제 동작은 다수 화면이 의존한다. 값 기반으로 바꾸지 않는다.
- `items` 비었을 때 자동 비활성 규칙을 유지한다.
- 다중 선택이 필요하면 이 컴포넌트를 확장하지 말고 사용자에게 요청한다.
