---
name: component-choice-chip-group
description: {{PROJECT_NAME}}의 선택 칩 그룹(src/shared/ui/choice-chip-group) 사용 및 수정 가이드. 단일 선택 칩과 읽기 전용 상태 표시를 다룰 때 사용.
---

# ChoiceChipGroup

## 대상

- `src/shared/ui/choice-chip-group/choice-chip-group.tsx`
- `src/shared/ui/choice-chip-group/choice-chip-group.css`

## 계약

문자열 값을 갖는 제네릭 단일 선택 그룹이다.

| prop | 기본값 | 설명 |
| --- | --- | --- |
| `options` | 필수 | `{ label, value, tone?, disabled? }[]` |
| `value` | 없음 | 현재 선택 값. `null` 허용 |
| `onChange` | 없음 | `(value: TValue) => void` |
| `readOnly` | `false` | `true`면 모든 칩이 `disabled` |
| `ariaLabel` | 없음 | `role="group"`의 라벨 |

`ChoiceChipTone`은 `neutral | positive | warning | danger | info`다. 기본값은 `neutral`이다.

동작에서 알아야 할 점은 다음과 같다.

- **선택 해제가 없다.** 같은 칩을 다시 눌러도 `onChange(value)`가 그대로 호출된다. `dropdown`의 재선택 해제와 다르다.
- 선택 상태는 `data-selected`와 `aria-pressed` 두 곳에 반영된다.
- `onChange`가 없으면 `onClick`이 아예 붙지 않는다.
- `readOnly`는 정의서상 상태 표시 전용 영역을 위한 것이다. 이때도 마크업은 `button`이다.

## 사용 기준

- 소수의 상호 배타 선택지에 사용한다. 항목이 많으면 `dropdown`을 사용한다.
- 상태 표시 전용이면 `readOnly`를 사용한다. 클릭 가능한 것처럼 보이지 않게 한다.
- 선택 상태는 소비처가 보관한다. 내부 상태는 없다.

## 수정 규칙

- 해제 동작을 추가하면 `dropdown`과 계약이 뒤섞인다. 필요하면 사용자에게 요청한다.
- `data-selected`와 `aria-pressed`를 함께 유지한다. 하나는 CSS, 하나는 접근성 계약이다.
- 다중 선택으로 확장하려면 `value` 타입과 모든 호출부를 함께 바꾼다.
