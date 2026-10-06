# EC 구매자 MSW → Logic 검증 인계

## 최신 상태 — 2026-09-30 부모 병합·README 복원 완료

- 사용자 승인으로 feature/ec-buyer-ui를 직접 부모 sy-main에 ff-only 병합했다. 두 브랜치 HEAD는 55194e6c2ac6e2189fa11be2d5741bac6c277a2f다.
- 병합 위치: /Users/okand/SynologyDrive/asan-metaverse-user-ui. 보호 실행 operation 831402317ab843499193406cc255ac5d는 retained, verification_passed=true이며 target npm run lint·npm run build 모두 종료 코드 0이다.
- 병합 전 대상 테스트 59개와 공유 UI 테스트 18개, 총 77개 통과. 전체 테스트·실 브라우저·실 서버 검증은 추가 실행하지 않았다.
- source branch/worktree와 Git 제외 환경설정을 유지했다. push하지 않았다. 현재 sy-main은 origin/sy-main보다 5개 커밋 앞서 있다.
- 부모 README.md의 기존 라우팅 문서 링크 한 줄은 사용자 승인으로 보관한 뒤 복원했다. 보호 실행 operation d5416aecfea8cb1ef638f3e18cf9d597은 done이다. target의 유일한 미커밋 변경은 기존 README.md 한 줄이며 source 작업 트리는 깨끗하다.
- 복원된 README SHA-256은 병합 전과 같은 03deaf663348c0480738e6bc0ba342a2542012511c9af623a50d74b169ff41bd다. 백업 stash 765bb7dcd582fc5ecd464045bbbfb41fa22178c2는 유지했다.
- requested_roles / confirmed_roles / completed_roles: logic / logic / logic. next_role: 후속 요청 시 결정. 승인된 병합·검증·기존 변경 복원이 모두 완료됐다.

## 최신 상태 — 2026-09-30

공통 포맷·lint·대상 테스트 59개·build·git diff --check를 통과하고 사용자 승인 후 55194e6으로 커밋했다. 사후 Git 작업 트리는 깨끗하다. 아래 9월 29일의 검증 차단과 새 세션 권고는 과거 상태다.

- project/worktree: 기존 asan-metaverse-user-ui / /Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-user-ui-worktree/ec-buyer-ui
- branch/HEAD: feature/ec-buyer-ui / 55194e6c2ac6e2189fa11be2d5741bac6c277a2f. 직접 부모 sy-main.
- requested_roles / confirmed_roles / completed_roles: logic / logic / logic (MSW 소스 및 자동 검증).
- next_role: 후속 요청 시 결정. 승인된 stage·commit은 완료했으며 merge·push는 범위 밖.
- 포맷 해소: 기존 recovery 완료·활성 writes 없음·EcRoutes.tsx가 HEAD와 동일함을 확인하고 내용을 보존해 정상 저장했다. 공통 formatter가 성공했으며 EcRoutes.tsx의 최종 Git diff는 없다.
- 검증: lint 통과, EC·라우팅·startMocks 6개 파일 59개 테스트 통과(새 MSW 11개), build 통과(기존 청크 크기 경고), git diff --check 통과.
- staged·unstaged·untracked 변경 없음. browser.ts 및 mocks 3개·testing.ts 총 5개를 커밋했다. 보호 실행 operation f86621d600bdf48f3b29d5c410f8eff7은 done이다.
- Git 제외 .env.development.local에는 VITE_API_BASE_URL_STATUS=dev가 있다. 이 파일은 커밋하지 않는다.
- 브라우저 시각 QA·실 서버 검증·전체 테스트 재실행은 수행하지 않았다. HTTP 계약은 실제 Axios를 쓰는 MSW 통합 테스트로 확인했다.
- 이전 안내의 “이 세션에서는 해결 불가” 판단을 정정한다. 정상 쓰기 확인 절차와 공통 포맷으로 재개했으며 중앙 정책을 수정하지 않았다.

## 최신 인계 — 2026-09-29 MSW 후속 요청

### 후속 진단: 실제 실행에서 MSW 미활성화

- 사용자가 요청을 가로채지 못한다고 보고하여 활성화 조건을 조사했다.
- 이 worktree의 .env에는 VITE_API_BASE_URL만 있었으며 VITE_API_BASE_URL_STATUS는 없었다. startMocks는 값이 dev가 아니면 worker를 시작하지 않는다.
- Git 제외 파일 .env.development.local에 VITE_API_BASE_URL_STATUS=dev를 추가했다. 기존 API 주소·인증·라우팅 코드는 변경하지 않았다.
- Vite loadEnv의 실제 조회 결과: development=dev, production=unset. 개발 서버 재시작·브라우저 새로고침이 필요하다.
- 이 설정 조회는 소스의 포맷·lint·test·build를 대체하지 않는다. 해당 검증과 실제 브라우저 가로채기 확인은 여전히 남아 있다.
- 사용자 확인: 같은 ec-buyer-ui worktree / feature/ec-buyer-ui에서 http://localhost:2426/ec 접속. GET https://api.oasis.shovvel.com:8443/ec/products?page=1&size=10이 실 서버 404를 반환했다. MSW 콘솔 메시지는 전달받지 못했다.
- 이 실행 환경에서는 localhost:2426에 일반·권한 상승 HTTP 조회 모두 연결하지 못해 실행 중 서버의 설정과 worker 제공 상태를 직접 확인하지 못했다. 사용자의 서버 재시작·새로고침 후 확인이 남았다.

**MSW 소스 연결·테스트 작성 완료, 정책 훅 차단으로 포맷과 실행 검증 미완료.** 아래 기존 Logic → UI 인계는 이전 단계 이력이며 이 절이 최신 상태다.

- requested_roles / confirmed_roles: logic / logic (inject)
- completed_roles: 없음. 이번 MSW 검증이 남아 있다.
- next_role: logic. 새 assignment로 같은 기존 worktree에서 순차 재개한다.
- 사용자 승인: 실제 API가 없으므로 예상 계약 기준 MSW 연결. 기존 DTO 추측 승인과 결제·주소 검색·배송 추적 제외 결정 유지.
- project·저장소: asan-metaverse-user-ui / /Users/okand/SynologyDrive/asan-metaverse-user-ui
- 실제 및 목적지 worktree·실행 디렉터리: /Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-user-ui-worktree/ec-buyer-ui
- branch·HEAD: feature/ec-buyer-ui / f6273c4b8571e8d4f0ba8f532e117eeaa7c80bf1
- 직접 부모: sy-main. 별도 worktree 생성·branch 전환 불필요.
- 기존 커밋: 5ba02b6 Logic, f6273c4 페이지네이션·검색 버튼·오류/재시도·EC 문의 목록 UI. 이 구현을 보존한다.
- staged: 없음. unstaged: src/app/mocks/browser.ts. untracked: src/features/ec/mocks/fixtures.ts, handlers.ts, handlers.test.ts, src/features/ec/testing.ts.
- 세션 산출물 경로는 .codex/logs/sessions/ec-buyer-logic 유지. 다른 host 로그는 읽기 전용.

### 재개할 작업

1. 위 위치에서 HEAD·status·미커밋 소스를 다시 확인한다. MSW 구현을 되돌리지 않는다.
2. policy-task-role-routing, policy-git-branch-strategy, policy-coding-convention, recipe-api-authoring 및 transport-contracts를 적용한다.
3. 기존 app/mocks/startMocks.ts의 dev 활성화와 browser.ts 등록을 유지하며 [MSW 실행 안내](unknown/msw-guide.md)의 11개 통합 테스트를 실행한다.
4. 새 세션에서 포맷 대상 추적도 확인하고 현재 수정 파일 5개에 공통 포맷 트리거를 정상 적용한다. 이 세션의 포맷은 실패했다.
5. lint → EC·라우팅·startMocks 대상 test → build를 실행한다. 실패 시 관련 MSW 구현만 보완하고 결과를 기록한다.
6. 현재 API는 예상 계약이며 mock 통과를 실 서버 검증으로 간주하지 않는다. 승인되지 않은 Git 변경은 하지 않는다.

### 차단 근거와 중앙 정책 후속

- formatting.py apply가 PreToolUse에서 “결과 미확인 코드 쓰기를 먼저 확인한 뒤 포맷하세요.”로 거부됐다. 이후 테스트·build는 우회 실행하지 않았다.
- 과거 recovery 7c19d02ada7c456287774bafd037bc9b는 stage:done이다. 기존 종료 기록을 다시 승인할 필요는 없다.
- formatting/v1/calls/1879c356804642ebe98d5d49d0b9bd9afd7186ff948a8f3ebd4bbf7e29e89d9e.json에 과거 exec-eddc9579-5267-4562-a18e-bb76a4f95850 기록이 남아 있다.
- 현재 assignment의 EcRoutes.tsx 상태는 formatted이나 최신 writer는 UI assignment de67eb2a5f17423c97fb97a6ea77dcbb의 toolu_01QMzWxuD3BPV4LYXCZTX3CU다.
- 바인딩된 중앙 formatting.py의 unconfirmed_calls는 복구된 기록을 제외할 때 현재 assignment의 token과 전역 writer token 일치를 요구한다. 이후 다른 세션이 파일을 수정하면 과거 실패가 재활성화되는 구조다.
- 이번 신규 MSW 5개 파일의 쓰기는 pending으로 정상 확인되어 있다. 새로운 patch 실패가 아니다.
- 해결을 위해 EcRoutes.tsx를 불필요하게 다시 쓰거나 중앙 state·정책을 직접 편집하지 않았다.
- 중앙 수정 시 필요한 회귀 사례: 실패 도구 기록 → 승인 복구 → 정상 수정·포맷 → 다른 assignment의 같은 파일 정상 수정·커밋 → 원 assignment에서 다른 기능 포맷. 이 마지막 단계가 재차 차단되지 않아야 한다.
- 중앙 정책 수정은 해당 저장소의 별도 세션 범위다. 새 정책 적용은 새 inject assignment가 필요하다.

---

# 이전 단계: EC 구매자 Logic → UI 인계

아래 HEAD·dirty·검증·UI 미완료 표기는 당시 이력이다. 현재 상태는 위 최신 인계를 따른다.

## 결론

승인된 예상 API·DTO·parser·query/mutation·controller와 기존 화면 연결을 구현했다. 포맷, lint, build 및 EC·라우팅 대상 테스트 41개가 통과했다. 전체 테스트는 853개 통과·13개 실패이며 실패는 이전 UI 인계에 기록된 citizen/MSW·투표 항목과 동일하다. 실제 EC 서버 명세 검증과 아래 UI 후속 작업은 남아 있다.

## 역할·작업 공간

- requested_roles: logic
- confirmed_roles: logic (inject)
- completed_roles: logic (승인한 구현·검증 범위)
- next_role: ui
- 사용자 확인: 같은 워크트리 Logic 구현, 예상 DTO 생성·기존 자산 재사용 승인. 마지막 추가 결정은 EC 전용 문의 목록·010 번호 검증 및 페이지네이션 UI 인계 요청.
- project: asan-metaverse-user-ui
- 저장소 루트: /Users/okand/SynologyDrive/asan-metaverse-user-ui
- 작업 공간 이름: ec-buyer
- 현재 위치 및 UI 목적지 worktree·실행 디렉터리: /Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-user-ui-worktree/ec-buyer-ui
- branch: feature/ec-buyer-ui
- HEAD: b52a5bc260520edf6befe238f89b164279a83def
- 직접 부모: sy-main (앞선 UI handoff의 relation create 기록)
- 인계 시점: 2026-09-29. UI → Logic → UI 순차 작업이므로 같은 기존 공간을 사용한다.
- UI는 시작할 때 최신 HEAD·status·diff를 확인하고 아래 미커밋 변경을 보존한다.
- 기본 checkout의 README.md 및 Claude 세션 로그는 다른 작업으로 보존했다.

## 사용자 확정 사항

- 실제 서버 명세 없음. UI 기반 예상 요청/응답 DTO·API 구현을 명시적으로 승인. 이 예상 계약을 서버 확정 명세로 간주하지 않는다.
- 바로 구매·장바구니 구매는 router state로 전달.
- 실제 결제·주소 검색·배송 조회는 제외. 연결 자리와 주석·문서만 유지.
- 검색은 버튼 제출 시 실행. 카테고리에 전체 포함. 목록은 페이지당 10개, 기존 페이지 패턴 재사용.
- 주문 조회 기간을 클라이언트에서 정하지 않는다. FAQ는 서버 응답 전부 표시.
- 배송지 필수, 형식 제한 없음. 휴대전화는 01012345678 및 010-1234-5678 허용.
- 기본 배송지 없음. 문의 제목·내용은 필수이며 길이 상한 없음.
- 사진 첨부는 보류. 문의 제출 후 EC 전용 목록 이동, 성공 안내는 기존 알림 모달.
- 기존 inquiry 패턴과 공통 client·페이지 DTO·표시 자산을 재사용. 향후 도메인 통합 여부는 미정.

## 실제 변경·보존 상태

새 commit과 staged 변경은 없다. 소스 24개 경로의 변경을 그대로 다음 작업에 전달한다.

- tracked 수정 6개: src/app/routing.ts, src/app/routing.test.ts, src/pages/ec/index.ts, src/pages/ec/model/presentation.ts, src/pages/ec/ui/EcRoutes.tsx, src/shared/config/ecRoutes.ts
- 신규 API 5개: src/features/ec/api/client.ts, ec.api.ts, ec.dto.ts, ec.parser.ts, ec.api.test.ts
- 신규 hook 2개: src/features/ec/hook/useEcQueries.ts, useEcMutation.ts
- 신규 model 3개: src/features/ec/model/apiResult.ts, forms.ts, queryKeys.ts
- 신규 page model 8개: src/pages/ec/model/useEcCartController.ts, useEcCheckoutController.ts, useEcControllers.test.tsx, useEcListLocation.ts, useEcMarketController.ts, useEcOrderControllers.ts, useEcProductController.ts, useEcSupportControllers.ts
- 세션 산출물: .codex/logs/sessions/ec-buyer-logic/ (ignore 대상). 다른 host의 문서는 수정하지 않았다.
- 기존 features/ec/ui/**의 표현 구현은 변경하지 않았다. 문의 목록은 기존 InquiryListPage를 pages 계층에서 재사용한다.
- 예상 API 전송·캐시·폼은 EC 전용이다. /manage 문의 API나 데이터를 합치지 않았다.

## API·controller 연결 계약

UI 선행은 controller -> UI로 맞췄다. 응답 표시 변환은 pages/ec/model/presentation.ts, 양방향 화면 계약은 같은 model의 useEc*Controller에 있다. query/mutation은 features/ec/hook에서 담당한다.

| 기능 | 예상 요청 | 반환 payload·처리 |
| --- | --- | --- |
| 상품 목록 | GET /ec/products?page=1&size=10, keyword?, categoryId? | 공통 items/total/page/size. thumbnailUrl → imageUrl |
| 카테고리 | GET /ec/categories | id/name 배열. UI 전체 값은 all, 개별 값은 category:ID로 충돌 방지 |
| 상품 상세 | GET /ec/products/:id | imageUrls → images, 재고·최대 수량으로 구매 제한 |
| 찜 | POST 또는 DELETE /ec/products/:id/wish | wished. 공통 client에 PUT이 없어 예상 추가 계약은 POST |
| 장바구니 | GET /ec/cart, GET /ec/cart/count | items/summary 및 count |
| 담기·변경·삭제 | POST /ec/cart/items {productId,quantity}; PATCH /ec/cart/items/:id {quantity}; DELETE 동일 경로 | 관련 cart/cart-count/checkout 캐시만 무효화 |
| checkout 조회 | GET /ec/checkout?productId=&quantity= 또는 반복 cartItemIds | items/summary. 가격·배송비는 응답 사용 |
| 주문 내역·상세·완료 | GET /ec/orders?page=&size=10, /ec/orders/:id, /ec/orders/:id/completion | 기간 필터 없음. 날짜는 YYYY.MM.DD로 표시 |
| FAQ | GET /ec/faqs?keyword= | 배열 전부 표시, size 제한 없음 |
| EC 문의 목록·작성 | GET /ec/inquiries?page=&size=10, POST /ec/inquiries {type,title,content} | 공통 페이지 및 {inquiryId}. 첨부 필드 미전송 |

- 정확한 예상 필드와 nullable·검증 형태는 src/features/ec/api/ec.dto.ts에 있다. parser는 캐시 진입 전에 응답을 검증한다.
- 공통 ApiClient, createPageResponseSchema, 인증 customConfig, withAbortSignal을 재사용했다.
- 실제 개발 MSW mock이나 운영 fallback은 추가하지 않았다. 테스트만 로컬 Axios adapter 및 client spy를 사용한다.
- router state는 {kind:"product",productId,quantity} 또는 {kind:"cart",cartItemIds}. 금액을 state에서 신뢰하지 않는다.
- checkout state가 잘못되거나 없으면 조회를 막고 장바구니로 이동한다. 유효 state의 배송지 초기값은 전부 비어 있다.
- 실제 주문 생성·결제 mutation은 구현하지 않았다. 결제 버튼은 배송지 폼 검증까지만 연결한다.
- 문의 성공 알림을 닫으면 /ec/support/inquiries로 replace 이동한다.
- EC 문의 목록은 기존 InquiryListPage 표시 컴포넌트를 사용한다. 데이터·캐시·경로는 EC 전용이며 임시 상태는 OPEN/COMPLETED.
- 문의 상세 계약은 이번 범위에 없어 onItemClick을 연결하지 않았다.
- 중복 담기·찜·장바구니 변경·문의 제출을 막으며 문의 실패 시 입력을 유지하고 재제출한다.

## UI 후속 작업 1 — 상품 페이지네이션

- 역할: ui. 공간: ec-buyer. Logic 검증이 완료됐으므로 최신 미커밋 diff 확인 후 같은 공간에서 순차 작업한다.
- 수정 대상: src/features/ec/ui/market/EcMarketPage.tsx, src/pages/ec/ui/EcRoutes.tsx.
- 재사용: src/shared/ui/pagination/pagination.tsx.
- 사용 예: src/features/ec/ui/order/EcOrderListPage.tsx 및 src/features/inquiry/ui/InquiryListPage.tsx.
- EcMarketPage에 page:number, pageCount:number, onPageChange:(page:number)=>void props를 추가한다.
- EcMarketContent에서 controller.page, controller.pageCount, controller.onPageChange를 전달한다.
- 로딩이 끝나고 pageCount > 1이면 기존 Pagination의 page·pageCount·handler를 연결한다.
- 페이지 크기는 10. controller가 응답 total/size로 페이지 수를 제공하므로 UI에서 요청·계산을 중복하지 않는다.
- useEcListLocation은 page를 URL에 replace로 반영하며 1페이지는 page 인자를 생략한다. keyword/categoryId를 유지한다.
- 검색 제출과 카테고리 변경은 1페이지로 이동한다.
- 완료 기준: 2페이지 요청·전환, 1페이지 쿼리 생략, 검색/카테고리 유지, 로딩 및 0/1페이지 표시 확인.
- 기존 Vitest 방식으로 UI callback 연결을 확인한 뒤 포맷 → lint → 대상 test → build를 실행한다.

## UI 후속 작업 2 — 검색 버튼

- 대상: features/ec/ui/market/EcMarketPage.tsx 및 support/EcSupportPage.tsx.
- onKeywordChange는 draft만 변경하고 onKeywordSubmit이 조회를 실행한다. 두 callback은 route에 이미 연결했다.
- 요청한 input 내부 “검색” 버튼을 type=submit으로 기존 form에 연결한다. 현재는 Enter 제출만 가능하다.
- TextInput에는 startContent만 있고 endContent는 없다. 우측 버튼 확장이 필요하면 UI 역할에서 자산 선정 후 shared TextInput·IconButton 재사용을 검토한다.
- Logic에서 검색 버튼 마크업·스타일은 변경하지 않았다.

## UI 후속 검토·남은 연결

- controller는 error/refetch/isEmpty를 제공하나 기존 EC 화면에 오류·재시도 props가 없다. 전역 오류 알림과 중복하지 않도록 화면 상태 연결을 검토한다. 현재 API 실패를 controller에서 정상 빈 목록으로 분류하지는 않는다.
- EC 문의 목록은 기존 표시 컴포넌트를 재사용한 상태다. EC 전용 헤더·하단 탭이 필요하면 UI가 구성하며 /manage 데이터로 합치지 않는다.
- 문의 목록 항목 상세 화면은 미정이다. 임의 상세 경로를 추가하지 않는다.
- 결제·주소 검색·배송 조회·사진 첨부는 별도 계약과 승인 후 연결한다.
- 기존 알림·하단 카테고리 탭·고객센터 빠른 메뉴·더 많은 질문 보기 callback의 대상 화면은 미정 상태를 유지한다.
- UI 역할은 구현 전 policy-ui-library의 자산 선정 절차를 따른다. 이 세션은 표현 코드를 새로 구현하지 않았다.

## 검증 결과

- 공통 formatting.py apply: 수정 파일의 실제 Prettier 실행 완료.
- npm run lint: 최종 통과.
- npm run test -- src/features/ec src/pages/ec src/app/routing.test.ts --maxWorkers=4: 최종 4개 파일, 41개 테스트 통과.
- npm run build: 최종 통과. 기존 500kB 초과 청크 경고 있음.
- git diff --check: 통과.
- npm run test -- --maxWorkers=4: 100개 파일 통과·4개 파일 실패, 853개 테스트 통과·13개 실패.
- 전체 실패: citizen mocks/browserHandlers 8개, mocks/handlers 3개, api/http/citizenParticipation.api 1개, pages/citizen-participation/ui/CitizenResultRoutes 1개.
- 해당 항목은 이전 UI handoff의 기존 실패와 동일하다. git diff sy-main -- src/features/citizen-participation src/pages/citizen-participation 출력이 비어 있음을 확인했다. 기본 checkout의 전체 테스트를 이번 세션에서 다시 실행하지는 않았다.
- 최초 lint 2건은 adapter의 불필요한 async와 render 중 handleSubmit 생성에 대한 refs 규칙이었다. 수정 후 lint·대상 테스트·build를 다시 통과했다.
- 이후 변경이 EC handler 생성과 테스트 adapter에 국한되어 전체 테스트는 다시 반복하지 않았다.
- 실제 서버·브라우저 시각 QA는 미실행. 독립 리뷰 에이전트는 호출하지 않았다.

## 실행 기록 문제 해결

- 실패한 patch의 종료 기록 때문에 포맷이 차단됐으나 정상 보호 복구로 해소했다.
- Codex PreToolUse에서 workdir가 누락되면 세션 시작 위치로 판정한다. 기본 checkout에서 같은 저장소 EC 기록을 복구하는 지원 경로를 사용했다.
- 복구 operation 7c19d02ada7c456287774bafd037bc9b 및 508b5eeca8fc4c7c9edd874c763cf210: 사용자 일반 채팅 승인 후 done 확인.
- 중앙 lock/state 접근 때문에 처음부터 require_escalated 실행이 필요했다. 선택형 질문 답변은 이 세션의 승인 훅에 반영되지 않았다.
- 정책 파일·중앙 state·.git를 직접 편집하지 않았다. 현재 EC 포맷 차단은 해소됐다.
- unknown/test-drafts.md는 중단 당시 초안 이력이며 현재 테스트 코드가 정본이다.

## Git·다음 순서

- 다음 담당자는 위 ec-buyer 공간에서 UI props 연결을 수행한다. 역할별 별도 branch/worktree를 만들지 않는다.
- 공유 파일 EcRoutes.tsx는 최신 controller 연결을 보존하면서 UI props만 추가한다. 소스 수정과 Git 작업은 순차로 진행한다.
- 이번 세션 승인된 Git 관리 작업은 종료 기록 복구뿐이다. stage·commit·merge는 미승인.
- 향후 통합은 feature/ec-buyer-ui → 직접 부모 sy-main. 형제·자식·dirty 상태를 다시 검토하고 별도 Git 승인을 받아야 한다.
