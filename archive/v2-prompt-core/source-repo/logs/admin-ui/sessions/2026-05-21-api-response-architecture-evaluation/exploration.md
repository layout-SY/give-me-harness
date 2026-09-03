# 탐색 로그

## 단계
- 에이전트: planner
- 상태: completed

## 확인한 SKILL
- `policy-abstraction-strategy`
  - 추상화 4조건 중 "불안정 영역에 안정 경계 필요"에 해당.
  - 별도 mapper 인터페이스는 구현 교체 사례가 없어 과잉 추상화로 판단.
- `policy-refactoring`
  - 전체 API 일괄 전환 대신 `discussion` 도메인부터 범위를 제한.
- `hook-use-api`
  - API 호출은 hook/page에서 `useApi().execute()`를 경유.
  - 성공/실패 UX는 `onSuccess/onError`와 기본 Dialog 처리로 연결.
- `recipe-data-dto`
  - 도메인 DTO와 공통 응답 DTO의 책임 분리 확인.
- `policy-documentation`
  - 결론 중심 문서화를 적용.

## 재사용 가능 자산
1. `src/apis/common/api-result/types.ts`
   - 기존 `ApiError`, `ApiResult`, `ServerResponse` 타입 존재.
   - 새 응답 타입을 만들지 않고 기존 `ServerResponse<TData>`를 재사용.

2. `src/apis/common/api-result/server-response.ts`
   - 서버 envelope을 정규화하는 `toServerResponse` 존재.
   - unwrap 함수 내부에서 재사용.

3. `src/apis/common/api-result/api-error.mapper.ts`
   - 서버 실패 응답을 프론트 에러 객체로 변환하는 `toApiError` 존재.
   - 실패 throw 시 `CustomException` payload 생성에 재사용.

4. `src/exceptions/custom.exception.ts`
   - 기존 공통 예외 클래스 존재.
   - 별도 `ApiException`을 새로 만들지 않고 기존 예외를 사용.

5. `src/hooks/use-api.tsx`
   - `execute<T>()`, `onSuccess`, `onError`, 기본 Dialog 처리 흐름 존재.
   - 장기 구조의 성공/실패 제어 지점으로 재사용.

## 기존 문제 패턴
- `src/apis/services/dao/discussion/discussion.api.ts`
  - `ApiResult`, `toApiResult`, `ServerResponse`가 도메인 API에 노출되어 있었다.
  - 도메인 API가 endpoint 책임과 응답 envelope 해석 책임을 동시에 가졌다.

- `src/pages/dao/discuss-posts-management/**`
  - `result.success` 검사 후 `new CustomException(result.error)`를 반복했다.
  - `useApi.execute()`의 try/catch 모델과 `ApiResult` 값 모델이 혼재했다.

## 탐색 결론
- 새 mapper 인터페이스는 만들지 않는다.
- 기존 `toServerResponse`, `toApiError`, `CustomException`을 조합해 `unwrapServerResponse`만 추가한다.
- axios instance를 직접 바꾸는 대신 typed `apiClient`를 둬 interceptor 타입 한계를 보완한다.
- PoC/1차 적용 범위는 discussion 도메인으로 제한한다.
