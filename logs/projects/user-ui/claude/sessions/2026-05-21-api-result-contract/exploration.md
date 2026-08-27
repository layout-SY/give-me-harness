# Exploration — ApiResult Contract Migration

> 작성일: 2026-05-21
> 세션: 2026-05-21-api-result-contract

---

## 1. 현재 api-client 레이어 상태

### createApiClient (src/apis/api-client.ts)
- 모든 HTTP 메서드(get/post/patch/delete)가 `unwrapServerResponse`를 호출
- `unwrapServerResponse`는 `success !== true`이면 `throw new CustomException` 발생
- 반환 타입: `Promise<TData>` — 호출부에서 성공/실패 구분 불가

### unwrapServerResponse vs toApiResult (이중 표현형)
- `toApiResult`: `ApiResult<TData>` discriminated union 반환 (throw 없음)
- `unwrapServerResponse`: 실패 시 throw, 성공 시 data 반환
- 두 경로가 `toServerResponse`를 각각 중복 호출하는 구조
- `toApiError`도 내부에서 `toServerResponse`를 재호출 → 3중 정규화

### ApiErrorData 타입
```ts
type ApiErrorData = string | number | boolean | null | ApiErrorData[] | { [key: string]: ApiErrorData };
```
재귀 타입으로 선언. 실제 사용처에서 구체 타입으로 좁히지 않고 `any` cast가 빈번.

---

## 2. useApi 현황 (src/hooks/use-api.tsx)

- `execute` 반환: `Promise<T | undefined>` — 취소/실패 모두 `undefined`로 동일 처리 (silent failure)
- `silent` 기본값 `false` → 오류 시 Dialog.alert 자동 노출 (opt-out 방식)
- `onSuccess`, `onError` 콜백 중심 흐름 — 반환값 기반 흐름 없음
- Race 가드 없음: `controllersRef`는 unmount 정리용 AbortController 집합이나 seq token 미발행
- `isLoading` 상태 관리 내장

### useAsyncTask 현황 (src/hooks/use-async-task/useAsyncTask.ts)
- `runAsyncTask`: try/catch 래퍼, 반환 `T | undefined`
- `isLoading` 상태 내장
- `useDiscussDetailFetch`에서 `execute` 위에 다시 `runAsyncTask`로 중첩 — 이중 로딩 레이어
- useApi 사용 파일: ~85개 (전 도메인 확산)
- useAsyncTask 사용 파일: 2개 (useAsyncTask.ts 자체 + useDiscussDetailFetch.tsx)

---

## 3. 서비스 레이어 패턴 분류

| 패턴 | 파일 예시 | 특징 |
|------|-----------|------|
| createApiClient 적용 (신형) | discussion.api.ts 외 다수 | client.get/post 등, unwrap은 api-client 내부에 은닉 |
| 구형 직접 instance 호출 | users.api.ts, videos.api.ts 등 | `instance.get` 직접 + 수동 `resData.data` 추출 또는 any 캐스팅 |

- DAO/discussion: `createApiClient` 적용 완료 (신형)
- users, videos, usage: 구형 패턴 잔존

---

## 4. 파일럿 대상: useDiscussDetailFetch.tsx

현재 문제점:
1. `useAsyncTask` + `useApi.execute` 이중 레이어 — `isLoading` 중복
2. `execute`의 `onSuccess` 콜백으로만 데이터 수신 — 반환값 미활용
3. 실패/취소 구분 불가 (`undefined` 동일 반환)
4. fetchDetail 내부에서 다시 runAsyncTask로 감싸는 중첩 구조

---

## 5. 영향 범위 요약

- `useApi.execute` 호출부: ~85개 파일
- `useAsyncTask` 폐기 대상: 2개 파일 (useDiscussDetailFetch가 유일 실사용)
- 서비스 API 반환 타입 전환 대상: 전 도메인 (DAO 하위 11개 + users/videos/usage/기타)
- `ApiErrorData` 단순화 대상: types.ts 1개 파일
- `unwrapServerResponse` 점진적 폐기 대상: api-client.ts (createApiClient 내 호출)

