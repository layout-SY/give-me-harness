# PR 정의: `sy-main` → `main`

비교 기준은 `origin/main`(`d753f0e`)과 로컬 `sy-main` HEAD다. 기간은 2026-08-13 ~ 2026-08-27, 커밋 114개, 작성자는 `okandycho-bit` 한 명이다. 전체 diff는 314 files / +16555 / -568이며, 이 중 `.codex`·`.claude` 세션·템플릿이 144개다. 애플리케이션·설정 중심 범위는 169 files / +11783 / -568이다.

제안 제목: `시민참여 서비스와 loginId 인증을 사용자 UI에 추가한다`

제안 베이스: `main`
제안 헤드: `sy-main`

이 문서는 GitHub PR 본문으로 붙여 넣을 수 있다. 워킹트리의 미커밋 `AGENTS.md`·`package.json` 변경은 PR 범위에 넣지 않는다.

---

## Summary

사용자 UI가 회의 전용 앱에서 시민참여 서비스와 로그인 세션을 포함한 모바일 셸 앱으로 바뀐다.

`main`은 `/`에서 회의 화면만 렌더하고 `/ui-showcase`로 공용 UI를 보여준다. `sy-main`은 라우트 테이블을 `src/app/routing.ts`로 옮기고, 기본 진입을 `/meeting`으로 두며, `/login`과 `/citizen-participation/**`를 추가한다. 시민참여는 FSD 경계로 `features`(API·훅·UI)와 `pages`(route 조합·표시 모델)를 나눈다. 인증은 `loginId`/`password`로 `/auth/login`을 호출하고, 액세스 토큰을 Axios에 Bearer로 붙이며, 만료 30초 전에 `/auth/refresh`로 회전한다. 개발 목은 `VITE_API_BASE_URL_STATUS=dev`일 때만 MSW를 켠다.

## 왜 이 PR인가

`main`의 사용자 UI는 Agora 회의 흐름만 제공한다. 아산 시민참여(제안·투표·토론·정책·설문·내 활동)와 통합 계정 로그인을 같은 앱에서 제공하려면 라우팅, 데이터 계층, 인증, 모바일 셸이 함께 들어가야 한다. 이 브랜치는 그 작업을 `main` 위에 한 줄기로 모은 것이다.

## 작업 내용

### 1. 시민참여 서비스 (핵심)

경로: `src/features/citizen-participation/**`, `src/pages/citizen-participation/**`, `src/shared/config/citizenParticipationRoutes.ts`

화면과 라우트:

| 화면 | 경로 |
| --- | --- |
| 메인 | `/citizen-participation` |
| 제안 목록 / 작성 / 상세 | `/citizen-participation/proposals`, `.../new`, `.../:proposalId` |
| 투표 목록 / 상세 | `/citizen-participation/votes`, `.../:voteId` |
| 토론 목록 / 상세 | `/citizen-participation/discussions`, `.../:discussionId` |
| 정책 목록 / 상세 | `/citizen-participation/policies`, `.../:policyId` |
| 설문 목록 / 상세 | `/citizen-participation/surveys`, `.../:surveyId` |
| 내 활동 | `/citizen-participation/me/activity` |

연결된 동작:

- 목록·상세 조회, 제안 작성, 투표, 토론 참여, 댓글 작성·좋아요, 신고
- 목록 `mine` 필터와 `/citizen/*` API 계약
- 투표·토론 결과 표시, 댓글 반응, 정책 댓글
- 도메인 상태 상수(`PROPOSAL_STATUS`, `VOTE_STATUS` 등), DTO/parser, TanStack Query 훅
- MSW 핸들러·픽스처로 로컬 계약 검증

구조:

- `features/citizen-participation`: API 클라이언트, DTO, parser, query/mutation 훅, 화면 UI
- `pages/citizen-participation`: route 조합, 표시 모델(`presentation.ts`, `resultRatios.ts`), route 상태 훅
- 공용 `Tabs`, `TextInput`, `Button`, `date-range-picker` 등을 화면에서 재사용

### 2. 인증과 세션

경로: `src/features/auth/**`, `src/shared/config/authRoutes.ts`, `src/shared/api/attach-access-token.ts`

- `/login`에서 `loginId`·비밀번호로 `/auth/login` 호출
- 성공 시 `localStorage`에 access/refresh 토큰과 만료 시각 저장
- 앱 시작 시 `scheduleAuthSessionRefresh()`로 만료 30초 전 `/auth/refresh` 회전
- Axios 요청 인터셉터가 저장된 액세스 토큰을 `Authorization: Bearer`로 부착
- 회의 API 헤더도 명시 토큰이 없으면 같은 저장소의 액세스 토큰을 사용
- 로그인 성공 후 `oasisapp://login` 딥링크에 access/refresh 토큰을 쿼리로 전달

`LoginPage`는 제어형 props UI이고, `/login` 라우트는 `LoginTestPage`가 훅을 연결한다.

### 3. 애플리케이션 셸과 라우팅

경로: `src/App.tsx`, `src/main.tsx`, `src/app/routing.ts`, `src/index.css`

- `useRoutes` + `routes` 테이블. 미매칭은 `/meeting`으로 리다이렉트
- `QueryClientProvider`와 MSW bootstrap을 `main.tsx`에서 기동
- 고정 모바일 셸: `#root` 폭을 `--app-mobile-max`(480px)로 제한
- `/ui-showcase`와 `src/features/shared-ui-showcase` 제거

### 4. 공용 계층

- `src/shared/ui/tabs`: 시민참여 서비스 탭
- `text-input`/`text-area` 스타일, 날짜 범위 팝오버 앵커·날짜 숫자 복구
- `withAbortSignal`, `unwrap-axios-response`, API result mapper 보강
- 로딩 중에도 UI 입력을 막지 않도록 조정

### 5. 개발 목(MSW)

- 의존성: `msw@^2.15.0`, worker는 `public/mockServiceWorker.js`
- `startMocks()`는 `VITE_API_BASE_URL_STATUS === "dev"`일 때만 worker를 시작
- 그 외 환경은 실제 `VITE_API_BASE_URL`로 요청

### 6. 의존성

추가된 runtime: `@tanstack/react-query`, `react-hook-form`, `@hookform/resolvers`, `zod`
추가된 dev: `msw`

### 7. 문서·거버넌스 (저장소에 포함된 것)

커밋된 `AGENTS.md`, `DESIGN.md` 보강, `docs/citizen-participation-case-study.md`, `docs/external-browser-deep-link-auth.md`. 후자는 설계 후보이며 현재 앱에 Deep Link 인증 서버 계약은 구현되어 있지 않다고 명시한다. `.gitignore`는 `.codex/*`·`.agents/*`·`docs/*` 등을 무시하도록 정리했다. 과거 세션 로그가 커밋에 남아 있을 수 있으나 이후 추가는 무시된다.

## `main` 대비 사용자 체감 변화

| 항목 | `main` | `sy-main` |
| --- | --- | --- |
| 기본 화면 | `/` 회의 | `/meeting` 회의. `/`는 `/meeting`으로 리다이렉트 |
| 시민참여 | 없음 | `/citizen-participation/**` |
| 로그인 | 없음 | `/login` |
| 공용 UI 쇼케이스 | `/ui-showcase` | 제거 |
| 레이아웃 | 전체 폭 | 480px 모바일 셸 |
| 인증 헤더 | 회의 API에 명시 토큰만 | 저장된 Bearer를 기본 부착 |
| 데이터 목 | 없음 | `VITE_API_BASE_URL_STATUS=dev`일 때 MSW |

## 테스트 계획

저장소 테스트 파일은 `origin/main...sy-main` 기준 24개(이름에 `test` 포함)가 추가·변경된다. 시민참여 API/훅/route, 인증 세션·로그인, MSW 기동 조건, 라우트 테이블, 공용 Tabs를 덮는다.

PR 머지 전 확인:

- [ ] `npm run test`
- [ ] `npm run lint`
- [ ] `npm run build`
- [ ] `VITE_API_BASE_URL_STATUS=dev`에서 시민참여 목록·상세·작성·투표·댓글·신고가 MSW로 동작하는지
- [ ] `VITE_API_BASE_URL_STATUS`가 `dev`가 아니면 MSW가 켜지지 않고 실제 API로 가는지
- [ ] `/login` → loginId 로그인 → 토큰 저장 → API Bearer 부착 → 만료 전 리프레시
- [ ] `/meeting` 회의 흐름이 깨지지 않는지
- [ ] 날짜 범위 선택 팝오버 앵커와 날짜 숫자가 보이는지
- [ ] 480px 셸에서 시민참여·로그인·회의 레이아웃

## 제외·남은 제한

- 3D 클라이언트 Deep Link 인증 서버 계약은 문서만 있고 미구현이다. 현재는 `oasisapp://login`으로 토큰을 쿼리에 실어 넘긴다.
- `/login`은 `LoginTestPage`가 `LoginPage`에 훅을 붙인 연결이다. 별도 프로덕션 라우트 가드(미인증 시 강제 로그인)는 이 diff에 없다.
- 회의 기능의 도메인 동작은 거의 그대로다. 변경은 Bearer 폴백, 환경 타입, 일부 CSS다.
- 워킹트리 미커밋: `package.json`의 `vite --port 12001`, `AGENTS.md` 세션 디렉터리 귀속 절. PR에 넣으려면 별도 커밋이 필요하다.
- 로컬 `sy-main`은 `origin/sy-main`보다 커밋 1개 앞선다(`586908c git ignore 정리`). origin에 올린 뒤 PR을 열면 이 커밋이 포함된다.

## 주요 커밋 묶음 (시간순)

1. 시민참여 데이터 계층·Mock (08-13): DTO, API, QueryClient, 의존성
2. 인증 기초와 시민참여 화면·라우트 (08-14): 로그인, 페이지 UI, route 테이블, 모바일 셸, showcase 제거
3. FSD pages 이관과 Mock 데이터 연결 (08-18): feature route → pages, MSW bootstrap
4. 결과·댓글·신고·도메인 상수 (08-19~08-20): 상세 상호작용, 작성 흐름 복구
5. API 확정 스펙·인증 완성 (08-26): `/citizen` 계약, Bearer, loginId, 리프레시 회전, MSW `dev` 전용
6. gitignore 정리 (08-27)

## 변경 규모 (참고)

명령: `git diff --stat origin/main...sy-main`

- 전체: 314 files, +16555, -568
- 앱·설정만 (`src`, `package.json`, `public`, `index.html`, `DESIGN.md`, `AGENTS.md`, `.gitignore`, `docs`): 169 files, +11783, -568
- `src/features/citizen-participation`: 83 files
- `src/features/auth`: 12 files
- `src/pages`: 17 files
- `src/shared`: 27 files
