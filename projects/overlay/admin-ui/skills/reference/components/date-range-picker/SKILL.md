---
name: component-date-range-picker
description: {{PROJECT_NAME}}의 날짜 범위 어댑터(src/shared/ui/date-range-picker) 사용 및 수정 가이드. HeroUI·react-aria 격리 경계와 문자열 날짜 계약을 다룰 때 사용.
---

# DateRangePicker (어댑터)

## 대상

- `src/shared/ui/date-range-picker/date-range-picker.tsx`

## 계약

HeroUI v3 `DateRangePicker`, `RangeCalendar`, react-aria `DateInput`/`DateSegment`를 감싸는 **anti-corruption layer**다.

| prop | 설명 |
| --- | --- |
| `value` | `{ startDate?: string; endDate?: string }`. 부분값 허용 |
| `onChange` | `(range: { startDate: string; endDate: string }) => void`. 확정값만 |
| `minDate`, `maxDate` | `"YYYY-MM-DD"` |
| `isDateDisabled` | `(date: string) => boolean` |
| `label`, `isDisabled` | 선택 사항 |
| `placeholder` | 인터페이스에 있으나 **구현에서 사용하지 않는다** |

경계 규칙이 이 파일의 존재 이유다.

- **`@heroui/react`, `react-aria-components`, `@internationalized/date` import는 오직 이 파일 안에만 둔다.** 소비처는 `CalendarDate`, `DateValue` 같은 타입을 몰라야 한다.
- 문자열 → `DateValue` 변환(`parseDate`)과 `DateValue` → 문자열 변환(`toString()`)을 이 어댑터가 전부 흡수한다.
- `startDate`와 `endDate`가 **둘 다 있을 때만** range 값을 구성한다. 부분값은 controlled-empty(`null`)로 넘긴다.
- `onChange`는 `range`가 `null`이면 아무것도 하지 않는다.

## 사용 기준

- 도메인 화면은 이 어댑터를 직접 쓰기보다 `~/features/calendar-picker`의 `DateRangeField`를 사용한다.
- 날짜는 처음부터 끝까지 `"YYYY-MM-DD"` 문자열로 다룬다.
- HeroUI 날짜 타입이 필요해지면 소비처가 아니라 이 파일을 수정한다.

## 수정 규칙

- **`Group`으로 감싸는 구조를 일반 `div`로 바꾸지 않는다.** react-aria가 팝오버 앵커(`PopoverContext.triggerRef`)를 `GroupContext`로만 연결하므로, 앵커가 사라져 팝오버가 좌상단에 뜬다.
- **`RangeCalendar.Cell`에 children을 주지 않는다.** HeroUI가 `children || formattedDate`로 렌더링하므로 children을 주면 날짜 숫자가 사라진다.
- HeroUI·react-aria import를 다른 파일로 퍼뜨리지 않는다. 경계가 무너지면 어댑터의 의미가 없다.
- 부분값을 `null`로 넘기는 규칙을 바꾸면 입력 중간 상태에서 예외가 발생한다.
