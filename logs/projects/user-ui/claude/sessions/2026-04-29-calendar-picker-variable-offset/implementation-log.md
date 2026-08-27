# Implementation Log

## Task Summary
- calendar-picker 의 week-from-click 모드에서 사용자가 모달 내부에서 offset(기간 일수)을 직접 입력할 수 있도록 확장.
- 추상화 누수 회피를 위해 `CalendarBehaviors` 에 범용 `controls` 슬롯 도입.
- watcher 1차 검토에서 prim 레이어 격리 위반(prim 이 `params.offsetDays` 직접 해석)이 발견되어 prim 의 mode 디스패치 자체를 제거하고 도메인 훅이 onSelectDate 를 직접 합성하는 구조로 리팩터링(round 2 PASS).

## Reused Assets
- `selectFreeRange`, `selectWeekFromClick` (`utils/date-range.ts`)
- `useDateRangeState`
- `useCalendarPicker`(L4) / `DateRangeField`(L5 props 컴포넌트) / pubsub 채널 — 변경 없음
- 도메인 wrapper 11개 사용처 — 인터페이스 변경 없음(superset 확장만)

## New Files / Updated Files

### Updated: `src/components/calendar-picker/types.ts`
- `ControlSpec` 타입 추가 — 렌더 명세(`kind: "number" | "preset-chips"`, label, value, min/max/presets)
- `ControlParams = Record<string, number>` 타입 추가
- `CalendarBehaviors` 확장:
  - `controls?: ControlSpec[]`
  - `onControlsChange?: (current, params) => CalendarSelectResult | null`
  - `onSelectDate` 4번째 인자 `params?: ControlParams` (optional, 하위 호환)

### Updated (rewrite): `src/components/calendar-picker/hook/behaviors/useCalendarBehavior.ts`
- mode 디스패치 제거. `selectFreeRange` / `selectWeekFromClick` import 제거.
- prim 레이어 책임 축소: `disablePast → isDateDisabled` 변환 + 메타 슬롯(initialRange / onSelectDate / controls / onControlsChange) 묶기.
- `onSelectDate` 를 도메인 훅이 주입하는 필수 옵션으로 변경.
- 정책 어휘 무지 원칙을 헤더 주석에 명시.

### Updated: `src/components/calendar-picker/hook/behaviors/useFreeRangeBehavior.ts`
- 자체 `onSelectDate` 를 `useCallback` 으로 합성: `selectFreeRange` 호출 + `nextSelectType` 토글.
- 합성한 onSelectDate 를 prim 에 주입.

### Updated: `src/components/calendar-picker/hook/behaviors/useWeekFromClickBehavior.ts`
- `currentOffset` useState + `offsetRef` (stale closure 방지).
- `controls` 옵션: `boolean | { min?, max?, label? }`. true 시 `kind: "number"` 컨트롤 노출(기본 min=1, label="기간(일)").
  - 초기 구현은 `preset-chips` + `presets` 였으나 사용자 요청으로 `number` 입력으로 전환.
- 자체 `onSelectDate` 합성: `params?.[OFFSET_KEY]` 우선, 폴백은 `offsetRef.current`. `OFFSET_KEY` 해석은 이 도메인 훅 내부에서만 발생.
- `onControlsChange` 구현: 새 offset 으로 currentOffset 업데이트 + startDate 가 있으면 `selectWeekFromClick` 으로 end 재계산.

### Updated: `src/components/calendar-picker/calendar-picker.tsx`
- `params: ControlParams` state 추가.
- `_handleOpen`: `behaviors.controls` 로부터 초기 params 시드.
- `_handleClose`: params 리셋.
- `handleDateClick`: `behaviors.onSelectDate(date, current, selectType, params)` — 4번째 인자 전달.
- `handleControlChange`: 새 params 계산 + setParams + `behaviors.onControlsChange?.()` 호출 → 결과 non-null 이면 formState 갱신.
- `renderControls()`: `behaviors.controls` 가 없으면 null. 있으면 sub-header 와 main-header 사이 슬롯에 렌더.
- `ControlField` 로컬 컴포넌트: `kind === "preset-chips"` (칩 버튼) / `kind === "number"` (input) 분기.
- 정책 어휘(`offsetDays`, `week`, `range`) 직접 참조 0건.

### Updated: `src/components/calendar-picker/calendar-picker.css`
- `.calendar-controls`, `.calendar-control-field`, `.calendar-control-label`, `.calendar-control-chips`, `.calendar-control-chip(.active)`, `.calendar-control-number` 스타일 추가.

### Updated: `src/components/calendar-picker/index.ts`
- `ControlSpec`, `ControlParams` re-export 추가.

### Updated: `src/pages/dao/proposal-manage/create/_id.modal.tsx`
- `useWeekFromClickBehavior({ ..., weekOffsetDays: 7, controls: true })` 로 controls 활성화.

## Key Logic

### 레이어 격리
- L5 calendar-picker: `ControlSpec.kind` 만 해석. `key` 의미 무지. `params` 를 불투명 맵으로 정책에 전달.
- L3 prim(useCalendarBehavior): 정책 함수 호출 0건. mode 디스패치 0건. `onSelectDate` 를 도메인 훅이 주입.
- L4 도메인 훅: 정책 어휘(`OFFSET_KEY`) 와 정책 함수(`selectWeekFromClick`) 호출 모두 이 계층에 캡슐화.

### 모달 재오픈 시 offset 복원
- `currentOffset` state 가 도메인 wrapper 의 useState 에 보존됨.
- 사용자가 칩/입력으로 변경 → `onControlsChange` 가 `setCurrentOffset` 호출 → 다음 렌더에 `controls[0].value = currentOffset` 갱신.
- 모달 재오픈 시 `_handleOpen` 이 `behaviors.controls[0].value` 로 params 시드 → 마지막 값 복원.

### Stale closure 방지
- `useWeekFromClickBehavior` 의 `onSelectDate` 는 `useCallback(..., [])` 로 안정화.
- `currentOffset` 직접 참조 시 stale closure 위험 → `offsetRef.current` 로 항상 최신값 읽음.
- `params?.[OFFSET_KEY]` 우선 → 사용자가 input 으로 변경한 즉시 클릭에도 반영.

## Validation / Request Handling
- `yarn tsc --noEmit` 결과: calendar-picker 관련 신규 에러 0건. (잔여 에러는 모두 기존 별개 이슈 — `mock/handlers/shared.ts`, `dao-logs`, `pass-management`, `proposal-audit`, `quest-reward`)
- L5 정책 어휘 grep 검증: `offsetDays|weekOffsetDays|\\boffset\\b|\\bweek\\b|\\brange\\b` → 매치는 module path 와 CSS 클래스명 뿐.
- watcher round 2: PASS. V1(prim 레이어 격리 위반) 해소. V2/V3 은 warning(필수 수정 아님).

## Risks
- `controls` 활성화한 도메인은 currentOffset 이 도메인 wrapper 인스턴스 lifetime 동안 유지됨. 페이지 언마운트 시 휘발 — 의도된 동작.
- 사용자가 input 에 0 또는 음수 입력 가능. `min: 1` 기본값으로 일부 방어하나 강제 클램프는 없음 → 향후 `validate` 정책 도입 시 처리.
- prim 의 `useMemo` deps 에 `controls`, `onControlsChange` 가 추가됨. 도메인 훅 측 useMemo/useCallback 안정화 책임 명시(헤더 주석).

## Handoff Note
- Ready for browser verification.
- 핵심 시나리오: 7일 input → 5/1 클릭 → 5/1~5/7 자동 채움 → input 21 변경 → 즉시 5/1~5/21 재계산.
