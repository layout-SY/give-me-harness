<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/hosts/codex/harness/retry-policy.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 재시도 정책

구체적인 원인을 확인한 후에만 재시도한다. Watcher가 FAIL을 반환하면 구현을 한 번 재시도하며, 다시 실패하면 근거와 조정된 범위를 첨부하여 Planner에게 상향 보고한다. 새로운 정보 없이 동일한 명령을 두 번 넘게 반복하지 않는다.
