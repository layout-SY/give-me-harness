---
name: hook-use-pub-sub
description: synthoria-admin-ui의 usePubSub 훅(src/hooks/use-pub-sub) 사용 가이드. 모달 열기/닫기, 목록 리프레시, 도메인 액션 트리거 등 컴포넌트 간 직접 의존 없이 이벤트로 연동할 때 사용.
---

# usePubSub Hook (synthoria-admin-ui)

## 언제 이 스킬을 사용하나요?

- 페이지 ↔ 모달, 위젯 ↔ 사이드 모달처럼 **부모-자식 관계가 아닌 컴포넌트 간** 액션을 전달할 때
- 목록 페이지에서 모달 작업 후 데이터를 갱신해야 할 때 (`refresh-*` 패턴)
- 공용 팝업(`open-image-upload-popup`, `open-calendar-picker`, `open-image-uploader-modal` 등)을 호출할 때
- 신규 도메인 모달 흐름을 설계할 때 (이벤트 이름·페이로드 타입을 먼저 정의)

## 0) 작업 시작 전 필수 확인

1. 동일한 동작이 가능한 기존 이벤트가 `PubSubEvents`에 이미 있는지 확인한다.
2. 진짜로 전역 통신이 필요한지 검토한다 — 부모-자식 직접 props 전달이 가능하면 우선 사용한다.
3. 페이로드 형태와 응답 형태(callback이 필요한지)를 먼저 결정한다.

---

## 1) 모듈 구조

- `src/hooks/use-pub-sub/index.ts`
  - 제네릭 `PubSub<TEvents>` 클래스 + 싱글톤 인스턴스
  - 훅 진입점 `usePubSub()` → `{ pubsub: { subscribe, publish } }`
- `src/hooks/use-pub-sub/events.ts`
  - 전체 이벤트 카탈로그(`PubSubEvents` 타입)
  - **이벤트 추가/수정 시 반드시 이 파일을 함께 변경**

### 1-1. 핵심 동작

- `subscribe(event, callback)` 은 unsubscribe 함수를 반환한다 → `useEffect` cleanup에 반드시 등록한다.
- `publish(event, payload?)` — 페이로드가 `undefined` 타입이면 두 번째 인자 생략 가능.
- 리스너 컬렉션은 `Set` 기반이므로 동일 콜백 중복 등록은 1회로 합쳐진다.
- 인스턴스가 싱글톤이라 모든 컴포넌트가 같은 채널을 공유한다.

---

## 2) 이벤트 카탈로그 (대표)

`src/hooks/use-pub-sub/events.ts`의 `PubSubEvents`가 단일 진실 소스다. 카테고리별 대표 이벤트는 다음과 같다.

### 2-1. 공용 팝업/모달 제어

- `close-modal`
- `open-image` / `open-calendar-picker` / `close-calendar-picker`
- `open-image-upload-popup` / `close-image-upload-popup`
- `open-image-uploader-modal` / `close-image-uploader-modal`
- `open-send-parcel-popup` / `close-send-parcel-popup`
- `open-select-items-popup` / `open-select-users-popup`

### 2-2. 도메인 CRUD 진입 + 리프레시

도메인별로 `create-*`, `read-*`, `refresh-*` 트리오 패턴을 따른다.

- 사용자: `read-user`, `update-user-currency`, `suspend-user`, `restore-user`, `refresh-users`
- 아이템: `create-item`, `read-item`, `refresh-items`, `create-item-category`, `update-item-category`, `refresh-item-categories`
- 콘텐츠: `create-video`, `read-video`, `refresh-videos`, `create-video-playlist`, `read-video-playlist`, `select-video-playlist-video`, `refresh-video-playlist`, `create-news`, `read-news`, `refresh-news`
- 이벤트: `read-attendance-event`, `create-attendance-event`, `refresh-event-attendance`, `read-roulette-event`, `create-roulette-event`, `refresh-event-roulette`
- 운영: `create-faq`, `read-faq`, `refresh-faqs`, `read-inquiry`, `refresh-inquiries`
- 이커머스: `read-ecommerce-product`, `refresh-ecommerce-products`
- 어드민: `create-admin`, `read-admin`, `refresh-admins`
- DAO: `open-proposal-detail-modal`, `open-create-proposal-modal`, `refresh-dao-proposals`, `open-author-history-modal`, `open-discussion-post-detail-modal`, `open-discussion-comment-detail-modal`, `refresh-dao-proposals-discussion-posts-list`, `refresh-dao-proposals-discussion-posts`, `open-dao-pass-create-id-modal`, `refresh-dao-pass-management`, `open-proposal-audit-detail-modal`, `refresh-dao-proposals-review-list`
- 통계: `open-user-statistics-top-ten-modal`
- 활동 설정: `open-activity-settings`, `update-activity-settings`

> 누락이 있다면 항상 `events.ts`를 직접 확인한다.

---

## 3) 사용 패턴

### 3-1. 목록 페이지 — 모달 열기 + 리프레시 구독

```tsx
const { pubsub } = usePubSub();
const { setRequestSearch } = useFetchAdapter({ /* ... */ });

useEffect(() => {
  const unsubscribe = pubsub.subscribe("refresh-users", () => setRequestSearch(true));
  return () => unsubscribe();
}, []);

const handleOpenModal = (userId: number) => {
  pubsub.publish("read-user", userId);
};
```

### 3-2. 모달 — 진입 이벤트 구독

```tsx
useEffect(() => {
  const offRead = pubsub.subscribe("read-item", (itemId) => {
    setMode(MODAL_STATES.READ);
    setSelectedId(itemId);
  });
  const offCreate = pubsub.subscribe("create-item", () => {
    setMode(MODAL_STATES.CREATE);
  });
  return () => {
    offRead();
    offCreate();
  };
}, []);
```

### 3-3. 콜백을 페이로드에 포함하는 패턴

`callback: Function` 페이로드는 모달이 작업 완료 후 호출자에게 결과를 전달하는 용도다.

```ts
pubsub.publish("update-user-currency", {
  userId,
  currencyType: CURRENCY_TYPES.SORIA,
  callback: () => setRequestSearch(true),
});
```

### 3-4. 작업 완료 후 리프레시 트리거

모달의 저장 핸들러 마지막에서 `refresh-*` 이벤트를 발행한다.

```ts
const requestUpdate = async () => {
  await execute(() => api.users.updateUser(...));
  pubsub.publish("refresh-users");
  pubsub.publish("close-modal");
};
```

---

## 4) 신규 이벤트 추가 절차

1. **이름 규칙 확인**
   - 모달 진입: `open-*`, `read-*`, `create-*`
   - 데이터 갱신: `refresh-<리소스>`
   - 닫기: `close-*`
2. **`events.ts`에 타입 추가**
   - 페이로드 없음: `"event-name": undefined;`
   - 페이로드 있음: `"event-name": { foo: string; callback?: Function };`
3. **publisher/subscriber 구현**
   - publisher 측에서 트리거
   - subscriber는 `useEffect` cleanup에서 unsubscribe 보장
4. **연관 화면 갱신**
   - 같은 도메인의 `refresh-*` 이벤트가 이미 있다면 신규 이벤트 대신 재사용한다.

---

## 5) 구현 시 주의사항

- **타입 등록 누락 금지**: `events.ts`에 없는 이벤트는 컴파일 자체가 막혀야 한다. 임의 캐스팅으로 우회하지 않는다.
- **cleanup 누락 금지**: subscribe 후 unsubscribe를 빼면 모달 재오픈 시 핸들러가 누적된다.
- **publish 시점**: 비동기 흐름에서는 await 이후에 publish한다 (저장 완료 전 리프레시 금지).
- **callback 페이로드 의존**: `Function` 타입은 약하다. 새 이벤트는 가능하면 명확한 시그니처(`(payload: X) => void`)로 정의한다.
- **싱글톤 공유**: 페이지 전환 후에도 잔존 가능. 페이지 unmount 시점에 cleanup이 필요한 이벤트는 빠짐없이 정리한다.
- **자식-부모만의 통신은 props로**: 가까운 트리에서는 props/콜백이 더 명확하다. PubSub은 트리를 가로지를 때만 쓴다.
- 도메인 액션(`suspend-user`, `restore-user`, `update-user-currency` 등)은 페이로드 안에 callback을 받도록 설계되어 있다. 결과 후 화면 갱신은 callback에서 처리한다.

---

## 6) 빠른 템플릿

### 6-1. 이벤트 타입 추가 (`events.ts`)

```ts
export type PubSubEvents = {
  // 기존 이벤트들...

  "open-foo-modal": { fooId: number };
  "refresh-foos": undefined;
};
```

### 6-2. 목록 페이지 사이드

```tsx
const { pubsub } = usePubSub();

useEffect(() => {
  const off = pubsub.subscribe("refresh-foos", () => setRequestSearch(true));
  return () => off();
}, []);

const openFooModal = (fooId: number) => pubsub.publish("open-foo-modal", { fooId });
```

### 6-3. 모달 사이드

```tsx
useEffect(() => {
  const off = pubsub.subscribe("open-foo-modal", ({ fooId }) => {
    setSelectedId(fooId);
    setMode(MODAL_STATES.READ);
  });
  return () => off();
}, []);

const requestUpdate = async () => {
  await execute(() => api.foo.updateFoo(...));
  pubsub.publish("refresh-foos");
  pubsub.publish("close-modal");
};
```
