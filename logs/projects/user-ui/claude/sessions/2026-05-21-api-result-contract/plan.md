# Plan — ApiResult 정식 계약 승격 + useApi 통합

## Request Summary

evaluator 평가 결과를 바탕으로 사용자가 확정한 3가지 방향을 구현한다.
1. `ApiResult<T>`를 도메인 API 반환 타입의 정식 계약으로 승격 (`Promise<T>` → `Promise<ApiResult<T>>`)
2. `useAsyncTask` 폐기 + `useApi` 단일화 (execute 반환 형태 개선, race 가드, silent opt-in)
3. i18n 인터셉터 위치 유지 (이번 범위 밖)

---

## Work Type

refactor

---

## Scope (In)

- `src/apis/common/api-result/types.ts` — `ApiErrorData` 단순화
- `src/apis/common/api-result/api-result.mapper.ts` — `toServerResponse` 중복 호출 정리
- `src/apis/common/api-result/api-error.mapper.ts` — `toServerResponse` 중복 호출 정리
- `src/apis/api-client.ts` — `createApiClient` 메서드 반환 타입을 `ApiResult<T>`로 전환
- `src/hooks/use-api.tsx` — execute 반환 형태 개선, race 가드, silent opt-in
- `src/hooks/use-async-task/useAsyncTask.ts` — 폐기 처리
- `src/apis/services/dao/discussion/discussion.api.ts` — 파일럿: 반환 타입 `Promise<ApiResult<T>>`로 전환
- `src/pages/dao/discuss-posts-management/detail/hooks/useDiscussDetailFetch.tsx` — 파일럿: 새 계약 기반으로 마이그레이션
- 파일럿 검증 후 나머지 도메인 확대 (dao 하위 나머지 → users/videos/usage → 기타 비-DAO)

## Scope (Out)

- i18n 인터셉터 위치 변경
- `axiosInstance` 자체 구조 변경
- 비-DAO 14개 서비스 중 이미 createApiClient 적용 완료된 부분의 내부 로직 재작업 (단, 반환 타입 전환은 포함)
- UI 컴포넌트 레이어 변경 (호출부 시그니처가 유지되는 한)

---

## Sections

### Section 0 — 기반 타입/유틸 정리 (선행 작업)
> 담당: refactorer | SKILL: policy-refactoring, policy-coding-convention

**작업 내용:**

1. `ApiErrorData` → `unknown`으로 단순화
   - `types.ts`의 재귀 타입 제거
   - 도메인별 type guard는 각 도메인이 필요 시 선언 (글로벌 강제 금지)

2. `toApiResult` / `toApiError` / `unwrapServerResponse`의 `toServerResponse` 중복 호출 정리
   - 현재: `toApiResult` → `toServerResponse` 호출 + `toApiError` 내부에서도 `toServerResponse` 재호출
   - 정책: 성공 판정은 `toServerResponse` 정규화 단계에서 1회만 수행
   - `toApiError`가 이미 정규화된 `ServerResponse`를 받도록 시그니처 변경 (내부에서 재정규화 제거)

3. `ApiResult` export 배럴(`api-result.ts`) 정리 — `unwrapServerResponse` 노출 유지하되 `@deprecated` JSDoc 마킹

**산출물:** `types.ts`, `api-result.mapper.ts`, `api-error.mapper.ts` 수정

---

### Section 1 — createApiClient ApiResult 반환 전환
> 담당: refactorer | SKILL: policy-refactoring, policy-abstraction-strategy

**작업 내용:**

`api-client.ts`의 `createApiClient` 메서드 4종(get/post/patch/delete)을:
- 기존: `Promise<TData>` (내부에서 unwrap → throw)
- 변경: `Promise<ApiResult<TData>>` (내부에서 toApiResult → discriminated union 반환)

`ApiClient` 타입도 함께 업데이트.

`unwrapServerResponse` 기반 경로는 `api-client.ts` 내에서만 제거하고, `server-response.unwrap.ts` 파일 자체는 `@deprecated` 마킹 후 유지 (다른 직접 참조가 없으므로 Section 0에서 확인 후 제거 가능).

**레이어 제약:**
- `api-client`는 `common/api-result` 유틸에만 의존 가능
- `CustomException`에 대한 의존을 이 레이어에서 제거 (throw 경로 삭제)

**산출물:** `api-client.ts` 수정

---

### Section 2 — useApi execute 반환 형태 개선 + race 가드
> 담당: refactorer | SKILL: policy-hook-extraction, policy-refactoring

**작업 내용:**

`useApi.execute` 시그니처 변경:

```ts
// 변경 전
execute<T>(apiCall: () => Promise<T>, options?: ApiCallOptions<T>): Promise<T | undefined>

// 변경 후
execute<T>(apiCall: () => Promise<ApiResult<T>>, options?: ApiCallOptions<T>): Promise<ApiResult<T> | { canceled: true }>
```

세부 변경:
1. **silent opt-in 전환**: `silent` 기본값 `false` → `true` (자동 Dialog 표시가 opt-in)
   - 기존 코드의 `silent: false` 명시는 그대로 동작
   - 기존 코드의 `silent` 미지정은 이제 조용히 실패 → 주의: 호출부 검토 필요 (Section 4에서 처리)

2. **race 가드**: 호출별 seq token 발행
   ```ts
   const seqRef = useRef(0);
   // execute 내부에서 seq++ 후 await, 완료 시점에 현재 seqRef.current와 비교
   // 늦게 도착한 결과는 { canceled: true } 반환
   ```

3. **취소/실패 구분**: AbortError는 `{ canceled: true }`, API 실패는 `ApiResult<T>` success:false

4. **onSuccess/onError 콜백 유지**: 선택적 부가물로 유지 (하위 호환), 정식 흐름은 반환값

**공용화 수준:** `useApi`는 전역 공용 훅 유지 (변경 없음)

**산출물:** `use-api.tsx` 수정

---

### Section 3 — 파일럿: discussion API + useDiscussDetailFetch 마이그레이션
> 담당: generator | SKILL: policy-coding-convention, policy-hook-extraction

**작업 내용:**

**3-A. discussion.api.ts 반환 타입 전환**
- 각 메서드의 반환 타입을 `Promise<TData>` → `Promise<ApiResult<TData>>`로 변경
- `createApiClient`가 이미 `ApiResult`를 반환하므로 메서드 시그니처 수정이 핵심

**3-B. useDiscussDetailFetch.tsx 재작성**
- `useAsyncTask` 제거, `useApi` 단일화
- `execute` 반환값(`ApiResult<T> | { canceled: true }`)을 기반으로 분기 처리
- `fetchDetail` 내 이중 레이어(`runAsyncTask` → `execute`) 제거
- 취소/실패 구분 반영 (canceled이면 상태 변경 없이 early return)
- `isLoading`은 `useApi`의 것만 사용

**기대 효과:**
- `useAsyncTask` 의존 제거 → 파일 자체 폐기 가능 확인
- 이중 isLoading 중복 해소
- silent 처리 명시적 선택

**산출물:** `discussion.api.ts`, `useDiscussDetailFetch.tsx` 수정

---

### Section 4 — Watcher 파일럿 검증 게이트
> 담당: watcher | SKILL: policy-review-checklist

**검증 항목:**
- [ ] `ApiResult` discriminated union이 호출부에서 정확히 좁혀지는가 (`if (result.success)` 분기)
- [ ] `canceled` 케이스가 상태 오염 없이 처리되는가
- [ ] race 가드: 빠른 연속 호출 시 마지막 결과만 반영되는가
- [ ] `isLoading` 단일화 (중복 레이어 없음)
- [ ] `useAsyncTask` import 잔존 없음
- [ ] TypeScript 오류 없음 (`yarn tsc --noEmit`)
- [ ] 기존 동작 동등성: 성공/실패/대화상자 동작이 이전과 동일

**파일럿 통과 시 → Section 5 진행 승인**
**파일럿 실패 시 → Section 3 재작업 후 재검증**

---

### Section 5 — DAO 도메인 확대 (파일럿 승인 후)
> 담당: refactorer | SKILL: policy-refactoring

**대상 (PR 단위: DAO 하위 도메인별):**
- `dao/proposal`, `dao/proposal-review`, `dao/vote` + 관련 훅/페이지
- `dao/banner`, `dao/policy`, `dao/nft`, `dao/voice-room`, `dao/report` + 관련 훅/페이지
- `dao/dao-logs`, `dao/main-board` + 관련 훅/페이지

**각 도메인 PR 포함 범위:**
1. 해당 `*.api.ts` 반환 타입 전환
2. 해당 도메인 페이지/훅의 `execute` 반환값 기반 처리 전환
3. `onSuccess`/`onError` 콜백 의존 → 반환값 기반으로 점진 전환

**PR 단위 분할 이유:** 30+ 호출부 일괄 변경 시 리뷰 불가 + 롤백 단위 명확화

---

### Section 6 — 잔여 도메인 확대 (users / videos / usage / 기타)
> 담당: refactorer | SKILL: policy-refactoring

**대상:**
- `users.api.ts`: 구형 `instance.get` 직접 호출 패턴 → `createApiClient` + `ApiResult` 전환
- `videos.api.ts`, `usage.api.ts`: 동일
- 이미 `createApiClient` 적용된 비-DAO 14개: 반환 타입만 `ApiResult<T>`로 전환 (내부 로직 재작업 최소화)

**주의:** `users.api.ts`는 구형 패턴(직접 instance 호출 + any cast)이므로 createApiClient 적용이 선행되어야 함

---

### Section 7 — useAsyncTask 폐기 처리 + silent 기본값 전환 영향 검토
> 담당: refactorer + watcher | SKILL: policy-refactoring, policy-review-checklist

**작업 내용:**
1. `useAsyncTask.ts` 파일 삭제 (Section 3 파일럿에서 마지막 사용처 제거 확인 후)
2. `silent` 기본값 `false` → `true` 전환으로 인해 기존 `silent` 미지정 호출부에서 오류 다이얼로그가 더 이상 자동 표시되지 않는 파일 식별
   - `useApi` 사용 85개 파일 중 `onError` 미지정 + `silent` 미지정 케이스 확인
   - 필요한 곳에 `silent: false` 명시 추가

---

### Section 8 — 최종 Watcher 전체 게이트 + Evaluator 검토
> 담당: watcher → evaluator

**watcher 최종 체크:**
- [ ] `Promise<T>` 반환 서비스 API 잔존 없음 (단, deprecated 경로 제외)
- [ ] `unwrapServerResponse` 직접 호출 잔존 없음 (api-client 외부)
- [ ] `useAsyncTask` import 잔존 없음
- [ ] TypeScript 전체 오류 없음
- [ ] silent 기본값 전환 영향 누락 없음

**evaluator 검토:**
- ApiResult 계약이 아키텍처적으로 일관성 있게 관철되었는지
- 향후 개선 제안 (예: React Query 도입 가능성 등)

---

## PR 분할 계획

| PR | 범위 | Section |
|----|------|---------|
| PR-1 | 기반 타입/유틸 정리 + api-client ApiResult 전환 | 0, 1 |
| PR-2 | useApi execute 개선 + race 가드 | 2 |
| PR-3 | 파일럿 (discussion API + useDiscussDetailFetch) | 3 |
| PR-4 | DAO 도메인 확대 (proposal/review/vote) | 5-a |
| PR-5 | DAO 도메인 확대 (banner/policy/nft/voice-room/report) | 5-b |
| PR-6 | DAO 도메인 확대 (dao-logs/main-board) | 5-c |
| PR-7 | users/videos/usage 구형 패턴 전환 | 6 |
| PR-8 | useAsyncTask 폐기 + silent 영향 정리 | 7 |

> PR-1, PR-2는 병렬 작업 가능. PR-3는 PR-1, PR-2 머지 후 시작.

---

## Required Agents

- refactorer: Section 0, 1, 2, 5, 6, 7
- generator: Section 3 (파일럿 신규 패턴 구현)
- watcher: Section 4 (파일럿 게이트), Section 8 (최종 게이트)
- evaluator: Section 8 최종 검토

---

## Required Skills

- policy-refactoring
- policy-coding-convention
- policy-hook-extraction
- policy-abstraction-strategy
- policy-review-checklist
- policy-documentation

---

## Dependency / Architecture Constraints

### 의존 방향 (레이어 순서)

```
axiosInstance (인프라)
  ↓
api-client.ts (HTTP 클라이언트 추상화)
  ↓
services/*.api.ts (도메인 API)
  ↓
hooks/use-api.tsx (실행 계층)
  ↓
pages/**/*.tsx (UI)
```

- `api-client`는 `common/api-result` 유틸에만 의존. `CustomException` 의존 제거.
- `services/*.api.ts`는 `api-client`만 사용. `useApi` 직접 import 금지.
- `useApi`는 글로벌 공용 훅. 도메인 로직 포함 금지.
- `useAsyncTask`는 폐기 대상. 신규 코드에서 사용 금지.

### 공용화 수준

- `ApiResult<T>`, `ApiError` 타입: 글로벌 (`common/api-result/types.ts`)
- `createApiClient`: 글로벌 (`apis/api-client.ts`)
- `useApi`: 글로벌 공용 훅
- 도메인별 type guard (ApiErrorData 대체): 각 도메인 내부

---

## Risks / Assumptions

| 리스크 | 영향도 | 대응 |
|--------|--------|------|
| `silent` 기본값 전환 → 기존 오류 다이얼로그 누락 | 중 | Section 7에서 전수 검토 + 명시적 `silent: false` 추가 |
| 구형 `users.api.ts` any cast → createApiClient 전환 시 타입 깨짐 | 중 | Section 6에서 DTO 타입 정비 병행 |
| race 가드 도입 → 기존 단건 호출에서 `canceled` 케이스 처리 누락 | 하 | watcher 체크리스트에 포함, `canceled` 미처리 시 TS 경고로 포착 |
| PR 간 의존성 (PR-3은 PR-1, PR-2 선행 필요) | 중 | PR 순서 가이드라인 명시 |

### 롤백 계획

- PR 단위로 분할하므로 개별 PR revert 가능
- `unwrapServerResponse`는 `@deprecated` 마킹 후 일정 기간 유지 → 급한 롤백 시 api-client.ts만 이전 버전으로 복구하면 전체 복원
- `useAsyncTask` 폐기는 마지막 단계 → 중간 단계에서는 파일 유지

---

## Artifacts

- `plan.md` (본 파일)
- `exploration.md`
- `implementation-log.md` (구현 단계에서 작성)
- `review-log.md` (watcher 검증 시 작성)
- `final-summary.md` (파이프라인 완료 시 작성)

---

## Approval Request

이 계획대로 진행할까요, 아니면 조정할 부분이 있나요?
