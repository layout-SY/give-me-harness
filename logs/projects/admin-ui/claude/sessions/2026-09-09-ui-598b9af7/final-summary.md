# 최종 요약

## 한 줄

없던 관리자 로그인 화면(`/sign-in`)을 신설하고 라우터에 연결했다. 인증 로직은 기존 `useAuth` 를 그대로 쓴다.

## 변경 목록

**신규** `src/pages/sign-in/`
- `index.ts` · `ui/sign-in-page.tsx` · `ui/sign-in-view.tsx` · `ui/sign-in.css` · `hook/use-sign-in-controller.tsx` · `model/sign-in.types.ts`

**수정** `src/app/router/routes.tsx`
- 관리자 셸 밖에 `{ path: "/sign-in", element: <SignInPage /> }` 추가

## 해결한 문제

`private-route.tsx` 와 `app-header/header.tsx` 가 이미 `/sign-in` 으로 이동하고 있었으나 그 경로에 화면이 없었다.
헤더 로그아웃 시 빈 경로로 떨어지던 동작이 해소됐다.

## 검증

- `npm run build` 통과(`tsc -b` 포함)
- `npm run lint` — 신규·수정 경로 지적 0건 (저장소 전체 68 error 는 기존 부채)

## 남은 제한

- `/cp/**` 는 여전히 인증 없이 접근 가능하다. `PrivateRoute` 연결은 이번 범위에서 제외했다.
- 로그인 후 항상 `/cp/dashboard` 로 이동한다. 원래 목적지 복원은 라우트 보호 작업과 함께 처리하는 것이 맞다.
- 브라우저 시각 QA 미수행.

## 상태

구현·검증·문서 완료. commit 과 `sy-main` merge 는 사용자 승인 대기 중.
