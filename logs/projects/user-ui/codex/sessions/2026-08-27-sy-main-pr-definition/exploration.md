# 탐색

## 요청

현재 프로젝트에서 `main`과 비교해 `sy-main` 작업 내용을 정의하는 PR 문서를 만든다.

## 대상 관련 사실

- 현재 브랜치: `sy-main`. `origin/HEAD`는 `origin/sy-main`
- `origin/main`과 로컬 `main`은 모두 `d753f0e`
- merge-base(`origin/main`, `sy-main`) = `d753f0e`
- `origin/main..sy-main`: 114 커밋, 2026-08-13 ~ 2026-08-27, 작성자 `okandycho-bit`
- 전체 diff: 314 files, +16555, -568
- 앱·설정 중심: 169 files, +11783, -568 (`src` 160, 그중 citizen-participation 83)
- 로컬 `sy-main`은 `origin/sy-main`보다 1커밋 앞섬: `586908c git ignore 정리`
- 워킹트리 미커밋: `AGENTS.md`(세션 디렉터리 귀속), `package.json`(`vite --port 12001`)
- `main`의 `App.tsx`는 `/` → `MeetingPage`, `/ui-showcase` → showcase
- `sy-main`의 `src/app/routing.ts`는 `/meeting`, `/login`, `/citizen-participation/**`
- 인증: `loginId` 로그인, `persistAuthSession`, `scheduleAuthSessionRefresh`, Axios Bearer, `oasisapp://login` 딥링크
- MSW: `VITE_API_BASE_URL_STATUS === "dev"`일 때만 기동
- 시민참여 API 예: `GET /citizen/proposals` with `mine` 쿼리

## 불러온 스킬

- `.agents/skills/policy/SKILL.md`
- `.agents/skills/policy/documentation/SKILL.md`
- `.agents/skills/policy/harness/SKILL.md`
- `.agents/skills/policy/portfolio/SKILL.md`
- `.agents/skills/policy/review-checklist/SKILL.md`

## `src/shared/ui/`의 재사용 가능 자산

이 작업은 신규 UI 구현이 아니라 기존 브랜치 요약이다. `sy-main`에서 시민참여가 쓰는 공용 UI는 다음과 같다.

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| `tabs` | `sy-main`에서 신규 추가된 자산으로 문서에 기록 | `src/shared/ui/tabs/`가 `origin/main` 대비 Added |
| `button`, `text-input`, `date-range-picker` | 기존 자산 재사용으로 기록 | 로그인·시민참여 화면이 해당 경로를 import |
| showcase 페이지 | 제거됨으로 기록 | `src/features/shared-ui-showcase/**` Deleted |

## 제약 조건 및 미확인 사항

- `npm run test`/`lint`/`build`는 이 세션에서 실행하지 않았다. PR 테스트 계획에만 적었다.
- `layout-sy` 원격 push 계정 문제는 이번 요청 범위가 아니다.
- Deep Link 설계 문서는 보류 상태이며, 런타임은 `oasisapp://login` 쿼리 토큰 전달만 확인했다.

## 결론

PR 정의서는 시민참여·인증·셸/라우팅·MSW·공용 계층 순으로 쓰고, 하네스 파일은 규모만 분리한다. 미커밋 변경은 PR 범위에서 뺀다.
