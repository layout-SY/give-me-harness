---
name: component-no-results
description: synthoria-admin-ui의 NoResults 컴포넌트 사용 가이드. 목록 조회 결과가 없을 때 빈 상태를 표시해야 하는 요구사항에서 사용.
---

# No Results Component

## 대상
- `src/components/no-results/no-results.tsx`

## 언제 선택하나
- 테이블/리스트 결과가 비어 있을 때 공통 빈 상태를 제공해야 할 때

## 사용 핵심
- `rows.length === 0` 같은 조건에서 렌더한다.
- 로딩 상태와 충돌하지 않도록 `!isLoading` 조건과 함께 사용한다.

## 주의
- 빈 상태 문구는 한글로 직접 작성한다.
