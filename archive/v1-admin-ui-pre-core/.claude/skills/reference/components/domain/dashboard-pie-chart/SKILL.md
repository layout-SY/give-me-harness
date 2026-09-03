---
name: domain-component-dashboard-pie-chart
description: Dashboard 도메인 PieChart 사용 가이드. 비율형 지표(디바이스 점유율 등)를 시각화할 때 사용.
---

# Dashboard PieChart

## 대상
- `src/pages/dashboard/components/pie.chart.tsx`

## 언제 선택하나
- 비율 데이터(합계 대비 분포)를 원형 차트로 보여줄 때

## 사용 핵심
- `data: [{ label, value, color }]`를 전달한다.
- 필요 시 `duration`, `animate`를 조정한다.

## 주의
- Canvas 렌더/리사이즈 debounce가 내장되어 있다.
- 색상은 CSS 변수 기반 사용을 권장한다.
