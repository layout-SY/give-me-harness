# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 응답 경계 | 서버가 반환한 현재 좋아요 상태는 어느 경계에서 검증되고 소비자에게 전달되는가? | vote schema에서 검증하고 parser가 공용 댓글 모델에 그대로 전달한다. | DTO·parser 테스트 및 `voteComments.api.test.ts` | `likeCount`, `liked`를 손실 없이 유지한다. |
| 전송 | 사용자가 원하는 다음 상태에 따라 HTTP method와 경로가 달라지는가? | vote에서 `nextLiked === false`이면 인증 DELETE를 사용하고 나머지는 기존 POST를 유지한다. | API·hook 테스트 | 취소는 DELETE, 추가는 기존 POST 계약을 사용한다. |
| 즉시성 | 서버 응답 전 사용자가 관찰하는 cache 상태는 무엇인가? | 대상 comment의 count가 1 감소하고 `liked`가 false가 된다. | hook optimistic 성공 테스트 | 클릭 직후 다음 상태를 반영한다. |
| 오류 복구 | 취소 대상이 서버에 없을 때 어떤 상태가 남는가? | 404 후 `onMutate` 이전 snapshot 전체가 복원된다. | hook 404 rollback 테스트 | 서버 오류가 로컬 상태를 손상시키지 않아야 한다. |
| 최종 일관성 | optimistic 결과와 서버 상태가 다를 때 무엇이 정본인가? | 성공·실패 모두 comment root를 invalidate해 서버 목록을 다시 조회한다. | `onSettled` 구현과 mutation 테스트 | 서버 재조회 결과를 최종 정본으로 사용한다. |
| mock 현실성 | DELETE 성공과 이미 취소된 상태를 실제 handler 경계에서 구분하는가? | 성공은 200/null, 미좋아요는 404/`LIKE_NOT_FOUND`를 반환한다. | MSW handler 7 tests PASS | API 문서의 상태별 응답을 재현한다. |
| UI 연결 | production route가 현재 다음 좋아요 상태를 mutation에 전달하는가? | 아직 전달하지 않는다. 기존 콜백 계약은 준비됐고 Claude 인계가 필요하다. | `CitizenParticipationDetailRoutes.tsx:97` | `(commentId, nextLiked)`를 그대로 mutation 입력에 전달한다. |

## 결론

- Logic Session 승인 범위의 API·상태 관리·mock 동작은 검증 근거와 일치한다.
- 사용자 노출 흐름의 마지막 연결은 production UI 소유권 때문에 의도적으로 남겨 두었으며 `handoff.md`에 단일 수정 계약을 기록한다.
