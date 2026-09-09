---
name: policy-git-branch-strategy
description: 저장소 변경 작업의 V3 task 계약, 격리 worktree, session assignment, merge 검증과 안전한 종료를 관리한다.
---

# Git 브랜치 전략

기준 브랜치는 `{{BASE_BRANCH}}`다. 읽기 전용 조사에는 branch를 만들지 않는다. 저장소 변경은 역할·구현 계획 승인과 유효한 V3 branch task 계약을 확인한 뒤 시작한다. 새 branch 생성 계약은 구현 승인과 별도로 승인받는다.

## 핵심 구분

- **branch task 계약**: 목적, parent, 40자리 parent SHA, merge target, 역할, scope, Git 통합 담당자, 분기 근거와 worktree를 고정한다.
- **session assignment**: 현재 host·세션이 맡은 role, 산출물 디렉터리와 `owner|contributor` 책임을 정한다.
- 역할이나 산출물 책임은 host 이름에 내장하지 않는다. 같은 branch에서 다른 host·역할이 순차적으로 각자 assignment를 받을 수 있다.
- 한 세션에는 assignment 권한 root 하나와 현재 작업 branch 초점 하나만 둔다. root 또는 그 ACTIVE V3 자손에서 승인 생성한 child는 `asan-parent` 계보를 따라 같은 권한에 전이적으로 포함된다.
- V1, V2 또는 버전이 없는 branch metadata는 이력 조회에만 사용하며 변경 권한으로 인정하지 않는다. 계속 작업할 branch는 canonical V3 proposal과 승인을 새로 받아야 한다.
- parent-root assignment는 root와 승인된 자손 사이에서 초점을 바꿀 수 있다. child-root assignment에는 ancestor·형제 권한이 없고, 이름 유사성은 권한 근거가 아니다. 계보 밖 독립 task는 기존 root가 `CLOSED`된 뒤 같은 세션에서 시작하거나, `PRESERVED` 후 별도 worktree·세션에서 병행한다.

## 분기 판단

1. 현재 branch, HEAD, `git status --short --branch`, 관련 미병합 branch와 worktree를 읽는다.
2. 새 작업이 이전 미병합 commit에 의존하거나 수정 경로가 겹치면 그 task branch를 parent로 삼는다.
3. 독립 작업은 `{{BASE_BRANCH}}`를 parent로 삼는다.
4. child는 ACTIVE task parent에서만 만들고, parent worktree에 commit되지 않은 변경이 있으면 생성하지 않는다. 그 변경은 child 기준 commit에 포함되지 않기 때문이다.
5. 기준 branch worktree가 dirty이거나 사용 중이면 기존 변경을 commit·stash·reset·restore하지 않고, 저장소 밖의 격리 `--worktree`를 계약에 넣는다.
6. branch 이름은 `task/<ascii-kebab-summary>`이고 parent와 직접 merge target은 같다.

## 생성 계약

system prompt가 바인딩한 중앙 inject snapshot 안의 스크립트 절대 경로를 사용한다. 소비자 저장소의 같은 이름 파일로 fallback하지 않는다.

```text
.agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py
```

먼저 proposal을 출력한다. `--role`은 launcher의 `logic|ui|orchest|review|generate`를 사용하며 여러 역할이면 반복한다.

```sh
python3 <absolute-branch-workflow.py> proposal \
  --branch task/<summary> \
  --purpose "<작업 목적>" \
  --parent <parent> \
  --role <role> \
  --git-integrator <codex|claude|opencode|user> \
  --scope <path> \
  --reason "<분기 판단 근거>" \
  [--worktree <repository-outside-path>]
```

proposal은 모든 필드를 정렬·정규화한 canonical JSON을 Git 공용 상태의 `asan-agent-policy/proposals/`에 기록한다. SHA-256에는 purpose, roles, scopes, reason과 worktree까지 포함된다. 승인 요청에는 파일 경로와 64자리 전체 SHA-256이 함께 표시된다. 공통 guard가 정확한 계약을 연결할 수 있도록 proposal 출력 후 사용자 승인을 별도 prompt로 받는다.

사용자의 독립된 승인 뒤에는 값을 다시 조립하지 않고 승인된 파일을 그대로 소비한다.

```sh
python3 <absolute-branch-workflow.py> create \
  --proposal-file <printed-absolute-json-path> \
  --proposal-sha256 <printed-64-character-sha256>
```

create는 파일 경로, canonical bytes, SHA-256, parent HEAD, parent의 `ACTIVE` 상태, branch 존재 여부와 worktree 상태를 재검증한다. 값 하나라도 달라지면 새 proposal과 승인이 필요하다. V3 metadata는 task id, purpose, parent/full SHA, merge target, roles, scopes, reason, integrator, contract SHA와 `ACTIVE` 상태를 기록한다.

## scope 변경 계약

작업 중 승인 범위가 부족하다고 확인되면 raw `git config`로 metadata를 고치거나 새 branch를 만들지 않는다. 현재 V3 task worktree에서 변경 후 전체 scope를 proposal로 출력한다.

```sh
python3 <absolute-branch-workflow.py> scope-proposal \
  --scope <기존에 유지할 경로> \
  --scope <새로 승인받을 경로>
```

`--scope`는 추가분만이 아니라 변경 후 전체 목록이다. 출력된 canonical proposal 파일과 64자리 SHA-256을 사용자에게 별도 승인받은 뒤 적용한다.

```sh
python3 <absolute-branch-workflow.py> update-scope \
  --proposal-file <printed-absolute-json-path> \
  --proposal-sha256 <printed-64-character-sha256>
```

`update-scope`는 현재 ACTIVE V3 계약에서 scopes 외 필드가 바뀌지 않았는지 확인한다. 새 scope가 현재 dirty 경로를 모두 포함하지 못하면 기존 metadata로 되돌리고 실패한다. 따라서 사용자의 일반적인 “범위 추가 승인” 문장을 raw metadata 변경 권한으로 해석하지 않는다.

## session과 worktree 선택

격리 worktree를 만들었다는 이유만으로 현재 세션을 종료하지 않는다. 생성된 branch가 현재 assignment 권한 root 또는 승인된 V3 자손이면, 해당 worktree를 이후 도구의 `workdir` 또는 `git -C` 대상으로 삼아 그대로 작업을 계속할 수 있다. 세션의 산출물 디렉터리와 책임은 유지하고 현재 branch 초점만 갱신한다. 새 세션은 권한 계보 밖의 미완료 task를 `PRESERVED`로 보존한 채 다른 독립 task를 병행하거나, host·role·담당자를 인계할 때 필요하다. 매번 폴더를 새로 만들 필요는 없고, 동시에 보존할 독립 작업이 있거나 기준 worktree가 dirty·사용 중일 때만 격리한다.

세션을 격리 worktree에서 새로 시작해야 하는 경우에는 다음 launcher 계약을 사용한다.

```sh
bin/agent-policy start \
  --project <project> \
  --host <codex|claude|opencode> \
  --mode inject \
  --role <role> \
  --task task/<summary> \
  --responsibility <owner|contributor> \
  --worktree <absolute-worktree> \
  --branch task/<summary> \
  --session-dir .<host>/logs/sessions/<task-session>
```

- `owner`: 공통 8종 산출물 책임.
- `contributor`: `handoff.md` 책임.
- 다른 host·다른 세션 산출물은 읽을 수 있지만 쓸 수 없다.
- 정의되지 않은 보조 문서는 자기 세션의 `unknown/`에 둔다.

미완료 task를 다른 worktree·세션에 그대로 남길 때는 handoff를 작성한 뒤 다음 명령으로 상태를 고정한다. 같은 worktree에서 권한 계보 밖의 독립 task로 전환하지 않는다.

```sh
python3 <absolute-branch-workflow.py> preserve --reason "<보존·인계 이유>"
```

그 worktree에서 새 assignment로 돌아올 때 `resume`으로 `ACTIVE`를 복원한다.

```sh
python3 <absolute-branch-workflow.py> resume
```

## Git 통합 권한

V3 계약의 승인 worktree에서 Git 통합 담당자 한 명만 branch 전환, index, commit과 완료 workflow를 실행한다. guard는 세션 시작 cwd가 아니라 각 Git 명령의 실제 대상(`workdir`, `git -C`, `--git-dir/--work-tree`)을 다시 해석한다. 다른 host는 승인 scope의 파일과 자신의 산출물을 수정할 수 있어도 Git 상태를 바꾸지 않는다.

다음 명령은 승인으로 해제하지 않는 사용자 전용 작업이다.

- `git push`
- `git reset --hard`
- `git clean`
- `git update-ref`

에이전트는 명령을 실행하거나 재시도하지 않고 필요 이유, 정확한 대상과 영향을 사용자에게 양도한다. 파일 복원은 통합 담당자가 승인 scope의 구체 경로를 적은 `git restore ... -- <path>`만 사용한다. `git checkout -- <path>`는 사용하지 않는다. branch 전환과 다른 Git 변경을 `&&`나 `;`로 결합하지 않는다. `cd`, `env -C`, `GIT_DIR` 또는 `GIT_WORK_TREE`로 대상 저장소를 숨기지 않는다.

`git symbolic-ref`는 현재 branch 조회형만 허용한다. raw branch 생성·tracking·force·orphan 옵션과 local ref를 직접 갱신하는 fetch refspec은 workflow 우회로 차단한다. stage path는 `git add ... -- <path>`로 명시하고, `git commit -a|--only|<path>`처럼 unstaged 파일을 암시적으로 포함하지 않는다. `git commit -m <message>`와 반복된 `-m`의 값은 URL이나 `/`를 포함해도 pathspec으로 해석하지 않는다.

## 완료 workflow

구현·필수 8종·검증·commit이 끝난 source worktree에서 완료 proposal을 만든다.

완료 workflow는 `owner` session assignment만 수행한다. contributor의 `handoff.md`는 부분 결과 인계이며 branch merge·verify·close의 완료 근거가 아니다.

```sh
python3 <absolute-branch-workflow.py> finish-proposal \
  --source task/<summary> \
  --merge-strategy ff-only \
  --verify-command "npm run lint" \
  --verify-command "npm run build" \
  [--cleanup]
```

출력된 source/target 전체 HEAD, ff-only 또는 merge-commit 방식, 통합 worktree, 검증 명령, cleanup 여부, finish proposal 파일과 64자리 SHA-256을 사용자에게 별도 prompt로 승인받는다. 공통 guard는 승인된 SHA-256과 실행 인자가 일치하는지 확인한다. 승인 후 다음을 각각 별도 명령으로 실행한다. workflow는 계약의 통합 worktree를 사용하며, 단일 worktree에서는 source와 target이 clean이고 target이 다른 곳에 checkout되지 않았을 때만 승인된 target 전환을 수행한다.

`--verify-command`는 공통 runtime 계약에 렌더된 프로젝트 `lint`, `test`, `build` 명령의 정확한 argv만 허용한다. shell wrapper, Git, 임의 Python과 다른 실행 파일을 검증 명령으로 숨길 수 없다.

```sh
python3 <absolute-branch-workflow.py> finish --proposal-file <path> --proposal-sha256 <sha256>
python3 <absolute-branch-workflow.py> verify --proposal-file <path> --proposal-sha256 <sha256>
python3 <absolute-branch-workflow.py> close --proposal-file <path> --proposal-sha256 <sha256>
```

- `finish`: source/target HEAD가 승인 후 그대로이고 target이 clean일 때만 승인된 방식으로 merge한다. 병렬 sibling이 분기되었으면 최신 target 기준의 merge-commit 계약을 별도로 승인받는다. 실행 후 실제 integration HEAD를 기록한다.
- `verify`: 기록된 integration HEAD와 승인 source 포함 관계를 확인한 target에서 승인된 명령을 shell 없이 실행하고 모두 통과하면 `MERGED_VERIFIED`로 기록한다.
- `close`: ancestry와 clean 상태를 다시 확인한 뒤 `CLOSED` 기록을 남긴다. `--cleanup`이 승인된 계약만 격리 worktree와 local source branch를 안전 삭제한다.
- 실패하면 자동 rollback, rebase, 강제 삭제를 하지 않고 source와 worktree를 보존한다.

raw `git merge`, V3 branch 삭제와 worktree 제거는 사용하지 않는다. 자식 branch가 있으면 leaf부터 `child -> parent -> {{BASE_BRANCH}}` 순서로 각 단계의 finish 계약을 별도 승인받는다.

## compact·resume

compact, resume, handoff 직후에는 `context`를 실행하거나 주입된 `[BRANCH_CONTEXT]`를 확인한다. 첫 변경 전에는 `[SESSION_READINESS]`도 확인한다. 같은 상태를 다시 조회하려면 현재 bundle의 공통 guard를 읽기 전용으로 실행한다.

```sh
python3 -I <absolute-managed-policy-guard.py> branch-context <codex|claude|opencode>
```

guard를 직접 실행할 때도 launcher가 설정한 assignment·role 환경을 유지한다. 조회는 스킬·탐색 완료나 구현 승인을 만들지 않는다.

기본 폴더에 checkout된 기존 V3 task에서 새 세션으로 이어갈 수 있다. 계약에 worktree 경로가 고정되어 있으면 현재 위치와 일치해야 한다. 유효한 기존 계약의 생성 승인은 반복하지 않고 인계 계획, 현재 assignment의 구현 승인·탐색 근거와 Git 소유권을 확인한다. 새 assignment의 미충족 조건은 변경 명령을 실행하기 전에 보고하며, 기존 세션의 승인 상태를 복사하지 않는다. 이미 유효한 승인·탐색 근거는 반복 요청하지 않는다.

```sh
python3 <absolute-branch-workflow.py> context
```

현재 task 상태, branch/HEAD, parent와 승인 SHA, merge target, roles, integrator, scope, worktree, dirty 경로, 미병합 자식과 다음 안전 조치를 확인한다. 실제 Git 상태와 문서가 다르면 작업을 멈추고 불일치를 보고한다.


`PRESERVED` task는 launcher에 --task/--worktree를 명시해 진단·재개 세션을 열 수 있다. 귀속된 진단·handoff 쓰기는 가능하지만 source 변경은 명시적 resume 후에만 허용된다. READY_TO_MERGE와 MERGED_VERIFIED도 완료 복구 진입만 허용하며 일반 source 권한으로 취급하지 않는다.

일반 질문과 compact는 구현·계약 승인을 철회하지 않는다. 새 독립 task나 승인 scope 변경에는 관련 승인을 새로 받아야 한다. 같은 assignment 재개는 launcher --resume-assignment <id>를 사용한다. 정책 업데이트를 적용하는 새 세션과 구별한다.


### 실행 중단 복구

동일 완료 계약의 finish를 다시 실행하면, 승인 source와 병합 방식에 맞는 결과 HEAD·부모 관계를 재조회하여 누락된 실행 기록을 복구한다. verify와 close도 동일 결과 HEAD에서는 재시도할 수 있다. cleanup 실패를 CLOSED로 기록하지 않으며 worktree 제거 전에 모든 host의 세션 로그를 수집한다.

충돌·ff-only 실패는 중앙 `bin/agent-policy integration-recover --project {{PROJECT_ID}} --finish-file <원본 파일> --finish-sha256 <전체 SHA>`로 현재 HEAD·dirty 파일 해시·통합 예약을 검토한다. 출력된 복구 SHA를 사용자에게 승인받고 같은 명령에 `--approved-sha256 <복구 SHA>`를 붙여야 merge --abort와 ACTIVE 복원을 수행한다. 검토 후 변경이 생기면 다시 검토한다. source 변경이나 새로운 결과 HEAD를 이 계약으로 승인하지 않는다.

결과 hook이 누락된 귀속 예약은 중앙 `assignment-recover --project {{PROJECT_ID}} --assignment <ID> --call-id <도구 ID> --outcome confirmed|cancelled`로 현재 상태를 검토하고 복구 SHA를 승인받아 처리한다. 이 복구는 탐색 완료나 구현 승인을 만들지 않는다. 중단된 `assignment-handoff`는 이미 승인한 동일 계약을 재실행하며, 인계가 끝날 때까지 양쪽 assignment의 작업을 차단한다.
