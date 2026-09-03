<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/hosts/claude/harness/retry-policy.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# Retry Policy

- Maximum rejection count per task section: 3
- Same rejection reason repeated twice triggers escalation
- Escalation target depends on root cause:
  - scope issue -> Planner
  - structural debt -> Evaluator
  - unclear requirement -> User
