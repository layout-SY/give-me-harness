# 구현 로그

## 단계
- 에이전트: refactorer
- 상태: review_requested

## YAML 결과
```yaml
summary: discussion API 응답 흐름을 `ApiResult<T>`에서 `Promise<T> + CustomException throw` 구조로 전환했다.
decision: review_requested
refactor_targets:
  - src/apis/common/api-result
  - src/apis/api-client.ts
  - src/apis/services/dao/discussion/discussion.api.ts
  - src/pages/dao/discuss-posts-management/**
applied_changes:
  - typed apiClient 추가
  - ServerResponse unwrap 함수 추가
  - discussion API의 ApiResult/toApiResult 의존 제거
  - discussion hook/page의 result.success 분기 제거
  - ApiError/CustomException의 unknown 제거
simplification_pass_applied: true
deferred_improvements:
  - 전체 API 도메인으로 apiClient 전환 확대
  - ApiResult 잔여 사용처 정책 결정
  - useApi.execute 에러 처리 recipe/reference 보강
risk_notes:
  - 전체 tsc는 기존 경로 깨짐으로 실패하므로 이번 변경 경로만 필터 검증했다.
  - apiClient 적용은 discussion 도메인에만 국소 적용했다.
grill_me_notes:
  - 실패를 return하지 않고 throw해야 hook에서 T | Error 분기가 생기지 않는다.
  - interceptor에서 Dialog를 직접 띄우면 계층 의존이 역전된다.
handoff_to_watcher: true
reasons:
  - useApi.execute가 이미 try/catch 모델이므로 Promise<T> + throw가 더 단순하다.
  - ServerResponse는 공통 envelope이라 도메인 API 경계 밖으로 숨기는 것이 유지보수성이 높다.
artifacts:
  - implementation-log.md
  - final-summary.md
next_action: watcher_review
log:
  - 사용자 승인 후 리팩터를 진행했다.
status: review_requested
```

## 작업 요약
- `discussion.api.ts`가 `ServerResponse<T>`, `ApiResult<T>`, `toApiResult<T>()`를 직접 다루던 구조를 제거했다.
- 공통 `apiClient`가 서버 응답 envelope을 받고, 성공 시 `TData`, 실패 시 `CustomException` throw로 정리했다.
- hook/page 호출부는 `result.success`를 확인하지 않고 `useApi.execute(..., { onSuccess })` 성공 경로에서만 상태 갱신과 refresh를 실행하도록 정리했다.

## 재사용 자산
- `toServerResponse`: 서버 응답 envelope 정규화
- `toApiError`: 실패 응답을 프론트 에러 객체로 변환
- `CustomException`: 공통 실패 예외
- `useApi.execute`: hook/page의 성공/실패 처리 경계
- `TableApiResponseDto`: 목록 응답 DTO

## 신규 파일 / 수정 파일
- 신규:
  - `src/apis/api-client.ts`
  - `src/apis/common/api-result/server-response.unwrap.ts`
- 수정:
  - `src/apis/common/api-result.ts`
  - `src/apis/common/api-result/types.ts`
  - `src/apis/common/api-result/api-error.mapper.ts`
  - `src/exceptions/custom.exception.ts`
  - `src/apis/services/dao/discussion/discussion.api.ts`
  - `src/pages/dao/discuss-posts-management/index.tsx`
  - `src/pages/dao/discuss-posts-management/detail/hooks/useDiscussDetailFetch.tsx`
  - `src/pages/dao/discuss-posts-management/detail/commend/proposalPostDetailCommentWidget.tsx`
  - `src/pages/dao/discuss-posts-management/detail/commend/hooks/useDiscussionCommentDelete.tsx`

## 핵심 로직
- `createApiClient(instance)`
  - `get/post/patch/delete` 메서드에서 axios instance를 호출한다.
  - 반환값을 `ServerResponse<TData>`로 받고 `unwrapServerResponse`를 통과시킨다.
- `unwrapServerResponse(response)`
  - `success === true`: `data` 반환
  - 그 외: `toApiError` 결과를 `CustomException`으로 throw
- `discussion.api.ts`
  - `Promise<ApiResult<T>>` 대신 `Promise<T>` 또는 `Promise<void>` 반환
  - `toApiResult` 호출 제거
- hook/page
  - fetch 함수는 API 데이터를 바로 반환
  - mutation 성공 side effect는 `onSuccess` 내부에서만 실행

## Self-Grill
1. Question: `CustomException`을 return하면 안 되는가?
   - Branch: Yes
   - Answer: return하면 `T | CustomException`이 되어 hook이 다시 분기해야 하므로 throw가 맞다.
   - Evidence: 사용자 요구는 실패 시 모달 유지이며, 이는 `onSuccess` 미실행만으로 충족된다.

2. Question: `toApiResult`를 유지해야 하는가?
   - Branch: 일부만
   - Answer: 일반 CRUD 흐름에서는 제거하고, 에러를 값으로 다뤄야 하는 특수 케이스에만 남기는 것이 장기적으로 적합하다.
   - Evidence: 기존 discussion 호출부는 `result.success` 검사 후 다시 throw하는 중복 패턴이었다.

3. Question: axios interceptor에서 Dialog를 직접 띄워도 되는가?
   - Branch: No
   - Answer: interceptor는 HTTP infra 계층이므로 UI Dialog 의존을 두지 않는다.
   - Evidence: 현재 프로젝트의 `useApi.execute`가 Dialog 표시 책임을 이미 가진다.

4. Question: 전체 API를 한 번에 바꿔야 하는가?
   - Branch: No
   - Answer: 호출부 영향이 크므로 discussion 도메인부터 국소 적용한다.
   - Evidence: 전체 `tsc`는 기존 경로 깨짐이 많아 일괄 전환 시 회귀 분석 비용이 크다.

## 검증 / 요청 처리
- `yarn lint`: 통과
- `unknown` 검색:
  - 변경 범위에서 `unknown` 제거 확인
- `tsc --noEmit`:
  - 전체 실행 실패
  - 실패 원인: 기존 `~/apis/users`, `~/apis/videos`, `~/apis/usage` 경로 깨짐 및 기존 암시적 any
  - 이번 변경 경로 필터에서는 추가 오류 없음

## 리스크
- 실제 런타임에서 백엔드 성공 응답이 항상 `{ success: true, data }` envelope을 준다는 전제가 필요하다.
- `void` 응답의 경우 `data`가 없으면 `undefined as void`로 처리된다.
- 전체 `ApiResult` 제거가 아니므로 프로젝트에 두 모델이 당분간 공존한다.

## 핸드오프 메모
- watcher 리뷰 준비 완료
