# 댓글 응답 mine 전환 계획

댓글 응답의 본인 여부 필드를 사용자가 확정한 `mine`으로 통일하고, 연결된 본인 확인·mock·테스트를 함께 변경한다.

- 역할: 확인된 Logic, 작업 책임: owner.
- 위치: `/Users/okand/SynologyDrive/asan-metaverse-user-ui`, `sy-main`, 시작 HEAD `fe9d95afbcf9422f30c24c24f05b6275fefcad71`.
- 사용자 결정: 댓글 API 응답의 `isMine`을 `mine`으로 변경. 계획 제시 후 사용자의 `커밋 진행` 요청에 따라 구현·검증·커밋을 준비한다. Git 실행은 구체적인 명령에 대한 별도 승인 절차를 따른다.
- 시작 상태: staged·unstaged·untracked 변경 없음.
- 범위: `src/features/citizen-participation/` 안의 댓글 DTO 3개, 투표 목록 파서, 댓글 action hook, 공지 댓글 본인 확인 함수, 기존 mock·fixture·테스트. 기존 선택 boolean과 `true`만 본인으로 인정하는 동작을 보존한다.
- 재사용: `commentSchema`, `voteCommentSchema`, `noticeCommentSchema`, `parseVoteCommentList`, `isOwnNoticeComment`, `useCitizenCommentActions`, 기존 API·hook·MSW 테스트를 수정한다. 공통 `PageResponseDto`·`createPageResponseSchema`와 ApiClient envelope 처리 구조를 유지한다.
- 조사: 위 경로와 `src/shared/api/common/`, 수정 mutation의 기존 캐시 병합, 댓글 조회·작성·수정·삭제 테스트를 확인했다. mutation은 기존 댓글을 spread하므로 변경된 소유 필드를 그대로 보존한다.
- 적용 스킬: task-role-routing, git-branch-strategy, skill-index, coding-convention, type-definition, data-fetch-layer, implementation-quality, documentation.

## 작업 순서

1. 현재 workdir의 기존 댓글 테스트 입력·기대값을 `mine`으로 변경하여 새 응답 계약의 회귀 검증을 준비한다.
2. 같은 workdir에서 DTO·파서·본인 확인·mock을 `mine`으로 변경하여 데이터 전달과 수정·삭제 판단을 일치시킨다.
3. 지정된 `formatting.py apply`를 실행하고 lint·test·build로 타입·기능·빌드를 확인한다.
4. 변경 diff와 검증 결과를 확인하고 최종 요약을 작성한다. 승인된 경로만 stage·commit하도록 실제 명령을 준비한다.

## 완료 기준

- 댓글 구현·mock·테스트가 새 필드를 사용하고, `mine: true/false` 및 필드 생략을 기존 정책대로 처리한다.
- 댓글 수정 후 캐시에 본인 여부가 보존되고 타인 댓글 관리가 거부된다.
- 포맷·lint·test·build 결과와 커밋 상태를 실제 실행 근거로 기록한다.

## 현재 상태

- 사용자의 후속 `계획대로 진행`으로 구현 승인을 받고 14개 파일의 패치를 적용했다.
- 구현 재개 시 추가된 `src/features/inquiry/`의 untracked 변경은 별도 작업으로 보존하며 이번 stage·commit 대상에서 제외한다.
- 정책 훅이 안내한 host·session 지정 공통 포맷 명령으로 14개 파일의 실제 Prettier 처리를 완료했다.
- 변경 파일 lint·댓글 관련 71개 테스트·전체 빌드가 통과했다. 전체 lint는 별도 inquiry 작업의 오류, 전체 테스트 재실행은 투표·토론 관련 13개 실패가 남았다. 상세 근거는 `final-summary.md`에 기록했다.
- 승인된 댓글 변경 14개 파일만 stage·commit해 `8ba021a3e7148a8b13f94d8906213a882bdf8205`를 생성했다. 보호 실행기 결과 `done`과 커밋 후 index·작업 트리 상태를 확인했다. 별도 inquiry 변경은 보존했다.
