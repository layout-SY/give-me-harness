# 로그인 기능 최종 요약

## 완료

- auth 요청·응답 DTO와 Zod parser
- `VITE_API_BASE_URL_DEV` 기반 auth Axios client
- access token 저장과 `/login?access-token=<실제값>` replace navigation mutation hook
- auth route 상수와 Vite 환경 타입
- 공용 input·button 기반 임시 로그인 form과 `/login` route
- 실제 응답에서 생략되는 profile 필드를 허용하는 Zod 계약
- API, hook, form handler 및 route 테스트

## 검증

- 테스트 17개 통과
- auth 의존 그래프 strict TypeScript 검증 통과
- auth 대상 ESLint 통과
- production build 통과
- 전체 lint 통과

## 대기

현재 `/login`은 임시 테스트 페이지다. Production 로그인 UI가 준비되면 최신 파일을 다시 읽고 route element를 교체해야 한다. Query를 수신한 뒤 access token 노출 시간을 줄이기 위한 URL 정리 정책도 production UI 계약에서 확정해야 한다.
