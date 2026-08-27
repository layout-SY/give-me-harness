# 최종 요약

## 제공 사항

- `GET /citizen/proposals` query에 `mine?`·`sort?` (`createdAt`/`id`, 기본 `createdAt,desc`)
- `mine===true`일 때만 `mine=true`와 인증 설정을 전송
- 제안 목록 「내활동만 보기」가 같은 목록 API를 사용
- 목록 아이템에 본문 4필드 없음
- MSW·테스트가 `mine=true` 필터와 기본 sort를 검증

## 제외 사항

- 투표·토론·정책 목록의 activity API
- 내 활동 페이지
- 정렬 UI
- 목록 카드 summary 제거

## 검증

| 명령어 | 결과 |
| --- | --- |
| `npx vitest run src/pages/citizen-participation/ui/CitizenDataRoutes.test.tsx src/features/citizen-participation src/pages/citizen-participation/model` | 62 passed |
| `npm run build` | 성공 |
| `npm run lint` | 성공 |

## 산출물

`.codex/logs/sessions/2026-08-26-proposal-list-mine-filter/`의 plan, exploration, implementation-log, grill-me-review, review-log, evaluation-log, final-summary, portfolio-log

## 남은 제한 사항

- 목록 카드 summary는 빈 값이다.
- 투표 목록은 여전히 `/me/activity`다.
- 정렬은 기본값만 보내고 화면 컨트롤은 없다.

## 다음 단계

다른 콘텐츠 타입에 `mine`이 확정되면 같은 list query 패턴으로 옮긴다.
