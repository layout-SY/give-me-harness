# 탐색

## 요청

"현재 news 관련 공지사항 페이지에 ui 작업이 필요해. handoff 문서 확인한 후에 작업 진행해"

## 조사 대상 경로

- `.codex/logs/sessions/2026-09-09-logic-3bf3fa3a/handoff.md`, `.codex/logs/sessions/2026-09-08-connect-news-api-adc9f97a/handoff.md`
- `src/entities/news/**`
- `src/pages/cp-board/**`, `src/pages/cp-proposal/ui/**`
- `src/shared/ui/**`, `src/widgets/admin-page-layout/**`, `src/widgets/side-navigation/model/_navigation5.ts`
- `src/app/router/routes.tsx`, `src/shared/assets/css/_cp-admin.css`

## 현재 코드와 인접 구현의 사실

| 영역 | 확인한 사실 |
| --- | --- |
| API·hook | `src/entities/news`가 목록·상세 query와 등록·수정·삭제 mutation, Zod 검증을 공개한다. 화면은 없다. |
| 등록 payload | `title`, `content`, `type`, `status`, `isPinned` 5개 필수. PATCH는 전부 선택이고 `isPinned: false`는 의미 있는 변경이다. |
| 목록 응답 | `items`, `totalElements`, `totalPages`, `pinnedItemCount`. 순서·집계는 서버 값이다. |
| 검색 계약 | `by`와 `keyword`는 함께 입력하거나 함께 생략해야 한다. |
| label | `NEWS_STATUS_LABELS`, `NEWS_TYPE_LABELS`는 `_news_*` 번역 키라서 화면에 그대로 노출하면 안 된다. |
| 기존 공지 폼 | `/cp/boards/notices/:noticeId/edit`의 `CpNoticeFormPage`. 노출 기간·메인 노출·미리보기 등 news 계약에 없는 입력을 포함한다. |
| 기존 목록 | `cp-board-list-view.tsx`가 `PageHeader` + `KpiStrip` + `FilterBar` + `MasterDetailLayout` 조합을 사용한다. |
| 표 | `Table`은 `columns`/`rows`/`page`/`pageCount`/`pageSize`/`itemCount`/`handler`를 받고 빈 목록에 `NoResults`를 렌더한다. |
| 상태 색 | `StatusBadgeColor`는 `positive · neutral · warning · danger · info · deleted`다. `CategoryBadgeColor`와 값 집합이 다르다. |
| 스타일 | `_cp-admin.css`에 `cp-page`, `cp-grid-2`, `cp-caption`, `cp-field-label`, `cp-popup*`, `cp-col-*` 토큰이 있다. |
| 브랜치 | `task/sign-in-page`(CLOSED)에서 시작했고 `sy-main`과 HEAD가 같았다. 새 V3 계약이 필요했다. |

## 불러온 스킬

`task-role-routing`(+`references/ui.md`, `handoff-and-ownership.md`), `git-branch-strategy`, `styles`, `ui-library`, `coding-convention`, `implementation-quality`, `abstraction-strategy`, `documentation`.

## 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| `widgets/admin-page-layout`의 `PageHeader`·`FilterBar`·`ActionBar` | 사용 | 인접 관리 화면과 동일한 셸·간격을 유지한다 |
| `shared/ui/table` | 사용 | 페이지네이션·빈 결과·컬럼 정의 계약을 이미 제공한다 |
| `shared/ui/dropdown` | 사용 | 유형·상태·검색 범위 선택의 기존 관행 |
| `shared/ui/text-input`, `text-area` | 사용 | 제목·본문 입력과 clear 동작 |
| `shared/ui/choice-chip-group` | 사용 | 유형 선택과 상단고정 표현. `ariaLabel` 지원 |
| `shared/ui/popup`, `section-card`, `definition-list`, `button`, `loading` | 사용 | 삭제 확인 팝업과 기본 정보 표기 |
| `_cp-admin.css` 토큰 | 사용 | 새 CSS 파일 없이 기존 레이아웃 토큰으로 구성 |
| `shared/ui/toggle-switch` | 미사용 | 접근 가능한 이름을 받을 수 없고 shared 수정은 이번 scope 밖이다 |
| `shared/ui/search-state-bar` | 미사용 | 상태 탭 형식이라 유형·상태·검색 범위 3필터 구성과 맞지 않는다 |
| `widgets/admin-page-layout`의 `KpiStrip` | 미사용 | 목록 API가 상태별 전체 집계를 제공하지 않아 현재 페이지 행으로 KPI를 만들 수 없다 |
| `widgets/admin-page-layout`의 `MasterDetailLayout` | 미사용 | 공지는 상세 패널이 아니라 전체 폼 화면으로 수정한다 |
| `features/cp-notice-publish`의 팝업 | 미사용 | 노출 기간·메인 노출 등 news 계약에 없는 정보를 요구한다 |
| `pages/cp-board`의 폼·목록 계약 | 미사용 | mock DTO·작성자 검색·KPI 기반이라 news DTO와 다르다 |

## 재사용하지 않은 후보와 이유

기존 `CpNoticeFormView`는 노출 기간·메인 노출·Mobile 미리보기를 포함하고 상태를 읽기 전용 칩으로만 표시한다. news 계약에는 해당 필드가 없고 유형·상단고정이 추가로 필요해 그대로 복사하지 않았다.

## 새 자산 필요 여부와 근거

`src/shared/ui/`로 승격할 새 공용 요소는 만들지 않았다. 삭제 확인 팝업은 news 전용 문구·필드를 갖고 현재 사용처가 하나뿐이라 페이지 로컬 컴포넌트로 두었다.

## 성능·의존성 영향

새 패키지·아이콘·CSS 파일을 추가하지 않았다. 기존 컴포넌트 조합만 사용해 번들 영향은 신규 화면 코드 크기에 한정된다.

## 제약 조건 및 미확인 사항

- 고정 항목이 서버 집계·페이지 크기에 포함되는 방식은 계약으로 확정되지 않았다.
- news MSW handler는 브라우저 registry에 등록되어 있지 않아 개발 화면에서 mock이 자동 동작하지 않는다.
- controller가 없어 화면을 실제로 렌더해 확인하지 못했다.

## 결론

전용 목록·폼·삭제 확인 View를 `src/pages/cp-news`에 신설하고 표현·계약만 담당한다. 라우트·메뉴 연결은 Logic controller 완료 후 별도 승인으로 수행한다.
