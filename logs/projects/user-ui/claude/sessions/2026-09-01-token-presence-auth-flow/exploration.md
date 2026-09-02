# 탐색

## 요청

- 로그인 사용자에게 댓글 작성기가 비활성화되는 원인이 권한인지 중복 인증 판정인지 확인한다.
- `/me` query를 로그인 판정에 사용하지 않고 token presence·401·로그인 복귀 흐름으로 통합한다.

## 대상 관련 사실

- Vote·Discussion·Policy route는 `meQuery.isSuccess`를 `isAuthenticated`로 전달해 `/me` pending/error에서 댓글을 비활성화했다.
- 댓글 enablement에는 role·permission 검사가 없고 boolean 인증 상태만 사용됐다.
- `authSession`은 이미 revision listener를 가진 external store이며 Zustand는 다른 UI 상태에만 사용됐다.
- URL의 `access-token`, `refresh-token`을 localStorage로 가져오는 bootstrap은 없었다.
- React Query 401은 이미 `reportApiFailure`를 통해 `serverErrorQueue`의 `reauthenticate` 이벤트로 변환됐다.
- `ApiErrorDialogBridge`는 Dialog 종료 시 session을 지우고 안전한 `returnTo`와 함께 `/login`으로 이동했다.
- 로그인 성공 후 `LoginTestPage`가 기존 `returnTo`로 복귀하는 흐름과 테스트가 존재했다.

## 불러온 스킬

- `policy-git-branch-strategy`, `policy-harness`, `policy-coding-convention`
- `policy-hook-extraction`, `policy-validation`, `policy-documentation`
- `policy-portfolio`, `policy-review-checklist`, `programming`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| `src/shared/ui/dialog/` | 재사용 | 기존 401 reauthentication alert가 확인·Escape 종료 callback을 제공함 |
| `src/shared/ui/modal/` | 제외 | 401 흐름이 이미 Dialog queue에 통합되어 있어 두 번째 시스템이 됨 |
| `src/shared/lib/pub-sub/` | 제외 | 실제 401 정본은 pub-sub이 아니라 `serverErrorQueue` external store임 |

## 제약 조건 및 미확인 사항

- TypeScript LSP는 이전 사용자 거절로 설치되지 않아 diagnostics를 실행할 수 없었다.
- 실제 회사 backend credential은 없으므로 live backend 401은 MSW·integration test로 검증했다.
- 브라우저 자동화와 시각 QA는 정책상 수행하지 않았다.

## 결론

- 원인은 권한 부족이 아니라 `/me` query 상태와 로그인 존재 상태의 잘못된 결합이었다.
- 새 Zustand store나 interceptor를 추가하지 않고 기존 authSession external store와 전역 401 Dialog 흐름을 재사용하는 것이 최소 변경이다.
