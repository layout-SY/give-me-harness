# Plan

## Request Summary
- 이벤트 출석/룰렛의 생성·상세 모달 총 4곳에 중복 분산된 드래그&드롭 로직을 공용 hook으로 통합
- 출석 모달의 내부 상태를 Map(Day 그룹) → 평면 배열로 구조 변경
- Day 컨테이너 드롭 존 UX 제거 (빈 Day 영역에 드롭하는 기능)
- 백엔드 미구현 상태인 출석 아이템 API에 대한 mock 데이터 적용

## Work Type
- hybrid (refactor + feature)

## Scope
- `src/pages/manage/events/hooks/use-list-drag-drop.ts` 신규 생성 (공용 훅)
- `src/apis/event/attendance/attendance.mock.ts` 신규 생성 (mock 데이터)
- `src/apis/event/attendance/attendance.api.ts` 수정 (mock fallback)
- `src/pages/manage/events/attendance/_id/modules/reward.module.tsx` 리팩터
- `src/pages/manage/events/attendance/create/modules/reward.module.tsx` 리팩터
- `src/pages/manage/events/roulette/_id/modules/items.module.tsx` 리팩터
- `src/pages/manage/events/roulette/create/modules/items.module.tsx` 리팩터
- `_id.modal.css`, `create/index.css` — `[data-drag-over]` 스타일 제거

## Out of Scope
- 룰렛 API mock (백엔드 정상 운영 중)
- 출석/룰렛 이외 이벤트 타입
- 드래그&드롭 애니메이션/UX 개선

## Sections
1. S1 — `useListDragDrop` 공용 훅 설계 및 생성
2. S2 — 출석 API mock 데이터 및 fallback 적용
3. S3 — 출석 상세 모달(reward.module) Map → 평면 배열 전환 + 훅 적용
4. S4 — 출석 생성 모달(reward.module) 동일 전환
5. S5 — 룰렛 상세/생성 모달(items.module) 인라인 코드 → 훅 교체
6. S6 — CSS `[data-drag-over]` 스타일 제거 및 퍼블리싱 정리

## Required Agents
- planner (구조 설계 결정 및 UX 트레이드오프 검토)
- generator (S1~S5 구현)
- publisher (S6 CSS 정리)
- watcher (tsc --noEmit 검증)

## Required Skills
- coding-convention/SKILL.md
- refactoring/SKILL.md

## Risks / Assumptions
- 출석 아이템 내 Day 순서 변경 UX 변경: Day 컨테이너 전체 드롭 → 아이템 간 드래그로 통일 (UX degradation 수용)
- 드래그 시 이동 아이템의 `day` 값은 드롭 대상 아이템의 `day`를 자동 상속
- `day` 순서 내 아이템 생성 순서는 무관 (사용자 확인 완료)
- mock fallback은 DEV 환경에서만 동작 (`import.meta.env.DEV`)
- 빈 Day 슬롯(아이템 없는 날) UI 제거 → 아이템 추가 폼의 day 입력으로 대체

## Approval Request
이 계획대로 진행할까요, 아니면 조정할 부분이 있나요?
