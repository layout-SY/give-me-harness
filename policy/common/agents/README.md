# 하위 에이전트 역할 본문

호스트 native agent 정의에 들어가는 역할별 본문의 단일 원본이다. 렌더러가 `{{AGENT_CONTRACT:<역할>}}` 표식 위치에 이 본문과 `../CHILD_AGENT_CORE.template.md`의 공통 계약을 함께 삽입한다. 호스트 adapter에는 frontmatter·TOML 키·도구 목록 같은 형식과 그 호스트에만 있는 기능만 둔다.

본문은 TOML 여러 줄 문자열에 그대로 들어가므로 역슬래시와 연속된 큰따옴표 세 개를 쓰지 않는다. 정책·runtime 경로는 `.agent-policy/` 상대 경로로 적으면 inject 시 번들 절대 경로로 바인딩된다.
