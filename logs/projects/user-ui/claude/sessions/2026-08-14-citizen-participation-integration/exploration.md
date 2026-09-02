# 시민참여 production UI 통합 탐색

## 결론

- Handoff: `.claude/logs/sessions/2026-08-14-citizen-participation-mobile-ui/handoff-hephaestus.md`, 상태 `UI_COMPLETE`.
- Claude Code 소유 경로는 `src/features/citizen-participation/ui/**`, `src/shared/ui/**`이며 이번 통합에서 수정하지 않는다.
- 13개 page는 모두 default export이며 controlled props/callback을 제공한다.
- 기존 query는 main, 5개 목록/상세, comments, my activity를 지원한다.
- 기존 mutation은 proposal create, vote, discussion participation, survey answer, comment, like, report를 제공한다.
- Generic DTO에는 author, 기간, D-Day, 설문 문항, 정책 처리 단계가 없다.
- 제안 UI values에는 API 필수 `category`가 없고 report UI는 comment id를 주지만 API는 content id를 요구한다.

## 결정

- Service tab `all`은 `citizenParticipationRoutes.main`으로 이동한다.
- API 미제공 표시값은 빈 controlled value로 전달해 PDF 예시 fallback을 차단한다.
- `scheduled` vote/discussion은 제출을 허용하지 않는 closed 상태로 보수적으로 표시한다.
- 제안 제출, comment 신고, survey 참여는 계약 확보 전 요청하지 않는다.

## 불러온 스킬

- `project-ui`, `reference-index`, `reference-components`, `reference-custom-hooks`
- `policy-harness`, `programming`
