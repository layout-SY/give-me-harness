# 오케스트레이션 세션의 하위 에이전트 본문

`orchest` 세션에서 host가 읽는 하위 에이전트 정의의 역할별 본문이다. inject가 host adapter의 형식(이름·설명·도구 목록)에 이 본문과 `../CHILD_AGENT_CORE.template.md`의 공통 계약, 세션 바인딩을 합쳐 3개 host에 같은 내용으로 설치한다. host에만 있는 기능은 `adapters/<host>/`에 둔다(예: `adapters/claude/pipeline-agents.json`).

`logic`·`ui`·`review`·`generate` 세션은 이 본문을 쓰지 않고 `adapters/<host>/files/`의 기존 정의를 그대로 설치한다.

본문은 TOML 여러 줄 문자열에 그대로 들어가므로 역슬래시와 연속된 큰따옴표 세 개를 쓰지 않는다. 정책·runtime 경로는 `.agent-policy/` 상대 경로로 적으면 inject 시 번들 절대 경로로 바인딩된다.
