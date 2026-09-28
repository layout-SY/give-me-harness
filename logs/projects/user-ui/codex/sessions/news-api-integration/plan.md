# 공지사항 API 연결 계획

현재 `sy-main`에서 기존 공지사항 영역을 확장하고 메인 공지를 `/news?page=1&size=10`으로 전환한다. 사용자가 API 연결 구현과 아래 계약을 승인했다. Git 변경은 요청하지 않았으며 수행하지 않는다.

- 역할: Logic. 작업 위치: `/Users/okand/SynologyDrive/asan-metaverse-user-ui`.
- 시작 HEAD: `c9063464ec4cddcf0d847c6b2695ccf3b0b756f9`. 시작 시 미커밋 변경 없음.
- 공지 유형은 `ANNOUNCEMENT`, `EVENT`다. 목록의 서버 정렬 순서를 보존하고 정렬 인자를 보내지 않는다.
- 댓글 목록·작성·수정 응답의 `isMine`은 선택적 boolean이다. `true`만 본인 댓글로 인정한다.
- 상세는 진입할 때 조회하며 포커스·재연결·실패에 따른 자동 재요청을 끈다.
- 메인 공지는 첫 페이지 10건이다. 나머지 API 기본 페이지는 1, 크기는 20이다.
- `items/total/page/size` 공통 DTO·schema 추가를 승인받았다.

## 구현과 검증

1. `src/shared/api/common/`에 공통 페이지 응답을 추가하고 `api/notice/`에서 6개 endpoint의 요청·응답 검증과 인증·취소를 연결한다. `ApiClient`, `ApiResult`, `withAbortSignal`, 기존 오류 처리를 재사용한다.
2. 공지 전용 query key와 hook을 구성하고 댓글 변경 성공 시 해당 공지의 댓글 목록만 무효화한다. 숨겨진 공지의 404와 댓글 403을 오류로 유지한다.
3. `CitizenMainRoute`에 목록 조회를 연결하고 숫자 ID를 기존 표시 모델에 매핑한다. 새 상세 화면은 생성하지 않는다.
4. 기존 MSW와 Vitest를 사용해 실제 Axios 요청, 성공·빈 목록·오류·취소, 댓글 검증, 캐시 범위, 상세 재조회, 메인 10건 연결을 확인한다.
5. 중앙 `formatting.py apply` 실행 후 `npm run lint`, `npm run test`, `npm run build`로 검증한다. 결과와 미완료 항목을 같은 세션의 `final-summary.md`에 기록한다.

## 탐색 근거

- 기존 공지는 `/citizen/notices`의 배열 응답이며 `useNoticeListQuery`의 화면 사용처가 없다.
- 메인은 `/citizen/main`의 `notices`로 표시하므로 기존 메인 데이터와 신규 목록의 연결을 분리한다.
- 공통 `dto.ts`에는 새 페이지 응답 구조가 없고 `ApiClient`가 envelope를 처리한다. 삭제의 `data: null`은 공통 mapper에서 `undefined`로 정규화된다.
- 인접 `discussion.api.ts`, `vote.api.ts`, query·mutation hook과 MSW 테스트를 확인했다.
- 적용 스킬: task-role-routing, git-branch-strategy, api-authoring 및 transport-contracts/query-mutation, coding-convention, type-definition, data-fetch-layer, abstraction-strategy, implementation-quality, documentation.

## 승인 검사 이력

- 요구사항 결정은 모두 확정되었지만 소스 수정 시 PreToolUse가 `소스 구현 준비가 필요합니다: 사용자 구현 승인`으로 차단했다.
- 공통 페이지 DTO와 공지 API·DTO·parser 패치는 적용되지 않았다. 동일 차단 재시도는 하지 않았다.
- 이후 사용자가 `진행해`로 확정 계획을 승인했고 소스 변경이 정상 허용되었다. 구현과 검증 결과는 `final-summary.md`에 기록했다.

## 완료 상태

- 위 구현 항목 1~4 완료.
- 자동 포맷, 관련 37개 테스트, lint, build 통과.
- 전체 테스트는 투표·예약 영역 실패와 반복 경고를 관찰한 후 중단했다. 전체 통과로 판정하지 않는다.
