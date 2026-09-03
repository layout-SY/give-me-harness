# 최종 요약

## 제공 사항

- proposal list 전용 요청/응답 DTO와 parser
- `getProposalList`는 `page`/`size`만 전송
- 내 활동은 `/me/activity?content=&page=&size=`로 분리
- 목록 훅·MSW·`CitizenListRoutes`가 새 목록 DTO를 직접 사용
- `code === "SUCCESS"` envelope 수용

## 제외 사항

- proposal 상세/작성 API
- 다른 콘텐츠 타입 목록 응답 재설계
- 목록 카드 요약 UI 제거
- activity 응답 본문 재설계

## 검증

| 명령어 | 결과 |
| --- | --- |
| `npx vitest run src/pages/citizen-participation/ui/CitizenDataRoutes.test.tsx src/features/citizen-participation src/pages/citizen-participation/model` | 43 passed |
| `npm run build` | 성공 |
| `npm run lint` | 성공 |

## 산출물

`.codex/logs/sessions/2026-08-25-proposal-list-api-contract/`의 plan, exploration, implementation-log, grill-me-review, review-log, evaluation-log, final-summary, portfolio-log

## 남은 제한 사항

- 목록 카드 summary는 빈 값이다.
- activity 응답 스키마는 기존 content list 형태다.
- `REJECTED` 제안은 기존 UI 규칙대로 목록에서 빠진다.

## 다음 단계

proposal 상세와 activity 응답이 확정되면 같은 방식으로 DTO를 맞춘다.
