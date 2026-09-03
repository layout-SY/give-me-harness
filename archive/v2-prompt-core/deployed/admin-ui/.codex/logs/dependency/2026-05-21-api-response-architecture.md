# Dependency Log — API Response Architecture

## 결정
- `ServerResponse<TData>` 해석 책임은 도메인 API가 아니라 공통 API client 계층에 둔다.
- 도메인 API는 endpoint, params, payload, 도메인 DTO 반환 타입만 관리한다.
- hook/page는 `ApiResult<T>` 분기가 아니라 `useApi.execute()`의 성공/실패 흐름으로 UI side effect를 제어한다.

## 의존 방향
```text
axiosInstance
  -> apiClient
  -> common api-result unwrap/error mapper
  -> domain api
  -> useApi.execute
  -> hook/page
```

## 금지 의존
- `domain api -> ServerResponse`
- `domain api -> toApiResult`
- `axios interceptor -> Dialog/UI`

## 적용 범위
- 1차 적용: DAO discussion API 및 관련 hook/page
- 후속 적용: 도메인 단위로 순차 전환
