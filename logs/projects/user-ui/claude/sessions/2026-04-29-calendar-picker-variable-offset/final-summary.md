# Final Summary

## What Changed
- `CalendarBehaviors` 에 범용 파라미터 슬롯(`controls`, `onControlsChange`) 추가, `onSelectDate` 4번째 인자 `params?` 도입.
- `useCalendarBehavior`(prim) 에서 mode 디스패치 및 정책 함수 호출 완전 제거. 도메인 훅이 `onSelectDate` 를 직접 합성하여 prim 에 주입하는 구조로 전환.
- `useFreeRangeBehavior`, `useWeekFromClickBehavior` 가 자체 `onSelectDate` 를 `useCallback` 으로 합성.
- `useWeekFromClickBehavior` 에 `controls` 옵션 추가 — 모달 내부에서 offset 값을 number input 으로 직접 입력. `currentOffset` state + `offsetRef` 로 모달 재오픈 시 복원.
- `calendar-picker.tsx` 에 `params` state 추가, controls 슬롯 렌더(`ControlField` 로컬 컴포넌트 — number / preset-chips 분기), 4번째 인자로 params 전달.
- `proposal-manage/create/_id.modal.tsx` 가 `controls: true` 활성화하여 새 기능 사용.

## Why It Changed
- 기존 7일 고정 offset 을 사용자가 모달 내부에서 직접 변경 가능하도록 하는 기능 요구.
- "모달 닫기 → 외부 변경 → 다시 열기" 마찰 제거를 위해 모달 내부 컨트롤(Option A) 채택.
- 추상화 누수 회피를 위해 prim/L5 가 정책 어휘를 모르는 일반 슬롯 패턴 도입.
- watcher 1차 검토에서 prim 이 `params.offsetDays` 를 직접 해석하는 레이어 격리 위반이 발견되어 prim 의 mode 디스패치 자체를 제거하는 더 깊은 리팩터링으로 확장.

## Reused Assets
- `selectFreeRange`, `selectWeekFromClick` (`utils/date-range.ts`)
- `useDateRangeState`
- `useCalendarPicker`, `DateRangeField`, pubsub 채널 — 변경 없음
- 도메인 사용처 11개 — 인터페이스 변경 없음

## Impacted Areas
- `src/components/calendar-picker/types.ts`
- `src/components/calendar-picker/hook/behaviors/useCalendarBehavior.ts` (rewrite)
- `src/components/calendar-picker/hook/behaviors/useFreeRangeBehavior.ts`
- `src/components/calendar-picker/hook/behaviors/useWeekFromClickBehavior.ts`
- `src/components/calendar-picker/calendar-picker.tsx`
- `src/components/calendar-picker/calendar-picker.css`
- `src/components/calendar-picker/index.ts`
- `src/pages/dao/proposal-manage/create/_id.modal.tsx`

## Architecture Model (요약)

`CalendarBehaviors`(타입) = 계약. 도메인 훅 = 구현. prim = 조립. L5 = 계약 소비자. 사용처 = 카탈로그 소비자. 정책 어휘는 도메인 훅 안에서 태어나 죽고, prim/L5 는 무지하다. 상세는 `architecture.md` 참조.

## Remaining Risks
- input 값 0 / 음수 / 매우 큰 값 강제 클램프 없음 (HTML `min` attribute 만 의존). 향후 `validate` 정책 도입 시 처리.
- `currentOffset` 은 도메인 wrapper 인스턴스 lifetime 동안만 유지 — 페이지 언마운트 시 휘발(의도된 동작).
- `useMemo` deps 안정화 책임이 도메인 훅 측에 있음. 새 도메인 훅 추가 시 useCallback/useMemo 누락 시 prim 의 behaviors 재생성 빈발 가능.

## Follow-up Suggestions
- `validate` 슬롯에 min/max 강제 클램프 정책 추가 (input 값 1 미만 또는 weekOffsetDays * 365 같은 비정상 입력 차단).
- `kind` 확장: `"toggle"`, `"select"` 등 다른 컨트롤 형태 추가 시 `ControlField` 분기 보강.
- `useFreeRangeBehavior` 에도 controls 활용 — `maxRangeDays` 를 controls 로 노출하여 모달 내 즉시 조정 가능.
- detail/summarySection 등 7일 고정이 의도인 사용처는 `controls` 미전달로 명시적 정책 표명. 변경 없음.
- 단위 테스트: free-range 토글 시퀀스 / week-from-click input 변경 시 재계산 / 모달 재오픈 시 offset 복원.
