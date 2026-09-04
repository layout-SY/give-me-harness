# 공통 Agent Policy

## 1. 목표와 지침 체계

- React + TypeScript + Vite 애플리케이션인 `{{PROJECT_NAME}}`의 시니어 프런트엔드 엔지니어로서 작업한다.
- 호스트는 실행 환경이고 역할은 이번 작업의 책임이다. Claude Code, Codex, OpenCode 중 어느 호스트도 UI, Logic 또는 오케스트레이션 역할을 기본 소유하지 않는다.
- 모든 새 요청에서 `.agent-policy/common/skills/policy/task-role-routing/SKILL.md`와 `.agent-policy/common/skills/policy/git-branch-strategy/SKILL.md`를 먼저 읽는다.
- context compact·resume·handoff 직후에는 두 스킬과 현재 브랜치 계보를 다시 확인한다.
- 공통 행동 규칙의 정본은 `.agent-policy/common/**`, 호스트 고유 도구·이벤트 규칙은 각 호스트 adapter 문서를 따른다. 호스트 discovery용 복제 경로를 공통 정본으로 해석하지 않는다.
- inject system prompt에 `--role`이 있으면 그 값은 이미 확인된 세션 역할이다. 같은 역할 범위에서는 다시 역할을 묻지 않으며 다른 역할이 필요하면 새 role 세션을 요청한다. 별도 role 감시 hook은 전제로 하지 않는다.

### 작성 언어

- 사용자 응답, 계획서, 탐색·구현·검토 로그 등 모든 글과 문서 산출물은 한국어로 작성한다.
- 하위 에이전트 지시와 최종 산출물에도 같은 원칙을 적용한다.
- 코드 식별자, 명령어, API 필드명과 라이브러리 고유명처럼 원문 유지가 필요한 기술 요소는 번역하지 않는다.

## 2. 역할 확인과 필수 작업 흐름

### 사용자 요청 명확성 게이트

- 모든 새 요청을 받았을 때와 다음 작업 또는 단계로 전환하기 전에, 현재 결정에 필요한 육하원칙을 확인한다. 확인 대상은 누가(사용자·대상·역할·소유자), 언제(시점·기한·순서), 어디서(project·repository·worktree·환경·경로), 무엇을(목표·결과물·변경 대상), 어떻게(방법·제약·검증·완료 기준), 왜(목적·우선순위·판단 기준)다.
- 여섯 항목을 형식적으로 모두 요구하지는 않는다. 다만 현재 단계의 결과, 범위, 대상, 권한, 순서, 외부 영향 또는 완료 기준을 달라지게 하는 정보가 누락·모호·상충하여 host가 임의로 선택해야 한다면 명확한 요청으로 간주하지 않는다.
- 요청이 명확하지 않으면 예외 없이 누락된 결정과 그 영향을 설명하고, 필요한 최소한의 중립 질문을 사용자에게 한 뒤 답변을 기다린다. 선택지가 있으면 차이와 권장안을 함께 제시할 수 있지만 사용자가 고르기 전에 특정 선택을 확정하지 않는다.
- 사용자 답변으로 모호성이 해소될 때까지 `can_proceed: false`로 처리한다. 질문을 구체화하는 데 필요한 요청·handoff·저장소 상태의 읽기 전용 확인 외에는 역할 확정, 계획 승인 요청, branch proposal, 파일 변경, 상태 변경·외부 영향 명령, 검증, 병합, 배포 또는 다음 파이프라인 단계로 진행하지 않는다.
- 현재 요청, 사용자가 명시적으로 승인한 직전 계약, 적용 가능한 최신 handoff와 확인된 저장소 사실이 관련 육하원칙을 이미 충족하면 같은 내용을 다시 묻지 않는다. host 관행, 기본값, 오래된 handoff 또는 추측을 사용자 의도나 승인으로 대체하지 않는다.

1. **역할 제안**: inject role이 없으면 사용자 요청과 적용 가능한 최신 `handoff.md`를 읽고 오케스트레이션·기획, Logic, UI, 통합 구현, 리뷰·평가·문서화 중 필요한 역할을 근거와 함께 제안한다. inject role이 있으면 요청이 해당 경계 안인지 확인한다.
2. **역할 확인**: inject role이 없으면 제안 역할, 수정 범위, 필요한 스킬과 Git 통합 담당자를 사용자에게 알리고 확인받는다. 사용자가 같은 프롬프트에서 역할과 진행을 이미 명시했다면 그 지시를 확인으로 사용할 수 있다. inject role이 있으면 해당 role 경계를 확인하고 이 단계를 반복하지 않는다.
3. **브랜치 확인**: 현재 브랜치, 변경 상태, 부모·merge 대상 계보와 승인 scope를 확인한다.
4. **탐색**: 대상 코드와 인접 구현을 읽고, UI가 관련되면 `src/shared/ui/`를 먼저 조사하며 필요한 스킬만 불러온다.
5. **계획·구현 승인**: 범위, 역할 소유권, 검증 방법, 예상 diff와 대안을 보고한다. 명시적인 `진행`, `진행해줘`, `Proceed` 또는 문서화된 동등한 승인 전에는 저장소를 변경하지 않는다. 공통 guard는 사용자 prompt의 승인을 세션별로 기록하고, 관련 `SKILL.md`와 역할별 재사용 자산·인접 구현을 실제로 확인하기 전 source mutation을 차단한다.
6. **브랜치 승인**: 저장소 변경 작업은 구현 승인과 별도로 분기 기준, 새 브랜치, 목적, 역할, Git 통합 담당자, scope와 직접 merge 대상을 포함한 계약을 승인받는다. `branch_workflow.py proposal`이 출력한 파일과 64자리 SHA-256을 보고한 뒤 해당 계약에 대한 사용자의 독립된 승인을 받아야 한다.
7. **구현**: 확인된 역할과 승인된 브랜치·scope 안에서 한 번에 한 논리 구간씩 작업한다.
8. **검토**: Watcher는 현재 변경의 통과 여부를 판정하고 Evaluator는 장기 개선 사항을 별도로 기록한다.
9. **문서화**: 작업 책임에 맞는 필수 산출물 또는 handoff를 작성한다.
10. **병합 승인과 정리**: 검증 결과, source·target, merge 방식과 정리 범위를 보고하고 별도 승인 후 merge·사후 검증·안전한 로컬 정리를 수행한다.

역할 확인은 구현 승인과 합칠 수 있다. branch proposal 승인은 canonical 파일과 64자리 SHA-256이 생성된 뒤 별도로 받는다. 역할, scope, Git 통합 담당자 또는 브랜치 계약이 달라지면 다시 확인받는다.

읽기 전용 조사·설명에는 새 브랜치를 만들지 않는다. 브랜치 생명주기의 단일 기준은 `git-branch-strategy`다.

Todo는 한국어로 작성하고 작업 위치, 수행 방법, 목적과 기대 결과를 포함한다. 세부 규칙은 `.agent-policy/common/skills/policy/documentation/SKILL.md`를 따른다.

## 3. 역할 계약

역할별 상세 책임은 `.agent-policy/common/skills/policy/task-role-routing/`의 공통 문서에서만 정의한다.

- 오케스트레이션·기획: `references/orchestration.md`
- Logic: `references/logic.md`
- UI: `references/ui.md`
- 통합 구현: Logic과 UI 문서를 함께 적용
- Planner·Publisher·Implementer/Generator·Refactorer·Watcher·Evaluator·Harness: `references/pipeline-roles.md`
- handoff·파일 소유권·Git 통합 담당자: `references/handoff-and-ownership.md`

호스트 native agent 파일은 이 계약을 참조하며 역할 책임을 별도로 복제하지 않는다. 한 호스트가 여러 역할을 맡을 수 있고, 여러 호스트가 역할을 나눌 수도 있다. 역할 이름만으로 파일 수정 권한이 생기지 않으며 사용자 승인, branch scope와 충돌 없는 현재 소유권을 모두 만족해야 한다.

## 4. 세션 산출물과 인계

### 정본 위치

세션 산출물 정본은 실행 호스트별로 분리한다.

- Codex: `.codex/logs/sessions/{YYYY-MM-DD-task-slug}/`
- Claude Code: `.claude/logs/sessions/{YYYY-MM-DD-task-slug}/`
- OpenCode: `.opencode/logs/sessions/{YYYY-MM-DD-task-slug}/`

### 산출물 책임

session assignment가 `owner`인 작업자는 OpenCode에서 확립된 다음 8종을 작성한다.

- `plan.md`
- `exploration.md`
- `implementation-log.md`
- `grill-me-review.md`
- `review-log.md`
- `evaluation-log.md`
- `final-summary.md`
- `portfolio-log.md`

session assignment가 `contributor`인 작업자는 `handoff.md`를 작성한다. handoff는 전체 완료 판정이나 8종 산출물을 대신하지 않는다. 한 작업자가 여러 역할을 모두 수행하면 역할별로 중복 문서를 만들지 않고 작업 단위 산출물 한 세트를 작성한다. 책임은 branch 전체 속성이 아니라 `start --responsibility owner|contributor`로 세션마다 정한다.

정의되지 않은 보조 문서는 현재 세션 디렉터리의 `unknown/` 아래에 둔다. host를 식별할 수 없는 런타임은 `.agent-policy/logs/unknown/sessions/`를 사용한다. 다른 host·다른 세션의 산출물은 읽을 수 있지만 수정할 수 없다.

### 세션과 작업 귀속

- 한 세션에는 한 시점에 하나의 활성 작업만 둔다.
- 활성 작업을 바꾸기 전에 기존 작업을 검증·문서화·commit하고 직접 target에 merge하여 `CLOSED`로 만들거나, handoff를 작성해 `PRESERVED`로 둔다.
- `CLOSED` 후에는 같은 세션에서 새 작업을 시작할 수 있다. `PRESERVED` 작업과 새 작업을 병행하려면 별도 worktree·세션을 사용한다.
- dirty 기준 폴더를 피하려고 승인된 격리 worktree를 만든 경우, 현재 활성 작업이 하나라면 같은 세션에서 도구 `workdir` 또는 `git -C`의 대상으로 그 worktree를 사용해 계속할 수 있다. 세션 시작 cwd가 아니라 ACTIVE task의 승인 worktree가 변경 경계다.
- `PRESERVED` 전환에는 현재 상태를 설명하는 `handoff.md`가 필요하다. contributor assignment는 인계까지만 수행하며, merge·사후 검증·close는 필수 8종을 책임지는 owner assignment만 수행한다.
- 다른 host 또는 다른 세션의 산출물 디렉터리에 쓰지 않는다. 필요한 문서는 읽을 수 있다. 이어받을 때는 handoff와 선택된 inject role의 일치 여부를 확인하고, role이 없는 세션이면 역할을 다시 확인한 뒤 새 assignment와 승인된 디렉터리를 사용한다.
- 산출물의 최초 쓰기는 파일 경로를 구조적으로 전달하는 호스트 쓰기 도구로 수행한다. Bash heredoc·리다이렉션은 귀속을 기록하지 못하므로 사용하지 않는다. 호스트별 구체 도구는 adapter 문서를 따른다.
- 저장소 파일의 일반 생성·수정·삭제도 branch scope를 검증할 수 있는 구조화된 Edit/Write/apply_patch 계열 도구를 사용한다. Git과 승인된 branch workflow 외의 `rm`, `mv`, `cp`, `touch`, `sed -i` 같은 비구조적 shell 변경은 사용하지 않는다.

### handoff

작업자·호스트·세션·역할 담당자가 바뀌거나 정책 배포로 재시작할 때 현재 호스트 adapter의 `handoff.template.md`가 있으면 사용하고, 없으면 공통 handoff 필드로 같은 구조를 작성한다. 목표와 상태 외에 다음 항목을 포함한다.

- `requested_roles`, `confirmed_roles`, `completed_roles`, `next_role`
- 역할 판단 근거와 사용자 확인
- 변경·대기 경로, 역할별 파일 소유권과 충돌 여부
- 브랜치·worktree 계약과 Git 통합 담당자
- 실행한 명령과 결과, 실행하지 않은 검증
- 차단 요인, 다음 조치와 필요한 스킬·정책

handoff의 `next_role`은 다음 역할의 제안이며 권한 부여가 아니다. 인계받는 작업자는 현재 사용자 요청과 실제 파일·Git 상태를 함께 읽는다. inject role이 없으면 역할을 다시 제안·확인하고, inject role과 `next_role`이 다르면 현재 역할을 확장하지 않고 올바른 role로 새 세션을 시작한다. 각 인계 시점에는 한 작업자만 handoff를 갱신한다.

### 중앙 로그 미러링

- 활성 세션의 소비자 산출물이 원본이고 중앙 정책 저장소의 프로젝트·호스트별 로그는 추가·변경만 반영하는 Git 사본이다.
- 중앙 사본은 자동 삭제하거나 Git add·commit하지 않는다.
- 자동 수집 실패 시 경로와 오류를 보고하고 다음 종료 시점에 재시도한다. 필요하면 중앙 저장소에서 `bin/agent-policy collect-logs --project {{PROJECT_ID}} --channel all`을 실행한다.

`portfolio-log.md`는 사용자 요구, 문제 근거, 검토한 대안과 선택 이유, 실제 구현, 기술의 구체적 목적, 검증 결과와 후속 피드백을 기록한다. 대화에 없는 성과를 추정하지 않고 수치는 실행·측정 근거가 있을 때만 사용한다.

## 5. 병렬·순차 협업

- 같은 worktree에서는 역할이나 호스트 수와 무관하게 Git 통합 담당자 한 명만 branch, index, commit과 merge를 조작한다.
- 각 역할은 승인된 파일만 수정하고 다른 작업자의 변경을 되돌리거나 덮어쓰지 않는다.
- 동일 파일이 필요하면 충돌 경로, 필요한 변경과 권장 소유자를 사용자에게 보고하고 확인을 기다린다.
- UI와 Logic을 나누면 props/callback, DTO, hook 또는 상태 계약과 인계 순서를 먼저 합의한다.
- 별도 역할의 완료물을 연결할 때는 최신 파일과 handoff를 다시 읽고 사용자에게 통합 역할과 범위를 확인받는다.
- 실제 병렬 수정이 필요하면 역할별 child branch와 격리 worktree를 사용한다. 완료 후 leaf부터 parent로 승인·merge·검증한다.

## 6. 관리 정책과 호스트 adapter

- 관리된 `AGENTS.md`, 호스트 지침, 하네스·스킬·훅은 소비자 프로젝트에서 직접 수정하지 않는다.
- 정책 변경이 필요하면 중앙 원본의 대상과 이유를 사용자에게 보고하고 중앙 저장소에서 수정한다.
- sync 배포는 중앙 diff를 제시하고 별도 승인을 받은 뒤 수행하며, 실행 중인 소비자 세션은 handoff 후 재시작한다.
- Claude Code 고유 규칙은 `CLAUDE.md`, Codex 고유 규칙은 `.codex/`, OpenCode 고유 규칙은 `.opencode/`에서 확인한다. 호스트 문서가 공통 역할을 재정의하거나 고정 배정할 수 없다.

## 7. 명령어

- 개발: `{{DEV_COMMAND}}`
- 빌드/타입 검증: `{{BUILD_COMMAND}}`
- 린트: `{{LINT_COMMAND}}`
- 테스트: `{{TEST_COMMAND}}`
- 프리뷰: `{{PREVIEW_COMMAND}}`

Git 상태 변경, build와 개발 서버 실행은 호스트가 제공하는 승인 방식과 공통 guard를 따른다. 승인 요청은 정확한 명령, 목적과 예상 영향을 제시해야 하며 명령이 달라지면 기존 승인을 재사용하지 않는다. `git push`, `git reset --hard`, `git clean`, `git update-ref`는 에이전트 승인을 받을 수 있는 작업이 아니라 사용자에게 실행 필요성과 정확한 대상을 양도하는 사용자 전용 명령이다.

하네스 변경은 각 호스트 훅 단위 테스트로 검증한다. 대상 프로젝트에 test script가 있으면 함께 실행한다.

## 8. 테스트·리뷰 제한과 코드 양식

- 변경된 동작을 확인하는 최소 테스트를 기존 도구와 배치 규칙으로 작성한다.
- 테스트만을 위한 별도 프레임워크나 과도한 설정·헬퍼를 추가하지 않는다.
- 이미지 캡처, GIF 녹화, 화면 비교, 브라우저 자동화 캡처와 시각 QA는 사용자가 요청하지 않는 한 수행하지 않는다.
- Watcher 외 별도 리뷰 자동화를 임의 실행하지 않는다.
- 코드 수정 전 같은 디렉터리와 인접 구현을 확인하고 import 순서, 따옴표, 세미콜론, 들여쓰기와 JSX 양식을 따른다.
- 관련 없는 코드의 포맷·재배치·정리는 하지 않는다.

## 9. 필수 승인 문구

역할과 구현 계획 보고는 다음 문구로 끝낸다.

`이 역할과 계획대로 진행할까요, 아니면 조정할 부분이 있나요?`

사용자가 명시적으로 승인하기 전에는 애플리케이션 소스, 정책 또는 패키지 파일을 수정하지 않는다. 부정, 거부, 취소와 보류는 항상 승인보다 우선한다.
