---
name: hook-use-auth
description: synthoria-admin-ui의 useAuth 훅(src/hooks/use-auth.ts) 사용 가이드. 로그인/토큰 리프레시/로그아웃 흐름과 jotai 사용자·인증 상태 동기화가 필요할 때 사용.
---

# useAuth Hook

## 대상

- `src/hooks/use-auth.ts`
- 연관 atom: `src/atoms/auth.atom.ts`, `src/atoms/user.atom.ts`
- 토큰 키: `LOCAL_STORAGE_ACCESS_TOKEN_KEY`, `LOCAL_STORAGE_REFRESH_TOKEN_KEY` (`src/assets/constants`)

## 언제 선택하나

- 로그인 페이지에서 자격증명 제출 (`getAuthentication`)
- 앱 부트스트랩에서 세션 복구 (`refreshAuthentication`)
- 헤더/설정 메뉴에서 로그아웃 (`rmAuthentication`)

## 사용 핵심

- 반환값: `{ getAuthentication, refreshAuthentication, rmAuthentication }`
- 내부적으로 `useApi().execute`를 사용하므로 로딩/에러 Dialog 규약을 따른다.
- 성공 시 access/refresh 토큰을 localStorage에 저장하고 `userAtom`, `authAtom`을 갱신한다.

## 호출 예시

```ts
// 로그인
const { getAuthentication } = useAuth();
await getAuthentication(loginId, password);

// 앱 시작 시 세션 복구
const { refreshAuthentication } = useAuth();
await refreshAuthentication();

// 로그아웃
const { rmAuthentication } = useAuth();
await rmAuthentication();
```

## 주의

- `getAuthentication`의 기본 에러 경로는 `CustomException`이면 재-throw, 일반 `Error`면 `alert(err.message)`이다. 호출부에서 에러 UX를 재정의할 경우 `use-auth.ts` 자체를 수정하지 말고 상위에서 try/catch 한다.
- `refreshAuthentication`은 `silent: true`로 동작한다. 리프레시 실패는 사용자에게 노출되지 않는다.
- 리프레시 응답이 도착한 시점에 localStorage 토큰이 이미 다른 로그인으로 교체됐다면 결과를 무시한다 (stale response guard). 이 로직을 우회하지 않는다.
- `rmAuthentication`의 서버 로그아웃 호출은 주석 처리되어 있다. 서버 세션 무효화가 필요해지면 이 훅을 업데이트한다 (페이지에서 별도 처리 금지).
- access/refresh 토큰은 반드시 이 훅을 통해서만 저장/제거한다. 다른 위치에서 `localStorage.setItem(LOCAL_STORAGE_*_KEY, ...)`를 직접 호출하지 않는다.
