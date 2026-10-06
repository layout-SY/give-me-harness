# 계획 — 튜토리얼 관리 UI 2차 마무리

승인 영역은 목표·범위·역할·계약·검증 기준이다. 진행 결과는 종료 표식 아래에 기록한다.
진행 기록에 새 요구를 적는 것으로 승인 범위를 확대할 수 없다.

<!-- asan-plan:approval:start:v1 -->

## 목표

이전 세션(`.claude/logs/sessions/튜토리얼-관리-UI/`)이 구현만 하고 검증하지 못한 UI 2차(기획서 p11·p12 이미지 편집, 제목 카운터)를 같은 범위 안에서 검증·보완해 완료한다.

## 작업 유형

- feature(UI)

## 범위

- **대상**: admin-ui, `feature/tutorial`, `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/tutorial`, HEAD `811c8bb`, 직접 부모 `sy-main`
- **이어받는 미커밋 변경(이전 세션 작성)**: `package.json`·`package-lock.json`(`@dnd-kit` 3종), `src/shared/ui/sortable-list/*`, `src/features/image-manager/ui/{ImageManager.tsx,ImageManager.css,types.ts}`, `components/ImageSlot{List,Row}.{tsx,css}`, `src/pages/tutorial/ui/{tutorial-editor-view.tsx,tutorial.css}`
- **이 세션의 변경**
  1. lint 오류 해소: `SortableHandle`의 `ref` 필드가 `react-hooks/refs` 규칙에 걸린다(`ImageSlotRow.tsx` 3건). 필드 이름을 바꿔 규칙을 통과시킨다. 대상은 `sortable-list.tsx`, `ImageSlotRow.tsx`.
  2. 이전 계획의 미구현 항목: `fields.imagesError`를 이미지 섹션에 표시한다. 대상은 `tutorial-editor-view.tsx`.
  3. 검증에서 드러나는 오류가 있으면 위 파일 범위에서 고친다.
- **산출물**: 이 계획, `unknown/ui-asset-plan.md`, `unknown/ui-library-skills/dnd-kit/SKILL.md`(구현 확인본), `final-summary.md`

## 제외 사항

- 이전 계획의 제외 사항 그대로: Logic 파일(controller·entity·`tests/tutorial-*.test.mjs`), 현상 유지로 결정된 화면 항목, 시각 QA·브라우저 자동화
- `components/ImageSlotEmpty.tsx` 삭제: 사용처가 없는 파일이며 커밋 때 `git rm`으로 처리한다(Git 승인 대상)
- Git 작업 전체(별도 승인)

## 제약 조건

- 아이템 폼(`src/pages/item/ui/item-form-sections.tsx`)의 `ImageManager` 호출 계약을 보존한다.
- 이미지 변경은 `fields.onImagesChange`·`fields.uploadApi`로만 연결하고, 추가 버튼은 `fields.canAddImage`로만 활성화한다.
- 새 색상·토큰을 만들지 않는다.

## 스킬 및 역할

- 역할: `ui`(inject)
- 승인할 Git 작업: 없음
- 산출물 책임: owner(UI 2차 범위)

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 드래그 어댑터 lint 보완 | ui | ui-library | `SortableHandle` 필드 이름 변경, lint 통과 |
| 편집 화면 보완 | ui | api-authoring/ui-controller | `imagesError` 표시 |
| 검증 | ui | — | 포맷, 테스트, lint, build |

## UI 자산 선정

- [UI 자산 선정 계획](unknown/ui-asset-plan.md)
- 외부 라이브러리 스킬: `unknown/ui-library-skills/dnd-kit/SKILL.md`. 중앙 등록은 인계 대상이다.
- 미정 항목: 없음

## UI·Logic 연결 계약

- **선행**: Logic `811c8bb`, 계약 문서 `.codex/logs/sessions/tutorial-api-controller/unknown/controller-contract.md`. 방향은 `controller <- UI`.
- **사용 필드**: `fields.{title,titleError,titleLength,titleMaxLength,images,imagesError,maxImages,canAddImage,isReady,isDirty,isUploading,onTitleChange,onImagesChange,uploadApi}`, `save.*`, `delete.*`, `preview.*`
- **매핑**: 교체·빈 칸 채우기는 같은 길이 배열, 삭제는 해당 index를 뺀 배열, 드래그는 이동한 배열, 페이지 추가는 끝에 `null`을 붙인 배열을 `onImagesChange`로 전달한다.
- **오류 중복**: `imagesError`는 `save.errorMessage`에도 반영된다(계약 문서). 같은 문구를 두 번 표시하지 않는다.
- **불일치**: 없음

## 검증

- `formatting.py apply`
- `node --test tests/image-manager-slots.test.mjs tests/tutorial-contract.test.mjs tests/tutorial-controller.test.mjs`
- `npm run lint`, `npm run build`

## 위험 요소 및 결정 사항

- 드래그 동작은 DOM 테스트 도구가 없어 자동 검증하지 못한다. 브라우저 확인은 사용자 몫으로 남는다.
- 이전 세션의 결과 미확인 쓰기 기록(`5473ab3e…`, `ImageManager.css`)이 남아 있다. 검증 명령은 이 세션에서 실행되므로 지금은 막지 않지만, 포맷·커밋이 막히면 `write-recovery`를 승인받아 해소한다.

<!-- asan-plan:approval:end:v1 -->

## 진행 기록 (해시 제외)

- 2026-10-02 착수 시 확인: build 통과, 테스트 29/29 통과, lint 실패 3건(`ImageSlotRow.tsx:52,56,57`, `react-hooks/refs`).
- 사용자 승인: 2026-10-02 "진행".
- `SortableHandle.ref` → `setNode` 이름 변경은 lint를 통과시키지 못했다. 같은 목적(lint 해소)으로 핸들 버튼을 `sortable-list.tsx` 안에서 렌더하도록 바꿨다. `renderItem`의 셋째 인자가 `ReactNode`가 됐고 `getHandleLabel`·`handleContent`·`handleClassName`이 추가됐다. 수정 파일에 `ImageSlotList.tsx`가 더해졌다.
- 미확인 쓰기 기록 때문에 포맷·lint가 막혀 `write-recovery`(`ad23faa6…`)를 실행해 해소했다.
- 최종 검증: 포맷 성공, lint 통과, build 통과, 테스트 29/29. 상세는 [final-summary.md](final-summary.md).
- 인계 출처: `.claude/logs/sessions/튜토리얼-관리-UI/{handoff.md,plan.md}`, `.codex/logs/sessions/tutorial-api-controller/handoff.md`(읽기 전용 참조)

## 승인

- 상태: approved (2026-10-02 사용자 "진행")
- 필수 문구: `이 역할과 계획대로 진행할까요, 아니면 조정할 부분이 있나요?`
