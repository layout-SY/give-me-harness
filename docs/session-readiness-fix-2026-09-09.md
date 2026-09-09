# 기존 브랜치의 새 세션 준비 상태와 Codex 읽기 회귀 수정

## 결과

기존 V3 task에서 새 세션으로 이어갈 때 구현 승인·스킬·탐색 조건을 먼저 안내하고, 종료된 다른 task의 역할·scope가 새 작업에 섞이지 않도록 공통 guard를 수정했다. Codex의 성공한 스킬·공용 UI 읽기가 기록되지 않았던 보고는 기존 이벤트 보정 코드로 해결되는 것을 별도 회귀 테스트로 고정했다.

## 확인한 장애

문제 assignment는 `67e2d7b272644e31996cf91abc67439c`, native session은 `01a08164-410d-72e1-9ea2-90f837e5ceaa`다. 실행 번들은 `build/user-ui/codex-logic-5d4898e41ff87790`이었다.

- 해당 번들에는 현재 중앙 원본의 Codex 문자열 결과 보정 코드가 없다. 실제 종료 코드가 0인 스킬·공용 UI 읽기 완료 기록을 대조했을 때 구형 판정은 `None`, 현재 중앙 판정은 `True`였다. 형식과 기존 수정 책임은 [Codex 읽기 근거 누락 수정](codex-read-evidence-fix-2026-09-08.md)에 정리되어 있다.
- 새 assignment는 `role=logic`, `task=""`였지만 기본 폴더에는 `CLOSED` 상태의 `task/meeting-reserve-ui`가 남아 있었다. `requires_ui_exploration`과 `approval_scope`가 이 브랜치를 참조해 UI 탐색과 이전 scope를 요구했다.
- 사용자 대화의 이어서 작업하라는 요청은 기존 명시 승인 파서에 일치하지 않았다. 이후 전체 SHA 승인만 저장됐으며, SHA 승인은 구현 승인을 만들지 않는다. SessionStart는 branch 정보만 출력해 첫 변경 전에 이 차이를 안내하지 못했다.
- 별도 테스트에서 `--task` 없이 기존 ACTIVE 브랜치에 진입하면 첫 변경 전 승인 scope의 task가 비어 있음을 확인했다. 이때 다른 독립 브랜치로 이동해도 이전 준비 상태를 사용할 수 있었다.

## 변경 범위

| 중앙 파일 | 변경 |
| --- | --- |
| `policy/guards/approval_policy.py` | 기존 task를 첫 변경 전 승인 범위에 연결하고 CLOSED branch를 제외한다. create의 UI 조건은 proposal 역할과 현재 세션 역할에서 계산한다. 준비 조건 판정을 gate와 상태 안내가 공유한다. |
| `policy/guards/managed_policy_guard.py` | SessionStart와 branch-context에 `[SESSION_READINESS]`를 추가한다. |
| `policy/common/AGENT_POLICY.template.md` | 새 branch 생성, 기존 V3 task 이어받기, 동일 assignment 재개를 구분하고 준비 조건 확인을 명시한다. |
| `policy/common/skills/policy/git-branch-strategy/SKILL.md` | 기본 폴더의 기존 task 재진입과 준비 상태 조회 절차를 설명한다. |
| `tests/test_session_readiness.py` | 기존 fixture로 세션 진입, 승인 격리, 종료된 UI 문맥, proposal UI 조건과 bundle 교체를 검증한다. |
| `tests/test_codex_events.py`, `tests/smoke_codex_hooks.py` | SHA 승인과 실제 공용 UI 읽기의 결과를 각각 검증한다. |
| `docs/usage-guide.md` | 증상별 조치와 새 세션 적용 절차를 보완한다. |

기존 `event_protocol.py`와 Codex 어댑터의 보정 코드를 재사용했다. launcher의 새 start와 resume 동작은 이미 올바르므로 코드 변경 없이 회귀 테스트로 검증했다. 소비자 소스·기존 branch·기존 assignment 승인 상태는 변경하지 않았다.

## 회귀 검증

먼저 새 세션 테스트 6개를 현재 수정 전 원본에서 실행해 8개 실패(세 host subtest 포함)를 확인했다. 보고된 읽기 테스트는 해당 구형 runtime을 임시 fixture에 넣어 `skill_confirmed` 누락으로 실패하는 것을 확인한 뒤 현재 중앙 runtime에서 통과시켰다. 과거 build는 문제의 실행본 대조에만 사용하며 영구 테스트는 중앙 renderer와 native 이벤트 fixture를 사용한다.

- 새 세션·재개·조회 테스트: 8개 통과.
- Codex 이벤트와 관련 승인·복구 테스트: 28개 통과.
- 실제 `codex-cli 0.153.4` smoke: 스킬 읽기, 실패한 읽기, 외부 worktree 읽기, 공용 UI 읽기 모두 통과. 임시 저장소와 로컬 응답 서버만 사용했다.
- `bin/agent-policy audit`: 중앙·admin-ui·user-ui 통과.
- 실제 문제 assignment의 저장 상태를 새 판정기로 조회해 기존 SHA 보존과 Logic 탐색 조건을 확인했다. 원래 `harness-state-v3.json`의 바이트가 바뀌지 않았음도 검증했다.
- 전체 unittest: **185개 통과**, 588.659초. `git diff --check`도 통과했다.

실행 기록:

- `/private/tmp/asan-session-readiness-red.log`
- `/private/tmp/asan-reported-codex-read-red.log`
- `/private/tmp/asan-session-readiness-green.log`
- `/private/tmp/asan-readiness-extra-tests.log`
- `/private/tmp/asan-readiness-related-tests.log`
- `/private/tmp/asan-session-readiness-native/`
- `/private/tmp/asan-session-readiness-full-suite.log`
- `/private/tmp/asan-session-readiness-real-state.txt`
- `/private/tmp/asan-session-readiness.diff` — 이번 승인 이후 변경만 포함한 diff. 기존 미커밋 수정은 제외한다.

## 적용 인계

중앙 launcher의 `start --print-only`로 기본 user-ui 폴더를 사용하는 새 Logic 실행을 준비했다. 새 bundle은 `codex-logic-01f4c6f24836bba2`, 준비된 assignment는 `e9eb48848ac44b2f861db172d9e88252`다. 실제 host는 아직 열지 않았으며 기존 문제 세션도 바꾸지 않았다. 실행 정보는 `/private/tmp/asan-user-ui-readiness-launch.txt`에 있다.

새 bundle의 `approval_policy.py`, `event_protocol.py`, `managed_policy_guard.py`가 중앙 원본과 같고 manifest의 SHA-256과 일치함을 확인했다. 준비된 Codex home의 SessionStart와 PostToolUse도 이 새 bundle의 절대 guard 경로를 사용한다.

기존 작업자는 현재 작업 상태를 자기 `handoff.md`에 남긴다. 기존 assignment의 Git 소유권을 넘겨야 한다면 중앙 `assignment-handoff` 절차를 사용한다. 새 세션은 구현 승인을 자동으로 복사하지 않고 인계 계획·현재 상태와 준비 조건을 확인한다. 문제 세션의 이전 assignment를 `--resume-assignment`로 재개하면 구형 bundle을 계속 사용한다.

중앙 수정 적용 후 일반적인 새 세션 시작 명령:

```sh
bin/agent-policy start --project user-ui --host codex --mode inject --role logic --responsibility owner
```

기존 ACTIVE task가 기본 폴더에 checkout되어 있으면 `--task <기존 task> --branch <기존 task>`를 추가해 대상까지 명시한다. 이때 새 branch/worktree를 만들지 않는다. 외부 worktree 경로가 기존 계약에 고정돼 있다면 기본 폴더로 임의 이동할 수 없으며 계약에 맞는 실제 경로를 사용해야 한다.

`[SESSION_READINESS]`는 준비 상태 안내다. branch 계약 무결성, worktree 일치, 소유권, 산출물과 개별 명령 승인은 기존 PreTool 검사를 따른다. OpenCode는 시작 시 공통 guard 출력을 로그에 기록하고 compact의 branch-context에 넣으며, 첫 변경 전에는 공통 정책의 조회 절차로 상태를 확인한다.
