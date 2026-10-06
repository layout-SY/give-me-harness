# 계획

승인 영역은 목표·범위·역할·계약·검증 기준이다. 진행 결과는 종료 표식 아래에 기록한다.
진행 기록에 새 요구를 적는 것으로 승인 범위를 확대할 수 없다.

<!-- asan-plan:approval:start:v1 -->

## 목표

Figma `해커톤, EC` 페이지의 **판매자** 섹션 19개 프레임을 `/ec/*` 라우트의 화이트 모드 UI로 구현한다. API 미정 상태이므로 각 화면의 표시 데이터를 임의 key/value 타입(View props 계약)으로 정의해 Logic이 이후 controller·DTO를 맞출 수 있게 한다(`controller -> UI`).

## 작업 유형

- feature (UI 선행 publish + 공용 사이드바 수정)

## 범위

- 대상 repository·branch·worktree: `asan-metaverse-admin-ui`, 기준 `sy-main`(HEAD `bc579b3`). 작업 위치는 사용자 결정(질문 Q5).
- 포함할 작업과 변경 대상:
  1. 공용 사이드바(`src/widgets/side-navigation/ui/navigation.tsx`·`.css`·`.responsive.css`) — Figma `상품 목록`(45:2645) 사이드바 기준: 흰 배경, 브랜드 영역 아래 구분선, 부모 탭은 라우팅 제거·펼침 토글 전용(닫힘 ▼ / 열림 ▲ + bold), 자식 탭 세로 나열(좌측 가이드 라인·활성 배경), 닫기 토글 유지, 콘텐츠 영역과 border·배경으로 분리, 선택적 하단 사용자 영역(footer). 기존 `/cp`·`/vo`·`/manage`·`/events` 셸에도 동일 적용된다.
  2. `/ec/*` 라우트·셸: `src/app/router/ec-seller-shell.tsx`(사이드바 셸), `ec-apply-shell.tsx`(입점 신청·승인 대기용 상단 헤더 단독 레이아웃), `routes.tsx` 등록, `_navigation8.ts` + `buildEcSellerNavigationItems`.
  3. 신규 공용 UI: `shared/ui/trend-badge`(증감 추이 뱃지), `shared/ui/filter-tabs`(개수 포함 상태 탭 / pill 기간 필터 variant).
  4. EC 페이지(FSD `pages/ec-*`): 입점 신청, 승인 대기, 대시보드(빈 페이지 컴포넌트), 상품 목록, 상품 수정(=등록 재사용), 주문 목록(+송장 입력 모달), 주문 상세 관리, 주문 상세 정보, 매출 분석, 매출 현황, 누적 매출 요약, 고객 문의 목록, 문의 상세, 기본 정보 관리 및 중복 프레임 처리(Q1 결정에 따름).
  5. EC 테이블 공통 스타일: 중앙 `Table` 컴포넌트는 수정하지 않고 column `className`·`custom` cell 계약으로 페이지에서 스타일링. EC 전용 `ec-table` 클래스·셀 컴포넌트를 `widgets/ec-seller`에 두고 모든 EC 테이블이 같은 스타일을 쓴다.
  6. 세션 초안: 증감 뱃지 중앙 정책 스킬 문서 초안, HeroUI·lucide-react 라이브러리 스킬 초안.

## 확정 결정 (사용자 답변 2026-09-30)

- Q1: 주문 상세 = `주문 상세 관리`(45:3325)와 `주문 상세 정보`(45:6633)를 주문 id 기준 한 페이지(`/ec/orders/:orderId`)로 합침. 화이트 `주문 상세 정보` 레이아웃 기준. 배송 정보 미입력 시 `배송 정보 입력` 카드 표시 + 배송 진행 현황표 숨김, 입력된 경우에만 현황표 표시. 매출 3개 화면은 각각 유지. 문의 목록 = `고객 문의 목록`(+`문의 관리` 상태 탭), 문의 상세 = `1:1 문의 내역`(+`문의 상세` 구성) 한 페이지. 나머지 제안 유지.
- Q2: 제안한 사이드바 트리(대시보드 / 상품 관리 / 주문 관리 / 문의 관리 / 정산 관리 / 설정).
- Q3: 임시 데이터 미반영. 화면 형태와 props 계약(타입)만 구현. page는 빈 계약값(빈 배열·null)과 no-op callback 없이 Logic 연결 지점만 남긴다.
- Q4: TextArea 사용, 툴바 제외.
- Q5: `feature/ec-seller-ui` 브랜치 + `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/ec-seller-ui` (생성 완료, 기준 `bc579b3`).

## 제외 사항

- 대시보드 화면 구현(페이지 컴포넌트만 생성).
- 모든 차트 그래프(영역만 확보). API·DTO·controller·query·MSW handler 구현(Logic 담당).
- 기존 비-EC 페이지의 필터 UI 일괄 교체(EC 적용 후 사용자 확인 뒤 별도 작업).
- 중앙 정책 저장소 직접 수정(세션 초안 작성 후 중앙 작업으로 인계).
- 시각 QA·캡처(요청 시에만).

## 제약 조건

- 화이트 모드만. 입점 신청에서 `사업자 번호` 항목 제거.
- 상품 등록은 상품 수정 View를 그대로 재사용(`mode: "create" | "edit"`만 구분).
- 목록 3종(상품·주문·고객 문의)은 `주문 리스트`(45:4349) 레이아웃(검색 카드 → 상태 탭 바가 붙은 테이블 카드), 테이블 컬럼 셀은 `주문 목록`(45:3002) 스타일.
- 상태 탭은 `전체` 고정 + API 상수 → 한글 라벨·개수 배열(`{ key, label, count }[]`)을 props로 받는다.
- 주문 목록 행 클릭 → `/ec/orders/:orderId` 주문 상세 관리.
- 문의 상세는 콘텐츠 스크롤(프레임 넘침 해소). 주문 상세 정보의 하단 고정 바는 관리자 메모 아래 별도 카드로 이동.
- Figma의 간격·버튼 비율 어색함은 기존 토큰(`--cp-*`) 기준으로 조정.

## 스킬 및 역할

- 제안 역할: UI (inject `--role ui`로 확인됨)
- 역할 판단 근거: 화면 구조·스타일·props 계약 작업이며 API는 Logic 담당으로 사용자 명시.
- 사용자에게 확인할 역할: 없음
- 승인할 Git 작업: Q5 결정(브랜치·worktree 생성 여부). commit은 완료 후 별도 승인.
- 산출물 책임: owner

| 작업 구간 | 역할 | 스킬 | 예상 결과 |
| --- | --- | --- | --- |
| 사이드바·셸·라우트 | UI | task-role-routing, coding-convention, styles, ui-library, frontend-design | 공용 사이드바 개편, `/ec/*` 셸 |
| 공용 UI 신규 | UI | ui-library, styles | TrendBadge, FilterTabs |
| EC 페이지 | UI | coding-convention, styles, ui-library | pages/ec-* View + props 타입 |
| 문서 | UI | documentation, ui-library | 정책 스킬·라이브러리 스킬 초안, handoff |

## UI 자산 선정

- 항목별 자산 선정 문서: [UI 자산 선정 계획](unknown/ui-asset-plan.md)
- 외부 UI 라이브러리 사용 스킬: `@heroui/react@3.2.3`, `lucide-react@1.25.0` 초안을 `unknown/ui-library-skills/`에 작성, 중앙 등록은 인계.
- 미정: Q1~Q5 (사용자 응답 대기).

## UI·Logic 연결 계약

- 선행 구현·계약 제공자: UI 선행(사용자 명시 "임의 key/value로 구성"). 계약 제공자는 각 `pages/ec-*/model/*.types.ts`의 View props.
- 맞추는 방향: `controller -> UI`
- 위치: View는 `XxxViewProps`(데이터·상태·callback)만 받는다. Page는 Logic controller 연결 전까지 Q3 결정에 따른 데이터를 전달한다.
- 불일치 항목: 해당 없음(API 미정). Logic 연결 시 불일치는 사용자 확인.

## 검증

- `npm run lint`, `npm run build` 통과. 라우트별 렌더 오류 없음(dev 서버 기동 확인은 요청 시).

## 위험 요소 및 결정 사항

- 공용 사이드바 변경은 기존 4개 셸 전체의 시각·동작(부모 클릭 시 이동 안 함, 흰 배경)을 바꾼다 — 사용자 요청 범위.
- `--clr-nav-*` 토큰 값 변경으로 다크 사이드바 전제의 스타일이 있으면 함께 확인한다.

<!-- asan-plan:approval:end:v1 -->

## 진행 기록 (해시 제외)

- 단계별 상태·완료한 작업: 사이드바·셸·라우트, 공용 UI(TrendBadge·FilterTabs·line-icons, KpiCard·ChoiceChipGroup 확장), `widgets/ec-seller`, EC 페이지 전체(대시보드는 빈 페이지) 구현 완료. 인계: [handoff.md](handoff.md).
- 실행한 검증·결과·근거: `tsc --noEmit` 통과, `npm run lint` 통과(trend-badge export 1건 수정), `npm run build` 통과.
- 장애·미확인 사항·인계 출처: 자동 안전 검사 일시 오류로 결과 미확인 쓰기 기록이 남아 공통 포맷 트리거가 차단됨(포맷 미완료). 구매자 EC UI 자산은 admin-ui에서 확인되지 않음.
- UI 라이브러리 스킬 등록 상태·계약 질문에 대한 답변: 세션 초안 작성(lucide-react, heroui, trend-badge 정책), 중앙 미등록. Q1~Q5 답변은 승인 영역에 반영.

## 승인

- 상태: awaiting approval
- 필수 문구: `이 역할과 계획대로 진행할까요, 아니면 조정할 부분이 있나요?`
