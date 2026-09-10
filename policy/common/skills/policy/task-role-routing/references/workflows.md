# 역할 기반 작업 흐름

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

- Planner가 Logic과 UI의 파일 소유권, props/callback·DTO·hook 계약과 통합 순서를 정한다.
- 같은 worktree이면 순차 인계하고 Git 변경은 사용자 승인 후 순차 실행한다.
- 실제 병렬 수정이면 역할별 child branch와 worktree를 사용한다.
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
