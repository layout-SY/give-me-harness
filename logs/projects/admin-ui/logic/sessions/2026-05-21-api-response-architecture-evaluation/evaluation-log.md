# 평가 로그

## 컨텍스트
- 작업 주제: `synthoria-admin-ui`의 API 응답 추상화 구조 평가 및 장기 구조 전환
- 논의 대상:
  - `ServerResponse<TData>`를 도메인 API가 직접 알 필요가 있는가
  - `toApiResult` 기반 `ApiResult<T>` 반환과 `Promise<T> + throw` 모델 중 어떤 구조가 장기 유지보수에 적합한가
  - 요청 성공 시 모달을 닫고, 실패 시 모달을 유지하면서 공통 에러 알림을 표시하는 hook 흐름을 어떻게 설계할 것인가
- 실제 적용 범위:
  - `src/apis/api-client.ts`
  - `src/apis/common/api-result/server-response.unwrap.ts`
  - `src/apis/common/api-result.ts`
  - `src/apis/common/api-result/types.ts`
  - `src/apis/common/api-result/api-error.mapper.ts`
  - `src/exceptions/custom.exception.ts`
  - `src/apis/services/dao/discussion/discussion.api.ts`
  - `src/pages/dao/discuss-posts-management/**`

## 적용한 SKILL / 정책 근거
- `policy-abstraction-strategy`
  - `ServerResponse` 해석은 서버 응답 envelope이라는 불안정 영역이므로 안정 경계가 필요하다.
  - 단, mapper 인터페이스 다층화는 구현 교체 사례가 없어 과잉 추상화에 가깝다.
  - 공통 typed client + unwrap 함수 수준의 추상화가 현재 비용 대비 적합하다.
- `policy-refactoring`
  - 전역 API 전체를 한 번에 바꾸지 않고 `discussion` 도메인에 먼저 국소 적용했다.
  - 기존 기능을 보존하면서 반환 계약만 `ApiResult<T>`에서 `T | throw` 흐름으로 정리했다.
- `hook-use-api`
  - 화면과 hook은 API를 직접 호출하지 않고 `useApi().execute()` 경유를 유지한다.
  - 성공 처리는 `onSuccess`, 실패 처리는 `execute`의 catch/default Dialog 흐름에 맡기는 구조가 프로젝트 기존 패턴과 맞다.
- `policy-coding-convention`
  - 신규 코드에서 `any`와 `unknown`을 추가하지 않는다.
  - 타입 alias 우선, arrow function 형태를 유지한다.
- `policy-documentation`
  - 논의 결론, 구조적 리스크, 선택 근거, 검증 결과를 결론 중심으로 기록한다.

## 질의응답 요약
1. 사용자는 `discussion.api.ts`가 서버 응답 구조와 프론트 `ApiResult` 구조를 모두 아는 현재 방식이 유지보수에 취약하다고 지적했다.
2. 초기 평가에서는 `toApiResult`가 이미 존재하므로 별도 mapper 인터페이스는 과하다고 판단했다.
3. 사용자는 여기서 말한 mapper가 `toApiResult`라고 명확히 했다.
4. 사용자는 백엔드 응답 구조가 전 API에서 동일하다면 `ServerResponse<TData>` 처리를 `axios instance` 또는 중간 client로 내리고, 도메인 API는 프론트 반환 매핑만 담당하는 구조를 제안했다.
5. 평가 결과, `axios instance` 자체에 타입 처리를 모두 기대하는 것은 약하고, `axios instance`와 도메인 API 사이의 typed `apiClient`가 더 안정적인 경계라고 판단했다.
6. 이후 장기 구조로는 `ApiResult<T>`를 hook까지 전달하지 않고, 공통 client가 성공 시 `T`, 실패 시 `CustomException`을 throw하는 구조가 더 단순하다고 정리했다.
7. 사용자는 모달 저장/삭제 같은 흐름에서 성공 시 닫고 실패 시 유지하려면 hook이 성공/실패를 알아야 한다고 우려했다.
8. 결론은 hook이 성공/실패를 알아야 하지만, 반드시 `ApiResult.success` 값으로 알 필요는 없다는 것이다.
9. `await` 이후 `onSuccess`가 실행되면 성공, throw/catch 경로로 가면 실패이므로 `useApi.execute()`의 `onSuccess/onError` 계약으로 동일한 제어가 가능하다.
10. 사용자는 장기 구조 방식의 리팩터 진행과 `unknown` 없이 작업할 것을 승인했다.

## 구조적 리스크
1. **도메인 API의 응답 envelope 지식 누수**
   - 기존 `discussion.api.ts`는 `ServerResponse<T>`, `ApiResult<T>`, `toApiResult<T>()`를 모두 알아야 했다.
   - 서버 응답 필드 변경 시 도메인 API가 함께 수정될 가능성이 있었다.

2. **Result 모델과 throw 모델의 혼재**
   - 기존 호출부는 `useApi.execute()`의 try/catch 흐름을 쓰면서도 `result.success`를 다시 검사했다.
   - 이 구조는 실패 표현 방식이 중복되어 hook마다 `if (!result.success) throw ...` 반복을 만든다.

3. **hook 성공/실패 제어의 불명확성**
   - 모달 닫기, 목록 refetch, 성공 알림 같은 UI side effect가 `ApiResult` 분기 내부에 섞이면 실패 시 유지해야 하는 UI 상태와 성공 후 처리의 경계가 흐려진다.

4. **axios interceptor에 UI 책임을 넣을 위험**
   - 에러 응답을 받자마자 interceptor에서 Dialog를 띄우면 HTTP 인프라 레이어가 UI 모듈에 직접 결합된다.
   - 현재 프로젝트 기준으로는 interceptor는 `CustomException` 생성까지, Dialog 표시는 `useApi.execute()`가 담당하는 경계가 더 적절하다.

5. **전역 일괄 전환 리스크**
   - 전체 API를 한 번에 `Promise<T> + throw`로 바꾸면 호출부 영향이 크다.
   - `discussion` 도메인을 PoC/1차 적용 범위로 제한하는 것이 안전하다.

## 왜 중요한가
- 공통 응답 envelope은 백엔드 계약 변경 가능성이 높은 영역이므로 도메인 API에서 반복 처리하면 유지보수 비용이 커진다.
- hook에서 원하는 동작은 “실패 객체를 직접 다루기”가 아니라 “성공 경로에서만 후속 UI 조작을 실행하기”이다.
- `Promise<T> + throw` 구조는 이 요구를 더 직접적으로 표현한다.
  - 성공: `onSuccess(data)`에서 모달 닫기, refetch, 성공 알림 실행
  - 실패: throw로 `onSuccess` 미실행, 모달 유지, 공통 에러 알림 표시
- `ApiResult<T>`는 에러를 값으로 다뤄야 하는 특별한 화면/도메인에는 유효하지만, 일반 CRUD 흐름에서는 중복 분기를 만든다.

## 개선 옵션
1. **중간안: `apiClient -> ServerResponse<T>`, 도메인 API -> `toApiResult<T>`**
   - 장점: 기존 `ApiResult` 호출부를 유지하면서 `ServerResponse` 타입 처리를 공통화할 수 있다.
   - 단점: hook/page에서 `result.success` 분기가 계속 남는다.
   - 평가: 안전한 중간 단계지만 장기 목표로는 중복 모델이 남는다.

2. **장기안: `apiClient -> T | throw`, 도메인 API -> `Promise<T>`**
   - 장점: 도메인 API가 서버 envelope과 프론트 Result wrapper를 모두 몰라도 된다.
   - 장점: hook은 `onSuccess/onError`로 성공/실패 흐름을 자연스럽게 제어한다.
   - 단점: 기존 `ApiResult<T>` 호출부를 순차적으로 전환해야 한다.
   - 평가: 현재 `useApi.execute()` 구조와 가장 잘 맞는다.

3. **비권장: interceptor가 UI Dialog까지 직접 처리**
   - 장점: 표면적으로는 호출부 코드가 줄어든다.
   - 단점: HTTP 인프라 레이어가 UI 레이어를 알게 되어 의존 방향이 나빠진다.
   - 평가: 공통 에러 객체 생성은 가능하지만 UI 표시는 hook/useApi 경계에 남기는 것이 적절하다.

## 확정한 방향
- `ServerResponse<TData>` 해석은 도메인 API에서 제거한다.
- `apiClient`가 `ServerResponse<TData>`를 받고 `unwrapServerResponse<TData>()`로 성공 데이터만 반환한다.
- 서버 실패 응답은 `CustomException`으로 throw한다.
- `discussion.api.ts`는 `Promise<T>` 또는 `Promise<void>`만 반환한다.
- hook/page는 `result.success`를 보지 않고 성공 경로에서만 UI side effect를 실행한다.
- 신규/변경 API 응답 구조에서는 `unknown`을 사용하지 않는다.

## 실제 반영 요약
1. `src/apis/api-client.ts`
   - `get`, `post`, `patch`, `delete` 메서드를 가진 typed client를 추가했다.
   - 각 메서드는 axios instance에서 받은 `ServerResponse<TData>`를 unwrap해 `Promise<TData>`를 반환한다.

2. `src/apis/common/api-result/server-response.unwrap.ts`
   - `success === true`면 `data`를 반환한다.
   - 실패면 `toApiError` 결과를 `CustomException`으로 throw한다.

3. `src/apis/services/dao/discussion/discussion.api.ts`
   - `ApiResult`, `toApiResult`, `ServerResponse` 직접 import를 제거했다.
   - 모든 discussion API 메서드를 `Promise<T>` 또는 `Promise<void>` 반환으로 전환했다.

4. `src/pages/dao/discuss-posts-management/**`
   - `result.success` 검사와 `new CustomException(result.error)` 반복을 제거했다.
   - 목록/댓글 fetch는 API 응답 데이터를 바로 반환한다.
   - 상세/삭제/숨김/복구 흐름은 `execute(..., { onSuccess })` 성공 경로에서만 상태 갱신, 알림, refresh를 수행한다.

5. `src/apis/common/api-result/types.ts`, `src/exceptions/custom.exception.ts`
   - `ApiError.data`, `ApiError.cause`, `CustomException.data`에서 `unknown` 사용을 제거했다.
   - `ApiErrorData` JSON-like 타입과 `Error` 기반 cause로 타입을 좁혔다.

## 권장 백로그
1. **P1 — discussion 적용 흐름 런타임 확인**
   - 목록 조회, 상세 조회, 게시글 숨김/복구/삭제, 댓글 조회/삭제를 실제 UI에서 확인한다.

2. **P1 — `ApiResult<T>` 잔여 사용처 정책 결정**
   - 일반 CRUD는 `Promise<T> + throw`로 전환한다.
   - 에러를 값으로 직접 다뤄야 하는 예외적 흐름만 `ApiResult<T>`를 유지한다.

3. **P1 — typed `apiClient` 적용 범위 확대 기준 수립**
   - 한 PR에서 한 도메인 단위로만 전환한다.
   - 호출부의 `result.success` 제거 가능 여부를 선행 점검한다.

4. **P2 — `useApi.execute()` 에러 처리 계약 정리**
   - `onError`를 지정하면 기본 Dialog가 생략되는 현재 정책을 문서화/강화한다.
   - 실패 시 모달 유지, 성공 시 close/refetch 패턴을 recipe로 남긴다.

5. **P2 — `toApiResult`의 장기 위치 결정**
   - 전면 제거가 아니라 특수 케이스 전용 유틸로 축소할지 결정한다.

## 검증 결과
- `yarn lint`: 통과
- `unknown` 검색:
  - 신규 `apiClient`, `unwrapServerResponse`, `discussion` 적용 범위, `CustomException`/`api-result` 변경 범위에서 제거 확인
- `tsc --noEmit`:
  - 전체 실행은 실패
  - 실패 원인은 현재 워크트리에 이미 존재하는 `~/apis/users`, `~/apis/videos`, `~/apis/usage` 등 경로 깨짐과 기존 암시적 any 오류
  - 이번 변경 경로로 필터링했을 때 추가 타입 오류는 확인되지 않음

## 다음 단계 제안
- 우선 `discussion` 도메인에서 실제 UI 동작을 확인한다.
- 문제가 없으면 다음 전환 후보를 하나만 선택한다.
  - 추천 후보: 같은 DAO 하위 도메인 중 mutation 후 모달/refresh 흐름이 있는 API
- 전환 시 원칙은 동일하다.
  - 도메인 API: `Promise<T>` 또는 `Promise<void>`
  - 공통 client: `ServerResponse<T>` unwrap 및 실패 throw
  - hook/page: `onSuccess`에서만 성공 side effect 실행
