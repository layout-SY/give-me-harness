# Plan — calendar-picker 추상화 재설계

> 작성일: 2026-04-29
> 작업 유형: refactor (hybrid — 버그 수정 포함)
> 기반 문서: evaluation-log.md, architecture-discussion.md
> 담당 Planner: claude-sonnet-4-6

---

## Request Summary

`src/components/calendar-picker/` 전체 구조를 5-Layer + Behavior Injection 패턴으로 재설계한다.  
핵심 원칙: **"컴포넌트는 메커니즘만 안다. 훅은 정책을 안다. 사용처는 의도만 안다."**

---

## Work Type

hybrid (버그 수정 P1/P2 + 구조 리팩터링 + 신규 자산 생성)

---

## 1. Goals

| # | 목표 | 성공 기준 |
|---|---|---|
| G1 | 닫기 책임을 컴포넌트로 수렴 | `close-calendar-picker` publish를 사용처에서 0건으로 |
| G2 | pubsub 이벤트 이름을 사용처에서 제거 | `"open-calendar-picker"` / `"close-calendar-picker"` 문자열을 사용처 코드에서 0건으로 |
| G3 | 정책 변경 시 컴포넌트·사용처 수정 0건 | Behavior Contract 내 함수만 교체하면 전파 종료 |
| G4 | `_handleClose` Year/Month 버그 해결 | 달력 닫기 후 재오픈 시 연도 정상 표시 |
| G5 | 사용처 보일러플레이트 30줄 → 5줄 | `<DateRangeField>` 도입으로 사용처 코드 량 감소 |

---

## 2. Non-Goals

- 다른 전역 팝업(image-upload 등)의 pubsub 패턴 변경은 이번 작업 범위 밖이다. calendar-picker에 한정한다.
- Headless 패턴(Layer 강 — `useCalendarLogic()` + 사용처 직접 UI 조립)은 비범위다. Slot 주입(약) 수준까지만 도입한다.
- 단위 테스트 코드 작성은 이번 플랜의 구현 범위 밖이다. 단위 테스트가 가능한 구조로의 분리는 목표에 포함된다.
- `suspend.popup.tsx`의 단일 날짜(startDate만 전달, endDate 없음) 사용처를 위한 `single-date` 모드 추가는 Phase 2 인벤토리 결과 후 결정한다.

---

## 3. Scope

**In-scope:**

- `src/components/calendar-picker/calendar-picker.tsx` 내부 레이어 분리 및 리팩터링
- `src/components/calendar-picker/hook/useCalendar.ts` deprecated 처리 + `useCalendarPicker` 신규 생성
- `src/components/calendar-picker/` 하위 신규 파일 생성 (L1 순수 함수, L2 상태 훅, L4 도메인 훅, L5 표현 컴포넌트)
- 사용처 11개 파일 마이그레이션 (아래 인벤토리 참조)

**Out-of-scope:**

- `src/hooks/use-pub-sub/events.ts` PubSubEvents 타입 자체의 구조 변경
- 다른 컴포넌트의 pubsub 패턴
- 백엔드 API 변경

---

## 4. 사용처 정책 인벤토리 (Phase 0 선결 결과)

코드 탐색을 통해 사용처 11개의 실제 정책 차이를 사전 분류한다.

| 사용처 파일 | 접근 방식 | autoSelectOneWeek | 정책 분류 | 비고 |
|---|---|---|---|---|
| `dao/proposal-manage/create/_id.modal.tsx` | `useCalendar` | true (하드코딩) | `week-from-click` | form 필드: voteStartAt/voteEndAt |
| `dao/proposal-manage/detail/_id.modal.tsx` | `useCalendar` | true (하드코딩) | `week-from-click` | form 필드: voteStartAt/voteEndAt |
| `events/attendance/create/info.module.tsx` | pubsub 직접 | 미전달 (undefined) | `free-range` + 도메인 id/code 자동 계산 | startDate 기반으로 id(`900yyyyMM`), code(`yyyy_MM_ATTENDANCE`) 파생 — 추가 콜백 로직 존재 |
| `events/attendance/_id/info.module.tsx` | pubsub 직접 | 미전달 | `free-range` | ISO 변환: `new Date(\`\${date}T00:00:00\`).toISOString()` |
| `events/roulette/create/info.module.tsx` | pubsub 직접 | 미전달 | `free-range` + 도메인 id/code 자동 계산 | startDate 기반으로 id(`901yyyyMM`), code(`yyyy_MM_ROULETTE`) 파생 |
| `events/roulette/_id/info.module.tsx` | pubsub 직접 | 미전달 | `free-range` | ISO 변환 |
| `manage/sales/index.tsx` | pubsub 직접 | 미전달 | `free-range` | 검색 필터용, `handleDateSelect` callback 분리 |
| `manage/usage/calls/index.tsx` | pubsub 직접 | 미전달 | `free-range` | 검색 필터용 |
| `manage/usage/soria/index.tsx` | pubsub 직접 | 미전달 | `free-range` | 검색 필터용 |
| `manage/usage/item/index.tsx` | pubsub 직접 | 미전달 | `free-range` | 검색 필터용 |
| `manage/users/suspend.popup.tsx` | pubsub 직접 | 미전달 | `single-date` (endDate 없음) | startDate만 전달, 정지 날짜 단건 선택 |

**인벤토리 결론:**

- `autoSelectOneWeek: true`를 명시적으로 전달하는 곳: DAO 2개 뿐
- `autoSelectOneWeek`를 아예 전달하지 않는 곳: 9개 (즉, 해당 플래그는 실질적으로 DAO 전용 정책)
- 정책 유형 3종: `week-from-click` (DAO 2), `free-range` (events 4 + usage 4), `single-date` (users/suspend 1)
- `week-from-click`은 `autoSelectOneWeek: true`의 명시적 이름 대체이며 DAO 전용 prim 훅으로 캡슐화 가능
- `free-range`는 공용 기본 동작이므로 별도 prim 훅 불필요 (기본값으로 충분)
- `single-date`는 endDate 없는 예외 케이스로 `suspend.popup`에만 해당 — Phase 2에서 처리 방식 결정

---

## 5. Behavior Contract 초안

```ts
type DateRange = {
  startDate: string;  // "YYYY-MM-DD" 형식
  endDate: string;    // "YYYY-MM-DD" 형식
};

type CalendarBehaviors = {
  initialRange?: Partial<DateRange>;
  onSelectDate: (date: Date, current: Partial<DateRange>) => Partial<DateRange>;
  isDateDisabled?: (date: Date) => boolean;
  isDateHighlighted?: (date: Date) => boolean;
  validate?: (range: Partial<DateRange>) => string | null;
};
```

**도메인 Hook 네이밍 컨벤션:** `use{Domain}{Mode}Behavior`

- `useWeekFromClickBehavior(opts)` — DAO 투표 기간 (7일 자동 선택)
- `useFreeRangeBehavior(opts)` — 이벤트 기간, 검색 필터 (자유 범위 선택)
- `useSingleDateBehavior(opts)` — 단건 날짜 선택 (suspend 정지일) — Phase 2 결정 대기

**prim 훅 (공통 래퍼):**

- `useCalendarBehavior({ mode, constraints })` — 도메인 훅들이 내부적으로 호출하는 단일 공통 베이스
- 도메인 훅은 prim 훅의 얇은 래퍼로, 도메인 인자를 prim 훅의 mode/constraints로 번역한다

---

## 6. 5-Layer 구조 정의

```
L5. <DateRangeField />
    - 사용처 90%가 사용하는 표현 컴포넌트
    - props: value(DateRange), onChange(DateRange), behaviors, disabled, label
    - 내부: TextInput × 2 + separator + IconButton + useCalendarPicker 호출
    - 파일: src/components/calendar-picker/DateRangeField.tsx

L4. useCalendarPicker(behaviors)
    - pubsub open/close를 완전 캡슐화
    - behaviors: CalendarBehaviors를 받아 open 시 payload로 전달
    - handleOpen, handleClose 반환 (pubsub 이름 미노출)
    - 내부적으로 pubsub 유지 (프로젝트 컨벤션 비대칭 회피)
    - 파일: src/components/calendar-picker/hook/useCalendarPicker.ts

L3. <CalendarPicker /> (리팩터링)
    - behaviors를 open 이벤트 payload로 수신
    - 정책 무지: behaviors.onSelectDate 호출만 수행
    - handleConfirm 후 _handleClose 자동 호출 (G1)
    - _handleClose Year/Month 버그 수정 (G4)
    - 파일: src/components/calendar-picker/calendar-picker.tsx (수정)

L2. useDateRangeState()
    - start/end 선택, 월 이동, selectType 전환 순수 React 상태 훅
    - CalendarPicker 내부에서만 사용
    - 파일: src/components/calendar-picker/hook/useDateRangeState.ts

L1. date-range.ts (순수 함수)
    - selectDate(date, current, type): DateRange
    - autoSelectWeek(date, offsetDays): DateRange
    - normalizeRange(range): DateRange
    - getNormalizedDateValue(dateStr): string | undefined
    - 파일: src/components/calendar-picker/utils/date-range.ts
```

**단방향 의존 규칙:** L5 → L4 → L3 → L2 → L1. 역방향 의존 금지.

---

## 7. Phase별 단계적 구축 시퀀스

### Phase 0 — 사용처 정책 인벤토리화 (완료)

- 산출물: 이 plan.md 내 인벤토리 표 (섹션 4)
- 담당: planner (탐색 전용)
- 완료 조건: 11개 사용처의 정책 유형이 분류되고 contract 최소 형태 결정됨

---

### Phase 1 — 즉시 버그 수정 (P1 + P2)

**작업 산출물:**

- `src/components/calendar-picker/calendar-picker.tsx` 수정
  - L102: `setCurrentYear(new Date().getMonth())` → `setCurrentMonth(new Date().getMonth())`
  - L191-196: `handleConfirm` 끝에 `_handleClose()` 호출 추가

- 사용처 11개에서 콜백 내 `pubsub.publish("close-calendar-picker")` 제거
  - `dao/proposal-manage/create/_id.modal.tsx`
  - `dao/proposal-manage/detail/_id.modal.tsx`
  - `events/attendance/_id/info.module.tsx`
  - `events/roulette/_id/info.module.tsx`
  - `manage/sales/index.tsx`
  - `manage/usage/calls/index.tsx`
  - `manage/usage/soria/index.tsx`
  - `manage/usage/item/index.tsx`
  - `manage/users/suspend.popup.tsx`

  (attendance/create, roulette/create는 현재 콜백 내 close publish가 없으므로 수정 불필요)

**참조 SKILL:** `.claude/skills/coding-convention/SKILL.md`

**담당 에이전트:** refactorer

**완료 조건:**
- `_handleClose`에서 setCurrentYear가 두 번 호출되는 코드가 0건
- `handleConfirm` 호출 후 팝업이 자동으로 닫힘
- 사용처 콜백에서 `close-calendar-picker` publish 호출이 0건
- watcher 검증 게이트 통과

---

### Phase 2 — Behavior Contract + L1(순수 함수) + L2(상태 훅) 구축

**작업 산출물:**

- `src/components/calendar-picker/utils/date-range.ts` (신규)
  - `selectDate`, `autoSelectWeek`, `normalizeRange`, `getNormalizedDateValue` 순수 함수

- `src/components/calendar-picker/hook/useDateRangeState.ts` (신규)
  - start/end range 상태, 월 이동, selectType 관리 훅

- `src/components/calendar-picker/types.ts` (신규)
  - `DateRange`, `CalendarBehaviors` 타입 정의

- `src/components/calendar-picker/calendar-picker.tsx` (수정)
  - 내부 날짜 계산 로직을 L1 함수 호출로 교체
  - `useDateRangeState`로 상태 관리 위임
  - behaviors prop 수신 및 `behaviors.onSelectDate` 호출 구조로 전환
  - `isAutoSelectOneWeek` 내부 상태 제거 (behavior injection으로 대체)

**참조 SKILL:** `.claude/skills/coding-convention/SKILL.md`

**담당 에이전트:** refactorer

**완료 조건:**
- `calendar-picker.tsx`에 날짜 계산 인라인 로직이 0건 (모두 L1 함수 위임)
- `CalendarBehaviors` 타입이 types.ts에 단일 정의됨
- 기존 동작(Phase 1 완료 기준)과 동일하게 작동
- watcher 검증 게이트 통과

---

### Phase 3 — L4 `useCalendarPicker` + 도메인 prim 훅 구조 도입

**작업 산출물:**

- `src/components/calendar-picker/hook/useCalendarPicker.ts` (신규)
  - open/close pubsub 완전 캡슐화
  - `handleOpen(behaviors: CalendarBehaviors)` 반환
  - pubsub 이름 문자열 미노출

- `src/components/calendar-picker/hook/behaviors/useCalendarBehavior.ts` (신규, prim)
  - `mode: "week-from-click" | "free-range" | "single-date"` 수신
  - `constraints: { disablePast?: boolean; maxRangeDays?: number }` 수신
  - `CalendarBehaviors` 반환

- `src/components/calendar-picker/hook/behaviors/useWeekFromClickBehavior.ts` (신규)
  - prim 훅의 얇은 래퍼, DAO 도메인 전용
  - 내부에서 `useCalendarBehavior({ mode: "week-from-click" })` 호출

- `src/components/calendar-picker/hook/behaviors/useFreeRangeBehavior.ts` (신규)
  - prim 훅의 얇은 래퍼, 검색 필터 / 이벤트 기간 전용

- `src/hooks/use-pub-sub/events.ts` (수정)
  - `open-calendar-picker` payload에 `behaviors: CalendarBehaviors` 필드 추가
  - `autoSelectOneWeek` 필드 deprecated 표시

- `src/components/calendar-picker/hook/useCalendar.ts` (deprecated 처리)
  - JSDoc `@deprecated` 태그 추가
  - 내부적으로 `useCalendarPicker` 호출로 위임 (삭제는 Phase 6)

**참조 SKILL:** `.claude/skills/coding-convention/SKILL.md`

**담당 에이전트:** generator (신규 파일), refactorer (기존 파일 수정)

**완료 조건:**
- `useCalendarPicker`가 open/close 양쪽을 모두 캡슐화
- 도메인 hook 2종(`useWeekFromClickBehavior`, `useFreeRangeBehavior`) 작동
- `useCalendar.ts`에 `@deprecated` 표시됨
- watcher 검증 게이트 통과

---

### Phase 4 — L5 `<DateRangeField>` 표현 컴포넌트 추출

**작업 산출물:**

- `src/components/calendar-picker/DateRangeField.tsx` (신규)
  - props: `value: Partial<DateRange>`, `onChange: (range: DateRange) => void`, `behaviors: CalendarBehaviors`, `disabled?: boolean`, `label?: string`
  - 내부: `useCalendarPicker` 호출 + TextInput × 2 + separator + IconButton
  - slot: `slots?: { trigger?: ReactNode }` — 아이콘 교체 허용 (약한 Slot 주입)

- `src/components/calendar-picker/index.ts` (수정)
  - `DateRangeField` export 추가

**참조 SKILL:** `.claude/skills/coding-convention/SKILL.md`, `.claude/skills/reference/components/DOMAIN_COMPONENTS.md`

**담당 에이전트:** generator

**완료 조건:**
- `<DateRangeField>` 단독 렌더 동작 확인
- TextInput + IconButton 조합을 컴포넌트 외부에서 직접 조립하지 않아도 됨
- watcher 검증 게이트 통과

---

### Phase 5 — 사용처 11개 마이그레이션

마이그레이션 우선순위 및 담당:

**그룹 A — DAO (useCalendar 사용, 2개)** — 우선 처리
- `dao/proposal-manage/create/_id.modal.tsx`
- `dao/proposal-manage/detail/_id.modal.tsx`
- 전환: `useCalendar` → `useWeekFromClickBehavior` + `<DateRangeField>`
- 담당: refactorer

**그룹 B — Events (pubsub 직접, 4개)** — 그룹 A 완료 후
- `events/attendance/create/info.module.tsx` — id/code 파생 로직은 `onConfirm` 내 유지, behaviors는 `useFreeRangeBehavior`
- `events/attendance/_id/info.module.tsx`
- `events/roulette/create/info.module.tsx` — id/code 파생 로직은 `onConfirm` 내 유지
- `events/roulette/_id/info.module.tsx`
- 전환: 인라인 pubsub → `useFreeRangeBehavior` + `<DateRangeField>`
- 담당: refactorer

**그룹 C — Usage/Sales (pubsub 직접, 4개)** — 그룹 B와 병렬 가능
- `manage/sales/index.tsx`
- `manage/usage/calls/index.tsx`
- `manage/usage/soria/index.tsx`
- `manage/usage/item/index.tsx`
- 전환: 인라인 pubsub → `useFreeRangeBehavior` + `<DateRangeField>`
- 담당: refactorer

**그룹 D — Users (단일 날짜, 1개)** — Phase 2 결정 이후 처리
- `manage/users/suspend.popup.tsx`
- `useSingleDateBehavior` 또는 `useFreeRangeBehavior`의 endDate 선택적 처리로 커버할지 결정 후 진행
- 담당: refactorer

**각 그룹별 완료 조건:**
- 해당 파일에서 `"open-calendar-picker"` / `"close-calendar-picker"` 문자열 0건
- `useCalendar` import 0건 (그룹 A)
- 동작 회귀 없음
- 개별 watcher 검증 게이트 통과

---

### Phase 6 — 기존 자산 정리 및 deprecated 제거

**작업 산출물:**

- `src/components/calendar-picker/hook/useCalendar.ts` 삭제
- `src/hooks/use-pub-sub/events.ts` — `autoSelectOneWeek` 필드 완전 제거
- `src/components/calendar-picker/calendar-picker.tsx` — `isAutoSelectOneWeek` 관련 잔여 코드 최종 정리

**담당 에이전트:** refactorer

**완료 조건:**
- 프로젝트 전체에서 `useCalendar` import 0건
- `autoSelectOneWeek` 필드 참조 0건
- `yarn lint && tsc --noEmit` 통과
- watcher 최종 검증 게이트 통과

---

## 8. Migration 안전 장치

### 신구 병존 전략

| 자산 | 현재 상태 | 전환 상태 | 삭제 시점 |
|---|---|---|---|
| `useCalendar.ts` | 활성 | Phase 3에서 `@deprecated`, 내부를 `useCalendarPicker`로 위임 | Phase 6 |
| `autoSelectOneWeek` payload 필드 | 활성 | Phase 3에서 `@deprecated` 표시 | Phase 6 |
| 인라인 pubsub 호출 (8개 파일) | 활성 | Phase 5 그룹별 순차 제거 | Phase 5 완료 시점 |

Phase 3 완료 ~ Phase 5 완료 기간 동안 구 패턴(pubsub 직접)과 신 패턴(`useCalendarPicker`)이 공존한다. CalendarPicker 컴포넌트는 두 패턴 모두를 수신해야 하므로, Phase 3에서 `calendar-picker.tsx`가 구 payload(autoSelectOneWeek)와 신 payload(behaviors) 양쪽을 처리하는 호환 레이어를 잠시 유지한다.

### 마이그레이션 검증 게이트 (watcher 체크리스트)

각 Phase/그룹 완료 시 watcher가 아래 항목을 검증한다:

1. `yarn lint` 오류 0건
2. `tsc --noEmit` 타입 오류 0건
3. 해당 사용처 파일에 `"open-calendar-picker"` / `"close-calendar-picker"` 문자열 잔존 여부
4. `handleConfirm` 호출 후 팝업 자동 닫힘 (Phase 1 완료 후 전 사용처)
5. 달력 닫기 후 재오픈 시 연도 정상 표시 (Phase 1 완료 기준)

---

## 9. 위험 요소 / 결정 필요 사항

| # | 항목 | 현재 결정 | 결정 대기 |
|---|---|---|---|
| R1 | 다중 인스턴스 가정 (콜백 슬롯 경쟁) | 단일 인스턴스 유지. 어드민 구조상 동시 오픈 시나리오가 현실적이지 않으므로 현재 Phase에서 큐잉 도입 안 함 | 페이지 복잡도 증가 시 재검토 |
| R2 | L4 내부 pubsub 유지 vs Context 전환 | pubsub 유지 (프로젝트 컨벤션 비대칭 회피). 사용처는 여전히 pubsub을 모름 | - |
| R3 | `suspend.popup` 단일 날짜 탈출구 | Phase 2 완료 후 `useSingleDateBehavior` 추가 또는 `useFreeRangeBehavior`의 optional endDate 처리로 커버 결정 | Phase 2 완료 시점 |
| R4 | attendance/roulette create의 id/code 파생 로직 | `onConfirm` 콜백 내 도메인 로직은 사용처에 유지. behaviors와 분리된 책임이므로 컴포넌트/훅으로 흡수 안 함 | - |
| R5 | `DateRangeField`가 커버 못하는 사용처 (detail 모달 등) | L4 `useCalendarPicker`를 직접 호출하고 트리거 버튼을 직접 작성하는 탈출구 유지. L5 강제 사용 금지 | - |
| R6 | Phase 3 호환 레이어 기간 | Phase 5 그룹 D 완료 전까지 구 payload 처리 코드가 `calendar-picker.tsx` 내 잔존 | Phase 6에서 일괄 제거 |

---

## 10. Required Agents

| Phase | 에이전트 | 역할 |
|---|---|---|
| Phase 0 | planner | 사용처 인벤토리, 계획 수립 |
| Phase 1 | refactorer | 버그 수정, close 책임 수렴 |
| Phase 2 | refactorer | L1 순수 함수 추출, L2 상태 훅 분리, CalendarPicker 리팩터링 |
| Phase 3 | generator + refactorer | L4 hook + prim 훅 신규 생성, events.ts 수정, useCalendar deprecated |
| Phase 4 | generator | L5 DateRangeField 신규 생성 |
| Phase 5 A-D | refactorer | 사용처 마이그레이션 |
| Phase 6 | refactorer | 정리 및 deprecated 제거 |
| 전 Phase | watcher | 각 Phase 완료 시 검증 게이트 |

---

## 11. Required Skills

- `.claude/skills/coding-convention/SKILL.md`
- `.claude/skills/review-checklist/SKILL.md`
- `.claude/skills/reference/components/DOMAIN_COMPONENTS.md`

---

## 12. Artifacts Checklist

- [x] `plan.md` — 이 문서
- [ ] `exploration.md` — Phase 0 사용처 인벤토리 (이 plan.md 섹션 4에 통합)
- [ ] `implementation-log.md` — Phase 1~6 구현 기록
- [ ] `review-log.md` — watcher 검증 결과
- [ ] `evaluation-log.md` — 기존 작성 완료
- [ ] `final-summary.md` — 전체 파이프라인 완료 후 작성

---

## Approval Request

이 계획대로 진행할까요, 아니면 조정할 부분이 있나요?
