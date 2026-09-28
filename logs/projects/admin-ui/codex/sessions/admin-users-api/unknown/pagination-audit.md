# 전체 도메인 목록 응답 조사

## 결론

`src/entities`의 30개 도메인과 관련 `src/shared/api`, `src/pages`, `src/features`, `src/mocks`를 조사했다. 사용자 설명의 `data: { items, total, page, size }` 형식은 전체 도메인에 통일되어 있지 않다. 이 형식을 쓰는 목록은 items, users의 관리자 탈퇴 로그, inquiries, cp-proposal, cp-vote다. 같은 형식을 공용 DTO·Zod schema로 재사용하지 않고 각각 정의한다.

요청 기본값도 통일되지 않았다. items는 null 입력을 page 1 / size 10으로 정규화하지만 news, inquiries, cp-proposal, cp-vote, 관리자 탈퇴 로그에는 size 20이 남아 있다. 앞선 탈퇴 로그 명세의 기본 size가 20이었던 이력과 별개로, 현재 사용자가 말한 전체 1 / 10 기준에는 맞지 않는다.

이번 요청은 조사이며 애플리케이션 소스·테스트·설정을 수정하지 않았다. 실제 백엔드 응답을 호출한 결과가 아니라 현재 코드의 계약과 전달 흐름을 확인한 결과다.

## 조사 기준

- 위치: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`
- branch: `sy-main`
- HEAD: `52011e5ad746e3c62b7e75b0a3f11cf1472c6c78`
- 앞선 user·item의 미커밋 변경을 포함한 현재 작업 트리를 조사했다.
- 외부 응답 envelope의 `data`와 목록 내부의 `items`를 구분했다. 사용자 제공 item·탈퇴 명세에서 목록 배열 필드의 실제 이름은 `items`다.
- 일반 배열·설정·상세·집계 응답을 페이지 목록으로 간주하지 않았다. 현재 코드에 page/size가 없는 API는 해당 사실을 기록했으며 실제 백엔드 계약이 없다고 단정하지 않았다.

## 공용 계층

| 자산 | 실제 계약 | 판정 |
| --- | --- | --- |
| `src/shared/api/common/api-result/types.ts`의 `ServerResponse<TData>` / `ApiResult<TData>` | 외부 envelope 및 성공·실패 | 페이지 메타 구조를 지정하지 않는다. |
| `src/shared/api/api-client.ts` | `ServerResponse<TData>`를 `ApiResult<TData>`로 전달 | total/page/size 정규화나 기본값 강제가 없다. |
| `src/shared/api/common/dto.ts`의 `PageSizeQueryDto` | `{ page: number, size: number }` | 요청 타입만 공용이며 실행 시 기본값이 없다. |
| 같은 파일의 `OptionalPageSizeQueryDto` | `{ page?: number, size?: number }` | 필수 여부도 공용 정의가 둘로 나뉜다. |
| 같은 파일의 `PaginationDto` | `{ page, pageCount, itemCount }` | 사용자 설명의 `{ total, page, size }`와 다르다. |
| 같은 파일의 `TableApiResponseDto<T, TKey>` | `{ content, count: { totalItemCount, tabItemCount }, pagination: { page, pageCount } }` | 여러 기존 도메인이 재사용하지만 목표 응답 형식과 다르다. |

`items/total/page/size` 전체를 감싸는 공용 페이지 응답 DTO와 Zod schema factory는 조사 범위에서 확인되지 않았다.

## 30개 도메인별 결과

아래 경로는 모두 `src/entities/` 아래다. 기본값은 DTO/schema/API에서 확인한 값이며, 화면에서 명시적으로 전달하는 값은 별도 표시했다.

| 도메인 | 목록 또는 조회 응답의 현재 구조 | 연결·기본값·판정 근거 |
| --- | --- | --- |
| `items` | `items/total/page/size`, 각 값 nullable | `api/items.dto.ts:41`; parser → query options → hook에서 보존. null page/size는 1/10. 카테고리 API는 별도 배열 조회. |
| `users` | `/admin/users/withdrawals`: `items/total/page/size`; 구형 `/v1/users` 및 device-logs: 응답 `unknown` | `api/admin-users.dto.ts:33`, `api/users.api.ts:26`; 탈퇴 조회는 parser·hook 연결, 기본 1/20·최대100. 구형 목록은 공용 형식 보장 없음. |
| `inquiries` | API: `items/total/page/size`; parser 결과에 `pageCount` 추가 | `api/inquiry.dto.ts:21`, `api/inquiry.parser.ts:4`; hook 연결. schema 기본 1/20. |
| `cp-proposal` | API: `items/total/page/size`; parser가 항목을 UI 모델로 변환하고 `pageCount` 추가 | `api/cp-proposal.dto.ts:52`, `api/cp-proposal.parser.ts:23`; hook·controller 연결. schema와 화면 모두 1/20. |
| `cp-vote` | API: `items/total/page/size`; parser 결과에 `pageCount` 추가 | `api/cp-vote.dto.ts:41`, `api/cp-vote.parser.ts:5`; hook·controller 연결. schema와 화면 모두 1/20. |
| `news` | `items/totalElements/totalPages/pinnedItemCount` | `api/news.dto.ts:25`; parser·controller·mock이 모두 이 형식을 사용. total/page/size 없음. schema와 화면 모두 1/20. |
| `cp-board` | `content/count/pagination`; count는 totalItemCount·상태별 집계, pagination은 page/pageCount | `api/cp-board.dto.ts:89`; parser·hook·controller·mock 연결. schema·화면 1/10. |
| `cp-comment` | `content/count/pagination`; count에 신고·숨김 등 집계 포함 | `api/cp-comment.dto.ts:59`; parser·hook·controller·mock 연결. schema·화면 1/10. |
| `cp-report` | `content/count/pagination`; count에 상태별 집계 포함 | `api/cp-report.dto.ts:91`; parser·hook·controller·mock 연결. schema·화면 1/10. |
| `cp-activity-log` | `content/count/pagination`; count에 todayCount·tabItemCount 포함 | `api/cp-activity-log.dto.ts:63`; parser·hook·controller·mock 연결. schema·화면 1/10. |
| `cp-reward` | 대상 목록: `content/count/pagination`; count는 pendingCount/completedCount/pendingPointLabel | `api/cp-reward.dto.ts:57`; total 자체가 없고 페이지 hook에서 pendingCount + completedCount 계산. schema·화면 1/10. |
| `cp-discussion` | `TableApiResponseDto` + `opinionTotal` | `api/cp-discussion.dto.ts:20,66`; parser·hook·controller·mock 연결. schema·화면 1/10. |
| `cp-policy` | `TableApiResponseDto` | `api/cp-policy.dto.ts:19,65`; parser·hook·controller·mock 연결. query schema 자체 기본값 없음, 화면 1/10. |
| `cp-survey` | `TableApiResponseDto` | `api/cp-survey.dto.ts:21,64`; parser·hook·controller·mock 연결. query schema 자체 기본값 없음, 화면 1/10. |
| `event` | 출석·룰렛 목록 모두 `{ content, pagination: PaginationDto }` | `api/attendance/attendance.dto.ts:57`, `api/roulette/roulette.dto.ts:51`; API가 해당 타입 반환. page/size 필수지만 API 기본값 없음. 이벤트별 아이템 조회는 별도 배열. |
| `dao` | 제안·심사·감사로그·전체 토론·댓글 API는 TableApiResponseDto; 개별 제안 토론·투표·신고·음성방은 content/PaginationDto | `api/` 각 하위 API. total/page/size 공통 형식이 아니며 일부 DTO와 API 반환 타입도 다름. 아래 상세 참조. |
| `admin-settings` | 관리자 목록·감사로그 응답 `unknown` | `api/admin-settings.api.ts:14,35`; 항목 DTO는 있지만 페이지 컨테이너가 반환 타입에 연결되지 않음. page/size 필수, API 기본값 없음. 역할 목록은 별도 배열. |
| `faq` | 목록 응답 `unknown` | `api/faq.api.ts:13`; GetFaqListResponseDto는 단일 항목 모양. page/size 필수, API 기본값 없음. |
| `sales` | 매출 목록 응답 `unknown` | `api/sales.api.ts:20`; page/size 필수, API 기본값 없음. summary/statistics는 별도 집계 요청. |
| `usage` | calls/items/points/soria/soria-plus 모두 Axios 응답 제네릭 미지정 | `api/usage.api.ts`; 응답 페이지 구조가 타입·parser로 검증되지 않음. page/size 필수, API 기본값 없음. |
| `vo` | 예약·이용이력·패널티 DTO는 TableApiResponseDto | API 연결 전 임시 DTO와 fixture 화면. 세 화면 크기는 10. 실시간 방 목록은 `{ rooms }`, 일정·대시보드는 별도 구조. |
| `maps` | 활동 조회: `GetMapActivityResponseDto[]` | `api/map.api.ts`; page/size 없는 배열 조회. 현재 코드상 페이지 목록 아님. |
| `maintenance` | 설정 조회: `SynthoriaConfigDto[]` | `api/maintenance.api.ts`, `api/maintenance.dto.ts`; page/size 없는 설정 배열. |
| `auth` | 로그인·갱신·비밀번호 작업 | `api/auth.api.ts`; 현재 코드에 페이지 목록 없음. |
| `profile` | 관리자 본인 상세·RBAC | `api/profile.api.ts`, `api/profile.dto.ts`; 현재 코드에 페이지 목록 없음. |
| `dashboard` | 사용자·매출·장치 등 집계 | `api/dashboard.api.ts`; 현재 코드에 page/size 페이지 목록 요청 없음. |
| `cp-dashboard` | KPI와 recentTasks/participation/notices 등 묶음 | `api/cp-dashboard.dto.ts`; 현재 코드에 페이지 목록 없음. |
| `cp-main-display` | banners/featured/notices와 개별 개수 | `api/cp-main-display.dto.ts`; 전체 배치 설정 조회이며 현재 코드에 페이지 목록 없음. |
| `cp-notice` | 공지 상세·초안·게시 | `api/cp-notice.api.ts`; 현재 코드에 별도 목록 API 없음. |
| `cp-operation-policy` | 운영정책 단일 객체 | `api/cp-operation-policy.dto.ts`; 현재 코드에 페이지 목록 없음. |

## DAO 내부 추가 불일치

- `api/proposal/proposal.dto.ts:44`는 count를 `item_amount/status_count`, pagination을 `page/totalPage`로 선언한다. 그러나 `api/proposal/proposal.api.ts:24`는 `TableApiResponseDto`의 `totalItemCount/tabItemCount`, `page/pageCount`를 반환 타입으로 사용한다. 기존 전용 DTO는 실제 API 함수에 연결되지 않았다.
- `api/discussion/discussion.dto.ts:83`의 댓글 목록 전용 DTO는 `{ content, pagination: PaginationDto }`다. `api/discussion/discussion.api.ts:63`의 실제 댓글 함수는 `TableApiResponseDto`를 사용한다. 동일 기능을 위한 선언이 서로 다르다.
- 제안 목록·제안 이력·심사·DAO 감사로그는 TableApiResponseDto다. 투표·신고·음성방·개별 제안 토론은 content/PaginationDto다. 배너 조회는 `{ content: DaoBannerDto[] }`이며 page/size가 없다.

## hook·controller까지의 영향

1. **형식이 맞는 5개 목록도 공용 타입을 재사용하지 않는다.** items와 탈퇴는 메타를 보존하고, inquiries·cp-proposal·cp-vote는 `Math.max(1, Math.ceil(total / size))`로 pageCount를 각각 추가한다. 계산 로직도 중복이다.
2. **news는 요청한 공통 응답을 그대로 받을 수 없다.** parser가 totalElements/totalPages/pinnedItemCount를 요구한다. controller도 totalPages/totalElements를 직접 참조한다. 공통 응답만 오면 parser에서 실패한다. 근거: `src/entities/news/api/news.dto.ts:25`, `src/pages/cp-news/hook/use-cp-news-list-controller.ts:66`.
3. **8개 CP 도메인의 다른 구조가 끝까지 연결되어 있다.** 각 parser는 content/count/pagination을 요구하고, `src/pages/cp-*/hook/use-*-list-data.tsx`에서 content를 rows로, pagination을 page/pageCount로, count를 KPI와 itemCount로 읽는다. 타입만 공통형으로 바꾸면 parser·controller·mutation 캐시 처리·mock도 영향을 받는다.
4. **total과 KPI는 같은 값이라고 단정할 수 없다.** `src/mocks/utils/mock-table.ts`는 totalItemCount를 별도로 받지만 pageCount는 전달된 items 길이로 계산한다. `src/mocks/cp-discussion.handlers.ts:68` 및 `cp-activity-log.handlers.ts:124`에서 totalItemCount는 상태·활동 탭 적용 전 집합이다. 현재 mock의 이 의미를 공통 페이지 total로 단순 치환하면 페이지 개수 의미가 달라진다. 실제 서버의 집계 정책을 이 mock으로 확정할 수는 없다.
5. **구형 API는 보장이 부족하다.** unknown 또는 Axios 제네릭 미지정 반환은 응답 필드 누락을 타입·parser에서 차단하지 못한다. 실제 서버가 공통형을 반환할 가능성과 별개로 현재 구현이 그것을 반영했다고 판정할 근거가 없다.
6. **VO는 미연결 상태다.** `src/pages/vo-reservation/ui/vo-reservation-list-page.tsx`, `vo-meeting-history/ui/vo-meeting-history-list-page.tsx`, `vo-penalty/ui/vo-penalty-page.tsx`가 fixture를 직접 전달한다. 현재 DTO만으로 백엔드 계약과 일치한다고 볼 수 없다.

## page/size 기본값 요약

| 위치 | 현재 값 |
| --- | --- |
| item query | null을 1/10으로 정규화. 필드 생략은 불가. |
| 관리자 탈퇴 query | 1/20. size는 100으로 제한. |
| news / inquiries / cp-proposal / cp-vote query schema | 1/20. |
| news / cp-proposal / cp-vote 화면 설정 | PAGE_SIZE = 20. |
| cp-board / cp-comment / cp-report / cp-activity-log / cp-reward / cp-discussion | schema·화면 1/10. |
| cp-policy / cp-survey | 화면 1/10. schema는 page/size 필수이며 자체 기본값 없음. |
| VO 예약·이용이력·패널티 | fixture 화면 크기10. 실제 API 기본값 미구현. |
| 기타 구형 페이지 API | 전달받은 params를 전송. 타입의 page/size 정의만으로 기본값은 강제되지 않음. |

item의 nullable 허용은 앞선 사용자 임시 계약이다. 이 정책을 다른 도메인에 일괄 적용한 상태는 아니다. 이번 조사에서는 다른 도메인의 nullable 정책을 변경하거나 임의 확정하지 않았다.

## 향후 정리 시 필요한 범위

공통 응답 DTO와 항목 schema를 받는 Zod 페이지 schema, 공통 요청 기본값을 기준으로 맞추는 방식이 적합하다. 공용 네트워크 클라이언트는 전송을 담당하고 각 도메인의 항목 계약을 유지한다. UI용 rows/pageCount 및 KPI는 별도 변환 경계로 취급해야 한다. 기존 news의 고정 항목 집계와 CP의 상태별 집계는 해당 필드의 실제 서버 계약을 확인해야 한다.

이 문서는 조사 결과이며 위 정리 작업은 실행하지 않았다. 소스·패키지·테스트 변경, Git 변경, 백엔드 호출, 빌드·테스트 실행은 이번 조사에서 수행하지 않았다. 검색 중 파이프 패턴과 동적 Python 열거 명령이 정책 guard에 차단되어 재시도하지 않았고, 명시적 경로의 rg/cat/sed/find 조회로 조사했다.
