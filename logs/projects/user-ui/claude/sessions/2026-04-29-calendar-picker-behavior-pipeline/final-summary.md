# Final Summary

## What Changed
- `CalendarBehaviors.onSelectDate` 반환 타입을 `CalendarSelectResult` 로 확장. `nextSelectType?: "start" | "end"` 가 추가되어 정책이 다음 포커스를 직접 지정할 수 있다.
- `useCalendarBehavior` 의 `mode === "free-range"` 분기에서 `selectFreeRange` 결과에 토글된 `nextSelectType` 을 합성하여 반환. free-range 정책의 정식 거처가 됨.
- `calendar-picker.tsx` 의 `handleDateClick` 을 단일 경로로 단순화. 기존 default free-range 분기(L130~149) 와 디버그 `console.log` 제거. 정책 함수 직접 import 제거.
- `PubSubEvents["open-calendar-picker"].behaviors` 를 optional → required 로 좁힘.

## Why It Changed
- 기존 분기 조건이 "behaviors.onSelectDate 존재 여부" 였으나 `useCalendarBehavior` 가 모든 mode 의 onSelectDate 를 항상 합성해 반환 → free-range 모드에서 default 분기(setSelectType 토글 포함) 가 영원히 도달 불가하여 포커스 토글 동작이 누락되는 버그.
- 정책 디스패치 어휘(mode) 가 calendar-picker 까지 새지 않도록 하면서, free-range 의 토글 책임을 정책 측이 가져가는 형태로 추상화를 정리.

## Reused Assets
- `selectFreeRange`, `selectWeekFromClick` (`utils/date-range.ts`)
- `useDateRangeState`
- 도메인 wrapper `useFreeRangeBehavior`, `useWeekFromClickBehavior` (시그니처 변경 없음 → 사용처 무수정)

## Impacted Areas
- `src/components/calendar-picker/types.ts`
- `src/components/calendar-picker/hook/behaviors/useCalendarBehavior.ts`
- `src/components/calendar-picker/calendar-picker.tsx`
- `src/hooks/use-pub-sub/events.ts`
- 도메인 사용처(11개 파일): 인터페이스 변경 없음, 무수정 통과.

## Remaining Risks
- `maxRangeDays` / `validate` / `isDateHighlighted` 등 `CalendarBehaviors` 에 정의되어 있으나 calendar-picker 에서 활용되지 않는 슬롯이 남아 있음 — 후속 과제로 분리.
- 외부에서 직접 `pubsub.publish("open-calendar-picker", ...)` 를 호출하는 코드가 추후 추가되면 `behaviors` required 로 인해 컴파일 타임 차단됨(긍정적 리스크).

## Follow-up Suggestions
- `CalendarSelectResult` 에 `validate` 결과(에러 문자열) 를 합쳐 정책이 거부할 수 있는 경로를 도입 가능.
- `maxRangeDays` 를 free-range 정책에 흡수하여 클릭 시점에 강제 클램핑.
- week-from-click 모드도 `nextSelectType` 을 명시적으로 반환(예: `"start"`) 하도록 정리하여 "미반환 = 유지" 의 암묵 규약을 명시 규약으로 바꿀 수 있음.
- E2E 또는 단위 테스트 추가: free-range 토글 시퀀스 / week-from-click 7일 자동 채움.
