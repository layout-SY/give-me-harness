---
name: policy-ui-library
description: 외부 UI 라이브러리 도입을 규정하고 기능 코드가 공용 UI 어댑터 뒤에 위치하도록 한다.
---

<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/common/skills/policy/ui-library/SKILL.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# UI 라이브러리

라이브러리를 선택하기 전에 설치된 의존성과 현재 프로젝트 관행을 조사한다. 외부 기본 요소는 반드시 `src/shared/ui/`에서 감싸야 하며, 기능 코드는 공급자 패키지 대신 어댑터에서 가져온다. 새로운 UI 의존성을 도입하기 전에 사용자에게 확인받는다.
