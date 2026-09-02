# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 응답 계약 | 집계에 필요한 값이 API에 이미 존재하는가? | 예 | `content.dto.ts` | 기존 count 계약을 유지한다. |
| 공개 정책 | 진행 중 결과가 presentation/UI에 노출되는가? | 아니오 | `resultPresentation.test.ts`, route test | `closed`에서만 ratio를 생성한다. |
| ID 정확성 | 서로 다른 종료 항목이 각자의 비율을 표시하는가? | 예 | vote-2 31/69, discussion-2 30/45/25 | fixture별 count를 mapper에 전달한다. |
| 제출 요청 | Discussion 선택값이 POST body에 포함되는가? | 예 | `discussion.dto.ts`, route, handler test | domain request DTO로 전달한다. |
| 완료 상태 | 개인 제출과 전체 종료를 구분하는가? | 예 | `hasSubmitted`와 `closed` | 완료 문구만 표시하고 결과는 숨긴다. |
| 지속성 | invalidate 후 개인 선택이 유지되는가? | 예 | handler POST→GET tests | 상세 응답의 `my*Choice`를 사용한다. |

## 결론

결과 공개 정책, item별 비율, Vote·Discussion 제출 request와 화면 완료 상태가 서로 분리되어 요구사항을 충족한다.
