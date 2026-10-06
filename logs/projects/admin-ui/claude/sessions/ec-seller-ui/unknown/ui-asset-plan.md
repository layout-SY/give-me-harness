# UI 자산 선정 계획

## 작업과 조사 근거

- 요구사항·UI 구현 범위: Figma `해커톤, EC` 판매자 섹션 19개 프레임 → `/ec/*` 화이트 모드 UI, 공용 사이드바 개편, 증감 뱃지·상태 탭 공용화. 상세는 `../plan.md`.
- 대상 project·branch·worktree·확인한 HEAD: `asan-metaverse-admin-ui`, `sy-main`, `bc579b3`, 기본 worktree(작업 위치는 Q5).
- 현재 스택·설치 버전: `package.json` — `@heroui/react ^3.2.3`, `lucide-react ^1.25.0`(lock 1.25.0), `react-router-dom ^7.18.1`, `tailwindcss ^4.3.3`, `babel-plugin-react-compiler`.
- 조사한 공용 경로: `src/shared/ui/*`(button, icon-button, text-input, text-area, dropdown, date-range-picker, pagination, table, tabs, choice-chip-group, search-state-bar, kpi-card, section-card, status-badge, toggle-switch, modal, popup, image-upload, definition-list, no-results), `src/widgets/admin-page-layout/*`(PageHeader, KpiStrip, FilterBar, ActionBar), `src/widgets/side-navigation/*`, `src/app/router/*-shell.tsx`.
- 인접 구현: `src/pages/inquiry/ui/inquiry-list-view.tsx`(PageHeader+KpiStrip+FilterBar+SectionCard+Table), `src/pages/item/*`, `src/features/meeting/ui/*`(lucide-react 직접 import 사용처).
- 구매자 EC UI 자산: admin-ui 전 브랜치·`src`에서 확인되지 않음 → 재사용 대상 없음(다른 프로젝트라면 세션 경계 밖).
- 적용한 디자인: `src/shared/assets/css/_variables.css` 토큰(`--clr-*`, `--cp-*`), React Compiler 사용 중이므로 수동 memo 추가 없음.

## 구현 항목별 선택

| 요구사항·UI 구현 항목 | 선택 | 자산·경로 | 선택·제외 이유와 조사 근거 | 계약·예상 변경·검증 | 결정 상태 |
| --- | --- | --- | --- | --- | --- |
| 공용 사이드바(흰 배경·구분선·부모 토글·자식 목록·닫기) | 기존 공용 자산 재사용(수정) | `widgets/side-navigation/ui/navigation.tsx`, `navigation.css`, `navigation.responsive.css`, `_variables.css`의 `--clr-nav-*` | 사용자 지시로 공용 사이드바 자체 개편. 부모 `Link` 제거 → `button[aria-expanded]` 토글, 활성 경로의 부모는 초기 펼침 | props 추가: `footer?: ReactNode`. `NavigationItem.path`는 자식 없는 항목(대시보드)만 이동에 사용. 4개 기존 셸 회귀 확인(lint/build) | 요청으로 확정 |
| 사이드바·콘텐츠 영역 분리 | 기존 자산 수정 | `app/router/cp-admin-shell.css` | 사이드바 흰 배경 + `border-right`, 본문 `--clr-background` 회색 | 셸 CSS만 변경 | 요청으로 확정 |
| 사이드바 아이콘(대시보드·상품·주문·정산·설정·문의) | 외부 라이브러리 사용(기설치) | `lucide-react@1.25.0` → `shared/assets/icons/ec-icons.tsx`에서 필요한 아이콘만 re-export | 기존 svg 세트에 상자·영수증·지폐 아이콘 부재. lucide는 이미 meeting에서 사용 | 기능 코드는 `ec-icons`에서만 import | 제안 |
| EC 셸(사이드바형) | 기존 공용 자산 재사용 | `Navigation`, `Header`, `cp-shell` 클래스 | 기존 셸 구조 동일 | `app/router/ec-seller-shell.tsx` 신규 | 제안 |
| 입점 신청·승인 대기 단독 레이아웃 | 기존 공용 자산 재사용 | `Header` + 신규 `ec-apply-shell.tsx` | 프레임에 사이드바 없음(승인 전 판매자) | 헤더 + 중앙 컨텐츠 | 제안 |
| 페이지 헤더(제목·설명·액션) | 기존 공용 자산 재사용 | `widgets/admin-page-layout` `PageHeader` | 전 관리자 화면 공통 | 변경 없음 | 제안 |
| KPI 카드(아이콘+라벨+값, 상품 목록·매출 현황·누적) | 기존 공용 자산 재사용(확장) | `shared/ui/kpi-card` | 현재 라벨/값/캡션만 존재. `icon?`, `trend?`(TrendBadge) 슬롯 추가 | 선택 prop 추가, 기존 사용처 동작 불변 | 제안 |
| 증감 추이 뱃지(12.5% / 5.2% / -2.1%) | 공용 자산 신규 작성 | `shared/ui/trend-badge` | 사용자 지시 "별도 공용 뱃지". 기존 StatusBadge는 상태 코드 전용 | `{ value: number; unit?: "%" \| "%p"; direction?: "up"\|"down"\|"flat" }` — 부호로 방향 자동, 색 success/danger/neutral | 요청으로 확정 |
| 상태 탭 바(전체 120 / 주문 접수 5 …) | 공용 자산 신규 작성 | `shared/ui/filter-tabs` | 기존 `SearchStateBar`(미사용, 검색 결합)·`Tabs`(패널 결합, HeroUI)·`ChoiceChipGroup`(상태 선택용)은 "탭+개수, 패널 없음, 테이블 카드 상단" 요구 불충족. 사용자 지시로 신규 방식 채택 | `{ items: {key,label,count?}[]; value; onChange(key); variant: "underline" \| "pill"; ariaLabel }`, `role="tablist"` 키보드 이동 | 요청으로 확정 |
| 매출 분석 기간 필터(오늘/7일/1개월/직접입력) | 공용 자산 신규 작성(위 FilterTabs `pill`) | `shared/ui/filter-tabs` | 사용자 지시 "이 공용 UI를 적용, radius 조정" | `variant="pill"`(radius 0.5rem 세그먼트) | 요청으로 확정 |
| 검색 영역 카드(기간·검색 기준·검색어·조회) | 기존 공용 자산 재사용 | `FilterBar`, `DateRangePicker`, `Dropdown`, `TextInput`, `Button` | 목록 3종의 별도 검색 카드. FilterBar가 라벨+필드+조회 구조를 이미 제공 | 주문일자 빠른 기간 선택은 FilterTabs `pill` 사용 | 제안 |
| 테이블 | 기존 공용 자산 재사용 | `shared/ui/table` (수정 없음) | 사용자 지시: 중앙 스타일 유지, 컬럼 계약으로 페이지별 스타일 | `selection`, `onRowClick`, `custom` cell, column `className` 사용 | 요청으로 확정 |
| EC 테이블 공통 스타일·셀(상품 썸네일+이름/옵션, 2줄 텍스트, 링크형 ID, 재고 바, 행 액션 버튼) | 공용 자산 신규 작성(EC 범위 위젯) | `widgets/ec-seller/ui/ec-table.css`, `ec-table-cells.tsx` | 주문 목록 컬럼 스타일을 EC 전 테이블에 일관 적용. EC 도메인 전용이라 shared가 아닌 widgets | `EcProductCell({imageUrl,name,meta})`, `EcTwoLineCell({primary,secondary})`, `EcStockCell({stock,max})` | 제안 |
| 상태 뱃지(주문 접수·판매중 등) | 기존 공용 자산 재사용 | `shared/ui/status/status-badge` | `color` prop으로 도메인 색 지정 가능 | 페이지 config에서 key→label/color 매핑 | 제안 |
| 페이지네이션 | 기존 공용 자산 재사용 | Table 내장 `Pagination` | 동일 기능 | 없음 | 제안 |
| 카드 섹션(폼 섹션·정보 카드) | 기존 공용 자산 재사용 | `shared/ui/section-card` | 상품 수정·주문 상세·문의 상세 카드 | 없음 | 제안 |
| 정보 목록(배송지·결제 정보) | 기존 공용 자산 재사용 | `shared/ui/definition-list` | 라벨-값 쌍 | 없음 | 제안 |
| 입력(텍스트·셀렉트·텍스트영역·토글) | 기존 공용 자산 재사용 | `text-input`, `dropdown`, `text-area`, `toggle-switch` | 동일 기능 | `TextInput unit`로 원/₩ 표기 | 제안 |
| 카테고리 다중 선택 칩(입점 신청) | 기존 공용 자산 재사용(확장 검토) | `choice-chip-group` | 현재 단일 선택. 다중 선택 필요 → `selectionMode?: "single" \| "multiple"` 추가 또는 페이지에서 칩 반복 | Q 없이 확장 제안(기존 호출 불변) | 제안 |
| 판매 상태 선택 카드(판매중/판매 중지/품절) | 공용 자산 신규 작성 없이 페이지 로컬 | `pages/ec-product/ui` | 1개 화면 전용 radio card. 공용 목적 요구 없음 | `role="radiogroup"` | 제안(예외: 로컬) |
| 이미지 업로드 슬롯(대표·추가 이미지, 로고) | 기존 공용 자산 재사용 | `shared/ui/image-upload`(팝업 pubsub) + 로컬 슬롯 표시 | 업로드 팝업은 기존 자산, 슬롯 격자는 화면 표시 | 업로드 callback은 props | 제안 |
| 송장 정보 입력 모달 | 기존 공용 자산 재사용 | `shared/ui/modal` | HeroUI 기반 모달 어댑터 존재 | `open/close` + 폼 props | 제안 |
| 주문 진행 단계(주문 접수→배송 완료) | 기존 공용 자산 재사용 검토 → 불충족 시 로컬 | `shared/ui/timeline-list` 조사 결과 세로 목록형 → 가로 stepper 불충족, 페이지 로컬 | 1개 화면 | `steps: {key,label,at?,state}[]` | 제안(예외: 로컬) |
| 리치 텍스트 입력(상품 설명·답변 작성) | 기존 공용 자산 재사용 | `text-area` (툴바 제외) | 에디터 패키지 미설치(`_react-quill.css`만 존재). 기능 없는 툴바는 오해 소지 | Q4 | 미정 |
| 차트 영역 | 없음(자리만) | 페이지 로컬 placeholder | 사용자 지시 보류 | 고정 높이 빈 카드 | 요청으로 확정 |
| 카테고리 비중 막대(누적 매출 요약) | 기존 공용 자산 재사용 | `shared/ui/ratio-bar` | 비율 막대 존재 | 없음 | 제안 |

## 계약과 공용화 영향

- props·이벤트: 모든 EC View는 `XxxViewProps`(데이터 + callback)만 받는다. 목록: `tabs{items,value,onChange}`, `search{...values,onChange*,onSubmit,onReset}`, `table{rows,page,pageCount,onPageChange,onRowClick}`.
- 공용 수정 영향: Navigation(4개 셸 전체 — 부모 클릭 이동 제거, 흰 테마), KpiCard(선택 prop 추가, 기존 불변), ChoiceChipGroup(선택 prop 추가 시 기존 불변).
- 신규 공용 목적: TrendBadge — 매출 KPI 증감 표시(사용자 지시, 중앙 정책 스킬화 대상). FilterTabs — 목록 상태 탭·기간 필터(사용자 지시, 이후 기존 화면 일괄 적용 후보).
- 번들: lucide-react는 이미 의존성·번들 포함(tree-shaking named import). 신규 의존성 없음.
- 미확정: Q1~Q5.

## UI·Logic 연결

- 선행 구현·계약 제공자: UI 선행, `pages/ec-*/model/*.types.ts`
- 맞추는 방향: `controller -> UI`
- controller: Logic이 `pages/ec-*/hook/use-*-controller.ts`로 구현 예정. UI는 page에서 View에 props 전달.
- 불일치: 없음(API 미정).

## 외부 UI 라이브러리 스킬

| 패키지·설치 버전 | 사용 목적·적용 항목 | 어댑터·공개 계약 | 기존 스킬 | 세션 초안·대상 중앙 경로 | 상태 |
| --- | --- | --- | --- | --- | --- |
| `@heroui/react` 3.2.3 | 기존 어댑터(Button, Select, Modal, Chip, Pagination, Switch, TextArea) 경유 | `src/shared/ui/*` 기존 어댑터 | 주입 번들에서 미확인 | `unknown/ui-library-skills/heroui/SKILL.md` → `policy/common/skills/reference/libraries/heroui/SKILL.md` | 구현 전 초안 작성 |
| `lucide-react` 1.25.0 | 사이드바·카드 아이콘 | `src/shared/assets/icons/ec-icons.tsx` named re-export | 미확인 | `unknown/ui-library-skills/lucide-react/SKILL.md` → `.../libraries/lucide-react/SKILL.md` | 구현 전 초안 작성 |

## 승인과 변경

- 승인 요청에 제시한 선택·미정 항목: 위 표, Q1~Q5
- 사용자 승인 근거·확정 범위: 대기
- 구현 중 달라진 항목:
  - 카테고리 비중(누적 매출 요약): `ratio-bar`는 한 줄 누적 막대라 항목별 막대 요구와 달라 페이지 로컬 막대(`role="progressbar"`)로 구현.
  - 주문 진행 단계: 페이지 로컬 `ec-order-progress.tsx`.
  - 추가 EC 위젯: `EcSelect`(index 기반 Dropdown → key 계약), `EcField`, `EcTrendCaption`, `toTableSelection`, 빈 계약값(`ec-contract.ts`).
  - 짧은 표(주문 상품·판매 상위 상품)는 중앙 Table을 쓰고 `.ec-table-static`으로 페이지네이션만 숨김.
  - 사용자 결정(Q3): 임시 데이터 없이 빈 계약값만 전달.
- 승인: 2026-09-30 "작업 진행"
