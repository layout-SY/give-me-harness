# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용
- [x] 확정되지 않은 lifecycle 값을 임의로 추가하지 않음

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 상수 계약 | 세 값 집합이 서로 독립적인가? | 예 | `constants.ts` | 별도 `as const`와 파생 타입을 유지한다. |
| API 경계 | lowercase 선택값을 수용하는가? | 아니오 | Vote·Discussion Zod schema | 외부 입력은 uppercase만 파싱한다. |
| 상태 저장 | Vote에 중립 선택이 섞일 수 있는가? | 아니오 | 분리된 MSW map 타입 | VoteChoice map을 별도로 유지한다. |
| UI 소유권 | production UI를 직접 바꿨는가? | 아니오 | route adapter | UI lowercase 계약은 adapter 뒤에 둔다. |
| Proposal 표시 | `UNDER_REVIEW`가 기존 검토중 UI로 보이는가? | 예 | presentation mapping | transport와 presentation 값을 분리한다. |
| 미확정 값 | 참여 lifecycle을 uppercase로 추측했는가? | 아니오 | `PARTICIPATION_STATUS` 유지 | 백엔드 확정 전 기존 값을 유지한다. |

## 결론

확정된 세 도메인 값만 분리했고 API·mock·presentation·route에서 동일 계약을 사용한다.
