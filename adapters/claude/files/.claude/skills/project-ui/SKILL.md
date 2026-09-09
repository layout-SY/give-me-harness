---
name: project-ui
description: {{PROJECT_NAME}}에서 UI 역할이 사용자에게 확인된 경우 공통 UI 정책으로 연결하는 Claude Code 호환 진입점입니다.
---

# Project UI 호환 진입점

이 스킬은 Claude Code의 기본 역할을 UI로 지정하지 않는다. 사용자 요청과 handoff를 바탕으로 UI 또는 통합 구현 역할이 확인된 경우에만 사용한다.

1. `.claude/skills/project-role/SKILL.md`를 따른다.
2. `.agent-policy/common/skills/policy/task-role-routing/references/ui.md`를 읽는다.
3. 통합 구현 역할이면 주입된 시스템 프롬프트에 나열된 Logic reference도 함께 읽는다.
4. `DESIGN.md`, `src/shared/ui/`, 같은 디렉터리와 인접 구현을 조사한다.

## TalkToFigma 연결

중앙 launcher는 `user-ui`·`admin-ui`의 `host=claude`, `role=ui` 새 inject 세션에 TalkToFigma MCP를 기본 제공한다. 실행 정의는 중앙 `adapters/claude/mcp.defaults.json`에 있고, 세션은 불변 번들의 `claude-mcp.json`을 `--mcp-config`로 읽는다. `generate`를 포함한 다른 role에는 이 기본 MCP가 자동 주입되지 않는다.

Figma를 사용하는 작업에서는 다음을 확인한다.

1. `/mcp`에서 `TalkToFigma` 연결 상태와 `mcp__TalkToFigma__*` 도구 로드를 확인한다. 누락되면 현재 launcher 인자의 `--mcp-config`와 새 번들 적용 여부를 확인한다.
2. 로컬 WebSocket 서버와 Figma의 TalkToFigma 플러그인이 실행 중인지 확인한다. MCP 도구 로드 성공만으로 Figma 연결 완료를 판단하지 않는다.
3. 사용자 입력이나 최신 handoff에 있는 현재 플러그인 채널에 참가한다. 채널이 없거나 만료됐다면 현재 채널을 확인한다. 이전 세션의 채널 ID를 기본값으로 사용하지 않는다.
4. 선택한 디자인을 읽어 연결을 검증하고 승인된 작업을 진행한다. 연결 실패는 MCP 실행·WebSocket·채널 중 어느 단계인지 구분해 보고한다.

이미 실행 중인 세션에 새 기본값을 적용하려면 handoff 후 중앙 launcher로 새 세션을 시작한다. `--resume-assignment`는 원래 MCP 실행 설정을 유지한다.

완료·인계·검증은 `.agent-policy/common/AGENT_POLICY.md`와 `.agent-policy/common/skills/policy/task-role-routing/references/handoff-and-ownership.md`를 따른다.
