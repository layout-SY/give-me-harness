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
- 중앙 원본을 바꾼 뒤 sync하고 실행 중인 세션을 handoff한 다음 새 세션을 시작해야 합니다.
