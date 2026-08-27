# CP 도메인 책임 분리 리팩터링 계획

## 요청 요약

- 공용 `shared` 리소스 리팩터링은 후순위로 보류한다.
- API·상태·검증·payload·부수효과·JSX 책임이 섞인 CP 화면을 도메인별로 순차 리팩터링한다.
- 첫 섹션은 Discussion 목록이며 기능·시각·API 계약을 변경하지 않는다.

## 작업 유형

- refactor

## 전체 범위

1. Discussion 목록·상세
2. Vote 목록·상세
3. Comment 목록 controller
4. Proposal 상세·process
5. Dashboard
6. Policy·Survey API UI 연결 시 책임 분리
7. Board·Report·Reward 등 fixture 화면의 API 연결 시 책임 분리

## 제외 범위

- `src/shared/**` 공용 컴포넌트·hook 수정
- 공용 generic list controller 신규 도입
- API endpoint, DTO, parser, query key, MSW handler 계약 변경
- 화면 마크업, 스타일, 문자열, 라우트 변경
- Auth, Select Users, Image Manager, Meeting 리팩터링
- Watcher 비가용 상태에서 Closure 또는 완료 처리

## 현재 섹션 — Discussion 목록

### 목표

`src/pages/cp-discussion/ui/cp-discussion-list-page.tsx`에 혼재한 검색·조회·선택·처리·표현 책임을 Proposal 목록과 같은 도메인 전용 controller/view 경계로 분리한다.

### 파일 계획

1. `cp-discussion-list-page.tsx`
   - route 진입점 역할만 유지한다.
   - controller를 호출하고 view에 전달한다.
   - router 호환을 위해 default export는 유지한다.
2. `cp-discussion-list.types.ts`
   - controller와 view 사이 계약을 `interface`로 정의한다.
   - search, table, detail, retry 묶음으로 소비자 책임을 표현한다.
3. `use-cp-discussion-list-controller.tsx`
   - data/search/process controller를 조합한다.
   - 상세 화면 navigation을 소유한다.
   - KPI 표시 데이터를 구성한다.
4. `use-cp-discussion-list-data.tsx`
   - committed query와 `useCpDiscussionListQuery` 결과를 소유한다.
   - 조회 오류 Dialog의 중복 노출 방지와 refetch를 소유한다.
5. `use-cp-discussion-list-search.tsx`
   - 검색 draft, 기간 validation, submit/reset, page reset을 소유한다.
   - DTO mapping을 도메인 내부에서 수행한다.
   - `DateRangeField`의 DOM invalid 상태를 확인하는 ref 계약을 유지한다.
6. `use-cp-discussion-list-process.tsx`
   - 현재 데이터 선택, 상태 전이, 공개 기준 선택, mutation payload, 저장 Dialog를 소유한다.
   - placeholder data 중 선택·저장을 금지하는 기존 규칙을 유지한다.
7. `cp-discussion-list-view.tsx`
   - 기존 JSX·마크업·컴포넌트·문자열을 그대로 보존한다.
   - controller 계약만 소비한다.
8. `cp-discussion-list.config.ts`
   - 기존 컬럼·필터·상태 상수를 유지한다.
   - 신규 공용 추상화는 추가하지 않는다.

### 기능 보존 불변식

- 검색 submit 시 page가 1로 초기화된다.
- 기간 입력의 segment invalid 상태 또는 역전 범위는 조회를 차단하고 기존 오류 문구를 표시한다.
- reset 시 검색 draft, validation, DateRangeField revision, query, 선택 상태가 초기화된다.
- placeholder data 표시 중 row 선택과 저장을 허용하지 않는다.
- 선택 ID가 없으면 현재 rows의 첫 항목을 선택 항목으로 표시한다.
- 상태·공개 기준 중 하나 이상 변경된 경우에만 저장할 수 있다.
- 저장 성공 후 선택 ID, 공개 기준, 상태 transition을 서버 응답 기준으로 동기화한다.
- 조회·저장 성공/실패 Dialog 문구와 상세 라우트는 변경하지 않는다.
- loading, pagination, retry 표시 조건과 기존 화면 구조를 유지한다.

## 에이전트

- Planner: 계획 문서 확정. Claude API 제한으로 현재 orchestrator가 탐색 근거를 계획 문서로 승격했다.
- Refactorer: Discussion 목록 구조 변경과 단순화 패스.
- Watcher: Claude Code API 복구 후 실행. 현재는 실행하지 않는다.

## 적용 스킬

- `policy-refactoring`
- `policy-hook-extraction`
- `policy-data-fetch-layer`
- `policy-type-definition`
- `policy-coding-convention`
- `policy-codex-native-quality`
- `reference-components`
- `reference-custom-hooks`
- `programming`

## 검증

- 변경 파일별 TypeScript LSP diagnostics
- `yarn eslint <Discussion 변경 파일>`
- `yarn tsc -b --pretty false`
- `yarn build`
- 실제 브라우저에서 초기 조회, 검색, 기간 오류, row 선택, 저장, pagination, 상세 이동 확인
- 코드 크기와 금지 패턴 검사

## 리스크와 대응

- 상태 분리 후 stale closure 위험: controller 반환 계약과 hook dependency를 LSP·브라우저에서 확인한다.
- placeholder data 중 선택 규칙 유실 위험: process hook의 `isCurrentData` guard를 보존한다.
- 검색 reset 순서 변경 위험: 기존 상태 전이를 그대로 옮기고 화면 observable을 확인한다.
- 테스트 script 부재: 타입·lint·build와 실제 브라우저 사용자 흐름으로 회귀를 확인한다.

## 승인

- 사용자 승인: `작업 진행`
- 승인 범위: 전체 문서화 후 Discussion 목록 한 섹션부터 순차 진행

## 종료 상태

- Refactorer와 로컬 검증 후 `paused_after_generator`
- Watcher `confirmed` 전 Closure 금지

## 다음 섹션 — Discussion 상세

### 목표

`cp-discussion-detail-page.tsx`의 query lifecycle, 종료일 form, validation, mutation payload, Dialog, navigation, JSX를 Discussion 상세 전용 경계로 분리한다.

### 파일 계획

1. `cp-discussion-detail-page.tsx`
   - controller와 view 결선만 유지하고 default export를 보존한다.
2. `cp-discussion-detail.types.ts`
   - controller와 view 사이 detail/process/retry 계약을 `interface`로 정의한다.
3. `cp-discussion-detail.model.ts`
   - 종료일 validation과 process payload mapping을 순수 함수로 분리한다.
4. `use-cp-discussion-detail-process.tsx`
   - 종료일 draft, 상태 transition, mutation, 저장 Dialog를 소유한다.
   - detail ID와 연결된 draft를 사용해 비동기 detail 교체 시 stale form state를 방지한다.
5. `use-cp-discussion-detail-controller.tsx`
   - route param, detail query, 조회 오류 Dialog, retry, navigation, process hook 조합을 소유한다.
6. `cp-discussion-detail-view.tsx`
   - 기존 JSX·문구·ARIA·CSS class를 보존하고 controller 계약만 소비한다.

### 기능 보존 불변식

- detail query의 `refetchOnMount: always`와 오류 Dialog 중복 방지 동작을 유지한다.
- 종료일은 trim 후 `YYYY-MM-DD` 형식이며 시작일보다 빠를 수 없다.
- 종료일이 바뀌지 않았으면 payload에서 `closedAt`을 생략한다.
- status가 선택되지 않았으면 payload에서 `status`를 생략한다.
- status 또는 종료일 중 하나 이상 변경되고 종료일이 유효할 때만 저장할 수 있다.
- 저장 성공 후 종료일 draft를 응답 `periodTo`로 동기화하고 상태 transition을 reset한다.
- 중복 submit guard, 성공·실패 Dialog, list navigation, retry UI를 유지한다.
- ratio, opinion, history, 기본 정보와 사용자 노출 문자열을 변경하지 않는다.

### 검증

- 변경 파일 targeted ESLint, TypeScript compile, production build
- detail 초기 조회와 refetch network 확인
- invalid 종료일의 error/ARIA와 POST 차단 확인
- status 변경 저장의 POST 200, 성공 Dialog, detail/list cache 갱신 확인
- 목록 이동과 console errors/warnings 확인

## 다음 섹션 — Vote 목록

### 목표

`src/pages/cp-vote/ui/cp-vote-list-page.tsx`에 혼재한 query lifecycle, 검색 draft, 선택·처리 상태, mutation payload, Dialog, navigation, JSX를 Vote 목록 전용 경계로 분리한다.

### 에이전트

- Planner: 프로젝트 Planner 호출은 Anthropic credit 제한으로 실패했다.
- Planner fallback: 메인 Codex가 코드그래프·5개 Explore 결과와 기존 Discussion/Proposal 계약을 계획 문서로 승격했다.
- Refactorer: 승인된 파일 계약에 따라 Vote 목록 구조 변경을 수행한다.
- Watcher: Claude Code API 비가용 정책에 따라 실행하지 않는다.

### 파일 계획

1. `cp-vote-list-page.tsx`
   - controller와 view 결선만 유지하고 router용 default export를 보존한다.
2. `cp-vote-list.types.ts`
   - controller/view의 search, table, detail, retry 계약을 `interface`로 정의한다.
3. `use-cp-vote-list-data.tsx`
   - `useCpVoteListQuery`, rows/KPI/pagination, placeholder 판별, 조회 오류 Dialog, retry를 소유한다.
4. `use-cp-vote-list-search.tsx`
   - status/author/title/period draft와 committed query, submit/reset/page 변경을 소유한다.
   - page 전용 validation state를 추가하지 않고 기존 `DateRangeField` native invalid/form submit 차단을 유지한다.
5. `use-cp-vote-list-process.tsx`
   - row 선택, status transition, disclosure 선택, 조건부 payload, mutation guard와 저장 Dialog를 소유한다.
6. `use-cp-vote-list-controller.tsx`
   - data/search/process를 조합하고 submit/reset/page 변경 시 process selection을 reset한다.
   - 선택 행의 상세 route navigation을 소유한다.
7. `cp-vote-list-view.tsx`
   - 기존 JSX·문구·shared primitive·Table keyboard/selection props를 보존하고 controller 계약만 소비한다.
8. `cp-vote-list.config.ts`
   - 컬럼·status filter·disclosure items·page size를 변경하지 않는다.

### 기능 보존 불변식

- 초기 query는 `{ page: 1, size: 10 }`이며 첫 current row를 상세 패널에 표시한다.
- 검색 submit 시 status/author/title/period를 query에 매핑하고 page를 1로 초기화하며 선택 상태를 reset한다.
- 기간 역전 또는 segment invalid는 기존 `DateRangeField`의 native invalid/form validation이 submit을 차단하며 page 전용 오류 문구를 추가하지 않는다.
- reset 시 status/author/title/period/query와 선택·disclosure·status transition을 초기화한다.
- page 변경 시 현재 query를 보존하고 선택 상태를 reset한다.
- placeholder data 중 row 선택과 저장을 허용하지 않는다.
- row 클릭·Enter·Space 선택, `aria-selected`, selected class를 보존한다.
- 상태 또는 공개 기준 중 하나 이상 변경된 경우에만 저장할 수 있다.
- 저장 payload에는 변경된 `status`와 `disclosureRule`만 포함하고 목록에서는 `closedAt`을 사용하지 않는다.
- mutation 중복 submit guard와 loading/disabled 상태를 유지한다.
- 저장 성공 후 선택 ID, 공개 기준, status transition을 응답 기준으로 동기화하고 list query를 재조회한다.
- 조회·저장 성공/실패 Dialog, retry, 상세 route `/cp/votes/:voteId`, 모든 사용자 노출 문자열을 변경하지 않는다.

### 검증

- 변경 파일 targeted ESLint
- `yarn tsc -b --pretty false`
- `yarn build`
- `git diff --check`와 금지 패턴·pure LOC 검사
- 실제 브라우저에서 초기 GET, 작성자/제목/상태/기간 검색, 초기화, row 선택, pagination, 처리 저장, cache 갱신, 상세 이동 확인
- 1280·768·375 fresh capture와 console errors/warnings 확인

### 리스크와 대응

- 검색 hook에 Discussion validation state·오류 문구가 유입될 위험: Vote의 기존 `DateRangeField` native submit 차단만 유지한다.
- placeholder 중 stale row 조작 위험: data의 `isCurrentData`를 process와 table click 계약에 유지한다.
- 첫 행 fallback과 explicit selection 불일치 위험: selected ID lookup 뒤 `rows[0]` fallback 순서를 보존한다.
- 단일 disclosure item 때문에 불필요한 공용화가 생길 위험: Vote config와 process를 도메인 전용으로 유지한다.
- test script 부재: 타입·lint·build와 MSW 실제 브라우저 흐름으로 회귀를 확인한다.

### 종료 상태

- Refactorer와 로컬·브라우저 검증 후 `paused_after_generator`
- Watcher `confirmed` 전 Closure 금지

## 다음 섹션 — Comment 목록 controller

### 목표

`src/pages/cp-comment/ui/cp-comment-list-page.tsx`와 `use-cp-comment-list-page.tsx`에 분산·혼재한 query lifecycle, source tab·검색 draft, row 선택·처리 상태, mutation payload·Dialog, reset 순서와 JSX를 Comment 목록 전용 data/search/process/controller/view 경계로 분리한다.

### 에이전트

- Planner: 프로젝트 Planner 호출은 Anthropic credit 제한으로 실패했다.
- Planner fallback: 메인 Codex가 코드그래프·5개 Explore 결과와 완료된 Discussion/Vote 목록 계약을 계획 문서로 승격했다.
- Refactorer: 사용자 승인 후 아래 파일 계약에 따라 Comment 목록 구조 변경을 수행한다.
- Watcher: Claude Code API 비가용 정책에 따라 실행하지 않는다.

### 파일 계획

1. `cp-comment-list-page.tsx`
   - CSS import, 기존 `ADM` 주석, router용 default export를 보존하고 controller/view 결선만 유지한다.
2. `cp-comment-list.types.ts`
   - search/table/detail/process/retry controller 계약을 `interface`로 정의하고 `CpCommentSourceType`·`CpCommentState` closed vocabulary를 유지한다.
3. `use-cp-comment-list-data.tsx`
   - `useCpCommentListQuery`, rows/count/pagination, 조회 오류 Dialog 중복 방지, loading과 retry를 소유한다.
   - 현재 Comment에는 없는 `isPlaceholderData` guard나 새 조작 차단 정책을 추가하지 않는다.
4. `use-cp-comment-list-search.tsx`
   - source tab, source type index, author/source title/comment ID draft, committed query, submit/reset/page 변경을 소유한다.
5. `use-cp-comment-list-process.tsx`
   - selected row ID, comment ID keyed state draft, 첫 row fallback, 저장 가능 여부, mutation guard와 성공·실패 Dialog를 소유한다.
6. `use-cp-comment-list-controller.tsx`
   - data/search/process를 조합하고 tab/submit/reset/page 변경 뒤 process selection reset 순서를 소유한다.
7. `cp-comment-list-view.tsx`
   - 기존 JSX·문구·class·Table keyboard/selection·ChoiceChip ARIA 계약을 보존하고 controller만 소비한다.
8. `use-cp-comment-list-page.tsx`
   - 신규 controller가 모든 책임을 대체한 뒤 삭제한다. 호환 wrapper는 추가하지 않는다.
9. `cp-comment-list.config.ts`, `cp-comment-list-page.css`
   - 컬럼·탭·필터·상태 옵션·페이지 크기와 스타일을 변경하지 않는다.

### 기능 보존 불변식

- 기본 query는 `{ page: 1, size: 10 }`이며 query key와 `placeholderData` 정책을 변경하지 않는다.
- 현재 Comment는 placeholder 표시 중 이전 row 선택·처리를 차단하지 않으므로 새 `isCurrentData` guard를 도입하지 않는다.
- source tab은 `ALL | BOARD | PROPOSAL | VOTE | DISCUSSION`이며 클릭 시 page 1과 선택 상태를 초기화한다.
- source type Dropdown의 index 기반 선택·재선택 해제와 `ALL` fallback을 유지한다.
- author/sourceTitle/commentId는 submit 시 trim하고 빈 문자열을 `undefined`로 매핑한다.
- submit/reset/page 변경 시 기존 순서대로 query를 갱신하고 selected row·process draft를 reset한다.
- selected ID가 current rows에 없으면 `rows[0]`을 상세와 처리 대상으로 사용하는 fallback을 유지한다.
- process draft는 현재 selected row ID와 일치할 때만 사용하고, 다른 경우 row의 원래 state를 사용한다.
- `NORMAL | HIDDEN | REPORT_REJECTED` 중 현재 row와 다른 state가 선택된 경우에만 저장할 수 있다.
- mutation payload는 `{ state }`만 포함하고 중복 submit guard·loading/disabled·성공·실패 Dialog를 유지한다.
- 저장 성공 후 selected ID와 process state를 응답 기준으로 동기화하고 entity mutation의 cache count 보정·list invalidate를 그대로 사용한다.
- KPI 5개, 탭, Table 5개 컬럼, row click·Enter·Space·`aria-selected`, detail fallback, ChoiceChip `aria-pressed`, 모든 문구·class를 변경하지 않는다.
- API·DTO·parser·entity query/mutation·shared UI·widgets·CSS·route를 변경하지 않는다.

### 검증

- 변경 파일 targeted ESLint
- `yarn tsc -b --pretty false`
- `yarn build`
- `git diff --check`와 금지 패턴·pure LOC 검사
- 전체 `yarn lint`는 기존 73 errors·5 warnings baseline을 별도 기록하고 Comment 대상 파일 오류 0건을 확인한다.
- 실제 브라우저에서 초기 36건·KPI, source tab, source type/author/sourceTitle/commentId 검색, clear·초기화, row click·Enter·Space, pagination, first-row fallback을 확인한다.
- state-only POST body, 저장 중 중복 방지, row/KPI/cache 동기화, 조회 실패·retry와 저장 실패 Dialog를 확인한다.
- 1280·768·375 fresh capture에서 master/detail, filter, tab wrap, Table horizontal viewport, ChoiceChip과 저장 버튼을 확인하고 console errors/warnings를 수집한다.

### 리스크와 대응

- Vote/Discussion placeholder guard가 유입돼 Comment observable이 바뀔 위험: 기존 stale placeholder row 조작 가능 동작을 이번 tranche에서 보존하고 후속 debt로 분리한다.
- tab과 source type filter를 하나로 합칠 위험: query의 `tab`과 `sourceType`을 별도 draft/committed 계약으로 유지한다.
- 첫 행 fallback과 explicit selection 불일치 위험: selected ID lookup 뒤 `rows[0]` fallback 순서를 유지한다.
- process state가 다른 row로 누수될 위험: `{ commentId, state }` draft의 ID 일치 조건을 유지한다.
- generic CP list 추상화로 Comment의 query·KPI·state 어휘가 누수될 위험: Comment-local data/search/process/controller/view만 추가한다.
- test script 부재: 타입·targeted lint·build와 MSW 실제 브라우저 흐름으로 회귀를 확인한다.

### 종료 상태

- 사용자 승인 전 소스 수정 금지
- Refactorer와 로컬·브라우저 검증 후 `paused_after_generator`
- Watcher `confirmed` 전 Closure 금지

## 다음 섹션 — Vote 상세

### 목표

`src/pages/cp-vote/ui/cp-vote-detail-page.tsx`에 혼재한 route/query lifecycle, 조회 오류·retry, 종료일 draft·validation, 상태 전이, mutation payload·guard·Dialog, navigation, JSX를 Vote 상세 전용 경계로 분리한다.

### 에이전트

- Planner: 프로젝트 Planner 호출은 Anthropic credit 제한으로 실패했다.
- Planner fallback: 메인 Codex가 코드그래프·5개 Explore 결과와 기존 Discussion 상세 계약을 계획 문서로 승격했다.
- Refactorer: 승인된 파일 계약에 따라 Vote 상세 구조 변경을 수행한다.
- Watcher: Claude Code API 비가용 정책에 따라 실행하지 않는다.

### 파일 계획

1. `cp-vote-detail-page.tsx`
   - controller와 view 결선만 유지하고 router용 default export와 기존 `ADM` 주석을 보존한다.
2. `cp-vote-detail.types.ts`
   - controller/view와 process의 계약을 `interface`로 정의한다.
3. `cp-vote-detail.model.ts`
   - Vote 전용 종료일 validator와 조건부 process payload builder를 순수 함수로 정의한다.
4. `use-cp-vote-detail-process.tsx`
   - detail ID에 연결된 종료일 draft, status transition, 변경·validation 상태, mutation guard와 저장 Dialog를 소유한다.
5. `use-cp-vote-detail-controller.tsx`
   - route param, detail query, 조회 오류 Dialog 중복 방지, retry, navigation, process hook 조합을 소유한다.
6. `cp-vote-detail-view.tsx`
   - 기존 JSX·문구·ARIA·CSS class를 보존하고 controller 계약만 소비한다.

### 기능 보존 불변식

- detail query의 `refetchOnMount: always`와 `errorUpdatedAt` 기반 오류 Dialog 중복 방지 동작을 유지한다.
- detail ID와 연결된 draft를 사용해 비동기 detail 교체 시 stale 종료일 상태를 방지한다.
- 종료일은 trim 후 정확한 `YYYY-MM-DD` 형식이며 `periodFrom`보다 빠를 수 없다.
- Vote의 invalid 종료일은 입력값을 유지하고 저장만 비활성화하며 오류 문구, `aria-invalid`, `aria-describedby`를 추가하지 않는다.
- 종료일이 바뀌지 않았으면 payload에서 `closedAt`을 생략하고 status가 선택되지 않았으면 `status`를 생략한다.
- status 또는 종료일 중 하나 이상 변경되고 종료일이 유효할 때만 저장할 수 있다.
- 저장 성공 후 종료일 draft를 응답 `periodTo`로 동기화하고 status transition을 reset한다.
- 중복 submit guard, 성공·실패 Dialog, retry, `/cp/votes` navigation을 유지한다.
- `choices`, 2분할 ratio, stance 없는 의견, 처리 이력, 사용자 노출 문자열과 ARIA를 변경하지 않는다.
- entity API·DTO·parser·query·mutation, shared UI, widgets, CSS, route는 변경하지 않는다.

### 검증

- 변경 파일 targeted ESLint
- `yarn tsc -b --pretty false`
- `yarn build`
- `git diff --check`와 금지 패턴·pure LOC 검사
- 실제 브라우저에서 초기 GET, 404 Alert와 retry, 상태·종료일 변경, invalid 종료일 POST 차단, 조건부 payload, 저장 성공 Dialog·detail/history/cache 갱신, 목록 이동 확인
- 1280·768·375 fresh capture와 console errors/warnings 확인

### 리스크와 대응

- Discussion의 validation message·ARIA가 유입될 위험: Vote의 기존 저장 비활성화 observable만 유지한다.
- route detail 교체 시 stale draft 위험: detail ID와 draft를 함께 저장해 현재 detail의 `periodTo`를 선택한다.
- status vocabulary와 2분할 결과 UI가 generic 상세 계약으로 희석될 위험: Vote-local controller/process/model/types/view를 유지한다.
- 동일 화면의 연속 저장 위험: 기존 `mutationGuardRef`를 process에 유지한다.
- test script 부재: 타입·lint·build와 MSW 실제 브라우저 흐름으로 회귀를 확인한다.

### 종료 상태

- Refactorer와 로컬·브라우저 검증 후 `paused_after_generator`
- Watcher `confirmed` 전 Closure 금지

## 다음 섹션 — Proposal 상세·process

### 목표

`src/pages/cp-proposal/ui/cp-proposal-detail-page.tsx`에 혼재한 route/query lifecycle, 조회 오류·retry, 처리 의견 draft·저장 조건, reviewComment-only mutation payload·Dialog, navigation, JSX를 Proposal 상세 전용 `controller/process/types/view` 경계로 분리한다. API·DTO·parser·entity query/mutation·shared UI·widgets·CSS·문구·route는 변경하지 않는다.

### 에이전트

- Planner: 프로젝트 Planner 호출은 Anthropic credit 제한으로 실패했다.
- Planner fallback: 메인 Codex가 Codegraph와 5개 병렬 Explore 결과, 완료된 Discussion/Vote 상세 계약을 보수적으로 합성했다.
- Refactorer: 사용자 승인 후 아래 파일 계약에 따라 Proposal 상세 구조 변경을 수행한다. 프로젝트 Refactorer가 credit 제한으로 실패하면 메인 Codex가 동일 계약으로 fallback한다.
- Watcher: Claude Code API 비가용 정책에 따라 실행하지 않는다.

### 파일 계획

1. `cp-proposal-detail-page.tsx`
   - controller와 view 결선만 유지하고 router용 default export와 기존 `ADM_CP_PROPOSAL_DETAIL_WEB` 주석을 보존한다.
2. `cp-proposal-detail.types.ts`
   - controller/view, process, retry의 레이어 계약을 readonly `interface`로 정의한다.
3. `use-cp-proposal-detail-process.tsx`
   - 현재 detail ID에 연결된 처리 의견 draft, trim·변경 여부·저장 가능 여부, mutation 호출, 성공·실패·입력 확인 Dialog를 소유한다.
   - 별도 model 파일은 만들지 않는다. trim·기존값 비교·`{ reviewComment }` payload는 단일 입력의 짧은 규칙이므로 process 내부에 유지한다.
4. `use-cp-proposal-detail-controller.tsx`
   - `proposalId` route param, detail query, `errorUpdatedAt` 기반 조회 오류 Dialog 중복 방지, retry, 목록 navigation과 process 조합을 소유한다.
5. `cp-proposal-detail-view.tsx`
   - 기존 pending/fallback/success JSX·문구·class·ARIA·shared/widget primitive를 보존하고 typed controller 계약만 소비한다.

### 기능 보존 불변식

- route parameter는 `proposalId`이고 빈 문자열이면 detail query를 실행하지 않는다.
- detail query key, AbortSignal, 전역 query retry 1회와 staleTime 정책을 변경하지 않는다.
- 동일한 `errorUpdatedAt`에는 `조회 실패` Dialog를 한 번만 표시하고 fallback의 `다시 조회` loading/disabled와 `/cp/proposals` 이동을 유지한다.
- 처리 의견 초기값과 draft는 현재 detail ID에 연결하며 trim 결과를 표시값으로 덮어쓰지 않는다.
- trim 결과가 비어 있거나 기존 `detail.reviewComment.trim()`과 같으면 저장할 수 없다.
- 빈 값 save guard의 `입력 확인` / `처리 의견을 입력해 주세요.` 문구는 유지하되, 현재처럼 disabled 버튼을 우회한 경우에만 도달한다.
- payload는 trim된 `{ reviewComment }` 하나만 포함한다. `status`와 `department`는 읽기 전용이며 payload에 추가하지 않는다.
- 현재 UI에 없는 1000자 client max validation, 오류 문구, `maxLength`, `aria-invalid`를 추가하지 않는다. 길이 검증은 기존 DTO/server 경계를 그대로 따른다.
- mutation retry 0, pending loading/disabled, 성공·실패 Dialog와 오류 `message` 전달을 유지한다.
- 기존 코드에 없는 별도 `mutationGuardRef`나 optimistic update를 추가하지 않는다.
- mutation 성공 응답의 `detail.id`로 detail cache를 교체하고 Proposal list prefix를 invalidate하는 entity hook 계약을 변경하지 않는다.
- 기본 정보, 제안 배경·상세 내용, 읽기 전용 상태·담당부서, 처리 의견, 처리 이력의 순서·문구·값·ARIA를 변경하지 않는다.
- `PageHeader`, `ActionBar`, `SectionCard`, `DefinitionList`, `TimelineList`, `TextArea`, `Button`, `Loading`, `useDialog`를 그대로 재사용한다.
- `StatusTransitionField`, `Dropdown`, `useStatusTransition`, `MasterDetailLayout`, Table·검색·이미지 관리 자산은 상세 화면에 새로 도입하지 않는다.
- generic CP detail/controller/process/model abstraction을 만들지 않는다.

### 구현 순서와 검증

1. 계약 정의
   - `cp-proposal-detail.types.ts`에 최소 controller/process/retry 계약을 추가한다.
   - 검증: targeted ESLint와 TypeScript diagnostics. 실패 시 신규 파일만 제거한다.
2. process 분리
   - 처리 의견 state·trim·변경·save gating·mutation callback·Dialog를 `use-cp-proposal-detail-process.tsx`로 이동한다.
   - 검증: payload가 reviewComment-only인지 정적 확인하고 targeted ESLint·TypeScript compile을 실행한다. 실패 시 content의 기존 inline 로직으로 복귀한다.
3. controller 분리
   - route/query/error dedupe/retry/navigation과 process 조합을 `use-cp-proposal-detail-controller.tsx`로 이동한다.
   - 검증: hook 순서, detail ID draft, errorUpdatedAt ref, retry callback을 점검하고 targeted ESLint·TypeScript compile을 실행한다.
4. view·thin page 분리
   - 기존 JSX를 `cp-proposal-detail-view.tsx`로 이동하고 page는 controller/view만 결선한다.
   - 검증: 기존 문구·class·ARIA·shared import diff, targeted ESLint, `yarn tsc -b --pretty false`, `yarn build`를 실행한다.
5. 브라우저 회귀 검증
   - `/cp/proposals/CP-001`: 초기 GET, 섹션·읽기 전용 상태/담당부서, textarea 초기값, 저장 disabled를 확인한다.
   - 공백-only 변경은 disabled·POST 0건, 유효 변경은 trimmed `reviewComment`-only POST, status/department 미포함을 확인한다.
   - 저장 성공 Dialog, 응답 기반 textarea·history·detail cache 동기화, Proposal list invalidation과 저장 재비활성화를 확인한다.
   - 1000자 초과 입력은 새 client 오류 UI 없이 기존 server validation으로 실패하는 observable을 확인한다.
   - `/cp/proposals/CP-999`: 최초 GET 2회, `조회 실패` Alert 단일 노출, fallback, `다시 조회` 추가 GET과 loading/disabled, 목록 이동을 확인한다.
   - 필요 시 활성 MSW worker에 일회성 POST 500 handler를 등록해 `저장 실패`와 원래 오류 message 전달을 확인하고 즉시 reset한다.
6. 최종 품질·시각·문서 gate
   - `git diff --check`, 금지 패턴, pure LOC, 전체 lint baseline과 대상 파일 오류를 확인한다.
   - `evidence/cp-proposal-detail-1280.png`, `cp-proposal-detail-768.png`, `cp-proposal-detail-375.png` fresh capture와 console errors/warnings를 수집한다.
   - 독립 Visual QA Oracle 2건 후 implementation/review/evaluation/final-summary와 동일 slug portfolio를 갱신한다.
   - Stop hook을 통과하고 `paused_after_generator`로 중단한다.

### 리스크와 대응

- Discussion/Vote의 날짜 validator 때문에 불필요한 model 파일이 생길 위험: Proposal 단일 입력의 trim·비교·payload는 process에 유지한다.
- DTO의 1000자 제한이 새 client validation으로 유입될 위험: 현재 server validation observable을 보존한다.
- status/department 선택 UI가 상세에 유입될 위험: 기존 읽기 전용 box와 reviewComment-only payload를 고정한다.
- detail 교체·async 도착 시 draft가 섞일 위험: current detail ID와 연결된 draft만 사용하고 다른 ID에는 detail의 persisted reviewComment를 사용한다.
- 저장 성공 후 local draft와 response detail이 어긋날 위험: 응답 detail 기준으로 draft를 동기화해 저장 가능 상태를 재계산한다.
- generic 상세 공용화로 도메인 어휘가 누수될 위험: Proposal-local 경계만 추가하고 shared 리팩터링은 모든 도메인 책임 분리 이후로 미룬다.
- test script 부재: targeted lint·type·build와 실제 MSW 브라우저 정상/오류 흐름으로 회귀를 확인한다.

### Team Staffing Recommendation

- `total_atomic_steps`: 6
- `file_independent_steps`: 1
- `cross_file_dependent_steps`: 5
- `per_step_assignment`:
  - `types`: quick, blockedBy 없음, 계약 파일의 기계적 추가
  - `process`: unspecified-low, blockedBy `types`, 상태·mutation observable 보존 필요
  - `controller`: unspecified-low, blockedBy `types`, route/query/error/process 조합 필요
  - `view-page`: unspecified-low, blockedBy `process`, `controller`, JSX·계약 결선 필요
  - `verification`: unspecified-low, blockedBy `view-page`, 정적·브라우저 회귀 확인
  - `documentation`: writing, blockedBy `verification`, 기존 세션 문서 갱신
- `dispatch_path_recommendation`: `legacy`
- 근거: 파일은 여럿이지만 controller/process/view가 동일 계약과 상태 shape에 순차 의존해 병렬 편집보다 한 Refactorer의 연속 작업이 안전하다.

### 종료 상태

- 사용자 승인 전 소스 수정 금지
- Refactorer와 로컬·브라우저·시각 검증 후 `paused_after_generator`
- Watcher `confirmed` 전 Closure 금지

## 다음 섹션 — Policy 목록 API UI 연결·책임 분리

### 목표

`src/pages/cp-policy/ui/cp-policy-list-page.tsx`의 fixture 조회, 검색 draft, 선택·처리 draft, navigation, JSX 책임을 Policy 전용 `data/search/process/controller/view` 경계로 분리하고, 이미 존재하는 `useCpPolicyListQuery`와 `useCpPolicyProcessMutation`을 실제 화면에 연결한다. Policy 상세 route·상세 페이지·entity API/DTO/parser/query key/mutation·MSW·shared UI·widgets·CSS는 변경하지 않는다.

### 승인과 에이전트

- 사용자 승인: `이어서 작업해`, `Continue if you have next steps, or stop and ask for clarification if you are unsure how to proceed.`
- 승인 범위: 앞서 보고한 다음 단일 섹션인 Policy 목록의 entity hook 연결과 책임 분리
- Planner fallback: 메인 Codex가 Codegraph와 5개 병렬 Explore 결과, 완료된 Proposal 목록 계약을 계획 문서로 승격했다.
- Generator/Refactorer: 아래 계약에 따라 Policy 목록만 변경한다.
- Watcher: Claude Code API 비가용 정책에 따라 실행하지 않는다.

### 파일 계획

1. `cp-policy-list-page.tsx`
   - 기존 `ADM_CP_POLICY_LIST_WEB` 주석과 router용 default export를 유지하고 controller/view 결선만 소유한다.
2. `cp-policy-list.types.ts`
   - controller/view 사이 search, table, detail, retry 계약을 readonly `interface`로 정의한다.
3. `cp-policy-list.config.ts`
   - page size, 기본 query, status/stage filter, Table 컬럼을 Policy 도메인 안에 유지한다.
4. `use-cp-policy-list-search.ts`
   - status/department/title/stage draft, committed query, submit, page 변경을 소유한다.
5. `use-cp-policy-list-data.tsx`
   - `useCpPolicyListQuery`, rows/KPI/pagination/loading/placeholder 판별, 조회 오류 Dialog 중복 방지와 retry를 소유한다.
6. `use-cp-policy-list-process.tsx`
   - current row 선택, policy ID keyed reflection/stage draft, 변경 필드만 포함한 payload, mutation guard와 성공·실패 Dialog를 소유한다.
7. `use-cp-policy-list-controller.tsx`
   - data/search/process 조합, submit/page 변경 시 process reset, `/cp/policies/:policyId` navigation을 소유한다.
8. `cp-policy-list-view.tsx`
   - 기존 PageHeader/KPI/FilterBar/MasterDetailLayout/Table/상세 패널 구조·문구·class를 유지하고 controller 계약만 소비한다.

### 기능 계약

- 초기 query는 `{ page: 1, size: 10 }`이며 MSW 64건 중 첫 페이지를 조회한다.
- 검색 draft는 submit 시 trim해 status/department/title/stage query로 커밋하고 page를 1로 초기화한다.
- 기존 화면에 없던 초기화 버튼은 추가하지 않는다.
- page 변경은 committed query를 보존하고 선택·process draft를 reset한다.
- placeholder data 표시 중 stale row 선택·저장을 차단한다.
- current rows에서 explicit 선택 ID를 찾고, 없으면 첫 current row를 상세 패널에 표시한다.
- row click·Enter·Space, selected class와 `aria-selected`, 상세 route `/cp/policies/:policyId`를 유지한다.
- 반영 내용과 처리 단계 draft는 현재 policy ID에 연결하며 row 변경 시 persisted 값으로 전환한다.
- payload에는 실제 변경된 `reflectionContent`와 `stage`만 포함한다. reflectionContent는 trim 후 전송하고 빈 변경값은 저장하지 않는다.
- 변경 필드가 없거나 mutation pending이면 저장하지 않고, 성공·실패 Dialog와 entity mutation의 detail cache 갱신/list invalidation을 사용한다.
- 초기 loading, query 오류 Alert·retry, pagination, API count 기반 KPI를 Proposal 목록과 같은 기존 CP API 목록 surface로 제공한다.
- Policy 상세 페이지의 fixture·query 미연결 상태와 상세 전용 필드는 후속 tranche로 남긴다.

### 구현 순서와 검증

1. config/types/search/data/process/controller/view를 Policy-local로 추가하고 page를 thin entry로 교체한다.
2. 변경 파일별 LSP diagnostics와 targeted ESLint를 실행한다.
3. `yarn tsc -b --pretty false`, `yarn build`, `git diff --check`, 금지 패턴·pure LOC를 확인한다.
4. `/cp/policies`에서 초기 GET/KPI/첫 행, status·department·title·stage 검색, pagination, row 선택, changed-fields-only process POST, 성공·실패 Dialog와 cache/list 갱신, 상세 이동을 확인한다.
5. 조회 실패의 자동 retry·Alert·수동 retry를 확인하고 임시 MSW handler를 사용한 경우 즉시 원복한다.
6. 1280·768·375 fresh capture와 console errors/warnings, 독립 Visual QA를 수집한다.
7. 세션 문서와 동일 slug portfolio를 갱신하고 Stop hook 통과 후 `paused_after_generator`로 중단한다.

### 리스크와 대응

- fixture-only no-op 버튼을 API 동작으로 바꾸는 범위 확대 위험: 사용자에게 보고·승인된 entity hook 연결만 수행하고 entity/server 계약은 변경하지 않는다.
- placeholder 중 이전 row가 수정될 위험: `isPlaceholderData`를 `isCurrentData` guard로 전달한다.
- row 변경 시 draft가 누수될 위험: reflection/stage draft를 policy ID와 함께 저장한다.
- empty reflection 변경이 server 400을 만들 위험: trim된 빈 변경값은 저장 가능 조건과 payload에서 차단한다.
- 목록 tranche가 상세 구현을 선점할 위험: 상세 route 문자열만 사용하고 detail page/query/fixture는 변경하지 않는다.
- generic CP 목록 공용화 위험: Policy-local 경계만 추가하고 shared 리팩터링은 모든 도메인 책임 분리 이후로 미룬다.

### 종료 상태

- Generator와 로컬·브라우저·시각 검증 후 `paused_after_generator`
- Watcher `confirmed` 전 Closure 금지
