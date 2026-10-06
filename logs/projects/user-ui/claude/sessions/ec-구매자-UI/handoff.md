# 인계: EC 구매자 UI → Logic (API·DTO·controller 연결)

> 아래 DTO·endpoint는 모두 **화면 데이터에서 역산한 추정**이다(사용자 결정 Q1). 서버 명세가 오면 명세가 우선이며, 이 문서의 필드명·경로를 계약으로 확정하지 않는다. 명세와 다르면 view model(`src/features/ec/ui/types.ts`)은 유지하고 mapper만 바꾼다.

## Assignment 이동

- 보내는 host·session·role: Claude Code · `ec-구매자-UI` · `ui`
- 받는 host·session·제안 role: 미정 host · 새 세션 · `logic`

## 역할 라우팅

- 요청 역할(`requested_roles`): ui, logic
- 확인된 역할(`confirmed_roles`): ui (inject role)
- 완료 역할(`completed_roles`): ui
- 다음 제안 역할(`next_role`): logic
- 역할 판단 근거: API·DTO·parser·hook·폼 검증은 `ui` 역할 경계 밖(`references/ui.md` 경계). 사용자가 Q1에서 "예상 DTO·API 연결은 logic handoff 문서로" 결정.
- 사용자 확인: Q1~Q5 답변(2026-09-28), 구현 승인 "작업 진행"

## 목표 및 현재 상태

피그마 "구매자" 9개 화면을 `/ec/*`로 구현했다. 화면·shared 컴포넌트·라우트는 완료했고, 모든 route는 **빈 데이터**를 넘겨 빈 상태·기본 화면을 보여 준다. Logic 세션은 아래 계약으로 API·DTO·parser·query/mutation hook·controller·폼 검증을 만들고 `src/pages/ec/ui/EcRoutes.tsx`의 빈 값 자리를 교체한다.

## 완료된 작업

- 화면(props 기반): `src/features/ec/ui/**`
- view model 타입: `src/features/ec/ui/types.ts`
- 임시 상수: `src/features/ec/model/constants.ts` (탭, 주문 상태, 결제 수단, 문의 유형, 첨부 제한, 고객센터 메뉴)
- 표시 매핑: `src/features/ec/ui/ecStatus.ts`, 포맷: `src/features/ec/ui/format.ts`
- 라우트: `src/shared/config/ecRoutes.ts`, `src/pages/ec/**`, `src/app/routing.ts` 등록(인증 경계 안)
- shared 신규: top-app-bar, bottom-dock, bottom-tab-bar, info-list, thumbnail, image-carousel(+ImageFrame), image-gallery-modal, quantity-stepper, chip-group, choice-card-group, progress-steps, accordion
- shared 확장: `PageScreen.header`, `SectionBlock.aside`, `NoResults.message`

## 대기 중인 작업

1. EC API client·DTO·parser·mapper (아래 "예상 API 계약")
2. query/mutation hook과 route controller (아래 "화면별 연결")
3. 폼 검증(주문/결제, 1:1 문의) — react-hook-form + zod, 기존 `features/inquiry/model/forms/inquiryForm.ts` 패턴
4. 장바구니 수(`tabBar.cartCount`) 전역 조회
5. 사진 첨부 업로드 흐름
6. (필요 시) MSW mock — **사용자에게 범위 확인 후** (정책: 미확정 계약을 mock으로 채우지 않음)

## 결정 사항 및 제약 조건

- EC는 citizen·meeting·`/manage` 문의와 **별개 개념**. `src/features/ec`, `src/pages/ec`만 사용한다. API 연결 패턴은 기존(`features/inquiry`)을 그대로 따른다: `api/client.ts` → `*.api.ts` → `*.dto.ts` → `*.parser.ts` → `hook/use*Queries.ts`·`use*Mutation.ts`·`use*Controller.ts` → `model/queryKeys.ts` → `pages/ec/model/presentation.ts`(DTO→view model).
- 공통 envelope는 `ApiClient`/mapper 경계에서 처리하고, 목록 응답은 `src/shared/api/common/page-response.dto.ts`의 `PageResponseDto<T>`·`createPageResponseSchema`를 재사용한다(도메인별 중복 정의 금지).
- 1:1 문의 유형 4종(배송·반품/환불·상품·기타)과 사진 첨부 최대 3장(JPG·PNG)은 사용자 확정. API 확정 시 `EC_INQUIRY_TYPE` 값을 서버 코드로 교체한다(주석 있음).
- 결제 수단은 "신용카드" 하나만 두는 **UI 평가 요소**. 실제 결제(Stripe 등) 연동, 주소 검색, 배송 조회 동작은 **미정** — 콜백만 연결되어 있다.
- 카테고리 탭·알림·더 많은 질문 보기·고객센터 빠른 메뉴는 대응 화면이 없어 **버튼과 콜백만** 있다(사용자 결정 Q3).
- 금액은 원 단위 정수, 날짜는 view model에서 `YYYY.MM.DD` 문자열(변환은 presentation에서 `formatDateToLocalTimezone(value, "YYYY.MM.DD")`).

## 보내는 작업의 위치와 변경 상태

- project·저장소 루트: `/Users/okand/SynologyDrive/asan-metaverse-user-ui` (user-ui)
- 현재 branch·HEAD·worktree: `feature/ec-buyer-ui` · `3e30393` · `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-user-ui-worktree/ec-buyer-ui`
- 확인 시점·인계 기준 commit: 2026-09-28, 인계 기준 **`b52a5bc`** (부모 `sy-main` `3e30393`에서 분기)
- 완료한 commit: `b52a5bc feat: EC 구매자 화면과 공용 UI 컴포넌트 추가` — 72 files, +4089/−6. 변경: `DESIGN.md`, `package.json`·`package-lock.json`(embla-carousel-react ^8.6.0), `src/app/routing.ts`·`routing.test.ts`, `src/shared/ui/content/*`, `src/shared/ui/no-results/no-results.tsx`, `src/shared/ui/screen/*`, 신규 `src/features/ec/`, `src/pages/ec/`, `src/shared/config/ecRoutes.ts`, `src/shared/ui/{accordion,bottom-tab-bar,chip-group,choice-card-group,image-carousel,image-gallery-modal,progress-steps,quantity-stepper,thumbnail}/`
- staged·unstaged·untracked 변경: 없음(commit 후 `git status` clean 확인). 세션 산출물 `.claude/logs/`는 git ignore 대상
- 보존할 내용: 기본 checkout(`sy-main`)의 미커밋 `README.md`는 다른 작업이며 건드리지 않았다.

## 인계 대상 작업 공간

### 작업 공간: ec-buyer

- 수행할 기능·하위 작업: EC API·hook·controller 연결
- 사용할 역할: logic
- project·저장소 루트: `/Users/okand/SynologyDrive/asan-metaverse-user-ui`
- 목적지 branch: `feature/ec-buyer-ui` (공유) — UI 변경이 commit된 뒤 이어서 작업하는 것을 제안
- worktree·실행 디렉터리: `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-user-ui-worktree/ec-buyer-ui`
- 기존 공간 / 생성 예정: 기존 공간(이 세션에서 생성, relation 등록 완료)
- HEAD: `b52a5bc` (미커밋 변경 없음)
- 직접 부모: `sy-main` (relation create로 등록)
- 공유 / 분리: UI→Logic 순차 연결이라 공유를 제안. 병렬로 UI 보완이 계속되면 `feature/ec-buyer-ui` 아래 `task/ec-buyer-logic` 분리를 사용자에게 확인.
- 진입 전 확인: `git -C <worktree> status --short`, HEAD, 이 문서의 파일 목록과 비교. `.env`가 worktree에 없다(기본 checkout에만 있는 ignored 파일) — 필요 시 사용자 확인.
- 필요한 Git 작업: 없음(UI commit 완료). logic 변경 commit·sy-main 병합은 별도 승인 필요

## 역할별 상세 작업

### 역할·하위 작업: logic — EC API·DTO·parser

- 작업 공간: ec-buyer
- 파일(제안): `src/features/ec/api/{client.ts, product.api.ts, product.dto.ts, cart.api.ts, cart.dto.ts, order.api.ts, order.dto.ts, support.api.ts, support.dto.ts, ec.parser.ts}`, `src/features/ec/model/queryKeys.ts`
- 재사용: `src/shared/api/api-client.ts`, `src/shared/api/common/page-response.dto.ts`, `src/shared/api/common/dto.ts`(`PageSizeQueryDto`, `KeywordQueryDto`), `features/inquiry/api/*` 구조
- 완료 기준: DTO·parser 단위 테스트, `npm run lint`·`npm run test`·`npm run build`

#### 예상 API 계약 (추정 · 미확정)

| # | 화면 | method · path(추정) | 요청(추정) | 응답 payload(추정) |
| --- | --- | --- | --- | --- |
| A1 | 마켓 | `GET /ec/products` | `{ page, size, categoryId?, keyword? }` | `PageResponseDto<EcProductListItemDto>` |
| A2 | 마켓 | `GET /ec/categories` | – | `EcCategoryDto[]` |
| A3 | 마켓·상세 | `POST /ec/cart/items` | `{ productId, quantity }` | `{ cartItemId, cartCount }` |
| A4 | 상품 상세 | `GET /ec/products/{productId}` | – | `EcProductDetailDto` |
| A5 | 상품 상세 | `PUT/DELETE /ec/products/{productId}/wish` | – | `{ wished: boolean }` |
| A6 | 장바구니 | `GET /ec/cart` | – | `EcCartDto` |
| A7 | 장바구니 | `PATCH /ec/cart/items/{cartItemId}` | `{ quantity }` | `EcCartDto` |
| A8 | 장바구니 | `DELETE /ec/cart/items/{cartItemId}` | – | `EcCartDto` |
| A9 | 공통 탭 | `GET /ec/cart/count` (또는 A6의 개수) | – | `{ count }` |
| A10 | 주문/결제 | `GET /ec/checkout?cartItemIds=` 또는 `?productId=&quantity=` | 바로 구매·장바구니 구매 구분 **미정** | `EcCheckoutDto` |
| A11 | 주문/결제 | `POST /ec/orders` | `EcCreateOrderRequestDto` | `{ orderId }` |
| A12 | 주문 완료 | `GET /ec/orders/{orderId}/completion` (또는 A14 재사용) | – | `EcOrderCompletionDto` |
| A13 | 주문 내역 | `GET /ec/orders` | `{ page, size, from? }` | `PageResponseDto<EcOrderListItemDto>` |
| A14 | 주문 상세 | `GET /ec/orders/{orderId}` | – | `EcOrderDetailDto` |
| A15 | 고객센터 | `GET /ec/faqs` | `{ keyword?, size? }` | `EcFaqDto[]` |
| A16 | 1:1 문의 | `POST /ec/inquiries` (multipart 또는 선업로드 id) | `EcCreateInquiryRequestDto` | `{ inquiryId }` |
| A17 | 1:1 문의 | `POST /ec/uploads/images` (A16 방식에 따라) | `File` | `{ fileId, url }` |

#### 예상 DTO (추정)

```ts
type EcCategoryDto = { id: string; name: string };
type EcProductListItemDto = { id: number; name: string; thumbnailUrl: string | null; price: number; rating: number | null };
type EcProductDetailDto = {
  id: number; name: string; imageUrls: string[]; price: number; originalPrice: number | null;
  stockQuantity: number; maxOrderQuantity: number | null; rating: number | null; reviewCount: number;
  delivery: { title: string; description: string } | null; // 예: "빠른 무료 배송", "내일 10월 24일(금) 도착 보장"
  features: string[]; usageGuide: string | null; shippingGuide: string | null; wished: boolean;
};
type EcCartItemDto = { id: number; productId: number; name: string; optionLabel: string | null; thumbnailUrl: string | null; price: number; quantity: number; maxOrderQuantity: number | null };
type EcPriceSummaryDto = { productAmount: number; shippingFee: number; totalAmount: number };
type EcCartDto = { items: EcCartItemDto[]; summary: EcPriceSummaryDto };
type EcOrderLineDto = { id: number; productId: number; name: string; optionLabel: string | null; thumbnailUrl: string | null; price: number; quantity: number };
type EcShippingAddressDto = { recipient: string; phone: string; zipCode: string; address: string; addressDetail: string; memo: string | null };
type EcCheckoutDto = { items: EcOrderLineDto[]; summary: EcPriceSummaryDto; defaultShipping: EcShippingAddressDto | null; paymentMethods: ("CARD")[] };
type EcCreateOrderRequestDto = { cartItemIds?: number[]; productId?: number; quantity?: number; shipping: EcShippingAddressDto; paymentMethod: "CARD" };
type EcOrderStatusDto = "ORDERED" | "PREPARING" | "SHIPPING" | "DELIVERED"; // 취소·반품 코드 미정
type EcOrderListItemDto = { id: number; orderNumber: string; orderedAt: string /* ISO */; status: EcOrderStatusDto; representativeName: string; itemCount: number; totalAmount: number; thumbnailUrl: string | null };
type EcOrderDetailDto = { id: number; orderNumber: string; orderedAt: string; status: EcOrderStatusDto; tracking: { location: string; message: string } | null; items: EcOrderLineDto[]; shipping: EcShippingAddressDto; payment: EcPriceSummaryDto };
type EcOrderCompletionDto = { orderId: number; orderNumber: string; paidAmount: number; shipping: EcShippingAddressDto };
type EcFaqDto = { id: number; question: string; answer: string };
type EcInquiryTypeDto = "DELIVERY" | "RETURN_REFUND" | "PRODUCT" | "ETC"; // 사용자 확정 값, 서버 코드는 미정
type EcCreateInquiryRequestDto = { type: EcInquiryTypeDto; title: string; content: string; imageFileIds: string[] /* 최대 3 */ };
```

### 역할·하위 작업: logic — 화면별 연결 (view model · callback)

- 작업 공간: ec-buyer
- 수정 파일: `src/pages/ec/ui/EcRoutes.tsx`(빈 값 → controller), `src/pages/ec/model/presentation.ts`(DTO→view model), 신규 `src/features/ec/hook/*`
- 원칙: 화면 컴포넌트(`features/ec/ui/**`)의 props 계약은 유지. 추가 필드가 필요하면 UI 세션과 조율.

| 경로 · Route | 화면 컴포넌트 | 데이터 props (view model) | callback | 연결 API · 변환 |
| --- | --- | --- | --- | --- |
| `/ec` · `EcMarketRoute` | `EcMarketPage` | `products: EcProductCardItem[]`, `categories: {label,value}[]`, `category`, `keyword`, `isLoading`, `hasUnreadNotification`, `tabBar{value:"home",cartCount}` | `onCategoryChange`, `onKeywordChange`, `onKeywordSubmit`, `onProductClick(id)`→상세 이동(연결됨), `onAddToCart(id)`, `onNotificationClick`(화면 없음) | A1(`thumbnailUrl→imageUrl`), A2(`{name→label, id→value}`, "전체" 칩 포함 여부 **미정**), A3, A9. 검색 실행 시점(입력 즉시/제출) **미정** |
| `/ec/products/:productId` · `EcProductDetailRoute` | `EcProductDetailPage` | `product: EcProductDetail`, `isLoading`, `quantity`, `isWished`, `cartCount` | `onQuantityChange`, `onWishToggle`, `onAddToCart`, `onBuyNow`→결제 이동(연결됨), `onCartClick`(연결됨), `onBack`(연결됨) | A4: `imageUrls→images[{url, alt: name}]`, `stockQuantity>0→inStock`, `maxOrderQuantity→maxQuantity`, A5, A3. 구매하기 시 결제 화면에 상품·수량 전달 방식(상태/쿼리) **미정** |
| `/ec/cart` · `EcCartRoute` | `EcCartPage` | `items: EcCartItem[]`, `summary: EcPriceSummary|null`, `isLoading`, `isOrdering`, `tabBar{value:"cart",cartCount}` | `onQuantityChange(itemId,q)`, `onRemove(itemId)`, `onOrder`→결제 이동(연결됨), `onItemClick(productId)`(연결됨), `onShop`(연결됨) | A6·A7·A8. 선택 주문(체크박스)은 피그마에 없어 전체 주문으로 구현 |
| `/ec/checkout` · `EcCheckoutRoute` | `EcCheckoutPage` | `items: EcOrderLine[]`, `summary`, `values{recipient,phone,zipCode,address,addressDetail,memo}`, `errors`, `paymentMethod`, `isLoading`, `isSubmitting` | `onChange(field,value)`, `onAddressSearch`(**미정**), `onPaymentMethodChange`, `onSubmit` → A11 성공 시 `ecRoutes.orderComplete(orderId)`로 replace 이동 | A10(`defaultShipping`으로 폼 초기값), A11. 필수값·전화번호 형식 검증 규칙 **미정** |
| `/ec/orders/:orderId/complete` · `EcOrderCompleteRoute` | `EcOrderCompletePage` | `completion: EcOrderCompletion`, `isLoading` | `onViewOrders`, `onContinueShopping`(연결됨) | A12 또는 A14 |
| `/ec/orders` · `EcOrderListRoute` | `EcOrderListPage` | `orders: EcOrderListItem[]`, `isLoading`, `periodLabel?`("최근 6개월 주문 내역" — 기간 정책 **미정**), `page`, `pageCount` | `onOrderClick(id)`(연결됨), `onPageChange` | A13: `itemCount-1→extraItemCount`, `orderedAt→YYYY.MM.DD`, `thumbnailUrl→imageUrl`. page 쿼리는 `/manage` 패턴(1페이지 생략) |
| `/ec/orders/:orderId` · `EcOrderDetailRoute` | `EcOrderDetailPage` | `order: EcOrderDetail`, `isLoading` | `onCopyOrderNumber`(clipboard 연결됨, 완료 안내 없음), `onTrackDelivery`(**미정**), `onProductClick`(연결됨) | A14: `tracking{location,message}→{title:"현재 위치: {location}", description:message}` |
| `/ec/support` · `EcSupportRoute` | `EcSupportPage` | `faqs: EcFaqItem[]`, `keyword`, `isLoading`, `tabBar{value:"support",cartCount}` | `onKeywordChange`, `onKeywordSubmit`, `onMenuClick(menu)`(화면 없음), `onMoreFaqClick`(화면 없음), `onInquiryClick`(연결됨) | A15 (피그마 "TOP 5" 개수 정책 **미정**) |
| `/ec/support/inquiry/new` · `EcInquiryWriteRoute` | `EcInquiryWritePage` | `values{type,title,content}`, `errors{type,title,content}`, `attachments: EcAttachment[]`, `isSubmitting` | `onTypeChange`, `onChange`, `onAddAttachment`, `onRemoveAttachment(id)`, `onSubmit` | A16·A17. 첨부 파일 선택은 기존 `pubsub.publish("open-image-upload-popup", …)`(`ImageUploadPopup`, JPG·PNG 검사 포함) 재사용 제안. 미리보기 URL은 같은 출처 `blob:` URL이면 `Thumbnail` 출처 정책을 통과한다. 제출 후 이동 위치 **미정** |

- 하단 탭 이동: `src/pages/ec/model/useEcTabNavigation.ts`(카테고리는 이동 없음). `cartCount`는 A9를 공통 hook으로 만들어 탭 화면 4곳에 전달.
- 완료 기준: 각 route에서 로딩→데이터→빈 상태 전환, mutation 후 관련 query 무효화(장바구니 변경 → 장바구니·개수), controller 테스트. `npm run lint`·`npm run test`·`npm run build`.

## 미확정 사항 · 사용자에게 할 질문

1. EC API 명세(endpoint, envelope, 필드명, ID 체계, 상태 코드) 제공 여부와 시점
2. 바로 구매(상품 상세 → 결제)와 장바구니 구매의 결제 화면 진입 데이터 전달 방식
3. 주문 내역 조회 기간(최근 6개월 등)·페이지 크기, FAQ 노출 개수
4. 주문/결제 폼 필수값·검증 규칙, 기본 배송지 제공 여부
5. 1:1 문의 첨부 업로드 방식(선업로드 id / multipart)과 제출 후 이동 화면
6. 장바구니 담기 성공 피드백(toast/dialog) 방식
7. MSW mock 허용 범위(허용 시 어떤 데이터로 확인할지)

## 협업 순서와 Git 통합

- 공유 공간 순서: UI 변경 commit(완료, `b52a5bc`) → logic 세션 진입 → 연결 작업.
- 통합: `feature/ec-buyer-ui` → 직접 부모 `sy-main`. 하위 logic 브랜치를 분리하면 자식부터 `feature/ec-buyer-ui`로 먼저 통합.
- 승인된 Git 작업: 브랜치·worktree 생성(완료), UI commit(완료). 미승인: merge.
- 산출물 책임: 이 세션 owner(`plan.md`, `final-summary.md`), logic 세션은 자기 세션 산출물 작성.

## 관련 경로와 스킬

- 정책: `task-role-routing/references/logic.md`, `git-branch-strategy`, `documentation`, `ui-library`
- 참고 구현: `src/features/inquiry/**`, `src/pages/manage/**`
- 라이브러리 초안: `unknown/skill-drafts.md`

## 명령어 및 결과

- `npm run lint` → 통과
- `npm run build` → 통과(기존 500kB 청크 경고만)
- `vitest run`(EC·신규 shared·routing 20건) → 통과
- 전체 `vitest run --maxWorkers=4` → 13 failed / 823 passed. 13건은 `sy-main` 기본 checkout에서도 같은 목록으로 실패(citizen MSW·vote 관련, 기존 문제)
- 전체 `vitest run`(기본 worker) → `MeetingReservationRoutes` 16건 추가 실패. 단독·`src/pages` 범위·worker 4에서는 통과 → 병렬 부하에서의 시간 의존 실패로 판단

## 실행하지 않은 검증

- 브라우저 실제 렌더링·시각 QA(정책상 요청 시에만)
- 실기기 스와이프 확인

## 다음 조치

1. logic 세션: `b52a5bc`에서 진입해 위 질문 1~7 확인 후 API·hook·controller 연결
