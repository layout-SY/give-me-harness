---
name: hook-use-api
description: {{PROJECT_NAME}}의 useApi 훅(src/shared/lib/hooks/use-api.tsx) 사용 및 수정 가이드. ApiResult 계약, race 가드, unmount 취소와 실패 처리 정책을 다룰 때 사용.
---

# useApi

## 대상

- `src/shared/lib/hooks/use-api.tsx`
- `src/shared/api/common/api-result.ts` (`ApiResult`, `ApiError` 타입)

## 계약

```ts
const { execute, isLoading } = useApi();
```

**반환값은 `execute`와 `isLoading` 두 개뿐이다.** 도메인 API 집계 객체는 없다. API 함수는 소비처가 직접 import한다.

`execute`는 오버로드된 함수다.

- `apiCall`이 `Promise<ApiResult<T>>`를 반환하면 결과는 `ApiResult<T> | { canceled: true }`다.
- 그 외에는 `T | undefined`다.

옵션은 `{ onSuccess?, onError?, silent? }`이며 **`silent` 기본값은 `true`다.**

실패 처리 순서는 다음과 같다.

1. `onError`가 있으면 그것만 호출한다.
2. 없고 `silent`가 `false`면 `Dialog.alert`로 메시지를 표시한다.
3. 없고 `silent`가 기본값 `true`면 **아무 UI도 뜨지 않는다.** 개발 환경에서만 `console.warn`으로 경고한다.

즉 실패를 사용자에게 알리려면 `onError`를 주거나 `silent: false`를 명시하거나 반환된 `ApiResult`를 직접 분기해야 한다.

race·수명 관리는 다음과 같다.

- 호출마다 `seqRef`를 증가시켜 **마지막 호출만 반영한다.** 뒤늦게 도착한 이전 응답은 `ApiResult` 경로에서 `{ canceled: true }`를 반환하고 콜백을 호출하지 않는다.
- 언마운트 시 등록된 모든 `AbortController`를 `abort`한다.
- axios cancel과 `AbortError`는 실패로 처리하지 않고 `undefined`를 반환한다.
- `isLoading`은 최신 호출일 때만 해제된다.

## 사용 기준

- 화면에서 API를 호출할 때 이 훅을 거친다. 컴포넌트에서 axios를 직접 쓰지 않는다.
- 실패를 사용자에게 보여야 하면 `silent: false` 또는 `onError`를 명시한다. 기본값에 기대지 않는다.
- `ApiResult` 계약 API는 반환값을 분기해 성공·실패를 값으로 다룬다.
- 검색어 입력처럼 연속 호출되는 화면은 race 가드가 이미 있으므로 별도 디바운스 취소 로직을 중복 구현하지 않는다.
- `{ canceled: true }`는 실패가 아니다. 오류 처리로 분기하지 않는다.

## 수정 규칙

- `silent` 기본값을 바꾸면 모든 호출부의 실패 UX가 한 번에 바뀐다. 사용자 승인 없이 바꾸지 않는다.
- `seqRef` 최신 호출 판정과 `isMountedRef` 검사를 제거하지 않는다. 지난 응답이 화면을 덮어쓴다.
- `finally`에서 최신 호출일 때만 `isLoading`을 내리는 조건을 유지한다.
- `ExecuteFn` 오버로드 순서를 바꾸면 `ApiResult` 계약 호출부의 타입 추론이 깨진다.
