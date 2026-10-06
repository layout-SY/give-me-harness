# EC 판매자 임시 API 계약

실제 서버 명세가 없는 상태에서 사용자 위임으로 설계한 개발용 계약이다. UI 선행 View props에 맞춰 DTO를 작성했으며 서버 확정 계약으로 간주하지 않는다.

## 실행과 경계

- 작업 위치: `feature/ec-seller-ui` worktree.
- `.env.local`에 `VITE_ENVIRONMENT=dev`를 설정했다. 이 worktree에서 `npm run dev` 실행 시 기존 MSW worker가 시작된다.
- API base URL은 기존 Axios 설정을 그대로 사용한다. 별도 base URL이 없으면 동일 origin이다. 기존 로그인·인증 흐름은 변경하지 않았다.
- MSW는 `/ec/*` 경로에 등록한다. HTML 문서 탐색은 통과시키므로 같은 경로의 SPA 페이지와 충돌하지 않는다.
- production 환경 활성화 규칙은 변경하지 않았다. MSW를 끄면 실제 API 호출이므로 서버 구현 전에는 해당 환경에서 성공을 보장하지 않는다.
- handler 인스턴스 메모리에 저장한다. 새로고침 시 초기화한다. 반품·알림 발송·배송 추적 등 외부 서비스는 호출하지 않는다.

## 공통 계약

- 응답 envelope: 기존 `ApiResponseDto<T>`의 `{ code: "SUCCESS", message: "성공", data }`.
- 오류: HTTP 400(입력), 404(대상 없음), 409(잘못된 상태 전이), `{ code: "EC_<status>", message, data: null }`.
- DTO schema로 요청을 검증하고, 공통 `unwrapApiResult` 이후 schema 검증을 통과한 응답만 Query에 저장한다. query signal은 Axios까지 전달한다.
- 문자열 ID는 path segment로 인코딩한다. 금액은 원 단위 숫자, 입력 중 가격·재고는 UI에서 문자열이다. 일시는 ISO 8601, 기간 필터는 UTC 날짜 `YYYY-MM-DD` 양 끝 포함.
- 목록: 공통 `items/total/page/size`, 기본 page=1·size=20, size 최대 100. status=ALL 기본. counts는 검색·기간·카테고리 필터 후 상태 필터 적용 전의 개수다.
- 상품 검색: 상품명 keyword·categoryKey·status. 주문: 기간·keyword·searchBy(ORDER_NUMBER/BUYER/PRODUCT)·sort(LATEST/OLDEST)·status. 문의: 제목 keyword·typeKey·기간·status.
- 폼 mapper는 허용 필드만 옮긴다. 서버 데이터와 입력 draft를 분리하고, 상세 ID 변경 시 controller를 remount한다.

## Endpoint

| Method | 경로 | 요청 / 응답 |
| --- | --- | --- |
| GET | /ec/metadata | categories·couriers·inquiryTypes 선택지 |
| GET | /ec/products | 목록 query → 상품 rows·summary·counts·페이지 |
| POST | /ec/products | 상품 요청 DTO → { id } |
| GET | /ec/products/:id | { productId, values } |
| PUT | /ec/products/:id | 상품 전체 요청 DTO → { id }; SKU 변경 불가 |
| DELETE | /ec/products/:id | { id } |
| GET | /ec/orders | 목록 query → 주문 rows·counts·페이지 |
| GET | /ec/orders/:id | 주문·items·shipment·recipient·payment·memo |
| POST | /ec/orders/:id/actions | { action: PREPARE/DELIVER/CANCEL } → { id } |
| PUT | /ec/orders/:id/shipment | { courierKey, trackingNumber } → { id } |
| PATCH | /ec/orders/:id/memo | { memo } → { id } |
| GET | /ec/inquiries | 목록 query → 문의 rows·counts·페이지 |
| GET | /ec/inquiries/:id | 문의·관련 주문 nullable·동일 고객 최근 3건·답변 |
| PUT | /ec/inquiries/:id/answer | { content, isNotifyBuyer } → { id } |
| GET | /ec/answer-template | { content }; 단일 예시 답변 |
| GET/PUT | /ec/seller/profile | 판매자 정보 조회 / 폼 저장 → { id } |
| GET | /ec/seller/application | { application: 신청 정보 또는 null } |
| POST | /ec/seller/application | 브랜드·카테고리·약관 동의 → { id } |
| POST | /ec/seller/logo | multipart file → { imageId, url, fileName }; MSW URL은 data URL |
| GET | /ec/settlement/analysis | 기간 query → 확정 매출·누적 판매 건수 |
| GET | /ec/settlement/sales | 기간·페이지 → 일별 집계·KPI |
| GET | /ec/settlement/summary | 기간 → 누적 KPI·카테고리 비율·상품 순위 |
| GET | /ec/orders/export | 적용 필터 전체 주문 → { fileName, content } |
| GET | /ec/inquiries/export | 적용 필터 전체 문의 → { fileName, content } |
| GET | /ec/settlement/sales/export | 기간 전체 일별 집계 → { fileName, content } |
| GET | /ec/settlement/summary/export | 기간 상품 순위 → { fileName, content } |

다운로드는 Excel에서 열 수 있는 UTF-8 BOM CSV다. XLSX 생성은 포함하지 않는다. CSV 값은 인용·수식 시작 문자 이스케이프를 적용한다. 페이지 크기와 관계없이 적용 필터의 전체 데이터를 내려준다.

## 입력과 상태

- 상품: 상품명 1~100자, 카테고리 필수, 가격·재고는 0 이상 정수. 정상가 공란은 null. 이미지 최대 4개, 대표 ID는 images 중 하나 또는 null. SKU는 생성 때만 편집.
- 상품 상태: ON_SALE/STOPPED/SOLD_OUT/PENDING/REJECTED. 예시 재고 부족 기준은 1~5개.
- 주문: RECEIVED → PREPARING(PREPARE) → SHIPPED(송장 입력) → DELIVERED(DELIVER). CANCEL은 RECEIVED/PREPARING에서만 허용. MSW가 409로 잘못된 전이를 거절한다.
- 송장: metadata에 있는 택배사, 숫자·하이픈 6~30자. 메모 2000자 이하.
- 문의: WAITING/ANSWERED. 답변은 trim 후 1~1000자. 저장 시 ANSWERED 전이. isNotifyBuyer는 저장하지만 실제 알림은 발송하지 않는다.
- 판매자 신청: 브랜드명·설명·카테고리·약관 동의 필수. 설명 최대 200자. 저장 시 PENDING 신청을 생성한다.
- 프로필: 브랜드명·연락처 필수, 설명 최대 500자. 로고는 5MB 이하. 신청 JPG/PNG, 설정 JPG/PNG/GIF.
- 매출 예시는 주문·환불 기록으로 계산한다. 배송 완료·미환불 결제액을 확정 매출로 집계한다. 취소와 반품을 구분하며, 반품률은 반품 기록/조회 기간 전체 주문이다. 비교 기간은 아직 정의하지 않아 changeRate·differenceAmount·comparisonLabel은 null이다.

## 보류 기능

상품 이미지 추가 팝업, 상품 옵션 편집, 수령인 수정, 약관·개인정보·도움말 콘텐츠, 배송 추적 화면, 고객 문의 이력 전체 화면, 카테고리 상세는 추가 UI/콘텐츠가 없어 보류했다. 해당 callback은 명시적 `ecDeferred`로 남겼다. 기존 대시보드·차트 보류도 유지한다.

## 구현 위치

- DTO: `src/entities/ec-seller/api/ec-*.dto.ts`
- API: `src/entities/ec-seller/api/ec.api.ts`
- 서버 상태: `src/entities/ec-seller/model/ec-{query,mutation}-options.ts`
- controller: `src/pages/ec-*/hook/`
- MSW: `src/mocks/ec-seller.handlers.ts`, `ec-seller.fixtures.ts`, `ec-settlement.model.ts`
- 테스트: `tests/ec-seller-api.test.mjs`
