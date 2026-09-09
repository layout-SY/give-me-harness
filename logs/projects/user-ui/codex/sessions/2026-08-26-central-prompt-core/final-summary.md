# 최종 요약

## 제공 사항

- `~/SynologyDrive/asan-prompt-core` 중앙 시스템 프롬프트 저장소. user-ui 프롬프트를 단일 기준 원본으로 보유한다.
- `bin/sync.py` 배포 도구. `deploy`, `check`, `status` 세 명령으로 129개 파일을 결정적으로 배포하고 SHA-256으로 대조한다.
- 3호스트 편집 차단 훅. 중앙 관리 경로 편집 시도를 종료 코드 2로 차단하고 중앙 대응 경로와 재시작 절차를 안내한다.
- 산출물 강제 훅. Codex와 OpenCode는 8종, Claude Code는 `handoff.md`를 요구한다.
- user-ui 프롬프트 교정. 사용자가 확정한 D1~D8 결정을 `AGENTS.md`와 `CLAUDE.md`에 반영했다.
- admin-ui 배포. 두 프로젝트의 관리 대상 129개 파일이 해시 수준에서 동일해졌다.
- admin-ui `package.json`에 `test` 스크립트 추가. 두 프로젝트 모두 `npm run test`로 거버넌스 훅을 검증한다.

## 제외 사항

- 프로젝트 고유 오버레이. user-ui의 Agora RTC, admin-ui의 TanStack Query 관련 프롬프트는 `reserved/`에 보관만 했다.
- `.agents/skills/**` 얇은 스킬 본문 보강.
- `asan-harness` 재사용 및 정리.
- 애플리케이션 코드 변경.

## 검증

| 명령어 | 결과 |
| --- | --- |
| `python3 test_governance_hooks.py` | 20 tests OK |
| 훅 오탐·차단 시나리오 8종 | 전부 기대값 일치 |
| 세션 자동 귀속 | 두 세션 분리 판정 확인 |
| `python3 -m unittest discover -s tests` (중앙) | 29 tests OK |
| `python3 bin/sync.py check --target all` | user-ui 정합 129개, admin-ui 정합 129개 |
| MANIFEST 해시 대조 | 경로 집합 동일, 해시 불일치 0건 |
| 훅 차단 4종 | 관리 경로 exit 2, 비관리 경로 exit 0 |
| Stop 훅 3종 | 8종 완비 exit 0, 미작성 exit 2, 재진입 방지 exit 0 |
| drift 검출 | 임의 수정 후 exit 1, 재배포 후 정합 |
| `npm run lint` | 통과 |
| `npm run build` | 통과 |
| `npm run test` (user-ui) | 2 failed / 209 passed. 실패는 사전 존재 |
| `npm run test` (admin-ui) | 11 tests OK |

## 산출물

`.codex/logs/sessions/2026-08-26-central-prompt-core/` 아래 8종을 작성했다.

## 주입 방식 (사용자 추가 요청)

대상 프로젝트에 파일을 남기지 않고 중앙 정책만 주입하는 실행 경로를 추가했다.

```sh
python3 bin/sync.py start --target user-ui --host claude
python3 bin/sync.py start --target user-ui --host codex
```

Claude Code 는 `--setting-sources user`로 프로젝트 로컬 설정을 배제하고 `--plugin-dir`로 스킬·에이전트·훅을, `--append-system-prompt`로 지침을 받는다. Codex 는 `CODEX_HOME`으로 전용 홈을 사용한다. 빈 Git 디렉터리에서 에이전트 6종, 스킬, 8종 산출물 규칙, 훅 실행이 모두 확인되었다.

기존 배포 방식은 `deploy` 명령과 `start --mode deploy`로 유지된다.

## 역할 범위 세션 연구

`docs/role-scoped-sessions.md` 에 `--role` 도입 방안을 정리했다. 관심사가 혼재된 파일에서 경로 기반 판정이 불가능함을 저장소 실제 코드로 규명하고, 강제와 관측을 분리한 4단계 도입안과 도입 판단 기준을 제시했다. 검증 과정에서 테스트 코드의 모킹 경계가 역할 경계와 일치함을 확인했다. 도입하지 않았으며 세 호스트의 역할 배분 확정 후 재검토한다.

## 남은 제한 사항

1. **OpenCode 플러그인 미검증** — 사용자 지시로 이번 범위에서 제외했다. Python 브리지는 codex와 동일하나 JS 어댑터 실행은 확인하지 않았다.
2. **admin-ui 잔여 고유 스킬** — `tanstack-query`와 일부 컴포넌트 참고 스킬이 인덱스에 없는 채 남아 있다. 사본은 `reserved/admin-ui/`에 있다.
3. **프로젝트 고유 오버레이 부재** — 두 프로젝트가 완전히 동일한 프롬프트를 사용한다. 스택 차이를 프롬프트에 반영할 수단이 없다.
4. **훅 무결성 검증 축소** — 기존 SHA-256 부트스트랩을 재도입하지 않았다. `sync.py check`가 부분적으로 대신한다.
5. **사전 존재 테스트 실패 2건** — `meeting.api.test.ts`의 `resolveApiBaseUrl` 관련 실패로 이번 범위 밖이다.
6. **셸 명령 내 코드 예시 오탐** — 명령 문자열에 코드가 포함되면 정적 패턴이 실제 쓰기로 오인한다. 검증 스크립트를 파일로 분리해 회피했으며 근본 해결은 아니다.

## 후속 감사와 정본 확정

이 세션의 구현 이후 별도 작업자가 중앙 저장소를 감사하여 개선판을 만들었고, 사용자가 개선판을 정본으로 확정했다. 이 세션의 원본은 `~/SynologyDrive/asan-prompt-core.pre-audit-20260826-204040`에 보존되어 있다.

감사에서 교정된 이 세션 구현의 결함은 다음과 같다.

| 결함 | 내용 | 교정 |
| --- | --- | --- |
| `check` 탐지 범위 | MANIFEST 해시와 프로젝트 파일만 비교하여 중앙 원본 수정을 탐지하지 못했다 | `expected_files()`로 원본에서 매번 재계산 |
| `apply_patch` 우회 | `tool_target()`이 경로를 하나만 반환하여 다중 파일 패치의 나머지 관리 경로가 통과되었다 | `tool_targets()`가 패치 헤더의 모든 경로를 추출 |
| 프로젝트 사실 하드코딩 | `asan-metaverse-user-ui`와 명령어가 고정되어 admin-ui에 사실과 다른 지침이 배포되었다 | `{{PROJECT_NAME}}`, `{{PROJECT_COMMANDS}}` 토큰 치환 |
| 호스트 선택 세션 시작 부재 | 사용자 원 요구사항인 호스트 선택 시작을 구현하지 않았다 | `sync.py start --target <id> --host <host>` |
| `SessionStart` 훅 부재 | 계획에 포함했으나 구현하지 않았다 | 세션 시작 시 정합성 검사와 안내 |
| 회수 미지원 | 중앙에서 삭제한 원본이 프로젝트에 남았다 | 회수 대상 탐지 |
| 기타 | `filePath`/`notebookPath` 키 누락, `--dry-run` 부재, 중앙 저장소 자체 지침과 `sync.py` 테스트 부재 | 모두 추가 |

정본 확정 후 `check --target all`이 양쪽 정합 129개, 중앙 `unittest` 4종 통과를 확인했다.

## 다음 단계

1. 두 프로젝트에서 배포 결과를 검토하고 커밋한다.
2. 새 세션을 시작해 훅이 실제 호스트에서 동작하는지 확인한다.
3. 오버레이 기능을 설계해 프로젝트별 스택 사실을 프롬프트에 반영한다.
4. 스킬 본문을 보강한다.
