# calendar-picker 아키텍처 모델

## 한 줄 요약

`CalendarBehaviors`(타입) 가 정책-표현 사이의 **계약**이고, 도메인 훅이 그 계약의 **구현**을 만들고, prim 훅이 그 구현을 **조립**하고, calendar-picker 가 그 계약을 **소비**한다.

## 계층별 역할

| 계층 | 식별자 | 역할 | 정책 어휘 인지 |
|---|---|---|---|
| 계약 | `CalendarBehaviors` (type) | 정책-표현 인터페이스. 메서드 시그니처 + 메타 슬롯의 **순수 계약**. 런타임 객체 아님. | — (타입) |
| L3 prim | `useCalendarBehavior` | 도메인 훅이 만든 정책 함수에 횡단 관심사(`disablePast → isDateDisabled`) + 메타 슬롯을 묶어 `CalendarBehaviors` 객체를 **물리적으로 조립**. | **무지** (격리 원칙) |
| L4 도메인 훅 | `useFreeRangeBehavior`, `useWeekFromClickBehavior`, ... | `onSelectDate`, `controls`, `onControlsChange` 를 각 정책 약속(예: `OFFSET_KEY`)에 맞게 **합성**. 정책 어휘는 여기서만 살아있음. | **인지(유일)** |
| L4 표현 컴포넌트 | `DateRangeField`, `useCalendarPicker` | pubsub 채널 캡슐화 + 트리거 UI. behaviors 를 props 로 받아 그대로 전달. | 무지 |
| L5 표현 모달 | `calendar-picker.tsx` | `CalendarBehaviors` 계약만 호출. `ControlSpec.kind` 라는 **렌더 어휘**만 인지. `key` 의미 무지. | 무지 |
| 사용처 | 페이지/모달 | **카탈로그 소비자**. 어떤 도메인 훅을 부를지 선택만. 옵션(`weekOffsetDays`, `controls: true`)으로 행동 파라미터화. | 무지 |

## 데이터 흐름

```
사용처 (페이지/모달)
   │  weekOffsetDays, controls: true 등 옵션 선택
   ▼
L4 도메인 훅 (useWeekFromClickBehavior)
   │  onSelectDate / controls / onControlsChange 합성 (OFFSET_KEY 해석은 여기서만)
   ▼
L3 prim (useCalendarBehavior)
   │  disablePast → isDateDisabled 변환 + 메타 슬롯 묶기
   ▼
CalendarBehaviors (계약 객체)
   │  DateRangeField → useCalendarPicker.open() → pubsub publish
   ▼
L5 calendar-picker
   │  계약만 호출. params 는 불투명 맵으로 정책에 되돌려보냄.
   ▼
화면 렌더 + 사용자 인터랙션
```

## 비유

- `CalendarBehaviors` ↔ **USB 규격**
- 도메인 훅 ↔ 실제 USB 장치(키보드/마우스/저장소)
- prim ↔ 케이블/허브(어댑팅)
- calendar-picker ↔ 호스트 PC (포트만 알고 무엇이 꽂혔는지 모름)
- 사용처 ↔ 사용자(USB 장치를 선택해 꽂는 주체)

## 격리 원칙

### prim 격리 (round 2 watcher 게이트의 핵심 위반/수정 사유)
- prim 은 정책 함수(`selectFreeRange`, `selectWeekFromClick`)를 호출하지 않는다.
- prim 은 `params` 의 어떤 키(`offsetDays`, ...)도 해석하지 않는다.
- 위반 시 → 도메인 추가 때마다 prim 이 `mode` 분기로 부풀고, 정책 어휘가 prim 으로 새는 단방향 부패가 발생.

### L5 격리
- calendar-picker 는 `ControlSpec.kind`("number" / "preset-chips")라는 **렌더 어휘**만 안다.
- `ControlSpec.key` 의 의미는 모른다 — `params[key]` 를 불투명 맵으로 정책에 되돌려보냄.
- 위반 시 → 새 정책 도메인을 추가할 때마다 L5 가 분기로 부풀어 OCP 깨짐.

## 확장 시나리오

새 정책 도메인 X 를 추가한다고 가정.

1. `useXBehavior` (L4) 작성
   - 자체 `onSelectDate` 합성
   - 필요 시 자체 `controls` 명세 노출 (`kind` 는 기존 표현 어휘 재사용)
   - 자체 `onControlsChange` 작성 (도메인 키 해석)
   - `useCalendarBehavior` 호출하여 prim 에 주입
2. 사용처에서 `useXBehavior` 호출하여 `behaviors` prop 으로 전달
3. **prim, L5, 다른 도메인 훅 모두 무수정**

## 책임 경계 한 줄 정리

> **"정책 어휘는 도메인 훅 안에서 태어나고 죽는다."**
> 사용처는 옵션으로 정책을 고르고, prim 은 횡단 관심사를 입히고, L5 는 계약만 호출한다.
