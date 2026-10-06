---
name: reference-ui-trend-badge
description: 지표의 증감 추이(전주 대비 +12.5% 등)를 표시할 때 공용 TrendBadge를 사용하는 규칙과 계약
---

# 증감 추이 뱃지(TrendBadge) 사용 규칙

> 세션 초안 — 사용자 요청("증가 추이 UI(12.5%/5.2%)를 별도 공용 뱃지로 빼고 중앙 정책 스킬화 문서로 반영")에 따라 작성. 중앙 등록 전.

## 규칙

- 매출·판매량·주문 수 등 **이전 기간 대비 증감**을 보여줄 때는 화면에서 새 뱃지를 만들지 말고 `src/shared/ui/trend-badge/trend-badge.tsx`의 `TrendBadge`를 사용한다.
- 증감 방향은 값의 **부호**로만 결정한다. 양수 = 증가(초록, ↗), 음수 = 감소(빨강, ↘), 0 = 변동 없음(회색, —). 화면에서 색·아이콘을 따로 지정하지 않는다.
- 값은 절댓값으로 표시하고 방향은 아이콘·색·접근성 이름으로 전달한다. `+`/`-` 기호를 문자열로 붙이지 않는다.
- 증감률 계산은 Logic(controller·mapper) 책임이다. 뱃지에는 계산된 숫자(예: `12.5`, `-2.1`)만 전달한다.
- 비율 지표의 포인트 차이(반품률 -0.5%p 등)는 `unit="%p"`를 쓴다.
- 비교 기준 문구(예: "전주 대비")는 `comparisonLabel`로 넘겨 스크린리더 이름에 포함한다. 화면에 문구도 보이려면 뱃지 옆에 텍스트를 둔다(EC에서는 `widgets/ec-seller/ui/ec-trend-caption.tsx`).
- 증감값이 없으면(`null`) 뱃지를 렌더링하지 않는다. `0%`로 대체하지 않는다.

## 공개 계약

| prop | 타입 | 기본값 | 설명 |
| --- | --- | --- | --- |
| `value` | `number` | 필수 | 부호 포함 증감 값 |
| `unit` | `"%" \| "%p"` | `"%"` | 표시 단위 |
| `fractionDigits` | `number` | `1` | 소수점 자릿수 |
| `comparisonLabel` | `string` | - | 비교 기준(접근성 이름에 포함) |
| `className` | `string` | - | 배치용 클래스 |

- 접근성: `role="img"` + `aria-label="전주 대비 12.5% 증가"` 형태. 내부 아이콘·숫자는 `aria-hidden`.
- 아이콘: `~/shared/assets/icons/line-icons`의 `TrendingUp/TrendingDown/Minus` 어댑터.

## 사용 예시

```tsx
import TrendBadge from "~/shared/ui/trend-badge/trend-badge";

<TrendBadge value={12.5} comparisonLabel="전주 대비" />
<TrendBadge value={-0.5} unit="%p" comparisonLabel="전월 대비" />
```

KPI 카드에서는 `KpiCard`의 `trend`(헤더 우측) 또는 `caption`(하단) 슬롯에 넣는다.

## 적용 현황과 등록

- 적용: EC 매출 분석(결제 확정 매출·누적 판매량), 매출 현황, 누적 매출 요약 (`feature/ec-seller-ui`).
- 대상 중앙 경로(제안): `policy/common/skills/reference/ui/trend-badge/SKILL.md` — 중앙 저장소 구조에 맞춰 조정 필요.
- 상태: 미등록 — 중앙 저장소 작업으로 인계. 중앙 등록 후 새 inject 세션부터 적용.
