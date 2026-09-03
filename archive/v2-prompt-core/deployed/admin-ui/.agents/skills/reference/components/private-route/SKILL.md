---
name: component-private-route
description: synthoria-admin-ui의 PrivateRoute 사용 가이드. 인증된 사용자만 접근 가능한 라우트 요구사항에서 사용.
---

# Private Route Component

## 대상
- `src/app/router/private-route.tsx`

## 언제 선택하나
- 로그인 상태가 아니면 접근 차단/리다이렉트해야 하는 경로일 때

## 사용 핵심
- 라우터 설정에서 보호할 element를 `PrivateRoute`로 감싼다.
- 인증 판단은 기존 auth 상태 흐름(`authAtom`, 토큰 리프레시)과 일치시킨다.

## 주의
- 인증 로직 자체를 이 컴포넌트에 과도하게 추가하지 않는다.
