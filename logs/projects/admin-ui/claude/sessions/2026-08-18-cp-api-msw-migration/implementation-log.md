# 구현 로그

## MSW 부트스트랩

- 개발 의존성으로 MSW를 추가하고 `public/mockServiceWorker.js`를 생성했다.
- React 렌더 전에 개발 환경 worker가 준비되도록 `src/app/index.tsx`를 구성했다.
- 미전환 API는 기존 네트워크 동작을 유지하도록 unhandled request를 bypass한다.

## CP Dashboard 수직 슬라이스

- `@tanstack/react-query`, `zod`와 전역 `QueryClientProvider`를 추가했다.
- query 기본값은 조회 `retry: 1`, `staleTime: 30초`, mutation `retry: 0`으로 구성했다.
- Dashboard 응답 DTO·Zod schema/parser와 typed `ApiClient` repository를 추가했다.
- TanStack Query의 `AbortSignal`이 Axios config까지 전달되도록 공용 helper를 추가했다.
- `ApiResult` 실패를 `CustomException`으로 전환하는 공용 unwrap helper를 추가했다.
- Dashboard query key와 `useCpDashboardOverviewQuery`를 추가했다.
- `/v1/cp/dashboard/overview` MSW handler가 기존 fixture를 `ServerResponse` envelope로 반환하도록 구성했다.
- Dashboard page는 query 데이터를 렌더링하고 `refetch`, loading, 오류 Dialog를 surface에서 처리한다.
- 최초 조회 실패 시에도 오류 Dialog와 재시도 버튼을 남기고, refetch 실패 시에는 기존 캐시 데이터를 유지한다.
- 정상적인 Axios 요청 취소가 콘솔 오류로 기록되지 않도록 response interceptor의 취소 분기를 보완했다.
- `recipe-api-authoring`, `policy-tanstack-query`와 관련 인덱스·data-fetch 연결 규칙을 추가했다.
