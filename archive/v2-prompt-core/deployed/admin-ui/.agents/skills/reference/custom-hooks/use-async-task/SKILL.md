---
name: hook-use-async-task
description: synthoria-admin-ui의 legacy useAsyncTask 가이드. 현재 구현 파일이 없으므로 신규 사용 전 대체 자산을 다시 탐색할 때 사용.
---

# useAsyncTask Hook

## 대상

- 현재 `src/`에 useAsyncTask 구현 파일이 없다. 신규 사용 전 `src/shared/lib/hooks/`와 도메인 hooks를 다시 탐색한다.

## 언제 선택하나

- API 호출, 파일 처리, 후속 refetch 등 도메인 무관 async task를 실행하면서 화면 단위 `isLoading`이 필요할 때 사용한다.
- task 내부에서 어떤 id를 쓰는지, 어떤 API를 호출하는지, 성공 후 어떤 이벤트를 발행하는지는 호출 도메인이 결정한다.

## 사용 핵심

```ts
const { isLoading, runAsyncTask } = useAsyncTask();

await runAsyncTask(async () => {
  await requestSomething();
});
```

## 책임 경계

- 공용 hook 책임: loading on/off, async task 실행, error fallback 처리
- 호출부 책임: id guard, API 선택, Dialog, pubsub, refetch, payload 구성

## 주의

- `useAsyncTask`는 id, DTO, pubsub event, Dialog 문구를 받지 않는다.
- 성공 메시지나 refresh 이벤트가 필요하면 도메인 hook에서 `runAsyncTask`를 감싼다.
- 병렬 task count를 관리하지 않는 단순 boolean loading 모델이다.
