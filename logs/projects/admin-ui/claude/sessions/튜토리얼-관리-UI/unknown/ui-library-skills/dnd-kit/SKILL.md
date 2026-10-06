---
name: reference-ui-library-dnd-kit
description: admin-ui에서 @dnd-kit으로 세로 목록 드래그 정렬을 구현할 때 공용 어댑터(SortableList)의 계약과 사용법
---

# dnd-kit 사용 계약

## 목적과 적용 범위

- **해결할 요구**: 튜토리얼 기획서 p12의 "페이지 순서 변경". 드래그 핸들(⠿)로 이미지 페이지 순서를 바꾼다.
- **선택 이유**: 저장소에 드래그 구현이나 의존성이 없었다. 사용자가 접근성(키보드)·터치 지원을 이유로 `@dnd-kit` 도입을 결정했다(2026-10-02). 함께 검토한 대안은 HTML 기본 드래그와 이동 버튼뿐인 방식이다.
- **대상 프로젝트**: `asan-metaverse-admin-ui`만
- **적용 범위**: 세로 한 줄 목록의 순서 변경
- **제외 범위**: 그리드·다중 컨테이너 간 이동, 가상 스크롤 목록
- **문서 상태**: 계획 초안. 구현 확인 후 갱신한다. 중앙 등록 전이다.

## 버전과 근거

- **패키지**(`package.json` 선언 = lockfile 설치 버전)
  - `@dnd-kit/core` ^6.3.1 = 6.3.1
  - `@dnd-kit/sortable` ^10.0.0 = 10.0.0
  - `@dnd-kit/utilities` ^3.2.2 = 3.2.2
  - 전이 의존성: `@dnd-kit/accessibility` 3.1.1
- **peer**: core는 `react`/`react-dom >=16.8.0`, sortable은 `@dnd-kit/core ^6.3.0`. 프로젝트는 React ^19.2.7이다.
- **제외한 패키지**: `@dnd-kit/react` 0.5.0. 신규 API이며 1.0 이전이다.
- **공식 문서**: https://docs.dndkit.com. 이번 세션에서 원문 대조는 하지 않았다. 계약은 설치 패키지 API 기준이다.

## 구현 방식과 계약 (제안)

- **어댑터**: `src/shared/ui/sortable-list/sortable-list.tsx`(default export `SortableList`). 기능 코드는 `@dnd-kit/*`를 import하지 않는다.
- **props**
  - `items: readonly T[]`
  - `getItemId: (item: T, index: number) => string`
  - `onMove: (from: number, to: number) => void`(드롭 시 한 번, 위치가 바뀐 경우만)
  - `disabled?: boolean`
  - `renderItem: (item: T, index: number, handle: SortableHandle) => ReactNode`
  - `className?: string`
- **`SortableHandle`**: 핸들 버튼에 펼치는 속성(`attributes`·`listeners`)과 `ref`, 드래그 중 여부 `isDragging`
- **내부 구성**
  - 센서: `PointerSensor`(이동 거리 5px 이후 시작해 클릭과 구분), `KeyboardSensor` + `sortableKeyboardCoordinates`
  - 정렬: `verticalListSortingStrategy`, `restrict`는 사용하지 않는다.
  - 항목 래퍼에 `CSS.Transform.toString(transform)`과 `transition`을 적용한다.
- **ID**: 호출부가 고유 문자열을 준다. 슬롯에 고유 ID가 없으면 index 기반 ID를 써도 된다. 드래그 중에는 배열이 바뀌지 않는다.
- **상태 소유권**: 순서 배열은 호출부(controller)가 소유한다. 어댑터는 이동 결과만 전달한다.
- **접근성**: 핸들은 `<button type="button">`과 접근성 이름을 갖는다. 키보드로는 Space로 잡고, 화살표로 옮기고, Space로 놓고, Esc로 취소한다. 기본 스크린리더 안내는 dnd-kit 기본(영문)이다.

## 사용법

```tsx
import SortableList from "~/shared/ui/sortable-list/sortable-list";

<SortableList
  items={images}
  getItemId={(_image, index) => `slot-${index}`}
  disabled={isBusy}
  onMove={(from, to) => onChange(moveImageSlot(images, from, to))}
  renderItem={(image, index, handle) => (
    <Row image={image}>
      <button type="button" ref={handle.ref} aria-label={`${index + 1}번 순서 이동`} {...handle.attributes} {...handle.listeners}>⠿</button>
    </Row>
  )}
/>
```

## 제약과 검증

- DOM 테스트 도구가 없어 `npm run build`·`npm run lint`로 확인한다. 실제 드래그는 사용자 실행으로 확인한다.
- 스크린리더 안내 문구 한국어화는 범위 밖이다.

## 중앙 등록·갱신

- **세션 초안**: `.claude/logs/sessions/튜토리얼-관리-UI/unknown/ui-library-skills/dnd-kit/SKILL.md`. 자산 선정 문서는 `../../ui-asset-plan.md`의 "2차 항목".
- **대상 중앙 경로**: `policy/common/skills/reference/libraries/dnd-kit/SKILL.md`. 기존 정본은 없다.
- **상태**: 미등록. 중앙 저장소 작업으로 인계한다.
