# 세션 프로젝트의 명령 실행 경계

## 요청과 의도

사용자는 브랜치·worktree 공유에 프로젝트 경계를 추가하도록 요청했다. user-ui 세션에서 admin-ui의 Git을 다루거나 그 반대로 작업하지 않게 한다. 동일 프로젝트의 브랜치·연결 worktree 공유와 Git 작업 단위 승인은 유지한다.

## 발견한 누락

기존 V4 guard는 Git 변경에 대해 다른 저장소인지 검사했지만 조회는 검사 전에 반환했다. 세션 저장소도 도구 이벤트의 cwd로 결정했으므로 이벤트 위치가 다른 프로젝트로 바뀌면 검사 기준이 함께 바뀔 수 있었다. 일반 shell 실행 위치와 cd·패키지 실행 경로, Git 출력·로컬 remote에 대한 공통 경계도 필요했다.

수정 전 4개 회귀 테스트에서 62개 실패를 확인했다. 실제 소비자 프로젝트의 Git 변경 없이 임시 저장소와 실제 렌더된 guard로 재현했다.

## 계약과 구현

- runtime 계약에 `execution.boundary=session-project`, `linked_worktrees=same-git-common-directory`, `outside_project=deny-before-approval`을 추가하고 중앙 audit가 검사한다.
- 기준 프로젝트는 renderer가 bundle에 넣은 `PROJECT_ROOT`다. 도구 cwd와 `ASAN_AGENT_POLICY_PROJECT_PATH`를 바꿔 기준 프로젝트를 재지정하지 않는다.
- shell의 실제 workdir, 리터럴 cd·env -C, 패키지 명령의 prefix/cwd, Git -C와 저장소 옵션을 승인 전에 검사한다. 경로 비교는 resolve와 Git common directory를 사용한다. 다른 저장소가 프로젝트 폴더 아래 있거나 심볼릭 링크로 연결되어도 같은 프로젝트로 취급하지 않는다.
- 같은 프로젝트의 cd 이동과 여러 Git 명령의 위치는 승인 내용 계산에도 반영한다. 기존 연결 worktree를 사용할 때 추가 소유권 계약은 필요 없다.
- 다른 로컬 저장소를 가리키는 명시 경로·remote와 Git 파일 출력을 차단한다. 새 연결 worktree의 외부 디렉터리는 허용하되 다른 저장소 아래에 만들지 않는다. 별도 저장소를 만드는 init/clone과 global/system Git 설정은 현재 세션 범위가 아니다.
- 실행 대상이 감춰지는 Git alias, 동적인 디렉터리 전환과 해석할 수 없는 shell 구문은 위치를 추정하지 않고 실제 명령·workdir를 요구한다.
- 공통 정책·Git 스킬·세 host의 inject preamble에 같은 경계를 명시한다. 다른 프로젝트 작업은 해당 프로젝트의 별도 세션에서 수행한다.

| user-ui 세션의 작업 | 결과 |
| --- | --- |
| user-ui 연결 worktree에서 status·lint·build | 허용 |
| user-ui 연결 worktree에서 commit·merge | 기존 작업 단위 승인 |
| 다른 저장소에 속하지 않은 경로에 user-ui worktree 추가 | 기존 작업 단위 승인 |
| admin-ui를 workdir·cd·git -C·패키지 실행 경로로 지정 | 조회·변경 모두 차단 |
| admin-ui를 로컬 push 대상·출력 파일·새 worktree 위치로 지정 | 승인 전에 차단 |
| 이벤트 cwd만 admin-ui로 바꿔 실행 | user-ui 기준을 유지하고 차단 |

중앙 정책·스킬 문서의 읽기와 시스템 실행 파일 사용은 프로젝트 이동으로 간주하지 않는다. HTTPS/SSH 원격 Git 사용은 기존 승인 계약을 따른다. 이 검사는 훅에 전달된 명령·명시 경로의 경계이며, 임의 프로그램 내부나 훅이 관찰하지 않는 후속 입력을 OS 수준에서 격리하는 기능은 아니다. 기존 host sandbox는 유지한다.

## 검증과 적용

회귀 테스트는 세 host와 두 프로젝트의 실제 native inject hook을 실행하며, 프로젝트 밖 차단과 연결 worktree 허용을 함께 검사한다. Git 승인 후 remote가 다른 로컬 프로젝트로 바뀐 경우도 승인 여부보다 프로젝트 경계를 먼저 확인한다.

최종 실행 결과와 원본 로그 해시는 `operations/2026-09-10-project-boundary-validation.json`에 기록한다. 중앙 원본·테스트·이 문서만 이번 작업 단위에 포함하며, 수집된 다른 세션의 로그와 소비자 Git 상태는 변경하지 않는다.

새 계약은 새 inject assignment에 적용된다. 기존 bundle을 수정하지 않으며 `--resume-assignment`는 원래 정책을 재개한다.
