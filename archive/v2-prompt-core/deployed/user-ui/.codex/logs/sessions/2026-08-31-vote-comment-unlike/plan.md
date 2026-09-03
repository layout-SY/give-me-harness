# 계획

## 목표

- 시민 투표 댓글의 현재 좋아요 상태를 목록 응답부터 UI mutation 경계까지 보존한다.
- 좋아요 상태에서 다시 누르면 인증된 `DELETE /citizen/votes/{voteId}/comments/{commentId}/likes` 요청을 보내고, 즉시 감소한 화면 상태를 실패 시 복구한 뒤 서버 상태로 재동기화한다.
- production UI 수정이 필요한 경계를 Claude Code가 이어받을 수 있도록 구체적인 인계서를 제공한다.

## 범위

- 투표 댓글 DTO와 parser의 `likeCount`, `liked` 필드
- 투표 댓글 좋아요 취소 API 어댑터
- TanStack Query mutation의 DELETE 분기, optimistic update, rollback, invalidation
- Axios·MSW·hook 회귀 테스트와 투표 댓글 mock 상태
- Logic Session 필수 문서와 Claude Code UI 인계

## 제외 사항

- `src/**/ui/**` production UI 직접 수정
- 패키지 추가 또는 빌드 설정 변경
- 사용자 승인 전 commit, merge, 브랜치 삭제
- 투표 외 댓글 API 계약 변경

## 제약 조건

- Logic Session은 API, parser, hook, mock 등 기능 로직만 소유한다.
- Claude Code가 production UI를 수정하려면 별도 자식 브랜치 승인과 파일 소유권 계약을 따라야 한다.
- 이미지 캡처, 브라우저 자동화, 시각 QA는 프로젝트 정책상 실행하지 않는다.
- TypeScript LSP가 설치되지 않았으므로 `npm run build`의 `tsc -b`를 타입 검증 근거로 사용한다.

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 계보·범위 확인 | Planner | `policy-git-branch-strategy`, `git-master` | `sy-main` 기준 작업 브랜치와 승인 범위 확정 |
| 계약 탐색 | Planner | `skill-index`, `reference-index`, `reference-components`, `recipe-api-authoring` | 기존 API·UI 콜백·cache 경계 재사용 결정 |
| DTO·API 구현 | Generator | `programming`, `policy-coding-convention`, `policy-type-definition`, `policy-data-fetch-layer` | 응답 상태 보존과 인증 DELETE 전송 |
| mutation 구현 | Generator | `policy-hook-extraction`, `policy-validation` | optimistic update·rollback·재조회 |
| 독립 판정 | Watcher | `policy-review-checklist` | 승인 범위의 PASS/FAIL 및 근거 기록 |
| 장기 평가 | Evaluator | `policy-portfolio`, `policy-documentation` | 기술 부채와 재사용 가능성 분리 기록 |

## 검증

- 실패하는 회귀 테스트로 DELETE 미구현과 rollback 누락을 먼저 재현한다.
- 대상 API·hook·MSW 테스트를 실행한다.
- 최종 상태에서 `npm run test`, `npm run lint`, `npm run build`, `git diff --check`를 실행한다.
- Axios가 실제 MSW DELETE handler를 통과해 200/null과 404/`LIKE_NOT_FOUND`를 관찰하는 것을 사용 표면 검증으로 삼는다.

## 위험 요소 및 결정 사항

- 기존 `CommentList`는 `(commentId, nextLiked)`를 제공하지만 `VoteDetailRoute`가 두 번째 인자를 버린다. Logic Session에서는 hook 입력을 임시 optional로 유지하고 UI 연결은 Claude Code에 인계한다.
- DELETE 성공 응답의 `data`가 `null`이므로 기존 POST 응답 schema로 파싱하지 않고 `null`을 mutation 결과로 사용한다.
- 실패 시 하나의 page만 복원하면 동일 comment root 아래 다른 cache가 어긋날 수 있으므로 `getQueriesData` snapshot 전체를 복원한다.

## 승인

- 상태: approved
- 구현 승인: 사용자가 `Proceed`로 승인했다.
- 브랜치 승인: 사용자가 `task/vote-comment-unlike`를 `sy-main@fde3693`에서 생성하고 직접 merge 대상으로 `sy-main`을 사용하는 설정을 승인했다.
- 필수 문구: `이 계획대로 진행할까요, 아니면 조정할 부분이 있나요?`
