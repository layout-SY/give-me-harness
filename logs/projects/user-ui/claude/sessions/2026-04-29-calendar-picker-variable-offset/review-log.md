# Review Log

## Review Target
- 변경: calendar-picker "controls 일반 슬롯 도입" (variable-offset 기능)
- 검토일: 2026-04-29
- 세션: 2026-04-29-calendar-picker-variable-offset

## Result
- **fail**

---

## Checklist Review

### CP1. calendar-picker.tsx(L5)가 정책 어휘를 단 하나도 직접 참조하지 않는가?
- **pass**
- `calendar-picker.tsx` 전체에서 `offsetDays`, `weekOffsetDays`, `offset`, `week`, `range` 키워드 grep 결과 0건 (CSS 클래스 `calendar-in-range`, import 경로 `date-range` 제외).
- L5 레이어는 `ControlSpec.key` 값을 불투명하게 전달만 하며, 의미 해석 없음. pass.

### CP2. `ControlSpec.key` 값을 L5가 해석하지 않고 불투명하게 전달만 하는가?
- **pass**
- `calendar-picker.tsx`의 `handleControlChange(key, nextValue)` 는 key 를 그대로 `params[key]` 에 저장하고 `onControlsChange` 로 포워딩한다. 정책 해석은 `useWeekFromClickBehavior` 가 담당한다.

### CP3. `onSelectDate` 4번째 인자 `params` 추가가 기존 3-인자 사용처에 타입 오류를 발생시키는지?
- **pass** (단, 주의사항 존재)
- `CalendarBehaviors.onSelectDate` 시그니처의 4번째 인자는 `params?: ControlParams` (optional) 이므로 기존 3-인자 구현체(`useFreeRangeBehavior` → `useCalendarBehavior` 내부 `onSelectDate`)는 타입 오류 없음.
- `summarySection.tsx`의 `useWeekFromClickBehavior` 호출 시 `controls` 미전달 → L5 controls 미렌더. 의도치 않은 변경 없음.
- `yarn tsc --noEmit` 결과: calendar-picker 관련 신규 에러 0건. 기존 에러는 mock 데이터 및 무관 페이지(`shared.ts`, `dao-logs`, `pass-management` 등) 한정.

### CP4. `controls` 배열 참조 안정성 — `useWeekFromClickBehavior`의 `useMemo` deps 적절성
- **pass** (단, 주석 수준 경고)
- `presets` useMemo deps: `[presetsRaw?.join(",")]` — 배열 내용 기반 문자열 비교로 안정화. 단 `presetsRaw` 자체가 매 렌더 새 참조여도 내용이 같으면 재생성 없음. 설계 의도대로 동작.
- `controls` useMemo deps: `[controlsEnabled, currentOffset, presets, label]` — 필요 deps 모두 포함. pass.
- `onControlsChange` useCallback deps: `[]` — 내부에서 `setCurrentOffset` (안정적 setter), `selectWeekFromClick` (순수 함수), `OFFSET_KEY` (모듈 상수) 만 참조. deps 누락 없음. pass.

### CP5. 모달 닫힘 후 재오픈 시 offset이 도메인 wrapper의 `currentOffset`으로 올바르게 복원되는 구조인지
- **fail — 핵심 위반**
- `currentOffset` 의 `useState` 가 `useWeekFromClickBehavior` 내부에 위치한다 (L52). 이 훅은 `_id.modal.tsx` 컴포넌트 최상위에서 호출된다.
- 컴포넌트가 언마운트되지 않는 한 `currentOffset` state 는 모달 닫힘/재오픈 간 유지된다 → 이 부분은 정상.
- **그러나**: `controls` useMemo 의 `value: currentOffset` (L71) 은 `ControlSpec.value` 필드에 현재 offset 을 기록한다. `_handleOpen` 시 `calendar-picker.tsx` L80~83에서 `initialParams[spec.key] = spec.value` 로 초기화하므로, 재오픈 시 `params` 상태가 `currentOffset` 에서 파생된 `controls[0].value` 로 복원된다.
- 복원 경로: `currentOffset(hook state)` → `controls[0].value` → `_handleOpen initialParams` → `params state`. 경로가 간접적으로 연결되어 있어 기능 자체는 동작하나 **경로의 명시성이 낮다**. 이는 경고 수준.
- **그러나 더 심각한 문제**: `useCalendarBehavior` 내부 L55에서 `params?.offsetDays` 를 직접 읽는다. 이는 prim 레이어(`useCalendarBehavior`)가 `offsetDays` 라는 도메인 어휘를 직접 알고 있음을 의미한다 → CP1 통과(calendar-picker.tsx 한정) 이지만, **prim 훅 레이어 경계 위반**에 해당한다. 하단 CP8 참조.

### CP6. `onControlsChange`가 `current.startDate` 없을 때 `null` 반환하여 formState 변경하지 않는지
- **pass**
- `useWeekFromClickBehavior` L84: `if (!current.startDate) return null;` 확인.
- `calendar-picker.tsx` L152: `if (!result) return;` 로 null guard. formState 갱신 없음. 정상.

### CP7. `summarySection.tsx`(7일 고정 유지) 및 `useFreeRangeBehavior` 사용처에 의도치 않은 변경이 없는지
- **pass**
- `summarySection.tsx`: `useWeekFromClickBehavior({ initialRange: ... })` — `controls` 미전달, `weekOffsetDays` 미전달(기본 7). controls 슬롯 미렌더, 기존 동작 유지.
- `useFreeRangeBehavior`: `controls`/`onControlsChange` 미전달 → `useCalendarBehavior` 의 controls/onControlsChange 모두 undefined. 영향 없음.

### CP8. `yarn tsc --noEmit` 결과 calendar-picker 관련 신규 에러 0건
- **pass**
- tsc 에러 전량 `src/mock/handlers/shared.ts` (DTO 필드 누락) 및 무관 페이지. calendar-picker 관련 에러 0건.

---

## Violations

1. **[V1 — FAIL] `useCalendarBehavior` prim 레이어의 도메인 어휘 직접 참조**
   - 파일: `src/components/calendar-picker/hook/behaviors/useCalendarBehavior.ts` L55
   - 코드: `const offsetFromParams = params?.offsetDays;`
   - `useCalendarBehavior` 는 prim(원시) 레이어이므로 도메인 어휘(`offsetDays`)를 알아서는 안 된다.
   - plan.md CP1 게이트는 `calendar-picker.tsx`(L5) 기준이었으나, prim 레이어 경계 역시 동일 원칙이 적용된다.
   - 영향: 향후 다른 도메인 훅이 `offsetDays` 외 키를 params 로 전달할 때, prim 레이어가 오독하거나 우선순위 충돌이 발생할 수 있다. 현 단일 사용처에서는 동작하지만 확장 시 잠재적 버그 경로.

2. **[V2 — WARNING] `onControlsChange` useCallback의 빈 deps 배열**
   - 파일: `src/components/calendar-picker/hook/behaviors/useWeekFromClickBehavior.ts` L91
   - `useCallback(fn, [])` 이나 내부에서 `selectWeekFromClick`(외부 함수)을 참조한다. 현재 모듈 상수이므로 실질적 문제 없으나, 린트(react-hooks/exhaustive-deps) 경고 가능성. warning 수준.

3. **[V3 — WARNING] 모달 재오픈 시 offset 복원 경로의 명시성 부족**
   - `currentOffset` → `controls[].value` → `_handleOpen` initialParams 경로가 암묵적.
   - 코드 읽는 사람이 복원 흐름을 추적하기 위해 세 파일을 cross-reference 해야 한다.
   - 기능 정확성에는 문제 없으나 유지보수 부채.

---

## Required Fixes

1. **[필수] `useCalendarBehavior` L55의 `params?.offsetDays` 직접 참조 제거**
   - prim 레이어는 params 내용을 해석하지 않아야 한다.
   - 수정 방향: `onSelectDate` 에서 `params` 를 그대로 도메인 훅 측에 전달하고, 도메인 훅(`useWeekFromClickBehavior`) 이 `onSelectDate` 콜백을 직접 구현하거나, prim이 외부에서 주입된 `onSelectDate` 를 우선 사용하는 구조로 변경.
   - 예: `useCalendarBehavior` Options 에 `onSelectDate?: CalendarBehaviors["onSelectDate"]` 를 추가하고, 도메인 훅에서 params 해석 로직이 포함된 onSelectDate 를 직접 구성해 주입.

2. **[권장] `onControlsChange` useCallback deps 명시**
   - `[selectWeekFromClick]` 또는 eslint-disable-next-line 주석으로 의도 명시.

---

## Repeat Issue
- false

## Escalation
- none

---

## Summary
CP1(calendar-picker.tsx 정책 어휘 격리): pass. CP2(key 불투명 전달): pass. CP3(타입 오류): pass. CP4(useMemo deps): pass. CP5(재오픈 복원): 기능 동작하나 경로 암묵적. CP6(null guard): pass. CP7(기존 사용처 영향): pass. CP8(tsc 0건): pass. **V1 위반: prim 레이어(`useCalendarBehavior`)가 `params?.offsetDays` 도메인 어휘를 직접 해석 — 레이어 경계 위반. 필수 수정 필요.**

판정: **fail**

---

## Re-review (round 2)

- 검토일: 2026-04-29
- 대상 커밋: V2 재작성 — prim 레이어 경계 강화 (mode 디스패치 제거, onSelectDate 도메인 훅 주입)

### CP1 (V1 해소). useCalendarBehavior가 정책 어휘를 직접 참조하지 않는가?
- **pass**
- grep 결과: `useCalendarBehavior.ts` 전체에서 `offsetDays`, `selectFreeRange`, `selectWeekFromClick`, `mode`, `params.*키` 실행 코드 0건.
- 주석 내 언급(L8-9)은 "이 훅이 하지 않는 것"을 명시하는 정책 어휘 무지 원칙 서술이므로 위반 아님.
- V1 이슈 완전 해소. **이전 fail 사유 제거됨.**

### CP2. useFreeRangeBehavior — onSelectDate 자체 합성
- **pass**
- `selectFreeRange` 호출 및 `nextSelectType` 토글을 `useCallback` 내에서 직접 구성 후 `useCalendarBehavior` 에 주입.
- prim 레이어에 정책 함수 없음.

### CP3. useWeekFromClickBehavior — onSelectDate 자체 합성 및 offsetRef 패턴
- **pass**
- `onSelectDate = useCallback(..., [])` — deps 빈 배열이지만 내부에서 `offsetRef.current` 를 읽어 항상 최신 `currentOffset` 접근.
- `offsetRef.current = currentOffset` 은 렌더마다 동기화(L60). stale closure 위험 없음.
- `OFFSET_KEY("offsetDays")` 해석은 이 도메인 훅 내부(L86-87)에서만 발생. prim 무지 원칙 충족.

### CP4. onControlsChange 의 deps — V2 이전 경고 재확인
- **pass (warning 유지)**
- `onControlsChange = useCallback(fn, [])` — 내부에서 `setCurrentOffset`(stable setter), `OFFSET_KEY`(모듈 상수), `selectWeekFromClick`(순수 함수 import) 만 참조.
- 실질적 stale closure 없음. 린트 경고 가능성은 유지되나 기능 정확성 문제 없음.
- 이전 V2 warning 수준 동일 — 필수 수정 사항 아님.

### CP5. useFreeRangeBehavior 사용처 인터페이스 변경 없음
- **pass**
- 7개 파일(sales, usage/calls, usage/soria, usage/item, users/suspend, events/attendance/*, events/roulette/*) 전부 `useFreeRangeBehavior({ disablePast, initialRange? })` 형태로 호출.
- Options 타입 변경 없음. 영향 0건.

### CP6. useWeekFromClickBehavior 사용처 — summarySection / create modal
- **pass**
- `summarySection.tsx`: `controls` 미전달 → `controlsEnabled=false` → `controls=undefined` → prim에 controls 미전달 → 표시 계층 controls 미렌더. 기존 7일 고정 동작 유지.
- `create/_id.modal.tsx`: `controls: true` 전달 → 프리셋 칩 활성화. 의도대로 동작.
- Options 타입은 superset(추가만) — 기존 호출 오류 없음.

### CP7. tsc --noEmit calendar-picker 신규 에러
- **pass**
- `tsc --noEmit` 실행 결과 calendar-picker 관련 신규 에러 0건. 기존 무관 에러(shared.ts 등) 만 존재.

---

## Violations (round 2)

1. **[V2 — WARNING, 이월] `onControlsChange` useCallback deps 빈 배열**
   - 실질적 stale closure 없음. warning 수준 유지. 필수 수정 아님.

2. **[V3 — WARNING, 이월] 모달 재오픈 offset 복원 경로 암묵성**
   - `currentOffset → controls[].value → _handleOpen initialParams` 경로 간접적. 기능 정확성 문제 없음.

---

## Required Fixes (round 2)

없음. V1 필수 수정 사항 해소 완료. warning 2건은 기능 정확성과 무관하며 필수 수정 범위 아님.

---

## Repeat Issue
- false

## Escalation
- none

---

## Summary (round 2)
V1(prim 레이어 offsetDays 직접 참조): 완전 해소. V2/V3 warning 이월이나 필수 수정 아님. tsc 신규 에러 0건. 사용처 인터페이스 변경 없음.

판정: **pass**
