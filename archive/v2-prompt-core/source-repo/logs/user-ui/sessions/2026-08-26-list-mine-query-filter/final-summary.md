# 최종 요약

## 제공 사항

- 제안·투표·토론·정책 목록이 `mine=true|false`를 항상 전송
- 목록 「내 활동만 보기」가 `/me/activity`를 치지 않음
- `useMyProposalActivityQuery` 삭제
- 내 활동 페이지 제안 탭은 `GET /citizen/proposals?mine=true`
- MSW·테스트가 목록 `mine` 필터를 검증

## 제외 사항

- 내 활동 페이지 전체/비제안 조회 (`/me/activity`)
- 설문 목록 `mine`
- 정렬 UI

## 검증

| 명령어 | 결과 |
| --- | --- |
| `npx vitest run src/pages/citizen-participation/ui/CitizenDataRoutes.test.tsx src/features/citizen-participation src/pages/citizen-participation/model` | 66 passed |
| `npm run build` | 성공 |
| `npm run lint` | 성공 |

## 산출물

`.codex/logs/sessions/2026-08-26-list-mine-query-filter/`의 plan, exploration, implementation-log, grill-me-review, review-log, evaluation-log, final-summary, portfolio-log

## 남은 제한 사항

- 내 활동 페이지의 비제안 필터는 `/me/activity`다.
- 화면 URL 이름은 `myActivity`다.

## 다음 단계

내 활동 페이지 계약이 확정되면 비제안 탭도 같은 목록 `mine`으로 옮길지 결정한다.
