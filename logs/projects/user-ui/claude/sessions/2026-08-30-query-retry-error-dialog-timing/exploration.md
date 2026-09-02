# 탐색

## 요청

페이지 이동 후 `/citizen/main` 로딩이 남고 404 Dialog가 누락되거나 늦게 표시되는 현상을 조사한 뒤 승인된 수정 계획을 구현한다.

## 대상 관련 사실

- `useCitizenParticipationMainQuery`는 TanStack Query의 `signal`을 `meApi.getCitizenParticipationMain`과 Axios `config.signal`까지 전달한다.
- 실제 브라우저에서 응답 대기 중 `제안` route로 이동하면 `/citizen/main`은 `net::ERR_ABORTED`로 종료됐다.
- 기존 `shouldRetryQuery`는 401을 제외한 모든 server failure를 한 번 재시도했다.
- 404를 유지한 브라우저 재현에서는 약 1초 간격으로 두 번 요청한 뒤 terminal Dialog가 표시됐다.
- `serverErrorQueue`는 `code + path`를 3초간 dedupe하고 `ApiErrorDialogBridge`는 다른 Dialog가 열려 있으면 표시를 보류한다.
- production query별 `retry` override는 없으며 시민참여 query 전체가 전역 기본값을 상속한다.

## 불러온 스킬

- `policy-git-branch-strategy`
- `policy-harness`
- `policy-coding-convention`
- `policy-data-fetch-layer`
- `policy-documentation`
- `policy-review-checklist`
- `policy-portfolio`
- `policy-type-definition`
- `policy-codex-native-quality`
- `programming`
- `debugging`
- `playwright`
- `git-master`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| `src/shared/ui/dialog/` | 변경하지 않음 | 지연의 직접 원인은 Dialog 컴포넌트가 아니라 query retry 예산이었다. |
| `src/shared/ui/loading/` | 변경하지 않음 | route 이탈 시 query가 실제로 취소되어 loading UI 수정이 필요하지 않았다. |

## 제약 조건 및 미확인 사항

- 실제 인증 토큰 없이 Playwright route override로 서버 응답을 통제했다.
- jsdom/MSW에서는 transport `AbortSignal`을 직접 관찰하지 못해 Query의 observer·fetch 상태와 실제 Chromium 네트워크 이벤트를 결합했다.
- TypeScript LSP는 미설치 상태이며 설치 거절 기록 때문에 실행하지 않았다.

## 결론

root fix는 전역 query retry를 5xx에만 허용하는 최소 변경이며, route 취소 로직과 Dialog queue 자체는 수정하지 않는다.
