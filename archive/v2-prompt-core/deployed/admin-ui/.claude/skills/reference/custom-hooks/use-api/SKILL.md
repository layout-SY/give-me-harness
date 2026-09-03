---
name: hook-use-api
description: synthoria-admin-ui의 useApi 훅(src/hooks/use-api.tsx) 사용 가이드. ApiResult 정식 계약을 통해 성공/실패/취소를 값으로 분기하고, race 가드·unmount cleanup·실패 Dialog 정책을 표준화할 때 사용.
---

# useApi Hook

## 대상

- `src/hooks/use-api.tsx`

## 언제 선택하나

- 컴포넌트/모달/훅에서 `src/apis`의 API 메서드를 호출할 때 **항상 선택한다**.
- `api` 모듈을 직접 import 하는 대신 `useApi().api`로 주입받는다.

## 책임 (4계층 모델 중 "요청 단위 라이프사이클 + 결과 어댑터")

- 모든 결과를 호출부가 값으로 분기 가능한 형태로 노출 (`ApiResult` discriminated union)
- isLoading, race 가드(seqRef), unmount cleanup
- 실패 시 자동 Dialog 정책 (silent opt-in)

## 반환값

```ts
const { api, execute, isLoading } = useApi();
```

- `api`: 도메인 집계 객체 (`api.users`, `api.dao`, ...)
- `execute<T>(apiCall, options?)`: 실제 호출 실행기 — **오버로드 2종**
- `isLoading`: 호출 진행 여부 (훅 인스턴스 단위, 마지막 호출만 추적)

## `execute` 시그니처 (오버로드)

```ts
// 신규 계약 (api.ts가 ApiResult를 반환할 때 — 권장)
execute<T>(apiCall: () => Promise<ApiResult<T>>, options?): Promise<ApiResult<T> | { canceled: true }>

// 레거시 (throw 기반 호출부 호환 — PR-8에서 제거 예정)
execute<T>(apiCall: () => Promise<T>, options?): Promise<T | undefined>
```

### options

```ts
type ApiCallOptions<T> = {
  onSuccess?: (data: T) => void;
  onError?: (error: ApiError | unknown) => void;
  silent?: boolean;  // 기본 true (자동 Dialog 안 함). 자동 Dialog 원하면 false 명시.
};
```

## 사용 패턴

### 정식 패턴 (반환값 분기)

```ts
const { api, execute } = useApi();

const result = await execute(() => api.dao.getDaoProposalDiscussionPostDetail(postId), { silent: false });
if ("canceled" in result) return;       // race/unmount로 폐기
if (!result.success) return;            // 실패 — useApi가 silent:false로 자동 Dialog 처리
setFetchedData(result.data);            // 성공
```

### silent 정책

- 기본 `silent: true` — 자동 Dialog 안 뜸. 정식 흐름은 반환값으로 분기.
- 사용자에게 실패를 자동 알리고 싶으면 `silent: false` 명시.
- `onError` 콜백을 주면 silent 정책과 무관하게 콜백이 우선.
- 셋 다 없으면 dev 환경에서 `console.warn`으로 누락 감지.

### 콜백 사용은 부가물

- `onSuccess`/`onError`는 하위 호환 부가물. 다단 시퀀스(성공해야 모달 닫고 refresh 등)는 반환값 분기로 표현하는 것이 가독성·합성성에서 유리.

## 라이프사이클 보장

### Race 가드
- 같은 hook 인스턴스에서 빠른 연속 호출 시 늦게 도착한 응답은 `{ canceled: true }` 반환.
- `isLoading=false`는 마지막 호출에 한해서만 적용 (loading 깜빡임 방지).

### Unmount cleanup
- 컴포넌트 unmount 시 `AbortController.abort()` 호출.
- unmount 이후 도달한 응답도 `{ canceled: true }`로 처리되어 setState 폭주 방지.

### 주의
- 현재 `execute`는 AbortController를 만들지만 `apiCall`에 `signal`을 자동 전달하지 않는다.
- 실제 네트워크 취소가 필요하면 도메인 API 레이어에서 `signal`을 받도록 별도 설계 필요.

## 안티패턴

### ❌ throw에 의존
```ts
try {
  await execute(() => api.x.create(payload));
  Dialog.alert("success");
} catch { /* never reached — silent: true에서는 throw 안 함 */ }
```

### ❌ undefined 반환을 실패로 해석 (레거시 경로)
```ts
const data = await execute(() => api.legacy.x(), { silent: false });
if (!data) { /* 취소인지 실패인지 구분 불가 */ }
```
→ 신규 계약(ApiResult 반환)으로 마이그레이션 필요.

### ❌ useApi 우회한 직접 호출
```ts
import api from "~/apis";
const result = await api.x.delete(id);  // race/loading/dialog 모두 잃음
```

## 관련 정책

- [policy/data-fetch-layer/SKILL.md](../../../policy/data-fetch-layer/SKILL.md) — useApi가 속한 4계층 모델 전체
- 호출부가 fetch hook(도메인 facade)인지 modal hook(surface)인지에 따라 alert/pubsub 책임이 달라짐 — 위 정책 참조
