# UI 자산 선정 계획 — 튜토리얼 관리 UI 2차 마무리

## 작업과 조사 근거

- **범위**: 이전 세션이 구현한 UI 2차(세로 이미지 목록, 드래그 정렬, 제목 카운터)의 검증과 보완
- **대상**: admin-ui, `feature/tutorial`, `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/tutorial`, HEAD `811c8bb`
- **스택 근거**: `package.json` — `react` ^19.2.7, `@heroui/react` ^3.2.3, `@dnd-kit/core` ^6.3.1, `@dnd-kit/sortable` ^10.0.0, `@dnd-kit/utilities` ^3.2.2(미커밋, `node_modules/@dnd-kit` 설치 확인)
- **이 세션에서 다시 읽은 코드**
  - `src/shared/ui/sortable-list/sortable-list.{tsx,css}`
  - `src/features/image-manager/ui/{ImageManager.tsx,types.ts,hooks/useImageSlots.tsx}`, `components/ImageSlot{List,Row}.{tsx,css}`
  - `src/pages/tutorial/ui/{tutorial-editor-view.tsx,tutorial.css}`, `src/pages/tutorial/model/tutorial-controller.types.ts`
  - `src/shared/ui/button/button.tsx`, `src/shared/ui/dialog/hook.ts`
  - `ImageManager`의 다른 사용처: `src/pages/item/ui/item-form-sections.tsx:234`(타일, `layout` 미지정)
- **인계 문서**: 이전 세션의 `unknown/ui-asset-plan.md` "2차 항목"을 읽기 전용으로 참조했다. 아래 표는 현재 코드와 대조한 결과다.

## 구현 항목별 선택

| UI 항목 | 선택 | 자산·경로 | 이유·근거 | 계약·변경·검증 | 결정 상태 |
| --- | --- | --- | --- | --- | --- |
| 드래그 순서 변경 | 외부 라이브러리 사용 | `@dnd-kit/*` → 어댑터 `src/shared/ui/sortable-list/sortable-list.tsx` | 사용자가 2026-10-02 도입을 결정했다. 기능 코드에서 `@dnd-kit` 직접 import는 어댑터 1곳뿐이다(`grep` 확인) | `items`, `getItemId`, `onMove(from,to)`, `disabled`, `renderItem(item,index,handle)`. 이 세션에서 `SortableHandle.ref`를 `setNode`로 바꾼다(lint `react-hooks/refs`) | 확정, 이름 변경만 추가 |
| 세로 이미지 목록 | 기존 자산 확장 | `ImageManager layout="list"`, `components/ImageSlotList.tsx`, `ImageSlotRow.tsx` | 사용자 결정 "ImageManager 확장". 구현되어 있다 | 판별 유니온. 타일 계약은 그대로다(build로 아이템 폼 타입 확인) | 확정 |
| 이미지 삭제 확인 | 기존 공용 재사용 | `useDialog().confirm`(`~/shared/ui/dialog`) | 기존 확인 팝업 패턴 | 문구는 호출부 `removeConfirm` | 확정 |
| 수정·삭제·페이지 추가 버튼 | 기존 공용 재사용 | `~/shared/ui/button/button`, `add.icon`, `menu.icon`, `add-photo-alternative.icon` | 기존 버튼·아이콘이 있다 | `canAddSlot`(= `fields.canAddImage`) | 확정 |
| 제목 글자 수 카운터 | 화면 로컬 마크업 | `tutorial-editor-view.tsx`, `cp-caption` | `TextInput`에 카운터 옵션이 없고 한 화면 전용이다. 이전 세션에서 승인됐다 | `fields.titleLength/titleMaxLength` | 확정 |
| 페이지 수 초과 오류 표시 | 화면 로컬 마크업 | `tutorial-editor-view.tsx`, `cp-caption` | 제목 오류와 같은 표시 방식을 쓴다 | `fields.imagesError`. 하단 `save.errorMessage`와 같은 문구면 하단은 생략한다 | 이전 계획 항목, 이 세션에서 구현 |

## 계약과 공용화 영향

- **`SortableHandle`**: `{ setNode, attributes, listeners, isDragging }`. 핸들 버튼에 `ref={handle.setNode}`와 `attributes`·`listeners`를 펼친다. 사용처는 `ImageSlotRow.tsx` 1곳이다.
- **아이템 폼**: 호출부 변경 없음. `npm run build` 타입 검사로 확인한다.
- **번들**: build 출력의 메인 청크는 2,838.43 kB(gzip 802.98 kB)다. 도입 전 수치는 이 세션에서 측정하지 않았다.
- **미정 항목**: 없음

## UI·Logic 연결

- 선행 Logic `811c8bb`, 방향 `controller <- UI`. 상세는 [plan.md](../plan.md)의 "UI·Logic 연결 계약".

## 외부 UI 라이브러리 스킬

| 패키지·버전 | 사용 목적 | 어댑터·공개 계약 | 기존 스킬 | 세션 초안·중앙 경로 | 상태 |
| --- | --- | --- | --- | --- | --- |
| `@dnd-kit/core` 6.3.1, `@dnd-kit/sortable` 10.0.0, `@dnd-kit/utilities` 3.2.2 | 세로 목록 드래그 정렬 | `src/shared/ui/sortable-list/sortable-list.tsx` | 중앙 `reference/libraries/`에는 `heroui`, `lucide-react`만 있다 | `unknown/ui-library-skills/dnd-kit/SKILL.md` → 중앙 `policy/common/skills/reference/libraries/dnd-kit/SKILL.md` | 구현 확인본 작성, 중앙 미등록 |
| `@heroui/react` ^3.2.3 | 버튼 | `src/shared/ui/button/button.tsx` | 중앙 `reference/libraries/heroui/SKILL.md` | 갱신 없음 | 기존 스킬 사용 |

## 승인과 변경

- 승인 요청에 제시한 항목: 위 표 전체. 새로 확인받는 것은 `SortableHandle.ref` → `setNode` 이름 변경과 `imagesError` 표시 방식이다.
- 승인 근거: 2026-10-02 사용자 "진행"
- 구현 중 달라진 항목: `setNode` 이름 변경으로는 lint가 통과하지 않았다. 핸들 버튼을 어댑터가 렌더하도록 바꿨고, 위 표와 "계약과 공용화 영향"의 `SortableHandle` 설명은 더 이상 맞지 않는다. 실제 계약은 `renderItem(item, index, handle: ReactNode)`, `getHandleLabel`, `handleContent`, `handleClassName`이며 [dnd-kit 스킬 초안](ui-library-skills/dnd-kit/SKILL.md)에 적었다. 사용처는 `ImageSlotList.tsx` 1곳이다.
