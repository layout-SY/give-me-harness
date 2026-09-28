# 사용자 관리 API 로직 구현

## 범위와 승인

- 작업 위치: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`, `sy-main`, 기준 HEAD `52011e5ad746e3c62b7e75b0a3f11cf1472c6c78`.
- 역할: `logic`, owner. 사용자가 `item`을 `user`로 정정하고 “작업 진행해”로 구현을 승인했다.
- 목표: 제공된 `/admin/users` 5개 API의 전송·DTO·parser·Query/Mutation hook을 기존 `news` 연결 패턴에 맞춰 제공한다.
- 기존 `/v1/users`는 명세가 다른 API이므로 기존 공개 계약을 보존하고 같은 entity에 `admin-users` 모듈을 추가한다.
- `reason`, `citizenCard`, `roles`는 사용자 답변에 따라 필수다. 추가 길이 제한이나 역할 목록은 정의하지 않는다.
- `direction`은 `as const`로 정의한다. 확인된 값은 `RECHARGE`뿐이며 차감 값은 사용자가 확인 중이다. 미확정 값을 코드나 테스트에 계약으로 추가하지 않는다.
- 권한 API는 현재 no-op이므로 응답을 실제 권한 변경으로 해석하지 않는다.
- `publicId`는 상세·탈퇴 로그 응답의 식별자다. path의 int64 `userId`로 변환하지 않으며 호출자가 별도로 전달한다.
- Git 변경은 승인 범위에 없다.

## 확인한 재사용 근거

- `src/entities/news/api/news.api.ts`, `news.dto.ts`, `news.parser.ts`: ApiClient factory, Zod 요청 검증, 성공 data 파싱.
- `src/entities/news/model/news-query-options.ts`, `news-mutation-options.ts`, `query-keys.ts`: query options와 mutation 성공 후 취소·무효화.
- `src/entities/news/hook/`, `src/pages/cp-news/hook/use-cp-news-form-controller.ts`: 얇은 hook과 UI controller 연결.
- `src/shared/api/api-client.ts`, `axios-instance.ts`, `common/api-result/`, `with-abort-signal.ts`: 인증·envelope·실패·요청 취소.
- `src/app/providers/query-client.ts`: 공통 오류 표시와 재시도 정책.
- `src/entities/users/api/`, `model/user.enum.ts`: 기존 사용자 API와 상태가 새 명세와 다름을 확인.
- `src/shared/ui/table/interface/sharedTableTypes.ts`, `src/shared/lib/validation/index.ts`: 기존 공용 계약 확인. 화면·폼을 만들지 않으므로 확장하지 않는다.
- `tests/news-contract.test.mjs`, `tests/news-mutation.test.mjs`: Node test·tsx·Vite SSR·MSW를 사용하는 기존 검증 방식.

## 구현 및 검증 순서

- [x] `src/entities/users/`에 새 관리자용 상수·DTO·API·parser를 추가하여 필수 필드, 양수 amount, ACTIVE/SUSPEND 요청, WITHDRAWN 조회, 탈퇴 목록 페이지 계약을 구현한다.
- [x] 같은 entity의 model·hook·public API에서 조회·mutation과 정확한 상세 캐시 갱신을 연결한다.
- [x] `tests/`에서 확정된 요청·응답, 실제 Axios 오류 전달, 요청 취소와 mutation 캐시 경계를 검증한다. 테스트 응답은 제공된 계약만 사용하고 앱용 mock 데이터는 추가하지 않는다.
- [x] 해당 테스트 및 기존 사용자 API 타입 검증, `npm run lint`, `npm run build`를 실행한다.
- [x] 최종 변경과 검증 결과, 차감 direction 대기 항목을 자기 세션 산출물에 기록한다.

## 적용 스킬

중앙 snapshot의 `policy-task-role-routing`, `policy-git-branch-strategy`, `skill-index`, `policy-coding-convention`, `policy-type-definition`, `policy-data-fetch-layer`, `policy-implementation-quality`, `policy-documentation`, `recipe-api-authoring`을 적용한다.

## 후속 작업: item API 연결

### 확정 계약과 범위

- 같은 세션·worktree·`sy-main`에서 사용자 요청에 따라 item 작업을 이어간다. 앞선 user 변경을 보존한다.
- 사용자 제공 `/admin/items` 10개 endpoint와 각 요청·응답 DTO를 기존 `/v1/items` 구현에 반영한다. 카테고리 API는 별도 명세가 없으므로 유지한다.
- 요청·응답 DTO는 모든 필드가 반드시 존재하고 각 값은 nullable이다. PATCH도 Partial을 쓰지 않는다. 경로 `itemId`, 업로드 query `subCategoryId`, 업로드 `file`은 명시된 필수값을 유지한다.
- enum 전체 목록은 미확정이므로 사용자 승인에 따라 문자열을 임시 허용한다. 값이나 매핑을 임의로 추가하지 않는다.
- 목록 query 필드는 모두 존재해야 하며 `page`, `size`가 null일 때 기본값 1, 10으로 정규화한다. 응답의 페이지 값은 재계산하지 않는다.
- 수정 응답의 `mainCateogoryId`, `imageUrl`은 명세 철자를 그대로 보존한다. 생성의 `imageUuid`, 수정의 `image`, 상세의 `image`를 임의로 연결하지 않는다.
- Query/Mutation hook까지 구현하며 화면·폼 controller는 아직 없는 UI 계약을 가정해서 만들지 않는다.

### 재사용과 검증

- `news` API·DTO·parser·query/mutation options·hook과 `use-cp-news-list-controller.ts`에서 연결 패턴을 확인했다.
- 공용 ApiClient, Axios 인증/오류 처리, AbortSignal, TanStack Query를 그대로 사용한다.
- 기존 ImageManager는 scope와 URL 응답을 사용하는 다른 계약이다. 이번에는 API에 필요한 File·subCategoryId와 uuid/url 응답만 hook으로 노출한다.
- 기존 item 관련 계약 테스트는 새 API 계약으로 갱신하고, 새 테스트에서 10개 endpoint·nullable/필드 누락·응답 반환·인증·multipart·취소·캐시 및 Query/Mutation 상태를 검증한다.
- [x] `src/entities/items/api/`의 요청·응답 DTO와 API를 명세에 맞게 수정하고 parser를 추가한다.
- [x] `src/entities/items/model/`, `hook/`, public API에 캐시·조회·변경 흐름을 구현한다.
- [x] `tests/`에서 기존 item 검증을 새 계약으로 옮기고 실제 Axios·Query/Mutation observer로 데이터 흐름을 확인한다.
- [x] 관련 테스트, `npm run lint`, `npm run build`, diff 확인을 실행하고 결과·한계를 기록한다.

## 후속 조사: 모든 도메인의 목록 응답 일관성

- 요청: 모든 도메인이 같은 total/page/size 목록 응답을 반영했는지 확인한다. 현재 logic 범위에서 읽기 전용 코드 조사를 수행한다.
- [x] 현재 worktree의 `src/entities` 30개 도메인과 `src/shared/api`를 검색해 목록 응답 DTO·schema·API 반환 타입과 기본값을 비교한다.
- [x] `src/pages`, `src/features`, `src/mocks`에서 hook·controller·fixture까지 전달되는 실제 형식을 추적한다.
- [x] 일치·불일치·응답 타입 미보장·API 미연결을 구분해 `unknown/pagination-audit.md`와 최종 요약에 기록한다.
- 기대 결과: 공통 응답 재사용 여부와 실제 차이를 경로 근거로 보고한다. 이번 요청에서는 애플리케이션 코드를 변경하지 않는다.

## 후속 구현: 호환되는 응답에 공용 DTO 적용

- 사용자 최종 결정: 기존 형식과 추가 통계는 그대로 유지하고, 이미 `items/total/page/size` 구조인 도메인만 공용 DTO를 사용한다. 공용 페이지 필드는 필수·non-nullable이다. 페이지 요청 없는 응답에는 페이지 필드를 추가하지 않는다.
- 현재 작업 공간·logic 역할·기존 구현 승인을 유지한다. 최신 결정으로 계약 확인을 마쳤으며 별도 Git 작업은 없다.
- [x] `src/shared/api/common/response.dto.ts`에 `ApiResponseDto<TData>`, `PageResponseDto<TItem>`, 공용 페이지 Zod schema factory를 추가한다.
- [x] 공용 ApiClient의 타입 경계가 새 envelope와 기존 envelope를 함께 수용하도록 연결하며 실행 시 정규화 동작은 유지한다.
- [x] items·관리자 탈퇴·inquiries·cp-proposal·cp-vote의 목록 DTO와 schema를 공용화한다. 항목 계약과 기존 숫자 검증·pageCount 계산을 유지한다.
- [x] 아이템 목록의 공용 필드와 root data에서 null을 거부하도록 parser·테스트를 갱신한다. 상세·mutation null 및 항목 내부 nullable은 유지한다.
- [x] `tests/`의 기존 도구로 공용 필수 타입·다섯 도메인 파싱·이전 응답 identity를 확인하고 전체 테스트·lint·build·diff check를 완료한다.
- 기존 count/opinionTotal/pinnedItemCount, TableApiResponseDto, 다른 도메인 형식, 일반 배열 및 기존 query 기본값·화면 설정은 이번 응답 공용화에서 변경하지 않는다.
