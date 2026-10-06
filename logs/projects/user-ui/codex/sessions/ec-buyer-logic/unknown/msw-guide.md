# EC MSW 개발 안내

2026-09-30 갱신: 공통 포맷·lint·MSW 포함 대상 테스트 59개·build가 통과했다. 아래의 정책 차단·미실행 표현은 이전 상태이며 자동 검증은 완료됐다. 브라우저에서 직접 가로채기 확인은 수행하지 않았다.

실제 API가 없어 사용자가 승인한 예상 DTO를 기반으로 만든 개발용 응답이다. 서버 명세·가격·재고·배송 정책 확정 자료가 아니다. 현재 코드의 실행 검증은 정책 훅 차단으로 남아 있다.

## 실행

후속 사용자 보고로 MSW 활성화 누락을 확인했다. 기존 .env에는 API 주소만 있고 VITE_API_BASE_URL_STATUS가 없어 일반 npm run dev 실행 시 worker가 시작되지 않았다. 이 worktree에 Git 제외 파일 .env.development.local을 추가하여 VITE_API_BASE_URL_STATUS=dev를 설정했다. 이미 실행한 개발 서버는 재시작하고 페이지를 새로고침한다.

Vite loadEnv로 실제 파일 해석 결과를 조회했다: development는 dev, production은 unset. 이 확인은 활성화 설정만 검증한 것이며 브라우저 요청 가로채기·MSW 통합 테스트를 통과했다는 의미는 아니다.

현재 worktree에서는 npm run dev만으로 개발용 MSW가 활성화된다. 아래 명령은 환경변수를 명시해서 실행하는 방법이다. 로컬 설정은 Git에 포함되지 않으므로 다른 worktree에서는 별도로 설정해야 한다.

작업 위치: /Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-user-ui-worktree/ec-buyer-ui

```sh
VITE_API_BASE_URL_STATUS=dev npm run dev
```

기존 startMocks가 dev 값일 때만 worker를 시작한다. EC 핸들러는 app/mocks/browser.ts에 기존 citizen·meeting 핸들러와 함께 등록했다. 기존 public/mockServiceWorker.js와 msw 패키지를 사용하며 재설치나 worker 재생성은 필요 없다. /ec에서 시작한다. dev 외 값에서는 기존처럼 MSW를 시작하지 않는다.

## 동작과 샘플

- 기존 API가 보내는 /ec 경로를 가로챈다. API baseURL의 /api 같은 접두사도 기존 handler 패턴과 같은 wildcard 방식으로 처리한다.
- 상품·주문·문의 각 12개: 첫 페이지 10개, 두 번째 2개. FAQ 6개를 전부 반환한다.
- 카테고리 응답은 뷰티·패션·생활. 전체는 기존 controller가 추가하고 categoryId를 보내지 않는다.
- 상품 7은 UI 예시의 영양 크림(5,500원, 원가 8,000원), 상품 12는 품절 샘플이다.
- 이미지 배열은 비어 있고 thumbnailUrl은 null이다. 기존 UI placeholder를 사용하며 외부 이미지 요청은 만들지 않는다.
- 장바구니 초기값은 상품 1 한 개와 상품 2 두 개다. 같은 상품 담기는 수량을 합산한다. count는 항목별 quantity의 합이다.
- 예시 재고 20·최대 구매 수량 10과 품절 상태를 검증한다. 수량 초과는 409, 없는 항목은 404, 잘못된 요청은 400이다.
- 장바구니·checkout·과거 주문 샘플 배송비는 0이다. 금액은 단가 × 수량으로 계산하며 실제 배송비 정책은 아니다.
- 찜·장바구니·문의 작성 결과는 같은 핸들러 인스턴스의 후속 조회에 반영한다. localStorage나 실 서버에 저장하지 않으며 새로고침 시 초기화한다.
- checkout의 반복 cartItemIds를 지원하며 선택한 항목만 합산한다. 바로 구매와 장바구니 파라미터 혼합은 거부한다.
- 문의는 필수 제목·내용에 길이 상한을 추가하지 않는다. 작성 후 OPEN 상태로 목록 첫 항목에 추가한다. 내용 상세 조회·첨부 API는 없다.
- EC mock은 개발 중 토큰을 검사하지 않는다. 기존 애플리케이션 인증 흐름·인터셉터·라우트 권한을 변경하지 않으며 운영 인증 정책도 정의하지 않는다.
- 주문 완료 조회는 샘플 과거 주문을 반환한다. 결제·주문 생성, 주소 검색, 배송 추적, 사진 첨부 요청은 구현하지 않았다.

## 테스트와 재개

features/ec/testing.ts에서 createEcHandlers를 내보낸다. 각 호출은 독립 상태를 만든다. 기본 성공 외 {empty:true}, {failReads:true}, 날짜 고정용 {now:()=>Date}를 지원한다. empty에서도 카테고리는 유지한다. failReads는 정상 항목 조회에 503을 반환하며 mutation 실패 시나리오는 잘못된 요청·없는 항목·수량 초과로 검증한다.

공통 포맷을 먼저 정상 완료한 뒤 해당 worktree에서 실행한다.

```sh
npm run lint
npm run test -- src/features/ec src/pages/ec src/app/routing.test.ts src/app/mocks/startMocks.test.ts --maxWorkers=4
npm run build
```

테스트는 실제 Axios → MSW → 공통 ApiClient → EC parser 흐름을 사용하며 상품 필터·페이지, 찜, cart CRUD·금액, 두 checkout 형태, 주문 상태·완료, FAQ, 문의 생성·페이지, 요청 오류, 빈 목록·503, 상태 초기화를 확인한다. 11개 테스트를 작성했으나 아직 실행하지 않았다.

기존 전체 테스트의 citizen/MSW·투표 실패 이력은 이전 최종 요약에 있다. 현재 변경의 검증 성공을 대신하지 않는다. 실제 브라우저 시각 QA는 요청되지 않아 수행하지 않았다.
