# 탐색

## 요청

- 기존 좋아요 상태인 투표 댓글을 다시 누를 때 DELETE API를 호출하고, UI 상태를 낙관적으로 감소시키며 404에서 rollback하도록 복원한다.

## 대상 관련 사실

- `CommentDto`와 투표 댓글 목록 parser/cache는 `likedByMe`를 사용한다.
- UI `CommentItem`과 mutation 응답은 `liked`를 사용한다.
- `toCommentItem()`이 `comment.liked`를 참조해 `a32b462` 이후 목록의 좋아요 상태를 UI에 전달하지 못했다.
- `useCitizenParticipationMutations.ts`에는 `nextLiked === false` DELETE 분기, `likeCount - 1` 낙관적 갱신, `onError` cache snapshot rollback, `onSettled` invalidation이 이미 있었다.
- DELETE endpoint는 `/citizen/votes/{voteId}/comments/{commentId}/likes`, 성공은 HTTP 200과 `data: null`, 이력이 없으면 404 `LIKE_NOT_FOUND`다.

## 불러온 스킬

- `policy-git-branch-strategy`
- `programming`
- `skill-index`, `policy-index`, `recipe-index`, `reference-index`
- `policy-harness`, `policy-coding-convention`, `policy-type-definition`
- `policy-validation`, `policy-data-fetch-layer`, `policy-hook-extraction`
- `policy-review-checklist`, `policy-documentation`, `policy-portfolio`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| 기존 댓글 좋아요 UI | 변경하지 않음 | UI 마크업과 상호작용 계약은 이미 존재하고, 문제는 DTO-to-UI adapter 경계에 있었다. |
| 신규 공용 UI | 도입하지 않음 | 시각 요소나 공용 컴포넌트가 필요한 작업이 아니다. |

## 제약 조건 및 미확인 사항

- production UI 파일은 수정하지 않는다.
- TypeScript LSP는 설치 거절 상태라 사용할 수 없으며 `npm run build`의 `tsc -b`로 대체한다.
- 실제 backend가 연결된 브라우저 수동 검증은 수행하지 않고 MSW 라우트 통합 테스트로 표면 동작을 검증한다.
- `presentation.ts` 등 일부 파일의 기존 크기는 이번 1줄 adapter 수정과 별개인 후속 리팩터링 후보다.

## 결론

- 원인은 mutation이나 API가 아니라 `toCommentItem()`의 필드 명칭 불일치다.
- 가장 작은 수정은 `comment.likedByMe`를 UI `liked`로 변환하고, fixture·테스트를 실제 목록 DTO 계약에 맞추는 것이다.
