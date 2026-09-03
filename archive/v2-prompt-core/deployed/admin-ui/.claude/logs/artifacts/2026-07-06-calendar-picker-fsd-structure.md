# FSD 구조 정의 — calendar-picker (refactor)

> 작성일: 2026-07-06 / 도메인: `features/calendar-picker` / work_type: refactor

## 목표 디렉터리 구조 (변경 후)

```
src/features/calendar-picker/
├── ui/
│   ├── index.ts                 # public API (유지, import 경로만 remap)
│   ├── calendar-picker.tsx       # 표현 컴포넌트 (renderCells → lib.buildCalendarCells 위임)
│   ├── calendar-picker.css
│   ├── DateRangeField.tsx
│   └── DateRangeField.css
├── model/
│   ├── types.ts                  # (from ui/types.ts)
│   ├── pub-sub.events.ts         # (from ui/pub-sub.events.ts) — 선언병합, entities/dao 패턴과 일치
│   ├── useDateRangeState.ts      # (from ui/hook/useDateRangeState.ts)
│   ├── useCalendarPicker.ts      # (from ui/hook/useCalendarPicker.ts)
│   └── behaviors/
│       ├── useCalendarBehavior.ts       # (from ui/hook/behaviors/)
│       ├── useFreeRangeBehavior.ts
│       └── useWeekFromClickBehavior.ts
└── lib/
    ├── date-range.ts             # (from ui/utils/date-range.ts) — 순수 함수
    └── calendar-cells.ts         # 신규 — buildCalendarCells 순수 추출 (P1-b)
```

## 세그먼트 책임

- `ui`: 표현 컴포넌트만. JSX 조립·이벤트 핸들러 바인딩·className 최종 렌더.
- `model`: 상태 소유 훅(useDateRangeState/useCalendarPicker), 정책 합성 훅(behaviors/*), 도메인 타입, pub-sub 계약.
- `lib`: React 비의존 순수 함수(date 문자열 정규화/변환, calendar cell 파생 계산).

## 신규 순수 함수 시그니처 (P1-b, 구현은 refactorer 위임)

```ts
// lib/calendar-cells.ts
type CalendarCell = {
  day: number;            // 0 이하 = 이전/다음달 placeholder
  isInMonth: boolean;
  isToday: boolean;
  isStart: boolean;
  isEnd: boolean;
  isInRange: boolean;
  isDisabled: boolean;
};

function buildCalendarCells(
  year: number,
  month: number,
  start: string | undefined,
  end: string | undefined,
  isDateDisabled?: (date: Date) => boolean,
): CalendarCell[];
```

- 내부 구현 세부(파일 분할 여부, 헬퍼 함수 추출 여부)는 refactorer 재량.
- `today` 기준값은 함수 내부에서 `new Date()`로 계산(순수성 관점에서는 인자 주입이 이상적이나, 기존 evaluator 진단이 "동일 동작 유지"를 요구하므로 시그니처 확장은 refactorer 판단에 위임 — 테스트 용이성 위해 `today?: Date` 선택적 인자 허용 가능).

## 레이어 제약 재확인

- `features/calendar-picker` → `shared` 방향만 허용 (기존 그대로, 변경 없음).
- 슬라이스 내부 `ui → model → lib` 참조는 허용, **역방향(`lib`/`model`이 `ui` import) 금지**.
