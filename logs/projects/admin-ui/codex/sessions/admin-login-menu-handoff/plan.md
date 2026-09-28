# 관리자 로그인과 메뉴 인계 계획

## 결론 및 승인

사용자가 제공한 `POST /auth/login` 명세에 맞춰 기존 로그인 화면 → 컨트롤러 → `useAuth` → 인증 API → 인증 세션 흐름을 확장한다. 성공 응답의 `accessToken`을 기존 `localStorage` 키에 저장하고, 저장 완료 직후 후속 `/menus` 요청이 필요하다는 주석을 남긴다. 메뉴 API·권한 응답·동적 메뉴·lazy 라우팅의 실제 구현은 다른 worktree에서 진행할 작업으로 handoff에 기록한다.

- 사용자 승인: “주석만 … 넣어놔”, “실구현에 대해선 … 핸드오프 문서만”, “이렇게 로그인 작업 진행해”.
- 확정 역할: `logic`. API·상태·hook·오류 처리 및 후속 인계 문서를 담당한다.
- 요청 명확성: 현재 작업 `can_proceed: true`. 메뉴 계약의 미정 항목은 사용자 지시에 따라 후속 작업으로 분리했다.
- 작업 위치: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`.
- branch: `sy-main`, 시작 HEAD: `efccd76b10a89e49e2c3f7a5c8c59326e6b6c3f3`.
- 시작 상태: staged·unstaged·untracked 변경 없음. Git 변경은 요청 범위에 포함되지 않는다.

## 확인한 근거와 재사용

- `src/entities/auth/api/auth.api.ts`, `auth.dto.ts`: 기존 로그인은 `/v1/auth/sign-in`과 access·refresh·profile·roles 응답을 요구한다. 새 로그인 응답을 별도로 검증하고 기존 refresh 계약을 보존한다.
- `src/features/auth/model/auth-session.ts`: 토큰·사용자·인증 여부·revision을 한 경계에서 관리한다. 로그인용 access token 저장을 이 경계에 추가하여 이전 refresh·사용자 정보가 새 로그인에 남지 않도록 한다.
- `src/features/auth/use-auth.ts`, `src/shared/lib/hooks/use-api.tsx`: 취소·오래된 요청은 `undefined`가 반환된다. 컨트롤러가 실제 성공 여부를 확인한 뒤 이동하도록 연결한다.
- `src/pages/sign-in/hook/use-sign-in-controller.tsx`: 성공 시 `/cp/dashboard`로 이동한다. 오류 표시에는 `ApiFailureError`만 인식하는 공백이 있어 기존 `toApiFailure`로 `CustomException`도 처리한다.
- `src/shared/api/axios-instance.ts`: HTTP 오류는 `CustomException`으로 변환되고 인증 요청에는 저장된 access token이 사용된다.
- `src/app/router/routes.tsx`, `src/widgets/side-navigation/lib/build-navigation-items.ts`: 라우트는 정적 import, 메뉴는 CP·VO 고정 목록이다. 해당 영역은 후속 설계의 근거로만 사용한다.
- 기존 `tests/auth-api-contract.test.mjs`, `tests/auth-session.test.mjs`와 Vite SSR·Node test를 사용하는 인접 테스트 방식으로 검증한다.

## 수행할 작업

1. 현재 workdir의 auth API·DTO에 새 로그인 명세를 적용하여 요청 URL·body·성공 envelope·토큰을 검증한다.
2. 인증 세션과 `useAuth`를 확장하여 access token 저장, 오래된 세션 정보 정리, 취소 시 미이동, `/menus` 후속 요청 주석을 연결한다.
3. 로그인 컨트롤러의 기존 입력·제출·성공 이동 흐름을 유지하면서 서버 오류 표시를 기존 오류 정규화 함수로 보완한다.
4. 실제 명세에 근거한 API·세션·로그인 흐름 테스트를 실행한다. 공통 포맷 트리거 실행 후 lint·test·build 결과를 기록한다.
5. `handoff.md`에 사용자 메뉴·권한·lazy 라우팅 구상, 현재 연결 지점, 후속 역할별 파일·순서·검증 및 미정 계약을 기록하고 `final-summary.md`에 실제 결과를 남긴다.

## 검증 및 완료 기준

- `/auth/login` 요청에 `loginId`, `password`를 전달하고 `SUCCESS` 응답의 access token을 저장한다.
- 400 `ADMIN_INVALID_PASSWORD`, 404 `ADMIN_NOT_FOUND` 메시지가 로그인 오류로 연결된다.
- 잘못된 성공 응답·취소·저장 실패는 로그인 완료나 이동으로 처리되지 않는다.
- 기존 refresh 세션 테스트와 새 access-only 로그인 테스트를 모두 확인한다.
- `python3 -I /Users/okand/SynologyDrive/asan-agent-policy/state/bundles/admin-ui/codex-logic-1b3bf4886899fa0fcf81fab5ef8ce3907bfbe7af1e8864bc6a0db28924b76a5f/policy/.agent-policy/runtime/formatting.py apply`.
- `TSX_TSCONFIG_PATH=tsconfig.app.json node --test --test-concurrency=1 tests/auth-api-contract.test.mjs tests/auth-session.test.mjs tests/auth-login-flow.test.mjs`.
- `npm run lint`, `npm run build` 및 필요한 기존 전체 Node 테스트. package.json에는 `test` script가 없다.
- 브라우저·실서버 로그인·Git 변경은 수행하지 않는다. 메뉴 API 요청은 이번 작업에서 실행하지 않는다.
