# Git 접근 공유와 작업 단위 승인

## 요청과 결정

사용자는 세션별 branch/worktree 생성·접근 권한과 Git 통합 소유권을 제거하고, Git 조회는 자유롭게 하되 생성·수정·삭제에는 사용자 승인을 요구하도록 요청했다. 다른 host의 읽기 전용 범위는 설정·세션 기록으로 정했다. 소스와 Git 작업은 프로젝트 내 모든 branch/worktree에서 공유한다. 제안 후 “오케이. 이대로 작업 진행해”로 구현을 승인받았다.

기존 문제는 Git 작업보다 앞서 V3 계약, assignment 계보, worktree claim, scope, 구현 탐색, 필수 문서, 완료 예약이 함께 검사되는 구조였다. CLOSED 누락이나 다른 host의 부모 worktree claim이 있으면 사용자 병합 승인만으로 작업을 진행할 수 없었다.

## 구현

- 공통 runtime 계약을 V4로 변경했다. 새 guard 경로는 branch metadata, Git claim, 완료 예약을 권한으로 읽거나 쓰지 않는다.
- `shared_git.py`가 실제 프로젝트/worktree, Git 조회·변경과 host/session 기록 경계만 검사한다. 기존 Git 대상 해석, 이벤트 정규화, 사용자 승인, 산출물 기록 코드를 재사용한다.
- 모든 role·responsibility는 사용자 승인 후 Git을 변경할 수 있다. source 구현의 역할·계획 승인·성공한 스킬/탐색 근거는 유지하며 Git 승인과 분리한다.
- 생성·전환·stage·commit·merge·fetch·push·config·복원·삭제를 일반 Git 명령으로 실행한다. V3 proposal/SHA/finish/verify/close는 새 bundle에서 사용하지 않는다.
- Claude는 native ask, Codex·OpenCode는 공통 guard에 대기 중인 작업에 `진행` 또는 `명령 실행 승인`으로 답하는 방식을 사용한다. stage+commit처럼 관련 명령을 한 번에 승인할 수 있다. 승인 SHA 입력은 제거했다.
- 승인은 실제 명령·위치·관련 ref·대상 내용에 연결한다. 승인 후 대상이나 index 변경은 재확인한다. 관련 없는 다른 host의 unstaged 로그 변경은 소스 commit의 재승인 사유가 아니다.
- 다른 host의 설정·로그, 같은 host의 다른 세션 산출물은 직접 수정하거나 stage/commit하지 못한다. 다른 host의 이미 커밋된 기록은 승인된 병합으로 그대로 전달할 수 있다.
- Git 조회와 일반 lint·test·build에는 별도 명령 승인을 요구하지 않는다. OpenCode의 중복 Git/build ask 설정을 제거하고 공통 guard에서 실제 argv를 분류한다. 개발 서버 승인은 유지한다.
- `owner` 기본 산출물은 `plan.md`와 `final-summary.md`, 부분 기여자·인계는 `handoff.md`다. 기존 6개 상세 템플릿은 선택 문서로 보존했다. 문서 누락이나 완료 상태로 Git·다음 작업·대화 종료를 차단하지 않는다.
- `--task`는 branch와 분리된 한 줄 설명이다. 세션 디렉터리는 안전한 ASCII slug와 assignment ID로 생성한다. `--worktree`와 `--branch`는 시작 위치 확인값이며 실행 중 접근 경계를 고정하지 않는다.

## 유지한 보호 규칙

중앙 정책은 소비자에서 직접 수정하지 않는다. 프로젝트 외 저장소의 변경, 다른 host/session의 직접 기록 변경, `.git` 내부 파일 직접 편집은 보호한다. 파일 수정은 실제 대상이 드러나는 구조화된 도구를 사용한다. 다른 작업의 미커밋 변경을 임의로 덮어쓰거나 commit하지 않는다.

같은 worktree의 Git 변경은 순차 실행하고 native Git lock을 임의로 지우지 않는다. 이 운영 규칙을 세션 독점 claim으로 구현하지 않는다. 병렬 구현에는 별도 worktree를 권장한다. host sandbox의 쓰기 권한과 중앙 정책 허용은 별개다.

검증 실패는 통과로 기록하지 않는다. 기존 오류가 남은 상태의 병합 여부는 실제 결과를 보고 사용자가 결정한다. 작업 완료와 branch/worktree 삭제는 분리한다.

## 이전 계약과 적용

기존 V1/V2/V3 metadata·claim·완료 기록과 기존 inject bundle은 변경하지 않았다. 이전 V3 실행을 복구하는 중앙 코드와 테스트는 유지한다. `tests/legacy_runtime.py`는 이 기존 실행/복구 테스트에만 V3 계약을 명시적으로 주입한다. production 환경 변수로 이전 정책을 선택하거나 새 guard를 우회하는 기능을 추가하지 않았다. 새 기본 동작은 별도 V4 테스트에서 검증한다.

실행 중이던 세션은 작업과 Git 상태를 handoff하고 새 inject assignment로 시작한다. 새 세션에는 Git 소유권 이전이나 CLOSED 처리가 필요하지 않다. `--resume-assignment`는 원래 bundle 재개이므로 새 정책 적용 방법이 아니다. 기존 세션과 새 세션이 같은 worktree에서 동시에 Git 변경을 하지 않도록 인계한다.

```sh
bin/agent-policy start --project admin-ui --host codex --role logic
```

user-ui, Claude, OpenCode도 project·host·role을 선택해 같은 방법으로 시작한다. 기존 격리 worktree에서 시작하려면 `--worktree <절대 경로>`를 붙인다. 새 세션을 시작하기 위해 branch를 다시 생성할 필요는 없다.

## 검증 기록

- 수정 전 재현: `test_shared_git_access.py` 5개 테스트에서 22개 실패. 계약 없는 기존 branch, 다른 세션 claim, raw merge/생성, 구현 gate, build 승인으로 새 요구사항을 충족하지 못했다.
- 추가 재현: 다른 host의 로그 변경으로 소스 commit 승인이 무효화되는 사례를 1개 실패로 확인한 후, 작업 대상에 한정해 승인 상태를 비교하도록 수정했다. 다른 worktree에 결과 로그를 쓰면 계획 승인이 풀리는 사례도 1개 실패로 재현한 뒤 원래 계획 위치를 유지하도록 수정했다.
- V4 검사 17개 통과: 세 host·기본 checkout·독립 worktree, 과거 claim/CLOSED, 생성·삭제·기존 사용자 전용 명령 승인, 역할과 Git 분리, 관련 명령 묶음 승인, 승인 재사용/상태 변경, 다른 host·세션 보호, 실제 자식 병합과 커밋된 로그 전달, 실제 native inject hook 경로 실행.
- launcher/inject 검사 26개 통과: 기존 branch 시작 허용, role/session 경계 유지, 한글 task 설명과 안전한 세션 경로, 호스트별 주입·MCP·bundle 검증.
- 최종 전체 unittest: **248개 모두 통과**, 1224.214초. 첫 전체 실행에서 발견한 선택 문서 수집 누락을 수정했고, 폐기한 V3 권한 문구를 기대하던 렌더 검사를 새 계약으로 바꾼 뒤 전체를 다시 실행했다.
- 중앙 audit와 diff 형식 검사 통과.

원본 실행 로그: `/private/tmp/asan-shared-git-before.log`, `/private/tmp/asan-shared-git-unrelated-before.log`, `/private/tmp/asan-shared-git-plan-before.log`, `/private/tmp/asan-shared-git-final-regressions.log`, `/private/tmp/asan-shared-git-injection-final.log`, `/private/tmp/asan-shared-git-full-suite.log`, `/private/tmp/asan-shared-git-full-final.log`, `/private/tmp/asan-shared-git-audit-final.log`.

[검증 결과와 원본 해시](operations/2026-09-10-shared-git-validation.json)를 함께 보관한다. 최종 전체 검사 동안 정책 원본과 테스트의 해시가 변경되지 않았음을 확인했다.

이번 작업은 중앙 원본·테스트·문서 변경이다. 소비자 branch, Git metadata, claim, 기존 세션의 산출물은 수정하지 않았다. 중앙으로 수집된 다른 세션 로그는 이 작업 커밋에 포함하지 않는다.
