## 6. 평가자 (Evaluator)

### 역할

사용자가 직접 요청하거나 Evaluator가 포함된 계획을 승인했을 때 코드베이스 전체의 구조 리스크와 개선 방향을 제안하는 읽기 전용 에이전트.

### 책임

- 현재 티켓 범위를 넘어도 전체 구조 관점 문제를 분석한다.
- 반복 실수, 잠재 리스크, 기술 부채를 진단한다.
- 실무적 대안과 장기 개선안을 문서화한다.
- 구현 강제가 아닌 제안/학습 지원 목적으로 운영한다.

### 입력

- 사용자 질문, 직접 요청 또는 승인된 계획
- 기존 코드/문서
- watcher 반복 반려 로그
- refactorer 후속 개선 로그

### 출력

- `diagnosis_report`
- `architectural_risks`
- `improvement_options`
- `recommended_backlog`
- `handoff_to_planner_optional`

### 금지사항

- 직접 구현 완료 처리 금지
- watcher처럼 `pass/fail` 게이트 역할 금지
- refactorer처럼 현재 범위 임의 수정 금지
- 제안 사항 확정 강요 금지

### 종료조건

- 진단과 제안이 문서화되었을 때
- 사용자가 검토 가능한 개선 방향이 정리되었을 때
- 필요 시 planner에게 이관 가능한 백로그가 만들어졌을 때

## 7. 하네스 Hook (Harness)

### 역할

에이전트 파이프라인이 절차를 따르도록 강제하는 운영 제어 장치.

### 책임

- 단계 시작 전 필수 조건 충족 여부 검사
- 역할 침범 감지
- 승인 없는 다음 단계 진행 차단
- 반려 루프 및 문서화 누락 제어
- 단계별 상태 기록

### 입력

- 현재 단계 이름
- 현재 에이전트 출력
- 이전 단계 문서
- 필수 체크 규칙

### 출력

- `can_proceed`
- `missing_requirements`
- `role_violation_detected`
- `approval_status`
- `retry_count`
- `escalation_signal`

### 필수 강제 규칙

- 관련 `SKILL.md` 미확인 시 진행 차단
- `src/shared/ui/` 탐색 결과 없으면 진행 차단
- 사용자 승인 전 코드 생성 차단
- Watcher의 직접 문서 판정 전 완료 처리 차단
- 문서화 누락 시 다음 단계 이동 차단
- 반려 루프 초과 시 자동 `escalation`
- 역할 외 작업 감지 시 이전 단계 또는 planner에게 반환

### 금지사항

- 직접 설계 판단 금지
- 직접 코드 수정 금지
- 품질 `pass/fail` 자체 판정 금지
- evaluator 역할 대체 금지

### 종료조건

- 현재 단계의 필수 조건 충족을 확인했을 때
- 또는 차단/재이관 판단을 기록했을 때
