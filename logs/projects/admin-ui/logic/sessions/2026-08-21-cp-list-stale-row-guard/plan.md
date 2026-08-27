# 계획

## 요청 요약
- 승인된 적용 우선순위 중 첫 단계로 Proposal·Discussion·Vote 목록의 stale `placeholderData` 처리 위험을 제거한다.
- 사용자 정정 피드백에 따라 Proposal 목록 페이지의 직접 state·query·mutation 소유도 페이지 전용 hook과 view로 분리한다.

## 작업 유형
- feature + refactoring

## 범위
- 이전 응답을 표시하는 동안 행 선택, 상태/공개 기준 편집, 처리 저장, 상세 화면 이동을 비활성화한다.
- mutation handler에서도 현재 응답이 아닌 경우 즉시 중단하는 방어 조건을 둔다.
- 이전 목록 표시는 유지해 페이지 전환 시 시각적 연속성을 보존한다.
- Proposal 목록을 thin route page, search-state hook, controller hook, presentational view로 분리한다.

## 제외 범위
- Discussion·Vote의 route-container/presentational view 분리
- Discussion·Vote의 search-state/controller hook 추출
- URL query state 도입
- DTO-to-view mapper 도입
- query key 또는 cache invalidation 변경
- CSS·레이아웃·디자인 토큰 변경

## 섹션
1. 세 페이지에서 query 결과의 `isPlaceholderData`를 소비한다.
2. stale 응답 동안 `selectedRow`를 `null`로 만들고 행 클릭·mutation을 방어한다.
3. LSP, lint, build와 실제 브라우저에서 필터/페이지 전환 동작을 검증한다.
4. Proposal의 draft/applied query와 검색 전이 규칙을 `useCpProposalListSearchState`로 이동한다.
5. Proposal의 서버 상태·선택·mutation·Dialog·navigation을 `useCpProposalListController`로 이동한다.
6. JSX를 props 기반 `CpProposalListView`로 이동하고 route page는 controller와 view만 결선한다.
7. 리팩터 전후 기능·stale 상태·3개 viewport를 재검증한다.

## 필요 에이전트
- Planner: 외부 Anthropic 크레딧 차단으로 실행 불가. 기존 감사 계획과 사용자 승인으로 범위를 확정했다.
- Generator: 세 페이지 최소 수정.
- Watcher: 프로젝트 정책상 현재 Claude Code API 비가용으로 실행하지 않고 `paused_after_generator`로 보류한다.

## 필요 스킬
- `policy-harness`
- `policy-coding-convention`
- `policy-tanstack-query`
- `policy-review-checklist`
- `programming`
- `playwright`

## 리스크 / 가정
- stale 행은 계속 표에 보이지만 클릭·선택 스타일·처리 컨트롤은 활성화되지 않아야 한다.
- 동일 query key의 background refetch는 `isPlaceholderData`가 아니므로 현재 행 조작을 유지한다.
- 기존 미커밋 변경은 사용자 작업으로 간주하고 되돌리거나 재정렬하지 않는다.

## 수락 기준
- 세 목록에서 query key 변경 중 `selectedRow`가 `null`이다.
- stale 응답의 행 클릭과 처리 mutation이 실행되지 않는다.
- 새 응답 확정 후 첫 행 자동 선택과 기존 처리 흐름이 복원된다.
- lint와 build가 성공한다.
- `cp-proposal-list-page.tsx`에 직접 `useState`, query/mutation, router, Dialog가 없다.
- 검색·행 선택·stale/settled 전환·상세 화면 이동이 리팩터 전과 동일하게 동작한다.
- 리팩터 전 기준 이미지와 375·768·1280px 시각 결과가 일치한다.
- 같은 상태의 다른 제안으로 fallback되어도 이전 제안의 상태 변경 draft가 저장 가능 상태나 mutation payload에 남지 않는다.

## 승인
- 사용자가 2026-08-21 대화에서 `오케이 이 적용 우선순위에 맞게 작업 진행해봐.`라고 명시적으로 승인했다.

## 추가 정정 범위: Proposal 목록 책임 분리
- 사용자 피드백: stale guard만 적용한 뒤에도 `cp-proposal-list-page.tsx`에 state와 query orchestration이 그대로 노출되어 전체 요청이 충족되지 않았음을 지적했다.
- 정정 목표: Proposal 목록을 thin route page, page controller hook, search-state hook, presentational view로 분리한다.
- 상태 소유권:
  - search-state hook: draft filter, applied query, submit/reset/page 규칙.
  - page controller: query/mutation, 선택·처리 상태, stale guard, Dialog, navigation.
  - presentational view: FilterBar·Table·DetailPanel JSX와 callback 결선.
  - route page: controller 호출과 view 렌더링만 수행.
- 제외: 범용 generic controller, 다른 CP 도메인 동시 변경, URL 상태화, DTO mapper, CSS 변경.
- 추가 수락 기준: `cp-proposal-list-page.tsx`에 `useState`, entity query/mutation, router, Dialog가 없어야 한다.
- 정정 범위 승인 근거: 사용자가 Proposal 페이지의 직접 state 소유를 지적하며 helper hook 분리를 요청했다.
- 자체 검토 보완: 상태 변경 draft는 현재 상태뿐 아니라 선택 제안 ID가 달라져도 초기화하도록 `useStatusTransition.resetKey` 계약을 추가한다.

## 추가 리팩터 범위: Proposal controller 책임 세분화
- 사용자 피드백: `useCpProposalListController`가 조회·오류·KPI·retry·선택·draft·mutation을 계속 함께 소유해 controller 자체가 비대하다고 지적했다.
- 목표 구조: router → `CpProposalListPage` → orchestration controller → search/data/process hooks → View.
- 분리 경계:
  - `useCpProposalListData`: entity list query 조합, 오류 Dialog dedupe, stale 의미, KPI, pagination, retry.
  - `useCpProposalListProcess`: 선택, 상태·부서 draft, mutation, 저장 Dialog, reset 불변식.
  - `useCpProposalListController`: 검색 전환과 process reset 조정, View 계약 조립, navigation.
  - `cp-proposal-list.types.ts`: controller와 View 사이 공개 계약.
- 제외: 별도 route wrapper, generic list controller, table/action/helper-only hook, entity query/cache 변경.
- 추가 수락 기준:
  - controller가 query/mutation/Dialog/local draft를 직접 소유하지 않는다.
  - controller 함수 본문이 50~70줄 수준의 orchestration만 담당한다.
  - 실제 status mutation, stale/settled, 동일 상태 교차 행 draft, 상세 이동이 보존된다.
- 추가 승인: 사용자가 2026-08-21 대화에서 `작업 진행`으로 명시적으로 승인했다.
