# 최종 요약

라우트 이동 시 in-flight fetch가 안 끊기던 이유는 TanStack Query의 `AbortSignal`이 axios까지 전달되지 않았기 때문이다.

## 적용

- 공용 `withAbortSignal`
- citizen-participation 전체 GET/POST API + query 훅
- auth 전송 계층 optional signal

## 검증

- build/lint 통과
- abort 관련 테스트 7개 통과

## 제한

- 현재 RQ mutation context에 `signal`이 없어 mutation 훅은 미연결
- 기존 MSW handlers Invalid URL 실패는 범위 밖
