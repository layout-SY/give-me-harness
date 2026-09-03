# Exploration

## Target Paths
- src/components/calendar-picker/**
- src/hooks/use-pub-sub/events.ts
- src/pages/**/*.tsx (도메인 사용처)

## Existing Reusable Assets Found
- Found: `selectFreeRange`, `selectWeekFromClick` (`src/components/calendar-picker/utils/date-range.ts`)
- Suggested Reuse: 그대로 재사용. `useCalendarBehavior` 의 mode 분기에서 호출.
- Reason: 순수 함수 + 단일 책임. React 의존 없음. 검증된 동작.

- Found: `useDateRangeState` (`src/components/calendar-picker/hook/useDateRangeState.ts`)
- Suggested Reuse: 그대로 재사용. SELECT_TYPE 토글 책임은 calendar-picker 에 그대로 둠(외부 정책 결과를 받아 setSelectType 호출).
- Reason: 내부 폼 상태 분리가 이미 깔끔.

- Found: 도메인 wrapper `useFreeRangeBehavior`, `useWeekFromClickBehavior`
- Suggested Reuse: 인터페이스 변경 없음. `useCalendarBehavior` 시그니처를 유지하므로 wrapper 들도 무수정.
- Reason: 이번 변경은 prim 훅의 반환 형 확장 + calendar-picker 분기 정리에 한정.

## Assets Not Suitable for Reuse
- Asset: calendar-picker.tsx 의 default free-range 분기(L130~149)
- Why not suitable: 정책 단일 출처 원칙 위배(중복). free-range 가 `useCalendarBehavior` 로 정식 이전된 이상 표시 컴포넌트에 잔존할 이유 없음 → 삭제.

## New Asset Necessity
- Needed: 신규 자산 없음. 기존 타입(`CalendarBehaviors`) 의 반환 형만 `CalendarSelectResult` 로 확장.
- Why: 추상화 누수 없이 포커스 토글 책임만 정책 측으로 이동시키기 위해 최소한의 타입 확장으로 충분.
