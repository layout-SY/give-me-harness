# asan-agent-policy

두 프런트엔드 저장소가 같은 AI 작업 정책을 사용하도록 만드는 독립 중앙 원본입니다. 공통 의미는 한 번만 보관하고 Codex, Claude Code, OpenCode의 파일·훅 형식 차이는 adapter에서 처리합니다.

## 핵심 원칙

- 기준: `asan-metaverse-user-ui` Git commit `9edd378560c3c3b7f258984698202498f5c31831`
- 현재 작업 트리의 `asan-prompt-core` 배포 결과는 기준에서 제외
- admin-ui는 기준을 제공하지 않고 소비만 함
- 프로젝트별 overlay는 V1에서 지원하지 않음
- 대상 파일 수정은 중앙 프로젝트에서만 수행
- sync는 이전 manifest에 기록된 파일만 안전하게 교체·퇴역

## 구조

```text
policy/common/          공통 AGENTS와 스킬
policy/guards/          관리 파일 차단 및 drift 검사
adapters/codex/         Codex 역할·워크플로·훅 형식
adapters/claude/        Claude UI 계약·역할·훅 형식
adapters/opencode/      OpenCode 역할·plugin 형식
projects/               대상 경로·명령과 legacy 감사 스냅샷
lib/agent_policy/       결정적 렌더링과 manifest 로직
bin/agent-policy        운영 CLI
tests/                  중앙 단위 테스트
```

## 명령

```bash
bin/agent-policy audit
bin/agent-policy diff --project all
bin/agent-policy check --project all
bin/agent-policy sync --project all
bin/agent-policy start --project user-ui --host codex --model <model>
```

`sync`는 소비자 프로젝트를 변경합니다. 먼저 `diff`를 검토하고 별도 승인을 받은 뒤 실행합니다. 기존 중앙화 시도의 잔여 파일은 기본 sync에서 삭제하지 않으며, 감사 스냅샷과 SHA-256이 일치할 때만 `--retire-legacy`로 퇴역합니다.

## 세션 동작

- Codex와 Claude Code는 SessionStart hook에서 중앙 source digest와 로컬 파일 hash를 검사합니다.
- OpenCode는 plugin 로드 시 같은 검사를 사용자에게 경고하고, `start` wrapper는 drift가 있으면 실행을 중단합니다.
- 세 호스트 모두 managed file 편집과 명시적인 shell write를 차단합니다.
- 에이전트가 제안한 모든 Git 명령과 build/dev/start/preview 계열 명령은 실행 전에 사용자가 직접 판단합니다.
- 중앙 원본을 바꾼 뒤 sync하고 실행 중인 세션을 handoff한 다음 새 세션을 시작해야 합니다.

## 병렬 세션 역할

- `user-ui`와 `admin-ui`에서 Logic Session(Codex 또는 OpenCode)과 Claude UI 구현 세션을 각각 열어 네 세션을 동시에 운용할 수 있습니다.
- Claude 기본 세션이 파이프라인을 오케스트레이션하고, `planner`와 `evaluator`는 호출 단위의 서브 에이전트로 코드베이스 전체를 읽어 기능 로직까지 기획·평가하지만 구현 파일을 수정하거나 서브 에이전트를 중첩 실행하지 않습니다.
- Claude 기본 구현 세션은 계속 production UI만 수정하고, Logic Session은 기능 로직과 통합 파일을 소유합니다.
- 분석 권한과 구현 소유권을 분리했으므로 Planner/Evaluator 확장이 동일 파일 병렬 수정 권한을 만들지 않습니다.

## 보호 명령 승인 방식

- Codex: 첫 시도를 차단하고 정확한 명령을 표시합니다. 사용자가 `명령 실행 승인`만 독립된 메시지로 보내면 같은 명령을 30분 안에 한 번 실행할 수 있습니다.
- Claude Code: 중앙 `PreToolUse` 훅이 `ask`를 반환하여 호스트 권한 UI에서 사용자가 결정합니다.
- OpenCode 1.18.x: 생성된 `opencode.json`의 `permission.bash`가 명령 패턴별 권한 UI를 표시합니다. 기본적으로 `once`를 선택하고 `always`는 사용자가 의도한 경우에만 선택합니다.
- lint와 test는 이 보호 명령 범위가 아니며 기존 승인·검증 정책을 따릅니다.

OpenCode V2는 `permission`/`bash` 대신 `permissions`/`shell` 규칙 배열을 사용합니다. 현재 adapter는 설치된 OpenCode 1.18.19의 V1 스키마를 대상으로 하므로 V2로 올릴 때 config renderer와 smoke test를 함께 마이그레이션해야 합니다.

정책 훅이 중앙 manifest와 저장소 루트를 찾기 위해 수행하는 내부 읽기 전용 저장소 확인은 에이전트가 제안하는 Git 작업과 구분합니다.
