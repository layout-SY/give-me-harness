# Grill Me 검토

## Method Guardrails

- [x] neutral question-first 적용 여부
- [x] 사용자 증상과 자동 재현 결과를 구분했는지 여부

## Neutral Question Flow

| 질문 | 답변 | 근거 | 권고 | Recommended Answer |
| --- | --- | --- | --- | --- |
| 입력 손실이 jsdom에서도 재현됐는가? | 아니다 | StrictMode 문자 단위 테스트 통과 | 사용자 브라우저 증상과 공식 구독 경계를 함께 기록 | `useWatch`로 구독을 명시하고 회귀 테스트를 유지한다 |
| HeroUI adapter를 바꿔야 하는가? | 아니다 | v3 공식 `onChange` 계약과 full payload test | 불필요한 UI 수정 금지 | route form subscription만 변경한다 |
| URL이 route에서 고정되는가? | 아니다 | `onSuccess({ id })`가 그대로 navigation에 전달 | mock response를 수정 | 생성마다 다른 ID를 반환한다 |
| random ID가 필요한가? | 아니다 | 테스트 재현성과 fixture 충돌 회피 요구 | deterministic sequence 사용 | 다음 빈 `proposal-N`을 발급한다 |
| 구문 오류는 범위에 포함해야 하는가? | 그렇다 | proposal test suite가 0 tests로 중단 | prerequisite 최소 수정 | 두 invalidation을 `Promise.all`로 묶는다 |

## 결론

사용자 증상에 필요한 form 구독과 mock ID 경계를 수정했으며 production UI 자체는 변경하지 않았다.
