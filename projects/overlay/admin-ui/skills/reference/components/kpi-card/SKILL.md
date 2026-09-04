---
name: component-kpi-card
description: {{PROJECT_NAME}}의 KPI 카드(src/shared/ui/kpi-card) 사용 및 수정 가이드. 대시보드 지표 타일과 tone 색상을 다룰 때 사용.
---

# KpiCard

## 대상

- `src/shared/ui/kpi-card/kpi-card.tsx`
- `src/shared/ui/kpi-card/kpi-card.css`

## 계약

HeroUI를 쓰지 않는 단순 표시 컴포넌트다.

| prop | 기본값 | 설명 |
| --- | --- | --- |
| `label` | 필수 | 지표 이름 |
| `value` | 필수 | `ReactNode`. 문자열뿐 아니라 엘리먼트도 넣을 수 있다 |
| `tone` | `"default"` | `default \| info \| positive \| warning \| danger \| accent` |
| `caption` | 없음 | 있을 때만 렌더링된다 |

구조는 `kpi-card > kpi-card__label + kpi-card__value.is-{tone} + kpi-card__caption`이다. tone은 값 요소에만 `is-{tone}` 클래스로 적용된다.

## 사용 기준

- 대시보드 지표 타일에 사용한다. 카드 레이아웃을 새로 만들지 않는다.
- 숫자 포맷(천 단위 구분, 단위 표기)은 소비처가 처리해 `value`로 넘긴다. 컴포넌트는 포맷하지 않는다.
- 증감 화살표 같은 장식이 필요하면 `value`에 엘리먼트로 구성한다.
- `tone`은 `StatusBadge`의 `StatusBadgeColor`와 이름이 겹치지만 **다른 타입이다.** 값을 서로 옮겨 쓰지 않는다.

## 수정 규칙

- `is-{tone}` 클래스 규칙은 CSS 계약이다. tone을 추가하면 CSS도 함께 추가한다.
- `caption` 조건부 렌더링을 항상 렌더링으로 바꾸면 빈 요소가 레이아웃에 영향을 준다.
- 카드 내부에 클릭 동작을 넣지 않는다. 필요하면 소비처가 감싼다.
