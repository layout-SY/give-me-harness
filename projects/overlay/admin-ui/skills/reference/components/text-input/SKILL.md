---
name: component-text-input
description: {{PROJECT_NAME}}의 공용 TextInput(src/shared/ui/text-input) 사용 및 수정 가이드. 입력 필드, 지우기·표시 토글과 오류 표기를 다룰 때 사용.
---

# TextInput

## 대상

- `src/shared/ui/text-input/text-input.tsx`
- `src/shared/ui/text-input/text-input.css`

## 계약

`@heroui/react`의 `InputGroup`을 감싼 래퍼이며 `React.InputHTMLAttributes<HTMLInputElement>`에서 `size`와 `color`를 제외한 속성을 그대로 받는다.

| prop | 기본값 | 설명 |
| --- | --- | --- |
| `enableClear` | `true` | 값이 있고 비활성·읽기 전용이 아닐 때 지우기 버튼을 노출한다 |
| `enableShow` | `false` | 비밀번호 표시 토글을 노출하고 `type`을 `password`/`text`로 전환한다 |
| `error` | 없음 | `data-invalid` 속성으로 전달된다 |
| `onClear` | 없음 | 지우기 버튼 클릭 콜백이다 |

접미 버튼은 `disabled` 또는 `readOnly`일 때 렌더링되지 않는다. 아이콘은 `~/shared/assets/icons/`의 `close.icon`, `visibility.icon`, `visibility-off.icon`을 사용한다.

## 사용 기준

- 단일 행 입력은 이 컴포넌트를 재사용한다. 여러 행은 `text-area`를 사용한다.
- 오류 표시는 자체 클래스가 아니라 `error` prop으로 전달한다. 스타일은 `data-invalid`가 담당한다.
- `enableClear`가 기본 활성이므로 지우기가 불필요한 화면에서는 명시적으로 `false`를 전달한다.

## 수정 규칙

- 테두리는 `InputGroup.Root` 한 겹만 그린다. 내부 요소에 테두리를 추가하지 않는다. Select.Trigger와 같은 field 토큰을 공유한다.
- `enableShow`가 켜진 경우에만 `type`을 제어한다. 외부에서 넘어온 `type`을 임의로 덮어쓰지 않는다.
- 접미 버튼은 `tabIndex={-1}`과 `aria-label`을 유지한다.
