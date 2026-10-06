# 전체 API 요청·응답·오류 계약

2026-09-28에 성공적으로 수집한 OpenAPI 스냅샷의 **75 paths / 106 operations**를 전부 수록했다. 현재 문서 서버 가용성과 별개로 후속 세션이 동일 근거를 읽도록 [원본 스냅샷](./openapi.snapshot.json)을 보존한다. [핸드오프](../handoff.md), [작업 항목·구현 차이](./api-work-items.md), [196개 DTO schema](./api-schema-catalog.md), [오류 계약 해설](./api-errors-and-integration.md)을 함께 읽는다.

## 읽는 방법

- 소스 기준: `sy-main@4b0b7db45aa9d15bf918a1a084370594e138a124`. 화면 연결 판정은 정적 호출 추적이며 실서버 검증이 아니다.
- 각 parameter의 `required`와 body 자체의 `required`, DTO 내부 `required`는 서로 다르다. schema 링크에서 필드별 필수·enum·format·길이·기본값을 확인한다. `required` 미기재를 null 허용으로 해석하지 않는다.
- query 객체 이름(`query`, `req`, `pageable`)은 OpenAPI의 표현을 그대로 보존했다. 이것만 보고 JSON 문자열 한 개로 전송하지 말고 기존 전송 코드와 서버 바인딩을 확인한다. 파라미터 원문에 style/explode 등이 있으면 그대로 적용한다.
- 성공·실패 예시는 명세의 예시이며 이번 세션의 실서버 응답이 아니다. 오류 응답이 미기재인 operation도 실패할 수 있다.
- 공통 JSON envelope는 `ApiResponseDto<TData>`와 `ApiClient`에서 처리한다. API 제네릭은 내부 payload이고 아래 envelope schema 자체를 다시 감싸지 않는다. `/health`, 영상 상세, Void, 파일 응답은 개별 원문을 확인한다.

## 전체 색인

| 번호 | method·path | 작업 | 현재 상태 |
| --- | --- | --- | --- |
| [op-001](#op-001) | `GET /accounts` | [T06](./api-work-items.md#t06) | **일치 호출 없음** |
| [op-002](#op-002) | `PUT /accounts/{adminId}/roles` | [T06](./api-work-items.md#t06) | **일치 호출 없음** |
| [op-003](#op-003) | `GET /admin/audit` | [T13](./api-work-items.md#t13) | **일치 호출 없음** |
| [op-004](#op-004) | `GET /admin/inquiries` | [T05](./api-work-items.md#t05) | **API·hook 정의, 화면 사용처 없음** |
| [op-005](#op-005) | `DELETE /admin/inquiries/{inquiryId}` | [T05](./api-work-items.md#t05) | **API·hook 정의, 화면 사용처 없음** · F05 |
| [op-006](#op-006) | `GET /admin/inquiries/{inquiryId}` | [T05](./api-work-items.md#t05) | **API·hook 정의, 화면 사용처 없음** |
| [op-007](#op-007) | `DELETE /admin/inquiries/{inquiryId}/answer` | [T05](./api-work-items.md#t05) | **API·hook 정의, 화면 사용처 없음** · F05 |
| [op-008](#op-008) | `POST /admin/inquiries/{inquiryId}/answer` | [T05](./api-work-items.md#t05) | **API·hook 정의, 화면 사용처 없음** · F05 |
| [op-009](#op-009) | `PUT /admin/inquiries/{inquiryId}/answer` | [T05](./api-work-items.md#t05) | **API·hook 정의, 화면 사용처 없음** · F05 |
| [op-010](#op-010) | `PATCH /admin/inquiries/{inquiryId}/status` | [T05](./api-work-items.md#t05) | **API·hook 정의, 화면 사용처 없음** · F05 |
| [op-011](#op-011) | `GET /admin/inquiries/types` | [T05](./api-work-items.md#t05) | **API·hook 정의, 화면 사용처 없음** |
| [op-012](#op-012) | `POST /admin/inquiries/types` | [T05](./api-work-items.md#t05) | **API·hook 정의, 화면 사용처 없음** · F05 |
| [op-013](#op-013) | `DELETE /admin/inquiries/types/{typeId}` | [T05](./api-work-items.md#t05) | **API·hook 정의, 화면 사용처 없음** · F05 |
| [op-014](#op-014) | `PUT /admin/inquiries/types/{typeId}` | [T05](./api-work-items.md#t05) | **API·hook 정의, 화면 사용처 없음** · F05 |
| [op-015](#op-015) | `GET /admin/items` | [T09](./api-work-items.md#t09) | **화면 호출 연결 확인** |
| [op-016](#op-016) | `POST /admin/items` | [T09](./api-work-items.md#t09) | **화면 호출 연결 확인** · F09 |
| [op-017](#op-017) | `DELETE /admin/items/{itemId}` | [T09](./api-work-items.md#t09) | **화면 호출 연결 확인** |
| [op-018](#op-018) | `GET /admin/items/{itemId}` | [T09](./api-work-items.md#t09) | **화면 호출 연결 확인** |
| [op-019](#op-019) | `PATCH /admin/items/{itemId}` | [T09](./api-work-items.md#t09) | **화면 호출 연결 확인** |
| [op-020](#op-020) | `DELETE /admin/items/{itemId}/image` | [T09](./api-work-items.md#t09) | **화면 호출 연결 확인** |
| [op-021](#op-021) | `PATCH /admin/items/batch` | [T09](./api-work-items.md#t09) | **화면 호출 연결 확인** |
| [op-022](#op-022) | `GET /admin/items/categories` | [T09](./api-work-items.md#t09) | **화면 호출 연결 확인** |
| [op-023](#op-023) | `POST /admin/items/categories` | [T09](./api-work-items.md#t09) | **화면 호출 연결 확인** |
| [op-024](#op-024) | `DELETE /admin/items/categories/{categoryId}` | [T09](./api-work-items.md#t09) | **화면 호출 연결 확인** |
| [op-025](#op-025) | `PATCH /admin/items/categories/{categoryId}` | [T09](./api-work-items.md#t09) | **화면 호출 연결 확인** |
| [op-026](#op-026) | `GET /admin/items/latest/id` | [T09](./api-work-items.md#t09) | **API·hook 정의, 화면 사용처 없음** |
| [op-027](#op-027) | `PATCH /admin/items/toggle/event/reward/{itemId}` | [T09](./api-work-items.md#t09) | **화면 호출 연결 확인** |
| [op-028](#op-028) | `POST /admin/items/upload` | [T09](./api-work-items.md#t09) | **화면 호출 연결 확인** |
| [op-029](#op-029) | `GET /admin/news` | [T08](./api-work-items.md#t08) | **화면 호출 연결 확인** · F08 |
| [op-030](#op-030) | `POST /admin/news` | [T08](./api-work-items.md#t08) | **화면 호출 연결 확인** · F08 |
| [op-031](#op-031) | `DELETE /admin/news/{newsId}` | [T08](./api-work-items.md#t08) | **화면 호출 연결 확인** · F08 |
| [op-032](#op-032) | `GET /admin/news/{newsId}` | [T08](./api-work-items.md#t08) | **화면 호출 연결 확인** · F08 |
| [op-033](#op-033) | `PATCH /admin/news/{newsId}` | [T08](./api-work-items.md#t08) | **화면 호출 연결 확인** · F08 |
| [op-034](#op-034) | `GET /admin/news/{newsId}/comments` | [T08](./api-work-items.md#t08) | **일치 호출 없음** · F08 |
| [op-035](#op-035) | `DELETE /admin/news/{newsId}/comments/{commentId}` | [T08](./api-work-items.md#t08) | **일치 호출 없음** · F08 |
| [op-036](#op-036) | `PATCH /admin/news/batch` | [T08](./api-work-items.md#t08) | **일치 호출 없음** · F08 |
| [op-037](#op-037) | `GET /admin/parcels` | [T11](./api-work-items.md#t11) | **API·hook 정의, 화면 사용처 없음** · F10 |
| [op-038](#op-038) | `POST /admin/parcels` | [T11](./api-work-items.md#t11) | **API·hook 정의, 화면 사용처 없음** |
| [op-039](#op-039) | `GET /admin/parcels/export` | [T11](./api-work-items.md#t11) | **API·hook 정의, 화면 사용처 없음** |
| [op-040](#op-040) | `GET /admin/usage/item` | [T03](./api-work-items.md#t03) | **API·hook 정의, 화면 사용처 없음** · F03 |
| [op-041](#op-041) | `GET /admin/usage/point` | [T03](./api-work-items.md#t03) | **API·hook 정의, 화면 사용처 없음** · F03 |
| [op-042](#op-042) | `GET /admin/users/{userId}` | [T02](./api-work-items.md#t02) | **API·hook 정의, 화면 사용처 없음** · F02 |
| [op-043](#op-043) | `POST /admin/users/{userId}/authorities` | [T02](./api-work-items.md#t02) | **API·hook 정의, 화면 사용처 없음** · F05 |
| [op-044](#op-044) | `POST /admin/users/{userId}/points` | [T02](./api-work-items.md#t02) | **API·hook 정의, 화면 사용처 없음** · F02 |
| [op-045](#op-045) | `PATCH /admin/users/{userId}/status` | [T02](./api-work-items.md#t02) | **API·hook 정의, 화면 사용처 없음** |
| [op-046](#op-046) | `GET /admin/users/withdrawals` | [T02](./api-work-items.md#t02) | **API·hook 정의, 화면 사용처 없음** |
| [op-047](#op-047) | `GET /admin/video` | [T04](./api-work-items.md#t04) | **API·hook 정의, 화면 사용처 없음** |
| [op-048](#op-048) | `POST /admin/video` | [T04](./api-work-items.md#t04) | **API·hook 정의, 화면 사용처 없음** · F04 |
| [op-049](#op-049) | `DELETE /admin/video/{videoId}` | [T04](./api-work-items.md#t04) | **API·hook 정의, 화면 사용처 없음** |
| [op-050](#op-050) | `GET /admin/video/{videoId}` | [T04](./api-work-items.md#t04) | **API·hook 정의, 화면 사용처 없음** |
| [op-051](#op-051) | `PATCH /admin/video/{videoId}` | [T04](./api-work-items.md#t04) | **API·hook 정의, 화면 사용처 없음** · F04 |
| [op-052](#op-052) | `POST /admin/video/{videoId}/thumbnail` | [T04](./api-work-items.md#t04) | **API·hook 정의, 화면 사용처 없음** |
| [op-053](#op-053) | `GET /admin/video/playlists` | [T04](./api-work-items.md#t04) | **API·hook 정의, 화면 사용처 없음** |
| [op-054](#op-054) | `POST /admin/video/playlists` | [T04](./api-work-items.md#t04) | **API·hook 정의, 화면 사용처 없음** |
| [op-055](#op-055) | `DELETE /admin/video/playlists/{playlistId}` | [T04](./api-work-items.md#t04) | **API·hook 정의, 화면 사용처 없음** |
| [op-056](#op-056) | `GET /admin/video/playlists/{playlistId}` | [T04](./api-work-items.md#t04) | **API·hook 정의, 화면 사용처 없음** |
| [op-057](#op-057) | `PATCH /admin/video/playlists/{playlistId}` | [T04](./api-work-items.md#t04) | **API·hook 정의, 화면 사용처 없음** |
| [op-058](#op-058) | `POST /auth/login` | [T06](./api-work-items.md#t06) | **화면 호출 연결 확인** |
| [op-059](#op-059) | `GET /citizen/proposals` | [T01](./api-work-items.md#t01) | **화면 호출 연결 확인** · F01 |
| [op-060](#op-060) | `GET /citizen/proposals/{proposalId}` | [T01](./api-work-items.md#t01) | **화면 호출 연결 확인** · F01 |
| [op-061](#op-061) | `PATCH /citizen/proposals/{proposalId}` | [T01](./api-work-items.md#t01) | **일치 호출 없음** · F01 |
| [op-062](#op-062) | `PATCH /citizen/proposals/{proposalId}/review-result` | [T01](./api-work-items.md#t01) | **일치 호출 없음** · F01 |
| [op-063](#op-063) | `GET /citizen/proposals/summary` | [T01](./api-work-items.md#t01) | **일치 호출 없음** · F01 |
| [op-064](#op-064) | `GET /citizen/votes` | [T01](./api-work-items.md#t01) | **화면 호출 연결 확인** |
| [op-065](#op-065) | `GET /citizen/votes/{voteId}` | [T01](./api-work-items.md#t01) | **화면 호출 연결 확인** |
| [op-066](#op-066) | `GET /citizen/votes/summary` | [T01](./api-work-items.md#t01) | **일치 호출 없음** |
| [op-067](#op-067) | `GET /events/attendance` | [T10](./api-work-items.md#t10) | **화면 호출 연결 확인** |
| [op-068](#op-068) | `POST /events/attendance` | [T10](./api-work-items.md#t10) | **화면 호출 연결 확인** |
| [op-069](#op-069) | `GET /events/attendance/{eventId}` | [T10](./api-work-items.md#t10) | **화면 호출 연결 확인** |
| [op-070](#op-070) | `PATCH /events/attendance/{eventId}` | [T10](./api-work-items.md#t10) | **화면 호출 연결 확인** |
| [op-071](#op-071) | `PATCH /events/attendance/{eventId}/configs` | [T10](./api-work-items.md#t10) | **화면 호출 연결 확인** |
| [op-072](#op-072) | `POST /events/attendance/{eventId}/configs/upload` | [T10](./api-work-items.md#t10) | **화면 호출 연결 확인** |
| [op-073](#op-073) | `GET /events/attendance/{eventId}/items` | [T10](./api-work-items.md#t10) | **API·hook 정의, 화면 사용처 없음** |
| [op-074](#op-074) | `PUT /events/attendance/{eventId}/items` | [T10](./api-work-items.md#t10) | **화면 호출 연결 확인** |
| [op-075](#op-075) | `GET /events/roulette` | [T10](./api-work-items.md#t10) | **화면 호출 연결 확인** |
| [op-076](#op-076) | `POST /events/roulette` | [T10](./api-work-items.md#t10) | **화면 호출 연결 확인** |
| [op-077](#op-077) | `GET /events/roulette/{eventId}` | [T10](./api-work-items.md#t10) | **화면 호출 연결 확인** |
| [op-078](#op-078) | `PATCH /events/roulette/{eventId}` | [T10](./api-work-items.md#t10) | **화면 호출 연결 확인** |
| [op-079](#op-079) | `PATCH /events/roulette/{eventId}/configs` | [T10](./api-work-items.md#t10) | **화면 호출 연결 확인** |
| [op-080](#op-080) | `POST /events/roulette/{eventId}/configs/upload` | [T10](./api-work-items.md#t10) | **화면 호출 연결 확인** |
| [op-081](#op-081) | `GET /events/roulette/{eventId}/items` | [T10](./api-work-items.md#t10) | **API·hook 정의, 화면 사용처 없음** |
| [op-082](#op-082) | `PUT /events/roulette/{eventId}/items` | [T10](./api-work-items.md#t10) | **화면 호출 연결 확인** |
| [op-083](#op-083) | `GET /external/dashboard/daily` | [T12](./api-work-items.md#t12) | **일치 호출 없음** |
| [op-084](#op-084) | `GET /external/dashboard/monthly` | [T12](./api-work-items.md#t12) | **일치 호출 없음** |
| [op-085](#op-085) | `GET /external/dashboard/summary` | [T12](./api-work-items.md#t12) | **일치 호출 없음** |
| [op-086](#op-086) | `GET /external/dashboard/weekly` | [T12](./api-work-items.md#t12) | **일치 호출 없음** |
| [op-087](#op-087) | `GET /health` | [T13](./api-work-items.md#t13) | **일치 호출 없음** |
| [op-088](#op-088) | `GET /maintenance` | [T07](./api-work-items.md#t07) | **기존 경로·계약 불일치** · F07 |
| [op-089](#op-089) | `PATCH /maintenance` | [T07](./api-work-items.md#t07) | **기존 경로·계약 불일치** · F07 |
| [op-090](#op-090) | `PATCH /maintenance/off` | [T07](./api-work-items.md#t07) | **일치 호출 없음** · F07 |
| [op-091](#op-091) | `PATCH /maintenance/on` | [T07](./api-work-items.md#t07) | **일치 호출 없음** · F07 |
| [op-092](#op-092) | `GET /maintenance/one` | [T07](./api-work-items.md#t07) | **일치 호출 없음** · F07 |
| [op-093](#op-093) | `PATCH /maintenance/time` | [T07](./api-work-items.md#t07) | **일치 호출 없음** · F07 |
| [op-094](#op-094) | `PATCH /maintenance/version` | [T07](./api-work-items.md#t07) | **일치 호출 없음** · F07 |
| [op-095](#op-095) | `GET /me` | [T06](./api-work-items.md#t06) | **일치 호출 없음** · F06 |
| [op-096](#op-096) | `GET /me/menus` | [T06](./api-work-items.md#t06) | **API만 정의** · F06 |
| [op-097](#op-097) | `GET /menus` | [T06](./api-work-items.md#t06) | **API만 정의** · F06 |
| [op-098](#op-098) | `PATCH /menus/{menuId}` | [T06](./api-work-items.md#t06) | **일치 호출 없음** |
| [op-099](#op-099) | `PUT /menus/order` | [T06](./api-work-items.md#t06) | **일치 호출 없음** |
| [op-100](#op-100) | `GET /permissions` | [T06](./api-work-items.md#t06) | **일치 호출 없음** |
| [op-101](#op-101) | `GET /roles` | [T06](./api-work-items.md#t06) | **일치 호출 없음** |
| [op-102](#op-102) | `POST /roles` | [T06](./api-work-items.md#t06) | **일치 호출 없음** |
| [op-103](#op-103) | `DELETE /roles/{roleId}` | [T06](./api-work-items.md#t06) | **일치 호출 없음** |
| [op-104](#op-104) | `GET /roles/{roleId}` | [T06](./api-work-items.md#t06) | **일치 호출 없음** |
| [op-105](#op-105) | `PATCH /roles/{roleId}` | [T06](./api-work-items.md#t06) | **일치 호출 없음** |
| [op-106](#op-106) | `PUT /roles/{roleId}/permissions` | [T06](./api-work-items.md#t06) | **일치 호출 없음** |

<a id="op-001"></a>

## GET /accounts

- 기능: getAccounts
- operationId: `getAccounts`; tag: `account-controller`
- 현재 상태: **일치 호출 없음**
- 인계 작업: [T06](./api-work-items.md#t06)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| query | `query` | 예 | [GetAccountListRequest](./api-schema-catalog.md#schema-getaccountlistrequest) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "query",
    "in": "query",
    "required": true,
    "schema": {
      "$ref": "#/components/schemas/GetAccountListRequest"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponsePageResponseAccountResponse](./api-schema-catalog.md#schema-apiresponsepageresponseaccountresponse)
- data payload: [PageResponseAccountResponse](./api-schema-catalog.md#schema-pageresponseaccountresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponsePageResponseAccountResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-002"></a>

## PUT /accounts/{adminId}/roles

- 기능: updateRoles
- operationId: `updateRoles`; tag: `account-controller`
- 현재 상태: **일치 호출 없음**
- 인계 작업: [T06](./api-work-items.md#t06)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `adminId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "adminId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/UpdateAccountRolesRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [UpdateAccountRolesRequest](./api-schema-catalog.md#schema-updateaccountrolesrequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-003"></a>

## GET /admin/audit

- 기능: 관리자 전체 활동 내역 조회
- operationId: `getAdminAllAuditLog`; tag: `활동 내역`
- 현재 상태: **일치 호출 없음**
- 인계 작업: [T13](./api-work-items.md#t13)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

관리자 전체 활동 내역을 조회하는데 사용, 반환 값으로는 id, 서비스명, 처리내용, 작업자, 작업일을 준다.
정렬은 createdAt, id desc 를 기본적용이고 createdAt과 id 가 아닌경우 400 반환.


일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| query | `page` | 아니오/미기재 | `integer` | One-based page index (1..N) |
| query | `size` | 아니오/미기재 | `integer` | The size of the page to be returned |
| query | `sort` | 아니오/미기재 | 배열&lt;`string`&gt; | Sorting criteria in the format: property,(asc\|desc). Default sort order is ascending. Multiple sort criteria are supported. |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "page",
    "in": "query",
    "description": "One-based page index (1..N)",
    "required": false,
    "schema": {
      "type": "integer",
      "default": 1,
      "minimum": 0
    }
  },
  {
    "name": "size",
    "in": "query",
    "description": "The size of the page to be returned",
    "required": false,
    "schema": {
      "type": "integer",
      "default": 20,
      "minimum": 1
    }
  },
  {
    "name": "sort",
    "in": "query",
    "description": "Sorting criteria in the format: property,(asc|desc). Default sort order is ascending. Multiple sort criteria are supported.",
    "required": false,
    "schema": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponsePageResponseGetAdminAllAuditLogResponse](./api-schema-catalog.md#schema-apiresponsepageresponsegetadminallauditlogresponse)
- data payload: [PageResponseGetAdminAllAuditLogResponse](./api-schema-catalog.md#schema-pageresponsegetadminallauditlogresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponsePageResponseGetAdminAllAuditLogResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-004"></a>

## GET /admin/inquiries

- 기능: 문의 목록 조회
- operationId: `getInquiries`; tag: `문의하기`
- 현재 상태: **API·hook 정의, 화면 사용처 없음**
- 인계 작업: [T05](./api-work-items.md#t05)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/inquiries/api/inquiry.api.ts:35](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.api.ts:35) — `getList`

같은 API 디렉터리의 DTO/parser 재사용 후보: [inquiry.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.dto.ts), [inquiry-type.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.parser.ts), [inquiry-type.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.dto.ts), [inquiry.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| query | `status` | 아니오/미기재 | `OPEN / IN_PROGRESS / COMPLETED` | — |
| query | `typeId` | 아니오/미기재 | `integer` (int64) | — |
| query | `by` | 아니오/미기재 | `TITLE / TITLE_CONTENT` | — |
| query | `keyword` | 아니오/미기재 | `string` | — |
| query | `page` | 아니오/미기재 | `integer` | One-based page index (1..N) |
| query | `size` | 아니오/미기재 | `integer` | The size of the page to be returned |
| query | `sort` | 아니오/미기재 | 배열&lt;`string`&gt; | Sorting criteria in the format: property,(asc\|desc). Default sort order is ascending. Multiple sort criteria are supported. |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "status",
    "in": "query",
    "required": false,
    "schema": {
      "type": "string",
      "enum": [
        "OPEN",
        "IN_PROGRESS",
        "COMPLETED"
      ]
    }
  },
  {
    "name": "typeId",
    "in": "query",
    "required": false,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  },
  {
    "name": "by",
    "in": "query",
    "required": false,
    "schema": {
      "type": "string",
      "enum": [
        "TITLE",
        "TITLE_CONTENT"
      ]
    }
  },
  {
    "name": "keyword",
    "in": "query",
    "required": false,
    "schema": {
      "type": "string"
    }
  },
  {
    "name": "page",
    "in": "query",
    "description": "One-based page index (1..N)",
    "required": false,
    "schema": {
      "type": "integer",
      "default": 1,
      "minimum": 0
    }
  },
  {
    "name": "size",
    "in": "query",
    "description": "The size of the page to be returned",
    "required": false,
    "schema": {
      "type": "integer",
      "default": 20,
      "minimum": 1
    }
  },
  {
    "name": "sort",
    "in": "query",
    "description": "Sorting criteria in the format: property,(asc|desc). Default sort order is ascending. Multiple sort criteria are supported.",
    "required": false,
    "schema": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponsePageResponseInquirySummaryResponse](./api-schema-catalog.md#schema-apiresponsepageresponseinquirysummaryresponse)
- data payload: [PageResponseInquirySummaryResponse](./api-schema-catalog.md#schema-pageresponseinquirysummaryresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponsePageResponseInquirySummaryResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-005"></a>

## DELETE /admin/inquiries/{inquiryId}

- 기능: 문의 삭제
- operationId: `deleteInquiry`; tag: `문의하기`
- 현재 상태: **API·hook 정의, 화면 사용처 없음** · F05
- 인계 작업: [T05](./api-work-items.md#t05)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/inquiries/api/inquiry.api.ts:41](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.api.ts:41) — `deleteInquiry`

같은 API 디렉터리의 DTO/parser 재사용 후보: [inquiry.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.dto.ts), [inquiry-type.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.parser.ts), [inquiry-type.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.dto.ts), [inquiry.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `inquiryId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "inquiryId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-006"></a>

## GET /admin/inquiries/{inquiryId}

- 기능: 문의 상세 조회
- operationId: `getInquiry`; tag: `문의하기`
- 현재 상태: **API·hook 정의, 화면 사용처 없음**
- 인계 작업: [T05](./api-work-items.md#t05)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/inquiries/api/inquiry.api.ts:38](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.api.ts:38) — `getDetail`

같은 API 디렉터리의 DTO/parser 재사용 후보: [inquiry.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.dto.ts), [inquiry-type.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.parser.ts), [inquiry-type.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.dto.ts), [inquiry.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `inquiryId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "inquiryId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseInquiryDetailResponse](./api-schema-catalog.md#schema-apiresponseinquirydetailresponse)
- data payload: [InquiryDetailResponse](./api-schema-catalog.md#schema-inquirydetailresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseInquiryDetailResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-007"></a>

## DELETE /admin/inquiries/{inquiryId}/answer

- 기능: 문의 답변 삭제
- operationId: `deleteInquiryAnswer`; tag: `문의하기`
- 현재 상태: **API·hook 정의, 화면 사용처 없음** · F05
- 인계 작업: [T05](./api-work-items.md#t05)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/inquiries/api/inquiry.api.ts:65](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.api.ts:65) — `deleteInquiryAnswer`

같은 API 디렉터리의 DTO/parser 재사용 후보: [inquiry.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.dto.ts), [inquiry-type.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.parser.ts), [inquiry-type.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.dto.ts), [inquiry.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `inquiryId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "inquiryId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-008"></a>

## POST /admin/inquiries/{inquiryId}/answer

- 기능: 문의 답변 등록
- operationId: `createInquiryAnswer`; tag: `문의하기`
- 현재 상태: **API·hook 정의, 화면 사용처 없음** · F05
- 인계 작업: [T05](./api-work-items.md#t05)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/inquiries/api/inquiry.api.ts:51](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.api.ts:51) — `postInquiryAnswer`

같은 API 디렉터리의 DTO/parser 재사용 후보: [inquiry.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.dto.ts), [inquiry-type.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.parser.ts), [inquiry-type.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.dto.ts), [inquiry.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `inquiryId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "inquiryId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/InquiryAnswerRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [InquiryAnswerRequest](./api-schema-catalog.md#schema-inquiryanswerrequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-009"></a>

## PUT /admin/inquiries/{inquiryId}/answer

- 기능: 문의 답변 수정
- operationId: `updateInquiryAnswer`; tag: `문의하기`
- 현재 상태: **API·hook 정의, 화면 사용처 없음** · F05
- 인계 작업: [T05](./api-work-items.md#t05)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/inquiries/api/inquiry.api.ts:58](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.api.ts:58) — `putInquiryAnswer`

같은 API 디렉터리의 DTO/parser 재사용 후보: [inquiry.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.dto.ts), [inquiry-type.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.parser.ts), [inquiry-type.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.dto.ts), [inquiry.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `inquiryId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "inquiryId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/InquiryAnswerRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [InquiryAnswerRequest](./api-schema-catalog.md#schema-inquiryanswerrequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-010"></a>

## PATCH /admin/inquiries/{inquiryId}/status

- 기능: 문의 상태 변경
- operationId: `updateInquiryStatus`; tag: `문의하기`
- 현재 상태: **API·hook 정의, 화면 사용처 없음** · F05
- 인계 작업: [T05](./api-work-items.md#t05)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/inquiries/api/inquiry.api.ts:44](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.api.ts:44) — `patchInquiryStatus`

같은 API 디렉터리의 DTO/parser 재사용 후보: [inquiry.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.dto.ts), [inquiry-type.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.parser.ts), [inquiry-type.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.dto.ts), [inquiry.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `inquiryId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "inquiryId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/UpdateInquiryStatusRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [UpdateInquiryStatusRequest](./api-schema-catalog.md#schema-updateinquirystatusrequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-011"></a>

## GET /admin/inquiries/types

- 기능: 문의 타입 조회
- operationId: `getInquiryType`; tag: `문의하기`
- 현재 상태: **API·hook 정의, 화면 사용처 없음**
- 인계 작업: [T05](./api-work-items.md#t05)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/inquiries/api/inquiry-type.api.ts:32](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.api.ts:32) — `getList`

같은 API 디렉터리의 DTO/parser 재사용 후보: [inquiry.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.dto.ts), [inquiry-type.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.parser.ts), [inquiry-type.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.dto.ts), [inquiry.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| query | `pageable` | 예 | [Pageable](./api-schema-catalog.md#schema-pageable) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "pageable",
    "in": "query",
    "required": true,
    "schema": {
      "$ref": "#/components/schemas/Pageable"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponsePageResponseGetInquiryTypeResponse](./api-schema-catalog.md#schema-apiresponsepageresponsegetinquirytyperesponse)
- data payload: [PageResponseGetInquiryTypeResponse](./api-schema-catalog.md#schema-pageresponsegetinquirytyperesponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponsePageResponseGetInquiryTypeResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-012"></a>

## POST /admin/inquiries/types

- 기능: 문의 타입 등록
- operationId: `createInquiryType`; tag: `문의하기`
- 현재 상태: **API·hook 정의, 화면 사용처 없음** · F05
- 인계 작업: [T05](./api-work-items.md#t05)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/inquiries/api/inquiry-type.api.ts:35](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.api.ts:35) — `postType`

같은 API 디렉터리의 DTO/parser 재사용 후보: [inquiry.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.dto.ts), [inquiry-type.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.parser.ts), [inquiry-type.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.dto.ts), [inquiry.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.parser.ts).

### 요청

path/query/header parameter 정의 없음.

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/CreateInquiryTypeRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [CreateInquiryTypeRequest](./api-schema-catalog.md#schema-createinquirytyperequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-013"></a>

## DELETE /admin/inquiries/types/{typeId}

- 기능: 문의 타입 삭제
- operationId: `deleteInquiryType`; tag: `문의하기`
- 현재 상태: **API·hook 정의, 화면 사용처 없음** · F05
- 인계 작업: [T05](./api-work-items.md#t05)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/inquiries/api/inquiry-type.api.ts:45](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.api.ts:45) — `deleteType`

같은 API 디렉터리의 DTO/parser 재사용 후보: [inquiry.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.dto.ts), [inquiry-type.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.parser.ts), [inquiry-type.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.dto.ts), [inquiry.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `typeId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "typeId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-014"></a>

## PUT /admin/inquiries/types/{typeId}

- 기능: 문의 타입 수정
- operationId: `updateInquiryType`; tag: `문의하기`
- 현재 상태: **API·hook 정의, 화면 사용처 없음** · F05
- 인계 작업: [T05](./api-work-items.md#t05)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/inquiries/api/inquiry-type.api.ts:38](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.api.ts:38) — `putType`

같은 API 디렉터리의 DTO/parser 재사용 후보: [inquiry.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.dto.ts), [inquiry-type.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.parser.ts), [inquiry-type.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.dto.ts), [inquiry.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `typeId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "typeId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/UpdateInquiryTypeRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [UpdateInquiryTypeRequest](./api-schema-catalog.md#schema-updateinquirytyperequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-015"></a>

## GET /admin/items

- 기능: 아이템 목록 조회
- operationId: `getItems`; tag: `아이템`
- 현재 상태: **화면 호출 연결 확인**
- 인계 작업: [T09](./api-work-items.md#t09)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/items/api/items.api.ts:42](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:42) — `getList`

같은 API 디렉터리의 DTO/parser 재사용 후보: [items.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.parser.ts), [item.category.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item.category.dto.ts), [item-category.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item-category.parser.ts), [items.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| query | `req` | 예 | [GetItemsRequest](./api-schema-catalog.md#schema-getitemsrequest) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "req",
    "in": "query",
    "required": true,
    "schema": {
      "$ref": "#/components/schemas/GetItemsRequest"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponsePageResponseGetItemSummaryResponse](./api-schema-catalog.md#schema-apiresponsepageresponsegetitemsummaryresponse)
- data payload: [PageResponseGetItemSummaryResponse](./api-schema-catalog.md#schema-pageresponsegetitemsummaryresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponsePageResponseGetItemSummaryResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-016"></a>

## POST /admin/items

- 기능: 아이템 생성
- operationId: `createItem`; tag: `아이템`
- 현재 상태: **화면 호출 연결 확인** · F09
- 인계 작업: [T09](./api-work-items.md#t09)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/items/api/items.api.ts:51](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:51) — `postItem`

같은 API 디렉터리의 DTO/parser 재사용 후보: [items.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.parser.ts), [item.category.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item.category.dto.ts), [item-category.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item-category.parser.ts), [items.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.dto.ts).

### 요청

path/query/header parameter 정의 없음.

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/CreateItemRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [CreateItemRequest](./api-schema-catalog.md#schema-createitemrequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseCreateItemResponse](./api-schema-catalog.md#schema-apiresponsecreateitemresponse)
- data payload: [CreateItemResponse](./api-schema-catalog.md#schema-createitemresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseCreateItemResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-017"></a>

## DELETE /admin/items/{itemId}

- 기능: 아이템 삭제
- operationId: `deleteItem`; tag: `아이템`
- 현재 상태: **화면 호출 연결 확인**
- 인계 작업: [T09](./api-work-items.md#t09)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/items/api/items.api.ts:57](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:57) — `deleteItem`

같은 API 디렉터리의 DTO/parser 재사용 후보: [items.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.parser.ts), [item.category.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item.category.dto.ts), [item-category.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item-category.parser.ts), [items.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `itemId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "itemId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-018"></a>

## GET /admin/items/{itemId}

- 기능: 아이템 상세 조회
- operationId: `getItem`; tag: `아이템`
- 현재 상태: **화면 호출 연결 확인**
- 인계 작업: [T09](./api-work-items.md#t09)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/items/api/items.api.ts:45](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:45) — `getDetail`

같은 API 디렉터리의 DTO/parser 재사용 후보: [items.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.parser.ts), [item.category.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item.category.dto.ts), [item-category.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item-category.parser.ts), [items.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `itemId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "itemId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseGetItemDetailResponse](./api-schema-catalog.md#schema-apiresponsegetitemdetailresponse)
- data payload: [GetItemDetailResponse](./api-schema-catalog.md#schema-getitemdetailresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseGetItemDetailResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-019"></a>

## PATCH /admin/items/{itemId}

- 기능: 아이템 수정
- operationId: `updateItem`; tag: `아이템`
- 현재 상태: **화면 호출 연결 확인**
- 인계 작업: [T09](./api-work-items.md#t09)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/items/api/items.api.ts:54](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:54) — `patchItem`

같은 API 디렉터리의 DTO/parser 재사용 후보: [items.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.parser.ts), [item.category.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item.category.dto.ts), [item-category.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item-category.parser.ts), [items.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `itemId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "itemId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/UpdateItemRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [UpdateItemRequest](./api-schema-catalog.md#schema-updateitemrequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseUpdateItemResponse](./api-schema-catalog.md#schema-apiresponseupdateitemresponse)
- data payload: [UpdateItemResponse](./api-schema-catalog.md#schema-updateitemresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseUpdateItemResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-020"></a>

## DELETE /admin/items/{itemId}/image

- 기능: 아이템 이미지 삭제
- operationId: `deleteItemImage`; tag: `아이템`
- 현재 상태: **화면 호출 연결 확인**
- 인계 작업: [T09](./api-work-items.md#t09)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/items/api/items.api.ts:78](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:78) — `deleteImage`

같은 API 디렉터리의 DTO/parser 재사용 후보: [items.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.parser.ts), [item.category.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item.category.dto.ts), [item-category.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item-category.parser.ts), [items.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `itemId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "itemId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-021"></a>

## PATCH /admin/items/batch

- 기능: 여러 아이템 상태 변경
- operationId: `updateItemsListStatus`; tag: `아이템`
- 현재 상태: **화면 호출 연결 확인**
- 인계 작업: [T09](./api-work-items.md#t09)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/items/api/items.api.ts:75](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:75) — `patchBatchStatus`

같은 API 디렉터리의 DTO/parser 재사용 후보: [items.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.parser.ts), [item.category.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item.category.dto.ts), [item-category.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item-category.parser.ts), [items.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.dto.ts).

### 요청

path/query/header parameter 정의 없음.

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/UpdateItemsListStatusRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [UpdateItemsListStatusRequest](./api-schema-catalog.md#schema-updateitemsliststatusrequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-022"></a>

## GET /admin/items/categories

- 기능: 아이템 카테고리 조회
- operationId: `getItemCategories`; tag: `아이템 카테고리`
- 현재 상태: **화면 호출 연결 확인**
- 인계 작업: [T09](./api-work-items.md#t09)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/items/api/item-category.api.ts:31](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item-category.api.ts:31) — `getList`

같은 API 디렉터리의 DTO/parser 재사용 후보: [items.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.parser.ts), [item.category.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item.category.dto.ts), [item-category.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item-category.parser.ts), [items.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.dto.ts).

### 요청

path/query/header parameter 정의 없음.

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseListGetItemCategoryResponse](./api-schema-catalog.md#schema-apiresponselistgetitemcategoryresponse)
- data payload: 배열&lt;[GetItemCategoryResponse](./api-schema-catalog.md#schema-getitemcategoryresponse)&gt;

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseListGetItemCategoryResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-023"></a>

## POST /admin/items/categories

- 기능: 아이템 카테고리 생성
- operationId: `createItemCategory`; tag: `아이템 카테고리`
- 현재 상태: **화면 호출 연결 확인**
- 인계 작업: [T09](./api-work-items.md#t09)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/items/api/item-category.api.ts:34](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item-category.api.ts:34) — `postCategory`

같은 API 디렉터리의 DTO/parser 재사용 후보: [items.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.parser.ts), [item.category.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item.category.dto.ts), [item-category.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item-category.parser.ts), [items.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.dto.ts).

### 요청

path/query/header parameter 정의 없음.

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/CreateItemCategoryRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [CreateItemCategoryRequest](./api-schema-catalog.md#schema-createitemcategoryrequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-024"></a>

## DELETE /admin/items/categories/{categoryId}

- 기능: 아이템 카테고리 삭제
- operationId: `deleteItemCategory`; tag: `아이템 카테고리`
- 현재 상태: **화면 호출 연결 확인**
- 인계 작업: [T09](./api-work-items.md#t09)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/items/api/item-category.api.ts:44](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item-category.api.ts:44) — `deleteCategory`

같은 API 디렉터리의 DTO/parser 재사용 후보: [items.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.parser.ts), [item.category.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item.category.dto.ts), [item-category.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item-category.parser.ts), [items.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `categoryId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "categoryId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-025"></a>

## PATCH /admin/items/categories/{categoryId}

- 기능: 아이템 카테고리 수정
- operationId: `updateItemCategory`; tag: `아이템 카테고리`
- 현재 상태: **화면 호출 연결 확인**
- 인계 작업: [T09](./api-work-items.md#t09)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/items/api/item-category.api.ts:37](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item-category.api.ts:37) — `patchCategory`

같은 API 디렉터리의 DTO/parser 재사용 후보: [items.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.parser.ts), [item.category.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item.category.dto.ts), [item-category.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item-category.parser.ts), [items.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `categoryId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "categoryId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/UpdateItemCategoryRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [UpdateItemCategoryRequest](./api-schema-catalog.md#schema-updateitemcategoryrequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-026"></a>

## GET /admin/items/latest/id

- 기능: 아이템 최신 아이디 조회
- operationId: `getItemLatestId`; tag: `아이템`
- 현재 상태: **API·hook 정의, 화면 사용처 없음**
- 인계 작업: [T09](./api-work-items.md#t09)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/items/api/items.api.ts:48](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:48) — `getLatestId`

같은 API 디렉터리의 DTO/parser 재사용 후보: [items.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.parser.ts), [item.category.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item.category.dto.ts), [item-category.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item-category.parser.ts), [items.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| query | `req` | 예 | [GetItemLatestIdRequest](./api-schema-catalog.md#schema-getitemlatestidrequest) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "req",
    "in": "query",
    "required": true,
    "schema": {
      "$ref": "#/components/schemas/GetItemLatestIdRequest"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseLong](./api-schema-catalog.md#schema-apiresponselong)
- data payload: `integer` (int64)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseLong"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-027"></a>

## PATCH /admin/items/toggle/event/reward/{itemId}

- 기능: 아이템 이벤트 리워드 노출 토글
- operationId: `toggleEventRewardItem`; tag: `아이템`
- 현재 상태: **화면 호출 연결 확인**
- 인계 작업: [T09](./api-work-items.md#t09)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/items/api/items.api.ts:72](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:72) — `toggleEventReward`

같은 API 디렉터리의 DTO/parser 재사용 후보: [items.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.parser.ts), [item.category.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item.category.dto.ts), [item-category.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item-category.parser.ts), [items.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `itemId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "itemId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseBoolean](./api-schema-catalog.md#schema-apiresponseboolean)
- data payload: `boolean`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseBoolean"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-028"></a>

## POST /admin/items/upload

- 기능: 아이템 이미지 업로드
- operationId: `uploadItemImage`; tag: `아이템`
- 현재 상태: **화면 호출 연결 확인**
- 인계 작업: [T09](./api-work-items.md#t09)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/items/api/items.api.ts:64](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:64) — `uploadImage`

같은 API 디렉터리의 DTO/parser 재사용 후보: [items.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.parser.ts), [item.category.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item.category.dto.ts), [item-category.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item-category.parser.ts), [items.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| query | `subCategoryId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "subCategoryId",
    "in": "query",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "multipart/form-data": {
      "schema": {
        "type": "object",
        "properties": {
          "file": {
            "type": "string",
            "format": "binary"
          }
        },
        "required": [
          "file"
        ]
      }
    }
  }
}
```

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseUploadItemImageResponse](./api-schema-catalog.md#schema-apiresponseuploaditemimageresponse)
- data payload: [UploadItemImageResponse](./api-schema-catalog.md#schema-uploaditemimageresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseUploadItemImageResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-029"></a>

## GET /admin/news

- 기능: 공지사항 목록 조회
- operationId: `listNews`; tag: `공지사항`
- 현재 상태: **화면 호출 연결 확인** · F08
- 인계 작업: [T08](./api-work-items.md#t08)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

공지사항 목록을 조회한다. 상단고정 공지사항은 페이지네이션과 무관하게 항상 먼저 노출된다.

실제 API 호출:

- [src/entities/news/api/news.api.ts:32](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/news/api/news.api.ts:32) — `getList`

같은 API 디렉터리의 DTO/parser 재사용 후보: [news.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/news/api/news.parser.ts), [news.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/news/api/news.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| query | `type` | 아니오/미기재 | `ANNOUNCEMENT / UPDATE / EVENT / ETC` | 공지사항 타입 지정, 지정 타입 외 요청시 INVALID_REQUEST 400 |
| query | `status` | 아니오/미기재 | `DRAFT / PUBLISHED / ARCHIVED` | 공지사항 상태 지정, 지정 타입 외 요청시 INVALID_REQUEST 400 |
| query | `by` | 아니오/미기재 | `TITLE / TITLE_CONTENT` | 검색 범위 지정, 지정 타입 외 요청시 INVALID_REQUEST 400 |
| query | `keyword` | 아니오/미기재 | `string` | 검색 키워드 지정 |
| query | `page` | 아니오/미기재 | `integer` | One-based page index (1..N) |
| query | `size` | 아니오/미기재 | `integer` | The size of the page to be returned |
| query | `sort` | 아니오/미기재 | 배열&lt;`string`&gt; | Sorting criteria in the format: property,(asc\|desc). Default sort order is ascending. Multiple sort criteria are supported. |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "type",
    "in": "query",
    "description": "공지사항 타입 지정, 지정 타입 외 요청시 INVALID_REQUEST 400",
    "required": false,
    "schema": {
      "type": "string",
      "enum": [
        "ANNOUNCEMENT",
        "UPDATE",
        "EVENT",
        "ETC"
      ]
    },
    "example": "EVENT"
  },
  {
    "name": "status",
    "in": "query",
    "description": "공지사항 상태 지정, 지정 타입 외 요청시 INVALID_REQUEST 400",
    "required": false,
    "schema": {
      "type": "string",
      "enum": [
        "DRAFT",
        "PUBLISHED",
        "ARCHIVED"
      ]
    },
    "example": "DRAFT"
  },
  {
    "name": "by",
    "in": "query",
    "description": "검색 범위 지정, 지정 타입 외 요청시 INVALID_REQUEST 400",
    "required": false,
    "schema": {
      "type": "string",
      "enum": [
        "TITLE",
        "TITLE_CONTENT"
      ]
    },
    "example": "TITLE"
  },
  {
    "name": "keyword",
    "in": "query",
    "description": "검색 키워드 지정",
    "required": false,
    "schema": {
      "type": "string"
    },
    "example": "제목"
  },
  {
    "name": "page",
    "in": "query",
    "description": "One-based page index (1..N)",
    "required": false,
    "schema": {
      "type": "integer",
      "default": 1,
      "minimum": 0
    }
  },
  {
    "name": "size",
    "in": "query",
    "description": "The size of the page to be returned",
    "required": false,
    "schema": {
      "type": "integer",
      "default": 20,
      "minimum": 1
    }
  },
  {
    "name": "sort",
    "in": "query",
    "description": "Sorting criteria in the format: property,(asc|desc). Default sort order is ascending. Multiple sort criteria are supported.",
    "required": false,
    "schema": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

성공

- 미디어 타입: `application/json`
- schema: [NewsApiResponseList](./api-schema-catalog.md#schema-newsapiresponselist)
- data payload: [NewsListResponse](./api-schema-catalog.md#schema-newslistresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/NewsApiResponseList"
  },
  "examples": {
    "SUCCESS": {
      "summary": "성공",
      "description": "SUCCESS",
      "value": {
        "code": "SUCCESS",
        "message": "성공",
        "data": {
          "items": [
            {
              "id": 1,
              "type": "ANNOUNCEMENT",
              "title": "공지사항 제목",
              "viewCount": 10,
              "status": "PUBLISHED",
              "isPinned": true,
              "createdAt": "2026-08-01T00:00:00Z",
              "deletedAt": null
            }
          ],
          "total": 1,
          "page": 1,
          "size": 20,
          "isPinnedCount": 1
        }
      }
    }
  }
}
```

### 오류 응답

#### HTTP 400

```json
{
  "description": "요청 조건이 잘못된 경우 400 에러를 반환한다",
  "content": {
    "application/json": {
      "examples": {
        "byKeywordMismatch": {
          "summary": "by/keyword 중 하나만 입력",
          "description": "byKeywordMismatch",
          "value": {
            "code": "NEWS_INVALID_BY_KEYWORD",
            "message": "검색타입과 키워드 입력시 둘 다 입력해야합니다.",
            "data": null
          }
        },
        "invalidSortProperty": {
          "summary": "지원하지 않는 정렬 조건",
          "description": "invalidSortProperty",
          "value": {
            "code": "INVALID_SORT_PROPERTY",
            "message": "지원하지 않는 정렬 조건입니다.",
            "data": null
          }
        }
      }
    }
  }
}
```
#### HTTP 401

```json
{
  "description": "토큰이 없거나 만료·위조된 경우 401 에러를 반환한다",
  "content": {
    "application/json": {
      "examples": {
        "expiredToken": {
          "summary": "토큰만료",
          "description": "expiredToken",
          "value": {
            "code": "EXPIRED_TOKEN",
            "message": "만료된 토큰입니다.",
            "data": null
          }
        },
        "invalidToken": {
          "summary": "토큰 위조/형식 오류",
          "description": "invalidToken",
          "value": {
            "code": "INVALID_TOKEN",
            "message": "유효하지 않은 토큰입니다.",
            "data": null
          }
        }
      }
    }
  }
}
```

<a id="op-030"></a>

## POST /admin/news

- 기능: 공지사항 등록
- operationId: `createNews`; tag: `공지사항`
- 현재 상태: **화면 호출 연결 확인** · F08
- 인계 작업: [T08](./api-work-items.md#t08)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

공지사항(알림, 업데이트. 이벤트, 기타)을 생성, isPinned를 이용해 상단고정을 설정할 수 있다.


실제 API 호출:

- [src/entities/news/api/news.api.ts:42](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/news/api/news.api.ts:42) — `postNews`

같은 API 디렉터리의 DTO/parser 재사용 후보: [news.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/news/api/news.parser.ts), [news.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/news/api/news.dto.ts).

### 요청

path/query/header parameter 정의 없음.

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/CreateNewsRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [CreateNewsRequest](./api-schema-catalog.md#schema-createnewsrequest).

### 성공 응답

#### HTTP 201

성공

- 미디어 타입: `application/json`
- schema: [NewsApiResponseVoid](./api-schema-catalog.md#schema-newsapiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/NewsApiResponseVoid"
  },
  "examples": {
    "SUCCESS": {
      "summary": "성공",
      "description": "SUCCESS",
      "value": {
        "code": "SUCCESS",
        "message": "성공",
        "data": null
      }
    }
  }
}
```

### 오류 응답

#### HTTP 400

```json
{
  "description": "필수 요청 데이터 미입력시 400 에러 반환",
  "content": {
    "application/json": {
      "examples": {
        "RequiredFieldEmpty": {
          "summary": "필수 데이터 미입력",
          "description": "RequiredFieldEmpty",
          "value": {
            "code": "INVALID_REQUEST",
            "message": "요청이 올바르지 않습니다",
            "data": [
              {
                "field": "title",
                "reason": "제목을 입력하세요."
              },
              {
                "field": "content",
                "reason": "내용을 입력하세요."
              },
              {
                "field": "type",
                "reason": "공지사항 종류를 선택하세요."
              },
              {
                "field": "status",
                "reason": "공지사항 상태를 선택하세요."
              },
              {
                "field": "isPinned",
                "reason": "상단고정여부를 선택하세요."
              }
            ]
          }
        }
      }
    }
  }
}
```
#### HTTP 401

```json
{
  "description": "토큰이 없거나 만료·위조된 경우 401 에러를 반환한다",
  "content": {
    "application/json": {
      "examples": {
        "expiredToken": {
          "summary": "토큰만료",
          "description": "expiredToken",
          "value": {
            "code": "EXPIRED_TOKEN",
            "message": "만료된 토큰입니다.",
            "data": null
          }
        },
        "invalidToken": {
          "summary": "토큰 위조/형식 오류",
          "description": "invalidToken",
          "value": {
            "code": "INVALID_TOKEN",
            "message": "유효하지 않은 토큰입니다.",
            "data": null
          }
        }
      }
    }
  }
}
```

<a id="op-031"></a>

## DELETE /admin/news/{newsId}

- 기능: 공지사항 삭제
- operationId: `deleteNews`; tag: `공지사항`
- 현재 상태: **화면 호출 연결 확인** · F08
- 인계 작업: [T08](./api-work-items.md#t08)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

공지사항을 soft delete 처리한다.

실제 API 호출:

- [src/entities/news/api/news.api.ts:52](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/news/api/news.api.ts:52) — `deleteNews`

같은 API 디렉터리의 DTO/parser 재사용 후보: [news.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/news/api/news.parser.ts), [news.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/news/api/news.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `newsId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "newsId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

성공

- 미디어 타입: `application/json`
- schema: [NewsApiResponseVoid](./api-schema-catalog.md#schema-newsapiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/NewsApiResponseVoid"
  },
  "examples": {
    "SUCCESS": {
      "summary": "성공",
      "description": "SUCCESS",
      "value": {
        "code": "SUCCESS",
        "message": "성공",
        "data": null
      }
    }
  }
}
```

### 오류 응답

#### HTTP 401

```json
{
  "description": "토큰이 없거나 만료·위조된 경우 401 에러를 반환한다",
  "content": {
    "application/json": {
      "examples": {
        "expiredToken": {
          "summary": "토큰만료",
          "description": "expiredToken",
          "value": {
            "code": "EXPIRED_TOKEN",
            "message": "만료된 토큰입니다.",
            "data": null
          }
        },
        "invalidToken": {
          "summary": "토큰 위조/형식 오류",
          "description": "invalidToken",
          "value": {
            "code": "INVALID_TOKEN",
            "message": "유효하지 않은 토큰입니다.",
            "data": null
          }
        }
      }
    }
  }
}
```
#### HTTP 404

```json
{
  "description": "존재하지 않거나 이미 삭제된 newsId인 경우 404 에러를 반환한다",
  "content": {
    "application/json": {
      "examples": {
        "newsNotFound": {
          "summary": "존재하지 않는 공지사항",
          "description": "newsNotFound",
          "value": {
            "code": "NEWS_NOT_FOUND",
            "message": "뉴스를 찾을 수 없습니다.",
            "data": null
          }
        }
      }
    }
  }
}
```

<a id="op-032"></a>

## GET /admin/news/{newsId}

- 기능: 공지사항 상세 조회
- operationId: `getNews`; tag: `공지사항`
- 현재 상태: **화면 호출 연결 확인** · F08
- 인계 작업: [T08](./api-work-items.md#t08)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

공지사항 상세를 조회한다.

실제 API 호출:

- [src/entities/news/api/news.api.ts:39](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/news/api/news.api.ts:39) — `getDetail`

같은 API 디렉터리의 DTO/parser 재사용 후보: [news.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/news/api/news.parser.ts), [news.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/news/api/news.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `newsId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "newsId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

성공

- 미디어 타입: `application/json`
- schema: [NewsApiResponseDetail](./api-schema-catalog.md#schema-newsapiresponsedetail)
- data payload: [NewsDetailResponse](./api-schema-catalog.md#schema-newsdetailresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/NewsApiResponseDetail"
  },
  "examples": {
    "SUCCESS": {
      "summary": "성공",
      "description": "SUCCESS",
      "value": {
        "code": "SUCCESS",
        "message": "성공",
        "data": {
          "id": 1,
          "type": "ANNOUNCEMENT",
          "status": "PUBLISHED",
          "title": "공지사항 제목",
          "content": "공지사항 내용",
          "isPinned": true,
          "viewCount": 10,
          "createdAt": "2026-08-01T00:00:00Z",
          "updatedAt": "2026-08-01T00:00:00Z"
        }
      }
    }
  }
}
```

### 오류 응답

#### HTTP 401

```json
{
  "description": "토큰이 없거나 만료·위조된 경우 401 에러를 반환한다",
  "content": {
    "application/json": {
      "examples": {
        "expiredToken": {
          "summary": "토큰만료",
          "description": "expiredToken",
          "value": {
            "code": "EXPIRED_TOKEN",
            "message": "만료된 토큰입니다.",
            "data": null
          }
        },
        "invalidToken": {
          "summary": "토큰 위조/형식 오류",
          "description": "invalidToken",
          "value": {
            "code": "INVALID_TOKEN",
            "message": "유효하지 않은 토큰입니다.",
            "data": null
          }
        }
      }
    }
  }
}
```
#### HTTP 404

```json
{
  "description": "존재하지 않거나 삭제된 newsId인 경우 404 에러를 반환한다",
  "content": {
    "application/json": {
      "examples": {
        "newsNotFound": {
          "summary": "존재하지 않는 공지사항",
          "description": "newsNotFound",
          "value": {
            "code": "NEWS_NOT_FOUND",
            "message": "뉴스를 찾을 수 없습니다.",
            "data": null
          }
        }
      }
    }
  }
}
```

<a id="op-033"></a>

## PATCH /admin/news/{newsId}

- 기능: 공지사항 수정
- operationId: `updateNews`; tag: `공지사항`
- 현재 상태: **화면 호출 연결 확인** · F08
- 인계 작업: [T08](./api-work-items.md#t08)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

공지사항 상세를 수정한다. 요청에 입력된 필드만 반영되고, 입력하지 않은 필드는 기존 값이 유지된다.

실제 API 호출:

- [src/entities/news/api/news.api.ts:45](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/news/api/news.api.ts:45) — `patchNews`

같은 API 디렉터리의 DTO/parser 재사용 후보: [news.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/news/api/news.parser.ts), [news.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/news/api/news.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `newsId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "newsId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/UpdateNewsRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [UpdateNewsRequest](./api-schema-catalog.md#schema-updatenewsrequest).

### 성공 응답

#### HTTP 200

성공

- 미디어 타입: `application/json`
- schema: [NewsApiResponseVoid](./api-schema-catalog.md#schema-newsapiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/NewsApiResponseVoid"
  },
  "examples": {
    "SUCCESS": {
      "summary": "성공",
      "description": "SUCCESS",
      "value": {
        "code": "SUCCESS",
        "message": "성공",
        "data": null
      }
    }
  }
}
```

### 오류 응답

#### HTTP 401

```json
{
  "description": "토큰이 없거나 만료·위조된 경우 401 에러를 반환한다",
  "content": {
    "application/json": {
      "examples": {
        "expiredToken": {
          "summary": "토큰만료",
          "description": "expiredToken",
          "value": {
            "code": "EXPIRED_TOKEN",
            "message": "만료된 토큰입니다.",
            "data": null
          }
        },
        "invalidToken": {
          "summary": "토큰 위조/형식 오류",
          "description": "invalidToken",
          "value": {
            "code": "INVALID_TOKEN",
            "message": "유효하지 않은 토큰입니다.",
            "data": null
          }
        }
      }
    }
  }
}
```
#### HTTP 404

```json
{
  "description": "존재하지 않거나 삭제된 newsId인 경우 404 에러를 반환한다",
  "content": {
    "application/json": {
      "examples": {
        "newsNotFound": {
          "summary": "존재하지 않는 공지사항",
          "description": "newsNotFound",
          "value": {
            "code": "NEWS_NOT_FOUND",
            "message": "뉴스를 찾을 수 없습니다.",
            "data": null
          }
        }
      }
    }
  }
}
```

<a id="op-034"></a>

## GET /admin/news/{newsId}/comments

- 기능: 공지사항 댓글 목록 조회
- operationId: `listNewsComments`; tag: `공지사항`
- 현재 상태: **일치 호출 없음** · F08
- 인계 작업: [T08](./api-work-items.md#t08)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

공지사항의 댓글 목록을 조회한다.

일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `newsId` | 예 | `integer` (int64) | — |
| query | `page` | 아니오/미기재 | `integer` | One-based page index (1..N) |
| query | `size` | 아니오/미기재 | `integer` | The size of the page to be returned |
| query | `sort` | 아니오/미기재 | 배열&lt;`string`&gt; | Sorting criteria in the format: property,(asc\|desc). Default sort order is ascending. Multiple sort criteria are supported. |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "newsId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  },
  {
    "name": "page",
    "in": "query",
    "description": "One-based page index (1..N)",
    "required": false,
    "schema": {
      "type": "integer",
      "default": 1,
      "minimum": 0
    }
  },
  {
    "name": "size",
    "in": "query",
    "description": "The size of the page to be returned",
    "required": false,
    "schema": {
      "type": "integer",
      "default": 20,
      "minimum": 1
    }
  },
  {
    "name": "sort",
    "in": "query",
    "description": "Sorting criteria in the format: property,(asc|desc). Default sort order is ascending. Multiple sort criteria are supported.",
    "required": false,
    "schema": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

성공

- 미디어 타입: `application/json`
- schema: [NewsApiResponseCommentList](./api-schema-catalog.md#schema-newsapiresponsecommentlist)
- data payload: [PageResponseNewsCommentResponse](./api-schema-catalog.md#schema-pageresponsenewscommentresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/NewsApiResponseCommentList"
  },
  "examples": {
    "SUCCESS": {
      "summary": "성공",
      "description": "SUCCESS",
      "value": {
        "code": "SUCCESS",
        "message": "성공",
        "data": {
          "items": [
            {
              "id": 1,
              "content": "댓글 내용",
              "createdAt": "2026-08-01T00:00:00Z",
              "updatedAt": "2026-08-01T00:00:00Z",
              "deletedAt": null,
              "deletedBy": null,
              "userId": 10,
              "userNickname": "닉네임"
            }
          ],
          "total": 1,
          "page": 1,
          "size": 20
        }
      }
    }
  }
}
```

### 오류 응답

#### HTTP 400

```json
{
  "description": "page/size 미입력시 400 에러를 반환한다",
  "content": {
    "application/json": {
      "examples": {
        "pageSizeEmpty": {
          "summary": "page/size 미입력",
          "description": "pageSizeEmpty",
          "value": {
            "code": "INVALID_REQUEST",
            "message": "요청이 올바르지 않습니다",
            "data": [
              {
                "field": "page",
                "reason": "널이어서는 안됩니다"
              },
              {
                "field": "size",
                "reason": "널이어서는 안됩니다"
              }
            ]
          }
        }
      }
    }
  }
}
```
#### HTTP 401

```json
{
  "description": "토큰이 없거나 만료·위조된 경우 401 에러를 반환한다",
  "content": {
    "application/json": {
      "examples": {
        "expiredToken": {
          "summary": "토큰만료",
          "description": "expiredToken",
          "value": {
            "code": "EXPIRED_TOKEN",
            "message": "만료된 토큰입니다.",
            "data": null
          }
        },
        "invalidToken": {
          "summary": "토큰 위조/형식 오류",
          "description": "invalidToken",
          "value": {
            "code": "INVALID_TOKEN",
            "message": "유효하지 않은 토큰입니다.",
            "data": null
          }
        }
      }
    }
  }
}
```
#### HTTP 404

```json
{
  "description": "존재하지 않거나 삭제된 newsId인 경우 404 에러를 반환한다",
  "content": {
    "application/json": {
      "examples": {
        "newsNotFound": {
          "summary": "존재하지 않는 공지사항",
          "description": "newsNotFound",
          "value": {
            "code": "NEWS_NOT_FOUND",
            "message": "뉴스를 찾을 수 없습니다.",
            "data": null
          }
        }
      }
    }
  }
}
```

<a id="op-035"></a>

## DELETE /admin/news/{newsId}/comments/{commentId}

- 기능: 공지사항 댓글 삭제
- operationId: `deleteNewsComment`; tag: `공지사항`
- 현재 상태: **일치 호출 없음** · F08
- 인계 작업: [T08](./api-work-items.md#t08)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

공지사항 댓글을 soft delete 처리한다. commentId가 존재하지 않거나 다른 newsId 소속이면 조용히 무시된다.

일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `newsId` | 예 | `integer` (int64) | — |
| path | `commentId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "newsId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  },
  {
    "name": "commentId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

성공

- 미디어 타입: `application/json`
- schema: [NewsApiResponseVoid](./api-schema-catalog.md#schema-newsapiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/NewsApiResponseVoid"
  },
  "examples": {
    "SUCCESS": {
      "summary": "성공",
      "description": "SUCCESS",
      "value": {
        "code": "SUCCESS",
        "message": "성공",
        "data": null
      }
    }
  }
}
```

### 오류 응답

#### HTTP 401

```json
{
  "description": "토큰이 없거나 만료·위조된 경우 401 에러를 반환한다",
  "content": {
    "application/json": {
      "examples": {
        "expiredToken": {
          "summary": "토큰만료",
          "description": "expiredToken",
          "value": {
            "code": "EXPIRED_TOKEN",
            "message": "만료된 토큰입니다.",
            "data": null
          }
        },
        "invalidToken": {
          "summary": "토큰 위조/형식 오류",
          "description": "invalidToken",
          "value": {
            "code": "INVALID_TOKEN",
            "message": "유효하지 않은 토큰입니다.",
            "data": null
          }
        }
      }
    }
  }
}
```
#### HTTP 404

```json
{
  "description": "존재하지 않거나 삭제된 newsId/newsCommentId인 경우 404 에러를 반환한다",
  "content": {
    "application/json": {
      "examples": {
        "newsNotFound": {
          "summary": "존재하지 않거나 삭제된 공지사항",
          "description": "newsNotFound",
          "value": {
            "code": "NEWS_NOT_FOUND",
            "message": "뉴스를 찾을 수 없습니다.",
            "data": null
          }
        },
        "newsCommentNotFound": {
          "summary": "존재하지 않거나 삭제된 댓글",
          "description": "newsCommentNotFound",
          "value": {
            "code": "NEWS_NOT_FOUND",
            "message": "댓글을 찾을 수 없습니다.",
            "data": null
          }
        }
      }
    }
  }
}
```

<a id="op-036"></a>

## PATCH /admin/news/batch

- 기능: 공지사항 일괄 상태 변경
- operationId: `batchUpdateNewsList`; tag: `공지사항`
- 현재 상태: **일치 호출 없음** · F08
- 인계 작업: [T08](./api-work-items.md#t08)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

여러 공지사항의 상태(status)·상단고정(isPinned)을 한 번에 변경한다. 존재하지 않는 newsId는 조용히 무시된다.

일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

path/query/header parameter 정의 없음.

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/BatchUpdateNewsListRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [BatchUpdateNewsListRequest](./api-schema-catalog.md#schema-batchupdatenewslistrequest).

### 성공 응답

#### HTTP 200

성공

- 미디어 타입: `application/json`
- schema: [NewsApiResponseVoid](./api-schema-catalog.md#schema-newsapiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/NewsApiResponseVoid"
  },
  "examples": {
    "SUCCESS": {
      "summary": "성공",
      "description": "SUCCESS",
      "value": {
        "code": "SUCCESS",
        "message": "성공",
        "data": null
      }
    }
  }
}
```

### 오류 응답

#### HTTP 400

```json
{
  "description": "newsIds가 비어있는 경우 400 에러를 반환한다",
  "content": {
    "application/json": {
      "examples": {
        "newsIdsEmpty": {
          "summary": "newsIds 미입력",
          "description": "newsIdsEmpty",
          "value": {
            "code": "INVALID_REQUEST",
            "message": "요청이 올바르지 않습니다",
            "data": [
              {
                "field": "newsIds",
                "reason": "1개 이상의 뉴스를 선택하세요."
              }
            ]
          }
        }
      }
    }
  }
}
```
#### HTTP 401

```json
{
  "description": "토큰이 없거나 만료·위조된 경우 401 에러를 반환한다",
  "content": {
    "application/json": {
      "examples": {
        "expiredToken": {
          "summary": "토큰만료",
          "description": "expiredToken",
          "value": {
            "code": "EXPIRED_TOKEN",
            "message": "만료된 토큰입니다.",
            "data": null
          }
        },
        "invalidToken": {
          "summary": "토큰 위조/형식 오류",
          "description": "invalidToken",
          "value": {
            "code": "INVALID_TOKEN",
            "message": "유효하지 않은 토큰입니다.",
            "data": null
          }
        }
      }
    }
  }
}
```

<a id="op-037"></a>

## GET /admin/parcels

- 기능: 우편 내역 확인
- operationId: `getParcelHistory`; tag: `소포 관리`
- 현재 상태: **API·hook 정의, 화면 사용처 없음** · F10
- 인계 작업: [T11](./api-work-items.md#t11)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

발송한 우편을 최신순(createdAt desc, id desc)으로 조회한다.
page는 1부터 시작하고 생략 시 1, size는 생략 시 20이며 100을 넘으면 100으로 잘린다.
sort는 createdAt/id만 허용하고 그 밖이면 400이다. recipient는 받는사람 닉네임 부분일치 필터다.

실제 API 호출:

- [src/entities/parcels/api/parcel.api.ts:27](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/parcels/api/parcel.api.ts:27) — `getList`

같은 API 디렉터리의 DTO/parser 재사용 후보: [parcel.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/parcels/api/parcel.parser.ts), [parcel.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/parcels/api/parcel.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| query | `recipient` | 아니오/미기재 | `string` | 받는사람 닉네임 부분일치 |
| query | `page` | 아니오/미기재 | `integer` | One-based page index (1..N) |
| query | `size` | 아니오/미기재 | `integer` | The size of the page to be returned |
| query | `sort` | 아니오/미기재 | 배열&lt;`string`&gt; | Sorting criteria in the format: property,(asc\|desc). Default sort order is ascending. Multiple sort criteria are supported. |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "recipient",
    "in": "query",
    "description": "받는사람 닉네임 부분일치",
    "required": false,
    "schema": {
      "type": "string"
    },
    "example": "김영희"
  },
  {
    "name": "page",
    "in": "query",
    "description": "One-based page index (1..N)",
    "required": false,
    "schema": {
      "type": "integer",
      "default": 1,
      "minimum": 0
    }
  },
  {
    "name": "size",
    "in": "query",
    "description": "The size of the page to be returned",
    "required": false,
    "schema": {
      "type": "integer",
      "default": 20,
      "minimum": 1
    }
  },
  {
    "name": "sort",
    "in": "query",
    "description": "Sorting criteria in the format: property,(asc|desc). Default sort order is ascending. Multiple sort criteria are supported.",
    "required": false,
    "schema": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

조회 성공, 결과가 없으면 items는 빈 배열

- 미디어 타입: `application/json`
- schema: [ApiResponsePageResponseParcelHistoryResponse](./api-schema-catalog.md#schema-apiresponsepageresponseparcelhistoryresponse)
- data payload: [PageResponseParcelHistoryResponse](./api-schema-catalog.md#schema-pageresponseparcelhistoryresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponsePageResponseParcelHistoryResponse"
  },
  "examples": {
    "firstPage": {
      "description": "firstPage",
      "value": {
        "code": "SUCCESS",
        "message": "성공",
        "data": {
          "items": [
            {
              "id": 42,
              "recipient": "김영희",
              "sentAt": "2026-09-01T00:00:00Z",
              "content": "9월 출석 이벤트 참여 보상으로 지급되었습니다.",
              "reason": "출석 이벤트 보상"
            }
          ],
          "total": 1,
          "page": 1,
          "size": 20
        }
      }
    }
  }
}
```

### 오류 응답

#### HTTP 400

```json
{
  "description": "허용 목록 밖 정렬",
  "content": {
    "application/json": {
      "examples": {
        "invalidSort": {
          "description": "invalidSort",
          "value": {
            "code": "INVALID_SORT_PROPERTY",
            "message": "지원하지 않는 정렬 조건입니다.",
            "data": null
          }
        }
      }
    }
  }
}
```
#### HTTP 401

```json
{
  "description": "토큰 만료/위조",
  "content": {
    "application/json": {
      "examples": {
        "expiredToken": {
          "description": "expiredToken",
          "value": {
            "code": "EXPIRED_TOKEN",
            "message": "만료된 토큰입니다.",
            "data": null
          }
        },
        "invalidToken": {
          "description": "invalidToken",
          "value": {
            "code": "INVALID_TOKEN",
            "message": "유효하지 않은 토큰입니다.",
            "data": null
          }
        }
      }
    }
  }
}
```

<a id="op-038"></a>

## POST /admin/parcels

- 기능: 우편 보내기
- operationId: `sendParcel`; tag: `소포 관리`
- 현재 상태: **API·hook 정의, 화면 사용처 없음**
- 인계 작업: [T11](./api-work-items.md#t11)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

받는 사용자에게 아이템을 지급하는 우편을 발송한다.
userId는 활성 사용자여야 하며 탈퇴·부재 시 404다. itemId가 없으면 404다.
amount는 1 이상이어야 한다.

실제 API 호출:

- [src/entities/parcels/api/parcel.api.ts:37](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/parcels/api/parcel.api.ts:37) — `send`

같은 API 디렉터리의 DTO/parser 재사용 후보: [parcel.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/parcels/api/parcel.parser.ts), [parcel.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/parcels/api/parcel.dto.ts).

### 요청

path/query/header parameter 정의 없음.

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/SendParcelRequest"
      },
      "examples": {
        "send": {
          "description": "send",
          "value": {
            "title": "출석 이벤트 보상",
            "content": "9월 출석 이벤트 참여 보상으로 지급되었습니다.",
            "userId": 7,
            "itemId": 100001,
            "amount": 3
          }
        }
      }
    }
  },
  "required": true
}
```

요청 DTO: [SendParcelRequest](./api-schema-catalog.md#schema-sendparcelrequest).

### 성공 응답

#### HTTP 200

발송 성공

- 미디어 타입: `application/json`
- schema: [ApiResponse](./api-schema-catalog.md#schema-apiresponse)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponse"
  },
  "examples": {
    "success": {
      "description": "success",
      "value": {
        "code": "SUCCESS",
        "message": "성공",
        "data": null
      }
    }
  }
}
```

### 오류 응답

#### HTTP 400

```json
{
  "description": "필수 값 누락 또는 수량이 1 미만",
  "content": {
    "application/json": {
      "examples": {
        "invalidRequest": {
          "description": "invalidRequest",
          "value": {
            "code": "INVALID_REQUEST",
            "message": "요청이 올바르지 않습니다.",
            "data": null
          }
        }
      }
    }
  }
}
```
#### HTTP 401

```json
{
  "description": "토큰 만료/위조",
  "content": {
    "application/json": {
      "examples": {
        "expiredToken": {
          "description": "expiredToken",
          "value": {
            "code": "EXPIRED_TOKEN",
            "message": "만료된 토큰입니다.",
            "data": null
          }
        },
        "invalidToken": {
          "description": "invalidToken",
          "value": {
            "code": "INVALID_TOKEN",
            "message": "유효하지 않은 토큰입니다.",
            "data": null
          }
        }
      }
    }
  }
}
```
#### HTTP 404

```json
{
  "description": "받는 사용자 또는 아이템을 찾을 수 없음",
  "content": {
    "application/json": {
      "examples": {
        "userNotFound": {
          "summary": "없는/탈퇴 사용자",
          "description": "userNotFound",
          "value": {
            "code": "USER_NOT_FOUND",
            "message": "사용자를 찾을 수 없습니다.",
            "data": null
          }
        },
        "itemNotFound": {
          "summary": "없는 아이템",
          "description": "itemNotFound",
          "value": {
            "code": "ITEM_NOT_FOUND",
            "message": "아이템을 찾을 수 없습니다.",
            "data": null
          }
        }
      }
    }
  }
}
```

<a id="op-039"></a>

## GET /admin/parcels/export

- 기능: 우편 발송 내역 엑셀 출력
- operationId: `exportParcelHistory`; tag: `소포 관리`
- 현재 상태: **API·hook 정의, 화면 사용처 없음**
- 인계 작업: [T11](./api-work-items.md#t11)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

목록과 같은 recipient 필터로 전체를 xlsx 하나에 담아 내려준다 (페이지 없음).

실제 API 호출:

- [src/entities/parcels/api/parcel.api.ts:40](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/parcels/api/parcel.api.ts:40) — `exportHistory`

같은 API 디렉터리의 DTO/parser 재사용 후보: [parcel.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/parcels/api/parcel.parser.ts), [parcel.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/parcels/api/parcel.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| query | `recipient` | 아니오/미기재 | `string` | 받는사람 닉네임 부분일치 |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "recipient",
    "in": "query",
    "description": "받는사람 닉네임 부분일치",
    "required": false,
    "schema": {
      "type": "string"
    },
    "example": "김영희"
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: `string` (byte)
- data payload: envelope/data 구조 미지정 또는 직접 응답

```json
{
  "schema": {
    "type": "string",
    "format": "byte"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-040"></a>

## GET /admin/usage/item

- 기능: getItemHistoryList
- operationId: `getItemHistoryList`; tag: `이용내역`
- 현재 상태: **API·hook 정의, 화면 사용처 없음** · F03
- 인계 작업: [T03](./api-work-items.md#t03)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/usage/api/admin-usage.api.ts:28](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/usage/api/admin-usage.api.ts:28) — `getItemList`

같은 API 디렉터리의 DTO/parser 재사용 후보: [usage.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/usage/api/usage.dto.ts), [admin-usage.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/usage/api/admin-usage.dto.ts), [admin-usage.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/usage/api/admin-usage.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| query | `query` | 예 | [GetItemHistoryListRequest](./api-schema-catalog.md#schema-getitemhistorylistrequest) | — |
| query | `page` | 아니오/미기재 | `integer` | One-based page index (1..N) |
| query | `size` | 아니오/미기재 | `integer` | The size of the page to be returned |
| query | `sort` | 아니오/미기재 | 배열&lt;`string`&gt; | Sorting criteria in the format: property,(asc\|desc). Default sort order is ascending. Multiple sort criteria are supported. |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "query",
    "in": "query",
    "required": true,
    "schema": {
      "$ref": "#/components/schemas/GetItemHistoryListRequest"
    }
  },
  {
    "name": "page",
    "in": "query",
    "description": "One-based page index (1..N)",
    "required": false,
    "schema": {
      "type": "integer",
      "default": 1,
      "minimum": 0
    }
  },
  {
    "name": "size",
    "in": "query",
    "description": "The size of the page to be returned",
    "required": false,
    "schema": {
      "type": "integer",
      "default": 20,
      "minimum": 1
    }
  },
  {
    "name": "sort",
    "in": "query",
    "description": "Sorting criteria in the format: property,(asc|desc). Default sort order is ascending. Multiple sort criteria are supported.",
    "required": false,
    "schema": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponsePageResponseItemHistoryResponse](./api-schema-catalog.md#schema-apiresponsepageresponseitemhistoryresponse)
- data payload: [PageResponseItemHistoryResponse](./api-schema-catalog.md#schema-pageresponseitemhistoryresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponsePageResponseItemHistoryResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-041"></a>

## GET /admin/usage/point

- 기능: getPointHistoryList
- operationId: `getPointHistoryList`; tag: `이용내역`
- 현재 상태: **API·hook 정의, 화면 사용처 없음** · F03
- 인계 작업: [T03](./api-work-items.md#t03)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/usage/api/admin-usage.api.ts:18](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/usage/api/admin-usage.api.ts:18) — `getPointList`

같은 API 디렉터리의 DTO/parser 재사용 후보: [usage.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/usage/api/usage.dto.ts), [admin-usage.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/usage/api/admin-usage.dto.ts), [admin-usage.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/usage/api/admin-usage.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| query | `query` | 예 | [GetPointHistoryListRequest](./api-schema-catalog.md#schema-getpointhistorylistrequest) | — |
| query | `page` | 아니오/미기재 | `integer` | One-based page index (1..N) |
| query | `size` | 아니오/미기재 | `integer` | The size of the page to be returned |
| query | `sort` | 아니오/미기재 | 배열&lt;`string`&gt; | Sorting criteria in the format: property,(asc\|desc). Default sort order is ascending. Multiple sort criteria are supported. |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "query",
    "in": "query",
    "required": true,
    "schema": {
      "$ref": "#/components/schemas/GetPointHistoryListRequest"
    }
  },
  {
    "name": "page",
    "in": "query",
    "description": "One-based page index (1..N)",
    "required": false,
    "schema": {
      "type": "integer",
      "default": 1,
      "minimum": 0
    }
  },
  {
    "name": "size",
    "in": "query",
    "description": "The size of the page to be returned",
    "required": false,
    "schema": {
      "type": "integer",
      "default": 20,
      "minimum": 1
    }
  },
  {
    "name": "sort",
    "in": "query",
    "description": "Sorting criteria in the format: property,(asc|desc). Default sort order is ascending. Multiple sort criteria are supported.",
    "required": false,
    "schema": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponsePageResponsePointHistoryResponse](./api-schema-catalog.md#schema-apiresponsepageresponsepointhistoryresponse)
- data payload: [PageResponsePointHistoryResponse](./api-schema-catalog.md#schema-pageresponsepointhistoryresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponsePageResponsePointHistoryResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-042"></a>

## GET /admin/users/{userId}

- 기능: 사용자 조회
- operationId: `getAdminUser`; tag: `사용자 관리`
- 현재 상태: **API·hook 정의, 화면 사용처 없음** · F02
- 인계 작업: [T02](./api-work-items.md#t02)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

탈퇴한 사용자도 조회된다 (status가 WITHDRAWN, 응답은 동일 스키마).

실제 API 호출:

- [src/entities/users/api/admin-users.api.ts:35](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.api.ts:35) — `getDetail`

같은 API 디렉터리의 DTO/parser 재사용 후보: [admin-users.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.parser.ts), [admin-users.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.dto.ts), [users.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/users.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `userId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "userId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

조회 성공

- 미디어 타입: `application/json`
- schema: [ApiResponseAdminUserResponse](./api-schema-catalog.md#schema-apiresponseadminuserresponse)
- data payload: [AdminUserResponse](./api-schema-catalog.md#schema-adminuserresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseAdminUserResponse"
  },
  "example": {
    "code": "SUCCESS",
    "message": "성공",
    "data": {
      "publicId": "9e0d0000-0000-4000-8000-000000009001",
      "nickname": "홍길동",
      "status": "ACTIVE",
      "createdAt": "2026-08-18T12:00:00Z",
      "updatedAt": "2026-08-20T09:30:00Z"
    }
  }
}
```

### 오류 응답

#### HTTP 401

```json
{
  "description": "토큰 만료/위조",
  "content": {
    "application/json": {
      "examples": {
        "expiredToken": {
          "description": "expiredToken",
          "value": {
            "code": "EXPIRED_TOKEN",
            "message": "만료된 토큰입니다.",
            "data": null
          }
        },
        "invalidToken": {
          "description": "invalidToken",
          "value": {
            "code": "INVALID_TOKEN",
            "message": "유효하지 않은 토큰입니다.",
            "data": null
          }
        }
      }
    }
  }
}
```
#### HTTP 404

```json
{
  "description": "존재하지 않는 사용자",
  "content": {
    "application/json": {
      "example": {
        "code": "USER_NOT_FOUND",
        "message": "사용자를 찾을 수 없습니다.",
        "data": null
      }
    }
  }
}
```

<a id="op-043"></a>

## POST /admin/users/{userId}/authorities

- 기능: 사용자 권한(시민증, 역할) 부여
- operationId: `grantAuthority`; tag: `사용자 관리`
- 현재 상태: **API·hook 정의, 화면 사용처 없음** · F05
- 인계 작업: [T02](./api-work-items.md#t02)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

아직 미구현. 현재는 200 no-op이다.

실제 API 호출:

- [src/entities/users/api/admin-users.api.ts:53](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.api.ts:53) — `postUserAuthorities`

같은 API 디렉터리의 DTO/parser 재사용 후보: [admin-users.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.parser.ts), [admin-users.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.dto.ts), [users.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/users.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `userId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "userId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/GrantUserAuthorityRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [GrantUserAuthorityRequest](./api-schema-catalog.md#schema-grantuserauthorityrequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-044"></a>

## POST /admin/users/{userId}/points

- 기능: 사용자 포인트 지급/차감
- operationId: `adjustUserPoint`; tag: `사용자 관리`
- 현재 상태: **API·hook 정의, 화면 사용처 없음** · F02
- 인계 작업: [T02](./api-work-items.md#t02)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

direction이 방향을 가르고 amount는 크기(양수)만 담는다. 차감 결과가 음수면 409.

실제 API 호출:

- [src/entities/users/api/admin-users.api.ts:45](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.api.ts:45) — `postUserPoints`

같은 API 디렉터리의 DTO/parser 재사용 후보: [admin-users.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.parser.ts), [admin-users.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.dto.ts), [users.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/users.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `userId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "userId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/AdjustUserPointRequest"
      },
      "examples": {
        "recharge": {
          "summary": "지급",
          "description": "recharge",
          "value": {
            "amount": 1000,
            "direction": "RECHARGE",
            "reason": "이벤트 보상 수동 지급"
          }
        },
        "deduct": {
          "summary": "차감",
          "description": "deduct",
          "value": {
            "amount": 500,
            "direction": "DEDUCT",
            "reason": "오지급 회수"
          }
        }
      }
    }
  },
  "required": true
}
```

요청 DTO: [AdjustUserPointRequest](./api-schema-catalog.md#schema-adjustuserpointrequest).

### 성공 응답

#### HTTP 200

처리 성공

- 미디어 타입: `application/json`
- schema: 미기재
- data payload: envelope/data 구조 미지정 또는 직접 응답

```json
{
  "example": {
    "code": "SUCCESS",
    "message": "성공",
    "data": null
  }
}
```

### 오류 응답

#### HTTP 400

```json
{
  "description": "필수 값 누락 또는 amount가 0 이하",
  "content": {
    "application/json": {
      "example": {
        "code": "INVALID_REQUEST",
        "message": "요청이 올바르지 않습니다.",
        "data": null
      }
    }
  }
}
```
#### HTTP 404

```json
{
  "description": "존재하지 않는 사용자 / 탈퇴한 사용자",
  "content": {
    "application/json": {
      "examples": {
        "notFound": {
          "description": "notFound",
          "value": {
            "code": "USER_NOT_FOUND",
            "message": "사용자를 찾을 수 없습니다.",
            "data": null
          }
        },
        "withdrawn": {
          "description": "withdrawn",
          "value": {
            "code": "USER_WITHDRAWN",
            "message": "탈퇴한 사용자입니다.",
            "data": null
          }
        }
      }
    }
  }
}
```
#### HTTP 409

```json
{
  "description": "차감액이 잔액을 초과",
  "content": {
    "application/json": {
      "example": {
        "code": "USER_POINT_INSUFFICIENT",
        "message": "차감할 포인트가 잔액을 초과합니다.",
        "data": null
      }
    }
  }
}
```

<a id="op-045"></a>

## PATCH /admin/users/{userId}/status

- 기능: 사용자 상태 수정(정상/정지)
- operationId: `updateUserStatus`; tag: `사용자 관리`
- 현재 상태: **API·hook 정의, 화면 사용처 없음**
- 인계 작업: [T02](./api-work-items.md#t02)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

정상(ACTIVE) ↔ 정지(SUSPEND) 토글. 탈퇴는 시민 본인이 하므로 이 경로에 없다. 이미 그 상태면 409. 정지 시 user_suspend 이력을 남긴다.

실제 API 호출:

- [src/entities/users/api/admin-users.api.ts:60](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.api.ts:60) — `patchUserStatus`

같은 API 디렉터리의 DTO/parser 재사용 후보: [admin-users.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.parser.ts), [admin-users.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.dto.ts), [users.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/users.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `userId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "userId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/UpdateUserStatusRequest"
      },
      "examples": {
        "suspend": {
          "summary": "정지",
          "description": "suspend",
          "value": {
            "status": "SUSPEND",
            "reason": "커뮤니티 규정 위반"
          }
        },
        "active": {
          "summary": "정지 해제",
          "description": "active",
          "value": {
            "status": "ACTIVE"
          }
        }
      }
    }
  },
  "required": true
}
```

요청 DTO: [UpdateUserStatusRequest](./api-schema-catalog.md#schema-updateuserstatusrequest).

### 성공 응답

#### HTTP 200

변경 성공

- 미디어 타입: `application/json`
- schema: 미기재
- data payload: envelope/data 구조 미지정 또는 직접 응답

```json
{
  "example": {
    "code": "SUCCESS",
    "message": "성공",
    "data": null
  }
}
```

### 오류 응답

#### HTTP 400

```json
{
  "description": "status 누락 또는 목록에 없는 값",
  "content": {
    "application/json": {
      "example": {
        "code": "INVALID_REQUEST",
        "message": "요청이 올바르지 않습니다.",
        "data": null
      }
    }
  }
}
```
#### HTTP 404

```json
{
  "description": "존재하지 않는 사용자 / 탈퇴한 사용자",
  "content": {
    "application/json": {
      "examples": {
        "notFound": {
          "description": "notFound",
          "value": {
            "code": "USER_NOT_FOUND",
            "message": "사용자를 찾을 수 없습니다.",
            "data": null
          }
        },
        "withdrawn": {
          "description": "withdrawn",
          "value": {
            "code": "USER_WITHDRAWN",
            "message": "탈퇴한 사용자입니다.",
            "data": null
          }
        }
      }
    }
  }
}
```
#### HTTP 409

```json
{
  "description": "이미 해당 상태",
  "content": {
    "application/json": {
      "example": {
        "code": "USER_STATUS_ALREADY_SET",
        "message": "이미 해당 상태의 사용자입니다.",
        "data": null
      }
    }
  }
}
```

<a id="op-046"></a>

## GET /admin/users/withdrawals

- 기능: 사용자 탈퇴 로그 조회
- operationId: `getUserWithdrawLogs`; tag: `사용자 관리`
- 현재 상태: **API·hook 정의, 화면 사용처 없음**
- 인계 작업: [T02](./api-work-items.md#t02)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

탈퇴(deletedAt) 최신순 고정 정렬. page는 1부터, size는 생략 시 20이고 100을 최대로 잘린다.

실제 API 호출:

- [src/entities/users/api/admin-users.api.ts:38](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.api.ts:38) — `getWithdrawals`

같은 API 디렉터리의 DTO/parser 재사용 후보: [admin-users.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.parser.ts), [admin-users.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.dto.ts), [users.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/users.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| query | `page` | 아니오/미기재 | `integer` | One-based page index (1..N) |
| query | `size` | 아니오/미기재 | `integer` | The size of the page to be returned |
| query | `sort` | 아니오/미기재 | 배열&lt;`string`&gt; | Sorting criteria in the format: property,(asc\|desc). Default sort order is ascending. Multiple sort criteria are supported. |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "page",
    "in": "query",
    "description": "One-based page index (1..N)",
    "required": false,
    "schema": {
      "type": "integer",
      "default": 1,
      "minimum": 0
    }
  },
  {
    "name": "size",
    "in": "query",
    "description": "The size of the page to be returned",
    "required": false,
    "schema": {
      "type": "integer",
      "default": 20,
      "minimum": 1
    }
  },
  {
    "name": "sort",
    "in": "query",
    "description": "Sorting criteria in the format: property,(asc|desc). Default sort order is ascending. Multiple sort criteria are supported.",
    "required": false,
    "schema": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

조회 성공, 없으면 items는 빈 배열

- 미디어 타입: `application/json`
- schema: [ApiResponsePageResponseUserWithdrawLogResponse](./api-schema-catalog.md#schema-apiresponsepageresponseuserwithdrawlogresponse)
- data payload: [PageResponseUserWithdrawLogResponse](./api-schema-catalog.md#schema-pageresponseuserwithdrawlogresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponsePageResponseUserWithdrawLogResponse"
  },
  "example": {
    "code": "SUCCESS",
    "message": "성공",
    "data": {
      "items": [
        {
          "publicId": "9e0d0000-0000-4000-8000-000000009003",
          "nickname": "박탕정",
          "withdrawnAt": "2026-03-01T00:00:00Z"
        }
      ],
      "total": 1,
      "page": 1,
      "size": 20
    }
  }
}
```

### 오류 응답

#### HTTP 401

```json
{
  "description": "토큰 만료/위조",
  "content": {
    "application/json": {
      "examples": {
        "expiredToken": {
          "description": "expiredToken",
          "value": {
            "code": "EXPIRED_TOKEN",
            "message": "만료된 토큰입니다.",
            "data": null
          }
        },
        "invalidToken": {
          "description": "invalidToken",
          "value": {
            "code": "INVALID_TOKEN",
            "message": "유효하지 않은 토큰입니다.",
            "data": null
          }
        }
      }
    }
  }
}
```

<a id="op-047"></a>

## GET /admin/video

- 기능: 비디오 목록 조회
- operationId: `getVideos`; tag: `영상 관리`
- 현재 상태: **API·hook 정의, 화면 사용처 없음**
- 인계 작업: [T04](./api-work-items.md#t04)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/video/api/video.api.ts:47](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.api.ts:47) — `getList`

같은 API 디렉터리의 DTO/parser 재사용 후보: [playlist.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.dto.ts), [video.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.dto.ts), [video.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.parser.ts), [playlist.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| query | `pageable` | 예 | [Pageable](./api-schema-catalog.md#schema-pageable) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "pageable",
    "in": "query",
    "required": true,
    "schema": {
      "$ref": "#/components/schemas/Pageable"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponsePageResponseGetVideoListResponse](./api-schema-catalog.md#schema-apiresponsepageresponsegetvideolistresponse)
- data payload: [PageResponseGetVideoListResponse](./api-schema-catalog.md#schema-pageresponsegetvideolistresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponsePageResponseGetVideoListResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-048"></a>

## POST /admin/video

- 기능: 비디오 등록
- operationId: `registerVideo`; tag: `영상 관리`
- 현재 상태: **API·hook 정의, 화면 사용처 없음** · F04
- 인계 작업: [T04](./api-work-items.md#t04)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/video/api/video.api.ts:60](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.api.ts:60) — `postVideo`

같은 API 디렉터리의 DTO/parser 재사용 후보: [playlist.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.dto.ts), [video.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.dto.ts), [video.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.parser.ts), [playlist.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.parser.ts).

### 요청

path/query/header parameter 정의 없음.

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "multipart/form-data": {
      "schema": {
        "type": "object",
        "properties": {
          "data": {
            "$ref": "#/components/schemas/CreateVideoRequest"
          },
          "file": {
            "type": "string",
            "format": "binary"
          }
        },
        "required": [
          "data",
          "file"
        ]
      }
    }
  }
}
```

요청 DTO: [CreateVideoRequest](./api-schema-catalog.md#schema-createvideorequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseLong](./api-schema-catalog.md#schema-apiresponselong)
- data payload: `integer` (int64)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseLong"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-049"></a>

## DELETE /admin/video/{videoId}

- 기능: 비디오 삭제
- operationId: `deleteVideo`; tag: `영상 관리`
- 현재 상태: **API·hook 정의, 화면 사용처 없음**
- 인계 작업: [T04](./api-work-items.md#t04)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/video/api/video.api.ts:80](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.api.ts:80) — `deleteVideo`

같은 API 디렉터리의 DTO/parser 재사용 후보: [playlist.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.dto.ts), [video.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.dto.ts), [video.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.parser.ts), [playlist.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `videoId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "videoId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-050"></a>

## GET /admin/video/{videoId}

- 기능: 비디오 조회
- operationId: `getVideo`; tag: `영상 관리`
- 현재 상태: **API·hook 정의, 화면 사용처 없음**
- 인계 작업: [T04](./api-work-items.md#t04)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/video/api/video.api.ts:57](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.api.ts:57) — `getDetail`

같은 API 디렉터리의 DTO/parser 재사용 후보: [playlist.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.dto.ts), [video.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.dto.ts), [video.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.parser.ts), [playlist.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `videoId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "videoId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseObject](./api-schema-catalog.md#schema-apiresponseobject)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseObject"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-051"></a>

## PATCH /admin/video/{videoId}

- 기능: 비디오 수정
- operationId: `updateVideo`; tag: `영상 관리`
- 현재 상태: **API·hook 정의, 화면 사용처 없음** · F04
- 인계 작업: [T04](./api-work-items.md#t04)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/video/api/video.api.ts:70](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.api.ts:70) — `patchVideo`

같은 API 디렉터리의 DTO/parser 재사용 후보: [playlist.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.dto.ts), [video.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.dto.ts), [video.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.parser.ts), [playlist.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `videoId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "videoId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "multipart/form-data": {
      "schema": {
        "type": "object",
        "properties": {
          "data": {
            "$ref": "#/components/schemas/UpdateVideoRequest"
          },
          "file": {
            "type": "string",
            "format": "binary"
          }
        },
        "required": [
          "data"
        ]
      }
    }
  }
}
```

요청 DTO: [UpdateVideoRequest](./api-schema-catalog.md#schema-updatevideorequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-052"></a>

## POST /admin/video/{videoId}/thumbnail

- 기능: 썸네일 등록
- operationId: `registerThumbnail`; tag: `영상 관리`
- 현재 상태: **API·hook 정의, 화면 사용처 없음**
- 인계 작업: [T04](./api-work-items.md#t04)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/video/api/video.api.ts:83](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.api.ts:83) — `postThumbnail`

같은 API 디렉터리의 DTO/parser 재사용 후보: [playlist.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.dto.ts), [video.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.dto.ts), [video.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.parser.ts), [playlist.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `videoId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "videoId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "multipart/form-data": {
      "schema": {
        "type": "object",
        "properties": {
          "file": {
            "type": "string",
            "format": "binary"
          }
        },
        "required": [
          "file"
        ]
      }
    }
  }
}
```

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-053"></a>

## GET /admin/video/playlists

- 기능: 플레이리스트 목록 조회
- operationId: `getPlaylists`; tag: `영상 관리`
- 현재 상태: **API·hook 정의, 화면 사용처 없음**
- 인계 작업: [T04](./api-work-items.md#t04)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/video/api/playlist.api.ts:37](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.api.ts:37) — `getList`

같은 API 디렉터리의 DTO/parser 재사용 후보: [playlist.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.dto.ts), [video.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.dto.ts), [video.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.parser.ts), [playlist.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| query | `pageable` | 예 | [Pageable](./api-schema-catalog.md#schema-pageable) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "pageable",
    "in": "query",
    "required": true,
    "schema": {
      "$ref": "#/components/schemas/Pageable"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponsePageResponseGetPlaylistSummaryResponse](./api-schema-catalog.md#schema-apiresponsepageresponsegetplaylistsummaryresponse)
- data payload: [PageResponseGetPlaylistSummaryResponse](./api-schema-catalog.md#schema-pageresponsegetplaylistsummaryresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponsePageResponseGetPlaylistSummaryResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-054"></a>

## POST /admin/video/playlists

- 기능: 플레이리스트 생성
- operationId: `createPlaylist`; tag: `영상 관리`
- 현재 상태: **API·hook 정의, 화면 사용처 없음**
- 인계 작업: [T04](./api-work-items.md#t04)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/video/api/playlist.api.ts:50](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.api.ts:50) — `postPlaylist`

같은 API 디렉터리의 DTO/parser 재사용 후보: [playlist.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.dto.ts), [video.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.dto.ts), [video.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.parser.ts), [playlist.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.parser.ts).

### 요청

path/query/header parameter 정의 없음.

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/CreatePlaylistRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [CreatePlaylistRequest](./api-schema-catalog.md#schema-createplaylistrequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseLong](./api-schema-catalog.md#schema-apiresponselong)
- data payload: `integer` (int64)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseLong"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-055"></a>

## DELETE /admin/video/playlists/{playlistId}

- 기능: 플레이리스트 삭제
- operationId: `deletePlaylist`; tag: `영상 관리`
- 현재 상태: **API·hook 정의, 화면 사용처 없음**
- 인계 작업: [T04](./api-work-items.md#t04)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/video/api/playlist.api.ts:60](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.api.ts:60) — `deletePlaylist`

같은 API 디렉터리의 DTO/parser 재사용 후보: [playlist.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.dto.ts), [video.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.dto.ts), [video.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.parser.ts), [playlist.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `playlistId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "playlistId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-056"></a>

## GET /admin/video/playlists/{playlistId}

- 기능: 플레이리스트 조회
- operationId: `getPlaylist`; tag: `영상 관리`
- 현재 상태: **API·hook 정의, 화면 사용처 없음**
- 인계 작업: [T04](./api-work-items.md#t04)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/video/api/playlist.api.ts:47](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.api.ts:47) — `getDetail`

같은 API 디렉터리의 DTO/parser 재사용 후보: [playlist.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.dto.ts), [video.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.dto.ts), [video.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.parser.ts), [playlist.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `playlistId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "playlistId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseGetPlaylistResponse](./api-schema-catalog.md#schema-apiresponsegetplaylistresponse)
- data payload: [GetPlaylistResponse](./api-schema-catalog.md#schema-getplaylistresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseGetPlaylistResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-057"></a>

## PATCH /admin/video/playlists/{playlistId}

- 기능: 플레이리스트 수정
- operationId: `updatePlaylist`; tag: `영상 관리`
- 현재 상태: **API·hook 정의, 화면 사용처 없음**
- 인계 작업: [T04](./api-work-items.md#t04)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/video/api/playlist.api.ts:53](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.api.ts:53) — `patchPlaylist`

같은 API 디렉터리의 DTO/parser 재사용 후보: [playlist.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.dto.ts), [video.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.dto.ts), [video.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.parser.ts), [playlist.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `playlistId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "playlistId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/UpdatePlaylistRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [UpdatePlaylistRequest](./api-schema-catalog.md#schema-updateplaylistrequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-058"></a>

## POST /auth/login

- 기능: 관리자 로그인
- operationId: `login`; tag: `관리자 인증`
- 현재 상태: **화면 호출 연결 확인**
- 인계 작업: [T06](./api-work-items.md#t06)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

관리자 로그인은 sso 이전의 권환 확인용 코드이다.


실제 API 호출:

- [src/entities/auth/api/auth.api.ts:12](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/auth/api/auth.api.ts:12) — `signIn`

같은 API 디렉터리의 DTO/parser 재사용 후보: [auth.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/auth/api/auth.dto.ts).

### 요청

path/query/header parameter 정의 없음.

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/LoginRequest"
      },
      "examples": {
        "LOGIN": {
          "summary": "관리자 로그인",
          "description": "LOGIN",
          "value": {
            "loginId": "admin01",
            "password": "password1!"
          }
        }
      }
    }
  },
  "required": true
}
```

요청 DTO: [LoginRequest](./api-schema-catalog.md#schema-loginrequest).

### 성공 응답

#### HTTP 200

로그인 성공

- 미디어 타입: `application/json`
- schema: [AdminApiResponseTokenResponse](./api-schema-catalog.md#schema-adminapiresponsetokenresponse)
- data payload: [TokenResponse](./api-schema-catalog.md#schema-tokenresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/AdminApiResponseTokenResponse"
  },
  "examples": {
    "SUCCESS": {
      "summary": "성공",
      "description": "SUCCESS",
      "value": {
        "code": "SUCCESS",
        "message": "성공",
        "data": {
          "accessToken": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzg3NTQxNTg3LCJleHAiOjE3ODgxNDYzODd9.JpP4JnXWtFOdq4GFUm6WsACXr0zgpUcywUVdbQeN7zg"
        }
      }
    }
  }
}
```

### 오류 응답

#### HTTP 400

```json
{
  "description": "사용자의 잘못된(잘못된 아이디와 비밀번호) 요청시 400에러 반환",
  "content": {
    "application/json": {
      "examples": {
        "AuthLoginValidation": {
          "summary": "잘못된 요청",
          "description": "AuthLoginValidation",
          "value": {
            "code": "ADMIN_INVALID_PASSWORD",
            "message": "비밀번호가 일치하지 않습니다.",
            "data": null
          }
        }
      }
    }
  }
}
```
#### HTTP 404

```json
{
  "description": "존재하지 않은 관리자면 404에러 반환",
  "content": {
    "application/json": {
      "examples": {
        "AdminNotFound": {
          "summary": "존재하지 않는 관리자 요청",
          "description": "AdminNotFound",
          "value": {
            "code": "ADMIN_NOT_FOUND",
            "message": "존재하지 않는 관리자입니다.",
            "data": null
          }
        }
      }
    }
  }
}
```

<a id="op-059"></a>

## GET /citizen/proposals

- 기능: 시민참여 제안 목록 조회
- operationId: `listCitizenProposals`; tag: `시민참여 제안`
- 현재 상태: **화면 호출 연결 확인** · F01
- 인계 작업: [T01](./api-work-items.md#t01)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

관리자 인증이 있어야 조회가 가능하다.
목록에는 본문이 포함되어 있지 않으며 상세조회에서만 조회가 가능하다.
page는 1부터 시작한다. 생략하면 1, size는 생략하면 20이고 100을 최대로 100 이상도 100으로 잘린다.
sort는 createdAt/id로 정렬하고 생략시 createdAt desc로 고정된다.
author는 탈퇴한 회원의 제안이면 null이다.

실제 API 호출:

- [src/entities/cp-proposal/api/cp-proposal.api.ts:34](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/cp-proposal/api/cp-proposal.api.ts:34) — `getList`

같은 API 디렉터리의 DTO/parser 재사용 후보: [cp-proposal.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/cp-proposal/api/cp-proposal.dto.ts), [cp-proposal.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/cp-proposal/api/cp-proposal.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| query | `status` | 아니오/미기재 | 배열&lt;`RECEIVED / UNDER_REVIEW / ADOPTED / REJECTED`&gt; | 상태 필터, 목록에 없는 경로로 요청시 INVALID_REQUEST 400 |
| query | `title` | 아니오/미기재 | `string` | 제목 일부를 검색시 해당 단어가 포함된 제안 목록 조회 |
| query | `author` | 아니오/미기재 | `string` | 작성자 닉네임 일부가 포함된 제안 목록 조회 |
| query | `page` | 아니오/미기재 | `integer` | One-based page index (1..N) |
| query | `size` | 아니오/미기재 | `integer` | The size of the page to be returned |
| query | `sort` | 아니오/미기재 | 배열&lt;`string`&gt; | Sorting criteria in the format: property,(asc\|desc). Default sort order is ascending. Multiple sort criteria are supported. |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "status",
    "in": "query",
    "description": "상태 필터, 목록에 없는 경로로 요청시 INVALID_REQUEST 400",
    "required": false,
    "schema": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "RECEIVED",
          "UNDER_REVIEW",
          "ADOPTED",
          "REJECTED"
        ]
      }
    },
    "example": "RECEIVED"
  },
  {
    "name": "title",
    "in": "query",
    "description": "제목 일부를 검색시 해당 단어가 포함된 제안 목록 조회",
    "required": false,
    "schema": {
      "type": "string"
    },
    "example": "키워드"
  },
  {
    "name": "author",
    "in": "query",
    "description": "작성자 닉네임 일부가 포함된 제안 목록 조회",
    "required": false,
    "schema": {
      "type": "string"
    },
    "example": "홍길동"
  },
  {
    "name": "page",
    "in": "query",
    "description": "One-based page index (1..N)",
    "required": false,
    "schema": {
      "type": "integer",
      "default": 1,
      "minimum": 0
    }
  },
  {
    "name": "size",
    "in": "query",
    "description": "The size of the page to be returned",
    "required": false,
    "schema": {
      "type": "integer",
      "default": 20,
      "minimum": 1
    }
  },
  {
    "name": "sort",
    "in": "query",
    "description": "Sorting criteria in the format: property,(asc|desc). Default sort order is ascending. Multiple sort criteria are supported.",
    "required": false,
    "schema": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

조회 성공, 결과가 없으면 items는 빈배열로 반환한다.

- 미디어 타입: `application/json`
- schema: [ApiResponsePageResponseProposalSummaryResponse](./api-schema-catalog.md#schema-apiresponsepageresponseproposalsummaryresponse)
- data payload: [PageResponseCitizenProposalSummaryResponse](./api-schema-catalog.md#schema-pageresponsecitizenproposalsummaryresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponsePageResponseProposalSummaryResponse"
  },
  "examples": {
    "firstPage": {
      "summary": "첫 페이지",
      "description": "firstPage",
      "value": {
        "code": "SUCCESS",
        "message": "성공",
        "data": {
          "items": [
            {
              "id": 59,
              "title": "도서관 야간 개방 시간 연장",
              "status": "RECEIVED",
              "author": "홍길동",
              "createdAt": "2026-08-18T12:56:46.633288Z"
            },
            {
              "id": 58,
              "title": "버스 정류장 그늘막 확대",
              "status": "RECEIVED",
              "author": null,
              "createdAt": "2026-08-18T12:56:35.448924Z"
            }
          ],
          "total": 2,
          "page": 1,
          "size": 20
        }
      }
    }
  }
}
```

### 오류 응답

#### HTTP 400

```json
{
  "description": "정렬조건이 허용 목록 밖이거나 파라미터 값이 타입에 맞지 않는 경우",
  "content": {
    "application/json": {
      "examples": {
        "invalidSort": {
          "summary": "허용되지 않은 정렬 프로퍼티",
          "description": "invalidSort",
          "value": {
            "code": "INVALID_SORT_PROPERTY",
            "message": "지원하지 않는 정렬 조건입니다.",
            "data": null
          }
        },
        "invalidStatus": {
          "summary": "status에 없는 값",
          "description": "invalidStatus",
          "value": {
            "code": "INVALID_REQUEST",
            "message": "요청이 올바르지 않습니다.",
            "data": null
          }
        }
      }
    }
  }
}
```
#### HTTP 401

```json
{
  "description": "토큰이 만료, 위조된경우에 401 에러를 반환한다",
  "content": {
    "application/json": {
      "examples": {
        "expiredToken": {
          "summary": "토큰만료",
          "description": "expiredToken",
          "value": {
            "code": "EXPIRED_TOKEN",
            "message": "만료된 토큰입니다.",
            "data": null
          }
        },
        "invalidToken": {
          "summary": "토큰 위조/형식 오류",
          "description": "invalidToken",
          "value": {
            "code": "INVALID_TOKEN",
            "message": "유효하지 않은 토큰입니다.",
            "data": null
          }
        }
      }
    }
  }
}
```

<a id="op-060"></a>

## GET /citizen/proposals/{proposalId}

- 기능: 제안 상세(id) 조회
- operationId: `CitizenProposal`; tag: `시민참여 제안`
- 현재 상태: **화면 호출 연결 확인** · F01
- 인계 작업: [T01](./api-work-items.md#t01)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

id값을 가진 제안의 상세 데이터를 조회한다.


실제 API 호출:

- [src/entities/cp-proposal/api/cp-proposal.api.ts:40](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/cp-proposal/api/cp-proposal.api.ts:40) — `getDetail`

같은 API 디렉터리의 DTO/parser 재사용 후보: [cp-proposal.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/cp-proposal/api/cp-proposal.dto.ts), [cp-proposal.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/cp-proposal/api/cp-proposal.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `proposalId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "proposalId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

제안 상세 조회 성공

- 미디어 타입: `application/json`
- schema: [ApiResponseProposalResponse](./api-schema-catalog.md#schema-apiresponseproposalresponse)
- data payload: [CitizenProposalResponse](./api-schema-catalog.md#schema-citizenproposalresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseProposalResponse"
  },
  "examples": {
    "success": {
      "summary": "조회 성공",
      "description": "success",
      "value": {
        "code": "SUCCESS",
        "message": "성공",
        "data": {
          "id": 58,
          "author": "홍길동",
          "title": "버스 정류장 그늘막 확대",
          "background": "여름철 정류장 대기 중 직사광선 노출이 심하다.",
          "content": "이용객이 많은 정류장부터 그늘막을 단계적으로 설치한다.",
          "expectedEffect": "폭염기 온열질환 위험이 줄어든다.",
          "referenceCase": null,
          "status": "UNDER_REVIEW",
          "reviewResult": "담당 부서 검토 중입니다.",
          "createdAt": "2026-08-18T12:56:35.448924Z",
          "updatedAt": "2026-08-20T09:12:04.118273Z"
        }
      }
    }
  }
}
```

### 오류 응답

#### HTTP 401

```json
{
  "description": "토큰이 만료, 위조된경우에 401 에러를 반환한다",
  "content": {
    "application/json": {
      "examples": {
        "expiredToken": {
          "summary": "토큰만료",
          "description": "expiredToken",
          "value": {
            "code": "EXPIRED_TOKEN",
            "message": "만료된 토큰입니다.",
            "data": null
          }
        },
        "invalidToken": {
          "summary": "토큰 위조/형식 오류",
          "description": "invalidToken",
          "value": {
            "code": "INVALID_TOKEN",
            "message": "유효하지 않은 토큰입니다.",
            "data": null
          }
        }
      }
    }
  }
}
```
#### HTTP 404

```json
{
  "description": "존재하지 않은 id 입력시 404에러를 반환",
  "content": {
    "application/json": {
      "examples": {
        "proposalNotFound": {
          "summary": "유효하지 않은 id 입력",
          "description": "proposalNotFound",
          "value": {
            "code": "CITIZEN_PROPOSAL_NOT_FOUND",
            "message": "제안을 찾을 수 없습니다.",
            "data": null
          }
        }
      }
    }
  }
}
```

<a id="op-061"></a>

## PATCH /citizen/proposals/{proposalId}

- 기능: 제안 상태 수정
- operationId: `CitizenProposalStatusUpdate`; tag: `시민참여 제안`
- 현재 상태: **일치 호출 없음** · F01
- 인계 작업: [T01](./api-work-items.md#t01)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

해당 URI는 제안 목록에서 상태만 변경될때 사용된다. 넣을 수 있는 값은 네 가지다.

| 값 | 의미 |
| --- | --- |
| `RECEIVED` | 접수 — 제안 생성 시의 초기값이며, 이 값으로 되돌리는 것도 허용한다 |
| `UNDER_REVIEW` | 검토중 |
| `ADOPTED` | 채택 |
| `REJECTED` | 반려 |

목록에 없는 값을 넣거나 입력을 안하면 400에러를 반환한다.
또한 존재하지 않는 제안 변경 요청시 404에러를 반환한다.


일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `proposalId` | 예 | `integer` (int64) | 제안 ID |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "proposalId",
    "in": "path",
    "description": "제안 ID",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    },
    "example": 1
  }
]
```

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/UpdateCitizenProposalStatusRequest"
      },
      "examples": {
        "underReview": {
          "summary": "검토중",
          "description": "underReview",
          "value": {
            "status": "UNDER_REVIEW"
          }
        },
        "adopted": {
          "summary": "채택",
          "description": "adopted",
          "value": {
            "status": "ADOPTED"
          }
        },
        "rejected": {
          "summary": "반려",
          "description": "rejected",
          "value": {
            "status": "REJECTED"
          }
        },
        "received": {
          "summary": "접수로 되돌림",
          "description": "received",
          "value": {
            "status": "RECEIVED"
          }
        }
      }
    }
  },
  "required": true
}
```

요청 DTO: [UpdateCitizenProposalStatusRequest](./api-schema-catalog.md#schema-updatecitizenproposalstatusrequest).

### 성공 응답

#### HTTP 200

제안 상태 변경 성공

- 미디어 타입: `application/json`
- schema: [ApiResponse](./api-schema-catalog.md#schema-apiresponse)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponse"
  },
  "examples": {
    "success": {
      "summary": "상태 변경 성공",
      "description": "success",
      "value": {
        "code": "SUCCESS",
        "message": "성공",
        "data": null
      }
    }
  }
}
```

### 오류 응답

#### HTTP 400

```json
{
  "description": "목록에 없는 상태를 입력하거나 빈칸이면 400에러를 반환한다.",
  "content": {
    "application/json": {
      "examples": {
        "invalidRequest": {
          "summary": "상태 미입력 또는 목록에 없는 값",
          "description": "invalidRequest",
          "value": {
            "code": "INVALID_REQUEST",
            "message": "요청이 올바르지 않습니다.",
            "data": null
          }
        }
      }
    }
  }
}
```
#### HTTP 401

```json
{
  "description": "토큰이 만료, 위조된경우에 401 에러를 반환한다",
  "content": {
    "application/json": {
      "examples": {
        "expiredToken": {
          "summary": "토큰만료",
          "description": "expiredToken",
          "value": {
            "code": "EXPIRED_TOKEN",
            "message": "만료된 토큰입니다.",
            "data": null
          }
        },
        "invalidToken": {
          "summary": "토큰 위조/형식 오류",
          "description": "invalidToken",
          "value": {
            "code": "INVALID_TOKEN",
            "message": "유효하지 않은 토큰입니다.",
            "data": null
          }
        }
      }
    }
  }
}
```
#### HTTP 404

```json
{
  "description": "존재하지 않은 id 입력시 404에러를 반환",
  "content": {
    "application/json": {
      "examples": {
        "proposalNotFound": {
          "summary": "유효하지 않은 id 입력",
          "description": "proposalNotFound",
          "value": {
            "code": "CITIZEN_PROPOSAL_NOT_FOUND",
            "message": "제안을 찾을 수 없습니다.",
            "data": null
          }
        }
      }
    }
  }
}
```

<a id="op-062"></a>

## PATCH /citizen/proposals/{proposalId}/review-result

- 기능: 제안 검토 결과 수정
- operationId: `CitizenProposalReviewResultUpdate`; tag: `시민참여 제안`
- 현재 상태: **일치 호출 없음** · F01
- 인계 작업: [T01](./api-work-items.md#t01)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

운영자가 작성한 검토 결과를 저장한다. 시민 앱의 제안 상세에 그대로 노출된다.
상태 변경과 별개라 상태는 바뀌지 않으며, 다시 호출하면 이전 내용을 덮어쓴다.

빈 값·공백만 보내면 400에러를 반환한다. 최대 5,000자다.
존재하지 않는 제안 변경 요청시 404에러를 반환한다.


일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `proposalId` | 예 | `integer` (int64) | 제안 ID |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "proposalId",
    "in": "path",
    "description": "제안 ID",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    },
    "example": 1
  }
]
```

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/UpdateCitizenProposalReviewResultRequest"
      },
      "examples": {
        "reviewResult": {
          "summary": "검토 결과 작성",
          "description": "reviewResult",
          "value": {
            "reviewResult": "담당 부서 검토 중입니다."
          }
        }
      }
    }
  },
  "required": true
}
```

요청 DTO: [UpdateCitizenProposalReviewResultRequest](./api-schema-catalog.md#schema-updatecitizenproposalreviewresultrequest).

### 성공 응답

#### HTTP 200

검토 결과 저장 성공

- 미디어 타입: `application/json`
- schema: [ApiResponse](./api-schema-catalog.md#schema-apiresponse)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponse"
  },
  "examples": {
    "success": {
      "summary": "저장 성공",
      "description": "success",
      "value": {
        "code": "SUCCESS",
        "message": "성공",
        "data": null
      }
    }
  }
}
```

### 오류 응답

#### HTTP 400

```json
{
  "description": "검토 결과가 비었거나 5,000자를 넘으면 400에러를 반환한다. `data`에 필드별 사유가 담긴다.",
  "content": {
    "application/json": {
      "examples": {
        "validationFailed": {
          "summary": "검토 결과 미입력",
          "description": "validationFailed",
          "value": {
            "code": "INVALID_REQUEST",
            "message": "요청이 올바르지 않습니다.",
            "data": [
              {
                "field": "reviewResult",
                "reason": "검토 결과는 필수입니다."
              }
            ]
          }
        }
      }
    }
  }
}
```
#### HTTP 401

```json
{
  "description": "토큰이 만료, 위조된경우에 401 에러를 반환한다",
  "content": {
    "application/json": {
      "examples": {
        "expiredToken": {
          "summary": "토큰만료",
          "description": "expiredToken",
          "value": {
            "code": "EXPIRED_TOKEN",
            "message": "만료된 토큰입니다.",
            "data": null
          }
        },
        "invalidToken": {
          "summary": "토큰 위조/형식 오류",
          "description": "invalidToken",
          "value": {
            "code": "INVALID_TOKEN",
            "message": "유효하지 않은 토큰입니다.",
            "data": null
          }
        }
      }
    }
  }
}
```
#### HTTP 404

```json
{
  "description": "존재하지 않은 id 입력시 404에러를 반환",
  "content": {
    "application/json": {
      "examples": {
        "proposalNotFound": {
          "summary": "유효하지 않은 id 입력",
          "description": "proposalNotFound",
          "value": {
            "code": "CITIZEN_PROPOSAL_NOT_FOUND",
            "message": "제안을 찾을 수 없습니다.",
            "data": null
          }
        }
      }
    }
  }
}
```

<a id="op-063"></a>

## GET /citizen/proposals/summary

- 기능: 상태별 제안 데이터(count) 조회
- operationId: `CitizenStatusProposalCount`; tag: `시민참여 제안`
- 현재 상태: **일치 호출 없음** · F01
- 인계 작업: [T01](./api-work-items.md#t01)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

제안의 전체갯수 및 제안 상태별로 데이터의 갯수를 조회한다.


일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

path/query/header parameter 정의 없음.

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

상태별 조회 데이터 갯수 조회 성공

- 미디어 타입: `application/json`
- schema: [ApiResponseProposalStatusCountResponse](./api-schema-catalog.md#schema-apiresponseproposalstatuscountresponse)
- data payload: [CitizenProposalStatusCountResponse](./api-schema-catalog.md#schema-citizenproposalstatuscountresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseProposalStatusCountResponse"
  },
  "examples": {
    "success": {
      "summary": "조회 성공 시",
      "description": "success",
      "value": {
        "code": "SUCCESS",
        "message": "성공",
        "data": {
          "total": 124,
          "received": 15,
          "underReview": 46,
          "adopted": 54,
          "rejected": 9
        }
      }
    }
  }
}
```

### 오류 응답

#### HTTP 401

```json
{
  "description": "토큰이 만료, 위조된경우에 401 에러를 반환한다",
  "content": {
    "application/json": {
      "examples": {
        "expiredToken": {
          "summary": "토큰만료",
          "description": "expiredToken",
          "value": {
            "code": "EXPIRED_TOKEN",
            "message": "만료된 토큰입니다.",
            "data": null
          }
        },
        "invalidToken": {
          "summary": "토큰 위조/형식 오류",
          "description": "invalidToken",
          "value": {
            "code": "INVALID_TOKEN",
            "message": "유효하지 않은 토큰입니다.",
            "data": null
          }
        }
      }
    }
  }
}
```

<a id="op-064"></a>

## GET /citizen/votes

- 기능: 시민참여 투표 목록 조회
- operationId: `listCitizenVotes`; tag: `시민참여 투표`
- 현재 상태: **화면 호출 연결 확인**
- 인계 작업: [T01](./api-work-items.md#t01)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

관리자 인증이 있어야 조회가 가능하다.
page는 1부터 시작한다. 생략하면 1, size는 생략하면 20이고 100을 최대로 100 이상도 100으로 잘린다.
sort는 createdAt/id/startsAt/endsAt로 정렬하고 생략시 createdAt desc로 고정된다.
status는 저장된 컬럼이 아니라 파생값이라 정렬할 수 없다.

| status | 의미 |
| --- | --- |
| `DRAFT` | 임시저장 — 아직 공개하지 않아 시민에게는 보이지 않는다 |
| `UPCOMING` | 공개했으나 시작 전 |
| `IN_PROGRESS` | 투표중 — 시작·종료 시각을 양끝 포함해 판단한다 |
| `CLOSED` | 완료 |
| `CANCELLED` | 중단 — 기간이 남아 있어도 투표할 수 없다 |


실제 API 호출:

- [src/entities/cp-vote/api/cp-vote.api.ts:22](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/cp-vote/api/cp-vote.api.ts:22) — `getList`

같은 API 디렉터리의 DTO/parser 재사용 후보: [cp-vote.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/cp-vote/api/cp-vote.parser.ts), [cp-vote.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/cp-vote/api/cp-vote.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| query | `page` | 아니오/미기재 | `integer` | One-based page index (1..N) |
| query | `size` | 아니오/미기재 | `integer` | The size of the page to be returned |
| query | `sort` | 아니오/미기재 | 배열&lt;`string`&gt; | Sorting criteria in the format: property,(asc\|desc). Default sort order is ascending. Multiple sort criteria are supported. |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "page",
    "in": "query",
    "description": "One-based page index (1..N)",
    "required": false,
    "schema": {
      "type": "integer",
      "default": 1,
      "minimum": 0
    }
  },
  {
    "name": "size",
    "in": "query",
    "description": "The size of the page to be returned",
    "required": false,
    "schema": {
      "type": "integer",
      "default": 20,
      "minimum": 1
    }
  },
  {
    "name": "sort",
    "in": "query",
    "description": "Sorting criteria in the format: property,(asc|desc). Default sort order is ascending. Multiple sort criteria are supported.",
    "required": false,
    "schema": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

조회 성공, 결과가 없으면 items는 빈배열로 반환한다.

- 미디어 타입: `application/json`
- schema: [ApiResponsePageResponseVoteSummaryResponse](./api-schema-catalog.md#schema-apiresponsepageresponsevotesummaryresponse)
- data payload: [PageResponseCitizenVoteSummaryResponse](./api-schema-catalog.md#schema-pageresponsecitizenvotesummaryresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponsePageResponseVoteSummaryResponse"
  },
  "examples": {
    "firstPage": {
      "summary": "첫 페이지",
      "description": "firstPage",
      "value": {
        "code": "SUCCESS",
        "message": "성공",
        "data": {
          "items": [
            {
              "id": 12,
              "status": "IN_PROGRESS",
              "title": "아산시 대표 축제 명칭 선정",
              "startsAt": "2026-08-25T00:00:00Z",
              "endsAt": "2026-09-10T23:59:59Z"
            },
            {
              "id": 11,
              "status": "CLOSED",
              "title": "시민공원 야간 조명 설치 여부",
              "startsAt": "2026-07-01T00:00:00Z",
              "endsAt": "2026-07-31T23:59:59Z"
            },
            {
              "id": 10,
              "status": "DRAFT",
              "title": "작성 중인 투표",
              "startsAt": "2026-09-01T00:00:00Z",
              "endsAt": "2026-09-30T23:59:59Z"
            }
          ],
          "total": 3,
          "page": 1,
          "size": 20
        }
      }
    }
  }
}
```

### 오류 응답

#### HTTP 400

```json
{
  "description": "정렬조건이 허용 목록 밖이거나 파라미터 값이 타입에 맞지 않는 경우",
  "content": {
    "application/json": {
      "examples": {
        "invalidSort": {
          "summary": "허용되지 않은 정렬 프로퍼티",
          "description": "invalidSort",
          "value": {
            "code": "INVALID_SORT_PROPERTY",
            "message": "지원하지 않는 정렬 조건입니다.",
            "data": null
          }
        },
        "invalidParameter": {
          "summary": "파라미터 타입 불일치",
          "description": "invalidParameter",
          "value": {
            "code": "INVALID_REQUEST",
            "message": "요청이 올바르지 않습니다.",
            "data": null
          }
        }
      }
    }
  }
}
```
#### HTTP 401

```json
{
  "description": "토큰이 만료, 위조된경우에 401 에러를 반환한다",
  "content": {
    "application/json": {
      "examples": {
        "expiredToken": {
          "summary": "토큰만료",
          "description": "expiredToken",
          "value": {
            "code": "EXPIRED_TOKEN",
            "message": "만료된 토큰입니다.",
            "data": null
          }
        },
        "invalidToken": {
          "summary": "토큰 위조/형식 오류",
          "description": "invalidToken",
          "value": {
            "code": "INVALID_TOKEN",
            "message": "유효하지 않은 토큰입니다.",
            "data": null
          }
        }
      }
    }
  }
}
```

<a id="op-065"></a>

## GET /citizen/votes/{voteId}

- 기능: 투표 상세(id) 조회
- operationId: `CitizenVote`; tag: `시민참여 투표`
- 현재 상태: **화면 호출 연결 확인**
- 인계 작업: [T01](./api-work-items.md#t01)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

id값을 가진 투표의 상세 데이터를 조회한다. 존재하지 않는 id면 404를 반환한다.

임시저장·중단된 투표도 그대로 조회된다 -- 목록과 같은 규칙이다.
찬성·반대 수는 마감 여부와 무관하게 항상 내려간다. 시민 API는 마감 전 집계를 가리지만
그것은 남은 기간의 표심에 영향을 주지 않기 위한 시민 화면의 사정이다.
totalCount는 agreeCount + disagreeCount이며, updatedAt은 안건이 수정된 시각이라
표가 들어와도 갱신되지 않는다.


실제 API 호출:

- [src/entities/cp-vote/api/cp-vote.api.ts:25](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/cp-vote/api/cp-vote.api.ts:25) — `getDetail`

같은 API 디렉터리의 DTO/parser 재사용 후보: [cp-vote.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/cp-vote/api/cp-vote.parser.ts), [cp-vote.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/cp-vote/api/cp-vote.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `voteId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "voteId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

투표 상세 조회 성공

- 미디어 타입: `application/json`
- schema: [ApiResponseVoteDetailResponse](./api-schema-catalog.md#schema-apiresponsevotedetailresponse)
- data payload: [CitizenVoteDetailResponse](./api-schema-catalog.md#schema-citizenvotedetailresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoteDetailResponse"
  },
  "examples": {
    "success": {
      "summary": "조회 성공",
      "description": "success",
      "value": {
        "code": "SUCCESS",
        "message": "성공",
        "data": {
          "id": 12,
          "status": "IN_PROGRESS",
          "title": "아산시 대표 축제 명칭 선정",
          "agenda": "내년 봄 개최하는 시 대표 축제의 명칭을 두 안 중에서 정한다.",
          "startsAt": "2026-08-25T00:00:00Z",
          "endsAt": "2026-09-10T23:59:59Z",
          "totalCount": 128,
          "agreeCount": 91,
          "disagreeCount": 37,
          "createdAt": "2026-08-20T04:12:09.113204Z",
          "updatedAt": "2026-08-24T09:30:41.882910Z"
        }
      }
    }
  }
}
```

### 오류 응답

#### HTTP 401

```json
{
  "description": "토큰이 만료, 위조된경우에 401 에러를 반환한다",
  "content": {
    "application/json": {
      "examples": {
        "expiredToken": {
          "summary": "토큰만료",
          "description": "expiredToken",
          "value": {
            "code": "EXPIRED_TOKEN",
            "message": "만료된 토큰입니다.",
            "data": null
          }
        },
        "invalidToken": {
          "summary": "토큰 위조/형식 오류",
          "description": "invalidToken",
          "value": {
            "code": "INVALID_TOKEN",
            "message": "유효하지 않은 토큰입니다.",
            "data": null
          }
        }
      }
    }
  }
}
```
#### HTTP 404

```json
{
  "description": "존재하지 않은 id 입력시 404에러를 반환",
  "content": {
    "application/json": {
      "examples": {
        "voteNotFound": {
          "summary": "유효하지 않은 id 입력",
          "description": "voteNotFound",
          "value": {
            "code": "CITIZEN_VOTE_NOT_FOUND",
            "message": "투표를 찾을 수 없습니다.",
            "data": null
          }
        }
      }
    }
  }
}
```

<a id="op-066"></a>

## GET /citizen/votes/summary

- 기능: 상태별 투표 데이터(count) 조회
- operationId: `CitizenVoteStatusCount`; tag: `시민참여 투표`
- 현재 상태: **일치 호출 없음**
- 인계 작업: [T01](./api-work-items.md#t01)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

투표의 전체 갯수와 투표중·완료의 갯수를 조회한다.

total은 임시저장·예정·중단까지 포함한 전체 건수라 inProgress + closed와 같지 않다.
투표중·완료는 저장된 컬럼이 아니라 공개된 투표의 기간과 조회 시각에서 파생되므로,
같은 데이터라도 시각이 지나면 값이 달라진다.


일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

path/query/header parameter 정의 없음.

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

상태별 조회 데이터 갯수 조회 성공

- 미디어 타입: `application/json`
- schema: [ApiResponseVoteStatusCountResponse](./api-schema-catalog.md#schema-apiresponsevotestatuscountresponse)
- data payload: [CitizenVoteStatusCountResponse](./api-schema-catalog.md#schema-citizenvotestatuscountresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoteStatusCountResponse"
  },
  "examples": {
    "success": {
      "summary": "조회 성공 시",
      "description": "success",
      "value": {
        "code": "SUCCESS",
        "message": "성공",
        "data": {
          "total": 42,
          "inProgress": 3,
          "closed": 31
        }
      }
    }
  }
}
```

### 오류 응답

#### HTTP 401

```json
{
  "description": "토큰이 만료, 위조된경우에 401 에러를 반환한다",
  "content": {
    "application/json": {
      "examples": {
        "expiredToken": {
          "summary": "토큰만료",
          "description": "expiredToken",
          "value": {
            "code": "EXPIRED_TOKEN",
            "message": "만료된 토큰입니다.",
            "data": null
          }
        },
        "invalidToken": {
          "summary": "토큰 위조/형식 오류",
          "description": "invalidToken",
          "value": {
            "code": "INVALID_TOKEN",
            "message": "유효하지 않은 토큰입니다.",
            "data": null
          }
        }
      }
    }
  }
}
```

<a id="op-067"></a>

## GET /events/attendance

- 기능: 출석 이벤트 목록 조회
- operationId: `getAttendanceEventList`; tag: `출석체크 이벤트 등록 및 설정`
- 현재 상태: **화면 호출 연결 확인**
- 인계 작업: [T10](./api-work-items.md#t10)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/event/api/attendance/attendance.api.ts:22](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.api.ts:22) — `getList`

같은 API 디렉터리의 DTO/parser 재사용 후보: [attendance.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.parser.ts), [attendance.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| query | `query` | 예 | [GetEventAttendanceListRequest](./api-schema-catalog.md#schema-geteventattendancelistrequest) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "query",
    "in": "query",
    "required": true,
    "schema": {
      "$ref": "#/components/schemas/GetEventAttendanceListRequest"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponsePageResponseEventAttendanceSummaryResponse](./api-schema-catalog.md#schema-apiresponsepageresponseeventattendancesummaryresponse)
- data payload: [PageResponseEventAttendanceSummaryResponse](./api-schema-catalog.md#schema-pageresponseeventattendancesummaryresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponsePageResponseEventAttendanceSummaryResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-068"></a>

## POST /events/attendance

- 기능: 출석 이벤트 등록
- operationId: `createAttendanceEvent`; tag: `출석체크 이벤트 등록 및 설정`
- 현재 상태: **화면 호출 연결 확인**
- 인계 작업: [T10](./api-work-items.md#t10)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/event/api/attendance/attendance.api.ts:28](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.api.ts:28) — `postEvent`

같은 API 디렉터리의 DTO/parser 재사용 후보: [attendance.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.parser.ts), [attendance.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.dto.ts).

### 요청

path/query/header parameter 정의 없음.

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/CreateEventAttendanceRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [CreateEventAttendanceRequest](./api-schema-catalog.md#schema-createeventattendancerequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-069"></a>

## GET /events/attendance/{eventId}

- 기능: 출석 이벤트 조회
- operationId: `getAttendanceEvent`; tag: `출석체크 이벤트 등록 및 설정`
- 현재 상태: **화면 호출 연결 확인**
- 인계 작업: [T10](./api-work-items.md#t10)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/event/api/attendance/attendance.api.ts:25](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.api.ts:25) — `getDetail`

같은 API 디렉터리의 DTO/parser 재사용 후보: [attendance.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.parser.ts), [attendance.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `eventId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "eventId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseEventAttendanceResponse](./api-schema-catalog.md#schema-apiresponseeventattendanceresponse)
- data payload: [EventAttendanceResponse](./api-schema-catalog.md#schema-eventattendanceresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseEventAttendanceResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-070"></a>

## PATCH /events/attendance/{eventId}

- 기능: 출석 이벤트 수정
- operationId: `updateAttendanceEvent`; tag: `출석체크 이벤트 등록 및 설정`
- 현재 상태: **화면 호출 연결 확인**
- 인계 작업: [T10](./api-work-items.md#t10)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/event/api/attendance/attendance.api.ts:31](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.api.ts:31) — `patchEvent`

같은 API 디렉터리의 DTO/parser 재사용 후보: [attendance.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.parser.ts), [attendance.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `eventId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "eventId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/PatchEventAttendanceRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [PatchEventAttendanceRequest](./api-schema-catalog.md#schema-patcheventattendancerequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-071"></a>

## PATCH /events/attendance/{eventId}/configs

- 기능: 출석 이벤트 설정 수정
- operationId: `updateAttendanceEventConfigs`; tag: `출석체크 이벤트 등록 및 설정`
- 현재 상태: **화면 호출 연결 확인**
- 인계 작업: [T10](./api-work-items.md#t10)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/event/api/attendance/attendance.api.ts:44](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.api.ts:44) — `patchConfigs`

같은 API 디렉터리의 DTO/parser 재사용 후보: [attendance.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.parser.ts), [attendance.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `eventId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "eventId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/PatchEventAttendanceConfigRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [PatchEventAttendanceConfigRequest](./api-schema-catalog.md#schema-patcheventattendanceconfigrequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-072"></a>

## POST /events/attendance/{eventId}/configs/upload

- 기능: 출석 이벤트 설정 이미지 업로드
- operationId: `uploadAttendanceEventConfigImage`; tag: `출석체크 이벤트 등록 및 설정`
- 현재 상태: **화면 호출 연결 확인**
- 인계 작업: [T10](./api-work-items.md#t10)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/event/api/attendance/attendance.api.ts:55](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.api.ts:55) — `uploadConfigImage`

같은 API 디렉터리의 DTO/parser 재사용 후보: [attendance.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.parser.ts), [attendance.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `eventId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "eventId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "multipart/form-data": {
      "schema": {
        "type": "object",
        "properties": {
          "file": {
            "type": "string",
            "format": "binary"
          }
        },
        "required": [
          "file"
        ]
      }
    }
  }
}
```

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseUploadEventAttendanceConfigImageResponse](./api-schema-catalog.md#schema-apiresponseuploadeventattendanceconfigimageresponse)
- data payload: [UploadEventAttendanceConfigImageResponse](./api-schema-catalog.md#schema-uploadeventattendanceconfigimageresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseUploadEventAttendanceConfigImageResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-073"></a>

## GET /events/attendance/{eventId}/items

- 기능: 출석 이벤트 보상 조회
- operationId: `getAttendanceEventItems`; tag: `출석체크 이벤트 등록 및 설정`
- 현재 상태: **API·hook 정의, 화면 사용처 없음**
- 인계 작업: [T10](./api-work-items.md#t10)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/event/api/attendance/attendance.api.ts:34](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.api.ts:34) — `getItems`

같은 API 디렉터리의 DTO/parser 재사용 후보: [attendance.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.parser.ts), [attendance.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `eventId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "eventId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseListEventAttendanceItemResponse](./api-schema-catalog.md#schema-apiresponselisteventattendanceitemresponse)
- data payload: 배열&lt;[EventAttendanceItemResponse](./api-schema-catalog.md#schema-eventattendanceitemresponse)&gt;

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseListEventAttendanceItemResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-074"></a>

## PUT /events/attendance/{eventId}/items

- 기능: 출석 이벤트 보상 수정
- operationId: `updateAttendanceEventItems`; tag: `출석체크 이벤트 등록 및 설정`
- 현재 상태: **화면 호출 연결 확인**
- 인계 작업: [T10](./api-work-items.md#t10)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/event/api/attendance/attendance.api.ts:37](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.api.ts:37) — `putItems`

같은 API 디렉터리의 DTO/parser 재사용 후보: [attendance.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.parser.ts), [attendance.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.dto.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `eventId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "eventId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/UpdateEventAttendanceItemsRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [UpdateEventAttendanceItemsRequest](./api-schema-catalog.md#schema-updateeventattendanceitemsrequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-075"></a>

## GET /events/roulette

- 기능: 룰렛 이벤트 목록 조회
- operationId: `getRouletteEventList`; tag: `룰렛 이벤트 등록 및 설정`
- 현재 상태: **화면 호출 연결 확인**
- 인계 작업: [T10](./api-work-items.md#t10)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/event/api/roulette/roulette.api.ts:22](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.api.ts:22) — `getList`

같은 API 디렉터리의 DTO/parser 재사용 후보: [roulette.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.dto.ts), [roulette.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| query | `query` | 예 | [GetEventRouletteListRequest](./api-schema-catalog.md#schema-geteventroulettelistrequest) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "query",
    "in": "query",
    "required": true,
    "schema": {
      "$ref": "#/components/schemas/GetEventRouletteListRequest"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponsePageResponseEventRouletteSummaryResponse](./api-schema-catalog.md#schema-apiresponsepageresponseeventroulettesummaryresponse)
- data payload: [PageResponseEventRouletteSummaryResponse](./api-schema-catalog.md#schema-pageresponseeventroulettesummaryresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponsePageResponseEventRouletteSummaryResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-076"></a>

## POST /events/roulette

- 기능: 룰렛 이벤트 등록
- operationId: `createRouletteEvent`; tag: `룰렛 이벤트 등록 및 설정`
- 현재 상태: **화면 호출 연결 확인**
- 인계 작업: [T10](./api-work-items.md#t10)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/event/api/roulette/roulette.api.ts:28](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.api.ts:28) — `postEvent`

같은 API 디렉터리의 DTO/parser 재사용 후보: [roulette.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.dto.ts), [roulette.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.parser.ts).

### 요청

path/query/header parameter 정의 없음.

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/CreateEventRouletteRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [CreateEventRouletteRequest](./api-schema-catalog.md#schema-createeventrouletterequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-077"></a>

## GET /events/roulette/{eventId}

- 기능: 룰렛 이벤트 조회
- operationId: `getRouletteEvent`; tag: `룰렛 이벤트 등록 및 설정`
- 현재 상태: **화면 호출 연결 확인**
- 인계 작업: [T10](./api-work-items.md#t10)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/event/api/roulette/roulette.api.ts:25](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.api.ts:25) — `getDetail`

같은 API 디렉터리의 DTO/parser 재사용 후보: [roulette.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.dto.ts), [roulette.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `eventId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "eventId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseEventRouletteResponse](./api-schema-catalog.md#schema-apiresponseeventrouletteresponse)
- data payload: [EventRouletteResponse](./api-schema-catalog.md#schema-eventrouletteresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseEventRouletteResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-078"></a>

## PATCH /events/roulette/{eventId}

- 기능: 룰렛 이벤트 수정
- operationId: `updateRouletteEvent`; tag: `룰렛 이벤트 등록 및 설정`
- 현재 상태: **화면 호출 연결 확인**
- 인계 작업: [T10](./api-work-items.md#t10)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/event/api/roulette/roulette.api.ts:31](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.api.ts:31) — `patchEvent`

같은 API 디렉터리의 DTO/parser 재사용 후보: [roulette.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.dto.ts), [roulette.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `eventId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "eventId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/PatchEventRouletteRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [PatchEventRouletteRequest](./api-schema-catalog.md#schema-patcheventrouletterequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-079"></a>

## PATCH /events/roulette/{eventId}/configs

- 기능: 룰렛 이벤트 설정 수정
- operationId: `updateRouletteEventConfigs`; tag: `룰렛 이벤트 등록 및 설정`
- 현재 상태: **화면 호출 연결 확인**
- 인계 작업: [T10](./api-work-items.md#t10)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/event/api/roulette/roulette.api.ts:44](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.api.ts:44) — `patchConfigs`

같은 API 디렉터리의 DTO/parser 재사용 후보: [roulette.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.dto.ts), [roulette.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `eventId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "eventId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/PatchEventRouletteConfigRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [PatchEventRouletteConfigRequest](./api-schema-catalog.md#schema-patcheventrouletteconfigrequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-080"></a>

## POST /events/roulette/{eventId}/configs/upload

- 기능: 룰렛 이벤트 설정 이미지 업로드
- operationId: `uploadRouletteEventConfigImage`; tag: `룰렛 이벤트 등록 및 설정`
- 현재 상태: **화면 호출 연결 확인**
- 인계 작업: [T10](./api-work-items.md#t10)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/event/api/roulette/roulette.api.ts:55](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.api.ts:55) — `uploadConfigImage`

같은 API 디렉터리의 DTO/parser 재사용 후보: [roulette.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.dto.ts), [roulette.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `eventId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "eventId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "multipart/form-data": {
      "schema": {
        "type": "object",
        "properties": {
          "file": {
            "type": "string",
            "format": "binary"
          }
        },
        "required": [
          "file"
        ]
      }
    }
  }
}
```

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseUploadEventRouletteConfigImageResponse](./api-schema-catalog.md#schema-apiresponseuploadeventrouletteconfigimageresponse)
- data payload: [UploadEventRouletteConfigImageResponse](./api-schema-catalog.md#schema-uploadeventrouletteconfigimageresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseUploadEventRouletteConfigImageResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-081"></a>

## GET /events/roulette/{eventId}/items

- 기능: 룰렛 이벤트 보상 조회
- operationId: `getRouletteEventItems`; tag: `룰렛 이벤트 등록 및 설정`
- 현재 상태: **API·hook 정의, 화면 사용처 없음**
- 인계 작업: [T10](./api-work-items.md#t10)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/event/api/roulette/roulette.api.ts:34](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.api.ts:34) — `getItems`

같은 API 디렉터리의 DTO/parser 재사용 후보: [roulette.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.dto.ts), [roulette.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `eventId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "eventId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseListEventRouletteItemResponse](./api-schema-catalog.md#schema-apiresponselisteventrouletteitemresponse)
- data payload: 배열&lt;[EventRouletteItemResponse](./api-schema-catalog.md#schema-eventrouletteitemresponse)&gt;

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseListEventRouletteItemResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-082"></a>

## PUT /events/roulette/{eventId}/items

- 기능: 룰렛 이벤트 보상 수정
- operationId: `updateRouletteEventItems`; tag: `룰렛 이벤트 등록 및 설정`
- 현재 상태: **화면 호출 연결 확인**
- 인계 작업: [T10](./api-work-items.md#t10)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/event/api/roulette/roulette.api.ts:37](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.api.ts:37) — `putItems`

같은 API 디렉터리의 DTO/parser 재사용 후보: [roulette.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.dto.ts), [roulette.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.parser.ts).

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `eventId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "eventId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/UpdateEventRouletteItemsRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [UpdateEventRouletteItemsRequest](./api-schema-catalog.md#schema-updateeventrouletteitemsrequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-083"></a>

## GET /external/dashboard/daily

- 기능: 일별 현황 조회
- operationId: `getExternalDashboardDaily`; tag: `외부 대시보드`
- 현재 상태: **일치 호출 없음**
- 인계 작업: [T12](./api-work-items.md#t12)
- 인증 원문: `[]` (operation 지정)

외부 서비스 공유용. 인증 없이 호출한다.
date(yyyy-MM-dd)가 가리키는 하루의 사용자·OS·문의·상품 집계를 돌려준다. date는 필수다.
os.osCounts는 그날 로그인한 사용자의 OS 분포, item.salesRanks의 salesCount는 건수·salesQty는 수량이다.
rate는 퍼센트 숫자다. 현재는 고정된 Mock 값이며 statDate만 요청값을 돌려준다.

일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| query | `date` | 예 | `string` (date) | 기준 날짜 (yyyy-MM-dd) |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "date",
    "in": "query",
    "description": "기준 날짜 (yyyy-MM-dd)",
    "required": true,
    "schema": {
      "type": "string",
      "format": "date"
    },
    "example": "2026-08-31"
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

조회 성공

- 미디어 타입: `application/json`
- schema: [ApiResponseDailyDashboardResponse](./api-schema-catalog.md#schema-apiresponsedailydashboardresponse)
- data payload: [DailyDashboardResponse](./api-schema-catalog.md#schema-dailydashboardresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseDailyDashboardResponse"
  },
  "examples": {
    "success": {
      "summary": "조회 성공",
      "description": "success",
      "value": {
        "code": "SUCCESS",
        "message": "성공",
        "data": {
          "statDate": "2026-08-31",
          "user": {
            "totalCount": 12008,
            "newCount": 38,
            "loginCount": 1585,
            "onlineAvgCount": 180,
            "onlineMaxCount": 260
          },
          "os": {
            "osCounts": [
              {
                "os": "IOS",
                "count": 892,
                "rate": 56.3
              },
              {
                "os": "ANDROID",
                "count": 693,
                "rate": 43.7
              }
            ]
          },
          "inquiry": {
            "receivedCount": 19,
            "ongoingCount": 8,
            "resolvedCount": 15
          },
          "item": {
            "salesRanks": [
              {
                "rank": 1,
                "itemName": "테디베어 스웨터",
                "salesCount": 40,
                "salesQty": 52
              },
              {
                "rank": 2,
                "itemName": "클래식 보드(핑크)",
                "salesCount": 28,
                "salesQty": 31
              },
              {
                "rank": 3,
                "itemName": "호버 바이크",
                "salesCount": 17,
                "salesQty": 17
              }
            ]
          }
        }
      }
    }
  }
}
```

### 오류 응답

#### HTTP 400

```json
{
  "description": "date가 없거나 yyyy-MM-dd 형식이 아닌 경우",
  "content": {
    "application/json": {
      "examples": {
        "invalidDate": {
          "summary": "date 누락·형식 오류",
          "description": "invalidDate",
          "value": {
            "code": "INVALID_REQUEST",
            "message": "요청이 올바르지 않습니다.",
            "data": [
              {
                "field": "date",
                "reason": "널이어서는 안됩니다"
              }
            ]
          }
        }
      }
    }
  }
}
```

<a id="op-084"></a>

## GET /external/dashboard/monthly

- 기능: 월별 현황 조회
- operationId: `getExternalDashboardMonthly`; tag: `외부 대시보드`
- 현재 상태: **일치 호출 없음**
- 인계 작업: [T12](./api-work-items.md#t12)
- 인증 원문: `[]` (operation 지정)

외부 서비스 공유용. 인증 없이 호출한다.
date(yyyy-MM-dd)가 속한 달의 사용자·OS·문의·상품 집계를 돌려준다. date는 필수다.
month는 yyyy-MM 표기이고 startDate·endDate는 그 달의 1일과 말일이다.
섹션 필드의 의미는 일별 현황과 같다. 현재는 고정된 Mock 값이며 month·startDate·endDate만 요청값으로 계산한다.

일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| query | `date` | 예 | `string` (date) | 기준 날짜 (yyyy-MM-dd) |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "date",
    "in": "query",
    "description": "기준 날짜 (yyyy-MM-dd)",
    "required": true,
    "schema": {
      "type": "string",
      "format": "date"
    },
    "example": "2026-08-31"
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

조회 성공

- 미디어 타입: `application/json`
- schema: [ApiResponseMonthlyDashboardResponse](./api-schema-catalog.md#schema-apiresponsemonthlydashboardresponse)
- data payload: [MonthlyDashboardResponse](./api-schema-catalog.md#schema-monthlydashboardresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseMonthlyDashboardResponse"
  },
  "examples": {
    "success": {
      "summary": "조회 성공",
      "description": "success",
      "value": {
        "code": "SUCCESS",
        "message": "성공",
        "data": {
          "month": "2026-07",
          "startDate": "2026-07-01",
          "endDate": "2026-07-31",
          "user": {
            "totalCount": 11720,
            "newCount": 980,
            "loginCount": 8450,
            "onlineAvgCount": 171,
            "onlineMaxCount": 318
          },
          "os": {
            "osCounts": [
              {
                "os": "IOS",
                "count": 4760,
                "rate": 56.3
              },
              {
                "os": "ANDROID",
                "count": 3690,
                "rate": 43.7
              }
            ]
          },
          "inquiry": {
            "receivedCount": 545,
            "ongoingCount": 18,
            "resolvedCount": 531
          },
          "item": {
            "salesRanks": [
              {
                "rank": 1,
                "itemName": "테디베어 스웨터",
                "salesCount": 1120,
                "salesQty": 1435
              },
              {
                "rank": 2,
                "itemName": "클래식 보드(핑크)",
                "salesCount": 742,
                "salesQty": 810
              },
              {
                "rank": 3,
                "itemName": "호버 바이크",
                "salesCount": 505,
                "salesQty": 512
              }
            ]
          }
        }
      }
    }
  }
}
```

### 오류 응답

#### HTTP 400

```json
{
  "description": "date가 없거나 yyyy-MM-dd 형식이 아닌 경우",
  "content": {
    "application/json": {
      "examples": {
        "invalidDate": {
          "summary": "date 누락·형식 오류",
          "description": "invalidDate",
          "value": {
            "code": "INVALID_REQUEST",
            "message": "요청이 올바르지 않습니다.",
            "data": [
              {
                "field": "date",
                "reason": "널이어서는 안됩니다"
              }
            ]
          }
        }
      }
    }
  }
}
```

<a id="op-085"></a>

## GET /external/dashboard/summary

- 기능: 통합 현황 조회
- operationId: `getExternalDashboardSummary`; tag: `외부 대시보드`
- 현재 상태: **일치 호출 없음**
- 인계 작업: [T12](./api-work-items.md#t12)
- 인증 원문: `[]` (operation 지정)

외부 서비스 공유용. 인증 없이 호출한다.
사용자·OS·문의·상품 집계를 한 번에 돌려준다.
changeRate·rate는 퍼센트 숫자다 (5.2 = +5.2%). 현재는 고정된 Mock 값이다.

일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

path/query/header parameter 정의 없음.

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

조회 성공

- 미디어 타입: `application/json`
- schema: [ApiResponseExternalDashboardResponse](./api-schema-catalog.md#schema-apiresponseexternaldashboardresponse)
- data payload: [ExternalDashboardResponse](./api-schema-catalog.md#schema-externaldashboardresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseExternalDashboardResponse"
  },
  "examples": {
    "success": {
      "summary": "조회 성공",
      "description": "success",
      "value": {
        "code": "SUCCESS",
        "message": "성공",
        "data": {
          "user": {
            "totalCount": 11800,
            "statusCounts": [
              {
                "status": "ACTIVE",
                "count": 11230
              },
              {
                "status": "SUSPENDED",
                "count": 320
              },
              {
                "status": "WITHDRAWN",
                "count": 250
              }
            ],
            "newTodayCount": 37,
            "loginTodayCount": 1520,
            "onlineCount": 214,
            "changeRate": 5.2
          },
          "os": {
            "osCounts": [
              {
                "os": "IOS",
                "count": 7120,
                "rate": 55.5
              },
              {
                "os": "ANDROID",
                "count": 5210,
                "rate": 44.5
              }
            ]
          },
          "inquiry": {
            "totalCount": 3480,
            "ongoingCount": 42,
            "todayCount": 18,
            "todayOngoingCount": 7,
            "todayResolvedCount": 11,
            "changeRate": -2.1
          },
          "item": {
            "salesTodayCount": 96,
            "salesRanks": [
              {
                "rank": 1,
                "itemName": "테디베어 스웨터",
                "salesCount": 320
              },
              {
                "rank": 2,
                "itemName": "클래식 보드(핑크)",
                "salesCount": 210
              },
              {
                "rank": 3,
                "itemName": "호버 바이크",
                "salesCount": 150
              }
            ],
            "changeRate": 8.7
          }
        }
      }
    }
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-086"></a>

## GET /external/dashboard/weekly

- 기능: 주별 현황 조회
- operationId: `getExternalDashboardWeekly`; tag: `외부 대시보드`
- 현재 상태: **일치 호출 없음**
- 인계 작업: [T12](./api-work-items.md#t12)
- 인증 원문: `[]` (operation 지정)

외부 서비스 공유용. 인증 없이 호출한다.
date(yyyy-MM-dd)가 속한 ISO 주(월~일)의 사용자·OS·문의·상품 집계를 돌려준다. date는 필수다.
week는 yyyy-Www 표기이며 연말·연초에는 달력 연도와 다를 수 있다 (예: 2027-01-01 → 2026-W53).
섹션 필드의 의미는 일별 현황과 같다. 현재는 고정된 Mock 값이며 week·startDate·endDate만 요청값으로 계산한다.

일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| query | `date` | 예 | `string` (date) | 기준 날짜 (yyyy-MM-dd) |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "date",
    "in": "query",
    "description": "기준 날짜 (yyyy-MM-dd)",
    "required": true,
    "schema": {
      "type": "string",
      "format": "date"
    },
    "example": "2026-08-31"
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

조회 성공

- 미디어 타입: `application/json`
- schema: [ApiResponseWeeklyDashboardResponse](./api-schema-catalog.md#schema-apiresponseweeklydashboardresponse)
- data payload: [WeeklyDashboardResponse](./api-schema-catalog.md#schema-weeklydashboardresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseWeeklyDashboardResponse"
  },
  "examples": {
    "success": {
      "summary": "조회 성공",
      "description": "success",
      "value": {
        "code": "SUCCESS",
        "message": "성공",
        "data": {
          "week": "2026-W35",
          "startDate": "2026-08-24",
          "endDate": "2026-08-30",
          "user": {
            "totalCount": 11980,
            "newCount": 245,
            "loginCount": 4820,
            "onlineAvgCount": 176,
            "onlineMaxCount": 291
          },
          "os": {
            "osCounts": [
              {
                "os": "IOS",
                "count": 2714,
                "rate": 56.3
              },
              {
                "os": "ANDROID",
                "count": 2106,
                "rate": 43.7
              }
            ]
          },
          "inquiry": {
            "receivedCount": 132,
            "ongoingCount": 11,
            "resolvedCount": 128
          },
          "item": {
            "salesRanks": [
              {
                "rank": 1,
                "itemName": "테디베어 스웨터",
                "salesCount": 268,
                "salesQty": 342
              },
              {
                "rank": 2,
                "itemName": "클래식 보드(핑크)",
                "salesCount": 173,
                "salesQty": 190
              },
              {
                "rank": 3,
                "itemName": "호버 바이크",
                "salesCount": 119,
                "salesQty": 121
              }
            ]
          }
        }
      }
    }
  }
}
```

### 오류 응답

#### HTTP 400

```json
{
  "description": "date가 없거나 yyyy-MM-dd 형식이 아닌 경우",
  "content": {
    "application/json": {
      "examples": {
        "invalidDate": {
          "summary": "date 누락·형식 오류",
          "description": "invalidDate",
          "value": {
            "code": "INVALID_REQUEST",
            "message": "요청이 올바르지 않습니다.",
            "data": [
              {
                "field": "date",
                "reason": "널이어서는 안됩니다"
              }
            ]
          }
        }
      }
    }
  }
}
```

<a id="op-087"></a>

## GET /health

- 기능: health
- operationId: `health`; tag: `공통`
- 현재 상태: **일치 호출 없음**
- 인계 작업: [T13](./api-work-items.md#t13)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

path/query/header parameter 정의 없음.

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseMapStringString](./api-schema-catalog.md#schema-apiresponsemapstringstring)
- data payload: `object`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseMapStringString"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-088"></a>

## GET /maintenance

- 기능: getAll
- operationId: `getAll`; tag: `시스템 점검`
- 현재 상태: **기존 경로·계약 불일치** · F07
- 인계 작업: [T07](./api-work-items.md#t07)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

path/query/header parameter 정의 없음.

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseListMaintenanceResponse](./api-schema-catalog.md#schema-apiresponselistmaintenanceresponse)
- data payload: 배열&lt;[MaintenanceResponse](./api-schema-catalog.md#schema-maintenanceresponse)&gt;

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseListMaintenanceResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-089"></a>

## PATCH /maintenance

- 기능: update
- operationId: `update`; tag: `시스템 점검`
- 현재 상태: **기존 경로·계약 불일치** · F07
- 인계 작업: [T07](./api-work-items.md#t07)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

path/query/header parameter 정의 없음.

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/UpdateMaintenanceItemRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [UpdateMaintenanceItemRequest](./api-schema-catalog.md#schema-updatemaintenanceitemrequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-090"></a>

## PATCH /maintenance/off

- 기능: maintenanceOff
- operationId: `maintenanceOff`; tag: `시스템 점검`
- 현재 상태: **일치 호출 없음** · F07
- 인계 작업: [T07](./api-work-items.md#t07)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

path/query/header parameter 정의 없음.

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-091"></a>

## PATCH /maintenance/on

- 기능: maintenanceOn
- operationId: `maintenanceOn`; tag: `시스템 점검`
- 현재 상태: **일치 호출 없음** · F07
- 인계 작업: [T07](./api-work-items.md#t07)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

path/query/header parameter 정의 없음.

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-092"></a>

## GET /maintenance/one

- 기능: getOne
- operationId: `getOne`; tag: `시스템 점검`
- 현재 상태: **일치 호출 없음** · F07
- 인계 작업: [T07](./api-work-items.md#t07)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| query | `query` | 예 | [GetMaintenanceItemRequest](./api-schema-catalog.md#schema-getmaintenanceitemrequest) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "query",
    "in": "query",
    "required": true,
    "schema": {
      "$ref": "#/components/schemas/GetMaintenanceItemRequest"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseMaintenanceResponse](./api-schema-catalog.md#schema-apiresponsemaintenanceresponse)
- data payload: [MaintenanceResponse](./api-schema-catalog.md#schema-maintenanceresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseMaintenanceResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-093"></a>

## PATCH /maintenance/time

- 기능: maintenanceTime
- operationId: `maintenanceTime`; tag: `시스템 점검`
- 현재 상태: **일치 호출 없음** · F07
- 인계 작업: [T07](./api-work-items.md#t07)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

path/query/header parameter 정의 없음.

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/SetMaintenanceTimeRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [SetMaintenanceTimeRequest](./api-schema-catalog.md#schema-setmaintenancetimerequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-094"></a>

## PATCH /maintenance/version

- 기능: setVersion
- operationId: `setVersion`; tag: `시스템 점검`
- 현재 상태: **일치 호출 없음** · F07
- 인계 작업: [T07](./api-work-items.md#t07)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

path/query/header parameter 정의 없음.

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/SetMaintenanceVersionRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [SetMaintenanceVersionRequest](./api-schema-catalog.md#schema-setmaintenanceversionrequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-095"></a>

## GET /me

- 기능: getMe
- operationId: `getMe`; tag: `관리자`
- 현재 상태: **일치 호출 없음** · F06
- 인계 작업: [T06](./api-work-items.md#t06)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

path/query/header parameter 정의 없음.

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseMeResponse](./api-schema-catalog.md#schema-apiresponsemeresponse)
- data payload: [MeResponse](./api-schema-catalog.md#schema-meresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseMeResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-096"></a>

## GET /me/menus

- 기능: getMyMenus
- operationId: `getMyMenus`; tag: `메뉴`
- 현재 상태: **API만 정의** · F06
- 인계 작업: [T06](./api-work-items.md#t06)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/menus/api/menus.api.ts:20](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/menus/api/menus.api.ts:20) — `getMyList`

같은 API 디렉터리의 DTO/parser 재사용 후보: [menus.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/menus/api/menus.dto.ts), [menus.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/menus/api/menus.parser.ts).

### 요청

path/query/header parameter 정의 없음.

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseListMenuGroupResponse](./api-schema-catalog.md#schema-apiresponselistmenugroupresponse)
- data payload: 배열&lt;[MenuGroupResponse](./api-schema-catalog.md#schema-menugroupresponse)&gt;

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseListMenuGroupResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-097"></a>

## GET /menus

- 기능: getMenus
- operationId: `getMenus`; tag: `메뉴`
- 현재 상태: **API만 정의** · F06
- 인계 작업: [T06](./api-work-items.md#t06)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

실제 API 호출:

- [src/entities/menus/api/menus.api.ts:15](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/menus/api/menus.api.ts:15) — `getList`

같은 API 디렉터리의 DTO/parser 재사용 후보: [menus.dto.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/menus/api/menus.dto.ts), [menus.parser.ts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/menus/api/menus.parser.ts).

### 요청

path/query/header parameter 정의 없음.

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseListManagedMenuResponse](./api-schema-catalog.md#schema-apiresponselistmanagedmenuresponse)
- data payload: 배열&lt;[ManagedMenuResponse](./api-schema-catalog.md#schema-managedmenuresponse)&gt;

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseListManagedMenuResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-098"></a>

## PATCH /menus/{menuId}

- 기능: updateMenu
- operationId: `updateMenu`; tag: `메뉴`
- 현재 상태: **일치 호출 없음**
- 인계 작업: [T06](./api-work-items.md#t06)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `menuId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "menuId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/UpdateMenuRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [UpdateMenuRequest](./api-schema-catalog.md#schema-updatemenurequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-099"></a>

## PUT /menus/order

- 기능: updateMenuOrder
- operationId: `updateMenuOrder`; tag: `메뉴`
- 현재 상태: **일치 호출 없음**
- 인계 작업: [T06](./api-work-items.md#t06)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

path/query/header parameter 정의 없음.

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/UpdateMenuOrderRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [UpdateMenuOrderRequest](./api-schema-catalog.md#schema-updatemenuorderrequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-100"></a>

## GET /permissions

- 기능: getPermissionCatalog
- operationId: `getPermissionCatalog`; tag: `role-controller`
- 현재 상태: **일치 호출 없음**
- 인계 작업: [T06](./api-work-items.md#t06)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

path/query/header parameter 정의 없음.

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseListPermissionCategoryResponse](./api-schema-catalog.md#schema-apiresponselistpermissioncategoryresponse)
- data payload: 배열&lt;[PermissionCategoryResponse](./api-schema-catalog.md#schema-permissioncategoryresponse)&gt;

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseListPermissionCategoryResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-101"></a>

## GET /roles

- 기능: getRoles
- operationId: `getRoles`; tag: `role-controller`
- 현재 상태: **일치 호출 없음**
- 인계 작업: [T06](./api-work-items.md#t06)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

path/query/header parameter 정의 없음.

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseListRoleSummaryResponse](./api-schema-catalog.md#schema-apiresponselistrolesummaryresponse)
- data payload: 배열&lt;[RoleSummaryResponse](./api-schema-catalog.md#schema-rolesummaryresponse)&gt;

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseListRoleSummaryResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-102"></a>

## POST /roles

- 기능: createRole
- operationId: `createRole`; tag: `role-controller`
- 현재 상태: **일치 호출 없음**
- 인계 작업: [T06](./api-work-items.md#t06)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

path/query/header parameter 정의 없음.

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/CreateRoleRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [CreateRoleRequest](./api-schema-catalog.md#schema-createrolerequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseCreateRoleResponse](./api-schema-catalog.md#schema-apiresponsecreateroleresponse)
- data payload: [CreateRoleResponse](./api-schema-catalog.md#schema-createroleresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseCreateRoleResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-103"></a>

## DELETE /roles/{roleId}

- 기능: deleteRole
- operationId: `deleteRole`; tag: `role-controller`
- 현재 상태: **일치 호출 없음**
- 인계 작업: [T06](./api-work-items.md#t06)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `roleId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "roleId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-104"></a>

## GET /roles/{roleId}

- 기능: getRole
- operationId: `getRole`; tag: `role-controller`
- 현재 상태: **일치 호출 없음**
- 인계 작업: [T06](./api-work-items.md#t06)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `roleId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "roleId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

requestBody 정의 없음.

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseRoleDetailResponse](./api-schema-catalog.md#schema-apiresponseroledetailresponse)
- data payload: [RoleDetailResponse](./api-schema-catalog.md#schema-roledetailresponse)

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseRoleDetailResponse"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-105"></a>

## PATCH /roles/{roleId}

- 기능: updateRole
- operationId: `updateRole`; tag: `role-controller`
- 현재 상태: **일치 호출 없음**
- 인계 작업: [T06](./api-work-items.md#t06)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `roleId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "roleId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/UpdateRoleRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [UpdateRoleRequest](./api-schema-catalog.md#schema-updaterolerequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.

<a id="op-106"></a>

## PUT /roles/{roleId}/permissions

- 기능: updateRolePermissions
- operationId: `updateRolePermissions`; tag: `role-controller`
- 현재 상태: **일치 호출 없음**
- 인계 작업: [T06](./api-work-items.md#t06)
- 인증 원문: `[{"bearerAuth":[]}]` (전역 상속)

일치하는 method·path 호출은 조사 범위에서 찾지 못했다. 기존 비슷한 기능과 새 계약의 관계는 작업 항목에서 구분한다.

### 요청

| 위치 | 이름 | parameter 필수 | schema | 설명 |
| --- | --- | --- | --- | --- |
| path | `roleId` | 예 | `integer` (int64) | — |

parameter 원문(기본값·최소/최대·예시·직렬화 정보 포함):

```json
[
  {
    "name": "roleId",
    "in": "path",
    "required": true,
    "schema": {
      "type": "integer",
      "format": "int64"
    }
  }
]
```

body 원문(미디어 타입·필수 여부·multipart 각 part 포함):

```json
{
  "content": {
    "application/json": {
      "schema": {
        "$ref": "#/components/schemas/UpdateRolePermissionsRequest"
      }
    }
  },
  "required": true
}
```

요청 DTO: [UpdateRolePermissionsRequest](./api-schema-catalog.md#schema-updaterolepermissionsrequest).

### 성공 응답

#### HTTP 200

OK

- 미디어 타입: `*/*`
- schema: [ApiResponseVoid](./api-schema-catalog.md#schema-apiresponsevoid)
- data payload: `상세 미지정`

```json
{
  "schema": {
    "$ref": "#/components/schemas/ApiResponseVoid"
  }
}
```

### 오류 응답

이 operation에는 비-2xx 응답이 **문서화되지 않았다**. 상태 코드·에러 코드·data 형태를 임의로 추가하지 않는다. 공통 오류 정규화는 재사용하며 실제 계약은 후속 확인한다.
