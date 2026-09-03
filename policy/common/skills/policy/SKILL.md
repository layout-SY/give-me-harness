---
name: policy-index
description: 코딩, 승인, 검증, 리뷰, 문서화 및 재사용에 관한 횡단 거버넌스 규칙을 안내한다.
---


# 정책 인덱스

- `task-role-routing`: 요청·handoff 기반 역할 제안, 사용자 확인, 역할별 소유권과 인계 계약.
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
- `implementation-quality`: 호스트 plugin에 의존하지 않는 기능, 리뷰, 타입, 단순화 및 프런트엔드 품질 기준.
- `codex-native-quality`: 이전 호출을 `implementation-quality`로 연결하는 호환 경로.
- `documentation`: 산출물 요구사항.
- `portfolio`: 모든 변경 작업 완료 후 작성하는 필수 이력서·포트폴리오 경험 기록.

모든 새 요청에서 `task-role-routing`으로 역할을 먼저 제안·확인하고 `git-branch-strategy`를 불러온다. 변경 작업에는 `coding-convention`을 함께 불러오고, 확인된 역할과 관련된 정책만 추가한다.
