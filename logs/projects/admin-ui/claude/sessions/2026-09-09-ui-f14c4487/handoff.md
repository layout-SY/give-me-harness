# 인계

## Assignment 이동

- 보내는 host·session·role: `claude` / `f14c4487b1bc4431a3ac89583753fad6` (native `68eeac38-cdf7-45d3-bbb4-b0446a482bcc`) / `ui`
- 받는 host·session·제안 role: 미지정. 새 `--role logic` 세션이 이 문서를 읽는다.

## 역할 라우팅

- 요청 역할(`requested_roles`): `ui`
- 확인된 역할(`confirmed_roles`): `ui` (inject `--role ui`)
- 완료 역할(`completed_roles`): UI의 View·표기·controller 계약 작성. 라우트·메뉴 연결은 미완료.
- 다음 제안 역할(`next_role`): `logic`
- 역할 판단 근거: 남은 작업은 news hook 조합, 검색·페이지 상태, 요청 DTO 매핑, mutation 후 이동·캐시 처리로 Logic 책임이다.
- 사용자 확인: 계획 보고 후 `진행해`로 구현 승인, branch proposal SHA에 `승인`.

## 목표 및 현재 상태

공지사항 전용 관리 화면 중 UI 표현 계층과 controller 계약을 `src/pages/cp-news`에 신설했다. 8개 파일이 추가되었고 기존 파일은 변경하지 않았다. 화면은 아직 라우트에 연결되어 있지 않아 사용자 접근 경로가 없다. 변경은 `task/news-management-ui`(ACTIVE, 미병합)의 로컬 커밋 `49aa739`에 있으며 작업 폴더는 clean이다. Logic 담당이 이 커밋 위에서 작업을 이어받는다.

## 완료된 작업

1. handoff 2건(`.codex/logs/sessions/2026-09-09-logic-3bf3fa3a`, `2026-09-08-connect-news-api-adc9f97a`)과 news API·DTO·hook, 인접 화면·공용 UI를 읽었다.
2. `task/news-management-ui` V3 계약을 승인받아 생성했다.
3. 목록·폼·삭제 확인 View와 두 controller 계약, 표기 config, barrel을 작성했다.
4. 타입·lint·기존 news 회귀 테스트를 실행했다.
5. owner 산출물 8종을 작성했다.

## 대기 중인 작업

| 순서 | 위치·담당 | 수행 방법·목적·기대 결과 |
| --- | --- | --- |
| 1 | Logic / `src/pages/cp-news/hook/`, `lib/` (신규 제안) | 공개 news hook으로 `CpNewsListController`, `CpNewsFormController`를 구현해 화면에 실제 데이터를 연결 |
| 2 | Logic / 필요 시 `src/mocks` registry | 개발 환경 mock 연결 여부를 결정. registry 수정이 필요하면 scope에 포함 |
| 3 | UI 후속 / `src/app/router/routes.tsx`, `_navigation5.ts` | 준비된 페이지를 `/cp/news`, `/cp/news/new`, `/cp/news/:newsId/edit`와 메뉴에 연결 |
| 4 | Logic·UI 협의 / `src/pages/cp-board` 공지 폼 | 기존 `/cp/boards/notices/:noticeId/edit`의 유지·redirect·제거 방침 확정 |
| 5 | 각 담당 / `tests/` | controller 동작(첫 페이지 복귀, 빈 검색 쌍, false PATCH, void 생성 응답, 마지막 항목 삭제 후 페이지 복귀)을 기존 `tests/*.test.mjs` 배치에 추가 |

## 결정 사항 및 제약 조건

### Logic이 구현할 계약

`~/pages/cp-news`에서 가져온다. View는 아래 인터페이스에만 의존한다.

**`CpNewsListController`**

- `isPending: boolean` — 최초 로딩. true면 `Loading`만 렌더한다.
- `search` — `type`(`NewsType | "ALL"`), `status`(`NewsStatus | "ALL"`), `searchBy`(`"TITLE" | "TITLE_CONTENT"`), `keyword`, 각 `on*Change`, `onSubmit`, `onReset`. 적용 시 첫 페이지 복귀는 controller 책임이다.
- `table` — `rows`(서버 순서 보존), `isFetching`, `page`, `pageSize`, `pageCount`, `itemCount`, `pinnedItemCount`, `onPageChange(page)`, `onOpenEdit(newsId: number)`.
- `error` — `isVisible`, `message`, `isFetching`, `onRetry`. true면 표 대신 오류 영역을 렌더하므로 빈 결과와 구분해 설정해야 한다.
- `onOpenCreate()` — 등록 화면 이동.

**`CpNewsFormController`**

- `mode`: `"create" | "edit"`, `isPending`, `detail`(등록 모드는 `undefined`), `saveErrorMessage`.
- `fields` — `title`, `content`, `type`, `isPinned`, `isSaving`, `canSaveDraft`, `canPublish`, `onTitleChange`, `onContentChange`, `onTypeChange`, `onPinnedChange(boolean)`, `onSaveDraft()`, `onPublish()`.
- `delete` — `isAvailable`(수정 모드에서만 true), `isOpen`, `isDeleting`, `errorMessage`, `onRequestDelete()`, `onCancelDelete()`, `onConfirmDelete()`. `isAvailable && detail`일 때만 팝업이 렌더된다.
- `load` — `isFailed`, `message`, `isFetching`, `onRetry()`. 잘못된 ID 진입도 여기로 표현한다.
- `onBack()` — 목록 복귀.

### 지켜야 할 제약

- `by`와 `keyword`는 함께 전송하거나 함께 생략한다. View의 검색 범위 드롭다운에는 "전체"가 없으므로 빈 키워드일 때 두 값을 모두 생략하는 판단은 controller가 한다.
- 등록 payload는 `title`·`content`·`type`·`status`·`isPinned` 5개가 모두 필수다. 임시 저장은 `DRAFT`, 게시는 `PUBLISHED`.
- PATCH는 전 필드 선택이며 `isPinned: false`는 의미 있는 변경이다. 미입력 필드를 기본값으로 덮어쓰지 않는다.
- mutation 성공 data는 `void`다. 등록 후 새 ID를 가정한 상세 이동을 만들지 말고 목록으로 돌아간다.
- 캐시 무효화·상세 제거는 `news-mutation-options.ts`가 이미 처리한다. 페이지에서 중복 구현하지 않는다.
- 목록 집계·순서는 서버 값을 그대로 넘긴다. View는 재계산하지 않는다.
- 상세 진입 ID는 숫자다. `NT-*`·빈 문자열은 `load.isFailed`로 표현한다.
- 화면 표기는 `cp-news-list.config.ts`의 한국어 상수를 쓴다. entities의 `_news_*` label을 화면에 노출하지 않는다.

### UI 구현 결정

- 상단고정은 `ChoiceChipGroup`(`PINNED`/`NORMAL`)으로 표현하고 View에서 boolean과 변환한다. `ToggleSwitch`는 접근 가능한 이름을 받지 못해 사용하지 않았다.
- `Dropdown`의 index 계약은 View에서 값으로 변환한다. 해제(-1)는 유형·상태에서 "전체", 검색 범위에서는 기존 값 유지다.
- 목록 API가 상태별 전체 집계를 주지 않아 KPI 영역을 두지 않았다.
- 노출 기간·메인 노출·작성자 검색은 넣지 않았다.

## 소유권과 Git 계약

- 변경 경로: `src/pages/cp-news/` 신규 8개 파일, `.claude/logs/sessions/2026-09-09-ui-f14c4487/` 산출물 9개.
- 역할별 파일 소유권: View·config·표기는 UI, 신규 `hook/`·`lib/`는 Logic. `model/*.types.ts`와 `index.ts`는 순차 공유이며 동시 편집하지 않는다. `routes.tsx`·`_navigation5.ts`는 Logic 통합 후 UI가 담당한다.
- 충돌 여부: 시작 시 clean이었고 이번 변경은 이 assignment가 모두 작성했다. 다른 세션 산출물은 수정하지 않았다.
- task·branch·worktree: `task/news-management-ui`(V3, ACTIVE, 미병합) / 시작 HEAD `5834f920fcce` → 현재 HEAD `49aa739` / `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`
- 분기 기준·직접 merge 대상: `sy-main`
- 계약 SHA-256: `0aa18eee3ae6503590c79bfa855822f76df4e5ebac7d6221093038e9d70b9775`
- 승인된 작업 경로: `src/pages/cp-news`. Logic이 다른 경로가 필요하면 scope-proposal로 확장 승인을 받는다.
- Git 통합 담당자: `claude`
- 산출물 책임: owner

## 관련 경로와 스킬

- 정책 snapshot: `/Users/okand/SynologyDrive/asan-agent-policy/build/admin-ui/claude-ui-880948b679e8bfac/policy`
- 적용한 스킬: `task-role-routing`(+`references/ui.md`, `handoff-and-ownership.md`), `git-branch-strategy`, `styles`, `ui-library`, `coding-convention`, `implementation-quality`, `abstraction-strategy`, `documentation`, `portfolio`
- Logic 후속 참고: `data-fetch-layer`, `recipe-data-fetch`, `recipe-data-dto`, `validation`과 `src/entities/news/model/news-mutation-options.ts`
- 이전 인계: `.codex/logs/sessions/2026-09-09-logic-3bf3fa3a/handoff.md`, `.codex/logs/sessions/2026-09-08-connect-news-api-adc9f97a/handoff.md`

## 명령어 및 결과

| 명령 | 결과 |
| --- | --- |
| `git -C <repo> status --short --branch`, `rev-parse HEAD sy-main` | 시작 시 `task/sign-in-page` clean, HEAD와 `sy-main` 모두 `5834f920fcce` |
| `branch_workflow.py proposal` → `create` | `task/news-management-ui` 생성, ACTIVE |
| `npx tsc --noEmit -p tsconfig.app.json` | 신규 경로 오류 0건 / 기존 파일 오류 14건(변경 전부터 존재) |
| `npx eslint src/pages/cp-news --ext .ts,.tsx` | PASS |
| `node --test tests/news-*.test.mjs` | 28/28 PASS |
| `git add -- src/pages/cp-news`, `git diff --cached --check` | exit 0, 신규 8개 파일 591줄 추가 |
| `git commit` | `49aa739` 생성, 이후 `git status` clean |

## 실행하지 않은 검증

`npm run build`, 전체 `npm run lint`, 개발 서버 실행, 실서버 호출, 브라우저 조작·시각 QA. merge·push·finish·close도 수행하지 않았다.

## 다음 조치

1. Logic 담당이 새 `--role logic` 세션에서 이 문서와 `src/pages/cp-news`의 계약 파일을 읽고 현재 branch 계약·준비 조건을 확인한다.
2. controller를 구현하고 빈 검색 쌍, 첫 페이지 복귀, false PATCH, void 생성 응답, 마지막 항목 삭제 후 페이지 복귀를 검증한다.
3. UI가 라우트·메뉴를 연결한 뒤 등록 → 목록 갱신 → 수정·게시 → 삭제 흐름을 통합 확인한다.
4. 기존 공지 진입점 방침을 사용자와 확정한다.
5. 검증 완료 후 owner assignment가 commit·merge 승인을 요청한다.
