# 최종 요약

## 1. 작업 결과

중앙 정책을 특정 host 중심 구조에서 host-neutral 공통 계약 구조로 전환하고, 역할 선택형 inject와 Branch Contract V3를 구현했다. 이번 중앙 변경으로 Claude Code, Codex, OpenCode는 동일한 역할·workflow·산출물·브랜치 의미를 공유하되, 각 host의 system prompt·hook/plugin·native agent 형식만 adapter에 남는다.

핵심 결과는 다음과 같다.

1. Claude가 Codex 문서를 경유하지 않고 모든 host가 `.agent-policy/common/**`를 직접 참조한다.
2. 역할은 host/model과 독립된 `--role logic|ui|orchest|review|generate`로 선택한다.
3. owner는 OpenCode 기준 8종 산출물을 작성하고 portfolio는 Claude 사례형 프롬프트를 따른다.
4. contributor는 `handoff.md`로 부분 결과를 넘기며 branch 완료는 owner가 수행한다.
5. Codex legacy Python hook의 승인·탐색·mutation·Stop 기능을 공통 guard로 흡수한 뒤 legacy 파일과 등록을 제거했다.
6. 다른 host·session 산출물은 읽을 수 있지만 수정·stage·commit할 수 없다.
7. 정의되지 않은 문서는 current session의 `unknown/`, host 미상 문서는 unknown host root에 둔다.
8. branch 생성과 완료는 canonical proposal 파일과 전체 64자리 SHA-256 승인으로 고정한다.
9. dirty 기준 worktree를 정리하지 않고 별도 isolated worktree에서 독립 task를 시작할 수 있다.
10. `git -C . reset --hard`와 모든 push는 승인으로 해제하지 않고 사용자에게 실행을 양도한다.

## 2. 변경 전 문제 상황

### 역할·문서 문제

- Claude 문서는 production UI, Codex/OpenCode는 Logic이라는 현재 관행을 장기 정책처럼 표현했다.
- 일부 Claude 진입 흐름이 Codex 쪽 공통 문서를 참고해, Claude adapter만 inject되는 경우 필요한 내용을 찾지 못할 수 있었다.
- 같은 Planner/Watcher/Evaluator 의미가 host별 harness, workflow, multi-agent spec과 template에 반복돼 drift 가능성이 컸다.
- host 고정 문장을 제거하는 과정에서 역할별 세부 출력 필드까지 삭제될 위험이 있었다.

### hook 문제

- Codex legacy Python hook과 중앙 common guard가 동일 이벤트에서 중복 실행됐다.
- Codex에서는 matching hook이 모두 실행되고 deny 하나가 전체를 차단하므로 우선순위로 중복을 해결할 수 없었다.
- common guard만 남기기 전에 legacy 기능을 실제로 흡수하지 않으면 구현 승인·skill·재사용 탐색 gate가 사라질 수 있었다.

### branch·Git 문제

- dirty sy-main에서 새 task branch를 만들면 다른 세션의 미커밋 파일이 따라오므로 guard가 branch 생성을 막았다.
- 기존 안내는 먼저 dirty를 commit/stash하라는 방향이어서 독립 작업까지 타 세션 소유권에 종속됐다.
- inject branch workflow가 snapshot보다 stale consumer guard를 골라 `FULL_SHA_PATTERN` AttributeError로 죽었다.
- proposal의 축약 SHA와 이후 전체 SHA가 달라 승인 식별자 불일치가 발생했다.
- `git checkout -- path`와 compound checkout+merge를 정확히 판정하지 못했다.
- `git -C . reset --hard`, `git -C . push`는 global option 뒤 subcommand를 놓치면 허용될 수 있었다.

### 산출물 문제

- Bash heredoc/redirect 산출물은 tool payload에 구조화된 파일 경로가 없어 session 귀속을 남기기 어려웠다.
- 모든 host 로그를 scope 예외로만 두면 다른 host·session 기록까지 수정할 수 있었다.
- 미분류 문서 위치와 host를 알 수 없는 runtime의 경로가 명확하지 않았다.
- Stop이 dirty 파일만 보면 이미 commit된 애플리케이션 변경을 산출물 없이 놓칠 수 있었다.

## 3. 해결 구조

### 3.1 공통 의미 계층

`policy/common/AGENT_POLICY.template.md`를 단일 의미 정본으로 만들었다. 역할별 세부 책임은 `task-role-routing` references, branch lifecycle은 `git-branch-strategy`, 산출물 형식은 `templates`, runtime 상수는 `contracts/runtime-policy.json`에 둔다.

renderer는 공통 정본을 소비자 `AGENTS.md`와 `.agent-policy/common/AGENT_POLICY.md`에 동일하게 제공한다. host adapter는 common 경로를 직접 참조하며 다른 host adapter에 의존하지 않는다.

### 3.2 role-aware inject

`bin/agent-policy start --mode inject`는 `--role`을 필수로 받는다. `role_profiles.py`가 role별로 필요한 references, skill과 native agents를 선택한다. `--host`, `--model`, `--role`은 서로 독립된 인자다.

외부 worktree를 지정하면 같은 Git common directory인지, worktree root인지, 현재 branch가 `--branch`·`--task`와 일치하는지 검사한다. 실패 시 기본 프로젝트 폴더로 조용히 fallback하지 않는다.

### 3.3 공통 산출물 계약

owner의 필수 8종:

- `plan.md`
- `exploration.md`
- `implementation-log.md`
- `grill-me-review.md`
- `review-log.md`
- `evaluation-log.md`
- `final-summary.md`
- `portfolio-log.md`

contributor는 `handoff.md`를 작성한다. 한 작업자가 여러 역할을 맡아도 역할별로 8종을 복제하지 않고 task 단위 한 세트를 작성한다. 공통 template은 세 host native template 경로에 동일한 bytes로 렌더된다.

### 3.4 공통 guard

- UserPrompt: 구현 승인, command 승인, proposal SHA 승인 기록
- PostTool: 실제 skill/read/search evidence와 proposal output 기록
- PreTool: managed path, artifact ownership, branch scope, readiness, operation gate
- Stop: parent 이후 committed diff와 dirty diff를 확인하고 owner 8종 또는 contributor handoff 검증

Codex legacy Python 파일과 등록은 제거했다. common guard가 legacy의 기능을 실제로 포함하는지 중앙 audit와 회귀 테스트로 고정했다.

### 3.5 Branch Contract V3

branch task 계약은 목적, parent full SHA, direct merge target, role, scope, Git integrator, reason과 선택 worktree를 고정한다. session assignment는 host, current role, owner/contributor와 session directory를 별도로 기록한다.

create lifecycle:

```text
role·구현 계획 승인
  -> branch proposal 생성
  -> canonical JSON과 64자리 SHA 표시
  -> 사용자의 별도 SHA 승인
  -> create가 file/bytes/SHA/parent HEAD 재검증
  -> isolated task worktree ACTIVE
```

finish lifecycle:

```text
구현 + 검증 + 8종 + commit
  -> finish proposal 생성
  -> source/target full HEAD + 검증 argv + cleanup SHA 승인
  -> finish: ff-only merge
  -> verify: target에서 등록 argv 실행
  -> close: ancestry·clean 재검증 후 CLOSED
```

미완료 task는 handoff 후 PRESERVED로 고정하고 같은 worktree의 새 assignment가 resume한다. PRESERVED 상태에서 다른 독립 작업을 병행하려면 별도 worktree·session을 사용한다. CLOSED 이후에는 같은 session에서 다음 task를 시작할 수 있다.

### 3.6 Git 안전 경계

Git global option 뒤 실제 subcommand를 파싱하고 해석 실패는 fail-closed한다. nested shell과 alias 문자열도 위험 명령을 다시 검사한다.

절대 사용자 전용:

- `git push`
- `git reset --hard`
- `git clean`
- `git update-ref`

이 명령은 “승인을 요청하면 실행 가능”한 범주가 아니다. 에이전트는 필요한 이유, 정확한 대상과 영향을 사용자에게 설명하고 직접 실행하도록 양도한다.

파일 복원은 `git restore ... -- <path>`를 사용하고, branch 전환과 merge는 각각 별도 명령으로 실행한다. raw branch create/force/orphan, raw merge, unsafe add/commit pathspec과 자동 계보 변경 명령도 차단한다.

## 4. 구현 과정에서 해결한 추가 문제

1. **공통화 방향 정정**: Claude 문서를 Codex와 분리하는 데서 끝내지 않고, Codex와 무관한 중앙 common을 모든 host가 직접 참조하도록 수정했다.
2. **hookify 귀속 정정**: Claude 실행 중 생성되는 hookify 문서를 Claude adapter 아래에 유지했다.
3. **Claude schema 복구**: 삭제 예정 template에서 역할별 세부 필드를 다시 추출해 common union schema에 복원했다.
4. **`functions.exec` 정규화**: Bash/Shell 외 exec alias도 공통 guard가 판정하도록 했다.
5. **redirect 오탐 제거**: `2>&1`, `/dev/null`, 외부 임시 진단 경로와 실제 저장소 쓰기를 구분했다.
6. **trusted workflow 구분**: inject snapshot script와 sync common script만 신뢰하고 stale host 사본을 배제했다.
7. **contributor 완료 제한**: contributor handoff만으로 finish/verify/close하지 못하게 owner-only로 강화했다.
8. **preserve 문서 조건**: owner/contributor와 무관하게 PRESERVED 전에 현재 session `handoff.md`를 요구했다.
9. **Python cache 제외**: `compileall` 산출물이 renderer와 source digest에 섞이지 않게 했다.
10. **테스트 fixture 보완**: session assignment 없는 preserve 테스트를 실제 start 계약에 맞게 수정했다.

## 5. 변경 파일 영역

- 공통 정책·template·contract: `policy/common/**`
- 기계적 차단: `policy/guards/managed_policy_guard.py`, `policy/guards/branch_guard.py`
- branch workflow: `policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py`
- renderer·audit: `lib/agent_policy/core.py`
- role-aware inject: `lib/agent_policy/injection.py`, `lib/agent_policy/role_profiles.py`
- launcher: `lib/agent_policy/cli.py`
- 로그 수집: `lib/agent_policy/log_mirror.py`
- host adapter: `adapters/{codex,claude,opencode}/**`
- 프로젝트 metadata: `projects/**`
- 회귀 테스트: `tests/**`
- 설계·전수조사 기록: `docs/branch-worktree-session-strategy.md`, `docs/host-neutral-commonization-audit.md`

## 6. 검증 결과

### Python 전체 회귀

```text
python3 -m unittest discover -s tests -v
Ran 89 tests in 76.840s
OK
```

### 중앙·소비자 audit

```text
[central-contract] PASS
[admin-ui] PASS (183 managed files)
[user-ui] PASS (183 managed files)
```

### 소비자 배포 예상 diff

```text
admin-ui: current=false, add=99, change=82, stale=0, legacy=11
user-ui:  current=false, add=99, change=82, stale=0, legacy=11
```

### patch 검사

```text
git diff --check
PASS
```

## 7. 재사용한 자산

- 기존 project renderer와 manifest/digest 체계
- 기존 managed policy guard의 path 보호 기반
- 기존 project JSON의 base branch와 validation command
- 기존 host native agent 포맷
- OpenCode의 8종 산출물 이름
- Claude의 portfolio 사례 프롬프트와 역할별 output schema 의미
- V2의 parent, scope, integrator 기본 개념

## 8. 제외하거나 제거한 자산

- host별 중복 harness/workflow/multi-agent-spec 정본
- host별 중복 template 정본
- Codex legacy Python hook, bootstrap hash와 자체 hook test
- 특정 host를 UI/Logic 전담으로 고정하는 문구
- stale consumer host branch guard fallback
- branch 단위 `artifact-mode`를 최종 responsibility로 사용하는 방식

## 9. 알려진 제한

- 소비자에는 아직 새 정책이 적용되지 않았다.
- 각 소비자 legacy 11개는 별도 retire 승인이 필요하다.
- role 침범은 현재 prompt 계약이며 별도 semantic hook은 없다.
- host 제품의 event payload가 바뀌면 adapter를 갱신해야 한다.
- proposal과 CLOSED/PRESERVED state가 누적될 수 있어 향후 읽기 전용 status 도구가 유용할 수 있다.
- 현재 중앙 branch는 V3 이전 생성 branch라 V3 metadata를 소급 적용하지 않았다.

## 10. 다음 단계

1. 중앙 commit을 검토한다.
2. 배포 전에 `bin/agent-policy diff --project all`을 다시 확인한다.
3. 사용자가 별도 승인한 경우에만 sync한다.
4. 한 소비자에서 host/role별 inject smoke test를 수행한다.
5. 새 common guard가 실제 session에서 동작함을 확인한 뒤 legacy retire를 별도 승인한다.
6. 실행 중인 소비자 session은 handoff하고 새 role/session-dir로 재시작한다.

## 11. 최종 상태

- 중앙 구현: 완료
- 중앙 전체 테스트: 통과
- 중앙·소비자 audit: 통과
- 8종 현재 세션 산출물: 작성 완료
- 중앙 commit: 이 산출물과 함께 수행 예정
- 소비자 sync: 미수행, 별도 승인 필요
- 원격 push: 미수행, 사용자 전용
