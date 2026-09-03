# Evaluation Log

## Context
이벤트 도메인(출석/룰렛) 드래그&드롭 리팩터 완료. 공용 훅 1개로 4개 모달 통합. 출석 내부 상태 Map → 평면 배열 전환.

## Structural Risks

1. **출석 평면 배열의 Day 경계 모호성**: `onMove` 콜백에서 `targetDay = prev[targetIndex]?.day`로 Day를 상속하는데, 목록 끝에 drop 시 `prev[targetIndex]`가 undefined가 될 수 있어 `prev[sourceIndex]?.day`로 fallback. 극단적 엣지케이스이지만 잠재적 버그.

2. **mock fallback의 영속성**: `attendance.api.ts`의 DEV fallback은 임시 조치임에도 코드베이스에 영구 포함됨. 백엔드 완성 후 제거 타이밍을 놓칠 위험.

3. **`useListDragDrop`의 이동 로직 분산**: 훅이 `dragOverItem` state만 관리하고, 실제 배열 이동은 각 컴포넌트의 `onMove`에 구현됨. 출석/룰렛 모두 거의 동일한 splice 로직을 중복 작성하는 구조. 향후 이벤트 타입 추가 시 같은 패턴이 또 복제될 수 있음.

## Why This Matters
- 1번: 목록이 비어있는 상태에서 drag 시작 → drop 직전 목록이 변경되는 극단적 시나리오. 실사용에서 발생 확률 낮음.
- 2번: DEV mock 코드가 코드 리뷰 없이 방치될 경우, 백엔드 완성 후에도 mock이 실제 응답을 숨길 수 있음.
- 3번: 이벤트 타입이 3개, 4개로 늘어날 경우 `onMove` 패턴의 복사가 반복될 가능성.

## Improvement Options

1. **이동 로직 훅 내부화 옵션**: `useListDragDrop`이 `items` 배열을 직접 받아 내부에서 splice 후 결과를 `onOrderChange(newItems)`로 전달하는 방식으로 변경. 단, 출석의 `day` 상속 로직은 컴포넌트별로 다르므로 `getTargetMetadata?(sourceItem, targetItem) => Partial<T>` 콜백으로 확장 필요.

2. **mock 격리**: `attendance.mock.ts` 를 `src/mocks/` 디렉토리에 이동하고, `attendance.api.ts`에서 dynamic import + DEV 조건으로 분리. 빌드 시 트리쉐이킹 보장.

3. **TODO 코멘트 추가**: mock fallback 라인에 `// TODO: remove after attendance items API is ready` 주석 추가로 가시성 확보.

## Recommended Backlog

1. 백엔드 완성 후 `attendance.api.ts` mock fallback + `attendance.mock.ts` 제거
2. 이벤트 타입 추가 예정이 있다면 `useListDragDrop`의 `onMove` 인터페이스를 `getTargetMetadata` 콜백으로 확장 검토
3. `src/mocks/` 디렉토리 도입 — 프로젝트 차원의 mock 관리 패턴 수립

## Suggested Next Step
백엔드 출석 아이템 API 완성 시점에 mock 코드 제거 PR을 별도로 올릴 것. 지금은 현 구조로 충분.
