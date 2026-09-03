# Dependency & Architecture Decision — ApiResult Contract

> 작성일: 2026-05-21
> 도메인: api-result-contract (전 도메인 횡단)

---

## 의존 방향 (레이어 순서)

```
axiosInstance (인프라)
  ↓
common/api-result/* (순수 유틸/타입)
  ↓
api-client.ts (HTTP 클라이언트 추상화)
  ↓
services/*.api.ts (도메인 API)
  ↓
hooks/use-api.tsx (실행 계층)
  ↓
pages/**/*.tsx (UI)
```

## 레이어 간 허용/금지 규칙

| 레이어 | 허용 | 금지 |
|--------|------|------|
| `common/api-result` | 순수 TS 유틸만 | axios, React, CustomException 의존 금지 |
| `api-client.ts` | `common/api-result` 유틸 | `CustomException` throw 금지 (ApiResult로 표현) |
| `services/*.api.ts` | `api-client.ts`, `common/dto` | `useApi` 직접 import 금지 |
| `hooks/use-api.tsx` | 모든 서비스 API | 도메인 비즈니스 로직 포함 금지 |

## 공용화 수준 결정

| 자산 | 수준 | 근거 |
|------|------|------|
| `ApiResult<T>`, `ApiError` | 글로벌 | 전 도메인 반환 계약 |
| `createApiClient` | 글로벌 | 단일 HTTP 클라이언트 추상화 |
| `useApi` | 글로벌 공용 훅 | 전 페이지 사용 |
| `useAsyncTask` | 폐기 | useApi로 통합 |
| 도메인 type guard | 도메인 내부 | `ApiErrorData` 대체 용도 |

## 주요 결정 사항

1. `ApiResult<T>` = 정식 반환 계약. `Promise<T>` 단독 반환은 신규 코드에서 금지.
2. `throw`는 네트워크 오류/취소 등 진짜 예외에만 허용. 비즈니스 실패는 `ApiResult.success:false`.
3. `unwrapServerResponse`는 @deprecated 처리 후 점진 제거.
4. `silent` 기본값: opt-in(true). 자동 오류 다이얼로그는 명시적으로 요청해야 함.
5. race 가드: seq token 발행 방식, 늦은 결과는 `{ canceled: true }` 반환.
