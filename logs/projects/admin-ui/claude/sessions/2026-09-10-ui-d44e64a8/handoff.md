# 인계

## 최신 상태 (2026-09-11) — UI 6·7번 완료, 커밋 대기

Logic 작업 1~5번(`.codex/logs/sessions/2026-09-11-logic-8d0e5f50/handoff.md`)은 미커밋 상태로 넘어왔고, 같은 작업 폴더에서 사용자 "작업 진행" 승인 후 UI 6·7번을 구현했다. 아래 본문의 대기 작업 표는 작성 당시 기록이다.

| 파일 | 변경 |
| --- | --- |
| `src/pages/cp-news/ui/cp-news-list-page.tsx` | `OpenedNewsForm`(`locationKey` + 등록/수정 대상) state로 목록↔폼 전환. 목록은 안쪽 `CpNewsListContent`로 분리해 폼이 열린 동안 목록 controller를 언마운트. 폼 key `create` / `edit-{id}`, ID는 `String(id)`로 전달. 위치(`location.key`)가 바뀌면 렌더 중 state를 비워 목록으로 복귀 |
| `src/pages/cp-news/ui/cp-news-form-page.tsx` | `mode`·`newsId`·`onClose` props를 받는 `CpNewsFormPage` 하나로 정리. `useParams`·`navigate`·`newsListPath` 사용 제거 |
| `src/pages/cp-news/index.ts` | `CpNewsCreatePage`, `CpNewsEditPage` export 제거 |
| `src/app/router/routes.tsx` | `news/new`, `news/:newsId/edit`, `boards/notices/:noticeId/edit` 라우트와 import 제거, news 주석 갱신 |
| `src/pages/cp-board/index.ts` | `CpNoticeFormPage` export 제거. 옛 `cp-notice-form-*` 파일은 유지 |

검증: `npm run lint` 0건, `npx tsc --noEmit -p tsconfig.app.json` 통과, `npm run build` 성공, `node --test --test-concurrency=1` 167/167 통과. 새 테스트는 추가하지 않았다(기존 SSR 도구로 클릭 전환을 확인할 수 없고, 바뀐 것은 페이지 조합뿐). 개발 서버·브라우저 확인은 미실행.

커밋: 사용자 승인 후 보호 실행 `a2c20701db9d16b1f30ef64a350964a5`로 소스·테스트 11개 파일을 커밋 `6efd8ab`(`feat : 공지사항 등록·수정을 목록 페이지 state로 전환하고 news mock 등록`)으로 기록. 첫 execute는 승인이 작업 준비 전에 입력되어 "사용자 승인과 도구 실행 예약이 필요합니다"로 거부됐고, 준비 후 재승인으로 실행됐다. 작업 폴더 clean, `sy-main`보다 8커밋 앞섬.

병합 (2026-09-13): review `9be0231405fa4304b7189fd1ea87f790`(보고서 `unknown/news-merge-review.json`) 수집 후 completion `2bbbfb67532e41a389753c7faf047d77`을 승인·실행했다. `task/news-management-ui` `6efd8ab` → `sy-main` ff-only 병합으로 `sy-main`이 `5834f92`에서 `6efd8ab`로 이동했고, 사후 `npm run lint`·`npm run build`가 exit 0으로 `verification_passed: true`다. cleanup 미포함이라 source branch는 유지되며 stage는 `retained`다. 실행 위치의 checkout branch는 `sy-main`으로 바뀌었다. 원격 반영 없음.

정리 (2026-09-13): review `3c01ee99361f4dee82ed5bcbc6836c6a`(보고서 `unknown/news-cleanup-review.json`) 기반 completion `3a7217188d9b450bb951ce1b91dc5a48`을 승인·실행해 stage `cleaned`. 사후 `npm run lint` 통과 후 `task/news-management-ui` 로컬 branch를 삭제했다. 병합 단계는 source·target이 같은 commit이라 no-op이었다. 관계 기록이 없는 `task/connect-news-api`, `task/connect-inquiry-mutation-api`, `task/sign-in-page`는 완료 정리 경로 대상이 아니어서 사용자가 직접 `git branch -d`로 삭제했다. 현재 로컬 branch는 `sy-main`, `main`, `harness/v0.1.3-admin-ui`뿐이고 worktree는 기본 checkout 하나다.

남은 것: `newsListPath`는 테스트에서만 쓰이며 유지. 옛 `cp-notice-form-*` 파일은 사용처 없이 남아 있고 테스트만 참조. 개발 서버 화면 확인 미실행. 원격 push 미실행. `git remote -v`의 origin URL에 GitHub 토큰이 그대로 들어 있어 정리가 필요하다(이번 범위 밖).

## Assignment 이동

- 보내는 host·session·role: `claude` / `2026-09-10-ui-d44e64a8` / `ui`
- 받는 host·session·제안 role: 미지정. 새 `--role logic` 세션이 이 문서를 읽는다.
- 작성일: 2026-09-11, Asia/Seoul.

## 역할 라우팅

- 요청 역할(`requested_roles`): `ui`
- 확인된 역할(`confirmed_roles`): `ui` (inject `--role ui`)
- 완료 역할(`completed_roles`): 현재 브랜치 상태 확인, 추가 커밋 4개(`a4c4ec9`, `cd08d5e`, `fd619a6`, `7c5f91c`) 검토·검증, 공지 수정 라우팅 방침 확정. 소스 변경 없음.
- 다음 제안 역할(`next_role`): `logic`
- 역할 판단 근거: 남은 작업 중 개발 환경 MSW 등록과 controller hook의 이동 계약 변경은 데이터 계층과 hook 상태 전이라 Logic 책임이다. 페이지 조합·라우트 정리는 Logic 완료 후 UI가 한다.
- 사용자 확인 (2026-09-11):
  - "공지 수정은 별도 라우팅 없이 그냥 react 컴포넌트 state로 처리해"
  - 대상: **news 등록·수정 둘 다** state로 전환 (`/cp/news/new`, `/cp/news/:newsId/edit` 라우트 제거)
  - 옛 경로 `/cp/boards/notices/:noticeId/edit`: **라우트 제거**
  - hook 수정 담당: **Logic에 handoff로 위임**
  - "mock 관련해선 logic에 위임" → 이 문서로 위임

## 목표 및 현재 상태

`task/news-management-ui`(HEAD `7c5f91c`)의 공지사항 관리 화면을 URL 라우트 3개 대신 목록 페이지 안의 컴포넌트 state로 목록↔폼을 전환하도록 바꾼다. 이 문서는 그중 Logic 몫 두 가지를 넘긴다.

1. 개발 환경에서 news mock이 동작하도록 브라우저 MSW에 등록
2. controller hook이 `navigate`를 직접 호출하지 않고 페이지가 주입한 callback을 호출하도록 계약 변경

현재 브랜치 상태 (2026-09-11 이 세션에서 직접 확인):

- 작업 폴더 clean, linked worktree 없음, `sy-main`보다 7커밋 앞서고 뒤처진 커밋 없음
- `npm run lint` 0건, `npx tsc --noEmit -p tsconfig.app.json` 통과, `npm run build` 성공, `node --test --test-concurrency=1` 163/163 통과
  - 첫 실행 1회는 164건 중 1건 실패. 다른 세션이 worktree를 정리하던 시점이었고 재실행에서 재현되지 않음. 원인 미확인.

## 완료된 작업

- 새로 들어온 커밋 4개의 diff 검토. 동작을 깨는 변경 없음.
  - `text-input` 초기값 변경은 유일한 사용처(로그인 화면)에서 결과가 같다.
  - 삭제된 `useFetchAdapter`, `SelectUsersPopup` 조회 코드는 사용처가 없다.
  - `[pubsub]` 의존성은 `usePubSub`이 안정 참조라 재구독이 반복되지 않는다.
- 공지 수정 방침 확정 (위 사용자 확인)

## 대기 중인 작업

| 순서 | 담당·위치 | 수행 방법·목적·기대 결과 |
| --- | --- | --- |
| 1 | Logic / `src/mocks/handlers.ts` | `createNewsHandlers()`를 `handlers` 배열에 등록해 개발 서버에서 `/cp/news` 목록·등록·수정·삭제가 mock으로 동작하게 한다 |
| 2 | Logic / `src/pages/cp-news/hook/use-cp-news-list-controller.ts` | `navigate` 대신 주입된 callback으로 등록·수정 열기를 알린다 (아래 계약) |
| 3 | Logic / `src/pages/cp-news/hook/use-cp-news-form-controller.ts` | 저장 성공·삭제 성공·`onBack`에서 `navigate(returnPath)` 대신 주입된 `onClose()`를 호출한다 (아래 계약) |
| 4 | Logic / `src/pages/cp-news/ui/cp-news-list-page.tsx`, `cp-news-form-page.tsx` | 바뀐 hook 시그니처로 빌드가 깨지지 않게 **기존 라우트 동작 그대로** callback 안에서 `navigate`를 호출하도록 최소 수정. 화면 동작은 바꾸지 않는다 |
| 5 | Logic / `tests/news-list-controller.test.mjs`, `tests/news-form-controller.test.mjs` | 이동 검증을 callback 호출 검증으로 바꾸고, 기존 경합·늦은 응답 무시 검증은 유지 |
| 6 | UI 후속 / `cp-news-list-page.tsx`, `cp-news-form-page.tsx`, `src/pages/cp-news/index.ts` | 목록 페이지가 `formTarget` state를 들고 목록 또는 폼을 렌더하도록 조합 변경. 4번의 임시 `navigate`를 제거 |
| 7 | UI 후속 / `src/app/router/routes.tsx`, `src/pages/cp-board/index.ts` | `news/new`, `news/:newsId/edit`, `boards/notices/:noticeId/edit` 라우트와 `CpNoticeFormPage` export 제거 |

4번은 Logic 커밋 단독으로도 lint·build·test가 통과하게 하려는 임시 연결이다. 6번에서 UI가 state 전환으로 교체한다.

## 결정 사항 및 제약 조건

### 1. MSW 등록

- `src/mocks/news.handlers.ts`의 `createNewsHandlers()`는 이미 있고 테스트(`news-msw`, `news-mutation`, 두 controller 테스트)에서만 쓰인다. `handlers.ts`에 import와 `...createNewsHandlers()`만 추가한다.
- news RESOURCE는 `/admin/news`, 옛 `cp-notice.handlers.ts`는 `/v1/cp/notices`라 경로가 겹치지 않는 것으로 보인다. 등록 순서에 따른 가로채기가 없는지 Logic이 확인한다.
- 브라우저 worker의 활성 조건(환경 변수 등)은 이 세션에서 확인하지 못했다. Logic이 개발 서버에서 mock이 실제로 켜지는 조건을 확인해 결과에 적는다.
- mock 데이터(`NEWS` 4건)와 in-memory 동작은 바꾸지 않는다.

### 2. 목록 controller 계약

제안 시그니처 (이름은 Logic이 인접 관행에 맞게 조정 가능):

```ts
type CpNewsListNavigation = {
  readonly onOpenCreate: () => void;
  readonly onOpenEdit: (newsId: number) => void;
};

export const useCpNewsListController = (navigation: CpNewsListNavigation): CpNewsListController
```

- 반환 타입 `CpNewsListController`는 **바꾸지 않는다.** View(`cp-news-list-view.tsx`)가 그대로 동작해야 한다.
- `table.onOpenEdit`의 `Number.isSafeInteger` 방어는 유지하고, 통과한 경우에만 `navigation.onOpenEdit(newsId)`를 호출한다.
- `returnSearch`와 `useNavigate`는 제거한다. 검색 조건과 페이지는 계속 URL query(`useSearchParams`)에 둔다. state 전환 뒤에도 URL이 바뀌지 않으므로 목록 복귀 시 검색·페이지가 그대로 유지된다.

### 3. 폼 controller 계약

```ts
export const useCpNewsFormController = (
  mode: CpNewsFormMode,
  newsId: string,
  onClose: () => void,
): CpNewsFormController
```

- `newsId`는 기존처럼 문자열로 받아 `parseNewsFormId`로 검증한다. UI는 state의 숫자 ID를 `String(id)`로 넘긴다. 잘못된 ID는 계속 `load.isFailed`로 표현한다.
- `onClose`를 호출하는 곳: 저장 성공, 삭제 성공, `onBack`. `onBack`은 기존처럼 요청 진행 중이면 무시한다.
- `requestGuard`의 비활성화(언마운트) 뒤에는 `onClose`를 호출하지 않는다. 사용자가 폼을 닫은 뒤 늦게 도착한 성공 응답이 화면을 다시 전환하면 안 된다.
- 반환 타입 `CpNewsFormController`는 바꾸지 않는다.
- `useSearchParams`, `newsListPath` 의존은 제거한다. `newsListPath`가 다른 곳에서 쓰이지 않게 되면 삭제 여부는 Logic이 판단한다 (현재 사용처: 폼 controller와 두 controller 테스트).
- mutation 성공 data는 `void`이고 캐시 무효화는 `news-mutation-options.ts`가 처리한다. 목록 재조회를 페이지에서 따로 구현하지 않는다.

### 4. UI가 6·7번에서 할 조합 (참고)

```ts
type NewsFormTarget = { readonly mode: "create" } | { readonly mode: "edit"; readonly newsId: number };
```

- 목록 페이지가 `formTarget: NewsFormTarget | null` state를 들고, null이면 목록, 아니면 폼을 렌더한다.
- 폼은 `key`를 `create` / `edit-{id}`로 줘서 대상이 바뀔 때 편집 생명주기를 분리한다 (현재 `CpNewsEditPage`의 `key={newsId}`와 같은 의도).
- 트레이드오프 (사용자에게 설명함): 수정 화면에서 새로고침·뒤로가기를 하면 목록으로 돌아가고, 수정 화면 주소는 공유할 수 없다.

### 지켜야 할 제약

- View 파일(`cp-news-list-view.tsx`, `cp-news-form-view.tsx`, `cp-news-delete-popup.tsx`)과 `model/*.types.ts`의 공개 controller 타입은 바꾸지 않는다.
- 옛 `src/pages/cp-board/**/cp-notice-form-*` 파일은 이번에 지우지 않는다. `tests/news-form.test.mjs`가 `cp-notice-form.model.ts`와 `cp-notice-form.config.ts`를 직접 불러온다. 라우트와 export 제거(7번)만 UI가 한다.
- 검증을 약화해 통과시키지 않는다. 테스트 삭제·eslint disable 금지.
- 관련 없는 정리·포맷 변경을 섞지 않는다.

## 소유권과 Git 계약

- 이 세션의 변경 경로: 이 산출물(`.claude/logs/sessions/2026-09-10-ui-d44e64a8/handoff.md`)만. 애플리케이션 소스 변경 없음.
- 역할별 파일 담당:
  - Logic: `src/mocks/handlers.ts`, `src/pages/cp-news/hook/*`, `src/pages/cp-news/lib/*`(필요 시), 두 controller 테스트, 4번의 페이지 entry 최소 수정
  - UI(후속): 페이지 entry의 state 조합, `src/pages/cp-news/index.ts`, `src/app/router/routes.tsx`, `src/pages/cp-board/index.ts`
  - 페이지 entry 두 파일은 Logic → UI 순서로 **순차 수정**하며 동시에 편집하지 않는다.
- 충돌 여부: 현재 브랜치 clean, 다른 진행 중 worktree 없음.
- task·branch·worktree: `task/news-management-ui` / HEAD `7c5f91cf14e925c27b671c9d205939d42d631395` / `/Users/okand/SynologyDrive/asan-metaverse-admin-ui` (기본 checkout). 직접 부모는 `sy-main`.
- 승인할 Git 작업: 아직 없음. 작업 위치(이 브랜치에서 바로 할지, `task/news-management-ui`에서 자식 브랜치·linked worktree를 만들지)는 Logic 세션이 사용자에게 제안하고 승인받는다. 이전 Logic 작업은 자식 브랜치(`task/news-management-logic`)를 만들어 fast-forward로 병합했다.
- `sy-main` 병합은 이 작업(UI 6·7번 포함)이 끝난 뒤 별도 승인으로 진행한다.
- 산출물 책임: contributor (이 작업의 부분 역할 인계)

## 관련 경로와 스킬

- 정책 snapshot: `/Users/okand/SynologyDrive/asan-agent-policy/build/admin-ui/claude-ui-90b8c56e49d8f0d3/policy`
- Logic 참고 스킬: `task-role-routing`(+`references/logic.md`), `git-branch-strategy`, `data-fetch-layer`, `coding-convention`, `implementation-quality`, `documentation`
- 관련 소스: `src/mocks/handlers.ts`, `src/mocks/news.handlers.ts`, `src/pages/cp-news/hook/*`, `src/pages/cp-news/lib/cp-news-list.model.ts`, `src/pages/cp-news/lib/cp-news-form-request.ts`, `src/entities/news/model/news-mutation-options.ts`
- 이전 인계:
  - `.claude/logs/sessions/2026-09-09-ui-f14c4487/handoff.md` (UI 1·2차 인계, controller 계약 원문)
  - `.codex/logs/sessions/2026-09-11-logic-b5cf6915/handoff.md` (타입·lint 정리와 news 브랜치 병합 완료)

## 명령어 및 결과

| 명령 | 결과 |
| --- | --- |
| `git status --short --branch`, `git worktree list`, `git branch -vv` | `task/news-management-ui` clean, 기본 checkout만 존재 |
| `git log --oneline sy-main..task/news-management-ui` | 7커밋, `sy-main` 대비 뒤처짐 없음 |
| `git show` (`a4c4ec9`, `cd08d5e`, `fd619a6`, `7c5f91c`) | diff 검토, 동작을 깨는 변경 없음 |
| `npm run lint` | 오류·경고 0건 |
| `npx tsc --noEmit -p tsconfig.app.json` | 통과 |
| `npm run build` | 성공, 청크 크기 경고만 |
| `node --test --test-concurrency=1` | 163/163 통과 (첫 실행 1회 164건 중 1건 실패, 재현 안 됨) |

## 실행하지 않은 검증

개발 서버 실행, 브라우저 화면 확인, 실서버 호출, MSW worker 활성 조건 확인. 소스 변경이 없어 새 테스트는 작성하지 않았다.

## 다음 조치

1. Logic 담당이 새 `--role logic` 세션에서 이 문서와 위 관련 소스를 읽고 작업 위치(브랜치·worktree)를 사용자에게 제안·승인받는다.
2. 대기 작업 1~5번을 구현한다. 커밋 시점에 lint·tsc·build·전체 test가 통과해야 한다.
3. 결과·변경된 시그니처·MSW 활성 조건을 handoff로 UI에 넘긴다.
4. UI가 6·7번(state 조합, 라우트·export 제거)을 진행하고 개발 서버 mock으로 등록 → 목록 복귀 → 수정·게시 → 삭제 흐름을 확인한다.
5. 전체 완료 후 `task/news-management-ui` → `sy-main` 병합을 별도 승인으로 진행한다.
