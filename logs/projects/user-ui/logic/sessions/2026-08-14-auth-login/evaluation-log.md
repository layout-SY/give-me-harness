# 로그인 기능 장기 평가

## 결론

현재 auth 전용 경계는 기존 API envelope와 다른 로그인 계약을 안전하게 격리한다. 추가 auth endpoint가 같은 envelope를 사용하기 전에는 공용 추상화를 만들지 않는다.

## 후속 고려

- 로그인 외 auth endpoint가 추가될 때 auth Axios instance 재사용 범위를 재평가한다.
- Refresh token 저장·갱신 정책은 명시적인 제품 요구가 생길 때 별도 설계한다.
- Access token query는 브라우저 기록, 로그, 리퍼러 노출 위험이 있으므로 수신 측이 token을 소비한 직후 query를 제거하는 정책을 production UI 계약에서 확정한다.
- `src/features/auth/testing/LoginTestPage.tsx`는 임시 검증 surface이므로 production 로그인 UI가 준비되면 삭제하고 route element를 교체한다.
- 로그인 응답의 optional profile 필드를 실제로 소비하게 되면 누락 상태 처리 정책을 해당 소비자에서 명시해야 한다.
