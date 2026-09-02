# 탐색

## 결론

- Dashboard page는 `CP_DASHBOARD_OVERVIEW_FIXTURE`를 직접 사용하고 새로고침 버튼에는 동작이 없었다.
- `cpDashboardApi.getOverview()` 골격은 존재했지만 레거시 Axios payload 반환 방식이며 소비자가 없었다.
- 공용 `ApiClient`, `ApiResult`, `CustomException`, 인증 config는 그대로 재사용할 수 있다.
- `toServerResponse`는 envelope만 정규화하므로 `data` 내부에는 별도 Zod parser가 필요하다.
- 공용 `Button`은 `isLoading`, `disabled`, `onClick`을 지원하고 `Loading`은 조건부 렌더링으로 재사용할 수 있다.
- 개발 MSW는 미처리 요청을 bypass하므로 `/v1/cp/dashboard/overview` handler 등록이 필수다.

## user-ui 교차 분석

- `asan-metaverse-user-ui`는 동일한 `ApiClient/ApiResult` 위에 TanStack Query v5, 계층형 query key, AbortSignal, Zod parser, 최소 invalidation을 적용한다.
- query hook은 `useApi`로 다시 감싸지 않고 `ApiResult unwrap → parser` 순서를 사용한다.
- 관리자 프로젝트에는 TanStack Query와 Zod가 없었으므로 CP 도메인 수직 슬라이스에 한해 도입한다.

## 재사용 결정

- 기존 비 CP 화면의 `useApi`와 `useFetchAdapter`는 변경하지 않는다.
- 중앙 API registry를 새로 만들지 않고 entity의 `api/index.ts` wiring을 유지한다.
- fixture는 MSW handler의 초기 데이터로만 남기고 page/component에서는 import하지 않는다.
