# 구현 로그

## 결론

공용 `withAbortSignal`로 citizen GET/POST API와 query 훅에 signal을 연결했다. auth 전송 계층도 optional signal을 받도록 맞췄다.

## 변경

- `src/shared/api/withAbortSignal.ts` (+ test)
- citizen-participation `api/**/*.api.ts` GET/POST
- `useCitizenParticipationQueries.ts`
- `auth.api.ts`, `auth/api/client.ts`
- abort 검증을 `citizenParticipation.api.test.ts`에 추가

## 비고

mutation 훅은 타입 제약으로 signal 미연결. API 시그니처는 optional signal을 유지한다.
