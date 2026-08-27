# Implementation Log — ApiResult 정식 계약 승격 + useApi 통합

> PR-1과 PR-2는 병렬 진행. 섹션별 append.

---

## PR-1 / Section 0 + Section 1 — 기반 타입 정리 + api-client ApiResult 전환

- 담당: refactorer
- 일시: 2026-05-21
- 대상: `src/apis/common/api-result/`, `src/apis/api-client.ts`, `src/apis/axios-instance.ts`, `src/apis/services/dao/discussion/discussion.api.ts`

### 변경 파일

**Section 0 — 기반 타입/유틸 정리**

1. `src/apis/common/api-result/types.ts`
   - `ApiErrorData` 재귀 union → `unknown`으로 단순화. 도메인별 좁히기는 호출부 type guard 책임으로 이동.

2. `src/apis/common/api-result/api-error.mapper.ts`
   - `toApiError`가 이미 정규화된 `ServerResponse`를 받도록 시그니처 정리. 내부 `toServerResponse` 재호출 제거. JSDoc으로 사전 정규화 계약 명시.

3. `src/apis/common/api-result/api-result.mapper.ts`
   - 정규화 1회 후 그 결과를 `toApiError`에 전달 (중복 정규화 제거).

4. `src/apis/common/api-result/server-response.unwrap.ts`
   - `@deprecated` JSDoc 추가 ("Use ApiResult contract via createApiClient instead."). `toApiError` 시그니처 변경에 맞춰 정규화된 응답 전달.

5. `src/apis/axios-instance.ts`
   - 인터셉터에서 raw error body를 `toApiError`에 넘기던 부분을 `toApiError(toServerResponse(data), fallback)`로 보정.

**Section 1 — createApiClient ApiResult 반환 전환**

6. `src/apis/api-client.ts`
   - `get/post/patch/delete` 반환 타입 `Promise<TData>` → `Promise<ApiResult<TData>>`
   - 내부에서 `unwrapServerResponse` 제거, `toApiResult`로 교체. `CustomException` 의존 제거. 비즈니스 실패는 ApiResult discriminated union, axios 네트워크/취소만 throw.

7. `src/apis/common/api-result/legacy-unwrap.ts` (신규)
   - 마이그레이션 어댑터 `unwrapApiResult(result: ApiResult<T>): T`. 실패 시 `CustomException` throw. `@deprecated` 마킹 + PR-3에서 제거 예정 명시.

8. `src/apis/common/api-result.ts`
   - 배럴에 `unwrapApiResult` export 추가.

9. `src/apis/services/dao/discussion/discussion.api.ts`
   - 유일한 `createApiClient` 사용처. PR-1 범위에서 호출부 시그니처(`Promise<T>`)를 유지하기 위해 각 메서드 끝에 `unwrapApiResult(result)` 어댑터 호출 추가. PR-3에서 ApiResult 기반 마이그레이션 시 일괄 제거.

### 핵심 결정사항

- **어댑터 전략**: createApiClient는 ApiResult 반환, 도메인 API는 PR-3까지 어댑터 사용. 어댑터 파일은 `legacy-unwrap.ts`로 격리하여 `@deprecated` 표시 + grep으로 잔존 사용처 추적 용이.
- **`unwrapApiResult` vs `unwrapServerResponse` 분리**: 입력 타입(`ApiResult` vs `ServerResponse`)에 따라 명확히 분리. `unwrapServerResponse`는 axios 인터셉터·기타 ServerResponse 직접 핸들링 경로 안전성을 위해 deprecated 상태로 보존.
- **`toApiError` 정규화 책임 이동**: 정규화는 호출 측(`toApiResult`, `unwrapServerResponse`, `axios-instance`)에서 1회 수행하도록 통일.
- **CustomException 레이어 정리**: `api-client`에서 의존 완전 제거. throw 경로는 `axios-instance`(네트워크/HTTP) + 어댑터(deprecated) 두 곳만 남김.

### 검증

- `yarn tsc --noEmit` PASS (0 errors)
- `yarn lint` 0 errors, 2 warnings (`src/hooks/use-api.tsx`의 unused eslint-disable — PR-2에서 정리)
- 외부 동작 변경 없음

### Risks / Follow-ups

- `ApiErrorData = unknown` → 도메인별 type guard 필요 시 호출부 책임
- `unwrapApiResult`는 임시 자산. PR-3 완료 시 `legacy-unwrap.ts` 삭제 + 배럴 export 제거
- `unwrapServerResponse`는 PR-7/PR-8까지 deprecated 마킹 상태로 유지

---

## PR-2 / Section 2 — useApi execute 개선 + race 가드

- 담당: refactorer
- 일시: 2026-05-21
- 대상: `src/hooks/use-api.tsx`

### 의도

1. 반환 타입 전환: `Promise<T | undefined>` → 신규 계약 `Promise<ApiResult<T> | { canceled: true }>`
2. silent opt-in: 기본 `silent=true`. 자동 Dialog는 `silent: false` 명시 시에만
3. race 가드: seq token으로 늦은 응답 폐기
4. `onSuccess`/`onError` 콜백 하위 호환 유지

### Before / After

Before:
```ts
execute<T>(apiCall: () => Promise<T>, options?): Promise<T | undefined>
```

After (오버로드 2종):
```ts
execute<T>(apiCall: () => Promise<ApiResult<T>>, options?): Promise<ApiResult<T> | { canceled: true }>
execute<T>(apiCall: () => Promise<T>, options?): Promise<T | undefined>  // 레거시 호환

export type ExecuteResult<T> = ApiResult<T> | { canceled: true }
```

### 핵심 변경

1. **오버로드 도입**: 단일 `executeImpl` + `ExecuteFn` 인터페이스. PR-2 단독 머지 회귀 없음. 런타임은 `isApiResultShape()`로 분기.
2. **silent 기본값 flip** (false → true). 옵션명 `silent` 유지. dev `console.warn` 보강. 전수 검토는 PR-8.
3. **race 가드**: `seqRef = useRef(0)`, 호출마다 `++seqRef.current`. `currentSeq !== seqRef.current`이면 `{canceled:true}` 또는 `undefined`. `isLoading=false`는 마지막 호출만.
4. **unmount 가드**: `isMountedRef`. cleanup 이후 도달 응답도 canceled.
5. **콜백**: `onSuccess(data)` / `onError(ApiError | unknown)` 유지.

### 검증

- `yarn tsc --noEmit` PASS
- `yarn lint` PASS (0 warnings, 0 errors)

### 비변경 (의도적)

- `useAsyncTask` (PR-8)
- `src/apis/api-client.ts`, `src/apis/common/api-result/` (PR-1 영역)
- 85개 호출부 (PR-3 이후 점진 마이그레이션)

### 리스크

- silent flip → 자동 Dialog 누락 (중): dev console.warn + PR-8 전수 검토
- 오버로드 inference wrong-pick (하): 런타임 분기로 안전. PR-3 파일럿 검증
- isLoading 마지막 seq만 해제 (하): race 가드 의도와 일치

### Deferred

- legacy throw 경로 제거 + `isApiResultShape` 제거 (PR-8 이후)
- `useAsyncTask` 폐기 (PR-8)
- 호출부 `onError` → 반환값 분기 (PR-3..PR-7)

### Handoff

- PR-3 파일럿 후 watcher 게이트 진행

---

## PR-3 / Section 3 — 파일럿 (discussion API + useDiscussDetailFetch)

- 담당: generator
- 일시: 2026-05-21
- 대상:
  - `src/apis/services/dao/discussion/discussion.api.ts`
  - `src/pages/dao/discuss-posts-management/detail/hooks/useDiscussDetailFetch.tsx`
  - `src/pages/dao/discuss-posts-management/detail/commend/hooks/useDiscussDetailModal.ts`
  - `src/pages/dao/discuss-posts-management/index.tsx`
  - `src/pages/dao/discuss-posts-management/detail/commend/proposalPostDetailCommentWidget.tsx`
  - `src/pages/dao/discuss-posts-management/detail/commend/hooks/useDiscussionCommentDelete.tsx`
  - `src/apis/common/api-result.ts`
  - `src/apis/common/api-result/legacy-unwrap.ts` (삭제)

### 의도

PR-1, PR-2가 만들어둔 ApiResult 정식 계약을 첫 도메인(discussion)에 적용한다.
- `discussion.api.ts`에서 `unwrapApiResult` 어댑터를 제거하고 `Promise<ApiResult<T>>` 정식 노출
- `useDiscussDetailFetch`에서 `useAsyncTask` 의존 제거 + `useApi.execute` 신규 계약 사용
- 호출부(detail modal)는 boolean 반환값으로 성공/실패 분기
- legacy 어댑터 파일(`legacy-unwrap.ts`) 삭제 + 배럴에서 export 제거

### Before / After

**discussion.api.ts 시그니처**

Before:
```ts
getDaoProposalDiscussionPostDetail: async (postId: number): Promise<GetDaoDiscussionPostDetail> => {
  const result = await client.get<GetDaoDiscussionPostDetail>(...);
  return unwrapApiResult(result); // throw on failure
}
```

After:
```ts
getDaoProposalDiscussionPostDetail: (postId: number): Promise<ApiResult<GetDaoDiscussionPostDetail>> =>
  client.get<GetDaoDiscussionPostDetail>(...);
// 호출부에서 result.success로 분기
```

**useDiscussDetailFetch 핵심 변경**

- `useAsyncTask` import/사용 제거. `isLoading`은 `useApi`의 것만 노출 (이중화 해소).
- `fetchDetail`: `execute(() => api.dao.getDaoProposalDiscussionPostDetail(postId), { silent: false })` →
  - `"canceled" in result` 가드 → 상태 유지
  - `!result.success` → 자동 Dialog는 useApi가 `silent: false`로 처리
  - 성공 시에만 `setFetchedData(result.data)` + 반환 `boolean`
- `runCurrentPostAction`: 핵심. `Promise<boolean>` 반환으로 호출부가 분기 가능하게.
  - 성공 시에만 `Dialog.alert(successMessage)` + `pubsub.publish("refresh-dao-proposals-discussion-posts-list")`
  - 실패 시 silent failure 없이 `silent: false`로 자동 Dialog 표시
- `requestPostModerationRestore` / `requestDeletePost` / `requestPostModerationHide`: 모두 `Promise<boolean>` 반환

**useDiscussDetailModal (호출부) 변경**

기존 `try/catch` 패턴(throw에 의존) → 반환된 boolean으로 분기:
```ts
// Before
try { await requestDeletePost(); handleModalClose(); discussPostListRefetch(); } catch {}
// After
const ok = await requestDeletePost();
if (!ok) return;
handleModalClose();
discussPostListRefetch();
```

### 핵심 결정사항

- **반환 타입 선택 (boolean vs ApiResult passthrough)**: hook 외부 API는 `Promise<boolean>`으로 결정. 이유:
  1. 호출부(detail modal)에서 ApiResult 분기를 다시 풀어쓰는 비용 회피.
  2. 성공 후 모달 닫기/refresh는 hook의 책임. error payload는 useApi가 dialog로 노출하므로 호출부가 추가로 알 필요 없음.
  3. ApiResult를 그대로 노출하면 호출부에서 `"canceled" in result` 등 추가 분기 부담.
- **silent: false 명시**: useApi의 silent 기본값이 PR-2에서 `true`로 바뀐 결과, 자동 오류 Dialog가 사라진다. 기존 동작 동등성을 위해 모든 discussion 호출부에 `silent: false`를 명시.
- **legacy-unwrap.ts 삭제**: discussion.api가 마지막 사용처였고, grep으로 잔존 사용처 없음을 확인 → 파일 삭제 + 배럴 export 제거.
- **useFetchAdapter 영향**: 별도 어댑터 훅이 아직 throw 기반 계약(`Promise<TableApiResponseDto>`)을 사용한다. 25개 호출부에 영향을 주는 시그니처 변경은 PR-3 범위를 초과하므로, 두 discussion 호출부(`index.tsx`, `proposalPostDetailCommentWidget.tsx`)에서만 인라인 unwrap 적용:
  ```ts
  const result = await api.dao.getDaoProposalsDiscussionPosts(params);
  if (!result.success) throw new CustomException(result.error);
  return result.data;
  ```
  useFetchAdapter 자체의 ApiResult 마이그레이션은 후속 PR로 분리.
- **useDiscussionCommentDelete**: 기존 onSuccess 콜백 패턴 유지 (useApi가 ApiResult를 흡수해 onSuccess에 unwrap된 data를 넘김). `silent: false`만 명시 추가.

### 검증

- `yarn tsc --noEmit` PASS (0 errors)
- `yarn lint` PASS (0 errors, 0 warnings)
- 외부 동작 동등성:
  - 성공 시: Dialog.alert(success) + pubsub publish + 모달 닫기 → 유지
  - 실패 시: useApi의 silent:false 자동 Dialog → 기존 throw → CustomException → useApi catch dialog와 동일
  - 취소/unmount: canceled 가드 → 상태 오염 없음 (race 가드 신규 효과)
- silent failure: 없음. 모든 호출부 `silent: false` 명시.

### 신규/제거 자산

- 제거: `src/apis/common/api-result/legacy-unwrap.ts`, `unwrapApiResult` 배럴 export
- 신규: 없음 (재사용 자산 활용)

### Risks / Follow-ups

- `useFetchAdapter` 시그니처는 throw 기반 유지 → 다른 도메인(PR-4 이후) 진행 시 useFetchAdapter 자체 ApiResult 마이그레이션 동반 필요. 현 PR에서는 인라인 unwrap이 임시 어댑터 역할.
- `useAsyncTask` 파일 자체 폐기는 PR-8에서 진행 (다른 도메인 잔존 사용처 확인 후).

### Handoff

- watcher 게이트(Section 4) 검토 요청

---

## PR-3.1 / Hook 계층 분리 — discussion 도메인

- 담당: planner → 인라인 실행
- 일시: 2026-05-22
- 기반: 4계층 모델 합의 (.modal.tsx → modal hook → fetch hook → useApi → api.ts)

### 의도

4계층 책임을 코드에 반영. useDiscussDetailFetch가 침범하고 있던 surface 부수효과(Dialog.alert + pubsub.publish)를 modal hook으로 이전하고, fetch hook은 도메인 facade(상태 + 게이트 + ApiResult passthrough)에 집중.

### 변경 파일

1. `src/pages/dao/discuss-posts-management/detail/hooks/useDiscussDetailFetch.tsx`
   - `usePubSub` import 제거
   - `CurrentPostActionParams` / `runCurrentPostAction` 추상화 제거 (Dialog.alert + pubsub.publish 함께 사라짐)
   - 각 액션(`requestPostModerationRestore`, `requestDeletePost`, `requestPostModerationHide`)이 `Promise<ApiResult<void> | { canceled: true }>`를 passthrough 반환
   - `Dialog.confirm`(삭제 게이트)은 보존 — 요청 전 조건이라 분리 불가
   - `fetchedData` 상태, `postId < 0` 가드, `resetDetail`은 보존
   - `useLanguage`는 confirm dialog 메시지에 필요해 보존

2. `src/pages/dao/discuss-posts-management/detail/commend/hooks/useDiscussDetailModal.tsx` (← `.ts`에서 확장자 변경, JSX 사용)
   - 성공 후 부수효과 흡수: 각 핸들러에서 `Dialog.alert(successMessage)` + `pubsub.publish(REFRESH_LIST_EVENT)`
   - `useDialog` / `usePubSub` / `useLanguage` 신규 import
   - `discussPostListRefetch` prop 제거 (pubsub 구독으로 동등 동작)
   - `isActionSucceeded` 헬퍼로 ApiResult passthrough 분기 통일
   - `REFRESH_LIST_EVENT` 상수화 (이벤트명 typo 재발 방지)

3. `src/pages/dao/discuss-posts-management/detail/_id.modal.tsx`
   - `discussPostListRefetch` prop 제거

4. `src/pages/dao/discuss-posts-management/index.tsx`
   - `<DiscussPostsManagementDetailModal discussPostListRefetch={refetch} />` → `<DiscussPostsManagementDetailModal />`

5. `src/pages/dao/discuss-posts-management/detail/commend/hooks/useDiscussionCommentDelete.tsx`
   - pubsub 이벤트명 typo 수정: `"refresh-dao-proposals-discussion-posts"` → `"refresh-dao-proposals-discussion-posts-list"` (PR-3 watcher 게이트에서 발견된 미해결 이슈 해소)

### 검증

- `yarn tsc --noEmit` PASS
- `yarn lint` PASS
- 동작 동등성:
  - 성공 시: `Dialog.confirm` (delete만) → API → 성공 Dialog.alert → pubsub.publish → 모달 닫힘 / 리스트 자동 refetch (pubsub 구독)
  - 실패 시: useApi의 `silent: false` 자동 Dialog → modal 핸들러 early return → 모달 유지
  - 댓글 삭제 시 부모 게시글 목록 갱신 (typo 수정으로 정상 동작)

### 계층별 최종 책임

| 레이어 | 책임 |
|--------|------|
| `.modal.tsx` (DiscussPostsManagementDetailModal) | UI 렌더링 + pubsub subscribe(모달 open 이벤트) |
| `useDiscussDetailModal` | surface 흐름: 성공 후 alert/pubsub/close/reset 결합, ReasonPrompt 오케스트레이션 |
| `useDiscussDetailFetch` | 도메인 facade: 액션 함수 + fetchedData 상태 + postId 가드 + delete confirm gate |
| `useApi` (변경 없음) | 요청 단위 라이프사이클 + 결과 어댑터 |
| `api.ts` (변경 없음) | Repository: 통신 + envelope 정규화 |

### Follow-up (deferred)

- `followup-success-side-effect-pattern.md` 참조: alert + pubsub 패턴이 도메인 확대 시 반복될 것이므로 별도 추상화 작업 예정 (Option 1 얇은 헬퍼 → TQ 도입 시 Option 3로 일괄 치환)
