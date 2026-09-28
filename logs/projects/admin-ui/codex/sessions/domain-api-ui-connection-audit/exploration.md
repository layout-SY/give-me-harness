# Proposal·Vote 기준 UI와 Logic 연결 패턴 비교

## 결론

현재 sy-main(0e7c671b511f8e6cecebcce8946a13ee24d8c339)에서 proposal·vote의 라우팅된 UI와 Logic은 연결되어 있다. 미연결 구현물은 모두 같은 패턴이 아니며 아래 세 종류로 나뉜다.

1. 문의, 아이템·카테고리, 영상·재생목록, 관리자 회원, 관리자 사용 이력, 기존 CP 공지는 ApiClient → ApiResult → unwrap → parser → TanStack Query 계열이다. 계층 책임은 proposal·vote와 같지만 반환 데이터·캐시·페이지 전환 방식은 일부 다르다.
2. 기존 DAO·이벤트·FAQ·관리자 설정·프로필·대시보드·매출·맵·유지보수·기존 회원·기존 사용 이력은 대부분 Axios 직접 호출 계열이며 같은 수준의 Query hook·parser·controller가 확인되지 않는다. DAO discussion만 ApiResult를 사용하지만 상위 Query 연결은 없다.
3. 인증은 useApi를 통한 명령형 흐름이다. 목록·상세 Query 패턴과 별도로 비교해야 한다.

관련 기존 테스트 8개 파일, 69개 테스트가 모두 통과했다. 이는 저장소의 DTO·전송·캐시 동작 검증이며 실제 백엔드와 화면의 종단간 검증은 아니다.

## 조사 범위와 기준

- 작업 위치: /Users/okand/SynologyDrive/asan-metaverse-admin-ui
- 역할: logic, 읽기 전용 코드 조사와 기존 테스트 실행
- 사용자 요청: 기존 proposal/vote의 UI·Logic 연결성을 확인하고 미연결 Logic과 패턴을 비교
- 적용 스킬: task-role-routing, git-branch-strategy, data-fetch-layer, recipe-data-fetch, documentation
- 소스·패키지·설정·Git 변경 없음. 기존 자기 세션의 기록만 갱신
- “같은 패턴”을 HTTP 계약의 동일성으로 해석하지 않고 계층 책임, 요청/응답 처리, Query 상태, 취소, 캐시, UI 연결 경계로 나누어 비교

## 기준 UI의 실제 호출 경로

### Proposal

경로: /cp/proposals 및 /cp/proposals/:proposalId.

- src/app/router/routes.tsx에서 CpProposalListPage와 CpProposalDetailPage를 등록한다.
- src/pages/cp-proposal/ui/cp-proposal-list-page.tsx는 controller를 생성하여 view에 주입한다.
- src/pages/cp-proposal/hook/use-cp-proposal-list-controller.tsx는 검색 상태·조회 데이터·처리 동작·페이지 이동을 조합한다.
- use-cp-proposal-list-data.tsx → useCpProposalListQuery → cpProposalClient.getList → /citizen/proposals.
- use-cp-proposal-detail-controller.tsx → useCpProposalDetailQuery → cpProposalClient.getDetail → /citizen/proposals/:id.
- 목록의 상태·부서 저장과 상세 처리 의견 저장은 각각 process hook → useCpProposalProcessMutation → POST /v1/cp/proposals/:id/process로 이어진다.
- view의 onSave와 버튼 disabled/isSaving 연결을 확인했다.
- 목록은 이전 결과를 placeholderData로 유지하고 isPlaceholderData 동안 행 선택·처리 대상을 제한한다.
- 조회 응답은 parser에서 숫자 ID를 문자열로, API 상태 UNDER_REVIEW/REJECTED를 화면 상태 REVIEWING/RETURNED로 변환한다.
- 저장 성공은 진행 중 목록·상세 조회를 취소하고 상세 캐시를 응답으로 갱신한 뒤 목록을 무효화한다.

근거: src/pages/cp-proposal/hook/use-cp-proposal-list-controller.tsx:8, src/entities/cp-proposal/hook/use-cp-proposal-list-query.ts:15, src/entities/cp-proposal/hook/use-cp-proposal-process-mutation.ts:15, src/entities/cp-proposal/api/cp-proposal.api.ts:13.

### Vote

경로: /cp/votes 및 /cp/votes/:voteId.

- Page → useCpVoteListController → query-state/list-data → useCpVoteListQuery → cpVoteClient.getList → /citizen/votes.
- 상세 버튼에서 /cp/votes/:voteId로 이동하고 detail controller → useCpVoteDetailQuery → /citizen/votes/:id를 호출한다.
- 목록 이전 데이터 유지·placeholder 시 선택 제한·재시도·오류 Dialog를 연결한다.
- 상세 경로 ID를 양의 정수로 검증하고 숫자로 정규화한 query key를 사용한다.
- 현재 cp-vote는 목록·상세 조회만 구현되어 있다. 투표 생성·종료 mutation을 연결한 구조로 간주하지 않는다.
- src/entities/dao/api/vote/vote.api.ts의 생성·종료·강제 종료 API는 별도 미연결 구현이다.

근거: src/pages/cp-vote/hook/use-cp-vote-list-controller.tsx:9, src/entities/cp-vote/hook/use-cp-vote-detail-query.ts:10, src/entities/cp-vote/api/cp-vote.api.ts:20.

## 미연결 Logic 비교

| 구현물 | 공통점 | 차이와 현재 미연결 경계 |
| --- | --- | --- |
| inquiries | 목록 hook·placeholderData·pageCount 계산은 vote와 거의 같은 구조, 상세 ID 검증도 숫자 key 사용 | mutationOptions를 model로 분리. 문자열 응답을 상세에 넣지 않고 재조회. 해당 페이지·controller 없음 |
| items / item-category | ApiClient 주입, ApiResult unwrap, Zod parser, Query key, signal, query/mutation hook | queryOptions·mutationOptions 분리. pageCount 미계산. nullable 필드/상세 및 카테고리 배열 응답. 페이지·controller 없음 |
| video / playlist | 같은 Query·parser·signal·캐시 구조 | queryOptions·mutationOptions 분리. 영상 상세는 string 또는 null, 목록도 null 가능. 0 page를 허용. 페이지·controller 없음 |
| admin-users | 상세 ID 검사, queryOptions와 mutationOptions, 오류·취소 전달 | int64 ID 문자열 정규화. 포인트/상태 mutation 응답은 void. 권한 API는 코드상 no-op 계약. 페이지·controller 없음 |
| admin-usage | queryOptions, 응답 parser, signal, 조회 조건별 key | 조회 전용. 검색값 정규화. pageCount와 표시용 데이터 가공 없음. 페이지·controller 없음 |
| cp-notice | hook 안에 useQuery/useMutation 설정, parser, 상세 setQueryData | /v1/cp/notices hook 소비자가 없음. 현재 /cp/news는 /admin/news를 사용 |
| DAO | 도메인별 API factory 분리는 있음 | proposal/vote는 Axios 직접 호출. discussion만 ApiResult. Query hook·Zod 응답 parser 연결이 없음. 이미지 삭제 hook도 소비자가 없음 |
| 이벤트·FAQ·관리자 설정·프로필·기존 대시보드·매출·맵·유지보수·기존 회원·기존 사용 이력 | 도메인 API/DTO 파일 분리는 있음 | 대부분 Axios에서 data를 반환하거나 void로 종료. 현재 기준과 같은 Query·parser·controller 층은 없음 |
| auth 일부 | 로그인/갱신 DTO parser와 signal을 사용 | useApi 명령형 실행, Query 캐시 흐름과 다름. refreshAuthentication 소비자와 비밀번호 API 연결 없음 |

신규 Query 계열은 애플리케이션 QueryClient의 공통 오류 보고·재시도 정책을 사용하도록 작성되어 있다. 실제 UI가 hook을 사용하기 전에는 요청이 실행되지 않는다.

## UI 연결 시 보존해야 할 차이

### 1. 파일 분리는 다르지만 계층 책임은 같다

proposal·vote는 useQuery 설정을 hook 안에 두고, items/video/admin-users/admin-usage는 model의 queryOptions를 hook이 전달한다. inquiries는 조회는 hook 안, 변경은 model의 mutationOptions에 둔다.

이 분리 자체는 불일치 결함이 아니다. 현재 연결된 news도 model/news-query-options.ts와 news-mutation-options.ts 구조를 사용하므로 새 Logic이 UI 연결에 사용할 수 없는 별도 구조는 아니다.

근거: src/entities/items/model/item-query-options.ts:11, src/entities/items/hook/use-item-list-query.ts:6, src/entities/news/model/news-query-options.ts:10, src/pages/cp-news/hook/use-cp-news-list-controller.ts:27.

### 2. 페이지 전환 동작이 다르다

- proposal·vote·inquiries: placeholderData로 이전 페이지 유지.
- items·video·playlist·admin-users 탈퇴 목록·admin-usage: placeholderData 설정 없음.
- app/providers/query-client.ts에도 기본 placeholderData 설정은 없다.

따라서 캐시가 없는 새 페이지를 조회할 때 표시·선택 상태가 동일하다고 간주할 수 없다. 동일 UX가 요구되면 이전 데이터 유지 여부와 오래된 행의 액션 제한을 함께 정해야 한다.

### 3. 데이터 반환 형태와 페이지 수가 다르다

- proposal·vote·inquiries parser는 pageCount를 계산한다.
- items·video·playlist·admin-users·admin-usage는 기본 PageResponseDto(items/total/page/size)를 반환하며 pageCount를 계산하지 않는다.
- proposal은 화면 표시 모델로 상태·ID·필드 이름을 변환한다. 다른 도메인은 주로 검증한 DTO를 그대로 노출한다.
- items 응답은 page/size에 0을 허용하므로 proposal의 total/size 계산을 무조건 복사하면 안 된다.
- video·playlist는 목록 전체가 null일 수 있고 영상 상세는 객체가 아닌 string | null이다.
- item category 목록은 페이지가 아닌 배열 또는 null이다.

데이터가 없는 성공 응답과 로딩 중 undefined를 구분하고, 테이블 props로 변환하는 책임이 연결 단계에 남아 있다.

근거: src/entities/cp-proposal/api/cp-proposal.parser.ts:23, src/entities/items/api/items.parser.ts:9, src/entities/video/api/video.dto.ts:45, src/entities/usage/api/admin-usage.parser.ts:4.

### 4. 변경 응답과 캐시 갱신이 다르다

- proposal은 처리 응답이 상세 모델이므로 setQueryData로 상세를 갱신한다.
- inquiries는 문자열 응답, admin-users는 void 응답을 상세 캐시에 넣지 않고 취소 후 invalidate한다.
- items 수정 응답은 상세와 필드가 다르므로 재조회한다.
- video 변경은 영상 목록·상세 외에 해당 영상 정보를 가진 재생목록 상세도 갱신한다.
- 삭제 시 상세 캐시를 제거한다.
- admin-users 권한 부여는 코드에 no-op 계약이 명시되어 있고 캐시 갱신도 하지 않는다.

이는 도메인 계약에 따른 차이다. proposal의 캐시 업데이트를 일괄 적용할 근거가 없다.

근거: src/entities/items/model/item-mutation-options.ts:27, src/entities/inquiries/model/inquiry-mutation-options.ts:16, src/entities/video/model/video-mutation-options.ts:23, src/entities/users/model/admin-users-mutation-options.ts:31.

### 5. ID를 화면에서 가져오는 방법이 동일하지 않다

- vote는 목록의 숫자 id로 상세 경로를 만든다.
- proposal은 API 숫자 id를 화면 문자열 id로 변환한다.
- video 목록에는 uuid가 있지만 상세·수정 대상 videoId는 int64 형태다.
- admin-users 응답에는 publicId가 있지만 상세·포인트·상태 요청의 userId는 int64 형태다.
- 현재 조사한 도메인과 page/feature 코드에서 uuid→videoId, publicId→userId 대응 로직은 확인되지 않았다.

이 ID들을 같은 값으로 추정해서 연결할 수 없다. UI 연결 구현 시 ID 출처·전달 계약을 확인해야 한다. 이번 조사는 해당 매핑이나 서비스 정책을 확정하지 않았다.

### 6. 기준 proposal 자체도 조회·처리 계약이 다르다

proposal 목록/상세 조회는 /citizen/proposals, 처리는 /v1/cp/proposals를 사용한다. 조회 parser가 reviewComment="", departmentLabel="미지정", histories=[]를 채우는 반면 처리 응답 parser는 그 필드를 가진 상세 응답을 받는다.

이 동작은 코드와 기존 테스트에서 확인되는 사실이며, 조회·저장의 백엔드 영속성이 일치한다는 검증은 아니다. 화면 구조의 참고와 API 계약의 재사용은 구분해야 한다.

## 권고와 미확정 사항

- 같은 Query 계열의 기존 hook/options를 유지하고, 해당 화면의 controller에서 검색값·페이지·선택·폼·저장 결과·오류·재시도와 view props를 연결하는 방식이 현재 구조에 맞는다.
- 기존 DAO·이벤트 등의 직접 Axios 구현은 parser·Query 상태·캐시 계층까지 필요한지 별도 범위 확인 후 연결해야 한다.
- 동일 UX를 적용할지는 이전 데이터 유지, 페이지 수/0 값, nullable 응답 표현, ID 출처 등의 요구를 확정한 뒤 결정한다.
- auth는 명령형 흐름이라는 차이만으로 Query 전환 대상으로 결론내리지 않는다.
- 새 공통 추상화, 일괄 리팩터링, endpoint·ID 매핑 변경은 제안 범위에 포함하지 않았다.

## 실행 검증

다음 기존 테스트를 한 번 실행했다.

~~~sh
node --test tests/citizen-proposals-contract.test.mjs tests/citizen-votes-contract.test.mjs tests/inquiries-mutation.test.mjs tests/items-query-mutation.test.mjs tests/item-category-query-mutation.test.mjs tests/video-query-mutation.test.mjs tests/admin-users-query-mutation.test.mjs tests/usage-query.test.mjs
~~~

- 종료 코드 0
- tests 69, pass 69, fail 0, cancelled 0, skipped 0
- API factory/DTO/parser 계약, Axios와 MSW 경계의 요청·응답·취소, QueryObserver/MutationObserver의 상태 및 캐시 갱신을 검증
- proposal·vote UI 이벤트 연결은 실제 소스의 callback 경로로 확인
- 브라우저 자동화·화면 캡처·실제 서버 호출·lint·build는 실행하지 않음
- 실행 후 git status --short 및 git diff --stat 출력 없음

## 변경과 남은 작업

애플리케이션 구현 변경 없음. 현재 요청의 조사·비교는 완료했다. 실제 UI 연결 구현과 위 미확정 계약의 결정은 이번 요청에 포함하지 않는다.

