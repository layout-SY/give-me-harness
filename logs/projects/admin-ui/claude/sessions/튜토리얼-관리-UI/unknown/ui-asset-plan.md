# UI 자산 선정 계획 — 튜토리얼 관리

## 작업과 조사 근거

- **요구사항·범위**: 튜토리얼 목록 화면, 등록 화면, 상세·수정 화면. Logic 선행 controller에 연결하고, 라우트·메뉴를 연결하고, `ImageManager`를 확장한다.
- **대상**: admin-ui, `feature/tutorial`, `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/tutorial`, HEAD `987616b`. Logic 소스 19개는 untracked 상태다.
- **스택 근거**: `package.json`
  - `react` ^19.2.7, `react-router-dom` ^7.18.1, `@heroui/react` ^3.2.3
  - `test` script는 없다. 테스트는 `node --test` 파일로 실행한다.
- **조사한 경로**
  - 화면 스타일 기준: `src/pages/inquiry/ui/*`(목록·상세 분리), `src/pages/item-category/ui/*`
  - 공용 위젯: `src/widgets/admin-page-layout`(`PageHeader`, `KpiStrip`, `ActionBar`)
  - 공용 UI: `src/shared/ui/{button,icon-button,text-input,section-card,table,loading,modal,dialog}`
  - 이미지 관리: `src/features/image-manager/ui/*`. 현재 사용처는 `src/pages/item/ui/item-form-sections.tsx` 1곳이다.
  - 라우터·메뉴: `src/app/router/routes.tsx`, `src/widgets/side-navigation/{lib/build-navigation-items.ts,model/_navigation2.ts}`
- **디자인 기준**: 사용자 지시에 따라 기존 페이지 스타일을 그대로 따른다.
  - `cp-page`, `cp-field-label`, `cp-caption` 토큰을 쓰고 새 색상·토큰은 만들지 않는다.
  - `frontend-design` 스킬은 새 시각 방향을 정하는 용도라 이번에는 적용하지 않는다.
- **상태 소유권**
  - 서버 데이터·편집 draft·삭제 확인·미리보기 상태는 controller가 소유한다.
  - UI는 표시하고 callback을 호출하며, 확인창을 띄우고 화면을 이동한다.

## 구현 항목별 선택

| UI 항목 | 선택 | 자산·경로 | 이유·근거 | 계약·예상 변경·검증 | 결정 상태 |
| --- | --- | --- | --- | --- | --- |
| 페이지 골격(헤더·하단 버튼) | 기존 공용 재사용 | `~/widgets/admin-page-layout`의 `PageHeader`, `ActionBar`, `KpiStrip` | 문의·카테고리 화면과 같은 골격 | 변경 없음 | 확정 |
| 목록 표 | 기존 공용 재사용 | `~/shared/ui/table/table` | 문의 목록과 같다. 페이지네이션 없이 rows만 전달한다 | 컬럼은 ID·제목·페이지 수·등록일·수정일. `onRowClick`으로 상세 이동 | 확정 |
| 섹션 카드 | 기존 공용 재사용 | `~/shared/ui/section-card/section-card` | 기존 패턴 | 변경 없음 | 확정 |
| 제목 입력 | 기존 공용 재사용 | `~/shared/ui/text-input/text-input` | 카테고리 폼과 같다 | `fields.title`, `onTitleChange`. `titleError`는 `cp-caption`으로 표시 | 확정 |
| 버튼(등록·저장·삭제·목록) | 기존 공용 재사용(HeroUI 어댑터) | `~/shared/ui/button/button` | 기존 패턴 | `isLoading`·`disabled`를 controller 상태에 연결 | 확정 |
| 로딩 | 기존 공용 재사용 | `~/shared/ui/loading/loading` | 기존 패턴 | `load.isPending` | 확정 |
| 삭제 확인·완료 알림 | 기존 공용 재사용 | `useDialog`(`~/shared/ui/dialog`) | 카테고리·문의 화면이 `Dialog.confirm`/`alert` 사용 | `delete.onRequest` → `Dialog.confirm` → `onConfirm` 또는 `onCancel` | 확정 |
| 이미지 페이지 편집(추가·삭제) | 기존 공용 재사용 | `ImageManager` | 사용자 결정: ImageManager 확장 | `images`·`onChange`·`uploadApi`를 `fields.images`·`onImagesChange`·`uploadApi`에 연결 | 확정 |
| 이미지 순서 변경 | 기존 자산 확장 | `ImageManager`에 `reorderable?: boolean` 추가, 이동 버튼은 `IconButton`과 `chevron-left/right` 아이콘 | 현재 추가·삭제만 지원 | 앞·뒤 이동 결과 배열을 `onChange`로 전달. 첫·끝 슬롯은 해당 방향 비활성. 기본값 false라 아이템 폼 무변경 | 확정(사용자 선택) |
| 빈 자리(null) 표시·추가·채우기 | 기존 자산 확장 | `ImageManager`에 `allowEmptySlots`(타입상 null 허용 배열과 묶음) 추가, `components/ImageSlotEmpty` 신규 | null 슬롯 미지원 | 빈 슬롯은 점선 자리로 표시. 누르면 파일을 골라 그 index를 채우고, 삭제할 수 있다. "빈 페이지 추가"는 끝에 null 추가 | 확정(사용자 선택) |
| 페이지 번호 | 기존 자산 확장 | `reorderable` 슬롯 아래 `N페이지` 라벨 | 저장 순서 = 표시 순서를 보여 준다 | `ImageManager.css`에만 추가 | 제안 |
| 이미지 미리보기 | 기존 공용 재사용 | `~/shared/ui/modal/modal`(HeroUI 어댑터) + `<img>` | 공용 `ImageModal`은 pubsub 구동이고 이벤트 셸에만 마운트되어 있다. controller의 `preview` 상태를 쓰려면 prop 구동 모달이 맞다 | `preview.url`, `onClose`. `ImageManager.onPreview`에 index를 둘째 인자로 추가(기존 호출 호환)해 `preview.onOpen(index)` 호출 | 제안 |
| 슬롯 조작 계산(이동·채우기·빈 자리) | 기존 자산 확장 | `src/features/image-manager/lib/image-slots.ts`(순수 함수) | UI 렌더와 분리해 node 테스트로 검증 | `tests/image-manager-slots.test.mjs` | 제안 |

## 계약과 공용화 영향

- **`ImageManager` 확장 계약(제안)**
  - 기존 props는 그대로 둔다: `images: string[]`, `onChange(images: string[])`, `uploadApi`, `maxImages`, `isEditing`, `onPreview`, `accept`, `scope`, `className`, `disabled`.
  - `reorderable?: boolean`(기본 false)을 추가한다.
  - `allowEmptySlots: true`일 때만 `images`·`onChange` 타입이 `(string | null)[]`이 되도록 판별 유니온 props로 정의한다. 아이템 폼의 타입은 바뀌지 않는다.
  - `onPreview(url, index)`: 둘째 인자를 추가한다. 기존 `(url) => …` 호출은 그대로 호환된다.
  - 빈 슬롯 채우기: 업로드 성공 URL로 해당 index를 교체한 배열을 `onChange`로 전달한다.
- **아이템 폼 영향**: 새 props를 넘기지 않는다. 렌더 결과·업로드(`file`+`type`)는 그대로다. 검증은 `npm run build` 타입 검사와 코드 검토로 한다.
- **업로드 경로**
  - `ImageManager` 내부 `useImageUpload`가 `file`과 `type`을 담은 FormData를 `fields.uploadApi`로 보낸다.
  - controller는 `file`만 추출한다(Logic 계약). 따라서 `onAddImage(File)` 경로는 쓰지 않는다. 같은 파일을 두 경로로 보내지 않기 위해서다.
- **번들·의존성**: 새 의존성은 없다. 아이콘·HeroUI 어댑터는 기존 것을 쓴다.
- **미정 항목**: 없음. 페이지 번호 라벨과 미리보기 모달 방식은 이 승인 요청에서 함께 확인한다.

## UI·Logic 연결

- **선행 구현**: Logic(`.codex/logs/sessions/tutorial-api-controller/unknown/controller-contract.md`). 방향은 `controller <- UI`.
- **controller**: `src/pages/tutorial/index.ts`
  - 목록: `useTutorialListController`
  - 등록·수정: `useTutorialEditorController(mode, tutorialId)`
  - 타입: `model/tutorial-controller.types.ts`
- **목록 매핑**
  - `items[]`(`id/title/pageCount/createdAt/updatedAt`)를 표 행으로 쓴다.
  - `isEmpty`는 표의 빈 상태, `load.isFailed`는 "다시 조회"(`load.onRetry`)로 연결한다.
- **편집 매핑**
  - `fields.*`는 제목·이미지 편집, `save.onSave()`는 저장 버튼에 연결한다.
  - `delete.*`는 삭제 확인, `preview.*`는 모달에 연결한다.
  - `isNotFound`이면 "존재하지 않는 튜토리얼" 화면과 목록 버튼을 보여 준다.
- **이동(사용자 확정 2026-10-02)**
  - 등록·수정 저장 결과가 `success`이면 완료 알림 후 `/manage/operations/tutorials`로 이동한다.
  - `delete.onConfirm()` 결과가 `success`이면 완료 알림 후 같은 목록으로 이동한다.
  - `failed`/`busy`/`canceled`이면 이동하지 않는다.
- **오류 표시**: 서버 오류는 공통 reporter가 표시한다. UI는 `save.errorMessage`·`delete.errorMessage`·`load.errorMessage`가 있을 때만 `cp-caption`으로 보조 표시하고, 같은 오류를 별도 alert로 다시 띄우지 않는다.
- **불일치**: 없음. Logic 문서상 미확정이던 경로는 사용자가 2026-09-30 질문에서 확정했다.

## 외부 UI 라이브러리 스킬

| 패키지·버전 | 사용 목적·항목 | 어댑터·공개 계약 | 기존 스킬 | 세션 초안·중앙 경로 | 상태 |
| --- | --- | --- | --- | --- | --- |
| `@heroui/react` ^3.2.3 | 버튼, 아이콘 버튼(이동), 미리보기 모달 | `src/shared/ui/{button,icon-button,modal}` | 없음(`reference/libraries/`에 개별 문서 없음) | `unknown/ui-library-skills/heroui-react/SKILL.md` → 중앙 `policy/common/skills/reference/libraries/heroui-react/SKILL.md` | 구현 착수 직후, 사용 전에 초안 작성 예정 |

## 2차 항목 (기획서 p11·p12 반영, 2026-10-02)

| UI 항목 | 선택 | 자산·경로 | 이유·근거 | 계약·검증 | 결정 상태 |
| --- | --- | --- | --- | --- | --- |
| 드래그 순서 변경 | 외부 라이브러리 사용 | `@dnd-kit/core` 6.3.1, `@dnd-kit/sortable` 10.0.0, `@dnd-kit/utilities` 3.2.2 → 어댑터 `src/shared/ui/sortable-list/sortable-list.tsx` | 저장소에 드래그 구현·의존성이 없다(`package.json`, `src` 검색 결과 0건). 사용자가 접근성·터치 지원을 이유로 도입을 결정했다. `@dnd-kit/react` 0.x는 안정 전이라 제외 | `items`, `getItemId`, `onMove(from,to)`, `disabled`, `renderItem(item,index,handle)`. build·lint로 확인 | 확정(사용자 선택) |
| 세로 이미지 목록(번호·핸들·썸네일·안내·수정·삭제) | 기존 자산 확장 | `ImageManager`에 `layout: "list"` 추가, `components/ImageSlotRow.tsx` 신규 | 사용자 결정 "ImageManager 확장"을 유지한다. 1차의 `reorderable`·`allowEmptySlots`는 튜토리얼만 사용하므로 대체한다 | 판별 유니온 `layout:"list"`에서만 `(string\|null)[]`를 허용한다. 아이템 폼 타일은 무변경 | 승인 대기 |
| 이미지 삭제 확인 | 기존 공용 재사용 | `useDialog().confirm` | 기존 확인 팝업 패턴 | 문구는 호출부 `removeConfirm`으로 받는다 | 승인 대기 |
| 이미지 수정(교체) | 기존 자산 재사용 | `ImageSlotAdd`의 파일 선택 패턴, `useImageUpload` | 업로드 검증(JPG·PNG)을 공유한다 | 업로드 성공 URL로 같은 index를 교체 | 승인 대기 |
| 페이지 추가 버튼 | 기존 공용 재사용 | `Button`(HeroUI 어댑터), `add.icon` | 기존 버튼 | `canAddSlot`(= controller `canAddImage`) | 승인 대기 |
| 제목 글자 수 카운터 | 화면 로컬 마크업 | `tutorial-editor-view.tsx`, `cp-caption` | `TextInput`에 카운터 옵션이 없다. 한 화면 전용이라 공용화 근거가 없다 | `titleLength/titleMaxLength`(controller 값 그대로) | 승인 대기 |

- **제거 예정**: 1차 `components/ImageSlotEmpty.tsx`, `ImageManager.css`의 이동 화살표·순번 규칙, `types.ts`의 `reorderable`·`allowEmptySlots`. 모두 튜토리얼 외 사용처가 없다(`grep` 확인).
- **외부 라이브러리 스킬**: `unknown/ui-library-skills/dnd-kit/SKILL.md`(세션 초안) → 중앙 `policy/common/skills/reference/libraries/dnd-kit/SKILL.md`. 상태는 구현 착수 직후 작성 예정이다.

## 승인과 변경

- 승인 요청에 포함할 항목: 위 표 전체. 제안 상태 항목은 페이지 번호 라벨, Modal 미리보기, 순수 함수 분리와 테스트다.
- 사용자 승인 근거: 2026-10-02 "그대로 작업 진행". 제안 항목 모두 승인됐다.
- 구현 중 달라진 항목: 순번 라벨을 "N페이지"에서 숫자 `N`으로 바꿨다. 공용 feature에 튜토리얼 전용 문구를 넣지 않기 위해서다. 나머지 계약은 계획과 같다.
