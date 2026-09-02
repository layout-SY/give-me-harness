# 평가 로그

## 현재 판정과의 경계

여기서는 Watcher 판정을 다시 평가하지 않는다. 자동 Evaluator 호출은 Anthropic 크레딧 부족으로 실행되지 않아 역할 계약을 직접 적용했다.

## 장기 관찰 사항

- `useLikeMutation`의 comment-root cache 갱신은 다른 comment mutation에도 재사용 가능한 패턴이다.
- stateful MSW factory는 테스트 간 상태 누수를 막으면서 POST 후 GET 일관성을 검증한다.

## 목록에 등록할 재사용 가능 자산

- `createCitizenParticipationHandlers()`: handler instance별 mutable mock state 격리
- `citizenParticipationKeys.commentRoot()`: paginated comment cache 일괄 갱신 prefix

## 기술 부채

- `likePendingId` 한 개만 노출하므로 여러 댓글을 거의 동시에 누르는 경우 모든 요청의 pending 상태를 표현하지 못한다.
- `presentation.ts`는 pure LOC 231로 경고 구간이다. 다음 기능 추가 전 content별 mapper 분리를 검토한다.
- `mocks/fixtures.ts`는 댓글 10건 추가 후 pure LOC 217이다. 다음 fixture 확장 시 content fixture와 comment fixture를 분리한다.

## 프로세스 개선 사항

- 공유 worktree에서 Claude Code UI와 Hephaestus 통합 변경의 완료 신호를 파일 계약과 함께 중계하면 재확인 횟수를 줄일 수 있다.
- 전체 build 차단 파일의 소유 세션과 해결 상태를 세션 로그에 일찍 기록한다.

## 권고 사항

- 실제 제품이 동시 댓글 reaction을 허용해야 할 때 `ReadonlySet<commentId>` pending 계약 또는 comment별 mutation 상태를 도입한다.
- 새로운 optimistic comment 동작은 현재의 성공 보정·실패 rollback·POST 후 GET 테스트 묶음을 기준으로 재사용한다.
