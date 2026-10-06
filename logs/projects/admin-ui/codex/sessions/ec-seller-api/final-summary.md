# EC 판매자 API·MSW 연결 결과

## 결론

`/ec/*` 임시 API·DTO·Query/mutation·UI 없는 controller·MSW 연결을 완료했다. 기존 View props와 화면 구조를 유지했다. formatter 완료 후 lint·build와 관련 테스트 42개가 통과했다.

## 범위와 결정

- 작업 위치: `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/ec-seller-ui`
- branch: `feature/ec-seller-ui`, 기준 HEAD `b6fc92d2eed80a4920cc4681bda7f44a3565a8f5`.
- 사용자 승인: API 계약 설계 위임, 추가 UI 보류, v1 제거, 2026-10-02 "진행해".
- 실제 서버 명세가 없는 임시 계약이다. [계약 상세](unknown/api-contract.md)에 endpoint·필드·상태 전이·검증·개발 실행 방법을 기록했다.
- 생성·stage·commit·merge 등 Git 변경은 실행하지 않았다.

## 실제 변경

- `entities/ec-seller`: DTO schema, 기존 ApiClient factory 연결, 응답 unwrap·검증, ID encoding, signal 전달, Query key와 변경별 캐시 무효화.
- `features/ec-seller`: 목록 URL·검색 draft·선택 상태, 표시 매핑·기간 필터, 연속 실행 방지·unmount 후 부수 효과 방지, CSV 다운로드, 판매자 요약 조회.
- `pages/ec-*/hook`: 상품 CRUD, 주문 검색·처리·송장·메모, 문의 조회·답변, 매출 3화면, 입점 신청·대기, 프로필·로고 업로드.
- 기존 page와 EC shell에 controller 연결. 상세 ID 변경은 controller의 key를 바꿔 입력 수명을 분리했다.
- `mocks/ec-seller*`: 상품 27개·주문 36개·문의 24개 및 선택지·판매자 예시, 상태 변경 반영, 필터·페이지·CSV·매출 집계. API 없이 UI에 데이터를 직접 넣는 방식은 사용하지 않았다.
- `mocks/handlers.ts`: EC handler 등록. `app/mock-api-policy.ts`·`app/index.tsx`: EC 미등록 API 오류 감시와 HTML 문서 탐색 제외.
- 기존 환경 파일이 없던 이 worktree에 `.env.local`을 추가해 `VITE_ENVIRONMENT=dev` 설정. 개발 MSW 활성화 정책 자체는 유지했다. 로컬 환경 파일은 Git 추적 대상이 아니다.

## 검증

- 공통 `formatting.py apply`: 수정한 소스·테스트 대상으로 완료. 중앙 events.lock 쓰기 sandbox 제한은 승인된 escalated 실행으로 해소했다.
- `npm run lint`: 통과.
- `npm run build`: 통과. Vite tsconfig paths plugin 안내와 500kB 초과 chunk 경고가 있다.
- `node --test tests/ec-seller-api.test.mjs tests/mock-api-policy.test.mjs tests/news-msw.test.mjs tests/inquiries-msw.test.mjs tests/global-pagination-msw.test.mjs`: 42/42 통과.
- 신규 EC 테스트 15개: 실제 Axios·브라우저 handler registry, 필터·페이지·CRUD·캐시, 주문 전이·취소·반품 구분, 문의 답변, multipart 로고, 판매자 신청·프로필, 매출·CSV, 오류·취소, controller 표시·입력 mapper, 중복 클릭 단일 전송.
- `git diff --check`: 통과. EC 구현에서 `/v1/ec` 참조 없음.
- 실행하지 않음: 실제 서버 연결, 브라우저 시각 QA·자동화, 독립 Watcher 에이전트 검토. 서버 명세 정확성과 시각 결과는 테스트 통과로 확정하지 않는다.

## 제한과 보류

- MSW 저장은 메모리 기반이며 새로고침하면 초기화된다.
- CSV를 제공하며 XLSX 생성은 포함하지 않았다. 비교 기간 지표는 null이다.
- 추가 UI·콘텐츠가 필요한 동작은 사용자 지시에 따라 보류했다. [인계](handoff.md) 참조.
- 실제 서버 API 명세가 제공되면 endpoint·DTO·정책을 대조해야 한다.

## 커밋 완료

- 사용자가 커밋 요청 후 `명령 실행 승인`으로 동일 stage·commit 작업을 승인했다.
- 보호 작업: `a7b4b736e8d6fba16887c902d70d124b`, 메시지 `feat(ec): 판매자 API와 MSW 연결`, 대상 소스·테스트 40파일.
- 보호 실행기 진입에서 중앙 `branch-relations/v1/locks/operation-a7b4b736e8d6fba16887c902d70d124b.lock` 쓰기가 sandbox의 `Operation not permitted`로 실패했다.
- 같은 작업을 `require_escalated`로 재호출했으나 PreToolUse가 기존 승인을 재사용하지 못하고 다시 `명령 실행 승인`을 요구하며 차단했다.
- `show` 결과 stage는 `prepared`이고 Git 명령 실행 결과는 없다. HEAD `b6fc92d2eed80a4920cc4681bda7f44a3565a8f5`, staged 없음, 기존 변경 보존을 재확인했다.
- 위 내용은 최초 실행 실패 이력이다. 이후 사용자 재승인으로 실행을 재개했으며, 실패한 문서 패치의 미확인 쓰기 기록이 추가 차단 원인으로 확인됐다.
- 원본 도구 로그에서 문서 패치의 실패 종료를 확인하고, 별도 승인된 복구 작업 `ddb12f9da1a14a6395710cb5b132bc6a`로 해당 기록만 해소했다.
- 기존 승인된 커밋 작업을 재실행해 `bbb337d` (`feat(ec): 판매자 API와 MSW 연결`)를 생성했다. 40파일, 2296줄 추가·171줄 삭제.
- 커밋 후 `git status --short` 출력 없음. 소스 변경 없이 기존 lint·build·관련 테스트 42개 통과 결과를 유지한다. 병합·push는 수행하지 않았다.
