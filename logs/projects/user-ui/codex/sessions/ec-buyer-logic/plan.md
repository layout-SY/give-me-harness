# EC 구매자 Logic 구현

- 역할: logic. UI 선행 계약에 controller를 맞춘다.
- 작업 위치: /Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-user-ui-worktree/ec-buyer-ui
- branch: feature/ec-buyer-ui, HEAD: b52a5bc260520edf6befe238f89b164279a83def, 직접 부모: sy-main.
- 사용자 승인: 기존 UI 기준 예상 요청/응답 DTO 생성, inquiry 패턴과 공통 API·페이지 DTO·알림 모달 재사용, 같은 워크트리 작업 승인.
- 예상 계약은 서버 확정 명세가 아니다. 후속 요청에 따라 이 계약 기반 개발용 MSW를 연결하며 실 서버 검증은 수행하지 않는다.
- 구매 진입: 라우터 state. 실제 결제, 주소 검색, 배송 조회, 첨부 업로드는 보류한다.
- 검색: 제출 시 실행, 전체 카테고리 포함. 목록은 페이지당 10개. 주문 기간 필터 없음, FAQ는 전부.
- 폼: 배송지 필수(형식 제한 없음), 010 국내 휴대전화는 하이픈 유무 모두 허용. 기본 배송지 없음. 문의 제목/내용 필수, 길이 상한 없음.
- 문의: EC 전용 목록 API/controller와 이동 경로를 준비한다. 목록 화면·검색 버튼·상품 페이지네이션은 UI 인계한다.

## 작업 순서

1. 위 worktree의 features/ec/api에 예상 DTO/schema/parser/API를 작성하고 공통 client·page schema를 재사용한다.
2. features/ec/hook과 model에 query/mutation/controller/form을 작성하여 입력·응답 계약을 제공한다.
3. pages/ec에서 기존 화면 props로 연결하고, 미구현 외부 동작을 주석·문서화한다.
4. 예상 계약 경계·상태·폼·중복 제출·캐시를 기존 Vitest로 검증한다. 공통 포맷 트리거 후 lint/test/build를 실행한다.
5. 실제 변경·검증·제한과 UI 다음 작업을 final-summary.md 및 handoff.md에 기록한다.

## 재사용 근거

- src/features/inquiry/api, hook, model/forms/inquiryForm.ts 및 pages/manage/ui/InquiryRoutes.tsx
- src/shared/api/api-client.ts, common/page-response.dto.ts, common/api-result, withAbortSignal
- src/shared/ui/dialog/hook.ts 및 features/ec/ui/**의 기존 props
- 소스 외 기본 checkout README.md와 Claude 세션 로그는 보존한다. Git 변경은 이번 구현 승인에 포함하지 않는다.

## 후속 요청: EC MSW 연결

- 사용자 요청: 실제 API가 없으므로 추측한 계약을 기준으로 MSW 연결.
- 시작 상태: feature/ec-buyer-ui, HEAD f6273c4b8571e8d4f0ba8f532e117eeaa7c80bf1, 미커밋 변경 없음. Logic은 5ba02b6, UI 후속 작업은 f6273c4에 반영되어 있다.
- 같은 worktree에서 기존 msw@2 및 app/mocks/browser.ts 등록·startMocks.ts 활성화 방식을 재사용한다.
- features/ec/mocks에 예상 DTO를 따르는 fixture·상태 보유 handler·실제 Axios 통합 테스트를 추가하고 testing.ts로 공개한다.
- 상품/주문/문의 각 12개, FAQ 6개로 페이지 이동·검색을 검증한다. 품절·빈 목록·조회 실패도 검증한다.
- 장바구니·찜·문의 상태는 메모리에서만 유지한다. 새로고침 시 초기화한다.
- 결제·주소 검색·배송 추적·사진 첨부는 그대로 제외한다. 실제 인증 서버도 모사하지 않는다.
- 공통 포맷 후 lint, EC·라우팅·MSW 시작 테스트, build를 실행한다. 결과와 개발 실행 방법을 같은 세션 문서에 기록한다.
