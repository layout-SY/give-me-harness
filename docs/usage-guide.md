# asan-agent-policy 사용 가이드

이 문서는 중앙 정책으로 Codex, Claude Code, OpenCode 세션을 시작하고, 승인된 작업 branch와 worktree에서 구현한 뒤 검증·병합·종료하는 실제 사용 절차를 설명한다.

정책의 설계 근거와 상세 상태 전이는 [브랜치·worktree·세션 운영 전략 V3](branch-worktree-session-strategy.md), 역할별 세부 책임은 중앙 bundle에 렌더되는 task-role-routing과 git-branch-strategy 스킬을 정본으로 삼는다.

## 1. 가장 먼저 알아둘 원칙

- host는 실행 환경이고 role은 현재 세션의 책임이다. Codex, Claude Code, OpenCode 중 어느 host도 Logic, UI 또는 오케스트레이션을 고정 소유하지 않는다.
- 한 세션에는 assignment 권한 root 하나와 한 시점에 하나의 작업 branch 초점만 둔다.
- 권한 root나 그 ACTIVE V3 자손에서 승인 생성한 child는 `asan-parent` 계보를 따라 같은 세션이 전이적으로 작업할 수 있다. 이름이 비슷하다는 이유만으로 권한이 생기지는 않는다.
- parent-root 세션은 root와 승인된 자손 사이에서 초점을 바꿀 수 있지만 child-root 세션은 ancestor·형제 branch를 수정할 수 없다. 계보 밖 독립 task는 이전 권한 root가 검증·병합까지 끝나 CLOSED 상태여야 같은 세션에서 시작할 수 있다.
- 기준 branch가 dirty이면 기존 변경을 commit, stash, reset 또는 restore하지 않는다. 승인 계약에 격리 worktree를 포함해 별도 index와 작업 폴더를 만든다.
- 격리 worktree를 만들었다는 이유만으로 새 세션을 열 필요는 없다. 현재 assignment 권한 계보 안의 branch라면 기존 세션이 그 worktree를 도구 workdir 또는 git -C 대상으로 사용해 계속할 수 있다.
- 미완료 task를 PRESERVED로 남겨 놓고 계보 밖 독립 task를 병행하거나, host·role·담당자를 인계할 때는 별도 worktree와 세션을 사용한다.
- 소비자 저장소에는 세션 로그와 허용된 개인 설정 외의 정책 파일을 두지 않는다. 중앙 원본을 변경한 뒤 중앙 launcher로 새 세션을 시작한다.
- Git push, git reset --hard, git clean, git update-ref는 승인으로 해제되지 않는 사용자 전용 명령이다.

## 2. 저장소와 용어

### 중앙 정책 저장소

~~~text
/Users/okand/SynologyDrive/asan-agent-policy
~~~

중앙 원본의 주요 위치는 다음과 같다.

| 경로               | 용도                                    |
| ------------------ | --------------------------------------- |
| policy/common/     | 모든 host가 공유하는 정책과 skill 정본  |
| policy/guards/     | 파일, 명령, branch, 산출물 소유권 guard |
| adapters/codex/    | Codex 형식 adapter                      |
| adapters/claude/   | Claude Code 형식 adapter                |
| adapters/opencode/ | OpenCode 형식 adapter                   |
| projects/\*.json   | 소비자 경로, 기준 branch와 검증 명령    |
| lib/agent_policy/  | 렌더링과 inject 실행 구현               |
| bin/agent-policy   | 중앙 운영 CLI                           |
| build/             | source digest별 inject 번들             |
| state/             | inject host의 지속 상태                 |
| logs/projects/     | 소비자 세션 산출물의 중앙 Git 사본      |

### 등록된 소비자

| project 인자 | 소비자 저장소           | 기준 branch |
| ------------ | ----------------------- | ----------- |
| user-ui      | asan-metaverse-user-ui  | sy-main     |
| admin-ui     | asan-metaverse-admin-ui | sy-main     |

### 핵심 용어

| 용어               | 의미                                                                        |
| ------------------ | --------------------------------------------------------------------------- |
| primary checkout   | projects/\*.json에 등록된 소비자 기본 폴더                                  |
| task branch        | `task/ascii-kebab-summary` 형식의 승인된 작업 branch                        |
| worktree           | 같은 Git object를 공유하면서 작업 폴더와 index를 분리한 공간                |
| branch task 계약   | parent, 전체 parent SHA, 역할, scope, integrator, worktree 등을 고정한 계약 |
| session assignment | 현재 세션의 role, task, 산출물 위치와 owner/contributor 책임                |
| Git integrator     | 해당 task에서 index, commit과 완료 workflow를 담당하는 유일한 주체          |
| ACTIVE             | 현재 구현 가능한 task                                                       |
| PRESERVED          | handoff 후 미완료 상태로 보존된 task                                        |
| CLOSED             | merge, 사후 검증과 종료 기록이 모두 완료된 task                             |

## 3. 중앙 inject 실행

inject는 선택한 host와 role에 필요한 정책만 중앙 build 디렉터리의 불변 digest 번들로 만들고 세션에 직접 주입한다. 소비자 정책 파일이나 배포 manifest는 만들지 않는다.

적합한 경우:

- 중앙 정책 최신본으로 작업할 때
- host와 role별로 필요한 문서만 바인딩할 때
- primary checkout 또는 별도 worktree에서 동일한 중앙 계약으로 작업할 때

주의 사항:

- inject는 --role이 필수다.
- 선택된 worktree에 소비자 정책·프롬프트·훅 사본이 남아 있으면 시작을 중단하고 정확한 경로를 출력한다.
- 실행 중인 세션은 기존 번들을 계속 사용한다. 중앙 정책이 바뀌면 기존 세션을 단순 복원하지 말고 중앙 launcher를 다시 실행해야 한다.
- `--mode inject`는 기존 명령 호환을 위해 허용하며 생략할 수 있다. 다른 mode는 지원하지 않는다.

### Claude UI의 TalkToFigma 기본 MCP

`user-ui`와 `admin-ui`에서 `--host claude --role ui`로 새 세션을 시작하면 중앙 번들에 TalkToFigma 설정을 생성하고 `--mcp-config <bundle>/claude-mcp.json`으로 전달한다. 기본 정의는 `adapters/claude/mcp.defaults.json` 하나로 관리한다. 다른 프로젝트·host·role에는 이 기본 MCP를 자동 주입하지 않는다.

launcher는 `bunx`를 PATH에서 찾고, 없으면 `~/.bun/bin/bunx`를 확인한다. 둘 다 실행할 수 없으면 설치·경로 확인 메시지와 함께 세션 시작을 중단한다. 확인한 절대경로와 `cursor-talk-to-figma-mcp@latest` 실행 인자를 번들 digest 및 manifest에 반영한다. `@latest`는 실행 시 패키지 해석에 따르므로 MCP 패키지 자체의 버전까지 고정하는 계약은 아니다.

`--setting-sources user`는 유지한다. `~/.claude.json`이나 소비자 `.mcp.json`을 수정하지 않으며 전역 MCP 재등록이 필요하지 않다. Claude는 `--mcp-config`로 세션별 JSON 설정을 지원한다([공식 CLI 문서](https://code.claude.com/docs/en/cli-reference)). 개인 MCP를 전부 배제하는 `--strict-mcp-config`는 추가하지 않는다.

적용 확인:

1. `bin/agent-policy start --project user-ui --host claude --role ui --print-only`로 새 실행 인자에 `--mcp-config`가 있는지 확인한다. admin-ui도 같은 형식이다.
2. 기존 작업은 handoff를 남긴 뒤 중앙 launcher로 새 inject 세션을 시작한다. 기존 `--resume-assignment`는 원래 번들과 MCP 설정을 유지한다.
3. 새 Claude 세션의 `/mcp`에서 TalkToFigma 연결과 도구를 확인한다.
4. 로컬 WebSocket 서버와 Figma 플러그인의 실행 상태를 확인하고 현재 채널에 참가한다. 채널 ID는 세션별 값으로 전달하며 중앙 기본 설정에 저장하지 않는다.

회귀 검증은 `tests/test_injection.py`에 포함한다. 설치된 Claude CLI의 실제 MCP 연결·도구 탐색은 `python3 tests/smoke_claude_mcp.py`로 검증한다. 이 검사는 임시 개인 설정과 stdio MCP fixture를 사용하며 모델 요청이나 실제 Figma 작업은 수행하지 않는다.

## 4. role과 산출물 책임 선택

inject에서 사용할 수 있는 role은 다음과 같다.

| role     | 주요 책임                                                          |
| -------- | ------------------------------------------------------------------ |
| logic    | API, DTO, parser, validator, hook, util, store, 상태와 데이터 흐름 |
| ui       | 화면 구조, JSX/TSX, CSS, 자산, 접근성, 반응형과 시각적 상태        |
| orchest  | 조사, 작업 분류, 계획, 역할·소유권과 승인 게이트                   |
| review   | 구현 변경 없는 검토와 판정                                         |
| generate | 승인된 handoff와 branch scope를 기반으로 한 구현                   |

role은 host와 독립적이다. 예를 들어 Claude Code를 logic으로, Codex를 ui로, OpenCode를 orchest로 실행할 수 있다.

산출물 책임은 --responsibility로 선택한다.

| 값          | 책임                                                |
| ----------- | --------------------------------------------------- |
| owner       | 필수 산출물 8종, 완료 proposal, merge·verify·close  |
| contributor | 부분 결과와 handoff.md, Git 완료 workflow 수행 불가 |

role과 responsibility도 서로 다른 개념이다. UI role 세션이 owner일 수도 있고 contributor일 수도 있다.

## 5. 세션 시작

중앙 CLI 명령은 다음 저장소에서 실행한다.

### 소비처 작업 세션 실행 명령 예시

`user-ui`와 `admin-ui`에서 작업할 때는 소비자 저장소에서 host를 직접 실행하지 않고 중앙 저장소의 launcher를 사용한다. launcher가 `projects/*.json`에 등록된 소비자 경로를 세션 cwd로 설정하고 선택한 정책을 적용한다.

먼저 중앙 저장소로 이동한다.

~~~sh
cd /Users/okand/SynologyDrive/asan-agent-policy
~~~

#### inject 세션

중앙 최신 정책으로 작업하려면 책임에 맞는 `--role`을 지정한다. 아래 조합은 실행 형식의 예시이며 host와 role은 서로 독립적이다.

user-ui Logic 작업을 Codex로 실행:

~~~sh
bin/agent-policy start --project user-ui --host codex --mode inject --role logic --responsibility owner
~~~

admin-ui UI 작업을 Claude Code로 실행:

~~~sh
bin/agent-policy start --project admin-ui --host claude --mode inject --role ui --responsibility owner
~~~

user-ui 조사·계획 작업을 OpenCode로 실행:

~~~sh
bin/agent-policy start --project user-ui --host opencode --mode inject --role orchest --responsibility owner
~~~

admin-ui를 변경하지 않고 검토하는 Codex 세션:

~~~sh
bin/agent-policy start --project admin-ui --host codex --mode inject --role review --responsibility owner
~~~

승인된 handoff와 branch scope를 구현하는 OpenCode 세션:

~~~sh
bin/agent-policy start --project admin-ui --host opencode --mode inject --role generate --responsibility owner
~~~

부분 결과만 만들고 `handoff.md`로 넘길 세션은 `contributor`로 실행한다.

~~~sh
bin/agent-policy start --project admin-ui --host claude --mode inject --role ui --responsibility contributor
~~~

#### 실행 전 확인

host를 열지 않고 소비자 cwd, bundle, 환경 변수와 최종 실행 명령만 확인하려면 `--print-only`를 붙인다.

~~~sh
bin/agent-policy start --project admin-ui --host codex --mode inject --role ui --responsibility owner --print-only
~~~

출력이 올바르면 같은 명령에서 `--print-only`만 제거해 실제 세션을 시작한다.

inject 출력의 hook 경로는 다음처럼 중앙 build 번들 아래의 절대 경로여야 한다.

~~~text
.../build/<project>/<host>-<role>-<digest>/policy/.agent-policy/runtime/managed_policy_guard.py
~~~

#### 기존 task worktree에서 재시작

기존 admin-ui task worktree에서 Claude Code UI owner 세션을 다시 여는 예시다. task별 경로와 이름은 실제 계약값으로 바꾼다.

~~~sh
bin/agent-policy start \
  --project admin-ui \
  --host claude \
  --mode inject \
  --role ui \
  --responsibility owner \
  --worktree /Users/okand/Worktrees/admin-ui-fix-loading-spinner \
  --branch task/fix-loading-spinner-layout \
  --task task/fix-loading-spinner-layout \
  --session-dir .claude/logs/sessions/2026-09-04-fix-loading-spinner
~~~

명령은 한 줄로 작성해도 되고 줄 끝 `\`로 나눠도 된다. 기본 model을 사용하면 `--model`을 생략할 수 있다.

launcher는 다음을 확인한다.

- worktree 경로가 실제 Git worktree 루트인지
- 등록된 소비자와 같은 Git 저장소인지
- 현재 branch가 --branch 및 --task와 일치하는지
- --session-dir가 선택 host의 산출물 경로 형식인지

조건이 맞으면 launcher가 직접 해당 worktree를 세션 cwd로 사용한다. 사용자가 먼저 worktree로 cd할 필요는 없다.

primary checkout과 외부 worktree 모두 중앙 launcher의 `--worktree` 선택을 기준으로 한다. launcher는 실제 선택 위치를 검사하고 중앙 bundle의 절대 runtime 경로를 사용하며, 소비자 설정이나 primary checkout의 정책 파일로 fallback하지 않는다.

## 6. 새 요청을 받았을 때

### 읽기 전용 조사

설명, 진단, 리뷰처럼 저장소를 변경하지 않는 요청은 새 branch를 만들지 않고 진행할 수 있다.

### 변경 요청

구현 전에는 다음 두 종류의 승인이 필요하다.

1. 역할·구현 계획 승인
2. immutable branch proposal 승인

역할·구현 계획 승인에는 역할, 수정 범위, 조사한 재사용 후보, 구현 전략, 검증 방법과 예상 영향을 포함한다.

branch 승인은 계획 승인과 별도다. branch_workflow.py가 생성한 proposal 파일 경로와 64자리 SHA-256 전체값을 사용자에게 제시하고 독립된 승인을 받아야 한다.

## 7. clean sy-main에서 task 시작

현재 sy-main worktree가 clean하고 다른 작업이 사용 중이지 않으면 별도 worktree 없이 task branch를 만들 수 있다.

먼저 현재 상태를 확인한다.

~~~sh
git status --short --branch
git worktree list
~~~

system prompt에 바인딩된 중앙 snapshot 내부 `branch_workflow.py`의 절대 경로를 사용한다.

~~~text
.agent-policy/common/skills/policy/git-branch-strategy/scripts/branch_workflow.py
~~~

이하 branch_workflow.py 명령은 중앙 정책 저장소가 아니라 해당 소비자 primary checkout 또는 계약에 지정된 task worktree를 실행 cwd로 사용한다. host 도구의 workdir를 명시하면 사용자가 직접 cd할 필요가 없다.

proposal 예시:

~~~sh
python3 <absolute-branch-workflow.py> proposal \
  --branch task/add-comment-favorite-icons \
  --purpose "댓글 좋아요 글리프를 공통 SVG 아이콘으로 교체" \
  --parent sy-main \
  --role ui \
  --git-integrator claude \
  --scope src/shared/assets/icons \
  --scope src/features/citizen-participation \
  --scope DESIGN.md \
  --reason "sy-main이 clean이고 기존 미병합 작업과 경로가 겹치지 않음"
~~~

proposal 출력에서 다음 두 값을 그대로 사용한다.

- proposal JSON의 절대 경로
- 64자리 전체 SHA-256

축약 SHA를 사용하면 승인 요청 식별자가 달라지므로 차단된다.

사용자가 해당 proposal을 독립된 메시지로 승인한 뒤 create를 실행한다.

~~~sh
python3 <absolute-branch-workflow.py> create \
  --proposal-file <printed-absolute-json-path> \
  --proposal-sha256 <printed-64-character-sha256>
~~~

create는 proposal bytes, SHA-256, parent 전체 HEAD, branch, role, scope, integrator와 worktree 계약을 다시 검증하고 ACTIVE metadata를 기록한다.

### 작업 중 scope 변경

작업 중 새 경로가 필요하면 현재 scope를 raw `git config`로 수정하지 않는다. 변경 후 유지할 전체 scope를 새 canonical 계약으로 제안한다.

~~~sh
python3 <absolute-branch-workflow.py> scope-proposal \
  --scope src/existing \
  --scope src/new-path
~~~

출력된 proposal 파일과 64자리 SHA-256을 별도 승인받은 뒤 적용한다.

~~~sh
python3 <absolute-branch-workflow.py> update-scope \
  --proposal-file <printed-absolute-json-path> \
  --proposal-sha256 <printed-64-character-sha256>
~~~

`update-scope`는 scopes 이외의 기존 V3 필드가 동일한지 검증하고, 새 전체 scope가 현재 dirty 경로를 승인하지 못하면 원래 metadata로 복원한다.

## 8. dirty sy-main에서 격리 worktree 시작

sy-main에 다른 세션의 미커밋 변경이 있으면 다음 작업을 하지 않는다.

- 기존 변경을 임의 commit
- stash
- reset
- restore
- dirty 변경을 새 task branch에 그대로 데려가기

대신 저장소 바깥의 새 worktree 경로를 proposal에 포함한다.

~~~sh
python3 <absolute-branch-workflow.py> proposal \
  --branch task/fix-loading-spinner-layout \
  --purpose "공통 Loading spinner의 크기와 정렬 오류 수정" \
  --parent sy-main \
  --role ui \
  --git-integrator claude \
  --scope src/shared/ui/loading \
  --scope src/shared/assets/css/_default.css \
  --reason "primary sy-main에 다른 작업의 미커밋 변경이 있어 index와 working tree를 격리해야 함" \
  --worktree /absolute/path/outside-primary/admin-ui-spinner
~~~

승인 후 동일한 proposal 파일과 전체 SHA-256으로 create한다. branch_workflow.py가 승인된 branch와 worktree를 함께 만든다. raw git worktree add 또는 git checkout -b로 우회 생성하지 않는다.

### 기존 세션에서 계속하는 방법

격리 worktree를 만들었더라도 그 branch가 현재 session assignment의 권한 root 또는 승인된 V3 자손이라면 새 세션을 만들 필요가 없다.

- 파일 도구에는 격리 worktree의 절대 경로를 전달한다.
- shell 명령에는 도구의 workdir를 격리 worktree로 지정하거나 `git -C WORKTREE_PATH`를 사용한다.
- guard는 세션 시작 cwd가 아니라 실제 변경 대상 worktree의 branch, metadata와 scope를 확인한다.

허용되는 방향:

~~~sh
git -C /absolute/path/to/admin-ui-spinner add -- src/shared/ui/loading/loading.tsx
~~~

차단되는 방향:

~~~sh
git -C /absolute/path/to/primary-sy-main add -- src/shared/ui/loading/loading.tsx
~~~

task worktree에서 primary sy-main의 index를 변경하는 것은 현재 cwd와 관계없이 차단된다. child-root로 시작한 세션이 parent worktree를 수정하는 것도 같은 이유로 차단된다.

## 9. 같은 세션에서 여러 task 수행

### 같은 assignment 계보의 child 작업

세션 레코드의 `task`는 권한 root로 유지되고 `branch`만 현재 초점으로 갱신된다. 예를 들어 `task/meeting-reserve-ui` assignment에서 승인 생성한 `task/reserve-option-lazy-load`는 새 세션 없이 같은 산출물 디렉터리와 책임으로 작업할 수 있다. child에서 다시 생성한 grandchild도 `asan-parent` 계보가 유효하면 같은 권한에 포함된다.

- child 생성 parent는 ACTIVE여야 하고 commit되지 않은 변경이 없어야 한다.
- child의 scope, role, Git integrator, 상태와 worktree 계약을 그대로 적용한다.
- 한 파일/Git mutation은 한 branch만 대상으로 한다.
- parent assignment는 child 완료 후 parent로 돌아올 수 있으며 merge는 leaf부터 `child -> parent -> sy-main` 순서로 수행한다.
- child 자체를 권한 root로 시작한 세션에는 parent나 형제 권한이 없다.

### 계보 밖의 독립 task

하나의 세션은 독립 task를 순차 처리할 수 있다. 이 경우 이전 assignment 권한 root가 CLOSED여야 한다.

### 이전 task가 CLOSED인 경우

같은 세션에서 다음 task로 이동할 수 있다.

1. 이전 task가 merge·사후 검증·close까지 완료됐는지 확인
2. 다음 task의 새 proposal 승인 및 create
3. 다음 task용 새 산출물 디렉터리를 구조화된 Write 도구로 최초 작성
4. 이후 source와 Git mutation을 새 task에 귀속

이때 새 세션이나 새 worktree가 항상 필요한 것은 아니다. 기준 worktree가 clean하고 다른 작업과 충돌하지 않으면 재사용할 수 있다.

### 이전 권한 root가 ACTIVE인 경우

같은 승인 계보의 root·자손 초점 전환은 가능하지만, 계보 밖의 독립 task로 전환할 수 없다. 먼저 현재 root 작업군을 완료하거나 PRESERVED로 전환해야 한다.

### 이전 task가 PRESERVED인 경우

현재 task의 handoff.md를 작성하고 preserve한다.

~~~sh
python3 <absolute-branch-workflow.py> preserve \
  --reason "외부 의존성 확인 전까지 현재 변경과 worktree를 보존"
~~~

PRESERVED worktree에는 애플리케이션 소스 변경이 차단된다. 현재 assignment에 귀속된 진단·handoff 산출물은 작성할 수 있다. 다른 task를 병행하려면 별도 worktree와 별도 세션을 사용한다.

해당 task로 돌아오면 그 worktree에서 resume한다.

~~~sh
python3 <absolute-branch-workflow.py> resume
~~~

## 10. 파일과 Git 작업 규칙

### 구조화된 파일 도구 사용

파일 생성·수정·삭제는 경로를 명시적으로 전달하는 Edit, Write 또는 apply_patch 계열 도구를 사용한다.

Bash heredoc, tee 또는 redirect로 산출물을 만들면 session assignment 귀속이 기록되지 않아 완료·보존 workflow에서 차단될 수 있다. 일반 대화 종료와 읽기 전용 조사는 산출물 완료 검사를 실행하지 않는다.

현재 assignment와 host·session directory가 일치하는 산출물 전용 구조화 쓰기는 branch 계약 식별자가 손상된 경우에도 허용한다. 이 예외는 오류를 기록하고 handoff하기 위한 것이며 source 변경, Git mutation, finish·verify·close 권한까지 허용하지 않는다.

잘못된 예:

~~~sh
python3 - <<'PY' > .claude/logs/sessions/example/plan.md
print("plan")
PY
~~~

올바른 방식:

- host의 Write/Edit 도구로 정확한 파일 경로를 전달
- apply_patch로 파일 단위 변경

stderr만 터미널로 전달하는 2>&1 또는 /dev/null redirect는 파일 산출물 쓰기로 보지 않지만, managed file을 redirect 대상으로 숨길 수는 없다.

### Git 대상 명시

`git status`, `git diff`, `git log`, 조회형 `git branch`와 `git worktree list`는 저장소를 바꾸지 않으므로 구현 gate나 별도 명령 승인을 요구하지 않는다. 변경형 또는 해석할 수 없는 Git 명령은 기존 승인·branch 검증을 거친다.

stage는 path separator를 포함해 실행한다.

~~~sh
git add -- src/path/to/file.ts
~~~

`git commit -m <message>`의 메시지 값은 URL이나 `/`를 포함해도 pathspec으로 분류하지 않는다. 반복된 `-m`도 동일하다.

파일 복원은 승인 scope의 구체 경로에 git restore를 사용한다.

~~~sh
git restore -- src/path/to/file.ts
~~~

다음 형식은 사용하지 않는다.

~~~sh
git checkout -- src/path/to/file.ts
~~~

checkout은 파일 복원과 branch 전환이 혼동될 수 있어 차단된다.

### 명령 분리

branch 전환과 merge·commit을 한 복합 명령에 넣지 않는다.

잘못된 예:

~~~sh
git checkout sy-main && git merge task/example
~~~

전환 후 실제 branch와 worktree를 검증할 수 있도록 각각 별도 호출로 실행한다. V3 task의 실제 merge는 raw git merge가 아니라 승인된 finish workflow를 사용한다.

### Git repository 우회 금지

guard는 git -C와 --git-dir/--work-tree의 실제 대상 저장소를 계산한다. 다음 형태로 저장소 대상을 숨기거나 index를 바꾸지 않는다.

- GIT_DIR 또는 GIT_WORK_TREE 환경 변수
- cd 또는 pushd 뒤 Git 실행
- env -C
- 대상 worktree와 일치하지 않는 --git-dir/--work-tree 조합

해석할 수 없거나 Git directory와 worktree가 일치하지 않으면 fail-closed로 차단한다.

### 사용자 전용 명령

다음 명령은 host 승인 UI나 채팅 승인을 받아도 에이전트가 실행할 수 없다.

- git push
- git reset --hard
- git clean
- git update-ref

에이전트는 필요한 이유, 정확한 대상과 영향을 설명하고 사용자에게 실행을 양도한다.

## 11. 산출물과 handoff

### owner 필수 산출물 8종

| 파일                  | 목적                                               |
| --------------------- | -------------------------------------------------- |
| plan.md               | 목표, 범위, 승인, 구현·검증 계획                   |
| exploration.md        | 기존 구조, 재사용 후보와 문제 근거                 |
| implementation-log.md | 실제 변경, 결정과 진행 중 해결한 문제              |
| grill-me-review.md    | 반론, 위험, 대안과 정책 위반 가능성 점검           |
| review-log.md         | 변경 결과에 대한 결함 중심 검토                    |
| evaluation-log.md     | 테스트 결과, 장기 영향과 후속 개선                 |
| final-summary.md      | 완료 결과, 변경 파일, 검증과 남은 작업             |
| portfolio-log.md      | 문제·선택·구현·기술 목적·검증을 사례 형식으로 기록 |

host별 정본 위치:

~~~text
Codex       .codex/logs/sessions/<session-name>/
Claude Code .claude/logs/sessions/<session-name>/
OpenCode    .opencode/logs/sessions/<session-name>/
~~~

산출물 최초 파일 작성에는 반드시 구조화된 Write 계열 도구를 사용한다.

### contributor handoff

contributor는 handoff.md에 다음 내용을 기록한다.

- 목표와 현재 상태
- requested_roles, confirmed_roles, completed_roles, next_role
- 완료·대기 작업
- 변경 경로와 파일 소유권
- branch, worktree, task, Git integrator
- 실행한 검증과 실행하지 않은 검증
- 차단 요인과 다음 조치

handoff의 next_role은 제안이지 자동 권한이 아니다.

### 다른 host와 세션의 문서

- 읽기: 허용
- 수정·덮어쓰기: 금지
- 정의되지 않은 보조 문서: 현재 세션 디렉터리의 unknown/에 기록
- host를 식별할 수 없는 기록: .agent-policy/logs/unknown/sessions/ 사용

## 12. 구현 완료와 병합

구현, owner 산출물 8종, 검증과 source branch commit이 끝나면 완료 proposal을 만든다. 산출물 구조와 귀속은 이 명시적 완료 단계와 `finish`, `verify`, `close`, `preserve`에서 검증하며 Stop hook은 대화를 재개시키지 않는다.

finish-proposal은 source task worktree에서 실행하고, 승인된 finish·verify·close는 workflow가 요구하는 target 상태를 매 단계 다시 확인할 수 있도록 각각 별도 호출한다.

~~~sh
python3 <absolute-branch-workflow.py> finish-proposal \
  --source task/add-comment-favorite-icons \
  --verify-command "npm run lint" \
  --verify-command "npm run test" \
  --verify-command "npm run build" \
  --cleanup
~~~

finish proposal에는 다음 값이 포함된다.

- source와 target 전체 HEAD
- 승인된 ff-only 또는 merge-commit 방식과 실제 통합 worktree
- 사후 검증 명령
- cleanup 여부
- proposal 파일 절대 경로
- 64자리 SHA-256

사용자에게 이를 별도 prompt로 제시하고 승인받은 뒤 각 단계를 별도 명령으로 실행한다.

~~~sh
python3 <absolute-branch-workflow.py> finish \
  --proposal-file <finish-proposal-path> \
  --proposal-sha256 <printed-64-character-sha256>
~~~

~~~sh
python3 <absolute-branch-workflow.py> verify \
  --proposal-file <finish-proposal-path> \
  --proposal-sha256 <printed-64-character-sha256>
~~~

~~~sh
python3 <absolute-branch-workflow.py> close \
  --proposal-file <finish-proposal-path> \
  --proposal-sha256 <printed-64-character-sha256>
~~~

- finish: 승인된 source/target HEAD와 clean target을 확인하고 계약의 방식으로 merge. 필요한 단일 worktree의 target 전환은 이 명령 내부에서만 수행
- verify: 기록된 integration HEAD와 source 포함 관계를 확인하고 target에서 승인된 명령을 shell wrapper 없이 실행
- close: ancestry와 clean 상태를 확인하고 CLOSED 기록
- cleanup: finish proposal에 포함해 승인된 경우에만 로그 수집 성공을 확인한 뒤 격리 worktree와 local source branch 정리

`--cleanup`의 삭제 대상은 통합 worktree와 달라야 한다. target이 다른 worktree에서 checkout되어 있지 않으면 source worktree를 통합에 사용하므로, 이때는 `--cleanup`을 생략한다. 같은 경로를 통합과 삭제에 함께 지정하면 proposal과 신규 finish 실행을 차단한다.

실패 시 자동 rollback, rebase, reset 또는 강제 삭제하지 않는다. source와 worktree를 보존하고 정확한 실패 단계를 보고한다.

과거 번들에서 동일 worktree cleanup 계약으로 이미 `MERGED_VERIFIED`까지 진행한 경우, 중앙 CLI에서 정리 보류 계약을 검토한다.

~~~sh
bin/agent-policy close-recover --project user-ui \
  --finish-file <original-finish-proposal-path> \
  --finish-sha256 <original-finish-sha256>
~~~

출력된 복구 JSON에는 원래 finish SHA, 현재 HEAD, 검증 receipt, assignment와 소유권, 보존할 branch·worktree가 담긴다. 정리 보류에 대한 새 SHA 승인을 받은 뒤 같은 명령에 `--approved-sha256 <recovery-sha256>`을 추가한다. 실행은 기존 검증 근거를 유지하고 `CLOSED` 기록과 해당 소유자의 통합 예약·Git claim 해제만 수행한다. branch, worktree, 로그를 보존하며 merge·검증 명령을 재실행하지 않는다. 승인 이후 상태가 달라지면 중단하고, 자신의 부분 기록 때문에 끊긴 경우에는 같은 복구 SHA로 재개한다. 완료한 복구의 재호출은 이후 작업의 예약을 해제하지 않는다.

## 13. 중앙 정책 운영

### 변경 전후 검사

~~~sh
python3 -m unittest discover -s tests -v
bin/agent-policy audit
~~~

- unittest: 렌더링, guard, 세 host inject와 실제 장애 회귀 테스트
- audit: 중앙 계약과 각 소비자 메타데이터 검사

### 정책 변경 반영

소비자 배포 명령은 없다. 중앙 원본과 회귀 테스트를 수정하고 전체 검증을 통과시킨 뒤 현재 세션을 handoff하고 중앙 `start`를 다시 실행한다. 단순 세션 resume은 이전 digest 번들을 계속 사용할 수 있으므로 최신 정책 적용으로 간주하지 않는다.

## 14. 중앙 로그 수집

세션 산출물의 정본은 소비자 worktree에 있고 중앙 logs/projects/는 Git 이력용 사본이다.

~~~sh
bin/agent-policy collect-logs \
  --project all \
  --channel all
~~~

특정 project 또는 host만 수집할 수도 있다.

~~~sh
bin/agent-policy collect-logs \
  --project user-ui \
  --channel claude
~~~

수집은 다음 원칙을 따른다.

- 추가·변경 파일만 반영
- 소비자에서 사라진 문서를 중앙에서 자동 삭제하지 않음
- 중앙 로그를 자동 stage·commit하지 않음
- logs/\*\*는 정책 source digest에서 제외

## 15. 자주 발생하는 문제

기존 브랜치를 기본 작업 폴더에서 이어가는 경우에도 새 assignment의 준비 상태는 별도로 확인한다. SessionStart의 `[SESSION_READINESS]`는 구현 승인, 스킬·코드 탐색, 종류별 SHA 승인과 미충족 항목을 보여 준다. 기존 V3 계약이 유효하고 현재 경로와 일치하면 branch를 다시 만들지 않는다. `PRESERVED`는 명시적 resume 후 구현할 수 있다. 현재 bundle의 `managed_policy_guard.py branch-context <host>`로 같은 상태를 다시 조회할 수 있다.

| 증상                                                  | 원인                                                         | 조치                                                                                                     |
| ----------------------------------------------------- | ------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------- |
| 외부 worktree에서 hook 파일을 찾지 못함               | 중앙 launcher가 아닌 소비자 legacy hook으로 실행             | 소비자 정책 출처를 중앙 history와 대조해 제거하고 중앙 launcher로 새 세션 시작                           |
| 재시작 후에도 소비자 `.claude/hooks` 경로를 사용      | 기존 세션을 resume했거나 소비자 정책 파일이 남아 있음        | 새 `start --print-only`에서 bundle 절대 guard 경로 확인; 잔존 파일이 있으면 launcher가 시작 전에 거부     |
| SHA 승인 후에도 구현 승인 누락                         | 생성 계약 SHA와 현재 assignment의 구현 승인은 별도 기록     | `[SESSION_READINESS]`를 확인하고 인계 계획·역할에 대한 미충족 구현 승인만 명시적으로 기록                  |
| 스킬·공용 UI 읽기가 성공했는데 확인 상태가 비어 있음    | 이전 번들이 Codex 문자열 결과의 완료 정보를 판정하지 못함  | handoff 후 중앙 launcher의 새 start로 수정된 bundle 적용; --resume-assignment는 이전 bundle 유지          |
| 새 Logic 작업에 종료된 UI 브랜치의 탐색·scope가 적용됨  | 이전 guard가 현재 폴더의 종료된 branch metadata를 참조       | 새 bundle에서 현재 assignment와 대상 계약 기준의 준비 상태 확인                                         |
| proposal/create가 정책 snapshot 경로 때문에 차단      | 오래된 guard가 inject snapshot workflow를 신뢰하지 못함      | 새 inject 번들로 재시작하고 system prompt가 제공한 절대 branch_workflow.py 사용                          |
| 승인 요청 식별자 불일치                               | 축약 SHA 또는 다른 proposal 값 사용                          | 현재 세션 산출물에 오류를 기록한 뒤 출력된 동일 파일과 64자리 SHA-256 전체값으로 계약 복구; source·Git 작업은 복구 전 중단 |
| finish·close가 산출물 누락·귀속 오류 보고             | 구조화된 Write 없이 산출물을 만들었거나 owner 문서가 미완료 | 현재 session directory에 구조화된 Write 도구로 필수 문서를 완성                                          |
| Codex SessionStart hook JSON 오류                      | 오래된 guard가 context를 일반 텍스트로 출력                 | 소비자 guard를 제거하고 중앙 launcher로 새 세션 시작                                                      |
| 읽기 전용 Git 조회가 구현·명령 승인을 요구             | 오래된 guard가 모든 Git 호출을 변경형으로 분류              | 중앙 launcher로 새 세션을 시작한 뒤 단순 조회 명령을 다시 실행                                           |
| `git checkout -- PATH`가 branch 전환으로 판정         | checkout 명령의 의미가 모호함                                | `git restore ... -- PATH` 사용                                                                           |
| checkout과 merge를 결합한 명령이 잘못 판정            | 전환 전 cwd·branch에서 복합 명령을 평가                      | 명령을 분리하고 V3 merge는 finish workflow 사용                                                          |
| dirty worktree라 branch 생성 불가                     | primary에 다른 작업의 변경이 존재                            | 기존 변경을 건드리지 말고 proposal에 외부 --worktree 포함                                                |
| primary에서 git -C task-worktree add가 차단           | 오래된 guard가 명령 cwd만 판정                               | 중앙 launcher로 새 세션 시작                                                                              |
| task worktree에서 primary sy-main add가 통과          | 오래된 guard가 -C 대상을 무시                                | 새 guard는 실제 대상 worktree를 판정해 차단                                                              |
| start가 소비자 정책 출처를 보고하며 중단              | 선택된 worktree에 `AGENTS.md` 또는 host별 hook·skill이 남음 | 중앙 history와 SHA-256을 대조한 뒤 해당 사본만 제거하고 다시 시작                                         |
| 다른 task로 전환할 수 없음                            | 대상이 현재 assignment root의 승인된 자손이 아닌 독립 task | 같은 계보면 `asan-parent` metadata·ACTIVE 상태를 확인하고, 독립 task면 root를 CLOSED로 만들거나 PRESERVED 후 별도 세션 사용 |
| 다른 host의 산출물을 수정할 수 없음                   | 산출물은 host·session별 write 소유권 적용                    | 읽기만 수행하고 현재 host의 session directory 또는 handoff 사용                                          |
| role 범위를 벗어난 요청이 차단                        | inject role은 세션 시작 시 고정                              | 올바른 --role로 새 inject 세션 시작                                                                      |

## 16. 대표 실행 시나리오

### 시나리오 A: 중앙 최신 정책으로 새 Logic 작업

1. 중앙 저장소에서 audit
2. inject --role logic --print-only로 bundle과 cwd 확인
3. 실제 inject 세션 실행
4. 사용자 요청과 기존 코드 조사
5. 계획 승인
6. branch proposal 생성 및 별도 승인
7. create 후 승인 scope 구현
8. 8종 산출물, 검증, commit
9. finish proposal 승인
10. finish → verify → close

### 시나리오 B: sy-main이 dirty인 상태에서 독립 UI 작업

1. 다른 작업의 dirty 경로와 소유권을 읽기만 함
2. 독립 작업임을 판단하고 parent는 sy-main으로 유지
3. proposal에 repository 밖의 worktree 절대 경로 포함
4. 승인 후 create
5. 현재 세션에서 해당 worktree를 workdir 또는 git -C 대상으로 사용
6. primary dirty 파일은 건드리지 않음
7. 완료 후 승인된 finish workflow로 sy-main에 통합·재검증

### 시나리오 C: 기존 inject 세션의 정책만 갱신

1. 현재 작업 상태와 산출물 기록
2. 실행 중인 기존 세션 종료
3. 소비자 sync는 실행하지 않음
4. 중앙 start --mode inject를 동일 host, role, task, worktree, branch, session-dir로 다시 실행
5. 새 bundle 절대 hook 경로 확인
6. 기존 파일, index와 commit을 유지한 채 작업 재개

### 시나리오 D: 미완료 작업을 남기고 긴급 작업 병행

1. 현재 task에 handoff.md 작성
2. preserve로 PRESERVED 기록
3. 긴급 task용 별도 worktree와 별도 세션 생성
4. 긴급 task를 독립적으로 완료
5. 기존 worktree의 task로 돌아와 resume

## 17. 시작·종료 체크리스트

### 시작 전

- project, host, mode를 선택했는가
- inject라면 role을 선택했는가
- owner/contributor 책임을 선택했는가
- 현재 branch, HEAD, dirty 경로와 worktree를 확인했는가
- 기존 ACTIVE 또는 PRESERVED task와 충돌하지 않는가
- --print-only의 cwd와 hook 경로가 기대와 일치하는가

### 구현 전

- 역할과 구현 계획을 승인받았는가
- 관련 공통 skill과 대상 코드·재사용 후보를 읽었는가
- branch proposal 파일과 64자리 SHA-256을 별도로 승인받았는가
- task metadata가 ACTIVE이고 scope가 정확한가
- Git integrator가 한 명으로 정해졌는가

### 완료 전

- 승인 scope 안의 파일만 변경했는가
- 다른 작업자의 dirty 파일을 건드리지 않았는가
- owner 8종 또는 contributor handoff 책임을 충족했는가
- lint, test, build 등 승인된 검증 결과를 기록했는가
- source 변경과 산출물이 commit됐는가
- finish proposal을 별도로 승인받았는가
- finish, verify, close를 분리 실행했는가
- 소비자 정책 파일을 만들거나 Git push처럼 사용자 전용 작업을 임의 실행하지 않았는가


## 18. 지속 assignment와 중단 복구

세션 시작·재개, 종류별 승인, 실행 예약, Git 소유권, 중단 복구 명령과 host 검증 범위는 [runtime 개선 보고](runtime-remediation-2026-09-08.md)를 따른다. `--resume-assignment`는 원래 native session·bundle·Codex home을 재사용한다. 다른 담당 세션에는 명시적 `assignment-handoff` 계약이 필요하며 구현 승인은 복제하지 않는다.
