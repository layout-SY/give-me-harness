---
name: recipe-i18n
description: 대상 프로젝트의 현지화 경계를 통해 사용자 노출 문자열을 추가하거나 교체합니다.
---

<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/common/skills/recipe/i18n/SKILL.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# i18n 레시피

먼저 현지화 인프라가 있는지 확인합니다. 인프라가 있으면 지원하는 모든 로케일을 함께 수정하고 현재 키 명명 규칙을 따릅니다. 인프라가 없으면 그 공백을 문서화하고 의존성 또는 아키텍처를 도입하기 전에 승인을 받습니다.
