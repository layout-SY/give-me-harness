# 평가 로그

## 현재 판정과의 경계

여기서는 Watcher 판정을 다시 평가하지 않는다.

## 장기 관찰 사항

- `CommentList`가 이미 다음 상태를 계산하므로 route와 mutation 사이에서도 boolean을 명시적으로 전달하면 HTTP method 선택이 cache 추론에 의존하지 않는다.
- optimistic update와 서버 응답 기반 update가 하나의 mutation에 공존한다. endpoint별 반환 형식이 더 늘어나면 mutation 결과를 폐쇄형 union으로 표현하는 방안을 검토할 수 있다.
- comment root 아래 여러 page를 한 번에 snapshot·갱신하는 방식은 동일 댓글이 여러 cache에 존재할 때 일관성을 보장한다.

## 목록에 등록할 재사용 가능 자산

- 없음. 이번 변경은 투표 댓글 API 계약에 한정되며 새 공용 UI·hook·utility 추상화를 만들지 않았다.

## 기술 부채

- `CommentLikeTarget.nextLiked`가 optional이며, 현재 `src/pages/citizen-participation/ui/CitizenParticipationDetailRoutes.tsx:97`도 이를 전달하지 않는다. 따라서 vote 좋아요 취소 DELETE 분기는 UI 인계 완료 전까지 실제 route에서 선택되지 않는다.
- vote POST mock은 과거 toggle 동작을 보존한다. 실제 서버의 좋아요 추가 중복 처리 계약이 확정되면 mock도 해당 의미로 좁힐 필요가 있다.
- 번들 크기 경고는 이번 변경과 무관하지만 장기적으로 route 단위 code splitting 검토가 필요하다.

## 프로세스 개선 사항

- production UI와 Logic Session이 나뉘는 작업에서는 UI 콜백 계약을 구현 승인 전에 확인하면 optional 임시 타입의 수명을 줄일 수 있다.
- 자식 브랜치를 만들기 전에 부모 Logic Session 변경을 검증·commit해야 Claude Code가 동일 기준점에서 안전하게 분기할 수 있다.

## 권고 사항

- Claude Code 연결 후 `nextLiked`를 required로 전환할 수 있는지 모든 caller를 점검한다.
- UI 연결 시 `src/pages/citizen-participation/ui/CitizenCommentRoutes.test.tsx`에 `CommentList`의 `nextLiked`가 `VoteDetailRoute`를 거쳐 mutation으로 전달되는 회귀 테스트를 추가한다.
- 성능 경고는 현재 기능 작업과 분리된 별도 승인 범위에서 처리한다.
