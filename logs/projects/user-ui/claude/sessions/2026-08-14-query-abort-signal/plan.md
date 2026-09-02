# 계획

## 목표

라우트 이탈·queryKey 변경 시 TanStack Query가 in-flight HTTP를 실제로 취소하도록 AbortSignal을 전송 계층까지 연결한다.

## 범위

- `src/shared/api/withAbortSignal.ts`
- citizen-participation GET/POST API의 optional `AbortSignal`
- `useCitizenParticipationQueries`의 `queryFn({ signal })`
- auth `postAuthSignIn`/`authClient` optional signal (mutation context에는 signal 타입 없음)

## 제외 사항

- mutationFn signal 연결 (현재 `@tanstack/react-query`의 `MutationFunctionContext`에 `signal` 없음)
- 로딩 UI 게이트·타임아웃 정책 변경
- MSW handlers Invalid URL 기존 실패

## 검증

- `npm run build`
- `npm run lint`
- abort/withAbortSignal/auth 관련 vitest

## 승인

- 상태: approved (`전체 도메인에 적용해봐`)
