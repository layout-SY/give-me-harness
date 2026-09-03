# Implementation Log

## Task Summary
이벤트 출석/룰렛 모달 4곳의 드래그&드롭 중복 코드를 단일 공용 훅으로 통합.
출석 모달은 추가로 내부 상태를 Map(Day 그룹) → 평면 배열로 구조 전환.
출석 아이템 API mock 적용.

## Reused Assets
- `useApi`, `useDialog`, `useLanguage`, `usePubSub` — 기존 훅 그대로 유지
- `toValidEventAttendanceItems` (`attendance-item.util.ts`) — loadFromEvent 검증에 계속 활용
- `toValidEventRouletteItems` (`roulette-item.util.ts`) — 동일

## New Files

### `src/pages/manage/events/hooks/use-list-drag-drop.ts`
- `enabled: boolean` + `onMove(sourceIndex, targetIndex, position)` 콜백 인터페이스
- 내부에서 `dragOverItem` state, `getDropPosition`, 모든 핸들러 관리
- 실제 배열 이동 로직은 컴포넌트(onMove 콜백)에 위임 → 룰렛/출석 모두 재사용 가능
- 룰렛: `onMove`에서 단순 배열 splice
- 출석: `onMove`에서 `targetDay = prev[targetIndex]?.day` 상속 후 splice

### `src/apis/event/attendance/attendance.mock.ts`
- 8개 샘플 아이템 (Day 1~7, DAILY/ACC 혼합)
- `getAttendanceEventItems` 실패 시 → `MOCK_ATTENDANCE_ITEMS` 반환 (DEV only)
- `updateAttendanceEventItems` 실패 시 → silent return (DEV only)

## Updated Files

### 출석 `_id/modules/reward.module.tsx`
- 내부 상태: `Map<number, EventAttendanceItemDto[]>` → `EventAttendanceItemDto[]`
- 제거: `cloneItemsMap`, `getSortedDays`, `getMaxDay`, `getDayRange`, `flattenItems`, `dayList` state
- 추가: `sortByDay()` (day → sortOrder 순 정렬), `applySortOrder()` (flat array용)
- 추가: `sortedDays`, `dayGroups` (useMemo로 렌더링 파생)
- 드래그 관련 state/함수 전량 제거 → `useListDragDrop` 1줄로 교체
- 렌더링: Day 헤더는 유지하되, Day 컨테이너 드래그 이벤트 제거
- 아이템 이동 시 `day` 자동 상속: `targetDay = prev[targetIndex]?.day`

### 출석 `create/modules/reward.module.tsx`
- 동일 Map → 평면 배열 전환
- `syncChange` 콜백: `onChange(flatArray)` 단순화 (flattenItems 불필요)
- `useListDragDrop` 적용, `onMove`에서 sorted 후 syncChange 호출

### 룰렛 `_id/modules/items.module.tsx`
- 인라인 `getDropPosition`, `parseDragPayload`, drag state, 5개 핸들러 제거
- `useListDragDrop` 1줄 + `onMove` 콜백으로 교체
- `onDragEnd={() => setDragOverItem(null)}` → `onDragEnd={handleDragEnd}`

### 룰렛 `create/modules/items.module.tsx`
- 동일. `onMove` 내부에서 `syncChange(next)` 호출 유지.

### CSS
- `attendance/_id/_id.modal.css` — `.reward-day[data-drag-over="true"]` 규칙 제거
- `attendance/create/index.css` — 동일

## Key Logic

### Day 자동 상속 (출석 평면 배열 이동)
```typescript
onMove: (sourceIndex, targetIndex, position) => {
  setFormItems((prev) => {
    const targetDay = prev[targetIndex]?.day ?? prev[sourceIndex]?.day ?? 1;
    const next = [...prev];
    const [moving] = next.splice(sourceIndex, 1);
    let insertAt = position === "before" ? targetIndex : targetIndex + 1;
    if (sourceIndex < insertAt) insertAt -= 1;
    next.splice(insertAt, 0, { ...moving, day: targetDay });
    return applySortOrder(next);
  });
},
```

### applySortOrder (flat array)
```typescript
const applySortOrder = (items: EventAttendanceItemDto[]): EventAttendanceItemDto[] => {
  const counters: Record<string, number> = {};
  return items.map((item) => {
    const key = `${item.day}-${item.type}`;
    counters[key] = (counters[key] ?? 0) + 1;
    return { ...item, sortOrder: counters[key] };
  });
};
```

## Validation / Request Handling
- `tsc --noEmit` 최종 통과 (catch 빈 바인딩 문법 오류 수정 후)
- DEV mock fallback은 `import.meta.env.DEV` 조건부 → 프로덕션 빌드에 영향 없음

## Risks
- 빈 Day(아이템 없는 날)는 더 이상 슬롯으로 표시되지 않음 (사용자 수용)
- Day 간 아이템 이동 UX가 아이템 경계 드래그로 변경됨

## Handoff Note
- Ready for watcher review
