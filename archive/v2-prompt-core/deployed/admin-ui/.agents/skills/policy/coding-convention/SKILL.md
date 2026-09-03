---
name: policy-coding-convention
description: 모든 애플리케이션 코드 변경에 필수인 React 및 TypeScript 코딩 규약이다.
---

<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/common/skills/policy/coding-convention/SKILL.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 코딩 규약

- 엄격한 타입을 사용하고 `any`를 도입하지 않는다.
- 함수형 컴포넌트, 조기 반환 및 단일 책임 모듈을 우선한다.
- 상태를 가진 재사용 가능 동작은 사용자 정의 훅에 두고, 렌더링 보조 함수에는 부수 효과를 두지 않는다.
- UI 기본 요소를 만들기 전에 `src/shared/ui/`를 검색한다.
- 대상에서 확인한 기존 가져오기 별칭과 폴더 경계를 따른다.
- 추측에 근거한 추상화와 관련 없는 정리를 피한다.
