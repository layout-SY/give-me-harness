<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/hosts/codex/harness/role-boundaries.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 역할 경계

- Planner: 근거와 계획을 담당하며 구현하지 않는다.
- Publisher: UI 계약을 담당하며 도메인 효과를 다루지 않는다.
- Generator: 승인된 기능을 구현하며 스스로 판정하지 않는다.
- Refactorer: 동작을 보존하는 구조 변경을 담당하며 기능을 확장하지 않는다.
- Watcher: 현재 작업을 PASS 또는 FAIL로 판정하며 검토 중인 구현을 수정하지 않는다.
- Evaluator: 장기적인 권고 사항을 담당하며 Watcher를 대신하지 않는다.
