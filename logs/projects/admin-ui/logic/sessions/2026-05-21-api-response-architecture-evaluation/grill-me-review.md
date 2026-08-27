# Grill-Me Review

## 단계
- 에이전트: watcher
- 상태: completed

## Neutral Question Tree

### 1. ServerResponse 해석 책임은 도메인 API에 남아야 하는가?
- Branch: No
- Answer: 서버 공통 envelope 해석은 공통 API client 계층으로 내리는 것이 맞다.
- Evidence:
  - `discussion.api.ts`는 endpoint/payload/DTO 책임만 가지는 편이 SRP에 맞다.
  - `ServerResponse<TData>`는 전 API 공통 계약이며 도메인별 관심사가 아니다.

### 2. 실패 응답은 값으로 반환해야 하는가?
- Branch: No for general CRUD
- Answer: 일반 CRUD/mutation 흐름에서는 실패를 `CustomException`으로 throw하는 것이 단순하다.
- Evidence:
  - hook의 요구사항은 실패 객체 렌더링이 아니라 성공 시 close/refetch 실행, 실패 시 유지다.
  - throw 모델에서는 `onSuccess`가 실행되지 않으므로 모달 유지가 자연스럽다.

### 3. hook이 성공/실패를 모르게 되는가?
- Branch: No
- Answer: hook은 `onSuccess/onError` 또는 try/catch 제어 흐름으로 성공/실패를 안다.
- Evidence:
  - 성공 시 `onSuccess(data)`가 실행된다.
  - 실패 시 `execute` catch/default Dialog 경로로 들어가며 성공 side effect가 실행되지 않는다.

### 4. interceptor가 Dialog를 직접 띄우는 것이 더 단순한가?
- Branch: No
- Answer: 표면적으로는 단순하지만 의존 방향이 나빠진다.
- Evidence:
  - interceptor는 axios infra 계층이다.
  - UI Dialog는 `useApi.execute` 또는 hook/page 경계가 담당해야 한다.

### 5. discussion만 먼저 적용하는 것이 충분한가?
- Branch: Yes
- Answer: 충분하다. 전체 API 일괄 전환은 범위가 크고 기존 경로 깨짐도 많다.
- Evidence:
  - `tsc --noEmit` 전체 실패가 기존 unrelated import 문제를 포함한다.
  - discussion 도메인은 `ApiResult` 반복 패턴이 명확해 PoC로 적합하다.

## 판정
- 결론: pass
- 조건:
  - 실제 UI 런타임 확인은 후속 백로그로 남긴다.
  - 전체 API 확장은 별도 planner 승인 후 도메인 단위로 진행한다.
