---
name: component-role-based-route
description: synthoria-admin-ui의 RoleBasedRoute 사용 가이드. 권한별 접근 제어가 필요한 라우트 요구사항에서 사용.
---

# Role Based Route Component

## 대상
- `src/app/router/role-based-route.tsx`

## 언제 선택하나
- 특정 관리자 역할에서만 접근 가능한 경로를 구성할 때

## 사용 핵심
- 허용 역할 목록을 명시하고, 미허용 시 fallback 동작을 기존 패턴과 맞춘다.
- 라우터 계층에서 PrivateRoute와 조합 가능 여부를 검토한다.

## 주의
- 권한 코드 상수/enum 변경은 관리자 영역 전체 영향이 있으므로 신중히 반영한다.
