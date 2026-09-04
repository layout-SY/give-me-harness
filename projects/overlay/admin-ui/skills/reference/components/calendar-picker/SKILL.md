---
name: component-calendar-picker
description: {{PROJECT_NAME}}의 날짜 범위 필드(src/features/calendar-picker) 사용 및 수정 가이드. DateRange 문자열 계약과 date-range-picker 어댑터를 다룰 때 사용.
---

# DateRangeField (calendar-picker)

## 대상

- `src/features/calendar-picker/index.ts`
- `src/features/calendar-picker/ui/DateRangeField.tsx`
- `src/features/calendar-picker/ui/index.ts`
- `src/features/calendar-picker/model/types.ts`
- `src/shared/ui/date-range-picker/date-range-picker.tsx` (어댑터)

`src/shared/ui`가 아니라 **`src/features` 아래의 기능 슬라이스**다. 배럴 `~/features/calendar-picker`에서 `DateRangeField`, `DateRangeFieldProps`, `DateRange`를 명명 내보내기로 가져온다.

## 계약

```ts
type DateRange = { startDate: string; endDate: string }; // "YYYY-MM-DD"
```

| prop | 설명 |
| --- | --- |
| `value` | `Partial<DateRange>`. 한쪽만 정해진 중간 상태를 허용한다 |
| `onChange` | `(range: DateRange) => void`. **확정된 범위만 올라온다** |
| `minDate`, `maxDate` | `"YYYY-MM-DD"` 문자열 |
| `isDateDisabled` | `(date: string) => boolean` |
| `disabled` | 어댑터의 `isDisabled`로 전달된다 |
| `label` | 필드 라벨 |

역할 분담이 분명하다.

- 이 파일은 **도메인 계약만 다룬다.** 입력은 부분값, 출력은 확정값이다.
- HeroUI와 react-aria 세부는 전부 `shared/ui/date-range-picker` 어댑터가 흡수한다. 이 컴포넌트는 날짜 객체를 다루지 않는다.
- 날짜는 처음부터 끝까지 `"YYYY-MM-DD"` 문자열이다.

## 사용 기준

- 기간 검색·기간 설정 입력은 이 필드를 재사용한다. 달력 UI를 직접 만들지 않는다.
- 상위 상태는 `Partial<DateRange>`로 보관하고, `onChange`로 확정될 때 질의 상태에 반영한다.
- HeroUI 날짜 타입이 필요하면 이 컴포넌트가 아니라 어댑터를 수정한다.

## 현재 상태

파일은 존재하지만 **현재 이 필드를 import하는 화면이 없다.** 기간 입력 화면을 새로 만들 때 재사용 대상이다. 과거의 pub-sub 모달 주입 방식은 어댑터 전환으로 제거됐다.

## 수정 규칙

- 문자열 날짜 계약을 `Date`나 HeroUI 날짜 객체로 바꾸지 않는다. 어댑터 경계가 무너진다.
- `value`는 부분값, `onChange`는 확정값이라는 비대칭을 유지한다.
- HeroUI·react-aria 관련 처리를 이 파일로 끌어올리지 않는다. 어댑터에 둔다.
- 배럴을 거치지 않고 `ui/DateRangeField`를 직접 import하지 않는다.
