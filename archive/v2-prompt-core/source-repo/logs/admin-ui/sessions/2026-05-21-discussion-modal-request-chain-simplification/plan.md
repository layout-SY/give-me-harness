# 계획 로그

## 단계
- 에이전트: planner
- 상태: ready_for_approval

## YAML 결과
```yaml
summary: >
  discussion 상세 모달의 API 요청 체인을 단순화한다.
  apiClient는 유지하고, useDiscussDetailFetch 내부의 useAsyncTask 중복 사용을 제거한다.
  request* 함수는 Promise<boolean>을 반환하고, useDiscussDetailModal은 성공 시에만 close/reset/refetch를 실행한다.

decision: plan_ready
work_type: refactor

scope:
  in:
    - src/pages/dao/discuss-posts-management/detail/hooks/useDiscussDetailFetch.tsx
    - src/pages/dao/discuss-posts-management/detail/commend/hooks/useDiscussDetailModal.ts
    - src/pages/dao/discuss-posts-management/detail/_id.modal.tsx
  out:
    - apiClient 제거 금지
    - toApiResult 복구 금지
    - src/hooks/use-async-task/useAsyncTask.ts 파일 삭제 금지
    - 다른 도메인의 useAsyncTask 사용처 변경 금지
    - useApi.execute 전역 계약 변경 금지
    - discussion 외 도메인 리팩터링 금지
    - UI 레이아웃/퍼블리싱 변경 금지

sections:
  - section: useDiscussDetailFetch 단순화
    tasks:
      - useAsyncTask import 제거
      - runAsyncTask 사용 제거
      - useApi.execute의 isLoading 반환
      - requestPostModerationHide/requestPostModerationRestore/requestDeletePost를 Promise<boolean> 계약으로 변경
      - requestGet은 detail fetch 성공 시 fetchedData만 갱신하도록 정리
  - section: useDiscussDetailModal 후속 동작 제어
    tasks:
      - try/catch 기반 후속 동작 제어 제거
      - const success = await request*(); if (!success) return 패턴 적용
      - success true일 때만 handleModalClose/refetch/reset 실행
      - handleModalClose 내부 resetDetail과 별도 resetDetail 중복 호출 제거
  - section: 검증
    tasks:
      - 실패 시 modal close 미실행 확인
      - 실패 시 resetDetail 미실행 확인
      - 삭제 confirm 취소 시 close/refetch 미실행 확인
      - 성공 시 기존 success alert와 refresh publish 유지 확인
      - yarn lint 실행
      - tsc는 기존 unrelated 실패가 있으면 변경 범위 필터로 확인

required_agents:
  - planner
  - refactorer
  - watcher
  - evaluator_optional

required_skills:
  - policy-refactoring
  - policy-abstraction-strategy
  - policy-coding-convention
  - hook-use-api
  - hook-use-async-task
  - policy-documentation

approval_request: 이 계획대로 진행할까요, 아니면 조정할 부분이 있나요?

reasons:
  - 현재 문제는 apiClient가 아니라 UI 액션 체인의 성공/실패 계약 부재다.
  - useApi.execute가 loading/error UX를 이미 담당하므로 discussion 상세 모달 흐름에서 useAsyncTask는 중복이다.
  - Promise<boolean> 계약은 성공/실패/취소/guard를 가장 단순하게 구분한다.
  - 공용 hook 전역 계약을 바꾸지 않아 영향 범위를 줄일 수 있다.

artifacts:
  - exploration.md
  - plan.md

next_action: user_approval_required
log:
  - 사용자 최신 요구에 따라 planner 위임 문서로 정리했다.
  - 승인 전 코드 수정은 하지 않는다.

status: ready_for_approval
```

## 구현 방향 상세

### 1. `useDiscussDetailFetch.tsx`
- 제거:
  - `useAsyncTask` import
  - `const { isLoading, runAsyncTask } = useAsyncTask();`
  - `runAsyncTask(...)` wrapper
- 유지:
  - `useApi`
  - `execute`
  - `Dialog`
  - `pubsub`
  - `resetDetail`
- 변경:
  - `const { api, execute, isLoading } = useApi();`
  - `runCurrentPostAction(...): Promise<boolean>`
  - 성공 시 `true`, 실패/guard 시 `false`

### 2. `request*` 계약
```ts
requestPostModerationRestore(): Promise<boolean>
requestDeletePost(): Promise<boolean>
requestPostModerationHide(reason: string): Promise<boolean>
```

의미:
```text
true  = 후속 UI 동작 가능
false = 실패 / confirm 취소 / invalid guard로 후속 UI 동작 금지
```

### 3. `useDiscussDetailModal.ts`
- 기존:
```ts
await requestDeletePost();
handleModalClose();
discussPostListRefetch();
```

- 변경 방향:
```ts
const success = await requestDeletePost();
if (!success) return;

handleModalClose();
discussPostListRefetch();
```

### 4. 중복 reset 정리
- `handleModalClose()`가 이미 `resetDetail()`을 호출한다.
- 따라서 `handleModalClose()` 직후 별도 `resetDetail()` 호출은 제거한다.

## Watcher 검토 기준
- API 실패 시 `handleModalClose()`가 실행되지 않는가
- API 실패 시 `resetDetail()`이 실행되지 않는가
- 삭제 confirm 취소 시 `handleModalClose()`와 `discussPostListRefetch()`가 실행되지 않는가
- 성공 시 기존 success alert와 refresh publish가 유지되는가
- `useDiscussDetailFetch.tsx`에서 `useAsyncTask` 의존이 제거되었는가
- `apiClient`가 유지되는가
- 공용 `useAsyncTask` 파일과 다른 도메인 사용처가 변경되지 않았는가

## 다음 액션
- 사용자 승인 후 refactorer가 위 범위만 구현한다.
- 구현 후 watcher가 `grill-me-review.md`와 `review-log.md`를 작성한다.
