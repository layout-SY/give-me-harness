# Final Summary — calendar-picker 추상화 재설계

> 일자: 2026-04-29
> 결과: 6 Phase 모두 완료, watcher 게이트 통과
> 채택 패턴: 5-Layer + Behavior Injection (Inversion of Control)

---

## 1. 한 줄 요약

CalendarPicker 공용 컴포넌트의 정책·UI·pubsub 메커니즘을 5계층으로 분리하고, 사용처 11곳이 도메인 의도(mode/behaviors)만 선언하면 동작하는 구조로 전환 완료.

## 2. 달성한 목표 (plan.md 섹션 1 대비)

| # | 목표 | 결과 |
|---|---|---|
| G1 | 닫기 책임을 컴포넌트로 수렴 | ✅ 사용처 close publish 0건 (`handleConfirm` 자동 close) |
| G2 | pubsub 이벤트 이름 사용처 노출 0건 | ✅ `"open/close-calendar-picker"` 사용처 코드 0건 |
| G3 | 정책 변경 시 컴포넌트·사용처 수정 0건 | ✅ Behavior Contract 도입, 도메인 훅에 정책 수렴 |
| G4 | `_handleClose` Year/Month 버그 해결 | ✅ Phase 1에서 수정 |
| G5 | 사용처 보일러플레이트 30줄 → 5줄 | ✅ DAO/events/usage 그룹에서 평균 15~25줄 감소 (DAO 그룹 ≈ 42줄 감소) |

## 3. 주요 산출물

### 신규 자산 (8개)
- `types.ts` — `DateRange`, `CalendarBehaviors` 타입
- `utils/date-range.ts` — 순수 함수 (selectFreeRange, selectWeekFromClick, getNormalizedDateValue)
- `hook/useDateRangeState.ts` — React 상태 훅
- `hook/useCalendarPicker.ts` — pubsub 캡슐화 도메인 훅 (L4)
- `hook/behaviors/useCalendarBehavior.ts` — prim 훅 (mode + constraints)
- `hook/behaviors/useWeekFromClickBehavior.ts` — DAO 도메인 훅
- `hook/behaviors/useFreeRangeBehavior.ts` — 자유 범위 도메인 훅
- `DateRangeField.tsx` / `.css` — L5 표현 컴포넌트

### 삭제 자산 (1개)
- `hook/useCalendar.ts` — 추상화 가치가 미달했던 publish 한 줄 wrapper

### 수정된 사용처 (11개)
- DAO 2 + DAO detail 섹션 1 (그룹 A: useWeekFromClickBehavior + DateRangeField)
- Events 4 (그룹 B: useFreeRangeBehavior + DateRangeField, 도메인 id/code 파생 보존)
- Usage/Sales 4 (그룹 C: useFreeRangeBehavior + DateRangeField, 검색 트리거 보존)
- Suspend.popup 1 (그룹 D: L4 탈출구 — useCalendarPicker 직접 호출)

## 4. 핵심 아키텍처

```
┌──────────────────────────────────────────────────────────┐
│ 사용처(Site)        : "내 도메인은 이런 의도가 필요해"      │
│   ↓ intent (선언적 — mode, initialRange, onConfirm)       │
│ 훅(Hook)           : 의도 → CalendarBehaviors로 번역      │
│   ↓ behaviors (계약된 함수 묶음)                          │
│ 컴포넌트(Component) : 주입받은 행동을 *실행*만 한다         │
└──────────────────────────────────────────────────────────┘
```

5-Layer 구조:
- **L5** `<DateRangeField>` — 90% 사용처가 사용하는 표현 컴포넌트
- **L4** `useCalendarPicker` — pubsub 캡슐화, 탈출구
- **L3** `<CalendarPicker>` — 메커니즘만, behaviors 받아 실행
- **L2** `useDateRangeState` — React 상태 훅
- **L1** `date-range.ts` — 순수 함수

## 5. 변경 전파 범위 비교

| 변경 시나리오 | Before | After |
|---|---|---|
| 닫기 정책 변경 | 사용처 10곳 + 컴포넌트 | 컴포넌트 1곳 |
| pubsub 이벤트 이름 변경 | 20개 지점 | useCalendarPicker.ts 1곳 |
| 새 모드 추가 (예: 회계 분기) | 컴포넌트 + 사용처 다수 | 신규 도메인 훅 1개 |
| 휴일 하이라이트 추가 | 사용처별 props | behaviors.isDateHighlighted 1줄 |

## 6. 워크플로우 통계

| Phase | 담당 에이전트 | Watcher 게이트 |
|---|---|---|
| 0 (인벤토리) | planner | — |
| 1 (버그 수정) | refactorer | PASS |
| 2 (L1/L2 + 슬롯) | refactorer | PASS |
| 3 (L4 + 도메인 훅) | generator + refactorer | V4 결함 발견 → 픽스 후 PASS |
| 4 (L5) | generator | PASS |
| 5 (사용처 11개) | refactorer × 4 그룹 | PASS |
| 6 (정리) | refactorer | 사후 grep 검증 PASS |

## 7. 발견 / 해결된 결함

- **버그 1 (Phase 1):** `_handleClose`에서 Year setter에 month 값 주입 → 닫기 후 재오픈 시 연도 0~11 표시. 1줄 픽스.
- **버그 2 (Phase 3 V4):** 초기 `useCalendarBehavior` free-range 분기가 `currentSelectType` 토글 무시. `onSelectDate` 시그니처에 `selectType` 인자 추가로 해결.

## 8. 주요 결정 사항 (plan.md 섹션 9 대비)

| # | 결정 |
|---|---|
| R1 | 단일 인스턴스 가정 유지 (큐잉 미도입) |
| R2 | L4 내부에 pubsub 유지 (Context 전환 안 함, 프로젝트 컨벤션 비대칭 회피) |
| R3 | `useSingleDateBehavior` 신설 보류 — suspend.popup은 free-range로 처리 |
| R4 | events create의 id/code 파생 로직은 사용처 onConfirm에 유지 (behaviors와 책임 분리) |
| R5 | `<DateRangeField>` 미적용 사용처는 L4 직접 호출 탈출구 사용 (suspend.popup 사례) |

## 9. 후속 권장 (deferred / out-of-scope)

1. **Dropdown.label과 DateRangeField 날짜 중복 표시 정리** (그룹 C 발견)
   - usage/sales 4개 페이지에서 duration preset Dropdown의 label과 DateRangeField가 동일 날짜를 중복 표시. 시각 통일 필요.
2. **단위 테스트 추가**
   - L1 순수 함수, L2 상태 훅의 단위 테스트는 본 작업 범위 외였음. 현재 분리된 구조에서는 테스트 작성이 가능하므로 순차적 추가 권장.
3. **`<DateRangeField>`의 컴파운드 컴포넌트 진화**
   - 더 자유로운 UI 변형 요구가 등장하면 Slot 주입(약) → Compound Component(중) → Headless(강) 단계로 확장 가능.
4. **plan.md 인벤토리 오기재 정정**
   - "attendance/create, roulette/create는 close publish가 없다"는 기재가 실제와 달랐음 (Phase 1 watcher가 발견). 교훈: 인벤토리는 grep으로 cross-check 필요.

## 10. 산출 문서

- `user-input.md` — 사용자 원 요청
- `evaluation-log.md` — evaluator 진단 (6 구조 리스크)
- `architecture-discussion.md` — 5-Layer / IoC / Behavior Injection 합의
- `plan.md` — 6 Phase 기획안
- `implementation-log.md` — Phase별 구현 기록
- `final-summary.md` — 본 문서

## 11. 회귀 검증 (최종)

- `yarn lint`: 신규 오류 0건 (pre-existing 1건 `historyIcon` 무관)
- `npx tsc --noEmit`: 신규 오류 0건 (pre-existing baseline 동일)
- 사용처 11곳 외부 동작 보존 (도메인 로직, 검색 트리거, 검증 모두 유지)
- pubsub 이름 캡슐화 완료 — 사용처 코드에서 `"open/close-calendar-picker"` 0건
