# 역할 기반 작업 흐름

## 기존 작업의 commit·merge

기존 변경의 commit·merge만 요청받으면 `git-branch-strategy`의 상태 확인·검토·승인·실행·검증·정리를 수행하고 결과를 대화로 보고한다. 기능 구현 파이프라인을 새로 시작하거나 필수 산출물·handoff를 만들지 않는다. 예외의 범위와 구현 작업으로 전환하는 기준은 `documentation`을 따른다.

## 기능 작업

1. Planner가 요청과 handoff를 분류하고 기본 역할, scope와 검증을 제안한다.
2. UI가 포함되면 Publisher가 재사용 자산과 props/callback 계약을 정의한다.
3. 사용자 승인 후 Implementer/Generator가 확인된 역할과 scope를 구현한다.
4. Watcher가 현재 변경을 판정한다.
5. 한 작업자가 전체를 맡으면 검증·산출물·merge 단계로 진행한다. 역할이 분리되면 부분 결과를 handoff한다. role이 없는 다음 세션은 역할을 다시 확인하고, inject 세션은 handoff와 일치하는 `--role`로 시작한다.

## 리팩터링

Planner → Refactorer → Watcher 순서를 기본으로 한다. 공개 계약과 관찰 가능한 동작을 보존하고, 새 기능이나 추가 역할이 필요하면 현재 호출을 멈춘 뒤 역할·scope 변경을 확인받는다.

## 기능과 리팩터링이 섞인 작업

- 동작 보존 리팩터링과 새 기능 구현을 별도 구간으로 계획한다.
- 먼저 기존 동작을 고정하는 검증 근거를 확보하고 리팩터링을 완료한 뒤 새 기능을 구현한다.
- 각 구간의 diff와 검증을 구분하며 기능 요구가 바뀌면 갱신된 승인과 scope를 받는다.
- 두 구간을 하나의 commit에 섞어 원인과 회귀 범위를 숨기지 않는다.

## Logic·UI 분리 작업

- Planner가 Logic과 UI의 예상 기여 범위, props/callback·DTO·hook 계약과 통합 순서를 제안한다. 파일 소유권을 만들지 않으며 형제 통합 순서는 변경 검토와 사용자 승인으로 결정한다.
- handoff에 역할별 목적지 branch·worktree 절대 경로·기준 HEAD·직접 부모와 상세 작업을 연결해 기록한다. 보내는 현재 위치만 적거나 역할 이름만으로 다음 할 일을 대신하지 않는다.
- UI·Logic이 같은 결과물을 순차로 연결하면 같은 branch·worktree를 공유할 수 있다. 소스 수정과 Git 변경을 순차 실행하고 역할 전환 전에 commit·staged·unstaged·untracked 변경과 선행 작업의 완료를 확인한다.
- 실제 병렬 수정이나 별도 변경 이력·검증이 필요하면 작업별 child branch와 linked worktree를 사용한다. 역할·세션 수만으로 작업 공간을 나누지 않는다. 각 작업의 부모·자식 관계, 직접 부모 통합 순서, 형제 변경 검토와 승인을 handoff에 명시한다.
- 각 역할의 수정할 파일·컴포넌트·hook·API·상태, 재사용 방법, 연결 계약, 시작 조건, 완료 기준·검증 명령과 다음 인계 대상을 구체적으로 기록한다. 위치나 계약이 미정이면 질문하고 임의로 확정하지 않는다. 공유·분리 예시는 `handoff-and-ownership.md`를 따른다.
- 선행 역할의 Watcher 판정과 handoff 후 사용자가 다음 역할을 확인한다.
- 통합 역할은 최신 파일과 handoff를 다시 읽고 기능을 연결한 뒤 전체 검증을 수행한다.

## 평가 작업

사용자가 평가·audit 역할을 요청한 경우에만 Evaluator를 실행한다. 코드를 수정하지 않고 관찰 사실과 장기 권고를 분리한다. 발견 사항에는 심각도, 영향받는 경로, 재현·판단 근거와 수정 권고를 기록하며 근거가 없는 가능성으로 목록을 부풀리지 않는다. 평가 결과를 자동 구현으로 전환하지 않는다.

## 상태 전이

- Planner: `draft -> ready_for_role_confirmation -> ready_for_approval`
- Implementer/Refactorer: `approved -> in_progress -> role_complete | hold`
- Watcher: `role_complete -> passed | rejected | escalated`
- 부분 인계: `passed -> handed_off -> next_role_confirmation`
- 통합·완료: `passed -> ready_to_merge -> merged_verified -> closed`

## 재시도와 escalation

- 같은 작업 구간의 Watcher 반려는 최대 3회다.
- 동일 사유가 2회 반복되면 `repeat_issue_detected: true`를 기록한다.
- 3회 초과, 반복 원인 누적, 역할·scope 충돌 또는 구조적 원인이면 자동 재시도하지 않는다.
- 범위·라우팅 문제는 Planner, 구조적 부채는 Evaluator, 요구·권한 선택은 사용자에게 이관한다.
- 보안 경계, 데이터 손실 가능성, 비가역 작업, 외부 의존성 도입 또는 아키텍처 방향을 바꾸는 결정은 자동 재시도하지 않고 사용자에게 선택지·영향과 권장안을 이관한다.
