# 오케스트레이션과 작업 현황판

## 적용 범위

오케스트레이션은 `--role orchest`로 시작한다. 이 문서의 계약과 훅 동작은 `orchest` 세션에만 적용하고 `logic`·`ui`·`review`·`generate` 세션은 작업 전과 같게 둔다.

작업 전 커밋(`11d501b`)과 현재 버전으로 3개 호스트 × 4개 role의 번들을 만들어 비교한 결과는 다음과 같다.

| 비교 대상 | 결과 |
| --- | --- |
| 하위 에이전트 정의 | 12개 조합 모두 동일 |
| MCP 주입 | 12개 조합 모두 동일 |
| 시스템 프롬프트 | "방안을 제시해 선택받은 뒤 진행" 규칙 한 줄 추가와 요청 명확성 게이트의 선택지 문장 한 줄 변경만 다르다(사용자가 모든 세션에 요청) |
| 공통 runtime 계약(`runtime-policy.json`) | 동일 |
| 그 밖의 정책 파일 | `task-role-routing/SKILL.md`(같은 규칙), `ui`·`generate` 번들의 `publishing` 스킬(사용자 결정으로 `ui` 프로필에 추가), `generate` 번들에 들어가는 `orchestration.md`의 내용 |

guard와 보호 실행기 코드는 모든 번들이 같은 runtime을 쓰므로 함께 바뀌지만, 오케스트레이션 게이트는 번들에 `orchestration-policy.json`이 있고 세션 role이 그 계약의 role일 때만 켜진다.

오케스트레이션 전용으로 둔 위치는 다음과 같다.

| 내용 | 위치 |
| --- | --- |
| 부모의 계약 | `references/orchestration.md`, `orchest` 세션의 inject 서문 |
| 하위 에이전트 본문과 공통 계약 | `policy/common/agents/`, `policy/common/CHILD_AGENT_CORE.template.md`. `orchest` 세션을 시작할 때만 host adapter의 이름·설명과 합쳐 설치한다 |
| 계약 값(대상 role, 현황판 단계, 문서, 예외 문구, 실행기 명령, 작업별 산출물 폴더) | `policy/common/contracts/orchestration-policy.json`. `orchest` 번들에만 들어간다 |
| Claude 고유 설정 | `adapters/claude/pipeline-agents.json`(도구 목록, Figma 절), `adapters/claude/mcp.defaults.json`의 role |
| 실행기 명령 `board`·`board-set`·`board-wait`·`fingerprint`·`verdict` | 기존 보호 실행기를 재사용한다. 다른 세션에서는 guard가 거부하고 Codex 실행 규칙에도 넣지 않는다 |
| `tasks/<작업 ID>/` 산출물 | 기존 세션 산출물 규칙과 중앙 로그 미러를 재사용한다. 다른 세션에서는 허용하지 않는다 |

공통 시스템 프롬프트에는 "guard가 orchest의 source 변경을 차단한다"는 기존 문장이 그대로 있다. `orchest` 세션의 서문이 이 문장보다 파이프라인 계약이 우선한다고 밝힌다. Claude `project-ui` 스킬도 기존 문장 그대로이며 `orchest`의 Publisher 정의에 Figma 주입 사실을 적는다.

## 목적

한 세션에서 부모가 하위 에이전트를 파이프라인으로 실행할 때 필요한 계약과 도구를 추가했다. 세션별 브랜치 권한이나 쓰기 잠금은 만들지 않는다.

기본 작업 형태는 다음과 같다.

사용자 요청 → 범위·스킬·도구·정책 탐색 → 범위 확정과 계획 수립 → `plan.md` 작성 → 작업 branch·worktree 생성(사용자 승인) → 해당 worktree에서 작업 → 미커밋 상태로 사용자에게 알림 → 사용자 검토 후 commit → 직접 부모로 merge, branch·worktree 제거

## 변경 내용

| 항목 | 내용 | 위치 |
| --- | --- | --- |
| 하위 에이전트 공통 계약 | 단일 원본을 렌더러가 3개 호스트의 자식 정의 18개에 삽입한다 | `policy/common/CHILD_AGENT_CORE.template.md`, `lib/agent_policy/core.py` |
| 역할 본문 단일화 | 호스트마다 따로 적혀 있던 역할 본문을 역할별 원본 6개로 옮겼다. adapter에는 형식과 호스트 고유 기능만 남는다 | `policy/common/agents/`, `adapters/*/files/**/agent*/` |
| 세션 바인딩 | inject 시 자식마다 적용할 역할 계약 문서와 스킬 경로를 넣는다 | `lib/agent_policy/injection.py`, `lib/agent_policy/role_profiles.py` |
| Figma MCP | Claude의 `orchest` 세션에도 주입하고 Publisher에 `mcp__TalkToFigma`와 `Skill` 도구를 준다 | `adapters/claude/mcp.defaults.json`, `adapters/claude/files/.claude/agents/publisher.md` |
| 자식 경로 바인딩 | 자식 정의의 정책·실행기 경로를 inject 번들 절대 경로로 바꾼다 | `lib/agent_policy/injection.py` |
| 실행 프로필 | `orchest`에 구현·검토 하위 에이전트와 전체 스킬을 추가했다 | `lib/agent_policy/role_profiles.py` |
| 하위 에이전트 Git 거부 | 이벤트에 `agent_id`가 있으면 Git 변경 준비·실행과 현황판 갱신을 거부한다 | `policy/guards/shared_git.py` |
| 작업 현황판 | 단계·범위·대기 기록, 관계·병합 순서 조회, 공용 항목 영향 확인 | `policy/guards/work_board.py`, `git_operations.py` |
| 검토 지문 | HEAD와 staged·unstaged·untracked 내용의 해시 | `git_operations.py fingerprint` |
| 대기 안내 | 세션 시작·compact·사용자 입력 훅이 대기 상태와 변경 파일을 안내한다 | `policy/guards/managed_policy_guard.py` |
| Codex 실행 규칙 | 보호 실행기 허용 동작에 `board`, `board-set`, `board-wait`, `fingerprint`를 추가했다 | `lib/agent_policy/injection.py` |

## 역할별 작업 방식

오케스트레이션에서도 기존 UI·Logic 세션과 같은 방식으로 작업하게 하는 것이 목적이다. `orchest` 세션에서 자식마다 적용하는 방식은 다음과 같다.

| 하위 에이전트 | 적용 방식 | 바인딩되는 스킬 |
| --- | --- | --- |
| Planner | `orchest` | `harness`, `review-checklist` |
| Publisher | `ui` | `publishing`, `styles`, `coding-convention`, `validation`, `i18n`, `reference/components` 등 |
| Generator·Refactorer | `logic` | `api-authoring`, `data-dto`, `data-fetch`, `data-fetch-layer`, `type-definition`, `validation` 등 |
| Watcher·Evaluator | `review` | `review-checklist`, `validation`, `implementation-quality` |

스킬 목록은 `role_profiles.py`의 기존 역할 프로필에서 가져오므로 역할 세션과 어긋나지 않는다. `logic`·`ui`·`review`·`generate` 세션은 기존 정의를 그대로 쓴다. 화면 구조·스타일 리팩터링은 Publisher가 맡는다.

Figma MCP는 Claude Code에만 넣는다. Codex·OpenCode의 Publisher 정의에는 Figma 관련 내용이 없다.

`publishing` 스킬은 `ui` 프로필의 스킬 목록에 빠져 있어 `ui` 세션 번들에 들어가지 않았다. 사용자 결정으로 `ui` 프로필에 추가했고, 이제 `ui` 세션과 `orchest` 세션의 Publisher 바인딩에 모두 들어간다.

## 작업 항목 배정과 UI·Logic 병렬 구현

Planner는 계획의 작업 항목마다 변경 종류(생성·수정·삭제)와 담당 하위 에이전트를 지정하고 부모는 그대로 호출한다.

| 담당 | 변경 대상 |
| --- | --- |
| Publisher | 마크업, 컴포넌트 구조, CSS·스타일·디자인 토큰, 정적 자산, 접근성, 반응형 표현과 이들의 리팩터링 |
| Generator | API, DTO, parser, validator, hook, util, store, 상태 전이, controller |
| Refactorer | 로직 영역에서 동작을 바꾸지 않는 구조 정리 |

화면 요구가 있는 작업은 다음 순서로 진행한다.

1. 계약 확정: Publisher가 디자인(Claude에서는 Figma)에서 UI 계약 초안을 정리하고, Planner가 API·DTO 근거와 대조해 controller 공개 타입을 계획에 기록한다. 사용자가 계획과 함께 승인한다.
2. 병렬 구현: Publisher는 계약의 props·callback으로 화면을, Generator는 UI 없는 controller까지 구현한다. 수정 파일은 겹치지 않게 나눈다.
3. 최종 연결: 둘 다 끝나면 부모가 포맷·검증을 실행하고 Generator가 page·container에서 연결한다. 그 뒤 Watcher가 검토한다.

- 같은 worktree의 병렬 구간에서는 하위 에이전트가 포맷과 lint·test·build를 실행하지 않는다. 포맷이 상대가 편집 중인 파일까지 다시 쓰기 때문이며, 부모가 둘 다 끝난 뒤 실행한다.
- 하위 에이전트는 배정 밖의 변경이 필요하면 직접 하지 않고 반환한다.
- 이 배정과 병렬 구간의 규칙은 프롬프트 계약이다. 훅은 하위 에이전트별 변경 종류나 병렬 중의 포맷 실행을 막지 않는다.

## 파이프라인 강제 (2026-10-09 실행 기록에서 확인한 결함의 수정)

### 발생한 문제

user-ui의 `orchest` 세션 "가상오피스-예약-실API"(assignment `bfdb584f`, 21:42 시작)에서 하위 에이전트가 한 번도 호출되지 않았다. 부모 세션이 Edit 102회, Write 26회로 22개 source 파일을 직접 구현했고 Watcher도 실행되지 않았다. `plan.md`와 `final-summary.md`는 작성됐지만 `exploration.md`, `implementation-log.md`, `review-log.md`는 없었다. 현황판은 조회만 3회였고 등록·갱신은 없었다.

### 원인

- 부모 프롬프트의 역할 목적이 "승인된 handoff와 branch scope에 적힌 기본 역할을 구현한다"였고, 파이프라인은 참조 문서에 "호출할 수 있다"로만 적혀 있었다.
- `orchest` 세션은 부모도 source를 쓸 수 있었고, 하위 에이전트를 거쳤는지나 Watcher 판정을 확인하는 훅이 없었다.
- 역할별 문서가 정책상 선택이었다.

### 수정 (사용자 선택)

| 선택 | 구현 |
| --- | --- |
| 훅으로 차단, 프롬프트 명시, 예외 허용 | `orchest` 세션에서 `agent_id`가 없는 호출(부모)과 Planner·Watcher의 source 쓰기를 거부한다. 부모 프롬프트에 "파이프라인 계약 (필수)"를 넣었다 |
| 예외는 다음 입력 전까지 | 사용자가 `직접 수정 승인`을 입력하면 그 응답 동안만 부모가 수정할 수 있고, 다음 사용자 입력에서 닫힌다 |
| 파이프라인을 `orchest`에서 실행 | 처음에는 `generate`에 넣었으나 사용자 결정으로 `orchest`로 옮기고 `generate`는 작업 전 상태로 되돌렸다 |
| 커밋 전 PASS 확인 | Watcher가 `verdict --result --start`로 판정을 기록한다. 커밋 준비와 실행 직전에 PASS와 지문 일치를 확인한다 |
| 단계마다 문서 확인 | source 수정 전 `plan.md`·`exploration.md`, 판정 기록 전 `implementation-log.md`·`review-log.md`, 병합 준비 전 `final-summary.md` |

위치는 `policy/guards/pipeline.py`, `shared_git.py`, `managed_policy_guard.py`, `git_operations.py`, `lib/agent_policy/injection.py`, `policy/common/agents/`다.

### 한계

- 부모와 Planner·Watcher의 source 쓰기 차단, 판정 기록 주체 확인은 Claude Code에서만 동작한다. Codex·OpenCode는 하위 에이전트 호출을 구분할 수 없어 문서 확인과 커밋 전 PASS 확인만 적용된다.
- 훅은 문서가 있고 내용이 비어 있지 않은지만 확인한다. 내용의 충실도는 Watcher와 사용자가 판단한다.
- 지문은 worktree의 파일 내용으로 계산한다. stage한 내용과 worktree의 내용이 다른 파일을 커밋하면 검토한 내용과 커밋 내용이 달라질 수 있다.
- 부모가 하위 에이전트를 호출하지 않으면 구현 자체가 진행되지 않을 뿐, 호출을 대신 실행해 주지는 않는다.

### Watcher가 검증하는 방식

1. 검토 대상 worktree에서 시작 지문을 기록한다.
2. `plan.md`, `exploration.md`, `implementation-log.md`와 실제 diff를 대조한다. 계획의 항목이 모두 구현됐는지, 배정된 역할이 변경했는지, 범위 밖 변경이 없는지, 적용했다는 스킬의 패턴과 코드가 맞는지, 근거 없이 채운 API·필드·기본값이 없는지를 `review-checklist` 기준으로 본다.
3. lint·test·build를 직접 실행한다. 구현 에이전트의 보고를 그대로 믿지 않으며 파일을 바꾸는 검증은 실행하지 않는다.
4. `review-log.md`에 PASS/FAIL과 위치·근거·영향이 있는 발견 사항, 수정 요구를 쓴다.
5. `verdict`로 판정을 기록한다. 검토 중 대상이 바뀌었으면 기록이 거부된다. FAIL이면 부모가 수정 요구를 구현 에이전트에 전달하고 다시 검토받는다. 같은 구간의 반려는 최대 3회다.

## 결정 방식

요청에 없는 결정을 에이전트가 정해야 하고 그 결정이 결과·범위·동작·운영 방식 또는 이후 변경 비용을 바꾸면, 문제 상황과 둘 이상의 방안, 각 방안의 장단점·영향과 권장안을 제시하고 사용자가 선택한 뒤 진행한다. 먼저 구현하고 사후에 보고하지 않는다. 하위 에이전트는 같은 형식으로 부모에게 반환한다. 병렬 구현의 작업 공간(같은 worktree)과 최종 연결 담당(Generator)은 이 방식으로 사용자가 선택했다.

## 호스트별 보장 범위

| 호스트 | 근거 | 하위 에이전트의 Git 변경 |
| --- | --- | --- |
| Claude Code | 공식 hooks 문서: 하위 에이전트 안의 도구 이벤트 입력에 `agent_id`가 들어온다 | guard가 거부 |
| Codex | 공식 hooks 문서: `PreToolUse` 입력에 식별 필드가 없고 하위 에이전트 훅은 부모 `session_id`를 쓴다 | 프롬프트 계약만 |
| OpenCode | 공식 plugins 문서에서 확인하지 못했다 | 프롬프트 계약만 |

실제 호스트를 띄운 종단 검증은 하지 않았다. 위 판단은 문서 근거와 단위 테스트까지다.

## 현황판 사용

명령은 system prompt에 바인딩된 `python3 -I <runtime>/git_operations.py`로 실행한다. 저장 위치는 `state/repositories/<common-directory-hash>/work-board/v1/board.json`이며 브랜치 관계 그래프와 분리되어 있다. 현황판 갱신이 준비된 Git 작업의 승인 대상 검사를 무효로 만들지 않게 하기 위해서다.

```text
board                                   관계·병합 순서·작업 단계·실제 Git 상태 조회
board --check src/shared/ui/Button.tsx  겹치는 작업과 다른 worktree의 참조 후보
board-set --task <ID> --title <제목> --stage planning --scope <경로...> --shared <공용 경로...>
board-set --task <ID> --stage working --branch <branch>
board-set --task <ID> --wait-for <선행 ID>
board-set --task <ID> --clear-wait
board-wait --task <ID> --timeout 3600
fingerprint
```

단계는 `planning`, `awaiting-creation`, `working`, `reviewing`, `awaiting-user-review`, `committed`, `merged`, `removed`, `cancelled`다.

- `working` 이후 단계는 실제 branch가 있어야 기록된다.
- `committed`는 해당 branch의 worktree에 미커밋 변경이 없어야 한다.
- `merged`는 등록된 직접 부모가 그 HEAD를 포함해야 한다.
- `removed`는 branch가 남아 있으면 거부된다.
- 범위가 겹쳐도 등록은 막지 않고 겹치는 작업을 `overlaps`로 알려 준다.
- 서로를 기다리게 되는 대기 등록은 거부된다.

## 대기와 재계획

1. 범위가 겹치는 선행 작업을 `--wait-for`로 기록한다. 접점 경로와 그 시점의 선행 HEAD가 저장된다.
2. 선행 작업이 `committed`가 되면 대기가 풀린다. 미커밋 완료(`awaiting-user-review`)는 풀지 않는다.
3. `board-wait` 출력과 훅 안내에 접점 경로에서 변경된 파일이 나온다. 그 파일만 다시 조사해 계획을 갱신한다.
4. 구현은 갱신한 계획의 승인 후 진행하고 `--clear-wait`로 대기를 해제한다.

자동으로 이어지는 범위는 재계획까지다. Claude Code는 백그라운드 명령이 끝나면 세션이 다시 깨어나므로 `board-wait`를 백그라운드로 실행하면 사용자 입력 없이 재계획으로 이어진다. Codex와 OpenCode에서 같은 동작이 되는지는 확인하지 않았으며, 이 경우 다음 사용자 입력 때 훅 안내를 받는다. 사용자 입력 훅의 안내는 같은 해제에 대해 한 번만 나온다.

## 중단 후 재개

현황판에는 마지막으로 기록한 세션이 식별용으로 남는다. 새 세션은 `board`의 `other_session`과 `actual`(branch 존재, HEAD, worktree, 미커밋 변경)을 보고 실제 worktree·diff·미확인 쓰기 기록(`writes`)과 대조한 뒤, 사용자 확인을 받고 해당 단계부터 이어간다. 기록이나 시간 경과만으로 완료 처리하지 않는다.

## 한 세션의 여러 작업

| 항목 | 동작 | 위치 |
| --- | --- | --- |
| 작업별 산출물 | 세션 산출물의 `tasks/<작업 ID>/` 아래에 기존과 같은 문서 이름을 허용한다. 중앙 로그 미러도 수집한다 | `policy/guards/artifact_policy.py`, `lib/agent_policy/log_mirror.py` |
| 작업 계획 등록 | `board-set --plan`은 세션 산출물 아래에 실제로 있는 `plan.md`만 받는다 | `policy/guards/work_board.py` |
| 작업별 승인 | 수정 대상 worktree에 계획이 등록된 미완료 작업이 하나 있으면 그 계획의 승인으로 source 변경을 판정한다 | `policy/guards/approval_policy.py` |
| 승인 입력 | `<작업 ID> 진행`, `<ID> <ID> 진행`, `<작업 ID> 구현 승인 취소`. 일반 `진행`은 세션 계획만 승인한다 | `policy/guards/approval_policy.py` |
| 재개 | `board`의 `resumable`이 다른 세션의 미완료 작업을 실제 Git 상태와 함께 보여 준다. 세션 시작 안내에도 개수와 ID가 나온다 | `policy/guards/work_board.py` |

- 작업 계획과 세션 계획이 같은 문서이면 세션 승인을 그 작업의 승인으로 인정한다.
- 한 worktree에 계획이 등록된 미완료 작업이 둘 이상이면 어느 계획인지 정할 수 없으므로 세션 계획으로 판정한다.
- 현황판에 작업이 없는 worktree는 기존과 같이 세션 계획으로 판정한다.
- 새 세션은 이전 세션의 승인을 승계하지 않는다. 원래 assignment를 재개하면 승인이 유지된다.
- 하위 에이전트가 자기 작업의 worktree 밖을 수정하지 못하게 막는 강제는 없다. 프롬프트 계약(전달받은 worktree에서만 작업)으로 운영한다.

## 남은 작업

- Codex·OpenCode에서 하위 에이전트 호출을 식별하는 방법. Codex는 `SubagentStart`·`SubagentStop` 기록과의 대조, OpenCode는 자식 세션의 부모 ID 조회가 후보이나 검증하지 않았다.
- 실제 호스트에서 자식 정의가 번들 경로의 정책 문서를 읽는지에 대한 종단 확인.
- `board --check`의 참조 후보는 경로 문자열 일치다. 같은 폴더의 상대 import는 잡지 못한다.

## 적용

실행 중인 소비자 세션은 원래 번들을 계속 사용한다. 새 정책은 현재 작업을 handoff한 뒤 중앙 launcher로 새 inject 세션을 시작해야 적용된다.

## 검증

- `tests/test_orchestration.py`: 자식 정의의 계약·경로(3개 호스트), `generate` 프로필, 부모 프롬프트, 현황판 등록·단계 검증·대기 해제·상호 대기 거부·조회·공용 항목 확인, 검토 지문, 하위 에이전트 Git 거부
- `tests/test_injection.py`: Codex 실행 규칙의 허용 동작 목록
- 전체 결과는 세션 산출물 `final-summary.md`에 기록한다.
