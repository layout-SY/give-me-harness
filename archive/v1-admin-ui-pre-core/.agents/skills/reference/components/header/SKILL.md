---
name: component-header
description: synthoria-admin-ui의 Header 컴포넌트 사용 가이드. 상단 브랜드/언어 전환/로그아웃 액션 요구사항에서 사용.
---

# Header Component

## 대상
- `src/widgets/app-header/ui/header.tsx`

## 언제 선택하나
- 전역 헤더 동작(언어 변경, 로그아웃, 홈 이동)을 수정/확장할 때

## 사용 핵심
- 언어 전환은 `useLanguage().setLanguage`로 처리한다.
- 인증 상태 분기(`authAtom`) 패턴을 유지한다.

## 주의
- 헤더 액션 변경은 전체 앱 UX에 영향이 크므로 이벤트/라우팅 동작을 함께 검증한다.
