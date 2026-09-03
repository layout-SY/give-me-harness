# 구현 로그

## 1. 구현 개요

이번 변경은 단일 버그 수정이 아니라 정책의 의미 계층, host adapter, inject launcher, Git branch lifecycle과 산출물 책임을 함께 재설계한 작업이다. 구현은 “공통 의미를 한 곳에 둔다”, “host는 실행 형식만 담당한다”, “위험한 상태 변경은 fail-closed한다”는 세 원칙으로 진행했다.

## 2. 승인된 범위

- 중앙 정책 원본과 테스트만 변경한다.
- `policy/`, `adapters/`, `projects/`, `lib/`, `tests/`, `docs/`의 연관 영역을 함께 수정한다.
- OpenCode 기준 8종을 owner 필수 산출물로 만든다.
- portfolio 형식은 Claude의 기존 문제·선택·적용·기술 목적·결과 구조를 따른다.
- Codex legacy Python hook 기능을 공통 guard에 포함한 뒤 중복 파일과 등록을 제거한다.
- `git -C . reset --hard`와 모든 push는 승인으로 풀지 않고 사용자에게 양도한다.
- 다른 host·session 산출물은 읽을 수 있지만 쓸 수 없게 한다.
- 알 수 없는 산출물은 현재 session의 `unknown/`에 둔다.
- 역할 침범 감시용 새 hook은 만들지 않고 system prompt에만 명시한다.
- 소비자 sync와 push는 수행하지 않는다.

## 3. 변경 사항 요약

| 영역 | 핵심 변경 | 결과 |
| --- | --- | --- |
| 공통 진입점 | `AGENT_POLICY.template.md` 신설, `AGENTS.md`와 common path에 동일 렌더 | Claude가 Codex 문서에 의존하지 않으면서 모든 host가 같은 정본 사용 |
| 역할 선택 | `--role logic|ui|orchest|review|generate`와 profile 도입 | host/model과 역할을 독립 축으로 분리 |
| 역할 문서 | routing, logic, ui, orchestration, pipeline, workflow, handoff/ownership 공통화 | 기존 역할 의미를 host 이름 없이 보존 |
| 산출물 | 8종+handoff 공통 template과 union schema | 모든 host에 동일 bytes 제공 |
| 공통 guard | 승인·탐색·mutation·산출물·명령 gate 통합 | Codex legacy hook 기능의 상위 단일 구현 |
| branch guard | Git global option parser, V3 metadata·scope·state | 위험 명령 우회와 계보 오류 차단 |
| branch workflow | canonical proposal, isolated worktree, preserve/resume, finish/verify/close | dirty worktree와 독립된 task lifecycle |
| inject | role별 immutable bundle, snapshot 절대 hook 경로 | 외부 worktree에서 consumer 상대 경로 의존 제거 |
| 로그 | codex/claude/opencode/unknown 채널과 unknown 파일 수집 | host 오귀속 방지와 legacy logic alias 유지 |
| 자동 감사 | 공통 정본·hook 단일화·template 동일성·금지 문구 검사 | 삭제·회귀 시 중앙 audit가 실패 |

## 4. 공통 정책 구조 구현

### 4.1 공통 진입 문서

`policy/common/AGENTS.template.md`를 host 중립 정본으로 사용하려던 기존 구조를 `policy/common/AGENT_POLICY.template.md`로 명확히 바꿨다. renderer는 이 한 파일을 다음 두 위치에 동일한 내용으로 렌더한다.

- 소비자 루트 `AGENTS.md`: host discovery용 진입점
- `.agent-policy/common/AGENT_POLICY.md`: 모든 host adapter가 직접 참조하는 의미 정본

Claude의 `CLAUDE.md`는 `AGENTS.md`나 `.codex/**`를 경유하지 않고 common 경로를 직접 참조한다. Codex와 OpenCode native agent도 같은 common references를 가리킨다.

### 4.2 역할 profile

`runtime-policy.json`에 CLI role과 canonical role을 분리했다.

| CLI role | canonical 의미 |
| --- | --- |
| `logic` | API, DTO, parser, validator, hook, util, store, 상태 전이 |
| `ui` | 화면, 스타일, 자산, 접근성, 반응형, UI 계약 |
| `orchest` | 요청 조사, 계획, 역할·소유권·승인·완료 gate |
| `review` | 구현을 바꾸지 않는 Watcher/Evaluator 검토 |
| `generate` | 승인된 handoff와 scope의 Logic+UI 통합 구현 |

`role_profiles.py`는 각 role에 필요한 common references, skill prefix와 host native agent 목록을 선택한다. `host`와 `model`은 여전히 별도 start 인자이며 role을 암시하지 않는다.

### 4.3 역할 확인 규칙

- inject의 `--role`은 세션 시작 시 확인된 profile로 본다.
- 같은 profile 범위에서는 요청마다 역할 질문을 반복하지 않는다.
- 다른 역할이 필요하면 현재 세션 권한을 자동 확대하지 않고 새 role 세션을 요청한다.
- role 없이 시작한 흐름은 사용자 요청과 최신 handoff를 근거로 역할을 제안하고 확인받는다.
- handoff의 `next_role`은 제안일 뿐 자동 권한이 아니다.

## 5. 8종 산출물과 schema 구현

### 5.1 owner와 contributor 분리

- `owner`: 작업 전체, 공통 8종, 최종 검증, finish/verify/close 책임
- `contributor`: 일부 역할 구현과 `handoff.md`, 필요 시 preserve 책임

기존 branch 단위 `artifact-mode=full|handoff`는 동일 branch에서 여러 assignment가 순차 작업하는 경우를 표현하지 못했다. V3에서는 responsibility를 start 시점 session assignment로 이동했다.

### 5.2 공통 템플릿

`policy/common/templates/**`를 하나의 source로 만들고 `.codex/templates`, `.claude/templates`, `.opencode/templates`에 동일 bytes로 렌더한다.

필수 8종:

1. `plan.md`
2. `exploration.md`
3. `implementation-log.md`
4. `grill-me-review.md`
5. `review-log.md`
6. `evaluation-log.md`
7. `final-summary.md`
8. `portfolio-log.md`

`portfolio-log.md`에는 Claude에서 사용하던 다음 구조를 정확히 유지했다.

- 사례 metadata: 작업 유형, 관련 도메인/서비스, 문제 출처
- 문제 상황
- 고민과 선택
- 적용
- 사용 기술과 구체적 목적
- 결과
- 이력서·포트폴리오 문구

### 5.3 구현 중 발견한 schema 누락과 보완

host별 template을 공통화하는 첫 과정에서 일반적인 summary/evidence만 남기면 기존 Claude agent-specific 필드가 사라지는 문제가 발견됐다. 삭제 전 파일을 다시 읽어 Planner부터 Harness까지의 모든 역할별 필드를 공통 union schema로 복구했다. `audit_source_contract()`에 핵심 role field가 사라지면 실패하는 검사를 추가해 같은 누락이 재발하지 않게 했다.

## 6. 공통 guard 단일화 구현

### 6.1 legacy 비교 결과 반영

기존 Codex hook의 네 이벤트 책임을 `managed_policy_guard.py` mode로 통합했다.

| 이벤트 | 공통 mode | 기록·판정 |
| --- | --- | --- |
| UserPromptSubmit | `user-prompt` | 구현 승인, command 승인, proposal SHA 승인 |
| PreToolUse | `pre-tool` | managed path, artifact ownership, branch scope, readiness, operation gate |
| PostToolUse | `post-tool` | 실제 skill/read/search evidence와 proposal output |
| Stop | `documentation-stop` | 변경 감지와 owner 8종/contributor handoff 구조 검사 |

Codex의 `hooks.base.json`은 legacy 등록을 비우고 renderer가 공통 네 이벤트를 생성한다. `.codex/hooks/`의 legacy Python 파일·README·자체 테스트는 삭제했다. Codex config에는 현재 지원되는 `[features] hooks = true`만 남겼다.

### 6.2 구현 승인과 evidence

- 승인 문구는 Unicode 정규화와 문장부호 제거 후 허용된 독립 문구만 인식한다.
- 취소·거부·보류가 포함되면 승인보다 우선한다.
- prompt의 “skill 읽었다” 자기 선언은 evidence로 인정하지 않는다.
- 성공한 Skill/Read/Grep/Glob/Search/shell read 이벤트를 PostTool state에 기록한다.
- UI role은 일반 인접 구현 외 `src/shared/ui` 또는 component reference 탐색도 요구한다.
- source mutation 전에 구현 승인, 관련 skill, 역할별 탐색이 모두 있어야 한다.

### 6.3 proposal SHA 승인 연결

proposal을 만들기 전에는 SHA가 존재하지 않으므로 계획 승인과 branch 승인을 한 prompt에서 합치면 정확한 digest를 binding할 수 없다. 이를 다음 흐름으로 고정했다.

1. proposal/finish-proposal 실행 성공 output에서 canonical 64자리 SHA를 PostTool state에 기록한다.
2. 그 다음 독립 사용자 prompt의 승인만 해당 pending SHA에 연결한다.
3. create/finish/verify/close 실행 인자의 SHA가 승인된 SHA와 정확히 일치하는지 확인한다.
4. 다른 SHA, 축약 SHA 또는 변경된 proposal은 거부한다.

### 6.4 tool 이름 차이 보완

초기 공통 guard는 `Bash`/`Shell` 이름만 shell 도구로 인식했다. 현재 실행 환경의 `functions.exec` alias를 놓치면 같은 명령이 host에 따라 다른 판정을 받을 수 있어 tool name normalization과 `exec`, `exec_command`, `functions.exec` 지원을 추가했다.

### 6.5 shell redirect 오탐 보완

- `2>&1`, `2>/dev/null`, 저장소 밖 임시 진단 파일 redirect는 source mutation으로 보지 않는다.
- 저장소 안 실제 redirect target은 branch scope 검사 대상으로 추가한다.
- Bash heredoc/redirect로 산출물을 만드는 것은 귀속을 기록할 수 없어 계속 거부한다.
- `rm`, `mv`, `cp`, `touch`, `sed -i`와 compound command 안의 비구조적 파일 mutation은 structured Edit/Write/apply_patch 사용을 안내하며 차단한다.

## 7. 산출물 소유권 구현

### 7.1 경로와 binding

host별 root:

- Codex: `.codex/logs/sessions/`
- Claude: `.claude/logs/sessions/`
- OpenCode: `.opencode/logs/sessions/`
- unknown host: `.agent-policy/logs/unknown/sessions/`

최초 structured write에서 session directory를 host+session state에 binding한다. start가 `ASAN_SESSION_DIR`을 제공하면 session ID가 없는 runtime도 선언된 디렉터리만 사용할 수 있다.

### 7.2 교차 읽기와 쓰기

- 다른 host 또는 session의 산출물 Read는 허용한다.
- Write/Edit/patch와 Git stage/commit은 현재 binding 디렉터리만 허용한다.
- current host라도 다른 session directory 쓰기는 거부한다.
- 알려진 8종과 handoff는 session root에 둔다.
- 그 외 이름은 current session의 `unknown/` 아래에만 둔다.

### 7.3 Stop 변경 감지

기존 Stop은 dirty status만 보면 이미 commit된 source 변경을 놓칠 수 있었다. V3 metadata의 승인 parent HEAD부터 current HEAD까지의 committed diff와 working tree/index diff를 모두 합쳐 애플리케이션 변경을 판단하도록 수정했다.

## 8. Branch Contract V3 구현

### 8.1 immutable branch proposal

proposal은 다음 모든 필드를 정렬한 canonical JSON으로 저장한다.

- version, task id, branch, purpose
- parent, 40자리 parent HEAD, merge target
- roles, scopes, reason
- Git integrator
- 선택적 절대 worktree 경로

파일은 Git common directory 아래 `asan-agent-policy/proposals/<sha256>.json`에 저장한다. create는 긴 인자를 다시 받지 않고 proposal file과 64자리 SHA만 소비한다. canonical bytes, digest, parent HEAD, branch/worktree 상태 중 하나라도 달라지면 실패한다.

### 8.2 isolated worktree

- 기준 폴더가 dirty이거나 사용 중인 독립 작업은 기존 파일을 commit/stash/reset하지 않는다.
- 승인 proposal에 저장소 밖 절대 worktree 경로를 포함한다.
- create는 parent ref의 승인된 commit에서 새 branch와 독립 index/working directory를 만든다.
- parent의 미커밋 변경에 실제로 의존하는 child는 생성하지 않고 parent owner의 commit/handoff를 요구한다.

### 8.3 lifecycle

```text
IDLE -> ACTIVE -> READY_TO_MERGE -> MERGED_VERIFIED -> CLOSED
          |  ^
          v  |
       PRESERVED
```

- `preserve`: 현재 session에 내용이 있는 `handoff.md`가 있어야 한다.
- `resume`: 같은 task/worktree에서 새 assignment가 ACTIVE를 복원한다.
- `finish-proposal`: source/target full HEAD, ff-only, validation argv, cleanup을 canonical SHA로 고정한다.
- `finish`: target clean과 두 HEAD 불변을 확인한 뒤 ff-only merge한다.
- `verify`: 등록된 lint/test/build argv만 shell 없이 target에서 실행한다.
- `close`: ancestry, target clean, MERGED_VERIFIED를 재검사하고 CLOSED를 기록한다.
- cleanup은 proposal에 포함돼 승인된 경우만 worktree와 local branch에 적용한다.

### 8.4 contributor 완료 권한 보완

처음에는 contributor가 handoff를 작성하면 preserve뿐 아니라 완료 흐름에 접근할 여지가 있었다. handoff는 부분 기여의 증거이지 8종·통합 검증의 대체물이 아니므로 finish-proposal/finish/verify/close를 owner assignment로 한정했다.

## 9. Git parser·위험 명령 구현

### 9.1 global option 처리

`git -C`, `git -c`, `--config-env`, `--git-dir`, `--work-tree`, `--namespace`, `--exec-path` 등을 소비한 뒤 실제 subcommand를 찾는다. alias 설정이나 해석할 수 없는 wrapper는 안전하다고 추측하지 않고 차단한다.

### 9.2 절대 사용자 전용 명령

다음은 operation approval 검사보다 먼저 차단한다.

- `git push`
- `git reset --hard`
- `git clean`
- `git update-ref`

메시지는 “승인 요청”을 안내하지 않는다. 에이전트가 명령의 이유, 정확한 ref/경로와 영향을 사용자에게 양도하고 사용자가 직접 실행하도록 한다. nested shell과 Git alias 문자열도 별도 텍스트 검사로 찾는다.

### 9.3 기타 Git 우회 차단

- raw reset, rebase, stash, pull, cherry-pick
- `git branch --track/-f`
- checkout/switch orphan 및 implicit branch create
- local ref 목적지 fetch refspec
- 쓰기형 `git symbolic-ref`
- raw merge, V3 branch 삭제, worktree remove
- separator 없는 `git add`, pathspec file 사용
- unstaged 파일을 암시적으로 포함하는 `git commit -a|--only|<path>`

파일 복원은 구체 pathspec이 있는 `git restore ... -- <path>`만 사용한다. branch 전환과 merge는 각각 독립 호출로 판정한다.

## 10. inject와 external worktree 구현

### 10.1 launcher 검증

- `--mode inject`는 `--role`을 필수로 요구한다.
- `--worktree`는 대상 프로젝트와 같은 Git common directory인지 확인한다.
- 경로가 존재하지 않거나 다른 저장소이거나 worktree root가 아니면 기본 프로젝트 폴더로 fallback하지 않는다.
- `--branch`, `--task`, 실제 current branch가 서로 일치해야 한다.
- `--session-dir`는 해당 host root 바로 아래의 검증된 slug만 허용한다.

### 10.2 snapshot 절대 경로

Claude 외부 worktree에서 `${CLAUDE_PROJECT_DIR}/.claude/hooks/...`를 사용하면 해당 worktree에 sync 파일이 없어 hook이 실행되지 않는 문제가 있었다. inject bundle에는 snapshot runtime을 포함하고 Claude plugin/Codex home/OpenCode home의 hook command를 그 절대 경로로 치환했다. `branch_workflow.py`도 inject에서는 snapshot의 common runtime만 신뢰한다.

### 10.3 OpenCode event 연결

- `chat.message` -> user approval state
- `tool.execute.before` -> pre-tool guard
- `tool.execute.after` -> skill/read/search evidence
- `session.idle` -> documentation Stop과 성공 시 log collection
- `experimental.session.compacting` -> branch context 재주입

기존 `logic` log channel 고정을 `opencode`로 수정하고 session ID shape 차이를 정규화했다.

## 11. 구현 과정에서 발생한 문제와 해결

### 문제 A — “Claude 독립”을 Codex와의 완전 분리로 잘못 해석할 가능성

초기 방향은 CLAUDE 문서를 독립적으로 충분히 작성하는 데 치우칠 수 있었다. 사용자는 의도가 “공통 진입 방향을 버리는 것”이 아니라 “Codex에 종속되지 않은 중앙 공통 정본을 모든 host가 직접 참조하는 것”이라고 정정했다. 이에 common path를 독립 정본으로 만들고 host 문서는 도구 차이만 갖게 수정했다.

### 문제 B — hookify 문서 귀속

Claude 실행 중 생기는 hookify 문서는 Codex adapter가 아니라 Claude adapter 내부에 있어야 한다는 지적을 반영했다. `.claude/hookify.require-documentation.local.md`는 Claude 배포 경로에 유지하고 공통 역할 정본과 혼합하지 않았다.

### 문제 C — common guard가 legacy approval gate를 실제로 대체하지 못함

문서에서만 “통합”이라 쓰고 legacy 파일을 삭제하면 source mutation 승인·탐색 gate가 사라질 수 있었다. legacy 함수와 테스트를 기능 단위로 재검토하고 UserPrompt/PostTool state와 readiness gate를 공통 guard에 구현한 뒤 삭제했다.

### 문제 D — trusted workflow 경로 차이

inject snapshot과 sync 소비자의 `branch_workflow.py` 경로가 달라 한쪽만 trusted로 인식할 수 있었다. inject는 bundle의 정확한 script, sync는 `.agent-policy/common/.../branch_workflow.py`만 허용하고 stale host 사본은 신뢰하지 않게 했다.

### 문제 E — `functions.exec` 누락

tool 이름을 Bash/Shell만 비교하면 현재 host의 shell alias를 통해 pre-tool 판정이 빠질 수 있었다. normalized tool name 집합에 exec 계열을 추가하고 세 host 회귀 테스트를 만들었다.

### 문제 F — preserve 테스트의 잘못된 fixture

새 테스트는 session directory를 binding하지 않은 채 곧바로 handoff 누락 문구를 기대했다. 실제 guard는 먼저 “귀속 디렉터리 없음”을 정확히 반환했다. 구현을 느슨하게 만들지 않고 테스트 환경에 `ASAN_SESSION_DIR`을 선언해 실제 운영 순서대로 handoff 검사를 수행하게 수정했다.

### 문제 G — Python compile cache가 렌더 source에 섞일 가능성

검증 중 `compileall`이 `__pycache__`와 `.pyc`를 만들 수 있다. source file selector에서 cache, `.pyc/.pyo`, `.DS_Store`를 제외하고 renderer/audit 회귀 테스트를 추가했다.

## 12. 검증 근거

| 명령 | 결과 | 확인한 범위 |
| --- | --- | --- |
| `python3 -m compileall -q lib policy tests` | PASS | Python syntax |
| targeted guard/render/branch/injection tests | 최초 1 fixture FAIL 후 보완, 재실행 PASS | 새 공통 guard와 V3 핵심 경로 |
| `python3 -m unittest discover -s tests -v` | 89 tests PASS | 전체 renderer, sync, inject, guard, log mirror, branch 회귀 |
| `bin/agent-policy audit` | central-contract PASS | 공통 registry, template, hook 단일화, 금지 문구, runtime invariant |
| `bin/agent-policy audit` | admin-ui PASS (183 managed files) | 현재 소비자 파일 무결성과 legacy audit |
| `bin/agent-policy audit` | user-ui PASS (183 managed files) | 현재 소비자 파일 무결성과 legacy audit |
| `bin/agent-policy diff --project all` | 각 add 99, change 82, stale 0, legacy 11 | 다음 sync 예상 영향 |
| `git diff --check` | PASS | whitespace·patch 형식 |

## 13. 알려진 제한과 잔여 작업

- 소비자에 새 manifest와 common/runtime 파일이 아직 배포되지 않아 diff의 `current=false`는 정상적인 배포 전 상태다.
- legacy 11개는 audit SHA가 일치하고 사용자가 `--retire-legacy`를 별도 승인한 경우에만 제거할 수 있다.
- sync 뒤 실행 중인 소비자 세션은 이전 snapshot을 계속 사용할 수 있으므로 handoff 후 재시작해야 한다.
- role boundary는 요청대로 prompt 계약이며 기계적 의미 검사 hook은 아직 없다.
- 현재 중앙 branch는 V3 구현 전에 생성돼 V3 metadata를 소급 기록하지 않았다.

## 14. 다음 담당자 인계

1. 이 중앙 변경과 commit을 검토한다.
2. 배포하려면 `bin/agent-policy diff --project all`의 add/change/legacy 범위를 다시 확인한다.
3. 별도 승인 후에만 `bin/agent-policy sync --project all`을 실행한다.
4. legacy 퇴역이 필요하면 hash mismatch 항목을 먼저 해결하고 `--retire-legacy`를 독립 승인한다.
5. 소비자 세션을 handoff하고 `--role`, `--task`, `--responsibility`, `--worktree`, `--branch`, `--session-dir`를 명시해 새 세션을 시작한다.
6. 실제 consumer smoke test에서 event payload, artifact binding과 isolated worktree 흐름을 확인한다.
