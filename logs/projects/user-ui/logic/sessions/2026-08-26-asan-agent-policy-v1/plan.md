# 계획

## 목표

user-ui의 Git HEAD에 추적된 AI 정책을 기준으로 독립 중앙 프로젝트 `/Users/okand/SynologyDrive/asan-agent-policy`를 구축하고, Codex·Claude Code·OpenCode용 산출물을 결정적으로 생성·감사한다.

## 범위

- user-ui Git HEAD와 현재 작업 트리의 정책 차이 감사
- 공통 정책과 호스트 어댑터 분리
- 프로젝트 메타데이터 기반 렌더링
- manifest와 SHA-256 기반 `audit`, `diff`, `sync`, `check`, `start`
- 중앙 관리 파일 수정 거부 및 세션 시작 drift 안내
- 중앙 프로젝트 단위 테스트와 두 프로젝트 dry-run

## 제외 사항

- `폐기된 외부 정책 저장소`, 백업 또는 `asan-harness`의 수정·삭제·재사용
- user-ui/admin-ui 대상 파일의 실제 배포
- 프로젝트별 overlay와 Agora 전용 정책
- 애플리케이션 소스와 UI 변경

## 제약 조건

- 현재 작업 트리에 있는 `폐기된 외부 정책 저장소` 배포 흔적은 기준에서 제외한다.
- 실제 타깃 배포는 dry-run 검토 뒤 별도 승인을 받는다.
- 기존 세션과 다른 세션의 변경을 되돌리지 않는다.

## 스킬 및 역할

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 기준 감사 | Planner | `skill-index`, `policy-harness`, `openai-docs` | 공식 호스트 계약과 기준 파일 확정 |
| 구조 설계 | Generator | `policy-abstraction-strategy` | 두 사용처에 필요한 최소 공통화 |
| 검증 | Watcher | `policy-review-checklist` | 명령·파일 근거가 있는 PASS/FAIL |
| 문서화 | Evaluator | `policy-documentation`, `policy-portfolio` | 필수 8종 산출물 완성 |

## 검증

- Python 표준 라이브러리 단위 테스트
- 중앙 소스 변경 및 소비자 drift 탐지 테스트
- managed 파일 차단과 애플리케이션 파일 허용 테스트
- user-ui/admin-ui dry-run 및 `폐기된 외부 정책 저장소` 문자열 부재 확인

## 위험 요소 및 결정 사항

- user-ui 현재 작업 트리의 AI 파일이 기존 중앙 프로젝트 산출물로 오염되어 있으므로 Git HEAD만 기준으로 사용한다.
- 배포 시 기존 manifest가 없는 파일을 임의 삭제하지 않는다.
- 호스트 선택과 모델 선택은 서로 다른 인자로 유지한다.

## 승인

- 상태: approved
- 근거: 사용자 메시지 `이대로 진행`
