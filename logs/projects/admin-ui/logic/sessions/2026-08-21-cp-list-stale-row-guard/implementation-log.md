# 구현 로그

## 작업 요약
- Proposal·Discussion·Vote 목록이 TanStack Query의 이전 `placeholderData`를 표시하는 동안 stale 행을 선택하거나 처리 mutation 대상으로 사용할 수 없게 했다.
- Proposal 목록의 검색 상태·서버 상태·mutation·Dialog·navigation·JSX를 route page에서 분리했다.

## 재사용 자산
- TanStack Query query 결과의 `isPlaceholderData`.
- 기존 `Table.onRowClick` optional 계약.
- 기존 상세 패널과 `Button`·`Dropdown`·`StatusTransitionField`의 disabled 계약.

## 수정 파일
- `src/features/cp-status-transition/hook/useStatusTransition.ts`
- `src/pages/cp-proposal/ui/cp-proposal-list-page.tsx`
- `src/pages/cp-proposal/ui/use-cp-proposal-list-search-state.ts`
- `src/pages/cp-proposal/ui/use-cp-proposal-list-controller.tsx`
- `src/pages/cp-proposal/ui/use-cp-proposal-list-data.tsx`
- `src/pages/cp-proposal/ui/use-cp-proposal-list-process.tsx`
- `src/pages/cp-proposal/ui/cp-proposal-list.types.ts`
- `src/pages/cp-proposal/ui/cp-proposal-list-view.tsx`
- `src/pages/cp-discussion/ui/cp-discussion-list-page.tsx`
- `src/pages/cp-vote/ui/cp-vote-list-page.tsx`

## 핵심 로직
- `isPlaceholderData`가 `true`이면 `selectedRow`를 `null`로 만든다.
- stale 응답 동안 `Table.onRowClick`을 전달하지 않아 마우스·키보드 선택 affordance를 제거한다.
- 각 `handleRowClick`과 `handleSaveProcess`에도 `isCurrentData` guard를 두어 이벤트 참조가 남더라도 실행을 중단한다.
- Proposal의 `canSaveProcess`도 `selectedRow !== null`을 필수 조건으로 맞췄다.
- query hook, cache, API, 공용 Table, CSS는 변경하지 않았다.

## Proposal 책임 분리
- `useCpProposalListSearchState`로 draft filter, 적용 query, 검색·초기화·페이지 이동 규칙을 옮겼다.
- `useCpProposalListController`로 query/mutation, 선택·처리 상태, stale guard, Dialog, navigation을 옮겼다.
- `CpProposalListView`는 FilterBar·Table·DetailPanel을 props와 callback으로만 결선한다.
- `cp-proposal-list-page.tsx`는 10줄의 controller/view 결선만 남겼다.
- 범용 helper나 API/cache 변경 없이 기존 Proposal 도메인 계약을 그대로 유지했다.
- `useStatusTransition`에 선택적 `resetKey`를 추가해 `currentStatus` 또는 선택 대상 ID 중 하나가 바뀌면 해당 렌더부터 `nextStatus`를 비활성화하고 내부 draft를 초기화한다.
- Proposal controller는 `selectedRow.id`를 `resetKey`로 전달하고 기존 `canSaveProcess`와 payload가 활성 `nextStatus`만 사용하도록 유지했다.

## Proposal controller 책임 세분화
- `CpProposalListController` 공개 계약을 `cp-proposal-list.types.ts`로 이동해 View가 controller 구현을 type import하지 않게 했다.
- `useCpProposalListData`가 기존 entity query를 단 한 번 호출하고 오류 Dialog dedupe, stale/current 의미, rows, pagination, KPI, retry를 page surface 값으로 변환한다.
- `useCpProposalListProcess`가 선택 ID, 첫 행 fallback, 상태·부서 draft, stale 저장 차단, 변경 필드 payload, mutation 성공·실패 Dialog를 소유한다.
- `useCpProposalListController`는 search/data/process 조합, submit/reset/page 전환과 process reset 조정, View 계약 조립, detail navigation만 남겼다.
- 파일 크기: page 10줄, View 127줄, contract 57줄, controller 72줄, search 64줄, data 58줄, process 123줄. 모든 파일이 250줄 미만이다.
- entity query key, cache update/invalidation, API, DTO, parser, shared UI와 CSS는 변경하지 않았다.

## 검증 / 요청 처리
- `git diff --check` 통과.
- 변경한 세 파일 대상 ESLint 통과.
- `yarn build` 통과(TypeScript project build + Vite production build).
- 전체 `yarn lint`는 이번 세 파일과 무관한 기존 73개 오류와 5개 경고로 실패했다.
- TypeScript LSP는 설치되어 있지 않고 사용자가 이전에 설치를 거부한 상태라 diagnostics를 실행할 수 없었다.
- programming skill의 no-excuse 스크립트는 로컬에 `bun`이 없어 실행할 수 없었다.
- Planner와 Generator 하위 에이전트는 Anthropic 크레딧 차단으로 실행되지 않아 승인된 계획에 따라 orchestrator가 최소 변경을 직접 적용했다.
- 추가 controller 분리 단계의 Planner와 Refactorer도 Anthropic 크레딧 차단으로 실행되지 않아 승인된 계획과 Oracle 경계 검토를 따라 orchestrator가 직접 적용했다.
- Playwright에서 Proposal·Discussion·Vote 요청을 각각 1.2초 지연해 stale 구간을 실제 재현했다. stale 구간에는 이전 행이 남아 있어도 클릭 가능 행과 선택 행이 0개였고 저장·상세 버튼이 비활성화됐다. 새 응답 후에는 클릭 가능 행과 첫 행 선택이 복구됐다.
- 375·768·1280px의 세 페이지 stale 상태 9개를 캡처했고 독립 시각 검토 2회에서 현재 변경 범위가 모두 PASS였다.
- Proposal 리팩터 후 변경한 4개 파일 대상 ESLint와 `yarn build`가 통과했다.
- Playwright에서 초기 첫 행 선택, 두 번째 행 상세 갱신, 1.2초 지연 stale 구간의 클릭·선택·처리 비활성화, settled 후 첫 행 선택 복원, `/cp/proposals/CP-001` 상세 이동을 확인했다.
- 브라우저 console error는 0건이었다.
- 리팩터 전 기준 이미지와 리팩터 후 375·768·1280px 이미지를 비교해 모두 100/100 유사도를 확인했다. 375px의 13픽셀 차이는 diff ratio 0으로 판정됐고 768·1280px는 0픽셀 차이였다.
- Oracle 1차 자체 검토에서 같은 상태의 다른 제안으로 fallback될 때 상태 draft가 누수될 수 있는 차단 결함을 발견했다.
- 새 브라우저에서 CP-001 `REVIEWING`에 `ADOPTED` draft를 만든 뒤 mock 데이터를 변경하고 같은 query key를 invalidate했다. CP-005 `REVIEWING`으로 fallback되자 상태 필드는 placeholder로 복원되고 저장 버튼은 비활성화됐다.
- CP-001을 원상복구한 뒤에도 draft는 비어 있고 저장 버튼은 비활성화됐으며 fresh-session console error는 0건이었다.
- Oracle 2차 재검토에서 같은 상태·다른 ID와 같은 ID·다른 상태 모두 초기화되고 handler/payload까지 동일 활성값으로 게이트됨을 확인해 차단 발견 0건 판정을 받았다.
- controller 세분화 후 대상 7개 파일 ESLint, `tsc -b` + Vite production build, `git diff --check`가 통과했다.
- Playwright에서 첫 행 fallback, CP-002 선택, 실제 `RECEIVED → REVIEWING` 저장, 성공 Dialog, 선택 유지, draft 초기화와 원상복구를 확인했다.
- 1.2초 지연 검색에서 stale 행 10개는 유지됐지만 클릭 가능 행·선택 행은 0개였고 저장·상세 이동은 비활성화됐다. settled 후 첫 행 선택과 상호작용이 복구됐다.
- 동일 `REVIEWING` 상태의 CP-001 draft를 만든 뒤 same-key refetch로 CP-005에 fallback시켜 draft와 저장 가능 상태가 누출되지 않음을 재확인했다.
- 상세 URL `/cp/proposals/CP-001` 이동과 fresh-session console error 0건을 확인했다.
- 이전 기준 이미지와 375·768·1280px를 비교해 모두 100/100 유사도였다. 독립 시각 검토 2회 모두 PASS, 차단 0건이었다.
- 코드 품질 Oracle은 서버 상태 복제·순환 의존·pass-through 추상화 없이 책임이 분리됐다고 판정했으며 차단 발견 0건이었다.

## 리스크
- 현재 작업 트리에 기존 대규모 미커밋 변경이 있어 전체 검증 실패 시 이번 변경과 선행 변경을 구분해야 한다.
- 테스트 runner가 프로젝트 script에 등록되어 있지 않아 회귀 테스트는 추가하지 않고 실제 브라우저 시나리오로 보완한다.
- 기존 반응형 표 잘림, 토론 모바일 여백, 투표 날짜 placeholder 줄바꿈은 이번 변경과 무관한 별도 잔여 이슈다.
- Proposal 375px에서도 기존 테이블 우측 열·페이지네이션 클리핑과 접힌 사이드바 잔여 폭이 재확인됐으나 리팩터 전 기준 이미지와 동일해 범위에서 제외했다.
- process 내부 ID가 사라진 행을 기억한 채 UI는 첫 행으로 fallback하므로 같은 query에서 해당 ID가 다시 나타나면 선택이 복원될 수 있는 낮은 잠재 위험이 있다.
- 캐시가 있는 background refetch 실패에서는 오류 Dialog는 표시되지만 retry ActionBar는 기존 계약대로 노출되지 않는다.

## 핸드오프 메모
- Generator 범위 구현 완료.
- 프로젝트 정책상 Watcher는 실행하지 않으며, 정적·브라우저 검증 후 `paused_after_generator`로 보류한다.
- Oracle은 Watcher를 대체하지 않으며, 차단 결함 수정의 교차 검토 증거로만 기록한다.
