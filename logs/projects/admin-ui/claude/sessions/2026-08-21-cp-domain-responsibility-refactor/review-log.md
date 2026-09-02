# CP 도메인 책임 분리 리뷰 로그

## 리뷰 대상

- Discussion 목록·상세 책임 분리
- 목록 tranche 신규·수정 파일 7개
- 상세 tranche 신규·수정 파일 6개
- Vote 목록 책임 분리 신규·수정 파일 7개
- Vote 상세 책임 분리 신규·수정 파일 6개
- Comment 목록 책임 분리 신규·수정 7개 및 삭제 1개

## 결과

- 로컬 품질 검증: pass
- 상세 독립 시각 QA Oracle 2건: pass
- Vote 목록 독립 시각 QA Oracle 2건: pass
- Vote 상세 최종 독립 시각 QA Oracle 2건: pass
- Comment 목록 독립 시각 QA Oracle 2건: pass
- Watcher 독립 판정: 미실행
- 파이프라인 상태: `paused_after_generator`

## 체크리스트 검토

- SKILL 준수: 기능 보존, 도메인 전용 hook, 계약 interface, shared 변경 금지 준수
- 재사용 확인: Proposal 구조, entity query/mutation, 기존 UI 자산 재사용
- 검증 확인: ESLint, tsc, build, browser flow 통과
- Payload 완결성: 기존 status/disclosureRule 조건부 payload 유지
- 성능 우려: 신규 fetch 추가 없음, query/mutation 호출 횟수 보존
- 중복 코드 우려: Proposal과 구조는 유사하지만 공용화 조건이 미확정이므로 의도적으로 도메인별 유지
- 상세 응집도: query/navigation은 controller, form/mutation은 process, 순수 validation/payload는 model에 배치
- 상세 stale state 방지: detail ID와 연결된 종료일 draft만 현재 detail에 사용
- 상세 payload 완결성: status-only 저장의 실제 POST body가 `{"status":"CLOSED"}`이며 변경 없는 `closedAt` 생략
- 상세 접근성: invalid 종료일 alert, `aria-invalid`, `aria-describedby`, 저장 차단 확인

## Vote 목록 리뷰

### 체크리스트

- 책임 경계: data/search/process/controller/view와 thin route page 분리
- 계약: controller/view와 hook 반환을 readonly `interface`로 정의
- 재사용: 기존 entity query/mutation, Table, FilterBar, MasterDetailLayout, DateRangeField, useStatusTransition 유지
- placeholder: `isCurrentData`가 false이면 selected row·row click·save 차단
- selection: click·Enter·Space·`aria-selected`·첫 row fallback 보존
- query: status/author/title/date mapping, submit/reset/page selection reset 보존
- validation: 기존 DateRangeField native invalid/form submit 차단 보존, 새 오류 state·문구 없음
- payload: 실제 status-only POST body `{"status":"COMPLETED"}`, 변경 없는 disclosure/closedAt 미포함
- cache: detail setQueryData와 list invalidation 후 selected row/detail/KPI 동기화
- 성능: 신규 fetch 없음, 기존 query/mutation 호출 정책 유지
- 공용화: Vote status/disclosure/DTO/route 차이로 generic controller/process 미도입

### 독립 시각 QA

- 기능·디자인 시스템 무결성: PASS, HIGH confidence
- 시각·CJK 정밀성: PASS, HIGH confidence
- 1280·768·375 fresh PNG 크기·합성 정상
- 변경된 7개 Vote 파일 원인의 blocking issue 0건
- DateRange placeholder 분절, 768/375 Table horizontal viewport, navigation rail/toggle은 unchanged shared/widget deferred 이슈

## Discussion 상세 독립 시각 QA

### 기능·디자인 시스템 무결성

- 판정: PASS
- confidence: HIGH
- real DOM과 기존 shared primitive 사용 확인
- 1280·768·375에서 detail 카드·입력·ratio·의견·이력·액션의 clipping/overflow 없음
- 변경된 Discussion 상세 파일이 원인인 blocking issue 0건

### 시각·CJK 정밀성

- 판정: PASS
- confidence: HIGH
- 세 fresh PNG의 합성·크기 정상
- clipping, tofu, baseline 손실, 부자연스러운 한 글자 조사·어미 고립 0건
- 375px navigation toggle 겹침은 `widgets/side-navigation` 소유의 기존 deferred 이슈
- 375px timeline 줄바꿈은 의미 단위를 유지하며 CJK 결함 아님

## Vote 상세 리뷰

### 체크리스트

- 책임 경계: thin page, typed controller, process, pure model, JSX view 분리
- 계약: `nextStatus`를 `CpVoteStatus | null`로 유지하고 shared UI 입력 callback만 `string | null`로 수용
- query: 기존 detail hook의 mount refetch와 `errorUpdatedAt` 기반 Dialog 중복 방지 보존
- stale state: detail ID keyed 종료일 draft와 status transition `resetKey`로 detail 교체 안전성 확보
- validation: trim·ISO 형식·`periodFrom` 하한을 유지하되 기존처럼 저장만 차단하고 새 오류 문구·ARIA 없음
- payload: 실제 closedAt-only POST body `{"closedAt":"2026-03-21"}`, status-only body `{"status":"COMPLETED"}`
- mutation: 중복 submit guard, loading/disabled, 성공·실패 Dialog, response sync와 transition reset 보존
- view: choices, 2분할 ratio, stance 없는 의견, 이력, 문구·class·ARIA 보존
- 공용화: Vote/Discussion status·DTO·결과·의견 차이로 generic detail/process/model 미도입

### 독립 시각 QA

- 최초 기능 무결성 Oracle이 `nextStatus` 타입 확장을 REVISE로 판정했고 최소 타입 수정 후 재검증했다.
- 최종 기능·디자인 시스템 무결성: PASS, HIGH confidence
- 최종 시각·CJK 정밀성: PASS, HIGH confidence
- 1280×1127·768×1287·375×1549 fresh post-fix PNG 크기·합성 정상
- 세 viewport horizontal overflow·clipping·glyph 손실 0건
- 375px `처리자` 음절 분리는 unchanged shared TimelineList/copy의 기존 비차단 debt
- 변경된 6개 Vote 상세 파일 원인의 blocking issue 0건

## 확인된 결함

- 이번 변경으로 발생한 blocking defect 없음
- 두 Oracle 모두 변경된 상세 파일의 blocking defect가 없다고 독립 판정
- 두 Oracle 모두 변경된 Vote 목록 파일의 blocking defect가 없다고 독립 판정
- 최종 두 Oracle 모두 변경된 Vote 상세 파일의 blocking defect가 없다고 독립 판정
- 두 Oracle 모두 Comment 목록의 tranche regression과 blocking defect가 없다고 독립 판정

## Comment 목록 리뷰

### 체크리스트

- 책임 경계: data/search/process/controller/view와 thin route page 분리
- 계약: controller/view와 hook 반환을 readonly `interface`로 정의
- 재사용: 기존 entity query/mutation, Table, FilterBar, MasterDetailLayout, ChoiceChip, useStatusTransition 유지
- query: source tab, author, source title, comment ID trim/mapping과 submit/reset/page selection reset 보존
- selection: selected ID lookup 후 first-row fallback, click·Enter·Space·`aria-selected` 보존
- process: 변경된 `state`만 전송하고 double-click mutation 1건 guard, 성공 후 row/detail/KPI 동기화 확인
- placeholder: stale row 선택·처리 가능 observable을 의도적으로 보존했으며 guard 도입은 후속 debt
- 성능: 신규 fetch 없음, 기존 query retry와 mutation invalidation 정책 유지
- 공용화: Comment source/state/DTO 차이로 generic controller/process 미도입

### 독립 시각 QA

- 기능·디자인 시스템 무결성: PASS, MEDIUM confidence
- 반응형·CJK 정밀성: PASS, MEDIUM confidence
- 1280×1120·768×1400·375×2000 fresh PNG 크기·합성 정상
- Comment tranche가 도입한 시각·한글 렌더링 회귀와 blocking issue 0건
- 768/375 Table clipping·CJK 조각, navigation 침범, 필터 줄바꿈과 모바일 보조 문구 대비는 unchanged shared/widget deferred 이슈

### 조회 실패 검증

- 조회 실패 Alert·fallback·retry는 MSW Service Worker가 Playwright route를 선점했다.
- Oracle 권고의 CDP service worker bypass는 외부 API 인증서 `ERR_CERT_COMMON_NAME_INVALID`로 차단됐고, CDP Fetch도 service worker target을 가로채지 못했다.
- Playwright network 기록에서 app의 실제 query-bearing Vite worker module URL을 식별해 동일 활성 worker에 일회성 500 handler를 등록했다.
- 최초 query retry GET 2회 후 Alert·0 rows·`다시 조회`, 사용자 retry 후 GET 누적 4회·두 번째 Alert를 확인했다.
- handler reset·초기화 뒤 정상 GET 200·36건·10개 row·CM-001002 fallback·retry 제거·검색 draft 비움을 재확인했다.

## 잔여 사항

1. TypeScript LSP 미설치
2. test script 부재
3. 기존 DateRange placeholder 분절과 768/375 Table horizontal viewport
4. 기존 shared navigation rail 높이 단절과 모바일 toggle 겹침
5. 기존 375px TimelineList의 `처리자` 음절 분리
6. Watcher `confirmed` 부재

## 에스컬레이션

- Claude 결제/API 제한으로 Planner·Refactorer·Watcher agent 호출 불가
- 승인된 plan 기반 main Codex fallback 적용
- Closure 금지 유지

## Proposal 상세·process 리뷰

### 체크리스트

- 책임 경계: thin page, typed controller, page-local process, JSX view 분리
- 계약: process/retry/controller를 readonly `interface`로 정의
- 재사용: 기존 entity detail query/process mutation, PageHeader, ActionBar, SectionCard, DefinitionList, TimelineList, TextArea, Button, Loading, useDialog 유지
- query: 빈 proposalId disabled, AbortSignal, query key, retry 1회, `errorUpdatedAt` Dialog 중복 방지 보존
- process: detail ID keyed draft, 표시값 원본 유지, trim 기준 non-empty·changed gating 보존
- payload: 실제 POST body에 trim된 `reviewComment`만 포함, status·department 미포함
- validation: 현재 없는 1000자 client validation·maxLength·ARIA를 추가하지 않고 server 400 observable 보존
- mutation: retry 0, pending disabled/loading, response detail cache·history 동기화와 list prefix invalidation 보존
- view: status·department 읽기 전용, 기존 섹션 순서·문구·class·ARIA 보존
- 공용화: 단일 입력 규칙은 process에 유지하고 model/generic CP abstraction 미도입

### 독립 시각 QA

- 기능·디자인 시스템 무결성: PASS, MEDIUM confidence
- 반응형·CJK: 책임 분리 tranche PASS, 전체 화면 REVISE, MEDIUM confidence
- 1280×900·768×1024·375×1250 fresh PNG 크기·합성 정상
- Proposal tranche가 도입한 기능·시각·CJK blocking issue 0건
- 768/375 textarea의 종결어미·음절 분절과 navigation intrusion은 unchanged shared debt
- 사용자가 shared 리팩터링을 도메인 분리 이후로 지정했으므로 이번 tranche에서는 accepted deferred로 분류

### 확인된 결함

- 이번 Proposal 책임 분리로 발생한 blocking defect 없음
- CJK Oracle의 전체 화면 REVISE는 shared TextArea/layout의 기존 반응형 조판 문제이며 tranche source 수정 대상이 아님

### 잔여 사항

1. TypeScript LSP 미설치
2. test script 부재
3. 768/375 shared TextArea의 한국어 종결어미·음절 분절
4. 기존 shared navigation rail/toggle 침범
5. Watcher `confirmed` 부재

### 상태

- Watcher unavailable로 Closure 금지
- Proposal tranche: `paused_after_generator`
