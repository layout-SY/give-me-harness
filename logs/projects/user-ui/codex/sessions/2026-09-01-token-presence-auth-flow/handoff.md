# 인계

## 목표 및 현재 상태

- 목표: 로그인 존재 여부를 `/me` 성공이 아니라 localStorage 또는 URL query의 auth token 존재로 판단하고, token이 없는 보호 경로는 `/login`으로 이동시키며, token 요청의 401은 기존 세션 만료 Dialog 흐름을 사용한다.
- 현재 상태: 인증 model·hook·startup·route boundary와 Claude Code 소유 production UI 연결을 완료했다. 사용자가 Claude UI 완료를 확인했고 통합 검증도 통과했다.
- 인계 상태: `UI_COMPLETE` 확인 후 Logic 통합 완료.
- 작업 브랜치: `task/token-presence-auth-flow`, 부모 및 직접 merge 대상 `sy-main`, 승인 시점 부모 HEAD `5e2a97e495c473f348dc25a58163bdf0ea3b293e`.

## 완료된 작업

- `src/features/auth/model/authSession.ts`
  - `hasAuthTokenPresence()`가 `access-token` 또는 `refresh-token` 중 하나의 non-empty localStorage 값을 로그인 존재 상태로 반환한다.
  - `bootstrapAuthTokensFromLocation()`이 저장 token이 없을 때 URL query의 `access-token`, `refresh-token`을 저장한다.
  - URL token은 localStorage token을 덮어쓰지 않으며, token query만 제거하고 다른 query와 hash는 보존한다.
- `src/features/auth/hook/useAuthTokenPresence.ts`
  - 기존 auth session revision external store를 `useSyncExternalStore`로 구독한다. Zustand auth store를 추가하지 않았다.
- `src/main.tsx`
  - app render와 refresh 예약 전에 URL token bootstrap을 실행한다.
- `src/app/providers/AuthRouteBoundary.tsx`
  - access token expiry 선검증과 client-side reauthentication enqueue를 제거했다.
  - token이 없으면 기존 `createAuthReturnState()`를 사용해 현재 위치를 보존하고 `/login`으로 직접 이동한다.
  - token이 있으면 expiry metadata와 관계없이 보호 화면을 유지하며 backend 401을 authoritative 신호로 사용한다.
- 기존 `ApiFailureReporter → serverErrorQueue → ApiErrorDialogBridge` 401 흐름은 변경하지 않았다.
  - 확인 버튼과 Escape 종료가 모두 session 삭제, `/login` 이동, `returnTo` 보존을 수행하도록 테스트했다.

## 대기 중인 작업

- 필수 세션 8종 문서를 최신 검증과 Watcher/Evaluator 결과로 완료한다.
- commit·merge·사후 검증은 별도 사용자 승인을 기다린다.

## 결정 사항 및 제약 조건

- 원인은 role·permission 문제가 아니라 세 route의 `isAuthenticated: meQuery.isSuccess` 결합이었다.
- 기존 authSession external store가 session 변경의 정본이므로 Zustand auth store를 추가하지 않았다.
- access token을 요청 전에 매번 검증하지 않는다. token presence로 요청을 허용하고 backend 401에서 세션 만료 Dialog를 연다.
- token이 전혀 없는 최초 보호 경로는 Dialog를 열지 않고 `/login`으로 직접 이동한다.
- Hephaestus는 Claude Code 소유 `src/**/ui/**` production 파일을 수정하지 않았다.
- Claude Code는 `CitizenParticipationDetailRoutes.tsx`, `CitizenReadDetailRoutes.tsx`, `CitizenCommentRoutes.test.tsx`에서 `useMeQuery` 제거와 `useAuthTokenPresence()` 연결을 완료했고, 사용자가 `UI 작업 완료`를 확인했다.
- TypeScript LSP는 사용자가 이전에 설치를 거절해 사용할 수 없었다. 정적 타입 검증은 최종 `npm run build`에서 수행해야 한다.
- URL token bootstrap은 `startMocks()`보다 먼저 동기 실행해 credential query 제거가 mock 초기화에 지연되지 않는다.

## 관련 경로

- 인증 session 및 bootstrap: `src/features/auth/model/authSession.ts`
- token presence hook: `src/features/auth/hook/useAuthTokenPresence.ts`
- startup: `src/main.tsx`
- 보호 route: `src/app/providers/AuthRouteBoundary.tsx`
- 401 Dialog bridge: `src/app/providers/ApiErrorDialogBridge.tsx`
- Claude UI 연결 대상: `src/pages/citizen-participation/ui/CitizenParticipationDetailRoutes.tsx`, `src/pages/citizen-participation/ui/CitizenReadDetailRoutes.tsx`
- UI 회귀 테스트 대상: `src/pages/citizen-participation/ui/CitizenCommentRoutes.test.tsx`

## 명령어 및 결과

| 명령어 | 결과 |
| --- | --- |
| `npx vitest run src/app/providers/AuthRouteBoundary.test.tsx` | 5 tests PASS |
| `npx vitest run src/features/auth/model/authSession.test.ts` | 20 tests PASS |
| `npx vitest run src/features/auth/hook/useAuthTokenPresence.test.tsx` | 1 test PASS |
| `npx vitest run src/app/providers/ApiErrorDialogBridge.test.tsx` | 7 tests PASS |
| 인증 관련 5개 파일 묶음 실행 | 5 files, 36 tests PASS |
| UI/auth 통합 대상 실행 | 6 files, 47 tests PASS |
| `npm run test` | Vitest 63 files, 469 tests PASS, governance 20 tests PASS |
| `npm run lint` | PASS |
| `npm run build` | PASS, 기존 chunk size 경고만 출력 |
| TypeScript LSP diagnostics | server 미설치, 사용자 이전 설치 거절로 실행 불가 |

## 다음 조치

1. Watcher 재판정과 Evaluator 근거를 반영해 필수 세션 문서를 완료한다.
2. commit·merge 계약을 사용자에게 보고하고 별도 승인을 기다린다.
