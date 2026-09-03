---
name: policy-validation
description: 폼의 필수값 확인, 검증기, 제출 흐름 및 요청 데이터 매핑을 규정한다.
---

<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/common/skills/policy/validation/SKILL.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 검증

검증을 순수하게 유지하고 렌더링과 분리한다. 제출 전에 필수 필드를 검증하고, 허용된 모든 필드를 의도적으로 요청 데이터에 매핑하며, 비동기 제출의 부수 효과는 전용 훅 또는 서비스 경계에 둔다.
