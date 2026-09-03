---
name: policy-index
description: 코딩, 승인, 검증, 리뷰, 문서화 및 재사용에 관한 횡단 거버넌스 규칙을 안내한다.
---

<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/common/skills/policy/SKILL.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# 정책 인덱스

- `git-branch-strategy`: 모든 변경 작업의 분기·승인·병합·정리 및 compact 컨텍스트 규칙.
- `coding-convention`: React/TypeScript 구현 규약.
- `type-definition`: 계약 및 데이터 타입 규칙.
- `publishing`: UI 구조, 접근성 및 이벤트 계약.
- `styles`: 공용 스타일링 및 자산 재사용.
- `ui-library`: 외부 UI 어댑터 경계.
- `validation`: 폼 검증 및 요청 데이터 매핑.
- `data-fetch-layer`: 요청 계층의 책임 경계.
- `hook-extraction`: 상태를 가진 로직의 추출 여부 결정.
- `abstraction-strategy`: 추상화 전에 필요한 근거.
- `refactoring`: 동작을 보존하는 정리.
- `harness`: 승인 및 역할 게이트.
- `review-checklist`: Watcher의 pass/fail 판정 기준.
- `codex-native-quality`: 플러그인에 의존하지 않는 기능, 리뷰, 타입, 단순화 및 프런트엔드 품질 기준.
- `documentation`: 산출물 요구사항.
- `portfolio`: 모든 변경 작업 완료 후 작성하는 필수 이력서·포트폴리오 경험 기록.

모든 요청에서 `git-branch-strategy`를 먼저 불러온다. 변경 작업에는 `coding-convention`을 함께 불러오고, 작업과 관련된 정책만 추가한다.
