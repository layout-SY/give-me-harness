# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 원인 | 댓글 작성 상태를 결정하는 실제 입력은 무엇인가? | `/me` 성공 여부였다. | 기존 route의 `meQuery.isSuccess` 전달과 재현 테스트 | credential presence와 profile query를 분리한다. |
| 상태 정본 | 인증 presence를 어디에서 소유해야 하는가? | 기존 `authSession` revision store가 session 변경을 이미 소유한다. | `authSession.ts`, `useSignInMutation.ts` | 별도 Zustand store를 만들지 않는다. |
| 유효성 | client가 token 유효성을 언제 판단해야 하는가? | 요청 전 선판정하지 않는다. | 사용자 요구와 전역 401 reporter | token presence로 요청하고 backend 401을 따른다. |
| redirect | token 없음과 token 401을 같은 UX로 처리해야 하는가? | 아니다. | `AuthRouteBoundary`와 `ApiErrorDialogBridge` | token 없음은 direct login, 401은 Dialog 종료 후 login. |
| URL 보안 | URL credential은 언제 제거해야 하는가? | 가능한 가장 이른 동기 startup 시점이다. | Watcher 초기 FAIL, `main.tsx` 수정 | `startMocks()` 전에 bootstrap한다. |
| 복귀 | 로그인 후 원래 위치는 새 계약이 필요한가? | 기존 안전한 `returnTo` 계약이 있다. | `authReturnLocation.ts`, Login 테스트 | 기존 sanitizer와 state를 재사용한다. |
| 회귀 | `/me` 실패 상황에서 사용자 결과를 어떻게 증명하는가? | 세 상세 route의 textarea 활성화를 렌더링 테스트한다. | `CitizenCommentRoutes.test.tsx` | token fixture와 `/me` 401 조건을 사용한다. |

## 결론

- 요구사항을 기존 authSession·error queue·returnTo 경계에 배치해 중복 상태와 중복 Dialog를 만들지 않았다.
- Watcher가 지적한 startup credential 노출 시간을 수정했으며 최종 PASS를 받았다.
