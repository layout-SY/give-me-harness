---
name: component-status-transition-field
description: {{PROJECT_NAME}}의 상태 변경 필드(src/shared/ui/status-transition-field) 사용 및 수정 가이드. "현재 상태 → 선택" 형태의 상태 전환 입력을 다룰 때 사용.
---

# StatusTransitionField

## 대상

- `src/shared/ui/status-transition-field/status-transition-field.tsx`
- `src/shared/ui/status-transition-field/status-transition-field.css`

## 계약

`dropdown`을 감싸 "현재 상태 → [선택]" 형태를 만든다. **단계 고정 전이가 아니라 현재 상태를 제외한 임의 상태로 변경하는 모델이다.**

| prop | 기본값 | 설명 |
| --- | --- | --- |
| `currentLabel` | 필수 | 좌측에 고정 표시되는 현재 상태 라벨 |
| `options` | 필수 | `{ label, value }[]`. **현재 상태를 제외한 목록을 소비처가 만든다** |
| `value` | 필수 | 선택된 대상 상태 value. 미선택은 `null` |
| `onChange` | 필수 | `(value: string \| null) => void` |
| `dropdownType` | 필수 | 내부 `dropdown`의 그룹 식별자 |
| `label` | 없음 | 있으면 `cp-field-label`로 표시된다 |
| `placeholder` | `"변경할 상태 선택"` | |
| `disabled` | `false` | |

value ↔ index 변환을 이 컴포넌트가 흡수한다.

- `value`를 `options`에서 찾아 `dropdown`의 `index`로 변환한다. 못 찾으면 `-1`이다.
- `dropdown`이 `-1`을 돌려주면 `onChange(null)`을 호출한다. **`dropdown`의 재선택 해제가 여기서는 "선택 취소"로 이어진다.**

## 사용 기준

- 상태 변경 UI는 이 컴포넌트를 사용한다. `dropdown`을 직접 쓰지 않는다.
- `options`에서 현재 상태를 제외하는 것은 소비처 책임이다. 컴포넌트는 걸러 주지 않는다.
- 현재 상태 표시는 `currentLabel` 문자열이다. 배지가 필요하면 `StatusBadge`를 별도로 배치한다.
- `null` 수신은 오류가 아니라 선택 취소다. 저장 버튼 활성 조건에 반영한다.

## 수정 규칙

- value ↔ index 변환 책임을 소비처로 넘기지 않는다. 이 경계가 이 컴포넌트의 존재 이유다.
- `dropdown`을 다른 입력으로 교체하면 해제(-1) 계약이 함께 바뀐다.
- `cp-field-label`은 전역 클래스다. 이름을 바꾸기 전에 전역 CSS를 확인한다.
- 화살표 `→`는 `aria-hidden`이다. 제거하지 않는다.
