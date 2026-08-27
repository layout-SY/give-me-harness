# Exploration — 시민참여 관리자 Web UI (PDF p15~p43)

## 1. 원본 자료

- `~/Downloads/시민참여v_4.8.pdf` (총 43p). p15부터 관리자(ADMIN WEB) 화면정의서.
- 각 페이지 구조: **좌측 = 화면 목업(Red Marker 01~09)**, **우측 = 상세 정의/동작/권한·App·감사 카드**.
- 우측 카드는 "안내사항"이므로 UI 구현 대상 아님. 좌측 목업만 화면으로 옮긴다.

## 2. 대상 화면 인벤토리 (관리자 23종)

| PDF | 화면 ID | 화면명 | 유형 |
| --- | --- | --- | --- |
| p15 | ADM_CP_DASHBOARD_WEB | 운영 대시보드 | 대시보드 |
| p16 | ADM_CP_MAIN_DISPLAY_WEB | 메인 노출 관리 | 설정형 |
| p17 | ADM_CP_PROPOSAL_LIST_WEB | 시민제안 목록/처리 | 목록+상세패널 |
| p18 | ADM_CP_PROPOSAL_DETAIL_WEB | 시민제안 상세처리 | 상세 |
| p19 | ADM_CP_VOTE_LIST_WEB | 시민투표 목록/처리 | 목록+상세패널 |
| p20 | ADM_CP_VOTE_DETAIL_WEB | 시민투표 상세처리 | 상세 |
| p21 | ADM_CP_DISCUSS_LIST_WEB | 시민토론 목록/처리 | 목록+상세패널 |
| p22 | ADM_CP_DISCUSS_DETAIL_WEB | 시민토론 상세처리 | 상세 |
| p23 | ADM_CP_POLICY_LIST_WEB | 정책반영 목록/처리 | 목록+상세패널 |
| p24 | ADM_CP_POLICY_DETAIL_WEB | 정책반영 상세처리 | 상세 |
| p25 | ADM_CP_SURVEY_LIST_WEB | 설문조사 목록/처리 | 목록+상세패널 |
| p26 | ADM_CP_SURVEY_DETAIL_WEB | 설문조사 상세처리 | 상세 |
| p27 | ADM_CP_COMMENT_LIST_WEB | 댓글 통합 관리 | 목록+상세패널 |
| p28 | ADM_CP_REPORT_LIST_WEB | 신고 목록/처리 | 목록+상세패널 |
| p29 | ADM_CP_REPORT_DETAIL_WEB | 신고 상세처리 | 상세 |
| p30 | ADM_CP_BOARD_LIST_WEB | 게시판 관리 | 목록+상세패널 |
| p31 | ADM_CP_BOARD_DETAIL_WEB | 게시글 상세처리 | 상세 |
| p32 | ADM_CP_ACTIVITY_LOG_WEB | 활동 로그 | 목록+상세패널 |
| p33 | ADM_CP_USER_ACTIVITY_DETAIL_WEB | 사용자 활동 상세 | 상세(읽기전용) |
| p34 | ADM_CP_BOARD_NOTICE_FORM_WEB | 공지 등록/수정 | 폼 |
| p35 | ADM_CP_POLICY_SETTING_WEB | 시민참여 운영 정책 설정 | 설정형 |
| p36 | ADM_CP_REWARD_POLICY_WEB | 보상/포인트 정책 설정 | 설정형 |
| p37 | ADM_CP_REWARD_LIST_WEB | 보상/포인트 지급 관리 | 목록+상세패널 |
| p39 | ADM_CP_BOARD_BULK_HIDE_POPUP | 게시글 일괄 숨김 처리 팝업 | 팝업 |
| p40 | ADM_CP_BOARD_NOTICE_PUBLISH_POPUP | 공지 게시 확인 팝업 | 팝업 |
| p41 | ADM_CP_POLICY_SETTING_APPLY_POPUP | 운영 정책 적용 확인 팝업 | 팝업 |
| p42 | ADM_CP_REWARD_POLICY_APPLY_POPUP | 보상 정책 적용 확인 팝업 | 팝업 |
| p43 | ADM_CP_REWARD_PAY_CONFIRM_POPUP | 보상 지급 확인 팝업 | 팝업 |

> p38(CP_REPORT_POPUP_MOBILE)은 **사용자 Mobile 화면**이므로 이번 관리자 Web 범위에서 제외.

## 3. GNB(좌측 메뉴) 구성 — PDF 내 불일치 발견

PDF 페이지마다 좌측 메뉴 항목이 다르게 그려져 있다.

- p15/p16/p34/p35/p36/p37 등: `대시보드 · 메인 노출 관리 · 게시판 관리 · 댓글 관리 · 제안 관리 · 투표 관리 · 토론 관리 · 정책반영 관리 · 설문조사 관리 · 신고 관리 · (보상/포인트 관리) · (운영 정책 설정) · 활동 로그`
- p17~p33: **"메인 노출 관리"가 누락**되어 있고, `보상/포인트 관리`·`운영 정책 설정`도 없음.

→ **판단**: 가장 항목이 많은 p36/p42 기준을 정본으로 채택해 전 화면 동일 메뉴를 노출한다(13개 항목).

## 4. 재사용 가능 자산 (현행 코드베이스 실측)

### shared/ui (24종 존재)
| 자산 | 실제 계약 | 이번 활용 |
| --- | --- | --- |
| `table/table.tsx` | `TableColumnDef<TRow>` 기반. `kind: accessor(text·date·author·status·category·numbering_text) / action(open_detail) / custom`. `page/itemCount/pageSize/pageCount/handler`로 페이지네이션 내장, `getRowClassName` 제공 | 전 목록 화면. 선택 행 하이라이트는 `getRowClassName`으로 처리 |
| `status/status-badge.tsx` | `StatusBadgeColor = positive·neutral·warning·danger·info·deleted`. 기본 매핑은 영문 코드 스위치, 색상 override 가능 | 상태 칩 전부(검토중/채택/투표중/숨김/지급대기…) |
| `search-state-bar` | 탭 + 키워드 + searchBy 드롭다운 + 생성 버튼. **필터 4열 구조는 미지원** | 형태 불일치 → 신규 `admin-filter-bar` 위젯 필요 |
| `text-input`, `text-area`, `dropdown`, `toggle-switch`, `button`, `icon-button` | HeroUI 어댑터 | 필터/폼/액션 |
| `date-range-picker`, `features/calendar-picker/DateRangeField` | 문자열 `DateRange` 계약의 얇은 필드 | 기간 필터(투표/토론/설문/로그/보상), 공지 노출기간 |
| `popup` + `dialog`(zustand 전역) | `popup`: open/close/children 자유 구성. `dialog`: 전역 alert/confirm | 팝업 5종은 `popup` 기반, 단순 확인은 `useDialog` |
| `pagination`, `no-results`, `loading`, `fade-in` | table 내부에서 이미 조립 | 그대로 |
| `side-modal` | HeroUI Drawer 우측 | 이번 화면은 인라인 상세패널이라 미사용 |
| `author-badge`, `category-badge` | 테이블 셀 타입 | 작성자/유형 컬럼 |

### widgets / app
- `widgets/side-navigation`: `NavigationItem{icon,label,path,sublinks}` + `buildNavigationItems(roles)`로 `_navigation1~4` 조립. **여기에 시민참여 메뉴 그룹 추가만 하면 GNB 재사용 완료.**
- `widgets/app-header`: 상단바 그대로 사용.
- `app/router/private-route.tsx`, `role-based-route.tsx`: 가드 준비됨. **단 `pages/`가 비어 있어 라우터 미배선(App.tsx는 Vite 템플릿 잔존)** → 이번 작업에서 최초 배선.

### shared/lib
- `hooks/use-api.tsx`(도메인-무지 실행기), `utils/date.util.ts`, `pub-sub`, `validation`(zod 스켈레톤).

## 5. 부재 자산 (신규 필요)

| 신규 | 레이어 | 이유 |
| --- | --- | --- |
| `kpi-card` | shared/ui | 라벨+수치 카드. 22개 화면 중 12개가 사용하는 최다 반복 블록 |
| `section-card` | shared/ui | "기본 정보/처리 이력" 등 제목+본문 카드. 전 상세화면 공통 |
| `definition-list` | shared/ui | `라벨 값` 나열(제안 ID·상태·작성자·등록일). 상세화면 전부 |
| `choice-chip-group` | shared/ui | `정상/숨김`, `접수/검토중/처리완료` 등 단일선택 칩. 8개 화면 |
| `ratio-bar` | shared/ui | 찬성/반대/중립 비율 바 (p20·p22) |
| `timeline-list` | shared/ui | 처리 이력 시간순 목록 |
| `page-header` | widgets | 제목 + 서브설명 (전 화면 동일 규격) |
| `kpi-strip` | widgets | KPI 카드 n개 균등 배치 |
| `filter-bar` | widgets | 라벨+필드 n열 + 검색/초기화 |
| `master-detail-layout` | widgets | 좌측 목록 + 우측 상세패널 골격 (10개 화면) |
| `action-bar` | widgets | 하단 우측 정렬 액션 버튼 그룹 |

## 6. 레이아웃 불일치 (PDF 원본) → 재설정 대상

| PDF | 원본 문제 | 재설정 |
| --- | --- | --- |
| p15 | 하단 새로고침/바로가기 버튼 폭 제각각 | 전 버튼 `height 40 / min-width 120`, 좌측 secondary·우측 primary 그룹 |
| p16 | KPI 3개인데 4열 기준 폭 유지로 우측 여백 발생 | KPI strip `repeat(auto-fit, minmax(0,1fr))` 균등 분할 |
| p17·p19·p21·p23·p25·p28·p32·p37 | 필터 필드 3~4개로 제각각, 검색 버튼 위치/초기화 유무 불일치 | 필드 `minmax(200px,1fr)` auto-fit + 버튼 그룹 고정폭 우측 |
| p19 | 목록 "작성자/기간" 컬럼이 우측으로 몰려 붙음 | 컬럼 폭 비율 고정 |
| p20 | 하단 액션 버튼이 라벨 없이 잘려 있음(08/09) | `목록으로`/`처리 저장` 표준 액션바로 복원 |
| p23 | 우측 상세 패널 높이가 목록과 어긋남 | 패널 `position: sticky; top` + 목록과 동일 상단선 |
| p25 | 목록이 6행이라 상세 패널과 하단선 불일치 | 목록 영역 `min-height` 고정, 패널 sticky |
| p27·p28·p30·p32·p37 | `처리 상태`/`노출 상태`/`활동 유형` 칩이 목록 **바깥 하단**에 유리 배치됨 | 해당 칩 그룹을 **우측 상세 패널 내부**로 이동(실제 조작 대상이 선택 행이므로) |
| p30 | 목록 우측 `등록일` 컬럼이 상세 패널에 가려짐 | 목록/패널 2단 grid로 분리, 컬럼 폭 재산정 |
| p37 | `지급 상태`/`지급 근거`/`보상 지급` 버튼이 하단에 3분할 | 상태·근거는 패널로, 지급 버튼은 액션바로 |

## 7. 데이터/API 전제

- 백엔드 스펙 미확정. 각 entity는 `api/*.dto.ts` + `api/*.api.ts` **싱글턴 골격만** 만들고, 화면은 mock fixture(`model/*.fixture.ts`)로 구동한다.
- 기존 `entities/dashboard`와 이름 충돌 방지를 위해 시민참여 도메인은 `cp-` 접두어를 쓴다.
