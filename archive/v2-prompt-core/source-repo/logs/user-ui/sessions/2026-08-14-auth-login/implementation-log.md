# 로그인 기능 구현 기록

## 결론

- `POST /auth/sign-in` 요청과 응답 전체를 Zod schema로 정의했다.
- auth 전용 Axios factory가 `VITE_API_BASE_URL_DEV`를 지연 해석하고 잘못된 URL을 typed configuration error로 거부한다.
- 로그인 성공 시 `access-token` localStorage key에 token을 저장한다.
- token 저장 후 `URLSearchParams`로 실제 token 값을 인코딩해 `/login?access-token=<실제값>`으로 replace navigation하고 navigation 완료를 await한다.
- `/login` route 문자열을 공용 auth route 상수로 정의했다.
- `src/features/auth/testing/LoginTestPage.tsx`에 공용 `TextInput`과 `Button` 기반 임시 form을 추가했다.
- form은 email/password state를 관리하고 submit 시 `useSignInMutation`을 호출하며 pending과 오류 상태를 표시한다.
- `src/App.tsx`가 `authRoutes.login`에서 임시 페이지를 렌더링한다.
- 실제 응답에서 누락되는 `isTutorial`, `characterData`, `gameData`를 optional Zod 필드로 조정했다.
- MSW 응답 fixture에서 세 필드를 제거해 실제 missing-field 오류의 red→green 전환을 고정했다.
- `// @vitest-environment jsdom`은 hook 테스트를 위한 Vitest 지시문으로 유지했다.
