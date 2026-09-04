---
name: component-button
description: {{PROJECT_NAME}}의 공용 Button 컴포넌트(src/shared/ui/button) 사용 및 수정 가이드. 액션 버튼, 로딩 상태와 variant 매핑을 다룰 때 사용.
---

# Button

## 대상

- `src/shared/ui/button/button.tsx`

전용 CSS 파일은 없다. 시각 표현은 HeroUI variant와 전역 토큰이 담당한다.

## 계약

`@heroui/react`의 `Button`을 감싼 래퍼다.

| prop | 기본값 | 설명 |
| --- | --- | --- |
| `isLoading` | `false` | HeroUI `isPending`으로 전달된다 |
| `disabled` | `false` | HeroUI `isDisabled`로 전달된다 |
| `type` | `"button"` | `button \| submit \| reset` |
| `title` | 없음 | `aria-label`로 전달된다 |
| `className` | 없음 | 시맨틱 토큰이자 variant 결정 키다 |
| `fullWidth` | `true` | 기본이 전체 너비다 |
| `onClick` | 없음 | HeroUI `onPress`로 감싸 전달된다 |

`className`은 스타일 문자열이 아니라 variant 매핑 키로 쓰인다. `primary`, `secondary`, `outline`, `cancel`, `ghost`, `danger`를 받으며 `cancel`은 `secondary` variant로 매핑된다. 매핑에 없는 값이면 variant는 `primary`가 된다.

## 사용 기준

- 페이지 액션 버튼은 이 컴포넌트를 먼저 재사용한다.
- 로딩 상태는 자체 스피너를 얹지 말고 `isLoading`을 사용한다.
- 아이콘만 있는 버튼은 `icon-button`을 사용한다.
- 버튼 문구는 하드코딩하지 않고 다국어 키를 사용한다.

## 수정 규칙

- `className` 시맨틱 토큰 계약과 `CLASSNAME_VARIANT_MAP`을 깨지 않는다.
- `onClick`은 인자 없는 콜백 계약을 유지한다. HeroUI `onPress` 이벤트 객체를 그대로 노출하지 않는다.
- `fullWidth` 기본값이 `true`라는 점을 전제로 하는 소비처가 있다. 기본값을 바꾸지 않는다.
- 새 variant가 필요하면 임의 확장하지 말고 사용자에게 요청한다.
