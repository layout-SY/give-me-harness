# 구현 로그

## 결론

전역 API failure와 token-presence 인증 기반을 25개 파일에 구현하고 13개 atomic commit으로 구성했다. `task/admin-api-auth-foundation`을 `sy-main`에 `--ff-only`로 병합했으며 target HEAD는 `25f41f202d7bf042ae0cfddce9032b99bb904c72`다.

## 변경 사항

| 경로 | 변경 | 결과 |
| --- | --- | --- |
| `src/shared/api/error/**` | failure taxonomy, redacted diagnostics, module-level claim, 3초 dedupe FIFO queue | server·client-contract·transport·canceled가 typed 경계로 수렴 |
| `src/shared/api/axios-instance.ts` | HTTP error 보존, raw Axios console 제거, transport failure 상향 | transport는 report하지 않고 terminal이 표시 정책 결정 |
| `src/shared/lib/hooks/use-api.tsx` | `AbortSignal`, conditional 반환 계약, terminal reporting, 401 behavior 전달 | 기존 silent-default와 callback 동작 보존 |
| `src/app/providers/query-client.ts` | 5xx·transport retry와 Query·Mutation terminal reporter | 최종 실패만 report |
| `src/app/providers/api-error-dialog-bridge.tsx` | shared queue와 기존 Dialog 연결 | 일반 오류 FIFO 표시, 401 확인 후 session clear |
| `src/entities/auth/api/**` | Zod parser, injectable transport, signal 전달 | `any` 제거와 외부 응답 boundary parse |
| `src/features/auth/model/**`, `src/features/auth/use-auth.ts` | token write·clear·bootstrap, revision stale guard | access/refresh 단독 presence와 stale refresh 차단 |
| `src/app/index.tsx` | startup 전 URL credential bootstrap | credential query 제거 후 앱 startup |

## 주요 결정

- 동일 오류 객체는 module-level `WeakSet`으로 terminal 경계 전체에서 한 번만 처리한다.
- diagnostics는 allowlist context와 익명화한 issue만 기록한다.
- 401은 shared에서 route나 auth store를 참조하지 않고 `reauthenticate` queue event로 만든다.
- silent refresh 401은 presentation과 무관하게 재인증 queue로 보내고 sign-in 401만 `unauthorizedBehavior: "error"`로 caller-owned 처리한다.
- access token 또는 refresh token 중 하나가 있으면 presence는 true다.
- refresh 응답은 요청 당시 Zustand revision과 refresh token이 모두 현재 상태와 일치할 때만 commit한다.

## Watcher FAIL 후 수정

- 최초 Watcher는 refresh의 `silent: true`가 server 401을 presentation filter에서 소거한다고 판정했다.
- failing-first 테스트에서 실제 queue `[]`와 예상 `reauthenticate` event의 차이를 관찰했다.
- reporter의 401 분기를 presentation filter보다 먼저 실행하고 `useApi`가 typed `UnauthorizedBehavior`를 전달하도록 수정했다.
- sign-in만 `error`로 opt-out해 잘못된 자격증명 401의 caller-owned UX를 유지했다.
- 같은 Watcher 세션의 최종 판정은 PASS다.

## atomic commit과 병합

| commit | 메시지 |
| --- | --- |
| `a41fe7f` | `feat : API 오류 정규화 계약 정의` |
| `17187f4` | `feat : 서버 오류 표시 큐 추가` |
| `da5ac37` | `feat : API 오류 진단과 보고 추가` |
| `95a8910` | `feat : API 오류 모듈 공개` |
| `94e77d9` | `feat : Axios 오류 정규화 연결` |
| `4f869e9` | `feat : useApi 오류 보고 연결` |
| `c4200a2` | `feat : Query 최종 오류 처리 연결` |
| `1783b16` | `feat : 인증 API 응답 계약 정의` |
| `2140c30` | `feat : 인증 API 공개 계약 확장` |
| `c825586` | `feat : 토큰 존재 기반 인증 세션 추가` |
| `7a77067` | `feat : 인증 흐름을 세션 경계에 연결` |
| `e6f5bea` | `feat : 인증 세션 bootstrap 연결` |
| `25f41f2` | `feat : API 오류 Dialog bridge 연결` |

- source와 target 시작 HEAD: `ad687ac00c897163046d27b2f48bf9f2ae55d5b3`
- merge 방식: `git merge --ff-only task/admin-api-auth-foundation`
- merge 결과: `sy-main@25f41f202d7bf042ae0cfddce9032b99bb904c72`
- push 및 원격 브랜치 작업: 수행하지 않음

## 사후 검증

| 검증 | 결과 |
| --- | --- |
| `npm run build` | TypeScript·Vite build 성공, 기존 대형 chunk warning만 출력 |
| 신규 6개 테스트 | 25 tests, 25 pass, 0 fail |
| `TSX_DISABLE_CACHE=1`, `TSX_TSCONFIG_PATH=tsconfig.app.json`, `--test-concurrency=1` 전체 suite | 73 tests, 73 pass, 0 fail |
| 변경 source·신규 tests targeted ESLint | 0 errors, 부모 기준선 warning 1건 |
| `git diff --check ad687ac..HEAD` | 통과 |
| target 상태 | clean `sy-main@25f41f2`, source HEAD 포함 |

## 검증 환경 기록

- 외부 worktree를 Bash tool의 직접 `workdir`로 사용하면 실행 전 hook이 없는 `.claude/hooks/harness_hook.py`를 찾으면서 명령이 시작되지 않았다.
- `npm --prefix ... exec -- node`는 child cwd를 바꾸지 않고 별도 `node` package를 해석해 검증 경로로 사용하지 않았다.
- 원본 project cwd에서 harness를 통과한 뒤 child zsh만 외부 `sy-main` worktree로 이동시켜 동일 검증을 완료했다.
- source instrumentation, debugger port, tmux, 임시 fixture는 만들지 않았다.

## 기존 비차단 부채

- 기본 병렬 suite의 Vite/Rolldown native child는 비결정적으로 `SIGBUS`가 발생한 기록이 있다. 실패 파일과 통과 여부가 이동해 이번 앱 회귀로 분류하지 않았다.
- no-excuse helper는 project TypeScript 6.0.2에 없는 `typescript/unstable/*` API를 요구해 실행하지 못했다.
- whole lint 기준선은 71 errors·5 warnings이며 이번 targeted lint는 0 errors다.
- 사용자 지시와 프로젝트 정책에 따라 브라우저·시각 QA를 수행하지 않았다.
