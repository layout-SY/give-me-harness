# 인계

## Assignment 이동

- 보내는 host·session·role: Claude Code · `inquiry-ui` · `ui`
- 받는 host·session·제안 role: 미정(사용자가 시작할 Logic 세션) · 제안 role `logic`

## 역할 라우팅

- 요청 역할(`requested_roles`): ui, logic
- 확인된 역할(`confirmed_roles`): ui(현재 세션), logic(사용자가 "logic한테 먼저 controller부터 구현하라 할게"로 지시)
- 완료 역할(`completed_roles`): 없음(UI는 계약 정의만 완료, view 구현은 Logic 이후)
- 다음 제안 역할(`next_role`): logic
- 역할 판단 근거: controller hook은 entity query·mutation 연결, 검색 상태, 다이얼로그·라우팅 등 기능 로직이므로 Logic 담당. UI는 view·props 계약 담당.
- 사용자 확인: "view와 계약만 구현하면 돼", "UI 세션이 계약 먼저 정의(a)", "logic 핸드오프 문서에 추가 작성하면 돼"

## 목표 및 현재 상태

1:1 문의 관리 화면 3종(문의 목록, 문의 상세, 문의 유형 관리)을 `/manage` 운영관리 셸에 추가한다.
현재는 branch·worktree 생성과 controller 계약 정의까지 완료. 소스 변경은 없다.

## 완료된 작업

- 기존 아이템 화면(`src/pages/item/`, `src/pages/item-category/`)의 page → controller → view 구조와 공용 UI 확인
- `src/entities/inquiries/` 요청·응답 DTO와 hook 확인(아래 "확인한 API 계약")
- `feature/inquiry-ui` branch와 linked worktree 생성(사용자 승인, 부모 `sy-main` `4b0b7db`)
- 본 문서에 controller 계약 정의

## 대기 중인 작업

1. Logic: `inquiry.enum.ts` i18n 라벨 제거, controller 타입 파일과 controller hook 구현
2. UI(이후 세션): view·page·config·CSS·라우트·메뉴 구현

## 결정 사항 및 제약 조건 (사용자 확정)

| 항목 | 결정 |
|---|---|
| 범위 | 문의 목록·상세 + 문의 유형 관리 둘 다 |
| 경로 | 목록 `/manage/operations/inquiries`, 상세 `/manage/operations/inquiries/:inquiryId`, 유형 관리 `/manage/operations/inquiries/types` |
| 메뉴 | 운영관리 사이드 메뉴(`buildManageNavigationItems`)에 "1:1 문의" 노출 |
| 상태 표시명 | `OPEN` 접수(사용자가 올린 상태), `IN_PROGRESS` 처리중(관리자가 답변만 한 상태), `COMPLETED` 완료(관리자가 직접 완료) |
| 상태 전이 | 답변 등록 시 서버가 자동으로 `IN_PROGRESS`로 변경. 화면의 상태 변경은 "완료 처리"(→ `COMPLETED`) 하나만. 완료 이후 처리(되돌리기, 완료 후 답변 제한 등)는 나중으로 미룸 |
| 문의 목록 page size | 10 |
| 정렬 UI | 이번에는 구현하지 않음(`sort` 미전송) |
| 유형 등록 | `code`는 `INQUIRY_TYPE_CODES` enum 중 선택, `name` 입력 |
| 유형 수정 | `name`만 변경(`PUT {name}`), `code`는 수정 불가 |
| 표시 문자열 | i18n 사용하지 않음. 한글만 사용. 유형 코드 한글명은 나중에 추가하므로 지금은 enum 값(`USER_GUIDE` 등)을 그대로 표시 |
| 역할 분담 | UI는 view와 props 계약, Logic은 controller hook |

## 보내는 작업의 위치와 변경 상태

- project·저장소 루트: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`
- 현재 branch·HEAD·worktree: `feature/inquiry-ui` · `4b0b7db45aa9d15bf918a1a084370594e138a124` · `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/inquiry-ui`
- 확인 시점·인계 기준 commit: 2026-09-28, `4b0b7db`
- 완료한 commit: 없음
- staged·unstaged 변경: 없음
- untracked: 이 문서(`.claude/logs/sessions/inquiry-ui/handoff.md`)만
- 보존할 내용: 없음

## 인계 대상 작업 공간

### 작업 공간: inquiry-ui

- 수행할 기능·하위 작업: Logic controller 구현 → UI view 구현(순차)
- 사용할 역할: logic, 이후 ui
- project·저장소 루트: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`
- 목적지 branch: `feature/inquiry-ui`
- worktree 절대 경로·명령 실행 디렉터리: `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/inquiry-ui`
- 기존 공간(이번 세션에서 생성 완료, `git status -sb` → `## feature/inquiry-ui`)
- 확인한 HEAD: `4b0b7db`
- 직접 부모 branch: `sy-main`(relation create로 등록)
- 공유 선택과 이유: 같은 기능을 Logic → UI 순서로 연결하므로 한 공간 공유
- 진입 전 확인: `git -C <worktree> status -sb`, `git -C <worktree> log -1`로 branch·HEAD·미커밋 변경 확인
- 필요한 Git 작업: Logic 작업 commit(사용자 승인 필요)

## 역할별 상세 작업

### 역할·하위 작업: Logic — enum 정리

- 파일: `src/entities/inquiries/model/inquiry.enum.ts`
- 변경: i18n 키 라벨 상수 `INQUIRY_CUSTOMER_TYPE_LABELS`, `INQUIRY_TYPE_CODE_LABELS`(값이 `_inquiry_...` 번역 키)와 해당 타입 선언 제거. `INQUIRY_TYPE_CODES`, `INQUIRY_STATUS` 등 코드 상수는 유지.
- 사용처 확인 후 제거(현재 `src/` 내 사용처는 조사 시점에 발견하지 못함). 테스트(`tests/*inquir*`)가 참조하면 함께 확인.
- `INQUIRY_TYPE_CODES`를 `src/entities/inquiries/index.ts`에서 export(유형 코드 드롭다운 옵션용).

### 역할·하위 작업: Logic — controller 타입과 hook

- 사용할 작업 공간: inquiry-ui
- 만들 파일(경로는 기존 `src/pages/item*` 구조를 따름)
  - `src/pages/inquiry/model/inquiry-list.types.ts`, `inquiry-detail.types.ts`
  - `src/pages/inquiry/hook/use-inquiry-list-controller.tsx`, `use-inquiry-detail-controller.tsx`(필요 시 search-state·data hook 분리)
  - `src/pages/inquiry-type/model/inquiry-type.types.ts`
  - `src/pages/inquiry-type/hook/use-inquiry-type-controller.tsx`
- 재사용 자산: `useInquiryListQuery`, `useInquiryDetailQuery`, `useInquiryStatusMutation`, `useCreate/Update/DeleteInquiryAnswerMutation`, `useDeleteInquiryMutation`, `useInquiryTypeListQuery`, `useCreate/Update/DeleteInquiryTypeMutation`(`~/entities/inquiries`), `useDialog`(`~/shared/ui/dialog`), `KpiStripItem`, `TableSelection` 타입. 에러 알림·재조회 패턴은 `src/pages/item/hook/use-item-list-data.tsx`, 좌우 편집 패턴은 `src/pages/item-category/hook/use-item-category-controller.tsx` 참고.
- 경로 상수·상태 옵션은 UI가 `model/*.config.ts`에 만들 예정. Logic이 먼저 필요하면 아래 이름으로 만들고 UI가 이어서 확장한다.
  - `INQUIRY_ROUTES = { LIST: "/manage/operations/inquiries", TYPES: "/manage/operations/inquiries/types", detail: (id: number) => ... }`
  - `INQUIRY_PAGE_SIZE = 10`
  - `INQUIRY_STATUS_OPTIONS: Array<{ label: string; value: InquiryStatus }>`(접수/처리중/완료)
  - `INQUIRY_SEARCH_BY_OPTIONS: Array<{ label: string; value: InquirySearchBy }>`(`TITLE` 제목, `TITLE_CONTENT` 제목+내용)

#### 계약 1. 문의 목록 (`InquiryListController`)

```ts
import type { InquiryListResponseDto } from "~/entities/inquiries";
import type { KpiStripItem } from "~/widgets/admin-page-layout";

export type InquiryListRow = InquiryListResponseDto["items"][number];

export interface InquirySelectOption<T> {
  readonly label: string;
  readonly value: T;
}

interface InquiryListSearchController {
  readonly statusIndex: number; // INQUIRY_STATUS_OPTIONS 인덱스, -1 = 전체
  readonly typeOptions: InquirySelectOption<number>[]; // label=유형 name, value=유형 id
  readonly typeIndex: number; // -1 = 전체
  readonly searchByIndex: number; // INQUIRY_SEARCH_BY_OPTIONS 인덱스, -1 = 미선택
  readonly keyword: string;
  readonly onStatusChange: (index: number) => void;
  readonly onTypeChange: (index: number) => void;
  readonly onSearchByChange: (index: number) => void;
  readonly onKeywordChange: (value: string) => void;
  readonly onSubmit: () => void;
  readonly onReset: () => void;
}

interface InquiryListTableController {
  readonly rows: InquiryListRow[];
  readonly isFetching: boolean;
  readonly page: number | undefined;
  readonly pageCount: number | undefined;
  readonly pageSize: number; // 10
  readonly itemCount: number | undefined;
  readonly onPageChange: (page: number) => void;
  readonly onRowClick: ((row: InquiryListRow) => void) | undefined; // 상세로 이동
}

interface InquiryListRetryController {
  readonly isVisible: boolean;
  readonly isFetching: boolean;
  readonly onRetry: () => void;
}

export interface InquiryListController {
  readonly isPending: boolean;
  readonly kpiItems: KpiStripItem[]; // 최소 "전체 N건"
  readonly search: InquiryListSearchController;
  readonly table: InquiryListTableController;
  readonly retry: InquiryListRetryController;
  readonly onOpenTypes: () => void; // 유형 관리 화면으로 이동
}
```

- 검색 요청: `status`, `typeId`, `by`, `keyword`, `page`, `size=10`. `sort`는 보내지 않는다.
- `keyword`가 비어 있으면 `by`·`keyword`를 보내지 않는다. 검색어가 있는데 `by`가 미선택이면 처리 방식은 미정 → 아래 질문.

#### 계약 2. 문의 상세 (`InquiryDetailController`)

```ts
import type { InquiryDetailResponseDto } from "~/entities/inquiries";

interface InquiryDetailLoadController {
  readonly isFailed: boolean;
  readonly message: string;
  readonly isFetching: boolean;
  readonly onRetry: () => void;
}

interface InquiryAnswerController {
  /** 서버에 저장된 답변. null이면 등록 모드 */
  readonly saved: NonNullable<InquiryDetailResponseDto["answerContent"]> | null;
  /** 수정 중 여부. 등록 모드는 항상 true, 저장된 답변은 "수정" 누르면 true */
  readonly isEditing: boolean;
  readonly draft: string;
  readonly isSaving: boolean;
  readonly isDeleting: boolean;
  readonly canSave: boolean; // 공백 제외 1자 이상 + 변경 있음 + 비진행 중
  readonly onDraftChange: (value: string) => void;
  readonly onStartEdit: () => void;
  readonly onCancelEdit: () => void;
  readonly onSave: () => void; // saved === null → POST, 아니면 PUT
  readonly onDelete: () => void; // 확인 다이얼로그 후 DELETE answer
}

interface InquiryCompleteController {
  readonly isCompleted: boolean; // status === "COMPLETED"
  readonly isSaving: boolean;
  readonly canComplete: boolean; // 완료 아님 + 비진행 중
  readonly onComplete: () => void; // 확인 후 PATCH status COMPLETED
}

export interface InquiryDetailController {
  readonly isPending: boolean;
  readonly detail: InquiryDetailResponseDto | undefined;
  readonly load: InquiryDetailLoadController;
  readonly answer: InquiryAnswerController;
  readonly complete: InquiryCompleteController;
  readonly isDeleting: boolean;
  readonly onDelete: () => void; // 확인 후 DELETE 문의, 성공 시 목록으로
  readonly onBack: () => void;
}
```

- 답변 등록 성공 시 상태는 서버가 자동 변경하므로 클라이언트에서 상태 PATCH를 보내지 않는다(mutation 성공 후 기존 invalidate로 재조회).
- 완료 이후 답변 수정 제한·되돌리기는 이번 범위 밖.

#### 계약 3. 문의 유형 관리 (`InquiryTypeController`)

```ts
import type { InquiryTypeResponseDto } from "~/entities/inquiries";
import type { INQUIRY_TYPE_CODES } from "~/entities/inquiries";
import type { KpiStripItem } from "~/widgets/admin-page-layout";

interface InquiryTypeTableController {
  readonly rows: InquiryTypeResponseDto[];
  readonly isFetching: boolean;
  readonly selectedRowId: number | null;
  readonly page: number | undefined;
  readonly pageCount: number | undefined;
  readonly pageSize: number;
  readonly itemCount: number | undefined;
  readonly onPageChange: (page: number) => void;
  readonly onRowClick: (row: InquiryTypeResponseDto) => void;
}

interface InquiryTypeFormController {
  /** null이면 신규 등록, 값이 있으면 name 수정 */
  readonly target: InquiryTypeResponseDto | null;
  /** 등록 시 선택 가능 코드. label은 지금 enum 값 그대로 */
  readonly codeOptions: Array<{ readonly label: string; readonly value: INQUIRY_TYPE_CODES }>;
  readonly codeIndex: number; // 수정 모드에서는 target.code 위치, 선택 잠금
  readonly name: string;
  readonly isSaving: boolean;
  readonly isDeleting: boolean;
  readonly canSave: boolean;
  readonly onCodeChange: (index: number) => void;
  readonly onNameChange: (value: string) => void;
  readonly onSave: () => void; // target null → POST {code,name}, 아니면 PUT {name}
  readonly onDelete: () => void; // 확인 후 DELETE
  readonly onStartCreate: () => void;
}

export interface InquiryTypeController {
  readonly isPending: boolean;
  readonly kpiItems: KpiStripItem[];
  readonly table: InquiryTypeTableController;
  readonly form: InquiryTypeFormController;
  readonly retry: { readonly isVisible: boolean; readonly isFetching: boolean; readonly onRetry: () => void };
  readonly onBackToList: () => void; // 문의 목록으로
}
```

- 확인 근거: `src/entities/inquiries/api/inquiry.dto.ts`, `inquiry-type.dto.ts`, `inquiry.api.ts`, `inquiry-type.api.ts`, `hook/*`, `model/inquiry-mutation-options.ts`
- 선행 조건·순서: enum 정리 → 타입 파일 → controller hook → lint·build·test
- 겹치는 파일: `model/*.types.ts`는 Logic이 만들고 UI가 import. UI가 수정이 필요하면 사용자에게 보고 후 조율. `model/*.config.ts`는 UI가 주로 작성.
- 완료 기준: 타입·hook이 `npm run lint`, `npm run build`, `npm run test` 통과. page·view 없이 hook만 있어도 빌드되어야 함(미사용 export 허용 여부는 lint 결과로 확인).

#### Logic이 사용자에게 확인해야 할 미정 사항

1. 목록 유형 필터·유형 관리 표에서 유형 목록 API(`page`, `size`)를 어떤 `size`로 조회할지(문의 목록 size 10은 확정, 유형 목록 size는 미정. enum 코드는 12개).
2. 검색어가 있는데 검색 대상(`by`)을 선택하지 않았을 때의 처리(기본값 `TITLE` 적용 / 검색 버튼 비활성 / 미전송).
3. 유형 삭제 시 해당 유형을 쓰는 문의가 있으면 서버 동작(에러 메시지 표시 방식).

### 역할·하위 작업: UI — view 구현(Logic 완료 후)

- 파일: `src/pages/inquiry/{index.ts, ui/inquiry-list-page.tsx, ui/inquiry-list-view.tsx, ui/inquiry-detail-page.tsx, ui/inquiry-detail-view.tsx, ui/inquiry.css, model/inquiry.config.ts}`, `src/pages/inquiry-type/{index.ts, ui/inquiry-type-page.tsx, ui/inquiry-type-view.tsx, ui/inquiry-type-form-panel.tsx, model/inquiry-type.config.ts}`, `src/app/router/routes.tsx`, `src/widgets/side-navigation/lib/build-navigation-items.ts`
- 재사용: `PageHeader`, `KpiStrip`, `FilterBar`, `MasterDetailLayout`, `ActionBar`, `SectionCard`, `Table`, `Dropdown`, `TextInput`, `TextArea`, `Button`, `Loading`, `DefinitionList`
- 완료 기준: 포맷 트리거 후 lint·build·test 통과

## 협업 순서와 Git 통합

- 공유 공간 순서: Logic 수정·검증·commit → UI 세션이 최신 HEAD·handoff 재확인 후 view 구현 → commit
- 통합: `feature/inquiry-ui` → 직접 부모 `sy-main`(완료 시 별도 검토·승인)
- 형제: `feature/citizen-proposal-vote-api`(같은 `4b0b7db`에서 분기, 진행 중). 겹칠 수 있는 파일: `src/app/router/routes.tsx`, 사이드 메뉴 파일 → 통합 시 비교 필요
- 승인된 Git 작업: branch·worktree 생성(완료) / 미승인: 모든 commit·merge
- 산출물 책임: contributor

## 관련 경로와 스킬

- `.agent-policy/common/skills/policy/task-role-routing/references/logic.md`, `ui.md`
- `src/pages/item/`, `src/pages/item-category/`, `src/entities/inquiries/`

## 명령어 및 결과

- `git_operations.py relation --action create --name feature/inquiry-ui --parent sy-main --fork 4b0b7db...` → `execute 35b334b19324495495d19cc5cb07007f` 성공(stage `done`)
- `git -C <worktree> status -sb` → `## feature/inquiry-ui`, 변경 없음

## 실행하지 않은 검증

- 소스 변경이 없어 lint·build·test 미실행

## 2026-09-29 UI 구현 결과

- 기준: Logic commit `840051e`(sy-main에 `deb11f9`로 통합됨) 위에서 작업. 사용자 결정 (a)에 따라 sy-main 동기화 merge는 하지 않음.
- 신규: `src/pages/inquiry/{index.ts, lib/inquiry-display.ts, model/inquiry.columns.ts, ui/inquiry-list-page.tsx, ui/inquiry-list-view.tsx, ui/inquiry-detail-page.tsx, ui/inquiry-detail-view.tsx, ui/inquiry.css}`, `src/pages/inquiry-type/{index.ts, ui/inquiry-type-page.tsx, ui/inquiry-type-view.tsx, ui/inquiry-type-form-panel.tsx}`
- 수정: `src/pages/inquiry-type/model/inquiry-type.config.ts`(표 컬럼 추가), `src/app/router/routes.tsx`(경로 3개, types를 :inquiryId보다 먼저), `src/widgets/side-navigation/lib/build-navigation-items.ts`(라우트가 있는 하위 메뉴만 노출 → 아이템 관리 + 운영 관리 > 1:1 문의)
- Logic controller·타입은 변경하지 않음.
- 검증: 포맷 트리거 15개 파일, `npm run lint` 통과, `npm run build` 통과(기존 chunk 경고), 문의 테스트 71개 통과.
- 미완료: `docs/admin-routes.md`(sy-main에만 존재) 갱신은 sy-main 통합 후. 브라우저 확인은 미실행. commit·merge 미승인.

## 다음 조치

1. (완료) 사용자가 Logic 세션을 `--worktree /Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/inquiry-ui`로 시작하고 이 문서를 전달
2. Logic 완료 후 UI 세션에서 view 구현
