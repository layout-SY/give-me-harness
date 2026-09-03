# 검토 로그

## Watcher 판정

PASS

## 검토 범위

`.codex/logs/sessions/2026-08-27-sy-main-pr-definition/pr-definition.md`가 `origin/main...sy-main` git 결과와 현재 소스(`routing.ts`, `authSession.ts`, `startMocks.ts`, `attach-access-token.ts`, `proposal.api.ts`)와 맞는지 확인했다. 애플리케이션 코드는 이 세션에서 수정하지 않았다.

## 점검 항목

| 점검 | 결과 | 근거 |
| --- | --- | --- |
| 목표 충족 | PASS | `main` 대비 `sy-main` 작업을 Summary·라우트·인증·MSW·테스트 계획으로 정의함 |
| 승인 근거 | PASS | 사용자가 PR 문서 작성을 요청. 앱 코드 미수정 |
| 불러온 스킬 | PASS | documentation, harness, portfolio, review-checklist |
| `src/shared/ui/` 재사용 서술 | PASS | tabs 추가, showcase 제거, 기존 button/text-input 재사용을 문서에 구분 |
| 숫자 정확성 | PASS | 114 커밋, 314/+16555/-568, 앱 169/+11783/-568를 명령 출력과 대조 |
| 라우트 정확성 | PASS | `citizenParticipationRoutes`·`app/routing.ts`와 표가 일치 |
| 인증 서술 | PASS | loginId, Bearer, refresh 회전, `oasisapp://login`이 현재 코드와 일치 |
| 미커밋 혼입 | PASS | `vite --port 12001`과 AGENTS.md 귀속 절을 PR 범위에서 제외한다고 명시 |
| 빌드/린트 | 해당 없음 | 앱 변경 없음. 실행하지 않음을 implementation-log에 기록 |

## 발견 사항

| 심각도 | 경로 | 발견 사항 | 필수 조치 |
| --- | --- | --- | --- |
| 정보 | `src/features/auth/hook/useSignInMutation.ts` | 로그인 성공 시 토큰을 딥링크 쿼리에 넣는다. 설계 문서(`docs/external-browser-deep-link-auth.md`)는 이를 보류·비목표로 적는다 | PR 본문에 현재 동작과 문서 보류를 함께 적어 두었다. 코드 변경은 이 작업 범위 밖 |
| 정보 | `.codex/**` in diff | 과거 세션 로그가 커밋에 포함되어 전체 파일 수가 부풀어 있다 | 앱 규모를 별도 숫자로 분리해 적었다 |

## 결론

PR 정의서는 비교 기준, 기능 묶음, 라우트, 제외 범위를 git·현재 코드와 맞게 적었다. PASS.
