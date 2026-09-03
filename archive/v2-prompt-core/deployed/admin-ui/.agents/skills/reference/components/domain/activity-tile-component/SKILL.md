---
name: domain-component-activity-tile
description: Activity 도메인 TileComponent 사용 가이드. 맵 타일 이미지 로딩/오류 표시가 필요한 요구사항에서 사용.
---

# Activity TileComponent

## 대상
- `src/pages/activity/components/tile.component.tsx`

## 언제 선택하나
- 맵 타일을 좌표 기반으로 렌더하고 preload 캐시를 활용해야 할 때

## 사용 핵심
- `tile`(x, y, src)와 `preloadImage`를 전달한다.
- 로딩/에러 상태 클래스(`loaded`, `loading`, `error`)를 유지한다.

## 주의
- 오류 표시 텍스트/스타일은 Activity 화면 컨텍스트에 맞게 최소한으로 보강한다.
