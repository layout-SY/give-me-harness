# 계획 — 튜토리얼 관리 UI (2차: 기획서 이미지 편집 반영)

승인 영역에는 목표·범위·역할·계약·검증 기준을 적는다. 진행 결과는 종료 표식 아래에 기록한다.
진행 기록에 새 요구를 적는 것으로 승인 범위를 넓힐 수 없다. 1차 계획·결과는 진행 기록과 [final-summary.md](final-summary.md)에 있다.

<!-- asan-plan:approval:start:v1 -->

## 목표

기획서 p11·p12(`/Users/okand/Downloads/아산시 메타버스_튜토리얼 시스템기획서.pptx.pdf`)의 이미지 편집과 제목 입력 형태를 튜토리얼 편집 화면에 반영한다. Logic 보완 controller(`811c8bb`)의 새 계약에 맞춘다.

## 작업 유형

- feature(UI)

## 범위

- **대상**: admin-ui, `feature/tutorial`, `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/tutorial`, HEAD `811c8bb`
- **의존성 추가(`package.json`, `package-lock.json`)**: `@dnd-kit/core@^6.3.1`, `@dnd-kit/sortable@^10.0.0`, `@dnd-kit/utilities@^3.2.2`. 사용자가 2026-10-02 `@dnd-kit` 도입을 결정했다.
- **신규 `src/shared/ui/sortable-list/sortable-list.tsx`(+css)**: `@dnd-kit` 공용 어댑터. 기능 코드는 `@dnd-kit`를 직접 import하지 않는다.
  - 계약: `items`, `getItemId`, `onMove(from, to)`, `disabled`, `renderItem(item, index, handle)`
  - `handle`은 드래그 핸들 버튼에 펼칠 속성이다.
  - 포인터·키보드 센서를 쓰며, 세로 목록에 한정한다.
- **수정 `src/features/image-manager/ui/*`**: `layout: "list"` 판별 유니온을 추가하고, 1차에 넣은 `reorderable`·`allowEmptySlots`(튜토리얼만 사용)를 이것으로 대체한다. 기본 타일 레이아웃은 1차 이전 동작과 같다(아이템 폼 보존).
  - **행 구성**: 순번 배지, 드래그 핸들, 썸네일(누르면 미리보기), 안내 문구(호출부가 `slotGuide`로 전달), "수정" 버튼(파일 선택 후 해당 칸 교체), "삭제" 버튼
  - **빈 칸**: "순서대로 등록하여 주세요" 업로드 영역(누르면 파일을 골라 채움)과 "삭제" 버튼
  - **삭제**: 이미지가 있으면 확인 팝업(`useDialog().confirm`, 문구는 호출부의 `removeConfirm`)을 거친 뒤 칸을 제거한다. 빈 칸은 확인 없이 제거한다.
  - **하단 "+ 페이지 추가"**: 맨 아래에 빈 칸 1개를 추가한다. 활성 여부는 호출부의 `canAddSlot`, 안내 문구는 `addSlotCaption`으로 받는다.
  - **컴포넌트 정리**: `components/ImageSlotRow.tsx`를 신규로 만들고, 1차의 `components/ImageSlotEmpty.tsx`와 이동 화살표·순번 CSS는 제거한다.
- **수정 `src/pages/tutorial/ui/tutorial-editor-view.tsx`, `tutorial.css`**
  - 제목 라벨 오른쪽에 `titleLength/titleMaxLength` 카운터를 둔다. 30자를 넘으면 오류 색상과 `titleError`를 표시한다.
  - `ImageManager layout="list"`를 연결한다.
    - `canAddSlot={fields.canAddImage}`, `maxImages={fields.maxImages}`
    - `slotGuide`: "권장 사이즈 1200x675 / PNG, JPG 파일만 가능"
    - `removeConfirm`: "이미지를 삭제하시겠습니까?" / "삭제된 이미지는 복구할수 없습니다."
    - `addSlotCaption`: "최대 20페이지까지 추가 가능합니다."
  - `fields.imagesError`를 표시한다.
- **테스트**: 슬롯 순수 함수 테스트는 유지한다. 드래그 어댑터는 DOM 테스트 도구가 없어 build·lint로만 확인한다.
- **산출물**
  - 이 계획, `unknown/ui-asset-plan.md` 갱신
  - `unknown/ui-library-skills/dnd-kit/SKILL.md` 초안
  - `final-summary.md` 갱신

## 제외 사항

- 사용자 결정으로 현상 유지하는 항목: 메뉴·화면 제목·화면 구조·목록 컬럼·목록 상단·날짜 형식·목록에서 삭제·등록 버튼 활성 조건
- Logic 파일 수정(controller·entity·`tests/tutorial-*.test.mjs`)
- 시각 QA·브라우저 자동화
- Git 작업(별도 승인)

## 제약 조건

- 아이템 폼(`src/pages/item/ui/item-form-sections.tsx`)의 `ImageManager` 호출 계약·렌더를 보존한다.
- 모든 이미지 변경은 `fields.onImagesChange`(전체 배열)와 `fields.uploadApi`로만 연결한다.
- controller 규칙(빈 칸이 있으면 추가 불가, 20개 상한)을 UI가 우회하지 않는다. 추가 버튼은 `canAddImage`로만 활성화한다.
- 새 색상·토큰을 만들지 않는다. `_cp-admin.css`와 `_variables.css` 팔레트를 쓴다.

## 스킬 및 역할

- 역할: `ui`(inject)
- 승인할 Git 작업: 없음
- 산출물 책임: owner(UI 범위)

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| `@dnd-kit` 도입·어댑터 | ui | ui-library | 의존성 3개, `shared/ui/sortable-list`, 라이브러리 스킬 초안 |
| ImageManager 목록 레이아웃 | ui | ui-library, ui.md | `layout="list"`, 행 컴포넌트, 아이템 폼 무변경 |
| 편집 화면 연결 | ui | api-authoring/ui-controller | 제목 카운터, 새 controller 필드 연결 |

## UI 자산 선정

- [UI 자산 선정 계획](unknown/ui-asset-plan.md)의 2차 항목: `@dnd-kit` 외부 라이브러리 사용, `ImageManager` 확장 변경, 기존 `useDialog`·`Button`·아이콘 재사용
- 외부 라이브러리 스킬: `@dnd-kit` 세션 초안을 작성하고 중앙 `policy/common/skills/reference/libraries/dnd-kit/SKILL.md` 등록을 인계한다.

## UI·Logic 연결 계약

- **선행**: Logic `811c8bb`. 계약 문서는 `.codex/logs/sessions/tutorial-api-controller/unknown/controller-contract.md`. 방향은 `controller <- UI`.
- **새로 쓰는 필드**: `fields.titleLength`, `fields.titleMaxLength`, `fields.maxImages`, `fields.canAddImage`, `fields.imagesError`
- **기존 필드**: `fields.images`, `onImagesChange`, `uploadApi`, `isUploading`, `titleError`, `preview.onOpen(index)`
- **매핑**
  - 행 교체·빈 칸 채우기: 업로드 후 같은 길이 배열로 `onImagesChange`
  - 삭제: 해당 index를 제거한 배열
  - 드래그: 이동한 배열
  - 페이지 추가: 끝에 `null`을 추가한 배열. controller가 조건을 다시 검사한다.
- **불일치**: 없음

## 검증

- 공통 포맷 트리거 `formatting.py apply`
- `node --test tests/image-manager-slots.test.mjs tests/tutorial-contract.test.mjs tests/tutorial-controller.test.mjs`
- `npm run lint`, `npm run build`(아이템 폼 타입 호환 포함)

## 위험 요소 및 결정 사항

- **번들**: `@dnd-kit` 3개 패키지가 추가된다. 관리자 앱 메인 청크가 이미 500 kB를 넘으므로 영향은 build 출력으로 기록한다.
- **드래그 ID**: 슬롯에는 고유 ID가 없다(null 중복 가능). 드래그 중에는 배열이 바뀌지 않으므로 index 기반 ID를 쓴다.
- **업로드 고아 파일**: 업로드는 선택 즉시 서버에 저장되므로, 저장하지 않으면 스토리지에 파일이 남는다. 서버 동작이며 범위 밖이다.

<!-- asan-plan:approval:end:v1 -->

## 진행 기록 (해시 제외)

- 1차(2026-10-02): 목록·등록·수정 화면, 라우트·메뉴, `ImageManager` 1차 확장을 커밋했다(`2967764`). 내용은 [final-summary.md](final-summary.md)에 있다.
- 기획서 대조 후 사용자가 항목별 반영 여부를 결정했다. Logic 보완은 [handoff.md](handoff.md)로 인계했고, 반영 커밋 `811c8bb`를 검증했다(테스트 29/29, lint, build 통과).
- 1차 UI와 새 controller의 불일치 발견: 빈 칸이 있을 때 추가 타일이 업로드 후 무시된다. 2차에서 해소한다.

## 승인

- 상태: approved (2026-10-02 사용자 "작업 진행", 2차 범위·의존성 추가 포함)
- 필수 문구: `이 역할과 계획대로 진행할까요, 아니면 조정할 부분이 있나요?`
