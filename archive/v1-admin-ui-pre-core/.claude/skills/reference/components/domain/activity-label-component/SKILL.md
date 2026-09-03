---
name: domain-component-activity-label
description: Activity 도메인 LabelComponent 사용 가이드. 맵 위치 라벨(라이트/다크 스타일) 표시 요구사항에서 사용.
---

# Activity LabelComponent

## 대상
- `src/pages/activity/components/label.component.tsx`

## 언제 선택하나
- 맵 위치명/영역명을 좌표 기반으로 노출할 때

## 사용 핵심
- `label`(x, y, label), `show`, `style("light" | "dark" | "")`를 전달한다.
- 위치 계산은 상위(Activity)에서 수행한다.

## 주의
- 지도 타입별 라벨 스타일 매핑은 상위에서 일관되게 유지한다.
