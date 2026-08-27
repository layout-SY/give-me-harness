# 평가 로그

## 현재 판정과의 경계

여기서는 Watcher 판정을 다시 평가하지 않는다.

## 장기 관찰 사항

- `VoteDetailPage`가 `ongoing`/`closed`만 있으면 시작 전·중단이 완료 뱃지로 보일 수 있다. 전용 상태가 확정되면 UI 계약을 확장해야 한다.
- 댓글 OpenAPI 표기 `/citizen/votes/{voteId}/comments`와 현재 `/v1/api/citizen-participation/votes/{id}/comments`가 다르다. comments 계약이 확정되면 경로를 한 번에 맞춰야 한다.
- 투표 POST 응답은 여전히 `{ id: string, completed, choice }`다. 상세의 숫자 `id`와 맞출지는 미확정이다.

## 목록에 등록할 재사용 가능 자산

없음. 새 공용 UI/훅을 추가하지 않았다. `useVoteDetailQuery`는 투표 상세 전용이다.

## 기술 부채

- 시작 전·중단 안내가 `period` 문자열에 붙어 있다. UI가 상태별 카피를 갖게 되면 매퍼에서 분리할 수 있다.
- MSW 목록 `startsAt`/`endsAt`은 fixture 일정 헬퍼를 쓰지만 실서버 값과 동일하다는 보장은 없다.

## 프로세스 개선 사항

상세 JSON 예시에 시작 전·중단 status 문자열이 없었다. 목록 400 값으로 추론했다. 이후에는 상세 성공 예시에 해당 status를 같이 주면 enum을 두 번 정하지 않아도 된다.

## 권고 사항

Claude Code가 예정/중단 뱃지와 투표 불가 안내를 `VoteDetail` props로 받으면 `period` 접두사 매핑을 거둘 수 있다.
