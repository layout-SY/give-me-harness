# 최종 요약

## 제공 사항

공통 API failure 분류·redacted diagnostics·서버 오류 Dialog queue, Axios/fetch/Query/useApi 연결, Auth refresh race 보호, route guard, 401 확인 흐름, 안전한 로그인 복귀를 제공했다.

## 제외 사항

UI 디자인·마크업, package/lockfile, i18n, 중앙 하네스, 시민참여 보호 hook은 변경하지 않았다.

## 검증

| 명령어 | 결과 |
| --- | --- |
| `npm run lint` | exit 0 |
| `npm run test` | Vitest 452 + governance 20, exit 0 |
| `npm run build` | exit 0 |
| 실제 Chromium | F3 route/401/login/FIFO/diagnostics 통과 |
| F1/F4 Watcher | APPROVE / PASS |

## 산출물

`.codex/logs/sessions/2026-08-28-global-api-error-handling/`에 필수 8종 문서를 작성했다.

## 남은 제한 사항

실제 회사 API 자격 증명과 native custom protocol 환경은 제공되지 않아 각각 network mock과 Vitest로 검증했다. 기존 HeroUI warning은 범위 밖이다.

## 다음 단계

현재 브랜치를 보존하고 사용자에게 commit·merge 계약 승인을 요청한다.
