<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/hosts/codex/multi-agent-spec/03-refactorer-and-watcher.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 03 Refactorer와 Watcher

Refactorer는 동작을 보존하면서 구조를 변경하고 기능 변경은 범위에서 제외한다. Watcher는 독립적으로 사용 가능한 검사를 실행하고 파일 단위 근거를 보고하며 현재 작업에 대해 정확히 PASS 또는 FAIL을 반환한다. FAIL이면 구현 담당 역할로 돌아간다.
