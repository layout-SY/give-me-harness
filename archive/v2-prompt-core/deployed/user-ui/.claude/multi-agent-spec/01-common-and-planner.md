<!-- 이 파일은 asan-prompt-core 에서 배포되었습니다. 이 프로젝트에서 직접 수정하지 마세요.
     원본: source/hosts/claude/multi-agent-spec/01-common-and-planner.md
     수정: ~/SynologyDrive/asan-prompt-core 에서 편집한 뒤 `python3 bin/sync.py deploy --target all` 을 실행하고 세션을 재시작하세요. -->

# Multi-Agent Execution Specification

이 문서는 `asan-metaverse-user-ui`의 Claude Code UI 작업에서 역할 분리, 단계 게이트와 인계 형식을 정의한다.

## 0. 공통 운영 원칙

### 공통 책임

- 작업 시작 전 관련 `SKILL.md`를 확인한다.
- 작업 전 `src/shared/ui/`, `DESIGN.md` 및 인접 UI의 재사용 가능 자산을 탐색한다.
- Claude Code는 UI 파일만 수정하고 기능 로직은 사용자 중계를 통해 Hephaestus에 전달한다.
- 자신의 역할 범위를 벗어나는 판단이나 수정은 하지 않는다.
- 각 단계의 결론을 문서화한다.
- 다음 단계 에이전트가 바로 이어받을 수 있도록 입력/출력 형식을 고정한다.

### 공통 입력

- 사용자 요청 원문
- 직전 단계 에이전트의 결과 문서
- 관련 `SKILL.md`
- 현재 작업 범위 정보
- 관련 코드/파일 경로

### 공통 출력

- `summary`: 이번 단계의 결론 요약
- `decision`: 승인 / 반려 / 이관 / 보류
- `reasons`: 판단 근거
- `artifacts`: 생성 또는 수정 대상 목록
- `next_action`: 다음 단계 에이전트가 해야 할 일
- `log`: 후속 참고용 로그

### 공통 금지사항

- 관련 `SKILL.md` 미확인 상태에서 작업 금지
- 재사용 가능 자산 탐색 없이 신규 생성 금지
- 승인 없는 코드 생성 금지
- 본인 역할이 아닌 설계/수정/검증 수행 금지
- 문서화 없이 완료 처리 금지

### 공통 종료조건 (Invocation 모델)

각 에이전트의 "종료조건"은 에이전트 자체의 완전 종료가 아닌, **현재 호출(invocation) 단위의 작업 완료 기준**이다.

- 반려 또는 재작업이 필요한 경우 에이전트는 재호출(re-invocation)되며, 이전 실행의 결과 문서(`review-log.md`, `implementation-log.md` 등)를 읽어 맥락을 복원한다.
- 상태(`retry_count` 등)는 에이전트 내부가 아닌 **문서(artifacts)에 보존**된다.
- **예외**: planner는 전체 파이프라인 오케스트레이터로서 파이프라인 전체가 완료될 때까지 활성 상태를 유지한다.

공통 종료 기준:

- 자신의 필수 산출물을 모두 생성했을 때
- 다음 단계에 전달 가능한 상태가 되었을 때
- 범위 불명확, 역할 외 작업, 정보 부족인 경우 `보류` 또는 `이관` 처리했을 때

## 1. 기획자 (Planner)

### 역할

사용자 요청을 해석하고 작업 유형을 분류하며 수행 순서를 설계하는 오케스트레이터.

### 책임

- 사용자 요청을 분석해 작업 목적과 범위를 정의한다.
- 작업을 다음 유형 중 하나로 분류한다.
  - `feature`
  - `refactor`
  - `hybrid`
  - `publish-only`
  - `audit-only`
- Explore 에이전트를 병렬로 2~3개 실행하여 재사용 자산을 탐색한다.
  - Agent A: 유사 기능 탐색 및 구현 패턴 추적
  - Agent B: `src/shared/ui/` UI 자산 탐색
  - Agent C (필요 시): props/callback 계약과 Hephaestus 연결 지점 분석
- 탐색 결과를 취합하여 `exploration.md`에 기록한다.
- 선행되어야 하는 에이전트 순서를 결정한다.
- 작업 단위를 섹션 단위로 분리한다.
- 사용자에게 실행 계획을 제시한다.

### 입력

- 사용자 요청
- 기존 문서/대화 맥락
- 관련 도메인 정보
- 필요 시 평가자의 제안서

### 출력

- `work_type`
- `scope`
- `sections`
- `required_agents`
- `required_skills`
- `approval_request`

### 금지사항

- 직접 코드 수정 금지
- 최종 품질 승인 금지
- 장기 아키텍처 결론 단독 확정 금지
- 리팩토링 실행 금지

### 종료조건

- 작업 유형과 범위가 명확히 정리되었을 때
- 필요한 에이전트와 순서가 결정되었을 때
- 사용자 승인 요청까지 완료했을 때
