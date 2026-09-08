# 브랜치·worktree·세션 운영 전략 V3

## 문서 상태

- 기준일: 2026-09-03
- 대상: `user-ui`, `admin-ui`와 중앙 `asan-agent-policy`
- 상태: 중앙 원본 구현. 중앙 launcher로 시작한 새 inject 세션부터 유효
- 역할 원칙: host와 role은 독립이다. 특정 host를 UI·Logic·오케스트레이션 전담으로 고정하지 않는다.

## 1. 기존 상황

기존 V2는 task branch에 목적, parent, merge target, scope, 역할, Git 통합 담당자와 산출물 모드를 Git config로 기록했다. 기준 branch 직접 수정과 scope 이탈을 막는 장점은 있었지만 branch, session과 host 책임을 한 계약에 섞었다.

그 결과 다음 장애가 확인됐다.

1. dirty 기준 worktree에서 독립 작업 branch를 만들 수 없어 다른 세션의 변경을 임의 commit·stash하라는 압력이 생겼다.
2. inject의 `branch_workflow.py`가 snapshot runtime보다 소비자의 stale host hook을 읽어 `FULL_SHA_PATTERN` 누락으로 죽을 수 있었다.
3. proposal ID가 purpose, scope, reason을 포함하지 않아 승인 뒤 이 값이 바뀌어도 같은 식별자가 나왔다.
4. proposal의 축약 SHA와 create의 전체 SHA가 달라 “승인 요청 식별자 불일치”가 발생했다.
5. `git checkout -- <path>`를 branch 전환으로 오판했고, 전환과 merge를 결합한 명령은 전환 전 branch 기준으로 판정됐다.
6. `git -C . reset --hard`와 `git push`를 parser가 subcommand로 인식하지 못해 허용할 수 있었다.
7. shell stderr redirect를 파일 생성으로 오판하고, 반대로 shell로 만든 산출물은 구조화된 경로 정보가 없어 session 귀속을 기록하지 못했다.
8. branch 단위 `artifact-mode=full|handoff`는 같은 branch에서 contributor가 handoff한 뒤 owner가 8종을 마무리하는 흐름을 표현하지 못했다.
9. 모든 host의 artifact 경로를 scope 예외로 허용해 한 host 세션이 다른 host·다른 세션 문서를 수정할 수 있었다.
10. Stop이 현재 dirty 파일만 보아 이미 commit된 애플리케이션 변경은 산출물 없이 통과할 수 있었다.
11. 외부 worktree에서 launcher·log collector가 기본 프로젝트 폴더로 조용히 fallback해 잘못된 정책 또는 산출물을 볼 수 있었다.
12. Codex legacy Python hook과 공통 guard가 동시에 실행됐다. Codex는 여러 matching hook을 모두 실행하고 하나의 deny가 전체를 막으므로, 우선순위로 중복을 덮을 수 없었다.

## 2. 변경 방향

V3는 정적 **branch task 계약**, 동적 **session assignment**, 검증 가능한 **완료 계약**을 분리한다.

```text
사용자 요청
  -> role·계획 승인
  -> immutable branch proposal 승인
  -> task branch/worktree
  -> host별 session assignment
  -> 구현·handoff 또는 8종·commit
  -> immutable finish proposal 승인
  -> finish -> verify -> close
```

공통 의미는 `.agent-policy/common/**`에서만 정의한다. host adapter는 native 실행 형식과 도구 차이만 가진다. 공통 runtime registry는 `.agent-policy/common/contracts/runtime-policy.json`이며 role 이름, host artifact root, 8종 목록, unknown 경로와 task 상태를 renderer·launcher·guard가 공유한다.

## 3. 용어와 예시

| 용어 | 의미 | 예시 |
| --- | --- | --- |
| host | 세션을 실행하는 프로그램 | Codex, Claude Code, OpenCode |
| role | 이번 세션이 맡은 책임 | `logic`, `ui`, `orchest`, `review`, `generate` |
| 기준 branch | 독립 task의 시작·최종 통합점 | `sy-main` |
| task branch | 승인된 한 작업의 branch | `task/fix-spinner` |
| parent | task가 직접 분기된 branch | `sy-main` 또는 선행 task |
| merge target | 완료 후 직접 통합할 branch | 항상 parent와 동일 |
| HEAD/SHA | commit과 그 40자리 식별자 | 승인 계약에서는 축약 SHA 금지 |
| worktree | 같은 Git object를 별도 폴더와 index로 펼친 공간 | 기존 dirty 폴더와 새 clean 작업 폴더 |
| scope | task에서 수정 승인된 경로 | `src/shared/ui`, `DESIGN.md` |
| Git 통합 담당자 | branch·index·commit·완료 workflow 단일 소유자 | host 하나 또는 `user` |
| owner assignment | 작업 전체와 공통 8종을 책임지는 세션 | 통합 구현 또는 최종 마무리 |
| contributor assignment | 일부 역할과 `handoff.md`를 책임지는 세션 | UI 계약, Logic 일부, review |
| assignment 권한 root | 세션이 시작한 task이자 하향 권한의 기준 | `task/meeting-reserve-ui` |
| 현재 branch 초점 | 세션이 지금 수정하는 root 또는 승인된 V3 자손 | `task/reserve-option-lazy-load` |
| CLOSED | merge·target 검증·종료 기록이 끝난 task | 같은 세션에서 다음 task 가능 |
| PRESERVED | handoff 후 미완료 상태로 보존한 task | 다른 task는 별도 worktree·세션 |

## 4. 왜 worktree를 쓰는가

`git switch -c`는 현재 폴더의 tracked/untracked 변경과 같은 index 상태를 그대로 새 branch에 데려간다. 반면 `git worktree add`는 Git object와 branch 목록만 공유하고 working directory와 index를 분리한다.

```text
기본 폴더
  sy-main + 작업 A의 dirty 파일 + index A

격리 폴더
  task/work-b + clean working directory + 독립 index B
```

따라서 기본 폴더가 dirty이거나 다른 세션이 사용 중인 독립 작업은 격리한다. 모든 작업마다 worktree가 필요한 것은 아니다. 기존 task가 CLOSED이고 현재 폴더가 clean하며 단일 세션이 소유하면 같은 폴더에서 다음 task를 시작할 수 있다.

격리 worktree도 현재 세션 assignment가 소유한 root 또는 승인된 V3 자손의 실행 공간이 될 수 있다. 세션을 시작한 cwd가 소유권 경계가 되는 것이 아니라, 현재 초점 branch 계약에 기록된 worktree가 변경 경계가 된다. 따라서 기본 폴더에서 `git -C <승인된-descendant-worktree> add -- <scope-path>`를 실행하는 것은 허용할 수 있지만, task worktree에서 `git -C <기본-sy-main-worktree> add ...`로 기준 branch index를 바꾸는 것은 차단해야 한다.

task parent에 commit되지 않은 변경이 있는 경우는 다르다. child branch는 parent ref의 마지막 commit에서 시작하므로 그 dirty 변경을 포함하지 않는다. V3 도구는 이 경우 child 생성을 막고 parent 소유자의 commit 또는 handoff를 요구한다. child는 ACTIVE task parent에서만 생성한다.

## 5. immutable branch proposal

V2는 승인 내용을 긴 CLI 인자로 다시 입력했다. 오타, 축약 SHA와 일부 필드 누락이 식별자 불일치 또는 승인 범위 변조를 만들었다.

V3 proposal은 다음 전부를 canonical JSON으로 정렬·직렬화한다.

- version과 task id
- branch와 목적
- parent, 40자리 parent HEAD와 merge target
- role 목록
- scope 목록
- Git 통합 담당자
- 분기 판단 reason
- 선택적 절대 worktree 경로

SHA-256은 이 JSON 전체를 계산한다. proposal 파일은 Git common directory의 `asan-agent-policy/proposals/<sha256>.json`에 저장한다. create는 긴 인자를 다시 받지 않고 승인된 파일 경로와 64자리 SHA-256만 받는다.

```sh
python3 <branch_workflow.py> proposal \
  --branch task/fix-spinner \
  --purpose "Spinner 크기와 정렬 오류 수정" \
  --parent sy-main \
  --role ui \
  --git-integrator claude \
  --scope src/shared/ui/loading \
  --scope src/shared/assets/css/_default.css \
  --reason "기존 API 작업과 경로가 겹치지 않는 독립 UI 수정" \
  --worktree /worktrees/admin-ui-spinner
```

승인 후:

```sh
python3 <branch_workflow.py> create \
  --proposal-file <출력된 절대 경로> \
  --proposal-sha256 <출력된 64자리 SHA-256>
```

purpose·role·scope·reason·worktree 중 하나라도 바뀌면 JSON과 SHA가 달라져 새 승인이 필요하다.

## 6. session assignment와 산출물

branch는 작업 전체 경계이고 assignment는 현재 host·세션의 책임이다.

```sh
bin/agent-policy start \
  --project admin-ui \
  --host claude \
  --mode inject \
  --role ui \
  --task task/fix-spinner \
  --responsibility contributor \
  --worktree /worktrees/admin-ui-spinner \
  --branch task/fix-spinner \
  --session-dir .claude/logs/sessions/2026-09-03-fix-spinner-ui
```

동일 branch의 후속 세션이 전체 마무리를 맡으면 host나 role과 무관하게 `--responsibility owner`를 사용한다. branch에 `artifact-mode`를 고정하지 않는다.

owner가 작성하는 OpenCode 기준 8종은 다음과 같다.

1. `plan.md`
2. `exploration.md`
3. `implementation-log.md`
4. `grill-me-review.md`
5. `review-log.md`
6. `evaluation-log.md`
7. `final-summary.md`
8. `portfolio-log.md`

`portfolio-log.md` 구조는 Claude 작업에서 확정한 문제 상황, 고민·선택, 적용, 기술 목적, 결과와 이력서 문구 프롬프트를 따른다. 공통 템플릿이 세 host native template 경로에 동일하게 렌더링된다.

contributor는 `handoff.md`를 작성한다. 정의되지 않은 보조 기록은 자기 세션의 `unknown/`에 둔다. host를 알 수 없으면 Codex로 가정하지 않고 `.agent-policy/logs/unknown/sessions/`를 사용한다.

`PRESERVED` 전환은 owner/contributor와 무관하게 현재 상태를 담은 `handoff.md`를 요구한다. contributor는 여기까지 수행할 수 있지만 finish proposal, merge, 사후 검증과 close는 필수 8종을 책임지는 owner assignment가 수행한다.

다른 host·다른 세션의 문서는 읽을 수 있지만 수정할 수 없다. 이는 인계 문서를 읽는 협업은 허용하면서 출처와 소유권 변조를 막는다.

## 7. 공통 guard 통합

Codex legacy hook의 기능을 공통 guard와 비교했다.

| legacy 기능 | V3 처리 |
| --- | --- |
| 중앙 managed 파일 보호 | 공통 PreTool guard가 모든 host에 적용 |
| 구현 승인 확인 | 세 host의 사용자 prompt event를 공통 guard가 session별로 기록하고 source mutation 전에 검사 |
| skill·재사용 탐색 marker | 세 host의 PostTool event에서 성공한 skill·역할별 재사용/인접 구현 탐색 근거를 공통 guard가 기록 |
| source mutation marker | parent HEAD부터 current branch까지 committed diff와 dirty diff를 함께 검사 |
| session artifact 귀속 | host+session binding과 구조화된 Write 경로로 공통 처리 |
| 완료 단계 8종 내용 검사 | 제목-only, Grill Me 데이터 행, portfolio 사례 구조 검사를 명시적인 finish·verify·close 단계의 공통 guard로 이동 |
| Codex bootstrap hash | 단일 중앙 runtime bundle digest 검증으로 통합 |

Codex는 matching hook을 모두 실행하므로 legacy를 남겨 두고 공통 hook을 앞에 배치해도 중복이 사라지지 않는다. 따라서 adapter의 legacy Python hook과 등록은 제거하고 `managed_policy_guard.py` 하나로 통일한다. 공통 guard는 SessionStart, UserPrompt, PreTool과 PostTool mode로 승인·탐색·변경·산출물 보호를 포함하며 Claude Code와 OpenCode도 같은 상태 계약을 사용한다. Stop은 로그 수집만 수행하고, 호환용 `documentation-stop` mode는 항상 비차단이다.

## 8. Git 명령 분류와 사용자 전용 명령

parser는 `git -C <path>`, `git -c key=value`, `--git-dir` 같은 global option 뒤의 실제 subcommand를 찾는다. 해석 실패는 허용하지 않고 fail-closed한다.

`status`, `diff`, `log`, 조회형 `branch`, `worktree list`는 읽기 전용으로 분류해 구현 gate와 명령 승인을 적용하지 않는다. 나머지 변경형 또는 미분류 Git 호출에만 mutation 계약과 사용자 승인을 적용한다.

다음 명령은 host 승인 요청으로 해제하지 않는다.

- `git push`
- `git reset --hard`
- `git clean`
- `git update-ref`

에이전트는 실행을 반복하거나 우회하지 않는다. 필요한 이유, 정확한 ref·경로와 영향을 사용자에게 설명하고 사용자가 직접 실행하도록 양도한다.

`git pull`, reset, stash, rebase와 cherry-pick도 자동 계보 변경 때문에 차단한다. 파일 복원은 구체 pathspec의 `git restore ... -- <path>`를 사용한다. branch 전환과 merge는 별도 명령이어야 한다.

조회와 변경 형태를 함께 가진 `git symbolic-ref`는 현재 branch를 읽는 단일 인자 형태만 허용한다. raw `git branch --track/-f`, `checkout|switch --orphan`, local ref 목적지가 있는 fetch refspec도 branch workflow 우회이므로 차단한다. stage는 `git add ... -- <path>`처럼 path를 구조적으로 드러내야 하며, commit은 `-a`, `--only` 또는 pathspec으로 unstaged 파일을 암시적으로 포함하지 않는다. `git commit -m`의 메시지 값은 URL과 `/`를 포함해도 경로로 분류하지 않는다.

작업 도중 scope 변경이 필요하면 `scope-proposal`이 변경 후 전체 scope를 canonical JSON과 SHA-256으로 제시하고, 별도 승인 뒤 `update-scope`가 scopes 외 계약 불변성과 현재 dirty 경로 포함 여부를 검증한다. 검증 실패 시 기존 metadata를 복원한다.

## 9. 완료 상태와 immutable finish proposal

task 상태는 다음 순서다.

```text
IDLE -> ACTIVE -> READY_TO_MERGE -> MERGED_VERIFIED -> CLOSED
          |  ^
          v  |
       PRESERVED
```

source의 구현·산출물·검증·commit이 끝나면 `finish-proposal`이 source/target 전체 HEAD, ff-only 방식, 사후 검증 argv, cleanup 여부를 canonical JSON과 SHA-256으로 고정한다.

```sh
python3 <branch_workflow.py> finish-proposal \
  --source task/fix-spinner \
  --verify-command "npm run lint" \
  --verify-command "npm run build" \
  --cleanup
```

승인 뒤 target worktree에서 다음을 분리 실행한다.

1. `finish`: target clean과 두 HEAD를 재검증하고 ff-only merge.
2. `verify`: shell 없이 승인된 argv를 target에서 실행. 실패 시 source/worktree 보존.
3. `close`: ancestry·clean·MERGED_VERIFIED를 확인하고 CLOSED record 작성. cleanup이 계약에 있을 때만 격리 worktree와 local source branch 삭제.

raw merge·V3 branch 삭제·worktree remove는 사용하지 않는다. merge나 검증 실패 시 자동 rollback, rebase, force-delete를 하지 않는다.

## 10. 같은 세션에서 여러 작업

세션 레코드는 `task`에 불변 assignment 권한 root를, `branch`에 현재 작업 초점을 기록한다. 권한 root나 그 ACTIVE V3 자손에서 승인 생성한 child는 `asan-parent` metadata를 따라 같은 작업군에 직계·전이 자손으로 들어간다. `task/aaa-bbb` 같은 이름은 설명일 뿐 권한 판정에 사용하지 않는다.

```text
assignment root: task/meeting-reserve-ui
  └─ child: task/reserve-option-lazy-load
       └─ grandchild: task/reserve-option-api
```

이 assignment는 세 branch를 전이적으로 다룰 수 있고, clean worktree에서 root·자손 사이로 초점을 되돌릴 수도 있다. 각 mutation은 한 branch만 대상으로 하며 현재 초점 branch의 ACTIVE 상태, scope, role, Git 통합 담당자와 승인 worktree를 별도로 검증한다. 따라서 넓은 parent scope가 child의 좁은 scope를 덮어쓰지 않는다.

권한 상속은 하향 단방향이다. `task/reserve-option-lazy-load`를 root로 시작한 별도 assignment는 `task/meeting-reserve-ui`, 그 형제나 무관 branch를 수정할 수 없다. metadata가 없거나 손상됐거나 순환·깊이 제한을 위반하면 권한을 부여하지 않는다.

계보 밖의 독립 작업은 다음 규칙으로 전환한다.

- ACTIVE 또는 READY_TO_MERGE인 권한 root를 둔 채 독립 task 전환 불가.
- PRESERVED: 현재 상태를 handoff하고 별도 worktree·세션에서 독립 task 시작.
- CLOSED: 같은 프로세스에서 새 독립 branch와 새 session directory로 전환 가능.

미완료 task의 상태 전이는 `branch_workflow.py preserve --reason <근거>`로 기록하고, 같은 worktree에서 새 assignment로 재개할 때 `branch_workflow.py resume`으로 `ACTIVE`를 복원한다. `PRESERVED` 상태에서는 애플리케이션·산출물 쓰기를 허용하지 않는다.

이 제한은 “항상 새 폴더·새 세션”을 강제하려는 것이 아니다. 하나의 승인 계보는 같은 세션에서 이어가고, 무관한 미완료 작업을 번갈아 다루면서 context, index, stage와 commit 범위가 섞이는 상황만 격리한다.

dirty 기준 폴더 때문에 격리 worktree를 새로 만든 경우에도 그 branch가 권한 root의 승인된 자손이면 같은 세션이 산출물 디렉터리와 책임을 유지한 채 실행 위치와 현재 초점을 옮겨 계속할 수 있다. 반대로 `PRESERVED` 작업을 남겨 둔 채 계보 밖 작업을 동시에 진행하는 경우에는 두 독립 task의 assignment를 한 세션에 함께 바인딩하지 않고 별도 worktree·세션을 사용한다.

## 11. 실패 원칙

- Git status, path parse, contract file 또는 runtime contract를 읽지 못하면 허용하지 않는다.
- inject는 snapshot의 `.agent-policy/runtime/branch_guard.py`만 사용하고 stale consumer host hook으로 fallback하지 않는다.
- launcher는 선택한 실제 worktree에 중앙 bundle의 guard 절대 경로를 주입한다. 소비자 host 설정이나 같은 이름의 runtime으로 fallback하지 않는다.
- `git -C`, 도구 `workdir`, `--git-dir/--work-tree`는 실제 target worktree와 Git directory가 일치하는지 재평가한다. `cd`, `env -C`, `GIT_DIR/GIT_WORK_TREE`, Git directory/worktree 불일치는 해석 가능한 형태로 단순화하기 전까지 차단한다.
- launcher가 지정 worktree를 같은 Git 저장소로 검증하지 못하면 기본 프로젝트 폴더로 fallback하지 않는다.
- merge·검증·cleanup 실패는 source와 worktree를 보존한 채 사용자에게 정확한 상태를 보고한다.
- 소비자 정책 배포 기능은 사용하지 않는다. 로그 Git commit은 자동 후속 동작이 아니며 별도 승인을 받는다.

## 12. 구현 구성

| 책임 | 중앙 원본 |
| --- | --- |
| 공통 role·host·artifact registry | `policy/common/contracts/runtime-policy.json` |
| 공통 시스템 계약 | `policy/common/AGENT_POLICY.template.md` |
| 공통 8종·handoff 템플릿 | `policy/common/templates/` |
| 역할·workflow·소유권 | `policy/common/skills/policy/task-role-routing/` |
| branch 규범·CLI | `policy/common/skills/policy/git-branch-strategy/` |
| 계보·scope·Git parser | `policy/guards/branch_guard.py` |
| managed path·session·완료 단계 guard | `policy/guards/managed_policy_guard.py` |
| 중앙 bundle renderer | `lib/agent_policy/core.py` |
| inject bundle | `lib/agent_policy/injection.py` |
| worktree/session launcher | `lib/agent_policy/cli.py` |
| host·unknown log mirror | `lib/agent_policy/log_mirror.py` |

정책은 Python 한 파일에 있지 않다. 사람이 읽는 규범, 공통 machine registry, branch workflow, guard, launcher, renderer와 회귀 테스트가 하나의 계약을 구성한다.
