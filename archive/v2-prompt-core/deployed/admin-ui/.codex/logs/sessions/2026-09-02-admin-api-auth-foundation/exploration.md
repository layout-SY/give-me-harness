# 탐색

## 결론

user-ui의 오류 taxonomy·reporter·queue와 token-presence 원칙은 재사용하되, 현재 프로젝트의 Zustand, Dialog, `ApiResult`를 정본으로 유지한다. external revision store, route 결합, user-ui 전용 도메인 코드는 복사하지 않는다.

## 요청과 비교 대상

- user-ui의 `2026-08-28-global-api-error-handling`, `2026-09-01-token-presence-auth-flow` 산출물을 분석했다.
- user-ui는 `ApiFailure -> reportApiFailure -> serverErrorQueue -> ApiErrorDialogBridge`를 전역 오류 흐름으로 사용한다.
- 동일 오류 객체는 한 번만 claim하고 server만 UI queue로 보내며 contract·transport는 redacted development diagnostics로 처리한다.
- token presence는 JWT 선판정과 분리하고 backend 401을 최종 무효성 신호로 사용한다.
- URL credential bootstrap은 모든 비동기 startup보다 먼저 실행한다.

## 현재 프로젝트에서 확인한 사실

- `ApiResult`, `CustomException`, silent-default `useApi`, Zustand auth/user store, 기존 Dialog가 존재했다.
- Axios interceptor는 HTTP 오류만 `CustomException`으로 바꾸고 network/setup 오류를 console에 기록했다.
- QueryClient에는 terminal error callback이 없었다.
- `useApi`의 `AbortController.signal`은 API callback에 전달되지 않았다.
- auth hook은 localStorage와 Zustand를 여러 위치에서 직접 수정하고 refresh JWT를 요청 전에 판정했다.
- tracked production `/sign-in` page와 보호 route는 존재하지 않았다.
- 원본 spinner UI 변경과 이번 승인 경로는 겹치지 않았다.

## 재사용 자산 결정

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| `src/shared/ui/dialog` | 재사용 | alert callback을 queue acknowledge와 session clear에 사용할 수 있다. |
| 새 modal·toast | 제외 | 두 번째 표시 시스템과 불필요한 UI scope가 생긴다. |
| Zustand auth/user store | 재사용 | 인증 상태원을 추가하지 않고 revision만 확장할 수 있다. |
| `src/shared/ui/loading` | 제외 | 다른 세션의 dirty 변경 경로이며 현재 요구와 무관하다. |

## 제약과 검증 경계

- 현재 프로젝트에는 npm `test` script가 없어 기존 Node `tests/*.test.mjs` 관례를 직접 실행한다.
- 외부 worktree는 LSP request-cwd 경계 밖이므로 build·targeted ESLint·실행 테스트로 정적 근거를 보강한다.
- 실제 backend credential이 없고 사용자·프로젝트 정책이 browser automation과 capture를 금지한다.
- production 로그인 UI와 route guard는 Claude UI handoff 이후 별도 작업으로 연결한다.
