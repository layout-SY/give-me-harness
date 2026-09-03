# 탐색

## 결론

기존 ProposalStatus는 lowercase이고 Vote·Discussion 선택값은 DTO마다 inline literal이었다. production UI도 lowercase 값을 사용하므로 API 계약만 uppercase로 바꾸면 route에서 타입과 런타임 값이 충돌한다.

## 발견 사항

| 영역 | 기존 계약 | 확정 대응 |
| --- | --- | --- |
| Proposal | `received`, `reviewing`, `adopted`, `rejected` | uppercase ProposalStatus와 `UNDER_REVIEW` 적용 |
| Vote 선택 | `agree`, `disagree` inline schema | 독립 VoteChoice 상수·타입 적용 |
| Discussion 선택 | `agree`, `disagree`, `neutral` inline schema | 독립 OpinionStance 상수·타입 적용 |
| MSW 저장 | Vote·Discussion 공용 choice map | VoteChoice와 OpinionStance map 분리 |
| production UI | lowercase 선택값 | route 양방향 adapter 유지 |

## 변경하지 않은 값

- `scheduled`, `open`, `closed`는 미확정 참여 lifecycle 값이므로 유지했다.
- VoteStatus·DiscussionStatus 등 아직 제공되지 않은 도메인 값은 임의로 만들지 않았다.

## UI 소유권

`VoteDetailPage.tsx`, `DiscussionDetailPage.tsx`, `ProposalListPage.tsx`는 직접 수정하지 않았다. `CitizenParticipationDetailRoutes.tsx`에서 transport와 UI 값을 변환한다.
