# 최종 요약

## 제공 사항

- 로그인 입력은 이메일이 아닌 `loginId` 문자열
- 인증 없이 `POST /auth/login`에 `{ loginId, password }`를 보내고 SUCCESS `data`의 토큰을 파싱
- `accessToken`/`refreshToken`/`expiresIn`을 저장하고, 만료 30초 전에 `POST /auth/refresh`로 갱신
- 로그인·리프레시 요청에는 저장된 액세스 토큰을 붙이지 않음
- 아이디 없음과 비밀번호 틀림을 같은 실패 문구로 표시
- 앱 부팅 시 기존 세션이 있으면 refresh를 다시 스케줄

## 제외 사항

- refresh 공식 OpenAPI 본문 (미제공, `{ refreshToken }` 가정)
- 리프레시 실패 시 강제 로그아웃
- `oasisapp://login` 딥링크 제거

## 검증

| 명령어 | 결과 |
| --- | --- |
| `npx vitest run src/features/auth` | 7 passed |
| `npm run build` | 성공 |
| `npm run lint` | 성공 |

## 산출물

`.codex/logs/sessions/2026-08-26-auth-login-id/`의 plan, exploration, implementation-log, grill-me-review, review-log, evaluation-log, final-summary, portfolio-log

## 남은 제한 사항

- refresh 요청 본문은 `{ refreshToken }` 가정이다.
- 리프레시 실패 시 세션을 지우지 않는다.

## 다음 단계

refresh OpenAPI가 오면 요청/응답 DTO를 맞춘다. 웹에서 딥링크를 쓸지 확정하면 mutation 성공 경로를 조정할 수 있다.
