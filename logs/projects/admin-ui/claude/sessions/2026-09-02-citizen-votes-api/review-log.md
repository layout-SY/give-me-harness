# 검토 로그

## 현재 Watcher 판정

PASS

공유 worktree 소유권을 적용해 승인된 citizen-votes 작업 pathspec만 판정했다. 승인 경로 안에서는 차단 결함이나 미해결 회귀가 없다. `yarn.lock`은 이 작업이 소유하지 않는 동시 세션 잔여물이며 검토·수용·수정·stage 대상에서 명시적으로 제외한다. 이 문서는 전체 worktree를 단일 소유로 간주했던 이전 판정을 최신 scoped 판정으로 전면 대체한다.

## 승인된 검토 pathspec

```text
package.json
package-lock.json
src/entities/cp-vote/**
src/pages/cp-vote/**
src/mocks/cp-vote.handlers.ts
tests/citizen-votes-contract.test.mjs
tests/citizen-votes-msw.test.mjs
tests/cp-date-input-boundaries.test.mjs
.codex/logs/sessions/2026-09-02-citizen-votes-api/**
```

- 현재 브랜치: `task/connect-citizen-votes-api`
- 작업 목적: 시민투표 목록·상세를 실제 `GET /citizen/votes` 계약에 연결하고 조회 기준으로 화면 소비 모델과 MSW를 정합화
- 분기 기준·직접 merge 대상: `sy-main`
- 승인 시점 parent HEAD 및 현재 merge-base: `e26b263afe2478cbabd3e34fdc82306e0715d059`
- 현재 branch config의 scope 목록과 위 pathspec이 일치한다.

## 승인 경로 발견 사항

없음.

## 점검 결과

| 점검 | 결과 | 근거 |
| --- | --- | --- |
| stale-test 회귀 | 충족 | `tests/cp-date-input-boundaries.test.mjs:16-24`에서 삭제된 시민투표 mutation schema 등록이 제거됐고 시민토론 날짜 경계만 남았다. 직접 실행한 16-test에서 해당 2개 테스트를 포함해 모두 성공했다. |
| tsx loader 수명주기 | 충족 | `tests/citizen-votes-contract.test.mjs:2-15`와 `tests/citizen-votes-msw.test.mjs:4-17`은 Vite server 없이 `tsx/esm/api`의 `tsImport`를 사용한다. MSW test는 자신이 생성한 mock server만 종료하며 Node `v22.20.0`에서 crash 없이 정상 종료됐다. |
| 실제 API·serialization | 충족 | `src/entities/cp-vote/api/cp-vote.api.ts:8-25`는 목록·상세 GET만 제공하고 목록 배열 query에 `paramsSerializer: { indexes: null }`을 사용한다. contract test는 `/citizen/votes`, `/citizen/votes/12`, serializer 설정을 검증하고 MSW test는 반복 sort를 실제 `fetch`로 전달한다. |
| AbortSignal·query key·ID | 충족 | 목록·상세 TanStack Query signal이 API의 `withAbortSignal`까지 전달된다. 상세는 양의 정수 ID 또는 `null` key를 사용하고 유효 ID에서만 query를 활성화한다. |
| schema·parser·pagination | 충족 | `src/entities/cp-vote/api/cp-vote.dto.ts:5-54`는 실제 5개 상태, 허용 sort, 기본 page 1/size 20/sort, size 100 상한, 실제 목록·상세 필드와 집계 합계를 Zod로 검증한다. parser는 응답을 보존하고 pageCount를 계산한다. |
| controller·loading·retry·navigation | 충족 | query state는 지원되는 page/sort만 유지한다. controller는 placeholder 중 row action 제한, 초기 오류 retry, page 변경 선택 초기화, 숫자 ID 상세 이동, 상세 오류 Dialog와 목록 이동을 제공한다. |
| read-only UI·재사용·접근성 | 충족 | mutation/search API·hook·controller·UI 표면이 제거됐고 실제 응답 필드만 표시한다. 기존 `Table`, `Loading`, `Button`, `DefinitionList`, `RatioBar` 등을 재사용하며 신규 자체 interactive primitive는 없다. 브라우저 기반 검증은 사용자 지시에 따라 수행하지 않았다. |
| mock·오류 계약 | 충족 | `src/mocks/cp-vote.handlers.ts`는 `/citizen/votes` 목록·상세 GET과 반복 sort, pagination, 400/401/404 status/body를 구현하며 MSW test가 observable HTTP 동작을 검증한다. |
| 타입 안전·legacy 제거 | 충족 | 승인된 시민투표 source/tests에서 `any`, type suppression, non-null assertion, legacy `/v1/cp/votes`, 삭제된 mutation schema/hook, guessed write endpoint 및 placeholder backend 필드를 찾지 못했다. 대상 ESLint도 성공했다. |
| npm package 범위 | 충족 | `package.json:49`는 loader용 `tsx: ^4.23.13`을 추가한다. `package-lock.json:7-52,5272-5273`은 현재 manifest와 root dependency를 동기화하고 `tsx` 4.23.13을 고정한다. `npm ci --dry-run --ignore-scripts`, build, tests가 성공했다. npm-generated lockfile 동기화는 승인된 두 package 파일 범위 안에서 수용한다. |

## 직접 실행한 검증 근거

승인 입력이 바뀌지 않았다는 현재 요청의 소유권 확인과 최신 `git status`/pathspec 목록을 대조했으며, 직전 Watcher가 같은 승인 파일 상태에서 직접 실행한 다음 결과를 유지한다. 불필요한 고비용 검증은 반복하지 않았다.

- `node --version && node --test tests/cp-date-input-boundaries.test.mjs tests/citizen-votes-contract.test.mjs tests/citizen-votes-msw.test.mjs`: Node `v22.20.0`, 16/16 성공, crash 없이 종료.
- `npm run build`: 성공. `tsc -b`와 Vite build 완료; 기존 대형 chunk 경고만 출력.
- 승인된 변경 TypeScript/TSX/MJS 21개 대상 `npm exec eslint -- ...`: 성공, 출력 없음.
- `npm ci --dry-run --ignore-scripts`: exit 0.
- `GIT_MASTER=1 git diff --check`: 성공, 출력 없음.
- 이번 재판정에서 `GIT_MASTER=1 git status --short --branch`, branch scope, 승인 pathspec의 `git diff --name-status`, 별도 `yarn.lock` name-status를 다시 확인했다.

## `yarn.lock` 소유권 및 명시적 제외

- 현재 status에 `M yarn.lock`이 존재하는 사실은 직접 확인했다.
- branch config 승인 scope와 위 검토 pathspec에는 `yarn.lock`이 없다.
- 사용자가 제공한 공유-worktree 근거에 따르면 이 파일은 parent가 package lock을 수정한 뒤 다른 활성 세션/프로세스가 만든 동시 변경이며 parent는 Yarn을 실행하지 않았다.
- 따라서 이 판정은 `yarn.lock`의 내용이나 품질을 수용했다는 뜻이 아니다. 이 파일은 **미소유·미검토 동시 작업 잔여물**로 분류한다.
- 이 citizen-votes 작업의 stage/commit은 반드시 위 승인 pathspec을 명시적으로 사용하고 `yarn.lock`을 포함하지 않아야 한다.
- Watcher는 `yarn.lock`을 읽어 소유권을 재판정하거나 수정·복원·stage하지 않았다. 현재 상태 그대로 해당 소유자에게 남긴다.

## 잔여 한계

- 브라우저, Playwright, 스크린샷, 캡처, 시각 QA, 실제 인증 backend 호출은 사용자 지시에 따라 수행하지 않았다.
- 전체 worktree가 clean하다는 판정이 아니라, 공유 worktree에서 승인된 citizen-votes pathspec만 통과했다는 판정이다.

## 결론

승인된 citizen-votes 목록·상세 read-only diff는 기능, 타입, 요청 계약, loader 수명주기, 회귀 테스트, build, 정적 분석 및 npm lockfile 기준을 충족한다. downstream은 승인 pathspec만 사용해 Evaluator와 path-specific commit 절차를 진행할 수 있으며, `yarn.lock`은 반드시 untouched·unstaged 상태로 제외해야 한다.
