# 탐색 기록

## 대상 경로
- `src/shared/ui/table/`
- `src/shared/ui/button/`
- `src/widgets/admin-page-layout/`
- `src/entities/cp-proposal/model/`
- `src/entities/cp-discussion/model/`
- `src/entities/cp-vote/model/`
- `src/pages/cp-proposal/ui/`
- `src/pages/cp-discussion/ui/`
- `src/pages/cp-vote/ui/`
- `.agents/skills/reference/`
- `.codex/memory/reusable-assets.md`

## 발견한 기존 재사용 자산
- 발견 항목: TanStack Query 목록 훅, `Table`, `Button`, `StatusTransitionField`, `MasterDetailLayout`.
- 재사용 제안: 기존 query 결과의 `isPlaceholderData`와 기존 컴포넌트의 `disabled`·`isLoading` 계약만 사용한다.
- 근거: 세 목록 훅은 `placeholderData`로 이전 응답을 유지하고, 세 페이지는 query 결과를 직접 결선한다.

## 확인된 문제
- 필터 또는 페이지 변경 시 `selectedRowId`를 초기화해도 `rows[0]` fallback이 이전 응답의 첫 행을 다시 선택한다.
- 세 페이지가 `isPlaceholderData`를 소비하지 않아 이전 행의 클릭·처리 mutation을 막지 못한다.
- 기존 작업 트리에 대규모 미커밋 변경이 있으므로 대상 세 페이지 외 변경은 건드리지 않는다.

## 재사용이 어려운 자산
- 자산: `useFetchAdapter`.
- 부적합 사유: 현재 화면은 TanStack Query entity hook을 사용하며 이를 다시 감싸면 서버 상태 계약이 이중화된다.

## 신규 자산 필요성
- stale guard 단계 필요 항목: 없음.
- Proposal 책임 분리 단계 필요 항목:
  - 페이지 전용 search-state hook.
  - 페이지 전용 controller hook.
  - props 기반 presentational view.
- 필요 이유: `cp-proposal-list-page.tsx`가 250줄 이상에서 검색·서버 상태·선택·mutation·Dialog·navigation·JSX를 동시에 소유한다.
- 재사용 근거: `use-cp-comment-list-page.tsx`의 page hook 패턴과 user-ui의 route-to-view props 결선 패턴을 조합하되 Proposal 도메인 계약은 독립 유지한다.

## Proposal 책임 분리 결론
- `cp-proposal-list-page.tsx`는 282줄에서 검색 상태, query/mutation, Dialog, navigation, JSX를 함께 소유하고 있었다.
- `useCpProposalListSearchState`는 draft와 적용 query를 분리하고 검색·초기화·페이지 전이 시 page를 1로 되돌리는 규칙을 소유한다.
- `useCpProposalListController`는 stale guard를 포함한 서버 상태와 처리 흐름을 하나의 페이지 application 계약으로 제공한다.
- `CpProposalListView`는 query·router·mutation을 import하지 않고 controller가 제공한 값과 callback만 렌더링한다.
- generic controller나 전역 search-state로 확장하지 않았다. 현재 반복 횟수와 도메인 차이를 고려하면 페이지 전용 분리가 최소 추상화다.

## 자체 검토에서 발견한 상태 draft 경계
- 기존 `useStatusTransition`은 `currentStatus` 변경만 추적해 같은 상태의 다른 행으로 fallback되면 이전 행의 `nextStatus`가 남을 수 있었다.
- 선택 행 ID와 현재 상태를 모두 초기화 기준으로 삼아야 UI의 저장 가능 여부와 mutation payload가 동일한 행에 귀속된다.
- 공용 hook에는 선택적 `resetKey`만 추가하고 Proposal controller가 `selectedRow.id`를 전달해 기존 11개 호출부의 상태 기반 동작은 유지했다.

## Controller 추가 분리 판단
- 기존 controller 223줄은 query/error/KPI/retry, selection/process mutation, View 계약 조립을 함께 소유했다.
- 가장 가까운 기존 패턴은 Comment의 page-local controller였지만, Proposal은 process draft와 mutation 불변식이 더 커서 data/process 하위 hook이 추가로 필요했다.
- `useFetchAdapter`는 자체 fetch sequencing을 가진 공용 Table adapter라 TanStack Query entity hook을 사용하는 Proposal에는 부적합했다.
- 별도 route wrapper는 `routes.tsx`가 이미 `CpProposalListPage`를 직접 연결하므로 상태나 boundary 책임이 없는 pass-through가 된다.
- selection과 process를 나누면 행 전환마다 상태·부서 draft reset 순서가 controller로 역류하므로 하나의 process hook으로 유지했다.
- KPI/payload/retry helper는 단일 호출처의 무상태 계산이라 별도 hook으로 추출하지 않았다.
- View 공개 계약만 구현 파일에서 분리해 View → controller 구현 의존을 제거했다.
