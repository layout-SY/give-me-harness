---
name: policy-type-definition
description: 속성, 콜백, 훅 및 DTO에 대한 TypeScript 계약 경계와 데이터 형태 규약을 정의한다.
---

<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/common/skills/policy/type-definition/SKILL.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 타입 정의

속성, 콜백 경계, 훅 반환 계약 및 어댑터 API처럼 두 주체 사이의 계약에는 `interface`를 사용한다. 유니온, 파생 타입, DTO 데이터 형태 및 로컬 상태에는 `type`을 사용한다. 계약을 명시적으로 유지하고 `any`를 피한다.
