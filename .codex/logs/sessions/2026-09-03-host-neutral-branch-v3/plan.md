# 계획

## 1. 작업 식별

- 작업명: 호스트 중립 공통 정책과 Branch Contract V3 통합
- 기준일: 2026-09-03
- 작업 유형: `hybrid`
- 세션 역할: 오케스트레이션 + 통합 구현 + 검토 + 문서화
- 산출물 책임: `owner`
- Git 통합 담당자: 현재 Codex 세션
- 현재 브랜치: `task/host-neutral-policy-branch-v3`
- 기준 commit: `ae7ea3066eb4d33eb0ea7795b3538bfe2c8f7268`

## 2. 목표

현재 정책은 Claude Code, Codex, OpenCode라는 실행 호스트와 UI, Logic, 오케스트레이션이라는 작업 역할이 부분적으로 결합되어 있다. 지금의 운영 관행이 바뀌어 Claude가 Logic을 맡거나 한 호스트가 전체 기획·구현·검토를 수행할 때도 정책을 다시 복제하지 않도록 다음 구조로 재편한다.

1. 역할·workflow·산출물 의미는 `policy/common/**`에 단일 정본으로 둔다.
2. host adapter는 해당 도구의 system prompt, hook event, native agent 형식만 보유한다.
3. inject 시작 시 `--role logic|ui|orchest|review|generate`를 명시하고 선택 역할에 필요한 공통 문서만 바인딩한다.
4. OpenCode에서 사용하던 8종 산출물을 모든 owner 세션의 공통 기준으로 삼는다.
5. `portfolio-log.md`는 Claude에서 정립한 사례 중심 프롬프트 구조를 사용한다.
6. Codex legacy Python hook의 유효 기능을 공통 guard에 흡수하고 중복 파일·등록을 제거한다.
7. dirty worktree, stale guard, 축약 SHA, Git parser 우회 문제를 해결하는 Branch Contract V3를 도입한다.
8. 다른 host·session 산출물은 협업을 위해 읽을 수 있지만 현재 세션이 수정하지 못하게 한다.

## 3. 해결해야 할 실제 문제

### 3.1 호스트와 역할의 결합

- 기존 Claude 문서에는 Claude가 production UI를 구현하고 Logic Session이 기능을 통합한다는 고정 문구가 있었다.
- 기존 Codex 문서는 Logic 중심 역할을 전제로 하거나 Claude 문서를 간접 참조했다.
- host별 inject bundle에는 다른 host adapter가 포함되지 않을 수 있으므로 Claude 문서가 Codex 문서를 참조하면 독립 실행이 깨진다.
- 역할이 향후 역전되거나 한 호스트가 전 과정을 담당할 때 기존 고정 문구가 권한과 책임을 잘못 제한한다.

### 3.2 중복 hook과 서로 다른 상태

- Codex legacy hook은 승인, skill 확인, 공용 자산 탐색, Stop 산출물 검사를 수행했다.
- 중앙 공통 guard도 managed path와 산출물·명령 검사를 수행해 동일 이벤트에 두 체계가 등록됐다.
- Codex는 같은 이벤트에 일치한 hook을 모두 실행하며 어느 하나라도 deny하면 도구를 차단한다.
- 따라서 실행 순서로 상위 hook이 하위 hook을 덮는 구조는 성립하지 않는다. 기능을 한 구현으로 합치고 legacy 등록 자체를 제거해야 한다.

### 3.3 dirty worktree와 독립 작업

- `git switch -c`나 `git checkout -b`는 현재 폴더의 dirty 파일과 index를 새 branch에 그대로 데려간다.
- 기준 `sy-main`에 다른 세션의 미커밋 변경이 있으면 독립 UI 수정도 branch를 만들 수 없었다.
- 다른 세션 파일을 현재 세션이 commit·stash·restore하는 것은 소유권 침범이다.
- 기준 branch를 clean하게 만들도록 강요하는 대신, 승인된 parent commit에서 별도 worktree와 index를 만들어야 한다.

### 3.4 branch workflow와 승인 식별자

- inject의 `branch_workflow.py`가 snapshot runtime보다 소비자의 stale `.codex/.claude` guard를 먼저 읽으면 `FULL_SHA_PATTERN`이 없어 실행 중 예외가 발생했다.
- V2 proposal 식별자는 purpose, role, scope, reason, worktree 전체를 포함하지 않아 승인 후 일부 계약을 바꿔도 같은 식별자가 유지될 수 있었다.
- proposal에는 축약 SHA가 표시되지만 이후 Write/create에서는 전체 SHA를 요구해 “승인 요청 식별자 불일치”가 발생했다.
- proposal을 canonical JSON으로 고정하고 그 전체 bytes의 64자리 SHA-256만 승인 식별자로 사용해야 한다.

### 3.5 Git 명령 판정과 치명적 허용

- `git checkout -- <path>`가 branch 전환으로 오판됐다.
- `git checkout <target> && git merge <source>`는 전환 전 branch 상태로 두 번째 명령을 판정했다.
- `git -C . reset --hard`와 `git -C . push ...`는 global option 뒤 subcommand를 찾지 못하면 `None`, 즉 허용으로 끝날 수 있었다.
- 특히 push와 hard reset은 사용자의 승인 문구로 해제할 작업이 아니라, 에이전트가 필요 이유·정확한 대상·영향을 설명하고 사용자에게 실행을 양도해야 한다.

### 3.6 산출물 귀속과 shell redirect

- Bash heredoc/redirect로 만든 산출물은 구조화된 파일 경로를 hook이 받지 못해 세션 귀속이 기록되지 않았다.
- 반대로 `2>&1`, `2>/dev/null` 같은 진단용 stderr redirect를 일반 파일 쓰기로 오탐했다.
- 모든 host의 로그 경로를 scope 예외로만 처리하면 한 host가 다른 host 또는 다른 세션의 기록을 수정할 수 있었다.
- 정해진 8종과 handoff 외 문서를 어디에 둘지 규칙이 없었다.

## 4. 승인된 구현 범위

### 공통 정본

- `policy/common/AGENT_POLICY.template.md`
- `policy/common/contracts/runtime-policy.json`
- `policy/common/skills/policy/task-role-routing/**`
- `policy/common/skills/policy/git-branch-strategy/**`
- `policy/common/skills/policy/implementation-quality/**`
- `policy/common/templates/**`

### runtime과 CLI

- `policy/guards/managed_policy_guard.py`
- `policy/guards/branch_guard.py`
- `lib/agent_policy/core.py`
- `lib/agent_policy/cli.py`
- `lib/agent_policy/injection.py`
- `lib/agent_policy/role_profiles.py`
- `lib/agent_policy/log_mirror.py`

### host adapter

- `adapters/codex/**`
- `adapters/claude/**`
- `adapters/opencode/**`

### 프로젝트·감사·검증

- `projects/*.json`, `projects/legacy/*.json`
- `tests/**`
- `docs/**`
- 중앙에 아직 커밋되지 않은 수집 산출물

## 5. 명시적 제외 범위

- `bin/agent-policy sync --project all` 실행
- 소비자 프로젝트 파일의 직접 수정
- 소비자 legacy 파일의 즉시 퇴역
- 실행 중인 소비자 세션 재시작
- 원격 `git push`
- `git reset --hard`, `git clean`, `git update-ref`
- `asan-prompt-core`, 그 백업 또는 `asan-harness`를 원본으로 읽거나 복사하는 행위
- role 침범을 기계적으로 차단하는 새 hook 추가: 사용자가 이번에는 system prompt 명시만 요청함

## 6. 단계별 실행 계획

### 단계 A — 기존 의미 전수조사

1. 루트 진입 문서, host별 agent, harness, workflow, multi-agent spec, schema와 template을 목록화한다.
2. 기존 Claude 문서의 Planner, Publisher, Generator, Refactorer, Watcher, Evaluator, Harness 책임과 출력 필드를 추출한다.
3. Codex legacy Python hook의 UserPrompt, PreTool, PostTool, Stop 기능과 테스트를 공통 guard 기능표에 대응시킨다.
4. host 고정 역할 문장과 host와 무관하게 보존해야 할 운영 의미를 분리한다.
5. 누락된 역할별 schema 필드를 공통 union schema에 복구한다.

### 단계 B — 공통 문서와 role profile

1. 공통 진입 정책을 `AGENT_POLICY.template.md`로 독립시킨다.
2. `logic`, `ui`, `orchestration`, pipeline role, workflow, handoff/ownership을 references로 분리한다.
3. CLI 이름 `logic|ui|orchest|review|generate`와 canonical role을 registry에 기록한다.
4. role별 inject bundle이 필요한 공통 skill/reference와 native agent만 포함하도록 profile을 정의한다.

### 단계 C — 산출물 계약

1. owner는 `plan`, `exploration`, `implementation-log`, `grill-me-review`, `review-log`, `evaluation-log`, `final-summary`, `portfolio-log` 8종을 책임진다.
2. contributor는 `handoff.md`를 책임지고 branch 완료 권한은 갖지 않는다.
3. 다른 host·session 산출물 Read는 허용하고 Write·stage·commit은 차단한다.
4. 미분류 문서는 현재 세션의 `unknown/`, host 미상은 `.agent-policy/logs/unknown/sessions/`로 보낸다.

### 단계 D — 공통 guard 단일화

1. 세 host UserPrompt event에서 구현 승인과 proposal SHA 승인을 session state로 기록한다.
2. PostTool event에서 실제 skill read와 역할별 인접·재사용 탐색 근거를 기록한다.
3. source mutation 전 승인·skill·탐색 근거를 함께 검사한다.
4. managed path, artifact ownership, shell write, Git stage/commit, Stop 8종 검사까지 공통 guard에 합친다.
5. Codex legacy Python 파일·등록·테스트를 삭제하고 renderer audit로 재등장을 막는다.

### 단계 E — Branch Contract V3

1. branch task 계약과 session assignment를 분리한다.
2. proposal 전 필드를 canonical JSON과 SHA-256으로 고정한다.
3. dirty 기준 폴더를 변경하지 않고 저장소 밖 isolated worktree를 만든다.
4. `ACTIVE -> PRESERVED -> ACTIVE`와 `READY_TO_MERGE -> MERGED_VERIFIED -> CLOSED` 상태를 구현한다.
5. owner만 finish proposal, merge, target 검증과 close를 수행한다.
6. merge는 parent와 direct target이 같고 `--ff-only`인 경우만 허용한다.

### 단계 F — 안전성·회귀 검증

1. global option, alias, nested shell과 compound command를 포함한 Git parser 테스트를 추가한다.
2. 세 host에서 위험 명령이 승인으로 풀리지 않는지 확인한다.
3. stale consumer guard를 무시하고 inject snapshot runtime만 쓰는지 확인한다.
4. cross-host/session read/write, unknown, owner/contributor, committed diff Stop을 검증한다.
5. renderer가 세 host에 같은 template bytes를 배포하는지 검사한다.
6. 전체 unittest, 중앙 audit, 소비자 diff와 whitespace 검사를 실행한다.

## 7. 효율성·성능 검토

- 공통 registry를 Python과 문서가 공유해 host별 상수 복제를 줄인다.
- hook 상태는 session별 작은 JSON 파일로 저장하고 관련 event에서만 검사한다.
- role별 inject는 필요한 skill/reference만 포함해 context 사용량을 줄인다.
- Git 조회는 mutation·Stop·branch workflow 시점으로 제한한다.
- 새 외부 Python 패키지나 JavaScript 의존성은 추가하지 않는다.
- React 애플리케이션 runtime에는 영향을 주지 않으며 변경은 개발 도구와 agent 정책 레이어에 한정된다.

## 8. 장기 영향

- host 교체나 역할 역전 시 공통 역할 문서를 다시 복제하지 않아도 된다.
- 새 host는 공통 runtime과 문서를 호출하는 얇은 adapter만 추가하면 된다.
- branch와 session 책임을 분리해 같은 task에서 여러 host가 순차 협업할 수 있다.
- dirty 기준 worktree를 훼손하지 않고 독립 작업을 시작할 수 있다.
- proposal과 finish 계약이 불변이므로 승인한 내용과 실제 실행을 사후 추적할 수 있다.

## 9. 위험과 완화

| 위험 | 영향 | 완화 |
| --- | --- | --- |
| host 문서 삭제 중 의미 유실 | 기존 agent 행동 회귀 | 삭제 전후 문서·schema 필드 전수 대응표와 audit 작성 |
| common guard 비대화 | 변경 영향 범위 확대 | mode별 함수 분리, host adapter test, 전체 회귀 테스트 |
| OpenCode event payload 차이 | 승인·탐색 상태 누락 | session id 변형 지원과 smoke test 추가 |
| dirty parent의 미커밋 내용 누락 | child가 필요한 선행 변경 없이 생성 | parent worktree dirty이면 child 생성 차단 |
| finish 후 target 변경 | 잘못된 commit 검증·close | source/target full HEAD를 proposal에 고정하고 각 단계 재검증 |
| consumer legacy 공존 | 이중 hook 가능성 | sync diff와 고정 SHA 확인 후 별도 `--retire-legacy` 승인 |

## 10. 검증 기준

- `python3 -m unittest discover -s tests -v`: 전체 회귀 PASS
- `bin/agent-policy audit`: central-contract, admin-ui, user-ui PASS
- `bin/agent-policy diff --project all`: 배포 예정 변경과 legacy를 정확히 제시
- `git diff --check`: whitespace 오류 없음
- renderer 결과에 legacy Codex Python hook이 없음
- 세 host template bytes가 공통 template과 동일함
- `git -C . reset --hard`, `git -C . push ...`가 모든 host에서 사용자 전용으로 차단됨
- proposal SHA가 purpose, role, scope, reason, worktree까지 포함함

## 11. 승인 기록

- 사용자가 공통 진입 문서를 Codex에 의존시키지 않고 모든 host가 직접 참조하도록 요구했다.
- 사용자가 inject 실행 시 `--role logic/ui/orchest/review/generate`를 사용하도록 요구했다.
- 사용자가 OpenCode 8종과 Claude portfolio 구조를 결합하도록 요구했다.
- 사용자가 다른 host·session 산출물은 read-only, 미분류 문서는 `unknown/`으로 처리하도록 요구했다.
- 사용자가 push와 hard reset은 승인 요청이 아니라 사용자에게 실행을 양도하도록 요구했다.
- 사용자가 전수조사 뒤 Branch Contract V3를 구현하고 커밋하도록 반복 승인했다.

승인 상태: `approved`
