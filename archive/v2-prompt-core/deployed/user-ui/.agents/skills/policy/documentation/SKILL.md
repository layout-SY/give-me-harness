---
name: policy-documentation
description: 작업 범위의 거버넌스 산출물과 결론 우선 근거 요구사항을 정의한다.
---

<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/common/skills/policy/documentation/SKILL.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 문서화

`.codex/logs/sessions/{YYYY-MM-DD-task-slug}/` 아래에서 `.codex/templates/`를 사용한다. 기록은 결론부터 작성하고, 경로와 명령어를 인용하며, 관찰한 사실과 권고 사항을 구분한다. 이전 세션의 산출물을 현재 근거로 재사용해서는 안 된다.

변경 작업의 필수 산출물은 `plan.md`, `exploration.md`, `implementation-log.md`, `grill-me-review.md`, `review-log.md`, `evaluation-log.md`, `final-summary.md`, `portfolio-log.md`다. `portfolio-log.md`는 검증 후 마지막에 작성하며 `policy-portfolio`의 사례 구조를 따른다. 현재 사용자 대화, 실행 결과, 현재 코드에서 직접 확인한 근거만 사용한다.

## Todo 언어

- Todo의 제목과 설명은 한국어로 작성한다.
- 파일 경로, 코드 심볼, 명령어, 고유 기술명은 정확성을 위해 원문 표기를 유지할 수 있다.
- Todo에는 작업 위치, 수행 방법, 목적, 기대 결과를 한국어로 명확히 포함한다.
