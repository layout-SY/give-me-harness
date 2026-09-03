# Portfolio Entry — API Response Architecture

## 문제

- **기술**: `discussion.api.ts`가 서버 응답 envelope(`ServerResponse<TData>`)과 프론트 반환 모델(`ApiResult<T>`)을 모두 알아야 했다.
- **기술**: hook/page에서 `result.success`를 검사한 뒤 다시 `CustomException`을 throw하는 반복 패턴이 생겼다.
- **UX/동작**: 저장/삭제 요청 성공 시 모달을 닫고 실패 시 유지해야 하는 흐름에서, 성공/실패 제어 책임이 hook과 API 반환 모델 사이에 애매하게 걸쳐 있었다.

## 고민 과정

| 접근법 | 장점 | 단점 | 채택 여부 |
|---|---|---|---|
| 도메인 API에서 `toApiResult` 유지 | 기존 호출부 영향이 작다 | `result.success` 분기와 throw 모델이 계속 공존 | 부분 검토 |
| axios interceptor에서 모든 에러 UI 처리 | 호출부 코드가 줄어든다 | HTTP infra가 UI Dialog에 의존 | 미채택 |
| typed apiClient에서 unwrap 후 `T | throw` 반환 | 도메인 API와 hook 흐름이 단순해짐 | 기존 `ApiResult` 호출부를 순차 전환해야 함 | 채택 |

**판단 기준**: `useApi.execute()`의 기존 try/catch 구조와 맞추고, 성공 side effect를 `onSuccess`에만 배치해 모달 유지/닫기 흐름을 명확히 하는 것을 우선했다.

## 결과

### 결과 1: typed `apiClient` 추가
- axios instance와 도메인 API 사이에 typed client를 두었다.
- **도출 이유**: axios interceptor만으로 타입 안정성을 보장하기 어렵고, 도메인 API가 `ServerResponse<TData>`를 직접 알 필요가 없기 때문이다.

### 결과 2: `unwrapServerResponse` 추가
- `success === true`면 `data`를 반환하고 실패면 `CustomException`을 throw한다.
- **도출 이유**: 실패를 return하면 hook에서 `T | Error` 분기가 생기므로 exception flow가 더 단순하다.

### 결과 3: discussion API 반환 계약 전환
- `Promise<ApiResult<T>>`를 `Promise<T>` 또는 `Promise<void>`로 전환했다.
- **도출 이유**: 일반 CRUD 흐름에서는 에러를 값으로 다룰 필요가 낮고, 성공/실패는 `useApi.execute` 경계에서 처리하는 것이 더 일관적이다.

### 결과 4: hook/page의 `result.success` 반복 제거
- 목록/댓글 fetch는 데이터를 바로 반환한다.
- mutation 성공 side effect는 `onSuccess` 내부에서만 실행한다.
- **도출 이유**: 성공 시 close/refetch, 실패 시 유지 요구사항을 가장 직접적으로 표현하기 위해서다.

## 성과

- discussion 도메인의 `ApiResult` 직접 사용과 `result.success` 반복 분기를 제거했다.
- 서버 응답 envelope 해석 책임을 도메인 API 밖으로 이동했다.
- 실패 시 모달 유지, 성공 시 후속 side effect 실행이라는 UI 흐름을 `useApi.execute` 계약에 맞췄다.
- `yarn lint` 통과.

## 회고

- 최초 문서화 단계에서 evaluator 로그만 작성하고 planner/refactorer/watcher 산출물을 누락했다.
- 다음부터는 구조 변경을 시작하기 전에 planner 문서와 승인 게이트를 먼저 남겨야 한다.
- `ApiResult`와 throw 모델은 동시에 오래 유지하면 혼란이 생기므로, 후속 도메인 전환 기준을 명확히 문서화해야 한다.
