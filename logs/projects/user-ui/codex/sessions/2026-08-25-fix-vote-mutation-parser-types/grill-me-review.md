# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

별도 grill-me 인터뷰는 열지 않았다.

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 수정 위치 | `.then` 인자에 단언을 넣으면 되는가? | 아니다. `parseVoteResponse` 자체가 `error` 유형이다. | ReadLints L51 | 훅이 parser를 `.then`하지 않게 API에서 파싱한다. |

## 결론

닫힌 분기는 생성 POST와 같은 API 파싱이다.
