---
name: policy-tanstack-query
description: synthoria-admin-ui에서 TanStack Query로 서버 상태 조회·변경·캐시 무효화를 구현하거나 리뷰할 때 적용.
---

# TanStack Query (Policy)

## 언제 이 스킬을 사용하나요?

- `useQuery`, `useMutation`, query key 또는 invalidation을 추가·수정할 때
- fixture 화면을 취소 가능한 HTTP 서버 상태로 전환할 때

## 규칙

- query key에는 요청 결과를 바꾸는 ID·필터·검색·정렬·페이지를 모두 포함한다.
- query 함수의 `AbortSignal`을 실제 HTTP 요청까지 전달한다.
- 외부 응답은 `ApiResult`를 해제한 뒤 Zod parser를 통과시킨다.
- mutation 성공 시 영향받는 최소 key만 무효화한다.
- 초기 조회 오류와 기존 캐시가 있는 refetch 오류를 구분한다.
- 오류 Dialog, navigation, pubsub 같은 부수 효과는 query 함수가 아니라 surface에서 처리한다.
- 기존 `useApi`·`useFetchAdapter` 화면은 승인된 화면 단위로만 전환한다.

## 금지

- TanStack query hook을 `useApi`로 다시 감싸기
- query key에서 요청 의존값 누락
- 모든 query를 루트 key 하나로 일괄 무효화
- API/DTO 계층에 UI 부수 효과 추가
- fixture를 page/component에서 직접 import
