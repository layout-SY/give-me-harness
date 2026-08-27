# 계획

## 요청 요약
- CP Comment 목록이 TanStack Query의 `placeholderData(previousData)`를 표시하는 동안 이전 행이 선택·수정·저장 대상으로 남지 않도록 차단한다.

## 작업 유형
- refactor

## 범위
- `useCpCommentListData`가 `isPlaceholderData`를 `isCurrentData`로 변환해 노출한다.
- `useCpCommentListProcess`가 freshness를 입력받아 stale 행의 자동 선택, 직접 선택, 상태 변경, 저장을 차단한다.
- `useCpCommentListController`가 현재 데이터에만 행 클릭 계약을 제공한다.
- Comment 목록 table controller의 `onRowClick`을 optional 계약으로 정렬한다.

## 제외 범위
- CSS, 마크업, `cp-comment-list-view.tsx`, 공용 `Table` 변경
- API, DTO, parser, query key, mutation 변경
- `placeholderData` 제거 또는 로딩 UX 변경
- Proposal, Vote, Discussion 및 다른 CP 도메인 변경
- 신규 공용 hook·컴포넌트·추상화·테스트 프레임워크 추가

## 섹션
1. `useCpCommentListData`에 `isCurrentData: !isPlaceholderData` 계약을 추가한다.
2. `useCpCommentListProcess`를 `{ rows, isCurrentData }` 계약으로 변경하고 stale 상태를 내부에서 차단한다.
3. controller가 freshness를 process에 전달하고 현재 데이터일 때만 `onRowClick`을 노출한다.
4. 변경 파일 scoped lint, build, diff 검사와 브라우저 상호작용을 검증한다.

## 필요 에이전트
- planner: 구현 범위·레이어·재사용 계약 확정
- generator: 승인된 네 파일의 최소 diff 구현과 검증
- watcher: API 복구 후 최종 판정

## 필요 스킬
- `policy-harness`
- `policy-coding-convention`
- `policy-refactoring`
- `policy-hook-extraction`
- `policy-data-fetch-layer`
- `policy-tanstack-query`
- `policy-type-definition`
- `policy-documentation`
- `recipe-data-fetch`
- `component-table`

## 불변식
- 현재 query 데이터에서는 기존 첫 행 fallback, 명시적 행 선택, 변경·저장 흐름을 유지한다.
- 이전 query placeholder에서는 `selectedRow`가 반드시 `null`이고 `canSave`가 반드시 `false`다.
- placeholder에서는 controller가 `onRowClick`을 제공하지 않으며 process 직접 호출도 stale 행을 선택·저장할 수 없다.
- 동일 query의 background refetch는 `isPlaceholderData`가 아니므로 정상 상호작용을 차단하지 않는다.

## 리스크 / 가정
- controller만 차단하면 process의 첫 행 fallback으로 stale 상세가 남으므로 process 내부 차단도 함께 적용한다.
- `isFetching`은 background refetch도 포함하므로 freshness 기준으로 사용하지 않는다.
- 공용 `Table.onRowClick`이 이미 optional이므로 View와 공용 UI는 변경하지 않는다.
- Watcher API는 비가용 상태다. Generator 완료 후 `paused_after_generator`에서 보류하고 Closure를 실행하지 않는다.

## 승인
- 사용자는 전체 개선 순서와 첫 번째 Comment stale-row 차단 구현을 `오케이. 승인`으로 승인했다.

## 실행 상태
- 사용자 승인 완료
- planner 결정 완료
- 다음 단계: generator
