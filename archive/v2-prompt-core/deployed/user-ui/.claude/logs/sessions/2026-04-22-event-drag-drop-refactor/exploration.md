# Exploration

## Target Paths
- `src/pages/manage/events/attendance/_id/modules/`
- `src/pages/manage/events/attendance/create/modules/`
- `src/pages/manage/events/roulette/_id/modules/`
- `src/pages/manage/events/roulette/create/modules/`
- `src/apis/event/attendance/`
- `src/hooks/` (공용 훅 패턴 참고)

## Existing Reusable Assets Found
- Found: 없음 (프로젝트 내 드래그&드롭 관련 공용 훅 전무)
- Suggested Reuse: 4개 모듈 내 중복 코드를 추출해 공용 훅으로 생성

## 중복 코드 분석

### 4개 파일 전원 중복
| 함수 | 설명 |
|---|---|
| `getDropPosition(event)` | 마우스 Y 위치로 "before"/"after" 판정 (3줄) |
| `parseDragPayload(event)` | `dataTransfer`에서 JSON 파싱 |
| `handleDragStart` | `dataTransfer.setData` + `effectAllowed = "move"` |
| `handleDragOverItem` | `dropEffect` 설정 + `dragOverItem` state 갱신 |
| `handleDropOnItem` | payload 파싱 후 이동 처리 |
| `dragOverItem` state | `{ index, position } | null` (룰렛) or `{ day, targetIndex, position } | null` (출석) |

### 출석 전용 추가 코드 (2개 파일)
- `dragOverDay` state
- `handleDragOverDay`, `handleDragLeaveDay`, `handleDropDay`
- Map 구조 유틸: `cloneItemsMap`, `getSortedDays`, `getMaxDay`, `getDayRange`, `flattenItems`

### 구조 차이 분석
| 항목 | 룰렛 | 출석(변경 전) |
|---|---|---|
| 내부 상태 | `EventRouletteItemDto[]` | `Map<number, EventAttendanceItemDto[]>` |
| 드래그 페이로드 | `{ index }` | `{ day, index }` |
| 드롭 대상 | 아이템만 | 아이템 + Day 컨테이너 |

## Assets Not Suitable for Reuse
- Asset: 출석 모달의 Day 컨테이너 드롭 존 (`handleDragOverDay`, `handleDropDay`)
- Why not suitable: UX 제거 결정으로 폐기. 룰렛과 구조 통일을 위해 제거.

## New Asset Necessity
- Needed: `src/pages/manage/events/hooks/use-list-drag-drop.ts`
- Why: 4개 모달 공통 드래그&드롭 state + handler 관리. `enabled` + `onMove` 콜백으로 실제 아이템 이동 로직을 컴포넌트에 위임하는 설계로 범용성 확보.

- Needed: `src/apis/event/attendance/attendance.mock.ts`
- Why: 출석 아이템 API(`getAttendanceEventItems`, `updateAttendanceEventItems`) 백엔드 미구현. DEV 환경 fallback 데이터 필요.
