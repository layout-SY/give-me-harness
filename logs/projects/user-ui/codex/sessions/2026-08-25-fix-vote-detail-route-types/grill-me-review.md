# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

별도 grill-me 인터뷰는 열지 않았다. 사용자는 오류 수정을 지시했다.

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 수정 위치 | 68–71행 할당을 바꾸면 되는가, import를 바꿔야 하는가? | import. `useVoteDetailQuery` 호출부터 해석되지 않는다. | ReadLints L50 unsafe call | barrel 대신 훅 깊은 경로 |

## 결론

닫힌 분기는 import 경계 수정이다.
