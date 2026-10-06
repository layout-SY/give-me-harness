---
name: reference-ui-library-dnd-kit
description: admin-ui에서 @dnd-kit으로 세로 목록 드래그 정렬을 구현할 때 공용 어댑터(SortableList)의 계약과 사용법
---

# dnd-kit 사용 계약

세션 초안이다. 중앙 등록 전이며, 이전 세션 초안(`.claude/logs/sessions/튜토리얼-관리-UI/unknown/ui-library-skills/dnd-kit/SKILL.md`)을 구현 확인 후 다시 쓴 것이다.

## 목적과 적용 범위

- **해결할 요구**: 튜토리얼 기획서 p12의 페이지 순서 변경. 드래그 핸들로 이미지 페이지 순서를 바꾼다.
- **선택 이유**: 저장소에 드래그 구현·의존성이 없었고, 사용자가 접근성(키보드)·터치 지원을 이유로 도입을 결정했다(2026-10-02).
- **대상 프로젝트**: `asan-metaverse-admin-ui`만
- **적용 범위**: 세로 한 줄 목록의 순서 변경
- **제외 범위**: 그리드, 컨테이너 간 이동, 가상 스크롤 목록

## 버전과 근거

- `package.json` 선언 = lockfile 설치 버전: `@dnd-kit/core` ^6.3.1 = 6.3.1, `@dnd-kit/sortable` ^10.0.0 = 10.0.0, `@dnd-kit/utilities` ^3.2.2 = 3.2.2. 전이 의존성 `@dnd-kit/accessibility` 3.1.1.
- 프로젝트는 React ^19.2.7이다(peer `>=16.8.0`).
- 공식 문서 https://docs.dndkit.com 원문 대조는 하지 않았다. 계약은 설치 패키지 타입과 build 통과 기준이다.

## 어댑터 계약 (구현 확인)

- **경로**: `src/shared/ui/sortable-list/sortable-list.tsx`(default export `SortableList`), `sortable-list.css`. 기능 코드는 `@dnd-kit/*`를 import하지 않는다.
- **props**
  - `items: readonly T[]`
  - `getItemId: (item, index) => string` — 목록 안에서 고유해야 한다. 고유 ID가 없으면 index 기반 값을 쓴다.
  - `onMove: (from, to) => void` — 드롭으로 위치가 바뀐 경우에만 한 번 호출한다.
  - `renderItem: (item, index, handle: ReactNode) => ReactNode` — `handle`은 어댑터가 만든 드래그 핸들 버튼이다. 항목 안 원하는 위치에 그대로 넣는다.
  - `getHandleLabel: (item, index) => string` — 핸들 버튼의 `aria-label`
  - `handleContent: ReactNode` — 핸들 안 아이콘
  - `handleClassName?: string`, `disabled?: boolean`, `className?: string`
- **핸들을 어댑터가 렌더하는 이유**: `useSortable`의 `setActivatorNodeRef`·`attributes`·`listeners`를 객체로 묶어 다른 컴포넌트에 넘기면 `react-hooks/refs` 규칙이 렌더 중 ref 접근으로 판정한다. 필드 이름을 바꿔도 같았다.
- **내부 구성**: `PointerSensor`(5px 이동 후 시작), `KeyboardSensor` + `sortableKeyboardCoordinates`, `closestCenter`, `verticalListSortingStrategy`. 항목 `<li>`에 `CSS.Transform.toString(transform)`과 `transition`을 적용한다.
- **상태 소유권**: 순서 배열은 호출부가 소유한다.
- **접근성**: 핸들은 `<button type="button">`이다. Space로 잡고, 화살표로 옮기고, Space로 놓고, Esc로 취소한다. 스크린리더 안내는 dnd-kit 기본(영문)이다.
- **스타일**: 핸들에는 호출부가 `touch-action: none`을 준다(`ImageSlotRow.css`의 `.image-slot-row__handle`).

## 사용법

실제 사용처는 `src/features/image-manager/ui/components/ImageSlotList.tsx` 1곳이다.

```tsx
<SortableList
  items={images}
  getItemId={(_image, index) => `slot-${index}`}
  disabled={isLocked}
  onMove={move}
  getHandleLabel={(_image, index) => `이미지 ${index + 1} 순서 이동`}
  handleContent={menuIcon}
  handleClassName="image-slot-row__handle"
  renderItem={(imageUrl, index, handle) => <ImageSlotRow index={index} imageUrl={imageUrl} handle={isEditing ? handle : undefined} />}
/>
```

## 제약과 검증

- 검증: `npm run lint`, `npm run build` 통과(2026-10-02). DOM 테스트 도구가 없어 실제 드래그는 자동 검증하지 못했다.
- 스크린리더 안내 문구 한국어화는 하지 않았다.

## 중앙 등록·갱신

- 대상 중앙 경로: `policy/common/skills/reference/libraries/dnd-kit/SKILL.md`. 기존 정본은 없다.
- 상태: 미등록. 중앙 저장소 작업으로 인계한다.
