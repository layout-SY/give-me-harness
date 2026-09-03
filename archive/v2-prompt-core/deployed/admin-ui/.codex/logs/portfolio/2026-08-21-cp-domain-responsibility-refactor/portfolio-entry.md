# 포트폴리오 경험 기록 — CP 도메인 책임 분리

## 작업 개요

- 구현/수정 내용: Discussion 목록·상세, Vote 목록·상세, Comment 목록, Proposal 상세 page의 query/form/process/model/view 책임 분리
- 구현 이유: API·상태·검증·payload·Dialog·navigation·JSX가 한 파일에 집중된 구조 개선
- 작업 유형: 기능 보존형 refactor

## 문제 상황

- 문제 출처: 사용자 요청과 코드 구조 audit
- 대상 도메인·서비스: 시민토론 관리 목록·상세, 시민투표 관리 목록·상세, 댓글 통합 관리 목록, 시민제안 상세
- 기존 문제와 영향: Discussion 목록 190줄·상세 121줄, Vote 목록 180줄·상세 142줄, Proposal 상세 166줄 route page와 Comment 단일 page hook이 서버 상태, 검색/form draft, validation, 선택, mutation payload, feedback, navigation, rendering을 함께 소유해 변경 이유가 서로 얽혀 있었다.

## 요구사항 및 의사결정

- 사용자 요구: shared 공용 리소스는 후순위로 두고 도메인별 책임 분리를 순차 진행
- 에이전트 제안: Proposal 목록의 검증된 도메인 전용 page/controller/view 패턴을 Discussion에 적용

| 접근법 | 장점 | 단점 | 선택 여부와 이유 |
|---|---|---|---|
| 기존 page 내부 helper만 추출 | 파일 수 증가가 적음 | 상태 lifecycle과 JSX 결합이 유지됨 | 미채택 — 요청한 책임 경계가 생기지 않음 |
| Discussion 전용 controller/data/search/process/view | 변경 이유별 경계가 명확함 | 도메인 파일 수 증가 | 채택 — Proposal 기준 구조와 기능 보존에 적합 |
| Discussion·Vote 공용 generic controller | 중복 감소 가능 | query·validation·payload 차이를 generic으로 숨김 | 미채택 — 공용화 불변식 미확정 |
| shared hook 수정과 동시 진행 | 전체 구조 일관화 | 사용자 deferred 범위 위반, 영향 범위 확대 | 미채택 — 명시적 제외 |
| 상세도 목록처럼 data/search까지 세분화 | 파일 역할 형식 통일 | 상세에 없는 검색·선택 책임까지 빈 추상화로 추가 | 미채택 — 화면 복잡도에 맞춰 controller/process/model/view만 적용 |
| Vote에 Discussion search/process 직접 재사용 | 파일 증가 감소 | status·DTO·기간 validation observable이 다름 | 미채택 — 구조만 참조하고 Vote 전용 경계 채택 |
| Vote 목록에 새 기간 오류 문구 추가 | 사용자 피드백 강화 | 기능 보존 범위를 넘어 기존 native invalid 동작 변경 | 미채택 — 현재 DateRangeField/form 차단 유지 |
| Vote 상세에 Discussion 종료일 오류 UI 복제 | 접근성 피드백 강화 | 기존 Vote의 저장-only 차단 observable 변경 | 미채택 — 오류 문구·ARIA를 추가하지 않음 |
| Vote·Discussion 상세 generic process/model | 유사 코드 감소 | status·DTO·결과·의견·공개 규칙 차이를 generic으로 흡수 | 미채택 — Vote-local 경계 유지 |
| Comment에 선행 목록 placeholder guard 적용 | stale row 조작 방지 | 기존 Comment observable 변경 | 미채택 — 기능 보존 후 별도 개선으로 분리 |
| Comment·Vote 공용 list controller | 파일 수 감소 | source tab·기간·navigation·DTO 차이를 generic으로 숨김 | 미채택 — Comment-local 경계 유지 |
| Proposal 상세에 별도 model 추가 | 선행 상세와 파일 형태 통일 | trim·비교·단일 payload에 과잉 추상화 | 미채택 — process 내부의 짧은 규칙으로 유지 |
| Proposal에 1000자 client validation 추가 | 요청 전 오류 표시 | 기존 server validation observable과 UI 계약 변경 | 미채택 — DTO/server 경계 유지 |

## 사용 기술과 구체적 목적

| 기술/패턴/아키텍처 | 해결하려는 문제 | 적용 위치와 목적 | 미채택 대안/이유 |
|---|---|---|---|
| TanStack Query hook 재사용 | server state 중복 방지 | data/process hook에서 기존 entity hook 조합 | API 직접 호출 — cache·parser 계약 우회 |
| Controller/View | orchestration과 JSX 결합 | route page를 10줄 진입점으로 축소 | props 개별 전달 — 계약 분산 |
| 도메인 search hook | draft와 committed query 혼재 | validation·DTO mapping·reset 캡슐화 | 공용 search hook — 기간 규칙이 도메인 전용 |
| interface 계약 | controller와 view 관계 명시 | search/table/detail/retry contract | 임시 object type — 레이어 계약 의도 약화 |
| 순수 model 함수 | 종료일 규칙과 React lifecycle 분리 | 상세 date validation·조건부 DTO mapping | process hook 내부 유지 — 단위 규칙 변경 이유가 mutation과 결합 |
| placeholder data guard | 재조회 중 stale row 조작 방지 | Vote data/process/controller에서 `isCurrentData` 전달 | view 단독 loading 처리 — mutation 경계 보호 부족 |
| domain-local process hook | Vote 상태·공개 기준·payload 응집 | Vote 선택·transition·mutation/feedback 캡슐화 | 공용 generic process — 도메인 어휘 누수 |
| detail ID keyed draft | 비동기 detail 전환의 stale form 방지 | Vote 상세 종료일 selection에 detail ID 포함 | effect state sync — 추가 render와 이전 detail 값 노출 가능 |
| closed vocabulary contract | string 타입 확장 방지 | Vote 상세 `nextStatus`를 `CpVoteStatus \| null`로 고정 | shared callback 타입 그대로 노출 — invalid status 허용 |
| Comment data/search/process 분리 | query·검색·처리 lifecycle 결합 해소 | Comment 전용 source tab·state DTO와 feedback 국소화 | Vote controller 재사용 — 도메인 observable 차이 은폐 |
| Proposal detail-ID keyed draft | async detail 도착·전환 시 입력 혼입 방지 | Proposal process hook에서 persisted reviewComment fallback | 단순 문자열 state — 초기 query 전 빈 값과 detail 전환 혼입 가능 |

## 적용 내용

- `cp-discussion-list-page.tsx`: controller/view 결선만 유지
- `cp-discussion-list.types.ts`: view 소비 계약 정의
- `use-cp-discussion-list-data.tsx`: query lifecycle과 조회 feedback
- `use-cp-discussion-list-search.tsx`: 검색 draft, 기간 validation, DTO mapping
- `use-cp-discussion-list-process.tsx`: 선택, 상태 전이, mutation payload, 저장 feedback
- `use-cp-discussion-list-controller.tsx`: 세 hook 조합과 navigation
- `cp-discussion-list-view.tsx`: 기존 JSX 보존
- `cp-discussion-detail-page.tsx`: controller/view 결선만 유지
- `cp-discussion-detail.types.ts`: 상세 view 계약 정의
- `cp-discussion-detail.model.ts`: 종료일 validation과 process payload mapping
- `use-cp-discussion-detail-process.tsx`: form draft, status transition, mutation/feedback
- `use-cp-discussion-detail-controller.tsx`: route/query/error/retry/navigation orchestration
- `cp-discussion-detail-view.tsx`: 기존 상세 JSX·문구·ARIA 보존
- `cp-vote-list-page.tsx`: controller/view 결선만 유지
- `cp-vote-list.types.ts`: Vote view 소비 계약 정의
- `use-cp-vote-list-data.tsx`: query lifecycle, KPI, placeholder, retry
- `use-cp-vote-list-search.tsx`: 검색 draft, query mapping, reset/page
- `use-cp-vote-list-process.tsx`: 선택, status/disclosure transition, mutation/feedback
- `use-cp-vote-list-controller.tsx`: 세 hook 조합과 detail navigation
- `cp-vote-list-view.tsx`: 기존 JSX·Table keyboard/selection 계약 보존
- `cp-vote-detail-page.tsx`: controller/view 결선만 유지
- `cp-vote-detail.types.ts`: process/retry/controller와 Vote status 계약 정의
- `cp-vote-detail.model.ts`: 종료일 validation과 조건부 process payload mapping
- `use-cp-vote-detail-process.tsx`: detail keyed draft, status transition, mutation/feedback
- `use-cp-vote-detail-controller.tsx`: route/query/error/retry/navigation orchestration
- `cp-vote-detail-view.tsx`: choices·2분할 결과·의견·이력 JSX와 기존 문구·ARIA 보존
- `cp-comment-list-page.tsx`: controller/view 결선만 유지
- `cp-comment-list.types.ts`: source/search/table/detail/retry 계약 정의
- `use-cp-comment-list-data.tsx`: query lifecycle, KPI, 조회 feedback/retry
- `use-cp-comment-list-search.tsx`: source tab과 text draft, trim/query mapping
- `use-cp-comment-list-process.tsx`: row selection, state transition, mutation/feedback
- `use-cp-comment-list-controller.tsx`: 세 hook 조합과 selection reset 순서
- `cp-comment-list-view.tsx`: 기존 JSX·Table keyboard/selection 계약 보존
- `cp-proposal-detail-page.tsx`: controller/view 결선과 화면 정의 주석만 유지
- `cp-proposal-detail.types.ts`: process/retry/controller 계약 정의
- `use-cp-proposal-detail-process.tsx`: detail keyed reviewComment draft, 저장 조건, mutation/feedback
- `use-cp-proposal-detail-controller.tsx`: route/query/error/retry/navigation orchestration
- `cp-proposal-detail-view.tsx`: 기존 Proposal 상세 JSX·문구·ARIA 보존

```text
Before
CpDiscussionListPage
└─ query + search + validation + process + dialog + navigation + JSX

After
CpDiscussionListPage
└─ useCpDiscussionListController
   ├─ useCpDiscussionListData
   ├─ useCpDiscussionListSearch
   ├─ useCpDiscussionListProcess
   └─ CpDiscussionListView

CpDiscussionDetailPage
└─ useCpDiscussionDetailController
   ├─ useCpDiscussionDetailProcess
   │  └─ validation + payload model
   └─ CpDiscussionDetailView

CpVoteListPage
└─ useCpVoteListController
   ├─ useCpVoteListData
   ├─ useCpVoteListSearch
   ├─ useCpVoteListProcess
   └─ CpVoteListView

CpVoteDetailPage
└─ useCpVoteDetailController
   ├─ useCpVoteDetailProcess
   │  └─ validation + payload model
    └─ CpVoteDetailView

CpCommentListPage
└─ useCpCommentListController
   ├─ useCpCommentListData
   ├─ useCpCommentListSearch
   ├─ useCpCommentListProcess
   └─ CpCommentListView

CpProposalDetailPage
└─ useCpProposalDetailController
   ├─ useCpProposalDetailProcess
   └─ CpProposalDetailView
```

## 결과 및 성과

- before/after: Discussion 목록 190줄 → 10줄, 상세 121줄 → 10줄, Vote 목록 180줄 → 11줄, Vote 상세 142줄 → 11줄, Comment route page → 8줄, Proposal 상세 166줄 → 14 pure LOC
- 모든 신규 파일: 최대 176 pure LOC, 250 LOC 제한 이내
- targeted ESLint, tsc, production build 통과
- 실제 브라우저에서 목록 검색·초기화·선택과 상세 조회·종료일 ARIA validation·status-only POST payload·cache 갱신·목록 이동 통과
- Vote 목록에서 author/title/status/date query, click/keyboard selection, pagination fallback, status-only POST, list/KPI cache 갱신, 상세 이동 통과
- console errors/warnings 0건
- 상세 화면 1280·768·375 fresh capture에 대한 독립 시각 QA Oracle 2건 PASS
- Vote 목록 1280·768·375 fresh capture에 대한 독립 시각 QA Oracle 2건 PASS
- Vote 상세에서 invalid 종료일 저장 차단·오류 UI 부재, trimmed closedAt-only·status-only POST, history/cache sync, 404 retry/back 통과
- Vote 상세 1280·768·375 fresh post-fix capture에 대한 최종 독립 시각 QA Oracle 2건 PASS
- 최초 Oracle의 status 타입 확장 지적을 `CpVoteStatus | null`로 수정해 타입 경계까지 재검증
- Comment source/text query, click·keyboard selection, pagination, state-only POST, double-submit guard, cache/KPI 동기화 통과
- Comment 1280·768·375 fresh capture에 대한 독립 시각 QA Oracle 2건 PASS, MEDIUM confidence
- Comment 활성 MSW worker에 일회성 500 handler를 등록해 query retry 2회, Alert·fallback, 사용자 retry 추가 2회와 handler reset 후 정상 복구를 브라우저에서 확인
- Proposal 상세 공백·빈 값 차단, trimmed reviewComment-only POST, history/detail/list cache 동기화, 1001자 server validation, 404 자동·수동 retry 통과
- Proposal 상세 1280·768·375 fresh capture에서 tranche 원인 clipping·glyph 손실 0건, 기능 Oracle PASS와 CJK tranche PASS 확보
- CJK Oracle의 전체 화면 REVISE는 unchanged shared TextArea/navigation 부채로 분류하고 사용자 지정 순서에 따라 후속 shared 단계로 이관
- 사용자 후속 피드백: 현재 섹션 구현 후 미수집
- 잔여 리스크: test script와 Watcher 판정 부재, shared shell/table/TimelineList 반응형 이슈 deferred

## 회고

- 잘된 판단: 공용화를 미루고 도메인 전용 경계를 먼저 만든 점이 scope와 타입 계약을 단순하게 유지했다.
- 다시 한다면 바꿀 점: DOM ref를 처음부터 view 이벤트 경계에 남겼다면 React refs lint 수정 라운드를 줄일 수 있었다.
- 다음 작업에 적용할 인사이트: controller 계약에는 렌더링 데이터와 callback만 노출하고 mutable DOM resource는 포함하지 않는다.
- Vote에서 얻은 인사이트: 같은 레이아웃이라도 기간 validation observable과 DTO vocabulary가 다르면 구조만 재사용하고 도메인 hook은 분리해야 한다.
- Vote 상세에서 얻은 인사이트: shared Select가 string callback을 제공해도 controller/process의 저장 상태 계약은 domain union으로 다시 좁혀야 구조 분리 중 타입 불변식이 소실되지 않는다.
- Comment에서 얻은 인사이트: 구조가 유사해도 placeholder 조작 정책, source tab, query vocabulary가 다르면 기능 보존형 refactor에서 선행 도메인의 guard까지 이식하지 않아야 한다.
- Proposal 상세에서 얻은 인사이트: 선행 도메인에 model 계층이 있어도 단일 trim·비교·payload 규칙은 process에 유지해야 파일 형태 통일을 위한 과잉 추상화를 피할 수 있다.
