# 인계

## Assignment 이동

- 보내는 host·session·role: `codex` / `2026-09-11-logic-8d0e5f50` / `logic`.
- 받는 host·session: 미지정. 제안 role은 새 `--role ui` 세션이다.
- 작성일: 2026-09-11, Asia/Seoul.

## 역할 라우팅

- `requested_roles`: `logic`.
- `confirmed_roles`: `logic` (inject role 및 사용자 요청).
- `completed_roles`: Logic 인계 작업 1~5의 구현·검증·기록.
- `next_role`: `ui`.
- 판단 근거: controller와 mock 연결이 끝났고 남은 작업은 목록 페이지의 state 조합과 라우트·barrel 정리다.
- 사용자 확인: 원본 UI 인계의 등록·수정 state 전환 결정을 따랐다. 이번 세션에서 임시 라우트 연결의 저장·삭제·목록 복귀 모두 이력을 교체하도록 통일하는 차이를 설명했고 “그렇게 진행하고 작업 진행해”로 승인받았다.

## 목표 및 현재 상태

`.claude/logs/sessions/2026-09-10-ui-d44e64a8/handoff.md`의 Logic 작업 1~5를 완료했다. callback 계약을 새 시그니처로 연결했고, 전체 테스트 167/167·lint·타입 검사·build가 통과했다. 실제 화면은 UI 후속 작업 전이므로 현재까지 URL 라우트로 등록·수정 폼에 진입한다.

## 완료된 작업

| 경로 | 변경 내용 |
| --- | --- |
| `src/mocks/handlers.ts` | 기존 `createNewsHandlers()`를 브라우저용 배열에 추가. |
| `src/pages/cp-news/hook/use-cp-news-list-controller.ts` | `navigation.onOpenCreate`, `navigation.onOpenEdit(newsId)`를 호출. `useNavigate`·`returnSearch` 제거. 검색·페이지 query 유지. |
| `src/pages/cp-news/hook/use-cp-news-form-controller.ts` | 세 번째 인자 `onClose`를 저장·삭제 성공 및 `onBack`에 연결. Router·복귀 경로 의존 제거. |
| `src/pages/cp-news/ui/cp-news-list-page.tsx` | callback 안에 기존 등록·수정 경로와 정규화된 검색 query 연결. |
| `src/pages/cp-news/ui/cp-news-form-page.tsx` | `newsListPath`와 `navigate(..., { replace: true })`로 임시 닫기 동작 연결. |
| `tests/news-list-controller.test.mjs` | callback 호출·숫자 ID 전달·안전하지 않은 ID 차단 검증 추가. |
| `tests/news-form-controller.test.mjs` | Router 없이 폼 controller·닫기 동작 확인. 생성·수정·삭제의 void 성공 callback 확인. 기존 경합·늦은 응답 검증 유지. |
| `tests/news-msw.test.mjs` | 브라우저용 전체 배열에서 news 조회·등록·수정·삭제 확인. |

## 결정 사항 및 연결 계약

```ts
type CpNewsListNavigation = {
  readonly onOpenCreate: () => void;
  readonly onOpenEdit: (newsId: number) => void;
};

useCpNewsListController(navigation: CpNewsListNavigation): CpNewsListController;
useCpNewsFormController(mode: CpNewsFormMode, newsId: string, onClose: () => void): CpNewsFormController;
```

- `CpNewsListNavigation`은 hook 파일의 로컬 타입이다. UI는 callback 객체를 인자로 넘기면 된다.
- View 및 `model/*.types.ts`의 공개 반환 타입을 변경하지 않았다.
- 목록 수정 열기는 기존 `Number.isSafeInteger`를 통과한 ID만 전달한다. 폼은 기존 `parseNewsFormId`로 문자열 ID를 검증한다.
- 저장·삭제 성공과 요청 대기 중이 아닌 목록 복귀에 `onClose()`를 사용한다. 비활성 request guard는 늦은 비동기 성공·실패 callback을 전달하지 않는다.
- mutation 성공 data는 `void`; `news-mutation-options.ts`가 캐시 무효화와 취소를 처리한다. 페이지에서 별도 재조회를 추가하지 않는다.
- `newsListPath`는 현재 `cp-news-form-page.tsx`와 목록 controller 테스트에서 사용하므로 유지했다. UI가 임시 라우트 연결을 제거할 때 관련 사용처와 복귀 경로 테스트의 정리 필요성을 함께 검토한다.
- mock 초기 `NEWS` 4건 및 in-memory 동작은 그대로다. 전체 handler 배열에 대한 실제 CRUD 요청이 통과하여 기존 handler가 news 요청을 가로채지 않는 것을 확인했다.

## MSW 실행 조건

- `src/app/index.tsx` → `src/app/mock-api-policy.ts`에서 `VITE_ENVIRONMENT === "dev"`일 때만 활성화한다. `DEV` 플래그나 mode 이름만으로 켜지지 않는다.
- worker 경로: `/mockServiceWorker.js`. worker 시작 완료 후 React 앱을 렌더링한다.
- 현재 `loadEnv("development", process.cwd(), "VITE_ENVIRONMENT")`에서 값이 미설정임을 확인했다. 개발 확인은 프로젝트 루트에서 `VITE_ENVIRONMENT=dev npm run dev`로 실행한다.
- 활성 조건 및 환경 파일은 변경하지 않았다. `/admin/news`는 기존 CP·citizen 미처리 요청 감시 대상에 포함되지 않지만 등록된 handler로 정상 처리된다.

## 보내는 작업의 위치와 변경 상태

- project·저장소 루트: `admin-ui`, `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`.
- 현재 branch: `task/news-management-ui`.
- HEAD·인계 기준 commit: `7c5f91cf14e925c27b671c9d205939d42d631395`.
- worktree·실행 디렉터리: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`.
- 기준 시점: 2026-09-11 검증 및 산출물 작성 종료 시점.
- 완료한 새 commit: 없음. Git 변경 명령을 실행하지 않았다.
- staged: 없음.
- unstaged: 위 완료된 작업 표의 소스·테스트 8개 파일.
- 일반 untracked: 없음.
- ignored 산출물: `.codex/logs/sessions/2026-09-11-logic-8d0e5f50/`의 `plan.md`, `final-summary.md`, `handoff.md`. 파일은 로컬에 있으며 `git status --short --ignored --untracked-files=all`에서 세 파일 모두 `!!`로 확인했다. 다른 공간으로 옮길 경우 이 기록이 일반 commit에 자동 포함된다고 가정하지 않는다.
- 시작 시 clean 상태였으며 검증 후 변경 목록에서도 이번 작업 외 소스 변경을 발견하지 않았다. 기존 UI 완료물과 다른 세션의 로그를 보존한다.

## 인계 대상 작업 공간

### 작업 공간: `news-shared`

- 수행할 기능: news 목록 페이지 안에서 등록·수정 폼을 state로 표시하고 사용하지 않을 라우트를 제거한다.
- 사용할 역할: 후속 `ui`.
- project·저장소: `admin-ui`, `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`.
- 목적지 branch: `task/news-management-ui`.
- worktree·실행 디렉터리: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`.
- 기존 공간이며 `git worktree list --porcelain`에서 기본 checkout 하나만 확인했다.
- 확인한 HEAD: `7c5f91cf14e925c27b671c9d205939d42d631395`.
- 직접 부모: 원본 UI handoff의 `sy-main`. Git 조회에서 시작 HEAD가 `sy-main`보다 7커밋 앞서고 뒤처짐 없음을 확인했다. 병합 시 중앙 관계 기록은 다시 확인한다.
- 공간 공유 이유: 같은 결과물을 Logic → UI 순차로 연결하므로 이 미커밋 변경을 그대로 이어간다. 별도 branch/worktree를 만들지 않았다.
- 진입 전 실제 branch·HEAD·dirty를 다시 확인하고, 차이가 있으면 추가 변경을 비교한다. 이 문서의 HEAD로 되돌리지 않는다.
- Git 승인: 없음. 이 작업을 commit하거나 `sy-main`으로 통합할 때 실제 대상·diff와 명령에 대한 승인이 필요하다.

## 역할별 상세 작업 및 대기 작업

### UI: 목록↔폼 state 조합 및 라우트 정리

- 작업 공간: `news-shared`.
- 시작 조건: 이 문서와 현재 파일·diff 확인. Logic의 소스 쓰기는 종료되었다.
- `src/pages/cp-news/ui/cp-news-list-page.tsx`: `formTarget` state를 `null | { mode: "create" } | { mode: "edit"; newsId: number }`로 관리하고 null이면 목록, 아니면 폼을 표시한다. 현재 임시 이동 callback을 state 설정 callback으로 교체한다.
- `src/pages/cp-news/ui/cp-news-form-page.tsx`: 외부에서 `mode`, 문자열 `newsId`, `onClose`를 받아 폼 controller에 전달하도록 조합한다. 닫기 callback은 목록 페이지의 `formTarget`을 null로 만든다. 임시 `navigate`와 query 조회를 제거한다.
- 폼 key는 `create` 또는 `edit-{id}`로 주어 편집 생명주기를 분리한다. 숫자 ID는 `String(id)`로 hook에 전달한다.
- `src/pages/cp-news/index.ts`: 최종 페이지 조합에 맞게 export를 조정한다.
- `src/app/router/routes.tsx`: `news/new`, `news/:newsId/edit`, `boards/notices/:noticeId/edit` 경로와 불필요해지는 import를 제거한다.
- `src/pages/cp-board/index.ts`: `CpNoticeFormPage` export를 제거한다. 옛 `cp-notice-form-*` 구현은 이번 요청에서 삭제하지 않는다. `tests/news-form.test.mjs`가 옛 model·config를 직접 참조한다.
- 재사용 자산: 현재 목록·폼·삭제 View, 새 controller 인자 계약, 기존 query·mutation 훅과 request guard. 공개 View/controller 반환 타입을 유지한다.
- 검색·페이지 query는 URL에 계속 유지한다. 목록 재조회는 기존 mutation 캐시 무효화를 따른다.
- 겹치는 파일: 두 페이지 entry는 Logic → UI 순서로 수정한다. 이번 변경을 덮어쓰지 않고 callback 연결 부분을 state 조합으로 교체한다.
- 검증: lint·명시적 타입 검사·build·전체 Node 테스트. `VITE_ENVIRONMENT=dev npm run dev` 환경에서 등록 → 목록 복귀 → 수정·게시 → 삭제, 검색·페이지 복원, 새로고침·뒤로가기 동작을 확인한다.
- 현재 계약에 추가 미확정 사항은 없다. 후속 구현에서 새 서비스 계약이나 재사용 공백이 발견되면 별도 확인한다.
- 다음 결과: UI 구현·검증 결과와 실제 diff를 같은 작업 공간에서 최종 검토·Git 승인 단계로 전달한다.

## 협업 순서와 Git 통합

- Logic 쓰기·검증 종료 → 새 UI 세션이 실제 상태 확인 → 페이지 조합·라우트 정리 → 최종 검토 → Git 승인 순서다.
- 새 branch·worktree·commit·merge는 수행하지 않았다. 완료 후 `task/news-management-ui` → 직접 부모 `sy-main` 통합은 별도 승인 대상이다.
- 이번 작업은 Git 통합 검토 단계가 아니므로 형제·하위 작업에 대한 완료 판정을 하지 않았다. 병합 시 중앙 관계·형제 변경·미처리 하위 작업을 확인한다.
- 현재 assignment 산출물 책임은 `owner`. 계획·최종 요약에 더해 역할 전환용 handoff를 작성했다.
- 다른 host·세션의 로그는 읽기 전용이다. 다음 UI 세션은 자기 로그를 작성한다.

## 관련 경로와 스킬

- 원본 인계: `.claude/logs/sessions/2026-09-10-ui-d44e64a8/handoff.md`.
- 현재 정책 snapshot: `/Users/okand/SynologyDrive/asan-agent-policy/build/admin-ui/codex-logic-b55f2e8da3e80e9c/policy`.
- 적용 스킬: task-role-routing(+logic·handoff·pipeline), git-branch-strategy, skill-index, coding-convention, data-fetch-layer, implementation-quality, type-definition, documentation.
- 다음 UI 세션은 자기 bundle의 role·Git 스킬 및 UI 구현 스킬을 적용한다.

## 명령어 및 결과

| 명령어 | 결과 |
| --- | --- |
| `git status --short --branch`, `git worktree list --porcelain` | 현재 위치·HEAD·미커밋 변경 확인 |
| 변경된 세 파일의 `node --test --test-concurrency=1` | 30/30 통과 |
| `npm run lint` | 오류·경고 0건 |
| `npx --no-install tsc --noEmit -p tsconfig.app.json` | 통과 |
| `npm run build` | 성공. tsconfig paths plugin 안내·청크 크기 경고 |
| `node --test --test-concurrency=1 --test-reporter=spec` | 167/167 통과. MockTimers 실험 기능 경고 |
| `git diff --check` | 통과 |
| development 환경의 `VITE_ENVIRONMENT`만 조회 | 미설정 |

## 실행하지 않은 검증과 제한

- 개발 서버·브라우저 service worker 실행, 실제 화면의 mount/unmount·이력 전환, 시각 QA와 실서버 호출은 수행하지 않았다.
- callback·폼 상태는 기존 SSR 테스트, 비동기 요청은 request guard와 실제 Query/Mutation·Node MSW로 검증했다.
- 별도 Watcher 에이전트는 실행하지 않았다. 자체 diff 점검과 실행 검증을 완료했다.
- 첫 요청 조사 중 읽기 전용 검색 일부가 보호 훅에서 차단되었다. 사용자 후속 승인 이후 프로젝트 경로를 명시한 고정 문자열 검색과 파일 읽기로 필요한 조사를 완료했다. 정책 자체는 변경하지 않았다.

## 다음 조치

새 `--role ui` 세션에서 `news-shared`의 현재 diff를 보존하며 위 state 조합과 라우트·export 정리를 이어간다. 개발 mock 활성 조건을 반영해 최종 화면 흐름을 확인한다.
