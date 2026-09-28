# 최종 요약

## 후속 소포 API Logic 구현 결과

사용자의 “작업 진행” 승인에 따라 소포 목록 조회·발송·엑셀 다운로드 Logic을 구현했다. 작업 위치는 `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`, 브랜치는 `sy-main`, 구현 기준 HEAD는 `0e7c671b511f8e6cecebcce8946a13ee24d8c339`다. 후속 커밋 요청과 명령 실행 승인에 따라 소스 13개 파일과 테스트 1개 파일을 `3e52ff384fba44c5fc824c67bcb46d74d395f039`에 커밋했다.

### 커밋 결과

- 메시지: `feat(parcels): 소포 API와 엑셀 다운로드 hook 구현`.
- 보호 실행 작업 `d54e3b9112fb9947da40f9ed75787ce4`의 stage·commit 완료, 14개 파일·705줄 추가.
- 실행 전 중앙 잠금 파일 쓰기가 샌드박스에서 거부되었으나, 동일 작업 승인 후 권한을 높인 보호 실행으로 완료했다. 승인 상태나 중앙 정책은 직접 수정하지 않았다.
- 사후 `git show --stat --oneline HEAD`로 대상 파일을 확인했고, `git status --short --branch`에서 sy-main의 작업 트리가 깨끗함을 확인했다. push는 수행하지 않았다.

| API | 공개 hook | 구현 동작 |
| --- | --- | --- |
| GET /admin/parcels | useParcelListQuery | recipient 부분일치 검색, 1부터 시작하는 페이지, 기본 size 20·상한 100, createdAt/id 정렬, 기본 최신순 |
| POST /admin/parcels | useSendParcelMutation | 필수 body 5개 필드와 amount ≥ 1 검증, 성공 시 소포 목록 취소·무효화·활성 목록 재조회 |
| GET /admin/parcels/export | useExportParcelHistoryMutation | recipient만 선택 쿼리로 전달, 미입력 시 전체, 응답 파일 다운로드, UTF-8 파일명 우선 적용 |

### 변경과 재사용

- `src/entities/parcels/api`: 기존 ApiClient·ApiResult·인증·공용 ApiResponseDto/PageResponseDto·Zod를 재사용한다. 공용 응답 DTO를 중복 생성하지 않는다.
- `parcel-export.response.ts`: arraybuffer로 받은 파일과 Content-Disposition을 기존 클라이언트의 내부 envelope로 변환한다. HTTP 실패의 JSON envelope는 공용 오류 처리기로 전달해 상태·업무 코드·메시지를 유지한다. 파일명 헤더를 읽을 수 없으면 제공된 기본 파일명 parcel-history.xlsx를 사용한다.
- `model`·`hook`: 기존 도메인과 같은 Query key/options·mutation options·얇은 hook 구조다. 정규화된 요청값을 캐시 key에 반영한다.
- `lib/download-parcel-history.ts`: 파일 링크를 실행하고 링크·object URL을 정리한다. 실패·취소 응답은 다운로드하지 않고, export mutation 결과에 Blob을 남기지 않는다.
- 기존 공용 Axios 처리기, 다른 도메인 API, 페이지·버튼 UI는 수정하지 않았다.

### UI에서 사용할 연결 계약

`~/entities/parcels`에서 세 hook을 가져온다. 목록은 `useParcelListQuery({ recipient, page: 1, size: 20 })`로 조회한다. 발송은 `useSendParcelMutation()`의 `mutate({ payload: { title, content, userId, itemId, amount } })`를 호출한다. userId/itemId 조회 UI나 선택 정책은 이번 구현 범위에 포함하지 않는다.

엑셀 버튼은 `useExportParcelHistoryMutation()`의 `mutate({ params: { recipient } })`를 호출한다. 전체 내역은 `mutate({})`로 요청한다. 빈 recipient도 쿼리에서 생략한다. hook은 isPending/error 등 TanStack Query 상태를 그대로 제공하고 요청 성공 후 다운로드를 실행한다. API에는 업로드 파일이나 요청 body를 전달하지 않는다.

### 검증 결과와 한계

- 공통 포맷 트리거로 변경한 코드·테스트에 실제 Prettier 적용 완료.
- `node --test tests/parcels-query-mutation.test.mjs tests/citizen-proposals-contract.test.mjs tests/citizen-votes-contract.test.mjs tests/inquiries-mutation.test.mjs tests/items-query-mutation.test.mjs tests/item-category-query-mutation.test.mjs tests/video-query-mutation.test.mjs tests/admin-users-query-mutation.test.mjs tests/usage-query.test.mjs`: 9개 파일, 82개 테스트 모두 통과(소포 13개 + 기존 69개).
- `npm run lint`: 통과.
- `npm run build`: TypeScript·Vite 빌드 통과. tsconfig paths 플러그인 안내와 큰 chunk 경고 출력.
- 소포 테스트는 실제 Axios와 MSW 경계, Query/MutationObserver, 다운로드 DOM 대역을 사용했다. 최초 테스트의 조회 실패·발송 실패 캐시 검증이 섞인 기대값을 분리했고, 수정 후 전체 통과했다.
- 테스트 오류 응답은 공용 envelope의 보존 여부를 검증한다. export에서 어떤 업무 코드가 발생 가능한지에 대한 서버 정책을 추가로 확정하는 근거가 아니다.
- 실제 백엔드 호출, 실제 브라우저 다운로드·CORS 헤더 노출, 페이지 버튼 연결은 검증하지 않았다. UI 연결은 별도 작업이다.

### 정책 도구 실행 기록

최초 구현 시도는 승인 미등록으로 차단되었고 사용자 승인 후 구현했다. 후반 추가 테스트 정리 시도도 승인 미등록으로 차단되었다. 이후 일반 포맷 트리거는 미확인 쓰기 예약을 이유로 차단되었다. 읽기 전용 확인에서 남은 예약은 다른 event-api worktree의 다른 native session으로 확인했으며 해당 기록을 수정하거나 해제하지 않았다.

공식 `formatting.py check`가 안내한 현재 native session `01a0ae2d-50e0-7993-85a9-2abe1f22c655`를 명시한 동일 포맷 실행기 명령으로 포맷을 완료했다. 이후 최종 테스트·lint·build는 정상 실행했다. 중앙 정책이나 승인 상태를 직접 변경하지 않았다.

## 제공 사항

후속 proposal/vote 비교 결과, 문의·아이템·영상·회원·사용 이력·CP 공지는 같은 Query 계열이지만 페이지 전환·반환 모델·캐시 처리까지 동일하지 않다. 기존 DAO·이벤트 등은 대부분 Axios 직접 호출 계열이다. 구체적인 호출 경로와 차이는 [exploration.md](./exploration.md)에 기록했다. 기존 테스트 8개 파일의 69개 테스트가 모두 통과했다.

아래 현황은 소포 구현 전 기준 HEAD의 초기 조사 결과다. sy-main의 src/entities에 구현된 도메인 API 함수 193개 중 150개는 라우팅된 UI까지 이어지는 호출 경로가 확인되지 않았다. 43개는 UI 연결을 확인했다.

| 구분 | 미연결 함수 수 | 확인 내용 |
| --- | ---: | --- |
| 아이템·카테고리 | 14 | /admin/items 10개, /admin/items/categories 4개. query/mutation hook은 존재하지만 페이지 소비자가 없다. |
| 영상·재생목록 | 11 | /admin/video 6개, /admin/video/playlists 5개. hook까지 구현되어 있고 페이지 소비자가 없다. |
| 문의 | 7 | /admin/inquiries 목록·상세·삭제·상태·답변 등록/수정/삭제. hook 소비자가 없다. |
| 회원 관리 | 5 | /admin/users 상세·탈퇴·포인트·권한·상태. hook 소비자가 없다. |
| 사용 이력 | 2 | /admin/usage 포인트·아이템. hook 소비자가 없다. |
| 이전 CP 공지 | 3 | /v1/cp/notices 상세·초안 저장·발행 hook의 소비자가 없다. 현재 공지는 /admin/news를 사용한다. |
| 출석·룰렛 이벤트 | 16 | 각각 8개. API public singleton 외 사용처가 없다. |
| DAO | 41 | 제안 8, 심사 3, 투표 5, 메인 게시 2, 토론·댓글 11, 신고 2, 음성방 2, 배너 4, 정책 3, 로그 1. |
| FAQ | 6 | 생성·목록·상세·수정·일괄 수정·삭제. singleton 외 사용처가 없다. |
| 관리자 설정 | 8 | 관리자 관리·감사 로그·정책·역할·비밀번호. singleton 외 사용처가 없다. |
| 내 프로필 | 4 | 조회·RBAC·프로필 수정·비밀번호 수정. singleton 외 사용처가 없다. |
| 기존 대시보드 | 10 | /v1/dashboard 통계. CP 대시보드는 별도 cp-dashboard API를 사용한다. |
| 매출 | 3 | 요약·목록·통계. singleton 외 사용처가 없다. |
| 맵 | 1 | getMapActivity. singleton 외 사용처가 없다. |
| 유지보수 | 2 | 설정 조회·수정. singleton 외 사용처가 없다. |
| 기존 회원 | 9 | /v1/users 목록·상세·정지/복구·재화/상태·접속 및 통계. singleton 외 사용처가 없다. |
| 기존 사용 이력 | 5 | /v1/usage 통화·아이템·포인트·Soria·Soria Plus. singleton 외 사용처가 없다. |
| 인증 일부 | 3 | refreshToken, changePassword, requestChangePasswordEmail. |

### 구분이 필요한 사례

- 인증: authApi.refreshToken은 src/features/auth/use-auth.ts:26에서 호출하도록 구현되어 있지만 refreshAuthentication은 정의와 반환 외 소비자가 없다. 로그인 signIn은 src/pages/sign-in/hook/use-sign-in-controller.tsx:14에서 연결된다. 비밀번호 변경·변경 메일 요청은 호출부가 없다.
- DAO: deleteDaoProposalImage는 src/features/image-manager/ui/hooks/useImageDelete.ts:10에 참조가 있으나 useImageDelete의 소비자가 없어 현재 UI에서 도달할 수 없다.
- CP 공지: 기존 useCpNoticeDetailQuery/useCpNoticeDraftMutation/useCpNoticePublishMutation은 entity export만 남아 있다. 라우팅된 /cp/news는 useNewsListQuery 및 useNewsDetailQuery/useCreateNewsMutation/useUpdateNewsMutation/useDeleteNewsMutation을 사용한다.
- CpNoticeFormPage 파일도 남아 있으나 src/pages/cp-board/index.ts에서 export되지 않고 현재 router에 등록되지 않았다. 이 파일 역시 현재 /admin/news hook을 사용한다.
- VO: src/entities/vo/api에는 DTO만 있으며 페이지는 VO_*_FIXTURE를 사용한다. 구현된 HTTP API의 미연결 집계에서는 제외했다.
- 별도 Agora 회의 API: src/features/meeting/api/meeting.api.ts의 createMeeting, joinMeetingByInviteCode, joinMeetingByRtcToken은 라우팅된 /meeting 화면에 연결된다. src/entities 함수 193개 집계에는 포함하지 않았다.
- /admin/users의 postUserAuthorities에는 서버가 200 no-op을 반환한다는 기존 코드 주석이 있다. 서버 동작은 이번 조사에서 별도로 확인하지 않았다.

### 연결을 확인한 도메인

cp-dashboard, cp-main-display, cp-proposal, cp-vote, cp-discussion, cp-policy, cp-survey, cp-comment, cp-report, cp-board, cp-activity-log, cp-reward, cp-operation-policy의 API 함수 37개, news 5개, auth.signIn 1개.

## 변경 이유

사용자가 현재 구현된 도메인 API의 UI 미연결 목록을 요청했다. API 정의 → singleton → query/mutation hook → page controller → router 경로를 대조했다.

## 재사용한 자산

src/entities 각 도메인의 api/index.ts 및 최상위 index.ts, 기존 hook·query/mutation options, src/app/router/routes.tsx, 실제 페이지 controller를 조사 근거로 사용했다. 새 API·hook·추상화는 추가하지 않았다.

## 영향 영역

애플리케이션 소스·설정·패키지·Git 변경 없음. 자기 세션의 plan.md와 final-summary.md만 기록했다.

## 제외 사항

다른 branch/worktree, 실제 서버 연결 성공 여부, API 계약 정확성, 브라우저 동작, UI 구현 작업은 조사 범위에 포함하지 않았다.

## 검증

| 명령어 또는 방법 | 결과 |
| --- | --- |
| git branch --show-current / git rev-parse HEAD | sy-main / 0e7c671b511f8e6cecebcce8946a13ee24d8c339 |
| git status --short | 조사 시작과 기록 작성 직전 모두 변경 없음 |
| git worktree list --porcelain | 현재 checkout 외 event·video linked worktree 존재 확인. 해당 구현 내용은 이번 범위 제외 |
| rg --files src, API 정의와 참조 rg -n 검색 | 193개 API 함수 인벤토리 확인 |
| singleton·factory·Client·Api 및 hook 참조 검색 | entity 내부 참조와 실제 페이지 소비를 구분 |
| src/app/router/routes.tsx 및 페이지 controller 확인 | UI 연결 43개 / 미연결 150개 |
| 초기 현황 조사 lint / build / test / 포맷 | 코드 변경이 없는 정적 조사로 실행하지 않음 |
| 후속 패턴 비교의 기존 테스트 8개 파일 | node --test 실행, 69개 통과 / 실패 0. 명령과 범위는 exploration.md 참조 |

초기 복합 조회 명령, Node 기반 인라인 분석, 일부 복잡한 검색 명령은 PreToolUse의 경로 또는 파일 변경 판정으로 차단되었다. 해당 명령은 실행되지 않았으며 허용되는 리터럴 경로의 rg·cat·sed 조회 결과로 조사를 완료했다. Node 분석 실행 결과를 근거로 사용하지 않았다.

## 산출물

- plan.md: 범위·판정 기준·조회 방법
- final-summary.md: 결론·예외·전체 미연결 함수 목록
- exploration.md: 후속 proposal/vote 연결 경로, 미연결 Logic의 패턴 비교와 69개 기존 테스트 결과

## 알려진 제한

정적 소스 기준 판정이다. API 함수가 UI에 연결되어 있다는 사실은 백엔드 구현 또는 응답 성공을 보장하지 않는다. 개발 환경에서 /v1/cp/ 및 /citizen/는 MSW를 사용하도록 구성되어 있다.

동일 HTTP endpoint를 호출하는 서로 다른 함수도 별도로 센다. 예를 들어 DAO의 updateDaoProposalDiscussionPostModeration과 patchDaoDiscussionPostsModeration은 별도 함수 2개로 집계했다. factory·parser·DTO·주석 처리된 함수·MSW handler·테스트 참조는 API 함수 수에 포함하지 않았다.

## 다음 단계

요청한 현황 조사는 완료했다. UI 연결 구현·불필요 API 삭제 여부와 우선순위는 이번 요청에서 확정하지 않았다.

## 전체 미연결 함수 목록

### src/entities/admin-settings/api/admin-settings.api.ts (8개)

- [createAdmin](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/admin-settings/api/admin-settings.api.ts:9)
- [getAdmins](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/admin-settings/api/admin-settings.api.ts:13)
- [getAdminByAdminId](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/admin-settings/api/admin-settings.api.ts:20)
- [updateAdminByAdminId](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/admin-settings/api/admin-settings.api.ts:27)
- [getAdminAuditLogList](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/admin-settings/api/admin-settings.api.ts:31)
- [getPolicies](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/admin-settings/api/admin-settings.api.ts:38)
- [getAdminRoles](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/admin-settings/api/admin-settings.api.ts:45)
- [updatePasswordByAdminId](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/admin-settings/api/admin-settings.api.ts:52)

### src/entities/auth/api/auth.api.ts (3개)

- [refreshToken](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/auth/api/auth.api.ts:12)
- [changePassword](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/auth/api/auth.api.ts:19)
- [requestChangePasswordEmail](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/auth/api/auth.api.ts:22)

### src/entities/cp-notice/api/cp-notice.api.ts (3개)

- [getDetail](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/cp-notice/api/cp-notice.api.ts:36)
- [saveDraft](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/cp-notice/api/cp-notice.api.ts:39)
- [publish](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/cp-notice/api/cp-notice.api.ts:42)

### src/entities/dao/api/banner/banner.api.ts (4개)

- [getDaoBanners](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/banner/banner.api.ts:8)
- [createDaoBanner](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/banner/banner.api.ts:15)
- [patchDaoBanner](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/banner/banner.api.ts:22)
- [deleteDaoBanner](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/banner/banner.api.ts:29)

### src/entities/dao/api/dao-logs/logs.api.ts (1개)

- [getDaoLogsHistory](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/dao-logs/logs.api.ts:9)

### src/entities/dao/api/discussion/discussion.api.ts (11개)

- [getDaoProposalsDiscussionPosts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/discussion/discussion.api.ts:30)
- [getDaoProposalDiscussionPosts](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/discussion/discussion.api.ts:38)
- [createDaoProposalDiscussionPost](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/discussion/discussion.api.ts:44)
- [getDaoProposalDiscussionPostDetail](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/discussion/discussion.api.ts:49)
- [updateDaoProposalDiscussionPostModeration](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/discussion/discussion.api.ts:52)
- [deleteDaoProposalDiscussionPost](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/discussion/discussion.api.ts:57)
- [getDaoDiscussionPostComments](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/discussion/discussion.api.ts:60)
- [createDaoDiscussionComment](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/discussion/discussion.api.ts:69)
- [deleteDaoDiscussionComment](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/discussion/discussion.api.ts:72)
- [patchDaoDiscussionPostsModeration](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/discussion/discussion.api.ts:75)
- [patchDaoDiscussionCommentsModeration](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/discussion/discussion.api.ts:80)

### src/entities/dao/api/main-board/main-board.api.ts (2개)

- [getDaoMainBoardPublish](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/main-board/main-board.api.ts:8)
- [deleteDaoMainBoardPublish](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/main-board/main-board.api.ts:17)

### src/entities/dao/api/policy/policy.api.ts (3개)

- [getDaoPolicy](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/policy/policy.api.ts:8)
- [patchDaoPolicy](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/policy/policy.api.ts:15)
- [restartDaoJobsSettle](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/policy/policy.api.ts:22)

### src/entities/dao/api/proposal-review/proposal-review.api.ts (3개)

- [getDaoProposalsReview](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/proposal-review/proposal-review.api.ts:16)
- [getDaoProposalReviewDetail](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/proposal-review/proposal-review.api.ts:29)
- [createDaoProposalReview](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/proposal-review/proposal-review.api.ts:38)

### src/entities/dao/api/proposal/proposal.api.ts (8개)

- [createDaoProposal](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/proposal/proposal.api.ts:17)
- [getDaoProposals](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/proposal/proposal.api.ts:23)
- [getDaoProposalsHistory](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/proposal/proposal.api.ts:33)
- [getDaoProposalDetail](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/proposal/proposal.api.ts:42)
- [updateDaoProposal](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/proposal/proposal.api.ts:48)
- [deleteDaoProposal](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/proposal/proposal.api.ts:54)
- [uploadDaoProposalImage](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/proposal/proposal.api.ts:60)
- [deleteDaoProposalImage](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/proposal/proposal.api.ts:72)

### src/entities/dao/api/report/report.api.ts (2개)

- [getDaoDiscussionReports](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/report/report.api.ts:8)
- [patchDaoDiscussionReport](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/report/report.api.ts:15)

### src/entities/dao/api/voice-room/voice-room.api.ts (2개)

- [getDaoVoiceRooms](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/voice-room/voice-room.api.ts:8)
- [closeDaoVoiceRoom](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/voice-room/voice-room.api.ts:15)

### src/entities/dao/api/vote/vote.api.ts (5개)

- [createDaoProposalVote](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/vote/vote.api.ts:17)
- [getDaoVotes](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/vote/vote.api.ts:24)
- [getDaoVotesResult](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/vote/vote.api.ts:31)
- [closeDaoVote](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/vote/vote.api.ts:38)
- [forceEndDaoVote](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dao/api/vote/vote.api.ts:45)

### src/entities/dashboard/api/dashboard.api.ts (10개)

- [getTodaySoriaRechargeAmount](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dashboard/api/dashboard.api.ts:9)
- [getTodayNewUserCount](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dashboard/api/dashboard.api.ts:16)
- [getTodayUserAccessCount](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dashboard/api/dashboard.api.ts:23)
- [getCurrentUserAccessCount](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dashboard/api/dashboard.api.ts:30)
- [getUserCount](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dashboard/api/dashboard.api.ts:37)
- [getUserDeviceCount](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dashboard/api/dashboard.api.ts:44)
- [getTodayInquiryCount](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dashboard/api/dashboard.api.ts:56)
- [getItemSalesCount](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dashboard/api/dashboard.api.ts:63)
- [getItemSaleRanking](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dashboard/api/dashboard.api.ts:70)
- [getTodayVideoViewCount](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/dashboard/api/dashboard.api.ts:77)

### src/entities/event/api/attendance/attendance.api.ts (8개)

- [createAttendanceEvent](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.api.ts:20)
- [getAttendanceEventList](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.api.ts:24)
- [getAttendanceEvent](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.api.ts:31)
- [updateAttendanceEvent](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.api.ts:38)
- [uploadAttendanceEventConfigImage](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.api.ts:42)
- [updateAttendanceEventConfigs](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.api.ts:51)
- [getAttendanceEventItems](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.api.ts:55)
- [updateAttendanceEventItems](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/attendance/attendance.api.ts:66)

### src/entities/event/api/roulette/roulette.api.ts (8개)

- [createRouletteEvent](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.api.ts:19)
- [getRouletteEventList](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.api.ts:23)
- [getRouletteEvent](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.api.ts:30)
- [updateRouletteEvent](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.api.ts:37)
- [uploadRouletteEventConfigImage](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.api.ts:41)
- [updateRouletteEventConfigs](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.api.ts:50)
- [getRouletteEventItems](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.api.ts:54)
- [updateRouletteEventItems](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/event/api/roulette/roulette.api.ts:61)

### src/entities/faq/api/faq.api.ts (6개)

- [createFaq](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/faq/api/faq.api.ts:9)
- [getFaqs](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/faq/api/faq.api.ts:12)
- [getFaqById](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/faq/api/faq.api.ts:18)
- [updateFaqById](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/faq/api/faq.api.ts:24)
- [batchUpdateFaqList](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/faq/api/faq.api.ts:27)
- [deleteFaqById](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/faq/api/faq.api.ts:30)

### src/entities/inquiries/api/inquiry.api.ts (7개)

- [getList](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.api.ts:34)
- [getDetail](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.api.ts:37)
- [deleteInquiry](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.api.ts:40)
- [patchInquiryStatus](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.api.ts:43)
- [postInquiryAnswer](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.api.ts:50)
- [putInquiryAnswer](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.api.ts:57)
- [deleteInquiryAnswer](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/inquiries/api/inquiry.api.ts:64)

### src/entities/items/api/item-category.api.ts (4개)

- [getList](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item-category.api.ts:30)
- [postCategory](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item-category.api.ts:33)
- [patchCategory](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item-category.api.ts:36)
- [deleteCategory](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/item-category.api.ts:43)

### src/entities/items/api/items.api.ts (10개)

- [getList](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:41)
- [getDetail](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:44)
- [getLatestId](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:47)
- [postItem](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:50)
- [patchItem](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:53)
- [deleteItem](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:56)
- [uploadImage](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:59)
- [toggleEventReward](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:71)
- [patchBatchStatus](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:74)
- [deleteImage](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/items/api/items.api.ts:77)

### src/entities/maintenance/api/maintenance.api.ts (2개)

- [getSynthoriaConfigs](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/maintenance/api/maintenance.api.ts:10)
- [updateSynthoriaConfigs](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/maintenance/api/maintenance.api.ts:17)

### src/entities/maps/api/map.api.ts (1개)

- [getMapActivity](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/maps/api/map.api.ts:9)

### src/entities/profile/api/profile.api.ts (4개)

- [getProfile](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/profile/api/profile.api.ts:9)
- [getRbac](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/profile/api/profile.api.ts:16)
- [updateProfile](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/profile/api/profile.api.ts:22)
- [updatePassword](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/profile/api/profile.api.ts:26)

### src/entities/sales/api/sales.api.ts (3개)

- [getSalesSummary](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/sales/api/sales.api.ts:9)
- [getSales](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/sales/api/sales.api.ts:20)
- [getStatistics](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/sales/api/sales.api.ts:27)

### src/entities/usage/api/admin-usage.api.ts (2개)

- [getPointList](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/usage/api/admin-usage.api.ts:17)
- [getItemList](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/usage/api/admin-usage.api.ts:27)

### src/entities/usage/api/usage.api.ts (5개)

- [getCallHistoryList](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/usage/api/usage.api.ts:9)
- [getItemHistoryList](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/usage/api/usage.api.ts:16)
- [getPointHistoryList](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/usage/api/usage.api.ts:23)
- [getSoriaHistoryList](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/usage/api/usage.api.ts:30)
- [getSoriaPlusHistoryList](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/usage/api/usage.api.ts:37)

### src/entities/users/api/admin-users.api.ts (5개)

- [getDetail](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.api.ts:34)
- [getWithdrawals](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.api.ts:37)
- [postUserPoints](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.api.ts:44)
- [postUserAuthorities](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.api.ts:52)
- [patchUserStatus](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/admin-users.api.ts:59)

### src/entities/users/api/users.api.ts (9개)

- [getUsers](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/users.api.ts:24)
- [getUserByUserId](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/users.api.ts:31)
- [suspendUserByUserId](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/users.api.ts:38)
- [restoreUserByUserId](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/users.api.ts:42)
- [updateUserCurrencyByUserId](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/users.api.ts:48)
- [updateUserStatusByUserId](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/users.api.ts:52)
- [getuserDeviceLogs](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/users.api.ts:56)
- [getStatistics](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/users.api.ts:63)
- [getDailyAvgPlayTimeTopTen](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/users/api/users.api.ts:70)

### src/entities/video/api/playlist.api.ts (5개)

- [getList](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.api.ts:36)
- [getDetail](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.api.ts:46)
- [postPlaylist](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.api.ts:49)
- [patchPlaylist](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.api.ts:52)
- [deletePlaylist](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/playlist.api.ts:59)

### src/entities/video/api/video.api.ts (6개)

- [getList](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.api.ts:46)
- [getDetail](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.api.ts:56)
- [postVideo](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.api.ts:59)
- [patchVideo](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.api.ts:69)
- [deleteVideo](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.api.ts:79)
- [postThumbnail](/Users/okand/SynologyDrive/asan-metaverse-admin-ui/src/entities/video/api/video.api.ts:82)
