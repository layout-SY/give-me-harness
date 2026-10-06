# 문의 관리 Logic → UI 인계

## 결론

**Logic 구현 및 검증 완료.** 기존 변경 6개와 확정 요구사항을 보존하고 문의 목록·상세·유형 관리 controller 3종, 공개 타입과 config를 구현했다. 문의 관련 테스트 71개, 자동 포맷, lint, build를 통과했다. 다음 ui 세션이 같은 작업 공간에서 view/page·라우트·메뉴를 연결한다.

## 역할·승인 및 작업 위치

- requested_roles: logic
- confirmed_roles: logic (inject role 및 사용자 명시 요청)
- completed_roles: logic
- next_role: ui
- 보내는 host·session: Codex · `inquiry-controller-completion`, contributor.
- 역할 근거: UI handoff가 확정한 props/callback에 맞춰 UI 없는 controller를 작성했다(`controller -> UI`). JSX·CSS·view는 만들지 않았다.
- 구현 승인: 사용자의 “기존 변경 6개와 확정 요구사항을 보존하고, 기존 계획대로 … 구현해줘”, 테스트·포맷·lint·build·handoff 요청.
- project·저장소: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`.
- 실제 worktree·실행 디렉터리: `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/inquiry-ui`.
- branch: `feature/inquiry-ui`.
- HEAD·인계 기준 commit: `4b0b7db45aa9d15bf918a1a084370594e138a124`.
- 직접 부모: `sy-main`(원본 UI 인계의 relation create 완료 기록).
- 기준 시점: 2026-09-28, 최종 검증 후. cwd와 writable root에 inquiry-ui가 포함됨을 확인했다.
- Git 상태: staged 없음, 새 commit 없음. stage·commit·merge 미승인. 이번에 승인·실행한 작업은 아래 쓰기 예약 복구 1건뿐이다.

## 확정 요구와 구현

| 항목 | 구현 계약 |
| --- | --- |
| 목록·유형 표 | 각각 size 10, 1부터 시작하는 페이지 |
| 목록 유형 필터 | `useAllInquiryTypesQuery(10)`으로 모든 페이지 조회. label=name, value=유형 id. 순서가 바뀌어도 선택 ID 유지 |
| 검색 | 초안과 적용 요청 분리. 제출·초기화는 1페이지. 빈 검색어는 by·keyword 생략, 대상 미선택이면 TITLE. sort 미전송 |
| 상태 | OPEN 접수, IN_PROGRESS 처리중, COMPLETED 완료. 완료 동작만 COMPLETED PATCH |
| 답변 | 응답의 `answerContent.comment`를 초안으로 사용. 요청은 `{content}`. 답변 없음 POST, 저장된 답변 PUT. 등록 후 상태 PATCH 없음 |
| 답변 편집 | 공백 제외 1자 이상·변경 있음·비진행 중일 때 저장. 실패·재조회 시 초안 유지. 편집 취소 시 저장값 복원 |
| 문의 삭제 | 확인 후 DELETE, 성공 시 목록으로 replace 이동 |
| 유형 | 등록은 enum code 선택 + trim한 name, 수정은 name만 PUT. 코드 선택은 controller에서도 잠금 |
| 유형 삭제 | 확인 후 DELETE, 사용 중 유형의 삭제 허용은 서버 판단. 실패 시 서버 메시지·선택·초안 보존 |
| 오류 | 서버 오류는 기존 전역 QueryCache/MutationCache → 오류 다이얼로그 경로에 위임해 중복 표시하지 않음. 목록의 전송·계약 오류는 문자열 alert, 상세 조회 오류는 load.message |
| 요청 수명 | 확인 대기부터 동기 lock 적용, 동일 tick 중복 mutation 차단. unmount/상세 ID 전환 시 signal 취소 및 늦은 후속 처리 차단 |

완료 후 답변 제한·되돌리기 정책은 추가하지 않았다. 이름이나 코드의 중복 허용 같은 새 업무 정책도 추가하지 않았다.

## 실제 변경과 보존

기존 unstaged 6개를 보존했고 이번 세션에서 자동 포맷까지 마쳤다. 테스트 파일의 공백·줄바꿈 외에는 시작 시 기존 변경 내용을 유지한다.

1. `src/entities/inquiries/model/inquiry.enum.ts`: 미사용 i18n 라벨 2종 제거 유지.
2. `src/entities/inquiries/index.ts`: `INQUIRY_TYPE_CODES`, `useAllInquiryTypesQuery` 공개 유지.
3. `src/entities/inquiries/model/query-keys.ts`: 전체 유형 조회 key 유지.
4. `src/entities/inquiries/model/inquiry-type-query-options.ts`: 기존 API/parser를 이용한 전체 페이지 조회 유지.
5. `src/entities/inquiries/hook/use-inquiry-type-list-query.ts`: 전체 조회 hook 유지.
6. `tests/inquiry-types-query-mutation.test.mjs`: 전체 유형 조회·부분 실패·빈 결과·페이지 오류·취소 테스트 유지.

이번에 추가한 untracked 파일은 다음 9개다.

- `src/pages/inquiry/model/inquiry-list.types.ts`
- `src/pages/inquiry/model/inquiry-detail.types.ts`
- `src/pages/inquiry/model/inquiry.config.ts`
- `src/pages/inquiry/hook/use-inquiry-list-controller.tsx`
- `src/pages/inquiry/hook/use-inquiry-detail-controller.tsx`
- `src/pages/inquiry-type/model/inquiry-type.types.ts`
- `src/pages/inquiry-type/model/inquiry-type.config.ts`
- `src/pages/inquiry-type/hook/use-inquiry-type-controller.tsx`
- `tests/inquiry-controllers.test.mjs`

자기 산출물은 `.codex/logs/sessions/inquiry-controller-completion/{plan.md,handoff.md}`다. 원본 `.codex/logs/sessions/inquiry-controllers/`와 `.claude/logs/sessions/inquiry-ui/`는 수정하지 않았다. 기본 checkout과 형제 worktree의 변경도 건드리지 않았다.

재사용 근거는 `src/entities/inquiries/` DTO/parser·조회/mutation·캐시 무효화, `src/shared/api/common/response.dto.ts`, `src/shared/ui/dialog/`, `src/app/providers/query-client.ts`다. item·item-category controller의 상태/선택 방식과 cp-news·events 테스트를 참고했다. 전송·parser·Query 상태는 controller에서 중복 구현하지 않았다.

## UI 인계 대상 작업 공간

- 공간 이름: `inquiry-ui`(기존 공간).
- 사용할 역할: `ui`.
- 수행 작업: 목록·상세·유형 관리 view/page 연결, 라우트와 사이드 메뉴 등록.
- 목적지 project·branch·worktree·HEAD·직접 부모는 위 보내는 위치와 동일하다.
- 같은 기능을 Logic → UI 순차로 연결하므로 한 공간을 공유한다. 새 branch/worktree는 필요 없다.
- 진입 시 `git status --short`, `git branch --show-current`, `git rev-parse HEAD`로 위 상태와 비교한다. Logic 파일과 테스트는 아직 미커밋이므로 보존한다.
- 이번 Logic 소스 수정·검증은 종료했다. 이후 소스와 Git 작업은 순차 진행한다. UI가 공개 계약을 바꿔야 하면 차이와 영향을 사용자에게 보고한다.

## UI 상세 작업과 연결 계약

### 공통

- 원본 계약: `.claude/logs/sessions/inquiry-ui/handoff.md`.
- 공개 타입은 각 `model/*.types.ts`에서 named type으로 import한다. 전부 type alias이며 기존 필드명·인자·nullable 계약을 유지했다.
- controller는 기존 App의 QueryClientProvider, Router, 전역 오류·확인 다이얼로그 안에서 사용한다. page는 hook 결과를 view의 `controller` prop으로 전달한다.
- controller에 요청·로딩·검색·mutation 상태가 있으므로 view/page에 별도 API 호출이나 동일 상태를 만들지 않는다.
- config 파일은 이미 존재한다. UI가 필요한 표시 설정은 기존 파일을 확장하고 중복 파일을 만들지 않는다.
- 재사용 UI 후보는 원본 인계의 PageHeader, KpiStrip, FilterBar, MasterDetailLayout, ActionBar, SectionCard, Table, Dropdown, TextInput, TextArea, Button, Loading, DefinitionList다. 실제 UI 선정은 ui 세션에서 해당 스킬에 따라 확인한다.

### 문의 목록

- hook: `src/pages/inquiry/hook/use-inquiry-list-controller.tsx`의 `useInquiryListController()`.
- 타입: `InquiryListController`, `InquiryListRow`, `InquirySelectOption<T>` 및 search/table/retry 하위 타입.
- UI 대상: `src/pages/inquiry/ui/inquiry-list-page.tsx`, `inquiry-list-view.tsx`, 필요한 CSS와 page export.
- `search`를 필터 입력·제출·초기화에 연결한다. status/type 인덱스 -1은 전체, searchBy 인덱스 -1은 미선택이다. keyword는 사용자가 편집한 원문이며 요청할 때만 trim한다.
- `isPending`에는 유형 필터의 초기 조회도 포함한다. `retry`는 목록 또는 유형 조회 실패를 표시하고 두 조회를 다시 실행한다.
- `table`의 rows/page/pageCount/pageSize/itemCount와 callback을 공용 Table에 전달한다. row click은 상세, `onOpenTypes`는 유형 관리로 이동한다.
- config: `INQUIRY_ROUTES`, `INQUIRY_PAGE_SIZE`, `INQUIRY_STATUS_OPTIONS`, `INQUIRY_SEARCH_BY_OPTIONS`.

### 문의 상세

- hook: `src/pages/inquiry/hook/use-inquiry-detail-controller.tsx`의 `useInquiryDetailController()`.
- 타입: `InquiryDetailController`, `InquiryDetailLoadController`, `InquiryAnswerController`, `InquiryCompleteController`.
- UI 대상: `src/pages/inquiry/ui/inquiry-detail-page.tsx`, `inquiry-detail-view.tsx`.
- hook은 route param `inquiryId`를 읽는다. 기존 cp-news 방식처럼 ID별 keyed container로 편집 수명을 구분할 수 있다. hook 자체도 ID 변경 시 초안·확인 상태를 초기화하고 이전 요청을 취소한다.
- `isPending`, `load.isFailed/message/isFetching/onRetry`로 로딩·실패를 표시하고 `detail`로 질문·작성자·유형·날짜·상태를 표시한다.
- `answer.saved === null`은 등록 모드다. 저장된 답변은 `saved.comment`, 편집 입력은 `draft`를 사용한다. `isEditing`, `isSaving`, `isDeleting`, `canSave`에 따라 수정/취소/저장/삭제 버튼을 연결한다.
- `complete.isCompleted/isSaving/canComplete/onComplete`, controller의 `isDeleting/onDelete/onBack`을 연결한다. 확인 다이얼로그를 UI에서 중복 실행하지 않는다.

### 문의 유형 관리

- hook: `src/pages/inquiry-type/hook/use-inquiry-type-controller.tsx`의 `useInquiryTypeController()`.
- 타입: `InquiryTypeController`, `InquiryTypeTableController`, `InquiryTypeFormController`.
- UI 대상: `src/pages/inquiry-type/ui/inquiry-type-page.tsx`, `inquiry-type-view.tsx`, `inquiry-type-form-panel.tsx` 및 page export.
- `table.onRowClick`으로 수정 대상을 선택한다. 페이지 전환·`form.onStartCreate`는 선택과 초안을 초기화한다. 삭제로 마지막 페이지가 없어지면 유효한 마지막 페이지를 조회한다.
- `form.target === null`은 등록, 그 외는 name 수정이다. 수정 모드에서 코드 선택을 잠근다. 서버의 기존 code가 enum 외 값이면 `codeIndex`는 -1이지만 `target.code`는 보존하며 name 수정은 허용한다.
- 저장·삭제·재시도·목록 복귀를 각 callback에 연결한다. 실패 시 초안과 선택을 유지한다.
- config: `INQUIRY_TYPE_PAGE_SIZE = 10`, `INQUIRY_TYPE_CODE_OPTIONS`(label과 value 모두 enum 원문).

### 라우트·메뉴와 완료 기준

- `src/app/router/routes.tsx`에 `/manage/operations/inquiries`, `/manage/operations/inquiries/types`, `/manage/operations/inquiries/:inquiryId`를 연결한다.
- `src/widgets/side-navigation/lib/build-navigation-items.ts`의 운영관리 메뉴에 “1:1 문의”를 추가한다.
- UI 연결 후 해당 worktree에서 중앙 포맷, 아래 문의 테스트, lint, build를 실행하고 ui 세션의 handoff를 남긴다. 타입·config·hook은 중복 생성하지 않는다.
- 이후 사용자 승인 범위에서 stage·commit, `feature/inquiry-ui` → 직접 부모 `sy-main` 통합을 진행한다. 형제 `feature/citizen-proposal-vote-api`와 기본 checkout의 최신 라우트·메뉴 변경은 통합 시 비교해야 한다. 이번 작업에서는 병합 위험 판정이나 Git 통합을 수행하지 않았다.

## 검증 결과와 한계

- 중앙 `formatting.py apply`: 기존 6개 + 신규 9개 코드/테스트 파일에 실제 Prettier 적용 완료.
- `node --test --test-concurrency=2 tests/inquiries-contract.test.mjs tests/inquiries-msw.test.mjs tests/inquiries-mutation.test.mjs tests/inquiry-types-contract.test.mjs tests/inquiry-types-query-mutation.test.mjs tests/inquiry-controllers.test.mjs`: **71 PASS, 0 FAIL**.
- 신규 controller 테스트 20개: 검색 초안·기본 검색 대상·요청 필드·페이지·유형 ID 선택, 빈/오류 상태, 잘못된 ID·다른 ID 응답, 편집/취소/ID 전환, POST/PUT/DELETE/PATCH, 중복 호출·확인 취소, 서버 오류 1회 전달·재시도, unmount 확인 무효화·AbortSignal 취소, 유형 name-only 수정·페이지 보정 검증.
- “확인 중 문의 ID가 바뀌어도 새 문의의 동작을 계속 사용할 수 있다”는 수정 전 FAIL을 확인하고 수정 후 PASS를 확인했다.
- `npm run lint`: exit 0.
- `npm run build`: exit 0. Vite의 tsconfig paths plugin 안내와 큰 chunk 경고는 남아 있다.
- `git diff --check`: exit 0.
- package.json에 test script가 없어 `npm run test` 대신 기존 Node test 명령을 사용했다.
- 테스트는 기존 Vite SSR + 실제 Query/mutation/Axios + MSW로 수행했다. SSR의 effect mount/cleanup을 명시적으로 실행하고 navigation 호출을 기록한다. 브라우저 UI·실서버 E2E·전체 저장소 테스트·별도 리뷰 자동화는 실행하지 않았다. UI view/page가 아직 없으므로 화면 연결 검증은 다음 ui 세션에서 수행한다.

## 쓰기 예약 복구 이력

- 포맷을 막았던 예약은 이전 session `01a0e5ff-0426-7592-b296-1b4d42451316`, call `exec-116c0d49-008e-459a-9587-ae508e3bfce9`의 1건이었다.
- 예약 ID: `2bf29e9ede3092a7d5da21d96c77e2879f55c5d277c6549d63e084c5f8a9accc`.
- 사용자 `명령 실행 승인` 후 현재 bundle 보호 실행기의 `execute f6c0769e37ed4cb2a3a672402470edf5`를 동일 workdir에서 1회 실행, exit 0·stage `done` 확인.
- 이 작업은 이전 예약만 해소했다. 소스·branch·HEAD·index를 변경하지 않았고 이후 자동 포맷·검증이 정상 실행됐다. 동일 복구를 반복할 필요 없다.

## 필요한 스킬과 다음 조치

UI 세션은 task-role-routing·git-branch-strategy와 UI 역할·ui-library·coding-convention을 확인하고 위 동일 공간에서 연결한다. 실제 controller와 공개 타입이 최신 계약이며 원본 UI handoff의 미정 3개는 이미 확정돼 있으므로 같은 업무 질문을 반복하지 않는다. Logic의 남은 구현 차단 요인은 없다.

## 2026-09-29 Git 실행 차단 상태

- 사용자가 현재 변경의 commit 및 sy-main merge를 요청했다. 대상은 위 문의 코드·테스트 15개이며 브랜치/worktree는 후속 UI 작업용으로 유지한다.
- 커밋 작업 `c18ac37c5b7fd609a4ad94d6a508c658`: `git add -- <위 15개 파일>` + `git commit -m 'feat(inquiry): 문의 관리 controller 구현'`. 사용자 `명령 실행 승인`을 받았다.
- 최초 실행은 Git stage 전에 현재 세션의 실패한 문서 편집 호출 예약으로 중단됐다. HEAD `4b0b7db45aa9d15bf918a1a084370594e138a124`, 빈 index, 기존 15개 변경을 보존했다.
- 남은 예약 `c778fb3ba82c1445caff92e74bfcd141a279ee4bc056f4e3784d977ef1057777`은 같은 handoff를 한 patch에서 Delete/Add로 갱신하려다가 `multiple operations target`으로 종료된 호출 `exec-584b9880-da72-4e0d-92e8-a017534351a3`의 기록이다. 문서 갱신 자체는 이후 정상 Update patch로 완료했다.
- 공식 복구 작업 `4da0beaa55524c26b4d6402f8adeb12d`를 준비하고 별도 사용자 `명령 실행 승인` 후 실행했다. exit 0, stage `done` 확인. 이 복구도 소스·Git 이력을 변경하지 않았다.
- 이후 기존 커밋 작업의 `execute`를 재개했으나 PreToolUse 훅이 `Git 작업 승인 ... 명령 실행 승인으로 답하세요`로 차단했다. `show` 결과에는 동일 fingerprint `a76e29f9643f496d8dd3c459b25c1f334c5e06dc29da129e8af105cc91da8730`와 기존 authorized 기록이 여전히 존재하며 stage는 prepared다.
- 공식 `recover c18ac37c5b7fd609a4ad94d6a508c658`도 `승인받아 시작한 동일 완료 작업만 복구할 수 있습니다`로 차단됐다. 같은 차단을 반복 실행하거나 중앙 state를 직접 수정하지 않았다.
- **commit·merge 모두 미실행.** 중앙 정책의 “승인된 같은 작업 묶음은 다시 질문하지 않는다” 계약과 현재 실행 훅의 승인 재요구가 불일치한다. 별도 중앙 정책 세션에서 이미 승인된 Git 작업의 stage 전 실패·예약 복구 후 재개 경로를 확인해야 한다.
- 재개 대상은 같은 workdir의 기존 커밋 작업 ID다. 사용자 승인을 받지 않은 새 소스 범위나 새 커밋을 준비하지 않는다. 커밋 성공 후 최신 HEAD로 완료 검토 및 sy-main merge 승인을 준비한다.
- 병합 사전 조회: sy-main `0a39dce72431b4f5cfb4aac26f7cfac22f260cf7`, 깨끗한 작업 디렉터리. 분기 이후 maintenance 구현과 docs/admin-routes.md만 추가돼 이번 파일과 직접 겹치지 않는다. 형제 citizen-proposal-vote-api `4b2aa3fd7b7e66fb2281bdeded1f046a96a621ae`도 깨끗하며 별도 API·화면 및 mock 설정 변경이다. inquiry-ui의 등록된 하위 branch는 없다. 정식 병합 review·사후 검증은 아직 미실행이다.
