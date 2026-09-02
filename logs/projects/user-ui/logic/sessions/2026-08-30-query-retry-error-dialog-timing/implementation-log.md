# 구현 로그

## 승인된 범위

- `src/app/providers/queryClient.ts`
- `src/app/providers/queryClient.test.ts`
- `src/pages/citizen-participation/ui/CitizenDataRoutes.test.tsx`
- `.codex/logs/sessions/2026-08-30-query-retry-error-dialog-timing/`

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `src/app/providers/queryClient.ts` | server failure retry를 `500 <= statusCode < 600`으로 제한 | 404를 포함한 4xx는 즉시 terminal 처리 |
| `src/app/providers/queryClient.test.ts` | 404 server failure의 기대 시도 횟수 1회 추가 | 현 구현에서 RED, 수정 후 GREEN |
| `src/pages/citizen-participation/ui/CitizenDataRoutes.test.tsx` | 지연 main query 중 route 이탈 후 observer 0명·`fetchStatus: idle`·요청 1회 검증 | query 비활성 복원 계약 고정 |

## 결정 사항

- 408·429를 포함한 모든 4xx는 현재 승인된 정책대로 재시도하지 않는다.
- 5xx·transport·분류 불가 오류의 기존 최대 1회 retry는 유지한다.
- query 상태 테스트와 Chromium 네트워크 QA를 분리해 jsdom/MSW의 signal 관찰 한계를 우회한다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| `npm exec vitest -- run src/app/providers/queryClient.test.ts` (RED) | 404에서 `Expected 1 / Received 2`, 1개 실패·11개 통과 |
| `npm exec vitest -- run src/app/providers/queryClient.test.ts` (GREEN) | 12개 통과 |
| `npm exec vitest -- run src/app/providers/queryClient.test.ts src/pages/citizen-participation/ui/CitizenDataRoutes.test.tsx` | 2개 파일·17개 통과 |
| 변경 3개 파일 targeted ESLint | 출력 없이 통과 |
| `npm run build` | `tsc -b`와 Vite build 성공, 기존 500 kB 초과 청크 경고 |
| `npm run lint` | 출력 없이 통과 |
| `npm run test` | Vitest 62개 파일·454개 테스트, governance 20개 테스트 통과 |
| Playwright 404 시나리오 | `/citizen/main` 1회, 응답 후 약 91ms에 `NOT_FOUND` Dialog 표시 |
| Playwright route 이탈 시나리오 | `/citizen/main` 1회, `net::ERR_ABORTED`, 제안 route 도착, 오류 Dialog 0개 |

## Watcher 인계

- 최초 판정: FAIL
- 최초 Watcher 식별자: `ses_fadde9e5effexy3CCEy06v5Iii`
- 최초 차단 사유: 코드 결함이 아니라 필수 8종 세션 문서 부재
- 조치: 필수 문서를 작성하고 동일 Watcher에게 재검토를 요청했다.
- 최종 판정: PASS
- 최종 근거: 8종 문서 완결성, 4xx/5xx retry 경계, route 상태 복원, lint·test·build를 독립 재검증했으며 필수 조치가 없었다.
