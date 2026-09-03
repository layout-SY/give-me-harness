# 포트폴리오 경험 기록

## 작업 개요
- 구현/수정 내용: TanStack Query의 이전 목록 유지 기능과 관리자 처리 UI 사이에 stale 데이터 안전 경계를 추가하고 Proposal 목록의 route·controller·data·process·view 책임을 분리했다.
- 구현 이유: 필터·페이지 전환 중 이전 첫 행이 처리 대상으로 다시 선택되는 경쟁 조건과 Proposal route page의 책임 집중을 함께 제거하기 위해서다.
- 작업 유형: correctness bug fix + page architecture refactoring.

## 문제 상황
- 문제 출처: 구조적 위험과 브라우저 재현.
- 대상 도메인·서비스: 시민제안, 시민토론, 시민투표 관리자 목록.
- 기존 문제와 영향: query key가 바뀐 뒤 `placeholderData`가 이전 행을 유지하는 동안 `rows[0]` fallback이 이전 첫 행을 선택해 처리 mutation 대상이 될 수 있었다.

## 요구사항 및 의사결정
- 사용자 요구·제안: 비교 감사의 적용 우선순위에 맞춰 작업을 진행한다.
- 에이전트 제안: correctness 위험을 먼저 차단한 뒤 구조 리팩터링을 별도 섹션으로 진행한다.
- 사용자 후속 피드백: Proposal 페이지에 직접 남은 state를 helper hook으로 이동해 실제 책임 분리를 완성하도록 정정 요청했다.

| 접근법 | 장점 | 단점 | 선택 여부와 이유 |
|---|---|---|---|
| `placeholderData` 제거 | stale 행 자체가 사라짐 | 페이지 전환 시 목록 연속성과 기존 UX 손실 | 미선택 |
| query hook에서 data 제거 | page 수정 감소 | entity query 계약이 UI 정책을 소유 | 미선택 |
| page에서 `isPlaceholderData` 소비 | 이전 행 표시 유지, 처리만 차단 | 세 페이지에 불변식 명시 필요 | 선택: 최소 변경으로 계층 책임 유지 |
| Proposal 전용 search/controller hook + props view | 도메인 규칙 보존, route page 축소, 실제 동작 검증 용이 | 페이지 전용 파일 증가 | 선택: 범용 추상화 없이 책임 경계만 분리 |
| 범용 generic list controller | 여러 목록에 재사용 가능성 | 도메인별 필터·mutation·검증 차이를 union/분기로 은폐 | 미선택 |

## 사용 기술과 구체적 목적

| 기술/패턴/아키텍처 | 해결하려는 문제 | 적용 위치와 목적 | 미채택 대안/이유 |
|---|---|---|---|
| TanStack Query `isPlaceholderData` | 이전 응답과 현재 응답 구분 | 세 목록 page에서 현재 응답만 선택·처리 | cache 정책 변경은 UX와 entity 계약에 영향 |
| optional `Table.onRowClick` | stale 행의 마우스·키보드 선택 차단 | stale 기간에 callback 미전달 | 공용 Table 수정은 영향 범위 과다 |
| handler guard | 남은 이벤트 참조의 mutation 차단 | row/save handler early return | UI disabled만으로는 로직 안전성 부족 |
| Playwright XHR 지연 | 짧은 stale 구간을 관찰 가능하게 재현 | 세 목록의 stale/settled 상태 검증 | 정적 코드 판독만으로 실제 UI를 입증할 수 없음 |
| page controller hook | 서버 상태·선택·mutation·Dialog·navigation 응집 | Proposal 목록 application 계약 | route page 직접 소유는 변경 이유를 확산 |
| props 기반 view | JSX와 application orchestration 분리 | FilterBar·Table·DetailPanel 렌더링 | view 내부 query 호출은 표시 책임을 침범 |
| `useStatusTransition.resetKey` | 같은 상태의 다른 행으로 draft 누수 차단 | Proposal 선택 ID와 상태 draft 귀속 | controller별 중복 상태 저장은 공용 전이 계약과 중복 |
| page-local data hook | 조회 surface 책임 집중 제거 | entity query 결과를 오류·stale·KPI·pagination·retry 계약으로 변환 | entity query를 범용 fetch adapter로 다시 감싸면 cache 계약 중복 |
| page-local process hook | 선택과 처리 draft/mutation 불변식 응집 | selected row, status/department draft, changed-field payload, Dialog | selection/action hook을 따로 만들면 reset 순서와 callback 입력이 증가 |
| 별도 View contract | View의 controller 구현 의존 제거 | controller와 View가 type-only 계약 공유 | 전체 내부 타입을 한 파일로 모으면 결합도가 다시 증가 |

## 적용 내용
- 세 페이지에서 `isPlaceholderData`를 소비하고 `isCurrentData` 불변식을 정의했다.
- stale 기간에는 `selectedRow`를 `null`로 만들고 `Table.onRowClick`을 제거했다.
- 행 클릭과 저장 handler에도 stale guard를 추가했다.
- API, query key, cache, 공용 컴포넌트, CSS는 변경하지 않았다.
- Proposal의 draft/applied query와 검색 전이를 `useCpProposalListSearchState`로 이동했다.
- query/mutation, 선택·처리, stale guard, Dialog, navigation을 `useCpProposalListController`로 이동했다.
- JSX는 `CpProposalListView`로 이동하고 route page는 10줄의 controller/view 결선만 남겼다.
- 자체 검토에서 발견한 교차 행 상태 draft 누수를 `currentStatus`와 선택 ID의 복합 초기화 경계로 차단했다.
- query/error/KPI/retry는 `useCpProposalListData`, selection/draft/mutation은 `useCpProposalListProcess`로 이동했다.
- controller는 223줄에서 72줄로 축소하고 search transition과 process reset 조정, View 계약 조립, navigation만 남겼다.
- View 공개 계약을 별도 타입 파일로 이동해 View가 controller 구현을 import하지 않게 했다.

## 결과 및 성과
- before: query 전환 중 이전 행이 선택·처리 가능한 상태로 남을 수 있었다.
- after: Playwright 지연 시나리오에서 이전 행 4~10개가 표시되어도 클릭 가능 행 0개, 선택 행 0개, 저장·상세 버튼 비활성으로 확인됐다. 새 응답 후 클릭 가능 행과 첫 행 선택이 복구됐다.
- 구조 결과: Proposal route page에서 직접 `useState`, query/mutation, router, Dialog를 제거했다.
- 검증 결과: 변경 파일 ESLint 통과, production build 통과, 세 페이지 기능 QA 통과, 9개 viewport 시각 QA 통과. Proposal 리팩터 후 검색·행 선택·stale/settled·상세 이동을 재검증했고 console error 0건, 기준 이미지 대비 3개 viewport 모두 100/100 유사도를 확인했다.
- 회귀 검증 결과: CP-001과 CP-005가 모두 `REVIEWING`인 조건에서 CP-001의 `ADOPTED` draft를 만든 뒤 같은 query key refetch로 CP-005에 fallback시켰다. CP-005에는 draft가 남지 않았고 저장 버튼도 비활성화됐다.
- 검토 결과: Oracle 1차에서 차단 결함을 발견했고 수정 후 2차 검토에서 같은 상태·다른 ID, 같은 ID·다른 상태, 저장 handler/payload 모두 차단 발견 0건을 확인했다.
- controller 세분화 결과: data 58줄, process 123줄, controller 72줄, contract 57줄로 각 파일이 단일 책임과 250줄 제한을 충족했다.
- 실제 동작 결과: CP-002 상태 mutation과 성공 Dialog, 선택 유지, draft reset, stale/settled 전환, 교차 행 draft 차단, 상세 이동을 브라우저에서 확인했다.
- 시각 결과: 이전 기준 대비 375·768·1280px 모두 100/100 유사도였고 독립 시각 검토 2회가 PASS했다.
- 코드 검토 결과: cache 소유권, 순환 의존, reset/payload 불변식, 상세 페이지 mutation 호환성에서 차단 발견 0건이었다.
- 사용자 후속 피드백: stale guard만으로는 책임 분리가 되지 않았다는 지적을 반영해 Proposal 전용 helper hook과 view 분리를 완료했다.
- 잔여 리스크: 전체 lint 기존 오류, LSP 미설치, Watcher 미실행으로 `paused_after_generator` 상태다.

## 회고
- 잘된 판단: 이전 목록 표시 UX를 유지하면서 처리 가능성만 차단해 cache 정책과 UI 안전 책임을 분리했다.
- 잘된 판단: generic controller를 만들지 않고 Proposal 전용 경계로 분리해 부서 처리·Dialog·navigation 계약을 명시적으로 유지했다.
- 잘된 판단: draft를 UI disabled에만 의존하지 않고 hook 반환값, 저장 가능 조건, mutation payload가 동일한 활성 판정을 사용하게 했다.
- 잘된 판단: table/action/helper마다 hook을 만들지 않고 실제 상태 불변식이 있는 data/process 두 경계만 추가해 과분할을 피했다.
- 다시 한다면 바꿀 점: 첫 구현 단계에서 사용자 요청의 구조 목표까지 수락 기준에 포함해 stale guard만 적용하는 부분 완료를 피했을 것이다.
- 다음 작업에 적용할 인사이트: controller hook 추출 시 `isCurrentData`와 선택·mutation 불변식을 하나의 도메인 계약으로 함께 이동하고, route page에서 직접 state가 사라졌는지를 구조 수락 기준으로 검사해야 한다.
