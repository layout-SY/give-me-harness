# 구현 로그

## 승인된 범위

- 브랜치: `task/domain-pattern-alignment-logic`
- 부모·직접 merge 대상: `sy-main@3f5b4d4b31992d421a02bc44b97276e6863ee05e`
- 승인 경로: validation, 지정 CP API DTO/parser/hook, `tests`, 이 세션 문서와 `.omo` evidence/plan/ledger.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `src/shared/lib/validation/index.ts` | `isoCalendarDateSchema` 추가 | 실제 존재하는 ISO 달력 날짜만 허용 |
| `src/entities/cp-discussion/api/cp-discussion.dto.ts` | 조회 시작·종료일과 처리 종료일에 공용 schema 적용 | 응답 날짜 계약 변경 없이 입력 강화 |
| `src/entities/cp-vote/api/cp-vote.dto.ts` | 조회 시작·종료일과 처리 종료일에 공용 schema 적용 | 응답 날짜 계약 변경 없이 입력 강화 |
| comment/proposal DTO | 지정 query/process schema에 `.strict()` 적용 | 입력 extra key 거부, 응답 extra key 허용 유지 |
| board/report DTO | 지정 query schema에 `.strict()` 적용 | 입력 extra key 거부, 기존 strict 응답 유지 |
| `src/entities/cp-board/api/cp-board.parser.ts` | `parseCpBoardBulkHide` 추가 | 배열 성공, malformed/non-array 실패 |
| `src/entities/cp-board/api/index.ts` | parser 공개 export | hook이 API 공개 경계를 사용 |
| `src/entities/cp-board/hook/use-cp-board-bulk-hide-mutation.ts` | local Zod schema를 공개 parser로 교체 | API→unwrap→parse와 cache callback 유지 |
| `tests/*.test.mjs` | 실제 Vite 모듈 회귀 테스트 4개 추가 | 날짜·strictness·응답·parser 계약 13개 고정 |

## 결정 사항

- 날짜 validation은 두 도메인이 의미·생명주기·변경 압력을 공유하므로 공용 schema로 두었다.
- `.strict()`는 명시된 입력에만 적용해 서버 응답의 forward-compatible extra key를 손상시키지 않았다.
- parser 이동은 소유권 정렬에 한정하고 mutation cache 구현은 재작성하지 않았다.
- full lint/test baseline을 고치기 위해 package나 범위 밖 파일을 수정하지 않는 안을 사용자가 승인했다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| `node --test tests/cp-date-input-boundaries.test.mjs tests/cp-comment-proposal-input-boundaries.test.mjs tests/cp-board-report-input-boundaries.test.mjs tests/cp-board-bulk-hide-parser.test.mjs` | exit 0, 13/13 통과 |
| `npm run build` | exit 0, `tsc -b && vite build` 성공 |
| 변경 TypeScript 10개 대상 `./node_modules/.bin/eslint` | exit 0, 출력 없음 |
| `GIT_MASTER=1 git diff --check` | exit 0, 출력 없음 |
| `npm run lint` | exit 1, 변경 밖 기존 73 errors와 5 warnings |
| `npm run test` | exit 1, `package.json`에 script 부재 |

## Watcher 인계

- Attempt 1: 행동·범위 계약 PASS, 계획 gate 불일치로 FAIL.
- 사용자 결정: baseline-aware gate 승인.
- Attempt 2: `ses_fb9ba9b04ffe1bQ1pIpnp5Hoqn`, 최종 PASS, branch 결함 없음.
- 정본 evidence: `.omo/evidence/domain-pattern-alignment/watcher/attempt-2/`.

## 병합 및 사후 검증

- `task/domain-pattern-alignment-logic@5aa158a42669aef832f0031790ba964a164c88ff`를 `sy-main@3f5b4d4b31992d421a02bc44b97276e6863ee05e`에 `git merge --ff-only`로 병합했다.
- 병합 후 `sy-main` HEAD는 source와 동일한 `5aa158a42669aef832f0031790ba964a164c88ff`이며 worktree는 clean이다.
- 병합 후 실제 모듈 테스트 13/13, `npm run build`, 변경 TypeScript 10개 ESLint, `3f5b4d4..HEAD` diff-check가 모두 exit 0이었다.
- 사용자 지시에 따라 Claude Code를 사용하지 않았다. `oh-my-openagent`의 Claude Code 호환 command만 공식 user-level 설정으로 임시 비활성화하고 native OpenCode branch guard 아래에서 merge를 실행했으며, 정리 완료 후 임시 설정을 제거했다.
- source와 merge linked worktree를 제거하고 `git branch -d task/domain-pattern-alignment-logic`로 로컬 source branch를 안전 삭제했다. root의 다른 session 소유 dirty UI 파일 3개는 그대로 보존했다.
