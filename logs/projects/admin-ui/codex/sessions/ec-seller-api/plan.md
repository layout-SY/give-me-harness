# EC 판매자 API·MSW 연결 계획

<!-- asan-plan:approval:start:v1 -->

## 목표와 승인

- 사용자 요청: EC UI 계약을 기준으로 기존 API 연결 패턴과 MSW에 연결한다.
- 사용자 추가 결정: "1번 : 너가 설계해", "2번 : 일단 보류". 임시 API 계약 설계를 위임했고 추가 UI가 필요한 동작은 보류했다.
- 경로 결정: 사용자 지시 "라우트에 v1은 빼"에 따라 EC API·MSW 경로는 `/ec/*`로 통일한다.
- 역할: inject Logic. UI 선행 `controller -> UI`. owner 산출물.
- 작업 위치: `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/ec-seller-ui`, `feature/ec-seller-ui`, 기준 HEAD `b6fc92d2eed80a4920cc4681bda7f44a3565a8f5`.
- Git 변경 없음. 기존 UI commit 위에 순차 구현한다. 시작 시 worktree 깨끗함. 기본 checkout의 tutorial 변경은 별도 작업이다.

## 구현 범위

1. `src/entities/ec-seller/`: 임시 DTO·Zod schema·API factory·Query/mutation options·도메인 표시 매핑. URL은 `/ec`, 문자열 ID, 공통 `ApiResponseDto` envelope와 `createPageResponseSchema` 재사용.
2. `src/pages/ec-*/hook/`: UI 없는 controller. 상품 검색·CRUD, 주문 목록·상세·처리·송장·메모, 문의 검색·상세·답변, 매출 3화면, 입점 신청·승인 대기·판매자 정보·로고 업로드 연결.
3. 기존 page는 route 인자·controller·View 조립만 변경. 셸은 판매자 요약 조회 연결. 기존 View 타입·마크업·CSS 유지.
4. `src/mocks/ec-seller*`: 예시 데이터·stateful handler. 브라우저 handler registry와 개발환경 미등록 요청 감시에 EC 추가. 실제 서버 fallback 없음.
5. 추가 편집 UI가 없는 상품 이미지 추가·옵션 편집·수령인 수정, 별도 화면·콘텐츠 없는 약관·개인정보·도움말·배송 추적·카테고리 상세는 보류. 기존 파일 입력이 있는 로고 업로드는 연결한다. 대시보드·차트 구현은 기존 보류 유지.
6. 다운로드는 Excel에서 열 수 있는 CSV 응답으로 임시 계약을 문서화하고 기존 다운로드 버튼에서 요청한다.

## 재사용 근거와 스킬

- `entities/news/api`, `model/news-query-options.ts`, `news-mutation-options.ts`, `pages/cp-news/hook/use-cp-news-list-controller.ts`: factory → unwrap/parser → Query → controller의 실제 사용처.
- `shared/api/api-client.ts`, `common/response.dto.ts`, `with-abort-signal.ts`: 전송·envelope·페이지·취소 재사용.
- `mocks/handlers.ts`, `browser.ts`, `utils/mock-table.ts`: 기존 MSW 등록·상태 처리 구조 재사용.
- `shared/ui/`와 EC View·props 조사 완료. 새 UI를 작성하지 않고 page 연결만 변경한다.
- task-role-routing·git-branch-strategy: Logic 경계와 동일 worktree 확인.
- api-authoring·data-fetch-layer·type-definition: DTO와 View 분리, 공개 계약·취소·캐시 무효화.
- coding-convention·validation·implementation-quality: 순수 요청 mapper, 입력 검증, UI 없는 hook.
- documentation: 현재 계획, 최종 요약, 보류 UI 인계.

## 임시 정책

- 개발 MSW는 기존처럼 `VITE_ENVIRONMENT=dev`에서만 시작. 테스트·운영 환경 활성화 정책은 변경하지 않는다.
- 생성·변경은 MSW 인스턴스 메모리에 반영하며 새로고침 시 fixture로 초기화한다.
- 상태는 상품 ON_SALE/STOPPED/SOLD_OUT/PENDING/REJECTED, 주문 RECEIVED/PREPARING/SHIPPED/DELIVERED/CANCELED, 문의 WAITING/ANSWERED로 정의한다.
- 주문 준비: RECEIVED → PREPARING, 송장: PREPARING → SHIPPED, 완료: SHIPPED → DELIVERED, 취소: RECEIVED/PREPARING → CANCELED. handler에서 전이 검증.
- 검색·필터·페이지·상태 집계, nullable 필드, 숫자·문자열 입력 변환을 명시한다. 업무 미확정값을 실제 서버 확정 계약으로 표현하지 않는다.

## 검증

- 기존 Node test + Vite SSR + MSW 패턴으로 실제 Axios 요청/응답·등록·수정·오류·취소·controller 계약 검증.
- 공통 formatter 실행 후 lint·build와 관련 테스트 수행. package.json에는 test script가 없으므로 `node --test` 사용.
- 브라우저 자동화·시각 QA는 수행하지 않는다.

<!-- asan-plan:approval:end:v1 -->

## 진행 기록

- 임시 계약 설계 위임과 추가 UI 보류를 반영했다. 소스 생성은 자동 실행 검사의 사용자 구현 승인 요구로 차단되어 실행되지 않았다.
- API factory·MSW handler·미등록 요청 감시는 `/ec/*`를 기준으로 구현할 예정이다. 기존 CP 경로는 변경하지 않는다.
- 2026-10-02 사용자 "진행해"로 구현 승인. 초기 worktree·HEAD는 동일하고 기존 변경은 없었다.
- API·DTO·Query/mutation·controller·MSW 및 page 연결 완료. 추가 UI callback은 보류했다. [임시 계약 상세](unknown/api-contract.md).
- 기존 환경 파일이 없어 이 worktree의 ignored `.env.local`에 `VITE_ENVIRONMENT=dev`만 추가했다.
- 1차 formatter·lint·build 성공, 관련 테스트 16개 통과. 이후 라벨·반품률·승인 입력 오류 안내·중복 클릭 검증을 보완했으며 최종 검증을 진행한다.
- 최종 formatter·lint·build 통과. 신규 EC 15개를 포함한 관련 테스트 42/42 통과. `git diff --check` 통과. [최종 요약](final-summary.md)과 [보류 기능 인계](handoff.md) 작성 완료.
