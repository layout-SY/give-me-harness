# 인계: 미로그인 시 로그인 페이지 강제 리다이렉트

## Assignment 이동

- 보내는 host·session·role: Claude Code / `로그인-리다이렉트-가드-인계` / `ui`
- 받는 host·session·제안 role: 미정 / 미정 / `logic`(라우트 가드·인증 상태 연결). 로그인 화면 표시 변경이 필요하면 `ui`를 별도로 연결한다.

## 역할 라우팅

- 요청 역할(`requested_roles`): 로그인 API 확인, 로그인 페이지 구현과 라우팅(ui), 미로그인 리다이렉트 강제(handoff만)
- 확인된 역할(`confirmed_roles`): `ui` (inject `--role ui`)
- 완료 역할(`completed_roles`): `ui` — 로그인 화면 주소를 `/sign-in`에서 `/login`으로 변경(아래 “완료된 작업”). 로그인 API·페이지는 이 세션 이전에 이미 커밋되어 있었다.
- 다음 제안 역할(`next_role`): `logic`
- 역할 판단 근거: 가드는 `useAuthStore` 인증 상태와 라우터 구조, 401 재인증 흐름을 연결하는 작업이며 화면 마크업 변경이 거의 없다.
- 사용자 확인: 사용자는 이 항목을 “핸드오프로 남겨놔”라고 지시했다. 구현은 승인되지 않았다.

## 목표 및 현재 상태

목표: 로그인하지 않은 사용자가 보호 화면(`/cp/**`, `/vo/**`, `/manage/**` 등)에 접근하면 자동으로 `/login`으로 이동시킨다.

현재 상태(2026-09-18, `sy-main` `7bcc83e` 기준으로 확인한 사실):

- `src/app/router/private-route.tsx`에 `PrivateRoute`(`isAuthorized` prop이 false면 `<Navigate to="/login" replace />`)가 있지만 **어떤 라우트에도 연결되지 않았다.**
- `src/app/router/routes.tsx`의 `/cp`, `/vo`, `/manage`, `/meeting`은 인증 없이 접근 가능하다. `/`는 `/cp/dashboard`로 이동한다.
- 인증 여부는 `src/features/auth/model/auth.store.ts`의 `useAuthStore().isAuthenticated`이며, 값은 **토큰 존재 여부**(access 또는 refresh token)로 정해진다. 만료 여부는 검사하지 않는다.
- 앱 시작 시 `src/app/index.tsx`에서 `bootstrapAuthSession()`이 localStorage 토큰으로 상태를 동기화하므로, 렌더 시점에는 `isAuthenticated`가 이미 확정되어 있다(비동기 로딩 상태 없음).
- 401 응답은 `src/shared/api/error/api-failure-reporter.ts`가 `reauthenticate` 이벤트로 큐잉하고, `src/app/providers/api-error-dialog-bridge.tsx`가 알림 확인 시 `clearAuthSession()`만 호출한다. **이후 `/login` 이동은 없다.** 가드가 `isAuthenticated`를 구독하면 이 시점에 자동으로 리다이렉트된다.
- 로그아웃은 `src/widgets/app-header/ui/header.tsx`에서 `rmAuthentication()` 후 `navigate("/login")`을 직접 호출한다.
- 로그인 성공 시 `src/pages/sign-in/hook/use-sign-in-controller.tsx`가 항상 `/cp/dashboard`로 이동한다. 원래 목적지 복원은 없다.
- 이전 세션 기록 `.claude/logs/sessions/2026-09-09-ui-598b9af7/final-summary.md`에 “`PrivateRoute` 연결은 이번 범위에서 제외”, “원래 목적지 복원은 라우트 보호 작업과 함께 처리”가 남아 있다.

## 완료된 작업

- 로그인 관련 코드 조사만 수행했다. 소스·테스트 변경 없음.
- 기존 로그인 구현(이미 커밋됨): `5834f92`(로그인 화면·당시 `/sign-in` 라우트), `a25745c`(`POST /auth/login`, access token 저장).
- 이 세션(미커밋, `sy-main` 기본 checkout): 사용자 지시로 화면 주소를 `/sign-in` → `/login`으로 변경하고 기존 `/sign-in`은 삭제(자동 이동 미유지).
  - `src/app/router/routes.tsx`: `path: "/login"`
  - `src/app/router/private-route.tsx`: `<Navigate to="/login" replace />` (Prettier가 props 선언을 한 줄로 정리)
  - `src/widgets/app-header/ui/header.tsx`: 로그아웃 후 `navigate("/login")`
  - `src/pages/sign-in/` 폴더·`SignInPage` 등 코드 이름과 API 경로 `/v1/auth/sign-in`(diagnostics)은 유지.

## 현재 구현 점검 결과 (2026-09-18, `sy-main` `b382a96`)

| 기능 | 상태 | 근거 |
| --- | --- | --- |
| 401 → 팝업 | 부분 구현 | `api-failure-reporter.ts:72`가 `reauthenticate` 이벤트를 큐잉하고 `App.tsx`의 `ApiErrorDialogBridge`가 알림 표시. 문구는 `server-error-message.ts`의 `"로그인 필요" / "로그인 후 이용해 주세요."`로, 만료 안내가 아님 |
| 401 적용 범위 | 부분 확인 | `useApi`(`use-api.tsx:55`)와 TanStack Query(`query-client.ts`의 QueryCache·MutationCache `onError`)만 확인. 이 두 경로를 거치지 않는 axios 직접 호출 여부는 미확인 |
| 팝업 확인 → `/login` 이동 | 미구현 | `api-error-dialog-bridge.tsx:19`는 `clearAuthSession()`만 호출. 현재 화면에 남음 |
| 재로그인 후 원래 경로 복귀 | 미구현 | `use-sign-in-controller.tsx`의 `SIGN_IN_LANDING_PATH = "/cp/dashboard"` 고정 |
| 미인증 접근 차단 | 미구현 | `PrivateRoute` 미연결 |
| 화면 열 때 만료 검사 | 미구현 | `synchronizeAuthSession`은 토큰 존재만 판정 |
| 로그인 상태에서 `/login` 차단 | 미구현 | `/login` 라우트에 조건 없음 |
| 로그인 요청 자체의 401 | 정상(의도) | `use-auth.ts`가 `unauthorizedBehavior: "error"`로 팝업 없이 폼 오류 표시 |

## 대기 중인 작업 (Logic 추가 구현 목록)

각 항목의 상세 변경은 아래 “역할별 상세 작업”을 따른다. 권장 순서대로 적었다.

1. **보호 라우트 가드 연결**: `/login`을 제외한 모든 라우트(`/`, `/cp`, `/vo`, `/manage`, `/events`, `/meeting`)를 `PrivateRoute` 기반 layout route 하위에 둔다(결정 9). `isAuthorized`는 `useAuthStore`에서 받는다.
2. **화면 열 때 만료 검사**: 앱 진입 시(`bootstrapAuthSession`/`synchronizeAuthSession`) access token의 `exp`가 현재 이전이면 `clearAuthSession()`. 디코드 실패(`isValid: false`)는 만료로 취급하지 않는다(결정 8).
3. **401 이후 `/login` 이동**: 팝업 확인 → `clearAuthSession()` → 가드가 store 변화로 `/login`에 이동하는지 확인. 가드 밖 화면이거나 이동이 일어나지 않으면 bridge에서 명시 이동한다. 두 경우 모두 현재 경로를 `from`으로 넘긴다. bridge는 router 바깥(`App.tsx`)에 있을 수 있으므로 `useNavigate` 사용 가능 여부를 먼저 확인하고, 불가하면 `router.navigate` 사용 여부를 결정한다.
4. **원래 경로 복원**: `PrivateRoute`가 `<Navigate to="/login" replace state={{ from: location }} />`로 보내고, 로그인 성공 시 `from`(pathname+search+hash)으로 `replace` 이동, 없으면 `/cp/dashboard`. `from`은 앱 내부 경로만 허용하고 `/login` 자체는 제외한다.
5. **로그인 상태에서 `/login` 차단**: 인증 상태면 `from` 또는 `/cp/dashboard`로 돌려보낸다. 로그아웃 후에만 로그인 화면 접근(결정 3).
6. **팝업 문구**: 현상 유지(결정 10). `server-error-message.ts`는 수정하지 않는다.
7. **중복 팝업 확인**: 한 화면에서 여러 요청이 동시에 401을 받을 때 팝업이 여러 번 뜨는지 `server-error-queue.ts` 동작을 확인하고, 중복되면 재인증 이벤트를 1회로 제한한다.
8. **axios 직접 호출 점검**: `useApi`·TanStack Query를 거치지 않는 호출이 있으면 401 처리 누락 목록을 사용자에게 보고한다(임의 수정 금지).
9. **모든 API 요청에 토큰 헤더 기본 포함** (사용자 요구 2026-09-18, 결정 11 참고):
   - 현재 구조: `src/shared/api/axios-instance.ts`의 request interceptor는 `config.authRequired === true`일 때만 `Authorization: Bearer <admin-access-token>`을 붙인다. 각 API가 `customConfig`(`axios.interface.ts`, `{ authRequired: true }`)를 **호출마다 직접 넘겨야** 한다(opt-in).
   - 점검 결과(2026-09-18, `src/entities/**/*.api.ts`·`src/features/**/*.api.ts`의 `instance.`/`client.` 호출을 호출 단위로 확인):
     - 도메인 API(CP·VO·아이템·이벤트·영상·소포·문의·사용자·관리자 설정·대시보드·DAO 등)의 호출은 **2건을 제외하고 모두** `customConfig`를 설정 인자로 넘겨 토큰이 붙는다. `withAbortSignal`은 설정을 펼쳐서 유지하므로 `signal`과 함께 넘겨도 토큰이 유지된다.
     - **버그 2건**: `entities/dao/api/voice-room/voice-room.api.ts:16` `closeDaoVoiceRoom`, `entities/dao/api/policy/policy.api.ts:23` `restartDaoJobsSettle`이 `instance.post(url, { ...customConfig })`로 **설정을 요청 본문 자리에 넘긴다.** 토큰이 붙지 않고 `{ authRequired: true }`가 본문으로 전송된다. 현재 두 함수는 `src`에서 호출처가 없어 실제 동작 영향은 없다. opt-out 전환 시 헤더는 해결되지만 본문 오전송은 남으므로 함께 수정한다(수정 여부 사용자 확인).
     - 토큰 없이 보내는 호출: `auth.api.ts`의 login·password·password/email(의도로 보임), reissue(refresh token을 직접 지정).
     - axios를 쓰지 않는 호출: `features/meeting/api/meeting.api.ts`의 `fetch` 3개. 화면에서 받은 `accessToken`을 직접 헤더에 넣는다.
     - 한계: 변수명이 `instance`/`client`가 아닌 호출, `.api.ts` 밖의 호출은 이 방식으로 확인하지 않았다.
   - 변경 방향: interceptor를 **기본 포함(opt-out)**으로 바꾼다. 저장된 access token이 있으면 모든 요청에 붙이고, 토큰을 붙이면 안 되는 요청만 명시적으로 제외한다(예: `authRequired: false` 또는 별도 `skipAuth` 플래그 — 이름은 구현 계획에서 제시). 이후 `customConfig` 전달은 불필요해지므로 기존 사용처 정리 여부를 계획에 포함한다(동작 영향 없음, 범위가 넓으므로 별도 commit 권장).
   - 주의: `refreshToken()`은 `Authorization: Bearer <refreshToken>`을 **직접 지정**한다. interceptor가 무조건 덮어쓰면 재발급이 깨지므로, 요청에 이미 `Authorization`이 있으면 유지한다.
   - 제외 후보(사용자 확인 필요): `POST /auth/login`, `POST /v1/auth/token/reissue`(refresh token 사용), `POST /v1/auth/password/email`(loginId로 비밀번호 변경 메일 요청), `POST /v1/auth/password`(메일 token으로 비밀번호 변경).
   - `/meeting`의 `fetch` 호출: 현재 화면에서 전달한 `accessToken`을 헤더에 넣는다. 로그인 토큰으로 통일할지는 사용자 확인 필요.
   - 완료 기준: 제외 목록을 뺀 모든 axios 요청에 헤더가 포함되고, 토큰이 없으면 헤더를 넣지 않으며(서버 401 → 결정 7 흐름), 로그인·재발급 요청은 기존 계약을 유지한다. interceptor 동작을 기존 `tests/auth-login-flow.test.mjs`와 같은 방식으로 테스트한다.
10. **테스트**: 아래 완료 기준을 기존 `tests/*.test.mjs` 배치에 추가한다. `package.json`에 `test` 스크립트가 없으므로 `TSX_TSCONFIG_PATH=tsconfig.app.json node --test --test-concurrency=1 tests/...` 형식을 사용한다.

## 결정 사항 및 제약 조건

- 가드는 새 컴포넌트를 만들지 않고 기존 `PrivateRoute`를 재사용하는 것을 우선 검토한다. `isAuthorized`는 `useAuthStore((s) => s.isAuthenticated)`에서 받는다.
- 클라이언트 가드는 화면 접근 제어일 뿐이며 API 권한은 서버가 토큰으로 검증한다.
- 메뉴·권한별 라우팅(`.codex/logs/sessions/admin-login-menu-handoff/handoff.md`)과 `routes.tsx`, shell 파일이 겹친다. 두 작업의 순서를 조율한다.

## 보내는 작업의 위치와 변경 상태

- project·저장소 루트: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`
- 현재 branch·HEAD·worktree·실행 디렉터리: `sy-main` / `b382a96` / 위 루트(기본 checkout)
- 확인 시점·인계 기준 commit: 2026-09-18, `b382a96` (시작 시 `7bcc83e`, 도중 `d38ec3b` 이벤트 API 병합 포함)
- 완료한 commit: `b382a96` `refactor(auth): 로그인 화면 경로를 /login으로 변경` — `routes.tsx`, `private-route.tsx`, `header.tsx`
- staged 변경: 없음
- unstaged 변경: `package.json`(`dev` 스크립트의 `--port 13001` 제거) — 이 세션의 변경이 아님, 보존
- untracked: 없음(세션 로그는 ignore 정책을 따름)
- 보존할 내용: 위 `package.json` 변경(작업 시작 시 실제 상태 재확인)

## 인계 대상 작업 공간

### 작업 공간: auth-route-guard

- 수행할 기능: 미로그인 리다이렉트 가드 연결
- 사용할 역할: `logic` (필요 시 `ui`가 같은 공간을 순차 사용)
- project·저장소 루트: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`
- 목적지 branch·worktree: 사용자 결정에 따라 **`sy-main`에서 분기한 별도 branch**(이름·linked worktree 경로는 미정, 생성 시 Git 승인 필요).
- 기준 commit: `sy-main` 최신(인계 기준 `b382a96`)
- 직접 부모: 별도 branch를 만들 경우 `sy-main`
- 공유/분리: 메뉴·권한 작업이 동시에 진행되면 `routes.tsx` 충돌 가능성이 있어 분리 또는 순차 진행을 권장
- 진입 전 확인: 실제 branch·HEAD·dirty 상태, `private-route.tsx`·`routes.tsx`가 이 문서 이후 바뀌었는지
- 필요한 Git 작업: branch/worktree 생성·commit·merge 모두 미승인

## 역할별 상세 작업

### 역할·하위 작업: Logic — 인증 라우트 가드 연결

- 사용할 작업 공간: `auth-route-guard`
- 목표: 미인증 상태에서 보호 경로 접근 시 `/login`으로 `replace` 이동
- 남은 작업과 구체적인 변경:
  1. `src/app/router/routes.tsx`: `/login`을 제외한 모든 라우트를 pathless layout route로 감싼다(결정 9). 예:
     ```tsx
     { path: "/login", element: <SignInPage /> },
     { element: <AuthGuard />, children: [ { path: "/", ... }, { path: "/cp", ... }, { path: "/vo", ... }, { path: "/manage", ... }, { path: "/events", ... }, { path: "/meeting", ... } ] }
     ```
     `AuthGuard`는 `useAuthStore`의 `isAuthenticated`를 읽어 `<PrivateRoute isAuthorized={...} />`를 렌더하는 얇은 래퍼(또는 `PrivateRoute` 자체가 store를 읽도록 변경 — 방식은 결정 필요).
  2. 목적지 복원을 채택하면 `PrivateRoute`에서 `<Navigate to="/login" replace state={{ from: location }} />`를 전달하고, `use-sign-in-controller.tsx`의 `SIGN_IN_LANDING_PATH` 대신 `location.state.from`을 사용한다(없으면 `/cp/dashboard`).
  3. 인증된 사용자의 `/login` 접근 처리(대시보드로 돌려보낼지)를 확정 후 반영한다.
  4. `api-error-dialog-bridge.tsx`: `clearAuthSession()` 후 가드가 store 변화로 리다이렉트하는지 확인한다. 가드 밖 경로에서도 이동이 필요하면 명시 navigate 여부를 결정한다.
  5. `header.tsx`의 수동 `navigate("/login")`은 가드 연결 후 중복이 된다. 유지·제거는 선택(동작상 무해).
- 재사용 자산: `PrivateRoute`, `useAuthStore`, `clearAuthSession`, `getJwtTokenStatus`(`src/shared/lib/utils/token.util.ts`, 만료 검사를 채택할 경우)
- 연결 계약: `useAuthStore().isAuthenticated: boolean`, `PrivateRoute({ isAuthorized, children? })`
- 선행 조건: 아래 미확정 사항 답변
- 겹치는 파일: `routes.tsx`, `cp/vo/manage-admin-shell.tsx`, `use-sign-in-controller.tsx`, `use-auth.ts` — 메뉴·권한 작업(`admin-login-menu-handoff`)과 조율
- 완료 기준:
  - 토큰 없는 상태로 `/cp/dashboard`, `/vo/dashboard`, `/manage/items`, `/events/attendance`, `/meeting`, `/`, 상세 경로 직접 진입 시 `/login`으로 이동하고 보호 화면의 데이터 요청이 발생하지 않는다.
  - 만료된 access token(`exp` 경과)으로 앱을 열면 세션이 정리되고 `/login`으로 이동한다. 디코드 불가 토큰은 이 단계에서 로그아웃시키지 않는다.
  - 로그인 후 보호 화면 진입 가능, 로그아웃 후 뒤로가기로 보호 화면이 보이지 않는다.
  - 401 → 재인증 알림 1회 표시 → 확인 → `/login` 이동 → 재로그인 → 401이 났던 원래 경로(query 포함)로 복귀.
  - 미인증으로 `/cp/proposals/123?page=2` 직접 진입 → 로그인 → 같은 경로로 복귀. `from`이 없으면 `/cp/dashboard`.
  - 인증 상태로 `/login` 접근 시 보호 화면으로 이동.
  - 로그인 요청 자체의 401은 기존처럼 팝업 없이 폼 오류로 표시된다.
  - 기존 `tests/auth-*.test.mjs` 통과, 위 동작 테스트를 기존 `tests/*.test.mjs` 배치에 추가, 공통 포맷 → `npm run lint` → 인증 테스트(`node --test`) → `npm run build` 통과.
- 사용자 확정 사항(2026-09-18):
  1. `/meeting`도 로그인 필수로 보호한다.
  2. 로그인 후 **원래 가려던 경로로 복원**한다(`state.from`이 없을 때의 기본값은 기존 `/cp/dashboard`).
  3. 이미 로그인한 사용자가 `/login`에 접근하면 보호 화면으로 돌려보낸다. 로그인 페이지로 가려면 **로그아웃해야** 한다.
  4. 인증 판정은 토큰 존재가 아니라 **access token 만료(`exp`)까지** 검사한다. `getJwtTokenStatus`의 `isActive`를 재사용 후보로 검토한다. 만료 토큰 발견 시 세션 정리(`clearAuthSession`) 후 `/login`으로 보낸다. 판정 위치(가드 렌더 시점, `bootstrapAuthSession`, store selector 중 어디)는 구현 계획에서 제시하고 확인받는다.
  5. 작업은 **`sy-main`에서 분기한 별도 branch**에서 진행한다. branch 이름·linked worktree 사용 여부와 생성 명령은 구현 세션에서 Git 승인을 받는다.
- 사용자 추가 확정(2026-09-18):
  6. 만료 검사는 **화면이 열릴 때만**(앱 진입·보호 라우트 진입 시점) 한다. 타이머 등 사용 중 만료 감지는 구현하지 않는다.
  7. 사용 중 만료는 **API 401 응답으로 처리**한다: 로그인 세션을 만료(`clearAuthSession`)시키고 `/login`으로 이동한다. 현재 `api-error-dialog-bridge.tsx`는 재인증 알림 확인 시 `clearAuthSession()`만 호출하므로, 가드가 store 변화로 이동시키는지 확인하고 가드가 적용되지 않는 경우엔 명시 이동을 추가한다. 이때 현재 경로를 `state.from`으로 넘겨 재로그인 후 복원되게 한다. 알림을 먼저 보여 줄지 즉시 이동할지는 기존 알림 흐름 유지를 기본으로 하되 변경 시 사용자 확인.
  8. **JWT 형식 오류는 별도로 처리하지 않는다.** 서버 응답(401)에 맡긴다. 즉 클라이언트는 `exp`가 읽히고 현재 시각 이전인 경우만 만료로 판단하고, 디코드 실패 시 만료로 간주해 강제 로그아웃하는 분기를 따로 만들지 않는다. (`getJwtTokenStatus`는 디코드 실패 시 `isActive: false`를 반환하므로 그대로 쓰면 형식 오류도 로그아웃된다. `isValid`와 `isActive`를 구분해 `isValid && !isActive`일 때만 만료 처리할지 구현 계획에서 명시한다.)
- 남은 조율·사용자 질문 사항:
  - 원래 경로 복원 시 메뉴·권한 작업이 연결되면 권한 밖 경로는 복원하지 않아야 한다(아래 메뉴·권한 작업과 조율).
- 사용자 추가 확정(2026-09-18, 2차):
  9. **모든 관리자 페이지는 로그인 후에만 이용 가능**하다. `/events`를 포함해 `/login`을 제외한 모든 라우트(`/`, `/cp`, `/vo`, `/manage`, `/events`, `/meeting`, 이후 추가되는 관리자 라우트)를 가드 안에 둔다. 새 라우트가 가드 밖에 추가되지 않도록 “`/login`만 가드 밖, 나머지는 가드 하위” 구조로 구성한다.
  10. **401 팝업 문구는 현상 유지**한다(`"로그인 필요" / "로그인 후 이용해 주세요."`). 만료·미로그인 구분 문구는 구현하지 않는다.
  11. **모든 API 요청에는 항상 토큰 헤더가 포함**되어야 한다. 구현 방법·제외 대상은 “대기 중인 작업” 9번을 따른다. 제외 목록과 `/meeting` 토큰 통일 여부는 사용자 확인 전까지 미정.
- 다음 인계: 로그인 화면 문구·레이아웃 변경이 생기면 `ui` 세션

## 협업 순서와 Git 통합

- 공유 공간 순서: 메뉴·권한 작업과 같은 공간이면 한 작업이 `routes.tsx` 수정·commit을 끝낸 뒤 다른 작업이 시작한다.
- 분리 공간: `sy-main` → 자식 branch, 완료 시 자식에서 `sy-main`으로 통합.
- 승인된 Git 작업: 없음 / 미승인: branch·worktree 생성, commit, merge 전부
- 산출물 책임: contributor

## 관련 경로와 스킬

- `src/app/router/private-route.tsx`, `routes.tsx`, `role-based-route.tsx`(권한 가드, 미연결)
- `src/features/auth/model/auth.store.ts`, `auth-session.ts`, `use-auth.ts`
- `src/app/providers/api-error-dialog-bridge.tsx`, `src/shared/api/error/api-failure-reporter.ts`
- `src/pages/sign-in/hook/use-sign-in-controller.tsx`, `src/widgets/app-header/ui/header.tsx`
- `.codex/logs/sessions/admin-login-menu-handoff/handoff.md`(메뉴·권한 라우팅 후속)
- 스킬: `task-role-routing`, `git-branch-strategy`, `hook-use-auth`, `documentation`

## 명령어 및 결과

- `git log -- src/pages/sign-in src/features/auth src/entities/auth ...`: 로그인 관련 커밋 `a25745c`, `5834f92`, `7a77067`, `c825586`, `2140c30` 확인
- `grep PrivateRoute|/sign-in ...`: `PrivateRoute` 사용처 없음 확인

- `/login` 변경 후(`sy-main` HEAD `d38ec3b`, 미커밋): 공통 `formatting.py apply` 3개 파일 포맷, `npm run lint` 통과, `npm run build` 통과(기존 번들 크기·`vite-tsconfig-paths` 경고만), `TSX_TSCONFIG_PATH=tsconfig.app.json node --test --test-concurrency=1 tests/auth-*.test.mjs` 16/16 통과. `npm run test` 스크립트는 package.json에 없다.

## 실행하지 않은 검증

- 브라우저에서 `/login` 진입·로그아웃 이동은 확인하지 않았다.
- `/login` 변경은 사용자 승인 후 `sy-main`에 commit `b382a96`(`refactor(auth): 로그인 화면 경로를 /login으로 변경`)으로 반영했다. 3개 파일만 포함했고, 다른 작업의 미커밋 `package.json` 변경(`dev` 스크립트의 `--port 13001` 제거)은 제외·보존했다.

## 다음 조치

1. `logic` 역할 세션에서 `sy-main` 기준 별도 branch 생성을 승인받는다.
2. 남은 확인 사항을 계획에 포함해 확인받은 뒤, 확정 사항 1~5대로 가드를 연결하고 검증한다.
3. 메뉴·권한별 화면 구성 작업(`.codex/logs/sessions/admin-login-menu-handoff/handoff.md`)과 `routes.tsx`·원래 경로 복원·첫 화면 결정을 조율한다.

---

# 추가 작업 인계: 출석·룰렛 이벤트의 아이템 UI 정합 (2026-09-18)

위 로그인 가드 인계와 별개의 작업이다. 같은 세션 산출물에 기록한다.

## 역할과 사용자 결정

- 확인된 역할: `ui`(inject). 완료 역할: `ui`. 다음 제안 역할: `logic`(아래 (c) 이름 조회 연결).
- 사용자 요청: 출석·룰렛 페이지의 아이템 관련 UI를 아이템 관리 화면과 일관되게 추가 구현.
- 사용자 선택 범위: **(a) 아이템 검색 팝업 정합**, **(c) 보상 행 아이템 이름 표시 틀**만. (b) 보상 제외 아이템 표시·차단, (d) 이벤트 목록 필터·KPI는 범위 밖.
- 사용자 결정: 별도 branch에서 작업. 상태·성별 라벨 함수는 **`entities/items`로 이동해 공유**(권장안 채택).

## 작업 위치와 변경 상태

- 저장소·worktree: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui` (기본 checkout)
- branch: `feature/event-item-ui` — `sy-main` `b382a96`에서 `git switch -c`로 생성(사용자 승인, 보호 실행 `9e2d4e0b…`). 직접 부모 `sy-main`. branch 관계 graph 등록은 하지 않았다.
- commit: `ed9d65b` `feat(events): 아이템 검색 팝업을 아이템 목록 표로 맞추고 보상 행 이름 표시 틀 추가` (사용자 승인, 보호 실행 `96c067fc…`, 16개 파일). 이후 이 작업의 미커밋 변경 없음.
- 보존할 다른 변경: `package.json`(`dev` 스크립트 `--port 13001` 제거) — 이 작업과 무관, commit에 포함하지 않는다.

## 완료한 변경

| 경로 | 내용 |
| --- | --- |
| `src/entities/items/lib/item-display.ts` (신규) | `resolveItemStatusLabel`, `resolveItemStatusColor`, `resolveItemGenderLabel`을 `pages/item/lib`에서 이동 |
| `src/entities/items/index.ts` | 위 3개 함수 공개 |
| `src/pages/item/lib/item-display.ts` | 이동한 3개 함수 제거. 가격·결제수단·날짜·카테고리 트리 함수만 남김 |
| `src/pages/item/model/item.config.ts` | 라벨 함수를 `~/entities/items`에서 import(동작 동일) |
| `tests/item-form.test.mjs` | 이동한 함수는 entity 모듈에서 검증(기대값 동일, 경로만 변경) |
| `src/widgets/event-admin/model/item-search.config.ts` (신규) | 검색 결과 열 정의: ID·상태(배지)·이름·카테고리·성별. 아이템 목록과 같은 헤더·배지, 팝업 폭 540px에 맞춘 너비 |
| `src/widgets/event-admin/model/event-admin.types.ts` | `ItemSearchResult`에 `gender: number \| null` 추가(목록 API 응답에 이미 존재, hook 수정 없음) |
| `src/widgets/event-admin/ui/item-search-popup.tsx` | 결과를 카드 목록 → 공용 `Table`로 교체. 행 클릭·Enter로 선택, ID 없는 행은 흐리게 표시하고 선택 무시. 결과 없음은 `Table` 기본 `NoResults` |
| `src/widgets/event-admin/ui/object-id-field.tsx` | 선택 prop `itemName?: string \| null`. 문자열일 때만 입력칸 아래 한 줄로 표시하고 `aria-describedby`로 연결 |
| `src/widgets/event-admin/ui/event-admin.css` | 기존 결과 카드 스타일 제거, 선택 불가 행·이름 줄 스타일 추가 |
| `src/pages/event-attendance/model/event-attendance-reward.types.ts`, `src/pages/event-roulette/model/event-roulette.types.ts` | 보상 행에 `itemName?: string \| null` 추가(누적 보상 행은 상속) |
| `src/pages/event-attendance/ui/attendance-reward-rows.tsx`, `src/pages/event-roulette/ui/roulette-reward-editor.tsx` | `itemName`을 `ObjectIdField`로 전달 |
| `src/pages/event-attendance/ui/event-attendance.css`, `src/pages/event-roulette/ui/event-roulette.css` | 이름 줄이 생겨도 입력칸 윗줄이 맞도록 행 정렬을 `start`로 바꾸고, 순서 번호·버튼은 입력칸 높이(`--cp-field-h`) 안에서 가운데 정렬 |

제약: 공용 `Table`은 항상 페이지 번호 영역을 표시하므로 팝업에도 1/1이 보인다. 결과 5개 제한·필터 없는 검색은 로직 범위라 유지했다. 달력 칩(`AttendanceRewardChip`)과 휠 조각에는 이름을 넣지 않았다.

## Logic 후속 작업: 보상 행 아이템 이름 채우기 ((c))

- 현재 controller는 `itemName`을 채우지 않으므로 화면은 이전과 동일하게 보인다.
- 연결 대상: `src/pages/event-attendance/hook/use-attendance-reward-editor.ts`, `src/pages/event-roulette/hook/use-roulette-reward-editor.ts`(행 생성 위치), 필요 시 `src/widgets/event-admin/hook/use-event-item-search.ts`.
- 계약: 행의 `itemName`에 `string`이면 표시, `null`/생략이면 미표시. view는 조회·캐시를 하지 않는다.
- 제안 흐름(사용자 확인 필요):
  1. 검색 팝업에서 선택하면 결과의 `name`을 해당 행 이름으로 바로 기억한다(추가 요청 없음).
  2. 직접 입력·기존 보상 로드·다른 이벤트 보상 가져오기로 채워진 ID는 아이템 상세 API(`itemsApi.getDetail`, `useItemDetailQuery` 재사용 후보)로 이름을 조회한다.
- 미확정(사용자 질문):
  - 직접 입력 시 조회 시점(입력 멈춤 후 / 포커스 해제 시 / 저장 전).
  - 보상이 많을 때 ID별 개별 상세 조회를 허용할지(중복 ID 캐시 포함), 일괄 조회 API가 있는지.
  - 존재하지 않는 ID·조회 실패 시 표시(“이름 확인 불가” 문구 또는 `objectIdError`로 처리) — 현재 view는 `null`이면 아무것도 표시하지 않는다.
- 완료 기준: 팝업 선택·직접 입력·기존 보상·보상 가져오기 모두 이름 표시, 조회 실패가 저장을 막지 않음(또는 확정 정책대로), 기존 `tests/events-*.test.mjs` 통과와 이름 조회 테스트 추가.

## 검증

- 공통 `formatting.py apply`: 변경 16개 파일 포맷.
- `npm run lint`: 통과.
- `npm run build`: 통과(기존 번들 크기·`vite-tsconfig-paths` 경고만).
- `TSX_TSCONFIG_PATH=tsconfig.app.json node --test --test-concurrency=1 tests/item-form.test.mjs tests/item-id.test.mjs tests/items-contract.test.mjs tests/items-query-mutation.test.mjs tests/events-contract.test.mjs tests/events-controller.test.mjs tests/events-query-mutation.test.mjs`: 73/73 통과.
- `git diff --check`: 통과.
- 실행하지 않음: 브라우저 화면 확인(팝업 표 폭·행 정렬 실제 표시), 전체 테스트 묶음.

## 다음 조치

1. (완료) `feature/event-item-ui`에 commit `ed9d65b`.
2. (완료, 2026-09-21) `sy-main`에 ff-only 병합. 관계 등록 `4108575…`(부모 `sy-main`, fork `b382a96`), 검토 `be5b1106…`, 완료 작업 `13f66b50…`. 결과 `sy-main` = `ed9d65b`, 병합 후 `npm run lint`·`npm run build` 모두 exit 0(`verification_passed: true`). `--cleanup`을 넣지 않았으므로 `feature/event-item-ui` branch는 그대로 남아 있고 원격 반영도 하지 않았다.
   - 병합 도중 확인·해소한 사항: 다른 작업의 미커밋 `package.json` 변경은 사용자가 직접 되돌렸다. 폴더가 사라져 prunable 상태였던 `/private/tmp/asan-metaverse-admin-ui-video-api` 등록은 사용자가 `git worktree prune`으로 정리했다(해당 폴더의 미커밋 변경 존재 여부는 확인 불가). 남은 linked worktree는 `event-api`, `item-ui` 두 곳이다.
3. (c) 이름 조회는 `logic` 세션에서 위 미확정 사항을 확인한 뒤 연결.
