# 최종 요약

## 결론
- DetailModal 리팩토링은 완료되었다.
- pubsub 계약은 변경하지 않고 `_id.modal.tsx`가 orchestration을 담당하도록 유지했다.
- `useDiscussDetailFetch`는 current post 기반 액션을 캡슐화하고, 반복 비동기 흐름을 도메인 로컬 템플릿 helper로 정리했다.

## 변경 파일
- `src/pages/dao/discuss-posts-management/detail/_id.modal.tsx`
- `src/pages/dao/discuss-posts-management/detail/hook/useDiscussDetailFetch.tsx`
- `src/pages/dao/discuss-posts-management/detail/useDetailModal.ts`

## 검증
- `yarn lint`
- `./node_modules/.bin/tsc --noEmit`

## 후속 후보
- `usePubSub`가 반환하는 wrapper 안정화 검토
- 댓글 상세 모달의 과도한 pubsub payload 분리 검토
