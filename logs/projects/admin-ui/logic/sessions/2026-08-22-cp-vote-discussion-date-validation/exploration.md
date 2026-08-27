# 탐색 기록

## 상태
- `cancelled_by_user`
- 사용자의 하네스 우선 지시에 따라 날짜 검증 작업을 중단했다.

## 작업 분류
- 단일 섹션 correctness fix.
- 대상: Vote·Discussion 목록 기간 검색, 상세 종료일, API·응답 날짜 경계.

## 확인한 SKILL·근거
- `policy-harness`
- `policy-coding-convention`
- `policy-validation`
- `policy-hook-extraction`
- `policy-abstraction-strategy`
- `policy-type-definition`
- `policy-ui-library`
- `policy-documentation`
- `policy-review-checklist`
- `reference-components`
- `component-calendar-picker`
- `recipe-i18n`
- `programming` TypeScript reference
- Zod v4 공식 `z.iso.date()` 문서
- `.codex/memory/reusable-assets.md`

## 재사용 탐색
- `src/shared/ui/`: `date-range-picker`, `text-input`을 그대로 재사용한다.
- `src/widgets/`: 기존 `FilterBar`, `ActionBar`, `PageHeader` 계약을 유지한다.
- `src/features/calendar-picker/DateRangeField`: React Aria invalid segment와 `data-invalid` 표면이 이미 있어 수정할 필요가 없다.
- 대상 페이지에 신규 component/module/widget을 추가하지 않는다.
- HeroUI 항목 교체나 shared adapter 변경이 없으므로 별도 UI-library 채택 확인은 필요하지 않다.

## 현재 동작
### Vote 목록
- `useCpVoteListSearch.submit()`은 invalid segment와 역전 범위를 검사하지 않고 query를 갱신한다.
- controller는 submit 결과와 무관하게 process selection을 reset한다.
- View는 `DateRangeField`의 invalid 상태를 수집하거나 오류를 표시하지 않는다.

### Discussion 목록
- wrapper의 invalid event와 `[data-invalid=true]`를 수집한다.
- invalid segment 또는 `startDate > endDate`이면 query와 선택 상태를 유지하고 alert를 표시한다.
- reset 시 `periodInputRevision`으로 React Aria 내부 segment 상태도 초기화한다.
- 현재 메시지는 역전 범위만 설명해 invalid segment의 실제 원인까지 포함하지 못한다.

### Vote 상세
- 종료일 validator는 정규식과 `closedAt >= periodFrom`만 확인한다.
- invalid 변경값은 `canSave=false`로 만들지만 오류 문구와 접근성 상태를 노출하지 않아 silent validation이다.

### Discussion 상세
- Vote와 같은 정규식 validator를 사용한다.
- 오류 메시지, `error`, `aria-invalid`, `aria-describedby`, `role=alert` 계약은 이미 존재한다.

### DTO·API 경계
- Vote·Discussion date schema는 `/^\d{4}-\d{2}-\d{2}$/`만 사용해 `2026-99-99`, `2026-04-31`, 평년 `2026-02-29`를 허용한다.
- list/detail response parser는 DTO date schema를 사용하므로 잘못된 서버 날짜도 현재 통과한다.
- list query/update payload schema는 MSW handler에서만 실행되고 production API client는 typed object를 그대로 HTTP에 전달한다.

## 실증 결과
- 설치 버전: Zod `4.4.3`.
- `z.iso.date()` 실제 실행:
  - `2026-02-29` → false
  - `2026-04-31` → false
  - `2026-99-99` → false
  - `2028-02-29` → true
  - `2026-02-28` → true
- 공식 문서도 월별 일수와 윤년을 포함한 calendar-aware 검증을 명시한다.

## 스타일·문구 경계
- 현재 오류 CSS는 Discussion 전용 `.cp-discussion-validation-message`라 Vote에서 직접 재사용하면 도메인 누수다.
- `src/shared/assets/css/_cp-admin.css`에 공통 `.cp-validation-message`를 두고 네 사용처를 통일하는 것이 가장 작은 재사용 단위다.
- `--clr-error-500` token이 이미 존재한다.
- `recipe-i18n`이 가리키는 `src/assets/i18n`, `src/hooks/use-language.ts`는 현재 FSD source tree에 존재하지 않는다.
- 이번 섹션에서 레거시 i18n 인프라를 재도입하지 않고 기존 CP 화면의 한국어 문구 관례를 유지한다. i18n 복구는 별도 구조 작업이다.

## 추상화 판단
- 공용 hook/component/recipe는 추가하지 않는다.
- Zod `z.iso.date()`가 이미 명시적인 boundary primitive이므로 shared date helper를 감싸지 않는다.
- 상태와 부수효과는 기존 도메인 search/process hook이 계속 소유한다.
- 동일한 시각 표현만 공통 CSS class로 승격한다.

## Planner 실행
- 구성된 Planner는 외부 provider credit 부족으로 시작하지 못했다.
- 동일한 읽기 전용 Planner 계약을 독립 실행 경로로 수행해 범위와 검증 기준을 확정했다.

## 결론
- Vote parity만 추가하면 silent UX는 해결되지만 불가능한 달력 날짜가 DTO·상세 validator를 통과하는 근본 결함은 남는다.
- 최소 correctness-complete 범위는 실제 날짜 schema, production API parse boundary, Vote 목록 parity, Vote 상세 오류 UX, 공통 오류 class를 함께 적용하는 것이다.
