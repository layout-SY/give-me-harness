# 이용 내역 API 연결

## 범위와 확정 결정

- 역할은 `logic`, 작업 책임은 owner다. 최초 진행 지시와 후속 계약 답변을 확인했으며, 중앙 PreToolUse의 승인 문구 판정으로 중단된 뒤 사용자의 단독 `진행` 답변으로 정상 승인되어 구현을 완료했다.
- 작업 위치는 `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`, `sy-main`, 시작 HEAD는 `f3627abcd440709ccec1b98a6b37238fcf6936e2`다. 시작 시 미커밋 변경은 없었다.
- 제공된 `GET /admin/usage/point`, `GET /admin/usage/item`을 이용 내역 도메인에 추가한다. 사용자·아이템 관리 API와 서로 다른 도메인 계약 및 캐시를 사용한다.
- 설정하지 않은 검색 필드는 query key를 전송하지 않는다. 빈 검색어도 생략하며 by와 keyword의 동시 입력을 강제하지 않는다. 검색 문자열이나 ID를 다른 도메인 ID로 변환하지 않는다.
- by·type·action의 전체 enum은 미확정이며 사용자 지시에 따라 string으로 처리한다.
- 항목 응답은 모든 키가 필수이고 값은 nullable이다. 다른 도메인과 동일하게 공용 페이지 구조 `items`, `total`, `page`, `size`는 유지한다. 페이지 요청 기본값은 사용자 답변의 1, 10을 적용하며 응답에 기본값을 주입하거나 재계산하지 않는다.
- 현재 소비자가 없는 `/v1/usage` API는 별도 구형 계약으로 보존하고, `admin-users`의 분리 방식에 따라 같은 entity에 관리자 이용 내역 모듈을 추가한다.
- 최초 구현에는 Git 변경을 포함하지 않았다. 후속 사용자 커밋 요청과 명령 실행 승인으로 소스·테스트 11개 파일의 stage·commit을 수행했다.

## 재사용 근거와 예상 변경

- `src/entities/usage/api/usage.api.ts`, `usage.dto.ts`, `api/index.ts`: 기존 이용 내역 API는 `/v1/usage`와 구형 응답이며 `src` 내 호출부는 확인되지 않았다.
- `src/entities/users/api/admin-users.api.ts`, `admin-users.dto.ts`, `admin-users.parser.ts`, `api/index.ts`: 구형 API와 관리자 API 분리, 공용 ApiClient·AbortSignal 사용, factory 구성.
- `src/entities/items/api/items.dto.ts`, `items.parser.ts`, `model/item-query-options.ts`, `hook/use-item-list-query.ts`: 필수 키와 nullable 값, 공용 페이지 schema, queryOptions와 얇은 hook.
- `src/entities/news/api/news.api.ts`: 평탄화된 query params 및 반복 sort 직렬화.
- `src/shared/api/api-client.ts`, `common/response.dto.ts`, `with-abort-signal.ts`, `axios.interface.ts`: envelope·페이지 구조·인증·취소 재사용.
- `src/shared/ui/`, `src/app/router/routes.tsx`: 이용 내역 연결 대상 화면은 확인되지 않아 API·조회 hook까지만 제공한다.
- `tests/items-query-mutation.test.mjs`, `admin-users-contract.test.mjs`, `common-response-contract.test.mjs`: 기존 Node test·tsx·Vite SSR·MSW의 실제 Axios 검증 패턴.
- 예상 diff: `src/entities/usage/api/admin-usage.*`, `api/index.ts`, `model/admin-usage-query-*.ts`, `hook/use-*-usage-list-query.ts`, entity public API, 이용 내역 계약·query 테스트, 자기 세션 산출물.

## 작업과 검증

- [x] `src/entities/usage/api/`에서 확정 DTO·요청 검증·API·parser를 추가해 신규 명세의 전송 경계를 만든다.
- [x] 같은 entity의 model·hook·public API에서 포인트/아이템 조회와 독립 캐시를 노출한다.
- [x] `tests/`에서 요청 생략·기본값·sort·nullable/누락·응답 보존·오류·취소를 기존 테스트 도구로 검증한다. 테스트에서만 제공된 명세의 응답을 사용하며 앱용 mock을 만들지 않는다.
- [x] 실제 workdir에서 중앙 `formatting.py apply` 실행 후 관련 Node 테스트, `npm run lint`, `npm run build`를 수행한다. package.json에 test script가 없어 `node --test`를 사용한다.
- [x] 변경 diff와 결과를 검토하고 `final-summary.md`에 구현·검증·미완료 항목을 기록한다.

## 현재 실행 상태

- `진행` 승인 뒤 소스 9개 파일과 테스트 2개 파일의 추가·수정을 완료했다. 공용 날짜 검증은 `src/shared/lib/validation/index.ts`의 `isoCalendarDateSchema`를 재사용했다.
- 중앙 승인 상태나 정책은 수정하지 않았고 정상 PreToolUse 경로로 적용했다. 초기에 거절된 패치는 소스에 적용되지 않았음을 확인한 뒤 승인 답변마다 상태를 다시 확인했다.
- 관련 테스트 24개, lint, build, `git diff --check`가 통과했다. 최종 결과와 실제 검증 범위는 `final-summary.md`에 기록했다.
- 실서버 호출·화면 연결은 수행하지 않았다. API와 조회 hook이 연결 가능한 상태다. 후속 커밋은 `604e4dc46900edbedd0dc0369784b7a76f1ab83d`로 완료했으며 Git 작업 트리는 깨끗하다.

## 적용 스킬

중앙 bundle의 task-role-routing, git-branch-strategy, coding-convention, type-definition, data-fetch-layer, implementation-quality, documentation, recipe/api-authoring, recipe/data-dto, reference/custom-hooks를 확인했다. API·hook 관련 실제 프로젝트 자산을 재사용하며 새 패키지나 공용 추상화를 추가하지 않는다.
