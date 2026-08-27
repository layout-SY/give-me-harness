# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 데이터 출처 | production route의 표시 데이터는 어디에서 시작하는가? | MSW HTTP 응답에서 시작한다. | `mocks/handlers.ts`, route DOM test | fixture를 UI component default가 아닌 handler 응답에 둔다. |
| 신뢰 경계 | 응답 metadata가 runtime parser를 통과하는가? | Zod schema로 parsing된다. | parser red→green test | 외부 응답은 parser 이후에만 mapper가 소비한다. |
| 계층 책임 | UI component가 API 호출이나 parsing을 수행하는가? | 수행하지 않는다. | query hook과 pages mapper | transport/query/mapping/render 책임을 분리한다. |
| 임시값 | route가 API 필드를 빈 문자열·0·빈 stages로 대체하는가? | 응답이 있으면 대체하지 않는다. | presentation tests, policy/activity route test | loading fallback만 빈 값으로 유지한다. |
| mock 실행 | 개발 환경에서 추가 env 없이 worker가 시작되는가? | 시작된다. | `startMocks.test.ts` | production은 명시적 opt-in을 유지한다. |
| 범위 | production UI 마크업·CSS를 수정했는가? | 수정하지 않았다. | git diff | 기존 controlled props 계약을 사용한다. |

## 결론

승인된 mock API 데이터 흐름과 UI 소유권 제약을 충족한다. 전체 suite와 governance의 범위 밖 기존 실패는 별도 작업으로 남는다.
