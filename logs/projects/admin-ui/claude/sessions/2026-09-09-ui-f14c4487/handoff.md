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

**1~3항은 완료되었다.** 4항은 미결이며, 아래 2차 인계가 현재 대기 중인 작업이다.

---

# 2차 인계 — 기존 타입·lint 오류의 Logic 몫 위임

## Assignment 이동

- 보내는 host·session·role: `claude` / `f14c4487b1bc4431a3ac89583753fad6` / `ui`
- 받는 host·session·제안 role: 미지정. 새 `--role logic` 세션이 이 문서를 읽는다.
- 작성일: 2026-09-09, Asia/Seoul.

## 역할 라우팅

- 요청 역할(`requested_roles`): 기존 타입·lint 오류 정리
- 확인된 역할(`confirmed_roles`): 현재 세션은 `ui`
- 완료 역할(`completed_roles`): 공지 화면 UI, 라우트·메뉴 연결. 오류 정리는 미착수.
- 다음 제안 역할(`next_role`): `logic`
- 역할 판단 근거: 남은 오류의 대부분이 `entities/*/api`의 응답 타입 설계와 `shared/lib`의 데이터·전송 계층이다. `any` 제거는 실제 API 응답 계약을 확정해야 하는 작업이라 UI 역할 밖이다.
- 사용자 확인: "기존 오류 먼저 수정"으로 정리 방침을 승인했고, "타입/lint 관련 문제는 logic에게 위임할 handoff 문서 작성해"로 이 문서를 지시했다.

## 목표 및 현재 상태

공지 화면 작업(`task/news-management-ui`, HEAD `25c3ade`)은 끝났다. 남은 과제는 이 저장소에 **이번 작업과 무관하게 이미 존재하던** 타입 14건과 lint 68 errors / 5 warnings다. 이 오류 때문에 `npm run build`와 `npm run lint`가 실패하고, 그 결과 branch 완료 계약의 `verify` 단계를 통과할 수 없다. 즉 `sy-main` 병합의 실질적 차단 요인이다.

이 오류들은 현재 branch에서 발생한 것이 아니며, 현재 승인 scope(`src/pages/cp-news`, `routes.tsx`, `_navigation5.ts`) 밖이다.

## 완료된 작업

이번 세션에서 오류를 수정하지 않았다. 전체 목록을 조사해 역할별로 분류한 것이 결과물이다.

## 대기 중인 작업 — Logic 몫

`entities/*/api`와 `shared/lib`가 대상이다. 전체 lint 오류의 대부분(약 53건)이 여기 있다.

| 경로 | 오류 | 성격 |
| --- | --- | --- |
| `src/entities/admin-settings/api/admin-settings.api.ts` | `any` | 응답 타입 미정의 |
| `src/entities/dashboard/api/dashboard.api.ts` | `any` 10건 | 응답 타입 미정의 |
| `src/entities/event/api/attendance/attendance.api.ts` | `any` 3건 | 응답 타입 미정의 |
| `src/entities/event/api/roulette/roulette.api.ts` | `any` 3건 | 응답 타입 미정의 |
| `src/entities/faq/api/faq.api.ts` | `any` 2건 | 응답 타입 미정의 |
| `src/entities/items/api/item-category.api.ts`, `items.api.ts` | `any` 6건 | 응답 타입 미정의 |
| `src/entities/maintenance/api/maintenance.api.ts` | `any` | 응답 타입 미정의 |
| `src/entities/maps/api/map.api.ts` | `any` | 응답 타입 미정의 |
| `src/entities/profile/api/profile.api.ts` | `any` 2건 | 응답 타입 미정의 |
| `src/entities/sales/api/sales.api.ts` | `any` 3건 | 응답 타입 미정의 |
| `src/entities/users/api/users.api.ts` | `any` 3건 | 응답 타입 미정의 |
| `src/entities/event/api/attendance/attendance.dto.ts` | `const enum` 3건(TS1294), 빈 인터페이스 1건 | `erasableSyntaxOnly` 위반 |
| `src/entities/event/api/roulette/roulette.dto.ts` | `const enum` 2건(TS1294), 빈 인터페이스 1건 | 동일 |
| `src/entities/items/api/items.dto.ts` | 빈 인터페이스 2건 | 타입 설계 |
| `src/entities/dao/model/table-rows.ts` | 미사용 import 2건(TS6196) | 단순 정리 |
| `src/shared/lib/pub-sub/events.ts` | `Function` 타입 5건 | 이벤트 signature 설계 |
| `src/shared/lib/utils/performance.util.ts` | `any` 2건 | 유틸 제네릭 |
| `src/shared/lib/utils/token.util.ts` | `any` 2건 | 토큰 payload 타입 |
| `src/shared/lib/hooks/use-api.tsx` | ref cleanup warning | effect 정리 |

## UI 몫 — 이 세션 또는 다음 UI 세션이 담당

Logic이 건드리지 않는다. 소유권 충돌을 막기 위해 명시한다.

| 경로 | 오류 |
| --- | --- |
| `src/features/select-users/ui/select-users.tsx` | 미사용 선언 3건, `const enum` 2건, `any` 2건 |
| `src/shared/ui/dialog/dialog.store.ts` | `const enum` 1건 |
| `src/shared/ui/dialog/dialog.tsx` | hook 의존성 warning |
| `src/shared/ui/image-modal/image-modal.tsx` | `no-unused-expressions` 1건, warning 1건 |
| `src/shared/ui/image-upload/image-upload.tsx` | warning 1건 |
| `src/shared/ui/no-results/no-results.tsx` | 미사용 `children` |
| `src/shared/ui/reason-prompt/reason-prompt-host.tsx` | 미사용 `useEffect` |
| `src/shared/ui/search-state-bar/searchStateBar.tsx` | 미사용 `_` |
| `src/shared/ui/table/utils/commonCell.tsx` | 미사용 `_` |
| `src/shared/ui/table/hooks/useFetchAdapter.ts` | 렌더 중 ref 접근 2건 |
| `src/shared/ui/text-area/text-area.tsx` | 빈 인터페이스 |
| `src/shared/ui/text-input/text-input.tsx` | effect 내 동기 setState |

## 결정 사항 및 제약 조건

- **`any`를 추측으로 좁히지 않는다.** 실제 서버 응답을 확인할 수 없는 API는 그대로 두고 근거를 기록하는 편이, 잘못된 타입으로 런타임 오류를 만드는 것보다 낫다. 어떤 파일을 미해결로 남겼는지 반드시 보고한다.
- `const enum`은 `erasableSyntaxOnly` 위반이다. 이 저장소의 관행은 `src/entities/news/model/news.enum.ts`의 `as const` 객체 + 동명 타입 패턴이다. 같은 방식으로 바꾸면 소비처의 `FILTER_TYPES.BY` 같은 접근 형태를 유지할 수 있다.
- 빈 인터페이스는 `interface A extends B {}` 형태다. 확장 의도가 없으면 `type A = B`로 바꾼다.
- `shared/lib/pub-sub/events.ts`의 `Function`은 선언 병합 기반 구조라 이벤트별 signature를 확인하고 바꿔야 한다. 이 파일은 여러 화면이 구독하므로 영향 범위가 넓다.
- 검증을 약화해 통과시키지 않는다. eslint disable 주석, 규칙 완화, 테스트 삭제로 오류를 없애지 않는다.
- 관련 없는 리팩터링·포맷 정리를 함께 넣지 않는다.

## 소유권과 Git 계약

- 이번 세션의 변경 경로: `src/pages/cp-news`, `src/app/router/routes.tsx`, `src/widgets/side-navigation/model/_navigation5.ts`, 그리고 이 세션 산출물. 오류 정리 대상 파일은 **하나도 건드리지 않았다.**
- 현재 branch: `task/news-management-ui`, HEAD `25c3ade`, ACTIVE·미병합, 작업 폴더 clean
- 승인 scope: `src/app/router/routes.tsx`, `src/pages/cp-news`, `src/widgets/side-navigation/model/_navigation5.ts`
- Git 통합 담당자: `claude`
- 산출물 책임: owner
- **오류 정리는 이 branch에서 하지 않는다.** 공지 기능과 무관한 변경이 공지 diff에 섞이고 scope도 다르다. `sy-main` 기준의 새 V3 task를 proposal·승인 절차로 만들어 진행한다.
- 병합 순서 제안: 오류 정리 branch를 먼저 `sy-main`에 병합한 뒤, `task/news-management-ui`를 최신 `sy-main` 위에서 병합한다. 이 시점에는 ff-only가 성립하지 않으므로 merge-commit 계약을 별도 승인받는다.

## 관련 경로와 스킬

- 정책 snapshot: `/Users/okand/SynologyDrive/asan-agent-policy/build/admin-ui/claude-ui-880948b679e8bfac/policy`
- Logic 후속 참고 스킬: `task-role-routing`(+`references/logic.md`), `git-branch-strategy`, `type-definition`, `validation`, `coding-convention`, `implementation-quality`, `documentation`
- 기존 enum 관행: `src/entities/news/model/news.enum.ts`
- 기존 DTO·parser 관행: `src/entities/news/api/news.dto.ts`, `news.parser.ts`

## 명령어 및 결과

| 명령 | 결과 |
| --- | --- |
| `npx tsc --noEmit -p tsconfig.app.json` | 기존 파일 14건 오류. 이번 변경 파일 0건 |
| `npx eslint .` | 73 problems (68 errors, 5 warnings) |
| `npx eslint` (변경 3개 경로) | PASS |
| `node --test tests/news-*.test.mjs` (6개) | 46/46 PASS |
| `git commit` | `25c3ade` 생성, 이후 `git status` clean |

오류 내역 집계: `no-explicit-any` 45건, `no-unused-vars` 9건, `exhaustive-deps` 4건(warning), 렌더 중 ref 접근 2건, effect 내 setState 1건, `no-unused-expressions` 1건, 빈 인터페이스·`no-empty-object-type` 4건.

## 실행하지 않은 검증

`npm run build`(기존 타입 오류로 실패), 전체 `npm run lint`의 통과, 개발 서버 실행, 실서버 호출, 브라우저 조작·시각 QA. 오류 정리 작업 자체를 착수하지 않았다.

## 다음 조치

1. Logic 담당이 새 `--role logic` 세션에서 `sy-main` 기준 새 V3 branch를 proposal·승인받는다. 현재 news branch를 재사용하지 않는다.
2. 위 Logic 몫 표의 파일을 정리한다. `any`는 실제 응답 계약을 확인할 수 있는 것만 좁히고, 나머지는 근거와 함께 남긴다.
3. `npx tsc --noEmit`과 `npx eslint`로 잔여 건수를 보고한다. 어떤 항목이 왜 남았는지 명시한다.
4. UI 몫 12개 파일은 UI 세션이 별도로 담당한다. `shared/ui/text-input`과 `table/hooks/useFetchAdapter`는 동작 변경을 동반하고 거의 모든 관리 화면이 사용하므로, 회귀 확인 방법을 먼저 정한 뒤 손댄다.
5. 양쪽 정리가 끝나면 `sy-main` 병합과 news branch 병합 순서를 사용자와 확정한다.
