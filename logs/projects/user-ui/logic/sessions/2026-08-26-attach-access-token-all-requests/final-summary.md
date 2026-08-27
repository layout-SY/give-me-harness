# 최종 요약

## 제공 사항

- 공유 Axios 요청은 저장된 액세스 토큰이 있으면 항상 `Authorization: Bearer`를 붙임
- 로그인 Axios 인스턴스도 같은 규칙
- 회의 fetch는 인자 토큰이 비면 `localStorage` 토큰을 사용
- `authRequired` 옵트인에 의존하지 않음

## 제외 사항

- 토큰 없을 때 요청 차단
- API 파일에서 `customConfig` 일괄 삭제

## 검증

| 명령어 | 결과 |
| --- | --- |
| `npx vitest run src/shared/api/attach-access-token.test.ts src/features/auth/api/auth.api.test.ts` | 4 passed |
| `npm run build` | 성공 |
| `npm run lint` | 성공 |

## 산출물

`.codex/logs/sessions/2026-08-26-attach-access-token-all-requests/`의 plan, exploration, implementation-log, grill-me-review, review-log, evaluation-log, final-summary, portfolio-log

## 남은 제한 사항

- 토큰이 없으면 헤더를 붙이지 않는다.
- 기존 `customConfig` 플래그는 남아 있다.

## 다음 단계

토큰 없는 보호 API 호출을 막을지, 로그인만 헤더 제외할지를 확정하면 된다.
