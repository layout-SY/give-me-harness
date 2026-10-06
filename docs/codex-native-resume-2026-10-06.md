# Codex 내장 /resume의 프로젝트 이력 복구

## 원인과 변경 이유

2026-09-09 커밋 `e60ade9979255848b3ef4df027d476c66a80d157`은 프로젝트 공용 `state/user-ui/codex-home`을 assignment별 home으로 바꿨다. 목적은 동시에 실행한 Logic·Review 등의 writable home에서 hooks·agents 설정이 덮어써지는 것을 막고 승인·작업 소유권을 분리하는 것이었다. `tests/test_remediation.py`의 `test_same_project_sessions_have_independent_codex_homes`가 그 요구를 검증한다.

대화까지 같은 경계로 분리해 새 실행의 `/resume`에서 이전 실행을 찾을 수 없게 됐다. 당시 `docs/admin-inject-runtime-fix-2026-09-09.md`에도 이 문제가 기록됐지만 중앙 `sessions`와 `--resume-assignment`로 대응했다. 내장 picker를 복구하지 않았으며, guard도 한 launcher assignment가 다른 native ID로 전환되는 것을 거부했다.

## 수정

- `lib/agent_policy/codex_history.py`: 같은 Git 저장소의 대화·이름 index·writer lock을 공용 저장소에 연결한다. 기존 공용 home, 같은 프로젝트 assignment home, 사용자 home에서 귀속을 확인한 대화만 가져오며 원본·가져오기 해시·기존 수정 시각을 보존한다. 중복 ID의 서로 다른 내용은 덮어쓰지 않는다.
- `injection.py`: 새 V4 Codex 실행에서 설정 home은 격리하고 SQLite 위치만 프로젝트 이력 저장소로 지정한다. 이전 불변 bundle은 수정하지 않는다.
- `history_paths.py`, `session_diagnostics.py`: launcher가 만든 정확한 프로젝트 이력 연결만 허용하며 기존 일반 home 진단도 유지한다.
- `runtime_state.py`: 내장 `/resume`으로 대화를 전환하면 현재 launcher 정책·role 아래의 별도 assignment 상태에 연결한다. 승인·산출물·쓰기 예약은 복제하지 않으며 같은 실행에서 돌아온 대화는 자신의 상태를 유지한다.
- 포맷 실행은 native `CODEX_THREAD_ID`, Stop 로그 수집은 실제 hook의 `session_id`를 사용한다.

이력은 현재 launcher 정책으로 이어간다. 과거 정책·assignment 자체의 재개는 기존 중앙 `resume`을 사용한다. picker의 cwd·보관 필터는 Codex 기본 기능을 유지한다. 기존 home에서 실행 중인 세션은 handoff 후 종료하고 새 launcher로 시작한다.

## 검증 및 실제 데이터

수정 전 새 home의 이력 누락·legacy 이력 누락·native 전환 거부를 자동 테스트로 재현했다. 관련 회귀 검증은 프로젝트 분리, 훅 격리, 원본·이름·시간 보존, 반복 가져오기, 잘못된 링크와 중복 ID 차단, 상태 전환 및 포맷·로그 수집 귀속을 포함한다.

`tests/smoke_codex_resume.py --tui`는 임시 프로젝트·로컬 fixture로 설치된 Codex의 `thread/list`, `thread/resume`과 실제 터미널 `/resume` 목록·선택을 확인한다. 모델 요청은 보내지 않는다. hook 정책 판정은 별도의 실제 guard subprocess 회귀 테스트로 검증한다.

실제 user-ui에서 새 실행 미리보기를 생성해 기존 대화 11개를 연결했다. Codex의 프로젝트 필터 조회에서도 11개를 확인했으며 `01a1073b-2a0d-7ac2-8afe-9701dc12c745`(10월 4일)가 포함됐다. 대화와 이름 index 등 가져온 원본 36개의 해시가 유지됨을 확인했다. 대화 원본이 없는 과거 assignment는 복원한 것으로 취급하지 않는다. 실제 사용자 대화에 새 턴을 보내거나 과거 assignment를 덮어쓰지 않았다.

전체 unittest discover 대상 415개를 파일명 기준 네 그룹으로 나누어 실행했고 모두 통과했다(88 + 139 + 107 + 81). `bin/agent-policy audit`는 central-contract, admin-ui(296 bundle files), user-ui(226 bundle files) 모두 PASS다. 설치된 Codex 0.160.1의 실제 터미널 `/resume` 검증과 `git diff --check`도 통과했다. 가져온 원본 36개의 해시를 최종 재확인했으며 변경된 원본은 없다.
