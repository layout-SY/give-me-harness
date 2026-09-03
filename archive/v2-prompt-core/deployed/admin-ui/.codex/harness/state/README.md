<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/hosts/codex/harness/state/README.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# Harness 상태

런타임 마커는 프로젝트 외부의 `$TMPDIR/codex-harness-state-v2/<root-hash>/`에 저장한다. 이 디렉터리는 상태 계약을 설명하는 용도로만 사용하며, 현재 사용 중이거나 마이그레이션한 런타임 상태를 포함해서는 안 된다.
