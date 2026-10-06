# EC 구매자 UI 최종 요약

## 결론

피그마 "구매자" 9개 화면을 `/ec/*` 라우트의 props 기반 화면으로 구현했다. 공용 요소 12종은 `src/shared/ui`에 추가하고 3종은 확장했다. lint·build와 신규 테스트 20건은 통과했다. API 연결은 logic 세션으로 인계한다(`handoff.md`). 변경은 `b52a5bc`로 commit했다.

## 작업 위치

- `feature/ec-buyer-ui` (부모 `sy-main` 3e30393)
- `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-user-ui-worktree/ec-buyer-ui`

## 화면 ↔ 경로

| 피그마 | 경로 | 컴포넌트 |
| --- | --- | --- |
| 아산모아 마켓 | `/ec` | `features/ec/ui/market/EcMarketPage.tsx` |
| 상품 상세 | `/ec/products/:productId` | `features/ec/ui/product/EcProductDetailPage.tsx` |
| 장바구니 | `/ec/cart` | `features/ec/ui/cart/EcCartPage.tsx` |
| 주문/결제 | `/ec/checkout` | `features/ec/ui/checkout/EcCheckoutPage.tsx` |
| 주문 완료 | `/ec/orders/:orderId/complete` | `features/ec/ui/order/EcOrderCompletePage.tsx` |
| 주문 내역 | `/ec/orders` | `features/ec/ui/order/EcOrderListPage.tsx` |
| 주문 상세 | `/ec/orders/:orderId` | `features/ec/ui/order/EcOrderDetailPage.tsx` |
| 고객센터 | `/ec/support` | `features/ec/ui/support/EcSupportPage.tsx` |
| 1:1 문의 작성 | `/ec/support/inquiry/new` | `features/ec/ui/support/EcInquiryWritePage.tsx` |

## 주요 결정

- 색: `.ec-app` 범위에서 `--accent`·`--focus`를 `#135bec`(주문/결제)로 재정의했다. 마켓의 갈색, 장바구니의 보라, 완료 화면의 금색, 상세 가격의 빨강을 모두 통일했고 DESIGN.md에 기록했다.
- 영역 구성: 각 영역을 `SectionBlock` 카드로 분리했다(장바구니 기준).
- 하단 바: `BottomDock` 안에 `BottomActionBar`와 `BottomTabBar`(장바구니 기준: 텍스트 라벨, 강조색, 점)를 둔다. 탭 화면은 마켓·장바구니·주문내역·고객센터 4곳이다. 상품 상세는 액션 바만 둔다(하단 이중 바 방지).
- 이미지: 상품 상세는 embla 캐러셀로 스와이프한다. "3D 보기"는 "상세 보기"로 바꿔 전체 보기 모달(스와이프·contain)을 연다. 마켓 카드는 같은 `ImageFrame`을 쓰고, 미리보기는 주문 상세 기준 `Thumbnail`로 통일했다(주문 내역의 원형 이미지도 교체).
- 피그마 보정:
  - 마켓 3열 → 2열
  - 담기 버튼을 카드 우측 하단의 40px 원형 아이콘으로 축소
  - 주문 내역의 "상세보기" 풀폭 버튼 → 카드 전체 클릭 + chevron
  - 상품 특징 4개 카드 → 한 영역의 체크 목록
  - "¥ 5,000 결제하기" → "5,000원 결제하기"
  - 구매 수량 제목·라벨 중복 제거
  - 주문/결제에 주문 상품 영역과 배송 메모 추가
- 미정 동작(카테고리 탭, 알림, FAQ 더 보기, 빠른 메뉴, 주소 검색, 배송 조회, 결제)은 콜백만 연결했다.

## 변경 파일

- 수정:
  - `DESIGN.md`
  - `package.json`, `package-lock.json`
  - `src/app/routing.ts`, `routing.test.ts`
  - `src/shared/ui/content/{content.css, section-block.tsx}`
  - `src/shared/ui/no-results/no-results.tsx`
  - `src/shared/ui/screen/{page-screen.tsx, screen.css}`
- 신규:
  - `src/shared/config/ecRoutes.ts`
  - `src/shared/ui/{accordion, bottom-tab-bar, chip-group, choice-card-group, image-carousel, image-gallery-modal, progress-steps, quantity-stepper, thumbnail}/`
  - `src/shared/ui/content/info-list.tsx`
  - `src/shared/ui/screen/{top-app-bar, bottom-dock}.tsx`
  - `src/features/ec/**`, `src/pages/ec/**`

## 검증

- 포맷 트리거(`formatting.py apply`) 실행
- `npm run lint`: 통과
- `npm run build`: 통과(기존 청크 크기 경고)
- 신규·EC 관련 테스트 20건: 통과
- 전체 테스트(`--maxWorkers=4`): 13건 실패. `sy-main` 기본 checkout에서 실패하는 목록과 같다(citizen MSW·vote, 기존 문제).
- 전체 테스트(기본 worker): `MeetingReservationRoutes` 16건이 추가로 실패한다. 단독 실행과 worker 4 실행에서는 통과하므로 부하에 따른 시간 의존 실패로 판단했다.

## 미완료

- API·DTO·hook·폼 검증 연결 → logic 세션(`handoff.md`)
- merge → 사용자 Git 승인 필요

## 2차: logic 연결 후 UI 후속 (2026-09-29)

- 위치: `feature/ec-buyer-ui`. logic 세션(Codex `ec-buyer-logic`)의 미커밋 변경 24개 경로를 사용자 승인으로 `5ba02b6`에 commit한 뒤 작업했다.
- 마켓 페이지 이동: `EcMarketPage`에 `page`·`pageCount`·`onPageChange`를 추가하고 기존 `Pagination`을 연결했다.
- 검색 버튼: 공용 `TextInput`에 `endContent`를 추가하고, 마켓·고객센터 검색창 안에 `type=submit` "검색" 버튼을 두었다.
- 조회 실패 상태: 공용 `shared/ui/load-error`를 추가했다. 마켓·상품 상세·장바구니·주문/결제·주문 완료·주문 내역·주문 상세·고객센터 FAQ·문의 내역에 `loadError`·`onRetry`를 받아 빈 목록 대신 "불러오지 못함 + 다시 시도"를 보여 준다. 오류 상세는 기존 전역 오류 알림이 전달한다. 담기 실패 같은 다른 오류가 이미 받은 목록을 가리지 않도록, route에서 데이터가 없을 때만 실패로 본다.
- EC 문의 내역: `/manage`의 `InquiryListPage`를 쓰던 자리를 `features/ec/ui/support/EcInquiryListPage.tsx`(EC 앱바·탭 바·강조색)로 교체했다. 고객센터에 "내 문의 내역" 진입 버튼을 추가했다.
- 검증:
  - 포맷 트리거 실행(`text-input.css`는 포맷터가 파일 전체를 여러 줄 형식으로 바꿈)
  - lint 통과, build 통과
  - EC·shared·routing 테스트 62건 통과
  - 전체 테스트(`--maxWorkers=4`): 13건 실패, 기존 citizen 실패와 같은 목록
- 남은 항목: 주문 생성·결제, 주소 검색, 배송 조회, 사진 첨부, 문의 상세(계약 미정). 주문/결제·주문 완료 controller에 `refetch`가 없어 다시 시도 버튼은 표시하지 않는다(logic 보완 후보).

## 3차: 영역 제목 구분선 (2026-09-29)

- 피그마 45:2008 "결제 상세" 기준: 카드 안쪽 폭 284px, 제목 24px + 아래 8px 뒤 1px 선(#f3f4f6), 선 아래 16px 뒤 내용.
- `.ec-app .cp-section > .cp-section__title|__head`에 `padding-bottom: 8px; border-bottom: 1px solid var(--clr-cool-gray-100); margin-bottom: 16px`을 적용했다. 새 색은 만들지 않고 가장 가까운 기존 토큰을 썼다. 주문 상세 진행 단계의 중복 상단 여백(6px)을 제거하고 DESIGN.md에 기록했다.
- 검증: 포맷, lint, EC·shared 테스트 65건, build 통과. 사용자 승인으로 `3511f64 style: EC 영역 제목 아래 구분선 추가`(3 files)에 commit했다.

## Git 처리

- 보호 실행기 승인으로 `feature/ec-buyer-ui`에 commit `b52a5bc feat: EC 구매자 화면과 공용 UI 컴포넌트 추가`(72 files, +4089/−6)를 만들었다. commit 후 worktree는 clean이다. `sy-main`과 기본 checkout의 `README.md`는 변경하지 않았다.
- logic 세션 변경 24개 경로를 사용자 승인(A 방식)으로 `5ba02b6 feat: EC 구매자 예상 API와 화면 controller 연결`(24 files, +1477/−77)에 commit했다. 내용은 수정하지 않았다.
- 2차 UI 후속 변경을 사용자 승인으로 `f6273c4 feat: EC 페이지 이동·검색 버튼·조회 실패 상태와 문의 내역 화면 추가`(19 files, +452/−33)에 commit했다. `sy-main` 병합은 하지 않았다.
- 중앙 정책 스킬 문서 → 초안 `unknown/skill-drafts.md`
- `docs/routing.md`: 기본 checkout의 ignored 로컬 파일이라 이번 브랜치에서는 갱신하지 않았다(EC 경로는 DESIGN.md·handoff에 기록).
