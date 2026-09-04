---
name: hook-use-auth
description: {{PROJECT_NAME}}의 useAuth 훅(src/features/auth/use-auth.ts) 사용 및 수정 가이드. 로그인, 토큰 갱신, 로그아웃과 store·localStorage 반영을 다룰 때 사용.
---

# useAuth

## 대상

- `src/features/auth/use-auth.ts`
- `src/features/auth/model/auth.store.ts`
- `src/entities/users/model/user.store.ts`
- `src/entities/auth/api`
- `src/shared/lib/utils/token.util.ts` (`getJwtTokenStatus`)
- `src/shared/config/constants.ts` (토큰 키)

`src/shared/lib/hooks`가 아니라 **`src/features/auth` 아래에 있다.** 인증 기능 슬라이스에 속한다.

## 계약

```ts
const { getAuthentication, refreshAuthentication, rmAuthentication } = useAuth();
```

| 함수 | 동작 |
| --- | --- |
| `getAuthentication(loginId, password)` | 로그인. 성공 시 access·refresh 토큰을 `localStorage`에 저장하고 user store와 `isAuthenticated`를 갱신한다 |
| `refreshAuthentication()` | 저장된 refresh 토큰으로 재발급. 토큰이 없거나 유효하지 않으면 두 토큰을 모두 제거하고 종료한다 |
| `rmAuthentication()` | 로그아웃. 토큰 제거, user `null`, `isAuthenticated` 해제 |

내부적으로 `useApi`의 `execute`를 사용하고 상태는 zustand store에 반영한다.

동작에서 알아야 할 점은 다음과 같다.

- 로그인 실패에서 `CustomException`은 **다시 throw한다.** 화면이 잡아 처리해야 한다. 그 외 `Error`는 `alert`로 표시된다.
- `refreshAuthentication`은 `silent: true`다. 실패해도 UI를 띄우지 않는다.
- 갱신 응답이 도착했을 때 저장된 refresh 토큰이 요청 시점과 다르면 **응답을 버린다.** 로그인 등 다른 인증 흐름이 이미 토큰을 교체한 경우를 보호한다.
- 갱신 응답에 `accessToken`·`refreshToken`·`profile` 중 하나라도 없으면 아무것도 반영하지 않는다.
- `rmAuthentication`의 서버 로그아웃 호출은 현재 주석 처리되어 있다. 로컬 정리만 수행한다.

## 사용 기준

- 인증 상태 변경은 이 훅을 거친다. `localStorage` 토큰 키나 store를 화면에서 직접 조작하지 않는다.
- 로그인 화면은 `CustomException`을 잡아 사용자에게 표시할 책임이 있다.
- 인증 여부 조회는 이 훅이 아니라 `auth.store`를 구독한다.

## 수정 규칙

- 토큰 저장 위치와 키 상수를 화면에서 재정의하지 않는다. `constants.ts`가 단일 출처다.
- refresh 응답의 stale 검사를 제거하지 않는다. 로그인 직후 갱신 응답이 새 세션을 덮어쓴다.
- `CustomException` 재throw 계약을 바꾸면 로그인 화면의 오류 처리가 함께 깨진다.
- 주석 처리된 서버 로그아웃을 되살리려면 실패 시에도 로컬 정리가 실행되는 `finally` 구조를 유지한다.
