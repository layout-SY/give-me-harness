# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

별도 grill-me 세션은 없었다. 아래는 구현 전에 닫힌 가정이다.

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 대상 버튼 | 어느 「내 활동 보기」인가? | 제안 목록 토글. 메인은 내 활동 페이지 이동을 유지한다. | 직전 지시가 list의 `content` 구분 API였고, 토글 문구가 `내 활동 보기`다. | 제안 목록 토글에 activity API를 연결한다. |
| activity 응답 | `/me/activity?content=proposal` 본문은 무엇인가? | 확정 proposal list `data`와 같다. | 사용자는 목록 응답 구조를 유지한다고 했고, 같은 카드 목록에 그린다. | `parseProposalList`로 읽고 `toProposalListItem`으로 표시한다. |

## 결론

토글 표출은 확정 목록 응답을 재사용한다. activity 전용 응답이 나중에 확정되면 parser만 바꾸면 된다.
