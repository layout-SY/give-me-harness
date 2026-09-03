<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/hosts/codex/workflows/README.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 워크플로

- `feature-workflow.md`: 새로운 동작을 구현하는 워크플로.
- `refactor-workflow.md`: 동작을 보존하면서 구조를 변경하는 워크플로.
- `hybrid-workflow.md`: 기능 구현 단계와 리팩터링 단계를 명시적으로 분리하는 워크플로.
- `audit-workflow.md`: 읽기 전용 평가 워크플로.
- `escalation-workflow.md`: 작업이 차단되었거나 반복해서 실패할 때 사용하는 워크플로.

변경을 수행하는 모든 워크플로에는 승인 게이트와 Watcher 게이트가 포함되어야 한다.
