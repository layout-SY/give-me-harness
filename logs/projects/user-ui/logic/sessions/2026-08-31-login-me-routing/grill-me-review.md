# Grill Me 검토

## Method Guardrails (검토 방법 안전장치)

- [x] neutral question-first 적용 여부
- [x] 질문이 검토자를 특정 구현 선택으로 유도하지 않는지 여부

## Neutral Question Flow (중립 질문 흐름)

| 영역 | 중립적 질문 | 답변 | 근거 | Recommended Answer (권장 답변) |
| --- | --- | --- | --- | --- |
| 사용자 동작 | 인증 정보가 없는 사용자가 보호 경로에 처음 들어오면 무엇이 보이는가? | 보호 콘텐츠는 렌더링되지 않고 기존 Dialog에 로그인 필요 안내가 표시된다. | `AuthRouteBoundary.tsx`, `AuthRouteBoundary.reauthentication.test.tsx`, Playwright 비로그인 QA | 최초 렌더에서 콘텐츠를 차단하고 확인 가능한 안내만 제공한다. |
| 이동 상태 | 안내 확인 후 어디로 이동하며 원래 위치는 어떻게 전달되는가? | `/login`으로 replace 이동하며 query·hash를 포함한 안전한 원래 위치가 `returnTo`에 보존된다. | `ApiErrorDialogBridge.tsx`, 브라우저 `history.state.usr.returnTo` 확인 | 현재 위치를 기존 sanitizer로 정제해 Router state로 전달한다. |
| 민감 정보 | 인증 유사 query나 hash가 `returnTo`에 남을 수 있는가? | `createAuthReturnState()`가 이를 제거하며 큐 이벤트에는 경로 자체를 넣지 않는다. | `AuthRouteBoundary.reauthentication.test.tsx`의 credential-like 위치 회귀 테스트 | 인증 정보는 이벤트·navigation state에 포함하지 않는다. |
| 만료 조정 | 이미 보호 콘텐츠를 사용하던 세션이 만료되면 어떤 상태 전이가 발생하는가? | 재인증 Dialog가 활성화된 동안 기존 콘텐츠를 유지하고, 이벤트가 navigation 없이 종료되면 콘텐츠를 차단한다. | `AuthRouteBoundary.tsx`, 만료 조정 테스트 | 최초 비로그인과 사용 중 만료를 구분해 abrupt blank와 무단 노출을 함께 방지한다. |
| 중복 이벤트 | queue 갱신과 Dialog 확인 사이에 재인증 이벤트가 반복 발행되는가? | 활성 queue snapshot과 `hasRequestedReauthentication` ref로 같은 경계 생명주기에서 중복 발행을 막는다. | `AuthRouteBoundary.tsx`, acknowledge·clear·navigation 통합 테스트 | 큐 상태와 생명주기 flag를 함께 사용해 재발행 경합을 차단한다. |
| API 계약 | current-user와 활동 API는 각각 어떤 경로를 사용하는가? | current-user는 `/me`, 활동은 기존 `/citizen/me/activity`를 유지한다. | `me.api.ts`, API 회귀 테스트, Playwright network 요청 | 보고된 current-user endpoint만 최소 변경한다. |
| 재사용·접근성 | 새 UI나 접근성 경로를 추가했는가? | 새 UI 없이 기존 `Dialog`와 `ApiErrorDialogBridge`를 재사용했다. | source diff에 `src/**/ui/**` 없음 | 검증된 공용 Dialog 계약을 재사용한다. |
| 검증 한계 | 브라우저에서 입증하지 못한 것은 무엇인가? | 실제 인증 자격 증명과 CORS 허용이 없어 `/me` 성공 payload는 확인하지 못했다. 요청 pathname은 확인했다. | Playwright network의 `/me` 2회 `net::ERR_FAILED`, `/citizen/me` 0회 | endpoint 선택과 사용자 흐름은 입증하되 실제 backend 성공 응답은 제한으로 명시한다. |

## 결론

- 요구 동작, 기존 자산 재사용, 민감 위치 정제, 만료 경합, endpoint 최소 변경을 반증 질문으로 확인했다.
- 현재 변경을 막는 반례는 발견하지 못했다. 실제 인증된 `/me` 성공 payload 미검증은 명시적 잔여 제한이다.
