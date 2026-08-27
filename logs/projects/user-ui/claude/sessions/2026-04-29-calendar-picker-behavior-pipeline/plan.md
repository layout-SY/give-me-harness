# Plan

## Request Summary
- calendar-picker 의 free-range 모드에서 포커스 토글이 동작하지 않는 버그 해결.
- `useCalendarBehavior` 가 모든 mode 의 onSelectDate 를 합성해 반환하는데, calendar-picker 의 분기 조건이 "behaviors.onSelectDate 존재 여부"라서 default free-range 분기(setSelectType 토글 포함)가 영원히 도달 불가였음.

## Work Type
- refactor (버그 수정 + 추상화 정리)

## Scope
- `src/components/calendar-picker/types.ts` — onSelectDate 반환 타입 확장
- `src/components/calendar-picker/hook/behaviors/useCalendarBehavior.ts` — free-range 정책을 mode 분기 내에 정식 이전, `nextSelectType` 반환
- `src/components/calendar-picker/calendar-picker.tsx` — default 분기 삭제, behaviors 단일 경로
- `src/hooks/use-pub-sub/events.ts` — `behaviors` required 화

## Out of Scope
- 도메인 사용처(useFreeRangeBehavior / useWeekFromClickBehavior wrapper) 인터페이스 변경 없음
- maxRangeDays / validate 등 미사용 constraints 활성화 — 별도 후속 과제

## Sections
1. 분기 진단 및 대안 비교(안 1·2·3)
2. 안 2 채택 → calendar-picker 의 default 분기 제거까지 확장
3. 타입(`CalendarSelectResult`) 확장
4. `useCalendarBehavior` 에 free-range 정책 흡수
5. pubsub 페이로드 `behaviors` required 화
6. calendar-picker `handleDateClick` 단순화

## Required Agents
- generator (구현)
- watcher (게이트 검증)

## Required Skills
- coding-convention
- review-checklist

## Risks / Assumptions
- 가정: `open-calendar-picker` publish 진입점은 `useCalendarPicker.ts` 단일 (grep 으로 검증 완료)
- 리스크: 외부에서 직접 publish 하는 경로가 추가될 경우 behaviors 누락 시 런타임 에러 — 타입 required 로 컴파일 타임 차단

## Approval Request
사용자 승인 완료(2026-04-29).
