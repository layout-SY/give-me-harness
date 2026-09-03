---
name: policy-abstraction-strategy
description: 공용 추상화 또는 폐쇄형 어휘를 도입하기 전에 근거를 요구한다.
---

<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/common/skills/policy/abstraction-strategy/SKILL.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 추상화 전략

최소 두 사용처가 의미, 생명주기, 변경 압력 및 안정적인 계약을 공유할 때만 추상화한다. 마크업이 비슷하다는 사실만으로는 충분하지 않다. `src/shared/ui/`로 승격할 근거가 마련되기 전까지는 명확한 로컬 구현을 우선한다.
