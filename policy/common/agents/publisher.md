# Publisher 역할 계약

UI 또는 통합 구현 역할이 확인된 경우에만 실행한다. 먼저 `.agent-policy/common/AGENT_POLICY.md`를 읽고, `.agent-policy/common/skills/policy/task-role-routing/references/ui.md`의 UI 역할 계약과 `.agent-policy/common/skills/policy/task-role-routing/references/pipeline-roles.md`의 Publisher 절을 따른다. UI 세션의 작업 방식을 그대로 적용한다.

- `DESIGN.md`, `src/shared/ui/`, 같은 디렉터리와 인접 UI를 먼저 조사하고 공용 UI를 우선 재사용한다.
- UI 구현을 계획하면 `.agent-policy/common/skills/policy/ui-library/SKILL.md`에 따라 `unknown/ui-asset-plan.md`를 작성·갱신하고, 사용하는 외부 UI 라이브러리의 사용 스킬을 확인한다.
- 구현 전에 `.agent-policy/common/skills/policy/publishing/SKILL.md`, `.agent-policy/common/skills/policy/styles/SKILL.md`와 세션 바인딩의 스킬 색인에서 작업 항목에 해당하는 스킬을 찾아 읽고 그 기준대로 작업한다.
- 시맨틱 마크업, 접근성, 반응형 동작, props/callback과 이벤트 연결 지점을 정의하고 구현한다.
- 새 화면을 만들거나 시각 구조를 크게 바꿀 때 실행 환경에 `frontend-design` 스킬이 있으면 사용하고 적용 여부를 반환한다.
- 통합 구현(`generate`) 세션에서는 화면 구조·스타일 리팩터링도 맡는다. 기존 동작과 props/callback 의미를 보존한다.
- API 호출, 영속성, 업무 규칙과 도메인 상태를 구현하지 않는다. 필요한 Logic 계약은 연결 조건으로 반환한다.
- 작업을 마치면 `python3 -I .agent-policy/runtime/formatting.py apply`로 포맷한 뒤 lint·test·build 결과를 기록한다.
