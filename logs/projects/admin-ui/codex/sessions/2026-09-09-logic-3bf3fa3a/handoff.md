# 인계

기존 게시판을 유지하면서 공지사항 전용 관리 화면을 추가하는 방향을 사용자가 승인했다. `/admin/news` API와 조회·변경 hook, 기존 공지 수정 폼 연결은 구현되어 있다. 다음 작업은 전용 목록·등록·수정·삭제 UI와 이를 연결할 페이지 controller다. 이 문서는 UI 담당자에게 전달하는 구현 근거와 계약 초안이며, 이번 세션에서는 애플리케이션 코드를 변경하지 않았다.

## Assignment 이동

- 작성일: 2026-09-09, Asia/Seoul.
- 보내는 host·assignment·role: `codex` / `3bf3fa3a8b804e8fb4bf28a99fc37a68` / `logic`.
- native session: `01a08425-00ef-7600-a265-2f5d67c4ecd2`.
- 현재 산출물 디렉터리: `.codex/logs/sessions/2026-09-09-logic-3bf3fa3a/`.
- 받는 host·session: 미지정. UI 작업을 담당할 새 `--role ui` 세션이 이 문서를 읽는다.
- 인계 순서: UI 담당이 화면과 props/callback 계약 작성 → Logic 담당이 페이지 상태·검증·API 연결 → UI 담당이 준비된 페이지의 라우트·메뉴 연결 → 통합 검증.
- 다음 담당자는 현재 파일과 Git 상태를 다시 확인한다. 이 문서가 세션 이동이나 새 브랜치 생성을 실행한 것은 아니다.

## 역할 라우팅

- `requested_roles`: 공지 후속 작업의 UI 역할, 현재 Logic 역할의 UI 인계 문서 작성.
- `confirmed_roles`: 현재 세션은 inject로 확인된 `logic`. 사용자는 공지 전용 화면 추가 방향과 UI handoff 작성을 승인했다.
- `completed_roles`: 현재 Logic 담당의 읽기 전용 현황 조사 및 handoff 작성. 후속 화면 구현 완료를 뜻하지 않는다.
- `next_role`: `ui`. 페이지 controller와 API 통합은 이후 `logic` 담당에게 이어진다.
- 역할 판단 근거: 새 화면의 구조·표현·접근성·props/callback은 UI, 검색·페이지 상태·요청 DTO 매핑·mutation 후 이동은 Logic 책임이다.
- 사용자 확인: 직전 제안은 “기존 게시판을 유지하면서 공지 전용 관리 화면을 추가”였고, 사용자가 “진행하되, ui 작업을 위한 handoff 문서 작성해”라고 답했다. 같은 제품 방향을 다시 묻지 않는다.
- 현재 문서 작성 요청의 명확성: `clear`, `can_proceed: true`. 다음 assignment의 구현 준비 상태와 브랜치 계약은 별도로 확인한다.

## 목표 및 현재 상태

### 사용자 목표

일반 게시글을 관리하는 `/cp/boards`를 유지하면서 실제 news 데이터로 공지사항 목록 조회, 신규 등록, 수정, 임시 저장·게시, 삭제를 수행할 전용 관리 화면을 제공한다. 유형과 상단고정은 news API의 실제 필드를 사용하고, API에서 지원하지 않는 노출 기간·메인 노출을 저장할 수 있는 것처럼 표시하지 않는다.

### 현재 코드에서 확인한 사실

| 영역 | 구현 상태 및 근거 |
| --- | --- |
| 전송·DTO·parser | `src/entities/news/api/`에 `/admin/news` 5개 API, Zod 요청·응답 검증 구현 |
| 공개 hook | `src/entities/news/index.ts`가 목록·상세 query와 등록·수정·삭제 mutation을 공개 |
| 캐시 | `src/entities/news/model/news-mutation-options.ts`에서 요청 취소·무효화·삭제 상세 캐시 제거 처리 |
| 기존 수정 경로 | `src/app/router/routes.tsx`의 `/cp/boards/notices/:noticeId/edit` |
| 기존 수정 폼 | `src/pages/cp-board/hook/use-cp-notice-form-controller.tsx`와 `use-cp-notice-form-process.tsx`에서 숫자 ID 상세, 제목·본문, DRAFT/PUBLISHED PATCH 연결 |
| 기존 목록 | `src/pages/cp-board/hook/use-cp-board-list-data.tsx`는 `useCpBoardListQuery` 사용. `/v1/cp/boards`와 `BD-01001` 같은 fixture ID 계약이며 news 목록이 아님 |
| 기존 공지 mock | `src/entities/cp-notice/`는 `/v1/cp/notices`와 `NT-00043` 같은 ID 계약을 별도로 보유 |
| 현재 화면의 한계 | 등록/수정이라는 화면 제목과 달리 신규 생성 controller·전용 등록 라우트가 없음. 유형·상단고정 입력, 삭제 연결도 없음 |
| MSW | `src/mocks/news.handlers.ts`의 `createNewsHandlers`는 테스트에서 사용. `src/mocks/handlers.ts`에는 등록되지 않음 |
| 활성 메뉴 | `CpAdminShell` → `buildCitizenParticipationNavigationItems` → `src/widgets/side-navigation/model/_navigation5.ts`. `_navigation2.ts`의 기존 뉴스 메뉴는 이 셸의 메뉴가 아님 |

### Git 상태 정정

- 실제 조회한 현재 branch는 `task/sign-in-page`, HEAD는 `5834f920fcceadbe79491791d5cf8a35ca7e2a98`이며 작업 폴더는 clean이었다.
- 로컬 `sy-main`도 동일한 HEAD다. 공지 구현 커밋 `79d31f8bf5e5cb0d72e609e76c14b1fd069b198e`는 두 브랜치 모두에 포함되어 있다.
- `git config --get-regexp`로 조회한 `task/connect-news-api`와 `task/sign-in-page`의 V3 상태는 모두 `CLOSED`다. 이전 공지 handoff의 ACTIVE·미병합 표기와 이 세션 시작 시 주입된 PRESERVED 표기는 현재 조회 결과와 다르다.
- 현재 `assignment.json`의 task 값은 빈 문자열이다. 이번 문서 작성으로 뉴스 작업의 branch 권한을 획득했다고 해석하지 않는다.
- UI 후속 작업은 최신 `sy-main`을 기준으로 새 V3 계약을 준비한다. CLOSED 브랜치를 resume하거나 예전 scope를 그대로 사용하지 않는다.

## 완료된 작업

1. 현재 news API·DTO·query/mutation, 기존 폼·라우트·목록·메뉴와 MSW 연결을 읽었다.
2. 사용자가 승인한 전용 화면 추가 방향을 확인하고 UI와 Logic의 후속 책임을 정리했다.
3. 현재 Git 포함 관계와 CLOSED 상태를 확인하여 오래된 인계 기록을 보완했다.
4. 중앙 Codex handoff 템플릿을 사용하여 현재 assignment의 이 문서만 작성했다.

## 대기 중인 작업

아래 URL과 새 파일 경로는 구현을 구체화하기 위한 제안이다. 현재 존재하는 경로나 승인된 V3 scope가 아니다.

| 순서 | 위치·담당 | 수행 방법·목적·기대 결과 |
| --- | --- | --- |
| 1 | 새 UI 세션 / `src/pages/cp-news/ui/`, `model/` 제안 | 기존 공용 UI로 목록·등록·수정 View와 props/callback 계약을 작성하여 실제 데이터 연결을 위한 표현 계층 제공 |
| 2 | Logic 후속 / `src/pages/cp-news/hook/`, `lib/` 제안 | 공개 news hook을 조합해 검색·페이지·폼 상태, 검증, 성공·실패·이동 처리 구현 |
| 3 | UI 후속 / `src/app/router/routes.tsx`, `_navigation5.ts` | 준비된 페이지를 전용 라우트와 공지사항 메뉴에 연결하여 목록에서 등록·수정으로 접근 가능하게 함 |
| 4 | Logic·UI 순차 협의 / 기존 `src/pages/cp-board` 공지 폼 | 기존 숫자 ID 수정 URL의 동작을 보존하고, 전용 화면과 기존 진입점의 중복·복귀 경로를 확인 |
| 5 | 각 변경 담당 / 기존 `tests/`와 검증 명령 | 요청 매핑·등록·수정·삭제·오류·이동 동작을 검증하고 UI 결과와 Logic 통합 결과를 구분하여 기록 |

### 화면 제안

- 전용 목록: `/cp/news`. 제목, 유형, 게시 상태, 상단고정, 조회수, 등록일을 표시하고 등록·수정 진입을 제공한다.
- 신규 등록: `/cp/news/new`. 제목·본문·유형·상단고정을 입력하고 임시 저장 또는 게시로 생성한다.
- 수정: `/cp/news/:newsId/edit`. 상세를 불러와 편집하며 저장·게시와 삭제 확인을 제공한다.
- 기존 `/cp/boards`와 일반 게시글 상세·처리 기능은 유지한다. 기존 mock ID를 실제 news ID로 변환하거나 서로 같은 레코드라고 가정하지 않는다.
- 기존 `/cp/boards/notices/:noticeId/edit`의 제거·redirect는 아직 구현하지 않았다. 새 화면과 합칠 경우 실제 숫자 ID의 호환과 `noticeId`/`newsId` 파라미터 이름 차이를 함께 처리한다.
- 유형·상태 필터, 제목 또는 제목+본문 검색, 페이지 이동을 제공한다. 정렬 UI를 제공한다면 API의 `sort`로 처리한다.
- 작성자 검색, 노출 기간, 메인 노출은 news 요청 계약에 없다. 기존 폼의 관련 입력·설명·확인 팝업·미리보기를 그대로 복사하지 않는다.
- `ARCHIVED` 상세도 상태를 정확히 표시한다. 기존 폼은 임시 저장·게시 동작만 연결되어 있으므로 보관 동작이 이미 구현된 것으로 취급하지 않는다.

## 결정 사항 및 제약 조건

### 사용할 API와 공개 hook — 현재 구현됨

타입과 hook은 `~/entities/news`에서 가져올 수 있다. 전송 함수는 UI View에서 직접 호출하지 않고 Logic controller가 아래 hook을 조합한다.

| 기능 | HTTP | hook·입력 |
| --- | --- | --- |
| 목록 | `GET /admin/news` | `useNewsListQuery(params: GetNewsListQueryDto)` |
| 상세 | `GET /admin/news/:newsId` | `useNewsDetailQuery(newsId: string \| number)` |
| 등록 | `POST /admin/news` | `useCreateNewsMutation().mutate({ payload })` |
| 수정 | `PATCH /admin/news/:newsId` | `useUpdateNewsMutation().mutate({ newsId, payload })` |
| 삭제 | `DELETE /admin/news/:newsId` | `useDeleteNewsMutation().mutate({ newsId })` |

등록 payload는 `title`, `content`, `type`, `status`, `isPinned`가 모두 필수다. PATCH는 이 다섯 필드가 모두 선택이며, `isPinned: false`는 의미 있는 변경이다. 미입력 필드를 임의 기본값으로 덮어쓰지 않는다. 현재 기존 폼은 제목·본문·상태만 PATCH하므로 기존 유형·상단고정을 보존한다.

- `type`: `ANNOUNCEMENT`, `EVENT`, `UPDATE`, `ETC`.
- `status`: `DRAFT`, `PUBLISHED`, `ARCHIVED`.
- `isPinned`: 상단고정 boolean. 메인 노출과 같은 필드가 아니다.
- 제목·본문은 공백만 있는 값을 허용하지 않는다. 현재 폼 매핑은 두 값을 trim하여 저장한다.
- mutation의 성공 data는 `void`다. 서버의 `null`/공용 API 계층의 `undefined`를 수용하며, 신규 ID나 저장된 상세 객체를 반환하지 않는다. 등록 성공 후 응답 ID를 가정한 상세 이동을 만들지 말고 목록으로 돌아가 갱신된 데이터를 확인한다.
- 수정 성공 시 목록과 해당 상세를 무효화한다. 삭제 성공 시 해당 상세 캐시를 제거하고 목록을 무효화한다. 페이지에서 같은 캐시 동작을 중복 구현하지 않는다.

### 목록·상세 계약의 주의점

- 목록 query: 선택 `type`, `status`, `by`, `keyword`, `sort`; `page` 기본 1, `size` 기본 20.
- `by`는 `TITLE` 또는 `TITLE_CONTENT`이고 `keyword`와 함께 입력하거나 함께 생략해야 한다. 빈 검색을 초기화할 때 한쪽만 남기지 않는다.
- `sort`는 문자열 배열이며 예시는 `["createdAt,desc", "id,desc"]`다. 전송 계층이 반복 query parameter를 처리한다. UI가 별도 직렬화를 구현하지 않는다.
- 목록 응답은 `items`, `totalElements`, `totalPages`, `pinnedItemCount`다. 순서와 집계는 서버 값을 보존한다. 클라이언트에서 고정 공지를 재정렬하거나 서버 `totalPages`를 다시 계산하지 않는다.
- 고정 항목이 집계·페이지 크기에 포함되는 방식은 현재 확보된 계약으로 확정하지 못했다. MSW fixture의 집계 관례를 서버 규칙으로 단정하지 않는다. 공용 pagination adapter가 필요한 경우 Logic 담당이 서버 값 보존을 확인한다.
- 전체 게시 상태별 KPI나 작성자 정보는 목록 API가 제공하지 않는다. 현재 페이지의 행을 세어 전체 통계로 표시하지 않는다.
- 상세는 숫자 news ID를 사용한다. `NT-*`, `BD-*`, 빈 문자열은 정상 상세 진입 ID가 아니다. query hook의 자동 조회가 비활성화되는 것만으로 화면의 잘못된 주소 처리가 완성되지는 않으므로 controller가 상태를 제공해야 한다.
- 상세 필드: `id`, `type`, `status`, `title`, `content`, `isPinned`, `viewCount`, `createdAt`, `updatedAt`.

### UI → Logic props/callback 계약 초안 — 아직 구현되지 않음

UI 담당은 기존 `CpNoticeFormController`와 인접 페이지의 controller/View 분리를 참고하여 구체적인 타입을 작성하고, Logic 담당에게 실제 파일을 인계한다. 아래 이름은 역할 간 논의를 위한 초안이며 존재하는 export가 아니다.

| 화면 | UI가 받을 데이터·상태 | UI가 전달할 callback |
| --- | --- | --- |
| 목록 | `readonly NewsListItemResponseDto[]`, 서버 집계, 현재 페이지·크기, 필터·검색 입력값, 최초 로딩·재조회·오류 상태 | 필터·검색 입력 변경, 검색 적용·초기화, 페이지 변경, 숫자 ID 수정 열기, 등록 열기, 재시도 |
| 등록·수정 | mode, 상세 표시 정보, 제목·본문·유형·상단고정 입력값, 저장 가능·저장 중·오류 상태 | `onTitleChange(string)`, `onContentChange(string)`, `onTypeChange(NewsType)`, `onPinnedChange(boolean)`, `onSaveDraft()`, `onPublish()`, `onBack()` |
| 삭제 확인 | 삭제 대상의 숫자 ID·제목, 열림·처리 중·오류 상태 | `onRequestDelete()`, `onCancelDelete()`, `onConfirmDelete()` |

- UI는 입력과 상태를 표현하고 callback을 호출한다. API 요청, 요청 payload 매핑, 검증·캐시·페이지 이동은 Logic controller가 담당한다.
- 필터 변경 후 적용 시 첫 페이지로 복귀하는 상태 처리와, 등록·삭제 후 목록 이동을 Logic에 인계한다. 목록의 마지막 항목 삭제 후 유효 페이지 복귀도 확인한다.
- 최초 로딩, 검색 결과 없음, 조회 오류·재시도, 저장·삭제 처리 중, 저장·삭제 실패를 각각 표현한다. 실패를 빈 목록이나 성공으로 표시하지 않는다.
- 처리 중 중복 제출을 막고, 실패 시 입력값을 유지하며, 다른 ID로 이동한 뒤 이전 요청 결과가 새 화면을 덮어쓰지 않도록 한다.
- props 계약 작성은 구현 권한을 다른 역할에 자동 부여하지 않는다. 같은 파일을 수정해야 하면 소유권을 순차적으로 넘긴다.

### 재사용·표현·개발 환경

- 목록 구조는 `src/pages/cp-board/ui/cp-board-list-view.tsx`와 `src/pages/cp-proposal/ui/cp-proposal-list-view.tsx`를 참고한다. cp-board의 DTO·작성자 검색·KPI를 그대로 news에 이식하지 않는다.
- 공용 자산: `src/shared/ui/table/`, `pagination/`, `button/`, `text-input/`, `text-area/`, `choice-chip-group/`, `dialog/`, `loading/`, `section-card/`, `definition-list/`.
- 페이지 레이아웃: `src/widgets/admin-page-layout/`의 `PageHeader`, `FilterBar`, `ActionBar` 등. 기존 셸과 스타일 토큰을 따른다.
- news enum 파일의 label 상수는 `_news_status_*`, `_news_type_*` 문자열이다. 사용자에게 번역 키가 노출되지 않도록 UI 표시 설정에 한국어 label을 둔다.
- news MSW handler는 아직 브라우저 registry에 없다. 개발 화면에서 자동으로 news mock이 작동한다고 보고하지 않는다. 실 API 사용 여부와 개발 MSW 연결은 Logic 담당이 확인하며, registry 수정이 필요하면 해당 파일을 scope·소유권에 포함한다.
- 새로운 테스트 프레임워크·공용 추상화·패키지 추가는 이번 화면 작업의 기본 전제가 아니다.

## 소유권과 Git 계약

- 이번 변경 경로: `.codex/logs/sessions/2026-09-09-logic-3bf3fa3a/handoff.md`만.
- 현재 assignment의 산출물 책임: `owner`. 이번 요청은 인계 문서 작성이며 owner 8종을 갖춘 구현 완료·finish 판정을 수행하지 않는다.
- 현재 task·branch·worktree: assignment task는 빈 값, checkout은 `task/sign-in-page`(CLOSED), worktree는 `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`.
- 기존 Git 통합 담당 기록: `task/connect-news-api`는 `codex`, `task/sign-in-page`는 `claude`. 이 기록을 새 작업의 통합 권한으로 재사용하지 않는다.
- 후속 branch 제안: `task/news-management-ui`, parent·직접 merge target `sy-main`. 이름·scope·worktree·Git 통합 담당자는 다음 세션의 V3 proposal에서 확정한다. 이번 세션에서 proposal이나 branch를 생성하지 않았다.
- 충돌 여부: 확인 시 tracked 변경은 없고, 이번 문서는 현재 assignment 디렉터리에 처음 작성한다. 다른 세션 로그를 수정하지 않는다.

| 역할 | 소유권 제안 | 경계 |
| --- | --- | --- |
| UI | 새 `src/pages/cp-news/ui/` View·스타일, 표시 config·props 타입, 준비 완료 후 라우트·활성 메뉴 연결 | API·업무 검증·페이지 상태·mutation을 View에 구현하지 않음 |
| Logic | 새 페이지 hook·lib, news API/hook 소비, 폼 요청 매핑, 페이지 조합·기능 연결, 필요 시 MSW와 동작 테스트 | UI 담당의 View·스타일을 병행 수정하지 않음 |
| 순차 공유 | props 타입, 페이지 entry·barrel, 기존 공지 수정 진입점 | UI가 계약을 먼저 전달하고 Logic 통합 후 필요한 UI 연결만 수행. 동시 편집 금지 |
| Git 통합 | 다음 V3 계약에서 지정할 assignment 한 개 | 같은 worktree의 branch·index·commit·merge를 단독 관리 |

## 관련 경로와 스킬

현재 정책 snapshot: `/Users/okand/SynologyDrive/asan-agent-policy/build/admin-ui/codex-logic-0c09bf9c0b8f0edc/policy`.

- 이번에 적용한 스킬: `policy-task-role-routing`, `policy-git-branch-strategy`, `policy-documentation`.
- 사용한 템플릿: 위 snapshot의 `.codex/templates/handoff.template.md`.
- UI 후속: 새 세션에 바인딩된 `task-role-routing`과 `references/ui.md`, `references/handoff-and-ownership.md`, `git-branch-strategy`, `coding-convention`, `type-definition`, `implementation-quality`, `documentation`을 범위에 맞게 적용한다.
- Logic 통합 후속: `data-fetch-layer`, `recipe-data-fetch`, `recipe-data-dto`, `validation`과 기존 news query/mutation 구현을 확인한다.
- 구현된 기존 폼 계약: `src/pages/cp-board/model/cp-notice-form.types.ts`.
- 기존 로직 인계 기록: `.codex/logs/sessions/2026-09-08-connect-news-api-adc9f97a/handoff.md`. API 의도·제약의 참고 이력이며 Git·빌드 상태는 아래 최신 근거와 구분한다.

## 명령어 및 결과

### 이번 세션에서 직접 확인

| 명령·작업 | 결과 |
| --- | --- |
| `git status --short --branch` | `task/sign-in-page`, tracked 변경 없음 |
| `git rev-parse HEAD sy-main` | 두 결과 모두 `5834f920fcceadbe79491791d5cf8a35ca7e2a98` |
| `git branch --contains 79d31f8bf5e5cb0d72e609e76c14b1fd069b198e` | `sy-main`, `task/connect-news-api`, `task/sign-in-page`에 포함 |
| `git config --get-regexp '^branch\.(task/connect-news-api\|task/sign-in-page)\.asan-'` | 두 task 모두 V3·CLOSED, 기존 역할·scope·통합 담당 확인 |
| 중앙 assignment의 필요한 필드 읽기 | 현재 host·role·responsibility·산출물 디렉터리 확인 |
| `rg`, `cat`로 코드·정책·인계 기록 읽기 | API·폼·메뉴·MSW 및 템플릿 확인. 없는 `side-navigation/index.ts`와 `table/interface/pagination.ts`는 재사용 근거에서 제외 |

### 이전 세션의 실행 기록 — 이번 세션 재실행 결과가 아님

| 검증 | 기록된 결과·출처 |
| --- | --- |
| 공지 대상 테스트 | 28/28 PASS — `.codex/logs/sessions/2026-09-08-connect-news-api-adc9f97a/implementation-log.md` |
| 당시 전체 테스트 | 134/134 PASS — 같은 공지 구현 로그 |
| 공지 변경 파일 lint | PASS — 같은 공지 구현 로그 |
| 프로젝트 build·타입 검사 | 공지 작업 당시 미실행. 이후 `.claude/logs/sessions/2026-09-09-ui-598b9af7/review-log.md`에 `npm run build` PASS 기록 |
| 전체 lint | 이전 공지·로그인 검증 기록 모두 기존 68 errors / 5 warnings. 새 작업 결과와 별도로 보고할 기준 |

## 실행하지 않은 검증

이번 세션에서는 테스트·lint·build, 개발 서버 실행, 실서버 호출, 브라우저 조작·시각 QA를 실행하지 않았다. 애플리케이션 변경이 없어 새로운 기능 PASS/FAIL 판정은 하지 않는다. Git commit·merge·push·finish·preserve·resume도 수행하지 않았다.

## 다음 조치

1. UI 담당은 새 `--role ui` 세션에서 이 문서와 실제 `sy-main`, 활성 메뉴, 공용 UI를 읽는다. 사용자 승인 방향은 유지하고 현재 assignment의 준비 상태와 새 V3 계약을 확인한다.
2. 제안 경로와 역할별 파일 소유권을 실제 scope로 구체화하고, 공지 전용 목록·폼·삭제 확인 View 및 props/callback 계약을 먼저 구현한다. 이는 전체 기능 연결 완료와 구분하여 인계한다.
3. Logic 담당이 공개 news hook으로 controller를 구현하고 타입·동작을 검증한다. 기존 `noticeId` 경로와 새 `newsId` 경로의 조합, 목록 복귀, 숫자 ID, 빈 검색 쌍, false PATCH, void 생성 응답을 확인한다.
4. 준비된 페이지를 라우트와 메뉴에 연결하고 등록 → 목록 갱신 → 수정·게시 → 삭제의 흐름을 검증한다. 기존 게시판 접근과 동작도 확인한다.
5. 변경 동작에 필요한 기존 Node 테스트와 대상 lint를 실행하고, 승인된 명령으로 build·전체 lint를 수행한다. test script는 현재 없으므로 `node --test tests/news-contract.test.mjs tests/news-form.test.mjs tests/news-msw.test.mjs tests/news-mutation.test.mjs`를 기본 회귀 검증으로 사용한다. 필요 시 새 controller 동작 테스트를 기존 `tests/*.test.mjs` 배치에 추가한다.
6. 새 구현의 실행 결과로 리뷰와 owner 산출물을 작성한다. 시각 캡처는 사용자가 별도로 요청했을 때만 수행하고, 실서버 미확인과 기존 lint 오류를 완료 보고에서 명시한다.

문서 작성의 차단 요인은 없다. 후속 UI 소스 변경의 준비 조건은 올바른 role의 새 assignment, 현재 계약 확인과 새 V3 scope·Git 통합 담당 확정이다. 구현되지 않은 controller와 브라우저 news mock 연결을 준비 완료로 간주하지 않는다.
