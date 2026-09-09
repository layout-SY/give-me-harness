# 탐색 기록

## 로그인 화면 부재 확인

- `src/pages/` — `cp-*` 13개 슬라이스와 `meeting` 만 존재. 로그인 슬라이스 없음.
- `src/app/router/routes.tsx` — `/sign-in` 라우트 정의 없음. `/` 는 `/cp/dashboard` 로 리다이렉트.
- `src/app/router/private-route.tsx`, `role-based-route.tsx` — 파일은 있으나 `routes.tsx` 에서 사용되지 않음(라우트 보호 미적용).

## 이미 존재하는 인증 로직 (재사용 대상)

- `src/entities/auth/api/auth.api.ts` — `POST /v1/auth/sign-in`, 토큰 재발급.
- `src/entities/auth/api/auth.dto.ts` — `SignInDto { loginId, password }`, `parseAuthPayload`.
- `src/features/auth/use-auth.ts` — `getAuthentication(loginId, password)` / `refreshAuthentication` / `rmAuthentication`.
- `src/features/auth/model/auth-session.ts`, `auth.store.ts` — 토큰 저장과 zustand 인증 상태.

### 에러 표시 경로 확인

`useAuth.getAuthentication` 은 `execute(..., { onError: (error) => { throw error; } })` 를 쓴다.
`src/shared/lib/hooks/use-api.tsx` 의 `handleFailure` 는 `onError` 가 정의되면 `errorPresentation: "silent"` 로 보고하므로
`ApiErrorDialogBridge` 의 전역 다이얼로그가 뜨지 않고 예외가 호출자로 전파된다.
→ 로그인 화면은 예외를 직접 잡아 **인라인 오류 메시지**를 표시해야 하며, 전역 다이얼로그와 중복되지 않는다.

## src/shared/ui 재사용 자산

- `text-input/text-input.tsx` — HeroUI `InputGroup` 어댑터. `enableShow` 로 비밀번호 표시/숨김 토글 내장, `enableClear`, `error` (`data-invalid`) 지원. 나머지 props 는 `InputGroup.Input` 으로 spread 되어 `id` / `autoComplete` / `autoFocus` 전달 가능.
- `button/button.tsx` — `type="submit"`, `isLoading`(`isPending`), `disabled`, `fullWidth`(기본 true), `className` → HeroUI variant 매핑(`primary`).
- `loading/loading.tsx` — overlay 로딩. 이번 화면은 버튼 `isLoading` 으로 충분해 사용하지 않음.
- `form/index.ts` — react-hook-form 미설치 placeholder(`export {}`). 사용 불가.

## 디자인 토큰

- `src/shared/assets/css/_variables.css` — `--clr-primary-500 #1a73f9`, `--clr-gray-*`, `--clr-red-500`, `--clr-background #fafafa`, `--clr-nav-background`(=gray-800), `--clr-nav-font`, `--clr-nav-font-active`.
- `src/shared/assets/css/_cp-admin.css` — `--cp-card-pad/radius/bg/border`, `--cp-label`, `--cp-subtitle`, `--cp-gap`.
- `src/shared/assets/css/main.css` — 폰트 Noto Sans KR. `body { display:flex; place-items:center }` 로 이미 중앙 정렬(주석상 "로그인 등 중앙 정렬용").
- `src/app/styles/index.css`, `App.css` 는 `index.tsx` 에서 import 되지 않는 Vite 템플릿 잔재라 무시.

## 인접 구현 패턴

`src/pages/cp-dashboard/` 기준: `ui/*-page.tsx`(controller 연결) + `ui/*-view.tsx`(표현) + `hook/use-*-controller.tsx` + `model/*.types.ts` + `index.ts` 배럴. 동일 구조를 따랐다.
