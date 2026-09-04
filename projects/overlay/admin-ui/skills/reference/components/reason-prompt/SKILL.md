---
name: component-reason-prompt
description: {{PROJECT_NAME}}의 사유 입력 모달(src/shared/ui/reason-prompt) 사용 및 수정 가이드. 반려·차단 사유 입력과 최소 길이 검증을 다룰 때 사용.
---

# ReasonPrompt

## 대상

- `src/shared/ui/reason-prompt/reason-prompt.tsx`
- `src/shared/ui/reason-prompt/reason-prompt-host.tsx`
- `src/shared/ui/reason-prompt/reason-prompt.css`
- `src/shared/ui/reason-prompt/index.ts`

## 계약

`modal`(`CustomModal`)을 감싸 사유 입력 폼을 구성한다. **명명 내보내기 `ReasonPrompt`다.**

| prop | 설명 |
| --- | --- |
| `open`, `onClose` | 모달 열기·닫기 |
| `title`, `placeholder`, `submitLabel`, `cancelLabel` | 문구. 컴포넌트에 하드코딩되어 있지 않다 |
| `value`, `onChange` | 제어 입력. 소비처가 상태를 보관한다 |
| `onSubmit` | 제출 콜백 |
| `validation` | `{ minLength?: number; maxLength?: number }` |

검증 규칙은 다음과 같다.

- `minLength` 기본값은 `1`이다. `value.trim().length`가 미만이면 제출 버튼이 비활성이다. **공백만 입력하면 제출할 수 없다.**
- `maxLength`는 `textarea`의 `maxLength`로 전달된다. 초과 입력 자체가 막힌다.
- 입력은 `textarea` `rows={5}` 고정이다. 공용 `text-area` 컴포넌트를 쓰지 않는다.

## 사용 기준

- 반려·차단·회수처럼 사유가 필요한 액션에 사용한다.
- 문구는 모두 prop으로 전달한다. 화면마다 다른 문구를 컴포넌트에 넣지 않는다.
- 제출 후 상태 초기화와 모달 닫기는 소비처가 수행한다.

## 수정 규칙

- 제출 비활성 판정에 `trim()`이 포함된다. 제거하면 공백 사유가 통과한다.
- `reason-prompt__*` BEM 클래스는 CSS 계약이다. 이름을 바꾸지 않는다.
- 내부 `textarea`를 공용 `text-area`로 교체하는 변경은 스타일 계약이 달라지므로 사용자 승인을 받는다.
- 기본 내보내기로 바꾸지 않는다. 명명 내보내기다.
