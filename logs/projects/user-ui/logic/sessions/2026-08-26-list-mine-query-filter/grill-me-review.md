# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

별도 grill-me 인터뷰 세션은 열지 않았다. 아래 행은 구현 전에 사용자 대화에서 닫힌 분기만 기록한다.

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 목록 필터 출처 | 「내 활동만 보기」는 어느 요청인가? | 별도 API가 아니라 목록 query의 true/false | 사용자: `별도 API가 아닌 쿼리에 true/false로 요청하는 방식으로 변경해` | 각 목록 endpoint에 `mine=true|false`를 보낸다. |
| 이전 구성 | `/me/activity`로 목록 필터를 하던 내용은? | 지운다 | 사용자: `별도 API 구성으로 "내 활동만 보기"를 한다는 내용을 지워주고` | `useMyProposalActivityQuery`와 목록 라우트의 activity 분기를 제거한다. |
| 제안과 동일성 | 다른 목록도 제안과 같은가? | 같다 | 사용자: `제안 관련 도메인에 반영된 내용처럼` | 투표·토론·정책 목록도 `mine` query를 쓴다. |

## 결론

닫힌 분기는 구현에 반영했다. 열려 있는 것은 내 활동 페이지 전체 조회 계약이다.
