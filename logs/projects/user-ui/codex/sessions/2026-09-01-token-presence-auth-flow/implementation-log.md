# 구현 로그

## 승인된 범위

- 브랜치: `task/token-presence-auth-flow`
- 부모·직접 merge 대상: `sy-main@5e2a97e495c473f348dc25a58163bdf0ea3b293e`
- 승인 scope: auth model/hook, app route boundary·tests, startup, 세 시민참여 UI route·test, 현재 세션 문서

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `src/features/auth/model/authSession.ts` | token presence selector와 URL bootstrap 추가 | localStorage 우선, credential query 제거 |
| `src/features/auth/hook/useAuthTokenPresence.ts` | revision store React 구독 | session 저장·삭제에 반응하는 boolean 제공 |
| `src/main.tsx` | bootstrap을 모든 비동기 startup보다 먼저 실행 | URL credential 제거 지연 방지 |
| `src/app/providers/AuthRouteBoundary.tsx` | expiry 선판정 제거, token 없음 direct login redirect | backend 401을 authoritative 신호로 유지 |
| `src/pages/citizen-participation/ui/CitizenParticipationDetailRoutes.tsx` | Vote·Discussion `/me` 의존 제거 | token presence로 댓글 작성 가능 판단 |
| `src/pages/citizen-participation/ui/CitizenReadDetailRoutes.tsx` | Policy `/me` 의존 제거 | token presence로 댓글 작성 가능 판단 |
| 관련 테스트 | bootstrap, redirect, expiry 비차단, 401 종료, 세 댓글 route 회귀 | 사용자 요구 경계 고정 |

## 결정 사항

- Zustand를 추가하지 않고 기존 authSession external store를 정본으로 유지했다.
- token이 하나라도 있으면 UI를 허용하고 유효성·권한 실패는 backend 401에 맡겼다.
- token 없음은 Dialog 없이 `/login`, token 요청 401은 기존 Dialog 종료 후 `/login`으로 구분했다.
- Watcher 초기 FAIL에 따라 bootstrap을 `startMocks()`보다 앞으로 이동했다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| 관련 auth/UI suite | 6 files, 47 tests PASS |
| `npm run test` | Vitest 63 files, 469 tests PASS, governance 20 tests PASS |
| `npm run lint` | PASS |
| `npm run build` | PASS, 기존 chunk size 경고 |
| `git diff --check` | PASS |
| 변경 파일 pure LOC | 모두 250 이하, `authSession.test.ts` 235로 warning band |
| no-excuse checker | `bun` 미설치 및 Node type stripping 제한으로 실행 불가; ESLint·tsc로 대체 |

## Watcher 인계

- 초기 판정: FAIL. URL token bootstrap 지연과 UI_COMPLETE 문서 불일치 지적.
- 조치: bootstrap 동기 선실행, handoff를 실제 UI_COMPLETE·검증 상태로 갱신.
- 최종 판정: PASS. 관련 7 files, 55 tests, lint, build 통과를 Watcher가 독립 확인.
