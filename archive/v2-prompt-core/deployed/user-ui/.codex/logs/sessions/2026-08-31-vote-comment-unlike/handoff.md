# 인계

## 목표 및 현재 상태

- 목표: production 투표 상세 화면이 기존 댓글 좋아요 버튼의 `nextLiked`를 Logic Session mutation에 전달해, 좋아요 취소 클릭 시 DELETE 분기를 활성화한다.
- 현재 상태: DTO·parser·API·mutation·MSW·테스트는 `task/vote-comment-unlike`에서 구현·검증됐다. production UI 파일은 소유권 정책에 따라 수정하지 않았다.
- 인계 상태: `CLAUDE_HANDOFF_READY`

## 완료된 작업

- 투표 댓글 목록의 `likeCount`, `liked`를 검증하고 UI query 모델까지 보존했다.
- `voteClient.deleteVoteCommentLike(voteId, commentId)`를 추가했다.
- `useLikeMutation`은 `contentType === "vote" && nextLiked === false`에서 DELETE를 호출한다.
- mutation은 optimistic count 감소와 `liked: false`, 실패 snapshot 복구, 종료 후 comment root invalidation을 수행한다.
- API·hook·MSW 대상 14개 테스트와 전체 460개 테스트, lint, build가 통과했다.

## 대기 중인 작업

- `src/pages/citizen-participation/ui/CitizenParticipationDetailRoutes.tsx:97`의 `VoteDetailRoute` 콜백이 두 번째 인자를 전달하도록 수정한다.
- 기존 `src/pages/citizen-participation/ui/CitizenCommentRoutes.test.tsx`에 좋아요 취소의 `nextLiked: false`가 route를 거쳐 mutation 입력으로 전달되는 회귀 테스트를 추가한다.
- 필요한 변경은 다음 계약과 동등해야 한다.

```tsx
onLike={(commentId, nextLiked) =>
  likeMutation.mutate({ contentType: "vote", contentId, commentId, nextLiked })
}
```

- 시각 요소, 마크업, 스타일, `CommentList` props 계약은 변경하지 않는다.
- 연결 후 기존 명령으로 통합 검증한다.

## 결정 사항 및 제약 조건

- `CommentList`는 이미 `(commentId: string, nextLiked: boolean)`를 제공하고 버튼 클릭 시 현재 `liked`의 반대 값을 계산한다.
- `VoteDetailPage`와 중간 comment section은 이 콜백 계약을 이미 전달하므로 새 prop이나 UI 추상화가 필요하지 않다.
- Logic Session 변경은 현재 미커밋 상태다. 사용자에게 commit 요청을 받은 뒤 부모 브랜치에 commit하고, 그 후 Claude Code 자식 브랜치 생성에 대한 별도 승인을 받아야 한다.
- 자식 브랜치의 부모는 `task/vote-comment-unlike`, 직접 merge 대상도 `task/vote-comment-unlike`, 상위 계보는 `sy-main`이다.
- 다른 세션의 기능 로직 파일과 `.codex/logs/**`를 수정하거나 되돌리지 않는다.
- 프로젝트 정책상 스크린샷, 브라우저 자동화 캡처, 시각 QA를 수행하지 않는다.

## 관련 경로

- UI 수정 대상: `src/pages/citizen-participation/ui/CitizenParticipationDetailRoutes.tsx`
- UI 회귀 테스트 대상: `src/pages/citizen-participation/ui/CitizenCommentRoutes.test.tsx`
- 기존 콜백 원본: `src/features/citizen-participation/ui/parts/CommentList.tsx:17`
- Logic mutation: `src/features/citizen-participation/hook/useCitizenParticipationMutations.ts:104`
- API adapter: `src/features/citizen-participation/api/vote/vote.api.ts:58`
- hook 회귀 테스트: `src/features/citizen-participation/hook/useCitizenParticipationMutations.test.tsx`
- Logic Session 기록: `.codex/logs/sessions/2026-08-31-vote-comment-unlike/`

## 명령어 및 결과

| 명령어 | 결과 |
| --- | --- |
| 대상 Vitest 3개 파일 | 14 tests PASS |
| `npm run test` | 62 files, 460 tests와 governance 20 tests PASS |
| `npm run lint` | PASS |
| `npm run build` | PASS; 기존 chunk size 경고만 출력 |
| `git diff --check` | PASS |
| 일회성 Vite Node Axios/MSW 드라이버 | `true/3 → false/2`, `404 LIKE_NOT_FOUND` 관찰 |

## 다음 조치

1. 현재 부모 Logic Session 변경을 commit하도록 사용자에게 명시적 요청을 받는다.
2. 사용자가 Claude Code 자식 브랜치의 분기 기준·목적·merge 계보를 별도로 승인한다.
3. 최신 `CitizenParticipationDetailRoutes.tsx`와 `CitizenCommentRoutes.test.tsx`를 다시 읽고 위 콜백 연결 및 회귀 테스트만 수정한다.
4. `npm run test`, `npm run lint`, `npm run build`를 실행하고 결과를 Claude Code `handoff.md`에 갱신한다.
5. 사용자에게 UI 작업 완료를 알리고 Logic Session의 최종 통합 확인을 요청한다.
