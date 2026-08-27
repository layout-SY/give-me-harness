# Plan — 시민참여 관리자 Web UI 구현 (PDF p15~p43)

## Request Summary

- `시민참여v_4.8.pdf` **p15~p43의 관리자(ADMIN WEB) 화면 전부**를 UI로 구현한다.
- 스타일은 PDF 좌측 목업을 그대로 반영하되, **레이아웃 수치는 토큰으로 통일**한다.
- PDF 원본에서 레이아웃이 틀어진 부분은 임의 판단으로 수치를 재설정해 일정하게 맞춘다(§4 참조).
- FSD 아키텍처(`app → pages → widgets → features → entities → shared`) 준수.

## Work Type

publish-only 중심 hybrid — UI 퍼블리싱 + FSD 슬라이스 신설. API 연동은 골격만.

## Scope

- 관리자 화면 23종(목록 10 · 상세 7 · 설정/폼 4 · 팝업 5, PDF p15~p37, p39~p43).
- GNB 메뉴 13항목 배선, 라우터 최초 배선(`pages/` 신설).
- 공통 레이아웃 토큰 + shared/widgets 신규 자산 11종.
- mock fixture 기반 화면 구동.

## Out of Scope

- p38 `CP_REPORT_POPUP_MOBILE` (사용자 Mobile 화면).
- PDF 우측 "상세 정의 및 동작 · 권한·App·감사" 카드 (안내사항이며 화면 요소 아님).
- 실제 API 연동, 감사 로그 적재, 권한 정책 실제 판정 로직.
- 반응형 모바일 대응(관리자 Web은 데스크톱 기준 고정).

---

## 1. 레이아웃 표준 (PDF 수치 재설정 기준)

`shared/assets/css`에 `admin-layout.tokens.css` 추가.

```
--adm-nav-w: 240px          /* 좌측 GNB 고정폭 */
--adm-content-max: 1440px   /* 본문 최대폭 */
--adm-content-pad: 32px     /* 본문 상하좌우 패딩 */
--adm-gap: 20px             /* 블록 간 간격(전 화면 동일) */
--adm-card-pad: 24px
--adm-card-radius: 12px
--adm-card-border: 1px solid var(--color-line)
--adm-field-h: 40px         /* 입력/드롭다운/버튼 높이 통일 */
--adm-field-min-w: 200px
--adm-btn-min-w: 120px
--adm-detail-w: 360px       /* 우측 상세 패널 고정폭 */
--adm-list-min-h: 480px     /* 목록 영역 최소 높이(패널과 하단선 정렬) */
```

타이포: 페이지 타이틀 24/700, 서브설명 13/400, 섹션 타이틀 16/700, 라벨 13/500, 본문 14/400, KPI 수치 28/700.

**공통 화면 골격 (전 관리자 화면 동일)**

```
[side-navigation 240px] [ app-header ]
                        [ page-header  (제목 + 서브설명) ]
                        [ kpi-strip    (있을 때만) ]
                        [ filter-bar   (목록형만) ]
                        [ 본문         (master-detail / section grid) ]
                        [ action-bar   (있을 때만, 우측 정렬) ]
```

## 2. FSD 배치 설계

### shared/ui 신규 (도메인-무지)
`kpi-card` · `section-card` · `definition-list` · `choice-chip-group` · `ratio-bar` · `timeline-list`

### widgets 신규
`page-header` · `kpi-strip` · `filter-bar` · `master-detail-layout` · `action-bar`
기존 `side-navigation`에 시민참여 메뉴 그룹(`_navigation5`) 추가.

### entities 신규 (`cp-` 접두어, 기존 `dashboard`와 충돌 회피)
`cp-dashboard` · `cp-main-display` · `cp-proposal` · `cp-vote` · `cp-discussion` · `cp-policy` · `cp-survey` · `cp-comment` · `cp-report` · `cp-board` · `cp-notice` · `cp-activity-log` · `cp-reward` · `cp-operation-policy`

각 슬라이스: `api/{*.api.ts,*.dto.ts}` · `model/{types.ts,*.enum.ts,*.fixture.ts}` · `ui/`(도메인 표현 조각) · `index.ts`.

### features 신규 (유스케이스)
`cp-status-transition`(상태 변경 + 처리 저장) · `cp-bulk-hide`(p39) · `cp-notice-publish`(p40) · `cp-policy-apply`(p41,p42) · `cp-reward-pay`(p43)

### pages 신설 (라우트)
```
/cp/dashboard  /cp/main-display
/cp/proposals  /cp/proposals/:id
/cp/votes      /cp/votes/:id
/cp/discussions /cp/discussions/:id
/cp/policies   /cp/policies/:id
/cp/surveys    /cp/surveys/:id
/cp/comments
/cp/reports    /cp/reports/:id
/cp/boards     /cp/boards/:id   /cp/boards/notices/:id/edit
/cp/activity-logs  /cp/activity-logs/users/:userId
/cp/rewards    /cp/rewards/policy
/cp/operation-policy
```

---

## 3. 페이지별 기획

> 표기: **[PDF p]** 화면 ID / 사용 재사용 자산 → 신규 자산

### 3-1. [p15] ADM_CP_DASHBOARD_WEB — 운영 대시보드
- **구성**: KPI 4(오늘 신규/검토 필요/처리 완료/신고 접수) → 2×2 카드 그리드(최근 운영 업무·시민참여 현황·운영 알림·메인 노출 상태) → 하단 액션바(새로고침 + 바로가기 4).
- **재사용**: `widgets/side-navigation`(활성 메뉴 = 대시보드), `widgets/app-header`, `shared/ui/button`, `shared/ui/status`(메인 노출 "정상 반영" positive 칩), `shared/lib/hooks/use-api`.
- **신규**: `page-header`, `kpi-strip`(4열), `section-card`×4, `action-bar`.
- **레이아웃 재설정**: PDF의 버튼 폭 불균일 → 전 버튼 `height 40 / min-width 120`, 새로고침만 secondary로 좌측 분리, 바로가기 4개 primary 우측 그룹(gap 12).
- **비고**: KPI 수치 색상은 PDF대로 파랑/주황/초록/빨강 → `kpi-card`의 `tone` prop(`info|warning|positive|danger`).

### 3-2. [p16] ADM_CP_MAIN_DISPLAY_WEB — 메인 노출 관리
- **구성**: KPI 3(상단 배너/주요 콘텐츠/메인 공지) → 2×2 카드(상단 배너 목록·주요 콘텐츠·공지 노출·Mobile 메인 미리보기) → 선택 항목 노출 설정(노출/비노출 칩 + 순서) → 액션바(저장 / 저장 및 반영).
- **재사용**: `shared/ui/toggle-switch`(노출 여부 대안), `shared/ui/button`, `shared/ui/status`.
- **신규**: `kpi-strip`(3열 균등), `section-card`, `choice-chip-group`(노출/비노출), `action-bar`.
- **레이아웃 재설정**: KPI 3개를 4열 기준폭으로 그려 우측이 비어 있음 → `repeat(auto-fit, minmax(0,1fr))` 3등분.
- **비고**: 미리보기 카드는 읽기 전용 프리뷰 박스(연한 배경 + 요약 문자열).

### 3-3. [p17] ADM_CP_PROPOSAL_LIST_WEB — 시민제안 목록/처리
- **구성**: KPI 4(전체/접수/검토중/채택) → 필터(상태·작성자·제목 + 검색/초기화) → master-detail(좌: 제안 목록 테이블 / 우: 선택 제안 상세 + 상태 변경 + 담당부서 + 처리 저장).
- **재사용**: `shared/ui/table`(컬럼: ID `text`, 상태 `status`, 제목 `text`, 작성자 `author`, 등록일 `date`), `shared/ui/dropdown`(상태·담당부서), `shared/ui/text-input`(작성자·제목), `shared/ui/button`, `shared/ui/status`, `shared/ui/no-results`·`pagination`(table 내장).
- **신규**: `filter-bar`, `master-detail-layout`, `definition-list`, `section-card`, `features/cp-status-transition`.
- **레이아웃 재설정**: 필터 3필드 + 버튼 2개를 `auto-fit(minmax(200px,1fr))` + 우측 고정 버튼그룹으로 정렬. 우측 패널 `360px` sticky, 목록 `min-height 480`으로 하단선 정렬.
- **비고**: 행 선택 시 우측 패널 갱신 = `getRowClassName`으로 선택 행 하이라이트. 이 화면의 상태 전이는 `접수→검토중→채택/반려`.

### 3-4. [p18] ADM_CP_PROPOSAL_DETAIL_WEB — 시민제안 상세처리
- **구성**: 기본 정보 → 제안 내용(읽기 전용) → 2열(처리 상태[상태·담당부서] / 처리 의견) → 처리 이력 → 액션바(목록으로 / 처리 저장).
- **재사용**: `shared/ui/text-area`(처리 의견), `shared/ui/dropdown`, `shared/ui/button`.
- **신규**: `section-card`, `definition-list`(기본 정보 인라인 4항목), `timeline-list`(처리 이력), `action-bar`.
- **레이아웃 재설정**: 2열 섹션은 전 상세화면 공통으로 `1fr 1fr / gap 20`. 본문 카드 `min-height 200`.
- **비고**: 본문은 편집 불가(정의서 "원문 임의 수정 금지") → `readOnly` 텍스트 블록으로 표현.

### 3-5. [p19] ADM_CP_VOTE_LIST_WEB — 시민투표 목록/처리
- **구성**: KPI 4(전체/투표중/마감예정/완료) → 필터(상태·작성자·제목·기간) → master-detail(우: 상세 + 결과 공개 + 상태 변경 + 결과 공개 기준 + 처리 저장).
- **재사용**: `shared/ui/table`, `features/calendar-picker/DateRangeField`(기간 필터), `shared/ui/dropdown`, `shared/ui/status`, `shared/ui/button`.
- **신규**: `filter-bar`(4필드), `master-detail-layout`, `definition-list`.
- **레이아웃 재설정**: PDF에서 작성자/기간 컬럼이 우측으로 몰려 붙음 → 컬럼 비율 `ID 90 / 상태 100 / 제목 1fr / 작성자 120 / 기간 160`.
- **비고**: "투표 종료 후 공개"는 조작 불가 배지로 표기(조기 공개 금지 정책).

### 3-6. [p20] ADM_CP_VOTE_DETAIL_WEB — 시민투표 상세처리
- **구성**: 기본 정보 → 투표 안건(기간·선택지) → 2열(운영 상태[상태·종료일·결과 공개] / 결과 현황[투표수 + 찬반 비율 바]) → 댓글·의견 운영 → 처리 이력 → 액션바.
- **재사용**: `shared/ui/date-range-picker`(종료일), `shared/ui/dropdown`, `shared/ui/button`.
- **신규**: `ratio-bar`(찬성 89% / 반대 11%), `section-card`, `timeline-list`, `action-bar`.
- **레이아웃 재설정**: PDF 하단 버튼이 라벨 없이 잘려 있음(08/09 빈 박스) → `목록으로`(secondary) / `처리 저장`(primary) 표준 액션바로 복원.
- **비고**: 댓글 목록은 읽기 전용 요약(신고/숨김 처리는 댓글 관리 화면으로 이동 링크).

### 3-7. [p21] ADM_CP_DISCUSS_LIST_WEB — 시민토론 목록/처리
- p19와 **동일 패턴**. KPI(전체 토론/토론중/종료/의견 합계), 컬럼에 `의견 수` 추가.
- **재사용**: p19와 동일 세트.
- **레이아웃 재설정**: PDF 목록 컬럼 헤더 간격이 불규칙 → `ID 90 / 상태 90 / 제목 1fr / 작성자 110 / 의견 70 / 기간 160`.

### 3-8. [p22] ADM_CP_DISCUSS_DETAIL_WEB — 시민토론 상세처리
- p20과 동일 골격. 차이: 결과 현황이 **3분할 비율**(찬성/반대/중립) → `ratio-bar`에 `segments[]` 지원.

### 3-9. [p23] ADM_CP_POLICY_LIST_WEB — 정책반영 목록/처리
- **구성**: KPI 4(전체/반영완료/검토중/설치·시행 예정) → 필터(상태·담당부서·제목·처리단계) → master-detail(우: 상세 + 반영 내용 + 처리 단계 + 처리 저장).
- **재사용**: `shared/ui/table`(현재 단계 컬럼은 `category` 셀), `shared/ui/text-area`(반영 내용), `shared/ui/dropdown`.
- **레이아웃 재설정**: PDF에서 우측 패널이 목록보다 짧고 카드 경계가 어긋남 → 패널 sticky + 목록/패널 상단선 정렬.

### 3-10. [p24] ADM_CP_POLICY_DETAIL_WEB — 정책반영 상세처리
- **구성**: 기본 정보 → 제안 내용 → 처리 결과(날짜별 경과) → 2열(담당부서 / 반영 내용) → 댓글·의견 → 처리 이력 → 액션바.
- **신규**: `timeline-list`를 처리 결과·처리 이력 2회 사용.
- **레이아웃 재설정**: PDF에서 "처리 결과" 마지막 줄이 아래 카드에 겹침 → 카드 하단 패딩 24 확보, 겹침 제거.

### 3-11. [p25] ADM_CP_SURVEY_LIST_WEB — 설문조사 목록/처리
- **구성**: KPI 4(전체/진행중/예정/마감) → 필터(상태·제목·기간) → master-detail(우: 상세 + 운영상태 + 외부 URL + 처리 저장).
- **재사용**: `shared/ui/text-input`(외부 URL), `DateRangeField`, `table`.
- **레이아웃 재설정**: 목록 6행으로 패널보다 길어 하단선 불일치 → 목록 `min-height` 고정 + 패널 sticky.

### 3-12. [p26] ADM_CP_SURVEY_DETAIL_WEB — 설문조사 상세처리
- **구성**: 기본 정보 → 설문 정보(기간·대상·소요시간·문항수 2×2) → 설문 소개 → 2열(참여 링크 / 운영 상태) → 노출 설정 → 처리 이력 → 액션바.
- **신규**: `definition-list`의 `columns={2}` 변형으로 설문 정보 2×2 정렬.
- **레이아웃 재설정**: PDF 설문 정보의 항목 간격이 제각각(대상/문항수 열 어긋남) → 2열 그리드 라벨폭 96px 고정.

### 3-13. [p27] ADM_CP_COMMENT_LIST_WEB — 댓글 통합 관리
- **구성**: KPI 5(전체 댓글/신고 접수/가입정보 의심/숨김/오늘 신규) → 필터(댓글 유형·작성자·원문 제목·댓글 ID + 검색/초기화) → master-detail(좌: 유형 탭[전체·게시글·정책제안·투표·토론] + 목록 / 우: 상세 + 댓글 내용 + 처리 상태 + 처리 저장).
- **재사용**: `shared/ui/search-state-bar`의 **탭 UI 패턴 차용**(단 필터 구조가 달라 컴포넌트 자체는 신규 `filter-bar` + `choice-chip-group` 조합), `table`, `status`.
- **레이아웃 재설정**: PDF에서 `처리 상태` 칩이 목록 바깥 하단에 떠 있음 → **우측 상세 패널 내부로 이동**(조작 대상이 선택 행이므로). KPI 5개는 5등분 균등.

### 3-14. [p28] ADM_CP_REPORT_LIST_WEB — 신고 목록/처리
- **구성**: KPI 4(전체 신고/접수/검토중/처리완료) → 필터(상태·신고 유형·대상 유형·신고자 + 검색/초기화) → master-detail(우: 상세 + 처리 메모 + 처리 저장).
- **재사용**: `table`, `text-area`(처리 메모), `dropdown`, `status`.
- **레이아웃 재설정**: `처리 상태` 칩 그룹을 패널 내부로 이동(p27과 동일 원칙).

### 3-15. [p29] ADM_CP_REPORT_DETAIL_WEB — 신고 상세처리
- **구성**: 기본 정보 → 신고 대상 콘텐츠 → 신고 사유(읽기 전용) → 2열(처리 상태 칩 / 콘텐츠 노출 상태 칩 + 주석) → 처리 의견 → 처리 이력 → 액션바.
- **신규**: `choice-chip-group` 2개(3지/2지 선택), `section-card`, `timeline-list`.
- **비고**: "신고 접수만으로 자동 숨김하지 않음" 주석을 칩 하단 캡션으로 고정 노출.

### 3-16. [p30] ADM_CP_BOARD_LIST_WEB — 게시판 관리
- **구성**: KPI 4(전체 게시글/게시중/숨김/공지) → 필터(상태·유형·작성자·제목) → master-detail(우: 선택 게시글 상세) → 하단 2열(노출 상태 / 공지 구분) + 처리 저장.
- **재사용**: `table`(유형 컬럼 `category`), `status`, `dropdown`, `button`.
- **레이아웃 재설정**: PDF에서 목록 `등록일` 컬럼이 우측 패널에 가려짐 → 목록/패널 2단 grid로 완전 분리하고 컬럼 폭 재산정. 노출 상태·공지 구분 칩은 패널 하단으로 통합.
- **비고**: 다중 선택 → p39 일괄 숨김 팝업 진입점(`features/cp-bulk-hide`).

### 3-17. [p31] ADM_CP_BOARD_DETAIL_WEB — 게시글 상세처리
- **구성**: 기본 정보 → 게시글 내용(제목 + 본문) → 2열(댓글 현황 / 신고 현황) → 2열(노출 상태 / 공지 구분) → 처리 이력 → 액션바.
- **재사용/신규**: `section-card`, `definition-list`, `choice-chip-group`×2, `timeline-list`, `action-bar`.

### 3-18. [p32] ADM_CP_ACTIVITY_LOG_WEB — 활동 로그
- **구성**: KPI 4(오늘 활동/게시·제안/투표·토론/관리처리) → 필터(활동유형·대상유형·사용자·기간 + 조회) → master-detail(좌: 로그 테이블 / 우: 선택 로그 상세) → 하단(활동 유형 칩 · 대상 정보 · 상세 보기 버튼).
- **재사용**: `table`(결과 컬럼 `status`), `DateRangeField`, `dropdown`.
- **레이아웃 재설정**: 하단 칩/대상정보/버튼 3분할을 패널 내부(칩·대상정보) + 액션바(상세 보기)로 재배치.
- **비고**: `상세 보기` → p33 이동.

### 3-19. [p33] ADM_CP_USER_ACTIVITY_DETAIL_WEB — 사용자 활동 상세
- **구성**: 사용자 기본정보 → 활동 요약 KPI 4(게시/제안·투표/토론·신고·관리처리 영향) → 최근 활동 테이블 → 2열(참여 상태 / 관련 대상) → 조회 이력 → 액션바(목록으로만).
- **재사용**: `table`(읽기 전용), `status`.
- **비고**: 전 영역 읽기 전용. 저장 버튼 없음.

### 3-20. [p34] ADM_CP_BOARD_NOTICE_FORM_WEB — 공지 등록/수정
- **구성**: 기본 정보 → 공지 제목(input) → 노출 기간(시작~종료) → 공지 내용(textarea) → 2열(게시 상태 칩 / 메인 노출 칩) → Mobile 미리보기 → 액션바(목록으로 / 임시 저장 / 공지 게시).
- **재사용**: `shared/ui/text-input`, `text-area`, `features/calendar-picker/DateRangeField`, `shared/lib/validation`(zod 스키마 — 제목 필수·기간 유효).
- **신규**: `choice-chip-group`×2, `section-card`.
- **레이아웃 재설정**: 노출 기간 두 필드 폭 불일치 → `1fr ~ 1fr` 동일폭 + 구분자 `~` 고정 24px.
- **비고**: `공지 게시` 클릭 시 p40 팝업 호출.

### 3-21. [p35] ADM_CP_POLICY_SETTING_WEB — 시민참여 운영 정책 설정
- **구성**: 상태 요약 2(현재 상태/마지막 적용) → 2×2(작성 정책 / 댓글·신고 정책 / 노출 기본값 / 변경 사유) → 적용 예정 정책 미리보기 → 액션바(편집 저장 / 정책 적용).
- **재사용**: `toggle-switch` 또는 `choice-chip-group`(허용/차단), `text-area`(변경 사유), `button`.
- **레이아웃 재설정**: 상태 요약 2개 카드가 좌측에만 몰려 있음 → KPI strip 2열 균등(단 전체폭의 절반까지만, 나머지 여백 유지).
- **비고**: `정책 적용` → p41 팝업.

### 3-22. [p36] ADM_CP_REWARD_POLICY_WEB — 보상/포인트 정책 설정
- **구성**: 상태 요약 2(정책 상태/기준일) → 참여 보상 기준(2×2 항목: 제안·투표·토론·설문) → 2열(지급 제한 기준 / 적용 범위) → 2열(변경 사유 / 정책 미리보기) → 액션바(편집 저장 / 정책 적용).
- **재사용**: `text-input`(포인트 수치), `text-area`, `button`.
- **비고**: 수치는 "협의 확정값" 전제 → placeholder만 두고 임의 기본값 금지. `정책 적용` → p42 팝업.

### 3-23. [p37] ADM_CP_REWARD_LIST_WEB — 보상/포인트 지급 관리
- **구성**: KPI 3(지급대기/지급완료/대기 포인트) → 필터(상태·보상유형·사용자·기간 + 조회) → master-detail(좌: 지급 대상 목록 / 우: 선택 대상 상세) → 하단(지급 상태 칩 · 지급 근거 · 보상 지급 버튼).
- **재사용**: `table`(상태 `status`), `DateRangeField`, `dropdown`.
- **레이아웃 재설정**: 하단 3분할을 패널 내부(칩·근거) + 액션바(보상 지급)로 재배치. KPI 3열 균등.
- **비고**: `보상 지급` → p43 팝업.

### 3-24. 팝업 5종 [p39·p40·p41·p42·p43]
공통 골격: `shared/ui/popup` + 제목(20/700) + 안내문(13) + 본문 카드 n개 + 하단 2버튼(`취소` secondary / 실행 primary, 각 `min-width 140`, gap 12). 폭은 **540px 고정**으로 통일(PDF는 팝업마다 폭이 달라 재설정).

| PDF | 팝업 | 본문 구성 | 소속 feature |
| --- | --- | --- | --- |
| p39 | 게시글 일괄 숨김 | 처리 대상 / 변경 상태 2열(현재→변경) / 처리 사유 / 사용자 안내 문구 / 내부 메모 | `cp-bulk-hide` |
| p40 | 공지 게시 확인 | 공지 대상(ID·제목·기간) / 메인 노출 칩 / 확인 문구 | `cp-notice-publish` |
| p41 | 운영 정책 적용 확인 | 변경 요약 / 적용 사유 / 확인 | `cp-policy-apply` |
| p42 | 보상 정책 적용 확인 | 정책 요약 / 적용 범위 / 확인 | `cp-policy-apply` |
| p43 | 보상 지급 확인 | 지급 대상 / 포인트 기준 / 지급 근거 | `cp-reward-pay` |

> p39는 독립 팝업 화면, p40~p43은 부모 화면 위 오버레이로 그려져 있음 → 모두 `popup` 오버레이로 통일 구현.

---

## 4. Sections (실행 단계 — 한 번에 한 섹션)

| # | 섹션 | 산출물 | 담당 |
| --- | --- | --- | --- |
| S0 | 공통 기반 | 레이아웃 토큰 CSS, shared/ui 6종, widgets 5종, GNB 메뉴 추가, 라우터 배선 | publisher → watcher |
| S1 | 대시보드·메인 노출 (p15·p16) | pages 2, entities 2 | publisher → generator → watcher |
| S2 | 제안·투표·토론·정책반영 (p17~p24) | pages 8, entities 4, feature 1 | publisher → generator → watcher |
| S3 | 설문·댓글·신고 (p25~p29) | pages 5, entities 3 | publisher → generator → watcher |
| S4 | 게시판·공지·활동로그 (p30~p34) | pages 5, entities 3 | publisher → generator → watcher |
| S5 | 정책·보상 (p35~p37) | pages 3, entities 2 | publisher → generator → watcher |
| S6 | 팝업 5종 (p39~p43) | features 4 | generator → watcher |
| S7 | 정합성 검수 | `yarn lint && tsc --noEmit`, 레이아웃 수치 대조표 | watcher → evaluator |

## 5. Required Agents

`planner`(본 문서) → `publisher`(레이아웃/props 계약) → `generator`(구현) → `watcher`(섹션별 게이트) → `evaluator`(S7 후 장기 개선)

## 6. Required Skills

- `skills/reference/components/*` — table · search-state-bar · popup · dropdown · text-input · text-area · calendar-picker · navigation
- `skills/policy/*` — 코딩 컨벤션, FSD 경계, policy-validation(zod+RHF)
- `src/ARCHITECTURE.md` — 세그먼트 규칙(훅은 `hook/`, 순수함수는 `lib/`)

## 7. Risks / Assumptions

- **가정 A**: 백엔드 스펙 미확정 → 화면은 mock fixture로 구동, `*.api.ts`는 싱글턴 골격만.
- **가정 B**: GNB는 PDF 중 항목이 가장 많은 p36 기준(13항목)을 정본으로 채택.
- **가정 C**: PDF 우측 정의 카드는 화면 요소가 아니므로 구현 제외.
- **리스크 1**: `pages/`가 비어 있어 라우터가 미배선 상태(App.tsx = Vite 템플릿). S0에서 최초 배선하므로 기존 화면 회귀 위험은 없으나 App 진입 구조가 바뀐다.
- **리스크 2**: `tsconfig`의 `erasableSyntaxOnly`로 `enum` 사용 시 컴파일 에러(기존 16건). 신규 enum은 `as const` 객체 + union 타입으로 작성.
- **리스크 3**: `status-badge`의 기본 색 매핑이 영문 코드 스위치 → 시민참여 상태 코드(`REVIEWING`, `ADOPTED`, `VOTING`…) 추가 매핑 필요. shared 도메인-무지 원칙 유지를 위해 **호출부에서 color를 명시 주입**한다.
- **리스크 4**: 화면 23종 일괄 구현은 컨텍스트 과부하 → 섹션별 세션 분리 권장(S2, S4는 별도 세션).

## Approval Request

이 계획대로 진행할까요, 아니면 조정할 부분이 있나요?
