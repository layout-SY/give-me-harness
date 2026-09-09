# CP 도메인 책임 분리 탐색 기록

## 결론

실제 API가 연결된 Discussion·Vote·Comment·Proposal부터 책임 분리 효과가 크다. 첫 섹션은 책임 혼재가 가장 큰 Discussion 목록으로 확정했다. 공용 `shared` 리소스와 fixture-only 화면의 선제 hook 추출은 보류한다.

## 대상 경로

- `src/shared/ui/`
- `src/widgets/`
- `src/pages/cp-*/ui/`
- `src/entities/cp-*/model/`
- `src/features/`
- `.agents/skills/reference/`
- `.codex/memory/reusable-assets.md`

## 발견한 기존 재사용 자산

- Proposal 목록 page/controller/view 패턴
  - `src/pages/cp-proposal/ui/cp-proposal-list-page.tsx`
  - `src/pages/cp-proposal/ui/use-cp-proposal-list-controller.tsx`
  - `src/pages/cp-proposal/ui/cp-proposal-list-view.tsx`
- 상태 전이: `src/features/cp-status-transition/hook/useStatusTransition.ts`
- 필터·목록·상세 레이아웃: `FilterBar`, `Table`, `MasterDetailLayout`
- 입력: `DateRangeField`, `TextInput`, `Dropdown`
- 서버 상태: `useCpDiscussionListQuery`, `useCpDiscussionProcessMutation`
- surface feedback: `useDialog`

## Discussion 목록의 현재 책임 혼재

`src/pages/cp-discussion/ui/cp-discussion-list-page.tsx` 한 파일이 다음을 모두 담당한다.

1. 검색 draft와 committed query
2. 기간 DOM validation과 오류 상태
3. query 실행·loading·placeholder·retry
4. row 선택과 공개 기준 선택
5. 상태 transition
6. mutation payload 생성과 중복 저장 guard
7. 성공·실패 Dialog
8. KPI mapping과 상세 navigation
9. 전체 JSX 렌더링

## 선택한 구조

- Proposal 목록의 검증된 도메인 전용 구조를 따른다.
- Discussion 안에서 data/search/process hook을 분리하고 controller가 조합한다.
- view는 controller 계약만 소비한다.
- 소비자 둘 이상의 불변식이 아직 입증되지 않았으므로 공용 generic controller는 만들지 않는다.

## 재사용이 어려운 자산

- `useFetchAdapter`: 현재 Discussion은 TanStack Query placeholder data와 mutation cache 정책을 사용하므로 교체하지 않는다.
- Proposal controller 자체: 타입과 처리 필드가 다르므로 직접 재사용하지 않고 구조만 따른다.
- 공용 search hook: Discussion의 기간 DOM validation과 query shape가 도메인 전용이다.

## 신규 도메인 자산 필요성

- controller/view 계약: 렌더링과 orchestration 경계 표현
- data hook: query lifecycle과 조회 오류 표현 캡슐화
- search hook: draft·validation·DTO mapping 캡슐화
- process hook: 선택·상태 전이·mutation surface 캡슐화

## 보류 항목

- 공용 `shared` hook·component 리팩터링
- Discussion/Vote 유사 구조의 공용화
- fixture-only CP 페이지 hook 선제 추출
- Watcher 및 Closure

## Discussion 상세 탐색

### 현재 책임 혼재

`src/pages/cp-discussion/ui/cp-discussion-detail-page.tsx`가 다음 책임을 함께 가진다.

1. route param과 detail query lifecycle
2. 조회 오류 Dialog와 retry
3. 종료일 form draft와 trim
4. ISO date·시작일 기준 validation과 ARIA 오류 상태
5. 상태 transition과 mutation payload mapping
6. 중복 저장 guard와 성공·실패 Dialog
7. list navigation
8. ratio·opinion·history를 포함한 전체 JSX

### 선택한 구조

- 121줄 화면이므로 목록처럼 data/search/process를 모두 세분화하지 않는다.
- query/navigation은 controller, form/mutation은 process hook, validation/payload는 model, 표현은 view로 분리한다.
- detail이 없는 초기 render에도 hook 순서를 유지해야 하므로 process hook은 optional detail을 받는다.
- 종료일 draft는 `{ detailId, value }` selection으로 보관하고 현재 detail과 ID가 다르면 server `periodTo`를 표시한다.

### 재사용 자산

- `useCpDiscussionDetailQuery`
- `useCpDiscussionProcessMutation`
- `useStatusTransition`
- 기존 Discussion 목록의 typed controller/view 경계
- `PageHeader`, `ActionBar`, `StatusTransitionField`, `TextInput`, `RatioBar`, `TimelineList`

## Vote 목록 탐색

### 현재 책임 혼재

`src/pages/cp-vote/ui/cp-vote-list-page.tsx` 한 파일이 다음 책임을 함께 가진다.

1. committed query와 status/author/title/period draft
2. list query, loading, placeholder, 조회 오류 Dialog, retry
3. KPI·pagination mapping
4. current row 선택과 첫 row fallback
5. status transition과 disclosure 선택
6. mutation payload, 중복 저장 guard, 성공·실패 Dialog
7. submit/reset/page 변경과 selection reset 순서
8. 상세 navigation
9. FilterBar, Table, detail panel 전체 JSX

### 재사용 자산

- `useCpVoteListQuery`, `useCpVoteProcessMutation`
- `useStatusTransition`
- `Table`, `FilterBar`, `MasterDetailLayout`, `KpiStrip`
- `DateRangeField`, `TextInput`, `Dropdown`, `Button`
- Discussion 목록의 data/search/process/controller/view 계약 구조
- Proposal 목록의 query draft와 committed query 분리 방식

### Vote 고유 불변식

- status vocabulary는 `VOTING`, `CLOSING_SOON`, `COMPLETED`다.
- disclosure vocabulary는 현재 `AUTO_AFTER_CLOSE` 한 항목이다.
- list process payload는 변경된 `status`와 `disclosureRule`만 사용하며 `closedAt`은 상세 화면 전용이다.
- list query schema도 `startDate > endDate`를 거부하지만 현재 화면에서는 `DateRangeField`가 native invalid 상태를 만들고 form submit을 먼저 차단한다.
- placeholder data를 보여주는 동안 이전 row를 선택하거나 저장할 수 없다.
- 선택 ID가 current rows에 없으면 첫 row를 detail panel에 표시한다.

### 선택한 구조

- Vote 도메인 내부에 `data/search/process/controller/view` 경계를 둔다.
- controller/view 관계는 `cp-vote-list.types.ts`의 `interface` 계약으로 표현한다.
- `cp-vote-list.config.ts`와 entity/shared 계약은 변경하지 않는다.
- Discussion의 구조만 참조하고 기간 validation state·오류 문구·status/disclosure 타입은 복제하지 않는다.
- Proposal·Discussion·Vote의 query/payload/route 어휘가 달라 generic controller/search/process는 만들지 않는다.

### 검증 surface

- 전용 test/spec와 test script는 없다.
- 정적 검증은 targeted ESLint, TypeScript compile, production build를 사용한다.
- 개발 MSW는 128건 Vote seed와 GET list/detail, POST process, query 400, detail/process 404, 강제 500, malformed success를 제공한다.
- 기본 브라우저 QA ID는 `VT-001`, 검색·선택 비교 ID는 `VT-002` 이상을 사용한다.
- route는 `/cp/votes`, detail route는 `/cp/votes/:voteId`다.

### 보류 항목

- generic CP list/search/process 추상화
- `src/shared/**`, `src/widgets/**` 반응형·컴포넌트 수정
- Watcher와 Closure

## Vote 상세 탐색

### 현재 책임 혼재

`cp-vote-detail-page.tsx`가 다음 책임을 함께 소유한다.

1. route param과 detail query lifecycle
2. 조회 실패 Dialog 중복 방지와 retry
3. 종료일 draft, trim, ISO 형식·시작일 validation
4. Vote status transition과 변경 여부
5. 조건부 payload, mutation guard, 성공·실패 Dialog
6. 목록 navigation
7. 기본 정보, 안건·선택지, 운영 상태, 2분할 결과, 의견, 이력 JSX

### 재사용 자산

- `useCpVoteDetailQuery`, `useCpVoteProcessMutation`
- `useStatusTransition`
- `PageHeader`, `ActionBar`, `SectionCard`, `DefinitionList`, `StatusTransitionField`
- `RatioBar`, `TimelineList`, `TextInput`, `Button`, `Loading`
- Discussion 상세의 page/controller/process/model/types/view 책임 구조

### Vote 고유 불변식

- status vocabulary는 `VOTING`, `CLOSING_SOON`, `COMPLETED`다.
- 안건에는 `choices`가 있고 결과는 `agreePercent`·`disagreePercent` 2분할이다.
- 의견에는 Discussion의 `stance`가 없다.
- invalid 종료일은 저장 버튼만 비활성화하며 오류 문구나 오류 ARIA를 노출하지 않는다.
- 상세 process payload는 변경된 `status`와 `closedAt`만 사용하고 `disclosureRule`은 보내지 않는다.
- 성공 후 응답 detail과 처리 이력이 즉시 cache에 반영되고 Vote 목록 query가 invalidate된다.

### 선택한 구조

- Vote 도메인 내부에 `controller/process/model/types/view` 경계를 둔다.
- page는 controller와 view 결선만 수행한다.
- detail ID와 연결된 종료일 draft로 비동기 detail 교체의 stale 상태를 방지한다.
- Discussion의 구조만 참조하고 validation message·ARIA·상태 어휘·결과 UI는 복제하거나 공용화하지 않는다.
- entity/shared/widgets/CSS/route 계약은 변경하지 않는다.

### 검증 surface

- 전용 test/spec와 test script는 없다.
- 정적 검증은 targeted ESLint, TypeScript compile, production build를 사용한다.
- 개발 MSW는 `GET /v1/cp/votes/:voteId`, `POST /v1/cp/votes/:voteId/process`, 404·400·500·malformed success를 제공한다.
- 기본 브라우저 QA ID는 `VT-001`, 실패 route는 `/cp/votes/NOT-FOUND`를 사용한다.
- 정상 저장은 300ms delay이며 성공 시 detail cache 교체, list invalidate, 처리 이력 append를 확인할 수 있다.

### 보류 항목

- generic CP detail/process/model 추상화
- `src/shared/**`, `src/widgets/**` 반응형·접근성 수정
- Watcher와 Closure

## Comment 목록 탐색

### 현재 책임 혼재

`cp-comment-list-page.tsx`와 `use-cp-comment-list-page.tsx`가 다음 책임을 함께 소유한다.

1. list query lifecycle, rows/count/pagination, 조회 오류 Dialog와 retry
2. source tab과 source type·author·sourceTitle·commentId draft/query
3. submit/reset/page 변경과 selection reset 순서
4. selected row ID, comment ID keyed process state와 first-row fallback
5. state-only mutation payload, 중복 저장 guard, 성공·실패 Dialog
6. KPI·FilterBar·tab·Table·detail·ChoiceChip 전체 JSX

### 재사용 자산

- `useCpCommentListQuery`, `useCpCommentProcessMutation`
- `Table`, `FilterBar`, `KpiStrip`, `MasterDetailLayout`, `PageHeader`
- `Dropdown`, `TextInput`, `ChoiceChipGroup`, `DefinitionList`, `SectionCard`, `Button`, `Loading`
- 완료된 Vote/Discussion 목록의 data/search/process/controller/view 책임 구조
- `.codex/memory/reusable-assets.md`의 목록·검색·입력·loading 자산

### Comment 고유 불변식

- source vocabulary는 `BOARD`, `PROPOSAL`, `VOTE`, `DISCUSSION`이며 tab과 source type filter가 별도 query 필드다.
- process state vocabulary는 `NORMAL`, `HIDDEN`, `REPORT_REJECTED`다.
- query는 author/sourceTitle/commentId substring 필터와 page/size를 사용하며 URL search parameter를 변경하지 않는다.
- 선택 ID가 current rows에 없으면 첫 row를 상세와 처리 대상으로 표시한다.
- process draft는 `{ commentId, state }`이며 현재 selected row ID와 일치할 때만 적용한다.
- process payload는 `{ state }` 하나이고 성공 시 reported/hidden count cache 보정 뒤 list prefix를 invalidate한다.
- 현재 Comment는 query `placeholderData`를 사용하지만 `isPlaceholderData` guard가 없어 이전 rows가 fetching 중에도 선택·처리 가능하다.
- KPI는 전체·신고 접수·가입정보 의심·숨김·오늘 신규 5개다.

### 선택한 구조

- Comment 도메인 내부에 `data/search/process/controller/view` 경계를 둔다.
- page는 CSS import, `ADM` 주석, controller/view 결선만 수행한다.
- 기존 `useCpCommentListPage`는 신규 네 hook이 대체하므로 삭제하고 compatibility wrapper를 만들지 않는다.
- tab/submit/reset/page의 query 변경은 search가, process reset 순서는 controller가 소유한다.
- placeholder 조작 차단, 탭 ARIA 개선, shared responsive 수정은 기능 보존 범위 밖이므로 추가하지 않는다.
- query·KPI·process DTO 차이 때문에 generic CP list controller/hook을 만들지 않는다.

### 검증 surface

- 전용 test/spec와 test script는 없다.
- targeted ESLint, TypeScript compile, production build를 정적 검증으로 사용한다.
- 전체 lint는 기존 73 errors·5 warnings baseline이 있으며 Comment 대상 파일에는 현재 오류가 없다.
- 개발 MSW는 36건 seed, GET list, POST process, query 400, process 400·404와 300ms mutation delay를 제공한다.
- 기본 QA ID는 `CM-001002`, hidden 상태 비교는 `CM-001000`, route는 `/cp/comments`다.
- 필터 후 count는 현재 페이지가 아니라 전체 filtered rows 기준이며 `pageCount` 최소값은 1이다.

### 보류 항목

- placeholder 중 stale Comment row 조작 차단 정책
- tab의 `role=tab`·`aria-selected` 접근성 개선
- generic CP list/search/process 추상화
- `src/shared/**`, `src/widgets/**` 반응형·컴포넌트 수정
- Watcher와 Closure

## Proposal 상세·process 탐색

### 현재 책임 혼재

`cp-proposal-detail-page.tsx`가 다음 책임을 함께 소유한다.

1. `proposalId` route param과 detail query lifecycle
2. `errorUpdatedAt` 기반 조회 실패 Dialog 중복 방지와 retry
3. 처리 의견 draft, trim·변경 여부·저장 가능 여부
4. reviewComment-only mutation payload와 성공·실패·입력 확인 Dialog
5. mutation pending, detail/list cache 후처리 연결
6. `/cp/proposals` navigation과 pending/fallback/success 전체 JSX

### 재사용 자산

- entity: `useCpProposalDetailQuery`, `useCpProposalProcessMutation`, `CP_PROPOSAL_STATUS_LABELS`, `CpProposalDetail`
- widgets: `PageHeader`, `ActionBar`
- shared UI: `SectionCard`, `DefinitionList`, `TimelineList`, `TextArea`, `Button`, `Loading`, `useDialog`
- 완료된 Discussion/Vote 상세의 thin page, controller, process, typed view 계약 구조
- `.codex/memory/reusable-assets.md`의 입력·loading·QueryClient·ApiResult 경계

`MasterDetailLayout`, Table, FilterBar, KPI, `StatusTransitionField`, `Dropdown`, `useStatusTransition`, 이미지 관리 자산은 Proposal 상세의 현재 책임이 아니므로 도입하지 않는다. shared/widget 구현 자체도 변경하지 않는다.

### Proposal 고유 불변식

- route는 `/cp/proposals/:proposalId`이며 빈 ID에는 query가 disabled된다.
- detail GET은 AbortSignal과 `cpProposalKeys.detail(proposalId)`를 사용하고 전역 query retry 1회·staleTime 30초를 상속한다.
- 동일 `errorUpdatedAt`의 조회 실패 Dialog는 한 번만 표시한다.
- 상태와 담당부서는 읽기 전용이며 상세 화면에서 수정하거나 payload에 포함하지 않는다.
- 처리 의견은 trim 결과가 비어 있지 않고 persisted trim 값과 다를 때만 저장 가능하다.
- 정상 UI에서 빈 값은 disabled되지만, save guard의 `입력 확인` Dialog 문구는 유지한다.
- payload는 `{ reviewComment: normalizedReviewComment }` 하나다.
- DTO는 최대 1000자를 검증하지만 현재 페이지에는 `maxLength`나 client 오류 UI가 없다. 이를 새로 추가하지 않는다.
- mutation retry는 0이고 성공 응답은 전체 `CpProposalDetail`로 parse된다.
- 성공 시 response `detail.id`의 detail cache를 직접 교체하고 모든 Proposal list query prefix를 invalidate한다.
- mock success는 처리 의견뿐 아니라 history를 append한 전체 detail을 반환한다.

### 상세 패턴 비교와 선택

- Discussion/Vote의 route/query/error/retry/navigation controller 역할은 Proposal에도 적용한다.
- status/date를 관리하는 Discussion/Vote process와 달리 Proposal process는 reviewComment 단일 draft와 mutation feedback만 소유한다.
- trim·기존값 비교·단일 필드 payload는 짧고 단일 소비자라 별도 model 추상화 조건을 충족하지 않는다.
- 기존 코드에 없는 1000자 client validation, mutationGuardRef, optimistic update를 추가하지 않는다.
- Proposal 도메인 내부에 `controller/process/types/view` 경계를 만들고 page는 결선만 수행한다.
- CP generic detail/controller/process/model abstraction은 만들지 않는다.

### 검증 surface

- 전용 test/spec와 test script는 없다.
- targeted ESLint, `yarn tsc -b --pretty false`, `yarn build`, diff/금지 패턴/pure LOC를 정적 검증으로 사용한다.
- 기본 정상 ID는 `CP-001`, 저장 QA는 seed 오염을 피하기 위해 생성 fixture ID를 사용할 수 있고 실패 route는 `/cp/proposals/CP-999`다.
- 정상 상세의 섹션·textarea·읽기 전용 상태/담당부서·button gating·keyboard/ARIA를 확인한다.
- 공백-only POST 차단, trimmed reviewComment-only body, 성공 Dialog·history/detail cache·list invalidation을 확인한다.
- 1000자 초과 입력의 기존 server validation, 조회 404의 자동 retry·단일 Alert·fallback·수동 retry를 확인한다.
- 필요 시 활성 Vite query-bearing MSW worker에 일회성 handler를 추가하고 `resetHandlers()`로 원복한다.
- 1280·768·375 fresh capture와 독립 Visual QA Oracle 2건을 사용한다.

### 문서·harness 경계

- 기존 session slug와 `plan.md`, `exploration.md`, `implementation-log.md`, `review-log.md`, `evaluation-log.md`, `final-summary.md`를 계속 사용한다.
- evidence는 `cp-proposal-detail-{1280,768,375}.png`로 저장한다.
- 전체 lint 73 errors·5 warnings, build 500 kB chunk warning, TypeScript LSP 미설치, test script 부재는 기존 baseline과 대상 파일 결과를 분리 기록한다.
- 동일 slug portfolio를 갱신하고 Stop hook을 통과한다.
- Watcher unavailable이므로 Closure 없이 `paused_after_generator`로 중단한다.

### 보류 항목

- generic CP detail/process/model 추상화
- Proposal 상세 status·department 편집
- reviewComment client max-length validation·새 오류 UI
- `src/shared/**`, `src/widgets/**` 반응형·접근성·컴포넌트 수정
- 공용 shared 리팩터링 전체: 남은 도메인 책임 분리 완료 후 별도 단계
- Watcher와 Closure

## Policy 목록 API UI 연결·책임 분리 탐색

### 현재 책임과 미연결 계약

`cp-policy-list-page.tsx` 157줄은 fixture 4건을 직접 사용하면서 다음 책임을 함께 소유한다.

1. status/department/title/stage 검색 draft
2. 첫 row fallback과 선택 row ID
3. reflectionContent/stage process draft
4. KPI·컬럼·filter option 구성
5. 상세 route navigation
6. 전체 JSX

검색 form은 submit handler가 없고 `처리 저장` 버튼도 mutation handler가 없어 현재는 시각적 affordance만 제공한다. 반면 entity에는 `useCpPolicyListQuery`, `useCpPolicyProcessMutation`, parser, query key와 MSW 64건 seed가 이미 존재한다.

### API·DTO 불변식

- list query: `{ page, size, status?, department?, title?, stage? }`
- list response: `content`, `count.totalItemCount`, status별 `tabItemCount`, `pagination.page/pageCount`
- process payload: `{ stage?, reflectionContent? }`이며 한 필드 이상 필요하다.
- process success는 전체 `CpPolicyDetail`을 반환하고 detail cache를 교체한 뒤 모든 Policy list query를 invalidate한다.
- department/title은 trim 후 각각 최대 80/160자이고 reflectionContent는 trim 후 최소 1자다.
- list/detail ID는 동일한 `PL-\d{3}` 계약을 사용한다.

### 선택한 구조

- 가장 가까운 완료 선례인 Proposal 목록의 Policy-local `data/search/process/controller/view/config/types` 구조를 사용한다.
- `Table`, `FilterBar`, `KpiStrip`, `MasterDetailLayout`, `PageHeader`, `DefinitionList`, `SectionCard`, `Dropdown`, `TextInput`, `TextArea`, `Button`, `Loading`, `useDialog`를 재사용한다.
- `useFetchAdapter`, `SearchStateBar`, 공용 generic controller/hook, 신규 shared abstraction은 도입하지 않는다.
- 필터는 draft와 committed query를 분리하고 기존 `검색` submit 시점에 API query를 반영한다.
- 기존 화면에 없던 reset 버튼이나 상세 전용 status/manager/opinion/history 책임은 추가하지 않는다.
- process draft는 `{ policyId, reflectionContent, stageIndex }` 관계로 현재 선택 policy에만 적용한다.

### 상세 경계

- 목록 route는 `/cp/policies`, 상세 route는 `/cp/policies/:policyId`다.
- 목록은 선택 row의 `CpPolicyListItem` 필드와 list process만 소유한다.
- `authorName`, `proposalContent`, `managerName`, `progresses`, `opinions`, `histories`와 상세 query lifecycle은 후속 Policy 상세 tranche 소유다.
- 현재 상세 페이지가 route param/query/mutation 대신 fixture를 사용하는 문제는 이번 tranche에서 변경하지 않는다.

### 검증 surface

- 전용 test/spec와 test script는 없다.
- MSW는 GET list의 64건 pagination/filter, query 400, POST process의 400/404와 detail/list cache 후처리를 제공한다.
- 정적 검증은 targeted ESLint, `yarn tsc -b --pretty false`, `yarn build`, diff/금지 패턴/pure LOC를 사용한다.
- 브라우저에서는 초기 loading·64건 KPI·10개 rows, 네 필터, pagination, row keyboard selection, changed-fields-only process payload, 성공·실패, 조회 retry, 상세 이동을 확인한다.
- 1280·768·375 fresh capture와 console errors/warnings를 기록한다.

### 보류 항목

- Policy 상세의 route param/query/process 연결과 상세 책임 분리
- generic CP list/search/process 추상화
- `src/shared/**`, `src/widgets/**` 반응형·접근성·컴포넌트 수정
- Watcher와 Closure
