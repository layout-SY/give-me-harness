# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 요청 계약 | 사용자가 클릭한 댓글 ID가 실제 nested endpoint까지 전달되는가? | 예 | `comment.api.ts`, 상세 route 2개 | 댓글 ID를 path에 포함한다. |
| 상태 전이 | 좋아요와 취소가 모두 요청 전에 관찰되는가? | 예 | mutation focused test | 현재 `liked` 기준 `±1`과 boolean 반전이 적절하다. |
| 실패 처리 | 서버 실패가 다른 값으로 남지 않는가? | 예 | rollback test | 모든 matching page snapshot 복원이 적절하다. |
| 서버 보정 | optimistic 값과 서버 값이 다를 때 무엇이 기준인가? | 서버 응답 | mutation success test | `{ likeCount, liked }` 응답으로 대상 댓글을 보정한다. |
| 사용자 표면 | 같은 하트를 두 번 누르면 원래 상태로 돌아오는가? | 예 | Policy route DOM test | `3/false → 4/true → 3/false`를 유지한다. |
| 접근성 | 상태와 동작 이름이 보조기술에 노출되는가? | 예 | Claude Code의 `aria-pressed`, 동적 `aria-label` | 좋아요와 좋아요 취소 이름을 구분한다. |
| 동시성 | 여러 댓글의 동시 요청 상태를 모두 표현하는가? | 아니오 | 단일 `likePendingId` | 후속 요구가 생기면 pending ID 집합 또는 comment별 mutation으로 확장한다. |

## 결론

단일 댓글의 좋아요·취소 요청, optimistic 상태, 서버 보정, rollback, 실제 route 왕복은 요구사항을 충족한다. 다중 댓글 동시 요청 표현은 별도 장기 개선 항목이며 현재 범위의 정상 클릭 흐름을 막지 않는다.
