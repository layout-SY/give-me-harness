# asan-prompt-core

`asan-metaverse-user-ui`와 `asan-metaverse-admin-ui`가 함께 사용하는 시스템 프롬프트의 단일 원본이다. 두 프로젝트의 `AGENTS.md`, `CLAUDE.md`, 스킬, 역할, 훅, 템플릿은 모두 이 저장소에서 생성되어 배포된다.

## 원칙

프롬프트 편집은 이 저장소에서만 한다. 대상 프로젝트에 배포된 파일을 직접 수정하면 다음 배포에서 덮어씌워지며, 각 프로젝트의 훅이 편집 시도를 종료 코드 2로 차단한다.

## 구조

```
source/
  common/            세 호스트가 공통으로 사용하는 원본
    AGENTS.md        → 프로젝트 루트 AGENTS.md
    CLAUDE.md        → 프로젝트 루트 CLAUDE.md
    skills/          → .agents/skills/
    roles/           → .harness/roles/
    hooks/           → .codex/hooks/, .claude/hooks/, .opencode/plugins/
  hosts/
    codex/           → .codex/
    claude/          → .claude/
    opencode/        → .opencode/
build/               주입 번들 생성물. 언제든 삭제해도 재생성된다
logs/                각 프로젝트 세션 산출물의 조회용 사본. 정본은 프로젝트에 있다
state/               호스트 런타임 상태. Codex 세션 이력과 메모리가 쌓이며 삭제하면 복구할 수 없다
reserved/            대상 프로젝트 고유 자산 보관 (오버레이 기능 도입 전까지 대기)
docs/                설계 연구 문서. 도입하지 않은 검토 결과를 포함한다
targets.json         배포 대상 목록
MANIFEST.json        배포된 파일과 SHA-256 기록
bin/sync.py          배포 및 정합성 검사 도구
```

`common/hooks/harness_core.py`가 호스트 중립 판정 로직을 담고, 각 호스트 디렉터리의 `harness_hook.py`는 필요한 산출물 목록만 지정하는 얇은 진입점이다. Codex와 OpenCode는 8종 산출물을, Claude Code는 `handoff.md` 하나를 요구한다.

## 사용법

```sh
python3 bin/sync.py status                    # 대상별 배포 상태
python3 bin/sync.py deploy --target all --dry-run # 적용 전 실제 diff 확인
python3 bin/sync.py deploy --target all       # 중앙 원본을 모든 대상에 배포
python3 bin/sync.py deploy --target user-ui   # 특정 대상만 배포
python3 bin/sync.py check --target all        # 프로젝트 측 임의 수정 검사
python3 bin/sync.py start --target user-ui --host codex
python3 bin/sync.py start --target admin-ui --host claude --model sonnet
```

`check`는 현재 중앙 원본을 다시 렌더링해 프로젝트 파일과 비교한다. 중앙 원본만 수정하고 아직 배포하지 않은 상태, 프로젝트에서 수정된 파일, 누락·회수 대상과 MANIFEST 불일치를 보고하고 문제가 있으면 종료 코드 1을 반환한다.

`start`는 대상 정책을 먼저 동기화한 뒤 선택한 실행 호스트를 대상 프로젝트에서 시작한다. `--host`는 Codex, Claude Code, OpenCode 실행기를 선택하고 `--model`은 해당 호스트에 전달할 모델을 별도로 선택한다.

## 두 가지 적용 방식

### 주입 (inject) — 기본

대상 프로젝트에 파일을 남기지 않는다. 중앙에서 호스트 번들을 만들고 실행 인자로 정책을 전달한다.

```sh
python3 bin/sync.py start --target user-ui --host claude
python3 bin/sync.py start --target user-ui --host codex
python3 bin/sync.py start --target user-ui --host opencode
python3 bin/sync.py start --target user-ui --host claude --dry-run   # 실행 인자만 확인
```

`build/<target-id>/` 아래에 번들이 생성된다. Claude Code 는 `--setting-sources user`로 프로젝트 로컬 설정을 배제하고 `--plugin-dir`로 스킬·에이전트·훅을, `--append-system-prompt`로 `AGENTS.md`와 `CLAUDE.md`를 받는다. Codex 는 `CODEX_HOME`으로 전용 홈을 사용한다.

번들 안의 프롬프트는 프로젝트 이름과 명령어 토큰이 치환되고, 스킬 참조 경로가 번들 절대 경로로 재작성된다. 따라서 대상 프로젝트에 `AGENTS.md`, `.agents/`, `.claude/`, `.codex/`가 하나도 없어도 동작한다.

반드시 이 런처로 세션을 시작해야 한다. 호스트를 직접 실행하면 중앙 정책이 적용되지 않는다.

세 호스트 모두 주입을 지원한다.

| 호스트 | 주입 방식 |
| --- | --- |
| Claude Code | `--setting-sources user`로 프로젝트 설정 배제, `--plugin-dir`로 스킬·에이전트·훅, `--append-system-prompt`로 지침 |
| Codex | `CODEX_HOME`으로 전용 홈 지정. 세션 이력은 `state/<target-id>/codex-home/` 에 쌓인다 |
| OpenCode | `OPENCODE_CONFIG_DIR`로 전용 설정 디렉터리 지정, `OPENCODE_DISABLE_PROJECT_CONFIG=1`로 프로젝트 설정 배제 |

### 배포 (deploy)

중앙 원본을 대상 프로젝트 안으로 복사한다. 호스트를 직접 실행해도 정책이 적용되고, 클론만으로 프롬프트가 따라온다. 대신 생성물이 프로젝트에 남는다.

```sh
python3 bin/sync.py deploy --target all
python3 bin/sync.py check --target all
python3 bin/sync.py start --target user-ui --host claude --mode deploy
```

## 세션 산출물 보관

작업 산출물의 정본은 각 프로젝트의 `.codex/logs/sessions/{YYYY-MM-DD-task-slug}/` 다. 중앙은 조회용 사본만 보관한다.

```sh
python3 bin/sync.py collect --target all
```

`start` 는 세션을 시작하기 전에 이 수집을 자동으로 실행한다. 복사는 프로젝트에서 중앙으로만 향하며, 중앙 사본을 고쳐도 프로젝트로 되돌아가지 않는다. 프로젝트에서 사라진 기록도 중앙에서는 지우지 않는다.

사본은 `logs/<target-id>/sessions/` 아래에 대상별로 분리되므로 같은 이름의 세션이 서로 덮어쓰지 않는다. 모든 세션이 중앙 저장소 조회 권한을 갖기 때문에, user-ui 세션에서 admin-ui 의 `handoff.md` 를 읽는 식의 교차 참조가 가능하다.

## 프롬프트를 수정하는 절차

1. 작업 중인 세션에서 프롬프트 수정이 필요하다는 안내를 받는다.
2. 이 저장소의 `source/` 아래 대응 경로를 수정한다.
3. `python3 bin/sync.py deploy --target all`을 실행한다.
4. 작업 중이던 세션을 인계 처리하고 새 세션을 시작한다.

실행 중인 세션에는 반영되지 않는다. 프롬프트는 세션 시작 시점에 적재되므로 반드시 재시작해야 한다.

## 연구 문서

- `docs/role-scoped-sessions.md` — 런처에 `--role` 을 더해 세션별 담당 범위를 지정하는 방안. 관심사가 섞인 파일에서 경계 판정이 불가능한 문제를 다루고, 강제 대신 관측부터 시작하는 단계적 도입을 제안한다. 도입하지 않았으며 세 호스트의 역할 배분이 확정된 뒤 재검토한다.

## 현재 범위

프로젝트 고유 프롬프트 overlay는 아직 지원하지 않는다. 두 프로젝트는 같은 행동 정책을 사용하되, 프로젝트명과 실제 실행 명령만 `targets.json`의 최소 메타데이터로 렌더링한다. Agora RTC와 TanStack Query는 현재 양쪽 프로젝트에서 모두 사용되므로 한쪽 전용 정책으로 분류하지 않는다. 실제 한쪽에만 필요한 정책은 근거 확인 후 후속 overlay 기능에서 추가한다.
