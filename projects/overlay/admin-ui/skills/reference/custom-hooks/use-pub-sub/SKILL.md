---
name: hook-use-pub-sub
description: {{PROJECT_NAME}}의 usePubSub 훅(src/shared/lib/pub-sub) 사용 및 수정 가이드. 전역 싱글턴 이벤트 발행·구독과 타입 계약을 다룰 때 사용.
---

# usePubSub

## 대상

- `src/shared/lib/pub-sub/index.ts`
- `src/shared/lib/pub-sub/events.ts` (`PubSubEvents` 이벤트 타입 맵)

## 계약

```ts
const { pubsub } = usePubSub();
pubsub.subscribe(event, callback); // 해제 함수를 반환한다
pubsub.publish(event, payload);
```

- 모듈 수준 **싱글턴**이다. 훅은 `useMemo`로 고정된 동일 객체를 돌려준다. Provider가 없고 컴포넌트 트리와 무관하다.
- 이벤트 이름과 payload 타입은 `PubSubEvents`가 정의한다. 새 이벤트는 이 타입에 먼저 추가한다.
- payload가 `undefined`인 이벤트는 `publish(event)`로 인자 없이 호출한다. 타입이 이를 강제한다.
- `subscribe`는 해제 함수를 반환한다. 리스너는 `Set`이라 같은 콜백을 중복 등록해도 하나만 유지된다.

현재 이 채널로 열리는 전역 UI가 있다.

- `open-image` → `image-modal`
- `open-image-upload-popup`, `close-image-upload-popup` → `image-upload`

## 사용 기준

- 부모·자식 관계가 아닌 원거리 컴포넌트 사이의 일회성 신호에 사용한다.
- 지속 상태는 pub-sub이 아니라 store를 사용한다. 이 구현은 마지막 값을 보관하지 않으므로 **구독 이전에 발행된 이벤트는 받을 수 없다.**
- 구독은 `useEffect`에서 등록하고 반환된 해제 함수를 정리 함수에서 호출한다.
- 전역 UI를 열 때는 컴포넌트를 직접 렌더링하지 말고 정의된 이벤트를 발행한다.

## 수정 규칙

- 싱글턴과 `stableHookReturn` 고정 참조를 유지한다. 매 렌더 새 객체를 반환하면 구독 `useEffect`가 반복 실행된다.
- `subscribe`/`publish`의 `bind`를 제거하지 않는다. 구조 분해 시 `this`가 사라진다.
- 이벤트 이름을 바꾸면 발행·구독 양쪽을 함께 고친다. 문자열 계약이라 컴파일러가 일부만 잡는다.
- 값 보관·재생 기능을 추가하는 변경은 사용자 승인을 받는다.
