# 계획

## 목표

- `asan-metaverse-user-ui`의 AI 작업 정책을 감사·정정해 새 중앙 정책 프로젝트의 기준 원본으로 승격한다.
- `asan-metaverse-user-ui`와 `asan-metaverse-admin-ui`가 동일한 공통 정책을 Codex, Claude Code, OpenCode에서 사용하도록 동기화한다.
- 소비 프로젝트 세션에서는 중앙 관리 정책을 수정하지 못하게 하고 중앙 프로젝트 이동 및 세션 재시작을 안내한다.

## 범위

- 새 형제 프로젝트 `/Users/okand/SynologyDrive/asan-agent-policy` 생성
- 공통 정책, 호스트 어댑터, 최소 프로젝트 manifest, 동기화·검사·시작 도구 구현
- user-ui와 admin-ui의 중앙 관리 파일 동기화
- 관리 파일 drift 및 직접 수정 차단 검증

## 제외 사항

- 프로젝트별 임의 policy overlay
- SQLite, evidence 저장소, 세션 registry, release channel, migration state machine
- 실행 중인 세션의 hot reload
- 애플리케이션 기능·UI 변경

## 제약 조건

- user-ui의 기존 정책을 무조건 복제하지 않고 실제 코드·명령어·호스트 규격과 불일치하는 항목을 교정한다.
- 프로젝트별 컴포넌트·훅 카탈로그, 로그, 상태, 로컬 권한은 중앙화하지 않는다.
- 기존 `asan-harness`는 전체 재사용하지 않고 manifest, 안전한 동기화, 어댑터 검증 개념만 참고한다.
- 관리 파일 적용 전 dry-run diff를 확인하고 관련 없는 변경을 보존한다.

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 정책 감사 | Planner | `skill-index`, `policy-harness`, `policy-abstraction-strategy` | 공통·프로젝트 전용·오류 항목 분류 |
| 중앙 프로젝트 구현 | Generator | `policy-harness`, `policy-documentation` | 이해 가능한 최소 중앙 정책 프로젝트 |
| 검증 | Watcher | `policy-review-checklist` | 동기화·drift·guard PASS/FAIL |
| 장기 평가 | Evaluator | `policy-portfolio` | 후속 overlay와 기술 부채 기록 |

## 검증

- 중앙 프로젝트 자체 테스트
- 두 프로젝트 대상 `check` 및 dry-run 동기화
- 관리 파일 수정 차단 hook 단위 테스트
- Codex/Claude/OpenCode 진입 파일 구조 검증
- user-ui와 admin-ui의 기존 `npm run lint`, `npm run build`는 설정 영향이 있을 때 실행

## 위험 요소 및 결정 사항

- Claude Code는 현재 user-ui 계약대로 UI 전담 역할을 유지한다.
- OpenCode와 OMO는 별도 호스트로 분리하지 않고 OpenCode 어댑터에 포함한다.
- 중앙 원본 변경은 `sync` 또는 중앙 `start`를 거쳐야 소비 프로젝트에 반영된다.

## 승인

- 상태: approved
- 승인 근거: 사용자의 `계획대로 진행해봐`

