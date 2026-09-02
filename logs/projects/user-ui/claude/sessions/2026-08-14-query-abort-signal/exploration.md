# 탐색

## 결론

Query 언마운트 시 RQ는 `queryFn`에 `signal`을 abort하지만, API가 axios config에 넣지 않아 HTTP가 계속 살아 있었다.

## 관찰

- 프로젝트의 `useQuery`는 citizen-participation에만 존재한다.
- `ApiClient`/`axios`는 이미 `signal`을 받을 수 있다.
- meeting 도메인은 별도 `AbortSignal` 패턴이 이미 있다.
- 현재 RQ 타입의 mutation context에는 `signal`이 없다.
