# Implementation Log — calendar-picker 리팩토링

> 실행: refactorer / 2026-07-06 / work_type: refactor
> 원칙: 기능 동작 변경 0 (behavior-preserving). 렌더 결과(className/비활성) 픽셀 동일.

## 결정 기록 (추상화 범위 / 파일 구조)

- **세그먼트 3분할 확정** (planner 승인 구조 그대로 적용): `ui`(표현) / `model`(상태·정책 훅·타입·pub-sub 계약) / `lib`(React 비의존 순수 함수).
- **public API 위치**: `ui/index.ts` 유지(형제 `image-manager` 컨벤션 일치). 슬라이스 루트 `index.ts` 신설 안 함.
- **`hook/` 폴더 폐기**: 훅을 `model/` 루트로 승격, `behaviors/` 하위만 `model/behaviors/`로 보존.
- **`utils/` 폴더 폐기**: 순수 함수를 `lib/`로 이동.
- **buildCalendarCells 추상화 판단**: policy-hook-extraction §0 Q1 단독 통과(React/pubsub 무의존 순수 파생) → `lib/calendar-cells.ts` 순수 함수로 확정. 셀별 플래그(isToday/isStart/isEnd/isInRange/isDisabled/isInMonth/day)만 반환하고 className 문자열 조립·JSX·이벤트 바인딩은 `ui`에 잔류(표현 책임 분리).
- **시그니처 확정**: `buildCalendarCells(year, month, start, end, today = new Date(), isDateDisabled?) → CalendarCell[]`. `today`는 테스트 용이성 위해 주입 가능한 선택 인자로 노출(기본값 현재 시각). 인자 Date를 변형하지 않도록 내부에서 `new Date(today)` 복제 후 정규화.
- **범위 준수**: P2(useCalendarBehavior useMemo deps, useDateRangeState setRange/setFormState 표면) 및 behavior 파이프라인 해체·훅 인라인화·공용 제네릭 훅 신설은 손대지 않음.

## 섹션 1 — 세그먼트 재배치 + import remap

파일 이동 (mv):

| before | after |
|---|---|
| `ui/types.ts` | `model/types.ts` |
| `ui/pub-sub.events.ts` | `model/pub-sub.events.ts` |
| `ui/hook/useCalendarPicker.ts` | `model/useCalendarPicker.ts` |
| `ui/hook/useDateRangeState.ts` | `model/useDateRangeState.ts` |
| `ui/hook/behaviors/useCalendarBehavior.ts` | `model/behaviors/useCalendarBehavior.ts` |
| `ui/hook/behaviors/useFreeRangeBehavior.ts` | `model/behaviors/useFreeRangeBehavior.ts` |
| `ui/hook/behaviors/useWeekFromClickBehavior.ts` | `model/behaviors/useWeekFromClickBehavior.ts` |
| `ui/utils/date-range.ts` | `lib/date-range.ts` |

빈 폴더 `ui/hook/behaviors`, `ui/hook`, `ui/utils` 제거. `ui/`엔 표현 자산(`calendar-picker.tsx/.css`, `DateRangeField.tsx/.css`, `index.ts`)만 잔류.

import remap (exploration §3 지도 전량 + grep 재확인):

- `lib/date-range.ts`: `../types` → `../model/types`
- `model/useCalendarPicker.ts`: `../types` → `./types`
- `model/useDateRangeState.ts`: `../types` → `./types`
- `model/behaviors/useCalendarBehavior.ts`: `../../types` → `../types`
- `model/behaviors/useFreeRangeBehavior.ts`: `../../types` → `../types`, `../../utils/date-range` → `../../lib/date-range`
- `model/behaviors/useWeekFromClickBehavior.ts`: `../../types` → `../types`, `../../utils/date-range` → `../../lib/date-range`
- `model/behaviors/*`의 `./useCalendarBehavior` 상호참조: 변경 없음(동일 폴더 이동)
- `model/pub-sub.events.ts`의 `./types`: 변경 없음(동일 폴더)
- `ui/index.ts`: `./hook/useCalendarPicker`→`../model/useCalendarPicker`, `./hook/behaviors/useWeekFromClickBehavior`→`../model/behaviors/useWeekFromClickBehavior`, `./hook/behaviors/useFreeRangeBehavior`→`../model/behaviors/useFreeRangeBehavior`, `./types`→`../model/types`
- `ui/DateRangeField.tsx`: `./hook/useCalendarPicker`→`../model/useCalendarPicker`, `./types`→`../model/types`
- `ui/calendar-picker.tsx`: `./hook/useDateRangeState`→`../model/useDateRangeState`, `./types`→`../model/types`, `./utils/date-range`→`../lib/date-range`, (신규) `../lib/calendar-cells`

부수: 이동으로 부정확해진 JSDoc `의존:` 표기(`../../utils/date-range`, `../../types`, `../types`) 실경로로 동기화(코드 아님, 문서 정확성).

외부 소비자: `grep -rn features/calendar-picker` 결과 슬라이스 밖 실제 import 소비처 없음(pages 미배선). 파손 위험 0 재확인.

## 섹션 2 — 계약 문서 동기화

- `src/ARCHITECTURE.md` L42: `features/calendar-picker/ui/pub-sub.events.ts` → `.../model/pub-sub.events.ts`
- `.claude/logs/dependency/2026-07-03-fsd-layer-contract.md` L95: 동일 경로 갱신
- grep 재확인: 구 경로(`ui/pub-sub.events`, `ui/hook`, `ui/utils`, `ui/types`) 잔존 0건.

## 섹션 3 — buildCalendarCells 순수 함수 추출

- 신규 `lib/calendar-cells.ts`: `CalendarCell` 타입 + `buildCalendarCells(...)`.
  - daysInMonth/firstDay/totalCells 계산 + start/end/today 자정 정규화 + 셀별 플래그 산출을 그대로 이관.
  - 동작 동일성: `start &&`/`end &&` 진위 판정을 `startTime !== null`/`endTime !== null`로 명시화(유효 타임스탬프는 항상 truthy이므로 의미 불변). isInMonth 게이팅·비교연산자(`>`, `<`, `===`)·isDateDisabled 호출 시점(자정 정규화된 date, isInMonth 시에만) 원본과 동일.
- `ui/calendar-picker.tsx` `renderCells`: 파생 로직 제거 후 `buildCalendarCells(...)` 결과를 `map`만 수행. className 조립 순서(today→start→end→in-range) 원본 보존. onClick 가드(`isInMonth && !isDisabled`) 및 `disabled`(`!isInMonth || isDisabled`), 표시값(`isInMonth ? day : ""`) 동일.

## 검증 (회귀 0)

- `tsc --noEmit`(프로젝트 품질 게이트 = tsconfig.json): **0 errors** (전체 프로젝트, calendar-picker 포함). 재배치 전 baseline 0 → 후 0 유지.
- `tsc --noEmit -p tsconfig.app.json`(erasableSyntaxOnly=true): calendar-picker에서 1건 TS1294(`model/useDateRangeState.ts:21` `const enum SELECT_TYPE`). **사전 존재**(원본 `ui/hook/useDateRangeState.ts` 동일 코드 relocate) — 신규 유입 아님. 동 tsconfig는 프로젝트 전반(dao/event/news/dialog/select-users)이 미충족하는 별도 스트릭트로, 프로젝트 quality 명령(`yarn lint && tsc --noEmit`)의 게이트가 아님.
- `eslint src/features/calendar-picker`: 신규 유입 0. 잔존 3건 모두 사전 존재 & 범위 외(§risk_notes).

## code-simplifier

- 본 실행 컨텍스트에서 하위 에이전트 spawn 도구 미제공 → refactorer가 명료성 검토를 인라인 수행.
- 추출 코드는 이미 평탄 구조·명확 네이밍·불필요 추상화 없음. 시그니처/동작 불변 원칙상 추가 단순화 여지 없음(className 조립을 lib로 밀면 표현책임 침범이라 배제). 별도 명료성 변경 없음.

---

## 사후 정정 (2026-07-06, 사용자 피드백 반영)

### 정정 1 — hook 세그먼트 분리 (model→hook)
- **피드백**: "hook이 model 안에 들어가 있으면 안되고 hook 폴더 안에 들어가 있어야지."
- 최초 재배치는 훅을 `model/`에 뒀으나, 프로젝트 규약상 훅은 전용 `hook/` 세그먼트에 둔다.
- 이동:
  - `model/useCalendarPicker.ts` → `hook/useCalendarPicker.ts`
  - `model/useDateRangeState.ts` → `hook/useDateRangeState.ts`
  - `model/behaviors/*` → `hook/behaviors/*`
- `model/` 잔여 = `types.ts`, `pub-sub.events.ts` (비-훅 도메인 자산). `lib/` = `date-range.ts`, `calendar-cells.ts`.
- import 교정: 훅 내부 `./types`→`../model/types`, `../types`→`../../model/types`(behaviors); 외부 소비처(`ui/index.ts`, `calendar-picker.tsx`, `DateRangeField.tsx`)의 `../model/<hook>`→`../hook/<hook>`.
- 계약 문서 갱신: `src/ARCHITECTURE.md`·`.claude/logs/dependency/2026-07-03-fsd-layer-contract.md` 세그먼트 표준에 `hook/` 세그먼트 명문화("훅은 model이 아니라 hook에 둔다").
- 검증: `tsc --noEmit`(tsconfig.json) **0 errors**, cannot-find 0.

### 정정 2 — 최종 세그먼트 형태
```
features/calendar-picker/
├── ui/     calendar-picker.tsx, DateRangeField.tsx, *.css, index.ts
├── hook/   useCalendarPicker.ts, useDateRangeState.ts, behaviors/*
├── model/  types.ts, pub-sub.events.ts
└── lib/    date-range.ts, calendar-cells.ts
```

### watcher 반려(1회차) 처리 — 범위 외 constants.ts
- watcher가 `src/shared/config/constants.ts`(localStorage 키 `synthoria-admin-*`→`admin-*`)를 범위 외 혼입으로 반려.
- **원인 규명**: 본 calendar-picker 파이프라인(planner/refactorer/watcher)은 constants.ts를 수정하지 않음. FSD 재설계는 이미 커밋(`3c50035`). 해당 변경은 **그 이전부터 워킹트리에 있던 별개의 미커밋 편집**(리브랜딩 성격)으로, calendar-picker와 무관.
- **조치**: calendar-picker 리팩터 범위에서 분리(원복하지 않음 — 사용자 의도 편집일 수 있어 보존). 커밋 시 calendar-picker와 별개 커밋으로 분리 권장.
