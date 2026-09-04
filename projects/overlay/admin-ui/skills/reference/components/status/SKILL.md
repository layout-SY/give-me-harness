---
name: component-status-badge
description: {{PROJECT_NAME}}의 상태 배지(src/shared/ui/status) 사용 및 수정 가이드. 상태 코드 색상 매핑과 도메인 무지 유지 규칙을 다룰 때 사용.
---

# StatusBadge

## 대상

- `src/shared/ui/status/status-badge.tsx`
- `src/shared/ui/status/status-badge.css`
- `src/shared/ui/status/types`

**명명 내보내기 `StatusBadge`다.**

## 계약

`@heroui/react`의 `Chip`을 감싼 배지다.

| prop | 기본값 | 설명 |
| --- | --- | --- |
| `label` | 필수 | 화면에 보이는 문구. 상태 코드가 아니다 |
| `status` | 없음 | 상태 코드. 없거나 falsy면 **`-`만 렌더링한다** |
| `color` | 없음 | 기본 매핑 대신 호출부가 색을 지정한다 |
| `variant` | `"default"` | `compact`면 `Chip` size가 `sm` |
| `className` | 없음 | `status-badge`에 이어 붙는다 |

색 결정은 2단계다.

1. 의미 색 `StatusBadgeColor` = `positive | neutral | warning | danger | info | deleted`
2. `CHIP_COLOR_MAP`으로 HeroUI 팔레트(`success`/`default`/`warning`/`danger`/`accent`)에 매핑

`color`를 주지 않으면 `resolveDefaultColor`가 상태 코드로 추정한다. 코드는 대문자로 정규화된다.

- `positive`: `ACTIVE`, `PASSED`, `EXECUTED`, `RESOLVED`, `APPROVE`, `HOLD`
- `neutral`: `PENDING`, `PENDING_REVIEW`, `HIDDEN`, `CLOSED`, 그리고 미등록 코드 전부
- `info`: `FINALIZING`, `OPEN`
- `warning`: `REPORTED`
- `danger`: `REJECT`, `REJECTED`, `REJECTED_ADMIN`, `REJECTED_ABUSIVE`, `CANCELED`, `NONE`, `EXECUTE_FAILED`, `REVOKED`, `LOCKED`, `SUSPENDED`
- `deleted`: `DELETED`

`data-status`와 `data-color` 속성이 붙어 CSS와 테스트에서 사용할 수 있다. `title`에는 정규화된 코드가 들어간다.

## 사용 기준

- 상태 표시는 이 컴포넌트를 재사용한다. 표에서는 `table`의 셀에 넣는다.
- **`label`은 반드시 사용자에게 보일 문구를 넣는다.** 상태 코드를 그대로 넣지 않는다.
- 기본 매핑이 도메인 의미와 다르면 `color`를 명시한다. `shared`의 도메인 무지를 유지하기 위한 장치다.
- 미등록 코드는 조용히 `neutral`이 된다. 새 코드 도입 시 색을 확인한다.

## 수정 규칙

- `resolveDefaultColor`에 도메인 코드를 계속 추가하면 `shared`가 도메인을 알게 된다. 새 코드는 가급적 호출부에서 `color`로 지정한다.
- 의미 색과 HeroUI 팔레트를 분리한 2단계 매핑을 하나로 합치지 않는다.
- `status`가 없을 때 `-`를 반환하는 계약을 바꾸면 표 정렬이 흔들린다.
- `data-status`·`data-color`는 CSS 계약이다. 제거하지 않는다.
