# 공지사항 API 연결 결과

승인된 Logic 범위의 구현을 완료했다. 메인 공지는 `/news?page=1&size=10`으로 조회하며, 공지사항 6개 API와 DTO·parser·query/mutation hook을 제공한다. 관련 37개 테스트와 lint·build는 통과했지만 전체 테스트는 통과하지 못했다.

## 확정 계약과 실제 변경

- 공통 `src/shared/api/common/page-response.dto.ts`에 `PageResponseDto`와 `createPageResponseSchema`를 추가했다. 공지와 댓글의 목록이 함께 재사용한다.
- 기존 `api/notice/`에 `/news`, `/news/{newsId}`, 댓글 목록·작성·수정·삭제를 연결했다. `ApiClient`의 envelope 처리, 인증 config, `withAbortSignal`, 기존 오류 변환을 재사용한다.
- 공지는 `ANNOUNCEMENT`와 `EVENT`를 검증한다. 목록에 sort를 전송하지 않으며 서버의 순서를 보존한다. 댓글은 createdAt·id 정렬만 받고 기본값은 `createdAt,desc`다.
- 댓글 요청은 trim 후 1~1000자를 검증하고 content만 전송한다. 삭제의 200/SUCCESS/data:null은 공통 mapper를 거쳐 void 성공으로 처리한다.
- 댓글 목록·작성·수정 응답의 `isMine`은 optional boolean이다. 공개 helper `isOwnNoticeComment`는 true만 본인으로 판정한다. 미제공 필드를 false로 만들어 응답을 변조하지 않는다.
- `noticeKeys`와 `useNoticeQueries`에서 정규화한 page·size·sort·newsId를 키에 포함한다. 상세는 진입마다 조회하고 focus/reconnect/retry에 의한 자동 재요청을 끈다.
- 댓글 mutation은 성공 시 해당 공지의 댓글 페이지들만 무효화한다. 상세 조회수를 증가시키는 상세 재요청과 무관한 공지·목록 갱신을 유발하지 않는다. 오류 시 기존 캐시를 유지한다.
- `CitizenMainRoute`는 별도의 news query로 첫 페이지 10건을 표시하고 새로고침한다. 숫자 ID는 표시 모델 경계에서 문자열로 변환한다. 기존 `/citizen/main`의 다른 정보와 응답 계약은 유지한다.
- MSW 개발 목록 handler를 `/news`로 전환했다. 상세와 댓글 MSW 응답은 HTTP 계약 테스트에서 검증한다. 신규 상세·댓글 UI는 이번 구현 범위에 포함되지 않는다.

## 검증

| 명령 | 결과 |
| --- | --- |
| 중앙 `formatting.py apply` | 수정한 19개 소스 파일에 실제 Prettier 적용 완료. 테스트 수정 후 해당 3개 파일 재적용 완료 |
| `npm run test -- src/features/citizen-participation/api/notice/notice.api.test.ts src/features/citizen-participation/hook/useNoticeQueries.test.tsx src/pages/citizen-participation/ui/CitizenDataRoutes.test.tsx` | 3개 파일, 37개 테스트 통과 |
| `npm run lint` | 통과 |
| `npm run build` | 타입 검사 및 Vite 빌드 통과. 번들 크기 500 kB 초과 경고 있음 |
| `git diff --check` | 통과 |
| `npm run test` | 투표·예약 영역 실패와 반복 act 경고 관찰 후 SIGINT로 중단, exit 130. 전체 통과 아님 |

검증은 실제 Axios와 MSW를 사용했다. 인증 헤더, 6개 API의 취소 신호, page/sort 직렬화, 댓글 입력 경계, 선택적 isMine, null 삭제 결과, 오류 보존, query 실패, 캐시 범위, 상세 진입·포커스·재연결·실패 동작과 메인 10건 표시·새로고침을 확인했다. 초기 메인 테스트의 비동기 렌더 대기를 보완하고 테스트의 미사용 변수를 제거한 뒤 최종 검증했다.

## 전체 테스트의 미해결 사항

- `api/http/citizenParticipation.api.test.ts`: 투표 API가 `/ballots`로 요청하지만 테스트 handler는 `/responses`를 기다린다.
- `mocks/handlers.test.ts`: 투표 관련 3건 실패. 기존 runtime mock도 `/responses`를 사용한다. 변경 전 HEAD의 `vote.api.ts`와 `mocks/handlers.ts`를 `git show HEAD:...`로 확인해 이 경로 불일치가 기존 코드에 있음을 확인했다.
- `mocks/browserHandlers.test.ts`: 실행 중 초기화 지연과 skipped 상태를 관찰했다.
- `CitizenResultRoutes.test.tsx`: 투표 결과 표시 1건 실패를 관찰했다.
- `MeetingReservationRoutes.test.tsx`: 16건 실패와 반복 act 경고를 관찰했다. 이번 작업에서 예약 실패의 원인을 확정하거나 수정하지 않았다.
- 실서버 호출과 시각 QA는 수행하지 않았다. 전체 테스트를 통과했다고 보고하지 않는다.

## 작업 위치와 최종 상태

- 역할: Logic. 프로젝트·worktree: `/Users/okand/SynologyDrive/asan-metaverse-user-ui`.
- branch: `sy-main`, 기준 HEAD: `c9063464ec4cddcf0d847c6b2695ccf3b0b756f9`.
- 기존 9개 파일과 신규 10개 파일을 `fe9d95afbcf9422f30c24c24f05b6275fefcad71`로 커밋했다. `git status --short` 기준 남은 변경은 없다.
- 변경된 기존 파일에 대한 포맷 diff는 중앙의 실제 Prettier 적용 결과다. 관련 없는 기능 동작을 수정하지 않았다.
- 현재 공지 구현에서 발견된 미해결 결함은 없지만, 저장소 전체 검증은 위 실패로 완료되지 않았다.

## 커밋 실행 시도

- 사용자가 19개 소스 파일의 stage·commit 작업을 `명령 실행 승인`으로 승인했다.
- 보호 작업 ID: `095200ef2b53e69eecacb6d12695c7ac`. 메시지: `feat: 공지사항 API 연결 및 메인 공지 전환`.
- 첫 보호 실행은 중앙 `branch-relations/v1/locks/operation-095200ef2b53e69eecacb6d12695c7ac.lock` 접근에 `Operation not permitted`가 발생해 exit 2로 종료됐다.
- 동일 명령을 `require_escalated`로 요청했으나 PreToolUse가 다시 `명령 실행 승인`을 요구하며 차단했다.
- 실패 직후 `show` 결과는 `prepared`였으며 HEAD와 index가 변경되지 않았음을 확인했다.
- 사용자 재승인과 작업 재개 요청 후 같은 ID를 `require_escalated`로 실행했고 exit 0, `stage: done`으로 완료됐다. 승인된 19개 파일만 stage·commit했다.
- 최종 커밋: `fe9d95afbcf9422f30c24c24f05b6275fefcad71` (`feat: 공지사항 API 연결 및 메인 공지 전환`). 19 files changed, 1041 insertions(+), 288 deletions(-).
- 완료 후 `git status --short --branch`, `git log -1`, `git show --stat --oneline HEAD`로 커밋과 깨끗한 작업 폴더를 확인했다. 보호 실행의 fingerprint가 동일했고 소스 추가 수정이 없어 앞선 검증을 반복하지 않았다.
