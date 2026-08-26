# Refactor Workflow

## 단계별 흐름

1. Planner가 승인된 UI 리팩터링 범위와 Claude Code 소유 파일을 확정한다.
2. Refactorer가 props/callback 의미와 사용자 동작을 보존하며 UI 마크업·스타일만 정리한다.
3. 기능 파일 변경이 필요하면 사용자에게 Logic Session 작업으로 전달하고 중지한다.
4. `npm run build`, `npm run lint`와 필요한 기존 테스트를 실행한다.
5. Watcher가 별도 reviewer 없이 변경 범위와 정적 근거를 직접 판정한다.
6. PASS 후 `UI_COMPLETE` 또는 UI 리팩터링 완료 내용을 사용자에게 인계한다.

## 제한

- code-simplifier, code-review, pr-review-toolkit 또는 별도 리뷰 에이전트를 실행하지 않는다.
- hook, util, API, 상태 전이 또는 통합 파일을 수정하지 않는다.
- 이미지 캡처, 화면 비교 및 시각 QA를 수행하지 않는다.
