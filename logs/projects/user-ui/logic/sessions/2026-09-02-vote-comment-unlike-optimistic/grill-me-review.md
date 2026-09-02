# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 목표 | 현재 변경이 어떤 사용자 동작을 복원하는가? | 기존 좋아요 댓글의 재클릭이 DELETE를 선택하고 즉시 상태·수를 감소시킨다. | `presentation.ts`, `useCitizenParticipationMutations.ts`, 라우트 통합 테스트 | DTO 상태가 UI와 mutation 선택까지 끊김 없이 전달되어야 한다. |
| 계약 | API/cache와 UI의 필드명이 다를 때 어디서 변환하는가? | presentation adapter에서 `likedByMe`를 `liked`로 변환한다. | `toCommentItem()` | 각 계약은 유지하고 경계에서 명시적으로 변환한다. |
| 실패 | DELETE가 404를 반환하면 어떤 상태가 남는가? | `onError`가 이전 캐시 snapshot을 복원한다. | mutation 구현과 404 rollback 테스트 | 낙관적 갱신 이전 상태가 복원되어야 한다. |
| 요청 | 전송 method와 URL은 계약과 일치하는가? | DELETE `/citizen/votes/{voteId}/comments/{commentId}/likes`다. | vote API 및 API wire 테스트 | backend 계약과 정확히 일치해야 한다. |
| fixture | 테스트 데이터가 실제 DTO 형태를 모사하는가? | 목록 댓글은 `likedByMe`, mutation 응답은 `liked`를 유지한다. | DTO, fixture, handler 테스트 | 서로 다른 계약을 범용 shape로 합치지 않는다. |
| 범위 | 버그 수정에 필요하지 않은 UI나 구조 변경이 포함됐는가? | 포함되지 않았다. | 9개 source/test diff 및 branch scope | 최소 adapter·테스트 정렬만 유지한다. |
| 검증 | 변경이 관련·전체 회귀에서 안전한가? | 관련 51개와 전체 469개, governance 20개, lint, build가 통과했다. | 실행 결과 | 정적·동작 검증이 모두 통과해야 한다. |

## 결론

- Watcher는 현재 diff를 독립 검토해 PASS로 판정했다.
- 차단 또는 주요 발견 사항은 없다.
- 정상 backend 불변식 밖의 `likedByMe=true`, `likeCount=0` 조합은 기존 잔여 위험이며 이번 변경에서 새로 만든 문제는 아니다.
