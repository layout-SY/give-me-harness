---
name: component-category-badge
description: {{PROJECT_NAME}}의 카테고리 배지(src/shared/ui/category) 사용 및 수정 가이드. 카테고리 색상 매핑과 빈 값 처리를 다룰 때 사용.
---

# CategoryBadge

## 대상

- `src/shared/ui/category/category-badge.tsx`
- `src/shared/ui/category/category-badge.css`
- `src/shared/ui/category/types`

**명명 내보내기 `CategoryBadge`다.**

## 계약

`@heroui/react`의 `Chip`을 사용하며 `StatusBadge`와 같은 2단계 색 매핑 구조를 쓴다.

| prop | 설명 |
| --- | --- |
| `category` | 필수. 카테고리 코드 |
| `color` | 기본 매핑 대신 호출부가 지정한다 |
| `label` | 표시 문구. 없으면 **정규화된 코드가 그대로 보인다** |

- `category`가 `undefined`·`null`·공백 문자열이면 **`null`을 반환한다.** `StatusBadge`가 `-`를 렌더링하는 것과 다르다.
- 코드는 trim 후 대문자로 정규화된다.
- 의미 색 `CategoryBadgeColor` = `purple | gray | green | blue`
- 기본 매핑: `ETC` → purple, `BUSINESS` → gray, `ECONOMY` → green, `POLICY` → blue, 그 외 → purple
- HeroUI 팔레트 매핑에서 **`purple`과 `blue`가 모두 `accent`로 간다.** 두 값의 시각 차이는 `category-badge--{color}` 클래스가 만든다.
- `data-category`, `data-color` 속성과 `title`(정규화 코드)이 붙는다.

## 사용 기준

- 카테고리 표시는 이 배지를 재사용한다.
- **사용자에게 보일 문구는 `label`로 넘긴다.** 넘기지 않으면 영문 코드가 그대로 노출된다.
- 기본 매핑이 도메인 의미와 다르면 `color`를 명시한다.
- 빈 값에서 아무것도 렌더링되지 않으므로, 자리 유지가 필요하면 소비처가 대체 요소를 둔다.

## 수정 규칙

- `resolveCategoryColor`에 도메인 코드를 계속 추가하면 `shared`가 도메인을 알게 된다. 새 코드는 호출부에서 `color`로 지정한다.
- `purple`과 `blue`가 같은 Chip color를 쓰므로 CSS 클래스를 제거하면 두 색이 구분되지 않는다.
- 빈 값에서 `null`을 반환하는 계약을 바꾸면 표 레이아웃이 달라진다.
- `StatusBadge`와 구조가 비슷하지만 빈 값 처리와 색 집합이 다르다. 한쪽 변경을 그대로 옮기지 않는다.
