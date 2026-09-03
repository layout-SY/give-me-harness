# Architecture Discussion Log

> evaluation-log.md 작성 이후, 사용자와 어시스턴트 간의 추상화 방향성 논의 기록 (2026-04-29)

---

## Q1. 사용자 — 구조 전체를 바꿔도 된다면 업무 생산성을 높일 방법은?

> 각 삼각 구조 관계에서 추상화 단계를 엄격히 하며 구조 전체를 바꿔도 된다면 어떤 방식이 업무 생산성을 높일 수 있을까?

### A1. 어시스턴트 — 5-Layer 재설계 제안

**핵심 진단:** 현재 한 컴포넌트에 5개 레이어 책임이 응집되어 있고, 사용처가 모든 레이어를 직접 알아야 함.

**제안 구조 (단방향 의존):**

```
L5. <DateRangeField />          ← 사용처 90%가 여기만 사용
    value/onChange만 노출, 내부에서 picker 호출
L4. useCalendarPicker() Promise API   ← 비정형 트리거
    const range = await open({...})
    Context 기반, pubsub 이름 0개 노출, 자동 close
L3. <CalendarGrid />, <CalendarHeader />   ← 표현 컴포넌트
    완전 controlled, popup·전역 상태 없음
L2. useDateRangeState()        ← React 상태 훅
    start/end 선택, 월 이동, autoWeek 모드 처리
L1. date-range.ts              ← 순수 함수
    selectDate / autoSelectWeek / normalizeRange
```

**사용처 코드 변화:**

- 현재 (~30줄): `useCalendar` + 인라인 `pubsub.publish("close-calendar-picker")` + TextInput×2 + IconButton
- 제안 (~5줄): `<DateRangeField mode="week-from-click" value onChange />` 한 줄

**생산성 효과:**

1. 새 사용처 추가 비용 30줄 → 5줄
2. 변경 전파 범위 20곳 → 1곳
3. 타입 안전 Promise API로 콜백 슬롯 경쟁 조건 제거
4. 단위 테스트 가능 (L1 순수 함수)
5. 점진적 도입 가능
6. `autoSelectOneWeek: true` (의미 불명) → `mode: "week-from-click"` (의도 명시)

**트레이드오프:**

- 초기 구축 비용 + 20곳 마이그레이션
- 다른 전역 팝업이 pubsub을 사용 중이라면 컨벤션 비대칭
- L4 Promise API + L5 DateRangeField가 효과의 80% 차지 → 이 둘만 먼저 구축해도 가치 충분

---

## Q2. 사용자 — Hook 인자 주입은 추상화 위반인가?

> 상황이나 각 페이지/모달 상황에 따라서 캘린더 사용 방식이 변경될 수 있어. 각 페이지나 모달에서 본인이 필요로 하는 상황에 따라 hook을 인자로 넘기는 방식은 책임 분리 추상화 관점에서 옳바르지 않은 방법이야?

### A2. 어시스턴트 — Configuration Injection은 추상화의 *작동 메커니즘*

**결론:** Hook 인자 주입 자체는 위반이 아니며, 오히려 IoC(Inversion of Control)의 정상 형태.

**구분 기준:**

| 구분 | 의미 | 추상화 관점 |
|---|---|---|
| Configuration Injection | 사용처가 WHAT(필요한 것)을 선언 | 권장 — IoC 정상 형태 |
| Implementation Leakage | 사용처가 HOW(내부 동작)를 알아야 함 | 위반 — 캡슐화 깨짐 |

현재 `useCalendar`의 진짜 문제: 두 가지가 **섞여** 있음.

- `autoSelectOneWeek` 인자 → Config (OK)
- 콜백 안에서 `pubsub.publish("close-calendar-picker")` 호출 → 사용처가 close 구현을 알아야 함 (위반)

**옳은 인자 주입의 형태 (선언적 의도):**

```ts
useCalendarPicker({
  initialRange: { start, end },
  mode: "week-from-click" | "free-range" | "single-date" | "fiscal-quarter",
  constraints: { disablePast: true, maxRangeDays: 30 },
  onConfirm: (range) => setFormState(...),  // 도메인 콜백, close는 훅이 알아서
});
```

**자유도 형태 정의 3패턴:**

1. **Preset enum / Mode** — 알려진 변형이 유한할 때. 가장 강한 추상화.
2. **Strategy / Policy 함수 주입** — 변형이 무한하지만 동작 형태 일정할 때. 순수 함수만 주입.
3. **Composition (Layer 하향)** — 위 두 가지로 표현 못 하는 예외. L3 표현 컴포넌트 직접 조립.

**핵심 원칙:**

> 추상화는 자유도를 빼앗는 게 아니라, 자유도의 *형태*를 정의한다.

---

## Q3. 사용자 — 추상화 의도의 정밀화

> 지금 현재는 날짜를 선택했을 때 7일이 자동 선택되게끔 해당 기능이 calendar-picker에 하드코딩 되어 있다라고 보여져. 따라서 기획 정책이 변경되거나 추가될 경우 공용 컴포넌트와 내부 기능을 직접 손봐야 하고, 이에 따라서 연관된 사용처들의 변경도 불가피하게 크게 발생하게 돼.
>
> 그래서 사용처에서는 본인의 도메인과 상황에 따라서 어떤 기능이 필요한지만 알게끔 하고, hook에는 그에 따른 기능에 대한 구현이 정의되어 있고, calendar-picker 모달에서는 구현에 대해서 모르지만 사용처의 기능 요청에 따라서 해당 기능이 반영되어 실행되는 구조를 생각했어.
>
> 추가/변경 기능 자체에 calendar-picker 모달의 element 구조 변경/추가가 불가피한 상황에서는 공용 컴포넌트 수정이 필요하겠지만 그 외에 기능에 관련된 내용 만큼은 이러한 구조를 띄는 게 좋겠단 생각이 들었어. 혹시 element 구조에 대해서도 이러한 추상화 분리를 컴포넌트 단위로 가능하다면 하면 좋긴 하겠지만.

### A3. 어시스턴트 — Inversion of Control via Behavior Injection

**패턴 명명:**

> "컴포넌트는 *메커니즘*만 안다. 훅은 *정책*을 안다. 사용처는 *의도*만 안다."

OOP의 Open-Closed Principle을 React에 옮긴 형태.

**역할 재정의:**

```
사용처(Site)        : "내 도메인은 이런 의도가 필요해"
   ↓ intent (선언적)
훅(Hook)           : 의도 → 정책으로 번역 / 정책 = 행동 묶음
   ↓ behaviors (계약된 함수 묶음)
컴포넌트(Component) : 주입받은 행동을 *실행*만 한다
```

**Behavior Contract 예시:**

```ts
type CalendarBehaviors = {
  initialRange?: DateRange;
  onSelectDate: (date: Date, current: DateRange) => DateRange;  // 정책 주입점
  isDateDisabled?: (date: Date) => boolean;
  isDateHighlighted?: (date: Date) => boolean;
  validate?: (range: DateRange) => string | null;
};

const CalendarPicker = ({ behaviors, value, onChange }) => {
  const handleClick = (date) => {
    const next = behaviors.onSelectDate(date, value);  // 그냥 호출 (정책 무지)
    onChange(next);
  };
};
```

**도메인 hook 예시:**

```ts
useWeekAutoSelectBehavior(opts): CalendarBehaviors
useFreeRangeBehavior(opts): CalendarBehaviors
useBusinessDayOnlyBehavior(opts): CalendarBehaviors
```

**사용처:**

```tsx
const behaviors = useWeekAutoSelectBehavior({ initialRange });
<DateRangeField behaviors={behaviors} value onChange />
```

**기획 변경 시나리오 매트릭스:**

| 변경 시나리오 | 현재 | 제안 구조 |
|---|---|---|
| "투표 기간 7일 → 14일" | 컴포넌트 + 사용처 다수 영향 | hook 1개의 숫자 1개 |
| "출석 이벤트 주말 선택 불가" | 컴포넌트에 분기 추가 | 신규 hook 작성, 컴포넌트 0건 |
| "회계 분기 단위 모드 추가" | 컴포넌트에 새 모드 분기 | 신규 hook + behaviors 계약 그대로 |
| "휴일 하이라이트" | 컴포넌트 props 추가 + 사용처 검토 | 기존 hooks에 `isDateHighlighted` 추가, 컴포넌트 1줄 |

**Element 구조 추상화 — 3단계:**

- **(약) Slot 주입**: `slots={{ Header, Footer }}` — 부분 교체
- **(중) Compound Component**: `<Calendar.Root><Calendar.Grid /></Calendar.Root>` — 자유 조립
- **(강) Headless**: `useCalendarLogic()` + 사용처 UI 직접 작성 — Radix 패턴

권장: 처음엔 (약)까지만 도입, 필요 증명되면 확장.

**함정 두 가지:**

1. **계약이 너무 좁으면 정책마다 깨진다.** → 의미적 원시 동작(semantic primitive)을 노출, 구현 훅(implementation hook) 노출 금지.
2. **훅이 폭발한다.** → 공통 prim 훅(`useCalendarBehavior({ mode, constraints })`) 두고, 도메인 hook은 prim의 얇은 래퍼.

**다음 단계 제안:** 사용처 10곳의 *실제 정책 차이* 인벤토리화 → contract 최소 형태 자동 결정.

---

## 결론 — 채택된 아키텍처 방향

1. **L4(`useCalendarPicker`) + L5(`<DateRangeField>`)** 우선 구축. 효과의 80%.
2. 사용처는 **도메인 의도(mode, constraints, onConfirm)** 만 선언, pubsub 이름 비노출.
3. 컴포넌트는 **Behavior Contract** 를 받아 실행만 함. 정책 무지.
4. 훅은 **공통 prim 훅 + 도메인 래퍼 훅** 의 2단 구조.
5. UI 변형은 **Slot 주입(약)** 부터 도입, 필요 증명 시 Compound/Headless로 확장.
6. 기존 pubsub 컨벤션과의 비대칭 회피를 위해, L4 내부에 pubsub 유지 가능 (사용처는 여전히 모름).
7. 마이그레이션 선결 작업: **사용처 10곳의 정책 차이 인벤토리화** → Behavior Contract 최소 형태 결정.
