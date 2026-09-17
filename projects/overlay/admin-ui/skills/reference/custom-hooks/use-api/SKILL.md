---
name: hook-use-api
description: {{PROJECT_NAME}}의 기존 명령형 useApi 호출에서 최신 요청 판정, 로딩 종료, unmount 취소와 오류 보고를 다룬다.
---

# useApi

대상은 `src/shared/lib/hooks/use-api.tsx`와 `src/shared/api/common/api-result.ts`다. 반환값은 `{ execute, isLoading }`이며 도메인 API는 소비처에서 직접 import한다.

## admin-ui의 현재 계약

`ExecuteFn`은 조건부 타입으로 결과를 추론한다. ApiResult를 반환하는 호출은 `ApiResult<T> | { canceled: true }`, 원시 값 호출은 `T | undefined`를 반환한다. throw·Axios cancel·AbortError 경로는 런타임에서 undefined를 반환하므로 호출부가 이를 처리하는지 확인한다. ApiResult 경로의 선언 타입과 이 런타임 차이는 기존 제약이며 새 코드에서 성공을 가정하지 않는다.

옵션은 `onSuccess`, `onError`, `silent`, `unauthorizedBehavior`다. `silent` 기본값은 true다.

- 실패는 먼저 `reportApiFailure`에 전달한다. onError가 없고 silent가 false일 때 modal, 그 외에는 silent presentation을 지정한다. 인증 오류 처리는 reporter의 unauthorized 정책을 따른다.
- onError가 있으면 이어서 호출한다. 전역 보고가 생략되는 것은 아니다.
- onError 없이 silent가 true이면 개발 환경에서 미처리 오류 경고를 남긴다.

## 동시 호출과 loading

- 한 인스턴스에서 sequence를 증가시키고 마지막 호출만 반영한다. 이전 ApiResult는 `{ canceled: true }`, 이전 원시 값은 undefined로 반환하며 콜백·오류 보고를 생략한다.
- 최신 호출의 finally만 loading을 내린다. 이전 요청이 남았다는 이유로 loading을 유지하지 않는다.
- unmount에서 보관한 controller를 모두 abort한다. 수정 시에는 finally의 상태 갱신에도 mounted 조건을 적용해 해제 이후 갱신을 막는다.
- 최신 호출 정책은 이전 네트워크 요청을 자동 중단하거나 서버 mutation을 취소하지 않는다. 독립 명령의 결과가 모두 필요하면 hook 인스턴스나 도메인 orchestration을 분리한다.

## 사용과 수정 기준

서버 캐시 조회·mutation은 기존 TanStack Query hook/options를 사용하고 이를 useApi로 다시 감싸지 않는다. useApi는 기존 명령형 lifecycle 조정에 사용한다. 상세 기준은 공통 `recipe/api-authoring/references/query-mutation.md`를 따른다.

취소를 사용자 오류로 표시하지 않는다. silent 기본값과 공개 반환 타입 변경은 전체 호출부의 UX·타입에 영향을 주므로 동시 요청 수정에 섞지 않는다. 최신 응답 판정과 요청량을 줄이는 debounce는 별도 목적이므로 필요하면 함께 사용할 수 있다.

회귀 검증은 이전/최신 응답의 두 완료 순서, 오래된 실패의 reporter·callback 억제, 최신 요청 종료 시 loading 해제와 unmount 취소를 포함한다. user-ui는 동일한 동시 요청 방향을 사용하되 `status: completed | failed | canceled` 공개 반환 형식을 유지한다.
