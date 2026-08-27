# 구현 로그

## 승인된 범위

- 댓글별 좋아요 POST와 optimistic cache 보정·rollback
- 눌린 하트 재클릭 시 좋아요 취소 토글
- Vote·Discussion·Policy 상세 route 연결
- production UI는 Claude Code 변경을 그대로 사용하고 Hephaestus는 기능·통합 파일만 수정

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `src/features/citizen-participation/api/comment/` | 댓글 ID가 포함된 likes endpoint와 typed 응답 계약 | `{ commentId, likeCount, liked }` 파싱 |
| `src/features/citizen-participation/hook/useCitizenParticipationMutations.ts` | 현재 `liked` 기준 `±1` optimistic 토글, 성공 보정, 실패 snapshot 복원 | 좋아요·취소 양방향 지원 |
| `src/features/citizen-participation/mocks/handlers.ts` | handler instance별 댓글 상태와 POST 토글 응답 | 연속 POST 후 GET 일관성 유지 |
| `src/pages/citizen-participation/model/presentation.ts` | `CommentDto.liked` 보존 | 하트 pressed 상태 표시 가능 |
| `src/pages/citizen-participation/ui/CitizenParticipationDetailRoutes.tsx` | Vote·Discussion callback와 pending ID 연결 | 댓글별 요청 실행 |
| `src/pages/citizen-participation/ui/CitizenReadDetailRoutes.tsx` | Policy callback와 pending ID 연결 | 정책 댓글 요청 실행 |
| `src/pages/citizen-participation/ui/CitizenDataRoutes.test.tsx` | 실제 Policy route 하트를 두 번 클릭 | `3/false → 4/true → 3/false` 확인 |
| `src/features/citizen-participation/mocks/fixtures.ts` | 댓글 fixture 10건과 content별 노출 수 구성 | Policy 8건, Vote·Discussion 10건 렌더링 데이터 제공 |

## 결정 사항

- 별도 DELETE endpoint 없이 확정된 POST endpoint가 현재 상태를 토글하고 최종 상태를 응답한다.
- optimistic update는 comment-root 아래 캐시된 모든 page에 적용한다.
- 서버 응답을 최종 기준으로 다시 보정하고 실패하면 mutation 직전 전체 snapshot을 복원한다.
- UI의 두 번째 `nextLiked` 인자는 현재 body 없는 toggle endpoint에는 전송하지 않는다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| `npx vitest run ...Mutations.test.tsx ...handlers.test.ts ...presentation.test.ts` | 3 files, 18 tests PASS |
| `npx vitest run src/pages/citizen-participation/ui/CitizenDataRoutes.test.tsx` | 2 tests PASS, 실제 좋아요·취소 왕복 확인 |
| `npm run lint` | PASS |
| `npm test` | 범위 테스트 포함 149 PASS, 범위 밖 auth 1건·meeting 2건 FAIL |
| `npm run build` | 범위 밖 `src/shared/ui/text-input/text-input.tsx:27` exact optional 타입 오류로 차단 |
| 변경 파일 pure LOC 측정 | 모두 250 이하, 최대 `presentation.ts` 231 |
| `lsp_diagnostics` | TypeScript LSP 미설치·사용자 설치 거절 상태로 실행 불가 |

## Watcher 인계

- 자동 Watcher/Evaluator 호출은 Anthropic 크레딧 부족으로 실행되지 않았다.
- `.codex/agents/watcher.toml`과 `policy-review-checklist`를 직접 적용한 범위 판정을 `review-log.md`에 기록했다.

## 추가 데이터 검증

- `npx vitest run handlers.test.ts CitizenDataRoutes.test.tsx useCitizenParticipationMutations.test.tsx`: 3 files, 15 tests PASS
- Policy route에서 `.cp-comment` 8개와 `button.cp-comment__like` 8개를 확인했다.
- `fixtures.ts`는 pure LOC 217의 데이터 테이블이므로 다음 데이터 확장 시 별도 comment fixture 모듈 분리를 검토한다.
