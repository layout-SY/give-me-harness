# 포트폴리오 경험 기록

## 작업 개요
- 구현/수정 내용: CP Comment 목록에서 TanStack Query의 이전 목록 유지 UX는 보존하면서 stale 행의 선택·상세·상태 변경·저장을 차단했다.
- 구현 이유: query key 전환 중 이전 첫 행이 새 query의 처리 대상으로 노출될 수 있는 correctness 위험을 제거하기 위해서다.
- 작업 유형: correctness bug fix.
- 품질 상태: Generator 구현·정적·브라우저 검증 완료, Watcher `confirmed` 대기 중인 `paused_after_generator`.

## 문제 상황
- 문제 출처: 구조적 위험.
- 대상 도메인·서비스: 시민참여 Comment 통합 관리자 목록.
- 기존 문제와 영향: `placeholderData(previousData)`가 이전 행을 유지하는 동안 process의 `rows[0]` fallback과 항상 노출된 `onRowClick` 때문에 stale 행이 선택·처리 대상으로 남을 수 있었다.

## 요구사항 및 의사결정
- 사용자 요구·제안: 감사에서 도출된 개선 순서를 승인하고 한 번에 한 섹션씩 구현한다.
- 에이전트 제안: 첫 섹션에서 Comment freshness 경계만 최소 변경하고 다른 도메인·cache·날짜 검증은 후속 섹션으로 분리한다.

| 접근법 | 장점 | 단점 | 선택 여부와 이유 |
|---|---|---|---|
| `placeholderData` 제거 | stale 행 자체가 사라짐 | 목록 연속성과 기존 UX를 잃음 | 미선택: 표시 UX는 유지해야 함 |
| controller에서 클릭만 제거 | UI 입력 차단이 단순함 | 첫 행 fallback·직접 handler 호출·저장 경로가 남음 | 미선택: 로직 안전 경계 불완전 |
| data/process/controller에 freshness 전달 | 표시 UX 유지, 상세·입력·mutation 다중 방어 | page-local 계약 추가 | 선택: 최소 변경으로 계층 책임과 안전성 유지 |
| 범용 freshness helper 추가 | 여러 도메인 중복 축소 가능 | 현재 단일 섹션 범위를 확대하고 도메인 process 차이를 은폐 | 미선택: 추상화 4조건 미충족 |

## 사용 기술과 구체적 목적

| 기술/패턴/아키텍처 | 해결하려는 문제 | 적용 위치와 목적 | 미채택 대안/이유 |
|---|---|---|---|
| TanStack Query `isPlaceholderData` | 이전 응답과 현재 응답 구분 | data hook에서 `isCurrentData`로 변환 | `isFetching`은 background refetch까지 차단 |
| derived selection invariant | stale 첫 행 자동 선택 방지 | process에서 stale `selectedRow=null` | effect 기반 reset은 렌더 한 번 늦을 수 있음 |
| optional `Table.onRowClick` | stale 행 마우스·키보드 입력 차단 | controller가 현재 데이터에만 callback 제공 | shared Table 변경은 영향 범위 과다 |
| handler guard | 남은 직접 호출 경로 방어 | `selectRow`, `save` early return | disabled UI만으로 로직 안전성 보장 불가 |
| Playwright XHR 지연 | 짧은 placeholder 구간의 실제 관찰 | 탭 전환 GET을 15초 지연 | 정적 판독만으로 렌더·입력 계약 입증 불가 |

## 적용 내용
- `useCpCommentListData`가 `isCurrentData: !isPlaceholderData`를 노출하도록 변경했다.
- `useCpCommentListProcess`가 `{ rows, isCurrentData }`를 받고 stale 상태의 선택·상태·저장 가능성을 제거했다.
- `useCpCommentListController`가 freshness를 process에 전달하고 현재 데이터일 때만 행 클릭을 노출하도록 변경했다.
- `CpCommentListTableController.onRowClick`을 optional 계약으로 정렬했다.
- View, shared Table, entity query, mutation, API, DTO, CSS는 변경하지 않았다.

## 결과 및 성과
- before: query 전환 중 이전 목록이 남으면 process가 이전 첫 행을 상세·처리 대상으로 파생할 수 있었다.
- after: 지연된 탭 전환에서 이전 행 9개가 표시돼도 클릭 가능 행 0개, 선택 행 0개였고 click·Enter 입력과 처리·저장이 차단됐다.
- 최신 응답 후 첫 행 선택, 명시적 행 선택, 처리 상태 변경 후 저장 활성화가 정상 복구됐다.
- 검증 결과: scoped ESLint, production build, scoped diff check 통과. 1391×1043 두 상태의 독립 Visual QA Oracle 2회가 `PASS`했고 console error·warning은 0건이었다.
- 사용자 후속 피드백: 구현 후 추가 피드백은 확인되지 않았다.
- 잔여 리스크: TypeScript LSP 미설치, 전체 lint 기존 오류, Watcher 미실행으로 Closure는 보류한다.

## 회고
- 잘된 판단: stale 행 표시와 stale 행 처리 가능성을 분리해 UX 연속성은 유지하고 mutation 안전성만 강화했다.
- 잘된 판단: controller callback 제거에만 의존하지 않고 process의 파생 상태와 handler도 함께 방어했다.
- 다시 한다면 바꿀 점: 처음부터 XHR transport 지연을 사용했다면 Service Worker 때문에 CDP 지연이 적용되지 않았던 이전 탐색 비용을 줄일 수 있었다.
- 다음 작업에 적용할 인사이트: `placeholderData`를 사용하는 선택형 목록은 callback 비활성뿐 아니라 fallback selection과 mutation handler까지 동일 freshness 불변식으로 검증해야 한다.
