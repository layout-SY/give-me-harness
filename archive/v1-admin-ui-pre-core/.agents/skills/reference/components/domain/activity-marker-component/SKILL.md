---
name: domain-component-activity-marker
description: Activity 도메인 MarkerComponent 사용 가이드. 맵 좌표 기반 사용자 수 마커 표시 요구사항에서 사용.
---

# Activity MarkerComponent

## 대상
- `src/pages/activity/components/marker.component.tsx`

## 언제 선택하나
- 맵 위에 좌표/값 기반 인터랙티브 마커를 표시할 때

## 사용 핵심
- `marker`(x, y, label, value...)와 `show`를 전달한다.
- 클릭/선택 핸들러는 버튼 props로 전달한다.

## 주의
- 줌 레벨/노출 조건은 상위(Activity)에서 계산해 전달한다.
