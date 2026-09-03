---
name: component-header
description: synthoria-admin-ui의 Header 컴포넌트 사용 가이드. 상단 브랜드/로그아웃 액션 요구사항에서 사용.
---

# Header Component

## 대상
- `src/components/header/header.tsx`

## 언제 선택하나
- 전역 헤더 동작(로그아웃, 홈 이동)을 수정/확장할 때

## 사용 핵심
- 인증 상태 분기(`authAtom`) 패턴을 유지한다.

## 주의
- 헤더 액션 변경은 전체 앱 UX에 영향이 크므로 이벤트/라우팅 동작을 함께 검증한다.
