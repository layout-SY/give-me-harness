# 로그인 기능 탐색

## 결론

- 기존 공용 API mapper는 `success` 필드가 없는 로그인 응답에 적용할 수 없다.
- `src/shared/config/constants.ts`의 `ACCESS_TOKEN_STORAGE_KEY`를 재사용한다.
- 기존 Axios 인증 interceptor는 저장된 access token을 Bearer token으로 사용한다.
- `src/main.tsx`가 `QueryClientProvider`와 `BrowserRouter`를 제공한다.
- 기존 production `LoginPage`는 없고 `src/App.tsx`에도 `/login` route element가 없었다.
- 사용자가 임시 기능 확인 UI를 명시적으로 요청했으므로 `src/features/auth/testing/`에 production UI와 분리해 구현할 수 있다.
- `src/shared/ui/text-input/text-input.tsx`는 controlled value, clear, password 표시를 지원한다.
- `src/shared/ui/button/button.tsx`는 submit, pending, disabled 상태를 지원한다.
- Access token을 query string에 포함하면 브라우저 기록, 로그, 분석 도구, 리퍼러에 노출될 수 있다.
- 사용자는 위험 안내 후 `/login?access-token=<실제값>` 방식을 선택했다.
- 실제 browser network 응답에는 `isTutorial`, `characterData`, `gameData`가 없었다.
- 기존 Zod schema는 세 필드를 필수화해 access token이 유효해도 로그인 성공 처리를 차단했다.
- 현재 로그인 소비자는 응답의 `accessToken`만 사용하므로 세 profile 필드는 비보장 optional 계약이 맞다.
