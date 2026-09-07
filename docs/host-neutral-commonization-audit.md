# 호스트 중립 공통화 전수조사

## 조사 상태

- 기준일: 2026-09-03
- 범위: `policy/`, `adapters/`, `lib/`, `projects/`, `tests/`와 중앙 진입 문서
- 목적: 기존 Codex 중심 의미가 공통 정본으로 이동하는 과정에서 필요한 정책이 유실되지 않았는지 확인하고, host adapter와 Python runtime의 잔여 의존성을 제거한다.
- 결론: 역할·workflow·산출물·브랜치 의미는 공통 정본으로 보존했다. host adapter에는 실행 형식과 도구 차이만 남겼고, Codex legacy Python hook은 공통 guard로 기능을 흡수한 뒤 제거했다.

## 1. 문서 계층 조사

| 기존 분류 | 보존해야 할 의미 | 현재 공통 정본 | 처리 |
| --- | --- | --- | --- |
| 루트 진입 문서 | 역할 확인, 승인, 조사, 구현, 검토, 문서화 | `policy/common/AGENT_POLICY.template.md` | 공통 정본으로 통합 |
| host 역할 경계 | UI·Logic·통합·기획 책임과 금지 경계 | `policy/common/skills/policy/task-role-routing/references/` | host 이름을 제거해 보존 |
| 파이프라인 역할 | Planner, Publisher, Generator, Refactorer, Watcher, Evaluator, Harness | `task-role-routing/references/pipeline-roles.md` | 단계 책임으로 보존 |
| feature·refactor·hybrid·audit workflow | 단계 순서, 역할 분리, 재시도와 escalation | `task-role-routing/references/workflows.md` | 공통 workflow로 보존 |
| 승인·재사용 탐색·검증 gate | 명시적 승인, skill 확인, 기존 자산 조사, 완료 검토 | `AGENT_POLICY.template.md`, `policy/harness/SKILL.md`, 공통 guard | 의미와 기계적 차단을 분리 |
| Harness 단계 판정 | 진행 가능 여부, 누락 조건, 역할 위반, 승인, retry, escalation | `pipeline-roles.md`, 공통 `agent-output-schema.yaml` | host 자기 선언 형식 대신 공통 구조로 보존 |
| handoff와 파일 소유권 | 역할 전환, 충돌, Git 통합 담당자, 다음 역할 | `task-role-routing/references/handoff-and-ownership.md` | session assignment를 추가해 보존 |
| 산출물 형식 | 필수 8종, handoff, 포트폴리오 사례 | `policy/common/templates/`, `policy/documentation`, `policy/portfolio` | 세 host에 같은 bytes로 렌더링 |
| branch·worktree | 계보, scope, dirty 격리, merge·정리 | `policy/git-branch-strategy/`, 공통 branch runtime | V3 계약으로 대체 |

삭제한 host별 `harness/`, `workflows/`, `multi-agent-spec/` 사본에는 위 공통 문서에 없는 독립 규칙이 남아 있지 않다. 기존의 역할 고정 문구는 현재 운영 방향과 충돌하므로 의미를 보존하지 않았고, 승인·재사용·검토·retry 같은 실제 운영 규칙만 host 중립 표현으로 이동했다.

## 2. 진입 문서와 adapter 독립성

- 소비자 `AGENTS.md`와 `.agent-policy/common/AGENT_POLICY.md`는 같은 공통 정본으로 렌더링된다.
- `CLAUDE.md`는 Codex 파일을 경유하지 않는다. 공통 정본 경로를 직접 가리키며 Claude Code의 Write·Edit, 권한 UI와 native agent 형식만 별도로 설명한다.
- Codex와 OpenCode의 native agent 파일도 `.agent-policy/common/**`를 직접 참조한다.
- inject bundle은 선택 host의 진입 문서, 공통 계약, 선택 role 문서·skill, 공통 runtime과 host adapter만 포함한다. 다른 host의 adapter가 없어도 공통 계약을 읽을 수 있다.
- role은 `logic|ui|orchest|review|generate` 실행 인자로 선택하며 host 또는 model 이름과 결합하지 않는다.

## 3. Codex legacy hook 대 공통 guard

Codex에서는 같은 이벤트에 일치하는 hook이 모두 실행되며 하나의 deny도 전체 실행을 막는다. 따라서 “공통 hook을 먼저 실행하면 legacy가 덮인다”는 상속 구조를 사용할 수 없다. 공통 guard가 상위 계약이 되는 방법은 기능을 한 구현에 포함하고 legacy 등록과 파일을 제거하는 것이다.

| legacy 기능 | 공통화 결과 |
| --- | --- |
| 사용자 구현 승인 marker | 세 host의 사용자 prompt event를 공통 guard가 같은 session state로 기록하고 source mutation 전에 검사하도록 확대 |
| managed 파일 보호 | `managed_policy_guard.py`의 manifest·inject snapshot 보호로 통합 |
| skill·재사용 탐색 marker | 세 host의 공통 PostTool mode가 성공한 skill·역할별 탐색 근거를 기록하고 source mutation 전에 검사하도록 확대 |
| mutation target 검사 | 구조화된 경로, patch 경로, shell 쓰기와 branch scope 검사로 확대 |
| 세션 귀속 상태 | host·session·task·responsibility binding으로 확대 |
| source 변경 감지 | working tree뿐 아니라 승인 parent HEAD 이후 committed diff까지 검사 |
| 완료 단계 산출물 검사 | 제목-only, Grill Me 실제 데이터 행, portfolio 사례·필드 검사를 finish·verify·close·preserve의 공통 guard로 이동하고 Stop 재진입은 제거 |
| bootstrap 자체 hash | 불변 inject bundle digest와 sync manifest 검증으로 대체 |

중앙 Codex adapter의 legacy Python 파일과 기존 등록은 제거했다. 렌더 결과에는 `.agent-policy/runtime/managed_policy_guard.py`와 `.agent-policy/runtime/branch_guard.py` 한 쌍만 있고, Claude plugin과 OpenCode home도 같은 runtime bytes를 각 실행 형식에서 호출한다.

## 4. Python·JavaScript 구현 조사

| 구현 | 조사·변경 결과 |
| --- | --- |
| `lib/agent_policy/core.py` | 공통 계약·템플릿을 한 번 렌더하고 세 host native template 경로에 동일하게 투영한다. 단일 runtime guard invariant를 audit에 추가했다. |
| `lib/agent_policy/injection.py` | snapshot runtime을 직접 사용하고 host별 branch guard 사본을 만들지 않는다. 선택 role의 공통 문서를 직접 포함한다. |
| `lib/agent_policy/role_profiles.py` | role·host artifact root·responsibility를 공통 registry에서 읽는다. |
| `lib/agent_policy/cli.py` | `--role`, `--task`, `--responsibility`, `--worktree`, `--branch`, `--session-dir`를 검증하고 외부 worktree 오류 시 기본 폴더로 fallback하지 않는다. |
| `lib/agent_policy/log_mirror.py` | 8종과 handoff를 registry에서 읽고 host 미상 채널 및 각 세션의 `unknown/`을 수집한다. |
| `policy/guards/managed_policy_guard.py` | managed 파일, artifact host·session 귀속, shell 쓰기, 완료 단계 검사와 변경형 command approval을 통합한다. 읽기는 허용하고 다른 host·session 쓰기는 거부한다. |
| `policy/guards/branch_guard.py` | V3 계보·scope·Git 통합 담당자, global option parser, 사용자 전용 Git 명령과 fail-closed 분류를 담당한다. |
| `branch_workflow.py` | snapshot runtime 우선 로드, immutable create·finish proposal, ff-only merge, 검증, close와 preserve·resume 상태 전이를 담당한다. |
| OpenCode plugin | `chat.message`, `tool.execute.before|after`에서 session id, 사용자 승인과 도구 근거를 공통 guard에 전달하고, 없으면 선언된 `ASAN_SESSION_DIR` 계약으로 귀속한다. |

전수조사 중 발견해 함께 수정한 잔여 문제는 다음과 같다.

1. raw `git config`로 branch metadata를 바꿀 수 있던 경로를 차단했다.
2. 중첩 shell 또는 Git alias로 사용자 전용 명령을 숨기는 경우를 fail-closed로 처리했다.
3. `git add`와 `git commit`이 다른 host·session 산출물을 포함하지 못하도록 Git 단계에도 귀속 검사를 추가했다.
4. session id가 없는 런타임은 선언된 session directory 없이 산출물을 쓸 수 없게 했다.
5. 알려진 이름이 아닌 문서는 session root가 아니라 `unknown/` 아래에서만 허용했다.
6. 완료 검증 명령을 프로젝트의 등록된 lint·test·build argv로 한정해 shell wrapper나 임의 실행을 숨기지 못하게 했다.
7. 조회 명령으로 분류돼 있던 `git symbolic-ref`의 쓰기형과 `branch --track/-f`, `checkout|switch --orphan`, 강제 fetch refspec을 차단했다.
8. pathspec 파일, separator 없는 `git add`, unstaged 파일을 암시적으로 포함하는 `git commit -a|--only|<path>`를 차단했다.
9. 승인된 workflow도 `create`, `finish`, `verify`, `close`, `preserve`, `resume`은 계약의 Git 통합 담당자만 실행하도록 공통 guard에서 재검증한다.
10. CLOSED task 이름 재사용과 검증 뒤 target HEAD 변경을 차단해 종료 기록과 검증 대상을 불변으로 유지한다.
11. 구형 Codex 훅의 구현 승인·skill·탐색 marker를 공통 UserPrompt/PostTool 상태로 승격하고, branch create·finish 계열은 사용자가 승인한 64자리 proposal SHA-256과 일치할 때만 허용한다.
12. `preserve`는 미완료 상태의 `handoff.md`를 요구하고, contributor handoff만으로 finish·verify·close하지 못하도록 완료 workflow를 owner assignment로 제한한다.

## 5. 자동 감사와 회귀 기준

`bin/agent-policy audit`의 중앙 계약 검사는 다음을 실패 조건으로 다룬다.

- OpenCode 기준 8종 이름 또는 `owner|contributor`·`unknown` registry drift
- Claude 기준 portfolio 사례 구조 누락
- 세 host template bytes 불일치
- host별 legacy branch guard 또는 Codex legacy Python hook 재등장
- deprecated hook feature와 bootstrap marker 재등장
- host에 고정된 역할 문구 재등장
- host adapter가 가리키는 공통 경로 누락

회귀 테스트는 immutable proposal 전체 필드 digest, 40자리 parent SHA, dirty 기준 worktree 격리, stale consumer guard 무시, `git -C` 사용자 전용 명령, 승인으로 해제되지 않는 거부, ref 변경 우회형, cross-host read/write·stage 경계, `unknown/`, committed diff 기반 Stop, `preserve -> resume`과 `finish -> verify -> close` 생명주기를 검증한다.

브랜치 운영 변경의 상세 배경과 예시는 [브랜치·worktree·세션 운영 전략 V3](branch-worktree-session-strategy.md)를 따른다.
