# 출석·룰렛 이벤트 관리 UI 계획

## 역할·위치

- host: Claude Code / role: UI (inject)
- worktree: `/private/tmp/asan-metaverse-admin-ui-event-api`
- branch: `feature/event-attendance-roulette-api` (시작 HEAD `b418379`, 직접 부모 `sy-main`)
- 선행 인계: `.codex/logs/sessions/event-attendance-roulette-api/handoff.md` (Logic, API·hook 완료)

## 사용자 확정 결정

1. 라우트는 `/manage`를 제외한 `/events/*`. 새 `EventAdminShell`, 메뉴는 출석 체크·룰렛.
2. 목록은 cp-news 방식(ID/코드/시작일/종료일/활성, 20건, 필터 없음, 행 클릭→상세). 등록 버튼은 목록 헤더.
3. 상세는 `상세 / 환경 설정 / 보상` 3개 탭. 탭 데이터는 모두 `GET /events/{kind}/{eventId}`.
4. 신규 등록은 기본 정보 + 보상만(config 미포함 정책). 생성 성공 시 목록 이동.
5. 등록 id(900/901 + 시작 YYYYMM)·code(`YYYY_MM_ATTENDANCE|ROULETTE`)는 자동 입력하되 수정 가능.
6. 환경 설정 키는 고정. 키 순서와 TEXT/IMAGE는 프런트 상수(아래 표), 응답 type이 있으면 응답 우선. IMAGE는 즉시 업로드→저장값 기준 configs 전체 PATCH. TEXT는 탭 저장 버튼으로 전체 PATCH. HEX 입력기 없음.
7. 출석 보상 type 상수는 DAILY/ACC 두 개. DAILY는 월간 캘린더(시작일 + day-1), ACC는 캘린더와 별도 영역.
8. objectId는 직접 입력 가능 + 아이템 이름(keyword) 검색으로 id 확인·선택. 룰렛 objectImageUrl은 사장 필드지만 DTO에서 제거하지 않음.
9. 룰렛 chance는 값 그대로 표시. 휠 조각은 chance 비율.
10. 보상 가져오기: 원본 eventId 직접 입력 → 현재 보상 전체 교체(미저장) → 저장 시 PUT. 기간 초과 day 경고.
11. 시간은 KST(+09:00)로 전송·표시.
12. UI/Logic 분담: UI는 View·표시 컴포넌트·controller props 계약·config·CSS·셸/메뉴. Logic은 controller hook, 검증, payload, 날짜 매핑, page 진입 컴포넌트와 routes 등록.

## 설정 키 type 표(사용자 승인)

| 종류 | IMAGE | TEXT |
| --- | --- | --- |
| 출석 | ACC_HOLD_ICON, ACC_CURRENCY_BACKGROUND, DAILY_HOLD_ICON, DAILY_BACKGROUND, DAILY_TODAY_ICON, DAILY_FAILED_ICON, DAILY_CHECK_BUTTON, DAILY_SUCCESS_ICON | DAILY_TOP_TITLE, DAILY_RECOVERY_CURRENCY_TYPE, DAILY_RECOVERY_CURRENCY_AMOUNT |
| 룰렛 | ROULETTE_BACK_BOARD, ROULETTE_BACKGROUND, ROULETTE_PIN, ROULETTE_START_BUTTON | ROULETTE_COLOR_V1~V3, ROULETTE_TOP_TITLE |

## 예상 변경

- `src/shared/ui/tabs/` HeroUI Tabs 어댑터
- `src/widgets/event-admin/` 공용 표시 컴포넌트(기본 정보 필드, 설정 목록, 아이템 검색 팝업, 보상 가져오기 바, 저장 바, 상세 레이아웃)
- `src/pages/event-attendance/`, `src/pages/event-roulette/` View·types·config·CSS
- `src/app/router/event-admin-shell.tsx`, `_navigation7.ts`, `_navigation2.ts` 경로, `build-navigation-items.ts`

## 검증

중앙 포맷 트리거 → `npm run lint` → `npm run build` → 이벤트 계약 테스트. 브라우저 시각 검증 없음. Git 변경은 별도 승인.
