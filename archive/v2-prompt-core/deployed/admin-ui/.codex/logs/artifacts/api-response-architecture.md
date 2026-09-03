# Artifact Log — API Response Architecture

## 신규/변경 자산
- `src/apis/api-client.ts`
  - axios instance와 도메인 API 사이의 typed client.
  - `ServerResponse<TData>`를 unwrap해 `Promise<TData>`를 반환.

- `src/apis/common/api-result/server-response.unwrap.ts`
  - `ServerResponse<TData>` 성공 응답은 `TData`로 반환.
  - 실패 응답은 `CustomException`으로 throw.

## 기존 자산 재사용
- `toServerResponse`
- `toApiError`
- `CustomException`
- `useApi.execute`

## 아키텍처 패턴
- Result 모델(`ApiResult<T>`)에서 exception flow(`Promise<T> + throw`)로 점진 전환.
- 에러 객체 생성은 infra/common 계층, 에러 표시와 UI side effect는 hook/page 계층에 둔다.
