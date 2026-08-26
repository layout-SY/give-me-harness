# Retry Policy

- Maximum rejection count per task section: 3
- Same rejection reason repeated twice triggers escalation
- Escalation target depends on root cause:
  - scope issue -> Planner
  - structural debt -> Evaluator
  - unclear requirement -> User
