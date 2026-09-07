# 탐색

## 요청

meeting 관련 읽기 전용 조사에서 발생한 훅 오류와 산출물 무한루프를 수정하고, parent session의 V3 자손 branch 권한 상속 정책과 충돌하지 않게 한다.

## 조사 대상 경로

- `policy/common/AGENT_POLICY.template.md`
- `policy/guards/managed_policy_guard.py`
- `policy/guards/branch_guard.py`
- `lib/agent_policy/core.py`
- `adapters/codex/files/.codex/agents/*.toml`
- `adapters/opencode/files/.opencode/plugins/agent-policy.js`
- `tests/test_branch_guard.py`, `tests/test_guard.py`, `tests/test_rendering.py`
- `README.md`, `docs/usage-guide.md`, `docs/branch-worktree-session-strategy.md`

## 현재 코드와 인접 구현의 사실

- 기존 `render_codex_hooks`와 `render_claude_settings`가 Stop hook을 중앙에서 렌더한다.
- 기존 `managed_policy_guard.py`가 세 호스트의 준비 상태·명령 승인·산출물 검증을 공통 처리한다.
- 기존 `branch_guard.py`가 Git 명령 파싱과 V3 branch 계약을 처리하므로 조회 분류를 여기서 단일화할 수 있다.
- Codex 공식 문서상 SessionStart의 JSON context는 `hookSpecificOutput.hookEventName`과 `additionalContext` 형태다.
- Codex 공식 문서상 Stop의 `decision: block`은 작업 거절이 아니라 자동 continuation 요청이다. 반복 반환하면 종료 시도가 계속 재개된다.
- 정식 feature key는 `[features].hooks`이며 `codex_hooks`는 deprecated alias다.

## 불러온 스킬

- `openai-docs`: 최신 Codex hooks와 config 계약 확인

## 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| `managed_policy_guard.py` | 확장 | 세 호스트의 정책 판정을 이미 공통 처리함 |
| `branch_guard.py` Git parser | 확장 | 구현 gate와 branch guard가 같은 조회 분류를 공유할 수 있음 |
| 기존 렌더·guard 테스트 fixture | 재사용 | 실제 생성물과 런타임 경로를 함께 검증함 |
| 명시적 finish/verify/close/preserve 검증 | 재사용 | 산출물 강제의 적절한 lifecycle 경계임 |

## 재사용하지 않은 후보와 이유

- 별도 Codex 전용 documentation guard: 공통 lifecycle 계약을 다시 중복하므로 만들지 않는다.
- Stop 재진입 횟수 제한: 증상만 완화하고 일반 종료를 계속 방해하므로 사용하지 않는다.

## 새 자산 필요 여부와 근거

- 새 런타임 모듈은 필요 없다. 기존 guard와 renderer에 회귀 테스트만 추가한다.

## 성능·의존성 영향

- Stop 시 매번 전체 산출물을 스캔하고 자동 재개하던 경로를 제거해 종료 비용과 반복 실행을 줄인다.
- Git 호출은 기존 shell parser 결과를 재사용하며 외부 의존성을 추가하지 않는다.

## 제약 조건 및 미확인 사항

- 사용자 전역 `~/.codex/config.toml`에 남은 `codex_hooks`는 중앙 저장소에서 수정하지 않는다.
- 소비자 두 프로젝트는 manifest가 없어 전체 sync diff가 크며 배포 전 별도 검토가 필요하다.

## 결론

Found existing `managed_policy_guard.py` and `branch_guard.py`. 별도 훅을 추가하지 않고 두 공통 구현을 확장하는 것이 가장 재사용 가능하며 호스트 간 판정 drift를 방지한다.
