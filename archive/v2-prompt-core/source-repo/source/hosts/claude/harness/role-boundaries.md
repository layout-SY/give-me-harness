# Role Boundaries

- Planner는 Claude Code UI 범위만 계획하고 코드를 수정하지 않는다.
- Publisher는 UI 구조와 props/callback 계약만 정의하고 기능 로직을 구현하지 않는다.
- Generator는 `CLAUDE.md`의 production UI 소유 경로만 구현한다.
- Refactorer는 Claude Code 소유 UI 파일만 동작 보존 방식으로 정리한다.
- Watcher는 별도 리뷰 도구 없이 직접 읽고 판정하며 구현을 수정하지 않는다.
- Evaluator는 사용자가 명시적으로 요청한 평가에서만 동작하고 승인 게이트를 대신하지 않는다.
- hook, util, API, parser, validator, store, 상태 전이와 통합 파일은 Hephaestus 소유다.
