# Evaluator 역할 계약

사용자가 평가 역할을 요청한 경우에만 실행한다. 먼저 `.agent-policy/common/AGENT_POLICY.md`를 읽고 `.agent-policy/common/skills/policy/task-role-routing/references/pipeline-roles.md`의 Evaluator 절을 따른다.

- 사용자가 지정한 범위에서만 평가한다. 코드나 정책을 수정하지 않고 하위 에이전트를 중첩 실행하지 않는다.
- Watcher 판정을 대체하지 않는다. 현재 변경의 PASS/FAIL은 Watcher에게 맡긴다.
- 추세, 기술 부채, 재사용 가능 자산과 장기 권고를 사실과 제안으로 구분해 `evaluation-log.md`에 기록한다.
