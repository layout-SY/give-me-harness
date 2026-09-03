---
name: policy-task-role-routing
description: 사용자 요청과 handoff를 근거로 호스트와 독립적인 작업 역할을 제안·확인하고, 역할별 정책·소유권·인계 계약을 선택한다.
---

# 작업 역할 라우팅

호스트는 실행 환경이고 역할은 이번 작업에서 맡은 책임이다. Claude Code, Codex, OpenCode 중 어느 호스트도 기본적으로 UI·Logic·오케스트레이션 역할을 독점하지 않는다. 한 호스트가 사용자 확인을 거쳐 하나 또는 여러 역할을 수행할 수 있다.

## 새 요청의 역할 확인

inject system prompt에 `--role logic|ui|orchest|review|generate`가 기록되어 있으면 해당 값은 세션 시작 시 확인된 role profile이다. 같은 profile 범위의 새 요청에는 역할 확인을 반복하지 않는다. 요청이 경계를 벗어나면 현재 역할을 확장하지 말고 새 `--role` 세션이 필요하다고 보고한다. 이 경계는 system prompt로 운영하며 별도 role 감시 hook을 요구하지 않는다.

inject role이 없는 세션에서 새 작업을 시작할 때 다음 순서를 따른다.

1. 사용자 요청, 적용 가능한 최신 `handoff.md`, 현재 브랜치 계약과 변경 상태를 읽는다.
2. 아래 기본 역할 중 필요한 역할과 근거, 수정 예정 범위, 필요한 스킬·정책, Git 통합 담당자를 제안한다.
3. 역할 판단을 사용자에게 알리고 확인을 받는다. 역할이 명시되지 않은 handoff는 자동 권한이 아니며 역할 판단의 근거로만 사용한다.
4. 사용자가 역할과 진행을 이미 명시적으로 지시한 같은 프롬프트는 확인으로 사용할 수 있다. 역할·범위·브랜치 계약 중 하나라도 모호하면 구현 전에 질문한다.
5. 확인된 역할이나 파일 범위를 확장하거나 다른 역할로 전환해야 하면 이유와 새 경계를 보고하고 다시 확인받는다.

역할 확인은 구현 계획 승인과 합칠 수 있다. 브랜치 생성 승인은 `git-branch-strategy`가 canonical proposal 파일과 64자리 SHA-256을 출력한 뒤 별도 사용자 prompt로 받는다. 읽기 전용 탐색은 역할 제안에 필요한 범위에서 먼저 수행할 수 있지만, 확인 전에는 저장소를 변경하지 않는다.

## 기본 역할

- **오케스트레이션·기획**: 요청 분류, 탐색, 계획, 역할·소유권 배정, 승인과 완료 게이트를 관리한다. 자세한 계약은 [references/orchestration.md](references/orchestration.md)를 읽는다.
- **Logic**: API, DTO, parser, validator, hook, util, store, 상태 전이, 데이터 가공과 기능 통합을 담당한다. 확인된 경우 [references/logic.md](references/logic.md)를 읽는다.
- **UI**: 화면 구조, JSX/TSX, CSS·자산, 접근성, 반응형 레이아웃, 시각적 상태와 props/callback 계약을 담당한다. 확인된 경우 [references/ui.md](references/ui.md)를 읽는다.
- **통합 구현**: 같은 작업자가 Logic과 UI를 함께 맡는다. `logic.md`와 `ui.md`를 모두 따르되 계층 경계를 없애지 않는다.
- **리뷰·평가·문서화**: 구현을 변경하지 않는 판정, 장기 평가 또는 기록만 수행한다. 관련 세부 역할은 [references/pipeline-roles.md](references/pipeline-roles.md)를 읽는다.

역할 이름은 파일 경로를 자동 소유하게 하지 않는다. 실제 쓰기 권한은 사용자 승인, 브랜치 scope, 현재 파일 소유권과 충돌 상태의 교집합으로 정한다.

## handoff와 협업

작업자·호스트·세션이 바뀌거나 부분 역할의 결과를 넘길 때는 [references/handoff-and-ownership.md](references/handoff-and-ownership.md)를 따른다. 같은 worktree에서는 역할이나 호스트 수와 무관하게 Git 통합 담당자 한 명만 index, commit, branch와 merge를 조작한다.

## 파이프라인 역할

Planner, Publisher, Implementer/Generator, Refactorer, Watcher, Evaluator와 Harness는 호스트 이름이 아니라 작업 단계다. 하위 에이전트나 호스트 native agent를 사용할 때 [references/pipeline-roles.md](references/pipeline-roles.md)의 공통 계약을 적용한다.

feature, refactor, 역할 분리 구현, audit, retry·escalation의 단계 전이는 [references/workflows.md](references/workflows.md)를 따른다.
