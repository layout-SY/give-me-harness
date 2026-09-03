# 평가 로그

## 현재 판정과의 경계

여기서는 Watcher 판정을 다시 평가하지 않는다.

## 장기 관찰 사항

- 투표·토론도 `mine` query로 통일되면 `/me/activity` 분기를 같은 패턴으로 줄일 수 있다. 지금은 제안만 확정됐다.
- 허용 sort가 전송 계층에만 있고 화면 컨트롤이 없다. 백엔드가 기본값을 강제하면 클라이언트가 `sort`를 생략하는 쪽이 더 단순해질 수 있다.
- `MyActivityToggle`의 optional `label`은 제안만 다른 문구를 쓴다. 다른 목록도 문구가 갈리면 라벨을 화면별로 넘기는 계약이 남는다.

## 목록에 등록할 재사용 가능 자산

없음. 새 공용 UI/훅을 추가하지 않았다. `PROPOSAL_LIST_SORT`는 proposal list 전용 상수다.

## 기술 부채

- `ProposalListPage`는 응답에 없는 `summary`를 빈 문자열로 받아 빈 `<p>`를 그릴 수 있다.
- 내 활동 페이지는 여전히 `/me/activity`를 쓰고 제안 목록은 `mine`을 쓴다. 같은 「내 활동」 개념이 두 요청으로 나뉜다.
- 화면 URL은 `myActivity=true`, 서버 query는 `mine=true`다. 이름 불일치는 라우트 상태가 서버 계약을 직접 쓰지 않기 때문이다.

## 프로세스 개선 사항

직전 세션에서 내 활동을 `/me/activity`로 분리한 직후, 이번 지시가 list `mine`으로 되돌렸다. 목록 필터 API를 화면 작업과 한 문서에 묶어 전달하면 DTO를 두 번 바꾸지 않아도 된다.

## 권고 사항

투표 목록 `mine` 계약이 확정되면 `VoteListRoute`의 activity 분기를 같은 list query로 옮길 수 있다. 그 전에는 제안만 유지한다.
