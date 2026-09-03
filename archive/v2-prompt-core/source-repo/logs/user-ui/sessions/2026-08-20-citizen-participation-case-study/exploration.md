# 탐색

## 현재 근거

- Codegraph로 제안 form·mutation·route, 댓글·신고 action hook, query key, MSW store와 route call path를 재탐색했다.
- `CLAUDE.md`에서 Claude Code UI 소유권, Hephaestus 기능 소유권, `UI_COMPLETE` handoff를 확인했다.
- `src/features/citizen-participation/`, `src/pages/citizen-participation/`, `src/shared/ui/`의 현재 디렉터리 경계를 확인했다.
- `src/features/citizen-participation/index.ts`의 public export와 page route의 deep import 편차를 확인했다.

## 불러온 스킬

- `skill-index`
- `policy-documentation`
- `policy-portfolio`
- `policy-harness`
- `policy-data-fetch-layer`
- `policy-hook-extraction`
- `policy-type-definition`

## 핵심 결론

- 현재 구조는 `app → pages → features → shared` 방향의 실용적 FSD다.
- action hook, typed mapper, stateful MSW는 실제 구현 근거가 있다.
- deep import, 인증 판정 결합, 수동 agent 중계는 문서에서 제한 사항으로 다뤄야 한다.
