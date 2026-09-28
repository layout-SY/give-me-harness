---
name: policy-git-branch-strategy
description: 세션과 독립된 브랜치 관계, 직접 부모 통합 순서와 사용자 Git 승인·안전한 로컬 정리를 관리한다.
---

# Git 운영

기준 branch는 `{{BASE_BRANCH}}`다. 모든 host·role·session은 같은 프로젝트의 모든 branch와 linked worktree에서 사용자 요청을 이어갈 수 있다. 브랜치 소유자, 허용 파일 목록, Git integrator, 독점 claim, CLOSED 접근 조건은 없다. 역할은 구현 책임이며 Git 실행 권한이 아니다.

다른 프로젝트의 명령 실행은 승인 전에 차단한다. 같은 Git common directory를 공유하는 linked worktree만 같은 프로젝트다. 다른 host의 설정·세션 로그와 다른 세션 산출물은 읽기 전용이다. 기존에 commit된 로그는 승인된 branch 전환·병합으로 그대로 전달할 수 있다. 다른 작업의 변경을 임의로 stage·commit·stash·복원하지 않는다.

## 조회·승인·실행

조회형 status/diff/log/branch/config/worktree list와 일반 lint·test·build에는 Git 승인이 필요 없다. 파일 출력 옵션이나 해석할 수 없는 Git 명령은 조회로 간주하지 않는다. `.git` 직접 편집, 다른 저장소·Git alias·모호한 실행 경로로 우회하지 않는다.

Git 변경은 **현재 bundle의 `runtime/git_operations.py`**를 `python3 -I`로 호출한다. 일반 Git 변경을 도구에 요청하면 guard가 동일 명령의 보호 실행 명령을 제시한다. 제시된 `execute <id>`를 같은 workdir에서 호출한다. 실행 직전에 대상과 변경을 다시 확인하고 Git 명령이 실행되는 동안만 lock을 유지한다. native Git lock 제거·force 삭제는 하지 않는다.

사용자에게 실제 repository·workdir·명령·source/target HEAD·선택한 변경·영향을 보고한다. Claude는 `execute`의 native 권한 요청, Codex·OpenCode는 대기 중인 작업에 대한 **`명령 실행 승인`**을 사용한다. `Proceed`·`진행` 같은 구현 승인 문구로 별개의 Git 작업을 승인하지 않는다. 승인된 같은 작업 묶음은 다시 질문하지 않는다. 관련 HEAD·index·검토 변경·새 자식이 바뀌면 재검토한다. 무관한 세션 로그 갱신은 재승인 사유가 아니다.

명령 승인 요청·응답 기록과 승인 후 실행 예약에는 시간에 따른 유효 기간을 두지 않는다. 답변이나 실행이 늦어졌다는 이유로 같은 승인을 다시 요구하지 않는다. 승인은 보고한 동일 작업의 1회 실행 범위이며, 실제 실행 전 명령·위치·대상·변경 내용과 현재 실행 주체를 확인한다.

`git add -- <경로> && git commit -m <메시지>`는 하나의 작업으로 준비할 수 있다. 보호 실행기는 셸을 평가하지 않고 확인한 Git argv와 cwd를 순서대로 실행한다. `cd`, `git -C`, `env -C`의 실제 경로를 검사하며 동적 wrapper·파이프·해석하지 못한 변경 명령은 명시적인 형태로 풀어 쓴다.

## 관계와 작업 공간

관계 기록은 Git common directory를 기준으로 중앙 runtime state의 `branch-relations/v1/graph.json`에 둔다. UUID, 현재 이름, 직접 부모 UUID, fork commit, 목적, 관계 변경 이력을 기록한다. assignment와 소유 파일 목록을 추가하지 않는다. 완료·검증·정리는 `operations/`, 검토 근거는 `reviews/`, 필요한 파일은 `archives/`에 보존한다. 병합 commit과 fork는 `refs/asan-policy/integrations/`로 보존한다.

관계 명령은 먼저 작업을 준비하고 같은 `execute` 승인 경로를 사용한다.

- `relation --action register --name <branch> --parent <parent> --fork <전체 commit> --purpose <목적>`: 사용자와 확인한 기존 관계 등록. sy-main 등록은 parent를 생략한다. 이름·upstream·오래된 V3 assignment로 부모를 추측하지 않는다.
- `relation --action create ... --worktree <새 linked 경로>`: 승인한 부모의 현재 commit에서 별도 작업 공간 생성. 기능은 sy-main에서, 독립 하위 작업은 기능 branch에서 분기한다. 새 요청마다 생성하지 않는다.
- `relation --action rename --name <기존> --new-name <새 이름>`: UUID를 유지한 이름 변경.
- `relation --action reparent --name <자식> --parent <새 부모> --fork <commit>`: 승인한 부모 변경. 순환은 차단한다.
- `relation --action cancel --name <branch>`: commit·미커밋 변경을 보존하고 의존성에서 제외한다. branch/worktree와 접근 권한은 유지한다. 이후 변경이 추가되면 다시 미처리 작업이 된다.
- `relation --action retire --name <branch>`: 완료·취소된 branch의 외부 삭제를 확인하고 이름을 퇴역 처리한다. 이후 같은 이름은 새 UUID로 등록한다.
- `graph`: UUID와 직접 부모를 조회한다. 필요하면 이 데이터로 관계도를 보여준다.

부모를 모르는 기존 branch도 세션 시작·조회·일반 수정·commit은 가능하다. 완료에 필요한 관계만 확인해 등록한다. 외부에서 이름·ref를 바꾸거나 reflog를 정리해 식별이 불명확해지면 완료·정리 시 명시적으로 재확인한다. 다른 계열 접근을 차단하는 근거로 쓰지 않는다.

병렬 구현은 별도 linked worktree를 사용한다. branch만 다르고 worktree가 같으면 파일과 index는 격리되지 않는다. 세션은 workdir로 이동할 수 있다. sy-main의 직접 자식 아래를 한 기능 계열로 보며, 다른 계열로 이동하면 적절한 작업 위치와 별도 세션 선택지를 한 번 안내한다. 새 세션이나 소유권 인계는 의무가 아니다.

## 완료 검토와 통합

완료는 자식에서 **직접 부모**로 수행한다. 미처리 자식이 있으면 부모 완료를 차단한다. HEAD가 같거나 부모에 포함됐다는 사실만으로 작업을 완료 처리하지 않는다. 명시적인 완료 요청, 최종 commit, 미커밋 작업, 하위 작업을 함께 확인한다. 형제 계열의 진행 중인 작업은 그 자체로 차단하지 않는다.

1. `review --source <자식> --target <직접 부모> --strategy ff-only|merge --verify-command "{{LINT_COMMAND}}" --verify-command "{{BUILD_COMMAND}}" [--cleanup]`으로 근거를 수집한다.
2. 같은 직접 부모의 형제, 삭제된 형제 이력, 형제의 하위 작업, 분기 이후 부모 변경, staged·unstaged·untracked 근거를 읽는다. diff 함수 문맥과 문자열 참조 후보를 활용해 함수·타입·props·호출부·상태·API 계약의 영향을 **에이전트가** 검토한다. 자동 수집은 의미적 호환성 판정이 아니다.
3. 자기 세션의 JSON 보고에 `evidence_digest`, `comparisons`, `text_conflicts`, `contract_risks`, `validation`, `unknowns`, `recommendation`을 작성한다. 비교 commit·dirty 상태, 실제 검증·미확인 범위, 권장 병합 순서를 구체적으로 쓴다. 위험 자체는 자동 차단하지 않는다. 미확인을 “충돌 없음”으로 쓰지 않는다.
4. `complete --review <id> --report <보고 경로>`로 준비한다. 형제 검토와 `execute <id>` 승인을 하나의 보고로 묶는다. `--cleanup`은 검증 후 해당 source 로컬 branch·linked worktree 정리까지 승인에 포함한다. 원격 삭제는 포함하지 않는다.
5. 실행기는 승인한 source·target·관계·검토를 다시 확인하고 병합 → 결과 확인 → 승인한 검증 → 로그 보존 → 안전한 정리를 수행한다.

ff-only가 불가능한 분기는 Git 텍스트 충돌과 다르다. 형제를 먼저 병합하면 다른 파일만 바꿔도 이후 ff-only가 실패할 수 있다. 실패 후 임의로 전략을 바꾸지 않고 merge 전략의 새 검토·승인을 받는다. squash·rebase·cherry-pick·직접 ref 갱신은 초기 자동 완료 경로가 아니다. 이 경로를 완료 관계 우회에 사용하지 않는다. 일반 merge·fetch/pull/refspec 경로도 같은 검사를 적용한다.

부모를 자식으로 가져오는 직접 부모 동기화는 일반 Git 작업으로 승인하며 완료·삭제를 기록하지 않는다. 실제 미해결 Git 충돌은 통합 성공으로 기록하지 않는다.

## 실패·정리·복구

기본 worktree와 현재 실행 위치·세션 시작 위치는 자동 삭제하지 않는다. 정리 전 승인한 source의 통합, 검증 성공, 새 commit·미보존 변경·미처리 자식·실행 중 변경 도구의 부재, 로그 보존, 정확한 linked 경로를 확인한다. 로그가 dirty라면 임의로 commit·복원하거나 force 삭제하지 않고 정리만 보류한다.

`.env.local` 등 ignored 로컬 파일도 확인하며 미보존 파일이 있으면 정리를 보류한다. 재설치·빌드로 생성하는 프로젝트 루트의 `node_modules/`와 `dist/`만 완료 승인 보고의 재생성 가능한 산출물 정리 범위에 명시한다. 이 범위를 다른 파일이나 디렉터리로 자동 확대하지 않는다.

검증·로그 보존·정리 실패 시 병합은 되돌리지 않는다. `show <id>`로 사실과 이유를 보고하고 안전한 같은 프로젝트 workdir에서 `recover <id>`로 **같은 승인 작업**의 결과를 대조·검증·정리한다. Git 병합은 반복하지 않으며 다른 source commit이나 worktree를 선택하지 않는다. 일반 Git/관계 명령의 중단은 기록·실제 refs/index를 비교한 뒤 다음 조치를 새로 준비한다.

CLOSED를 요구하지 않는다. 통합·검증 실패 기록은 다음 형제 검토에 포함하며, 정리 보류가 다른 작업 시작이나 세션 이동을 막지 않는다. 결과 미확인 도구 쓰기는 해당 위치의 완료·정리만 보류한다.

미확인 쓰기·중단된 검증은 호스트 실행 기록과 실제 프로세스를 확인한다. 실행이 종료됐음을 확인한 뒤 `write-recovery --id <도구 기록 ID> --reason <종료 확인 근거>`를 준비하고 같은 Git 승인 경로로 기록을 해소한다. 시간 경과만으로 종료로 간주하거나 native Git lock을 제거하지 않는다. 이 복구는 파일을 복원·삭제하지 않는다.

## 기존 bundle과 적용

V3 소유권·완료 workflow를 재활성화하지 않는다. 기존 bundle을 resume하면 원래 정책이 유지된다. 현재 bundle과 중앙 정책의 차이를 확인한 뒤 기존 작업을 handoff하고 새 inject assignment로 적용한다. 소비자 설정·정책 사본을 직접 수정하지 않는다. 중앙 로그를 자동 삭제하거나 stage·commit하지 않는다.

외부 터미널·원격 작업은 하네스의 실행 lock에 참여하지 않는다. 전후 refs·dirty·충돌 검사로 변경을 발견할 수 있지만 외부 동시 실행까지 통제한다고 주장하지 않는다.
