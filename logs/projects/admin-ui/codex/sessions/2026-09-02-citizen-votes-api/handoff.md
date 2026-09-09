# 인계

## 목표 및 현재 상태

- 목표: 관리자 시민투표 목록·상세를 실제 `GET /citizen/votes`, `GET /citizen/votes/{voteId}` 계약에 연결한다.
- 현재 브랜치: `task/connect-citizen-votes-api`.
- 분기 기준·직접 merge 대상: `sy-main`.
- 승인 시점 부모 HEAD: `e26b263afe2478cbabd3e34fdc82306e0715d059`.
- 현재 상태: Hephaestus가 API·DTO·parser·query hook·controller·MSW·Node 테스트를 구현했으며 아직 commit하지 않았다. production UI 두 파일은 수정하지 않아 새 read-only controller와 타입이 연결되지 않은 상태다.

## 완료된 작업

- `src/entities/cp-vote/api/cp-vote.api.ts`의 목록·상세 resource를 `/citizen/votes`로 교체하고 반복 `sort`를 `paramsSerializer.indexes: null`로 직렬화했다.
- 목록 query에 page 1-based, size 기본 20·최대 100 제한, `createdAt/id/startsAt/endsAt` asc·desc sort를 적용했다.
- 외부 응답을 Zod로 파싱하고 실제 상태 `DRAFT`, `UPCOMING`, `IN_PROGRESS`, `CLOSED`, `CANCELLED`와 실제 목록·상세 필드만 read model에 남겼다.
- 목록 응답 `{ items, total, page, size }`에서 `pageCount`를 계산하고 상세의 `totalCount = agreeCount + disagreeCount`를 parser 경계에서 검증한다.
- 양의 정수 `voteId`만 상세 query를 활성화하며 `AbortSignal`을 실제 HTTP client까지 전달한다.
- 실제 목록 API가 지원하지 않는 status/author/title/date 검색 state와 명세가 없는 legacy process mutation hook·controller·API를 제거했다.
- `src/mocks/cp-vote.handlers.ts`에 실제 endpoint, pagination, 반복 sort, size 제한, 빈 page, `INVALID_SORT_PROPERTY`, `EXPIRED_TOKEN`, `CITIZEN_VOTE_NOT_FOUND` 계약을 구현했다.
- `tests/citizen-votes-contract.test.mjs`, `tests/citizen-votes-msw.test.mjs`를 추가했다.
- `src/shared/ui/`는 조사만 했고 수정하지 않았다. 기존 `Table`, `Loading`, `Dialog`, status badge를 계속 재사용한다.

## 대기 중인 작업

- Claude Code가 다음 production UI를 새 controller 계약에 맞춰 수정해야 한다.
  - `src/pages/cp-vote/ui/cp-vote-list-view.tsx`
  - `src/pages/cp-vote/ui/cp-vote-detail-view.tsx`
- 목록 UI에서 실제 query가 지원하지 않는 FilterBar와 작성자 검색, 제목 검색, 날짜 검색, 상태 필터를 제거한다.
- 목록·상세 UI에서 상태 변경, 종료일 변경, 공개 기준 변경, 처리 저장 등 mutation 표면을 제거한다.
- 목록에는 `id`, `status`, `title`, `startsAt`, `endsAt`만 표시한다.
- 상세에는 `id`, `status`, `title`, `agenda`, `startsAt`, `endsAt`, `totalCount`, `agreeCount`, `disagreeCount`, `createdAt`, `updatedAt`만 표시한다.
- 기존 loading, retry, 목록 이동, row 선택, 상세 열기 동작은 유지한다.
- Claude Code 완료 후 Hephaestus가 최신 UI와 이 문서를 다시 읽고 build·전체 테스트·lint를 수행한 뒤 Watcher/Evaluator와 나머지 필수 산출물을 완료해야 한다.

## 결정 사항 및 제약 조건

- 실제 backend 조회 계약이 source of truth다. backend에 없는 작성자, 댓글, 처리 이력, 공개 정책을 placeholder 도메인 데이터로 생성하지 않는다.
- 목록 응답에는 상태별 전체 count가 없으므로 현재 page 데이터로 전체 상태 KPI를 추정하지 않는다. controller는 전체 `total` KPI만 제공한다.
- mutation method·URI·payload·전이 규칙이 없으므로 legacy `/v1/cp/votes/{voteId}/process`를 유지하거나 추정하지 않는다.
- Hephaestus는 `hook`, `lib`, `api`, DTO, parser, model, test를 소유한다. Claude Code는 `src/pages/cp-vote/ui/**`와 이 `handoff.md`만 수정한다.
- Claude Code는 현재 `task/connect-citizen-votes-api` 브랜치를 그대로 사용하고 브랜치를 생성하거나 전환하지 않는다.
- 사용자 제약에 따라 브라우저, 이미지 캡처, 화면 비교, 시각 QA, 실제 인증 backend 호출을 수행하지 않는다.
- TypeScript LSP server는 설치되어 있지 않아 LSP 진단을 실행할 수 없었다.

## 관련 경로

- Claude Code 수정 가능:
  - `src/pages/cp-vote/ui/cp-vote-list-view.tsx`
  - `src/pages/cp-vote/ui/cp-vote-detail-view.tsx`
  - `.codex/logs/sessions/2026-09-02-citizen-votes-api/handoff.md`
- Claude Code 읽기 전용 controller 계약:
  - `src/pages/cp-vote/model/cp-vote-list.types.ts`
  - `src/pages/cp-vote/model/cp-vote-detail.types.ts`
  - `src/pages/cp-vote/hook/use-cp-vote-list-controller.tsx`
  - `src/pages/cp-vote/hook/use-cp-vote-detail-controller.tsx`
- 실제 read model:
  - `src/entities/cp-vote/model/types.ts`
  - `src/entities/cp-vote/api/cp-vote.dto.ts`
- 검증:
  - `tests/citizen-votes-contract.test.mjs`
  - `tests/citizen-votes-msw.test.mjs`

## 명령어 및 결과

- `node --test tests/citizen-votes-contract.test.mjs tests/citizen-votes-msw.test.mjs`: 14/14 통과.
- 변경 TypeScript·MJS 대상 `npm exec eslint -- ...`: 통과, 출력 없음.
- `git diff --check`: 통과, 출력 없음.
- `npm run build`: 실패. 오류는 수정하지 않은 `cp-vote-list-view.tsx`, `cp-vote-detail-view.tsx`가 제거된 legacy search/process 계약과 backend에 없는 필드를 참조하는 항목으로 한정됐다.
- 브라우저·캡처·실제 backend 호출: 수행하지 않음.

## 다음 조치

1. Claude Code가 현재 브랜치에서 지정된 production UI 두 파일만 새 read-only controller 계약으로 수정한다.
2. Claude Code가 이 문서를 구현 결과·변경 파일·props/callback 계약·남은 제한 사항으로 갱신한다.
3. Claude Code가 사용자에게 `UI_COMPLETE` 형식으로 보고한다.
4. 사용자가 UI 완료를 확인하면 Hephaestus가 최신 UI와 이 문서를 다시 읽고 기능 통합·검증·필수 산출물을 마무리한다.

## Claude Code 인계 확인 (2026-09-02)

- 확인자: Claude Code (production UI 담당 세션).
- 세션 귀속: 이 세션은 산출물 디렉터리로 `.codex/logs/sessions/2026-09-02-citizen-votes-api/`를 사용하며 다른 디렉터리를 만들지 않는다.
- 브랜치: `task/connect-citizen-votes-api`를 그대로 사용했고 생성·전환하지 않았다.
- 상태: 사용자 승인 후 지정된 production UI 두 파일을 새 read-only controller 계약으로 수정 완료했다.

### 변경한 파일

- `src/pages/cp-vote/ui/cp-vote-list-view.tsx`
- `src/pages/cp-vote/ui/cp-vote-detail-view.tsx`

### 목록 UI 변경 내용

- `FilterBar`와 상태 필터, 작성자 검색, 제목 검색, 기간 검색 control을 모두 제거했다. `Dropdown`, `TextInput`, `DateRangeField`, `StatusTransitionField` import를 함께 제거했다.
- 상세 패널에서 상태 변경, 결과 공개 기준, `처리 저장` mutation 표면을 제거했다.
- 선택 행 요약을 실제 read model 필드인 `id`, `status`, `title`, `startsAt`, `endsAt`로 교체했다. 제거된 `authorName`, `period`, `disclosureLabel` 참조를 없앴다.
- `PageHeader` description을 조회 전용 문구인 `투표 안건 목록 조회`로 바꿨다.
- `상세처리 화면 열기` 버튼 라벨을 `상세 화면 열기`로 바꿨다.
- `KpiStrip`, `MasterDetailLayout`, `Table`, 페이지 이동, row 선택, `다시 조회` `ActionBar`는 기존 동작 그대로 유지했다.

### 상세 UI 변경 내용

- `process` controller 사용부 전체(상태 변경, 투표 종료일 입력, `처리 저장`)를 제거했다.
- 명세에 없는 작성자, 등록일, 선택지, 결과 공개 기준, 공개 안내 문구, 댓글·의견 목록, 처리 이력 섹션을 제거했다. `StatusTransitionField`, `TextInput`, `TimelineList`, `CP_VOTE_DISCLOSURE_RULE_LABELS` import를 함께 제거했다.
- 표시 필드를 `id`, `status`, `title`, `agenda`, `startsAt`, `endsAt`, `totalCount`, `agreeCount`, `disagreeCount`, `createdAt`, `updatedAt`로 한정했다.
- `RatioBar`는 유지하되 backend가 주지 않는 `agreePercent`, `disagreePercent` 대신 `agreeCount`, `disagreeCount`, `totalCount`로 표시용 백분율을 계산한다. `totalCount`가 0이면 0%로 처리한다.
- `PageHeader` 제목을 `시민투표 상세`, description을 `투표 안건 · 기간 · 집계 결과 조회`로 바꿨다.
- `Loading`, 상세 없음 fallback, `목록으로`, `다시 조회` 동작은 유지했다.

### 소비한 props/callback 계약

- `CpVoteListView`는 `controller: CpVoteListController` 하나만 받는다. 사용 항목은 `isPending`, `kpiItems`, `table.*`(`rows`, `isFetching`, `page`, `pageCount`, `pageSize`, `itemCount`, `selectedRowId`, `onPageChange`, `onRowClick`), `detail.selectedRow`, `detail.onOpenDetail`, `retry.*`다. `controller.search`는 더 이상 사용하지 않는다.
- `CpVoteDetailView`는 `controller: CpVoteDetailController` 하나만 받는다. 사용 항목은 `isPending`, `detail`, `retry.isFetching`, `retry.onRetry`, `onBack`이다. `controller.process`는 더 이상 사용하지 않는다.
- 두 뷰 모두 API 호출, 영속성, 파싱, 업무 검증, 도메인 상태 전이를 포함하지 않는다. 유일한 UI 내부 계산은 상세의 표시용 백분율 함수 `toPercent`다.

### 실행한 명령어와 결과

- `npm run build`: 성공. 이전 인계 시점의 타입 오류가 모두 해소됐다.
- `npm exec eslint -- src/pages/cp-vote/ui/cp-vote-list-view.tsx src/pages/cp-vote/ui/cp-vote-detail-view.tsx`: 통과, 출력 없음.
- `node --test tests/citizen-votes-contract.test.mjs tests/citizen-votes-msw.test.mjs`: 14/14 통과.
- `npm run test`: script가 없어 실행할 수 없다. `npm run lint` 전체는 이번 변경과 무관한 기존 위반 78건(`src/shared/ui/**` 등)이 남아 있어 실패한다. 변경 파일 범위에서는 위반이 없다.
- 브라우저, 이미지 캡처, 화면 비교, 시각 QA, 실제 backend 호출: 수행하지 않음.

### 남은 UI 제한 사항

- 목록에서 검색·필터 UI가 사라져 현재는 pagination만으로 탐색한다. backend가 검색 파라미터를 제공하면 그때 UI를 다시 추가해야 한다.
- 목록 KPI는 controller가 제공하는 전체 `total` 하나뿐이며 상태별 KPI는 표시하지 않는다.
- 상세의 찬반 백분율은 정수 반올림이라 두 값의 합이 100이 아닐 수 있다. 정확한 비율이 필요하면 backend 또는 controller에서 값을 내려주는 편이 낫다.
- 투표 상태 변경·종료·결과 공개 등 관리 동작은 UI에 없다. mutation 명세가 확정되면 controller 계약부터 다시 정의해야 한다.
- `src/pages/cp-vote/lib/`는 이번 작업에서 사용하지 않았고 Logic Session 소유라 건드리지 않았다.

### Logic Session 다음 조치

1. 최신 UI 두 파일과 이 문서를 다시 읽고 전체 검증을 재실행한다.
2. Watcher 판정과 `AGENTS.md` 3절의 나머지 필수 산출물을 완료한다.
3. commit·merge 승인 절차를 진행한다.
