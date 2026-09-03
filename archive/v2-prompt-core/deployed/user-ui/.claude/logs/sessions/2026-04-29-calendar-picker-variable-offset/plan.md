# Plan

## Request Summary

`calendar-picker`의 `week-from-click` 모드에서 현재 N일 고정인 `offsetDays`를
사용자가 **캘린더 모달 내부에서 실시간 변경**할 수 있도록 한다.

핵심 시나리오:
"사용자가 기간 14일 설정 → 캘린더 열고 5/1 클릭(자동 5/1~5/14 채움)
→ '21일이었네' → 모달 안 칩 21 클릭 → 즉시 5/1~5/21 재계산 → 닫기 없이 완료"

이 흐름을 달성하기 위해 **Option A(controls 내부 슬롯)** 를 채택한다.
L5(`calendar-picker.tsx`)가 `offset`, `weekOffsetDays` 등 정책 어휘를 직접 알지 못하도록
`CalendarBehaviors`에 **범용 `controls` 슬롯**을 도입하여 추상화 누수를 방지한다.

---

## Option B → A 변경 사유 + 추상화 누수 회피 메커니즘

### 변경 사유

| 비교 항목 | Option B (외부 컨트롤) | Option A (내부 슬롯) |
|---|---|---|
| 핵심 시나리오 지원 | **불가** — 모달 열린 동안 offset 변경 불가. "닫기 → 외부 변경 → 다시 열기" 3단계 마찰 발생 | **가능** — 모달 내부에서 controls 변경 → 즉시 재계산 |
| L5 정책 무지 원칙 | 유지 | **유지** — controls 슬롯은 알지만 offset/week 어휘는 모름 |
| pubsub payload 변경 | 불필요 | `CalendarBehaviors`에 `controls` 추가 (payload 구조 확장, 하위 호환) |
| 도메인 offset 상태 위치 | 도메인 wrapper (useState in wrapper) | **도메인 wrapper** — 모달 닫힘 후에도 lastParams 보존 |

**결론**: 핵심 시나리오가 공식 요구사항으로 인정됨. Option B는 이 시나리오를 구조적으로 지원할 수 없다. Option A 채택.

### 추상화 누수 회피 메커니즘

`calendar-picker.tsx`(L5)가 `offsetDays`, `weekOffsetDays` 등 정책 어휘를 알면 안 된다.
이를 위해 **"일반 파라미터 슬롯(ControlSpec[])"** 패턴을 도입한다.

- `CalendarBehaviors.controls?: ControlSpec[]` — 렌더 명세(무엇을 어떻게 보여줄지)
- `CalendarBehaviors.onControlsChange?(current, params) => CalendarSelectResult | null` — 재계산 정책
- `calendar-picker.tsx`는 controls 배열을 순회하여 UI를 렌더하고, 사용자 변경 시 내부 `params` state를 갱신한 후 `onControlsChange`를 호출한다.
- `onSelectDate` 시그니처 확장: `(date, current, selectType, params)` — 정책 측이 `params.offsetDays` 등을 꺼내 쓴다.
- calendar-picker는 `"offsetDays"` 키의 의미를 모른다. `{ key, value }` 쌍의 params 맵만 전달한다.

---

## Work Type

feature

---

## Scope

### 변경 대상 파일 (In)

| 레이어 | 파일 | 변경 내용 |
|---|---|---|
| 타입 | `src/components/calendar-picker/types.ts` | `ControlSpec` 타입 추가, `CalendarBehaviors`에 `controls?`, `onControlsChange?`, `onSelectDate` 시그니처 확장(4번째 인자 `params`) |
| prim 훅 | `src/components/calendar-picker/hook/behaviors/useCalendarBehavior.ts` | `controls` 옵션 수신 후 `CalendarBehaviors.controls`로 전달, `onSelectDate` 콜백에 `params` 인자 포워딩 |
| domain 훅 | `src/components/calendar-picker/hook/behaviors/useWeekFromClickBehavior.ts` | `controls` 배열 노출(`preset-chips`, key=`offsetDays`), `onSelectDate`에서 `params.offsetDays` 사용, `onControlsChange` 구현 |
| L5 뷰 | `src/components/calendar-picker/calendar-picker.tsx` | 내부 `params` state 추가, controls 렌더(헤더 하단 슬롯), 사용자 변경 시 `onControlsChange` 호출 후 `formState` 갱신, `handleDateClick`에서 `params` 전달 |
| 도메인 UI | `src/pages/dao/proposal-manage/create/_id.modal.tsx` | `useWeekFromClickBehavior`에 `controls` 노출 옵션 전달, `lastParams` 보존(useState) |
| index | `src/components/calendar-picker/index.ts` | 신규 타입 re-export 정리 |

### 신규 파일 (In)

없음. `ControlSpec` 타입은 `types.ts`에 추가하고, controls 렌더는 `calendar-picker.tsx` 내부 로컬 렌더 함수로 처리한다. 범용성이 확인되면 `ControlsRenderer.tsx`로 추출 가능하나 이번 스코프에서는 인라인 처리한다.

---

## Out of Scope

- `useCalendarBehavior`의 `CalendarMode` 신규 추가 없음 — `week-from-click` 그대로 유지
- `useFreeRangeBehavior` 변경 없음 — controls 슬롯은 해당 모드에서 선택적(미제공 시 렌더 없음)
- `detail/summarySection.tsx` — 7일 고정 유지 (기존 제안 수정 화면은 자동 채움 덮어쓰기 위험)
- 백엔드 DTO / API 변경 없음
- i18n 키 신규 추가 없음 (프리셋 레이블은 숫자 리터럴 + 단위 문자열)
- `pubsub` `open-calendar-picker` 이벤트 구조 파괴적 변경 없음 — `CalendarBehaviors` 내부 확장이므로 하위 호환 유지

---

## Sections

### Section 1 — `ControlSpec` 타입 및 `CalendarBehaviors` 시그니처 확장

**담당 에이전트**: generator
**참조 SKILL**: `coding-convention/SKILL.md`

설계 확정사항:

```
ControlSpec = {
  key: string;                             // 도메인 파라미터 식별자 (e.g. "offsetDays")
  kind: "number" | "preset-chips";         // 렌더 방식 식별자 — L5는 이것만 안다
  label: string;                           // 표시 레이블
  value: number;                           // 현재 값
  // kind === "number" 전용
  min?: number;
  max?: number;
  // kind === "preset-chips" 전용
  presets?: number[];
};

ControlParams = Record<string, number>;    // { offsetDays: 21 } 식의 key-value 맵

CalendarBehaviors 변경:
  controls?: ControlSpec[];
  onControlsChange?: (
    current: Partial<DateRange>,
    params: ControlParams
  ) => CalendarSelectResult | null;         // null이면 formState 갱신 없음
  onSelectDate: (
    date: Date,
    current: Partial<DateRange>,
    selectType: CalendarSelectType,
    params: ControlParams                   // 추가 (4번째 인자)
  ) => CalendarSelectResult;
```

기존 `onSelectDate(date, current, selectType)` 3-인자 호출부는
prim 훅(`useCalendarBehavior`) 내부에서 `params = {}` 기본값으로 래핑하므로
`useFreeRangeBehavior` 등 기존 도메인 훅 변경 불필요.

출력물: `types.ts` 수정

---

### Section 2 — `useCalendarBehavior` (prim) controls 포워딩

**담당 에이전트**: generator
**참조 SKILL**: `coding-convention/SKILL.md`

변경 내용:
- `Options`에 `controls?: ControlSpec[]`, `onControlsChange?` 수신 추가.
- 반환 `CalendarBehaviors` 객체에 `controls`, `onControlsChange` 포함하여 전달.
- `onSelectDate` 내부에서 `params` 인자를 정책 함수에 포워딩:
  - `week-from-click` 분기: `params.offsetDays ?? weekOffsetDays ?? 7` 우선순위로 offset 결정.
  - `free-range` 분기: params 무시(미사용).
- `useMemo` deps에 `controls` 참조 안정성 주의 — controls 배열 자체를 deps에 넣으면 매 렌더마다 새 참조 발생. **도메인 훅에서 `useMemo`로 controls 안정화** 후 전달.

출력물: `useCalendarBehavior.ts` 수정

---

### Section 3 — `useWeekFromClickBehavior` (domain) controls 노출 + onControlsChange 구현

**담당 에이전트**: generator
**참조 SKILL**: `coding-convention/SKILL.md`

변경 내용:
- `Options`에 `controls?: boolean | Partial<ControlSpec>` 옵션 추가 (기본 false — 기존 사용처 하위 호환).
  - `controls: true`면 기본 preset-chips (`presets: [3, 7, 14, 21, 30]`) 노출.
  - `controls: { presets: [7, 14] }` 식으로 커스터마이즈 가능.
- `onControlsChange` 구현:
  - `current.startDate`가 존재하면 `params.offsetDays`로 end 재계산 → `{ startDate: current.startDate, endDate: 재계산값 }` 반환.
  - `current.startDate` 없으면 `null` 반환 (재계산 불필요).
- `weekOffsetDays` 옵션은 controls 초기값으로도 사용 (`value: weekOffsetDays ?? 7`).
- `useMemo`로 controls 배열 안정화.

출력물: `useWeekFromClickBehavior.ts` 수정

---

### Section 4 — `calendar-picker.tsx` (L5) controls 렌더 + params state 관리

**담당 에이전트**: generator
**참조 SKILL**: `coding-convention/SKILL.md`

변경 내용:
1. 내부 `params` state 추가 (`useState<ControlParams>({})`).
2. `_handleOpen` 시 `behaviors.controls`가 있으면 `controls`의 초기 `value`들로 `params` 초기화.
3. `_handleClose` 시 `params` 초기화 (`reset` 함수 확장 또는 별도 호출).
4. `renderControls()` 함수 추가:
   - `behaviors.controls`가 없으면 `null` 반환.
   - `kind === "preset-chips"`: 프리셋 숫자 칩 버튼 배열 렌더. 현재 `params[key]` 값과 일치하는 칩에 `active` 클래스.
   - `kind === "number"`: `<input type="number" min max />` 렌더.
   - 값 변경 시: `newParams = { ...params, [key]: newValue }` → `setParams(newParams)` → `onControlsChange?.(formState, newParams)` 호출 → 반환값 non-null이면 `setFormState` 갱신.
5. `handleDateClick`에서 `behaviors.onSelectDate(date, current, selectType, params)` 호출 (4번째 인자 추가).
6. 렌더 위치: `sub-header` 하단, 날짜 그리드 상단 (`<hr />` 사이 슬롯). controls가 없으면 해당 영역 렌더 안 함.
7. **L5 정책 무지 원칙 확인**: `"offsetDays"`, `"week"`, `"range"` 등 어휘 금지. `ControlSpec.key` 값은 string으로만 취급.

출력물: `calendar-picker.tsx` 수정

---

### Section 5 — `create/_id.modal.tsx` 사용처 적용

**담당 에이전트**: generator
**참조 SKILL**: `coding-convention/SKILL.md`

변경 내용:
1. `useWeekFromClickBehavior({ weekOffsetDays: 14, controls: true })` 또는 원하는 preset 목록 전달.
2. `lastParams` 보존을 위해 behaviors 내부 `onControlsChange`가 도메인 wrapper의 useState를 간접 업데이트하는 구조가 아님에 유의 — `onControlsChange`는 순수 재계산 함수이며 params state는 calendar-picker 내부에 보존됨.
   - 모달 닫힘(`_handleClose`) 시 `params` 초기화되므로, **다시 열 때 마지막 offset을 복원하려면** `useWeekFromClickBehavior`의 `weekOffsetDays`를 도메인 측 useState로 관리하고 `onControlsChange` 콜백으로 동기화해야 한다.
   - 구체적 패턴: `behaviors.onControlsChange` 래핑 시 `setLastOffsetDays(params.offsetDays)` 호출 추가 — 이를 `useWeekFromClickBehavior`의 `onParamsChange?: (params: ControlParams) => void` 옵션으로 노출하여 처리.
3. `detail/summarySection.tsx` 변경 없음 — `controls` 옵션 미전달이므로 자동으로 기존 동작 유지.

출력물: `create/_id.modal.tsx` 수정

---

### Section 6 — Watcher 검토

**담당 에이전트**: watcher
**참조 SKILL**: `review-checklist/SKILL.md`

체크포인트:
- `calendar-picker.tsx`(L5)가 `offsetDays`, `weekOffsetDays`, `offset` 등 정책 어휘를 단 하나도 직접 참조하지 않는가?
- `ControlSpec.key` 값을 L5가 해석하지 않고 불투명하게 전달만 하는가?
- `onSelectDate` 4번째 인자 `params` 추가가 기존 3-인자 사용처(`useFreeRangeBehavior`, `summarySection`)에 타입 오류를 발생시키지 않는가?
- `controls` 배열 참조 불안정으로 인한 불필요한 behaviors 재생성이 없는가? (`useMemo` deps 확인)
- 모달 닫힘 후 재열림 시 offset이 `weekOffsetDays` 초기값으로 올바르게 복원되는가?
- `onControlsChange`가 `current.startDate`가 없을 때 `null`을 반환하여 formState를 변경하지 않는가?
- `summarySection.tsx` 및 기타 기존 `DateRangeField` 사용처에 의도치 않은 변경이 없는가?
- `yarn lint && tsc --noEmit` pass 여부

---

## Required Agents

- generator: Section 1, 2, 3, 4, 5 구현
- watcher: Section 6 검토

---

## Required Skills

- `coding-convention/SKILL.md` — 컴포넌트 구조, 파일명, props 설계 규칙
- `review-checklist/SKILL.md` — watcher 검토 기준

---

## Risks / Assumptions

### Risk 1 — `onSelectDate` 시그니처 확장의 하위 호환성

기존 `useFreeRangeBehavior` 등 3-인자 구현체가 4번째 인자(`params`)를 받지 않는다.
TypeScript는 여분 인자를 무시하므로 런타임 문제는 없으나,
`CalendarBehaviors.onSelectDate` 타입을 4-인자로 변경하면 기존 3-인자 구현체가 타입 오류를 낼 수 있다.

**해결 방안**: `params: ControlParams = {}` 기본값을 타입 레벨에서 optional로 처리.
`onSelectDate(date, current, selectType, params?: ControlParams)` 형태로 4번째 인자를 optional로 선언.
기존 구현체는 무변경으로 통과.

---

### Risk 2 — `controls` 배열 참조 안정성

`useWeekFromClickBehavior` 내부에서 `controls` 배열을 매 렌더마다 새 참조로 생성하면
`useMemo` deps가 변경 감지를 못하거나 반대로 매 렌더마다 behaviors를 재생성한다.

**해결 방안**: `useWeekFromClickBehavior` 내부에서 `useMemo`로 `controls` 배열을 안정화.
deps: `[weekOffsetDays, presets(stable ref)]`.

---

### Risk 3 — `params` state와 `behaviors` 객체 타이밍 불일치

`onControlsChange`가 호출되는 시점에 `params`가 아직 이전 state일 수 있다(closure).

**해결 방안**: `setParams`와 `onControlsChange` 호출을 같은 이벤트 핸들러 내에서
`newParams` 로컬 변수 기준으로 처리. `setParams(newParams)` + `onControlsChange(formState, newParams)`.
React의 batched update 내에서 `formState`도 최신값을 읽어야 하므로
`setFormState(prev => ...)` 패턴 활용 또는 `useRef`로 최신 formState 추적.

---

### Risk 4 — 모달 재오픈 시 offset 휘발 방지

`_handleClose` 시 `params`가 초기화되므로, 다음 열림 시 `behaviors.controls`의 초기 `value`로 복원된다.
도메인이 `weekOffsetDays`를 useState로 관리하고 `onParamsChange` 콜백으로 갱신하면
재오픈 시 `controls[0].value = weekOffsetDays` 로 복원된다.

**전제**: `useWeekFromClickBehavior`에 `onParamsChange?: (params: ControlParams) => void` 옵션 추가.
도메인 wrapper에서 `setLastOffsetDays(params.offsetDays)` 연결.

---

### Risk 5 — `free-range` 및 기타 behaviors에서의 controls 활용 가능성

`CalendarBehaviors.controls`는 범용 슬롯이므로 `useFreeRangeBehavior`도 향후 `maxRangeDays` 등을
controls로 노출 가능하다. 이번 스코프에서는 `useWeekFromClickBehavior`만 구현하고,
타입과 렌더 인프라는 범용으로 설계한다.

---

### Risk 6 — pubsub `open-calendar-picker` payload와의 충돌

`CalendarBehaviors` 내부에 `controls`가 추가되므로 pubsub payload 구조 자체는 변경 없다.
`behaviors` 필드 내부 확장이므로 기존 구독자에 영향 없음. 하위 호환 유지.

---

### Assumption 1 — controls 렌더 위치

`sub-header`(날짜 범위 표시 헤더) 하단, 월 네비게이션 헤더 상단 사이 슬롯에 렌더.
CSS는 `calendar-picker.css`에 `.calendar-controls` 클래스로 추가.
controls가 없으면 해당 DOM 노드 자체를 렌더하지 않아 기존 레이아웃 영향 없음.

---

### Assumption 2 — ControlSpec `kind` 확장 가능성

현재 `"number" | "preset-chips"` 2종만 정의. 향후 `"toggle"`, `"select"` 등 추가 가능.
calendar-picker의 `renderControls` 함수는 unknown kind에 대해 `null` 렌더 처리.

---

## Approval Request

이 계획대로 진행할까요, 아니면 조정할 부분이 있나요?
