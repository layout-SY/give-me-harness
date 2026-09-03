---
name: policy-data-fetch-layer
description: 데이터 요청 작업에서 전송, 도메인 작업, 상태 조율 및 UI의 책임을 분리한다.
---

<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/common/skills/policy/data-fetch-layer/SKILL.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 데이터 요청 계층

1. 전송 모듈은 HTTP 세부 사항과 DTO 경계를 책임진다.
2. 도메인 작업은 요청 의도와 결과 매핑을 책임진다.
3. 훅은 로딩, 취소 및 화면 상태를 책임진다.
4. 컴포넌트는 렌더링과 사용자 이벤트를 책임진다.

가공하지 않은 요청과 UI 부수 효과를 동일한 컴포넌트 콜백에 두지 않는다.
