# 구현 로그

## 작업 요약
- `useDiscussDetailFetch.tsx`에 도메인 로컬 실행 템플릿을 추가했다.
- `_id.modal.tsx`는 pubsub open 이벤트를 받아 `handleOpen`과 `requestGet(postId)`를 조립하는 컨테이너 역할을 유지했다.

## 재사용 자산
- `useDetailModal`: open/close 상태 관리 재사용
- `useDiscussDetailFetch`: 상세 데이터 및 current post action hook으로 재사용
- `usePubSub`: 기존 `open-discussion-post-detail-modal` / `refresh-dao-proposals-discussion-posts-list` 계약 재사용

## 신규 파일 / 수정 파일
- 수정: `src/pages/dao/discuss-posts-management/detail/_id.modal.tsx`
- 수정: `src/pages/dao/discuss-posts-management/detail/hook/useDiscussDetailFetch.tsx`
- 수정: `src/pages/dao/discuss-posts-management/detail/useDetailModal.ts`

## 핵심 로직
- `runWithLoading`: loading on/off와 예외 로깅을 공통화
- `fetchDetail`: 상세 조회 후 `fetchedData` 갱신
- `runCurrentPostAction`: current post guard, execute, success alert, list refresh, optional detail refetch를 템플릿화
- `resetDetail`: 모달 close 시 stale detail 제거

## Grill-Me Self Review
- Question: 템플릿 helper를 공용 hook으로 올릴 필요가 있는가?
- Branch: No
- Recommended Answer: 도메인 로컬 helper로 제한한다.
- Evidence: 현재 소비자는 `useDiscussDetailFetch.tsx` 하나뿐이며, 공용화 조건을 충족하지 않는다.

- Question: `requestGet(postId)`도 템플릿에 포함해야 하는가?
- Branch: No
- Recommended Answer: 외부 payload로 상세 진입하는 함수라 별도 유지한다.
- Evidence: hide/restore/delete는 current post action이고, get은 postId 진입점이다.

- Question: pubsub 계약을 바꿔야 하는가?
- Branch: No
- Recommended Answer: 이번 범위에서는 `{ postId }` 계약을 유지한다.
- Evidence: pubsub 전면 리팩토링은 사용자 요청 범위를 초과한다.

## 검증 / 요청 처리
- `yarn lint`: 통과
- `./node_modules/.bin/tsc --noEmit`: 통과

## 리스크
- `usePubSub()`가 매 렌더 새 `pubsub` wrapper를 반환하므로 effect deps에 포함하면 재구독이 발생할 수 있다. 현재 cleanup이 있어 누수는 없지만, 공용 hook 안정화는 후속 과제다.

## 핸드오프 메모
- watcher 리뷰 준비 완료
