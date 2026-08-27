# Review Log

## Review Target
- `src/pages/manage/events/hooks/use-list-drag-drop.ts`
- `src/apis/event/attendance/attendance.mock.ts`
- `src/apis/event/attendance/attendance.api.ts`
- `src/pages/manage/events/attendance/_id/modules/reward.module.tsx`
- `src/pages/manage/events/attendance/create/modules/reward.module.tsx`
- `src/pages/manage/events/roulette/_id/modules/items.module.tsx`
- `src/pages/manage/events/roulette/create/modules/items.module.tsx`
- `attendance/_id/_id.modal.css`, `attendance/create/index.css`

## Result
- pass

## Checklist Review
- SKILL compliance: 공용 훅 분리, 재사용 자산 탐색 후 신규 생성 — 준수
- Reuse check: 기존 `useApi`, `useDialog`, `useLanguage`, `usePubSub`, util 함수 유지 — 준수
- Validation check: `tsc --noEmit` 오류 0건 확인
- Payload completeness: `updateAttendanceEventItems` payload 구조 기존과 동일 (`{ items: EventAttendanceItemDto[] }`)
- Performance concern: `dayGroups`, `sortedDays` useMemo 적용으로 불필요한 재파생 방지
- Duplicate code concern: 4개 모달의 drag&drop 인라인 코드 전량 제거, 훅 1개로 통일

## Violations
- 없음

## Required Fixes
- `catch` 빈 바인딩 문법 오류 (`attendance.api.ts`) → `catch (_e)`로 수정 완료

## Repeat Issue
- false

## Escalation
- none
