# EC 구매자 Logic·MSW 현재 결과

## 최신 결과 — 2026-09-30 sy-main 병합 완료

- feature/ec-buyer-ui → 직접 부모 sy-main ff-only 병합 완료. 결과 HEAD: 55194e6c2ac6e2189fa11be2d5741bac6c277a2f.
- 기본 checkout에서 병합 후 npm run lint·npm run build 모두 통과. 보호 실행 operation 831402317ab843499193406cc255ac5d는 retained, verification_passed=true다.
- 병합 전 EC 관련 59개 및 공유 UI 18개, 총 77개 테스트 통과. 전체 테스트와 실 브라우저 검증은 추가 실행하지 않았다.
- 브랜치·worktree·Git 제외 환경설정은 보존했으며 원격 push는 하지 않았다.
- 부모 README.md의 기존 한 줄 변경 복원 완료. 사용자 승인 후 operation d5416aecfea8cb1ef638f3e18cf9d597이 done이며 파일 SHA-256이 병합 전과 동일함을 확인했다. target의 유일한 미커밋 변경은 원래 README 수정이고 source 작업 트리는 깨끗하다. 백업 stash 765bb7dcd582fc5ecd464045bbbfb41fa22178c2는 유지했다. 승인된 병합 작업의 남은 항목은 없다.

## 최신 결과 — 2026-09-30 포맷·검증 완료

- 현재 HEAD: 55194e6c2ac6e2189fa11be2d5741bac6c277a2f, branch feature/ec-buyer-ui. 같은 ec-buyer-ui worktree에서 작업했다.
- 과거 복구가 완료됐고 활성 쓰기 예약이 없는 것을 확인했다. EcRoutes.tsx 전체를 읽고 HEAD와 동일한 내용을 정상 저장하여 확인 기록을 갱신했다. 해당 파일의 최종 diff는 없다. 중앙 정책·state는 직접 수정하지 않았다.
- 공통 formatting.py apply 성공. MSW 소스 5개 및 내용 보존된 EcRoutes.tsx에 실제 Prettier를 적용했다.
- npm run lint: 통과.
- npm run test -- src/features/ec src/pages/ec src/app/routing.test.ts src/app/mocks/startMocks.test.ts --maxWorkers=4: 6개 파일·59개 테스트 통과. 새 MSW HTTP 통합 테스트 11개 포함.
- npm run build: 통과. 기존 500kB 초과 청크 경고 있음.
- git diff --check: 통과. 전체 테스트는 이번에 재실행하지 않았다.
- 커밋 대상: src/app/mocks/browser.ts, src/features/ec/mocks/fixtures.ts, handlers.ts, handlers.test.ts, src/features/ec/testing.ts.
- .env.development.local은 개발용 MSW 활성화 값 dev를 유지하며 Git 제외 대상이다. 다른 worktree에는 환경변수를 별도로 설정해야 한다.
- 실 브라우저 가로채기 확인은 수행하지 않았다. 실제 Axios 요청·응답·parser 연결은 MSW 통합 테스트로 확인했다.
- 사용자 명령 승인 후 보호 실행기 operation f86621d600bdf48f3b29d5c410f8eff7로 stage·commit 완료(stage:done). 커밋: 55194e6 feat: EC 예상 API용 MSW 연결.
- 사후 git status --short가 비어 있음을 확인했다. Git 제외 로컬 환경설정과 세션 문서는 보존했다. push·merge는 수행하지 않았다.

아래는 이전 시점 이력이다. 기존의 “검증 차단·새 세션 필요” 상태는 위 절로 대체한다.

## 최신 상태 — MSW 후속 요청

후속 실행 문제의 원인 한 가지를 수정했다. 이 worktree에는 MSW 활성화 환경변수가 없어 일반 개발 실행에서 worker가 시작되지 않았다. Git 제외 파일 .env.development.local에 VITE_API_BASE_URL_STATUS=dev를 추가했고, Vite loadEnv 조회로 development=dev / production=unset을 확인했다. 실행 중인 서버를 재시작해야 한다. 브라우저 가로채기와 아래 소스 검증은 아직 미완료다.

실제 API가 없다는 사용자 요청에 따라 기존 예상 계약에 맞춘 EC MSW 코드를 추가했다. **현재 포맷·lint·test·build는 정책 훅 차단으로 미완료이며 검증 통과로 보고하지 않는다.**

- 시작 HEAD: f6273c4b8571e8d4f0ba8f532e117eeaa7c80bf1. 기존 Logic은 5ba02b6, UI 후속 구현은 f6273c4에 커밋되어 있다.
- 작업 위치: /Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-user-ui-worktree/ec-buyer-ui, branch feature/ec-buyer-ui.
- 수정: src/app/mocks/browser.ts에 EC 핸들러 등록.
- 신규: src/features/ec/mocks/fixtures.ts, handlers.ts, handlers.test.ts, src/features/ec/testing.ts.
- 상품·주문·문의 12개씩, FAQ 6개. 상품 검색·카테고리·페이지 이동·품절, 장바구니 CRUD·합계·배지, 찜 상태, checkout 조회, 문의 작성 후 목록 반영을 구현했다.
- 실제 Axios → MSW → 공통 client/parser 흐름으로 11개 테스트를 작성했지만 아직 실행하지 못했다.
- 개발 실행: 해당 worktree에서 VITE_API_BASE_URL_STATUS=dev npm run dev. 새로고침 시 샘플 초기화. 실제 결제·주소 검색·배송 추적·첨부는 미포함.
- 현재 변경은 unstaged 수정 1개·신규 4개이며 stage·commit·merge는 수행하지 않았다.
- 차단 원인: 복구 완료된 과거 EcRoutes.tsx 실패 기록이 다른 UI 세션의 정상 수정 뒤에 다시 unconfirmed로 계산된다. 이번 MSW 파일은 정상 pending으로 기록됐다.
- 추가 승인 반복으로 해결할 상태가 아니다. 같은 worktree의 새 Logic assignment에서 이어서 검증하거나 중앙 정책 세션에서 회귀 테스트와 함께 이 결함을 수정해야 한다.
- 상세 실행 방법·예상 mock 조건·재개 순서는 [unknown/msw-guide.md](unknown/msw-guide.md), 최신 인계는 [handoff.md](handoff.md)를 따른다.

## 아래는 MSW 추가 전 Logic 구현 이력

아래 검증 수치는 이전 구현 결과이며 현재 MSW 변경의 검증 결과가 아니다. 아래 UI 후속 작업은 f6273c4에서 이미 반영됐다.

승인된 예상 API·DTO·controller와 기존 화면 연결을 구현하고 포맷·lint·대상 테스트·build를 통과했다. 상품 페이지네이션과 검색 버튼의 UI 작업은 [handoff.md](handoff.md)에 계약과 수정 위치를 기록했다.

## 작업 위치·범위
- worktree: /Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-user-ui-worktree/ec-buyer-ui
- branch/HEAD: feature/ec-buyer-ui / b52a5bc260520edf6befe238f89b164279a83def
- 소스 24개 경로 변경. 신규 commit·staged 변경 없음. 기본 checkout README.md 보존.
- API/parser/query/mutation/form은 features/ec, 화면 controller·mapper·라우트 조합은 pages/ec.
- UI는 기존 props에 연결했다. EC 문의 목록은 기존 InquiryListPage 표시를 재사용하되 API·캐시·라우트를 EC 전용으로 분리했다.

## 반영한 결정
- UI 기준 예상 계약 작성. 서버 확정 명세가 아니며 실제 서버 연결 검증 없음.
- 구매 정보를 router state로 전달, 금액은 checkout 응답 사용.
- 제출 시 검색·전체 카테고리·페이지당 10개. 주문 기간 필터 없음, FAQ 전부 표시.
- 기본 배송지 없이 필수 배송지·010 휴대전화 형식 검증. 문의 길이 상한 없음.
- 문의 성공 알림 후 EC 전용 목록으로 이동. 중복 요청 방지·실패 후 입력 유지·관련 캐시 무효화.

## 검증
- Prettier: 공통 트리거 실행 완료.
- lint: 통과.
- EC·라우팅 대상 테스트: 41개 통과.
- build: 통과. 기존 청크 크기 경고 있음.
- 전체 테스트: 853개 통과·13개 실패. 기존 UI handoff와 동일한 citizen/MSW·투표 실패이며 해당 소스의 sy-main 대비 diff 없음.
- git diff --check: 통과.
- 전체 실패를 수정하거나 테스트를 약화하지 않았다. 실제 서버·시각 QA·별도 리뷰 에이전트 검증은 수행하지 않았다.

## 남은 작업
- UI: 상품 페이지네이션 props와 검색 input 내부 submit 버튼 연결. 인계 문서에 파일·재사용 자산·callback·검증 기준 명시.
- UI 후속 검토: 오류/재시도 표현, EC 문의 목록 표현 구성. 문의 상세 계약은 미정.
- 이번 범위 제외: 실제 결제·주문 생성, 주소 검색, 배송 조회, 사진 첨부.
- 확정된 서버 명세 수신 후 DTO/parser/mapper 대조.
- commit·merge는 별도 승인 필요.

## 실행 차단 해소
두 번의 patch 실패 기록을 사용자 승인된 보호 복구로 정리했다. 기본 checkout에서 EC worktree 기록을 복구한 뒤 포맷과 검증을 완료했다. 소스·Git 이력·중앙 정책을 복구 작업으로 변경하지 않았다.
