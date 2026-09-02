# 구현 로그

## 작업 요약
- `useAsyncTask` 공용 hook을 추가했다.
- `useDiscussDetailFetch`의 로컬 `runWithLoading`을 제거하고 `useAsyncTask`로 대체했다.
- current post action의 DAO 정책 래핑은 도메인 hook 내부에 유지했다.

## 재사용 자산
- `useApi`: API execute 유지
- `usePubSub`: DAO list refresh 이벤트 유지
- `useDialog`: DAO 액션 성공/확인 Dialog 유지

## 신규 파일 / 수정 파일
- 신규: `src/hooks/use-async-task/useAsyncTask.ts`
- 신규: `src/hooks/use-async-task/index.ts`
- 수정: `src/pages/dao/discuss-posts-management/detail/hook/useDiscussDetailFetch.tsx`
- 신규: `.agents/skills/reference/custom-hooks/use-async-task/SKILL.md`
- 수정: `.agents/skills/reference/custom-hooks/SKILL.md`
- 수정: `.codex/memory/reusable-assets.md`

## 핵심 로직
- `useAsyncTask`는 `runAsyncTask(task, options?)`와 `isLoading`만 노출한다.
- 공용 hook은 id, API, Dialog, pubsub를 알지 않는다.
- `useDiscussDetailFetch`는 `requestGet(postId)`와 `runCurrentPostAction`에서 `runAsyncTask`를 사용한다.

## Grill-Me Self Review
- Question: 공용 hook이 id를 받아야 하는가?
- Branch: No
- Recommended Answer: id는 도메인 hook에서 closure로 캡처한다.
- Evidence: 공용 hook이 id를 받으면 current post/action 정책이 공용 레이어로 누수된다.

- Question: Dialog/pubsub까지 공용 hook에 포함해야 하는가?
- Branch: No
- Recommended Answer: 공용 hook은 async task runner까지만 담당한다.
- Evidence: Dialog message key와 refresh event는 DAO 도메인 정책이다.

## 검증 / 요청 처리
- `yarn lint`: 통과
- `./node_modules/.bin/tsc --noEmit`: 통과

## 리스크
- `useAsyncTask`는 단순 boolean loading이므로 병렬 task 카운팅은 하지 않는다. 기존 동작과 동일한 수준이며, 병렬 요청 요구가 생기면 별도 개선 대상이다.

## 핸드오프 메모
- watcher 리뷰 준비 완료
