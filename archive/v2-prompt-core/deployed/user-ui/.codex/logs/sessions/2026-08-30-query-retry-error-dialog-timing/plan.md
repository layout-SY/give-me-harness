# 계획

## 목표

`/citizen/main`의 404를 불필요하게 재시도해 오류 Dialog가 늦게 나타나는 문제를 제거하고, route 이탈 시 진행 중인 query가 비활성 상태로 복원되는 계약을 회귀 테스트로 고정한다.

## 범위

- `src/app/providers/queryClient.ts`의 전역 query retry 분류
- `src/app/providers/queryClient.test.ts`의 404·5xx·transport retry 예산 검증
- `src/pages/citizen-participation/ui/CitizenDataRoutes.test.tsx`의 시민참여 메인 route 이탈 검증
- 현재 세션의 필수 8종 산출물

## 제외 사항

- `serverErrorQueue`의 3초 dedupe와 Dialog gating 정책 변경
- production UI 마크업·스타일 변경
- mutation retry 정책 변경
- 기존 Vite 대형 청크 경고 개선

## 제약 조건

- 브랜치는 `sy-main@f4a7323c3a38fb416164d780b50d8db926af2208`에서 `task/query-retry-error-dialog-timing`으로 분기하고 직접 merge 대상은 `sy-main`이다.
- TypeScript LSP는 사용자가 설치를 거절한 상태이므로 `tsc -b`가 포함된 `npm run build`로 타입을 검증한다.
- 스크린샷·GIF·화면 비교·시각 QA는 수행하지 않는다.
- production UI 파일은 변경하지 않는다.

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 탐색·계획 | Planner | `policy-git-branch-strategy`, `policy-data-fetch-layer`, `policy-type-definition` | 전역 retry seam과 승인 범위 확정 |
| 구현 | Generator | `programming`, `debugging`, `policy-coding-convention` | RED→GREEN 최소 수정과 route 회귀 테스트 |
| 검토 | Watcher | `policy-review-checklist`, `policy-harness` | 독립 PASS 또는 FAIL 판정 |
| 평가 | Evaluator | `policy-codex-native-quality`, `policy-portfolio` | 장기 개선 사항을 현재 판정과 분리해 기록 |

## 검증

- 404 테스트의 RED→GREEN 전환
- 변경 파일 targeted Vitest와 ESLint
- `npm run build`, `npm run lint`, `npm run test`
- 실제 브라우저에서 404 요청 횟수·Dialog와 route 이탈 abort 확인
- 독립 Watcher 재검토

## 위험 요소 및 결정 사항

- 4xx 전체를 영구 실패로 취급하고 5xx·transport·분류 불가 오류의 기존 1회 retry는 유지한다.
- `CitizenDataRoutes.test.tsx`의 jsdom/MSW `Request.signal`은 Axios abort를 반영하지 않아, route 테스트는 observer 수와 `fetchStatus` 복원을 검증하고 실제 네트워크 abort는 브라우저에서 확인한다.
- route 테스트 파일은 순수 LOC 238줄의 경고 구간이므로 이번 범위에서 더 확장하지 않는다.

## 승인

- 상태: approved
- 구현 승인: 사용자의 `계획대로 작업`
- 브랜치 승인: `branch:task/query-retry-error-dialog-timing|parent:sy-main@f4a7323c3a38fb416164d780b50d8db926af2208|merge:sy-main`
- 필수 문구: `이 계획대로 진행할까요, 아니면 조정할 부분이 있나요?`
