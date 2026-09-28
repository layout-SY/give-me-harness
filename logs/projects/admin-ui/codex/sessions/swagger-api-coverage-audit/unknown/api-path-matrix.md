# 전체 API path·요청·응답 대조표

2026-09-28, `sy-main@4b0b7db45aa9d15bf918a1a084370594e138a124` 기준. [OpenAPI 원본](https://admin-api.oasis.shovvel.com:8443/v3/api-docs)에서 75 path, 106 operation을 모두 읽었다. [판정 근거와 제한](../final-summary.md)을 함께 참조한다.

“화면 연결”은 호출 경로를 소스에서 확인했다는 뜻이며 계약 일치·실서버 성공 판정이 아니다. “호출 없음”은 현재 프로젝트 조사 범위에서 해당 method와 path의 요청을 찾지 못했다는 뜻이다. 요청 표기의 `*`는 schema required를 뜻한다. 경로 parameter는 URL의 `{...}`로 표시하며 query 객체는 OpenAPI 표현을 그대로 요약했다. 모든 일반 JSON 응답은 공통 `{code,message,data}` envelope다. 아래 응답에는 성공 payload를 적으며, 상세하지 않은 schema와 예시만 있는 응답은 명시한다.


## 1. GET /accounts

- 기능: getAccounts
- 상태: **일치 호출 없음**
- 요청: `query query*: GetAccountListRequest{page*:integer(int32), size*:integer(int32), keyword:string}`
- 성공 응답 200 payload: `PageResponseAccountResponse{items:[AccountResponse], total:integer(int64), page:integer(int32), size:integer(int32)}`
- 구현 근거: —

## 2. PUT /accounts/{adminId}/roles

- 기능: updateRoles
- 상태: **일치 호출 없음**
- 요청: `application/json: UpdateAccountRolesRequest{roleIds*:[integer(int64)]}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: —

## 3. GET /admin/audit

- 기능: 관리자 전체 활동 내역 조회
- 상태: **일치 호출 없음**
- 요청: `query page: integer; query size: integer; query sort: [string]`
- 성공 응답 200 payload: `PageResponseGetAdminAllAuditLogResponse{items:[GetAdminAllAuditLogResponse], total:integer(int64), page:integer(int32), size:integer(int32)}`
- 구현 근거: —

## 4. GET /admin/inquiries

- 기능: 문의 목록 조회
- 상태: **API·hook 정의, 화면 사용처 없음**
- 요청: `query status: OPEN / IN_PROGRESS / COMPLETED; query typeId: integer(int64); query by: TITLE / TITLE_CONTENT; query keyword: string; query page: integer; query size: integer; query sort: [string]`
- 성공 응답 200 payload: `PageResponseInquirySummaryResponse{items:[InquirySummaryResponse], total:integer(int64), page:integer(int32), size:integer(int32)}`
- 구현 근거: [src/entities/inquiries/api/inquiry.api.ts:35](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.api.ts:35) (`getList`)

## 5. DELETE /admin/inquiries/{inquiryId}

- 기능: 문의 삭제
- 상태: **API·hook 정의, 화면 사용처 없음** · F05
- 요청: `body/query 없음`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/inquiries/api/inquiry.api.ts:41](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.api.ts:41) (`deleteInquiry`)

## 6. GET /admin/inquiries/{inquiryId}

- 기능: 문의 상세 조회
- 상태: **API·hook 정의, 화면 사용처 없음**
- 요청: `body/query 없음`
- 성공 응답 200 payload: `InquiryDetailResponse{id:integer(int64), title:string, content:string, status:OPEN / IN_PROGRESS / COMPLETED, typeName:string, authorName:string, answerContent:InquiryCommentResponse{id:integer(int64), comment:string, createdAt:string(date-time)}, createdAt:string(date-time)}`
- 구현 근거: [src/entities/inquiries/api/inquiry.api.ts:38](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.api.ts:38) (`getDetail`)

## 7. DELETE /admin/inquiries/{inquiryId}/answer

- 기능: 문의 답변 삭제
- 상태: **API·hook 정의, 화면 사용처 없음** · F05
- 요청: `body/query 없음`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/inquiries/api/inquiry.api.ts:65](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.api.ts:65) (`deleteInquiryAnswer`)

## 8. POST /admin/inquiries/{inquiryId}/answer

- 기능: 문의 답변 등록
- 상태: **API·hook 정의, 화면 사용처 없음** · F05
- 요청: `application/json: InquiryAnswerRequest{content*:string}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/inquiries/api/inquiry.api.ts:51](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.api.ts:51) (`postInquiryAnswer`)

## 9. PUT /admin/inquiries/{inquiryId}/answer

- 기능: 문의 답변 수정
- 상태: **API·hook 정의, 화면 사용처 없음** · F05
- 요청: `application/json: InquiryAnswerRequest{content*:string}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/inquiries/api/inquiry.api.ts:58](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.api.ts:58) (`putInquiryAnswer`)

## 10. PATCH /admin/inquiries/{inquiryId}/status

- 기능: 문의 상태 변경
- 상태: **API·hook 정의, 화면 사용처 없음** · F05
- 요청: `application/json: UpdateInquiryStatusRequest{status*:OPEN / IN_PROGRESS / COMPLETED}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/inquiries/api/inquiry.api.ts:44](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.api.ts:44) (`patchInquiryStatus`)

## 11. GET /admin/inquiries/types

- 기능: 문의 타입 조회
- 상태: **API·hook 정의, 화면 사용처 없음**
- 요청: `query pageable*: Pageable{page:integer(int32), size:integer(int32), sort:[string]}`
- 성공 응답 200 payload: `PageResponseGetInquiryTypeResponse{items:[GetInquiryTypeResponse], total:integer(int64), page:integer(int32), size:integer(int32)}`
- 구현 근거: [src/entities/inquiries/api/inquiry-type.api.ts:32](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.api.ts:32) (`getList`)

## 12. POST /admin/inquiries/types

- 기능: 문의 타입 등록
- 상태: **API·hook 정의, 화면 사용처 없음** · F05
- 요청: `application/json: CreateInquiryTypeRequest{code*:string, name*:string}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/inquiries/api/inquiry-type.api.ts:35](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.api.ts:35) (`postType`)

## 13. DELETE /admin/inquiries/types/{typeId}

- 기능: 문의 타입 삭제
- 상태: **API·hook 정의, 화면 사용처 없음** · F05
- 요청: `body/query 없음`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/inquiries/api/inquiry-type.api.ts:45](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.api.ts:45) (`deleteType`)

## 14. PUT /admin/inquiries/types/{typeId}

- 기능: 문의 타입 수정
- 상태: **API·hook 정의, 화면 사용처 없음** · F05
- 요청: `application/json: UpdateInquiryTypeRequest{name*:string}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/inquiries/api/inquiry-type.api.ts:38](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.api.ts:38) (`putType`)

## 15. GET /admin/items

- 기능: 아이템 목록 조회
- 상태: **화면 호출 연결 확인**
- 요청: `query req*: GetItemsRequest{page*:integer(int32), size*:integer(int32), mainCategoryId:integer(int64), subCategoryId:integer(int64), gender:COMMON / MAN / WOMAN, status:PENDING / ON_SALE / ON_HOLD / END_SALE, keyword:string}`
- 성공 응답 200 payload: `PageResponseGetItemSummaryResponse{items:[GetItemSummaryResponse], total:integer(int64), page:integer(int32), size:integer(int32)}`
- 구현 근거: [src/entities/items/api/items.api.ts:42](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:42) (`getList`)

## 16. POST /admin/items

- 기능: 아이템 생성
- 상태: **화면 호출 연결 확인** · F09
- 요청: `application/json: CreateItemRequest{id*:integer(int64), name*:string, description*:string, mainCategoryId*:integer(int64), subCategoryId*:integer(int64), gender*:COMMON / MAN / WOMAN, paymentType*:POINT, saleAmount*:integer(int32), scopeMetaverse*:boolean, imageUuid:string(uuid), status*:PENDING / ON_SALE / ON_HOLD / END_SALE, newBadgeUntil*:string(date-time), excludeFromEventReward*:boolean}`
- 성공 응답 200 payload: `CreateItemResponse{id:integer(int64), name:string, createdAt:string(date-time)}`
- 구현 근거: [src/entities/items/api/items.api.ts:51](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:51) (`postItem`)

## 17. DELETE /admin/items/{itemId}

- 기능: 아이템 삭제
- 상태: **화면 호출 연결 확인**
- 요청: `body/query 없음`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/items/api/items.api.ts:57](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:57) (`deleteItem`)

## 18. GET /admin/items/{itemId}

- 기능: 아이템 상세 조회
- 상태: **화면 호출 연결 확인**
- 요청: `body/query 없음`
- 성공 응답 200 payload: `GetItemDetailResponse{id:integer(int64), name:string, description:string, mainCategoryId:integer(int64), subCategoryId:integer(int64), gender:COMMON / MAN / WOMAN, saleAmount:integer(int32), paymentType:POINT, newBadgeUntil:string(date-time), isShowApp:boolean, excludeFromEventReward:boolean, status:PENDING / ON_SALE / ON_HOLD / END_SALE, image:string}`
- 구현 근거: [src/entities/items/api/items.api.ts:45](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:45) (`getDetail`)

## 19. PATCH /admin/items/{itemId}

- 기능: 아이템 수정
- 상태: **화면 호출 연결 확인**
- 요청: `application/json: UpdateItemRequest{name:string, description:string, mainCategoryId:integer(int64), subCategoryId:integer(int64), gender:COMMON / MAN / WOMAN, saleAmount:integer(int32), paymentType:POINT, newBadgeUntil:string(date-time), isShowApp:boolean, excludeFromEventReward:boolean, status:PENDING / ON_SALE / ON_HOLD / END_SALE, image:string}`
- 성공 응답 200 payload: `UpdateItemResponse{id:integer(int64), name:string, description:string, mainCategoryId:integer(int64), subCategoryId:integer(int64), gender:COMMON / MAN / WOMAN, saleAmount:integer(int32), paymentType:POINT, newBadgeUntil:string(date-time), isShowApp:boolean, excludeFromEventReward:boolean, status:PENDING / ON_SALE / ON_HOLD / END_SALE, imageUrl:string}`
- 구현 근거: [src/entities/items/api/items.api.ts:54](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:54) (`patchItem`)

## 20. DELETE /admin/items/{itemId}/image

- 기능: 아이템 이미지 삭제
- 상태: **화면 호출 연결 확인**
- 요청: `body/query 없음`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/items/api/items.api.ts:78](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:78) (`deleteImage`)

## 21. PATCH /admin/items/batch

- 기능: 여러 아이템 상태 변경
- 상태: **화면 호출 연결 확인**
- 요청: `application/json: UpdateItemsListStatusRequest{itemIds*:[integer(int64)], status*:PENDING / ON_SALE / ON_HOLD / END_SALE}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/items/api/items.api.ts:75](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:75) (`patchBatchStatus`)

## 22. GET /admin/items/categories

- 기능: 아이템 카테고리 조회
- 상태: **화면 호출 연결 확인**
- 요청: `body/query 없음`
- 성공 응답 200 payload: `[GetItemCategoryResponse{id:integer(int64), name:string, parentName:string}]`
- 구현 근거: [src/entities/items/api/item-category.api.ts:31](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item-category.api.ts:31) (`getList`)

## 23. POST /admin/items/categories

- 기능: 아이템 카테고리 생성
- 상태: **화면 호출 연결 확인**
- 요청: `application/json: CreateItemCategoryRequest{name*:string, parentCatrgoryName:string}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/items/api/item-category.api.ts:34](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item-category.api.ts:34) (`postCategory`)

## 24. DELETE /admin/items/categories/{categoryId}

- 기능: 아이템 카테고리 삭제
- 상태: **화면 호출 연결 확인**
- 요청: `body/query 없음`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/items/api/item-category.api.ts:44](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item-category.api.ts:44) (`deleteCategory`)

## 25. PATCH /admin/items/categories/{categoryId}

- 기능: 아이템 카테고리 수정
- 상태: **화면 호출 연결 확인**
- 요청: `application/json: UpdateItemCategoryRequest{name*:string, parentCatrgoryName:string}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/items/api/item-category.api.ts:37](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item-category.api.ts:37) (`patchCategory`)

## 26. GET /admin/items/latest/id

- 기능: 아이템 최신 아이디 조회
- 상태: **API·hook 정의, 화면 사용처 없음**
- 요청: `query req*: GetItemLatestIdRequest{subCategoryId*:integer(int64), gender*:COMMON / MAN / WOMAN}`
- 성공 응답 200 payload: `integer(int64)`
- 구현 근거: [src/entities/items/api/items.api.ts:48](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:48) (`getLatestId`)

## 27. PATCH /admin/items/toggle/event/reward/{itemId}

- 기능: 아이템 이벤트 리워드 노출 토글
- 상태: **화면 호출 연결 확인**
- 요청: `body/query 없음`
- 성공 응답 200 payload: `boolean`
- 구현 근거: [src/entities/items/api/items.api.ts:72](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:72) (`toggleEventReward`)

## 28. POST /admin/items/upload

- 기능: 아이템 이미지 업로드
- 상태: **화면 호출 연결 확인**
- 요청: `query subCategoryId*: integer(int64); multipart/form-data: {file*:string(binary)}`
- 성공 응답 200 payload: `UploadItemImageResponse{uuid:string, url:string}`
- 구현 근거: [src/entities/items/api/items.api.ts:64](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:64) (`uploadImage`)

## 29. GET /admin/news

- 기능: 공지사항 목록 조회
- 상태: **화면 호출 연결 확인** · F08
- 요청: `query type: ANNOUNCEMENT / UPDATE / EVENT / ETC; query status: DRAFT / PUBLISHED / ARCHIVED; query by: TITLE / TITLE_CONTENT; query keyword: string; query page: integer; query size: integer; query sort: [string]`
- 성공 응답 200 payload: `NewsListResponse{items:[NewsSummaryResponse], total:integer(int64), page:integer(int32), size:integer(int32), isPinnedCount:integer(int32)}`
- 구현 근거: [src/entities/news/api/news.api.ts:32](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/news/api/news.api.ts:32) (`getList`)

## 30. POST /admin/news

- 기능: 공지사항 등록
- 상태: **화면 호출 연결 확인** · F08
- 요청: `application/json: CreateNewsRequest{title*:string, content*:string, type*:ANNOUNCEMENT / UPDATE / EVENT / ETC, status*:DRAFT / PUBLISHED / ARCHIVED, isPinned*:boolean}`
- 성공 응답 201 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/news/api/news.api.ts:42](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/news/api/news.api.ts:42) (`postNews`)

## 31. DELETE /admin/news/{newsId}

- 기능: 공지사항 삭제
- 상태: **화면 호출 연결 확인** · F08
- 요청: `body/query 없음`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/news/api/news.api.ts:52](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/news/api/news.api.ts:52) (`deleteNews`)

## 32. GET /admin/news/{newsId}

- 기능: 공지사항 상세 조회
- 상태: **화면 호출 연결 확인** · F08
- 요청: `body/query 없음`
- 성공 응답 200 payload: `NewsDetailResponse{id:integer(int64), type:ANNOUNCEMENT / UPDATE / EVENT / ETC, status:DRAFT / PUBLISHED / ARCHIVED, title:string, content:string, isPinned:boolean, viewCount:integer(int32), createdAt:string(date-time), updatedAt:string(date-time)}`
- 구현 근거: [src/entities/news/api/news.api.ts:39](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/news/api/news.api.ts:39) (`getDetail`)

## 33. PATCH /admin/news/{newsId}

- 기능: 공지사항 수정
- 상태: **화면 호출 연결 확인** · F08
- 요청: `application/json: UpdateNewsRequest{title:string, content:string, type:ANNOUNCEMENT / UPDATE / EVENT / ETC, status:DRAFT / PUBLISHED / ARCHIVED, isPinned:boolean}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/news/api/news.api.ts:45](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/news/api/news.api.ts:45) (`patchNews`)

## 34. GET /admin/news/{newsId}/comments

- 기능: 공지사항 댓글 목록 조회
- 상태: **일치 호출 없음** · F08
- 요청: `query page: integer; query size: integer; query sort: [string]`
- 성공 응답 200 payload: `PageResponseNewsCommentResponse{items:[NewsCommentResponse], total:integer(int64), page:integer(int32), size:integer(int32)}`
- 구현 근거: —

## 35. DELETE /admin/news/{newsId}/comments/{commentId}

- 기능: 공지사항 댓글 삭제
- 상태: **일치 호출 없음** · F08
- 요청: `body/query 없음`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: —

## 36. PATCH /admin/news/batch

- 기능: 공지사항 일괄 상태 변경
- 상태: **일치 호출 없음** · F08
- 요청: `application/json: BatchUpdateNewsListRequest{newsIds*:[integer(int64)], status:DRAFT / PUBLISHED / ARCHIVED, isPinned:boolean}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: —

## 37. GET /admin/parcels

- 기능: 우편 내역 확인
- 상태: **API·hook 정의, 화면 사용처 없음** · F10
- 요청: `query recipient: string; query page: integer; query size: integer; query sort: [string]`
- 성공 응답 200 payload: `PageResponseParcelHistoryResponse{items:[ParcelHistoryResponse], total:integer(int64), page:integer(int32), size:integer(int32)}`
- 구현 근거: [src/entities/parcels/api/parcel.api.ts:27](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/parcels/api/parcel.api.ts:27) (`getList`)

## 38. POST /admin/parcels

- 기능: 우편 보내기
- 상태: **API·hook 정의, 화면 사용처 없음**
- 요청: `application/json: SendParcelRequest{title*:string, content*:string, userId*:integer(int64), itemId*:integer(int64), amount*:integer(int32)}`
- 성공 응답 200 payload: `미상세`
- 구현 근거: [src/entities/parcels/api/parcel.api.ts:37](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/parcels/api/parcel.api.ts:37) (`send`)

## 39. GET /admin/parcels/export

- 기능: 우편 발송 내역 엑셀 출력
- 상태: **API·hook 정의, 화면 사용처 없음**
- 요청: `query recipient: string`
- 성공 응답 200 payload: `string(byte)`
- 구현 근거: [src/entities/parcels/api/parcel.api.ts:40](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/parcels/api/parcel.api.ts:40) (`exportHistory`)

## 40. GET /admin/usage/item

- 기능: getItemHistoryList
- 상태: **API·hook 정의, 화면 사용처 없음** · F03
- 요청: `query query*: GetItemHistoryListRequest{startDate*:string(date), endDate*:string(date), by:USER_ID / USER_NAME / ITEM_NAME, keyword:string}; query page: integer; query size: integer; query sort: [string]`
- 성공 응답 200 payload: `PageResponseItemHistoryResponse{items:[ItemHistoryResponse], total:integer(int64), page:integer(int32), size:integer(int32)}`
- 구현 근거: [src/entities/usage/api/admin-usage.api.ts:28](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/usage/api/admin-usage.api.ts:28) (`getItemList`)

## 41. GET /admin/usage/point

- 기능: getPointHistoryList
- 상태: **API·hook 정의, 화면 사용처 없음** · F03
- 요청: `query query*: GetPointHistoryListRequest{startDate*:string(date), endDate*:string(date), by:USER_ID / USER_NAME, keyword:string}; query page: integer; query size: integer; query sort: [string]`
- 성공 응답 200 payload: `PageResponsePointHistoryResponse{items:[PointHistoryResponse], total:integer(int64), page:integer(int32), size:integer(int32)}`
- 구현 근거: [src/entities/usage/api/admin-usage.api.ts:18](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/usage/api/admin-usage.api.ts:18) (`getPointList`)

## 42. GET /admin/users/{userId}

- 기능: 사용자 조회
- 상태: **API·hook 정의, 화면 사용처 없음** · F02
- 요청: `body/query 없음`
- 성공 응답 200 payload: `AdminUserResponse{publicId:string(uuid), nickname:string, status:ACTIVE / SUSPENDED / WITHDRAWN, createdAt:string(date-time), updatedAt:string(date-time)}`
- 구현 근거: [src/entities/users/api/admin-users.api.ts:35](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.api.ts:35) (`getDetail`)

## 43. POST /admin/users/{userId}/authorities

- 기능: 사용자 권한(시민증, 역할) 부여
- 상태: **API·hook 정의, 화면 사용처 없음** · F05
- 요청: `application/json: GrantUserAuthorityRequest{citizenCard:boolean, roles:[string]}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/users/api/admin-users.api.ts:53](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.api.ts:53) (`postUserAuthorities`)

## 44. POST /admin/users/{userId}/points

- 기능: 사용자 포인트 지급/차감
- 상태: **API·hook 정의, 화면 사용처 없음** · F02
- 요청: `application/json: AdjustUserPointRequest{amount*:integer(int32), direction*:RECHARGE / DEDUCT, reason:string}`
- 성공 응답 200 payload: `예시: {"code":"SUCCESS","message":"성공","data":null}`
- 구현 근거: [src/entities/users/api/admin-users.api.ts:45](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.api.ts:45) (`postUserPoints`)

## 45. PATCH /admin/users/{userId}/status

- 기능: 사용자 상태 수정(정상/정지)
- 상태: **API·hook 정의, 화면 사용처 없음**
- 요청: `application/json: UpdateUserStatusRequest{status*:ACTIVE / SUSPEND, reason:string}`
- 성공 응답 200 payload: `예시: {"code":"SUCCESS","message":"성공","data":null}`
- 구현 근거: [src/entities/users/api/admin-users.api.ts:60](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.api.ts:60) (`patchUserStatus`)

## 46. GET /admin/users/withdrawals

- 기능: 사용자 탈퇴 로그 조회
- 상태: **API·hook 정의, 화면 사용처 없음**
- 요청: `query page: integer; query size: integer; query sort: [string]`
- 성공 응답 200 payload: `PageResponseUserWithdrawLogResponse{items:[UserWithdrawLogResponse], total:integer(int64), page:integer(int32), size:integer(int32)}`
- 구현 근거: [src/entities/users/api/admin-users.api.ts:38](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.api.ts:38) (`getWithdrawals`)

## 47. GET /admin/video

- 기능: 비디오 목록 조회
- 상태: **API·hook 정의, 화면 사용처 없음**
- 요청: `query pageable*: Pageable{page:integer(int32), size:integer(int32), sort:[string]}`
- 성공 응답 200 payload: `PageResponseGetVideoListResponse{items:[GetVideoListResponse], total:integer(int64), page:integer(int32), size:integer(int32)}`
- 구현 근거: [src/entities/video/api/video.api.ts:47](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.api.ts:47) (`getList`)

## 48. POST /admin/video

- 기능: 비디오 등록
- 상태: **API·hook 정의, 화면 사용처 없음** · F04
- 요청: `multipart/form-data: {data*:CreateVideoRequest{name*:string, description:string}, file*:string(binary)}`
- 성공 응답 200 payload: `integer(int64)`
- 구현 근거: [src/entities/video/api/video.api.ts:60](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.api.ts:60) (`postVideo`)

## 49. DELETE /admin/video/{videoId}

- 기능: 비디오 삭제
- 상태: **API·hook 정의, 화면 사용처 없음**
- 요청: `body/query 없음`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/video/api/video.api.ts:80](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.api.ts:80) (`deleteVideo`)

## 50. GET /admin/video/{videoId}

- 기능: 비디오 조회
- 상태: **API·hook 정의, 화면 사용처 없음**
- 요청: `body/query 없음`
- 성공 응답 200 payload: `미상세`
- 구현 근거: [src/entities/video/api/video.api.ts:57](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.api.ts:57) (`getDetail`)

## 51. PATCH /admin/video/{videoId}

- 기능: 비디오 수정
- 상태: **API·hook 정의, 화면 사용처 없음** · F04
- 요청: `multipart/form-data: {data*:UpdateVideoRequest{name*:string, description:string}, file:string(binary)}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/video/api/video.api.ts:70](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.api.ts:70) (`patchVideo`)

## 52. POST /admin/video/{videoId}/thumbnail

- 기능: 썸네일 등록
- 상태: **API·hook 정의, 화면 사용처 없음**
- 요청: `multipart/form-data: {file*:string(binary)}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/video/api/video.api.ts:83](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.api.ts:83) (`postThumbnail`)

## 53. GET /admin/video/playlists

- 기능: 플레이리스트 목록 조회
- 상태: **API·hook 정의, 화면 사용처 없음**
- 요청: `query pageable*: Pageable{page:integer(int32), size:integer(int32), sort:[string]}`
- 성공 응답 200 payload: `PageResponseGetPlaylistSummaryResponse{items:[GetPlaylistSummaryResponse], total:integer(int64), page:integer(int32), size:integer(int32)}`
- 구현 근거: [src/entities/video/api/playlist.api.ts:37](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.api.ts:37) (`getList`)

## 54. POST /admin/video/playlists

- 기능: 플레이리스트 생성
- 상태: **API·hook 정의, 화면 사용처 없음**
- 요청: `application/json: CreatePlaylistRequest{name*:string, description:string, videoIds:[integer(int64)]}`
- 성공 응답 200 payload: `integer(int64)`
- 구현 근거: [src/entities/video/api/playlist.api.ts:50](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.api.ts:50) (`postPlaylist`)

## 55. DELETE /admin/video/playlists/{playlistId}

- 기능: 플레이리스트 삭제
- 상태: **API·hook 정의, 화면 사용처 없음**
- 요청: `body/query 없음`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/video/api/playlist.api.ts:60](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.api.ts:60) (`deletePlaylist`)

## 56. GET /admin/video/playlists/{playlistId}

- 기능: 플레이리스트 조회
- 상태: **API·hook 정의, 화면 사용처 없음**
- 요청: `body/query 없음`
- 성공 응답 200 payload: `GetPlaylistResponse{id:integer(int64), name:string, description:string, isDelete:boolean, createdAt:string(date-time), videos:[PlaylistVideoResponse]}`
- 구현 근거: [src/entities/video/api/playlist.api.ts:47](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.api.ts:47) (`getDetail`)

## 57. PATCH /admin/video/playlists/{playlistId}

- 기능: 플레이리스트 수정
- 상태: **API·hook 정의, 화면 사용처 없음**
- 요청: `application/json: UpdatePlaylistRequest{name*:string, description:string, videoIds:[integer(int64)]}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/video/api/playlist.api.ts:53](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.api.ts:53) (`patchPlaylist`)

## 58. POST /auth/login

- 기능: 관리자 로그인
- 상태: **화면 호출 연결 확인**
- 요청: `application/json: LoginRequest{loginId*:string, password*:string}`
- 성공 응답 200 payload: `TokenResponse{accessToken:string}`
- 구현 근거: [src/entities/auth/api/auth.api.ts:12](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/auth/api/auth.api.ts:12) (`signIn`)

## 59. GET /citizen/proposals

- 기능: 시민참여 제안 목록 조회
- 상태: **화면 호출 연결 확인** · F01
- 요청: `query status: [RECEIVED / UNDER_REVIEW / ADOPTED / REJECTED]; query title: string; query author: string; query page: integer; query size: integer; query sort: [string]`
- 성공 응답 200 payload: `PageResponseCitizenProposalSummaryResponse{items:[CitizenProposalSummaryResponse], total:integer(int64), page:integer(int32), size:integer(int32)}`
- 구현 근거: [src/entities/cp-proposal/api/cp-proposal.api.ts:34](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/cp-proposal/api/cp-proposal.api.ts:34) (`getList`)

## 60. GET /citizen/proposals/{proposalId}

- 기능: 제안 상세(id) 조회
- 상태: **화면 호출 연결 확인** · F01
- 요청: `body/query 없음`
- 성공 응답 200 payload: `CitizenProposalResponse{id:integer(int64), author:string, title:string, background:string, content:string, expectedEffect:string, referenceCase:string, status:RECEIVED / UNDER_REVIEW / ADOPTED / REJECTED, reviewResult:string, createdAt:string(date-time), updatedAt:string(date-time)}`
- 구현 근거: [src/entities/cp-proposal/api/cp-proposal.api.ts:40](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/cp-proposal/api/cp-proposal.api.ts:40) (`getDetail`)

## 61. PATCH /citizen/proposals/{proposalId}

- 기능: 제안 상태 수정
- 상태: **일치 호출 없음** · F01
- 요청: `application/json: UpdateCitizenProposalStatusRequest{status*:RECEIVED / UNDER_REVIEW / ADOPTED / REJECTED}`
- 성공 응답 200 payload: `미상세`
- 구현 근거: —

## 62. PATCH /citizen/proposals/{proposalId}/review-result

- 기능: 제안 검토 결과 수정
- 상태: **일치 호출 없음** · F01
- 요청: `application/json: UpdateCitizenProposalReviewResultRequest{reviewResult*:string}`
- 성공 응답 200 payload: `미상세`
- 구현 근거: —

## 63. GET /citizen/proposals/summary

- 기능: 상태별 제안 데이터(count) 조회
- 상태: **일치 호출 없음** · F01
- 요청: `body/query 없음`
- 성공 응답 200 payload: `CitizenProposalStatusCountResponse{total:integer(int64), received:integer(int32), underReview:integer(int32), adopted:integer(int32), rejected:integer(int32)}`
- 구현 근거: —

## 64. GET /citizen/votes

- 기능: 시민참여 투표 목록 조회
- 상태: **화면 호출 연결 확인**
- 요청: `query page: integer; query size: integer; query sort: [string]`
- 성공 응답 200 payload: `PageResponseCitizenVoteSummaryResponse{items:[CitizenVoteSummaryResponse], total:integer(int64), page:integer(int32), size:integer(int32)}`
- 구현 근거: [src/entities/cp-vote/api/cp-vote.api.ts:22](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/cp-vote/api/cp-vote.api.ts:22) (`getList`)

## 65. GET /citizen/votes/{voteId}

- 기능: 투표 상세(id) 조회
- 상태: **화면 호출 연결 확인**
- 요청: `body/query 없음`
- 성공 응답 200 payload: `CitizenVoteDetailResponse{id:integer(int64), status:DRAFT / UPCOMING / IN_PROGRESS / CLOSED / CANCELLED, title:string, agenda:string, startsAt:string(date-time), endsAt:string(date-time), totalCount:integer(int32), agreeCount:integer(int32), disagreeCount:integer(int32), createdAt:string(date-time), updatedAt:string(date-time)}`
- 구현 근거: [src/entities/cp-vote/api/cp-vote.api.ts:25](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/cp-vote/api/cp-vote.api.ts:25) (`getDetail`)

## 66. GET /citizen/votes/summary

- 기능: 상태별 투표 데이터(count) 조회
- 상태: **일치 호출 없음**
- 요청: `body/query 없음`
- 성공 응답 200 payload: `CitizenVoteStatusCountResponse{total:integer(int64), inProgress:integer(int64), closed:integer(int64)}`
- 구현 근거: —

## 67. GET /events/attendance

- 기능: 출석 이벤트 목록 조회
- 상태: **화면 호출 연결 확인**
- 요청: `query query*: GetEventAttendanceListRequest{page*:integer(int32), size*:integer(int32)}`
- 성공 응답 200 payload: `PageResponseEventAttendanceSummaryResponse{items:[EventAttendanceSummaryResponse], total:integer(int64), page:integer(int32), size:integer(int32)}`
- 구현 근거: [src/entities/event/api/attendance/attendance.api.ts:22](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.api.ts:22) (`getList`)

## 68. POST /events/attendance

- 기능: 출석 이벤트 등록
- 상태: **화면 호출 연결 확인**
- 요청: `application/json: CreateEventAttendanceRequest{id*:integer(int64), code*:string, startAt*:string(date-time), endAt*:string(date-time), items*:[EventAttendanceItemDto]}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/event/api/attendance/attendance.api.ts:28](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.api.ts:28) (`postEvent`)

## 69. GET /events/attendance/{eventId}

- 기능: 출석 이벤트 조회
- 상태: **화면 호출 연결 확인**
- 요청: `body/query 없음`
- 성공 응답 200 payload: `EventAttendanceResponse{id:integer(int64), code:string, startAt:string(date-time), endAt:string(date-time), isActive:boolean, configs:[EventAttendanceConfigResponse], items:[EventAttendanceItemResponse]}`
- 구현 근거: [src/entities/event/api/attendance/attendance.api.ts:25](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.api.ts:25) (`getDetail`)

## 70. PATCH /events/attendance/{eventId}

- 기능: 출석 이벤트 수정
- 상태: **화면 호출 연결 확인**
- 요청: `application/json: PatchEventAttendanceRequest{code:string, startAt:string(date-time), endAt:string(date-time), isActive:boolean}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/event/api/attendance/attendance.api.ts:31](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.api.ts:31) (`patchEvent`)

## 71. PATCH /events/attendance/{eventId}/configs

- 기능: 출석 이벤트 설정 수정
- 상태: **화면 호출 연결 확인**
- 요청: `application/json: PatchEventAttendanceConfigRequest{configs*:[AttendanceConfigItem]}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/event/api/attendance/attendance.api.ts:44](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.api.ts:44) (`patchConfigs`)

## 72. POST /events/attendance/{eventId}/configs/upload

- 기능: 출석 이벤트 설정 이미지 업로드
- 상태: **화면 호출 연결 확인**
- 요청: `multipart/form-data: {file*:string(binary)}`
- 성공 응답 200 payload: `UploadEventAttendanceConfigImageResponse{url:string}`
- 구현 근거: [src/entities/event/api/attendance/attendance.api.ts:55](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.api.ts:55) (`uploadConfigImage`)

## 73. GET /events/attendance/{eventId}/items

- 기능: 출석 이벤트 보상 조회
- 상태: **API·hook 정의, 화면 사용처 없음**
- 요청: `body/query 없음`
- 성공 응답 200 payload: `[EventAttendanceItemResponse{id:integer(int64), day:integer(int32), type:DAILY / ACC, objectId:integer(int64), objectName:string, objectAmount:integer(int32), sortOrder:integer(int32)}]`
- 구현 근거: [src/entities/event/api/attendance/attendance.api.ts:34](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.api.ts:34) (`getItems`)

## 74. PUT /events/attendance/{eventId}/items

- 기능: 출석 이벤트 보상 수정
- 상태: **화면 호출 연결 확인**
- 요청: `application/json: UpdateEventAttendanceItemsRequest{items*:[EventAttendanceItemDto]}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/event/api/attendance/attendance.api.ts:37](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.api.ts:37) (`putItems`)

## 75. GET /events/roulette

- 기능: 룰렛 이벤트 목록 조회
- 상태: **화면 호출 연결 확인**
- 요청: `query query*: GetEventRouletteListRequest{page*:integer(int32), size*:integer(int32)}`
- 성공 응답 200 payload: `PageResponseEventRouletteSummaryResponse{items:[EventRouletteSummaryResponse], total:integer(int64), page:integer(int32), size:integer(int32)}`
- 구현 근거: [src/entities/event/api/roulette/roulette.api.ts:22](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.api.ts:22) (`getList`)

## 76. POST /events/roulette

- 기능: 룰렛 이벤트 등록
- 상태: **화면 호출 연결 확인**
- 요청: `application/json: CreateEventRouletteRequest{id*:integer(int64), code*:string, startAt*:string(date-time), endAt*:string(date-time), items*:[EventRouletteItemDto]}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/event/api/roulette/roulette.api.ts:28](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.api.ts:28) (`postEvent`)

## 77. GET /events/roulette/{eventId}

- 기능: 룰렛 이벤트 조회
- 상태: **화면 호출 연결 확인**
- 요청: `body/query 없음`
- 성공 응답 200 payload: `EventRouletteResponse{id:integer(int64), code:string, startAt:string(date-time), endAt:string(date-time), isActive:boolean, configs:[EventRouletteConfigResponse], items:[EventRouletteItemResponse]}`
- 구현 근거: [src/entities/event/api/roulette/roulette.api.ts:25](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.api.ts:25) (`getDetail`)

## 78. PATCH /events/roulette/{eventId}

- 기능: 룰렛 이벤트 수정
- 상태: **화면 호출 연결 확인**
- 요청: `application/json: PatchEventRouletteRequest{code:string, startAt:string(date-time), endAt:string(date-time), isActive:boolean}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/event/api/roulette/roulette.api.ts:31](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.api.ts:31) (`patchEvent`)

## 79. PATCH /events/roulette/{eventId}/configs

- 기능: 룰렛 이벤트 설정 수정
- 상태: **화면 호출 연결 확인**
- 요청: `application/json: PatchEventRouletteConfigRequest{configs*:[RouletteConfigItem]}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/event/api/roulette/roulette.api.ts:44](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.api.ts:44) (`patchConfigs`)

## 80. POST /events/roulette/{eventId}/configs/upload

- 기능: 룰렛 이벤트 설정 이미지 업로드
- 상태: **화면 호출 연결 확인**
- 요청: `multipart/form-data: {file*:string(binary)}`
- 성공 응답 200 payload: `UploadEventRouletteConfigImageResponse{url:string}`
- 구현 근거: [src/entities/event/api/roulette/roulette.api.ts:55](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.api.ts:55) (`uploadConfigImage`)

## 81. GET /events/roulette/{eventId}/items

- 기능: 룰렛 이벤트 보상 조회
- 상태: **API·hook 정의, 화면 사용처 없음**
- 요청: `body/query 없음`
- 성공 응답 200 payload: `[EventRouletteItemResponse{id:integer(int64), objectId:integer(int64), objectName:string, objectAmount:integer(int32), objectImageUrl:string, chance:integer(int32), sortOrder:integer(int32)}]`
- 구현 근거: [src/entities/event/api/roulette/roulette.api.ts:34](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.api.ts:34) (`getItems`)

## 82. PUT /events/roulette/{eventId}/items

- 기능: 룰렛 이벤트 보상 수정
- 상태: **화면 호출 연결 확인**
- 요청: `application/json: UpdateEventRouletteItemsRequest{items*:[EventRouletteItemDto]}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: [src/entities/event/api/roulette/roulette.api.ts:37](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.api.ts:37) (`putItems`)

## 83. GET /external/dashboard/daily

- 기능: 일별 현황 조회
- 상태: **일치 호출 없음**
- 요청: `query date*: string(date)`
- 성공 응답 200 payload: `DailyDashboardResponse{statDate:string(date), user:PeriodUserStatsResponse{totalCount:integer(int64), newCount:integer(int64), loginCount:integer(int64), onlineAvgCount:integer(int64), onlineMaxCount:integer(int64)}, os:ExternalOsStatsResponse{osCounts:[OsCountResponse]}, inquiry:PeriodInquiryStatsResponse{receivedCount:integer(int64), ongoingCount:integer(int64), resolvedCount:integer(int64)}, item:PeriodItemStatsResponse{salesRanks:[PeriodItemSalesRankResponse]}}`
- 구현 근거: —

## 84. GET /external/dashboard/monthly

- 기능: 월별 현황 조회
- 상태: **일치 호출 없음**
- 요청: `query date*: string(date)`
- 성공 응답 200 payload: `MonthlyDashboardResponse{month:string, startDate:string(date), endDate:string(date), user:PeriodUserStatsResponse{totalCount:integer(int64), newCount:integer(int64), loginCount:integer(int64), onlineAvgCount:integer(int64), onlineMaxCount:integer(int64)}, os:ExternalOsStatsResponse{osCounts:[OsCountResponse]}, inquiry:PeriodInquiryStatsResponse{receivedCount:integer(int64), ongoingCount:integer(int64), resolvedCount:integer(int64)}, item:PeriodItemStatsResponse{salesRanks:[PeriodItemSalesRankResponse]}}`
- 구현 근거: —

## 85. GET /external/dashboard/summary

- 기능: 통합 현황 조회
- 상태: **일치 호출 없음**
- 요청: `body/query 없음`
- 성공 응답 200 payload: `ExternalDashboardResponse{user:ExternalUserStatsResponse{totalCount:integer(int64), statusCounts:[UserStatusCountResponse], newTodayCount:integer(int64), loginTodayCount:integer(int64), onlineCount:integer(int64), changeRate:number(double)}, os:ExternalOsStatsResponse{osCounts:[OsCountResponse]}, inquiry:ExternalInquiryStatsResponse{totalCount:integer(int64), ongoingCount:integer(int64), todayCount:integer(int64), todayOngoingCount:integer(int64), todayResolvedCount:integer(int64), changeRate:number(double)}, item:ExternalItemStatsResponse{salesTodayCount:integer(int64), salesRanks:[ItemSalesRankResponse], changeRate:number(double)}}`
- 구현 근거: —

## 86. GET /external/dashboard/weekly

- 기능: 주별 현황 조회
- 상태: **일치 호출 없음**
- 요청: `query date*: string(date)`
- 성공 응답 200 payload: `WeeklyDashboardResponse{week:string, startDate:string(date), endDate:string(date), user:PeriodUserStatsResponse{totalCount:integer(int64), newCount:integer(int64), loginCount:integer(int64), onlineAvgCount:integer(int64), onlineMaxCount:integer(int64)}, os:ExternalOsStatsResponse{osCounts:[OsCountResponse]}, inquiry:PeriodInquiryStatsResponse{receivedCount:integer(int64), ongoingCount:integer(int64), resolvedCount:integer(int64)}, item:PeriodItemStatsResponse{salesRanks:[PeriodItemSalesRankResponse]}}`
- 구현 근거: —

## 87. GET /health

- 기능: health
- 상태: **일치 호출 없음**
- 요청: `body/query 없음`
- 성공 응답 200 payload: `object`
- 구현 근거: —

## 88. GET /maintenance

- 기능: getAll
- 상태: **기존 경로·계약 불일치** · F07
- 요청: `body/query 없음`
- 성공 응답 200 payload: `[MaintenanceResponse{id:integer(int64), key:string, value:string, createdAt:string(date-time), updatedAt:string(date-time)}]`
- 구현 근거: —

## 89. PATCH /maintenance

- 기능: update
- 상태: **기존 경로·계약 불일치** · F07
- 요청: `application/json: UpdateMaintenanceItemRequest{config:[MaintenanceConfigItem]}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: —

## 90. PATCH /maintenance/off

- 기능: maintenanceOff
- 상태: **일치 호출 없음** · F07
- 요청: `body/query 없음`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: —

## 91. PATCH /maintenance/on

- 기능: maintenanceOn
- 상태: **일치 호출 없음** · F07
- 요청: `body/query 없음`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: —

## 92. GET /maintenance/one

- 기능: getOne
- 상태: **일치 호출 없음** · F07
- 요청: `query query*: GetMaintenanceItemRequest{key*:string}`
- 성공 응답 200 payload: `MaintenanceResponse{id:integer(int64), key:string, value:string, createdAt:string(date-time), updatedAt:string(date-time)}`
- 구현 근거: —

## 93. PATCH /maintenance/time

- 기능: maintenanceTime
- 상태: **일치 호출 없음** · F07
- 요청: `application/json: SetMaintenanceTimeRequest{start:string, end:string}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: —

## 94. PATCH /maintenance/version

- 기능: setVersion
- 상태: **일치 호출 없음** · F07
- 요청: `application/json: SetMaintenanceVersionRequest{version*:string}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: —

## 95. GET /me

- 기능: getMe
- 상태: **일치 호출 없음** · F06
- 요청: `body/query 없음`
- 성공 응답 200 payload: `MeResponse{id:integer(int64), loginId:string, name:string, department:string, roles:[RoleSummary], permissions:[string]}`
- 구현 근거: —

## 96. GET /me/menus

- 기능: getMyMenus
- 상태: **API만 정의** · F06
- 요청: `body/query 없음`
- 성공 응답 200 payload: `[MenuGroupResponse{key:string, label:string, order:integer(int32), children:[MenuItemResponse]}]`
- 구현 근거: [src/entities/menus/api/menus.api.ts:20](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/menus/api/menus.api.ts:20) (`getMyList`)

## 97. GET /menus

- 기능: getMenus
- 상태: **API만 정의** · F06
- 요청: `body/query 없음`
- 성공 응답 200 payload: `[ManagedMenuResponse{id:integer(int64), key:string, label:string, order:integer(int32), visible:boolean, requiredPermission:string, children:[ManagedMenuResponse]}]`
- 구현 근거: [src/entities/menus/api/menus.api.ts:15](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/menus/api/menus.api.ts:15) (`getList`)

## 98. PATCH /menus/{menuId}

- 기능: updateMenu
- 상태: **일치 호출 없음**
- 요청: `application/json: UpdateMenuRequest{label:string, visible:boolean}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: —

## 99. PUT /menus/order

- 기능: updateMenuOrder
- 상태: **일치 호출 없음**
- 요청: `application/json: UpdateMenuOrderRequest{items*:[Item]}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: —

## 100. GET /permissions

- 기능: getPermissionCatalog
- 상태: **일치 호출 없음**
- 요청: `body/query 없음`
- 성공 응답 200 payload: `[PermissionCategoryResponse{category:string, permissions:[PermissionResponse]}]`
- 구현 근거: —

## 101. GET /roles

- 기능: getRoles
- 상태: **일치 호출 없음**
- 요청: `body/query 없음`
- 성공 응답 200 payload: `[RoleSummaryResponse{id:integer(int64), code:string, name:string, immutable:boolean, permissionCount:integer(int32), adminCount:integer(int64)}]`
- 구현 근거: —

## 102. POST /roles

- 기능: createRole
- 상태: **일치 호출 없음**
- 요청: `application/json: CreateRoleRequest{code*:string, name*:string, permissionCodes*:[string]}`
- 성공 응답 200 payload: `CreateRoleResponse{id:integer(int64)}`
- 구현 근거: —

## 103. DELETE /roles/{roleId}

- 기능: deleteRole
- 상태: **일치 호출 없음**
- 요청: `body/query 없음`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: —

## 104. GET /roles/{roleId}

- 기능: getRole
- 상태: **일치 호출 없음**
- 요청: `body/query 없음`
- 성공 응답 200 payload: `RoleDetailResponse{id:integer(int64), code:string, name:string, immutable:boolean, permissionCodes:[string]}`
- 구현 근거: —

## 105. PATCH /roles/{roleId}

- 기능: updateRole
- 상태: **일치 호출 없음**
- 요청: `application/json: UpdateRoleRequest{name*:string}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: —

## 106. PUT /roles/{roleId}/permissions

- 기능: updateRolePermissions
- 상태: **일치 호출 없음**
- 요청: `application/json: UpdateRolePermissionsRequest{permissionCodes*:[string]}`
- 성공 응답 200 payload: `Void (data schema는 {})`
- 구현 근거: —

