# CP 도메인 책임 분리 구현 로그

## 현재 섹션

- 도메인: Discussion
- 화면: 목록
- 상태: Refactorer 적용 및 로컬 검증 완료, Watcher 대기

## 작업 요약

`cp-discussion-list-page.tsx`에 집중되어 있던 검색·조회·선택·처리·표현 책임을 Discussion 도메인 내부의 data/search/process/controller/view 경계로 분리했다. API·DTO·parser·query/mutation·shared UI·CSS는 변경하지 않았다.

## 에이전트 실행

- 프로젝트 Planner와 내장 Plan agent 호출은 Claude 결제 제한으로 실패했다.
- 승인된 탐색·계획을 orchestrator가 `plan.md`로 승격해 Planner stage를 보존했다.
- 프로젝트 Refactorer 호출도 같은 외부 제한으로 실패했다.
- 메인 Codex가 Refactorer 계약과 승인된 plan을 그대로 적용하는 fallback을 수행했다.
- Watcher는 Claude Code API 비가용 정책에 따라 호출하지 않았다.

## 재사용 자산

- Proposal 목록의 page/controller/view 구조
- `useCpDiscussionListQuery`
- `useCpDiscussionProcessMutation`
- `useStatusTransition`
- `FilterBar`, `Table`, `MasterDetailLayout`, `DateRangeField`, `StatusTransitionField`
- `useDialog`

## 신규 파일 / 수정 파일

- 수정: `src/pages/cp-discussion/ui/cp-discussion-list-page.tsx`
  - 190줄 규모의 orchestration+JSX 화면에서 10줄 route 진입점으로 축소했다.
- 신규: `cp-discussion-list.types.ts`
  - controller와 view 사이 search/table/detail/retry 계약을 정의했다.
- 신규: `use-cp-discussion-list-data.tsx`
  - query lifecycle, KPI mapping, 조회 오류 Dialog, retry를 소유한다.
- 신규: `use-cp-discussion-list-search.tsx`
  - 검색 draft, 기간 validation, query mapping, reset/page를 소유한다.
- 신규: `use-cp-discussion-list-process.tsx`
  - row 선택, 상태 전이, 공개 기준, mutation payload, 저장 Dialog를 소유한다.
- 신규: `use-cp-discussion-list-controller.tsx`
  - data/search/process 조합과 상세 navigation을 소유한다.
- 신규: `cp-discussion-list-view.tsx`
  - 기존 JSX와 사용자 노출 문자열을 보존하고 controller 계약만 소비한다.

## 핵심 결정

- Discussion 전용 경계만 만들고 공용 generic controller는 만들지 않았다.
- DOM ref는 controller 계약에 넣지 않았다. React refs lint가 controller 전체를 ref-like object로 판정한 뒤, view 이벤트 경계에서 DOM invalid 여부를 boolean으로 전달하도록 수정했다.
- invalid 기간 submit은 process 선택 상태를 reset하지 않는 기존 동작을 보존했다.
- placeholder data 중 row 선택·저장을 막는 `isCurrentData` guard를 process/controller에 유지했다.
- mutation guard, 성공 후 선택 동기화, Dialog 문구를 변경하지 않았다.

## 검증 / 요청 처리

- targeted ESLint: pass
- `yarn tsc -b --pretty false`: pass
- `yarn build`: pass
- `git diff --check`: pass
- TypeScript LSP: 서버 미설치 및 기존 설치 거절로 N/A
- no-excuse checker: Bun 미설치로 skip, Node 기반 금지 패턴 검사로 대체
- pure LOC: page 7, types 56, data 52, search 84, process 99, controller 71, view 176
- 금지 패턴 `as any`, `as unknown`, `@ts-ignore`, `@ts-expect-error`: 0건

## 브라우저 검증

- 초기 목록 GET 200 및 첫 row 선택 표시 확인
- 작성자 `빅데이터` 검색: query parameter 반영, DS-001만 표시
- 초기화: 검색 draft 제거, 전체 rows 복원
- DS-002 row 선택: table selection과 상세 패널 동기화
- 상태 `종료` 저장: POST 200, 성공 Dialog, list invalidation GET, row/detail 상태 `종료` 동기화
- 상세 화면 이동: `/cp/discussions/DS-002` 및 상세 heading 확인
- 역전 기간 `2026-03-20`~`2026-02-20`: validation 문구 노출, date query 요청 차단
- 전체 흐름 console errors/warnings: 0

## 리스크

- 별도 test script가 없어 자동 UI 회귀 테스트는 추가하지 않았다.
- 1280/768/375 캡처에서 기존 shell header overlay와 모바일 table 잘림이 관찰됐다. 이번 섹션은 CSS·shared layout을 변경하지 않았고 사용자가 shared 리소스를 후순위로 지정했으므로 보류한다.
- Watcher 독립 판정이 없으므로 Closure와 완료를 주장하지 않는다.

## 핸드오프 메모

- 상태: `paused_after_generator`
- 다음 섹션 후보: Discussion 상세
- Watcher API 복구 시 본 섹션부터 독립 검토한다.

---

## Discussion 상세 tranche

### 작업 요약

`cp-discussion-detail-page.tsx`에 함께 있던 detail query, 조회 오류 feedback, 종료일 form/validation, 상태 transition, mutation payload, 저장 feedback, navigation, JSX를 Discussion 상세 전용 page/controller/process/model/view 경계로 분리했다. API·DTO·parser·entity query/mutation·shared UI·CSS·문구는 변경하지 않았다.

### 신규 파일 / 수정 파일

- 수정: `cp-discussion-detail-page.tsx`
  - controller와 view만 결선하는 10줄 route page로 축소했다.
- 신규: `cp-discussion-detail.types.ts`
  - view가 소비하는 detail/process/retry/navigation 계약을 정의했다.
- 신규: `cp-discussion-detail.model.ts`
  - ISO date validation과 조건부 process payload mapping을 순수 함수로 분리했다.
- 신규: `use-cp-discussion-detail-process.tsx`
  - detail ID 기반 종료일 draft, status transition, mutation guard, 저장 Dialog를 소유한다.
- 신규: `use-cp-discussion-detail-controller.tsx`
  - route param, detail query, 조회 오류 Dialog, retry, navigation, process 조합을 소유한다.
- 신규: `cp-discussion-detail-view.tsx`
  - 기존 JSX·문구·ARIA·CSS class를 보존하고 typed controller 계약만 소비한다.

### 핵심 결정

- 작은 상세 화면에 목록의 data/search 분리를 그대로 복제하지 않고 query/navigation은 controller, form/mutation은 process로 묶었다.
- detail 도착 전에도 hook 순서를 유지하도록 process hook이 optional detail을 받는다.
- 종료일 draft는 `{ detailId, value }`로 관리해 route/detail 교체 시 이전 detail의 form state가 노출되지 않도록 했다.
- validation과 payload mapping은 React lifecycle과 무관한 순수 model 함수로 이동했다.
- status 또는 종료일 중 하나 이상 변경되고 종료일이 유효할 때만 저장하는 기존 조건을 유지했다.
- 변경하지 않은 `closedAt`과 선택하지 않은 `status`는 payload에서 생략했다.

### 정적 검증

- targeted ESLint: pass
- `yarn tsc -b --pretty false`: pass
- `yarn build`: pass
- `git diff --check`: pass
- pure LOC: page 10, types 29, model 23, process 101, controller 47, view 146
- 금지 패턴 `as any`, `@ts-ignore`, `@ts-expect-error`: 0건
- 초기 TypeScript 검증에서 nullable selection narrowing 1건을 발견했고 명시적 null guard로 수정 후 재검증했다.
- TypeScript LSP: 서버 미설치 및 기존 설치 거절로 N/A
- build의 500 kB chunk 경고는 기존 bundle 범위이며 build exit code는 0이다.

### 브라우저 검증

- detail GET `/v1/cp/discussions/DS-001`: 200
- 역전 종료일 `2020-01-01`: validation alert 노출, `aria-invalid=true`, `aria-describedby` 연결, 저장 disabled
- 종료일 원복 후 상태 `종료` 선택: 저장 enabled
- process POST `/v1/cp/discussions/DS-001/process`: 200
- 실제 request body: `{"status":"CLOSED"}`; 변경하지 않은 `closedAt` 미포함
- 성공 Dialog, detail 상태·처리 이력 갱신, 목록 DS-001 상태 `종료` 갱신 확인
- 목록 이동 URL `/cp/discussions` 확인
- 전체 흐름 console errors/warnings: 0

### 시각 증거

- fresh capture: `evidence/cp-discussion-detail-1280.png` 1280×1099, `evidence/cp-discussion-detail-768.png` 768×1255, `evidence/cp-discussion-detail-375.png` 375×1523
- detail 카드·입력·ratio·opinion·history·ActionBar의 clipping 또는 상호 겹침 없음
- 기존 shared navigation rail의 full-page 높이 단절과 375px toggle/content 겹침 재확인
- 사용자가 shared 리소스를 후순위로 지정했고 이번 변경에 CSS/shared diff가 없어 별도 backlog로 유지
- 기능·디자인 시스템 무결성 Oracle: PASS, HIGH confidence, 변경 파일 blocking 0건
- 시각·CJK 정밀성 Oracle: PASS, HIGH confidence, clipping·tofu·비정상 조사/어미 고립 0건

### tranche 상태

- local verification: pass
- independent visual QA: pass
- Watcher: Claude Code API 비가용으로 미실행
- pipeline: `paused_after_generator`
- Closure: 미진행
- 다음 섹션 후보: Vote 목록

---

## Vote 목록 tranche

### 작업 요약

`cp-vote-list-page.tsx`에 혼재한 query lifecycle, 검색 draft, 선택·처리 상태, mutation payload, Dialog, navigation, JSX를 Vote 도메인 내부의 data/search/process/controller/view 경계로 분리했다. API·DTO·parser·entity query/mutation·config·shared UI·widgets·CSS·문구·route는 변경하지 않았다.

### 에이전트 실행

- 프로젝트 Planner와 Refactorer 호출은 Anthropic credit 제한으로 실패했다.
- 코드그래프와 5개 Explore 결과를 기존 `plan.md`·`exploration.md`에 승격했다.
- 메인 Codex가 승인된 plan과 Refactorer 계약에 따라 fallback 구현했다.
- Watcher는 Claude Code API 비가용 정책에 따라 호출하지 않는다.

### 신규 파일 / 수정 파일

- 수정: `cp-vote-list-page.tsx`
  - controller/view만 결선하는 11줄 route page로 축소했다.
- 신규: `cp-vote-list.types.ts`
  - search/table/detail/retry controller 계약을 정의했다.
- 신규: `use-cp-vote-list-data.tsx`
  - list query, rows/KPI/pagination, placeholder 판별, 조회 오류 Dialog, retry를 소유한다.
- 신규: `use-cp-vote-list-search.tsx`
  - status/author/title/period draft, query submit/reset/page 변경을 소유한다.
- 신규: `use-cp-vote-list-process.tsx`
  - row 선택, status transition, disclosure 선택, 조건부 payload, mutation guard와 저장 Dialog를 소유한다.
- 신규: `use-cp-vote-list-controller.tsx`
  - data/search/process 조합, selection reset 순서, detail navigation을 소유한다.
- 신규: `cp-vote-list-view.tsx`
  - 기존 JSX·문구·Table keyboard/selection props를 보존하고 typed controller 계약만 소비한다.

### 핵심 결정

- Proposal·Discussion 구조는 참조하되 Vote status/disclosure/query/payload는 도메인 전용으로 유지했다.
- `DateRangeField`가 역전 기간에 native invalid 상태를 만들고 form submit을 차단하는 기존 동작을 유지했으며, Discussion의 별도 validation state·오류 문구를 추가하지 않았다.
- placeholder data 중 row 선택·저장을 막는 `isCurrentData` guard를 data/process/controller에 유지했다.
- 선택 ID lookup 뒤 current rows 첫 항목 fallback 순서를 유지했다.
- list process payload에는 변경된 `status`와 `disclosureRule`만 포함하고 `closedAt`은 추가하지 않았다.
- config와 generic shared abstraction은 변경·추가하지 않았다.

### 정적 검증

- targeted ESLint: pass
- `yarn tsc -b --pretty false`: pass
- `yarn build`: pass
- `git diff --check`: pass
- LOC: page 11, types 61, data 58, search 72, process 108, controller 74, view 173
- 금지 패턴 `as any`, `as unknown`, non-null assertion, `@ts-ignore`, `@ts-expect-error`: 0건
- TypeScript LSP: 서버 미설치 및 기존 설치 거절로 N/A
- build의 500 kB chunk 경고는 기존 bundle 범위이며 build exit code는 0이다.

### 브라우저 검증

- 초기 GET `/v1/cp/votes?page=1&size=10`: 200, VT-001 첫 row fallback·상세 동기화
- 작성자 `홍길동` + 제목 `반려동물`: query parameter 반영, VT-001만 표시
- 초기화: 검색 draft 제거, base GET, 전체 rows 복원
- VT-002 row click: `aria-selected`와 detail panel 동기화
- VT-003 row focus + Enter: keyboard selection과 detail panel 동기화
- VT-003 status `완료` 저장: POST 200, 실제 body `{"status":"COMPLETED"}`
- 저장 성공 후 list invalidation GET, selected row/detail `완료`, KPI 투표중 23건·완료 97건 동기화
- pagination page 2 GET, selection reset 후 VT-011 첫 row fallback
- 상세 이동 `/cp/votes/VT-011`, detail GET 200와 heading 확인
- status `COMPLETED` filter GET 200, VT-033 첫 row 표시
- 정상 기간 `2026-01-01~2026-01-31`: `startDate`·`endDate` query parameter 반영
- 역전 기간 `2026-03-20~2026-02-20`: `DateRangeField` native invalid와 form submit 차단, 추가 GET 없음
- 전체 흐름 console errors/warnings: 0

### 시각 증거

- fresh capture: `evidence/cp-vote-list-1280.png` 1280×1102, `evidence/cp-vote-list-768.png` 768×1408, `evidence/cp-vote-list-375.png` 375×2052
- page-local KPI/filter/card/detail/action 간 겹침 없음
- unchanged DateRange placeholder 분절, 768/375 Table 열 clipping, shared navigation rail/toggle 문제 재확인
- 기능·디자인 시스템 무결성 Oracle: PASS, HIGH confidence, 변경 파일 blocking 0건
- 시각·CJK 정밀성 Oracle: PASS, HIGH confidence, page-local CJK 회귀 0건

### tranche 상태

- local verification: pass
- independent visual QA: pass
- Watcher: Claude Code API 비가용으로 미실행
- pipeline: `paused_after_generator`
- Closure: 미진행
- 다음 섹션 후보: Vote 상세

---

## Vote 상세 tranche

### 작업 요약

`cp-vote-detail-page.tsx`에 혼재한 route/query lifecycle, 조회 오류·retry, 종료일 draft·validation, 상태 전이, mutation payload·guard·Dialog, navigation, JSX를 Vote 도메인 내부의 controller/process/model/types/view 경계로 분리했다. API·DTO·parser·entity query/mutation·shared UI·widgets·CSS·문구·route는 변경하지 않았다.

### 에이전트 실행

- 프로젝트 Planner와 Refactorer 호출은 Anthropic credit 제한으로 실패했다.
- 코드그래프와 5개 Explore 결과를 기존 `plan.md`·`exploration.md`에 승격했다.
- 메인 Codex가 승인된 plan과 Refactorer 계약에 따라 fallback 구현했다.
- 첫 Oracle A가 `nextStatus`의 `string | null` 타입 확장을 지적해 `CpVoteStatus | null`로 좁혔다.
- 수정 후 fresh production capture로 신규 Oracle A/B를 실행해 모두 PASS를 받았다.
- Watcher는 Claude Code API 비가용 정책에 따라 호출하지 않는다.

### 신규 파일 / 수정 파일

- 수정: `cp-vote-detail-page.tsx`
  - controller/view만 결선하는 11줄 route page로 축소하고 default export와 `ADM` 주석을 보존했다.
- 신규: `cp-vote-detail.types.ts`
  - process/retry/controller 계약과 `CpVoteStatus | null` 상태 불변식을 정의했다.
- 신규: `cp-vote-detail.model.ts`
  - 종료일 validation과 조건부 process payload mapping을 순수 함수로 분리했다.
- 신규: `use-cp-vote-detail-process.tsx`
  - detail ID keyed 종료일 draft, status transition, 저장 조건, mutation guard와 Dialog를 소유한다.
- 신규: `use-cp-vote-detail-controller.tsx`
  - route/query, `errorUpdatedAt` Dialog 중복 방지, retry, navigation과 process 조합을 소유한다.
- 신규: `cp-vote-detail-view.tsx`
  - 기존 JSX·문구·class·ARIA 부재를 보존하고 typed controller 계약만 소비한다.

### 핵심 결정

- Discussion 상세의 책임 구조만 참조하고 Vote status·choices·2분할 ratio·의견·DTO는 도메인 전용으로 유지했다.
- invalid 종료일은 입력값을 유지하고 저장만 비활성화하며 오류 문구, `aria-invalid`, `aria-describedby`를 추가하지 않았다.
- `{ detailId, value }` draft와 `resetKey`로 기존 keyed content remount의 detail 전환 동작을 보존했다.
- trim 후 변경된 `status`와 `closedAt`만 payload에 포함하고 `disclosureRule`은 보내지 않았다.
- generic CP detail/process/model 추상화는 추가하지 않았다.

### 정적 검증

- targeted ESLint: pass
- `yarn tsc -b --pretty false`: pass
- `yarn build`: pass
- `git diff --check`: pass
- pure LOC: page 7, types 24, model 17, process 82, controller 39, view 68
- 금지 패턴 `as any`, `as unknown`, `enum`, `@ts-ignore`, `@ts-expect-error`: 0건
- TypeScript LSP: 서버 미설치 및 기존 설치 거절로 N/A
- Bun 미설치로 no-excuse script는 실행할 수 없어 동일 금지 패턴·LOC 검사를 로컬 명령으로 대체했다.
- 전체 `yarn lint`: 이번 6파일 밖 기존 레거시 73 errors·5 warnings로 실패했으며 대상 파일 오류는 0건이다.
- build의 500 kB chunk 경고는 기존 bundle 범위이며 build exit code는 0이다.

### 브라우저 검증

- 초기 GET `/v1/cp/votes/VT-001`: 200, 상세 8개 섹션과 초기 저장 disabled 확인
- 종료일 `2026-02-19`: 입력 유지, 저장 disabled, 오류 문구·`aria-invalid`·`aria-describedby` 없음
- 종료일 ` 2026-03-21 ` 저장: POST 200, 실제 body `{"closedAt":"2026-03-21"}`
- 저장 성공 후 input·투표 기간·`처리 저장` 이력 동기화와 저장 재비활성화
- VT-002 status `완료` 저장: POST 200, 실제 body `{"status":"COMPLETED"}`
- status 저장 성공 후 현재 상태·이력 동기화, transition placeholder 복원, 저장 재비활성화
- `/cp/votes/NOT-FOUND`: 404 서버 메시지 Alert, fallback, retry GET, Alert 단일 노출, `/cp/votes` 복귀
- 정상 fresh route `/cp/votes/VT-011`: GET 200, console errors/warnings 0

### 시각 증거

- fresh post-fix capture: `evidence/cp-vote-detail-1280.png` 1280×1127, `evidence/cp-vote-detail-768.png` 768×1287, `evidence/cp-vote-detail-375.png` 375×1549
- 1280·768은 2열, 375는 1열이며 세 viewport 모두 horizontal overflow·clipping·glyph 손실 0건
- 375px 처리 이력의 `처리자` 음절 분리는 unchanged fixture/shared `TimelineList` wrapping의 기존 deferred debt
- 기능·디자인 시스템 무결성 최종 Oracle: PASS, HIGH confidence, blocking 0건
- 시각·CJK 정밀성 최종 Oracle: PASS, HIGH confidence, 변경 원인의 CJK 회귀 0건

### tranche 상태

- local verification: pass
- independent visual QA: pass
- Watcher: Claude Code API 비가용으로 미실행
- pipeline: `paused_after_generator`
- Closure: 미진행
- 다음 섹션 후보: Comment 목록 controller

---

## Comment 목록 tranche

### 작업 요약

`cp-comment-list-page.tsx`에 혼재한 query lifecycle, 유형·작성자·원문 제목·댓글 ID 검색 draft, tab/pagination, row 선택, 처리 상태 transition, mutation payload·Dialog, JSX를 Comment 도메인 내부의 data/search/process/controller/view 경계로 분리했다. API·DTO·parser·entity query/mutation·config·shared UI·widgets·CSS·문구·route는 변경하지 않았다.

### 에이전트 실행

- 프로젝트 Planner와 Refactorer 호출은 Anthropic credit 제한으로 실패했다.
- 코드그래프와 병렬 Explore 결과를 기존 `plan.md`·`exploration.md`에 승격했다.
- 메인 Codex가 사용자 승인과 Refactorer 계약에 따라 fallback 구현했다.
- 조회 실패 브라우저 주입이 MSW Service Worker 경계에서 차단되어 Oracle Triple을 실행했고, 세 Oracle 모두 CDP service worker bypass를 권고했다.
- CDP 우회 시 외부 API 인증서 오류 `ERR_CERT_COMMON_NAME_INVALID`가 발생해 실패 Alert·retry는 브라우저 end-to-end로 확정하지 못했다.
- Playwright network 기록에서 app이 실제 import한 query-bearing Vite worker module을 찾아 해당 활성 MSW registry에 일회성 500 handler를 등록해 오류 surface를 최종 검증했다.
- Watcher는 Claude Code API 비가용 정책에 따라 호출하지 않는다.

### 신규 파일 / 수정 파일

- 수정: `cp-comment-list-page.tsx`
  - controller/view만 결선하는 8줄 route page로 축소했다.
- 신규: `cp-comment-list.types.ts`
  - source tab, search/table/detail/retry controller 계약을 정의했다.
- 신규: `use-cp-comment-list-data.tsx`
  - list query, rows/KPI/pagination, 조회 오류 Dialog와 retry를 소유한다.
- 신규: `use-cp-comment-list-search.tsx`
  - source tab과 작성자·원문 제목·댓글 ID draft, trim/query mapping, reset/page 변경을 소유한다.
- 신규: `use-cp-comment-list-process.tsx`
  - row 선택, 처리 상태 draft, mutation guard와 성공·실패 Dialog를 소유한다.
- 신규: `use-cp-comment-list-controller.tsx`
  - data/search/process 조합과 selection reset 순서를 소유한다.
- 신규: `cp-comment-list-view.tsx`
  - 기존 JSX·문구·Table keyboard/selection props를 보존하고 typed controller 계약만 소비한다.
- 삭제: `use-cp-comment-list-page.tsx`
  - 기존 단일 orchestration hook을 위 책임 경계로 대체했다.

### 핵심 결정

- Proposal·Discussion·Vote 목록의 검증된 책임 구조만 참조하고 Comment source tab·query·state DTO는 도메인 전용으로 유지했다.
- placeholder data에서 stale row 선택·처리가 가능한 기존 observable을 변경하지 않았다. `isPlaceholderData` guard 도입은 별도 후속 개선으로 남겼다.
- selected ID lookup 뒤 current rows 첫 항목 fallback 순서와 click·Enter·Space 선택 동작을 보존했다.
- process payload는 변경된 `state`만 전송하고 query·mutation·config 계약은 수정하지 않았다.
- generic CP controller와 shared abstraction은 추가하지 않았다.

### 정적 검증

- targeted ESLint: pass
- `yarn tsc -b --pretty false`: pass
- `yarn build`: pass
- `git diff --check`: pass
- pure LOC: page 8, types 49, data 47, search 68, process 74, controller 67, view 171
- 금지 패턴 `as any`, `as unknown`, `@ts-ignore`, `@ts-expect-error`: 0건
- TypeScript LSP: 서버 미설치 및 기존 설치 거절로 N/A
- 전체 `yarn lint`: 기존 레거시 73 errors·5 warnings로 실패했으며 Comment 대상 파일 targeted lint는 통과했다.
- build의 500 kB chunk 경고는 기존 bundle 범위이며 build exit code는 0이다.

### 브라우저 검증

- 초기 GET `/v1/cp/comments?page=1&size=10`: 200, KPI `36/4/9/16/6`, CM-001002 첫 row fallback·상세 동기화
- source tab `VOTE`, 작성자·원문 제목·댓글 ID 복합 검색의 trim/query mapping과 초기화 확인
- row click·Enter·Space 선택과 `aria-selected`·상세 패널 동기화 확인
- page 2 GET과 selection reset 후 첫 row fallback 확인
- CM-000992 처리 상태 `숨김 → 정상`: POST 200, 실제 body `{"state":"NORMAL"}`
- 저장 double-click에도 POST 1건, row/detail/cache/KPI 동기화와 저장 재비활성화 확인
- 정상 경로 console errors/warnings: 0
- 활성 MSW worker 500 주입: 최초 GET 2회 후 `조회 실패` Alert, 0 rows fallback과 `다시 조회` 노출 확인
- `다시 조회`: GET 누적 4회와 두 번째 `조회 실패` Alert 재노출 확인
- handler reset·초기화 후 GET 200, 36건, 10개 row, CM-001002 first-row fallback, retry 제거, 검색 draft 비움으로 정상 복구 확인

### 시각 증거

- fresh capture: `evidence/cp-comment-list-1280.png` 1280×1120, `evidence/cp-comment-list-768.png` 768×1400, `evidence/cp-comment-list-375.png` 375×2000
- 기능·디자인 시스템 Oracle: PASS, MEDIUM confidence, tranche regression·blocking 0건
- 반응형·CJK Oracle: PASS, MEDIUM confidence, tranche 신규 레이아웃·한글 렌더링 회귀 0건
- 1280px의 page hierarchy와 table/detail 관계는 정상
- 768/375의 Table 열 clipping·CJK 조각, navigation 침범, 모바일 보조 문구 대비는 unchanged shared/widget 기존 debt

### tranche 상태

- local verification: pass
- independent visual QA: pass
- Watcher: Claude Code API 비가용으로 미실행
- pipeline: `paused_after_generator`
- Closure: 미진행
- 다음 섹션 후보: Proposal detail/process 정리

---

## Proposal 상세·process tranche

### 작업 요약

`cp-proposal-detail-page.tsx`에 혼재한 route/query lifecycle, 조회 오류·retry, 처리 의견 draft·저장 조건, reviewComment-only mutation payload·Dialog, navigation, JSX를 Proposal 상세 전용 controller/process/types/view 경계로 분리했다. API·DTO·parser·entity query/mutation·shared UI·widgets·CSS·문구·route는 변경하지 않았다.

### 에이전트 실행

- 프로젝트 Planner와 Refactorer 호출은 Anthropic credit 제한으로 실패했다.
- Codegraph와 5개 병렬 Explore 결과를 기존 `plan.md`·`exploration.md`에 승격했다.
- 메인 Codex가 사용자 승인과 Refactorer 계약에 따라 fallback 구현했다.
- 기능·디자인 시스템 Oracle은 PASS, MEDIUM confidence를 반환했다.
- 반응형·CJK Oracle은 책임 분리 tranche를 PASS로 판정했으나 768/375 shared TextArea 줄바꿈 때문에 전체 화면은 REVISE로 판정했다.
- 사용자가 shared 리팩터링을 도메인 책임 분리 완료 후 진행하도록 지정했으므로 해당 기존 부채는 이번 tranche 밖으로 유지한다.
- Watcher는 Claude Code API 비가용 정책에 따라 호출하지 않는다.

### 신규 파일 / 수정 파일

- 수정: `cp-proposal-detail-page.tsx`
  - controller와 view만 결선하는 14 pure LOC route page로 축소하고 default export와 `ADM` 주석을 보존했다.
- 신규: `cp-proposal-detail.types.ts`
  - process/retry/controller 레이어 계약을 readonly `interface`로 정의했다.
- 신규: `use-cp-proposal-detail-process.tsx`
  - detail ID keyed reviewComment draft, trim·변경·저장 조건, mutation과 입력·성공·실패 Dialog를 소유한다.
- 신규: `use-cp-proposal-detail-controller.tsx`
  - route/query, `errorUpdatedAt` Dialog 중복 방지, retry, navigation과 process 조합을 소유한다.
- 신규: `cp-proposal-detail-view.tsx`
  - 기존 pending/fallback/success JSX·문구·class·ARIA·shared/widget primitive를 보존한다.

### 핵심 결정

- Proposal 단일 입력의 trim·비교·payload는 짧고 단일 소비자이므로 별도 model 파일을 만들지 않았다.
- status와 department는 읽기 전용으로 유지하고 payload에 포함하지 않았다.
- 표시 draft는 trim하지 않고 저장 body만 trim한다.
- 현재 UI에 없는 1000자 client validation, `maxLength`, 오류 ARIA를 추가하지 않았다.
- 기존 코드에 없는 mutation guard, optimistic update, generic CP detail abstraction을 추가하지 않았다.
- detail ID와 연결된 draft만 사용해 async detail 도착과 다른 detail 전환에서 persisted reviewComment를 표시한다.

### 정적 검증

- targeted ESLint: pass
- `yarn tsc -b --pretty false`: pass
- `yarn build`: pass
- `git diff --check`: pass
- pure LOC: page 14, types 19, process 53, controller 35, view 91
- 금지 패턴 `as any`, `as unknown`, `enum`, `@ts-ignore`, `@ts-expect-error`: 0건
- 최초 TypeScript compile에서 nullable draft narrowing 1건을 발견해 명시적 null guard로 수정 후 재검증했다.
- TypeScript LSP: 서버 미설치 및 기존 설치 거절로 N/A
- 전체 lint의 기존 73 errors·5 warnings baseline과 Proposal 대상 targeted lint 결과를 분리한다.
- build의 500 kB chunk warning은 기존 bundle 범위이며 build exit code는 0이다.

### 브라우저 검증

- 목록 CP-002 선택 후 `/cp/proposals/CP-002` 상세 진입과 초기 GET 200 확인
- 초기 reviewComment `담당 부서 검토 전입니다.`, 읽기 전용 상태 `접수 유지`·담당부서 `미지정`, 저장 disabled 확인
- 앞뒤 공백-only와 빈 입력은 저장 disabled·POST 0건, 유효 변경은 저장 enabled 확인
- 실제 POST body `{"reviewComment":"리팩터링 검증 처리 의견"}`; status·department 미포함
- 저장 성공 Dialog, textarea trim 값, 저장 재비활성화, `처리 저장` history와 detail cache 동기화 확인
- 목록 복귀 시 invalidated list GET 200 확인
- CP-003 1001자 입력은 client에서 enabled, `maxLength`·`aria-invalid` 없음, POST 400과 기존 `저장 실패` Dialog 확인
- `/cp/proposals/CP-999`: 최초 GET 404 2회, `조회 실패` Alert 단일 노출, fallback·retry·목록 버튼 확인
- 수동 retry 후 GET 누적 4회와 두 번째 Alert 단일 노출, `/cp/proposals` 복귀 확인
- fresh `/cp/proposals/CP-001`: console/page errors 0, 초기 저장 disabled, 열린 Dialog 0

### 시각 증거

- fresh capture: `evidence/cp-proposal-detail-1280.png` 1280×900, `evidence/cp-proposal-detail-768.png` 768×1024, `evidence/cp-proposal-detail-375.png` 375×1250
- 세 PNG 모두 정상 합성, page bounds·카드·버튼 clipping과 글리프 누락 0건
- 기능·디자인 시스템 Oracle: PASS, MEDIUM confidence, tranche regression·blocking 0건
- 반응형·CJK Oracle: tranche PASS, 전체 화면 REVISE, MEDIUM confidence
- 768의 `진행합 / 니다.`, 375의 `진 / 행합니다.` textarea 분절과 navigation toggle 침범은 unchanged shared 부채
- 사용자의 순서 지정에 따라 shared CJK/navigation 개선은 남은 도메인 분리 완료 후 처리한다.

### tranche 상태

- local verification: pass
- independent visual QA: Proposal tranche pass, shared CJK debt deferred by user sequencing
- Watcher: Claude Code API 비가용으로 미실행
- pipeline: `paused_after_generator`
- Closure: 미진행
- 다음 섹션 후보: 남은 CP 도메인 책임 분리
