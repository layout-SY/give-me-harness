# 구현 로그

## 승인된 범위

앞서 제시한 Codex 런타임 흐름 수정안: SessionStart JSON, deprecated 설정 검증, Stop 무한루프, 읽기 전용 Git 조사, 산출물 쓰기 교착, 승인 문구와 Codex agent schema 보완.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `policy/common/AGENT_POLICY.template.md` | 읽기 전용 조사와 명시적 완료 lifecycle을 분리하고 승인 문구를 명확화 | 일반 조사 종료가 산출물 gate를 실행하지 않음 |
| `policy/guards/managed_policy_guard.py` | Codex SessionStart native JSON 출력, legacy documentation-stop 비차단, 공통 Git 분류 사용 | invalid JSON과 종료 continuation 제거 |
| `policy/guards/managed_policy_guard.py` | 현재 세션의 artifact-only 구조화 쓰기를 branch 계약 검사와 분리 | 손상된 승인 식별자를 문서화할 수 있고 source 쓰기는 계속 차단 |
| `policy/guards/branch_guard.py` | branch/worktree 포함 조회형 Git 명령 분류 추가 | 조회는 승인·구현 gate 없이 허용, 미분류는 fail-closed |
| `lib/agent_policy/core.py` | Stop의 blocking documentation hook 제거, agent TOML 감사 추가 | 렌더된 세 호스트 lifecycle 일관성 확보 |
| `adapters/codex/files/.codex/agents/*.toml` | 지원 필드 `developer_instructions` 사용 | Codex agent 설정 schema 정상화 |
| `adapters/opencode/files/.opencode/plugins/agent-policy.js` | idle 시 blocking 문서 검사 제거 | OpenCode에서도 종료 반복 방지 |
| `tests/` | 문제별 회귀 테스트 추가·수정 | 111개 전체 테스트 통과 |
| `README.md`, `docs/` | 증상, lifecycle, sync/inject 재시작 절차 문서화 | 운영자가 같은 오류를 진단할 수 있음 |

## 재사용한 자산과 새로 만든 자산

- 기존 guard, renderer, branch workflow와 unittest fixture를 재사용했다.
- 별도 런타임 모듈이나 외부 패키지는 추가하지 않았다.
- 새 자산은 문제별 회귀 테스트와 운영 문서 항목뿐이다.

## 핵심 로직·요청 처리

- SessionStart에서 Codex에만 native JSON context를 반환하고 다른 호스트는 기존 plain text를 유지한다.
- Stop은 로그 수집만 수행한다. 산출물 완성은 finish-proposal/finish/verify/close/preserve에서 검증한다.
- Git parser가 모든 Git 호출을 분류하고 하나라도 변경형·미분류이면 승인 대상으로 처리한다.
- 구조화된 현재 세션 산출물 Write는 V3 branch proposal 재승인을 요구하지 않는다.
- V3 proposal 식별자를 고의로 손상시킨 회귀 테스트에서 산출물 Write는 허용하고 source Write는 동일 오류로 거부한다.

## 결정 사항

- `stop_hook_active`에 따른 횟수 제어 대신 Stop 차단 자체를 제거했다.
- `전부 승인`과 `모두 승인`은 구현 승인으로만 인정하며 정확한 shell 명령 1회 승인을 대신하지 않는다.
- deprecated key는 중앙 렌더 감사에서 재발을 차단한다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| `git diff --check main...HEAD` | PASS |
| `python3 -m unittest discover -s tests -v` | PASS, 111/111 |
| `bin/agent-policy audit` | PASS, central/admin-ui/user-ui |
| `bin/agent-policy diff --project all` | 실행 완료, 두 소비자 모두 `current=false`; sync 미실행 |

## 알려진 위험과 제한

- 소비자 diff는 누적 정책 전체라 배포 영향이 크다.
- 사용자 전역 Codex 설정에 deprecated key가 남아 있으면 sync 후에도 경고가 계속될 수 있다.
- 현재 commit은 task branch에 있고 main 병합과 sync는 아직 수행하지 않았다.

## 다음 담당자 인계

현재 산출물을 포함해 branch 상태를 확인한 뒤 별도 승인을 받아 main 병합한다. 이후 소비자 diff를 재검토하고 sync 승인, 기존 세션 handoff, 신규 session start 순서로 배포한다.
