# 탐색

## 요청

- 투표 댓글 좋아요 취소 API를 실제 요청 흐름에 연결한다.
- 좋아요 수를 낙관적으로 감소시키고 요청 실패 시 원래 상태로 복구한다.
- UI 수정이 필요한 경우 Logic Session이 직접 수정하지 않고 Claude Code용 인계를 제공한다.

## 대상 관련 사실

- `voteApi`는 투표 목록·상세·댓글 목록·투표 제출을 담당하지만 댓글 좋아요 DELETE 메서드는 없었다.
- 투표 댓글 응답 schema와 `parseVoteCommentList`가 서버의 `likeCount`, `liked`를 버려 UI가 현재 상태를 알 수 없었다.
- `CommentList`의 `onLike` 계약은 이미 `(commentId: string, nextLiked: boolean)`이고 버튼은 `comment.liked !== true`를 전달한다.
- `VoteDetailRoute`는 `onLike={(commentId) => ...}`로 두 번째 인자를 버리고 있었다.
- 기존 `useLikeMutation`은 모든 요청을 POST로 보내고 성공 응답으로 cache를 갱신했으며 optimistic update와 rollback은 없었다.
- TanStack Query v5 공식 문서의 `onMutate` snapshot, `onError` rollback, `onSettled` invalidation 흐름이 현재 요구와 일치했다.

## 불러온 스킬

- `policy-git-branch-strategy`, `git-master`
- `skill-index`, `reference-index`, `reference-components`
- `programming`, `policy-coding-convention`, `policy-type-definition`
- `policy-data-fetch-layer`, `recipe-api-authoring`, `policy-hook-extraction`, `policy-validation`
- `policy-documentation`, `policy-review-checklist`, `policy-portfolio`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| 새 공용 UI 컴포넌트 | 사용하지 않음 | 시각 요소 추가가 아니라 기존 댓글 좋아요 콜백 연결 작업이다. |
| `CommentList`의 `onLike` 계약 | 재사용 | `nextLiked`가 이미 정의되고 실제 버튼 클릭에서 계산된다. |
| `CommentContent` | 변경하지 않음 | 표시 구조와 접근성 계약은 이번 API 연결과 무관하다. |

## 제약 조건 및 미확인 사항

- production UI는 Claude Code 소유이므로 `VoteDetailRoute`를 이번 Logic Session에서 변경할 수 없다.
- 실제 서버와 인증된 계정은 제공되지 않아 회사 API에 대한 실환경 호출은 실행하지 않았다.
- TypeScript LSP는 설치되지 않았고 설치 승인이 없어 진단을 실행할 수 없었다.
- 빌드는 기존 대형 chunk 경고를 출력하지만 exit code 0이며 이번 변경에서 번들 구조를 수정하지 않았다.

## 결론

- 기존 API·DTO·hook 계층에 최소 변경을 적용하고 새 UI 추상화는 만들지 않는다.
- 투표 댓글의 명시적 `nextLiked === false`만 DELETE로 분기하고, cache는 클릭 즉시 갱신한 뒤 오류 시 snapshot으로 복구한다.
- 서버 최종 상태는 mutation 종료 후 comment root invalidation으로 재조회한다.
- UI에서는 기존 콜백의 두 번째 인자를 `useLikeMutation`에 전달하는 한 곳의 연결만 필요하므로 Claude Code에 인계한다.
