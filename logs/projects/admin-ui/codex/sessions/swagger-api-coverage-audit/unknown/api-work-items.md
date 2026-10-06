# 전역 API 후속 작업 항목과 구현 차이

## 범위와 승인 구분

이 문서는 **13개 작업 묶음으로 106개 operation 전체**를 연결한다. 아래 작업 위치·검증·반영 방향은 다음 세션의 기술 인계이며 시민제안·투표(T01)를 제외한 소스 구현·새 화면·Git 변경은 아직 승인되지 않았다. 다른 작업 공간 이름이나 소유자를 임의로 배정하지 않았다. 각 세션은 [핸드오프](../handoff.md)의 실제 위치/승인 상태와 최신 소스를 다시 확인한다.

기준 소스는 `sy-main@4b0b7db45aa9d15bf918a1a084370594e138a124`. **74개 method/path 일치 / 32개 불일치 또는 부재**다. 74개 중 화면 호출37, hook까지35, API만2. 32개는 신규 호출 부재30 + 기존 점검의 경로/계약 불일치2다. 일치 호출은 동작 보증이 아니며 미사용은 자동 결함 판정이 아니다.

각 표의 요청 DTO는 requestBody와 query/path의 참조 schema다. primitive parameter, required/enum/format/nullable, 모든 성공/오류 예시는 method·path 링크의 [상세 계약](./api-contracts.md)에 있고, DTO 링크는 전체 schema 원문으로 이어진다. `없음/인라인`은 body가 반드시 없다는 뜻이 아니라 named schema 참조가 없다는 뜻이다.

## 작업 순서 제안

1. T01은 사용자 승인된 공간에서 이 문서 제공 후 이어갈 작업이다.
2. 별도 세션에서 이미 사용 중인 T09의 입력 검증, T08의 응답 매핑과 T07의 실제 경로 계약을 우선 검토할 수 있다. 이는 우선순위 제안이며 구현 승인이 아니다.
3. T02/T03/T05는 화면 연결 전에 DTO/빈 성공 파싱을 바로잡아야 한다. T04는 과거 확정 계약과 Swagger 충돌부터 해소한다.
4. T06의 동적 메뉴·관리자 권한은 로그인·route·navigation의 공유 계약을 먼저 정한다. T12/T13은 제품 사용 여부를 먼저 정한다.
5. 공통 API/error 계층은 기본적으로 재사용한다. 여러 작업을 이유로 전역 enum·envelope·추상화를 동시에 재설계하지 않는다.

## 색인

| 작업 | operation 수 | 범위 |
| --- | --- | --- |
| [T01](#t01) | 8 | 시민제안·투표 |
| [T02](#t02) | 5 | 사용자 |
| [T03](#t03) | 2 | 이용내역 |
| [T04](#t04) | 11 | 영상·플레이리스트 |
| [T05](#t05) | 11 | 문의·문의 타입 |
| [T06](#t06) | 15 | 로그인·계정·역할·권한·메뉴 |
| [T07](#t07) | 7 | 점검 설정 |
| [T08](#t08) | 8 | 공지사항·댓글 |
| [T09](#t09) | 14 | 아이템·분류 |
| [T10](#t10) | 16 | 출석·룰렛 이벤트 |
| [T11](#t11) | 3 | 소포 |
| [T12](#t12) | 4 | 외부 대시보드 |
| [T13](#t13) | 2 | 감사 내역·상태 확인 |

<a id="t01"></a>

## T01 — 시민제안·투표

| method·path | 요청 참조 DTO | HTTP 2xx envelope 참조 | 현재 상태 |
| --- | --- | --- | --- |
| [GET /citizen/proposals](./api-contracts.md#op-059) | 없음/인라인 | [ApiResponsePageResponseProposalSummaryResponse](./api-schema-catalog.md#schema-apiresponsepageresponseproposalsummaryresponse) | **화면 호출 연결 확인** · F01 |
| [GET /citizen/proposals/{proposalId}](./api-contracts.md#op-060) | 없음/인라인 | [ApiResponseProposalResponse](./api-schema-catalog.md#schema-apiresponseproposalresponse) | **화면 호출 연결 확인** · F01 |
| [PATCH /citizen/proposals/{proposalId}](./api-contracts.md#op-061) | [UpdateCitizenProposalStatusRequest](./api-schema-catalog.md#schema-updatecitizenproposalstatusrequest) | [ApiResponse](./api-schema-catalog.md#schema-apiresponse) | **일치 호출 없음** · F01 |
| [PATCH /citizen/proposals/{proposalId}/review-result](./api-contracts.md#op-062) | [UpdateCitizenProposalReviewResultRequest](./api-schema-catalog.md#schema-updatecitizenproposalreviewresultrequest) | [ApiResponse](./api-schema-catalog.md#schema-apiresponse) | **일치 호출 없음** · F01 |
| [GET /citizen/proposals/summary](./api-contracts.md#op-063) | 없음/인라인 | [ApiResponseProposalStatusCountResponse](./api-schema-catalog.md#schema-apiresponseproposalstatuscountresponse) | **일치 호출 없음** · F01 |
| [GET /citizen/votes](./api-contracts.md#op-064) | 없음/인라인 | [ApiResponsePageResponseVoteSummaryResponse](./api-schema-catalog.md#schema-apiresponsepageresponsevotesummaryresponse) | **화면 호출 연결 확인** |
| [GET /citizen/votes/{voteId}](./api-contracts.md#op-065) | 없음/인라인 | [ApiResponseVoteDetailResponse](./api-schema-catalog.md#schema-apiresponsevotedetailresponse) | **화면 호출 연결 확인** |
| [GET /citizen/votes/summary](./api-contracts.md#op-066) | 없음/인라인 | [ApiResponseVoteStatusCountResponse](./api-schema-catalog.md#schema-apiresponsevotestatuscountresponse) | **일치 호출 없음** |

**진행 상태·위치:** 구현 승인과 별도 branch/worktree 생성 완료. 소스 구현은 아직 시작하지 않았다. [핸드오프의 시민제안 작업 공간](../handoff.md#citizen-workspace)을 사용한다. 요청된 전역 핸드오프를 먼저 제공하는 단계다. 역할은 Logic이며 기존 UI 구조·KPIStripItem·callback을 활용한다.

**F01 — 현재와 명세의 차이**

- [src/entities/cp-proposal/api/cp-proposal.api.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/cp-proposal/api/cp-proposal.api.ts): GET 목록/상세는 `/citizen/proposals`를 사용하지만 변경은 `POST /v1/cp/proposals/{id}/process`에 `{status?, department?, reviewComment?}`를 보낸다. 이번 Swagger는 상태 PATCH와 review-result PATCH로 분리되어 있다. 기존 POST를 실서버에서도 미지원한다고 판정한 것은 아니다.
- 상태 요청 [UpdateCitizenProposalStatusRequest](./api-schema-catalog.md#schema-updatecitizenproposalstatusrequest)는 서버 enum `RECEIVED / UNDER_REVIEW / ADOPTED / REJECTED`. 기존 UI enum `RECEIVED / REVIEWING / ADOPTED / RETURNED`과 기존 mapper를 경계에서 연결한다. UI enum을 그대로 보내면 안 된다.
- [src/entities/cp-proposal/api/cp-proposal.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/cp-proposal/api/cp-proposal.dto.ts)에 상세 `reviewResult`가 빠져 있고 [src/entities/cp-proposal/api/cp-proposal.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/cp-proposal/api/cp-proposal.parser.ts)는 `reviewComment: ""`로 고정한다. 서버 값을 기존 화면 `reviewComment`에 매핑해야 한다.
- 현재 [src/entities/cp-proposal/hook/use-cp-proposal-process-mutation.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/cp-proposal/hook/use-cp-proposal-process-mutation.ts)는 응답을 detail로 파싱해 `setQueryData`한다. 새 두 PATCH의 성공 예시는 `{code:"SUCCESS",message:"성공",data:null}`이다. detail을 응답으로 받는다는 가정을 제거해야 한다.
- 목록 KPI는 검색 결과 목록의 `total` 하나를 보여주며 summary 요청이 없다. proposal summary는 `total/received/underReview/adopted/rejected`, vote summary는 `total/inProgress/closed`. 투표의 DRAFT/UPCOMING/CANCELLED도 전체에 포함될 수 있으므로 `total=inProgress+closed`로 만들지 않는다.

**사용자가 확정한 세 가지 결정 — 다시 질문하지 않는다**

1. 담당부서 조회·변경 계약이 없으므로 이번 연결에서 제외한다. 선택 시 미지원 안내를 표시하고 변경 요청을 차단한다. 가상 부서 endpoint·ID·변경 성공을 만들지 않는다.
2. 상세 reviewResult는 null 또는 필드 누락을 허용하며 기존 입력란에는 빈 문자열로 표시한다. Swagger의 string 예시만으로 non-null 필수를 강제하지 않는다.
3. 개발용 시민제안·투표 MSW 가로채기를 제거하여 개발 환경에서도 실제 서버를 호출한다. 새 mock으로 계속 가로채는 작업으로 바꾸지 않는다.

**수정 순서와 연결 계약**

1. 기존 `cp-proposal.dto.ts / parser.ts`에 status·review 요청, 두 summary 응답, nullish reviewResult 매핑을 보강한다. ID는 기존 `cpProposalIdSchema`와 목록/상세에서 얻는 proposal ID를 재사용한다. review 요청은 기존 trim 제출 동작에 최대 5,000자·공백 거부를 더한다. 검토 저장은 상태를 바꾸지 않고 이전 내용을 덮어쓴다는 명세를 지킨다.
2. `cp-proposal.api.ts`에 정확한 두 PATCH/summary GET, [src/entities/cp-vote/api/cp-vote.api.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/cp-vote/api/cp-vote.api.ts)에 summary GET을 연결한다. envelope는 공통 ApiClient에 맡긴다.
3. 기존 `model/query-keys.ts`와 `hook/`를 확장한다. 상태 성공 후 목록·해당 상세·제안 summary가 최신 상태가 되도록 취소/무효화한다. review 저장 후 해당 상세를 재조회한다. void 성공에 detail을 합성해 넣지 않는다. 실패 시 성공 알림·캐시 성공 처리·초안 초기화를 하지 않는다.
4. [src/pages/cp-proposal/hook/use-cp-proposal-list-process.tsx](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/pages/cp-proposal/hook/use-cp-proposal-list-process.tsx)의 부서 변경 callback을 승인된 안내·차단 동작으로 바꾸고 상태 변경만 보낸다. 기존 `onSuccess(updated)`에서 updated.id를 사용하는 가정은 요청 변수의 ID/재조회 데이터 기준으로 맞춘다.
5. [src/pages/cp-proposal/hook/use-cp-proposal-detail-process.tsx](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/pages/cp-proposal/hook/use-cp-proposal-detail-process.tsx)의 `reviewComment/canSave/isSaving/changeReviewComment/save` 계약을 유지하며 새 mutation에 연결한다. 성공 직후 초안과 서버 재조회가 서로 덮어쓰지 않게 기존 detail ID별 초안 상태를 보존한다.
6. [src/pages/cp-proposal/hook/use-cp-proposal-list-data.tsx](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/pages/cp-proposal/hook/use-cp-proposal-list-data.tsx), [src/pages/cp-vote/hook/use-cp-vote-list-data.tsx](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/pages/cp-vote/hook/use-cp-vote-list-data.tsx)의 기존 `KpiStripItem[]`에 서버 summary를 연결한다. 목록 검색 건수와 전역 summary를 섞지 않는다. 로딩·오류·재시도는 기존 hook 패턴으로 처리하고 새로운 표시 정책이 필요한 경우 확인한다.
7. [src/mocks/handlers.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/mocks/handlers.ts)에서 시민제안·투표 handler 등록을 제거하고 [src/app/mock-api-policy.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/app/mock-api-policy.ts)의 `/citizen/` mock 전용 판정을 해제한다. 기존 `/v1/cp/`의 다른 기능과 테스트 전용 mock 자산을 임의 삭제하지 않는다. 브라우저 handler 제거와 테스트 fixture 사용은 구별한다.

**추가 주의점:** 제안 author 검색은 명세상 부분일치인데 기존 mock은 완전일치여서 mock 화면 동작을 서버 계약으로 삼으면 안 된다. 제안 목록의 status/sort 반복 query, page 기본1·size 기본20/상한100은 operation 설명과 기존 DTO를 함께 확인한다. 투표의 status 5개, 종료 전 관리자 득표 집계, totalCount=agreeCount+disagreeCount, 기간 경계 포함·updatedAt 의미는 원문 설명을 보존하며 기존 투표 목록/상세 파싱을 회귀 검증한다.

**재사용/경계:** `useStatusTransition`, `useDialog`, 공통 API·페이지 schema, 기존 query keys, 목록·상세 controller와 KPI props를 확장한다. UI 구조 수정은 이 Logic 작업에 포함되지 않는다. `handlers.ts`, `mock-api-policy.ts`, 공통 tests는 다른 기능과 겹칠 수 있으므로 병합 전 변경을 재대조한다.

**완료 조건·검증:** 두 PATCH의 method/body/ID, null 성공, reviewResult 문자열/null/누락, 5,000자/공백, summary DTO·cache 갱신, 부서 선택 시 요청 없음, 개발 MSW 비가로채기, 기존 목록/상세·취소 동작을 검증한다. 기존 `tests/citizen-proposals-contract.test.mjs`, `citizen-votes-contract.test.mjs`, `citizen-proposals-msw.test.mjs`, `citizen-votes-msw.test.mjs`, `cp-comment-proposal-input-boundaries.test.mjs`, `mock-api-policy.test.mjs`의 해당 assertion을 유지·보강한다. 등록 정책 변경으로 기대값이 바뀌면 이유와 대체 검증을 남긴다.

**다음 인계:** 같은 시민제안 작업 공간에서 Logic 구현/검증 결과를 전달한다. commit·merge는 아직 승인되지 않았다.

<a id="t02"></a>

## T02 — 사용자

| method·path | 요청 참조 DTO | HTTP 2xx envelope 참조 | 현재 상태 |
| --- | --- | --- | --- |
| [GET /admin/users/{userId}](./api-contracts.md#op-042) | 없음/인라인 | [ApiResponseAdminUserResponse](./api-schema-catalog.md#schema-apiresponseadminuserresponse) | **API·hook 정의, 화면 사용처 없음** · F02 |
| [POST /admin/users/{userId}/authorities](./api-contracts.md#op-043) | [GrantUserAuthorityRequest](./api-schema-catalog.md#schema-grantuserauthorityrequest) | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **API·hook 정의, 화면 사용처 없음** · F05 |
| [POST /admin/users/{userId}/points](./api-contracts.md#op-044) | [AdjustUserPointRequest](./api-schema-catalog.md#schema-adjustuserpointrequest) | 예시/인라인 | **API·hook 정의, 화면 사용처 없음** · F02 |
| [PATCH /admin/users/{userId}/status](./api-contracts.md#op-045) | [UpdateUserStatusRequest](./api-schema-catalog.md#schema-updateuserstatusrequest) | 예시/인라인 | **API·hook 정의, 화면 사용처 없음** |
| [GET /admin/users/withdrawals](./api-contracts.md#op-046) | 없음/인라인 | [ApiResponsePageResponseUserWithdrawLogResponse](./api-schema-catalog.md#schema-apiresponsepageresponseuserwithdrawlogresponse) | **API·hook 정의, 화면 사용처 없음** |

**상태·역할·작업 공간:** 5개 API/DTO/hook은 있으며 화면 소비를 찾지 못했다. Logic 계약 보정과 UI 연결은 구분된 후속 제안이고, 목적지 branch/worktree·화면 범위는 미정이다. 기존 [src/entities/users/api/admin-users.api.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.api.ts), [src/entities/users/api/admin-users.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.dto.ts), [src/entities/users/api/admin-users.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.parser.ts), [src/entities/users/model/admin-user.enum.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/model/admin-user.enum.ts)를 확장 후보로 삼는다.

**F02/F05/F09 — 차이와 영향**

- GET `/admin/users/{userId}`의 [AdminUserResponse](./api-schema-catalog.md#schema-adminuserresponse)의 status: 서버 `ACTIVE/SUSPENDED/WITHDRAWN`, 현재 공통 enum `ACTIVE/SUSPEND/WITHDRAWN`. 실제 SUSPENDED 응답이 들어오면 Zod 실패 경로다. 반대로 [UpdateUserStatusRequest](./api-schema-catalog.md#schema-updateuserstatusrequest) 요청은 `ACTIVE/SUSPEND`이므로 전역 문자열 치환하면 요청이 틀어진다.
- [AdjustUserPointRequest](./api-schema-catalog.md#schema-adjustuserpointrequest): direction `RECHARGE/DEDUCT`, amount integer. 현재 `USER_POINT_DIRECTION`에는 RECHARGE만 있고 amount는 positive number여서 소수를 허용한다. reason은 Swagger 필수 목록에 없지만 로컬 schema는 필수 string이다.
- [UpdateUserStatusRequest](./api-schema-catalog.md#schema-updateuserstatusrequest)의 reason도 명세의 필수 목록과 현지 validator 차이를 확인한다. 운영상 이유 입력 필수를 유지할지는 사용자 확인 대상이며 Swagger optional만으로 업무 입력 규칙을 없애지 않는다.
- `POST /admin/users/{userId}/authorities`는 ApiResponseVoid인데 현재 parser가 string을 기대한다. null 성공 정규화 후 실패하는 경로는 [오류 문서](./api-errors-and-integration.md)를 참조한다.

**반영 방향:** 요청/응답 status schema를 계약별로 분리하고 필요한 UI 상태 mapper를 명시한다. DEDUCT를 실제 업무 입력과 연결하려면 범위·확인창·사유 규칙을 먼저 확인한다. 기존 `admin-users-query-options.ts / admin-users-mutation-options.ts / admin-users-query-keys.ts`의 성공 후 갱신 규칙을 보존하며 Void/parser를 맞춘다. 현재 userId는 int64를 위한 문자열·BigInt 정규화가 있으므로 일반 Number 변환을 추가하지 않는다.

**미확정 사항·질문:** 어떤 화면/경로에 연결할지, 기존 사용자 목록의 어떤 필드가 이 API의 userId인지, publicId와의 관계, 역할 strings/시민카드 권한 입력 출처, 차감·사유 업무 정책. Swagger에 `GET /admin/users` 목록이 없으므로 임의 생성하지 않는다. `accounts.adminId`와 서비스 사용자 userId도 별개로 확인한다.

**완료 조건·검증:** `node --test tests/admin-users-contract.test.mjs tests/admin-users-query-mutation.test.mjs`에 response SUSPENDED와 request SUSPEND를 별개 assertion으로 검증, DEDUCT/정수/409/404/null 성공 및 캐시 갱신을 포함한다. Logic 결과를 UI 담당에게 ID·mutation variables·에러·pending 계약과 함께 같은 작업 공간에서 인계한다. 구현 승인과 공간 결정은 아직 없다.

<a id="t03"></a>

## T03 — 이용내역

| method·path | 요청 참조 DTO | HTTP 2xx envelope 참조 | 현재 상태 |
| --- | --- | --- | --- |
| [GET /admin/usage/item](./api-contracts.md#op-040) | [GetItemHistoryListRequest](./api-schema-catalog.md#schema-getitemhistorylistrequest) | [ApiResponsePageResponseItemHistoryResponse](./api-schema-catalog.md#schema-apiresponsepageresponseitemhistoryresponse) | **API·hook 정의, 화면 사용처 없음** · F03 |
| [GET /admin/usage/point](./api-contracts.md#op-041) | [GetPointHistoryListRequest](./api-schema-catalog.md#schema-getpointhistorylistrequest) | [ApiResponsePageResponsePointHistoryResponse](./api-schema-catalog.md#schema-apiresponsepageresponsepointhistoryresponse) | **API·hook 정의, 화면 사용처 없음** · F03 |

**상태·재사용:** 2개 GET의 API·query hook은 있으나 화면 미연결. [src/entities/usage/api/admin-usage.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/usage/api/admin-usage.dto.ts), [src/entities/usage/api/admin-usage.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/usage/api/admin-usage.parser.ts), [src/entities/usage/api/admin-usage.api.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/usage/api/admin-usage.api.ts), `model/admin-usage-query-options.ts`, `hook/use-point-usage-list-query.ts / use-item-usage-list-query.ts`를 재사용한다. 역할 Logic, 작업 공간은 미정이다.

**F03 — 차이:** [PointHistoryResponse](./api-schema-catalog.md#schema-pointhistoryresponse)와 [ItemHistoryResponse](./api-schema-catalog.md#schema-itemhistoryresponse)는 `objectName`을 반환하지만 로컬 response schema는 필수 nullable `itemName`을 요구한다. 명세대로 objectName만 오면 파싱 실패한다. [GetPointHistoryListRequest](./api-schema-catalog.md#schema-getpointhistorylistrequest), [GetItemHistoryListRequest](./api-schema-catalog.md#schema-getitemhistorylistrequest)의 startDate/endDate는 필수이나 로컬은 optional이고, by도 임의 string이다. 포인트 by는 `USER_ID/USER_NAME`, 아이템은 `USER_ID/USER_NAME/ITEM_NAME`이다.

**반영 순서:** 원시 DTO를 objectName 계약에 맞추고 화면 모델이 itemName을 계속 사용한다면 parser에서 이름을 명시적으로 매핑한다. API DTO와 UI 모델을 같은 것으로 간주해 모든 itemName을 치환하지 않는다. 필수 날짜·검색 enum·반복 sort를 요청 경계에서 검증한다. 검색 query key·AbortSignal을 유지한다.

**확인할 결정:** 조회 화면의 날짜 입력 출처, 기본 검색 기간·최대 기간·start>end 처리, by/keyword 조합 정책 중 operation 원문에서 확정되지 않은 항목. 임의로 최근7일 등을 기본값으로 넣지 않는다. 공통 기간 validator와 기존 검색 hook의 재사용 적합성부터 확인한다.

**완료/검증/인계:** objectName 정상 목록, 누락/잘못된 데이터의 실패, 필수 날짜 및 by enum을 `node --test tests/usage-contract.test.mjs tests/usage-query.test.mjs`로 검증한다. Logic 완료 후 확정 query/row 모델·로딩·오류·재시도 계약을 UI에 전달한다. 신규 화면 승인은 없다.

<a id="t04"></a>

## T04 — 영상·플레이리스트

| method·path | 요청 참조 DTO | HTTP 2xx envelope 참조 | 현재 상태 |
| --- | --- | --- | --- |
| [GET /admin/video](./api-contracts.md#op-047) | [Pageable](./api-schema-catalog.md#schema-pageable) | [ApiResponsePageResponseGetVideoListResponse](./api-schema-catalog.md#schema-apiresponsepageresponsegetvideolistresponse) | **API·hook 정의, 화면 사용처 없음** |
| [POST /admin/video](./api-contracts.md#op-048) | [CreateVideoRequest](./api-schema-catalog.md#schema-createvideorequest) | [ApiResponseLong](./api-schema-catalog.md#schema-apiresponselong) | **API·hook 정의, 화면 사용처 없음** · F04 |
| [DELETE /admin/video/{videoId}](./api-contracts.md#op-049) | 없음/인라인 | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **API·hook 정의, 화면 사용처 없음** |
| [GET /admin/video/{videoId}](./api-contracts.md#op-050) | 없음/인라인 | [ApiResponseObject](./api-schema-catalog.md#schema-apiresponseobject) | **API·hook 정의, 화면 사용처 없음** |
| [PATCH /admin/video/{videoId}](./api-contracts.md#op-051) | [UpdateVideoRequest](./api-schema-catalog.md#schema-updatevideorequest) | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **API·hook 정의, 화면 사용처 없음** · F04 |
| [POST /admin/video/{videoId}/thumbnail](./api-contracts.md#op-052) | 없음/인라인 | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **API·hook 정의, 화면 사용처 없음** |
| [GET /admin/video/playlists](./api-contracts.md#op-053) | [Pageable](./api-schema-catalog.md#schema-pageable) | [ApiResponsePageResponseGetPlaylistSummaryResponse](./api-schema-catalog.md#schema-apiresponsepageresponsegetplaylistsummaryresponse) | **API·hook 정의, 화면 사용처 없음** |
| [POST /admin/video/playlists](./api-contracts.md#op-054) | [CreatePlaylistRequest](./api-schema-catalog.md#schema-createplaylistrequest) | [ApiResponseLong](./api-schema-catalog.md#schema-apiresponselong) | **API·hook 정의, 화면 사용처 없음** |
| [DELETE /admin/video/playlists/{playlistId}](./api-contracts.md#op-055) | 없음/인라인 | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **API·hook 정의, 화면 사용처 없음** |
| [GET /admin/video/playlists/{playlistId}](./api-contracts.md#op-056) | 없음/인라인 | [ApiResponseGetPlaylistResponse](./api-schema-catalog.md#schema-apiresponsegetplaylistresponse) | **API·hook 정의, 화면 사용처 없음** |
| [PATCH /admin/video/playlists/{playlistId}](./api-contracts.md#op-057) | [UpdatePlaylistRequest](./api-schema-catalog.md#schema-updateplaylistrequest) | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **API·hook 정의, 화면 사용처 없음** |

**상태·재사용:** 영상6개·플레이리스트5개 API/hook은 구현되어 있지만 화면 소비를 찾지 못했다. [src/entities/video/api/video.api.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.api.ts), [src/entities/video/api/video.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.dto.ts), [src/entities/video/api/video.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.parser.ts), [src/entities/video/api/playlist.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.dto.ts), `model/video-query-options.ts / video-mutation-options.ts`가 기존 자산이다. 역할 Logic, 작업 공간 미정.

**F04 — 반드시 먼저 풀어야 할 계약 충돌**

- Swagger POST `/admin/video`: multipart body에 `data`([CreateVideoRequest](./api-schema-catalog.md#schema-createvideorequest), name 필수·description 선택)와 `file`이 필수다.
- Swagger PATCH `/admin/video/{videoId}`: `data`([UpdateVideoRequest](./api-schema-catalog.md#schema-updatevideorequest), name 필수)가 필수이고 file은 선택이다.
- 현재 `createVideoFileFormData`는 file만 append하며 등록·수정 모두 파일 필수다. DTO 주석에는 **사용자 확정 계약: 등록·수정 모두 file만 전송**이라고 적혀 있다. 이번 Swagger와 충돌하므로 새 명세를 자동 우선하거나 기존 주석을 자동 폐기하지 않는다.
- 상세 GET은 [ApiResponseObject](./api-schema-catalog.md#schema-apiresponseobject)의 data가 빈 schema인데 로컬 parser는 `string | null`만 허용한다. 문자열 URL/객체 어느 형태인지 미확정이다.
- [CreatePlaylistRequest](./api-schema-catalog.md#schema-createplaylistrequest)/[UpdatePlaylistRequest](./api-schema-catalog.md#schema-updateplaylistrequest)의 name 필수 계약에 비해 현재 DTO는 null을 허용한다(F09).

**필수 질문:** 등록·수정의 확정 계약이 file-only인지 data+file인지, JSON data part의 실제 Content-Type/인코딩 및 name/description 출처, 상세 응답 구조·nullable 의미, 플레이리스트 입력 범위·video ID 출처와 순서 정책. 새 추상화/폼을 임의 작성하지 않는다.

**확정 후 반영:** 기존 FormData 생성기·request DTO를 승인된 계약에 맞춰 확장하고 thumbnail의 단일-file 요청과 혼합하지 않는다. PATCH에서 파일 없는 메타데이터 수정이 승인되면 이를 테스트한다. 상세 parser를 확정한 응답으로 보정하며 기존 목록·detail·playlist 캐시 갱신과 취소를 유지한다.

**완료/검증/인계:** `node --test tests/video-contract.test.mjs tests/video-query-mutation.test.mjs`에 multipart part 이름·필수/선택·파일 미첨부 수정·상세 payload·playlist name을 확인한다. 테스트 fixture를 새 계약 확인의 대용으로 쓰지 않는다. Logic DTO/hooks가 확정된 뒤 UI 설계·연결을 별도 요청한다.

<a id="t05"></a>

## T05 — 문의·문의 타입

| method·path | 요청 참조 DTO | HTTP 2xx envelope 참조 | 현재 상태 |
| --- | --- | --- | --- |
| [GET /admin/inquiries](./api-contracts.md#op-004) | 없음/인라인 | [ApiResponsePageResponseInquirySummaryResponse](./api-schema-catalog.md#schema-apiresponsepageresponseinquirysummaryresponse) | **API·hook 정의, 화면 사용처 없음** |
| [DELETE /admin/inquiries/{inquiryId}](./api-contracts.md#op-005) | 없음/인라인 | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **API·hook 정의, 화면 사용처 없음** · F05 |
| [GET /admin/inquiries/{inquiryId}](./api-contracts.md#op-006) | 없음/인라인 | [ApiResponseInquiryDetailResponse](./api-schema-catalog.md#schema-apiresponseinquirydetailresponse) | **API·hook 정의, 화면 사용처 없음** |
| [DELETE /admin/inquiries/{inquiryId}/answer](./api-contracts.md#op-007) | 없음/인라인 | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **API·hook 정의, 화면 사용처 없음** · F05 |
| [POST /admin/inquiries/{inquiryId}/answer](./api-contracts.md#op-008) | [InquiryAnswerRequest](./api-schema-catalog.md#schema-inquiryanswerrequest) | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **API·hook 정의, 화면 사용처 없음** · F05 |
| [PUT /admin/inquiries/{inquiryId}/answer](./api-contracts.md#op-009) | [InquiryAnswerRequest](./api-schema-catalog.md#schema-inquiryanswerrequest) | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **API·hook 정의, 화면 사용처 없음** · F05 |
| [PATCH /admin/inquiries/{inquiryId}/status](./api-contracts.md#op-010) | [UpdateInquiryStatusRequest](./api-schema-catalog.md#schema-updateinquirystatusrequest) | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **API·hook 정의, 화면 사용처 없음** · F05 |
| [GET /admin/inquiries/types](./api-contracts.md#op-011) | [Pageable](./api-schema-catalog.md#schema-pageable) | [ApiResponsePageResponseGetInquiryTypeResponse](./api-schema-catalog.md#schema-apiresponsepageresponsegetinquirytyperesponse) | **API·hook 정의, 화면 사용처 없음** |
| [POST /admin/inquiries/types](./api-contracts.md#op-012) | [CreateInquiryTypeRequest](./api-schema-catalog.md#schema-createinquirytyperequest) | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **API·hook 정의, 화면 사용처 없음** · F05 |
| [DELETE /admin/inquiries/types/{typeId}](./api-contracts.md#op-013) | 없음/인라인 | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **API·hook 정의, 화면 사용처 없음** · F05 |
| [PUT /admin/inquiries/types/{typeId}](./api-contracts.md#op-014) | [UpdateInquiryTypeRequest](./api-schema-catalog.md#schema-updateinquirytyperequest) | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **API·hook 정의, 화면 사용처 없음** · F05 |

**상태·재사용:** 문의7개·문의 타입4개 API/hook은 있으나 화면 사용처 없음. [src/entities/inquiries/api/inquiry.api.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.api.ts), [src/entities/inquiries/api/inquiry.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.dto.ts), [src/entities/inquiries/api/inquiry.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.parser.ts), [src/entities/inquiries/api/inquiry-type.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.dto.ts), [src/entities/inquiries/api/inquiry-type.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.parser.ts), `model/inquiry-mutation-options.ts / inquiry-type-mutation-options.ts / query-keys.ts`를 먼저 활용한다. Logic, 작업 공간 미정.

**F05 — 빈 성공 응답과 mutation 처리:** 문의 삭제·상태·답변 등록/수정/삭제 5개, 타입 등록/수정/삭제 3개는 Swagger ApiResponseVoid지만 현재 mutation 응답 schema는 string이다. `data:null`이면 공통 client가 undefined로 바꾸고 parser에서 실패하여 onSuccess 캐시 갱신까지 건너뛴다. 명세의 Void.data는 `{}`여서 실제 null 반환을 아직 확인하지 못했다는 조건을 유지한다.

**F09 — 타입 목록:** OpenAPI Pageable에는 sort가 있지만 현재 type list query는 page/size만 있다. Pageable의 minimum0와 공통 응답 page>0도 구분하여 서버 기준을 확인한다.

**반영 방향:** 실제 빈 성공 payload 계약 확인 후 기존 공통 성공 parser 재사용 여부를 조사하고 mutation의 반환형·소비자를 함께 보정한다. 빈 성공을 받았다고 생성/수정한 문의 객체를 합성하지 않는다. 기존 성공 callback의 목록·상세·타입 캐시 갱신은 유지한다. sort 필요 시 기존 반복 query 직렬화를 확장한다.

**필수 질문:** 화면 연결 대상, typeId 선택 출처, 답변 미등록 시 answerContent의 null/누락 형태, Void의 실제 성공 body, 타입 sort 지원·페이지 기준과 필요한 UI 옵션. 문의 입력·답변·상태 정책은 임의로 만들지 않는다.

**완료/검증/인계:** `node --test tests/inquiries-contract.test.mjs tests/inquiries-mutation.test.mjs tests/inquiry-types-contract.test.mjs tests/inquiry-types-query-mutation.test.mjs`로 빈 성공/실패 및 무효화를 검증한다. MSW는 기존 계약 검증 자산으로 유지하고, 테스트 통과를 위해 문자열 성공 fixture만 남기는 방식으로 문제를 숨기지 않는다. 최종 props·hook 계약을 UI에 인계한다.

<a id="t06"></a>

## T06 — 로그인·계정·역할·권한·메뉴

| method·path | 요청 참조 DTO | HTTP 2xx envelope 참조 | 현재 상태 |
| --- | --- | --- | --- |
| [GET /accounts](./api-contracts.md#op-001) | [GetAccountListRequest](./api-schema-catalog.md#schema-getaccountlistrequest) | [ApiResponsePageResponseAccountResponse](./api-schema-catalog.md#schema-apiresponsepageresponseaccountresponse) | **일치 호출 없음** |
| [PUT /accounts/{adminId}/roles](./api-contracts.md#op-002) | [UpdateAccountRolesRequest](./api-schema-catalog.md#schema-updateaccountrolesrequest) | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **일치 호출 없음** |
| [POST /auth/login](./api-contracts.md#op-058) | [LoginRequest](./api-schema-catalog.md#schema-loginrequest) | [AdminApiResponseTokenResponse](./api-schema-catalog.md#schema-adminapiresponsetokenresponse) | **화면 호출 연결 확인** |
| [GET /me](./api-contracts.md#op-095) | 없음/인라인 | [ApiResponseMeResponse](./api-schema-catalog.md#schema-apiresponsemeresponse) | **일치 호출 없음** · F06 |
| [GET /me/menus](./api-contracts.md#op-096) | 없음/인라인 | [ApiResponseListMenuGroupResponse](./api-schema-catalog.md#schema-apiresponselistmenugroupresponse) | **API만 정의** · F06 |
| [GET /menus](./api-contracts.md#op-097) | 없음/인라인 | [ApiResponseListManagedMenuResponse](./api-schema-catalog.md#schema-apiresponselistmanagedmenuresponse) | **API만 정의** · F06 |
| [PATCH /menus/{menuId}](./api-contracts.md#op-098) | [UpdateMenuRequest](./api-schema-catalog.md#schema-updatemenurequest) | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **일치 호출 없음** |
| [PUT /menus/order](./api-contracts.md#op-099) | [UpdateMenuOrderRequest](./api-schema-catalog.md#schema-updatemenuorderrequest) | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **일치 호출 없음** |
| [GET /permissions](./api-contracts.md#op-100) | 없음/인라인 | [ApiResponseListPermissionCategoryResponse](./api-schema-catalog.md#schema-apiresponselistpermissioncategoryresponse) | **일치 호출 없음** |
| [GET /roles](./api-contracts.md#op-101) | 없음/인라인 | [ApiResponseListRoleSummaryResponse](./api-schema-catalog.md#schema-apiresponselistrolesummaryresponse) | **일치 호출 없음** |
| [POST /roles](./api-contracts.md#op-102) | [CreateRoleRequest](./api-schema-catalog.md#schema-createrolerequest) | [ApiResponseCreateRoleResponse](./api-schema-catalog.md#schema-apiresponsecreateroleresponse) | **일치 호출 없음** |
| [DELETE /roles/{roleId}](./api-contracts.md#op-103) | 없음/인라인 | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **일치 호출 없음** |
| [GET /roles/{roleId}](./api-contracts.md#op-104) | 없음/인라인 | [ApiResponseRoleDetailResponse](./api-schema-catalog.md#schema-apiresponseroledetailresponse) | **일치 호출 없음** |
| [PATCH /roles/{roleId}](./api-contracts.md#op-105) | [UpdateRoleRequest](./api-schema-catalog.md#schema-updaterolerequest) | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **일치 호출 없음** |
| [PUT /roles/{roleId}/permissions](./api-contracts.md#op-106) | [UpdateRolePermissionsRequest](./api-schema-catalog.md#schema-updaterolepermissionsrequest) | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **일치 호출 없음** |

**상태·재사용:** 15개 중 login은 화면 연결, GET menus/me/menus 2개는 API만 있고, 나머지12개는 일치 호출을 찾지 못했다. Logic 계약·인증 상태 작업이며 동적 내비게이션/관리 화면의 구조 변경은 UI 역할과 별도 범위 합의가 필요하다. 작업 공간 미정.

**F06 — 기존과 신규 개념을 구분**

- [src/entities/menus/api/menus.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/menus/api/menus.dto.ts): ManagedMenuResponse.children이 현재 string[]이나 명세는 [ManagedMenuResponse](./api-schema-catalog.md#schema-managedmenuresponse) 객체 배열로 자기참조한다. 하위 메뉴 객체가 오면 parse 실패한다. 관리 메뉴 트리와 내 메뉴의 [MenuGroupResponse](./api-schema-catalog.md#schema-menugroupresponse)/[MenuItemResponse](./api-schema-catalog.md#schema-menuitemresponse)는 같은 DTO가 아니다.
- [src/features/auth/use-auth.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/features/auth/use-auth.ts)에 메뉴 연결 TODO가 있고 [src/widgets/side-navigation/lib/build-navigation-items.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/widgets/side-navigation/lib/build-navigation-items.ts)는 로컬 설정을 사용한다. GET /me 미구현으로 로그인 후 프로필/역할/메뉴 서버 초기화가 완성되어 있지 않다.
- [src/features/auth/model/auth-session.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/features/auth/model/auth-session.ts)는 accessToken-only 로그인에서 user=null, refresh token 제거로 처리한다. [TokenResponse](./api-schema-catalog.md#schema-tokenresponse)의 accessToken만 확인됐다는 사실과 로그인 후 /me 연결은 별도다. 새 refreshToken 값을 만들어 저장하지 않는다.
- [src/entities/admin-settings/api/admin-settings.api.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/admin-settings/api/admin-settings.api.ts)의 /v1/admins 계열을 신규 /accounts·/roles·/permissions 구현으로 세지 않았다.

**신규 계약의 입력 출처:** accounts 목록 [AccountResponse](./api-schema-catalog.md#schema-accountresponse)의 `id`와 path `adminId`의 관계를 확인한 뒤 [UpdateAccountRolesRequest](./api-schema-catalog.md#schema-updateaccountrolesrequest)의 `roleIds`를 연결한다. 역할은 [RoleSummaryResponse](./api-schema-catalog.md#schema-rolesummaryresponse)/[RoleDetailResponse](./api-schema-catalog.md#schema-roledetailresponse)의 `id`를 path `roleId`로 전달한다. 권한 변경 body는 [UpdateRolePermissionsRequest](./api-schema-catalog.md#schema-updaterolepermissionsrequest)의 **`permissionCodes: string[]`**이며 숫자 permission ID 배열이 아니다. 선택 값은 [PermissionCategoryResponse](./api-schema-catalog.md#schema-permissioncategoryresponse)의 permissions 안 [PermissionResponse](./api-schema-catalog.md#schema-permissionresponse).code를 따른다. 메뉴 order 요청 [UpdateMenuOrderRequest](./api-schema-catalog.md#schema-updatemenuorderrequest)·[Item](./api-schema-catalog.md#schema-item) 및 [UpdateMenuRequest](./api-schema-catalog.md#schema-updatemenurequest)를 API 원문대로 사용한다.

**반영 순서 제안:** 메뉴 response schema의 재귀 구조부터 확정 → /me·roles·permissions·accounts 전송/DTO → query/mutation 계약 → auth store/메뉴 초기화 → 승인된 화면 연결. 기존 `entities/menus/api`, `entities/auth/api`, `features/auth/model`와 공통 client를 재사용하며 새로운 entities slice 위치·공용화는 확인 후 정한다. 로그인 직후 요청 순서·실패 시 기존 세션 유지/해제·메뉴 미조회 fallback은 서비스 정책 결정이다.

**미확정 질문:** /me ID와 관리자 계정의 관계, 역할·권한 변경이 현재 세션에 적용되는 시점, 권한 없는 메뉴 숨김과 직접 URL 접근 처리, 부모/자식 메뉴 이동·정렬 규칙, 로컬 아이콘/route와 서버 메뉴 식별자의 매핑, 기존 /v1/admins 기능 대체 범위. 관리자 사용자와 일반 서비스 사용자(T02) 통합을 가정하지 않는다.

**완료/검증/인계:** 재귀 2단 이상 메뉴, 관리 메뉴/내 메뉴 모델 분리, accessToken-only 로그인, /me 초기화 실패, logout/cancel, 권한 갱신 무효화와 요청 ID 출처를 검증한다. 기존 `tests/menus-contract.test.mjs`, `auth-api-contract.test.mjs`, `auth-login-flow.test.mjs`, `auth-session.test.mjs`, `auth-route-guard.test.mjs`를 사용한다. UI와 auth 공유 파일 수정은 순차 수행한다. 모든 신규 관리 기능 구현 승인은 아직 없다.

<a id="t07"></a>

## T07 — 점검 설정

| method·path | 요청 참조 DTO | HTTP 2xx envelope 참조 | 현재 상태 |
| --- | --- | --- | --- |
| [GET /maintenance](./api-contracts.md#op-088) | 없음/인라인 | [ApiResponseListMaintenanceResponse](./api-schema-catalog.md#schema-apiresponselistmaintenanceresponse) | **기존 경로·계약 불일치** · F07 |
| [PATCH /maintenance](./api-contracts.md#op-089) | [UpdateMaintenanceItemRequest](./api-schema-catalog.md#schema-updatemaintenanceitemrequest) | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **기존 경로·계약 불일치** · F07 |
| [PATCH /maintenance/off](./api-contracts.md#op-090) | 없음/인라인 | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **일치 호출 없음** · F07 |
| [PATCH /maintenance/on](./api-contracts.md#op-091) | 없음/인라인 | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **일치 호출 없음** · F07 |
| [GET /maintenance/one](./api-contracts.md#op-092) | [GetMaintenanceItemRequest](./api-schema-catalog.md#schema-getmaintenanceitemrequest) | [ApiResponseMaintenanceResponse](./api-schema-catalog.md#schema-apiresponsemaintenanceresponse) | **일치 호출 없음** · F07 |
| [PATCH /maintenance/time](./api-contracts.md#op-093) | [SetMaintenanceTimeRequest](./api-schema-catalog.md#schema-setmaintenancetimerequest) | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **일치 호출 없음** · F07 |
| [PATCH /maintenance/version](./api-contracts.md#op-094) | [SetMaintenanceVersionRequest](./api-schema-catalog.md#schema-setmaintenanceversionrequest) | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **일치 호출 없음** · F07 |

**상태·재사용:** 정확히 일치하는7개 호출 없음. 이 중 GET/PATCH 기본 기능은 [src/entities/maintenance/api/maintenance.api.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/maintenance/api/maintenance.api.ts)에 있으나 경로·DTO 불일치이고, 나머지5개는 전용 API 미구현이다. Logic, 작업 공간 미정.

**F07 — URL만 교체할 수 없는 이유**

- 기본 URL `/v1/maintenance`; `VITE_SYNTHORIA_CONFIG_RESOURCE` 환경 override가 존재하지만 확인한 .env에는 없었다. 다른 배포 설정의 주입 여부는 미확인.
- 기존 GET DTO `{configKey,configValue,...}`; Swagger [MaintenanceResponse](./api-schema-catalog.md#schema-maintenanceresponse)는 `{key,value,...}`.
- 기존 업데이트는 `payload.configs`를 순회하여 각 `{key,value}`를 개별 PATCH한다. Swagger [UpdateMaintenanceItemRequest](./api-schema-catalog.md#schema-updatemaintenanceitemrequest)는 `{config:[{key,value}]}` 한 요청이다. config/configs/configKey는 각각 원시 DTO와 UI 모델 경계에서 구분해야 한다.
- /one 조회 query와 /version, /time, /on, /off의 목적별 요청도 따로 있다.

**반영 제안:** 기존 API·[src/entities/maintenance/api/maintenance.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/maintenance/api/maintenance.dto.ts)와 실제 설정 화면 hook/호출부를 함께 조사하여 승인된 endpoint·키 모델을 mapper로 연결한다. 임의로 단일-key 요청을 병렬화하지 않는다. 성공 후 읽어오는 설정 전체와 단일 설정 캐시 관계를 정하고 현재 저장 흐름을 유지한다.

**미확정 질문:** 배포 환경별 실제 경로, 설정 key 허용 목록/값 형태, 기존 UI의 어떤 동작을 config 일괄 PATCH와 전용 API 중 어디로 연결할지, 시간의 timezone/순서·버전·점검 on/off 업무 정책. API 이름만 보고 기존 UI의 키를 임의 매핑하지 않는다.

**완료/검증/인계:** 요청 횟수·정확한 config 배열, key/value 응답 매핑, 오류 시 부분 성공 표시 문제, 설정 재조회 및 override 경로를 확인한다. 전용 maintenance 테스트 파일은 조사 범위에서 확인하지 못했으므로 기존 node:test 배치 방식으로 필요한 회귀 테스트를 추가하는 범위를 계획한다. 새 프레임워크는 필요 없다. 승인 전 구현·실제 점검 변경 호출은 하지 않는다.

<a id="t08"></a>

## T08 — 공지사항·댓글

| method·path | 요청 참조 DTO | HTTP 2xx envelope 참조 | 현재 상태 |
| --- | --- | --- | --- |
| [GET /admin/news](./api-contracts.md#op-029) | 없음/인라인 | [NewsApiResponseList](./api-schema-catalog.md#schema-newsapiresponselist) | **화면 호출 연결 확인** · F08 |
| [POST /admin/news](./api-contracts.md#op-030) | [CreateNewsRequest](./api-schema-catalog.md#schema-createnewsrequest) | [NewsApiResponseVoid](./api-schema-catalog.md#schema-newsapiresponsevoid) | **화면 호출 연결 확인** · F08 |
| [DELETE /admin/news/{newsId}](./api-contracts.md#op-031) | 없음/인라인 | [NewsApiResponseVoid](./api-schema-catalog.md#schema-newsapiresponsevoid) | **화면 호출 연결 확인** · F08 |
| [GET /admin/news/{newsId}](./api-contracts.md#op-032) | 없음/인라인 | [NewsApiResponseDetail](./api-schema-catalog.md#schema-newsapiresponsedetail) | **화면 호출 연결 확인** · F08 |
| [PATCH /admin/news/{newsId}](./api-contracts.md#op-033) | [UpdateNewsRequest](./api-schema-catalog.md#schema-updatenewsrequest) | [NewsApiResponseVoid](./api-schema-catalog.md#schema-newsapiresponsevoid) | **화면 호출 연결 확인** · F08 |
| [GET /admin/news/{newsId}/comments](./api-contracts.md#op-034) | 없음/인라인 | [NewsApiResponseCommentList](./api-schema-catalog.md#schema-newsapiresponsecommentlist) | **일치 호출 없음** · F08 |
| [DELETE /admin/news/{newsId}/comments/{commentId}](./api-contracts.md#op-035) | 없음/인라인 | [NewsApiResponseVoid](./api-schema-catalog.md#schema-newsapiresponsevoid) | **일치 호출 없음** · F08 |
| [PATCH /admin/news/batch](./api-contracts.md#op-036) | [BatchUpdateNewsListRequest](./api-schema-catalog.md#schema-batchupdatenewslistrequest) | [NewsApiResponseVoid](./api-schema-catalog.md#schema-newsapiresponsevoid) | **일치 호출 없음** · F08 |

**상태·재사용:** 5개 CRUD/list는 현재 화면 연결, batch·댓글 GET/DELETE 3개는 미구현. [src/entities/news/api/news.api.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/news/api/news.api.ts), [src/entities/news/api/news.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/news/api/news.dto.ts), [src/entities/news/api/news.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/news/api/news.parser.ts), [src/pages/cp-news/hook/use-cp-news-list-controller.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/pages/cp-news/hook/use-cp-news-list-controller.ts)와 기존 mutation/query·폼을 확장한다. Logic, 작업 공간 미정.

**F08 — 차이**

- 목록 [NewsListResponse](./api-schema-catalog.md#schema-newslistresponse).isPinnedCount와 로컬 `pinnedItemCount`가 다르다. parser는 원래 서버 필드를 보존하지 않고 controller는 반환 items 중 pinned를 센다. 명세상 고정 공지가 매 페이지 반환되므로 현 상황에서는 같을 수 있지만 서버 count 계약 자체는 버려진다. 실서버 수치 불일치를 관측한 것은 아니다.
- batch body [BatchUpdateNewsListRequest](./api-schema-catalog.md#schema-batchupdatenewslistrequest), 댓글 목록 [PageResponseNewsCommentResponse](./api-schema-catalog.md#schema-pageresponsenewscommentresponse)/[NewsCommentResponse](./api-schema-catalog.md#schema-newscommentresponse) 연결이 없다.
- 댓글 DELETE의 newsId와 commentId는 각각 원 공지/그 공지의 댓글 데이터에서 얻어야 한다. 현재 cp-comment나 다른 게시판 ID를 재사용하지 않는다.

**반영 제안:** 서버 isPinnedCount를 도메인/화면에 어떤 이름으로 전달할지 mapper 경계를 정한다. batch에 선택한 newsIds와 확정된 변경 필드만 전송하고 성공 후 관련 list/detail을 갱신한다. 댓글 pagination과 delete 후 갱신은 기존 news key 구조에 맞춰 확장한다. 빈 ids, by/keyword 짝, comment list 필수 page/size는 원문 계약을 따른다.

**미확정 질문:** batch 적용 UI/허용 필드·선택 정책, 댓글 목록을 보여줄 기존/새 위치와 삭제 권한·확인 UX, isPinnedCount 표시 요구, 페이지 size/삭제 후 빈 페이지 처리 중 미정인 정책. 새로운 댓글 화면은 UI 역할 범위 승인 후 진행한다.

**완료/검증/인계:** `tests/news-contract.test.mjs`, `news-mutation.test.mjs`, `news-list-controller.test.mjs`, `news-msw.test.mjs`에 필드 매핑·batch·댓글 pagination/ID·필드 오류·null 성공/실패 갱신을 추가한다. 댓글 없음 404도 `NEWS_NOT_FOUND`인 예시를 임의 코드로 변경하지 않는다.

<a id="t09"></a>

## T09 — 아이템·분류

| method·path | 요청 참조 DTO | HTTP 2xx envelope 참조 | 현재 상태 |
| --- | --- | --- | --- |
| [GET /admin/items](./api-contracts.md#op-015) | [GetItemsRequest](./api-schema-catalog.md#schema-getitemsrequest) | [ApiResponsePageResponseGetItemSummaryResponse](./api-schema-catalog.md#schema-apiresponsepageresponsegetitemsummaryresponse) | **화면 호출 연결 확인** |
| [POST /admin/items](./api-contracts.md#op-016) | [CreateItemRequest](./api-schema-catalog.md#schema-createitemrequest) | [ApiResponseCreateItemResponse](./api-schema-catalog.md#schema-apiresponsecreateitemresponse) | **화면 호출 연결 확인** · F09 |
| [DELETE /admin/items/{itemId}](./api-contracts.md#op-017) | 없음/인라인 | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **화면 호출 연결 확인** |
| [GET /admin/items/{itemId}](./api-contracts.md#op-018) | 없음/인라인 | [ApiResponseGetItemDetailResponse](./api-schema-catalog.md#schema-apiresponsegetitemdetailresponse) | **화면 호출 연결 확인** |
| [PATCH /admin/items/{itemId}](./api-contracts.md#op-019) | [UpdateItemRequest](./api-schema-catalog.md#schema-updateitemrequest) | [ApiResponseUpdateItemResponse](./api-schema-catalog.md#schema-apiresponseupdateitemresponse) | **화면 호출 연결 확인** |
| [DELETE /admin/items/{itemId}/image](./api-contracts.md#op-020) | 없음/인라인 | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **화면 호출 연결 확인** |
| [PATCH /admin/items/batch](./api-contracts.md#op-021) | [UpdateItemsListStatusRequest](./api-schema-catalog.md#schema-updateitemsliststatusrequest) | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **화면 호출 연결 확인** |
| [GET /admin/items/categories](./api-contracts.md#op-022) | 없음/인라인 | [ApiResponseListGetItemCategoryResponse](./api-schema-catalog.md#schema-apiresponselistgetitemcategoryresponse) | **화면 호출 연결 확인** |
| [POST /admin/items/categories](./api-contracts.md#op-023) | [CreateItemCategoryRequest](./api-schema-catalog.md#schema-createitemcategoryrequest) | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **화면 호출 연결 확인** |
| [DELETE /admin/items/categories/{categoryId}](./api-contracts.md#op-024) | 없음/인라인 | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **화면 호출 연결 확인** |
| [PATCH /admin/items/categories/{categoryId}](./api-contracts.md#op-025) | [UpdateItemCategoryRequest](./api-schema-catalog.md#schema-updateitemcategoryrequest) | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **화면 호출 연결 확인** |
| [GET /admin/items/latest/id](./api-contracts.md#op-026) | [GetItemLatestIdRequest](./api-schema-catalog.md#schema-getitemlatestidrequest) | [ApiResponseLong](./api-schema-catalog.md#schema-apiresponselong) | **API·hook 정의, 화면 사용처 없음** |
| [PATCH /admin/items/toggle/event/reward/{itemId}](./api-contracts.md#op-027) | 없음/인라인 | [ApiResponseBoolean](./api-schema-catalog.md#schema-apiresponseboolean) | **화면 호출 연결 확인** |
| [POST /admin/items/upload](./api-contracts.md#op-028) | 없음/인라인 | [ApiResponseUploadItemImageResponse](./api-schema-catalog.md#schema-apiresponseuploaditemimageresponse) | **화면 호출 연결 확인** |

**상태·재사용:** 14개 API는 이미 존재한다. 최신 ID GET은 hook까지만 있고 화면은 수동 ID 입력을 사용한다. 나머지는 화면 호출을 확인했다. 별도 최신 ID 자동 적용은 사용자 요구가 아니라 미사용 endpoint이므로 자동 연결하지 않는다. Logic, 작업 공간 미정.

**F09 — 생성 필수값과 정수:** [CreateItemRequest](./api-schema-catalog.md#schema-createitemrequest)의 required는 description, excludeFromEventReward, gender, id, mainCategoryId, name, newBadgeUntil, paymentType, saleAmount, scopeMetaverse, status, subCategoryId다. imageUuid는 선택이다. [src/entities/items/api/items.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.dto.ts)의 생성 schema에는 이 필드 다수의 null을 허용하며, [src/pages/item/lib/item-form.model.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/pages/item/lib/item-form.model.ts)는 ID·금액 숫자 해석 중심이라 빈 필수값을 요청으로 만들 수 있다. saleAmount도 소수 허용이다.

**반영 제안:** 원시 요청 DTO는 non-null 필수 계약을 표현하되 폼의 편집 중 빈 상태까지 DTO로 강제하지 않는다. 기존 item-form validation/mapping 단계에서 필수 입력과 정수 제약을 검사한 뒤 DTO를 만든다. 생성 `scopeMetaverse/imageUuid`와 수정 `isShowApp/image`·응답 `image/imageUrl`은 자동 동일 필드로 취급하지 않는다. PATCH optional을 POST required로 일괄 통일하지 않는다. 기존 카테고리 API와 목록·상세·mutation keys를 보존한다.

**미확정 질문:** 빈 값일 때 사용할 기본값/옵션, newBadgeUntil 필수 입력 UX, 상·하위 category ID의 유효 관계, 숫자 범위와 이벤트 보상 제외 정책이 현재 화면/기획에 없으면 확인한다. 필수라는 사실만으로 임의 값/현재 시간을 채우지 않는다.

**완료/검증/인계:** `node --test tests/items-contract.test.mjs tests/items-query-mutation.test.mjs tests/item-form.test.mjs tests/item-id.test.mjs tests/item-category-contract.test.mjs tests/item-category-query-mutation.test.mjs`로 빈 필수값·소수·0/false의 잘못된 누락 방지·정상 등록·수정·수동 ID 동작을 검증한다. 필요한 입력 UI 변경은 같은 작업 공간에 Logic 결과를 인계한 후 별도 UI 역할로 수행한다.

<a id="t10"></a>

## T10 — 출석·룰렛 이벤트

| method·path | 요청 참조 DTO | HTTP 2xx envelope 참조 | 현재 상태 |
| --- | --- | --- | --- |
| [GET /events/attendance](./api-contracts.md#op-067) | [GetEventAttendanceListRequest](./api-schema-catalog.md#schema-geteventattendancelistrequest) | [ApiResponsePageResponseEventAttendanceSummaryResponse](./api-schema-catalog.md#schema-apiresponsepageresponseeventattendancesummaryresponse) | **화면 호출 연결 확인** |
| [POST /events/attendance](./api-contracts.md#op-068) | [CreateEventAttendanceRequest](./api-schema-catalog.md#schema-createeventattendancerequest) | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **화면 호출 연결 확인** |
| [GET /events/attendance/{eventId}](./api-contracts.md#op-069) | 없음/인라인 | [ApiResponseEventAttendanceResponse](./api-schema-catalog.md#schema-apiresponseeventattendanceresponse) | **화면 호출 연결 확인** |
| [PATCH /events/attendance/{eventId}](./api-contracts.md#op-070) | [PatchEventAttendanceRequest](./api-schema-catalog.md#schema-patcheventattendancerequest) | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **화면 호출 연결 확인** |
| [PATCH /events/attendance/{eventId}/configs](./api-contracts.md#op-071) | [PatchEventAttendanceConfigRequest](./api-schema-catalog.md#schema-patcheventattendanceconfigrequest) | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **화면 호출 연결 확인** |
| [POST /events/attendance/{eventId}/configs/upload](./api-contracts.md#op-072) | 없음/인라인 | [ApiResponseUploadEventAttendanceConfigImageResponse](./api-schema-catalog.md#schema-apiresponseuploadeventattendanceconfigimageresponse) | **화면 호출 연결 확인** |
| [GET /events/attendance/{eventId}/items](./api-contracts.md#op-073) | 없음/인라인 | [ApiResponseListEventAttendanceItemResponse](./api-schema-catalog.md#schema-apiresponselisteventattendanceitemresponse) | **API·hook 정의, 화면 사용처 없음** |
| [PUT /events/attendance/{eventId}/items](./api-contracts.md#op-074) | [UpdateEventAttendanceItemsRequest](./api-schema-catalog.md#schema-updateeventattendanceitemsrequest) | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **화면 호출 연결 확인** |
| [GET /events/roulette](./api-contracts.md#op-075) | [GetEventRouletteListRequest](./api-schema-catalog.md#schema-geteventroulettelistrequest) | [ApiResponsePageResponseEventRouletteSummaryResponse](./api-schema-catalog.md#schema-apiresponsepageresponseeventroulettesummaryresponse) | **화면 호출 연결 확인** |
| [POST /events/roulette](./api-contracts.md#op-076) | [CreateEventRouletteRequest](./api-schema-catalog.md#schema-createeventrouletterequest) | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **화면 호출 연결 확인** |
| [GET /events/roulette/{eventId}](./api-contracts.md#op-077) | 없음/인라인 | [ApiResponseEventRouletteResponse](./api-schema-catalog.md#schema-apiresponseeventrouletteresponse) | **화면 호출 연결 확인** |
| [PATCH /events/roulette/{eventId}](./api-contracts.md#op-078) | [PatchEventRouletteRequest](./api-schema-catalog.md#schema-patcheventrouletterequest) | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **화면 호출 연결 확인** |
| [PATCH /events/roulette/{eventId}/configs](./api-contracts.md#op-079) | [PatchEventRouletteConfigRequest](./api-schema-catalog.md#schema-patcheventrouletteconfigrequest) | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **화면 호출 연결 확인** |
| [POST /events/roulette/{eventId}/configs/upload](./api-contracts.md#op-080) | 없음/인라인 | [ApiResponseUploadEventRouletteConfigImageResponse](./api-schema-catalog.md#schema-apiresponseuploadeventrouletteconfigimageresponse) | **화면 호출 연결 확인** |
| [GET /events/roulette/{eventId}/items](./api-contracts.md#op-081) | 없음/인라인 | [ApiResponseListEventRouletteItemResponse](./api-schema-catalog.md#schema-apiresponselisteventrouletteitemresponse) | **API·hook 정의, 화면 사용처 없음** |
| [PUT /events/roulette/{eventId}/items](./api-contracts.md#op-082) | [UpdateEventRouletteItemsRequest](./api-schema-catalog.md#schema-updateeventrouletteitemsrequest) | [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid) | **화면 호출 연결 확인** |

**상태·재사용:** 16개 API 존재. 출석/룰렛의 items 단독 GET 2개는 화면 미사용이나 상세 GET 응답의 items를 화면이 사용하므로 미사용 자체는 결함이 아니다. [src/entities/event/api/event.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/event.dto.ts), [src/entities/event/api/attendance/attendance.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.dto.ts), [src/entities/event/api/roulette/roulette.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.dto.ts) 및 기존 query/mutation/controller를 재사용한다. Logic, 작업 공간 미정.

**F09 — 부분 수정·정수:** [PatchEventAttendanceRequest](./api-schema-catalog.md#schema-patcheventattendancerequest)/[PatchEventRouletteRequest](./api-schema-catalog.md#schema-patcheventrouletterequest)의 code/startAt/endAt/isActive는 required 목록이 없는데 현재 DTO는 모두 필수다. 모든 필드를 보내는 현재 화면이 즉시 오작동한다는 의미는 아니지만 명세의 부분 수정을 표현하지 못한다. 보상의 objectAmount와 roulette chance는 integer/minimum1인데 로컬 z.number()와 폼 입력이 소수를 허용한다. 출석 objectAmount는 required 목록에 없고 룰렛 objectAmount/chance는 필수여서 선택 여부도 구분한다.

**반영 제안:** 요청 schema·폼 DTO 매핑·검증을 함께 맞추고 partial payload에서 false/0을 누락하지 않는다. existing items·config·image 업로드와 무효화 구조는 재사용한다. chance의 합계·단위·범위 또는 보상 타입별 objectId 의미를 정수라는 이유만으로 새로 정하지 않는다. 기존 item picker가 반환하는 ID 계약을 확인한다.

**미확정 질문:** 기존 화면에 부분 수정이 필요한지, chance 단위/합계/상한, 출석 objectAmount 생략 시 기본값, 이벤트 코드·일정·활성화 정책 중 명세/기존 코드에서 확인 안 되는 것. 서버 schema integer 외 제약을 임의 도입하지 않는다.

**완료/검증/인계:** `node --test tests/events-contract.test.mjs tests/events-query-mutation.test.mjs tests/events-controller.test.mjs`에서 부분 payload, 정수 경계, 기존 상세 items·취소·캐시 갱신을 확인한다. 최신 ID·보상 GET 미사용만으로 추가 호출을 만들지 않는다. UI 입력 구성 변경은 별도 확인한다.

<a id="t11"></a>

## T11 — 소포

| method·path | 요청 참조 DTO | HTTP 2xx envelope 참조 | 현재 상태 |
| --- | --- | --- | --- |
| [GET /admin/parcels](./api-contracts.md#op-037) | 없음/인라인 | [ApiResponsePageResponseParcelHistoryResponse](./api-schema-catalog.md#schema-apiresponsepageresponseparcelhistoryresponse) | **API·hook 정의, 화면 사용처 없음** · F10 |
| [POST /admin/parcels](./api-contracts.md#op-038) | [SendParcelRequest](./api-schema-catalog.md#schema-sendparcelrequest) | [ApiResponse](./api-schema-catalog.md#schema-apiresponse) | **API·hook 정의, 화면 사용처 없음** |
| [GET /admin/parcels/export](./api-contracts.md#op-039) | 없음/인라인 | 예시/인라인 | **API·hook 정의, 화면 사용처 없음** |

**상태·재사용:** 목록·발송·export 3개 API/hook 존재, 화면 소비는 찾지 못했다. [src/entities/parcels/api/parcel.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/parcels/api/parcel.dto.ts), [src/entities/parcels/api/parcel.api.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/parcels/api/parcel.api.ts), [src/entities/parcels/api/parcel-export.response.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/parcels/api/parcel-export.response.ts), `model/parcel-query-options.ts / parcel-mutation-options.ts`와 다운로드 util을 사용한다. Logic, 작업 공간 미정.

**F09/F10 — 차이:** [SendParcelRequest](./api-schema-catalog.md#schema-sendparcelrequest)의 userId/itemId/amount는 integer인데 현지 number 검증은 정수를 강제하지 않는다. [ParcelHistoryResponse](./api-schema-catalog.md#schema-parcelhistoryresponse)에는 amount가 있지만 로컬 DTO에는 없고 Swagger 성공 예시에서도 amount가 누락된다. 실제 반환/필수/표시 여부를 확인해야 한다.

**반영 제안:** 발송 DTO에 확정된 정수·최소 수량 제약을 적용하고 ID 출처를 확인한다. 목록 amount는 확인 후 원시 DTO와 화면 row에 반영한다. export는 recipient 필터의 전체 결과이며 pagination을 보내지 않는 설명을 따른다. 기존 arraybuffer와 transformResponse·JSON 오류·파일명 처리 재사용이 중요하다.

**미확정 질문:** 수신자 userId와 목록 recipient 닉네임의 연결/조회 수단, itemId 선택 방식, 발송 사유·다중 발송 여부, 실제 amount 응답, 화면 연결 위치. 승인 없이 실제 소포 발송으로 검증하지 않는다.

**완료/검증/인계:** `node --test tests/parcels-query-mutation.test.mjs`와 기존 contract harness에 정상 정수·오류·목록 필터·바이너리 다운로드/JSON 실패를 검증한다. 다운로드를 새 JSON API로 구현하지 않는다. UI에 확정 ID·payload·다운로드 pending/error 계약을 전달한다.

<a id="t12"></a>

## T12 — 외부 대시보드

| method·path | 요청 참조 DTO | HTTP 2xx envelope 참조 | 현재 상태 |
| --- | --- | --- | --- |
| [GET /external/dashboard/daily](./api-contracts.md#op-083) | 없음/인라인 | [ApiResponseDailyDashboardResponse](./api-schema-catalog.md#schema-apiresponsedailydashboardresponse) | **일치 호출 없음** |
| [GET /external/dashboard/monthly](./api-contracts.md#op-084) | 없음/인라인 | [ApiResponseMonthlyDashboardResponse](./api-schema-catalog.md#schema-apiresponsemonthlydashboardresponse) | **일치 호출 없음** |
| [GET /external/dashboard/summary](./api-contracts.md#op-085) | 없음/인라인 | [ApiResponseExternalDashboardResponse](./api-schema-catalog.md#schema-apiresponseexternaldashboardresponse) | **일치 호출 없음** |
| [GET /external/dashboard/weekly](./api-contracts.md#op-086) | 없음/인라인 | [ApiResponseWeeklyDashboardResponse](./api-schema-catalog.md#schema-apiresponseweeklydashboardresponse) | **일치 호출 없음** |

**상태:** external dashboard 4개 GET 미구현. 기존 [src/entities/dashboard/api/dashboard.api.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dashboard/api/dashboard.api.ts)·[src/entities/dashboard/api/dashboard.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dashboard/api/dashboard.dto.ts)와 시민참여 dashboard를 같은 계약이라고 볼 수 없다. Logic 조사/연결은 후속 제안이며 작업 공간·제품 적용 대상은 미정이다.

**서버 명세가 직접 적은 조건:** 외부 공유용이고 인증 없이 호출한다고 설명한다. summary의 changeRate/rate는 퍼센트 숫자(5.2=5.2%). daily/weekly/monthly의 date(yyyy-MM-dd)는 필수다. weekly는 ISO 주/주연도이므로 달력 연도와 다를 수 있다. 명세 설명상 현재 집계는 **서버의 고정 Mock 값**이며 기간 표기만 요청값으로 계산한다. 이 항목을 프런트 MSW나 실시간 운영 통계로 설명하면 안 된다.

**추가 불일치·확인:** OpenAPI 전역 bearerAuth는 외부 API에도 상속되지만 operation description은 공개 호출이다. 실제 공통 client의 authRequired 옵션과 서버 설정을 대조한다. weekly 예시의 요청 date 2026-08-31과 예시 data 2026-W35/08-24~08-30은 서로 다른 주이고 monthly 요청 예시08-31에 응답 예시07월이어서 예시를 기간 계산 기대값으로 사용하지 않는다. 실제 기간 계산 검증은 설명에 맞는 계약 확인 후 한다.

**반영 제안:** 기존 dashboard 모델과 필드 의미를 대조하고 외부 API를 이 관리자 화면에 사용할 필요부터 확인한다. 사용 결정 후 공통 response DTO, 날짜 validator, query key/signal 패턴을 재사용한다. 기간별 [DailyDashboardResponse](./api-schema-catalog.md#schema-dailydashboardresponse)/[WeeklyDashboardResponse](./api-schema-catalog.md#schema-weeklydashboardresponse)/[MonthlyDashboardResponse](./api-schema-catalog.md#schema-monthlydashboardresponse)와 summary [ExternalDashboardResponse](./api-schema-catalog.md#schema-externaldashboardresponse)를 구분한다. 집계 값·OS 비율·매출 건수와 수량을 재계산/합산해 다른 의미로 바꾸지 않는다.

**필수 질문·완료:** 외부 공유 API의 admin-ui 사용 여부, 표시 화면, 기준 날짜 선택·timezone, 서버 Mock 해제 시점/실데이터 보장, 공개 호출 계약을 확인해야 한다. 승인 후 필수 date·연말 ISO 주·월말/윤년·퍼센트 단위·오류 배열·summary와 기간 응답 분리를 기존 node:test 방식으로 검증한다. 새 화면/차트는 UI 역할로 인계한다.

<a id="t13"></a>

## T13 — 감사 내역·상태 확인

| method·path | 요청 참조 DTO | HTTP 2xx envelope 참조 | 현재 상태 |
| --- | --- | --- | --- |
| [GET /admin/audit](./api-contracts.md#op-003) | 없음/인라인 | [ApiResponsePageResponseGetAdminAllAuditLogResponse](./api-schema-catalog.md#schema-apiresponsepageresponsegetadminallauditlogresponse) | **일치 호출 없음** |
| [GET /health](./api-contracts.md#op-087) | 없음/인라인 | [ApiResponseMapStringString](./api-schema-catalog.md#schema-apiresponsemapstringstring) | **일치 호출 없음** |

**상태:** GET /admin/audit와 /health 미구현. Logic 후속 제안, 작업 공간 미정. 모든 Swagger endpoint를 UI 버튼으로 만들 필요가 있는 것은 아니다.

**감사 내역:** [GetAdminAllAuditLogResponse](./api-schema-catalog.md#schema-getadminallauditlogresponse)의 id/서비스명/처리내용/작업자/작업일 필드 원문을 확인해 연결한다. 기본 정렬은 createdAt,id desc, 설명에는 다른 정렬이면400이라고 되어 있으나 responses에는 400 body가 없다. 따라서 공통 오류를 사용하되 임의 업무 에러 코드를 문서 계약으로 추가하지 않는다. page 설명 one-based/default1과 schema minimum0 표현 차이를 확인한다. 기존 cp-activity-log·DAO 로그의 endpoint/DTO는 별개라 신규 감사로그로 그대로 세지 않았다.

**health:** 성공은 [ApiResponseMapStringString](./api-schema-catalog.md#schema-apiresponsemapstringstring)의 map payload다. 인증/운영 상태 표시의 제품 요구와 호출 시점을 확인하기 전 폴링·알림·가짜 status enum을 만들지 않는다.

**반영/미확정 질문:** 감사 내역 대상 화면·조회 권한·정렬/페이지 UI, health가 필요한 위치·실제 map key·공개 여부를 확인한다. 공통 page/API/query/error 자산과 기존 로그 페이지의 재사용 적합성을 비교한 뒤 신규 위치를 결정한다.

**완료/검증/인계:** 감사 DTO·pagination·허용 정렬과 비허용 실패 경로, health 실제 map 계약을 검증한다. 기존 전용 테스트·hook은 조사에서 찾지 못했으므로 필요한 최소 node:test를 승인된 변경 범위에서 추가한다. UI 사용 자체가 불필요하면 서버 API 미사용을 남기는 결정도 가능하며 사용자와 확정한다.

## 공통 완료 기준과 협업 경계

- T01 외에는 목적지 branch/worktree·서비스 공백·재사용 방식·소스 수정 범위를 사용자와 확정해야 한다. 이 문서의 “미정”을 기본값으로 자동 채우지 않는다.
- 한 기능의 Logic→UI 순차 연결은 같은 공간을 쓸 수 있다. 실제 병렬 구현은 각각 승인된 linked worktree에서 수행한다. 공간·부모 관계가 정해지기 전 가상의 branch/worktree를 인계 완료로 기록하지 않는다.
- `src/shared/api/common/`, auth/store/router/navigation, `src/mocks/handlers.ts`, `src/app/mock-api-policy.ts`, 공통 tests가 작업 간 겹칠 수 있다. 실제 diff를 비교하고 수정 순서를 조율한다. 파일 독점 권한을 의미하지 않는다.
- 주고받을 기본 Logic 계약은 query 입력/ID 출처/도메인 row 또는 detail/mutation variables·void 여부/pending/error/retry/cache 갱신이다. UI가 필요한 세부 props/callback은 기존 소비자에서 확인해 별도 합의한다.
- 테스트는 위에 제시한 **실행 예정** 명령이며 이 조사에서 실행한 결과가 아니다. package.json에 test script가 없어 `npm run test` 대신 `node --test tests/<관련 파일>.test.mjs`를 사용한다.
- 소스 구현 후 바인딩된 정책의 실제 formatting.py apply를 작업 workdir에서 실행하고, 관련 node:test → `npm run lint` → `npm run build`를 수행한다. 정상 response·요청·null/오류·무효화가 검증되어야 한다. source 변경 없는 이번 문서 작업에는 이 실행이 필요하지 않다.
- endpoint의 명시 오류는 [오류 문서](./api-errors-and-integration.md)로 연결한다. 문자열 code와 HTTP status를 구분하고 필드별 오류가 자동 UI 표시된다고 가정하지 않는다.
- 실서버 업무 API의 수정/삭제/발송 호출로 검증하지 않았다. 문서와 로컬 테스트만으로 실제 운영 권한·CORS·서버 응답 성공을 보장하지 않는다.
- commit·merge·정리에는 별도 Git 승인과 직접 부모 통합 검토가 필요하다. 자식 branch의 검증 통과를 sy-main 통합 완료로 기록하지 않는다.

## Swagger에 없는 현재 호출의 처리

`GET /admin/users` 목록, `/v1/auth/token/reissue` 등 인증 부가 API, 다수 `/v1/cp/*`, DAO·FAQ·기존 통계·Agora 관련 코드가 이 Swagger에 없다고 해서 서버에 없거나 폐기되었다고 단정하지 않는다. 이번 검토는 “Swagger 전체에 대한 현재 프로젝트 대조”이며 역방향의 모든 legacy endpoint 운영 계약을 확정한 조사가 아니다. 후속 작업은 원 API의 유지/교체/삭제 범위와 데이터 출처를 확인해야 한다.
