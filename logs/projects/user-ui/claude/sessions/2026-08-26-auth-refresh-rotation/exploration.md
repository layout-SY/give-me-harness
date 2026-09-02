# 탐색

## 요청

사용자는 `POST /auth/refresh`로 리프레시 토큰을 보내 새 액세스·리프레시 토큰을 받으며, 인증 없이 호출한다고 했다. 리프레시 토큰은 1회용이라 응답 토큰으로 갈아끼워야 하고, 이미 쓴 토큰을 다시 보내면 그 계정의 리프레시 토큰이 전부 폐기되어 재로그인이 필요하다.

## 대상 관련 사실

- 기존 DTO는 이미 `{ refreshToken }` 요청과 SUCCESS `data` `{ accessToken, refreshToken, tokenType: "Bearer", expiresIn }` 응답이다. API 테스트가 같은 계약을 검증한다.
- `authSession`은 성공 시 `persistAuthSession`으로 새 토큰을 저장했지만, 전송 중 같은 토큰을 막지 않았고 실패 시 세션을 남겼다.
- 인증 Axios에는 Bearer 인터셉터가 없어 refresh는 무인증이다.
- `src/shared/ui/`는 이번 세션 작업과 무관하다.

## 불러온 스킬

- `.agents/skills/SKILL.md`
- `policy/harness`, `policy/coding-convention`, `policy/type-definition`, `policy/data-fetch-layer`, `policy/hook-extraction`, `policy/abstraction-strategy`, `policy/documentation`, `policy/portfolio`, `policy/review-checklist`
- `recipe/api-authoring`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| 공용 UI | 제외 | 세션 회전이며 UI 변경이 없다 |

## 제약 조건 및 미확인 사항

- 실패 HTTP 상태 코드는 스펙에 없다. 갱신 실패면 세션을 지운다.
- 여러 탭이 동시에 refresh하는 잠금은 지시되지 않았다.

## 결론

전송 계약은 유지하고, 세션 계층에서 토큰을 꺼내 한 번만 보내며 성공 시 교체, 실패 시 세션 삭제로 재사용 폐기를 피한다.
