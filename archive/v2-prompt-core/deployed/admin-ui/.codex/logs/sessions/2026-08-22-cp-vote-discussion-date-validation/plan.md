# 계획

## 상태
- `cancelled_by_user`
- 날짜 검증 구현·브라우저 QA·Watcher·이미지 캡처를 전면 중단했다.

## 목표
- Vote·Discussion의 목록 query, 상세 종료일, update payload, 응답 날짜가 실제 `YYYY-MM-DD` 달력 날짜만 허용하도록 한다.
- Vote 목록과 상세의 silent validation을 Discussion과 같은 no-op·inline alert 계약으로 맞춘다.
- 기존 DateRangeField, DTO shape, endpoint, query key, 성공 흐름을 유지한다.

## 섹션 1 — entity 날짜 경계
### 담당
- Generator

### 변경 파일
- `src/entities/cp-vote/api/cp-vote.dto.ts`
- `src/entities/cp-discussion/api/cp-discussion.dto.ts`
- `src/entities/cp-vote/api/cp-vote.api.ts`
- `src/entities/cp-discussion/api/cp-discussion.api.ts`

### 변경
1. 도메인 date schema를 regex에서 `z.iso.date()`로 교체한다.
2. list/detail response schema, range refine, DTO shape는 유지한다.
3. `getList`는 list query schema parse 성공값만 HTTP params로 전달한다.
4. `updateProcess`는 update schema parse 성공값만 HTTP body로 전달한다.
5. API 메서드를 async로 유지해 parse 오류를 Promise rejection으로 전달한다.

### 실패 계약
- invalid query/payload이면 HTTP 요청, cache 변경, 성공 callback이 발생하지 않는다.
- 유효한 입력의 endpoint와 직렬화 shape는 유지한다.

## 섹션 2 — Vote 목록 기간 parity
### 담당
- Generator

### 변경 파일
- `src/pages/cp-vote/ui/use-cp-vote-list-search.tsx`
- `src/pages/cp-vote/ui/use-cp-vote-list-controller.tsx`
- `src/pages/cp-vote/ui/cp-vote-list.types.ts`
- `src/pages/cp-vote/ui/cp-vote-list-view.tsx`

### 변경
1. Discussion과 같은 `periodValidationMessage`, `periodInputRevision`, invalid capture 계약을 추가한다.
2. invalid segment 또는 `startDate > endDate`이면 submit은 false를 반환한다.
3. invalid submit은 query, 조회 결과, 선택 상세를 유지한다.
4. 성공한 submit만 page 1 query를 적용하고 process selection을 reset한다.
5. 기간 수정 시 오류를 제거하고 reset 시 React Aria segment 상태까지 초기화한다.
6. View는 `role=alert` 오류를 표시한다.

## 섹션 3 — 상세 종료일·공통 오류 UX
### 담당
- Generator

### 변경 파일
- `src/pages/cp-vote/ui/cp-vote-detail.model.ts`
- `src/pages/cp-vote/ui/use-cp-vote-detail-process.tsx`
- `src/pages/cp-vote/ui/use-cp-vote-detail-controller.tsx`
- `src/pages/cp-vote/ui/cp-vote-detail.types.ts`
- `src/pages/cp-vote/ui/cp-vote-detail-view.tsx`
- `src/pages/cp-discussion/ui/cp-discussion-detail.model.ts`
- `src/pages/cp-discussion/ui/use-cp-discussion-list-search.tsx`
- `src/pages/cp-discussion/ui/cp-discussion-list-view.tsx`
- `src/pages/cp-discussion/ui/cp-discussion-detail-view.tsx`
- `src/pages/cp-discussion/ui/cp-discussion-list-page.css`
- `src/shared/assets/css/_cp-admin.css`

### 변경
1. 두 상세 validator는 로컬 `z.iso.date().safeParse(closedAt).success`와 `closedAt >= periodFrom`을 함께 요구한다.
2. Vote process/controller/types에 `closedAtErrorMessage`를 연결한다.
3. Vote TextInput에 `error`, `aria-invalid`, `aria-describedby`를 연결하고 `role=alert` 문구를 표시한다.
4. invalid 상세 입력은 `canSave=false`, mutation 0건, 성공 Dialog 0건을 보장한다.
5. Discussion의 목록·상세 검증 기능은 유지하고 메시지만 실제 날짜와 순서 조건을 모두 설명하도록 보정한다.
6. `_cp-admin.css`에 `--clr-error-500` 기반 `.cp-validation-message`를 추가한다.
7. Discussion 전용 validation class를 제거하고 Vote·Discussion 네 사용처를 공통 class로 통일한다.

## 명시적 비목표
- `src/features/calendar-picker/**` 변경
- `src/shared/ui/date-range-picker/**` 변경
- 신규 UI component, hook, recipe, dependency 추가
- DateRange·DTO 공개 필드, endpoint, query key 변경
- 서버 응답의 `periodFrom <= periodTo` 의미 규칙 추가
- 기존 CP 화면 전체 i18n 전환 또는 레거시 i18n 인프라 재도입
- 테스트 인프라 신설

## 대안과 판단
### A. 권고안: Zod boundary + Vote parity + 공통 오류 class
- 실제 날짜, production HTTP 경계, UI no-op·접근성을 함께 보장한다.
- 변경 파일은 많지만 각 계층의 기존 책임을 유지한다.

### B. Vote UI parity만 적용
- 변경량은 작지만 불가능한 달력 날짜와 API 경계 누락이 남아 부분 해결이므로 제외한다.

### C. shared date helper/schema 추가
- 현재는 `z.iso.date()` 자체가 충분히 명확하고 generic 계약이 추가되므로 제외한다.

### D. DateRangePicker adapter 수정
- 기존 invalid event와 `data-invalid` 표면으로 충족 가능해 제외한다.

### E. Discussion class를 Vote에서 직접 사용하거나 Vote CSS 복제
- 도메인 누수 또는 동일 표현 중복이므로 제외한다.

## 수용 기준
1. `2026-02-29`, `2026-04-31`, `2026-99-99`는 invalid다.
2. `2028-02-29`, `2026-02-28`은 valid다.
3. 두 도메인의 response parser가 불가능한 `periodFrom`·`periodTo`를 거부한다.
4. 두 API는 invalid query/update payload를 HTTP 전에 Promise rejection으로 거부한다.
5. Vote 목록 invalid submit은 query와 선택 상세를 보존한다.
6. Vote 목록 valid submit만 query page 1과 process reset을 수행한다.
7. Vote 목록 reset은 오류와 React Aria segment를 함께 초기화한다.
8. Vote 상세 invalid 종료일은 inline alert와 접근성 연결을 제공하고 저장을 막는다.
9. Discussion 목록·상세 검증에 회귀가 없다.
10. 모든 날짜 오류 문구는 `.cp-validation-message`를 사용한다.

## 검증 계획
### 정적
- 변경 TypeScript/TSX 파일 LSP diagnostics. LSP 미설치 상태면 제약 기록.
- 변경 파일 scoped ESLint.
- `yarn tsc --noEmit`.
- `yarn build`.
- scoped `git diff --check`.
- Bun no-excuse 도구가 미설치면 제약 기록.

### 런타임 schema/API
- Zod valid/invalid 날짜 matrix를 실제 설치 버전에서 실행한다.
- 두 API에 invalid list query/update payload를 전달하고 HTTP handler hit가 0인지 확인한다.
- impossible response date를 parser에 전달해 cache 진입 전 rejection을 확인한다.

### 브라우저
- `/cp/votes`, `/cp/discussions`: invalid segment, 역전 범위, valid 범위, 수정, reset을 검증한다.
- invalid 목록 submit 전후 query·목록·선택 행이 동일한지 확인한다.
- `/cp/votes/:voteId`, `/cp/discussions/:discussionId`: impossible date, 시작일 이전, 윤년 valid date를 검증한다.
- invalid 상세에서 `aria-invalid`, `aria-describedby`, `role=alert`, 저장 비활성, mutation 0건을 확인한다.
- valid 상세 저장의 기존 payload·성공 흐름을 확인한다.
- 두 도메인의 오류 스타일과 브라우저 console error·warning 0건을 확인한다.

## 필요 에이전트
- Planner: 범위·실패 계약·검증 matrix 확정 완료.
- Generator: 승인 후 세 섹션을 순서대로 구현.
- Watcher: 현재 API 비가용으로 실행하지 않음.
- Closure: Watcher `confirmed` 후에만 실행.

## 적용 스킬
- `policy-harness`
- `policy-coding-convention`
- `policy-validation`
- `policy-hook-extraction`
- `policy-abstraction-strategy`
- `policy-type-definition`
- `policy-ui-library`
- `policy-styles`
- `policy-data-fetch-layer`
- `policy-documentation`
- `policy-review-checklist`
- `reference-components`
- `component-calendar-picker`
- `component-text-input`
- `recipe-api-authoring`
- `programming`
- `frontend`
- `playwright`
- `visual-qa`

## 승인 게이트
- 승인 전 구현 금지.
- 승인 문구: `진행해줘` 또는 `Proceed`.
- 이 계획대로 진행할까요, 아니면 조정할 부분이 있나요?
