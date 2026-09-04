---
name: component-icon-button
description: {{PROJECT_NAME}}의 아이콘 전용 버튼(src/shared/ui/icon-button) 사용 및 수정 가이드. 아이콘만 노출하는 액션과 접근성 라벨을 다룰 때 사용.
---

# IconButton

## 대상

- `src/shared/ui/icon-button/icon-button.tsx`

## 계약

`@heroui/react`의 `Button`을 `isIconOnly`로 감싼 래퍼다.

| prop | 기본값 | 설명 |
| --- | --- | --- |
| `disabled` | `false` | HeroUI `isDisabled`로 전달된다 |
| `type` | `"button"` | `button \| submit \| reset` |
| `title` | 없음 | `aria-label`로 전달된다 |
| `className` | 없음 | variant 매핑 키다 |
| `onClick` | 없음 | HeroUI `onPress`로 감싸 전달된다 |

variant 매핑은 `primary`, `primary-light`, `secondary`, `ghost`, `danger`를 받고 `primary-light`는 `secondary`로 매핑된다. 매핑에 없으면 `secondary`가 기본이다. `button`과 달리 기본 variant가 `secondary`이고 `isLoading`과 `fullWidth`가 없다.

## 사용 기준

- 아이콘만 표시하는 액션에 사용한다. 문구가 함께 있으면 `button`을 사용한다.
- 화면에 텍스트가 없으므로 `title`을 반드시 전달한다. 접근성 라벨의 유일한 출처다.

## 수정 규칙

- `isIconOnly` 전제를 바꾸지 않는다.
- `button`과 variant 매핑 표가 다르다. 한쪽을 고칠 때 다른 쪽을 자동으로 맞추지 않는다.
- 로딩 상태가 필요하면 임의로 추가하지 말고 사용자에게 요청한다.
