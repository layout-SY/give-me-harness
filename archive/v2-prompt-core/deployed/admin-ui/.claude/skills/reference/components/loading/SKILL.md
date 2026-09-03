---
name: component-loading
description: synthoria-admin-ui의 Loading 컴포넌트 사용 가이드. API 요청/저장/업로드 중 진행 상태 표시가 필요한 요구사항에서 사용.
---

# Loading Component

## 대상
- `src/components/loading/loading.tsx`

## 언제 선택하나
- 비동기 동작 중 사용자에게 대기 상태를 명확히 보여줘야 할 때

## 사용 핵심
- `isLoading` 상태와 조건 렌더를 연결한다.
- 페이지 전체/섹션 단위 중 범위를 명확히 정해 배치한다.

## 주의
- 과도한 중첩 로딩 스피너를 피하고, 가장 큰 컨텍스트 하나를 우선 표시한다.
