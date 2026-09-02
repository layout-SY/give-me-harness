# Evaluation Log

## Context
- 대상: `src/components/calendar-picker`, `src/components/calendar-picker/hook/behaviors/useCalendarBehavior.ts`
- 범위: 공용 캘린더 사용처/추상화 수준/의존 관계/구현 방식/SOLID·KISS·YAGNI·DRY 관점 정적 평가
- 방식: `evaluator` 위임 결과 + 로컬 코드 라인 교차검증
- 사용자 요청 조건: 코드 변경 없이 평가 문서화

## Structural Risks
1. **P1 — 계층 의존 역전 (`src/utils` → `src/components`)**
- 근거: `src/utils/date.util.ts:4`에서 `FreeRangeSelectType`을 `~/components/calendar-picker/utils/date-range`에서 import.
- 추가 맥락: `src/components/calendar-picker/utils/date-range.ts:9`는 다시 `~/utils/date.util` 의존.
- 리스크: 공용 유틸 레이어가 UI 컴포넌트 레이어 타입을 알아야 하므로 경계가 약화됨.

2. **P1 — 계약과 구현 불일치 (`maxRangeDays`, `validate`, `isDateHighlighted`)**
- 근거: `src/components/calendar-picker/hook/behaviors/useCalendarBehavior.ts:23-26,39,59`, `src/components/calendar-picker/types.ts:55-56`.
- 리스크: 외부 소비자는 범위 제한/검증이 동작한다고 인식할 수 있으나 실제 실행 경로가 없음.

3. **P2 — `CalendarPicker` 단일 파일 책임 과밀 (SRP 약화)**
- 근거:
  - 오케스트레이션: `src/components/calendar-picker/calendar-picker.tsx:62-114`
  - 정책 실행/상태 전이: `src/components/calendar-picker/calendar-picker.tsx:116-159,173-179`
  - Grid 계산/렌더: `src/components/calendar-picker/calendar-picker.tsx:200-253`
  - Controls 렌더: `src/components/calendar-picker/calendar-picker.tsx:161-171,334-370`
- 리스크: UI/정책/이벤트 처리 변경이 단일 파일로 집중되어 변경 충돌과 회귀 가능성 증가.

4. **P2 — behavior memo 의도 대비 dependency 불안정**
- 근거: `src/components/calendar-picker/hook/behaviors/useCalendarBehavior.ts:59` + 소비처에서 inline object 생성 (`src/pages/manage/sales/index.tsx:133-135,325-328` 등).
- 리스크: `initialRange` 참조가 매 렌더 달라져 메모 이점 저하.

5. **P2 — 전역 pubsub 이벤트 타입이 UI 계약에 결합**
- 근거: `src/hooks/use-pub-sub/events.ts:3,12-20`.
- 리스크: hooks/global 이벤트 계층이 특정 컴포넌트 타입을 직접 의존.

6. **P3 — 공용 계층 하드코딩 라벨/타이틀**
- 근거: `src/components/calendar-picker/hook/behaviors/useWeekFromClickBehavior.ts:65`, `src/components/calendar-picker/DateRangeField.tsx:89`, `src/components/calendar-picker/calendar-picker.tsx:296,311,316`.
- 리스크: i18n/접근성 정책 일관성 저하.

## Why This Matters
- `DateRangeField`/behavior 훅이 다수 화면에서 이미 공용 사용 중이라(`src/pages/manage/*`, `src/pages/dao/*`) 경계 설계 품질이 전체 유지보수 비용에 직접 영향.
- 현재 구조는 OCP(정책 주입)는 좋지만, SRP/ISP/YAGNI 측면에서 누적 리스크가 존재.
- 특히 P1 두 항목은 “오해 가능한 계약”과 “계층 경계 붕괴”라 후속 기능 추가 시 결함 전파 가능성이 큼.

## Improvement Options
1. **최소 변경(권장 1차)**
- `date.util`에서 calendar 전용 타입 의존 제거.
- 미사용 계약(`maxRangeDays`, `validate`, `isDateHighlighted`)은 제거 또는 즉시 구현 중 하나로 결정.

2. **중간 변경(권장 2차)**
- `CalendarPicker`를 SRP 단위로 분리:
  - `useCalendarModalController` (pubsub/open-close/init)
  - `useCalendarSelection` (onSelectDate/onControlsChange/confirm)
  - `CalendarGrid` (셀 계산/렌더)
  - `CalendarControls` (control 렌더)

3. **확장 변경(선택)**
- pubsub payload 계약을 shared event contract로 승격.
- behavior strategy 계약을 명시적으로 분리해 전역 타입 결합 완화.

## Recommended Backlog
1. **P1** `src/utils/date.util.ts`의 `calendar-picker` 타입 import 제거.
2. **P1** `CalendarBehaviors` 계약 정리(제거 vs 구현) 의사결정 및 반영.
3. **P2** `useCalendarBehavior` deps를 primitive 기준으로 정리.
4. **P2** `CalendarPicker` 내부 역할 분리 리팩터.
5. **P3** 공용 라벨/타이틀 i18n 정리.

## Suggested Next Step
- 코드 변경을 시작한다면, P1 2개를 먼저 고정하고 이후 P2 SRP 분리를 진행하는 2단계 리팩터가 안전하다.

## Methodology Update (grill-me 적용 방식 보정)
- 이번 라운드의 질의는 "문제 지점(가설) 선확정 → 검증 질문 생성" 순서로 진행되었다.
- 다음 라운드부터는 `grill-me`를 아래 규칙으로 적용한다.
1. **중립 질문 선행**: 결론/문제 가설 없이 의사결정 트리 질문부터 시작한다.
2. **단일 질문 진행**: 한 번에 한 질문만 제시하고 답변/코드근거를 확정한다.
3. **분기 기반 결론**: 각 질문의 Yes/No 분기 결과를 누적해 결론을 도출한다.
4. **코드 우선 검증**: 코드로 답 가능한 질문은 사용자 확인 전 먼저 코드에서 확정한다.
5. **최종 리스크 판정 후순위화**: 모든 분기 확정 이후 P0~P3를 매긴다.

### Neutral Question Tree (다음 평가 시작점)
1. `CalendarBehaviors` 계약 항목 중 실제 런타임에서 소비되는 항목은 무엇인가?
2. 전역 pubsub 이벤트 계약은 UI 계층 타입과 분리 가능한가?
3. `CalendarPicker`의 변경 사유는 실제로 몇 개인가(이벤트/정책/UI/렌더)?
4. 소비처는 `DateRangeField` 단일 진입으로 충분한가, 예외가 필요한가?
5. 성능 최적화(useMemo deps)는 측정 가능한 이득이 있는가?
