# 구현 로그

## 승인된 범위

- 브랜치: `task/vote-comment-unlike`
- 부모 및 직접 merge 대상: `sy-main`
- 구현 범위: 투표 댓글 DTO·parser·API·mutation·MSW·테스트와 세션 문서
- 제외 범위: production UI, 패키지 설정, commit·merge·브랜치 정리

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `src/features/citizen-participation/api/vote/vote.dto.ts` | 투표 댓글 schema에 `likeCount`, `liked` 추가 | 서버 좋아요 상태를 타입 경계에서 검증 |
| `src/features/citizen-participation/api/http/citizenParticipation.parser.ts` | 두 필드를 공용 댓글 모델로 매핑 | UI query 데이터에 상태 보존 |
| `src/features/citizen-participation/api/vote/vote.api.ts` | 인증 설정을 사용하는 DELETE 메서드 추가 | 정확한 vote/comment 경로로 취소 요청 전송 |
| `src/features/citizen-participation/hook/useCitizenParticipationMutations.ts` | DELETE 분기, snapshot, optimistic update, rollback, invalidation 추가 | 즉시 반영과 오류 복구를 함께 제공 |
| `src/features/citizen-participation/mocks/voteCommentFixtures.ts` | fixture에 좋아요 상태 추가 | 성공·실패 상태 재현 가능 |
| `src/features/citizen-participation/mocks/commentHandlers.ts` | 투표 댓글 상태 저장과 DELETE 200/404 handler 추가 | 취소 후 목록 재조회까지 실제 mock 상태 반영 |
| `src/features/citizen-participation/api/http/voteComments.api.test.ts` | 필드 보존과 DELETE 요청 계약 검증 | transport 회귀 방지 |
| `src/features/citizen-participation/hook/useCitizenParticipationMutations.test.tsx` | 성공 optimistic 감소와 404 rollback 검증 | cache 상태 전이 회귀 방지 |
| `src/features/citizen-participation/mocks/voteComments.handlers.test.ts` | 200/null, 목록 재조회, `LIKE_NOT_FOUND` 검증 | Axios/MSW 사용 표면 확인 |

## 결정 사항

- DELETE 성공 응답은 schema 파싱 대상이 없는 `null`이므로 성공 분기에서 서버 결과로 cache를 다시 덮지 않는다.
- 좋아요 추가 POST의 기존 서버 응답 처리 흐름은 보존한다.
- `nextLiked`는 Claude UI 연결 전 기존 route의 타입 호환을 위해 optional로 두었다. UI 인계 후 required 전환 여부는 별도 개선 사항이다.
- rollback 대상은 하나의 query가 아니라 comment root 아래 모든 matching query snapshot이다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| 변경 전 대상 3개 테스트 | 3 files, 11 tests PASS |
| 회귀 테스트 우선 실행 | parser 필드 누락, DELETE 부재, POST 오호출, 404 오호출의 예상 실패 4건 확인 |
| `npm exec vitest -- run ...voteComments.api.test.ts ...useCitizenParticipationMutations.test.tsx ...voteComments.handlers.test.ts` | 3 files, 14 tests PASS |
| `npm run test` | 62 files, 460 Vitest tests와 20 governance hook tests PASS |
| `npm run lint` | PASS, 오류·경고 없음 |
| `npm run build` | PASS, `tsc -b`와 Vite build exit code 0; 기존 대형 chunk 경고만 출력 |
| `git diff --check` | PASS, 출력 없음 |
| 일회성 Vite Node Axios/MSW 드라이버 | PASS, 댓글 상태 `liked: true, likeCount: 3`에서 `liked: false, likeCount: 2`로 변경되고 미좋아요 취소는 `404 LIKE_NOT_FOUND`로 관찰 |
| `lsp_diagnostics` | TypeScript LSP 미설치 및 설치 거절 상태로 실행 불가; `tsc -b`로 대체 |

## Watcher 인계

- DTO에서 `liked`, `likeCount`가 parser를 통과하는지 확인한다.
- vote + `nextLiked: false`에서만 DELETE가 호출되고 POST가 호출되지 않는지 확인한다.
- `onMutate` 직후 count 감소와 `liked: false`가 보이며, 404 시 모든 snapshot이 복구되는지 확인한다.
- 성공·실패 모두 `onSettled`에서 comment root가 invalidate되는지 확인한다.
- Logic Session의 PASS와 production UI 연결 완료를 구분해 판정한다.
