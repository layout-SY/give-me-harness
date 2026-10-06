# 인계 — 튜토리얼 편집 controller 보완 (기획서 반영)

확인된 사실, 사용자 결정, 제안, 미정 항목을 구분해 적는다.

## Assignment 이동

- 보내는 host·session·role: Claude Code · 튜토리얼-관리-UI · `ui`
- 받는 host·session·제안 role: 미정(사용자 선택) · 새 세션 · `logic`

## 역할 라우팅

- 요청 역할: ui. 사용자가 기획서 대조 후 "logic에서 작업해야 하는 내용들은 핸드오프 문서로 남겨"라고 요청했다.
- 확인된 역할: ui (inject `--role ui`)
- 완료 역할: ui 1차 구현(미커밋, 아래 "보내는 작업의 위치" 참고)
- 다음 제안 역할(`next_role`): logic → 완료 후 ui(2차 이미지 편집 UI)
- 역할 판단 근거: 제목 길이·페이지 수 제한, 등록 초기 슬롯은 업무 검증·편집 상태 규칙이다. `src/pages/tutorial/hook/use-tutorial-editor-controller.ts`의 controller 책임이다(Logic 경계).

## 목표 및 현재 상태

- **기준 문서**: `/Users/okand/Downloads/아산시 메타버스_튜토리얼 시스템기획서.pptx.pdf`, "관리자 페이지" p9~p13. p11 페이지 추가, p12 페이지 수정, p13 페이지 삭제.
- **목표**: 사용자가 기획서에서 반영하기로 한 항목 중 controller 규칙을 Logic이 보완한다. UI는 그 계약으로 이미지 편집 화면을 다시 구성한다.
- **현재 상태**: controller(`6b96d7b`)는 제목 공백 검증만 하고, 페이지 수 제한이 없으며, 등록을 이미지 0개로 시작한다.

## 결정 사항 (사용자 확정, 2026-10-02)

| 항목 | 결정 | 담당 |
| --- | --- | --- |
| 메뉴 위치, 화면 제목, 화면 구조(목록/등록/수정 분리), 목록 컬럼, 목록 상단, 날짜 형식, 목록에서 삭제 | 현상 유지 | — |
| 등록 버튼 활성 조건 | 현상 유지: 제목만 필수, 이미지 0개·빈 칸도 등록 가능 | 변경 없음 |
| 제목 입력 | 기획서대로 최대 30자, 글자 수 표시(`n/30`) | **Logic**(검증), UI(카운터) |
| 이미지 영역 기본값 | **등록 화면만** 빈 칸 3개로 시작. 수정 화면은 저장된 페이지만 표시 | **Logic** |
| 페이지 추가 | 기획서대로. "+ 페이지 추가", **최대 20페이지**. 기존 칸을 모두 사용(빈 칸 없음)했을 때 맨 아래에 한 칸 추가 | **Logic**(제한·가능 여부), UI(버튼) |
| 이미지 레이아웃 | 기획서대로 세로 목록(번호, 드래그 핸들, 썸네일, 안내 문구, 수정·삭제 버튼) | UI |
| 이미지 교체 | 기획서대로. "수정"으로 파일을 골라 그 칸을 교체 | UI(기존 `onImagesChange`·`uploadApi`로 가능) |
| 이미지 삭제 | 기획서대로 확인 팝업 후 **칸 제거**(뒤 번호 당김). 빈 칸은 확인 없이 제거 | UI(기존 `onRemoveImage`로 가능) |
| 순서 변경 | 기획서대로 드래그. **`@dnd-kit` 도입** | UI(기존 `onMoveImage`/`onImagesChange`로 가능). 의존성 설치는 UI 계획에서 별도 승인 |
| 빈 칸 저장 | 현재 동작 유지(`imageUrl: null`로 전송) | 변경 없음 |

## 역할별 상세 작업

### 역할·하위 작업: Logic — 편집 controller 규칙 보완

- **사용할 작업 공간**: `feature/tutorial` 공유 공간(아래)
- **수정 대상**
  - `src/pages/tutorial/hook/use-tutorial-editor-controller.ts`
  - `src/pages/tutorial/model/tutorial-controller.types.ts`
  - 필요하면 `src/pages/tutorial/lib/tutorial-controller.model.ts`
  - 테스트: `tests/tutorial-controller.test.mjs`
- **변경 내용(요구)**
  1. **제목 최대 30자**
     - 30자를 넘으면 `titleError`에 메시지를 둔다(예: "제목은 30자 이하로 입력해 주세요."). `canSave`는 false가 된다. 공백 검증은 유지한다.
     - 글자 수 기준(UTF-16 `length` 또는 코드 포인트)을 정한다. UI 카운터가 같은 값을 쓰도록 공개한다.
     - 제안 필드: `fields.titleLength: number`, `fields.titleMaxLength: 30`
     - 서버 API에는 최대 길이 명세가 없다(Swagger는 `minLength: 1`만 있음). 서버 제한 여부는 확인하지 못했다.
  2. **등록 초기 슬롯 3개**
     - `mode === "create"`의 초기 `images`를 `[null, null, null]`로 둔다.
     - 등록 모드의 `canSave`는 지금처럼 제목만 본다. 빈 칸 3개 그대로 저장하면 `imageUrl: null` 3개가 전송된다(현재 동작 유지 결정).
     - 수정 모드는 바뀌지 않는다.
  3. **최대 20페이지와 페이지 추가 가능 여부**
     - `onAddEmpty`는 페이지가 20개 이상이면 무시한다.
     - `onImagesChange`도 20개를 넘는 배열은 반영하지 않는다(UI의 `ImageManager`가 전체 배열을 넘기는 경로).
     - 제안 필드: `fields.maxImages: 20`, `fields.canAddImage: boolean`(= 편집 가능 && `images.length < 20` && 빈 칸 없음)
     - 수정 모드에서 서버 데이터가 이미 20개를 넘는 경우 처리(표시는 하고 추가만 막을지)를 정해 계약 문서에 적는다.
- **바꾸지 않는 것**
  - `onRemoveImage`, `onMoveImage`, `uploadApi`, `save`·`delete` 동작
  - 이미지 삭제 확인 팝업은 UI가 띄운다. controller에는 이미지 단위 확인 상태가 필요 없다.
- **연결 방향**: Logic 선행(`controller <- UI`). 새 필드 이름·의미는 Logic 계약 문서(`.codex/logs/sessions/tutorial-api-controller/unknown/controller-contract.md` 또는 새 세션 문서)에 기록한다. 위 제안 필드명과 다르게 정하면 그 문서를 기준으로 UI가 맞춘다.
- **완료 기준**: 다음 경계를 controller 테스트로 확인하고, `npm run lint`·`npm run build`를 통과한다.
  - 30/31자 경계
  - 등록 초기 3칸, 수정 모드 미적용
  - 20개 경계(`onAddEmpty`·`onImagesChange`)
  - 빈 칸이 있을 때 추가 불가

### 역할·하위 작업: UI — 이미지 편집 2차 (Logic 완료 후, 참고용)

- `ImageManager`에 세로 목록 형태를 추가한다. 행 구성은 번호, 드래그 핸들, 썸네일, "권장 사이즈 1200x675 / PNG, JPG 파일만 가능", 수정·삭제 버튼이다. 빈 칸은 업로드 영역으로 표시한다.
- 드래그 정렬은 `@dnd-kit`를 공용 어댑터로 감싸 구현한다.
- 이미지 삭제 확인 팝업 문구: "이미지를 삭제하시겠습니까? * 삭제된 이미지는 복구할수 없습니다."
- "+ 페이지 추가 / 최대 20페이지까지 추가 가능합니다."를 추가하고, 제목 `n/30` 카운터를 표시한다.
- 1차의 가로 타일과 ◀▶ 이동 방식은 2차에서 이 형태로 교체한다.
- 시작 시 `ui-library` 자산 선정 갱신, `@dnd-kit` 설치 승인, 라이브러리 스킬 초안을 진행한다.

## 보내는 작업의 위치와 변경 상태

- **위치**: `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/tutorial`, `feature/tutorial`, HEAD `6b96d7b`(Logic 커밋), 직접 부모 `sy-main`
- **미커밋 변경(UI 1차, 이 세션 작성, 검증 통과)**
  - 수정: `docs/admin-routes.md`, `src/app/router/routes.tsx`, `src/features/image-manager/ui/{ImageManager.css,ImageManager.tsx,types.ts,hooks/useImageSlots.tsx}`, `src/pages/tutorial/index.ts`, `src/widgets/side-navigation/{lib/build-navigation-items.ts,model/_navigation2.ts}`
  - 신규: `src/features/image-manager/lib/image-slots.ts`, `src/features/image-manager/ui/components/ImageSlotEmpty.tsx`, `src/pages/tutorial/{lib/tutorial-display.ts,model/tutorial.columns.ts}`, `src/pages/tutorial/ui/{tutorial-list-page,tutorial-list-view,tutorial-editor-page,tutorial-editor-view}.tsx`, `src/pages/tutorial/ui/tutorial.css`, `tests/image-manager-slots.test.mjs`
- **보존할 내용**: 위 UI 변경. Logic은 이 파일들을 수정하지 않는다. 겹치는 파일은 없다. 단, `tutorial-editor-view.tsx`는 controller 필드를 읽으므로 공개 타입 변경 시 build로 호환성을 확인한다.

## 인계 대상 작업 공간

### 작업 공간: tutorial

- **project·경로**: admin-ui, `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/tutorial`(명령 실행 디렉터리 동일)
- **branch**: `feature/tutorial`(기존 공간, HEAD `6b96d7b` 확인), 직접 부모 `sy-main`
- **공유 방식**: Logic과 UI가 순차로 공유한다. 동시에 수정하지 않는다.
- **진입 전 확인**: `git status`로 위 UI 미커밋 변경의 존재를 확인한다.
- **Git**: UI 1차 변경은 사용자 승인 후 `2967764 feat(tutorial): 튜토리얼 목록·등록·수정 화면과 라우트·메뉴 연결`로 커밋했다(2026-10-02, 19개 파일). Logic은 HEAD `2967764`, 미커밋 변경 없음 상태에서 시작한다.

## 협업 순서와 Git 통합

1. (선택) UI 1차 커밋: 사용자 승인 필요
2. Logic controller 보완·커밋: Logic 세션이 승인받는다
3. UI 2차(이미지 편집 재구성, `@dnd-kit`)
4. `sy-main` 통합: 별도 승인

- 승인된 Git 작업: 없음
- 산출물 책임: contributor(이 handoff), owner(UI 1차 `final-summary.md`)

## 관련 경로와 스킬

- UI 자산 선정: [UI 자산 선정 계획](unknown/ui-asset-plan.md). 2차 시작 시 `@dnd-kit`과 목록 레이아웃 항목을 갱신한다.
- 외부 라이브러리 스킬
  - `unknown/ui-library-skills/heroui-react/SKILL.md`(초안, 중앙 등록 전)
  - `@dnd-kit`은 2차에서 새로 작성한다.
- Logic 스킬: task-role-routing(logic.md), api-authoring/ui-controller, documentation

## 실행하지 않은 검증

- 이번 handoff 작성에서는 소스를 변경하지 않았다. 1차 UI 검증 결과(테스트 23/23, lint, build)는 `final-summary.md`에 있다.

## UI 2차 진행 상태 (2026-10-02, 미완료)

- **기준**: Logic `811c8bb` 검증을 완료했다(29/29, lint, build). 2차 계획은 사용자 승인을 받았다(`plan.md`).
- **구현 완료, 미커밋**
  - `package.json`·`package-lock.json`: `@dnd-kit/core` 6.3.1, `@dnd-kit/sortable` 10.0.0, `@dnd-kit/utilities` 3.2.2 설치
  - 신규 `src/shared/ui/sortable-list/sortable-list.{tsx,css}`
  - 신규 `src/features/image-manager/ui/components/ImageSlot{List,Row}.{tsx,css}`
  - 수정 `ImageManager.{tsx,css}`, `types.ts`: 타일은 1차 이전 동작으로 되돌렸고, `layout="list"`를 추가했다.
  - 수정 `src/pages/tutorial/ui/tutorial-editor-view.tsx`, `tutorial.css`: 제목 `n/30`, 목록 레이아웃, 삭제 확인 문구
- **삭제 대기**: `src/features/image-manager/ui/components/ImageSlotEmpty.tsx`. 셸 삭제는 정책상 차단되어, 커밋 시 `git rm`으로 처리한다. 현재 import하는 곳은 없다.
- **차단**
  - `ImageManager.css` Write 직후 PostToolUse hook이 8초 제한을 넘겨, 결과 미확인 쓰기 기록이 남았다.
  - 그래서 `formatting.py apply`와 lint·test·build가 PreToolUse에서 막히고, Stop hook도 같은 이유로 종료를 막는다.
  - 파일 내용은 정상이다. 동일 내용 재기록에는 성공했지만 기존 기록이 해소되지 않았다.
  - 기록 ID를 이 세션에서 조회할 수 없어 `write-recovery --id`를 실행하지 못했다.
- **미실행 검증**: 포맷, `node --test`, `npm run lint`, `npm run build`. 타입 오류가 있을 수 있다.

## 다음 조치

1. 사용자: UI 1차 커밋 여부를 결정하고, `--role logic` 세션을 시작한다.
2. Logic: 이 문서의 "Logic — 편집 controller 규칙 보완"을 구현·검증하고, 계약 문서를 갱신한다.
3. UI(`--role ui`): Logic 계약을 읽고 2차 계획(자산 선정, `@dnd-kit` 승인 포함)을 세운다.
