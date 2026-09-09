# 탐색 기록

## 대상 경로
- `src/pages/dao/discuss-posts-management/detail/_id.modal.tsx`
- `src/pages/dao/discuss-posts-management/detail/hook/useDiscussDetailFetch.tsx`
- `src/pages/dao/discuss-posts-management/detail/useDetailModal.ts`
- `src/hooks/use-pub-sub/events.ts`

## 발견한 기존 재사용 자산
- 발견 항목: `useDetailModal`
- 재사용 제안: open/close 상태 전용 hook으로 유지
- 근거: pubsub 구독이 제거되어 modal visibility 책임만 남아 있음

- 발견 항목: `useDiscussDetailFetch`
- 재사용 제안: 상세 조회와 현재 상세 게시글 액션의 도메인 hook으로 유지
- 근거: `fetchedData.postId`를 기준으로 hide/restore/delete 액션을 수행하는 현재 상세 불변식을 소유함

- 발견 항목: `open-discussion-post-detail-modal`
- 재사용 제안: `{ postId }` payload 계약 유지
- 근거: payload가 작고, pubsub 전면 리팩토링 없이 `_id.modal.tsx`에서 orchestration 가능

## 재사용이 어려운 자산
- 자산: 공용 action runner hook
- 부적합 사유: 현재 반복은 단일 도메인 hook 내부의 액션 실행 흐름이며 공용화 조건을 충족하지 않음

## 신규 자산 필요성
- 필요 항목: `useDiscussDetailFetch.tsx` 내부 로컬 helper
- 필요 이유: loading, execute, success alert, list refresh, optional detail refetch 흐름이 반복됨
