# Implementation Log

## Task Summary
- calendar-picker 의 정책 디스패치를 `useCalendarBehavior` 단일 출처로 이전.
- `onSelectDate` 반환 타입에 `nextSelectType?` 을 추가하여 포커스 토글 책임을 정책 측이 가져가도록 변경.
- calendar-picker 는 정책 어휘를 모르는 표시 전용 컴포넌트로 정리.

## Reused Assets
- `selectFreeRange`, `selectWeekFromClick` (`utils/date-range.ts`) — 변경 없이 재사용.
- `useDateRangeState` — 변경 없음.
- 도메인 wrapper (`useFreeRangeBehavior`, `useWeekFromClickBehavior`) — 호출 시그니처 변경 없음.

## New Files / Updated Files
- Updated: `src/components/calendar-picker/types.ts`
  - `CalendarSelectType`, `CalendarSelectResult` 추가.
  - `CalendarBehaviors.onSelectDate` 반환을 `CalendarSelectResult` 로 확장 (`nextSelectType?` 포함).
- Updated: `src/components/calendar-picker/hook/behaviors/useCalendarBehavior.ts`
  - free-range 분기에서 `selectFreeRange` 결과에 `nextSelectType` 토글값을 합성하여 반환.
  - week-from-click 분기는 `nextSelectType` 미반환(기존 동작 유지).
  - 헤더 주석 갱신: 정책 단일 출처임을 명시.
- Updated: `src/components/calendar-picker/calendar-picker.tsx`
  - `handleDateClick` 의 우선순위 1·2 이중 분기 제거 → behaviors 단일 경로.
  - `next.nextSelectType` 존재 시 `setSelectType` 호출.
  - `selectFreeRange` import 삭제 (calendar-picker 가 정책 함수를 직접 부르지 않음).
  - 디버그용 `console.log` 제거.
  - `behaviors` 미주입 시 클릭 무시(`if (!behaviors) return`).
- Updated: `src/hooks/use-pub-sub/events.ts`
  - `open-calendar-picker.behaviors` 를 optional → required 로 좁힘.

## Key Logic
- 디스패치 모델
  - 도메인 → `useCalendarBehavior({ mode, ... })` → `behaviors.onSelectDate` 합성
  - `DateRangeField` → `useCalendarPicker.open()` → pubsub publish (behaviors 동봉)
  - `calendar-picker` → behaviors 만 호출 (`mode` 어휘 모름)
- free-range 토글 규칙: `selectType === "start"` → `nextSelectType: "end"`, 반대도 동일.
- week-from-click: `nextSelectType` 미반환 → calendar-picker 는 현재 포커스 유지.

## Validation / Request Handling
- 직접 publish 경로 grep: `open-calendar-picker` publish 는 `useCalendarPicker.ts:26` 단일 — required 화 안전.
- `yarn tsc --noEmit` 결과: calendar-picker 변경 관련 타입 에러 0건. 남은 에러는 모두 기존부터 존재하던 별개 이슈(`mock/handlers/shared.ts`, `dao-logs`, `pass-management`, `proposal-audit`, `quest-reward`).

## Risks
- behaviors 가 컴파일 타임 required 가 되었으므로 외부에서 직접 pubsub.publish 호출 시 타입 에러로 즉시 드러남 — 런타임 silent failure 차단.
- `maxRangeDays` 등 constraints 는 여전히 미사용 — 추후 free-range 정책에 흡수 예정.

## Handoff Note
- Ready for watcher review
- 검증 포인트: free-range 모드의 포커스 토글, week-from-click 모드의 자동 7일 채움, behaviors 미주입 시 무동작.
