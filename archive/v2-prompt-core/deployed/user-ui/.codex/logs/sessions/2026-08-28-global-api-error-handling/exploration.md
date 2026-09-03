# 탐색

## 요청

전역 API 오류 분류·표시·진단과 인증 route/returnTo 흐름을 기존 구조에 통합한다.

## 대상 관련 사실

- Axios, fetch, ApiResult, TanStack Query, useApi가 서로 다른 오류 경계를 가졌다.
- Auth는 access token 외에 만료 시각과 stale refresh 보호가 필요했다.
- 기존 Dialog는 header/content/callback 계약을 제공하며 새 modal은 불필요했다.
- `/login` 외 route는 pathless boundary 아래로 묶을 수 있었다.

## 불러온 스킬

policy-git-branch-strategy, policy-harness, policy-coding-convention, policy-type-definition, policy-data-fetch-layer, policy-validation, policy-review-checklist, policy-documentation, policy-portfolio, playwright.

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| 기존 Dialog/useDialog | 재사용 | header/content/callback으로 오류 표시와 확인 전이를 충족한다 |
| 새 modal | 제외 | 기존 UI 계약 중복이며 scope 밖 변경을 유발한다 |

## 제약 조건 및 미확인 사항

실제 회사 API 자격 증명은 제공되지 않아 로그인 성공은 Chromium network mock으로 검증했다. native custom protocol은 브라우저 이동 대신 Todo 12 Vitest를 정본 근거로 사용했다.

## 결론

UI 변경 없이 transport/domain/state/UI 책임을 분리한 공통 failure reporter와 외부 store queue를 적용하는 방향이 적합했다.
