# Handoff — EC 판매자 UI → Logic

## 결론

`/ec/*` 판매자 화면 UI와 View props 계약(UI 선행, `controller -> UI`)을 구현했다. 모든 page는 **빈 계약값**(null·빈 배열·no-op)만 View에 넘긴다(사용자 결정: 임시 데이터 미반영). Logic은 각 page의 빈 계약값을 controller 결과로 교체하면 된다. Prettier 포맷 완료, 포맷 후 lint·build 통과.

## 역할

- requested_roles: UI / confirmed_roles: UI(inject `--role ui`) / completed_roles: UI
- next_role(제안): Logic — API·DTO 확정 후 controller 구현
- 판단 근거: 사용자 지시 "API 미정, UI가 key/value를 임의 구성하면 Logic이 API를 맞춘다"

## 보내는 작업 위치

- project: `asan-metaverse-admin-ui`
- branch: `feature/ec-seller-ui` (sy-main `bc579b3`에서 생성, 직접 부모 `sy-main`, 관계 그래프 미등록)
- worktree: `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/ec-seller-ui`
- HEAD: `b6fc92d` (UI 변경 전체 commit, 작업 트리 깨끗)
- 기준 시점: 2026-09-30

## 인계 대상 작업 위치(제안)

- 같은 branch·worktree를 순차 공유(UI→Logic). UI 변경은 `b6fc92d`로 commit되었으므로 Logic이 이어서 작업할 수 있다.

## Logic 작업 — page별 연결 지점

| 라우트 | page 파일 | View props 타입 | 빈 계약값 | 연결할 controller(제안 이름) |
| --- | --- | --- | --- | --- |
| `/ec/apply` | `pages/ec-seller-apply/ui/ec-seller-apply-page.tsx` | `EcSellerApplyViewProps` | page 내부 inline | `useEcSellerApplyController` |
| `/ec/apply/pending` | `.../ec-seller-apply-pending-page.tsx` | `EcSellerApplyPendingViewProps` | inline | 신청 정보 조회 |
| `/ec/dashboard` | `pages/ec-dashboard` | 없음(보류) | - | - |
| `/ec/products` | `pages/ec-product/ui/ec-product-list-page.tsx` | `EcProductListViewProps` | inline | `useEcProductListController` |
| `/ec/products/new`, `/ec/products/:productId` | `.../ec-product-form-page.tsx` (공용) | `EcProductFormViewProps` (`mode`) | `EC_PRODUCT_EMPTY_FORM_PROPS` | `useEcProductFormController(productId?)` |
| `/ec/orders` | `pages/ec-order/ui/ec-order-list-page.tsx` | `EcOrderListViewProps` (+ `invoiceDialog`) | `EC_ORDER_LIST_EMPTY_PROPS` | `useEcOrderListController` |
| `/ec/orders/:orderId` | `.../ec-order-detail-page.tsx` | `EcOrderDetailViewProps` | `EC_ORDER_DETAIL_EMPTY_PROPS` | `useEcOrderDetailController(orderId)` |
| `/ec/inquiries` | `pages/ec-inquiry/ui/ec-inquiry-pages.tsx` | `EcInquiryListViewProps` | `EC_INQUIRY_LIST_EMPTY_PROPS` | `useEcInquiryListController` |
| `/ec/inquiries/:inquiryId` | 같은 파일 | `EcInquiryDetailViewProps` | `EC_INQUIRY_DETAIL_EMPTY_PROPS` | `useEcInquiryDetailController(inquiryId)` |
| `/ec/settlement/analysis·sales·summary` | `pages/ec-settlement/ui/ec-settlement-pages.tsx` | `EcSalesAnalysis/Status/SummaryViewProps` | `EC_SALES_*_EMPTY_PROPS` | 매출 controller |
| `/ec/settings/profile` | `pages/ec-settings/ui/ec-settings-profile-page.tsx` | `EcSettingsProfileViewProps` | `EC_SETTINGS_PROFILE_EMPTY_PROPS` | 판매자 정보 controller |
| 사이드바 하단 | `app/router/ec-seller-shell.tsx` | `EcSellerProfileData` | `profile={null}` | 판매자 요약 조회 |

## 공통 계약 (`src/widgets/ec-seller/model/ec-common.types.ts`)

- 금액·수량: `number`(원·개). 일시: ISO 8601 문자열. 표시 형식은 UI(`ec-format.ts`)가 결정.
- 상태: `EcStatusDisplay { code, label, tone }` — API 상수 원문·한글 라벨·뱃지 색을 controller가 매핑.
- 상태 탭: `EcStatusTabs { items: {key,label,count}[], selectedKey, onChange }` — `전체`도 항목으로 포함(현재 빈 값의 key `"ALL"`). 사용자 지시: 주문 접수·상품 준비 중 등은 API 상수를 한글로 매핑한 개수.
- 선택지: `EcSelectOption { key, label }`, 선택 상태는 key(`null` = 전체/미선택).
- 페이지: `EcPagination { page, pageSize, pageCount, totalCount, onPageChange }`.
- 증감: `EcTrendMetric { value, changeRate(부호 포함 %), comparisonLabel }`.

## 주요 동작 계약

- 주문 목록 행 클릭 → `/ec/orders/:orderId` (page에서 연결 완료). 행 처리 버튼은 `row.action {key,label,variant}` + `onRowAction(orderId, actionKey)`. 송장 입력 모달은 `invoiceDialog` 상태를 controller가 소유.
- 주문 상세: `shipment === null`이면 `배송 정보 입력` 카드(`shipmentForm`)를 표시하고 진행 현황표를 숨긴다. `shipment`가 있으면 `progressSteps`(state `done|current|upcoming`)와 운송장 정보를 표시한다. 하단 처리 버튼은 `primaryAction {key,label,isDisabled} | null`.
- 상품 등록/수정: 한 View, `mode`만 다름. 텍스트 입력은 `onFieldChange(field, value)`, 가격·재고는 입력 중 문자열.
- 이미지 업로드: View는 `onImageAdd`/`onLogoSelect(file)`만 호출한다. 업로드 팝업·API는 Logic.
- 화면 이동(등록·수정·상세·목록으로)은 page에서 `useNavigate`로 이미 연결했다.

## 불일치·미확정

- API·DTO 전부 미정. controller 매핑 시 View 계약과 다르면 사용자 확인 후 반영(ui-controller 정책).
- 사업자 번호는 사용자 지시로 입점 신청에서 제외.
- 차트(매출 3화면)는 영역만 있음. 대시보드는 보류.

## 실행한 검증

- `npx tsc -p tsconfig.app.json --noEmit` 통과
- `npm run lint` 통과(1건 수정 후), `npm run build` 통과 (chunk 크기 경고는 기존)
- 실행하지 않음: 공통 포맷 트리거(차단), 브라우저 확인(요청 없음)

## 차단 요인

- 없음. 앞서 자동 안전 검사 오류로 남았던 결과 미확인 쓰기 기록이 외부에서 해소되었고, 이후 포맷·lint·build를 완료했다.

## 기타 산출물

- 증감 뱃지 정책 스킬 초안: `unknown/policy-skill-drafts/trend-badge/SKILL.md`
- 라이브러리 스킬 초안: `unknown/ui-library-skills/{lucide-react,heroui}/SKILL.md`
- 자산 선정: `unknown/ui-asset-plan.md`
