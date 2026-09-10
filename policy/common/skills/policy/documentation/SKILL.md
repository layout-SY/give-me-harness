---
name: policy-documentation
description: 작업 범위의 거버넌스 산출물과 결론 우선 근거 요구사항을 정의한다.
---

# 문서화

실행 호스트의 산출물 경로를 사용한다. Codex는 `.codex/logs/sessions/`, Claude Code는 `.claude/logs/sessions/`, OpenCode는 `.opencode/logs/sessions/` 아래에 작업 디렉터리를 만들고 해당 host adapter의 템플릿을 사용한다. 기록은 결론부터 작성하고, 경로와 명령어를 인용하며, 관찰한 사실과 권고 사항을 구분한다. 이전 세션의 산출물을 현재 근거로 재사용해서는 안 된다.

`owner`는 `plan.md`와 `final-summary.md`에 범위·결정·변경·검증·미완료 항목을 기록한다. `contributor` 또는 중단·인계 시에는 `handoff.md`를 작성한다. 탐색·구현·리뷰·평가·grill-me·portfolio 문서는 작업 규모와 사용자 요청에 맞춰 선택한다. 문서가 부족하다는 이유로 Git 변경이나 다음 작업을 차단하지 않는다.

`portfolio-log.md`를 작성할 때는 검증 후 실제 근거와 `policy-portfolio`의 사례 구조를 사용한다.

정의된 산출물 이름에 속하지 않는 보조 기록은 현재 세션의 `unknown/` 하위에 둔다. 다른 host·다른 세션의 산출물은 인계 근거로 읽을 수 있지만 현재 세션에서 수정하지 않는다. host를 판별할 수 없을 때는 Codex 경로로 대체하지 않고 `.agent-policy/logs/unknown/sessions/`에 기록한다.

## Todo 언어

- Todo의 제목과 설명은 한국어로 작성한다.
- 파일 경로, 코드 심볼, 명령어, 고유 기술명은 정확성을 위해 원문 표기를 유지할 수 있다.
- Todo에는 작업 위치, 수행 방법, 목적, 기대 결과를 한국어로 명확히 포함한다.
