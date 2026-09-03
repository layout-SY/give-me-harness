---
name: project-ui
description: {{PROJECT_NAME}}에서 UI 역할이 사용자에게 확인된 경우 공통 UI 정책으로 연결하는 Claude Code 호환 진입점입니다.
---

# Project UI 호환 진입점

이 스킬은 Claude Code의 기본 역할을 UI로 지정하지 않는다. 사용자 요청과 handoff를 바탕으로 UI 또는 통합 구현 역할이 확인된 경우에만 사용한다.

1. `.claude/skills/project-role/SKILL.md`를 따른다.
2. `.agent-policy/common/skills/policy/task-role-routing/references/ui.md`를 읽는다.
3. 통합 구현 역할이면 `.agent-policy/common/skills/policy/task-role-routing/references/logic.md`도 함께 읽는다.
4. `DESIGN.md`, `src/shared/ui/`, 같은 디렉터리와 인접 구현을 조사한다.

완료·인계·검증은 `.agent-policy/common/AGENT_POLICY.md`와 `.agent-policy/common/skills/policy/task-role-routing/references/handoff-and-ownership.md`를 따른다.
