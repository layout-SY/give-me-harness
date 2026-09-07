# asan-agent-policy

처음 설정하거나 실제 세션·branch·worktree 흐름을 확인하려면 [중앙 정책 사용 가이드](docs/usage-guide.md)를 먼저 읽습니다. 정책의 설계 근거와 상태 전이는 [브랜치·worktree·세션 운영 전략 V3](docs/branch-worktree-session-strategy.md)에 있습니다.

두 프런트엔드 저장소가 같은 AI 작업 정책을 사용하도록 만드는 독립 중앙 원본입니다. 공통 의미는 한 번만 보관해 소비자 `.agent-policy/common/**`에 렌더하고 Codex, Claude Code, OpenCode의 파일·훅·skill discovery 형식 차이는 adapter에서 처리합니다.

## 핵심 원칙

- 기준: `asan-metaverse-user-ui` Git commit `9edd378560c3c3b7f258984698202498f5c31831`
- 다른 중앙 저장소는 직접 읽거나 복사하지 않으며, 2026-08-31에 한해 `user-ui` 소비자에 반영된 공통 정책 형태를 일회성으로 역이관
- admin-ui는 기준을 제공하지 않고 소비만 함
- 프로젝트별 overlay는 V1에서 지원하지 않음
- 대상 파일 수정은 중앙 프로젝트에서만 수행
- sync는 이전 manifest에 기록된 파일만 안전하게 교체·퇴역
- 소비자 `AGENTS.md`는 중앙 저장소 위치를 가리키지 않으며 관리 파일 판정과 차단은 manifest와 guard가 담당
- 역할 정책은 호스트·모델과 분리하며 사용자 요청과 handoff를 근거로 역할을 제안하고 확인받은 뒤 적용
- inject 모드는 시작 시 `--role logic|ui|orchest|review|generate`를 선택하고 해당 role 문서만 바인딩

## 구조

```text
policy/common/          공통 AGENTS와 스킬
policy/guards/          관리 파일 차단 및 drift 검사
adapters/codex/         Codex 역할·워크플로·훅 형식
adapters/claude/        Claude Code 도구·훅·native agent 형식
adapters/opencode/      OpenCode 역할·plugin 형식
projects/               대상 경로·명령과 legacy 감사 스냅샷
lib/agent_policy/       결정적 렌더링과 manifest 로직
build/                  source digest별 inject 번들(생성물, Git 제외)
state/                  inject Codex의 지속 상태(생성물, Git 제외)
bin/agent-policy        운영 CLI
tests/                  중앙 단위 테스트
logs/projects/          프로젝트·실행 호스트별 필수 산출물 Git 사본
```

## 명령

```bash
bin/agent-policy audit
bin/agent-policy diff --project all
bin/agent-policy check --project all
bin/agent-policy sync --project all
bin/agent-policy collect-logs --project all --channel all
bin/agent-policy start --project user-ui --host codex --mode sync --model <model>
bin/agent-policy start --project user-ui --host opencode --mode inject --role logic --model <model>
```

`sync`는 소비자 프로젝트를 변경합니다. 먼저 `diff`를 검토하고 별도 승인을 받은 뒤 실행합니다. 기존 중앙화 시도의 잔여 파일은 기본 sync에서 삭제하지 않으며, 감사 스냅샷과 SHA-256이 일치할 때만 `--retire-legacy`로 퇴역합니다.

`collect-logs`는 프로젝트의 필수 산출물 8종, 인계 문서와 각 세션의 `unknown/` 보조 기록을 `logs/projects/{project}/{host}/sessions/`로 복사합니다. 원본은 Codex `.codex/logs/sessions/`, Claude Code `.claude/logs/sessions/`, OpenCode `.opencode/logs/sessions/`로 분리하고, host를 판별할 수 없는 기록은 `.agent-policy/logs/unknown/sessions/`에 둡니다. 과거 `.codex` 기반 `logic` archive와 명시적 수집 alias는 삭제하지 않습니다. 같은 내용은 건너뛰고 변경된 파일만 원자적으로 교체하며, 프로젝트에서 삭제된 파일을 중앙 사본에서 자동 삭제하거나 Git add·commit하지 않습니다.

### 세션 시작 모드

`start`의 기본값은 기존과 같은 `--mode sync`입니다. 소비자 manifest와 관리 파일이 중앙 렌더 결과와 완전히 일치하지 않으면 세션을 시작하지 않습니다. `sync` 명령과 배포 승인 절차도 그대로 유지합니다.

`--mode inject`는 `--role`을 필수로 받고 공통 정본에서 해당 role에 필요한 문서·스킬과 선택한 host adapter만 골라 중앙 `build/{project}/` 아래의 불변 digest 번들로 생성합니다. 소비자 파일에 drift가 있으면 경고하지만 세션은 계속 시작하며, 소비자 저장소의 정책 파일을 쓰거나 manifest를 갱신하지 않습니다. 중앙 정책 audit 실패와 대상 프로젝트 부재는 계속 차단합니다. role 경계는 system prompt에 명시하며 별도 감시 hook은 두지 않습니다.

- Codex: 중앙 `state/{project}/codex-home/`을 `CODEX_HOME`으로 사용합니다. 사용자 `config.toml`과 `auth.json`은 내용을 복사하지 않고 심볼릭 링크로 참조하고 중앙 정책 설정은 CLI override로 적용합니다. 세션 동안 소비자 `.codex` 계층과 소비자 skill을 끄고, 프로젝트 `AGENTS.md` 자동 로드는 제한한 뒤 중앙 prompt를 developer instruction으로 한 번만 주입합니다.
- Claude Code: 사용자 설정만 유지하고 중앙 settings, 임시 plugin, hook, skill 및 합성 prompt를 `--settings`, `--plugin-dir`, `--append-system-prompt-file`로 주입합니다.
- OpenCode: 중앙 번들을 `OPENCODE_CONFIG_DIR`로 지정하고 `OPENCODE_DISABLE_PROJECT_CONFIG=1`로 프로젝트 설정·prompt 자동 로드를 끕니다. 중앙 config가 instructions, skills, agents, plugins를 제공합니다.

실행 전에 실제 명령과 환경만 확인하려면 `--print-only`를 붙입니다. 긴 system prompt는 출력하지 않고 해당 번들의 `system-prompt.md` 경로로 표시합니다.

기본 세션 cwd는 `projects/*.json`의 프로젝트 경로입니다. 승인된 격리 worktree에서 시작할 때는 `--worktree <path> --branch task/<name>`을 사용합니다. `--session-dir`은 선택 host에 맞춰 `.codex/logs/sessions/<task>`, `.claude/logs/sessions/<task>` 또는 `.opencode/logs/sessions/<task>`를 지정합니다. 도구는 지정 경로가 같은 Git 저장소인지와 현재 branch가 일치하는지만 확인하며 branch를 임의 전환하지 않습니다.

격리 worktree 생성이 언제나 새 세션을 뜻하지는 않습니다. 한 세션의 assignment 권한 root에서 승인 생성한 V3 자손 branch는 `asan-parent` 계보를 따라 같은 세션이 도구 `workdir` 또는 `git -C` 대상으로 사용해 계속할 수 있습니다. 권한은 하향으로만 상속되고 각 child의 scope·상태·Git 통합 담당자·worktree는 독립 검증됩니다. 권한 root가 `CLOSED`이면 같은 세션에서 다음 독립 task로 전환할 수 있고, 미완료 task를 `PRESERVED`로 남겨 계보 밖 작업을 병행할 때만 별도 worktree·세션이 필요합니다. sync hook은 실행 cwd가 아니라 `projects/*.json`에 등록된 소비자 기본 checkout의 절대 runtime 경로를 사용합니다.

## 세션 동작

- sync 모드의 Codex와 Claude Code는 SessionStart hook에서 중앙 source digest와 로컬 파일 hash를 검사합니다.
- sync 모드의 OpenCode는 plugin 로드 시 같은 검사를 사용자에게 경고하고, `start` wrapper는 drift가 있으면 실행을 중단합니다.
- inject 모드는 소비자 drift를 경고하되 중앙 digest 번들을 기준으로 계속하며, SessionStart hook도 같은 상태와 브랜치 context를 보고합니다.
- Codex와 Claude Code의 Stop hook 및 OpenCode의 `session.idle`은 세션 로그를 수집하되 대화를 차단하지 않습니다. 역할 계약에 맞는 산출물 검증은 명시적인 `finish-proposal`, `finish`, `verify`, `close`, `preserve` 단계에서 수행합니다.
- 세 호스트 모두 managed file 편집과 명시적인 shell write를 차단합니다.
- 세 호스트 모두 공통 UserPrompt/PostTool 상태로 구현 승인, 관련 skill 확인과 역할별 재사용·인접 구현 탐색을 기록하며, 조건을 갖추기 전 source mutation을 차단합니다.
- branch create와 finish 계열은 proposal 출력 뒤 사용자가 승인한 64자리 SHA-256이 실행 인자와 일치해야 합니다.
- 저장소를 변경하는 Git 명령과 build/dev/start/preview 계열 명령은 실행 전에 사용자가 직접 판단합니다. `status`, `diff`, `log`, branch 목록과 `worktree list` 같은 읽기 전용 Git 조사는 별도 명령 승인이나 구현 gate 없이 허용합니다.
- sync 모드에서 중앙 원본을 바꾼 뒤에는 sync하고 실행 중인 세션을 handoff한 다음 새 세션을 시작해야 합니다. inject 모드는 새 세션 시작 때 현재 중앙 source digest의 새 번들을 선택합니다.

## 역할과 병렬 세션

- sync 또는 role이 없는 세션은 공통 `task-role-routing` 스킬이 역할을 제안하고 사용자 확인을 받습니다. inject 세션은 시작 시 선택한 role을 이미 확인된 계약으로 사용합니다.
- Claude Code, Codex, OpenCode 어느 호스트도 특정 역할을 기본 소유하지 않습니다. inject 세션에서 역할을 바꾸려면 해당 `--role`로 새 세션을 시작합니다.
- inject profile은 `logic`(데이터·상태·API), `ui`(화면·스타일·접근성), `orchest`(조사·계획·승인), `review`(변경 없는 검토), `generate`(승인된 handoff·branch scope 구현)입니다. 이 값은 session 문서 바인딩용이며 branch task의 반복 가능한 역할 metadata와 자동으로 동일시하지 않습니다.
- handoff의 `next_role`은 다음 역할의 제안이며 자동 권한이 아닙니다. role이 없는 세션은 사용자에게 다시 확인하고, inject 세션은 선택된 role과 다르면 올바른 role로 재시작합니다.
- 같은 worktree에서는 Git 통합 담당자 한 명만 index·commit·merge를 조작합니다. 실제 병렬 수정은 역할별 child branch와 격리 worktree로 나눕니다.
- `start --responsibility owner` 세션은 필수 산출물 8종, `contributor` 세션은 `handoff.md`를 작성합니다. 산출물 책임은 호스트나 branch 고정 속성이 아니라 session assignment로 판정합니다. 다른 host·세션의 기록은 읽을 수 있지만 수정할 수 없고, 미정의 보조 문서는 현재 세션의 `unknown/`에 둡니다.

## 보호 명령 승인 방식

- 아래 승인은 저장소를 변경하는 Git 명령에만 적용합니다. 읽기 전용 Git 조회는 허용하며, 해석할 수 없는 Git 형태는 변경형으로 간주해 fail-closed합니다.
- Codex: 첫 시도를 차단하고 정확한 명령을 표시합니다. 사용자가 `명령 실행 승인`만 독립된 메시지로 보내면 같은 명령을 30분 안에 한 번 실행할 수 있습니다.
- Claude Code: 중앙 `PreToolUse` 훅이 `ask`를 반환하여 호스트 권한 UI에서 사용자가 결정합니다.
- OpenCode 1.18.x: 생성된 `opencode.json`의 `permission.bash`가 명령 패턴별 권한 UI를 표시합니다. 기본적으로 `once`를 선택하고 `always`는 사용자가 의도한 경우에만 선택합니다.
- lint와 test는 이 보호 명령 범위가 아니며 기존 승인·검증 정책을 따릅니다.

`git push`, `git reset --hard`, `git clean`, `git update-ref`는 위 승인 방식으로 해제되지 않습니다. 공통 branch guard가 실행을 거부하고 에이전트는 이유·정확한 대상·영향만 설명한 뒤 사용자 직접 실행으로 양도합니다.

OpenCode V2는 `permission`/`bash` 대신 `permissions`/`shell` 규칙 배열을 사용합니다. 현재 adapter는 설치된 OpenCode 1.18.25의 V1 스키마를 대상으로 하므로 V2로 올릴 때 config renderer와 smoke test를 함께 마이그레이션해야 합니다.

`전부 승인`과 `모두 승인`은 보고된 구현 계획에 대한 승인으로만 기록합니다. Codex의 정확한 shell 명령 1회 승인을 대신하지 않습니다.

정책 훅이 중앙 manifest와 저장소 루트를 찾기 위해 수행하는 내부 읽기 전용 저장소 확인도 같은 조회 분류를 사용합니다.

## 중앙 로그 운영

- 활성 세션 중에는 실제 worktree의 소비자 로그가 원본이며 중앙 로그는 실행 호스트별 Git 이력용 사본입니다. 수행 역할은 산출물 metadata에 기록합니다.
- 자동 수집 실패는 stderr에 표시하고 다음 Stop 또는 `session.idle`에서 다시 시도합니다. 필요하면 중앙 저장소에서 `collect-logs`를 직접 실행합니다.
- `logs/**`에만 있는 미커밋 변경은 정책 `sync`의 청결 판정을 막지 않습니다. `policy/`, `adapters/`, `projects/`, `lib/` 등 정책 소스의 미커밋 변경은 계속 sync를 차단합니다.
- 중앙 로그도 일반 파일처럼 검토 후 사용자가 승인한 Git 명령으로 커밋합니다.
