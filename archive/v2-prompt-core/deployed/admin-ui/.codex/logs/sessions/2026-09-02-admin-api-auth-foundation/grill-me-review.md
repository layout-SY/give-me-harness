# Grill Me 검토

## 결론

현재 구현은 오류 소유권, 민감 정보, 401 의미, 인증 상태 일관성, startup 순서와 승인 범위를 실행 근거로 설명할 수 있다. 최초 Watcher가 발견한 silent refresh 401 결함은 failing-first 테스트 후 수정됐고 최종 Watcher 판정은 PASS다.

## 중립 질문 흐름

| 영역 | 질문 | 답변과 근거 |
| --- | --- | --- |
| 오류 소유권 | Axios, `useApi`, Query를 거친 같은 오류가 중복 표시되는가? | Axios는 report하지 않고 reporter의 module-level `WeakSet`이 동일 오류 객체를 한 번만 claim한다. |
| 민감 정보 | raw payload·token·header가 diagnostics나 Dialog에 노출되는가? | failure와 diagnostics는 allowlist field만 복사하며 회귀 테스트에서 민감 문자열 부재를 확인했다. |
| 401 결합도 | shared 오류 계층이 auth store나 route를 직접 참조하는가? | shared는 `reauthenticate` event까지만 생성하고 app bridge가 Dialog와 session clear를 조립한다. |
| refresh 401 | silent refresh 401이 presentation filter에서 소실되는가? | 401 재인증 판단을 filter보다 먼저 수행하며 failing-first 테스트가 queue event를 고정한다. |
| sign-in 401 | 잘못된 자격증명이 강제 재인증으로 처리되는가? | sign-in만 `unauthorizedBehavior: "error"`를 사용해 caller-owned 오류로 남긴다. |
| 인증 일관성 | token과 Zustand가 서로 어긋나는가? | write·clear·bootstrap을 `auth-session.ts` 한 경계에서 처리하고 revision을 함께 갱신한다. |
| stale refresh | 늦은 refresh가 새 로그인이나 logout을 덮는가? | 요청 당시 revision과 refresh token이 모두 현재 값일 때만 commit한다. |
| startup | URL token 처리 전에 앱 요청이 시작되는가? | `bootstrapAuthSession()`을 MSW startup과 React mount보다 먼저 호출한다. |
| UI 범위 | 로그인 page 없이 route guard를 활성화했는가? | production `/sign-in`과 보호 route는 제외하고 기존 Dialog만 재사용했다. |
| 검증 | 환경성 SIGBUS를 앱 통과로 숨겼는가? | 상충 관찰을 보존하고 최종 no-cache·tsconfig·직렬 73/73과 앱 변경 테스트를 분리해 기록했다. |
| 승인 범위 | 변경 경로가 승인 scope와 일치하는가? | `CustomException` 경로는 별도 사용자 승인 후 metadata에 추가했고 25개 병합 파일은 모두 scope 안이다. |

## 결론적 답변

- typed normalization과 terminal reporting 경계를 유지한다.
- shared와 app/auth side effect의 의존 방향을 유지한다.
- raw error logging을 다시 도입하지 않는다.
- production 로그인 UI와 route guard는 별도 승인 작업으로 연결한다.
