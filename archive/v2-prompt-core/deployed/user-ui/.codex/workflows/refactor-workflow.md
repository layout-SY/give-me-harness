<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/hosts/codex/workflows/refactor-workflow.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 리팩터링 워크플로

Planner는 현재 동작, 작업 범위, 검증 방법을 확정해야 하며 반드시 승인을 받아야 한다. Refactorer는 동작을 확장하지 않고 한 번에 하나의 경계만 변경해야 한다. Watcher는 동작과 품질을 검증해야 한다. Evaluator는 유예된 기술 부채와 재사용 가능한 패턴을 기록해야 한다. 검증 후 리팩터링 요청, 대안, 선택 이유, 적용 전후 구조를 `portfolio-log.md`에 기록한다.
