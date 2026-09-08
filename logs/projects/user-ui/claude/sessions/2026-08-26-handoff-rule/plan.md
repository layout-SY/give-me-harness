# 계획

## 목표

중앙 정책 원본 `~/SynologyDrive/폐기된 외부 정책 저장소/source/common/AGENTS.md`에 작업자·호스트·세션 전환 시 적용할 일반 `handoff` 규칙을 정의한다.

## 범위

- 일반 작업 인계의 발동 조건, 기록 위치, 필수 내용, 작성자·수신자 책임을 규정한다.
- 인계 문서와 현재 파일·검증 근거의 우선순위를 규정한다.
- 일반 인계 문서와 8종 완료 산출물, Claude Code production UI 예외의 관계를 명시한다.
- 중앙 저장소 단위 테스트와 전체 대상 dry-run으로 생성 결과를 검증한다.
- 현재 작업의 필수 세션 산출물 8종을 작성한다.

## 제외 사항

- `python3 bin/sync.py deploy --target all`을 통한 대상 프로젝트 실제 배포
- 대상 프로젝트의 배포 산출물과 애플리케이션 코드 수정
- `handoff` 전용 런타임 상태 저장소, registry 또는 별도 자동화 추가

## 제약 조건

- 중앙 원본만 수정하고 대상 프로젝트에 배포된 정책 파일은 직접 수정하지 않는다.
- 현재 프로젝트에 이미 존재하는 변경은 되돌리거나 덮어쓰지 않는다.
- 관찰하지 않은 완료 상태나 실행하지 않은 검증을 인계 내용으로 추정하지 않는다.
- 모든 사용자 응답과 세션 산출물은 한국어로 작성한다.

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 정책 탐색 및 범위 확정 | Planner | `skill-index`, `policy-harness`, `policy-documentation` | 기존 Claude UI 인계 계약과 충돌하지 않는 일반 규칙 범위 확정 |
| 중앙 원본 수정 | Hephaestus | `policy-harness`, `policy-documentation` | `source/common/AGENTS.md`에 일반 작업 인계 규칙 추가 |
| 변경 검토 | Watcher | `policy-review-checklist` | 승인 범위·정합성·검증·문서화에 대한 PASS/FAIL 판정 |
| 장기 평가 및 경력 추합 | Evaluator | `policy-documentation`, `policy-portfolio` | 장기 개선 사항과 검증 가능한 포트폴리오 근거 기록 |

## 검증

- `python3 -m unittest discover -s tests`
- `python3 bin/sync.py deploy --target all --dry-run`
- 변경된 중앙 원본과 dry-run 출력에서 일반 규칙 및 기존 Claude Code 예외 정합성 확인

## 위험 요소 및 결정 사항

- 일반 `handoff.md`가 완료 산출물처럼 오해될 위험이 있어 8종 산출물을 대체하지 않는다고 명시한다.
- 기존 Claude Code production UI 예외는 유지하고 일반 규칙에서 명시적으로 참조한다.
- 인계 문서가 오래된 상태를 고정할 위험이 있어 수신자가 현재 파일과 검증 결과를 다시 확인하도록 규정한다.
- 요청한 `~/폐기된 외부 정책 저장소`는 존재하지 않아 프로젝트 지침이 지정한 `~/SynologyDrive/폐기된 외부 정책 저장소`를 실제 대상으로 확정했다.

## 승인

- 상태: approved
- 승인 문구: `진행해`
- 승인 시각: 2026-08-26

