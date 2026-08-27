# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

별도 grill-me 인터뷰 세션은 열지 않았다. 아래 행은 구현 전에 사용자 대화에서 닫힌 분기만 기록한다.

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 모의 켜는 조건 | 모의 서버는 언제 켜는가? | `.env`의 `VITE_API_BASE_URL_STATUS`가 `dev`일 때만 | 사용자: `VITE_API_BASE_URL_STATUS가 dev일 때만 사용하도록` | `status.trim() === "dev"`일 때만 `worker.start` |
| 기존 스위치 | `VITE_ENABLE_MSW`와 DEV 기본 켜짐을 유지하는가? | 아니오. 새 변수가 단일 스위치다 | 사용자가 새 변수만 지정했다 | `VITE_ENABLE_MSW`를 제거한다 |

## 결론

닫힌 분기는 구현에 반영했다. 열려 있는 것은 `dev`가 아닌 상태값의 이름이다.
