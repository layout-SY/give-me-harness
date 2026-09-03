<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/hosts/codex/multi-agent-spec/05-pipeline-and-status.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 05 파이프라인과 상태

상태 전이는 `EXPLORE -> PLAN -> AWAIT_APPROVAL -> IMPLEMENT -> WATCHER_REVIEW -> EVALUATE -> DOCUMENT -> COMPLETE` 순서다. FAIL이면 범위에 따라 IMPLEMENT 또는 PLAN으로 돌아간다. 차단된 작업은 누락된 입력을 보고하며 승인을 추측하지 않는다.
