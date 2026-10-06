# 오류 계약과 API 연결 방법

## 확인 범위

106개 operation 중 **26개**에 비-2xx 응답이 명시되어 있고, HTTP 상태별 응답 항목은 **52개**다(400: 16, 401: 20, 404: 14, 409: 2). 나머지 **80개**는 오류 계약 미기재다. 이것은 오류 미발생 또는 인증 불필요를 뜻하지 않는다. 403·422·500, timeout, CORS 등을 이 명세에 정의된 업무 오류처럼 덧붙이지 않는다.

오류 원문·예시는 [API별 계약](./api-contracts.md)의 각 operation에 전부 수록했다. 상태 코드와 업무 코드의 대응은 API별로 확인한다. 예를 들어 로그인 실패가 무조건 401이라는 관행을 적용하면 이 명세의 400/404와 어긋난다.

## 서버 오류 형태

일반 업무 오류 예시:

```json
{"code":"CITIZEN_PROPOSAL_NOT_FOUND","message":"제안을 찾을 수 없습니다.","data":null}
```

입력값 오류 예시:

```json
{"code":"INVALID_REQUEST","message":"요청이 올바르지 않습니다.","data":[{"field":"reviewResult","reason":"검토 결과는 필수입니다."}]}
```

- `code`: 문자열 업무 코드. HTTP status와 다른 값이다.
- `message`: 사용자 안내 문구. 예시에 마침표 유무도 다르며 완전히 같은 문자열로 모든 오류를 판별하지 않는다.
- `data`: 예시에서 `null` 또는 `{field:string, reason:string}[]`. 모든 오류에 같은 배열이 오는 계약은 아니다.
- `path`, `timestamp`, `statusCode`는 현재 공통 클라이언트가 받아들일 수 있지만 이 Swagger의 위 오류 예시에는 없다. 서버 필수 필드로 새로 선언하지 않는다.
- 오류 예시만 있고 별도 공통 error schema는 정의되지 않았다. 원본의 `content.example/examples`를 근거로 삼는다.

## HTTP 상태·업무 코드 목록

| method·path | HTTP | 문서에 있는 코드 | data 형태 |
| --- | --- | --- | --- |
| [POST /auth/login](./api-contracts.md#op-058) | 400 | `ADMIN_INVALID_PASSWORD` | null |
| [POST /auth/login](./api-contracts.md#op-058) | 404 | `ADMIN_NOT_FOUND` | null |
| [POST /admin/users/{userId}/points](./api-contracts.md#op-044) | 400 | `INVALID_REQUEST` | null |
| [POST /admin/users/{userId}/points](./api-contracts.md#op-044) | 404 | `USER_NOT_FOUND`, `USER_WITHDRAWN` | null |
| [POST /admin/users/{userId}/points](./api-contracts.md#op-044) | 409 | `USER_POINT_INSUFFICIENT` | null |
| [GET /admin/parcels](./api-contracts.md#op-037) | 400 | `INVALID_SORT_PROPERTY` | null |
| [GET /admin/parcels](./api-contracts.md#op-037) | 401 | `EXPIRED_TOKEN`, `INVALID_TOKEN` | null |
| [POST /admin/parcels](./api-contracts.md#op-038) | 400 | `INVALID_REQUEST` | null |
| [POST /admin/parcels](./api-contracts.md#op-038) | 401 | `EXPIRED_TOKEN`, `INVALID_TOKEN` | null |
| [POST /admin/parcels](./api-contracts.md#op-038) | 404 | `USER_NOT_FOUND`, `ITEM_NOT_FOUND` | null |
| [GET /admin/news](./api-contracts.md#op-029) | 400 | `NEWS_INVALID_BY_KEYWORD`, `INVALID_SORT_PROPERTY` | null |
| [GET /admin/news](./api-contracts.md#op-029) | 401 | `EXPIRED_TOKEN`, `INVALID_TOKEN` | null |
| [POST /admin/news](./api-contracts.md#op-030) | 400 | `INVALID_REQUEST` | 필드별 field/reason 배열 |
| [POST /admin/news](./api-contracts.md#op-030) | 401 | `EXPIRED_TOKEN`, `INVALID_TOKEN` | null |
| [GET /citizen/proposals/{proposalId}](./api-contracts.md#op-060) | 401 | `EXPIRED_TOKEN`, `INVALID_TOKEN` | null |
| [GET /citizen/proposals/{proposalId}](./api-contracts.md#op-060) | 404 | `CITIZEN_PROPOSAL_NOT_FOUND` | null |
| [PATCH /citizen/proposals/{proposalId}](./api-contracts.md#op-061) | 400 | `INVALID_REQUEST` | null |
| [PATCH /citizen/proposals/{proposalId}](./api-contracts.md#op-061) | 401 | `EXPIRED_TOKEN`, `INVALID_TOKEN` | null |
| [PATCH /citizen/proposals/{proposalId}](./api-contracts.md#op-061) | 404 | `CITIZEN_PROPOSAL_NOT_FOUND` | null |
| [PATCH /citizen/proposals/{proposalId}/review-result](./api-contracts.md#op-062) | 400 | `INVALID_REQUEST` | 필드별 field/reason 배열 |
| [PATCH /citizen/proposals/{proposalId}/review-result](./api-contracts.md#op-062) | 401 | `EXPIRED_TOKEN`, `INVALID_TOKEN` | null |
| [PATCH /citizen/proposals/{proposalId}/review-result](./api-contracts.md#op-062) | 404 | `CITIZEN_PROPOSAL_NOT_FOUND` | null |
| [PATCH /admin/users/{userId}/status](./api-contracts.md#op-045) | 400 | `INVALID_REQUEST` | null |
| [PATCH /admin/users/{userId}/status](./api-contracts.md#op-045) | 404 | `USER_NOT_FOUND`, `USER_WITHDRAWN` | null |
| [PATCH /admin/users/{userId}/status](./api-contracts.md#op-045) | 409 | `USER_STATUS_ALREADY_SET` | null |
| [GET /admin/news/{newsId}](./api-contracts.md#op-032) | 401 | `EXPIRED_TOKEN`, `INVALID_TOKEN` | null |
| [GET /admin/news/{newsId}](./api-contracts.md#op-032) | 404 | `NEWS_NOT_FOUND` | null |
| [DELETE /admin/news/{newsId}](./api-contracts.md#op-031) | 401 | `EXPIRED_TOKEN`, `INVALID_TOKEN` | null |
| [DELETE /admin/news/{newsId}](./api-contracts.md#op-031) | 404 | `NEWS_NOT_FOUND` | null |
| [PATCH /admin/news/{newsId}](./api-contracts.md#op-033) | 401 | `EXPIRED_TOKEN`, `INVALID_TOKEN` | null |
| [PATCH /admin/news/{newsId}](./api-contracts.md#op-033) | 404 | `NEWS_NOT_FOUND` | null |
| [PATCH /admin/news/batch](./api-contracts.md#op-036) | 400 | `INVALID_REQUEST` | 필드별 field/reason 배열 |
| [PATCH /admin/news/batch](./api-contracts.md#op-036) | 401 | `EXPIRED_TOKEN`, `INVALID_TOKEN` | null |
| [GET /external/dashboard/weekly](./api-contracts.md#op-086) | 400 | `INVALID_REQUEST` | 필드별 field/reason 배열 |
| [GET /external/dashboard/monthly](./api-contracts.md#op-084) | 400 | `INVALID_REQUEST` | 필드별 field/reason 배열 |
| [GET /external/dashboard/daily](./api-contracts.md#op-083) | 400 | `INVALID_REQUEST` | 필드별 field/reason 배열 |
| [GET /citizen/votes](./api-contracts.md#op-064) | 400 | `INVALID_SORT_PROPERTY`, `INVALID_REQUEST` | null |
| [GET /citizen/votes](./api-contracts.md#op-064) | 401 | `EXPIRED_TOKEN`, `INVALID_TOKEN` | null |
| [GET /citizen/votes/{voteId}](./api-contracts.md#op-065) | 401 | `EXPIRED_TOKEN`, `INVALID_TOKEN` | null |
| [GET /citizen/votes/{voteId}](./api-contracts.md#op-065) | 404 | `CITIZEN_VOTE_NOT_FOUND` | null |
| [GET /citizen/votes/summary](./api-contracts.md#op-066) | 401 | `EXPIRED_TOKEN`, `INVALID_TOKEN` | null |
| [GET /citizen/proposals](./api-contracts.md#op-059) | 400 | `INVALID_SORT_PROPERTY`, `INVALID_REQUEST` | null |
| [GET /citizen/proposals](./api-contracts.md#op-059) | 401 | `EXPIRED_TOKEN`, `INVALID_TOKEN` | null |
| [GET /citizen/proposals/summary](./api-contracts.md#op-063) | 401 | `EXPIRED_TOKEN`, `INVALID_TOKEN` | null |
| [GET /admin/users/{userId}](./api-contracts.md#op-042) | 401 | `EXPIRED_TOKEN`, `INVALID_TOKEN` | null |
| [GET /admin/users/{userId}](./api-contracts.md#op-042) | 404 | `USER_NOT_FOUND` | null |
| [GET /admin/users/withdrawals](./api-contracts.md#op-046) | 401 | `EXPIRED_TOKEN`, `INVALID_TOKEN` | null |
| [GET /admin/news/{newsId}/comments](./api-contracts.md#op-034) | 400 | `INVALID_REQUEST` | 필드별 field/reason 배열 |
| [GET /admin/news/{newsId}/comments](./api-contracts.md#op-034) | 401 | `EXPIRED_TOKEN`, `INVALID_TOKEN` | null |
| [GET /admin/news/{newsId}/comments](./api-contracts.md#op-034) | 404 | `NEWS_NOT_FOUND` | null |
| [DELETE /admin/news/{newsId}/comments/{commentId}](./api-contracts.md#op-035) | 401 | `EXPIRED_TOKEN`, `INVALID_TOKEN` | null |
| [DELETE /admin/news/{newsId}/comments/{commentId}](./api-contracts.md#op-035) | 404 | `NEWS_NOT_FOUND` | null |

## 개별 오류 적용 시 주의점

- 로그인: 비밀번호 불일치 `400 / ADMIN_INVALID_PASSWORD`, 관리자 없음 `404 / ADMIN_NOT_FOUND`. 토큰이 없다는 이유로 로그인 호출 자체를 막지 않는다. 현재 `authRequired:false`를 재사용한다. 전역 bearerAuth가 로그인 operation에도 상속되는 문서 표현과 실제 공개 로그인 호출은 구분해 기록한다.
- 시민제안 상태: `400 / INVALID_REQUEST`, 토큰 `401 / EXPIRED_TOKEN | INVALID_TOKEN`, 대상 없음 `404 / CITIZEN_PROPOSAL_NOT_FOUND`. 검토 결과 400의 `data`는 필드별 사유 배열이다.
- 시민투표 상세: `404 / CITIZEN_VOTE_NOT_FOUND`. 목록의 잘못된 정렬은 `400 / INVALID_SORT_PROPERTY`. 제안/투표 summary는 401만 문서화되었다.
- 사용자: 이미 같은 상태인 경우 `409 / USER_STATUS_ALREADY_SET`, 잔액보다 큰 차감 `409 / USER_POINT_INSUFFICIENT`. 존재하지 않음과 탈퇴 사용자는 둘 다 404이지만 `USER_NOT_FOUND`와 `USER_WITHDRAWN`을 구분한다.
- 공지사항: 목록 by/keyword 짝 불일치 `NEWS_INVALID_BY_KEYWORD`, 등록 필수값·batch의 빈 newsIds·댓글 목록 page/size 누락은 필드 배열을 포함한 `INVALID_REQUEST`.
- **댓글 삭제 404의 주의점:** 없는 공지와 없는 댓글 예시가 모두 `NEWS_NOT_FOUND`이며 message만 다르다. 임의 `NEWS_COMMENT_NOT_FOUND` 코드를 발명하지 않는다. 코드 차별이 필요한 UX라면 서버 계약을 확인한다.
- 외부 대시보드 daily/weekly/monthly는 필수 date 누락·형식 오류가 400이며 `data:[{field:'date',reason:...}]` 예시가 있다.
- 소포 목록 정렬 오류 400, 발송 400/401/404는 문서화되지만 export에는 성공만 있다. export 실패 계약을 일반 JSON 성공 응답으로 처리하지 않는다. 기존 바이너리/JSON 오류 디코더를 참조한다.

## 기존 프로젝트의 전송·오류 흐름

1. [src/shared/api/axios-instance.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/shared/api/axios-instance.ts): `VITE_API_BASE_URL` 사용, 기본 JSON 헤더, 저장한 accessToken의 Bearer 주입. 응답 성공 인터셉터는 `res.data`를 반환한다.
2. HTTP 실패: `toServerResponse` → `toApiError` → `CustomException`. HTTP status는 fallback의 `statusCode`에 보존한다. 서버 문자열 `code`는 `ApiError.apiCode`, 숫자 코드는 `ApiError.code`로 분리된다. `ApiError.code` 숫자만 비교하면 문자열 업무 코드를 놓친다.
3. HTTP 성공의 업무 결과: [src/shared/api/api-client.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/shared/api/api-client.ts) → [src/shared/api/common/api-result/api-result.mapper.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/shared/api/common/api-result/api-result.mapper.ts). `success:true` 또는 `code:"SUCCESS"`인지를 보고 `ApiResult<TData>`로 바꾼다. HTTP 200만으로 업무 성공을 가정하지 않는다.
4. [src/shared/api/common/api-result/api-result.unwrap.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/shared/api/common/api-result/api-result.unwrap.ts): 실패한 `ApiResult`도 `CustomException`으로 throw한다. 이후 도메인 parser는 성공한 내부 payload만 검사한다.
5. [src/shared/api/error/api-failure.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/shared/api/error/api-failure.ts): 서버/클라이언트 계약/네트워크·timeout/취소를 분리한다. `apiCode`가 있으면 서버 코드로 우선 사용한다.
6. [src/shared/api/error/api-failure-reporter.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/shared/api/error/api-failure-reporter.ts): 같은 오류 객체의 중복 보고를 막고, 취소는 알림하지 않는다. 기본 401은 재인증 이벤트, 기타 서버 오류는 공통 모달 queue로 보낸다. 계약·전송 실패는 diagnostics에 기록한다. 로그인처럼 401 처리 목적이 다른 호출은 현재 reporter 옵션과 기존 auth 흐름을 재사용한다.

### 필드 오류 표시의 현재 한계

[src/shared/api/common/api-result/api-error.mapper.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/shared/api/common/api-result/api-error.mapper.ts)와 [src/shared/lib/exceptions/custom.exception.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/shared/lib/exceptions/custom.exception.ts)는 오류 `data`를 보존하지만, `ApiFailure`의 server 변형과 공통 reporter에는 필드 배열을 폼 오류로 바꾸는 계약이 없다. **서버의 필드별 reason이 자동으로 각 입력란에 표시되는 구현은 아니다.** 시민제안 controller도 현재 `error.message`를 보여준다.

이 부분을 전역 수정하거나 새 필드 오류 어댑터로 확장하는 작업은 승인되지 않았다. 후속 화면에서 필드별 오류가 필요하면 기존 폼 validator·표시 방식·공통 오류 모달과의 중복 처리부터 확인하고 범위를 승인받는다. 원시 error.data를 무검증 단언하지 않는다.

### Void 성공과 null

`toApiResult`는 성공 data가 `null/undefined`이면 `undefined`로 정규화한다. 따라서 null 성공을 다시 `z.string()`으로 검사하면 실패한다. [F05](./api-work-items.md#t05)의 문의·타입 mutation 8개와 사용자 권한 mutation 1개가 이 경로에 해당한다.

명시적 null 예시가 있는 시민제안 PATCH에는 내부 `void` 성공을 수용하고 재조회/무효화로 최신 상태를 가져오는 연결이 필요하다. `ApiResponseVoid.data:{}`만 있는 다른 API는 실제 payload를 확인하기 전 문자열/null 중 어느 쪽이 실제 응답이라고 단정하지 않는다. 기존 동작과 명세를 대조한 후 parser·callback·cache를 함께 맞춘다.

## 모든 후속 작업이 재사용할 연결 자산

| 책임 | 실제 자산 | 적용 방법 |
| --- | --- | --- |
| JSON envelope | [src/shared/api/common/response.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/shared/api/common/response.dto.ts) | `ApiResponseDto<TData>`를 재사용하고 domain마다 중복 정의하지 않는다. |
| 페이지 payload | 같은 파일의 `PageResponseDto`, `createPageResponseSchema` | items/total/page/size를 재사용한다. 공통 응답은 page>0인데 OpenAPI Pageable 요청은 최소0인 표현도 있으므로 개별 API의 요청/응답 기준을 섞지 않는다. |
| 전송 및 취소 | [src/shared/api/api-client.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/shared/api/api-client.ts), [src/shared/api/with-abort-signal.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/shared/api/with-abort-signal.ts) | query의 AbortSignal을 전달하고 실패를 빈 배열/성공으로 덮지 않는다. |
| 반복 query | 기존 API의 `paramsSerializer: { indexes: null }` | status/sort 등 계약이 배열이면 기존 반복 parameter 방식을 재사용한다. |
| 도메인 검증 | `entities/*/api/*.dto.ts, *.parser.ts` | 요청 schema → client → 성공 payload parser 경계를 유지한다. request enum과 response enum은 실제 계약이 같을 때만 공유한다. |
| 캐시·상태 조율 | `entities/*/model/*query-options.ts, *mutation-options.ts`, `hook/*` | 이미 있는 query key·캐시 갱신·취소 흐름을 확장한다. API만 추가하고 화면이 기존 endpoint를 호출하게 남겨두지 않는다. |
| 입력·표시 | 기존 페이지 controller, `src/shared/lib/validation/`, `src/shared/ui/dialog/` | UI 폼 값과 서버 DTO 매핑을 분리한다. 레이아웃 변경은 별도 UI 역할이다. |
| multipart 단일 파일 | 아이템/이벤트 업로드 및 video API | FormData를 재사용한다. 영상의 data+file 혼합 계약은 과거 확정 주석과 충돌하므로 [T04](./api-work-items.md#t04) 결정을 먼저 받는다. |
| 파일 다운로드 | [src/entities/parcels/api/parcel-export.response.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/parcels/api/parcel-export.response.ts), [src/entities/parcels/lib/download-parcel-history.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/parcels/lib/download-parcel-history.ts) | ArrayBuffer·JSON 오류·Content-Disposition 파일명 처리를 보존한다. 공통 JSON envelope parser로 바이너리를 파싱하지 않는다. |

## 명세 해석의 미확정 부분

- `ApiResponseVoid`, `ApiResponseObject`, `ApiResponse`의 data는 빈 schema다. 이름으로 payload를 채우지 않는다. `NewsApiResponseVoid.data`의 writeOnly 표현도 원본 그대로 보존했다.
- 대부분 응답 객체에는 required 목록이 없다. 모든 필드를 필수/non-null로 만들거나 반대로 모든 필드를 nullish로 바꾸는 근거가 되지 않는다.
- `UpdateCitizenProposalReviewResultRequest.reviewResult`의 schema는 minLength 0이지만 operation 설명은 빈 값·공백뿐인 값 거절과 최대 5,000자를 명시한다. DTO 필드 표만 보지 말고 설명까지 적용한다. 기존 trim 제출과 사용자 결정은 [T01](./api-work-items.md#t01)을 따른다.
- `int64` 표기만으로 브라우저에서 모든 ID가 안전한 number라고 보장되지 않는다. 사용자 ID는 기존 문자열/BigInt 검증을 보존하고, 다른 ID 의미·출처·변환은 각 기능의 기존 계약에서 확인한다. `publicId`를 `userId/adminId`로 대체하지 않는다.
- pagination의 0/1 기준·기본 size·상한은 operation 설명과 기존 소비자별로 확인한다. 모든 API를 시민제안 기본값으로 통일하지 않는다.
- 문서에 없는 호출은 서버 부재 증거가 아니다. 기존 `/v1/*`를 일괄 삭제/치환하지 않는다.
