---
name: policy-data-fetch-layer
description: synthoria-admin-ui에서 데이터 페치/도메인 액션 코드를 작성/리팩터할 때 따르는 4계층 책임 분리 정책. 페이지·모달에 API 요청과 후처리(상태/UI/이벤트)가 섞일 때 어느 계층이 무엇을 책임지는지 판단해야 할 때 사용.
---

# Data Fetch Layer Architecture (Policy)

## 언제 이 스킬을 사용하나요?

- 새 페이지/모달에 API 요청을 결합할 때
- 기능 hook과 surface hook 사이 경계가 모호하다고 느낄 때
- "이 alert/pubsub/상태가 어디에 있어야 하는가" 판단이 필요할 때
- 리팩터 중 hook이 비대해지거나 surface 컴포넌트가 도메인 로직을 직접 갖고 있을 때

---

## 1) 4계층 모델 (필수 숙지)

```
┌──────────────────────────────────────────────────────────────┐
│  .modal.tsx / page.tsx  (UI 진입점)                          │
│    - JSX 렌더링                                              │
│    - 모달 open 이벤트 subscribe                              │
└──────────────────────────────────────────────────────────────┘
                          ↑ (hook 사용)
┌──────────────────────────────────────────────────────────────┐
│  use<Domain>Modal  (Surface 흐름 = Application Service)      │
│    - 액션 트리거(handle*)                                    │
│    - 성공 후 부수효과(Dialog.alert, pubsub.publish)          │
│    - 모달 close, refetch 등 UI 오케스트레이션                │
│    - ReasonPrompt 같은 surface-specific 흐름                 │
└──────────────────────────────────────────────────────────────┘
                          ↑
┌──────────────────────────────────────────────────────────────┐
│  use<Domain>Fetch  (도메인 facade = Stateful Service)        │
│    - 도메인 액션 함수들 (request*, fetch*)                   │
│    - 엔티티 상태(useState) 소유                              │
│    - 도메인 게이트(`id < 0` 가드, confirm dialog)            │
│    - 반환은 ApiResult passthrough (boolean으로 압축 금지)    │
│    - 향후 TQ 도입 시 invalidateQueries 위치                  │
└──────────────────────────────────────────────────────────────┘
                          ↑ (execute 사용)
┌──────────────────────────────────────────────────────────────┐
│  useApi  (요청 단위 라이프사이클 + 결과 어댑터)              │
│    - 모든 결과(success/failure/canceled)를 값으로 노출       │
│    - isLoading, race 가드(seqRef), unmount cleanup           │
│    - silent opt-in (실패 Dialog는 silent:false 명시 시만)    │
└──────────────────────────────────────────────────────────────┘
                          ↑
┌──────────────────────────────────────────────────────────────┐
│  api.ts  (Repository)                                        │
│    - 통신 + envelope 정규화                                  │
│    - 반환: Promise<ApiResult<T>>                             │
└──────────────────────────────────────────────────────────────┘
```

---

## 2) 계층별 책임 표

| 항목 | api.ts | useApi | fetch hook | modal hook | .modal.tsx |
|------|--------|--------|------------|------------|-----------|
| HTTP 호출 / envelope 정규화 | ✓ | | | | |
| 성공/실패/취소를 값으로 어댑팅 | | ✓ | | | |
| isLoading / race / cancel | | ✓ | | | |
| 실패 시 자동 Dialog (silent:false) | | ✓ | | | |
| 엔티티 상태 (`fetchedData`) | | | ✓ | | |
| 도메인 게이트 (id 가드, confirm) | | | ✓ | | |
| 도메인 액션 함수 정의 | | | ✓ | | |
| **성공 시 Dialog.alert** | | | | ✓ | |
| **성공 시 pubsub.publish** | | | | ✓ | |
| 모달 close / refetch 트리거 | | | | ✓ | |
| ReasonPrompt 등 surface 흐름 | | | | ✓ | |
| JSX / 모달 open subscribe | | | | | ✓ |

---

## 3) 핵심 원칙

### 3-1. 성공 부수효과는 surface(modal hook)에, 실패 표현은 useApi에
- 성공 시 토스트/refresh 이벤트는 surface마다 다를 수 있다 → modal hook 책임
- 실패 dialog는 모든 호출에서 동일 정책으로 → useApi가 `silent: false` opt-in으로 처리
- fetch hook은 **성공해도 Dialog.alert이나 pubsub.publish를 직접 하지 않는다**

### 3-2. fetch hook은 결과를 압축하지 않는다
- `Promise<boolean>` 반환 금지. `Promise<ApiResult<T> | { canceled: true }>` passthrough가 정답
- modal hook이 `if ("canceled" in r) return; if (!r.success) return;` 로 분기
- 압축하면 modal이 "왜 실패했는지" 알 수 없음 → 분기 표현력 손실

### 3-3. fetch hook 존재 정당화 3요소
fetch hook이 의미 있으려면 다음 중 **2개 이상**이 있어야 한다:
1. 엔티티 상태(`fetchedData` 같은 useState) 소유
2. 여러 액션이 공유하는 도메인 게이트 (id 가드 등)
3. 요청 전 도메인 dialog (`Dialog.confirm("정말 삭제?")` 같은 게이트)

이 조건을 못 채우면 fetch hook 만들지 말고 **modal hook이 직접 `useApi.execute`를 호출**한다.

### 3-4. 외부 결합도 최소화 — pubsub 우선
- 부모→자식 prop으로 refetch 함수를 내리는 대신 `pubsub.publish("refresh-<domain>-<scope>-list")` 를 사용
- 부모는 `pubsub.subscribe(...)`로 구독
- 이벤트명은 상수로 추출(`const REFRESH_LIST_EVENT = "..."`)해 typo 방지

### 3-5. useApi 반환은 신뢰
- 호출부는 항상 `ApiResult` discriminated union을 받음
- `result.success` 분기로 흐름 결정. throw에 의존하지 않음
- `onSuccess`/`onError` 콜백은 **선택적 부가물**. 정식 흐름은 반환값

---

## 4) 안티패턴

### 4-1. fetch hook이 alert/pubsub을 직접 수행
```ts
// ❌ 잘못된 예
const requestDelete = async () => {
  const result = await execute(...);
  if (!result.success) return false;
  Dialog.alert({ content: "..." });       // ← surface 책임 침범
  pubsub.publish("refresh-list");          // ← surface 책임 침범
  return true;
};
```

```ts
// ✓ 올바른 예
const requestDelete = async (): Promise<ApiResult<void> | { canceled: true }> => {
  if (id < 0) return { canceled: true };
  return execute(() => api.x.delete(id), { silent: false });
};
// modal hook에서 분기 + alert/pubsub
```

### 4-2. modal에 refetch 함수 prop 전달
```tsx
// ❌
<DetailModal refetch={refetch} />

// ✓ pubsub 구독
useEffect(() => {
  const unsub = pubsub.subscribe("refresh-x-list", refetch);
  return unsub;
}, [refetch]);
return <DetailModal />;
```

### 4-3. fetch hook이 boolean 반환
```ts
// ❌
const requestDelete = async (): Promise<boolean> => { ... };

// ✓ ApiResult passthrough
const requestDelete = async (): Promise<ApiResult<void> | { canceled: true }> => { ... };
```

### 4-4. surface 컴포넌트가 직접 api.x 호출
```tsx
// ❌ — api.ts가 useApi를 우회하면 race/loading/dialog 모두 잃음
const handleClick = async () => {
  const result = await api.x.delete(id);
  ...
};

// ✓ useApi.execute 경유
const { execute } = useApi();
const handleClick = async () => {
  const result = await execute(() => api.x.delete(id), { silent: false });
  ...
};
```

### 4-5. useDialog 같은 hook을 useCallback dep로 쓰는데 unstable
- 공용 hook(`useDialog`, `usePubSub`)의 반환 객체/메서드가 매 렌더 새 identity면 useCallback 체인 전체가 흔들림
- 본 프로젝트에서 발생했던 사례: `useDialog`가 매 렌더 새 객체 반환 → useApi의 `execute` identity 변경 → useFetchAdapter 무한 fetch
- 공용 hook은 반드시 `useCallback`/`useMemo`로 안정화

---

## 5) 의사결정 체크리스트 (작업 직전 점검)

새 페이지/모달 작성 시:

- [ ] 도메인 액션이 2개 이상이거나 엔티티 상태가 필요한가?
  - Yes → fetch hook 작성
  - No → modal hook에서 `useApi.execute` 직접 호출
- [ ] 성공 시 alert/pubsub은 modal hook에 두었는가?
- [ ] 실패 표현이 필요한 호출에 `silent: false` 명시했는가?
- [ ] fetch hook 반환 타입이 `ApiResult<T> | { canceled: true }` passthrough인가?
- [ ] 부모 ↔ 모달 결합이 prop 대신 pubsub으로 끊겼는가?
- [ ] 이벤트명은 상수로 추출했는가?

---

## 6) 금지

- fetch hook에 `Dialog.alert(성공 메시지)` 또는 `pubsub.publish` 직접 호출
- fetch hook의 액션 반환을 `Promise<boolean>` 등으로 압축
- modal/surface에서 `api.x.method()`를 useApi 우회로 직접 호출
- modal에 `refetch: () => void` prop 전달 (pubsub로 대체)
- 공용 hook을 unstable한 채로 두기 (반환 객체/메서드는 useCallback/useMemo 필수)

---

## 7) 관련 문서

- [reference/custom-hooks/use-api/SKILL.md](../../reference/custom-hooks/use-api/SKILL.md) — useApi 계약 상세
- [recipe/data-fetch/SKILL.md](../../recipe/data-fetch/SKILL.md) — fetch 조립 절차
- [policy/hook-extraction/SKILL.md](../hook-extraction/SKILL.md) — form/modal 3-layer 분리 (별개 축, 본 정책과 보완 관계)
- [.claude/logs/sessions/2026-05-21-api-result-contract/](../../../../logs/sessions/2026-05-21-api-result-contract/) — 본 정책 도출 배경 (ApiResult 계약 승격 작업 기록)
- 후속 추상화 follow-up: `followup-success-side-effect-pattern.md` — alert/pubsub 패턴 추상화 (deferred)
