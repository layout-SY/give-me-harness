# 탐색

## 1. 탐색 목적

이 문서는 구현 전에 확인한 중앙 정책 구조, 기존 host별 역할 계약, Python·JavaScript runtime, 브랜치 정책과 실제 실패 사례를 기록한다. 목표는 단순히 중복 파일을 삭제하는 것이 아니라, 삭제되는 문서와 hook에만 있던 중요한 의미를 공통 정본으로 옮겼는지 재현 가능하게 남기는 것이다.

## 2. 사용자 요청에서 추출한 핵심 질문

1. Claude, Codex, OpenCode의 역할이 현재 관행에 고정돼 있는가?
2. 각 host를 따로 inject했을 때 다른 host 문서 없이도 독립적으로 공통 계약을 이해할 수 있는가?
3. OpenCode의 8종 산출물과 Claude의 portfolio 프롬프트를 동시에 보존할 수 있는가?
4. Codex legacy Python hook이 가진 기능 중 공통 guard에 없는 것이 있는가?
5. 공통 guard와 legacy hook을 함께 실행하면 실제로 중복 차단이 사라지는가?
6. dirty 기준 worktree에서 다른 세션의 변경을 건드리지 않고 독립 branch를 만들 수 있는가?
7. `git -C . reset --hard`와 `git push`가 왜 허용됐고 어디에서 fail-closed해야 하는가?
8. 다른 host·session 문서를 읽는 협업은 유지하면서 쓰기 소유권을 어떻게 보호할 것인가?
9. 산출물 이름을 알 수 없는 경우 출처를 잃지 않고 어디에 저장할 것인가?
10. 하나의 세션에서 여러 작업을 수행할 때 어떤 상태에서 안전하게 다음 작업으로 넘어갈 수 있는가?

## 3. 조사 범위

### 중앙 진입·프로젝트 설정

- `AGENTS.md`
- `CLAUDE.md`
- `README.md`
- `projects/admin-ui.json`
- `projects/user-ui.json`
- `projects/legacy/*.json`

### 공통 정책 후보

- `policy/common/**`
- `policy/guards/**`
- 기존 `policy/common/AGENTS.template.md`
- 공통 skill index와 policy/reference/recipe skill

### host adapter

- `adapters/claude/CLAUDE.template.md`
- `adapters/claude/files/.claude/agents/**`
- 삭제 예정이던 `.claude/harness/**`, `.claude/workflows/**`, `.claude/multi-agent-spec/**`, `.claude/templates/**`
- `adapters/codex/files/.codex/agents/**`
- `.codex/hooks/**`, `.codex/harness/**`, `.codex/workflows/**`, `.codex/multi-agent-spec/**`, `.codex/templates/**`
- `adapters/codex/hooks.base.json`
- `adapters/opencode/files/.opencode/agent/**`
- `adapters/opencode/files/.opencode/plugins/agent-policy.js`

### renderer·launcher·로그

- `lib/agent_policy/core.py`
- `lib/agent_policy/cli.py`
- `lib/agent_policy/log_mirror.py`
- 새 inject 구현 후보
- 현재 중앙 `logs/projects/**` 아카이브

### 테스트

- `tests/test_guard.py`
- `tests/test_rendering.py`
- `tests/test_sync.py`
- `tests/test_log_mirror.py`
- OpenCode smoke test
- 새 branch/injection 테스트 후보

## 4. 기존 역할 문서 조사 결과

### 4.1 Claude 문서에서 발견한 보존 대상

기존 Claude 문서는 host를 UI 구현자로 고정하는 문제가 있었지만 다음 의미 자체는 host와 무관하게 유효했다.

- 모든 단계가 관련 `SKILL.md`를 먼저 확인한다.
- Planner는 구현하지 않고 요청 유형, 범위, 역할, skill, 순서와 승인 요청을 만든다.
- Publisher는 UI가 포함될 때 재사용 자산, 시맨틱 구조, 접근성, 레이아웃, props/callback 계약을 정의한다.
- Generator/Implementer는 승인된 scope 안에서만 구현하고 검증과 알려진 제한을 남긴다.
- Refactorer는 관찰 가능한 동작과 공개 계약을 보존하며 구조만 개선한다.
- 공용 자산을 생성·승격하거나 계약을 바꾼 경우 Watcher PASS 뒤 reference를 갱신한다.
- Watcher는 구현을 직접 바꾸지 않고 PASS/FAIL과 조치 가능한 위반을 기록한다.
- 같은 반려 사유가 두 번 반복되면 `repeat_issue_detected`, 한 구간에서 세 번을 넘기면 escalation한다.
- Evaluator는 현재 티켓 PASS/FAIL과 장기 구조 권고를 분리한다.
- Harness는 설계·구현·판정을 대신하지 않고 승인, skill, 탐색, 문서와 retry gate만 조율한다.
- invocation 단위가 종료되어도 상태는 대화 기억이 아니라 산출물에 남긴다.

### 4.2 기존 Claude schema에서 발견한 세부 필드

초기 공통화에서 일반 필드만 남기면 아래 역할별 의미가 사라질 수 있어 별도로 비교했다.

- 공통: `summary`, `decision`, `reasons`, `artifacts`, `next_action`, `log`, `status`
- Planner: `work_type`, `scope`, `sections`, `required_agents`, `required_skills`, `approval_request`
- Publisher: `ui_structure`, `reusable_components_found`, `new_components_needed`, `event_interface_points`, `handoff`
- Generator: `implementation_summary`, `reused_assets`, `newly_created_assets`, `validation_points`, `known_risks`, `handoff`
- Refactorer: `refactor_targets`, `applied_changes`, `deferred_improvements`, `risk_notes`, `handoff`
- Watcher: `review_result`, `pass_fail`, `violations`, `required_fixes`, `repeat_issue_detected`, `escalation_needed`
- Evaluator: `diagnosis_report`, `architectural_risks`, `improvement_options`, `recommended_backlog`, `handoff`
- Harness: `can_proceed`, `missing_requirements`, `role_violation_detected`, `approval_status`, `retry_count`, `escalation_signal`
- 상태: draft, ready_for_approval, approved, in_progress, review_requested, rejected, escalated, completed, deferred, recommendation_ready, handed_off 등

이 필드는 공통 `agent-output-schema.yaml`의 union 구조와 각 산출물 템플릿에 복구하는 대상으로 결정했다.

### 4.3 Codex 문서에서 발견한 보존 대상

- 한 번에 하나의 논리 구간을 작업한다.
- 관련 skill만 로드하고 인접 구현과 재사용 자산을 먼저 찾는다.
- Watcher와 Evaluator의 책임을 분리한다.
- 요구 불명확은 Planner, 계약 충돌은 Publisher, 구현 실패는 구현 역할, 반복 실패는 재계획으로 돌린다.
- 기존 7종에 portfolio를 더한 8종을 작업 산출물로 사용한다.
- 승인, skill, 탐색 marker가 없으면 source mutation을 차단한다.
- 애플리케이션 변경을 감지하면 Stop에서 산출물을 확인한다.

### 4.4 제거 대상으로 분류한 host 고정 의미

- “Claude Code는 production UI만 수정한다.”
- “Logic Session은 Codex/OpenCode가 소유한다.”
- “UI_COMPLETE 후 Logic Session이 통합한다.”
- “Claude가 `.claude/logs`, Logic Session이 `.codex/logs`를 의미적으로 소유한다.”
- 특정 host 이름만으로 파일 수정 권한이나 Git 통합 권한을 얻는 규칙

이 문장들은 현재 운영 관행의 기록일 뿐 미래의 역할 계약으로 사용할 수 없으므로, 역할명과 assignment로 치환하고 원문 의미를 그대로 보존하지 않았다.

## 5. 기존 Codex Python hook 대 공통 guard 비교

| 기존 파일·기능 | 기존 동작 | 공통 guard의 기존 상태 | 결정 |
| --- | --- | --- | --- |
| `track-user-prompt.py` | 명시적 구현 승인 marker 기록 | host 공통 구현 승인 상태가 부족 | `user-prompt` mode로 흡수 |
| `track-posttooluse.py` | skill과 재사용 탐색 marker 기록 | managed guard는 실제 탐색 evidence를 추적하지 않음 | `post-tool` mode로 흡수 |
| `enforce-pretooluse.py` | marker 없을 때 source mutation 거부 | managed path·branch 검사는 있었으나 readiness gate 부족 | 공통 `implementation_gate_denial`로 흡수 |
| `require-documentation-stop.py` | 애플리케이션 변경 시 산출물 구조 검사 | host별 Stop과 공통 Stop이 중복 | 공통 `documentation_denial`로 통합 |
| `hook_common.py` | root·state·path·hash 공통 함수 | 일부 기능이 managed guard와 중복 | 필요한 session state만 공통 guard 내부로 이동 |
| bootstrap SHA | legacy entry+common 자체 hash | inject snapshot/manifest digest와 별도 중복 | managed bundle digest로 대체 |

### 비교에서 확인한 핵심 결론

공통 guard가 “더 먼저 실행되는 hook”이어서는 안 된다. Codex는 matching hook을 모두 실행하므로 legacy deny는 계속 유효하다. 공통 guard가 상위 계약이 되는 유일하게 일관된 방법은 다음 두 조건을 동시에 만족하는 것이다.

1. legacy의 승인·evidence·mutation·Stop 기능을 공통 구현에 포함한다.
2. legacy hook 파일과 이벤트 등록을 제거해 공통 구현만 실행한다.

## 6. 브랜치 실패 사례 조사

### 6.1 stale guard 로딩

기존 `branch_workflow.py`의 후보 순서는 snapshot 안 `.agents/hooks`, 소비자 `.codex/hooks`, 소비자 `.claude/hooks`에 가까웠다. snapshot의 첫 후보가 없으면 오래된 소비자 사본을 선택했다. 소비자 사본에 `FULL_SHA_PATTERN`이 없으면 다음 오류가 발생했다.

```text
AttributeError: module 'asan_branch_guard' has no attribute 'FULL_SHA_PATTERN'
```

근본 원인은 기능 누락이 아니라 inject 실행이 불변 snapshot 대신 mutable consumer 파일에 의존한 것이었다. 따라서 inject에서는 snapshot runtime 외 fallback을 금지하기로 했다.

### 6.2 축약 SHA와 승인 식별자

Git commit SHA는 40자리이고 proposal 승인 식별자는 canonical JSON의 SHA-256 64자리다. 기존 흐름은 둘을 축약하거나 혼용할 수 있어 proposal을 승인한 뒤 Write/create에서 다른 문자열을 비교했다. 해결 방향은 출력, 사용자 승인, 실행 인자를 모두 전체 64자리 proposal digest로 통일하는 것이다.

### 6.3 dirty worktree

기준 폴더에 다른 세션의 `package.json`, lockfile, UI/API 변경이 남아 있을 때 direct branch 생성은 그 변경을 새 branch로 데려간다. guard가 이를 막는 것은 맞지만 “먼저 모두 commit/stash하라”만 제시하면 독립 작업을 불필요하게 차단한다. 독립 task는 기준 branch ref의 commit에서 저장소 밖 worktree를 만들고, 미커밋 선행 변경에 의존하는 child task만 parent owner의 commit/handoff를 기다리는 것으로 구분했다.

### 6.4 checkout과 compound command

- `git checkout -- src/x.ts`: branch 인자가 아니라 path restore다. 다만 의미가 중의적이므로 명시적 `git restore ... -- src/x.ts`를 사용한다.
- `git checkout sy-main && git merge task/x`: 두 번째 명령은 실제로 branch가 바뀐 후 평가해야 하지만 hook은 실행 전 상태만 본다. 따라서 전환과 merge를 별도 도구 호출로 나눈다.

### 6.5 global option 뒤 위험 subcommand

기존 파서는 첫 번째 토큰 뒤가 곧 subcommand라고 가정하거나 알 수 없는 형태에서 `None`을 반환했다. `git -C . reset --hard`의 실제 subcommand는 `reset`, `git -C . push`는 `push`다. `-C`, `-c`, `--git-dir`, `--work-tree`, `--config-env` 등 global option을 소비한 뒤 실제 subcommand를 찾고, 해석할 수 없는 alias·wrapper는 허용하지 않는 방향으로 정했다.

## 7. 산출물·세션 귀속 조사

### 확인된 문제

- Bash heredoc은 도구 payload에 최종 파일 경로가 구조적으로 들어오지 않을 수 있다.
- Stop hook은 “이 파일을 누가 처음 썼는가”를 재현하지 못한다.
- 모든 host 로그를 branch scope 예외로 허용하는 것만으로는 세션별 쓰기 소유권을 보호할 수 없다.
- 상대 host의 handoff를 읽지 못하게 하면 순차 협업이 불가능하다.
- 알려지지 않은 파일을 session root에 쓰면 8종 schema와 임시 메모가 섞인다.

### 선택한 규칙

- 최초 산출물 생성은 host의 구조화된 Write/Edit/apply_patch 도구를 사용한다.
- 현재 `host + session_id + session-dir + branch/task + responsibility`를 binding record로 남긴다.
- 다른 host·session 경로는 Read를 허용하고 mutation과 Git stage/commit을 차단한다.
- known artifact는 session root, unknown artifact는 해당 session의 `unknown/`만 허용한다.
- session id를 얻을 수 없는 runtime은 start에서 선언한 `ASAN_SESSION_DIR`이 없으면 쓰기를 허용하지 않는다.
- host 자체를 알 수 없으면 Codex로 추정하지 않고 unknown host root를 사용한다.

## 8. 재사용 가능 자산 조사

| 기존 자산 | 재사용 방식 | 이유 |
| --- | --- | --- |
| `managed_policy_guard.py` | mode와 session state 확장 | 이미 세 host 관리 파일 보호의 공통 실행점 |
| `core.render_project` | 공통 정본을 여러 native path에 동일 투영 | manifest·digest·프로젝트 placeholder 처리 재사용 |
| project JSON | validation argv와 base branch 공급 | 프로젝트별 값은 공통 코드에서 분리해야 함 |
| log mirror | host registry와 unknown 수집으로 확장 | 중앙 로그의 append/change-only 원칙 유지 |
| OpenCode 8종 목록 | runtime registry의 required 목록으로 승격 | 사용자 지정 공통 산출물 기준 |
| Claude portfolio prompt | 공통 portfolio template으로 승격 | 문제·대안·기술 목적·결과를 가장 상세히 보존 |
| 기존 branch metadata | V3 field와 task state로 확장 | parent·scope·integrator 개념 자체는 유효 |

## 9. 새 자산 필요성

### `runtime-policy.json`

role, host artifact root, required artifacts, responsibility, task states, never-agent 명령과 validation 명령을 문서·Python·JavaScript가 따로 정의하지 않게 한다.

### `role_profiles.py`

CLI role 이름과 canonical 역할, 포함할 references/skills/native agents를 한 곳에서 선택한다. host 인자는 경로·실행 형식에만 영향을 주고 역할 의미에는 영향을 주지 않는다.

### `injection.py`

소비자를 수정하지 않고 중앙 원본에서 immutable bundle을 만든다. 외부 worktree에서도 해당 bundle의 절대 runtime 경로를 hook command에 넣고, 선택 role 문서만 포함한다.

### `branch_guard.py`

Git parser, 계보, scope, integrator, task 상태와 사용자 전용 명령을 managed/document guard와 분리해 테스트 가능한 순수 판정 계층을 만든다.

### 새 `branch_workflow.py`

proposal/create/preserve/resume/finish-proposal/finish/verify/close를 하나의 lifecycle로 제공하고 raw Git 명령 우회를 줄인다.

## 10. 성능·복잡도 분석

- 이 저장소는 애플리케이션 UI가 아니라 정책 빌드 도구이므로 React re-render 영향은 없다.
- renderer는 공통 파일을 세 native template 경로로 복제하지만 입력 정본은 하나라 유지보수 비용이 감소한다.
- hook은 매번 전체 저장소를 스캔하지 않고 tool target, Git status/diff, 작은 session state를 중심으로 판정한다.
- Stop은 dirty diff뿐 아니라 parent HEAD 이후 committed diff도 확인하므로 기존보다 Git 호출이 늘지만, 완료 시점에만 실행되어 안전성 이득이 크다.
- inject bundle은 role별로 문서를 선택해 전체 공통 skill을 무조건 넣는 방식보다 context와 파일 수를 줄인다.
- 외부 라이브러리를 추가하지 않고 Python·Node 표준 기능과 기존 Git을 사용한다.

## 11. 미확인·배포 후 확인 항목

- 소비자 sync 전이므로 실제 consumer session에서 새 event payload가 들어오는 최종 smoke test는 남아 있다.
- 소비자 legacy 11개는 audit에 고정된 hash가 일치할 때만 별도 `--retire-legacy`로 제거해야 한다.
- role 침범은 이번 범위에서 system prompt 계약으로만 운영한다. 실제 침범 사례가 생기면 별도 hook 여부를 재평가한다.
- V3 도입 전에 만들어진 현재 중앙 branch에는 V3 metadata가 없으며 이를 사후 위조하지 않는다.

## 12. 탐색 결론

가장 안전하고 재사용 가능한 구조는 다음 의존 방향이다.

```text
공통 의미·runtime registry
  -> renderer와 inject selector
    -> host별 system prompt·hook/plugin·native agent 형식
      -> 소비자 세션 assignment
```

branch 실행은 다음과 같이 분리해야 한다.

```text
역할·계획 승인
  -> canonical branch proposal와 전체 SHA 승인
  -> isolated task worktree
  -> owner/contributor assignment
  -> 구현·검증·문서·commit
  -> canonical finish proposal와 전체 SHA 승인
  -> ff-only finish -> target verify -> close
```

이 구조는 host를 교체해도 역할 의미가 유지되고, 다른 세션의 dirty/index를 건드리지 않으며, 위험 Git 명령이 승인 경로로 빠지는 것을 막는다.

## 13. 후속 전수조사 — sync runtime과 다중 worktree 문맥

### 13.1 sync hook 경로 재현

`lib/agent_policy/core.py`의 기존 `hook_command()`는 다음 의미였다.

```text
hook 실행 cwd의 git top-level
  -> <그 top-level>/.agent-policy/runtime/managed_policy_guard.py
```

소비자 기본 checkout에는 sync가 만든 runtime이 있지만 `.agent-policy/`가 ignore된 새 worktree에는 해당 파일이 없다. 외부 worktree에서 `git rev-parse --show-toplevel`은 그 외부 폴더를 반환하므로 Python은 존재하지 않는 파일을 열고 exit 2로 끝났다. PreToolUse의 fail-closed 자체는 유지됐지만, 올바른 task worktree에서도 모든 작업이 불가능했다.

inject는 이미 bundle의 절대 runtime 경로를 command에 넣고 있어 같은 결함이 없었다. 따라서 공통 해결책은 `${CLAUDE_PROJECT_DIR}` 같은 실행 cwd 변수를 바꾸는 것이 아니라, sync 시점에 알고 있는 `projects/*.json:path`를 정책 anchor로 고정하는 것이다.

### 13.2 `git -C` 오탐과 미탐 재현

기존 `_strip_git_global_options()`는 `-C`와 뒤 경로를 제거하고 `add`, `commit` 같은 subcommand만 반환했다. 이후 모든 검사는 hook event의 `root`에서 수행됐다.

| event cwd | 실제 명령 대상 | 기존 판정 | 실제 위험 |
| --- | --- | --- | --- |
| primary `sy-main` | `git -C <task-wt> add` | primary가 기준 branch라 차단 | 정상 task index 작업을 오탐 |
| task worktree | `git -C <primary> add` | task branch가 ACTIVE라 허용 | `sy-main` primary index를 변경하는 미탐 |
| task worktree | `--git-dir=<primary> --work-tree=<primary>` | global option 제거 후 task로 판정 | primary index 우회 |
| task worktree | `GIT_DIR=... GIT_WORK_TREE=... git add` | 환경 prefix 미추적 | 임의 index/worktree 조합 가능 |

실제 임시 Git 저장소에서 두 번째 명령을 실행하면 primary index가 stage되는 것까지 확인했다. 따라서 단순히 `-C`를 허용 목록에 넣는 것이 아니라, 호출마다 target top-level과 current branch를 다시 읽어야 한다.

### 13.3 Git directory와 worktree 결합 문제

`--git-dir`와 `--work-tree`를 둘 다 해석해 top-level만 구하는 것으로는 충분하지 않았다. 예를 들어 primary의 `.git` directory와 task의 working tree를 조합하면 출력 경로는 task처럼 보이면서 primary index·HEAD를 사용할 수 있다. 이에 따라 다음 두 값을 비교하는 추가 invariant가 필요했다.

```text
명령이 실제로 선택한 Git directory
  == target worktree에서 git rev-parse --absolute-git-dir로 확인한 Git directory
```

일치하는 명시적 쌍은 실제 target branch에서 검사하고, 단독 `--git-dir` 또는 서로 다른 쌍은 변경 명령에서 차단한다.

### 13.4 shell 상태 변경 우회

다음 표현도 event cwd 기준 검사를 우회할 수 있었다.

- `cd <primary> && git add ...`
- `env -C <primary> git add ...`
- `GIT_DIR=<primary-git-dir> GIT_WORK_TREE=<primary> git add ...`
- `git switch scratch && git commit ...`

완전한 shell interpreter를 hook 안에 구현하는 것은 quoting, subshell, function과 환경 상속 때문에 신뢰하기 어렵다. 정책은 안전하게 표현 가능한 `tool_input.workdir`, `git -C`, 일치하는 `--git-dir/--work-tree`만 해석하고 나머지는 단순화 전까지 차단하는 방향으로 정했다. branch 전환과 후속 Git 변경도 한 command에서 분리한다.

### 13.5 session binding의 worktree 종속성

기존 session binding과 구현 승인 state 파일 이름은 `root + host + session id` hash였다. 같은 세션이 primary에서 승인 task worktree로 이동하면 서로 다른 세션 state처럼 보였다. 또한 binding record는 산출물 상대 경로만 가지고 있어 어느 worktree의 문서인지 복원할 수 없었다.

Git worktree들은 `git rev-parse --git-common-dir` 값은 공유한다. 따라서 session identity를 `git common directory + host + session id`로 변경하고 record에 절대 worktree를 추가하면 다음 두 요구를 함께 만족한다.

- 같은 세션이 단일 ACTIVE task의 승인 worktree로 이동해도 승인·탐색·산출물 귀속이 유지된다.
- 첫 task가 CLOSED되기 전에는 다른 task branch나 다른 session directory로 rebind할 수 없다.

### 13.6 구조화된 파일 경로 조사

Write/Edit/apply_patch가 event root 밖의 절대 경로를 받으면 기존 `repository_relative()`는 `None`을 반환했고 branch scope 검사 대상에서 조용히 빠졌다. 외부 worktree는 같은 저장소지만 경로상 primary 밖에 있으므로 정상 작업과 우회가 구분되지 않았다.

해결 기준은 대상 파일의 가장 가까운 기존 부모에서 Git top-level을 찾고, event root와 Git common directory가 같은지 확인한 뒤 그 target root 기준 상대 경로를 계산하는 것이다. 같은 저장소의 승인 task worktree이면 target branch scope를 검사하고, 다른 저장소이거나 Git 소속을 증명할 수 없으면 차단한다. `.git` 및 `.git/**`는 scope가 `.`이어도 구조화된 도구로 직접 수정할 수 없게 별도 보호한다.

## 14. 후속 탐색 결론

세션의 시작 폴더와 task의 변경 공간은 같은 개념이 아니다. 안정적인 판정 축은 다음과 같다.

```text
정책 실행 원본 = sync primary absolute runtime 또는 inject immutable bundle
세션 identity = Git common directory + host + session id
활성 작업 = binding record의 미종료 task branch
변경 경계 = 각 도구/각 Git 호출이 실제로 겨냥한 승인 worktree
```

이 네 축을 분리하면 dirty primary를 보존한 채 같은 세션에서 isolated task를 수행할 수 있고, cwd만 바꿔 기준 branch를 수정하는 우회도 동시에 막을 수 있다.

## 15. 사용 가이드 작성 전 조사

README는 중앙 구조와 mode의 핵심 차이를 설명하지만, 처음 사용하는 운영자가 세션 시작부터 branch 종료까지 그대로 따라갈 수 있는 순차 절차는 없었다. 상세 branch 전략은 설계 근거와 상태 기계에 집중해 다음 질문의 즉답을 찾기 어려웠다.

- sync와 inject 중 어떤 mode를 선택하는가.
- 중앙 정책 변경 뒤 sync가 필요한 세션과 필요하지 않은 세션은 무엇인가.
- dirty sy-main에서 worktree를 만든 뒤 현재 세션을 계속 써도 되는가.
- 기존 inject 세션을 갱신할 때 worktree로 직접 cd해야 하는가.
- owner와 contributor가 어떤 문서를 작성하고 누가 완료 workflow를 수행하는가.
- 기존 오탐 사례를 만났을 때 어떤 명령 형태로 바꿔야 하는가.

agent-policy start/sync/collect-logs와 branch_workflow.py의 모든 subcommand help를 직접 확인했다. proposal의 scope·role과 finish-proposal의 verify-command가 반복 인자이며, inject role 필수·sync role 금지, worktree/branch/task 일치 검증과 session-dir 형식을 CLI 구현과 대조했다.

또한 sync absolute runtime 수정의 경계를 문서에 명확히 했다. 이 수정은 primary에서 이미 로드한 sync hook이 외부 worktree를 대상으로 실행될 때 runtime을 잃지 않게 한다. 외부 worktree에 host 설정 자체를 복제하는 기능은 아니므로, 새 세션을 외부 worktree에 직접 열어야 할 때는 inject를 사용한다. 이 제한을 숨기지 않고 세션 시작 절에 포함했다.

결론적으로 새 문서는 정책 정본을 복제하는 사양서가 아니라 선택표, 실행 예시, 상태별 시나리오, 문제 해결표와 체크리스트를 제공하는 운영 진입 문서로 설계했다.
