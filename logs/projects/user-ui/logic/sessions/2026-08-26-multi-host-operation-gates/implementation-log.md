# 구현 로그

## 승인된 범위

- 중앙 정책 저장소에서 호스트 중립 역할 명칭, Claude Planner/Evaluator 확장, 세 호스트 보호 명령 승인 방식과 OpenCode 호환성을 구현한다.
- 소비 프로젝트 sync, legacy 퇴역, 애플리케이션 소스 변경은 수행하지 않는다.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `policy/common/AGENTS.template.md` | Logic Session·Claude 분석 역할·보호 명령 승인 계약 추가 | 세 호스트가 같은 의미 규칙을 공유 |
| `policy/guards/managed_policy_guard.py` | Git/build/dev 분류, Codex 세션별 동일 명령 1회 승인 상태, Claude `ask` 출력 추가 | Codex와 Claude 실행 전 게이트 구현 |
| `lib/agent_policy/core.py` | Codex UserPromptSubmit 등록, OpenCode config 렌더, 관리 루트 확장 | 소비 프로젝트 출력 128개로 결정적 렌더 |
| `adapters/opencode/opencode.base.json` | OpenCode 1.18.x V1 `permission.bash` ask 규칙 | Git/build/dev 명령에 native 권한 UI 사용 |
| `adapters/claude/**` | Hephaestus를 Logic Session으로 교체하고 Planner/Evaluator를 읽기 전용 호출 단위 역할로 변경 | 전역 분석과 구현 소유권 분리 |
| `README.md` | 네 세션 운용, 호스트별 승인 방식, OpenCode V2 마이그레이션 제한 문서화 | 운영자가 세션·버전 차이를 확인 가능 |
| `tests/**` | 승인 해시·1회성·세션 격리·독립 문구·호스트 출력·OpenCode effective config 검증 | 회귀 조건 26개 단위 테스트와 smoke로 고정 |

## 결정 사항

- 모든 Git 명령을 게이트하며 lint/test는 제외한다.
- Codex는 `ask` 미지원 때문에 차단 후 `명령 실행 승인` 독립 문구를 받고 동일 SHA-256 명령을 30분 내 1회 허용한다.
- Claude는 공식 `PreToolUse: ask`, OpenCode는 native `permission.bash: ask`를 사용한다.
- 승인 상태에는 원문 명령을 저장하지 않고 명령 해시·분류·시각만 0600 파일에 저장한다.
- Planner는 다른 서브 에이전트를 호출하거나 파이프라인에 상주하지 않는다. Claude 기본 세션이 오케스트레이션한다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| `python3 -B -m unittest discover -s tests -v` | PASS, 26 tests |
| `bin/agent-policy audit` | PASS, admin-ui/user-ui 각 128 managed files |
| `bin/agent-policy diff --project all` | dry-run 성공, 두 프로젝트 모두 미동기화 상태 확인 |
| `python3 -B tests/smoke_opencode_plugin.py` | PASS, OpenCode local plugin과 Git/build/dev 권한 effective config 확인 |
| `rg --hidden -n Hephaestus ...` | 실제 중앙 원본 0건, 테스트의 금지 assertion만 존재 |
| 중앙 커밋 | `3a291fc feat: 멀티 호스트 승인 게이트와 역할 계약 확장` |

## Watcher 인계

- managed 파일 수정 차단이 보호 명령보다 먼저 적용되는지 확인한다.
- Codex 승인이 다른 명령·다른 세션·두 번째 실행으로 전이되지 않는지 확인한다.
- Claude Planner/Evaluator의 전역 읽기와 UI 구현 쓰기 경계가 섞이지 않았는지 확인한다.
- 소비 프로젝트 sync가 수행되지 않았는지 확인한다.
