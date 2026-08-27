# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

별도 grill-me 세션은 없었다. 사용자는 `Fix it`으로 구현을 지시했다. 아래는 구현 중 닫힌 가정이다.

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 오류 실체 | 런타임 버그인가, 타입/lint 오류인가? | 편집기 typescript-eslint 오류 유형이다. CLI tsc는 이미 통과했다. | 사용자 메시지와 ReadLints 규칙명 `no-unsafe-assignment` | 훅/DTO/import 경계를 고쳐 오류 유형을 없앤다 |
| 수정 위치 | UI 파일만 고치면 되는가? | 루트는 훅과 barrel 순환이다. 라우트는 import와 지역 매핑만 고친다 | 훅 파일 L95 `proposalList` 미해결, ListRoutes도 동일 훅에서 오류 | UI 마크업은 유지하고 타입 경계를 고친다 |
| 우회 | `any`/eslint-disable로 막을 수 있는가? | 규약이 `any`를 금지하고, 사용자는 원인을 고치라고 했다 | `policy/coding-convention` | disable 없이 타입을 복구한다 |

## 결론

런타임 계약을 바꾸지 않고, 오류 유형의 출처(훅 추론, barrel 순환, presentation↔페이지 순환)를 끊는 쪽으로 진행한다.
