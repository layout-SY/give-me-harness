<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/hosts/claude/harness/approval-gate.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# Approval Gate

- Planner는 계획된 UI 내용을 generator/publisher/refactorer에게 이관하기 전 사용자 승인을 받아야 한다.
- generator/publisher/refactorer는 승인 없이 UI 코드를 생성하지 않는다.
- 승인은 Claude Code가 기능 로직 또는 Hephaestus 소유 파일을 수정할 권한을 포함하지 않는다.
