---
name: hook-use-api
description: synthoria-admin-ui의 useApi 훅(src/shared/lib/hooks/use-api.tsx) 사용 가이드. API 호출을 실행하면서 자동 취소/로딩/에러 Dialog 처리를 표준화할 때 사용.
---

# useApi Hook

## 대상

- `src/shared/lib/hooks/use-api.tsx`

## 언제 선택하나

- 컴포넌트/모달/훅에서 `src/apis`의 API 메서드를 호출할 때 **항상 선택한다**.
- `api` 모듈을 직접 import 하는 대신 `useApi().api`로 주입받는다.

## 사용 핵심

- 반환값: `{ api, execute, isLoading }`
  - `api`: 도메인 집계 객체 (`api.users`, `api.items`, ...)
  - `execute<T>(apiCall, options)`: 실제 호출 실행기
  - `isLoading`: 호출 진행 여부 (훅 인스턴스 단위)
- `options`:
  - `onSuccess(data)` / `onError(err)` / `silent`(true면 기본 alert 스킵)
- 기본 에러 UX: `onError` 미지정 + `silent !== true`면 `Dialog.alert`로 자동 표시
- 언마운트 시 진행 중인 요청은 AbortController로 취소됨

## 호출 예시

```ts
const { api, execute, isLoading } = useApi();

await execute(() => api.users.getUsers(queryState), {
  onSuccess: (data) => setRows(data.content),
});
```

## 주의

- 현재 `execute`는 AbortController를 만들지만 `apiCall`에 `signal`을 넘기지 않는다.
  - 실제 네트워크 취소가 필요한 경우 도메인 API 레이어에서 `signal`을 받도록 별도 설계가 필요하다.
- `onError`를 지정하면 기본 Dialog는 뜨지 않는다. 사용자 노출 에러 UX를 직접 관리할 때만 사용한다.
- `silent: true`는 리프레시 토큰처럼 사용자에게 알리지 않아야 하는 백그라운드 호출에만 사용한다.
- `isLoading`은 같은 `useApi()` 인스턴스 내 호출에 대해 전역적으로 토글된다. 여러 호출을 한 컴포넌트에서 독립적으로 관리하려면 로컬 `isLoading` state를 병행한다.
