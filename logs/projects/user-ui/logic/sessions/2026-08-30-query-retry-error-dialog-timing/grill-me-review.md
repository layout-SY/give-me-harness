# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 원인 | 관찰된 지연을 만드는 최소 메커니즘은 무엇인가? | 404를 포함한 server failure의 전역 1회 retry다. | 브라우저에서 수정 전 404 두 번, 수정 후 한 번을 관찰했다. | 4xx retry를 제거한다. |
| 취소 | route 이탈 후에도 main query가 실제 활성 상태인가? | 아니다. observer는 0명이고 fetch 상태는 idle로 복원된다. | route 테스트와 Chromium `net::ERR_ABORTED` | 취소 로직은 유지한다. |
| 범위 | Dialog queue나 production UI를 함께 변경해야 하는가? | 직접 원인 수정에는 필요하지 않다. | retry 제거 후 즉시 Dialog와 정상 abort를 확인했다. | queue/UI는 제외한다. |
| 회귀 | 5xx와 네트워크 오류의 복구 가능성을 보존했는가? | 기존 한 번의 retry를 유지했다. | queryClient 표 기반 테스트 | 503·transport 기대 2회를 유지한다. |
| 검증 | jsdom만으로 사용자 증상을 입증할 수 있는가? | transport abort는 부족하다. | MSW signal은 false였지만 Chromium은 `net::ERR_ABORTED`였다. | 상태 테스트와 실제 브라우저를 함께 사용한다. |

## 결론

승인 범위의 최소 수정으로 404 지연을 제거했으며, 취소·5xx 복구·Dialog 전달의 기존 계약을 보존했다.
