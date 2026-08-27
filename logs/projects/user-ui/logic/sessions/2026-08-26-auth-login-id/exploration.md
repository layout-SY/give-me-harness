# 탐색

## 요청

사용자는 로그인 페이지 값이 이메일이 아니라 일반 문자열이며, 아이디·비밀번호로 인증 없이 `POST /auth/login`을 호출해 액세스·리프레시 토큰을 받는다고 했다. `accessToken`은 `Authorization: Bearer`, `expiresIn` 초가 지나기 전에 `POST /auth/refresh`로 갱신한다. 아이디 없음과 비밀번호 틀림의 응답은 같다.

## 대상 관련 사실

- 기존 계약은 `POST /auth/sign-in`, 본문 `{ email, password, language: "KO", platform: "WEB" }`, 응답 `{ result: 1, data: { id, email, …, accessToken, refreshToken } }`였다.
- `LoginPage`는 이메일 라벨과 `email` props를 썼고, `loginCredentialsSchema`는 `z.email()`이었다.
- 인증 Axios는 공유 인스턴스와 분리되어 있다. 직전 세션에서 인증 인스턴스에도 Bearer 인터셉터를 붙였으나, 이번 스펙은 로그인을 인증 없이 호출한다.
- 예시 accessToken payload는 `sub`만 있고 `exp`가 없다. `getJwtTokenStatus`로는 만료를 알 수 없다.
- `oasisapp://login` 딥링크는 기존 mutation 성공 경로에 있으며 제거 지시가 없다.
- 공용 UI는 `TextInput`, `Button`을 이미 로그인 폼에서 사용한다.

## 불러온 스킬

- `.agents/skills/SKILL.md`
- `policy/harness`, `policy/coding-convention`, `policy/type-definition`, `policy/data-fetch-layer`, `policy/validation`, `policy/publishing`, `policy/hook-extraction`, `policy/documentation`, `policy/portfolio`, `policy/review-checklist`, `policy/codex-native-quality`
- `recipe/api-authoring`, `recipe/data-dto`
- `reference/components`, `reference/custom-hooks`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| `text-input`, `button` | 재사용 | 기존 `LoginPage`가 이미 사용한다. 새 입력 컴포넌트는 만들지 않는다 |
| `token.util.ts` | 제외 | 예시 JWT에 `exp`가 없고, 스펙은 응답 `expiresIn`이다 |

## 제약 조건 및 미확인 사항

- `POST /auth/refresh`의 요청 본문·응답 스키마는 사용자가 주지 않았다. 본문은 `{ refreshToken }`, 응답은 로그인과 같은 `data` 형태로 가정한다.
- 리프레시를 만료 몇 초 전에 호출할지는 지시되지 않았다. 30초 전으로 둔다.
- Claude Code가 `src/**/ui/**`를 소유한다. 아이디 필드 반영을 위해 `LoginPage.tsx`를 함께 수정했다.

## 결론

이메일 검증과 `/auth/sign-in`을 제거하고, 무인증 `POST /auth/login` + `expiresIn` 기반 refresh 스케줄러로 바꾼다. 실패 화면은 아이디/비밀번호를 구분하지 않는다.
