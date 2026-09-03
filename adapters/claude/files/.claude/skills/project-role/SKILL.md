---
name: project-role
description: {{PROJECT_NAME}}의 Claude Code 세션에서 inject role 또는 사용자 확인을 호스트 중립 공통 역할 정책으로 연결합니다.
---

# Project Role

1. `.agent-policy/common/AGENT_POLICY.md`와 `CLAUDE.md`를 읽는다.
2. inject system prompt에 `--role`이 있으면 그 role profile을 사용하고 같은 범위에서 다시 묻지 않는다.
3. role이 없으면 `.agent-policy/common/skills/policy/task-role-routing/SKILL.md`로 역할을 제안하고 사용자 확인을 받는다.
4. `.agent-policy/common/skills/policy/git-branch-strategy/SKILL.md`로 현재 branch·worktree 계약을 확인한다.
5. 확인된 역할 reference와 바인딩된 공통 스킬만 읽는다.
6. Claude native agent와 workflow는 호스트 실행 형식으로만 사용하고 공통 역할 계약을 우선한다.

inject role이나 scope가 달라지면 구현을 중단하고 새 role 세션 또는 변경된 계약을 요청한다.
