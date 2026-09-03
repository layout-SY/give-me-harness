# 계획

## 상태
- `paused_after_generator`
- 사용자가 `진행해`로 B안을 승인했고 Generator 구현·정적·브라우저 검증을 완료했다.
- Watcher `confirmed` 전에는 Closure와 완료 처리를 수행하지 않는다.

## 요청 요약
- 승인된 후속 순서에 따라 Vote·Discussion 목록의 상태 변경 draft를 선택 행 ID에 귀속한다.
- 탐색 중 확인된 공개 기준 draft의 동일한 행 귀속 누락을 함께 처리할지 사용자 결정을 받는다.

## 작업 유형
- correctness bug fix

## 권고 범위
- **`resetKey` + 행 소유 공개 기준 초안**
- 변경 파일은 다음 두 개로 제한한다.
  1. `src/pages/cp-vote/ui/use-cp-vote-list-process.tsx`
  2. `src/pages/cp-discussion/ui/use-cp-discussion-list-process.tsx`

## 권고 변경 계약
### Vote
- `useStatusTransition`에 `resetKey: selectedRow?.id ?? null`을 전달한다.
- `disclosureIndex` state를 `{ voteId, index } | null` 형태의 로컬 선택 상태로 교체한다.
- 현재 선택 행 ID와 초안 소유 ID가 같을 때만 초안 index를 사용하고, 아니면 현재 행의 persisted disclosure index를 사용한다.
- `changeDisclosure`는 현재 선택 행이 있을 때만 `{ voteId, index }`를 저장한다.
- `reset`, 명시적 행 선택, mutation 성공 시 공개 기준 초안을 제거한다.

### Discussion
- `useStatusTransition`에 `resetKey: selectedRow?.id ?? null`을 전달한다.
- 공개 기준 초안을 `{ discussionId, index } | null`로 저장하고 Vote와 같은 소유권 규칙을 적용한다.
- 기존 process 반환 interface와 controller/view 호출 계약은 유지한다.

## 불변식
1. `nextStatus`는 현재 `selectedRow.id`에만 유효하다.
2. 공개 기준 초안은 생성된 행 ID에만 유효하다.
3. fallback으로 선택 행이 바뀌면 새 행의 persisted disclosure 값이 즉시 표시된다.
4. `canSave`는 현재 행이 소유한 초안만 사용한다.
5. mutation 대상 ID와 상태·공개 기준 초안의 소유 ID가 일치한다.
6. 동일 행의 same-query refetch에서는 현재 행 소유 초안을 유지할 수 있다.
7. 저장 성공 후 초안을 제거하고 서버 응답값을 기준으로 사용한다.

## 대안
### A. 원안: `resetKey`만 추가
- 두 파일에 각각 한 필드를 추가한다.
- 상태 draft 누수는 막지만 공개 기준 draft의 잘못된 행 payload 경로는 남는다.
- correctness-complete 판정은 할 수 없다.

### B. 권고안: `resetKey` + 행 소유 공개 기준 초안
- 상태와 공개 기준의 소유 행을 모두 명시한다.
- Proposal에서 검증된 패턴을 재사용하며 두 process 파일 밖으로 범위를 넓히지 않는다.

### C. effect 기반 index 동기화
- 선택 행 변경 후 effect에서 index를 보정한다.
- effect 전 렌더에서 잘못된 `canSave`가 계산될 수 있어 제외한다.

## 검증 계획
### 정적 검증
- 변경한 두 파일 LSP diagnostics. TypeScript LSP가 계속 미설치면 해당 제약을 기록한다.
- 두 파일 scoped ESLint.
- `yarn build`.
- scoped `git diff --check`.

### 브라우저 회귀 시나리오
1. 같은 상태의 행 A와 B를 준비한다.
2. A에서 상태와 공개 기준 초안을 만든다.
3. same-query refetch로 A를 제거해 B가 fallback되게 한다.
4. B에서 `nextStatus=null`, persisted disclosure 표시, `canSave=false`를 확인한다.
5. A가 다시 나타나도 B에 A 초안이 결합되지 않는지 확인한다.
6. 명시적 행 전환, 저장 성공, 저장 실패에서 각 행 소유 초안이 다른 행으로 누수되지 않는지 확인한다.
7. browser console error·warning 0건을 확인한다.

## 필요 에이전트
- Planner: 범위 선택과 불변식 확정
- Generator: 승인된 두 process 파일 구현
- Watcher: API 복구 후 최종 판정
- Closure: Watcher `confirmed` 후에만 실행

## 필요 스킬
- `policy-harness`
- `policy-coding-convention`
- `policy-refactoring`
- `policy-hook-extraction`
- `policy-abstraction-strategy`
- `policy-type-definition`
- `policy-documentation`
- `policy-review-checklist`
- `programming`
- `playwright`

## 승인 선택
- **권고:** B안, `resetKey`와 공개 기준 draft 행 소유권을 함께 적용한다.
- A안을 선택하면 상태 draft만 수정하고 공개 기준 payload 위험은 알려진 잔여 결함으로 기록한다.

## 승인 결과
- 사용자 선택: B안
- 사용자 승인 문구: `진행해`
- 구현 상태: Generator 완료, Watcher 대기

## 승인 요청
- 이 계획대로 진행할까요, 아니면 조정할 부분이 있나요?
