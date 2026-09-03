# 탐색 기록

## 스킬 확인
- 확인한 `SKILL.md`: `policy-harness`, `policy-coding-convention`, `policy-refactoring`, `policy-hook-extraction`, `policy-data-fetch-layer`, `policy-tanstack-query`, `policy-type-definition`, `policy-documentation`, `recipe-data-fetch`, `component-table`
- 근거: 구현 전 정책·recipe·reference 원문을 확인하고 Comment 변경 범위와 기존 자산 재사용 여부를 교차 검토했다.

## 대상 경로
- `src/shared/ui/`
- `src/widgets/`
- `src/pages/cp-comment/`
- `src/entities/cp-comment/`
- `src/pages/cp-proposal/`
- `src/pages/cp-vote/`
- `src/pages/cp-discussion/`
- `.agents/skills/reference/`
- `.codex/memory/reusable-assets.md`

## 현행 데이터 흐름
- `useCpCommentListQuery`는 `placeholderData(previousData)`로 query 전환 중 이전 목록을 유지한다.
- `useCpCommentListData`는 `isPlaceholderData`를 반환하지 않아 화면 계층이 이전 행과 현재 행을 구분하지 못한다.
- `useCpCommentListProcess`는 선택 ID가 없거나 유효하지 않으면 `rows[0]`을 선택해 placeholder 첫 행도 상세 대상으로 노출한다.
- `useCpCommentListController`는 데이터 freshness와 관계없이 `process.selectRow`를 `onRowClick`으로 노출한다.

## 발견한 기존 재사용 자산
- `src/shared/ui/table/table.tsx`: optional `onRowClick`을 지원하며 `undefined`일 때 클릭·키보드 선택·선택 접근성 속성을 제공하지 않는다.
- `src/pages/cp-proposal/ui/use-cp-proposal-list-data.tsx`: `isPlaceholderData`를 `isCurrentData`로 변환하는 기준 구현이다.
- `src/pages/cp-proposal/ui/use-cp-proposal-list-process.tsx`: stale 상태에서 선택과 변경을 차단하는 기준 구현이다.
- `src/pages/cp-proposal/ui/use-cp-proposal-list-controller.tsx`: 현재 데이터에만 행 클릭 계약을 노출하는 기준 구현이다.
- Vote·Discussion 목록에도 동일한 freshness 전달 패턴이 있어 도메인 간 계약 일관성을 확인했다.

## 재사용 결정
- Comment 전용 data/process/controller에 기존 freshness 계약을 적용한다.
- 공용 `Table`의 optional `onRowClick`을 그대로 재사용한다.
- `cp-comment-list-view.tsx`는 기존에 controller 값을 그대로 전달하므로 수정하지 않는다.
- 단일 도메인 적용이므로 신규 공용 hook·component·generic controller를 만들지 않는다.

## FSD / 의존 방향
- `pages/cp-comment`의 data hook이 `entities/cp-comment` query 결과의 freshness를 화면용 boolean으로 변환한다.
- process hook은 화면 상호작용과 mutation 전 가드를 소유한다.
- controller는 data와 process를 조립하고 View에 optional interaction 계약만 제공한다.
- shared UI와 entity query의 공개 계약은 변경하지 않는다.

## 리스크 / 제약
- `isFetching`을 사용하면 동일 query background refetch도 차단되므로 `isPlaceholderData`만 사용한다.
- UI callback만 제거하면 직접 호출 경로와 첫 행 fallback이 남으므로 process 내부 guard가 필수다.
- 프로젝트에 자동 테스트 프레임워크가 없어 scoped lint, build, 실제 브라우저 조작으로 검증한다.
- Watcher API 비가용으로 최종 품질 판정과 Closure는 수행할 수 없다.

## 신규 자산 필요성
- 필요 항목: 없음
- 이유: 기존 data/process/controller 구조와 optional `Table.onRowClick` 계약만으로 요구사항을 충족한다.
