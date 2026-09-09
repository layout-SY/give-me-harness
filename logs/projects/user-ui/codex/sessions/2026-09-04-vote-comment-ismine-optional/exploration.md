# 탐색

## 요청

실제 vote comment 목록 API 응답이 Zod `client-contract`로 실패해 댓글이 화면에 렌더링되지 않는다. `isMine`을 당분간 optional로 두고 연관 코드를 맞춘다.

## 대상 관련 사실

- 실제 응답 `data.items[]`는 `id`, `authorName`, `content`, `createdAt`, `likeCount`, `likedByMe`, `updatedAt`과 `page`/`size`/`total`을 가진다. `isMine`은 없다.
- `voteCommentSchema`는 `isMine: z.boolean()`을 필수로 두었다. 항목 2개면 `invalid_type`/`expected: "boolean"` 이슈가 2개 난다.
- `parseVoteCommentList`는 먼저 `getVoteCommentListResponseSchema.parse`를 하므로 여기서 실패하면 목록 query가 error가 된다.
- `commentSchema`의 `isMine`은 이미 `z.boolean().optional()`이다.
- `useCitizenCommentActions.findManagedComment`는 `comment.isMine === true`만 내 댓글로 본다. `undefined`는 수정/삭제 대상이 아니다.
- `toCommentItem`은 `isMine`을 UI 모델로 넘기지 않는다. 목록 렌더링은 소유권 필드와 분리되어 있다.
- `voteComments.api.test.ts`의 `rejects a vote comment list item without ownership`은 `isMine` 없는 응답을 거절하도록 고정하고 있었다.

## 불러온 스킬

- `policy-git-branch-strategy`, `policy-index`, `policy-harness`
- `recipe-api-authoring`, `recipe-data-dto`
- `policy-coding-convention`, `policy-type-definition`, `policy-data-fetch-layer`
- `policy-documentation`, `policy-portfolio`, `policy-review-checklist`, `policy-abstraction-strategy`
- `policy-codex-native-quality`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| `src/shared/ui/` 공용 댓글 UI | 제외 | 이번 실패는 parser 계약이며 UI 마크업 변경이 아니다. |
| 기존 `CommentList` presentation | 재사용 | `toCommentItem`이 `isMine`을 사용하지 않아 목록 표시는 스키마만 완화하면 된다. |
| 신규 공용 추상화 | 제외 | optional 필드 하나이며 두 번째 사용처를 위한 새 어휘가 필요 없다. |

## 제약 조건 및 미확인 사항

- 백엔드가 `isMine`을 언제 필수로 넣을지는 사용자 설명 외에 배포 일정이 없다.
- 개발 콘솔 `[api-failure]`는 path를 `<field>`로 가린다. 이번 범위에서 진단 로그는 수정하지 않는다.
- 브라우저에서 실제 목록 화면을 다시 열지는 않았다. 검증은 parser 테스트와 빌드·린트다.

## 결론

필수 `isMine`만 실제 API와 어긋난다. `voteCommentSchema`를 optional로 바꾸고 거절 테스트를 성공 계약으로 바꾸면, parser·hook·UI는 추가 수정 없이 목록을 통과하고 소유권 동작만 필드 추가 전까지 비활성이다.
