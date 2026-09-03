# 계획

## 목표

댓글 하트 클릭 시 특정 댓글 좋아요 POST 요청을 보내고, 현재 `liked` 상태에 따라 TanStack Query comment cache를 증가 또는 감소시킨 뒤 서버 응답으로 보정하며 실패 시 이전 cache로 rollback하는 토글 기능을 구현한다.

## 범위

- `POST /{collection}/{contentId}/comments/{commentId}/likes` typed API 계약
- `{ commentId, likeCount, liked }` Zod 응답 parser
- content별 모든 paginated comment cache optimistic update·snapshot·rollback·revalidation
- 이미 좋아요한 댓글을 다시 누를 때 `likeCount - 1`, `liked: false`로 선반영하는 취소 흐름
- MSW handler instance별 댓글 좋아요 상태와 GET 일관성
- `CommentDto.liked`를 presentation 경계까지 보존
- vote·discussion·policy route에서 사용할 comment-like mutation 공개 API

## 제외 사항

- 사용자 확인 전 `src/features/citizen-participation/ui/**` production UI 파일 수정
- 댓글 작성·신고 기능 변경
- 다른 세션 소유 파일 수정

## 역할과 스킬

| 구간 | 역할 | 스킬 | 결과 |
| --- | --- | --- | --- |
| 탐색 | Hephaestus + Explore | `recipe-api-authoring`, `reference-custom-hooks` | endpoint·cache·UI contract |
| 구현 | Hephaestus | `programming`, `policy-data-fetch-layer` | API·MSW·optimistic hook |
| UI 인계 | 사용자 중계 + Claude Code | `project-ui` | heart button callback props |
| 검토 | Watcher 문서 판정 | `policy-review-checklist` | PASS/FAIL 근거 |

## 검증

- API/MSW POST 후 GET count 일치
- 요청 pending 중 현재 상태에 따라 cache `likeCount ± 1`, `liked` 반전
- 요청 실패 시 전체 comment page snapshot rollback
- 성공 응답의 정확한 count/state로 cache 보정
- focused Vitest, `npm run build`, `npm run lint`

## 승인

- 상태: approved
- 근거: 사용자의 `오케이. 현재 기능에 댓글 기능에서 하트를 클릭하면... 구현해.`
- 범위 확장 근거: 사용자의 `눌러져 있던 하트(좋아요)를 다시 누르면 하트 취소하는 거까지 추가 구현`
