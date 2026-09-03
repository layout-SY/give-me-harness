# Final Summary

## What Changed
- `src/pages/manage/events/hooks/use-list-drag-drop.ts` 신규 생성 — 이벤트 도메인 공용 드래그&드롭 훅
- `src/apis/event/attendance/attendance.mock.ts` 신규 생성 — 출석 아이템 API mock 데이터
- `src/apis/event/attendance/attendance.api.ts` 수정 — DEV 환경 mock fallback 추가
- `attendance/_id/modules/reward.module.tsx` — Map 구조 제거, 평면 배열 + 공용 훅 적용
- `attendance/create/modules/reward.module.tsx` — 동일
- `roulette/_id/modules/items.module.tsx` — 인라인 drag&drop 코드 → 공용 훅 교체
- `roulette/create/modules/items.module.tsx` — 동일
- CSS 2개 파일 — `[data-drag-over="true"]` 규칙 제거

## Why It Changed
- 출석/룰렛 4개 모달에 `getDropPosition`, `parseDragPayload`, drag state, 핸들러 5개가 그대로 복사되어 있었음
- 출석 모달의 `Map<number, EventAttendanceItemDto[]>` 구조가 Day 컨테이너 드롭 존이라는 룰렛과 다른 UX를 강제 → 훅 통합 불가 상태
- Day 컨테이너 드롭 UX 제거 + 평면 배열 전환으로 출석/룰렛 드래그&드롭 구조 통일
- 출석 아이템 API 백엔드 미구현으로 DEV 환경 개발 불가 상태였음

## Reused Assets
- `useApi`, `useDialog`, `useLanguage`, `usePubSub` — 기존 공용 훅
- `toValidEventAttendanceItems`, `toValidEventRouletteItems` — 기존 유틸
- `EventAttendanceItemDto`, `EventRouletteItemDto` DTO 타입 — 변경 없음

## Impacted Areas
- `src/pages/manage/events/attendance/` — _id/modules, create/modules
- `src/pages/manage/events/roulette/` — _id/modules, create/modules
- `src/apis/event/attendance/` — API + mock 추가

## Remaining Risks
- 출석 아이템 API 백엔드 완성 시 `attendance.mock.ts` + `attendance.api.ts` fallback 코드 제거 필요
- 이벤트 타입 추가 시 `onMove` 내 splice 패턴이 재복제될 수 있음 (훅 확장 여지 있음)

## Follow-up Suggestions
1. 백엔드 완성 후 attendance mock 코드 제거 PR
2. `useListDragDrop`의 `onMove` 인터페이스에 `getTargetMetadata` 콜백 추가 — Day 상속 같은 도메인별 메타 처리를 훅 내부로 수용 가능하게 확장
3. `src/mocks/` 디렉토리 도입으로 프로젝트 차원 mock 관리 패턴 수립
