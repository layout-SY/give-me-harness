---
name: policy-task-role-routing
description: 사용자 요청의 명확성을 확인하고, 요청과 handoff를 근거로 호스트와 독립적인 작업 역할·정책·소유권·인계 계약을 제안하고 확인한다.
---

# 작업 역할 라우팅

호스트는 실행 환경이고 역할은 이번 작업에서 맡은 책임이다. Claude Code, Codex, OpenCode 중 어느 호스트도 기본적으로 UI·Logic·오케스트레이션 역할을 독점하지 않는다. 한 호스트가 사용자 확인을 거쳐 하나 또는 여러 역할을 수행할 수 있다.

## 요청 명확성 게이트

모든 새 요청을 받았을 때와 단계 전환 전에 현재 사용자 요청, 사용자가 명시적으로 승인한 직전 계약, 적용 가능한 최신 `handoff.md`와 확인된 저장소 사실을 함께 읽고 다음 순서를 따른다.

1. 현재 결정에 관련된 육하원칙인 누가, 언제, 어디서, 무엇을, 어떻게, 왜를 식별한다.
2. 목표·결과물, project·경로·환경, 역할·소유권, 수행 순서·시점, 방법·제약·검증·완료 기준과 목적 중 누락·모호·상충한 값이 결과를 달라지게 하는지 판단한다.
3. host가 여러 유효한 선택지 중 하나를 임의로 골라야 한다면 `needs_clarification`으로 판정하고 `can_proceed: false`로 기록한다.
4. 무엇이 비어 있고 선택에 따라 무엇이 달라지는지 설명한 뒤 예외 없이 필요한 최소한의 중립 질문을 사용자에게 한다. 합리적인 권장안이 있으면 근거와 함께 제시하되 사용자 답변으로 확정하지 않은 선택을 실행하지 않는다.
5. 사용자 답변이 올 때까지 질문을 정확하게 만들기 위한 읽기 전용 확인만 수행한다. 역할 확정, 계획 승인 요청, branch workflow, source·설정·산출물 변경, 상태 변경·외부 영향 명령, 검증, 병합, 배포와 다음 파이프라인 호출은 시작하지 않는다.
6. 답변을 받으면 전체 요청 계약을 다시 평가한다. 관련 육하원칙이 모두 명확할 때만 `clear`로 판정하고 다음 단계로 이동한다.

모든 육하원칙을 형식적으로 다시 질문하지 않는다. 현재 결정과 무관한 항목이나 사용자 요청·승인 계약·현재 사실로 이미 확정된 항목은 질문 대상이 아니다. host 이름, 관행, 편의상 기본값, 오래된 handoff와 암묵적 추측은 누락된 사용자 결정을 대신할 수 없다.

## 새 요청의 역할 확인

inject system prompt에 `--role logic|ui|orchest|review|generate`가 기록되어 있으면 해당 값은 세션 시작 시 확인된 role profile이다. 같은 profile 범위의 새 요청에는 역할 확인을 반복하지 않는다. 요청이 경계를 벗어나면 현재 역할을 확장하지 말고 새 `--role` 세션이 필요하다고 보고한다. 이 경계는 system prompt로 운영하며 별도 role 감시 hook을 요구하지 않는다.

inject role이 없는 세션에서 새 작업을 시작할 때 다음 순서를 따른다.

1. 사용자 요청, 적용 가능한 최신 `handoff.md`, 현재 브랜치 계약과 변경 상태를 읽는다.
2. 아래 기본 역할 중 필요한 역할과 근거, 수정 예정 범위, 필요한 스킬·정책, 승인할 Git 작업를 제안한다.
3. 역할 판단을 사용자에게 알리고 확인을 받는다. 역할이 명시되지 않은 handoff는 자동 권한이 아니며 역할 판단의 근거로만 사용한다.
4. 사용자가 역할과 진행을 이미 명시적으로 지시한 같은 프롬프트는 확인으로 사용할 수 있다. 요청 명확성 게이트가 `clear`가 아니거나 역할·범위·브랜치 계약 중 하나라도 모호하면 다음 단계 전에 질문한다.
5. 확인된 역할이나 파일 범위를 확장하거나 다른 역할로 전환해야 하면 이유와 새 경계를 보고하고 다시 확인받는다.

역할 확인은 구현 계획 승인과 합칠 수 있다. 브랜치 생성·관계 변경은 `git-branch-strategy`의 구체적인 Git 작업 보고와 같은 승인 경로를 사용한다. V3 proposal SHA나 Git 통합 담당자를 요구하지 않는다. 읽기 전용 탐색은 역할 제안에 필요한 범위에서 먼저 수행할 수 있지만, 확인 전에는 저장소를 변경하지 않는다.

## 기본 역할

- **오케스트레이션·기획**: 요청 분류, 탐색, 계획, 역할·소유권 배정, 승인과 완료 게이트를 관리한다. 자세한 계약은 [references/orchestration.md](references/orchestration.md)를 읽는다.
- **Logic**: API, DTO, parser, validator, hook, util, store, 상태 전이, 데이터 가공과 기능 통합을 담당한다. 확인된 경우 [references/logic.md](references/logic.md)를 읽는다.
- **UI**: 화면 구조, JSX/TSX, CSS·자산, 접근성, 반응형 레이아웃, 시각적 상태와 props/callback 계약을 담당한다. 확인된 경우 [references/ui.md](references/ui.md)를 읽는다.
- **통합 구현**: 같은 작업자가 Logic과 UI를 함께 맡는다. `logic.md`와 `ui.md`를 모두 따르되 계층 경계를 없애지 않는다.
- **리뷰·평가·문서화**: 구현을 변경하지 않는 판정, 장기 평가 또는 기록만 수행한다. 관련 세부 역할은 [references/pipeline-roles.md](references/pipeline-roles.md)를 읽는다.

역할 이름은 파일·브랜치를 소유하게 하지 않는다. 작업 범위는 계획이며 세션별 허용 파일 목록이나 계열 접근 권한으로 저장하지 않는다. 모든 세션은 사용자 요청에 따라 기존 작업을 이어갈 수 있고, 다른 host·세션 로그 보호와 프로젝트 경계를 유지한다.

요청이 다른 기능 계열과 관련되는지는 에이전트가 판단하고 실제 경로·관계는 runtime이 확인한다. 다른 계열로 이동할 때 적절한 worktree와 선택적인 새 세션을 안내한다. 이미 요청한 이동을 다시 승인받거나 도구 호출마다 경고하지 않는다. 자동 요청 분류·새 branch 생성·우선순위 부여는 후속 설계 사항이며 현재 자동화하지 않는다.

## handoff와 협업

작업자·호스트·세션이 바뀌거나 부분 역할의 결과를 넘길 때는 [references/handoff-and-ownership.md](references/handoff-and-ownership.md)를 따른다. 모든 세션이 사용자 승인 후 Git을 변경할 수 있으며 같은 worktree의 Git 변경은 순차 실행한다.

## 파이프라인 역할

Planner, Publisher, Implementer/Generator, Refactorer, Watcher, Evaluator와 Harness는 호스트 이름이 아니라 작업 단계다. 하위 에이전트나 호스트 native agent를 사용할 때 [references/pipeline-roles.md](references/pipeline-roles.md)의 공통 계약을 적용한다.

feature, refactor, 역할 분리 구현, audit, retry·escalation의 단계 전이는 [references/workflows.md](references/workflows.md)를 따른다.
