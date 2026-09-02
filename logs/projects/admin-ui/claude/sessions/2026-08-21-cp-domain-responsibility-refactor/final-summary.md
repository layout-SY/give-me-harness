# CP 도메인 책임 분리 중간 요약 — Discussion 목록·상세·Vote 목록·상세·Comment 목록·Proposal 상세

## 무엇이 변경되었는가

- 전체 CP 책임 분리 순서와 shared deferred 범위를 문서화했다.
- Discussion 목록을 thin page, typed controller contract, data/search/process hooks, JSX view로 분리했다.
- Discussion 상세를 thin page, typed controller contract, process hook, 순수 model, JSX view로 분리했다.
- Vote 목록을 thin page, typed controller contract, data/search/process hooks, JSX view로 분리했다.
- Vote 상세를 thin page, typed controller contract, process hook, 순수 model, JSX view로 분리했다.
- Comment 목록을 thin page, typed controller contract, data/search/process hooks, JSX view로 분리했다.
- Proposal 상세를 thin page, typed controller contract, reviewComment process hook, JSX view로 분리했다.
- API·DTO·parser·entity query/mutation·shared UI·CSS는 변경하지 않았다.

## 왜 변경했는가

- 하나의 page가 검색, query, validation, selection, mutation, Dialog, navigation, JSX를 동시에 소유하고 있었다.
- 기능을 유지하면서 변경 이유별 경계를 도메인 내부에 만들기 위해 분리했다.
- 상세에는 없는 검색·선택 계층을 복제하지 않고 화면 복잡도에 맞춰 controller/process/model/view만 사용했다.
- Vote는 Discussion 구조만 참조하고 고유 status/disclosure/query/payload observable을 도메인 내부에 유지했다.
- Vote 상세의 invalid 종료일은 새 오류 문구·ARIA 없이 저장만 차단하는 기존 observable을 유지했다.
- Comment의 source tab·text query·state-only process와 placeholder observable을 도메인 내부에 유지했다.
- Proposal 상세의 읽기 전용 status/department와 reviewComment-only payload·server validation observable을 유지했다.

## 재사용한 자산

- Proposal 목록의 page/controller/view 구조
- 기존 Discussion entity query/mutation
- 기존 status transition과 shared UI primitives
- 목록 tranche에서 검증한 typed controller/view 경계
- 기존 Vote entity query/mutation과 config
- Discussion 상세의 detail keyed draft와 controller/process/model/view 책임 구조
- 기존 Comment entity query/mutation, config, Table, FilterBar, MasterDetailLayout, ChoiceChip
- 기존 Proposal detail query/process mutation, PageHeader, ActionBar, SectionCard, DefinitionList, TimelineList, TextArea

## 영향받는 영역

- `src/pages/cp-discussion/ui`, `src/pages/cp-vote/ui`, `src/pages/cp-comment/ui`, `src/pages/cp-proposal/ui`의 승인된 목록·상세 내부 구조만 변경
- route와 사용자 화면 observable은 유지

## 검증

- targeted ESLint: pass
- TypeScript compile: pass
- production build: pass
- browser search/reset/select/save/detail/invalid-period: pass
- detail GET, invalid 종료일 ARIA/저장 차단, status-only POST body, detail/list cache 갱신, 목록 이동: pass
- console errors/warnings: 0
- detail responsive capture 1280·768·375: page-local clipping/overflow 0건
- 독립 visual QA Oracle 2건: PASS, HIGH confidence
- Vote author/title/status/date query, click/keyboard selection, pagination, status-only POST, cache/KPI, detail navigation: pass
- Vote responsive capture 1280·768·375과 독립 visual QA Oracle 2건: PASS, HIGH confidence
- Vote 상세 invalid 종료일 차단, trimmed closedAt-only·status-only POST, response/history sync, 404 retry/back: pass
- Vote 상세 post-fix capture 1280×1127·768×1287·375×1549과 최종 독립 visual QA Oracle 2건: PASS, HIGH confidence
- Vote 상세 최초 Oracle의 `nextStatus` 타입 확장 finding을 `CpVoteStatus | null`로 수정하고 재검증
- 기존 shared navigation rail/toggle 문제: 현재 scope에서 deferred
- 기존 DateRange placeholder와 Table horizontal viewport 문제: 현재 scope에서 deferred
- 기존 375px TimelineList `처리자` 음절 분리: shared/copy scope로 deferred
- Comment source/text query, click·Enter·Space 선택, pagination, state-only POST, double-submit guard, cache/KPI 동기화: pass
- Comment 정상 route 복구 GET 200·36건·10개 row·상세와 console errors 0: pass
- Comment responsive capture 1280×1120·768×1400·375×2000과 독립 visual QA Oracle 2건: PASS, MEDIUM confidence
- Comment 조회 실패 Alert·fallback·retry: 활성 MSW worker 500 주입으로 최초 GET 2회, 사용자 retry 후 누적 4회, Alert 재노출과 정상 복구 확인
- 기존 Comment 768/375 Table clipping·CJK 조각·navigation 침범·보조 문구 대비: shared/widget scope로 deferred
- Proposal 상세 공백·빈 값 차단, trimmed reviewComment-only POST, success/history/cache/list invalidation, 1001자 server validation, 404 자동·수동 retry: pass
- Proposal 상세 capture 1280×900·768×1024·375×1250: 정상 합성, tranche 원인 clipping·glyph 손실 0건
- Proposal 기능·디자인 Oracle PASS; CJK Oracle은 tranche PASS·전체 화면 REVISE
- Proposal 768/375 TextArea CJK 분절과 navigation 침범: 사용자 지정 순서에 따라 shared 단계로 deferred

## 현재 상태

- local verification: pass
- independent visual QA: domain tranches pass; Proposal shared CJK debt accepted deferred
- Watcher: 미실행
- Closure: 미진행
- pipeline: `paused_after_generator`

## 후속 제안

- 다음 섹션 후보는 남은 CP 도메인 책임 분리다.
- 모든 도메인 책임 분리 후 shared TextArea·navigation·Table 반응형 리팩터링을 진행한다.
