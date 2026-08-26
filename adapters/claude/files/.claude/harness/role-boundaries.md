# Role Boundaries

- Claude 기본 세션은 파이프라인을 오케스트레이션한다. Planner는 UI와 기능 로직을 포함한 전체 범위를 호출 단위로 계획할 수 있지만 코드를 수정하거나 다른 서브 에이전트를 중첩 실행하지 않는다.
- Publisher는 UI 구조와 props/callback 계약만 정의하고 기능 로직을 구현하지 않는다.
- Generator는 `CLAUDE.md`의 production UI 소유 경로만 구현한다.
- Refactorer는 Claude Code 소유 UI 파일만 동작 보존 방식으로 정리한다.
- Watcher는 별도 리뷰 도구 없이 직접 읽고 판정하며 구현을 수정하지 않는다.
- Evaluator는 전체 코드의 장기 구조를 읽기 전용으로 평가하며 사용자가 직접 요청하거나 Evaluator가 포함된 계획을 승인한 경우에만 동작하고 승인 게이트를 대신하지 않는다.
- hook, util, API, parser, validator, store, 상태 전이와 통합 파일은 Logic Session 소유다.
- Planner/Evaluator의 전역 읽기 권한은 Claude 기본 구현 세션의 쓰기 소유권을 확장하지 않는다.
