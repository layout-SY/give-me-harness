# Implementation Log — calendar-picker 추상화 재설계

> 일자: 2026-04-29
> 기반 문서: plan.md / evaluation-log.md / architecture-discussion.md
> 결과: 6 Phase 모두 완료, watcher 게이트 통과

---

## Phase 1 — 즉시 버그 수정 (P1 + P2)

**담당:** refactorer
**Watcher:** PASS

### 변경 파일

- `src/components/calendar-picker/calendar-picker.tsx`
  - `_handleClose` L102: `setCurrentYear(new Date().getMonth())` → `setCurrentMonth(new Date().getMonth())` (Year/Month setter 버그)
  - `handleConfirm` 끝에 `_handleClose()` 호출 추가 (자동 close)
- 사용처 11개 콜백에서 `pubsub.publish("close-calendar-picker")` 제거 (총 11건 제거)
  - DAO 2 (create/detail), events 4 (attendance create/_id, roulette create/_id), usage/sales 4, suspend.popup 1

### 검증
- `_handleClose` setCurrentYear 중복 호출 0건
- 사용처 close publish 0건 (calendar-picker.tsx 구독 정의 + events.ts 타입 정의만 잔존)
- lint/tsc 신규 오류 0건

---

## Phase 2 — L1 순수 함수 + L2 상태 훅 + Behaviors 슬롯 도입

**담당:** refactorer
**Watcher:** PASS

### 신규 파일
- `src/components/calendar-picker/types.ts` — `DateRange`, `CalendarBehaviors` 타입
- `src/components/calendar-picker/utils/date-range.ts` — `getNormalizedDateValue`, `selectFreeRange`, `selectWeekFromClick` 순수 함수
- `src/components/calendar-picker/hook/useDateRangeState.ts` — start/end/year/month/selectType 통합 상태 훅

### 수정 파일
- `src/components/calendar-picker/calendar-picker.tsx`
  - 인라인 enum/타입/상태 → `useDateRangeState` 위임
  - `getNormalizedDateValue` 인라인 → utils 호출
  - `handleDateClick` 우선순위: `behaviors.onSelectDate` → `selectWeekFromClick`(legacy) → `selectFreeRange`(default)
  - `_handleOpen`에 `behaviors` / `initialRange` 수신 슬롯 추가
- `src/hooks/use-pub-sub/events.ts` — `open-calendar-picker` payload에 `behaviors?: CalendarBehaviors` optional 필드 추가 (backward compatible)

### 검증
- 단방향 import 그래프: `calendar-picker.tsx` → `useDateRangeState` + `utils/date-range` + `types`
- payload backward compatible — 사용처 11개 무수정
- lint/tsc 신규 오류 0건

---

## Phase 3 — L4 useCalendarPicker + 도메인 prim 훅

**담당:** generator + refactorer (deprecated)
**Watcher:** V4 (free-range selectType 결함) FAIL → 픽스 후 PASS

### 신규 파일
- `src/components/calendar-picker/hook/useCalendarPicker.ts` — pubsub 이름 캡슐화 (open/close)
- `src/components/calendar-picker/hook/behaviors/useCalendarBehavior.ts` — prim 훅 (mode + constraints)
- `src/components/calendar-picker/hook/behaviors/useWeekFromClickBehavior.ts` — DAO 도메인 래퍼
- `src/components/calendar-picker/hook/behaviors/useFreeRangeBehavior.ts` — 이벤트/검색 필터 도메인 래퍼

### 수정 파일
- `src/components/calendar-picker/hook/useCalendar.ts` — JSDoc `@deprecated` 태그 추가 (본문 무수정)
- `src/components/calendar-picker/index.ts` — `useCalendarPicker`, `useWeekFromClickBehavior`, `useFreeRangeBehavior`, `DateRange`, `CalendarBehaviors` export

### V4 결함 픽스 (선택 토글 결함)
초기 `useCalendarBehavior`가 free-range에서 `currentSelectType` 포커스 토글을 반영하지 못해 첫 클릭 시 endDate부터 채워지는 UX 버그 발생.

해결: `CalendarBehaviors.onSelectDate` 시그니처에 세 번째 인자 `selectType: "start" | "end"` 추가. 컴포넌트가 보유한 `currentSelectType`을 변환해 전달. `useCalendarBehavior` 내부에서 받은 selectType을 그대로 `selectFreeRange`에 위임.

수정 파일: `types.ts`, `useCalendarBehavior.ts`, `calendar-picker.tsx`

---

## Phase 4 — L5 DateRangeField 표현 컴포넌트

**담당:** generator
**Watcher:** PASS (검증 생략, 단독 빌드 통과 확인)

### 신규 파일
- `src/components/calendar-picker/DateRangeField.tsx`
  - props: `value`, `onChange`, `behaviors`, `disabled`, `startName`, `endName`, `placeholder`, `triggerIcon`, `triggerClassName`
  - 내부: `useCalendarPicker` 호출 + TextInput × 2 + separator + IconButton
  - Slot 주입(약): `triggerIcon`으로 트리거 아이콘 교체 가능
- `src/components/calendar-picker/DateRangeField.css` — 자체 flex 레이아웃

### 수정 파일
- `src/components/calendar-picker/index.ts` — `DateRangeField` export 추가

---

## Phase 5 — 사용처 11개 마이그레이션

**담당:** refactorer (4 그룹)
**Watcher:** PASS

### 그룹 A — DAO 2 (week-from-click)

- `src/pages/dao/proposal-manage/create/_id.modal.tsx`
- `src/pages/dao/proposal-manage/detail/_id.modal.tsx`
- `src/pages/dao/proposal-manage/detail/components/sections/summarySection.tsx`

전환: `useCalendar` 제거 → `useWeekFromClickBehavior` + `<DateRangeField>`. detail의 `onOpenCalendar` prop drilling 제거 → SummarySection 내부에 DateRangeField 직접 배치. 보일러플레이트 ≈ 42라인 감소.

### 그룹 B — Events 4 (free-range)

- `src/pages/manage/events/attendance/{create,_id}/modules/info.module.tsx`
- `src/pages/manage/events/roulette/{create,_id}/modules/info.module.tsx`

전환: 인라인 pubsub 제거 → `useFreeRangeBehavior` + `<DateRangeField>`. 도메인 로직 보존:
- create의 id/code 파생(`900yyyyMM`/`901yyyyMM`, `yyyy_MM_ATTENDANCE`/`yyyy_MM_ROULETTE`)은 onChange 콜백 내 유지
- ISO 변환(`T00:00:00`, `T23:59:59`)은 onChange 콜백 내 유지
- 도메인 이벤트 publish(`read-attendance-event`, `read-roulette-event`) 그대로 유지

### 그룹 C — Usage/Sales 4 (free-range, 검색 필터)

- `src/pages/manage/sales/index.tsx`
- `src/pages/manage/usage/{calls,soria,item}/index.tsx`

전환: 인라인 pubsub 제거 → `useFreeRangeBehavior` + `<DateRangeField>`. `setRequestSearch(true)` 검색 트리거를 `handleDateSelect` 함수로 보존하고 onChange로 직접 전달.

### 그룹 D — Suspend 1 (single-date 패턴, 탈출구)

- `src/pages/manage/users/suspend.popup.tsx`

전환: `<DateRangeField>` 미사용. UI 레이아웃이 "오늘(시작) | 복구일(끝)" 두 컬럼 분리 구조라 plan R5 탈출구 패턴 적용. `useCalendarPicker` 직접 호출 + `useFreeRangeBehavior` 주입. R3 결정에 따라 `useSingleDateBehavior` 신설하지 않음.

도메인 검증 보존: `today.getTime() > _endDate.getTime()` 검증 + `restoredDate` 저장.

### 사후 grep 결과
- `"open-calendar-picker"` 사용처 코드: 0건
- `"close-calendar-picker"` 사용처 코드: 0건
- `useCalendar` import 사용처 코드: 0건

---

## Phase 6 — Deprecated 자산 정리

**담당:** refactorer

### 삭제
- `src/components/calendar-picker/hook/useCalendar.ts`

### 수정
- `src/hooks/use-pub-sub/events.ts` — `autoSelectOneWeek?: boolean` 필드 제거
- `src/components/calendar-picker/calendar-picker.tsx` — `autoSelectOneWeek` 수신/저장 코드 제거, fallback 분기 단순화 (behaviors → free-range만 남음), `selectWeekFromClick` import 제거
- `src/components/calendar-picker/hook/useDateRangeState.ts` — `isAutoSelectOneWeek` 필드/액션 제거
- `src/components/calendar-picker/hook/useCalendarPicker.ts` — payload의 `autoSelectOneWeek: false` 호환 라인 제거
- `selectWeekFromClick` 함수는 `useWeekFromClickBehavior`에서 사용 중이므로 보존

### 사후 grep
- `useCalendar` (useCalendarPicker/useCalendarBehavior 제외): 0건
- `autoSelectOneWeek`: 0건
- `isAutoSelectOneWeek`: 0건
- lint/tsc 신규 오류 0건

---

## 최종 디렉토리 구조

```
src/components/calendar-picker/
├── DateRangeField.tsx        ← L5 표현 컴포넌트
├── DateRangeField.css
├── calendar-picker.tsx       ← L3 (메커니즘만, behaviors 받아 실행)
├── calendar-picker.css
├── types.ts                  ← DateRange, CalendarBehaviors
├── index.ts                  ← 배럴 export
├── hook/
│   ├── useCalendarPicker.ts  ← L4 (pubsub 캡슐화)
│   ├── useDateRangeState.ts  ← L2 (상태)
│   └── behaviors/
│       ├── useCalendarBehavior.ts       ← prim
│       ├── useWeekFromClickBehavior.ts  ← 도메인 래퍼 (DAO)
│       └── useFreeRangeBehavior.ts      ← 도메인 래퍼 (events/search)
└── utils/
    └── date-range.ts         ← L1 (순수 함수)
```

## 회귀 검증 결과 (전 Phase 누적)

- `yarn lint`: 신규 오류 0건 (pre-existing 1건 `footerSection.tsx historyIcon` 무관)
- `npx tsc --noEmit`: 신규 오류 0건 (pre-existing baseline 동일)
- 사용처 11개 외부 동작 보존 확인 (도메인 로직 / 검색 트리거 / 검증 / id 파생 모두 보존)
