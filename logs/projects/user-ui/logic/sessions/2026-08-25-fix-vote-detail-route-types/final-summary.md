# 최종 요약

## 제공 사항

`VoteDetailRoute`가 feature barrel 대신 훅·페이지 깊은 경로를 쓰도록 바꿔 `useVoteDetailQuery`/`persistedChoice` eslint 오류를 제거했다.

## 제외 사항

- 상세 API/DTO, `VoteDetailPage` 마크업, 전체 라우트 barrel 일괄 제거

## 검증

| 명령어 | 결과 |
| --- | --- |
| ReadLints 대상 파일 | 오류 없음 |
| `npx eslint src/pages/citizen-participation/ui/CitizenParticipationDetailRoutes.tsx` | 성공 |
| `npx vitest run` CitizenCommentRoutes·CitizenResultRoutes | 10 passed |

## 산출물

`.codex/logs/sessions/2026-08-25-fix-vote-detail-route-types/`

## 남은 제한 사항

다른 pages 라우트가 barrel에서 훅을 가져오면 같은 오류가 날 수 있다.

## 다음 단계

같은 eslint 오류가 나면 barrel 대신 훅 깊은 경로를 먼저 적용한다.
