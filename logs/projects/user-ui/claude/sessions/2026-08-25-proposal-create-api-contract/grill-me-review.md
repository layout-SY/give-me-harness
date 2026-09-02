# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

별도 grill-me 인터뷰 세션은 열지 않았다. 아래 행은 구현 전에 사용자 대화에서 닫힌 분기만 기록한다.

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 요청 필드 | 생성 POST body에 어떤 키가 들어가는가? | `title`, `background`, `content`, `expectedEffect`, 선택 `referenceCase` | 사용자 예시 JSON | 옛 `body`/`detail`/`effect`/`reference`를 이 이름으로 교체한다. |
| 선택 필드 | `referenceCase`를 빼면 무엇이 저장되는가? | `null` | 사용자: `생략하면 null로 저장된다` | 빈 폼 값은 `referenceCase: null`로 보낸다. |
| 성공 응답 | 성공 시 클라이언트가 무엇을 읽는가? | 201과 `Location: /citizen/proposals/{id}` | 사용자: `성공하면 201과 함께 Location` | JSON `{ id, completed }`를 유지하지 않고 Location에서 id를 파싱한다. |
| 작성 UI | 폼 필드명을 API 키로 바꿀 것인가? | 아니오. 페이지 마크업은 이번 범위가 아니다. | `ProposalWritePage`는 Claude Code 소유 | 매퍼만 `detail`→`content`, `effect`→`expectedEffect`로 옮긴다. |

## 결론

닫힌 분기는 구현에 반영했다. 열려 있는 것은 proposal 상세 GET 계약과 201 JSON body 여부다.
