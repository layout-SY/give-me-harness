# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

별도 grill-me 인터뷰는 열지 않았다. 아래는 사용자 스펙으로 닫힌 분기다.

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 요청 body | POST에 무엇을 보내는가? | `{ choice: "AGREE" }` | 사용자 예시 | `VoteRequestDto`는 `choice`만 |
| 참여 조건 | 언제 참여할 수 있는가? | 진행 중만, 1인 1표, 변경 불가 | 사용자 설명 | IN_PROGRESS가 아니면 409, 재투표는 ALREADY_VOTED |
| 오류 구분 | 불가를 한 메시지로 묶는가? | 아니오. 409 코드로 가른다 | 사용자: 네 코드 나열 | MSW와 도메인 상수가 네 코드를 가짐 |
| 200 응답 | 성공 `data`를 새로 설계하는가? | 아니오. 이번 JSON 없음 | 사용자 메시지에 200 예시 없음 | 기존 `{ id, completed, choice }` 유지 |

## 결론

닫힌 분기는 구현에 반영했다. 열려 있는 것은 성공 응답 재설계와 409 화면 문구다.
