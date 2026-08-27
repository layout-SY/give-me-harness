# 리뷰 로그

## 리뷰 대상
- Vote·Discussion 목록 process hook의 상태·공개 기준 draft 행 소유권.
- same-query refetch에서 선택 행이 fallback될 때 UI, `canSave`, mutation payload 경계.

## 결과
- `paused_after_generator`
- 구현과 정적·브라우저·독립 시각 검토는 통과했지만 프로젝트 Watcher를 실행하지 않았으므로 `confirmed` 또는 Closure로 처리하지 않는다.

## 체크리스트 검토
- SKILL 준수: `policy-harness`, `policy-coding-convention`, `policy-refactoring`, `policy-hook-extraction`, `policy-abstraction-strategy`, `policy-type-definition`, `policy-documentation`, `policy-review-checklist`, `programming`, `frontend`, `playwright`, `visual-qa` 확인.
- 재사용 확인: 기존 `useStatusTransition.resetKey`와 Proposal의 행 소유 selection 패턴 재사용.
- 범위 확인: Vote·Discussion list process 두 파일만 수정. controller, View, detail, entity, API, DTO, mutation, shared UI, CSS는 무수정.
- 상태 draft: `resetKey`가 `selectedRow.id`를 추적해 같은 상태의 다른 행에서도 즉시 `nextStatus=null`.
- 공개 기준 draft: 현재 행 ID와 draft 소유 ID가 일치할 때만 effective index에 참여.
- payload: 현재 행에서 파생한 `selectedDisclosureRule`만 현재 `selectedRow.id` mutation에 포함.
- 저장 guard: `isCurrentData`, `selectedRow`, `canSave`, mutation guard를 모두 확인.
- 현재 행 보존: 동일 행 refetch에서는 해당 행 소유 disclosure draft를 유지할 수 있다.
- 초기화: reset, 명시적 행 선택, mutation 성공 시 disclosure draft 제거.
- 타입: readonly local value type, 외부 hook 반환 interface 유지, 타입 우회 없음.
- 정적 검증: scoped ESLint, `tsc -b` 포함 production build, scoped diff check 통과.
- 브라우저 Vote: VT-001 제거 후 VT-002 fallback에서 상태 placeholder, VT-002 persisted 공개 기준, 저장 비활성 확인.
- 브라우저 Discussion: DS-001 제거 후 DS-002 fallback에서 상태 placeholder, DS-002 persisted 공개 기준, 저장 비활성 확인.
- console: error 0건, warning 0건.
- 시각 검토: 수정된 complete 캡처 세트의 independent Oracle 2회 `PASS`, 차단 0건.

## 위반 사항 / 차단
1. TypeScript LSP 미설치로 LSP diagnostics를 실행하지 못했다.
2. Bun 미설치로 programming no-excuse script를 실행하지 못했다.
3. 프로젝트 test runner script가 없어 자동 회귀 테스트가 없다.
4. 구성된 Planner·Generator는 외부 provider credit 소진으로 시작하지 못해 동일 역할 계약의 독립 실행 경로를 사용했다.
5. Watcher API 비가용으로 실제 `confirmed` verdict가 없다.

## 필수 수정 사항
- 현재 구현 범위의 추가 수정 사항은 발견되지 않았다.
- Closure 전 프로젝트 Watcher의 실제 `confirmed` 판정이 필요하다.

## 잔여 관찰
- Vote 날짜 placeholder 마지막 음절 줄바꿈은 기존 UI 부채이며 이번 process 변경과 무관하다.
- fixture의 공개 기준 선택지는 현재 하나뿐이므로 index `-1` 입력은 기존 callback을 runtime 계측으로 호출해 검증했다.

## 반복 이슈
- false

## 에스컬레이션
- 외부 의존성 차단: 구성된 Planner·Generator·Watcher 실행 환경.
