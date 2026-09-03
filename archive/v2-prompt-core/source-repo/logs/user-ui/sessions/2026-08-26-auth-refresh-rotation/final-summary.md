# 최종 요약

## 제공 사항

- `POST /auth/refresh` 요청 `{ refreshToken }`, 응답 SUCCESS 토큰 `data`는 기존 계약 유지
- 인증 없이 호출 (Authorization 없음)
- 성공 시 새 access/refresh/`expiresIn`으로 저장값을 교체
- 같은 리프레시 토큰을 동시에 다시 보내지 않음
- 갱신 실패 시 세션을 지워 재로그인하게 함

## 제외 사항

- 실패 후 `/login` 이동
- 탭 간 잠금

## 검증

| 명령어 | 결과 |
| --- | --- |
| `npx vitest run src/features/auth` | 9 passed |
| `npx eslint src/features/auth/model/authSession.ts src/features/auth/model/authSession.test.ts` | 성공 |

## 산출물

`.codex/logs/sessions/2026-08-26-auth-refresh-rotation/`의 plan, exploration, implementation-log, grill-me-review, review-log, evaluation-log, final-summary, portfolio-log

## 남은 제한 사항

- 여러 탭의 동시 refresh는 막지 않는다.
- 세션을 지운 뒤 로그인 페이지로 보내지 않는다.

## 다음 단계

실패 후 로그인 화면으로 보낼지, 탭 간 잠금이 필요한지 확정하면 된다.
