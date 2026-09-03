# 탐색 로그

## 단계
- 에이전트: planner
- 상태: completed

## 요청 요약
- 사용자는 `discussion` 상세 모달의 API 요청 체인을 단순화하고 싶어 한다.
- 핵심 요구는 다음과 같다.
  - `apiClient`는 유지한다.
  - `discussion` 상세 모달 흐름 안에서는 `useAsyncTask` 중복 사용을 제거한다.
  - `useApi.execute`의 `isLoading`을 사용한다.
  - 요청 성공 여부를 `boolean` 계약으로 명확히 반환한다.
  - 성공일 때만 `handleModalClose`, `resetDetail`, `discussPostListRefetch` 같은 후속 UI 동작을 실행한다.

## 확인한 코드 경로
- `src/pages/dao/discuss-posts-management/detail/hooks/useDiscussDetailFetch.tsx`
- `src/pages/dao/discuss-posts-management/detail/commend/hooks/useDiscussDetailModal.ts`
- `src/pages/dao/discuss-posts-management/detail/_id.modal.tsx`
- `src/hooks/use-api.tsx`
- `src/hooks/use-async-task/useAsyncTask.ts`

## 확인한 SKILL
- `policy-refactoring`
  - 기능 동작은 유지하고 구조만 단순화한다.
  - 현재 범위와 후속 범위를 분리한다.
- `policy-abstraction-strategy`
  - 이 문제는 새 추상화가 아니라 기존 체인의 계약 정리 문제다.
  - 공용 hook 전역 변경보다 discussion 로컬 계약 정리가 더 적합하다.
- `hook-use-api`
  - API 호출은 `useApi().execute()`를 사용한다.
  - `execute`는 `isLoading`, `onSuccess`, 기본 에러 Dialog 처리를 이미 제공한다.
- `hook-use-async-task`
  - `useAsyncTask`는 도메인 무관 async task의 loading/error fallback에 쓰인다.
  - 이번 discussion 상세 모달 체인에서는 `useApi.execute`와 책임이 중복된다.
- `policy-coding-convention`
  - `any` 금지, 타입 명시, arrow function 유지.

## 현재 구조
```text
useDiscussDetailModal
  -> try/catch
  -> requestPostModerationHide / requestDeletePost / requestPostModerationRestore
  -> useDiscussDetailFetch
  -> runAsyncTask
  -> execute
  -> discussion api
  -> apiClient
```

## 발견한 문제
1. `useApi.execute`는 API 실패를 catch하고 `undefined`를 반환한다.
2. `useAsyncTask`도 기본적으로 실패를 catch하고 `undefined`를 반환한다.
3. `requestDeletePost`는 confirm 취소 시에도 `undefined`를 반환한다.
4. `useDiscussDetailModal`은 `await request*()` 이후 성공 여부를 확인하지 않고 `handleModalClose`, `resetDetail`, `discussPostListRefetch`를 실행한다.

## 근본 원인
- 성공, 실패, confirm 취소, invalid postId guard가 모두 `undefined`로 합쳐진다.
- `useDiscussDetailModal`은 후속 UI 동작을 실행해도 되는지 판단할 명확한 계약을 받지 못한다.

## 재사용 가능 자산
- 유지:
  - `apiClient`
  - `useApi.execute`
  - `useModal`
  - `useReasonPrompt`
  - `usePubSub`
  - `CustomException` 기반 공통 에러 흐름
- 제거 검토:
  - `useDiscussDetailFetch.tsx` 내부의 `useAsyncTask` 사용
- 제거 금지:
  - `src/hooks/use-async-task/useAsyncTask.ts` 파일 자체
  - 다른 도메인의 `useAsyncTask` 사용처
  - `apiClient`

## 탐색 결론
- 이번 작업은 `apiClient` 계층의 문제가 아니다.
- 이번 작업의 목적은 `discussion` 상세 모달 UI 액션 체인의 불필요한 중첩을 제거하는 것이다.
- 가장 단순한 방향은 `request*` 함수가 `Promise<boolean>`을 반환하고, modal hook이 `success === true`일 때만 후속 동작을 실행하는 구조다.
