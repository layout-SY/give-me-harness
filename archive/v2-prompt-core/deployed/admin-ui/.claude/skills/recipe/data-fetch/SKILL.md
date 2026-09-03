---
name: recipe-data-fetch
description: synthoria-admin-ui에서 신규 API fetch 화면/모달을 조립할 때 따르는 recipe. 4계층 hook 모델(api.ts/useApi/fetch hook/modal hook/component) + ApiResult 정식 계약 + 공용 Table(useFetchAdapter) + 생성·수정 통합 모달 + 이미지 업로드 흐름을 한 번에 엮어야 할 때 사용.
---

# Data Fetch (synthoria-admin-ui)

## 언제 이 스킬을 사용하나요?

- 목록 페이지에서 fetch/pagination/filter를 추가/수정할 때
- 모달에서 조회/생성/수정 API를 연결할 때 (특히 생성+수정 통합 모달)
- 이미지 업로드 플로우에 API를 붙일 때
- `src/apis`에 새 엔드포인트를 추가할 때

---

## 선행 필독

이 recipe를 따르기 전에 반드시 다음 정책/레퍼런스를 숙지한다.

- **[policy/data-fetch-layer/SKILL.md](../../policy/data-fetch-layer/SKILL.md)** — 4계층 책임 분리 (api.ts / useApi / fetch hook / modal hook / component). 본 recipe는 이 정책의 **실행 가이드**다.
- [reference/custom-hooks/use-api/SKILL.md](../../reference/custom-hooks/use-api/SKILL.md) — `execute(apiCall, options)` 시그니처(오버로드 2종), ApiResult 반환, silent opt-in 정책
- [reference/custom-hooks/useFetchAdapter/SKILL.md](../../reference/custom-hooks/useFetchAdapter/SKILL.md) — 트리거 모델, mapRow/searchState 의존성
- [reference/custom-hooks/use-pub-sub/SKILL.md](../../reference/custom-hooks/use-pub-sub/SKILL.md) — `refresh-*` 이벤트 패턴
- [reference/components/table/SKILL.md](../../reference/components/table/SKILL.md)
- [reference/components/side-modal/SKILL.md](../../reference/components/side-modal/SKILL.md)
- [recipe/data-dto/SKILL.md](../data-dto/SKILL.md) — DTO 네이밍/구조

---

## 0) 작업 시작 전 필수 확인

1. 기존 도메인 API 재사용 가능성 확인 (`src/apis/index.ts`)
2. 목록 UI 패턴: 공용 Table + `useFetchAdapter` vs 수동 `<table>`
3. 모달 진입 방식: 대부분 `pubsub` 이벤트 기반

---

## 1) API 레이어 (`src/apis`) — Repository

### 1-1. 구조
- `src/apis/axios-instance.ts`: axios singleton + 인터셉터 (envelope 정규화, CustomException 변환)
- `src/apis/api-client.ts`: `createApiClient`로 도메인 API 작성. **메서드 반환은 `Promise<ApiResult<T>>`**
- `src/apis/common/api-result/`: `ApiResult<T>` discriminated union 타입
- 도메인 폴더: `${domain}.api.ts`, `${domain}.dto.ts`, `index.ts`

### 1-2. 작성 규칙 (신규 도메인 API)
- **반드시 `createApiClient` 사용** — `instance.get/post` 직접 호출 금지 (구형 패턴은 PR-7에서 마이그레이션 대상)
- 메서드 반환 타입을 명시: `Promise<ApiResult<T>>`. void 응답도 `Promise<ApiResult<void>>`
- DTO에 `any` 금지

### 1-3. 페이지/컴포넌트에서 호출
- `api` 직접 import 금지. `useApi().api`로 주입받음
- 정식 호출:
  ```ts
  const result = await execute(() => api.domain.method(params), { silent: false });
  if ("canceled" in result) return;
  if (!result.success) return;
  // result.data: T
  ```

---

## 2) Hook 계층 — 4계층 모델

> **상세는 [policy/data-fetch-layer/SKILL.md](../../policy/data-fetch-layer/SKILL.md) 참조.** 여기서는 실행 패턴만.

### 2-1. 계층 의사결정

새 모달/페이지 작성 시 fetch hook을 따로 만들지 판단:

| 조건 | fetch hook 분리? |
|------|-----------------|
| 도메인 액션 1개 + 상태 없음 | ❌ modal hook이 직접 `execute` 호출 |
| 액션 2+ 개 또는 엔티티 상태 필요 | ✓ fetch hook 분리 |
| 여러 액션이 공유하는 게이트(id, confirm) 있음 | ✓ fetch hook 분리 |

### 2-2. fetch hook 책임 (있을 경우)
- 도메인 액션 함수들 — 반환은 **ApiResult passthrough**: `Promise<ApiResult<T> | { canceled: true }>`
- 엔티티 상태(`fetchedData` useState)
- 도메인 게이트(`id < 0` 가드, `Dialog.confirm("정말 삭제?")`)
- **금지**: `Dialog.alert(성공)`, `pubsub.publish` 직접 호출

### 2-3. modal hook 책임
- 액션 트리거 핸들러(`handle*`)
- **성공 후 부수효과**: `Dialog.alert(성공 메시지)` + `pubsub.publish("refresh-<domain>-list")`
- 모달 close, surface-specific 흐름 (ReasonPrompt 등)
- `useDialog`/`usePubSub` import는 여기

### 2-4. 컴포넌트(.modal.tsx) 책임
- JSX
- `pubsub.subscribe("open-...")`로 모달 open 이벤트 구독
- **금지**: refetch 함수를 prop으로 받기 (pubsub 구독으로 대체)

---

## 3) 공용 테이블 fetch — `useFetchAdapter`

### 3-1. 스택
- `src/components/table/table.tsx`
- `src/components/table/hooks/useFetchAdapter.ts`
- `src/components/search-state-bar/`

### 3-2. 호출 흐름

```tsx
const { api } = useApi();

const fetchList = useCallback(
  async (params: GetListDto) => {
    const result = await api.domain.getList(params);
    if (!result.success) throw new CustomException(result.error);  // 임시 어댑팅 — PR-4+ 정리
    return result.data;
  },
  [api.domain],
);

const { rows, fetchedPagination, isLoading, refetch, totalItemCount } = useFetchAdapter({
  mapRow,
  searchState: queryState,
  fetchApi: fetchList,
});

useEffect(() => {
  const unsub = pubsub.subscribe("refresh-<domain>-list", refetch);
  return unsub;
}, [refetch]);
```

> `useFetchAdapter`가 ApiResult 계약으로 전환되기 전까지는 호출부에서 인라인 unwrap. 전환 후에는 `fetchApi`가 `Promise<ApiResult<T>>`를 그대로 받도록 변경 예정 (PR-4 이후).

---

## 4) 모달 fetch 구조 (생성/수정 통합 포함)

### 4-1. 공통 모달 상태 머신 (READ/CREATE/UPDATE)
- `MODAL_STATES.NULL | CREATE | READ | UPDATE` enum 사용
- 진입은 `pubsub` 이벤트 (`create-*`, `read-*`)
- 대표: `src/pages/manage/items/_id.modal.tsx`, `src/pages/manage/operations/faq/_id.modal.tsx`

### 4-2. 생성/수정 통합 원칙
- READ 모드에서 상세 조회 → `formState` 프리필
- UPDATE 진입 시 `initFormState` 저장 → dirty-check (`getDirtyStateSet`)
- 저장 버튼에서 모드 분기 (`CREATE → requestCreate()`, `UPDATE → requestUpdate()`)

### 4-3. 상세 모달 (액션 다수) 예시 흐름
1. `index.tsx`(목록)에서 행 클릭 → `pubsub.publish("open-<domain>-detail-modal", { id })`
2. `.modal.tsx`에서 `pubsub.subscribe("open-...", handleModalOpen)` — `handleModalOpen`은 modal hook 제공
3. modal hook이 fetch hook의 `requestGet(id)` 호출 (상세 조회 + `fetchedData` 채움)
4. 사용자 액션 → modal hook의 `handle*` → fetch hook의 `request*` → useApi → api.ts
5. fetch hook이 ApiResult passthrough 반환 → modal hook이 분기:
   - 성공: `Dialog.alert(성공)` + `pubsub.publish("refresh-<domain>-list")` + 모달 close
   - 실패: useApi의 `silent: false`가 자동 Dialog → early return

---

## 5) 이미지 업로드 fetch 구조

### 5-1. 책임 분리
- `src/components/image-manager/ImageManager.tsx`: 슬롯 UI + 검증 + 업로드 상태
- 실제 업로드 API는 `uploadApi` prop 주입 (`(formData: FormData) => Promise<string>`)

### 5-2. DTO 배열 ↔ URL 배열 브릿지
- ImageManager는 `string[]`만 다룸
- 서버가 `{ imageUrl, sortOrder }` DTO 배열을 주면 브릿지 훅으로 변환
- 예: `useDaoProposalImageBridge(dtos, onChange)` → `{ urls, onChange }`

### 5-3. 주의
- 파일 검증/에러 Dialog/로딩 상태는 ImageManager 내부 처리. 호출부에서 중복 구현 금지
- `useImageDelete`는 현재 `api.dao` 하드코딩 + delete 호출 주석 처리 상태 (서버 미반영). 추후 정리 대상

---

## 6) 새 API/Fetch 구현 절차

1. **도메인 결정**: 기존 도메인 재사용 vs 신규 도메인 폴더 생성
2. **DTO 정의**: `${domain}.dto.ts`에 요청/응답 타입. `any` 금지
3. **API 메서드 추가**: `createApiClient` 사용, 반환 `Promise<ApiResult<T>>`, void는 `Promise<ApiResult<void>>`
4. **루트 집계 반영**: `src/apis/index.ts`에 연결 확인
5. **호출부 연결** (계층 의사결정 §2-1 적용):
   - 단순: modal hook이 `execute` 직접 호출
   - 복합: fetch hook 분리 → modal hook이 결과 분기 + alert/pubsub
6. **이벤트명 상수화**: `const REFRESH_LIST_EVENT = "refresh-<domain>-list"` 같이 typo 방지
7. **검증**: `yarn lint && tsc --noEmit` + 실제 동작(성공/실패/취소) 확인

---

## 7) 빠른 템플릿

### 7-1. 도메인 API (`src/apis/services/${domain}/${domain}.api.ts`)

```ts
import { createApiClient } from "~/apis/api-client";
import type { ApiResult } from "~/apis/common/api-result";
import type { CreateSomethingDto, GetSomethingDto, SomethingDto } from "./something.dto";

const client = createApiClient();
const RESOURCE = "/v1/something";

export const somethingApi = {
  getList: (params: GetSomethingDto): Promise<ApiResult<SomethingDto[]>> =>
    client.get<SomethingDto[]>(RESOURCE, { params }),

  create: (payload: CreateSomethingDto): Promise<ApiResult<void>> =>
    client.post<void>(RESOURCE, payload),

  delete: (id: number): Promise<ApiResult<void>> =>
    client.delete<void>(`${RESOURCE}/${id}`),
};
```

### 7-2. fetch hook (도메인 액션 다수)

```ts
type ActionResult = ApiResult<void> | { canceled: true };

export const useSomethingDetailFetch = () => {
  const { api, execute, isLoading } = useApi();
  const Dialog = useDialog();
  const [fetchedData, setFetchedData] = useState<SomethingDto>(_initState);

  const fetchDetail = useCallback(
    async (id: number): Promise<boolean> => {
      const result = await execute(() => api.something.getDetail(id), { silent: false });
      if ("canceled" in result) return false;
      if (!result.success) return false;
      setFetchedData(result.data);
      return true;
    },
    [api.something, execute],
  );

  const requestDelete = useCallback(async (): Promise<ActionResult> => {
    const id = fetchedData.id;
    if (id < 0) return { canceled: true };
    const yes = await Dialog.confirm({ content: <p>{"삭제하시겠습니까?"}</p> });
    if (!yes) return { canceled: true };
    return execute(() => api.something.delete(id), { silent: false });
  }, [Dialog, api.something, execute, fetchedData.id]);

  // ... 추가 액션도 같은 패턴

  return { fetchedData, isLoading, fetchDetail, requestDelete };
};
```

### 7-3. modal hook (surface 흐름)

```ts
const REFRESH_LIST_EVENT = "refresh-something-list";

export const useSomethingDetailModal = () => {
  const { isOpen, handleOpen, handleClose } = useModal();
  const { fetchedData, isLoading, fetchDetail, requestDelete } = useSomethingDetailFetch();
  const { pubsub } = usePubSub();
  const Dialog = useDialog();

  const handleModalOpen = useCallback(
    ({ id }: { id: number }) => {
      handleOpen();
      fetchDetail(id);
    },
    [fetchDetail, handleOpen],
  );

  const handleDelete = useCallback(async () => {
    const result = await requestDelete();
    if ("canceled" in result || !result.success) return;
    Dialog.alert({ content: <p>{"삭제되었습니다."}</p> });
    pubsub.publish(REFRESH_LIST_EVENT);
    handleClose();
  }, [Dialog, handleClose, pubsub, requestDelete]);

  return { isOpen, isLoading, fetchedData, handleModalOpen, handleClose, handleDelete };
};
```

### 7-4. 컴포넌트

```tsx
export const SomethingDetailModal = () => {
  const { pubsub } = usePubSub();
  const { isOpen, isLoading, fetchedData, handleModalOpen, handleClose, handleDelete } =
    useSomethingDetailModal();

  useEffect(() => {
    const unsub = pubsub.subscribe("open-something-detail-modal", handleModalOpen);
    return unsub;
  }, [handleModalOpen, pubsub]);

  return (
    <SideModal open={isOpen} close={handleClose}>
      {isLoading && <Loading />}
      {/* ... */}
    </SideModal>
  );
};
```

---

## 8) 구현 시 주의사항

- `useApi.execute`의 반환은 항상 `ApiResult<T> | { canceled: true }`. throw catch에 의존하지 말 것
- 실패 자동 Dialog는 `silent: false` 명시 opt-in (기본은 안 띄움)
- `useFetchAdapter`는 search state 변경만으로는 재요청 안 함 — 트리거 플래그 사용
- 공용 hook(`useDialog`, `usePubSub`)을 useCallback dep로 받는 경우, 해당 hook 반환이 안정적이어야 함 (불안정하면 useApi `execute` identity 흔들려 무한 fetch 가능)
- pubsub 이벤트명은 상수 추출 — typo 방지
- 변경 후 `yarn lint && tsc --noEmit` + 실제 동작(성공/실패/취소) 검증
