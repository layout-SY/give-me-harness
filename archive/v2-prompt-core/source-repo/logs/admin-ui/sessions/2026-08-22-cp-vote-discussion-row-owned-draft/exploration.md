# 탐색 기록

## 상태
- `completed`
- 탐색 결과를 기반으로 사용자가 B안을 승인했고 두 process hook 구현으로 연결했다.

## 스킬 확인
- `policy-index`
- `reference-index`
- `policy-harness`
- `policy-refactoring`
- `policy-hook-extraction`
- `policy-abstraction-strategy`
- `policy-type-definition`
- `policy-documentation`

## 탐색 범위
- `src/shared/ui/`
- `src/widgets/`
- `src/features/cp-status-transition/`
- `src/pages/cp-proposal/ui/`
- `src/pages/cp-vote/ui/`
- `src/pages/cp-discussion/ui/`
- `.agents/skills/reference/`
- `.codex/memory/reusable-assets.md`

## 재사용 자산
- `useStatusTransition.resetKey`: 선택 대상 ID가 바뀌면 같은 상태값이어도 `nextStatus`를 현재 렌더부터 `null`로 만드는 기존 공용 계약.
- `useCpProposalListProcess`: `resetKey: selectedRow?.id ?? null`과 `{ proposalId, index }` 형태의 행 소유 부서 초안 기준 구현.
- Vote·Discussion의 기존 process hook: 선택·fallback·status/disclosure draft·mutation을 이미 한 경계에서 소유하므로 신규 hook이 필요하지 않다.

## 현재 Vote·Discussion 계약
- `selectedRow`는 현재 데이터에서 `selectedRowId` 검색 후 없으면 `rows[0]`으로 fallback한다.
- `useStatusTransition`에는 `currentStatus`만 전달하고 `resetKey`를 생략한다.
- 같은 상태의 다른 행으로 fallback되면 이전 `nextStatus`가 유효한 것으로 남을 수 있다.
- 공개 기준 초안은 plain `disclosureIndex`로 저장되어 어느 행에서 생성됐는지 식별할 수 없다.
- `hasDisclosureChange`, `canSave`, mutation payload는 현재 `selectedRow`와 전역 `disclosureIndex`를 결합한다.

## 확인된 결합 위험
1. 행 A에서 상태 또는 공개 기준 초안을 만든다.
2. 같은 query refetch에서 A가 사라지고 행 B가 `rows[0]`으로 fallback된다.
3. A와 B의 상태가 같으면 `currentStatus`만으로는 행 변경을 감지하지 못한다.
4. `resetKey`만 추가하면 상태 초안은 제거되지만 공개 기준 초안은 남는다.
5. A의 공개 기준 index와 B의 저장값이 다르면 B의 `canSave`가 활성화되고 B ID의 payload에 A 초안이 포함될 수 있다.

## 접근안 비교

| 접근안 | 상태 draft | 공개 기준 draft | 정확성 | 판단 |
|---|---|---|---|---|
| `resetKey`만 추가 | 행 ID 귀속 | 귀속 없음 | 부분 해결 | 비권고 |
| `resetKey` + 행 소유 공개 기준 초안 | 행 ID 귀속 | 행 ID 귀속 | 완전 해결 | 권고 |
| `useEffect`로 index 재동기화 | 행 ID 귀속 | effect 이후 보정 | 전이 렌더 위험 | 비권고 |

## 권고 재사용 방식
- Proposal의 행 소유 선택 패턴을 Vote와 Discussion process 내부에 각각 적용한다.
- 외부 반환 계약 `disclosureIndex`, `changeDisclosure(index)`는 유지한다.
- shared helper나 신규 hook을 만들지 않는다.

## 비목표
- API, DTO, parser, query key, mutation 구현 변경
- `useStatusTransition` 구현 변경
- controller, view, detail page 변경
- shared UI, CSS 변경
- 공개 기준 정책 또는 선택지 변경
- Proposal 코드 변경

## 제약
- 이전 Comment 섹션은 Watcher 미실행으로 `paused_after_generator` 상태다.
- 이 섹션도 Watcher 미실행으로 `paused_after_generator` 상태에서 보류한다.
