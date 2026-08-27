# Exploration — calendar-picker 리팩토링 (evaluator 이관)

> 작업: `src/features/calendar-picker/` FSD 세그먼트 재배치 + 순수 조각 lib 추출
> 입력: evaluator 진단 (부분적 필요 — 세그먼트 재배치는 필요, 파이프라인/의존 해체는 불필요)

## 1. 현재 파일 목록 (before)

```
ui/calendar-picker.css
ui/calendar-picker.tsx
ui/DateRangeField.css
ui/DateRangeField.tsx
ui/hook/behaviors/useCalendarBehavior.ts
ui/hook/behaviors/useFreeRangeBehavior.ts
ui/hook/behaviors/useWeekFromClickBehavior.ts
ui/hook/useCalendarPicker.ts
ui/hook/useDateRangeState.ts
ui/index.ts
ui/pub-sub.events.ts
ui/types.ts
ui/utils/date-range.ts
```

## 2. 외부 소비자 확인

- `grep -rn "features/calendar-picker" src` (슬라이스 외부): `src/shared/lib/pub-sub/events.ts:7` 주석 참조 1건뿐. 실제 import 소비처 없음 (`pages/` 미배선 상태).
- 결론: **외부 파손 위험 0**, 슬라이스 내부 상대경로만 remap하면 됨.

## 3. 내부 참조(상대경로) 지도 — 이동 시 깨지는 지점

| 파일(현재) | import 대상 | 현재 상대경로 | 이동 후 필요 경로 |
|---|---|---|---|
| `ui/index.ts` | useCalendarPicker | `./hook/useCalendarPicker` | `../model/useCalendarPicker` |
| `ui/index.ts` | useWeekFromClickBehavior | `./hook/behaviors/useWeekFromClickBehavior` | `../model/behaviors/useWeekFromClickBehavior` |
| `ui/index.ts` | useFreeRangeBehavior | `./hook/behaviors/useFreeRangeBehavior` | `../model/behaviors/useFreeRangeBehavior` |
| `ui/index.ts` | types | `./types` | `../model/types` |
| `ui/calendar-picker.tsx` | useDateRangeState, SELECT_TYPE | `./hook/useDateRangeState` | `../model/useDateRangeState` |
| `ui/calendar-picker.tsx` | types | `./types` | `../model/types` |
| `ui/calendar-picker.tsx` | getNormalizedDateValue | `./utils/date-range` | `../lib/date-range` |
| `ui/calendar-picker.tsx` | (신규) buildCalendarCells | 없음(인라인 L200-253) | `../lib/calendar-cells` |
| `ui/DateRangeField.tsx` | useCalendarPicker | `./hook/useCalendarPicker` | `../model/useCalendarPicker` |
| `ui/DateRangeField.tsx` | types | `./types` | `../model/types` |
| `model/useCalendarPicker.ts`(신규 위치) | types | (구)`../types` | `./types` |
| `model/useDateRangeState.ts`(신규 위치) | types | (구)`../types` | `./types` |
| `model/pub-sub.events.ts`(신규 위치) | types | (구)`./types` | `./types` (변경 없음, 동일 폴더) |
| `model/behaviors/useCalendarBehavior.ts`(신규 위치) | types | (구)`../../types` | `../types` |
| `model/behaviors/useFreeRangeBehavior.ts`(신규 위치) | types | (구)`../../types` | `../types` |
| `model/behaviors/useFreeRangeBehavior.ts`(신규 위치) | selectFreeRange | (구)`../../utils/date-range` | `../../lib/date-range` |
| `model/behaviors/useWeekFromClickBehavior.ts`(신규 위치) | types | (구)`../../types` | `../types` |
| `model/behaviors/useWeekFromClickBehavior.ts`(신규 위치) | selectWeekFromClick | (구)`../../utils/date-range` | `../../lib/date-range` |
| `lib/date-range.ts`(신규 위치) | DateRange 타입 | (구)`../types` | `../model/types` |

`./useCalendarBehavior` (behaviors 내부 상호참조)는 동일 디렉터리 이동이므로 변경 없음.

## 4. 문서 참조 동기화 필요 지점

- `src/ARCHITECTURE.md` L43 — `features/calendar-picker/ui/pub-sub.events.ts` 경로 표기
- `.claude/logs/dependency/2026-07-03-fsd-layer-contract.md` L95 — 동일 경로 표기 (ADR-2)

## 5. 재사용 가능 자산 탐색 (Agent A/B 관점 취합)

- **유사 기존 패턴**: `entities/dao/model/pub-sub.events.ts` — 도메인 pub-sub 선언병합의 표준 위치 예시로 그대로 참조 가능(추상화 내부까지 볼 필요 없음, 위치 패턴만 확인).
- **형제 feature 슬라이스 컨벤션**: `features/image-manager/ui/index.ts`(public API가 `ui/index.ts`에 위치) — calendar-picker도 슬라이스 루트 `index.ts` 신설 없이 동일 컨벤션 유지가 일관적.
- **`src/components/` 재사용 자산**: 이번 작업은 기존 로직의 위치 이동 + 1개 순수 함수 추출이며, 신규 UI 컴포넌트 생성이 없어 `src/components/` 탐색 결과 재사용 대상 없음(대상 외).
- **domain data flow / DTO 패턴 (Agent C 관점)**: calendar-picker는 API 호출이 없는 순수 UI+pubsub 흐름(fetch/DTO 없음) — 해당 없음.

## 6. tsc 베이스라인 실측

- `tsc --noEmit` 결과: **0 errors** (2026-07-06 기준). 게이트 목표: 재배치 후에도 0 유지.
