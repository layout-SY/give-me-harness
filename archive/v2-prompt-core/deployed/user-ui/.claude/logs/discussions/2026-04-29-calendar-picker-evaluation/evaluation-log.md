# Evaluation Log

> evaluator 에이전트 출력 원문 (2026-04-29)
> agentId: af2cec6ea32446ff5

## Context

분석 대상은 세 개의 파일이며, 전역 달력 팝업을 pubsub으로 제어하는 패턴이 프로젝트 전반에 얼마나 확산되어 있는지를 함께 파악했다.

- 공용 컴포넌트: `src/components/calendar-picker/calendar-picker.tsx`
- 공용 훅: `src/components/calendar-picker/hook/useCalendar.ts`
- 주요 사용처: `src/pages/dao/proposal-manage/create/_id.modal.tsx`

추가로 확인한 사실: `open-calendar-picker` / `close-calendar-picker` pubsub 이벤트를 직접 호출하는 코드가 `useCalendar.ts` 제외 기준으로 프로젝트 전체에 **20개 지점**에 분산되어 있다. `useCalendar`를 경유하지 않고 `pubsub.publish("open-calendar-picker", {...})`를 직접 인라인으로 호출하는 사용처가 8개 파일에 존재한다 (sales, usage/calls, usage/soria, usage/item, users/suspend.popup, events/attendance x2, events/roulette x2).

---

## Structural Risks

### Risk 1. 닫기 책임의 전면 누수 — 현재 전체 사용처가 close 를 직접 담당

**근거:**

- `calendar-picker.tsx` L191–195: `handleConfirm`은 콜백만 호출하고 `_handleClose()`를 스스로 호출하지 않는다.
- `_id.modal.tsx` (create) L59: 콜백 내부에서 `pubsub.publish("close-calendar-picker")` 직접 호출.
- 동일 패턴이 `detail/_id.modal.tsx` L121, `sales/index.tsx` L254, `usage/calls` L182, `usage/soria` L189, `usage/item` L212, `users/suspend.popup` L104, `events/attendance` L129 L56, `events/roulette` L129 L56 에서 반복된다.

CalendarPicker 컴포넌트가 confirm 후 자신을 닫는 정책을 갖고 있지 않기 때문에, "confirm = close"라는 당연한 기대를 모든 사용처가 각자 콜백 안에서 직접 구현하고 있다. 현재 확인된 close 직접 publish 호출 지점은 최소 10개다. 이 패턴은 향후 새로운 사용처를 추가할 때마다 close publish를 빠뜨릴 위험을 구조적으로 내포한다. 실제로 `calendar-picker.tsx`의 Cancel 버튼(L332)은 `_handleClose()`를 직접 호출하는 반면 Confirm 버튼(L338)은 `handleConfirm()`만 호출하므로, confirm과 cancel의 close 주체가 다르다. 이 비대칭 자체가 사용처에게 close 책임을 떠넘기는 설계의 산물이다.

---

### Risk 2. pubsub 인터페이스가 추상화 없이 전 사용처에 노출됨 (`useCalendar`의 추상화 가치 미달)

**근거:**

- `useCalendar.ts` L11–16: 본문 전체가 `pubsub.publish("open-calendar-picker", {...})` 한 줄이다. 메모이제이션, 조건 분기, 도메인 변환 로직이 전혀 없다.
- 8개 파일이 `useCalendar`를 거치지 않고 `pubsub.publish("open-calendar-picker", {...})`를 직접 인라인으로 호출한다.
- 콜백 안에서 `pubsub.publish("close-calendar-picker")`를 직접 호출하는 것도 모두 사용처 책임이다.

`useCalendar`가 open publish 하나만 감싸고 close는 감싸지 않기 때문에, 사용처는 어차피 pubsub을 직접 import해야 한다. 그 결과 훅 사용처(create/detail modal)와 훅 비사용처(sales, events 등)의 코드 구조가 뒤섞이고, 이벤트 이름(`"open-calendar-picker"`, `"close-calendar-picker"`)과 payload 구조가 사용처 코드에 그대로 노출되어 있다. 이벤트 이름 변경이 필요한 경우 20곳을 일일이 수정해야 한다.

---

### Risk 3. 전역 단일 인스턴스 가정 + 콜백 덮어쓰기 경쟁 조건

**근거:**

- `calendar-picker.tsx` L49: `useState<CalendarPickerCallback | null>(null)` — 콜백 슬롯이 1개.
- `calendar-picker.tsx` L82: `setCallback(() => callback)` — 나중에 publish된 이벤트가 이전 콜백을 덮어쓴다.
- `useEffect` L106–113: `[]` 의존성으로 구독하므로 클로저 내부의 `_handleOpen`은 컴포넌트 마운트 시점의 참조로 고정된다.

-중요-
**_현재는 캘린더가 전역 1개라는 묵시적 가정 위에서 동작한다. 여러 모달이 동시에 열려 있는 시나리오(예: SideModal 위에 또 다른 Popup)에서 두 번째 `open-calendar-picker`가 publish되면 첫 번째 콜백은 소실되고 두 번째 콜백으로 교체된다. 현재 어드민 페이지 구조상 실제로 충돌이 발생할 가능성은 낮지만, 페이지 구조가 복잡해질수록 이 가정이 깨질 수 있다._**

---

### Risk 4. `_handleClose` 내부의 상태 오염 버그 — 테스트 부재의 구조적 신호

**근거:**

- `calendar-picker.tsx` L101–102:
  ```ts
  setCurrentYear(new Date().getFullYear());
  setCurrentYear(new Date().getMonth()); // Year setter에 month 값(0–11)이 들어감
  ```
  `setCurrentMonth`가 호출되어야 할 자리에 `setCurrentYear`가 두 번 호출된다. 달력을 닫고 다시 열면 연도가 0–11 범위의 값(예: 3월이면 연도 = 2)으로 오염된다.

이 버그가 "닫기"라는 명백히 단순한 경로에 살아있다는 사실은, 이 컴포넌트에 단위 테스트가 없고 닫기 동작을 수동으로 검증하는 절차도 없음을 시사한다. 한 파일에 팝업 상태 / 월 네비게이션 / 셀 렌더 / range 로직 / autoSelectOneWeek / 콜백 호출이 모두 응집되어 있어 단위 테스트를 작성하기 어려운 구조인 것이 이 버그를 장기 생존시키는 환경적 원인이다.

---

### Risk 5. "기간 입력 + 달력 트리거" 보일러플레이트의 반복 복제

**근거:**

- `create/_id.modal.tsx` L211–234: `<TextInput name="voteStartAt" readOnly />` + `<span>~</span>` + `<TextInput name="voteEndAt" readOnly />` + `<IconButton onClick={handleOpenCalendar}>` 패턴.
- `detail/_id.modal.tsx` L219의 `onOpenCalendar={handleOpenCalendar}` prop 전달.
- `events/attendance` create/edit, `events/roulette` create/edit 에서도 동일 구조의 인라인 open-calendar-picker publish + date range TextInput 쌍 + IconButton 조합이 반복된다.

이 UI 조합은 최소 6개 이상의 사용처에서 각기 다른 방식(일부는 useCalendar, 일부는 직접 publish, 일부는 섹션 컴포넌트에 prop 전달)으로 복제된다. 표현 컴포넌트로 추출되어 있지 않기 때문에, 달력 아이콘 교체나 레이아웃 변경 시 모든 사용처를 개별 수정해야 한다.

---

### Risk 6. `autoSelectOneWeek` 플래그의 의미 불명확 및 도메인 정책 컴포넌트 누수

**근거:**

- `calendar-picker.tsx` L182–189: `handleAutoSelectOneWeek`는 클릭한 날짜로부터 7일 후를 endDate로 자동 설정한다. 이 로직은 "투표 기간 = 1주일" 같은 특정 도메인 정책에서 유래한 것으로 보인다.
- `useCalendar.ts` L5: `autoSelectOneWeek: boolean`이 일반 파라미터로 공용 훅 시그니처에 노출되어 있다.
- `create/_id.modal.tsx` L56, `detail/_id.modal.tsx` L118, `events/attendance` L40, `events/roulette` L40: 모두 `autoSelectOneWeek: true`로 하드코딩.

이 플래그가 모든 사용처에서 `true`라면 일반 옵션으로 추상화될 이유가 없다. 반대로 `false`인 사용처가 있다면 그 차이를 명시적으로 표현하는 별도 네이밍이 필요하다. 현재 상태는 도메인 정책이 공용 인터페이스에 의미 불명확하게 노출된 형태다.

---

## Why This Matters

첫째, **변경 전파 범위가 과도하게 넓다.** 달력 닫기 정책 하나를 바꾸려면 최소 10개 파일을 동시에 수정해야 한다. 이벤트 이름을 바꾸면 20개 지점이 영향을 받는다.

둘째, **새로운 사용처를 추가할 때 습관적으로 close를 빠뜨리는 버그가 발생할 수 있다.** 현재 구조에서 "올바른" 사용법은 문서화가 아닌 기존 코드를 읽고 복사하는 것에 의존한다. close publish를 콜백에 넣는 것이 컨벤션이라는 사실이 훅 시그니처나 컴포넌트 API에서 드러나지 않는다.

셋째, **`_handleClose` 버그가 실운영 환경에서 연도 오염을 유발할 수 있다.** 달력을 닫고 다시 열면 표시 연도가 현재 월 번호(0–11)로 표시된다. 사용자가 "2024년 3월"을 보아야 할 때 "2년 3월"이 표시될 수 있다.

넷째, **테스트가 불가능한 구조가 버그의 장기 생존을 허용한다.** 현재 컴포넌트 구조에서는 닫기 동작만 단독으로 검증하는 단위 테스트를 작성하기 어렵다.

---

## Improvement Options

### Option A. `handleConfirm` 내부에서 close를 직접 호출 (최소 개입)

`calendar-picker.tsx`의 `handleConfirm` 함수 끝에 `pubsub.publish("close-calendar-picker")`(또는 `_handleClose()` 직접 호출)를 추가한다.

- Trade-off (장점): 변경 범위가 한 파일의 한 함수이며, 모든 사용처의 콜백에서 close publish를 제거할 수 있다. `_handleClose` 버그도 이 시점에 함께 수정 가능.
- Trade-off (단점): 근본적인 추상화 누수(pubsub 이름 직접 노출, 반복 보일러플레이트)는 해결되지 않는다. `handleConfirm` 호출 후 컴포넌트가 자신을 닫는 것이 올바른지에 대한 암묵적 가정을 코드로만 정의한다.
- 난이도: 낮음 / 영향 범위: 단일 파일 수정 + 사용처 10개에서 `pubsub.publish("close-calendar-picker")` 제거 가능

---

### Option B. `useCalendar`를 `useCalendarPicker` 도메인 훅으로 격상 (중간 개입)

open/close 양쪽을 모두 캡슐화하는 훅으로 교체한다. 훅이 반환하는 콜백 래퍼 내부에서 도메인 필드명(`voteStartAt`, `voteEndAt`) 매핑과 close publish를 처리한다. `autoSelectOneWeek`는 훅 옵션에서 제거하고 컴포넌트 기본값으로 내린다.

```ts
// 예시 시그니처 (구현 아님)
const { handleOpenCalendar } = useCalendarPicker({
  startDate: formState.voteStartAt,
  endDate: formState.voteEndAt,
  onConfirm: ({ startDate, endDate }) => {
    setFormState((prev) => ({ ...prev, voteStartAt: startDate, voteEndAt: endDate }));
  },
});
```

- Trade-off (장점): 사용처가 pubsub 이름을 전혀 몰라도 된다. close 책임이 훅 내부로 수렴한다. 이벤트 이름 변경 시 훅 1개만 수정하면 된다.
- Trade-off (단점): `useCalendar`를 직접 사용하지 않고 pubsub을 인라인 호출하는 8개 파일은 별도로 마이그레이션해야 한다. 훅 교체 시 기존 `useCalendar`와 병존 기간이 발생할 수 있다.
- 난이도: 중간 / 영향 범위: 훅 교체 + `useCalendar` 사용처 2개 즉시 마이그레이션, 나머지 8개 파일은 단계적

---

### Option C. `<DateRangeField>` 표현 컴포넌트 추출 (UI 중복 해소)

"startDate TextInput + separator + endDate TextInput + 달력 IconButton" 묶음을 `<DateRangeField>` 단일 컴포넌트로 추출한다. 이 컴포넌트는 내부적으로 Option B의 훅을 사용하고, `value={{ startDate, endDate }}` / `onChange` / `disabled` 인터페이스만 노출한다.

```tsx
// 예시 사용 (구현 아님)
<DateRangeField
  label={mui["_dao_proposal_create_vote_period"]}
  value={{ startDate: formState.voteStartAt, endDate: formState.voteEndAt }}
  onChange={({ startDate, endDate }) => setFormState((prev) => ({ ...prev, voteStartAt: startDate, voteEndAt: endDate }))}
  disabled={isLoading}
/>
```

- Trade-off (장점): UI 변경(아이콘, 레이아웃, 포맷)이 1곳으로 수렴된다. 사용처 코드가 현저히 단순해진다. 달력 의존성이 사용처 import에서 사라진다.
- Trade-off (단점): 컴포넌트 추출 자체의 설계 비용이 있다. 일부 사용처는 disabled 조건이나 레이아웃이 달라 컴포넌트 prop이 복잡해질 수 있다.
- 난이도: 중간~높음 / 영향 범위: 6개 이상 사용처 마이그레이션

---

### Option D. pubsub 대신 Context/Ref 기반으로 전환 (근본 구조 변경)

`CalendarPicker`를 전역 pubsub이 아닌 React Context 또는 `useImperativeHandle` 기반으로 재설계한다. 단일 인스턴스 가정을 명시적으로 표현하고, 콜백 슬롯 경쟁 조건을 구조적으로 제거한다.

- Trade-off (장점): 이벤트 이름 string 의존성이 완전히 제거된다. TypeScript 타입 안전성이 강화된다. 단일 인스턴스 가정이 코드 구조에 명시된다.
- Trade-off (단점): 전체 사용처 마이그레이션 비용이 크다. 현재 pubsub 패턴이 프로젝트 전반의 관례이므로, 이 컴포넌트만 다른 패턴으로 전환하면 불일치가 생긴다.
- 난이도: 높음 / 영향 범위: 전체 사용처 + 아키텍처 결정 필요

---

## Recommended Backlog

우선순위 순서로 정렬한다.

**[P1] `_handleClose` Year/Month 버그 수정**

- 파일: `src/components/calendar-picker/calendar-picker.tsx` L102
- `setCurrentYear(new Date().getMonth())` → `setCurrentMonth(new Date().getMonth())`
- 영향 범위: 달력 사용 전체 / 예상 난이도: 매우 낮음 / 위험도: 즉시 사용자 노출 가능한 UI 오류

**[P2] `handleConfirm` 이후 자동 close 정책 확립 (Option A)**

- `handleConfirm` 내부에서 `_handleClose()` 직접 호출 추가
- 콜백에서 중복으로 close를 publish하는 사용처 10개에서 해당 라인 제거
- 영향 범위: 전체 사용처 / 예상 난이도: 낮음 / 가치: 닫기 책임 수렴

**[P3] `useCalendar` → `useCalendarPicker` 로 교체 — pubsub 이름 캡슐화 (Option B)**

- open과 close를 모두 훅 내부에서 처리
- `useCalendar`를 직접 사용하지 않는 8개 파일도 훅으로 마이그레이션
- 영향 범위: 10개 파일 / 예상 난이도: 중간 / 가치: 이벤트 이름 20곳 노출 → 1곳 수렴

**[P4] `autoSelectOneWeek` 처리 방식 결정**

- 현재 모든 사용처가 `true`임을 확인했으므로, `true`를 컴포넌트/훅 기본값으로 내리거나 제거
- 만약 `false`가 필요한 사용처가 존재한다면 명시적으로 이름을 부여 (예: `mode: "range" | "week-from-click"`)
- 영향 범위: 훅 시그니처 + events.ts / 예상 난이도: 낮음

**[P5] `<DateRangeField>` 표현 컴포넌트 추출 (Option C)**

- P3 완료 이후 진행하는 것이 적합
- 영향 범위: 6개 이상 사용처 / 예상 난이도: 중간 / 가치: UI 보일러플레이트 수렴

**[P6] `CalendarPicker` 내부 로직 분리 — 단위 테스트 가능 구조화**

- 날짜 range 계산 로직을 순수 함수로 추출 (`useDateRangeState` 등)
- 팝업 상태, 월 네비게이션, 셀 렌더, range 선택 로직을 레이어 분리
- 영향 범위: 컴포넌트 내부 리팩터링 / 예상 난이도: 중간~높음

---

## Suggested Next Step

**P1 버그 수정과 P2 자동 close 정책 확립을 단일 커밋으로 묶어 먼저 처리한다.**

`_handleClose`의 Year/Month 버그는 현재 사용자에게 노출되는 UI 오류이며 1줄 수정이다. `handleConfirm`의 자동 close는 2줄 추가(컴포넌트) + 사용처 10개에서 각 1줄 제거다. 두 작업 모두 추상화 결정이 필요 없고, 범위가 명확하며, 수정 후 다른 사용처의 동작이 깨지지 않는다. 이 두 항목을 완료하면 P3(훅 캡슐화) 작업 시 "close를 어디에 두어야 하는가"라는 문제가 이미 해결된 상태에서 시작할 수 있어 이후 단계의 설계 결정이 단순해진다.

---

## Agent Metadata

```yaml
summary: >
  CalendarPicker 공용 컴포넌트/훅/사용처 삼각 구조에서 닫기 책임이 전 사용처로 누수되고 있으며,
  pubsub 이벤트 이름이 20개 지점에 직접 노출된 상태다. _handleClose의 Year/Month 버그가
  실운영 환경에서 즉시 재현 가능한 UI 오류를 유발한다.
decision: recommendation_ready
architectural_risks:
  - 닫기 책임 전면 누수 (10개 지점)
  - pubsub 이벤트 이름/payload 직접 노출 (20개 지점)
  - 콜백 단일 슬롯 경쟁 조건
  - _handleClose Year/Month 버그
  - UI DateRange 보일러플레이트 중복 (6개 이상)
  - autoSelectOneWeek 도메인 정책 공용 인터페이스 누수
recommended_backlog:
  - P1: _handleClose Year/Month 버그 수정 (즉시)
  - P2: handleConfirm 자동 close 정책 확립 (낮음)
  - P3: useCalendarPicker pubsub 캡슐화 (중간)
  - P4: autoSelectOneWeek 처리 방식 결정 (낮음)
  - P5: DateRangeField 컴포넌트 추출 (중간)
  - P6: CalendarPicker 내부 로직 분리 (중간~높음)
status: recommendation_ready
```
