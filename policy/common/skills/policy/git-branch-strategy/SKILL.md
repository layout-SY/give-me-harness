---
name: policy-git-branch-strategy
description: 저장소 변경 작업의 V3 task 계약, 격리 worktree, session assignment, merge 검증과 안전한 종료를 관리한다.
---

# Git 브랜치 전략

기준 브랜치는 `{{BASE_BRANCH}}`다. 읽기 전용 조사에는 branch를 만들지 않는다. 저장소 변경은 역할·구현 계획 승인과 별도로 V3 branch task 계약을 승인받은 뒤 시작한다.

## 핵심 구분

- **branch task 계약**: 목적, parent, 40자리 parent SHA, merge target, 역할, scope, Git 통합 담당자, 분기 근거와 worktree를 고정한다.
- **session assignment**: 현재 host·세션이 맡은 role, 산출물 디렉터리와 `owner|contributor` 책임을 정한다.
- 역할이나 산출물 책임은 host 이름에 내장하지 않는다. 같은 branch에서 다른 host·역할이 순차적으로 각자 assignment를 받을 수 있다.
- 한 세션에는 활성 task 하나만 둔다. `CLOSED` 뒤에는 같은 세션에서 다음 task로 바꿀 수 있다. 미완료 task를 `PRESERVED`로 남기고 다른 작업을 병행하면 별도 worktree·세션을 사용한다.

## 분기 판단

1. 현재 branch, HEAD, `git status --short --branch`, 관련 미병합 branch와 worktree를 읽는다.
2. 새 작업이 이전 미병합 commit에 의존하거나 수정 경로가 겹치면 그 task branch를 parent로 삼는다.
3. 독립 작업은 `{{BASE_BRANCH}}`를 parent로 삼는다.
4. task parent의 worktree에 commit되지 않은 변경이 있으면 child를 만들지 않는다. 그 변경은 child 기준 commit에 포함되지 않기 때문이다.
5. 기준 branch worktree가 dirty이거나 사용 중이면 기존 변경을 commit·stash·reset·restore하지 않고, 저장소 밖의 격리 `--worktree`를 계약에 넣는다.
6. branch 이름은 `task/<ascii-kebab-summary>`이고 parent와 직접 merge target은 같다.

## 생성 계약

inject 세션에서는 system prompt가 바인딩한 정책 snapshot 안의 스크립트 절대 경로를 사용한다. sync 세션은 배포된 다음 경로를 사용한다.

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

create는 파일 경로, canonical bytes, SHA-256, parent HEAD, branch 존재 여부와 worktree 상태를 재검증한다. 값 하나라도 달라지면 새 proposal과 승인이 필요하다. V3 metadata는 task id, purpose, parent/full SHA, merge target, roles, scopes, reason, integrator, contract SHA와 `ACTIVE` 상태를 기록한다.

## session 시작

격리 worktree는 그 경로를 cwd로 지정해 새 세션을 시작한다. 매번 폴더를 새로 만들 필요는 없고, 동시에 보존할 독립 작업이 있거나 기준 worktree가 dirty·사용 중일 때만 격리한다.

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

미완료 task를 다른 worktree·세션에 그대로 남길 때는 handoff를 작성한 뒤 다음 명령으로 상태를 고정한다. 같은 worktree에서 다른 task로 전환하지 않는다.

```sh
python3 <absolute-branch-workflow.py> preserve --reason "<보존·인계 이유>"
```

그 worktree에서 새 assignment로 돌아올 때 `resume`으로 `ACTIVE`를 복원한다.

```sh
python3 <absolute-branch-workflow.py> resume
```

## Git 통합 권한

같은 worktree에서 V3 계약의 Git 통합 담당자 한 명만 branch 전환, index, commit과 완료 workflow를 실행한다. 다른 host는 승인 scope의 파일과 자신의 산출물을 수정할 수 있어도 Git 상태를 바꾸지 않는다.

다음 명령은 승인으로 해제하지 않는 사용자 전용 작업이다.

- `git push`
- `git reset --hard`
- `git clean`
- `git update-ref`

에이전트는 명령을 실행하거나 재시도하지 않고 필요 이유, 정확한 대상과 영향을 사용자에게 양도한다. 파일 복원은 통합 담당자가 승인 scope의 구체 경로를 적은 `git restore ... -- <path>`만 사용한다. `git checkout -- <path>`는 사용하지 않는다. branch 전환과 merge를 `&&`나 `;`로 결합하지 않는다.

`git symbolic-ref`는 현재 branch 조회형만 허용한다. raw branch 생성·tracking·force·orphan 옵션과 local ref를 직접 갱신하는 fetch refspec은 workflow 우회로 차단한다. stage path는 `git add ... -- <path>`로 명시하고, `git commit -a|--only|<path>`처럼 unstaged 파일을 암시적으로 포함하지 않는다.

## 완료 workflow

구현·필수 8종·검증·commit이 끝난 source worktree에서 완료 proposal을 만든다.

완료 workflow는 `owner` session assignment만 수행한다. contributor의 `handoff.md`는 부분 결과 인계이며 branch merge·verify·close의 완료 근거가 아니다.

```sh
python3 <absolute-branch-workflow.py> finish-proposal \
  --source task/<summary> \
  --verify-command "npm run lint" \
  --verify-command "npm run build" \
  [--cleanup]
```

출력된 source/target 전체 HEAD, ff-only 방식, 검증 명령, cleanup 여부, finish proposal 파일과 64자리 SHA-256을 사용자에게 별도 prompt로 승인받는다. 공통 guard는 승인된 SHA-256과 실행 인자가 일치하는지 확인한다. 승인 후 target worktree에서 다음을 각각 별도 명령으로 실행한다.

`--verify-command`는 공통 runtime 계약에 렌더된 프로젝트 `lint`, `test`, `build` 명령의 정확한 argv만 허용한다. shell wrapper, Git, 임의 Python과 다른 실행 파일을 검증 명령으로 숨길 수 없다.

```sh
python3 <absolute-branch-workflow.py> finish --proposal-file <path> --proposal-sha256 <sha256>
python3 <absolute-branch-workflow.py> verify --proposal-file <path> --proposal-sha256 <sha256>
python3 <absolute-branch-workflow.py> close --proposal-file <path> --proposal-sha256 <sha256>
```

- `finish`: source/target HEAD가 승인 후 그대로이고 target이 clean일 때만 ff-only merge한다.
- `verify`: target에서 승인된 명령을 shell 없이 실행하고 모두 통과하면 `MERGED_VERIFIED`로 기록한다.
- `close`: ancestry와 clean 상태를 다시 확인한 뒤 `CLOSED` 기록을 남긴다. `--cleanup`이 승인된 계약만 격리 worktree와 local source branch를 안전 삭제한다.
- 실패하면 자동 rollback, rebase, 강제 삭제를 하지 않고 source와 worktree를 보존한다.

raw `git merge`, V3 branch 삭제와 worktree 제거는 사용하지 않는다. 자식 branch가 있으면 leaf부터 `child -> parent -> {{BASE_BRANCH}}` 순서로 각 단계의 finish 계약을 별도 승인받는다.

## compact·resume

compact, resume, handoff 직후에는 `context`를 실행하거나 주입된 `[BRANCH_CONTEXT]`를 확인한다.

```sh
python3 <absolute-branch-workflow.py> context
```

현재 task 상태, branch/HEAD, parent와 승인 SHA, merge target, roles, integrator, scope, worktree, dirty 경로, 미병합 자식과 다음 안전 조치를 확인한다. 실제 Git 상태와 문서가 다르면 작업을 멈추고 불일치를 보고한다.
