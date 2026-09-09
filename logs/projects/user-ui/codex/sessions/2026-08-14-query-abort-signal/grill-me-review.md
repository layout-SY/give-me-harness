# Grill Me 검토

## Method Guardrails

- [x] 원인(미전달 signal) vs UI 로딩 게이트를 분리해 확인
- [x] mutation signal은 타입 부재로 보류

## Neutral Question Flow

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer |
| --- | --- | --- | --- | --- |
| 취소 지점 | HTTP abort가 필요한가, 캐시 무시면 충분한가? | HTTP abort 필요 | 라우트 이탈 후에도 요청이 계속됨 | axios `signal` 전달 |
| 범위 | query만인가 mutation도인가? | query 우선 | 라우팅 취소는 observer unmount | query 연결, mutation은 타입 허용 시 |

## 결론

query path에 AbortSignal을 연결하는 것이 요청된 문제의 직접 해법이다.
