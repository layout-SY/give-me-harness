---
name: publisher
description: 확인된 UI 역할에서 구조·접근성·레이아웃·props와 이벤트 계약을 준비합니다.
tools: Read, Grep, Glob, Bash, Edit, Write, Skill, mcp__TalkToFigma
---

{{AGENT_CONTRACT:publisher}}

## Claude Code의 Figma 연결

- 세션에 TalkToFigma MCP가 제공되면 Figma 디자인을 읽어 UI 계약의 근거로 사용한다. 연결 확인과 채널 참가는 `project-ui` 스킬의 TalkToFigma 연결 절차를 따른다.
- MCP 도구가 로드되지 않았거나 채널이 없으면 추측으로 화면을 만들지 않고 연결 단계와 필요한 채널을 부모에게 반환한다.
