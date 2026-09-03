# Implementation Log — 시민참여 관리자 Web UI (PDF p15~p43)

## 반영한 구현 컨펌 (사용자 지시)

| # | PDF | 지시 | 반영 |
| --- | --- | --- | --- |
| 1 | p17 | 상태 변경을 단계 고정 전이가 아닌 **현재 상태 → 나머지 상태 임의 선택**으로. 표시는 `"접수 →" + select(현재 상태 제외)` | `shared/ui/status-transition-field` 신설(현재 상태 고정 라벨 + 화살표 + Dropdown), `features/cp-status-transition`의 `buildTransitionOptions`가 현재 상태만 제외한 옵션 생성 |
| 2 | p17 | 담당부서도 select, 목록은 "스마트도시과"만 | `entities/cp-proposal/model/types.ts`의 `CP_DEPARTMENTS`에 스마트도시과 1건만 정의 |
| 3 | p18 | 관리자 임의 수정 불가 → 화면정의서 그대로 | 상태·담당부서를 select로 열지 않고 정의서 표기(`검토중 → 채택`, `스마트도시과`)를 `cp-readonly-box`로 표시. 입력은 정의서상 입력 항목인 처리 의견만 허용 |
| 4 | p20 | "결과 현황" → "투표 현황" | `cp-vote-detail-page.tsx` 섹션 제목 변경 (p22 토론은 지시 범위 밖이라 "결과 현황" 유지) |
| 5 | p27 | 처리 상태는 선택 댓글 대상 → "처리 저장" 버튼 **위**에 배치, 선택 시 POST 가능한 구조 | 상세 패널 하단 카드에 `ChoiceChipGroup` + 바로 아래 `처리 저장`. `cpCommentApi.updateProcess({commentId, state})` POST를 `useApi`로 호출 |

## 산출물

### shared/ui 신규 (7)
`kpi-card` · `section-card` · `definition-list` · `choice-chip-group` · `ratio-bar` · `timeline-list` · `status-transition-field`

### widgets 신규 (1 슬라이스 / 5 컴포넌트)
`admin-page-layout` — `PageHeader` · `KpiStrip` · `FilterBar` · `MasterDetailLayout` · `ActionBar`

### entities 신규 (13)
`cp-dashboard` `cp-main-display` `cp-proposal` `cp-vote` `cp-discussion` `cp-policy` `cp-survey` `cp-comment` `cp-report` `cp-board` `cp-notice` `cp-activity-log` `cp-reward` `cp-operation-policy`
각 슬라이스 = `api/{*.api.ts, index.ts}` + `model/{types.ts, *.fixture.ts}` + `index.ts`

### features 신규 (5)
`cp-status-transition`(hook+lib) · `cp-bulk-hide`(p39) · `cp-notice-publish`(p40) · `cp-policy-apply`(p41·p42 통합) · `cp-reward-pay`(p43)

### pages 신규 (12 슬라이스 / 23 화면)
`cp-dashboard` `cp-main-display` `cp-proposal`(2) `cp-vote`(2) `cp-discussion`(2) `cp-policy`(2) `cp-survey`(2) `cp-comment` `cp-report`(2) `cp-board`(3) `cp-activity-log`(2) `cp-reward`(2) `cp-operation-policy`

### app
- `app/router/routes.tsx` — 라우터 **최초 배선**(기존 App.tsx는 Vite 템플릿 잔존 상태였음)
- `app/router/cp-admin-shell.tsx` — GNB + 헤더 + Outlet 공통 셸
- `app/index.tsx` — 미배선 상태였던 `shared/assets/css/main.css` 로드로 교체

## 기존 자산 수정 (최소 침습, 기존 동작 보존)

| 파일 | 변경 | 이유 |
| --- | --- | --- |
| `shared/ui/table/table.tsx` | `onRowClick?`, `showRowNumber?`(기본 true) 추가 | 목록+상세패널 화면의 행 선택 계약 부재 / 화면정의서에 없는 index 열 숨김 |
| `shared/ui/table/table.css` | `.is-clickable-row`, `.is-selected-row` 추가 | 선택 행 표시 |
| `shared/ui/status/status-badge.tsx` | `color?` prop 추가 (미전달 시 기존 코드 매핑 유지) | 시민참여 상태 코드가 기존 영문 스위치에 없어 전부 neutral로 표시됨. shared 도메인-무지 유지를 위해 색을 호출부에서 주입 |
| `shared/ui/status/types/cellType.ts` | `color` 타입을 `StatusBadgeColor`로 통일 | 선언만 있고 미배선이던 필드를 `commonCell`에 연결 |
| `shared/ui/table/utils/commonCell.tsx` | status 셀에 `color` 전달 | 위와 동일 |
| `widgets/side-navigation/ui/navigation.tsx` | `items?`, `brand?` prop 추가 (미전달 시 기존 동작) | `/cp/*` 셸에서 시민참여 메뉴만 노출 + PDF의 "ASAN ADMIN / 시민참여 운영관리" 브랜드 블록 |
| `widgets/side-navigation/lib/build-navigation-items.ts` | `buildCitizenParticipationNavigationItems()` 추가 | 위와 동일 |
| `features/calendar-picker/index.ts` | 슬라이스 public API 신설 | 루트 배럴이 없어 내부 경로 직접 import를 해야 했음 |
| `shared/assets/css/main.css` | `_default.css`를 `layer(base)`로 import + `_cp-admin.css` 추가 | 아래 §"발견/해결한 문제" 1번 |

## 발견/해결한 문제 (브라우저 실검증 중)

1. **HeroUI 버튼이 배경 없이 렌더**
   HeroUI v3는 `@layer theme/base/components/utilities`로 스타일을 배포하는데, 프로젝트 전역 리셋 `_default.css`의 `:where(*){background-color:transparent}`가 **레이어 밖(unlayered)** 이라 컴포넌트 레이어를 이겼다. → `main.css`에서 리셋만 `layer(base)`로 이동. 프로젝트 자체 컴포넌트 CSS(unlayered)는 여전히 리셋보다 우선하므로 기존 의도 보존.

2. **관리자 셸이 세로 중앙 정렬되어 스크롤 시 상단이 잘림**
   전역 `body{display:flex; place-items:center; height:100%; overflow:auto}` 때문에 body 자체가 스크롤 컨테이너가 되어 GNB/헤더 sticky도 무효화. → `cp-admin-shell.css`에서 `body:has(.cp-shell)`에 한해 `display:block; height:auto; overflow:visible`로 해제(다른 화면 영향 없음).

3. **팝업이 좌상단에 붙어 렌더**
   `shared/ui/popup/popup`을 직접 import해 `index.ts`가 하던 `popup.css` 로드가 누락됨. → 전 팝업을 슬라이스 public API(`~/shared/ui/popup`)로 교체.

4. **`useStatusTransition`의 effect 내 setState** (lint `react-hooks/set-state-in-effect`)
   → effect 제거하고 렌더 중 파생 상태 조정(이전 값 추적) 방식으로 변경.

## 검증 결과

- `tsc --noEmit`: 신규 코드 오류 **0** (잔존 17건은 전부 기존 파일 — `select-users` 6, `event` DTO 5, `dao/table-rows` 2, 기타 4)
- `eslint`(신규 범위 전체): **0**
- `vite build`: 성공
- 브라우저 실검증: 23개 라우트 렌더 확인, 대시보드/제안목록/댓글/투표상세/공지폼+게시팝업/보상지급/게시판/운영정책 화면 대조 확인
