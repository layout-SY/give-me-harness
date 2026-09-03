---
name: policy-refactoring
description: 동작을 보존하는 구조 재편, 중복 제거, 추출 및 현대화를 규정한다.
---

<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/common/skills/policy/refactoring/SKILL.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 리팩터링

기존 동작을 고정하고 범위를 제한하며, 현재 정리와 후속 개선 기회를 분리한다. 계약이 실제로 일치할 때만 재사용한다. 각 논리적 구간을 마친 뒤 Watcher 검증을 실행한다.
