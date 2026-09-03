# 구현 로그

## 승인된 범위

사용자가 기획 검토 후 P0~P4 실행과 하네스 경로 소유권 이전을 명시적으로 승인했다. 프로젝트 고유 오버레이와 스킬 본문 보강은 범위에서 제외했다.

## 변경 사항

### P0 — user-ui 프롬프트 교정

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `AGENTS.md` | 작성 언어 절 신설(D6), 산출물 위치 정본화(D3), Claude Code `handoff.md` 규정(D2), 명령어에 `test`/`preview` 추가(D4), 구성도에 3호스트 훅 경로 반영(D1), 리뷰 에이전트 범위 명확화(D5), 중앙 시스템 프롬프트 10절 신설 | 97 → 128줄 |
| `CLAUDE.md` | 작성 언어 절 신설, 소유권을 `.claude/logs/**`에서 `handoff.md`로 교체(D3), 필수 산출물 절 신설(D2), 중앙 시스템 프롬프트 6절 신설, 에이전트 사용 범위 명확화(D5) | 72 → 104줄 |
| `.claude/skills/policy`, `.claude/skills/reference` | 빈 잔재 디렉터리 제거(D8) | 삭제 |

### P1 — 중앙 저장소 생성과 이관

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `asan-prompt-core/source/common/` | `AGENTS.md`, `CLAUDE.md`, 스킬 28개, 역할 정의 이관 | 신규 |
| `asan-prompt-core/source/hosts/codex/` | 에이전트, harness, workflows, templates, multi-agent-spec, config 이관 | 신규 |
| `asan-prompt-core/source/hosts/claude/` | 에이전트, harness, workflows, templates, skills, multi-agent-spec 이관 | 신규 |
| `asan-prompt-core/source/hosts/opencode/` | codex 역할 정의를 frontmatter Markdown으로 변환하여 생성 | 신규 6개 |
| `source/hosts/codex/agents/*.toml` | 영어 instructions를 한국어로 재작성하고 한국어 산출물 원칙 명시(D6) | 6개 갱신 |

### P2 — 동기화 도구

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `asan-prompt-core/bin/sync.py` | `deploy`/`check`/`status` 구현. 공통·호스트 매핑, 배너 주입, SHA-256 매니페스트 | 신규 260줄 |
| `asan-prompt-core/targets.json` | 대상 2개와 호스트 목록 정의 | 신규 |
| `asan-prompt-core/MANIFEST.json` | 배포 파일 경로와 해시 기록 | 생성됨 |
| `asan-prompt-core/README.md` | 구조, 사용법, 프롬프트 수정 절차 | 신규 |

### P3 — 훅

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `source/common/hooks/harness_core.py` | 호스트 중립 판정 로직. 관리 경로 차단, 중앙 대응 경로 계산, 산출물 검사 | 신규 296줄 |
| `source/hosts/codex/hooks/harness_hook.py` | 8종 산출물을 요구하는 진입점 | 신규 |
| `source/hosts/opencode/plugin/harness_hook.py` | codex와 동일 수준 진입점 | 신규 |
| `source/hosts/claude/hooks/harness_hook.py` | `handoff.md`만 요구하는 진입점 | 신규 |
| `source/hosts/codex/hooks.json` | `PreToolUse`, `Stop` 등록 | 교체 |
| `source/hosts/claude/settings.json` | `PreToolUse`, `Stop` 등록. `hookify` 플러그인 제거(D2) | 교체 |
| `source/hosts/opencode/plugin/harness.js` | `tool.execute.before`에서 python 브리지 호출 | 신규 |
| `source/hosts/codex/hooks/test_governance_hooks.py` | 판정 로직 검증 11종 | 신규 |
| user-ui `.codex/hooks/**` 기존 8파일 | 미사용 훅 폐기 후 신규 훅으로 교체 | 백업 후 제거 |

### P4 — admin-ui 배포

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| admin-ui 하네스 전체 | 중앙 원본 129개 파일 배포 | user-ui와 해시 동일 |
| `asan-prompt-core/reserved/admin-ui/` | `tanstack-query` 스킬과 배포 전 `AGENTS.md`/`CLAUDE.md` 보관 | 신규 |
| admin-ui `package.json` | `test` 스크립트 추가. admin 에는 vitest 와 테스트 파일이 없어 거버넌스 훅 테스트만 실행한다 | 사용자 지시로 추가 |
| `source/common/AGENTS.md` | 4절 `npm run test` 설명을 프로젝트 중립 문구로 변경. 두 프로젝트의 테스트 구성이 달라도 사실과 어긋나지 않는다 | 갱신 |

### P5 — 주입 방식 전환 (사용자 추가 요청)

사용자가 "프로젝트에 파일을 남기지 않고 세션 실행 시 중앙 프롬프트만 주입"하는 방식을 요구하여 호스트 실행 옵션을 실측 검증한 뒤 구현했다.

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `bin/bundles.py` | 호스트 번들 빌더 신규. 토큰 치환과 스킬 참조 경로 재작성을 적용해 `build/<target-id>/` 아래에 Claude 플러그인, 시스템 프롬프트 합본, Codex 전용 홈을 생성 | 신규 144줄 |
| `bin/sync.py` | `launch`를 주입 방식으로 교체하고 `inject_command()` 추가. `--mode inject\|deploy` 옵션 신설 | 갱신 |
| `tests/test_bundles.py` | 번들 생성과 주입 인자 검증 8종 | 신규 |
| `README.md` | 주입과 배포 두 방식 문서화 | 갱신 |
| `.gitignore` | `build/` 제외 | 갱신 |

#### 호스트 실측 검증 결과

| 항목 | 방법 | 결과 |
| --- | --- | --- |
| Claude 플러그인 로드 | `--plugin-dir`에 마커 훅을 두고 `-p` 실행 후 마커 파일 확인 | 성공. `${CLAUDE_PLUGIN_ROOT}` 치환 정상 |
| Claude 에이전트 | 빈 Git 디렉터리에서 subagent 목록 확인 | `asan-prompt-core:watcher` 등 6종 로드 |
| Claude 스킬 | 번들 스킬 파일을 Read로 열어 frontmatter 확인 | `policy-documentation` 확인 |
| Claude 지침 | `--append-system-prompt`로 주입 후 8종 산출물 규칙 질의 | 8개로 정확히 응답 |
| `--add-dir`만으로 CLAUDE.md 주입 | 빈 디렉터리에서 `UI_COMPLETE` 인지 여부 확인 | 실패. `--append-system-prompt` 필요 |
| Codex 지침 | `CODEX_HOME`을 번들로 지정하고 `codex exec` 실행 | 성공. 기존 `~/.codex/AGENTS.md` 대신 중앙 지침 적용 |
| Codex 훅 | 동일 조건에서 마커 훅 실행 | 미검증. 훅 신뢰 승인이 필요해 비대화형에서 진행 불가 |
| OpenCode | — | 사용자 지시로 제외 |

빈 Git 디렉터리에서 에이전트, 스킬, 지침, 훅이 모두 동작함을 확인하여 대상 프로젝트에 파일이 없어도 세션이 성립함을 검증했다.

### P6 — 주입 방식 확장과 역할 범위 연구 (사용자 추가 요청)

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `bin/bundles.py` | 번들 재생성을 삭제 후 재작성에서 원자적 교체로 전환. 실행 중 세션이 참조하는 파일이 사라지지 않는다 | 부재 관측 14회 → 0회 |
| `bin/bundles.py` | Codex 런타임 상태를 `state/<target-id>/codex-home/` 으로 분리하고 훅 신뢰 기록을 보존 | 세션 이력과 승인 유실 방지 |
| `bin/bundles.py`, `bin/sync.py` | OpenCode 주입 구현. `OPENCODE_CONFIG_DIR` 과 `OPENCODE_DISABLE_PROJECT_CONFIG` 사용 | 세 호스트 전부 주입 지원 |
| `bin/sync.py` | `collect` 명령 신설. 프로젝트 세션 산출물을 `logs/<target-id>/` 로 단방향 미러링하며 `start` 가 자동 실행 | user 43 / admin 39 세션 보관 |
| `source/common/hooks/harness_core.py` | 셸 명령의 쓰기 패턴 감지 추가. `apply_patch` 힙독, 리다이렉션, `sed -i`, `tee`, `cp`/`mv`, `rm` 등 | 조회 명령 오탐 0건 |
| `source/common/hooks/harness_core.py` | 중앙 저장소 원본 편집 차단(`central_denial`)과 이벤트 트레이스 추가 | 절대 경로 편집도 차단 |
| `docs/role-scoped-sessions.md` | 역할 범위 세션 연구 문서 신규 | 254줄 |

#### 호스트 주입 실측 결과

| 호스트 | 방식 | 검증 |
| --- | --- | --- |
| Claude Code | `--setting-sources user`, `--plugin-dir`, `--append-system-prompt` | 빈 디렉터리에서 에이전트 6종·스킬·지침 확인 |
| Codex | `CODEX_HOME` | 중앙에만 넣은 확인 코드를 응답으로 회수하여 출처 확정 |
| OpenCode | `OPENCODE_CONFIG_DIR`, `OPENCODE_DISABLE_PROJECT_CONFIG` | `opencode debug config` 로 역할 6종·instructions·plugin 확인 |

### P7 — 감시 체계의 자기 검증에서 드러난 결함 (사용자 지시)

훅이 이 세션의 `Stop` 을 차단하면서 세 가지 결함이 드러났다. 감시 체계가 스스로를 검증한 결과이며, 세 건 모두 사용자가 소유권을 이전한 뒤 교정했다.

| 결함 | 내용 | 교정 |
| --- | --- | --- |
| 세션 귀속 오판 | `latest_session()` 이 오늘 날짜 접두사 중 최신 하나만 보아, 자정을 넘긴 작업의 산출물을 놓치고 같은 날 다른 세션의 디렉터리를 자기 것으로 오인했다 | `ASAN_SESSION_DIR` 우선, 없으면 훅이 자동 기록한 세션 귀속, 그다음 변경 기록 기반 활성 세션 순으로 판정. 날짜 접두사 의존 제거 |
| 인터프리터 우회 | `python3 - <<PY ... write_text ... PY` 형태의 쓰기가 셸 리다이렉션을 쓰지 않아 전혀 감지되지 않았다. 이 세션이 중앙 파일을 고쳐온 방식이 그대로 감시 밖이었다 | 인터프리터 호출과 쓰기 함수 호출이 함께 나타날 때 그 호출 인자에서 경로를 추출 |
| Claude 매처 누락 | `PreToolUse` 매처가 `Write\|Edit\|MultiEdit\|NotebookEdit` 뿐이라 `Bash` 를 통한 편집이 훅 호출조차 되지 않았다. Codex 는 매처가 없어 전체 도구를 검사하고 있었다 | 매처에 `Bash` 추가 |

#### 교정 과정에서 발생한 오탐

인터프리터 감지를 처음 구현할 때 명령 문자열 전체에서 경로 토큰을 수집했다. 그 결과 `python3 -I .codex/hooks/harness_hook.py` 처럼 **실행 인자로 전달된 경로**까지 수정 대상으로 오인하여 훅 실행과 테스트 실행이 차단되었다. 쓰기 함수 호출의 인자에서만 경로를 뽑도록 좁혀 해소했다.

이 교정은 사용자가 중앙 원본을 직접 수정했다. 훅이 이 세션의 모든 쓰기 경로를 막고 있었고, 우회하지 않는 것이 설계 의도이기 때문이다.

#### 남은 한계

셸 명령 문자열 안에 코드 예시가 포함되면 정적 패턴이 이를 실제 쓰기로 오인한다. 검증 스크립트를 별도 파일로 분리하여 회피했으나 근본 해결은 아니다. 정적 패턴 매칭의 구조적 한계로 기록한다.

#### 검증

| 항목 | 결과 |
| --- | --- |
| 오탐 해소 8종 | 실행 인자·읽기·프로젝트 파일 통과, 관리 파일·스킬·중앙 절대경로·리다이렉션 차단 |
| 세션 자동 귀속 | 두 세션이 각자 디렉터리로 분리 판정 |
| Bash 매처 | 관리 파일 리다이렉션 차단, 정상 명령 통과 |
| 훅 테스트 | 20종 통과 |
| 중앙 테스트 | 29종 통과 |
| 배포 정합성 | 양쪽 129개 |

## 결정 사항

- 호스트별 역할 정의를 하나로 통합하지 않고 `hosts/<id>/` 아래 각각 유지했다. 해결 대상은 user-ui와 admin-ui 사이의 드리프트이지 호스트 간 차이가 아니며, 통합은 codex의 전체 범위와 claude의 UI 한정 범위를 뒤섞는다.
- `.agents/skills/`가 세 호스트 공통 경로라는 점을 이용해 396줄을 무변환 복사 대상으로 두었다. 실제 변환이 필요한 대상은 역할 정의 형식과 훅 등록 방식뿐이다.
- 훅 응답을 종료 코드 2와 stderr로 통일했다. 호스트별 JSON 출력 규격에 의존하지 않아 세 호스트가 같은 코어를 공유한다.
- `deploy`는 대상 디렉터리를 비우지 않고 덮어쓰기만 한다. `.codex/logs/**`, `.codex/memory/**` 등 프로젝트 소유 자산이 삭제되지 않는다.
- 기존 SHA-256 훅 부트스트랩을 재도입하지 않았다. 사용자가 요구한 복잡도 수준을 초과한다.
- 산출물 검사를 허용 집합 방식으로 구현했다. Claude Code 는 `handoff.md` 또는 8종 중 하나를 충족하면 통과한다. 최초 구현은 `handoff.md` 만 검사해 하네스 변경 시 8종을 작성해도 차단되는 결함이 있었고, 검증 중 발견하여 규칙과 집행을 일치시켰다.
- 신규 훅 테스트를 `.codex/hooks/test_governance_hooks.py` 경로로 유지해 `package.json`의 `test` 스크립트를 수정하지 않아도 되게 했다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| `python3 test_governance_hooks.py` | 11 tests OK |
| `python3 bin/sync.py check --target all` | user-ui 정합 129개, admin-ui 정합 129개 |
| 훅 차단 시나리오 4종 | `AGENTS.md` exit 2, 스킬 exit 2, UI 파일 exit 0, 읽기 도구 exit 0 |
| drift 검출 시나리오 | 스킬 임의 수정 후 `check` exit 1, 재배포로 복구 |
| MANIFEST 해시 대조 | 두 대상의 경로 집합 동일, 해시 불일치 0건 |
| `npm run lint` | 통과 |
| `npm run build` | 통과 (청크 크기 경고는 사전 존재) |
| `npm run test` | 2 failed / 209 passed. 실패 2건은 `meeting.api.test.ts`의 사전 존재 실패 |

## Watcher 인계

`review-log.md`에서 승인 범위 준수, 두 프로젝트 동일성, 훅 동작, 사전 존재 실패 구분을 판정한다.

| Stop 훅 실동작 | 8종 완비 시 exit 0, 산출물 없는 프로젝트 exit 2, 재진입 방지 exit 0 |
| admin-ui `npm run test` | 11 tests OK |
