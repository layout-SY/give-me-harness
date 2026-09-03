<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/hosts/codex/workflows/hybrid-workflow.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 혼합 워크플로

단계를 분리하여 계획해야 한다. 먼저 동작을 보존하는 리팩터링을 수행하고, 그다음 기능을 구현해야 한다. 각 단계에는 명확한 범위와 검증 방법이 있어야 하며, 기능 범위가 변경되면 갱신된 승인을 요청해야 한다. Watcher는 통합 결과를 검토하고 단계별 실패를 식별해야 한다. `portfolio-log.md`에는 리팩터링과 기능 구현의 문제·선택·적용·결과를 사례별로 구분한다.
