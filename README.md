# asan-agent-policy

현재 세션·branch·worktree 운영은 [세션 독립 브랜치 관계와 완료 통합](docs/branch-relations-2026-09-10.md)을 먼저 읽습니다. [이전 사용 가이드](docs/usage-guide.md)와 [V3 운영 전략](docs/branch-worktree-session-strategy.md)은 과거 bundle의 조사·복구를 위한 기록입니다.

두 프런트엔드 저장소가 같은 AI 작업 정책을 사용하도록 만드는 독립 중앙 원본입니다. 공통 의미는 한 번만 보관해 중앙 inject bundle로 렌더하고 Codex, Claude Code, OpenCode의 프롬프트·훅·skill discovery 형식 차이는 adapter에서 처리합니다.

## 핵심 원칙

- 기준: `asan-metaverse-user-ui` Git commit `9edd378560c3c3b7f258984698202498f5c31831`
- 다른 중앙 저장소는 직접 읽거나 복사하지 않으며, 2026-08-31에 한해 `user-ui` 소비자에 반영된 공통 정책 형태를 일회성으로 역이관
- admin-ui는 기준을 제공하지 않고 소비만 함
- 프로젝트별 기능 정책 overlay는 V1에서 지원하지 않음. 승인된 admin-ui 재사용 자산 reference 카탈로그만 예외로 렌더·digest에 포함
- 정책 수정은 중앙 프로젝트에서만 수행
- 소비자 저장소에는 host별 세션 로그와 허용된 개인 설정 외의 정책·프롬프트·훅 사본을 두지 않음
- 중앙 launcher는 선택된 실제 worktree에 소비자 정책 출처가 남아 있으면 시작 전에 경로를 보고하고 중단
- 역할 정책은 호스트·모델과 분리하며 사용자 요청과 handoff를 근거로 역할을 제안하고 확인받은 뒤 적용
- 세션 시작 시 `--role logic|ui|orchest|review|generate`를 선택하고 해당 role 문서만 중앙에서 바인딩
- 정책·훅 결함 수정은 수정 전 실패하고 수정 후 통과하는 자동 회귀 테스트를 반드시 함께 추가

## 구조

```text
policy/common/          공통 AGENTS와 스킬
policy/guards/          중앙 bundle·승인·변경 범위 검사
adapters/codex/         Codex 역할·워크플로·훅 형식
adapters/claude/        Claude Code 도구·훅·native agent 형식
adapters/opencode/      OpenCode 역할·plugin 형식
projects/               대상 경로·명령과 프로젝트별 중앙 overlay
lib/agent_policy/       결정적 렌더링과 inject 실행 로직
build/                  source digest별 inject 번들(생성물, Git 제외)
state/                  inject Codex의 지속 상태(생성물, Git 제외)
bin/agent-policy        운영 CLI
tests/                  중앙 단위 테스트
logs/projects/          프로젝트·실행 호스트별 필수 산출물 Git 사본
```

## 명령

```bash
bin/agent-policy audit
bin/agent-policy collect-logs --project all --channel all
bin/agent-policy start --project user-ui --host codex --role logic --model <model>
bin/agent-policy start --project user-ui --host opencode --mode inject --role logic --model <model>
```

`sync`, `diff`, `check` 소비자 배포 명령은 제거되었습니다. `--mode inject`는 기존 실행 명령 호환을 위해 허용하지만 생략해도 동일하며, 다른 mode 값은 거부됩니다.

`collect-logs`는 필수 plan·final-summary, 선택 문서 6종, handoff와 `unknown/` 보조 기록을 `logs/projects/{project}/{host}/sessions/`로 복사합니다. 소비자 host별 세션 로그가 원본입니다. 같은 내용은 건너뛰고 변경된 파일만 원자적으로 교체하며 중앙 사본을 자동 삭제하거나 Git add·commit하지 않습니다.

### 세션 시작

`start`는 inject 방식만 지원합니다. `--role`을 필수로 받고 공통 정본에서 해당 role에 필요한 문서·스킬과 선택한 host adapter만 골라 중앙 `build/{project}/` 아래의 불변 digest 번들로 생성합니다. 소비자 저장소의 정책 파일을 쓰거나 배포 manifest를 만들지 않습니다. 중앙 정책 audit 실패, 대상 프로젝트 부재, 선택된 worktree의 소비자 정책 출처 잔존은 시작 전에 차단합니다. role 책임은 system prompt에 명시하고 공통 guard에서 review·orchest의 source 변경을 차단합니다. Git 승인은 host·role·assignment와 무관한 작업 단위로 판정합니다.

- Codex: 중앙 `state/repositories/{repository-id}/assignments/{assignment-id}/codex-home/`을 `CODEX_HOME`으로 사용합니다. 사용자 `config.toml`과 `auth.json`은 내용을 복사하지 않고 심볼릭 링크로 참조하고 중앙 정책 설정은 CLI override로 적용합니다. 세션 동안 소비자 `.codex` 계층과 소비자 skill을 끄고, 프로젝트 `AGENTS.md` 자동 로드는 제한한 뒤 중앙 prompt를 developer instruction으로 한 번만 주입합니다.
- Claude Code: 사용자 설정만 유지하고 중앙 settings, 임시 plugin, hook, skill 및 합성 prompt를 `--settings`, `--plugin-dir`, `--append-system-prompt-file`로 주입합니다.
- OpenCode: 중앙 번들을 `OPENCODE_CONFIG_DIR`로 지정하고 `OPENCODE_DISABLE_PROJECT_CONFIG=1`로 프로젝트 설정·prompt 자동 로드를 끕니다. 중앙 config가 instructions, skills, agents, plugins를 제공합니다.

실행 전에 실제 명령과 환경만 확인하려면 `--print-only`를 붙입니다. 긴 system prompt는 출력하지 않고 해당 번들의 `system-prompt.md` 경로로 표시합니다.

기본 세션 cwd는 `projects/*.json`의 프로젝트 경로입니다. 승인된 격리 worktree에서 시작할 때는 `--worktree <path> --branch task/<name>`을 사용합니다. `--session-dir`은 선택 host에 맞춰 `.codex/logs/sessions/<task>`, `.claude/logs/sessions/<task>` 또는 `.opencode/logs/sessions/<task>`를 지정합니다. 도구는 지정 경로가 같은 Git 저장소인지와 현재 branch가 일치하는지만 확인하며 branch를 임의 전환하지 않습니다.

같은 프로젝트의 모든 branch·linked worktree에 세션과 무관하게 접근할 수 있습니다. 다른 기능 계열로 이동하면 한 번 안내하며 소유권 인계나 새 세션을 요구하지 않습니다. 병렬 구현에는 별도 linked worktree를 사용합니다. 작업 공간의 공유 접근과 별도로 완료는 자식에서 직접 부모로 수행하고 미처리 자식을 검사합니다.

## 세션 동작

- 모든 host는 중앙 digest bundle만 사용하며 SessionStart hook이 inject context와 브랜치 context를 보고합니다.
- 소비자 `AGENTS.md`, `CLAUDE.md`, host hook·skill·설정 사본은 우선순위로 덮지 않습니다. launcher가 시작 전에 탐지해 거부합니다.
- Codex와 Claude Code의 Stop hook 및 OpenCode의 `session.idle`은 세션 로그를 수집하되 대화를 차단하지 않습니다. 새 bundle에서 V3 finish/close 계약을 사용하지 않습니다.
- 세 호스트 모두 managed file 편집과 명시적인 shell write를 차단합니다.
- 세 호스트 모두 공통 UserPrompt/PostTool 상태로 구현 승인, 관련 skill 확인과 역할별 재사용·인접 구현 탐색을 기록하며, 조건을 갖추기 전 source mutation을 차단합니다.
- Git 변경은 현재 bundle의 `git_operations.py`가 승인된 정확한 명령·위치·상태를 실행 직전에 다시 검사합니다. 일반 Git 변경을 요청하면 guard가 보호 실행 명령을 제시합니다.
- `status`, `diff`, `log`, branch 목록과 `worktree list`는 승인 없이 조회합니다. 일반 lint/test/build도 별도 Git 승인이 필요 없습니다.
- source 구현 승인과 Git 실행 승인을 구분합니다. 다른 host·세션의 로그는 읽기 전용이며 branch·worktree 소유권은 없습니다.
- 중앙 원본을 바꾼 뒤에는 실행 중인 세션을 handoff하고 새 세션을 시작해야 현재 source digest의 새 bundle을 선택합니다. 기존 세션 resume은 이전 bundle을 유지합니다.

## 역할과 병렬 세션

- role이 없는 직접 실행은 지원하지 않습니다. 중앙 launcher에서 선택한 role은 이미 확인된 세션 계약으로 사용합니다.
- Claude Code, Codex, OpenCode 어느 호스트도 특정 역할을 기본 소유하지 않습니다. inject 세션에서 역할을 바꾸려면 해당 `--role`로 새 세션을 시작합니다.
- inject profile은 `logic`(데이터·상태·API), `ui`(화면·스타일·접근성), `orchest`(조사·계획·승인), `review`(변경 없는 검토), `generate`(승인된 handoff·branch scope 구현)입니다. 이 값은 session 문서 바인딩용이며 branch task의 반복 가능한 역할 metadata와 자동으로 동일시하지 않습니다.
- handoff의 `next_role`은 다음 역할의 제안이며 자동 권한이 아닙니다. role이 없는 세션은 사용자에게 다시 확인하고, inject 세션은 선택된 role과 다르면 올바른 role로 재시작합니다.
- 모든 host·role이 사용자 승인 후 Git을 실행할 수 있습니다. Git lock은 실제 실행 구간에만 유지하며 세션 소유권으로 사용하지 않습니다.
- `owner`는 plan·final-summary, `contributor`는 handoff를 기록합니다. 산출물 책임은 Git 실행 권한이 아닙니다. 다른 host·세션의 기록은 읽기 전용이고 보조 문서는 자기 세션의 `unknown/`에 둡니다.

## 보호 명령 승인 방식

- 아래 승인은 저장소를 변경하는 Git 명령에만 적용합니다. 읽기 전용 Git 조회는 허용하며, 해석할 수 없는 Git 형태는 변경형으로 간주해 fail-closed합니다.
- Codex·OpenCode: 보호 실행기에 대기 중인 정확한 작업을 `명령 실행 승인`으로 승인합니다. `진행`·`Proceed`는 구현 승인입니다.
- Claude Code: 보호 실행의 `PreToolUse`가 `ask`를 반환하며 native 권한 UI에서 결정합니다.
- 일반 Git 변경은 동일한 보호 실행기로 연결합니다. 승인 후 관련 HEAD·index·검토한 변경·새 자식이 달라지면 다시 검토합니다. 무관한 로그 갱신은 재승인 사유가 아닙니다.
- lint·test·build는 별도 Git 승인 범위가 아닙니다.

push·clean·현재 HEAD의 변경 복원 등도 대상과 영향을 보고 승인받습니다. 완료 관계를 우회하는 ref 갱신·이력 재작성은 초기 자동 완료 경로에서 지원하지 않습니다. 완료 통합은 ff-only 또는 승인된 일반 merge를 사용합니다.

OpenCode V2는 `permission`/`bash` 대신 `permissions`/`shell` 규칙 배열을 사용합니다. 현재 adapter는 설치된 OpenCode 1.18.25의 V1 스키마를 대상으로 하므로 V2로 올릴 때 config renderer와 smoke test를 함께 마이그레이션해야 합니다.

`전부 승인`과 `모두 승인`은 보고된 구현 계획에 대한 승인으로만 기록합니다. Codex의 정확한 shell 명령 1회 승인을 대신하지 않습니다.

정책 훅이 저장소 루트와 branch 계약을 찾기 위해 수행하는 내부 읽기 전용 저장소 확인도 같은 조회 분류를 사용합니다.

## 중앙 로그 운영

- 활성 세션 중에는 실제 worktree의 소비자 로그가 원본이며 중앙 로그는 실행 호스트별 Git 이력용 사본입니다. 수행 역할은 산출물 metadata에 기록합니다.
- 자동 수집 실패는 stderr에 표시하고 다음 Stop 또는 `session.idle`에서 다시 시도합니다. 필요하면 중앙 저장소에서 `collect-logs`를 직접 실행합니다.
- `logs/**`는 정책 source digest에서 제외하며 중앙 로그를 정책 실행 원본으로 사용하지 않습니다.
- 중앙 로그도 일반 파일처럼 검토 후 사용자가 승인한 Git 명령으로 커밋합니다.


## 세션 재개와 오류 복구

Codex writable home과 승인 상태는 중앙 state의 assignment별로 분리됩니다. `start` 출력의 assignment ID를 보관하고 동일 세션은 `start --project <project> --host <host> --role <role> --resume-assignment <id>`로 재개합니다. 기존 정책 bundle을 검증하여 그대로 사용하며 새 정책으로 교체하지 않습니다. 정책 업데이트는 handoff 후 새 start로 적용합니다.

일반 질문·compact는 승인을 철회하지 않습니다. 구현 계획과 개별 Git 승인은 독립적이며 Git 승인은 실제 workdir·명령·관련 상태에 묶입니다. `sessions --project <project> --json`과 resume 출력에서 원래 bundle과 현재 중앙 정책의 차이를 확인합니다.

완료는 `review → complete → execute`로 진행합니다. 형제·하위·삭제 이력·미커밋 변경 검토와 병합 승인을 한 보고에 묶습니다. 승인에 포함한 로컬 정리는 검증·로그 보존 후 안전할 때 수행합니다. 실패하면 병합을 되돌리지 않고 정리만 보류하며 `recover <operation-id>`로 같은 작업을 재검증합니다. CLOSED 전환은 요구하지 않습니다.

과거 V3 maintenance·integration-recover·close-recover 명령은 이전 실행 기록의 운영 복구용입니다. 새 세션의 접근 권한이나 완료 경로로 사용하지 않습니다. 소비자 정책 잔존물은 실제 경로와 기존 작업을 확인한 별도 적용 계획으로 처리합니다.

호스트 이벤트 등록은 adapters의 events.json(Codex·Claude)과 OpenCode plugin이 소유합니다. 공통 runtime의 이벤트 판정·결과 정규화·상태 저장, branch workflow의 실제 Git 실행을 분리합니다. OpenCode의 안전한 기본 Git 조회는 별도 승인 없이 사용하되 복잡한 global option이나 host가 안전하게 구분하지 못하는 형태는 승인 요청을 유지합니다.


새 세션은 handoff와 현재 Git 상태를 읽고 같은 branch/worktree에서 이어갈 수 있습니다. Git 소유권 인계는 필요 없습니다. 산출물·native session의 명시적 assignment 인계는 별도 기록 처리이며, 다른 세션의 로그나 구현 승인을 자동 복제하지 않습니다.

Codex/Claude hook payload는 각각 [Codex hooks](https://learn.chatgpt.com/docs/hooks), [Claude hooks](https://code.claude.com/docs/en/hooks)를 기준으로 정규화합니다. OpenCode는 [plugin 이벤트](https://opencode.ai/docs/plugins/)에 연결합니다. 성공 이벤트와 실패 결과를 구분하며, 성공 여부를 확인할 수 없는 결과는 탐색 완료 근거로 사용하지 않습니다.


미확인 tool 예약은 `assignment-recover`, 실패한 병합의 중단은 `integration-recover`로 현재 상태와 복구 SHA를 먼저 검토합니다. 검토한 SHA를 `--approved-sha256`으로 명시한 실행만 상태를 변경합니다. 구체적인 이벤트 흐름, 복구 절차, 검증 결과와 소비자 이관 범위는 [runtime 개선 보고](docs/runtime-remediation-2026-09-08.md)에 정리했습니다.
