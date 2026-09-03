# 구현 로그

## 승인된 범위

- `src/app/providers`
- `src/shared/api/error`
- `src/features/citizen-participation/api`
- `src/features/citizen-participation/mocks`
- `.codex/logs/sessions/2026-08-31-login-me-routing`

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `src/app/providers/AuthRouteBoundary.tsx` | 비로그인 보호 경로에서 직접 `<Navigate>`하지 않고 재인증 이벤트를 한 번 발행하도록 변경 | 최초 진입 콘텐츠를 차단하고 기존 전역 Dialog 흐름으로 안내 |
| `src/app/providers/AuthRouteBoundary.test.tsx` | 비로그인 차단, 이벤트 발행, 만료 시점 회귀 테스트 갱신 | 보호 경계 단위 동작 고정 |
| `src/app/providers/AuthRouteBoundary.reauthentication.test.tsx` | Dialog 확인 후 이동, 안전한 `returnTo`, 만료·큐 조정 회귀 테스트 추가·갱신 | 실제 재인증 조정 흐름 고정 |
| `src/shared/api/error/server-error-message.ts` | 인증 안내 문구를 `로그인 후 이용해 주세요.`로 변경 | 사용자 요구 문구를 단일 상수에서 제공 |
| `src/shared/api/error/server-error-message.test.ts` | 안내 문구 계약 갱신 | 상수 회귀 방지 |
| `src/shared/api/error/api-failure-reporter.test.ts` | 401 재인증 이벤트 기대 문구 갱신 | 기존 API 실패 흐름과 문구 일치 |
| `src/features/citizen-participation/api/me/me.api.ts` | `getMe()` 경로를 `/citizen/me`에서 `/me`로 변경 | current-user endpoint 수정 |
| `src/features/citizen-participation/api/http/citizenParticipation.api.test.ts` | current-user 실제 요청 pathname 검증 추가 | `/me` 계약 고정 |
| `src/features/citizen-participation/mocks/handlers.ts` | current-user MSW handler를 `*/me`로 변경 | 브라우저 mock과 production adapter 계약 일치 |

## 결정 사항

- 신규 모달을 만들지 않고 기존 `serverErrorQueue` → `ApiErrorDialogBridge` → `Dialog` 흐름을 재사용했다.
- 보호 경계는 위치나 인증 정보를 큐 이벤트에 싣지 않는다. `ApiErrorDialogBridge`가 확인 시점의 현재 위치를 `createAuthReturnState()`로 정제해 `returnTo`로 전달한다.
- 기존 인증 세션이 열린 보호 경로에서 만료될 때는 재인증 Dialog가 활성화된 동안 콘텐츠를 유지한다. 최초 비로그인 진입은 콘텐츠를 즉시 차단한다.
- `hasRequestedReauthentication` ref로 Dialog 확인 과정의 `acknowledge → clear → navigate` 사이에 같은 이벤트가 재발행되는 것을 막았다.
- `/citizen/me/activity`는 별도 활동 리소스 계약이므로 변경하지 않았다.

## 브라우저 디버깅 저널

- 런타임: Node.js로 실행한 Vite production preview, `127.0.0.1:4174`
- 진입 경로: `/citizen-participation/votes/2?tab=summary#comments`
- 읽은 참조: `runtimes/node.md`, `tools/playwright-cli.md`, `methodology/00-setup.md`, `methodology/02-investigate.md`
- 가설 1 [확정]: 이전 Playwright 세션의 인증 키 때문에 비로그인 경로가 인증 경로로 실행됐다.
  - 구분 근거: `localStorage`에서 `access-token=debug-token`, `access-token-expires-at=1788144966705`를 관찰했다.
- 가설 2 [확정]: 인증 키 제거 뒤 같은 URL navigation만 수행하면 기존 React 문서가 남아 인증 snapshot도 유지됐다.
  - 구분 근거: 같은 URL navigation 전후 `performance.timeOrigin`이 `1788144202733.6`으로 같았고, 실제 reload 뒤 `1788144566338.7`로 바뀌면서 비로그인 Dialog가 표시됐다.
- 가설 3 [기각]: `Dialog` 렌더링 예외가 안내 모달을 막았다.
  - 구분 근거: 콘솔에는 Dialog 예외가 없었고 reload 후 기존 Dialog가 정상 표시됐다.
- 가설 4 [기각]: preview가 이전 번들을 제공했다.
  - 구분 근거: 브라우저가 직전 build 결과인 `/assets/index-CJ-Zji_m.js`를 로드했다.
- 비로그인 수동 QA: 원래 상세 URL을 유지한 채 `로그인 필요` Dialog와 `로그인 후 이용해 주세요.` 문구가 표시됐고 보호 콘텐츠 및 관련 API 요청은 없었다. 확인 후 `/login`으로 이동했으며 `history.state.usr.returnTo`는 `/citizen-participation/votes/2?tab=summary#comments`였다.
- 인증 endpoint QA: 1시간 유효한 로컬 테스트 토큰으로 새 문서를 열었을 때 `GET https://api.oasis.shovvel.com:8443/me`가 2회 관찰됐고 `/citizen/me`는 0회였다. 실제 응답은 사용할 수 있는 자격 증명과 CORS 허용이 없어 `net::ERR_FAILED`였으므로 성공 payload는 검증하지 않았다.
- 정리 대상:
  - [x] preview listener PID `87020` 종료 및 `127.0.0.1:4174` 미수신 확인
  - [x] Playwright 브라우저 세션 종료
  - [x] Playwright에서 설정·관찰한 인증 키 제거
  - [x] 현재 작업이 생성한 `.playwright-mcp`의 02:43 이후 파일만 삭제하고 다른 세션 파일 보존

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| 관련 Vitest 7개 파일 실행 | 70개 테스트 통과 |
| `npm run test` | Vitest 62개 파일, 457개 테스트와 Python governance hook 통과 |
| `npm run lint` | 통과 |
| `npm run build` | 통과, 기존 500 kB 초과 chunk 경고만 관찰 |
| `git diff --check` | 통과 |
| `lsp_diagnostics` | TypeScript LSP 미설치 및 Markdown LSP 미구성으로 실행 불가. `npm run lint`와 `npm run build`로 대체 |
| Vite preview + Playwright 기능 사용 | 비로그인 Dialog·콘텐츠 차단·안전한 `returnTo`와 인증 상태 `/me` 요청 확인 |

## Watcher 인계

- 승인 범위 밖 production UI와 `/citizen/me/activity`는 변경하지 않았다.
- 검토 대상 source diff는 9개 파일, 142 insertions, 38 deletions이며 `git diff --check`를 통과했다.
- 성공 응답을 검증할 실제 인증 자격 증명은 없지만 production 브라우저 요청 pathname과 정적·회귀 테스트 계약은 확인했다.
