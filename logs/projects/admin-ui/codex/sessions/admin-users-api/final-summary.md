# 사용자·아이템 관리 API 구현 결과

## 현재 결론

사용자 최종 결정에 따라 기존 응답 형식은 보존하고, items·관리자 탈퇴·inquiries·cp-proposal·cp-vote에 공용 페이지 DTO와 schema를 적용했다. 공용 envelope DTO도 기존 전송 경계에 연결했다. 전체 테스트 211개, lint, build, diff check가 통과했다. 앞선 사용자·item API 구현과 조사 기록은 아래에 보존하며 최신 공용화 계약은 문서 마지막 절을 따른다.

## 결과

`/admin/users` 5개 API의 전송 함수, DTO·parser, 조회·mutation hook을 기존 `news` 패턴에 맞춰 추가했다. 확정된 계약의 구현과 검증을 마쳤다. 차감 direction 값은 아직 확인 대기이며 현재 포인트 요청은 확인된 `RECHARGE`만 허용한다.

## 변경

- `src/entities/users/api/admin-users.api.ts`: 사용자 상세, 탈퇴 목록, 포인트 지급, 권한 no-op, 상태 변경. 기존 ApiClient·인증·AbortSignal을 재사용한다.
- `src/entities/users/api/admin-users.dto.ts`: 필수 요청 필드와 양수 amount 검증, int64 userId 정밀도 보존, 상세의 WITHDRAWN 허용, 상태 변경의 ACTIVE/SUSPEND 제한, 탈퇴 목록 page 1·size 20 기본값 및 최대 100 적용.
- `src/entities/users/api/admin-users.parser.ts`: 상세·목록 검증, 상태·포인트 null data 처리, 권한 API의 문서상 string data 검증.
- `src/entities/users/model/admin-user.enum.ts`: 새 관리자 상태와 `USER_POINT_DIRECTION`의 `as const` 상수. 차감 값 확인 위치를 TODO로 표시한다.
- `src/entities/users/model/admin-users-{query-keys,query-options,mutation-options}.ts`: ID별 조회 캐시, 잘못된 ID 조회 비활성화, 상태·포인트 성공 후 해당 상세 취소·무효화. 권한 no-op은 응답만 전달한다.
- `src/entities/users/hook/`, `src/entities/users/index.ts`, `src/entities/users/api/index.ts`: API와 UI 연결용 hook의 공개 경계.
- `tests/admin-users-contract.test.mjs`, `tests/admin-users-query-mutation.test.mjs`: 신규 테스트 19개.

## UI 연결 계약

`~/entities/users`에서 다음 hook과 DTO를 가져온다.

- `useAdminUserDetailQuery(userId)`
- `useUserWithdrawalsQuery({ page, size, sort })`
- `useUpdateUserPointsMutation()` → `{ userId, payload: { amount, direction, reason } }`
- `useUpdateUserStatusMutation()` → `{ userId, payload: { status, reason } }`
- `useGrantUserAuthoritiesMutation()` → `{ userId, payload: { citizenCard, roles } }`

`userId`는 호출자가 별도로 전달하는 정수 ID다. JS 안전 정수 범위를 넘는 int64는 문자열로 전달한다. 응답의 `publicId`를 userId로 매핑하지 않는다. 목록은 서버 순서를 그대로 유지한다. 탈퇴 목록은 서버 설명대로 최신순 고정이며 sort 입력으로 정렬 변경을 보장하지 않는다.

## 검증

| 명령 | 결과 |
| --- | --- |
| `node --test tests/admin-users-contract.test.mjs tests/admin-users-query-mutation.test.mjs tests/logic-api-types.test.mjs` | 20개 통과, 실패 0개. 신규 19개 및 기존 타입 검사 1개. |
| `npm run lint` | 통과 |
| `npm run build` | 타입 검사 및 Vite 빌드 통과 |
| `git diff --check` | 통과 |

빌드에는 `vite-tsconfig-paths`를 Vite 내장 설정으로 대체할 수 있다는 안내와 500 kB 초과 chunk 경고가 있었다. 이번 작업에서는 설정을 변경하지 않았다.

테스트는 실제 프로젝트 Axios interceptor·ApiClient와 MSW 응답을 통해 인증·오류 전달을 확인한다. 포인트 409 테스트는 전달 경계의 검증이며 서버 잔액 판정이나 미확정 차감 direction의 검증은 아니다. 실제 백엔드 호출과 화면 검증은 수행하지 않았다. 별도 리뷰 에이전트는 호출하지 않았다.

## 상태와 남은 작업

- 작업 위치: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`, `sy-main`, HEAD `52011e5ad746e3c62b7e75b0a3f11cf1472c6c78`.
- Git 변경 명령을 실행하지 않았다. 소스·테스트는 미커밋 상태다. 앞선 user 작업 단계에서는 기존 `/v1/users` 구현·타입·store와 `items` 기능을 변경하지 않았다.
- 사용자 답변 대기: 차감 direction의 정확한 enum 값. 확인 후 `USER_POINT_DIRECTION`에 추가하고 해당 요청 계약 테스트를 보완한다.
- 권한 API는 명세상 200 no-op이다. 실제 권한 부여 완료로 표시하면 안 된다.

## 후속 item 작업 결과

### 확정 계약

- 사용자가 임시 구현을 승인했다. enum은 임시 문자열이며, DTO의 각 필드는 반드시 존재하고 null 값을 허용한다. 누락과 undefined는 거부한다. PATCH도 모든 필드가 필수다.
- path의 itemId와 업로드 query subCategoryId·file은 명세대로 필수 유효값이다.
- 목록 query는 page·size를 포함한 모든 필드가 필수이며, null page·size에 기본값 1·10을 적용한다. 응답 페이지·total·순서는 변환하지 않는다.
- JSON의 null 값은 전송 payload에 보존한다. URL query의 null 값은 기존 Axios 기본 직렬화에 따라 생략된다. query DTO 자체의 필드 누락은 전송 전에 거부한다.
- 응답 DTO 객체 내부 필드의 null을 그대로 유지한다. 성공 envelope의 data가 null일 때 공용 ApiClient가 undefined로 정규화하므로 parser에서 다시 null로 전달한다. envelope 자체는 기존 공용 계약을 따른다.
- 수정 응답의 mainCateogoryId와 imageUrl, 요청·상세의 mainCategoryId와 image를 구분한다. 업로드 uuid를 생성 imageUuid에 자동 주입하거나 최신 ID에 1을 더하는 처리는 없다.

### 변경 파일과 기능

- `src/entities/items/api/items.dto.ts`: 목록·생성·상세·수정·업로드·일괄 상태·최신 ID의 요청/응답 DTO 및 Zod 검증. 기존 숫자 enum·0/1 boolean·Partial 수정 DTO 의존 제거.
- `src/entities/items/api/items.api.ts`: `/admin/items` 10개 함수와 인증·취소, 필수 field 검증, File 기반 multipart 구성. 모든 mutation이 ApiResult를 반환한다.
- `src/entities/items/api/items.parser.ts`: 객체·문자열·boolean·숫자 응답 구분과 nullable 보존.
- `src/entities/items/api/index.ts`, `src/entities/items/index.ts`: 새 factory·client·DTO·hook 공개. 기존 itemsApi 이름은 새 client를 가리킨다.
- `src/entities/items/model/{query-keys,item-query-options,item-mutation-options}.ts`: 캐시 key·query·mutation 흐름.
- `src/entities/items/hook/`: 조회 3개·변경 7개 hook. 화면이 없으므로 임의 폼 controller나 UI는 만들지 않았다.
- `tests/items-contract.test.mjs`: 신규 계약 검증 9개.
- `tests/items-query-mutation.test.mjs`: 신규 Axios·Query/Mutation observer 검증 11개.
- `tests/logic-api-contract.test.mjs`, `tests/logic-api-types.test.mjs`: 기존 item 회귀 검증을 새 endpoint·ApiResult·File·nullable DTO 계약에 맞게 갱신. 기존 인증·전송·실패·타입 보호 검증을 유지했다.

카테고리 API는 기존 계약을 유지한다. 앞선 user 소스도 변경하지 않았다. 기존 `model/item.enum.ts`의 과거 상수는 새 DTO에서 사용하거나 새 public API로 노출하지 않는다.

### UI 연결용 hook

`~/entities/items`에서 가져온다.

| API | hook | 입력 |
| --- | --- | --- |
| 목록 | `useItemListQuery` | `{ page, size, mainCategoryId, subCategoryId, gender, status, keyword }` |
| 상세 | `useItemDetailQuery` | `itemId` |
| 최신 ID | `useLatestItemIdQuery` | `{ subCategoryId, gender }` |
| 생성 | `useCreateItemMutation` | `{ payload: PostItemRequestDto }` |
| 수정 | `useUpdateItemMutation` | `{ itemId, payload: PatchItemRequestDto }` |
| 삭제 | `useDeleteItemMutation` | `{ itemId }` |
| 업로드 | `useUploadItemImageMutation` | `{ params: { subCategoryId }, payload: { file } }` |
| 리워드 토글 | `useToggleItemEventRewardMutation` | `{ itemId }` |
| 일괄 상태 변경 | `useUpdateBatchItemStatusMutation` | `{ payload: { itemIds, status } }` |
| 이미지 삭제 | `useDeleteItemImageMutation` | `{ itemId }` |

mutation의 `mutateAsync`와 `data`로 서버 응답을 받는다. Query·Mutation의 pending/success/error 상태는 TanStack Query 계약을 따른다. ID가 잘못된 상세 조회는 비활성화되며 직접 요청에서도 ID 검증을 적용한다.

캐시 갱신은 생성 시 목록·최신 ID, 수정 시 목록·해당 상세·최신 ID, 토글 시 목록·해당 상세, 일괄 변경 시 목록·지정 상세, 이미지 삭제 시 해당 상세로 제한한다. 일괄 변경 itemIds가 null이면 대상이 특정되지 않으므로 item 상세 전체를 재조회 대상으로 표시한다. 아이템 삭제는 진행 중 상세를 취소하고 해당 상세 캐시를 제거한다. 다른 도메인 캐시는 변경하지 않는다.

### 최종 검증과 한계

실행 명령:

```sh
node --test tests/items-contract.test.mjs tests/items-query-mutation.test.mjs tests/logic-api-contract.test.mjs tests/logic-api-types.test.mjs tests/item-category-contract.test.mjs tests/admin-users-contract.test.mjs tests/admin-users-query-mutation.test.mjs
npm run lint
npm run build
git diff --check
```

- 테스트 48개 통과, 실패·취소·건너뜀 0개. item 신규 20개, 기존 API·타입·카테고리 9개, 앞선 user 19개.
- lint 통과. build에서 TypeScript와 Vite 모두 통과. tsconfig paths plugin 안내·500 kB 초과 chunk 경고는 남아 있다.
- 실제 프로젝트 Axios interceptor·ApiClient와 MSW를 통해 10개 endpoint, query·JSON·multipart·인증·응답 전달을 검증했다. 실제 백엔드 호출이나 React hook의 화면 mount 검증은 수행하지 않았다. hook과 동일한 options를 사용하는 QueryObserver/MutationObserver의 상태·데이터·재조회·오류를 검증했다.
- 초기 타입 검사에서 Zod pipe 입력 타입과 서로 다른 QueryKey의 배열 추론 오류를 발견해 수정했다. 최종 build와 타입 회귀 테스트가 통과했다.
- 별도 리뷰 에이전트는 호출하지 않았다.
- 추후 enum 목록과 실제 필수·nullable 계약이 확정되면 `items.dto.ts`의 임시 검증을 강화해야 한다. 현재 요청의 임시 계약에 따른 구현은 완료했다.
- branch·HEAD는 위 기록과 같으며 commit·merge는 수행하지 않았다.

## 후속 조사: 모든 도메인의 목록 응답 일관성

전체 30개 entity 도메인을 조사한 결과, 사용자 설명의 `data: { items, total, page, size }`는 전역에 일관되게 반영되어 있지 않다. 상세 근거와 전 도메인 표는 [pagination-audit.md](unknown/pagination-audit.md)에 기록했다.

- items·관리자 탈퇴 로그·inquiries·cp-proposal·cp-vote 목록은 형태가 맞지만 DTO와 schema를 도메인별로 중복 정의한다.
- news는 items/totalElements/totalPages/pinnedItemCount를 사용한다. 8개 기존 CP 목록은 content/count/pagination을 parser·hook·controller·mock까지 사용한다.
- event·DAO는 기존 pagination 또는 TableApiResponseDto를 사용한다. DAO 제안·댓글에는 DTO 선언과 API 함수의 실제 반환 타입 차이도 있다.
- 구형 users·admin-settings·faq·sales는 목록 응답이 unknown이고 usage는 Axios 응답 제네릭이 없어 페이지 형식을 보장하지 않는다. VO는 임시 DTO와 fixture 단계다.
- 기본 size 20이 news·inquiries·cp-proposal·cp-vote·관리자 탈퇴 로그에 남아 있다. 화면에서도 news·제안·투표는 20을 명시한다.
- 기본 page/size 강제와 items/total/page/size 공용 응답 타입·schema가 없다. 기존 KPI 집계는 공통 total과 의미가 다를 수 있어 단순 필드 치환으로 처리하면 안 된다.
- 이번에는 읽기 전용 코드 조사와 자기 세션 기록만 수행했다. 이전 user·item 미커밋 변경을 보존했으며 실제 서버 호출·테스트·빌드를 추가 실행하지 않았다.

## 최신 구현: 기존 형식을 유지하는 응답 DTO 공용화

### 최종 계약과 적용 범위

- 사용자 요청의 최종 범위는 기존 형식을 일괄 변환하는 것이 아니라, 이미 공통 페이지 형태인 도메인에서 같은 DTO를 재사용하는 것이다.
- `src/shared/api/common/response.dto.ts`에 `ApiResponseDto<TData>`와 `PageResponseDto<TItem>`를 추가했다. envelope는 code/message/data 필수이고 data에 임의 null union을 더하지 않는다. 명시된 기존 null 응답은 `ApiResponseDto<null>`처럼 해당 API 타입으로 표현할 수 있다.
- 공용 페이지 DTO는 items/total/page/size 모두 필수·non-nullable이다. `createPageResponseSchema(itemSchema)`가 공통 필드와 항목을 검증한다.
- 적용 대상: 아이템 목록, 관리자 사용자 탈퇴 목록, 문의 목록, 시민제안 목록, 시민투표 목록. 각 도메인의 항목 schema는 그대로 사용한다.
- 관리자 탈퇴·시민제안·시민투표는 기존 size 최대100 검증을 유지한다. 아이템은 기존 명세 예시의 page/size 0을 유지한다. 이번에는 응답 공용화만 수행하며 기존 query 기본값을 변경하지 않았다.
- item 목록은 null data 및 nullable 페이지 필드를 거부한다. 앞선 item 임시 nullable 계약 중 항목 내부 필드와 상세·mutation 응답은 유지한다. 빈 목록은 명세대로 items가 빈 배열인 유효한 페이지 객체여야 한다.

### 연결과 보존한 동작

- `src/shared/api/api-client.ts`와 `common/api-result/api-result.mapper.ts`가 `ApiResponseDto<TData> | ServerResponse<TData>`를 수용한다. `server-response.ts`의 입력은 외부 데이터답게 unknown으로 받고 기존 정규화를 유지한다. 성공 판단·오류 변환·null→undefined 동작을 변경하지 않았다.
- inquiries·cp-proposal·cp-vote의 parser는 기존 pageCount 계산을 유지한다. cp-proposal 목록 hook은 readonly items를 복사해 기존 mutable rows 타입을 유지한다.
- count/opinionTotal/pinnedItemCount와 관련 기존 DTO·parser·UI·mock은 변경하지 않았다. TableApiResponseDto 및 일반 배열 응답도 그대로 유지한다.
- 새 공통 데이터 형식을 자동 적용하는 URL 추론·fallback·임의 ID나 통계 매핑을 추가하지 않았다.

### 검증

- 전체 34개 테스트 파일을 명시적으로 나열한 `node --test` 실행: **211개 통과**, 실패·취소·건너뜀0. `tests/common-response-contract.test.mjs`의 신규4개와 item 계약 추가1개, 기존 전체 회귀 검증을 포함한다.
- 신규 검증은 공용 메타의 누락·null·undefined 거부, 항목 타입 검증, 각 parser의 pageCount, 기존 최대 size, 새 envelope·일반 배열·기존 통계 객체의 참조 동일성과 false/0/빈 문자열/null 처리 보존을 확인한다.
- `tests/logic-api-types.test.mjs`에 공용 envelope와 페이지 타입의 필수·non-nullable 경계 및 일반 응답의 페이지 필드 부재 검증을 추가했다.
- 기존 item null 목록 성공 테스트는 최신 계약에 따라 오류 상태를 기대하도록 변경했다. mutation null 성공과 항목 nullable 검증은 유지했다.
- `npm run lint`: 통과. `npm run build`: TypeScript·Vite 통과. `git diff --check`: 통과.
- 빌드에는 기존 tsconfig paths plugin 안내와 500 kB 초과 chunk 경고가 있다. 실제 백엔드 호출·시각 검증·별도 리뷰 agent는 실행하지 않았다.
- `node --test tests/*.test.mjs`는 wildcard 경로 확인 문제로 정책 guard가 실행 전에 차단했다. 같은 명령을 반복하지 않고 프로젝트 안의 실제 34개 파일을 명시해 전체 실행을 완료했다.

작업 위치·branch·HEAD는 그대로이며 모든 변경은 미커밋이다. 기존 user·item 미커밋 변경을 보존했다. 현재 공용화 작업의 미완료 항목은 없다.
