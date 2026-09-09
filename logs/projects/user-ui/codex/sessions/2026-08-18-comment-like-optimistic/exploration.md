# 탐색

## 결론

현재 `postCommentLike`는 parent content의 `/{contentId}/likes`로 요청하고 comment ID를 받지 않으며, `useLikeMutation`은 content detail만 invalidate한다. 댓글별 좋아요를 위해 nested comment endpoint와 comment-root cache optimistic update가 필요하다.

## 현재 계약

- comment query key: `['citizenParticipation', type, 'comments', contentId, page]`
- root prefix: `citizenParticipationKeys.commentRoot(type, contentId)`
- cache value: `CommentListResponseDto`
- comment state: `CommentDto.likeCount`, `CommentDto.liked`
- UI presentation: `toCommentItem`이 현재 `liked`를 제거함
- UI heart: `CommentList`가 `♡ count`를 non-interactive span으로 렌더함

## 확정 계약

- endpoint: `POST /v1/api/citizen-participation/{collection}/{contentId}/comments/{commentId}/likes`
- body: 없음
- response data: `{ commentId, likeCount, liked }`
- toggle: 현재 `liked`가 false면 count 증가/true, true면 count 감소/false
- cache scope: 해당 `contentType/contentId` 아래 캐시된 모든 comment page

## TanStack Query 방식

1. `onMutate`: comment-root query 취소
2. 모든 matching page snapshot
3. 대상 댓글을 현재 `liked` 기준으로 `likeCount ± 1`, `liked` 반전 선반영
4. `onError`: snapshot 전체 복원
5. `onSuccess`: 서버 응답 count/state로 정확히 보정
6. `onSettled`: comment-root invalidate

## UI 인계 계약

- `CommentItem.liked?: boolean`
- `CommentListPropTypes.onLike?: (commentId: string, nextLiked: boolean) => void`
- Vote/Discussion/Policy detail page가 `onLike`를 `CommentList`로 전달
- route가 comment-like mutation의 `mutate(commentId)`를 callback으로 전달

## 제약

- production UI는 Claude Code 소유이므로 기능 로직 완료 후 사용자 확인 전 수정하지 않는다.
- 브라우저 자동화·시각 QA는 수행하지 않는다.
- 저장소에 기존 optimistic mutation 관례가 없어 TanStack Query v5 공식 snapshot/rollback 패턴을 따른다.

## 구현 후 확인

- Claude Code가 하트 버튼의 `aria-pressed`, 좋아요/취소 접근성 이름, pending 비활성화 계약을 구현했다.
- Hephaestus는 UI 파일을 수정하지 않고 Vote·Discussion·Policy route에 같은 `useLikeMutation` 계약을 연결했다.
- Policy 상세 route DOM 테스트에서 `3/false → 4/true → 3/false` 왕복을 확인했다.

## 임시 데이터 확장

- 공통 댓글 fixture를 2건에서 10건으로 늘리고 작성자·본문·좋아요 수·`liked` 상태를 다양화했다.
- content별 응답은 Vote 10건, Discussion 10건, Policy 8건, Proposal 10/4건, Survey 6건으로 구성했다.
- route의 `size: 10` 범위에서 Policy 댓글 8건과 하트 버튼 8개가 실제 렌더링된다.
