# 최종 요약

## 제공 사항

Swagger의 **75개 path, 106개 operation**을 현재 `sy-main@4b0b7db45aa9`와 대조했다. **74개는 method·path가 일치하는 API 함수가 있고, 32개는 일치 호출을 찾지 못했다.** 32개 중 `GET/PATCH /maintenance`는 기존 기능이 있으나 기본 경로·DTO가 다르다. 이 숫자는 정상 작동률이 아니다.

일치하는 74개 중 정적 호출 흐름으로 화면 사용을 확인한 것은 37개, API·hook까지만 있고 화면 사용처를 찾지 못한 것은 35개, API만 정의한 메뉴 조회는 2개다. 화면 미사용은 의도된 범위 제한일 수 있으며 모두 결함이라고 판단하지 않는다.

전체 method·path, 요청·성공 응답, 소스 위치와 상태는 [전체 대조표](./unknown/api-path-matrix.md)에 기록했다. 원본은 [Swagger UI](https://admin-api.oasis.shovvel.com:8443/swagger-ui/index.html#/)와 [OpenAPI JSON](https://admin-api.oasis.shovvel.com:8443/v3/api-docs)이며 2026-09-28에 조회했다.

## 주요 발견

### F01 — 시민제안 처리 API와 검토 결과 응답이 현재 명세에 연결되지 않음

- Swagger: `PATCH /citizen/proposals/{proposalId}`에 `status`, `PATCH /citizen/proposals/{proposalId}/review-result`에 `reviewResult`를 보낸다. 후자는 최대 5,000자다.
- 현재: `POST /v1/cp/proposals/{id}/process`에 화면 상태값과 `reviewComment` 등을 전송한다. 해당 POST는 이번 Swagger에 없다. 현재 화면에서도 이 mutation을 호출한다.
- 상세 응답의 `reviewResult`가 DTO에 없고 parser는 `reviewComment: ""`로 반환하여 서버 검토 결과를 표시하지 못한다.
- `GET /citizen/proposals/summary`와 `GET /citizen/votes/summary`도 미연결이다. 현재 KPI는 목록의 `total`만 사용한다.
- 근거: [src/entities/cp-proposal/api/cp-proposal.api.ts:13](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/cp-proposal/api/cp-proposal.api.ts:13), [src/entities/cp-proposal/api/cp-proposal.dto.ts:58](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/cp-proposal/api/cp-proposal.dto.ts:58), [src/entities/cp-proposal/api/cp-proposal.parser.ts:51](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/cp-proposal/api/cp-proposal.parser.ts:51), [src/pages/cp-proposal/hook/use-cp-proposal-detail-process.tsx:45](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/pages/cp-proposal/hook/use-cp-proposal-detail-process.tsx:45).

### F02 — 사용자 상태 응답 enum과 포인트 차감 요청 enum 차이

- 사용자 조회의 Swagger 응답은 `ACTIVE / SUSPENDED / WITHDRAWN`; 현재 응답 schema는 `ACTIVE / SUSPEND / WITHDRAWN`을 공유한다. 명세대로 `SUSPENDED`가 오면 응답 파싱이 실패한다.
- 상태 변경 요청은 Swagger도 `SUSPEND`다. 요청·응답의 enum을 구분해야 하는 계약이다.
- 포인트 조정은 `RECHARGE / DEDUCT`를 지원하지만 현재 `USER_POINT_DIRECTION`에는 `RECHARGE`만 있어 차감 요청을 만들 수 없다. amount의 정수 검증도 빠져 있다.
- 근거: [src/entities/users/model/admin-user.enum.ts:1](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/model/admin-user.enum.ts:1), [src/entities/users/api/admin-users.dto.ts:15](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.dto.ts:15).

### F03 — 이용내역 응답 필드명과 필수 검색 기간 차이

- 두 Swagger 응답 `PointHistoryResponse / ItemHistoryResponse`의 필드는 `objectName`이다. 현재 DTO는 `itemName`을 필수 nullable 필드로 기대하므로 명세대로 오는 목록 항목은 파싱에 실패한다.
- Swagger의 `startDate/endDate`는 필수인데 현재 schema는 생략을 허용한다. `by`도 포인트 `USER_ID/USER_NAME`, 아이템 `USER_ID/USER_NAME/ITEM_NAME`과 달리 임의 문자열이다.
- 근거: [src/entities/usage/api/admin-usage.dto.ts:14](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/usage/api/admin-usage.dto.ts:14), [src/entities/usage/api/admin-usage.dto.ts:49](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/usage/api/admin-usage.dto.ts:49), [src/entities/usage/api/admin-usage.parser.ts:4](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/usage/api/admin-usage.parser.ts:4).

### F04 — 영상 multipart 요청의 필수 data 부분 누락

- 등록은 `data:{name, description?}`와 `file`이 필요하고 수정은 `data`가 필수이며 `file`은 선택이다.
- 현재 등록·수정 모두 `file`만 넣고 파일을 필수로 받는다. 현재 Swagger 기준으로 필수 `data.name`을 전송할 수 없다.
- 단, 코드에는 “사용자 확정 계약: 등록·수정 모두 file만 전송” 주석이 있다. **현재 명세와 과거 확정 계약의 충돌**로 기록하며 어느 쪽을 바꿀지는 이번 조사에서 결정하지 않았다.
- 영상 상세는 Swagger가 `ApiResponseObject`로만 기술하고, 현재는 `string | null`만 허용한다. 실제 상세 구조는 명세만으로 확정할 수 없다.
- 근거: [src/entities/video/api/video.api.ts:38](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.api.ts:38), [src/entities/video/api/video.dto.ts:34](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.dto.ts:34), [src/entities/video/api/video.parser.ts:7](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.parser.ts:7).

### F05 — Void 성공 응답에 문자열을 강제하는 parser

- 문의 삭제·상태 변경·답변 등록/수정/삭제 5개, 문의 타입 등록/수정/삭제 3개, 사용자 권한 부여 1개는 Swagger상 `ApiResponseVoid`이다.
- 현재 문의 mutation 공통 parser와 사용자 권한 parser는 `z.string()`이다. 공통 `ApiClient`가 `data:null`을 `undefined`로 바꾸므로, 서버가 빈 성공 payload를 반환하면 성공한 작업도 파싱 오류가 된다. 문의 쪽은 이어지는 `onSuccess` 캐시 갱신도 실행되지 않는다.
- 이 명세의 `ApiResponseVoid.data`는 빈 schema `{}`이며 실제 응답을 호출하지 않았으므로 서버가 반드시 null을 반환한다고 단정하지 않는다. **문자열 전용 구현과 Void 계약의 불일치 및 null일 때의 실패 경로**가 확인된 사항이다.
- 근거: [src/entities/inquiries/api/inquiry.dto.ts:76](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.dto.ts:76), [src/entities/inquiries/model/inquiry-mutation-options.ts:24](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/model/inquiry-mutation-options.ts:24), [src/entities/users/api/admin-users.parser.ts:7](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.parser.ts:7), [src/shared/api/common/api-result/api-result.mapper.ts:13](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/shared/api/common/api-result/api-result.mapper.ts:13).

### F06 — 메뉴 트리 DTO와 로그인 후 메뉴·권한 초기화 미완성

- `GET /menus`의 `children`은 재귀적인 `ManagedMenuResponse[]`다. 현재 `string[]`이므로 하위 메뉴 객체가 있으면 parser가 거부한다.
- `GET /menus`, `GET /me/menus`는 API만 정의되어 있고 실제 화면·로그인 흐름에서 호출하지 않는다. `GET /me`도 미구현이다.
- 로그인 응답 `accessToken` 저장은 구현되어 있으나 `useAuth`에 메뉴 연결 TODO가 남아 있다. 현재 메뉴는 로컬 navigation 설정을 사용한다.
- 관리자 계정·역할·권한의 기존 `/v1/admins*` 호출을 `/accounts`, `/roles`, `/permissions`, `/me` 구현으로 세지 않았다.
- 근거: [src/entities/menus/api/menus.dto.ts:10](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/menus/api/menus.dto.ts:10), [src/features/auth/use-auth.ts:19](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/features/auth/use-auth.ts:19), [src/features/auth/model/auth-session.ts:69](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/features/auth/model/auth-session.ts:69), [src/widgets/side-navigation/lib/build-navigation-items.ts:32](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/widgets/side-navigation/lib/build-navigation-items.ts:32).

### F07 — 점검 API는 URL만 바꿔도 계약이 맞지 않음

- 현재 기본 경로는 `/v1/maintenance`이며 `VITE_SYNTHORIA_CONFIG_RESOURCE`로 재정의 가능하다. 확인한 `.env`에는 해당 재정의가 없다. 실제 배포 환경의 외부 주입 여부는 미확인이다.
- 현재 업데이트는 `{key,value}`를 항목별 PATCH로 보내지만 Swagger는 `{config:[{key,value}]}`를 받는다.
- 응답도 Swagger는 `key/value`, 현재 DTO는 `configKey/configValue`다.
- `/maintenance/one`, `/version`, `/time`, `/on`, `/off`의 전용 호출도 찾지 못했다.
- 근거: [src/entities/maintenance/api/maintenance.api.ts:7](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/maintenance/api/maintenance.api.ts:7), [src/entities/maintenance/api/maintenance.dto.ts:11](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/maintenance/api/maintenance.dto.ts:11).

### F08 — 공지사항 일괄 처리·댓글 API 및 고정 개수 필드 누락

- `PATCH /admin/news/batch`, `GET /admin/news/{newsId}/comments`, `DELETE /admin/news/{newsId}/comments/{commentId}` 호출·전용 DTO·hook을 찾지 못했다.
- 목록 응답의 Swagger 필드는 `isPinnedCount`인데 DTO는 `pinnedItemCount`다. parser가 실제 필드를 보존하지 않고, 화면은 반환 items를 세어 고정 수를 계산한다. 현재 “고정 공지는 매 페이지 반환” 설명에서는 값이 같을 수 있으나 서버 count 계약은 사용하지 않는다.
- 근거: [src/entities/news/api/news.api.ts:30](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/news/api/news.api.ts:30), [src/entities/news/api/news.dto.ts:36](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/news/api/news.dto.ts:36), [src/pages/cp-news/hook/use-cp-news-list-controller.ts:36](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/pages/cp-news/hook/use-cp-news-list-controller.ts:36).

### F09 — 이미 연결된 요청도 필수값·정수·부분 수정 범위가 다름

- 아이템 생성: Swagger의 필수 name, description, category IDs, gender, status, saleAmount, newBadgeUntil 등에 현재 DTO는 null을 허용한다. 실제 등록 폼은 ID와 금액의 숫자 해석만 검사하여 필수값이 빈 요청을 만들 수 있다. saleAmount도 소수를 허용한다.
- 이벤트: PATCH의 code/startAt/endAt/isActive는 Swagger에서 선택 필드지만 현재 DTO는 모두 필수다. 보상 objectAmount와 룰렛 chance는 Swagger integer인데 현재 z.number()로 소수를 허용한다.
- 플레이리스트: name은 필수인데 현재 null을 허용한다. 문의 타입 목록은 Swagger Pageable.sort가 있으나 현재 query DTO는 page/size만 있다.
- 소포 발송의 userId/itemId/amount도 Swagger integer에 비해 현재 number 검증이 느슨하다.
- 이런 차이는 endpoint가 전혀 없다는 뜻이 아니라 **문서화된 요청 범위를 온전히 표현·검증하지 못하는 부분**이다.
- 근거: [src/entities/items/api/items.dto.ts:59](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.dto.ts:59), [src/pages/item/lib/item-form.model.ts:116](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/pages/item/lib/item-form.model.ts:116), [src/entities/event/api/event.dto.ts:60](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/event.dto.ts:60), [src/entities/event/api/roulette/roulette.dto.ts:15](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.dto.ts:15), [src/entities/video/api/playlist.dto.ts:35](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.dto.ts:35), [src/entities/inquiries/api/inquiry-type.dto.ts:7](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry-type.dto.ts:7), [src/entities/parcels/api/parcel.dto.ts:37](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/parcels/api/parcel.dto.ts:37).

### F10 — 일부 응답 필드·명세 상세는 추가 확인 필요

- `ParcelHistoryResponse.amount`가 Swagger schema에는 있지만 DTO에는 없다. 다만 Swagger의 목록 응답 예시도 amount를 생략하므로 실제 노출·필수 여부를 단정할 수 없다.
- 영상 상세 `ApiResponseObject.data`, 여러 Void payload는 schema가 구체적이지 않다.
- `GET /admin/users` 사용자 목록, refresh token API, 다수 `/v1/cp/*`, DAO·FAQ·기존 통계·Agora API는 소스에 있거나 UI에 필요해 보이더라도 이번 Swagger에서 확인되지 않았다. 서버에서 제거되었다고 판단하지 않는다.
- 근거: [src/entities/parcels/api/parcel.dto.ts:50](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/parcels/api/parcel.dto.ts:50), [src/entities/video/api/video.parser.ts:7](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.parser.ts:7), [src/entities/users/api/users.api.ts:24](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/users.api.ts:24), [src/entities/auth/api/auth.api.ts:15](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/auth/api/auth.api.ts:15).

## 일치 호출이 없는 32개 operation

| 영역 | 수 | 범위 |
| --- | ---: | --- |
| 관리자 계정·역할·권한·내 정보 | 10 | accounts 2, roles/permissions 7, me 1 |
| 메뉴 변경 | 2 | 메뉴 수정, 순서 변경 |
| 시스템 점검 | 7 | 전체·단건 조회, 설정·버전·시간·on/off |
| 외부 대시보드 | 4 | summary/daily/weekly/monthly |
| 시민제안·투표 | 4 | 제안 상태·검토 결과 수정, 제안·투표 summary |
| 공지사항 | 3 | 일괄 수정, 댓글 목록·삭제 |
| 감사 로그 | 1 | GET /admin/audit |
| 상태 확인 | 1 | GET /health |

각 요청 body·query와 응답은 전체 대조표의 “일치 호출 없음” 항목을 참조한다. `/health` 및 외부 대시보드처럼 화면에서 반드시 사용해야 하는지는 별도 제품 요구사항이다.

## 연결 패턴과 재사용 자산

| 패턴 | 현재 상태 | 관련 자산 |
| --- | --- | --- |
| Bearer 토큰·JSON envelope·오류 변환 | 구현됨 | shared/api/axios-instance.ts, api-client.ts, common/response.dto.ts |
| 목록·상세·mutation과 캐시 갱신 | 구현됨 | entities/*/model/*query-options.ts, *mutation-options.ts |
| 공통 pagination·Zod parser | 구현됨 | PageResponseDto, createPageResponseSchema |
| 반복 query 배열 전송 | 구현됨 | paramsSerializer.indexes=null |
| 단일 파일 multipart | 구현됨 | 아이템·이벤트 이미지, 영상 file 업로드 |
| JSON data와 file을 함께 보내는 multipart | Swagger 영상 계약에 해당하는 구현 없음 | 기존 video FormData 확장 검토 대상 |
| XLSX 바이너리·JSON 오류·파일명 처리 | 구현됨 | parcels/api/parcel-export.response.ts |
| 재귀 메뉴 트리 + 로그인 후 me/권한/메뉴 초기화 | 미완성 | menus API, auth TODO, 로컬 navigation |
| 집계 summary·별도 처리 결과 mutation | 해당 endpoint 연결 없음 | CP 목록/상세 hook 확장 검토 대상 |

공통 envelope/pagination을 새로 만드는 작업은 필요하지 않다. Swagger 대부분은 기존 공통 응답 계층을 재사용할 수 있다. 신규 기능·공용화 범위는 이번 검토에서 결정하지 않았다.

## 화면 연결과 mock 확인

- 사용자 5, 이용내역 2, 영상·플레이리스트 11, 문의·타입 11, 소포 3: 총 32개는 API·DTO·hook이 있으나 src/pages/features/widgets/app에서 화면 소비를 찾지 못했다.
- 추가로 아이템 최신 ID 조회 1개, 출석·룰렛 보상 단독 GET 2개는 hook이 있지만 화면에서 호출하지 않는다. 아이템 등록 ID는 수동 입력이고 이벤트 보상은 상세 GET의 items를 사용하므로 단독 GET 미사용 자체를 결함으로 보지 않는다.
- 메뉴 조회 2개는 API만 있고 로그인·메뉴 사용처가 없다.
- `VITE_ENVIRONMENT=dev`일 때 MSW가 동작하며 `/citizen/*`도 포함한다. 따라서 개발 화면에서 제안·투표가 보이는 사실만으로 실제 서버 연결 성공을 입증할 수 없다. 조사한 .env에서는 해당 dev 설정이 주석이다.
- 근거: [src/app/router/routes.tsx:40](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/app/router/routes.tsx:40), [src/app/mock-api-policy.ts:1](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/app/mock-api-policy.ts:1), [src/app/index.tsx:11](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/app/index.tsx:11), [src/mocks/cp-proposal.handlers.ts:124](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/mocks/cp-proposal.handlers.ts:124), [src/mocks/cp-vote.handlers.ts:77](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/mocks/cp-vote.handlers.ts:77).

## 변경 이유와 영향 영역

요청된 API 검토 결과를 남기기 위해 이 세션의 문서만 추가했다. 애플리케이션·패키지·Git 상태를 변경하는 작업과 실제 업무 API 호출은 수행하지 않았다.

## 검증

| 수행 내용 | 결과 |
| --- | --- |
| Swagger UI/initializer/config/OpenAPI 문서 GET | 성공, 단일 /v3/api-docs 명세 |
| 전체 method·path와 API 모듈 대조 | 75 paths / 106 operations / 74 일치 / 32 불일치·부재 |
| src 전체 endpoint 후보 및 사용처 재검색 | 메뉴·화면 미연결 및 별도/기존 호출 확인 |
| DTO·parser·query/mutation·controller 대조 | F01~F10 기록 |
| 소스 변경 여부 확인 | 조사 종료 전 HEAD 동일, 소스 diff 없음 |
| lint/test/build·브라우저·실서버 업무 호출 | 미실행: 정적 검토, 소스 변경 없음 |

텍스트 검색의 복합 패턴과 임시 AST 실행 시도는 정책 guard에서 차단되어 실행되지 않았다. 허용된 rg·cat으로 소스를 읽어 대조를 완료했다. 이 실패를 검증 성공으로 계산하지 않았다.

## 산출물

- [계획](./plan.md)
- [전체 API 대조표 및 계약](./unknown/api-path-matrix.md)

## 알려진 제한

실제 서버 데이터·인증 권한·배포 환경·네트워크 성공은 검증하지 않았다. 현재 Swagger와 소스의 차이를 기록했으며, 모든 응답의 optional/null 의미나 문서에 없는 업무 규칙을 확정하지 않았다. 화면 연결은 정적 호출 참조를 의미한다.

## 다음 단계

수정에 착수한다면 현재 사용 중인 시민제안 처리·검토 결과, 아이템 필수값을 먼저 검토하고, 화면 연결 전 사용자/이용내역/메뉴/영상/빈 성공 응답 계약을 정리하는 순서를 권고한다. Swagger와 과거 확정 주석이 충돌하는 영상 multipart, 상세 응답 등은 실제 계약을 확인한 뒤 변경해야 한다. 이번 요청에서는 구현하지 않았다.

