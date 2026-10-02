---
name: reference-admin-trend-badge
description: admin-ui의 지표 증감 표시에서 공용 TrendBadge의 부호·단위·접근성 계약을 재사용할 때 사용한다.
---

# 증감 뱃지

적용 프로젝트는 `asan-metaverse-admin-ui`다. `asan-metaverse-user-ui`에 같은 자산이 존재한다는 계약이 아니다.

2026-10-02 `feature/ec-seller-ui`의 `src/shared/ui/trend-badge/trend-badge.tsx`와 CSS, `widgets/ec-seller/ui/ec-trend-caption.tsx`를 재확인했다. 자산은 판매자 브랜치의 `b6fc92d2eed80a4920cc4681bda7f44a3565a8f5`에 커밋됐다. 사용 전 현재 worktree의 파일·계약을 확인한다. 카탈로그 등록 자체가 다른 브랜치에 컴포넌트를 배포하지 않는다.

## 계약

| prop | 타입·기본값 | 의미 |
| --- | --- | --- |
| `value` | `number`, 필수 | 부호를 포함한 증감 값 |
| `unit` | `"%" \| "%p"`, `"%"` | 증감률 또는 비율의 포인트 차이 |
| `fractionDigits` | `number`, `1` | `toFixed`에 전달하는 소수 자릿수 |
| `comparisonLabel` | `string`, 선택 | 접근성 이름의 비교 기준 |
| `className` | `string`, 선택 | 배치 클래스 |

- 방향 prop은 없다. 양수는 초록·상승 화살표, 음수는 빨강·하락 화살표, 0은 회색·가로선이다. 화면 숫자는 절댓값이며 별도 `+`·`-` 문자열이나 색·아이콘을 합성하지 않는다.
- 이 색 계약은 상승을 긍정으로 표시하므로 비용·반품률처럼 증가의 평가가 다른 지표에 적용하기 전 요구를 확인한다.
- 계산·DTO 매핑은 Logic/controller가 맡는다. `null`이면 호출부에서 렌더링하지 않는다. 컴포넌트 자체는 `null`·비유한 수 방어를 제공하지 않는다. `fractionDigits`는 유효한 `toFixed` 범위로 전달한다.
- `%p`는 비율 간 포인트 차이일 때 명시한다.
- `role="img"`와 `aria-label`로 비교 기준·절댓값·방향을 읽는다. 0이면 비교 기준과 “변동 없음”을 읽는다. 내부 아이콘·숫자는 `aria-hidden`이다. 비교 문구를 화면에도 보여주려면 `EcTrendCaption`처럼 옆에 배치한다.
- 아이콘은 `shared/assets/icons/line-icons.ts`, 색은 기존 CSS 토큰을 사용한다.

```tsx
import TrendBadge from "~/shared/ui/trend-badge/trend-badge";

<TrendBadge value={12.5} comparisonLabel="전주 대비" />
<TrendBadge value={-0.5} unit="%p" comparisonLabel="전월 대비" />
```

`KpiCard.caption`을 사용할 수 있다. 판매자 작업 브랜치에서는 `trend` 헤더 슬롯도 추가됐으므로 실제 카드 계약을 확인한다. 기존 브랜치에도 슬롯이 있다고 가정하지 않는다.
