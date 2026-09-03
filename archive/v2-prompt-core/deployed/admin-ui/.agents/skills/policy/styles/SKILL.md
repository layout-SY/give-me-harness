---
name: policy-styles
description: 프런트엔드 시각 요소를 추가하거나 변경할 때 스타일, 아이콘 및 자산을 규정한다.
---

<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/common/skills/policy/styles/SKILL.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 스타일

로컬 변형을 추가하기 전에 `src/shared/ui/` 스타일과 프로젝트 토큰을 재사용한다. 이모지를 인터페이스 아이콘으로 사용하지 않는다. 반응형 상태 및 포커스 상태를 명시적으로 유지하고, 기존 프로젝트 자산이 동일한 목적을 충족한다면 원본 자산을 추가하지 않는다.
