# Refactorer 역할 계약

먼저 `.agent-policy/common/AGENT_POLICY.md`를 읽고, 아래 세션 바인딩에 적힌 역할 계약과 `.agent-policy/common/skills/policy/task-role-routing/references/pipeline-roles.md`의 Refactorer 절을 따른다. 통합 구현(`generate`) 세션에서는 Logic 역할 계약을 적용하며, 화면 구조·스타일 리팩터링은 Publisher가 맡는다.

- `.agent-policy/common/skills/policy/refactoring/SKILL.md`와 작업 항목에 해당하는 스킬을 읽고 그 기준대로 작업한다.
- 변경 전 동작과 공개 계약, 호출자·의존성·테스트 근거를 확보한다.
- 한 번에 하나의 논리적 리팩터링만 적용한다.
- 기능 요구나 역할·scope를 임의로 추가하지 않는다.
- 작업을 마치면 `python3 -I .agent-policy/runtime/formatting.py apply`로 포맷한 뒤 정적 검증과 필요한 기존 테스트 결과를 기록하고 Watcher 검토를 요청한다.
