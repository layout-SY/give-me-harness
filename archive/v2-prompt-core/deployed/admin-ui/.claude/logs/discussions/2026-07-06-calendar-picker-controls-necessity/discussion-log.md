# Calendar-picker `controls` 필요성 검토 (Discussion Log)

> 일자: 2026-07-06
> 유형: 아키텍처 이해/검토 (코드 변경 없음)
> 대상: `src/components/calendar-picker/**`, 특히 `hook/behaviors/useWeekFromClickBehavior.ts` 의 `controls` / `onControlsChange`
> 결론: **현행 유지 (keep as-is)**

---

## 배경 질문

"`controls`(모달 내 기간 입력 UI + 재계산 로직)가 굳이 별도 기능으로 필요한가? `onSelectDate` 안에서 기간을 다루고 시작/종료만 받으면 되는 것 아닌가? 정책이 고정이라면 calendar-picker에 직접 박으면 되지 않나?"

---

## 핵심 사실 정리

### 1. `controls`는 "날짜 선택 UI"가 아니라 "offset 숫자 입력창"이다
- 날짜 선택 UI(달력 그리드)는 `controls`와 무관하게 항상 렌더된다. 클릭 반영은 `onSelectDate` 책임.
- `controls`는 그리드 위에 붙는 **별도 숫자 입력 위젯(기간 일수)** 의 렌더 명세일 뿐이다.

### 2. `onSelectDate` 단독으로 `controls`를 대체할 수 없는 이유 (기계적 제약)
- `onSelectDate`는 (a) **날짜 클릭 시에만** 호출되고, (b) range를 return하는 **순수 함수**다. UI를 그리거나 입력창 변경 이벤트를 받을 수 없다.
- 따라서 "모달 내 입력창을 유지"하면서 `controls`/`onControlsChange`를 없애는 것은 **불가능**하다.
  - 입력창 유지 → `controls` 제거 불가 (렌더 주체 + 변경 핸들러가 반드시 필요)
  - 입력창 폐기 → `controls` 제거 가능

### 3. `week-from-click` 과 `free-range` 는 상하(상위호환) 관계가 아니라 "다른 클릭 의미"다
- `week-from-click`: 클릭 1번 = start + offset 로 **고정 폭 범위 통째** 생성. 종료일을 그리드에서 직접 못 찍음.
- `free-range`: 클릭 2번 = 시작·종료를 각각 **임의로** 지정. offset 개념 없음. 검색 필터(sales/usage 등 9곳)가 사용.
- 이 둘은 **offset 숫자 하나로 매개변수화(전환)할 수 없다.** 클릭 semantics 자체가 다르기 때문.

### 4. 추상화(behaviors/controls 주입)가 정당한 유일한 이유
- 현재 사용처의 **선택 정책이 2종(week-from-click / free-range)으로 실제로 갈리기 때문**이다.
- 정책이 하나로 고정된다면 이 추상화(계약/슬롯/도메인 훅/주입)는 존재 이유가 사라지고 calendar-picker + 유틸로 인라인 가능하다. (그리드가 모두가 원해서 박혀있는 것과 동일 논리)

---

## 검토한 단순화 후보

| 안 | calendar에 고정할 단일 로직 | offset 입력창 | 추상화 | 대가 |
|---|---|---|---|---|
| 현행 | 훅 주입(정책 2종) | 옵션(`controls: true`) | 유지 | 복잡도 (단, 실제 정책 차이를 반영) |
| X | 클릭 → start+offset + offset 입력창 | calendar에 고정 | 전부 제거 | **검색 필터가 종료일 클릭 불가** → 일수를 숫자로 타이핑해야 함 |
| Y | 시작클릭=자동채움, 종료클릭=override | **불필요(제거)** | 전부 제거 | "기간 숫자 타이핑" 포기(대신 종료일 클릭) |

- X: 코드 최단순화. 그러나 검색 필터(임의 구간 선택)가 구조적으로 열화됨 → 실무상 곤란.
- Y: offset 입력창까지 사라져 더 깔끔하고 검색·DAO 모두 자연스러움. 단 "일수 타이핑" UX는 사라짐.

---

## 결론 및 근거

**현행 구조를 유지한다(keep as-is).**

- 단순화(X/Y)로 가려면 전제 조건은 "모든 사용처를 **하나의 선택 정책으로 통일**"이다.
- 그러나 실제로는 **두 상호작용 모델이 모두 필요**하다:
  - 검색 필터: "종료일을 그리드에서 직접 클릭"하는 임의 구간 선택(free-range)이 필수.
  - DAO 제안 생성: "한 번 클릭으로 기간 자동 채움"(week-from-click)의 편의.
- 이 둘은 offset 하나로 합칠 수 없으므로, 정책 분기를 유지하는 현재의 behavior 주입 구조가 정당하다.
- 즉 `controls`/`onControlsChange`는 "over-abstraction"이 아니라 **실제로 갈리는 정책을 표현하기 위한 최소 장치**이며, 이를 제거하면 어느 한쪽 사용처의 UX가 손상된다.

---

## 남은 정리 여지 (별도 판단 필요, 이번 결론 범위 밖)

현행 유지 결정과 별개로, 아래는 "기능 손실 없이 죽은 코드만 제거" 가능한 항목으로 이전 세션/평가에서도 지적됨. 필요 시 후속 작업으로 분리.

- `ControlSpec.kind: "preset-chips"` + `presets` + `ControlField`의 preset 분기: variable-offset 세션에서 number 입력으로 전환되며 남은 잔재. 이를 생성하는 behavior 없음.
- `controls`의 객체 형태(`{ min?, max?, label? }`): 사용처가 항상 `controls: true`(boolean)만 전달.
- `CalendarBehaviors.validate` / `isDateHighlighted` / `maxRangeDays`: 계약에만 있고 실행 경로 없음 (codex 2026-05-11 평가 P1 "계약과 구현 불일치").
- `src/utils/date.util.ts` → `~/components/calendar-picker/utils/date-range` 타입 import: 하위 유틸이 상위 UI 컴포넌트 타입을 의존하는 경계 역전 (codex 2026-05-11 평가 P1).

---

## 참고 (관련 이력)

- `.claude/logs/discussions/2026-04-29-calendar-picker-evaluation/` — 최초 평가 + Behavior Injection 방향 채택
- `.claude/logs/sessions/2026-04-29-calendar-picker-behavior-pipeline/` — free-range 포커스 토글(`nextSelectType`) 도입
- `.claude/logs/sessions/2026-04-29-calendar-picker-variable-offset/` — `controls` 슬롯 도입(preset-chips → number 전환)
- `.codex/logs/sessions/2026-05-11-calendar-picker-architecture-evaluation/` — 현행 구조 재평가(P1 dead/의존역전 지적)
