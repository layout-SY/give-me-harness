# payload / searchState 공용 hook 분리 방향성 검토

- 일자: 2026-05-08
- 형식: 질의응답
- 평가 위임: `evaluator` 에이전트
- 대상 도메인 예시: `src/pages/dao/proposal-manage/`
- 선행 토론
  - `.codex/logs/discussions/2026-05-07-architecture-qna.md` (주제 3, 7~10 — 추상화 4조건 / closed vocabulary 누수 / 신(神) 추상화 시그널)
  - `.codex/logs/discussions/2026-05-07-2-payload-searchstate-generalization.md`

---

## 1. 사용자 질문 요지

테이블 페이지의 `searchState`(요청 쿼리)와 모달의 `payload`(요청 body)에 대해 일관성을 유지시키는 **공용 hook**을 도입하는 것이 적절한가.

배경:
- 테이블 페이지: `searchState`는 `useFetchAdapter` 공용 hook에 그대로 들어감. hook으로 분리하려는 목적은 `SearchStateBar` props 양 축소 + 페이지에서 쿼리 도메인 state 제거.
- 모달: 생성/수정 기능이 한 컴포넌트에 hook 분리 없이 혼재. UI 재사용성은 지켜지지만 코드 복잡도가 매우 높음. 도메인 전용 hook으로 빼기엔 도메인 간 구조가 동일(검증 → 객체 묶기 → body 주입의 반복).

질문:
1. 이 방향성이 적절한가
2. 별도 hook 분리가 효율적인가, 불필요한 분리로 복잡도만 올라가는가
3. 분리가 옳다면 근거는 무엇이고 더 나은 방향성은 있는가

---

## 2. 결론 (한 줄)

- **searchState 트랙**: "공용 hook" 만들지 말 것. **도메인 전용 hook**으로 분리하는 것이 정답.
- **payload/모달 트랙**: 단일 공용 hook 금지. **3-layer 분리(순수 빌더 + 도메인 form hook + 작은 횡단 마이크로 hook)** 가 정답.
- 사용자 방향성은 절반은 맞고 절반은 위험. 특히 "도메인 모달 전체를 감싸는 공용 hook" 발상은 closed vocabulary 누수 / 신(神) 추상화 함정에 그대로 빠짐.

---

## 3. 평가 (질문별)

### 3-1. 방향성 적절성

**searchState (테이블 페이지) — 적절. 단 "공용"이 아니라 "도메인 전용".**
- `useFetchAdapter`(`src/components/table/hooks/useFetchAdapter.ts`)가 이미 `<TQuery, TItem, TRow>` 제네릭의 강한 공용 추상. 그 위에 또 한 겹의 공용 searchState hook을 얹으면 두 공용 추상이 같은 쿼리 객체를 들고 다툼.
- `proposal-manage/index.tsx`의 페이지 책임은 사실상 ① `_initFetchFilters` 정의, ② `_searchStatusItems / _searchSortItems / _searchByItems` 같은 i18n+enum 결합 메뉴 정의, ③ `setSearchState` 핸들러 — 이 셋. ②는 도메인 의존이라 공용으로 빼봐야 호출자에서 다시 작성해야 함.
- 진짜로 페이지를 무겁게 만드는 부분은 `searchState` 자체가 아니라 **드롭다운 메뉴 메모이제이션 + setSearchState 핸들러**. → 페이지 옆 `useDaoProposalSearchState()` 같은 도메인 전용 hook이 정답.
- 추상화 4조건 충족 0개 → 강한 공용 추상 비용 정당화 안 됨.

**payload/모달 — 부분적으로 부적절. "공용 hook"으로 묶지 말 것.**
- `pass-management/create/_id.modal.tsx`: 8개 number 필드, 필드별 number 캐스팅 onChange.
- `admin-settings/admins/_id.modal.tsx`: `Partial<GetAdminResponseDto> & { password, passwordConfirm }`, dirty 비교가 본질.
- `manage/operations/news/_id.tsx`: `translations: Record<LANGUAGES, ...>` nested 구조가 본질.
- 셋의 공통점은 "초기값 + setState + dirty + 검증" 정도이고, 차이점은 **타입·캐스팅·중첩 구조·검증 규칙**. 공통점은 작고 차이가 다양 → 단일 공용 contract로 흡수하면 generic 폭발 또는 `any` 회귀(closed vocabulary 누수).

### 3-2. 분리의 효율성

| 트랙 | 평가 | 비고 |
|---|---|---|
| searchState | 도메인 hook은 효율적 | `SearchStateBar` props 13개 → spread 1개로 축소, 페이지에서 쿼리 책임 제거 |
| payload (단일 공용 hook) | 비효율(복잡도↑) | generic 폭발 / 새 도메인 추가 시 breaking change 리스크 |
| payload (작은 횡단 + 도메인 form hook) | 효율적 | 표면 작고 변경 영향이 도메인 한 폴더에 한정 |

### 3-3. 권고 형태

#### searchState — 도메인 전용 hook + (선택) 작은 횡단 유틸

```ts
function useDaoProposalSearchState(): {
  searchState: GetDaoProposalsQueryDto;
  patch: (p: Partial<GetDaoProposalsQueryDto>) => void;
  reset: () => void;
  bar: Pick<SearchStateBarProps, "tabs"|"keyword"|"searchByItems"|"searchByIndex"|"onTabChange"|"onChangeKeyword"|"onClearKeyword"|"onSearchByChange">;
  sort: { sortItems; currentSort; onSortChange; onReset };
};
```

- `bar`/`sort` 묶음을 spread로 넘겨 `SearchStateBar`/`TableSortFilter` props 폭발 해소.
- `setRequestSearch`(fetch 트리거)는 hook에 넣지 않음. 페이지가 보유 → `useFetchAdapter`까지 hook이 알아야 하는 결합 폭증 회피.

작은 횡단 유틸은 **상태성 + 부수효과**가 본질일 때만(예: URL ↔ state 양방향 동기화 `useSearchStateUrlSync`). 단순 객체 구성에는 hook 금물.

#### payload — 3-layer 분리, 한 덩어리 공용 hook 금지

| Layer | 역할 | 형태 | 위치 |
|---|---|---|---|
| L1. 빌더 | 도메인 form → API payload 변환 | 순수 함수 `buildCreateXPayload(form)` | 도메인 `model.ts` |
| L2. 검증 | 필드/객체 단위 validation | 순수 함수 또는 zod 스키마 | 도메인 |
| L3. 상태 hook | initialState, setState, dirty, submit 게이팅 | 도메인 전용 form hook `useXForm()` | 도메인 |

추가로 **공용 횡단은 "한 덩어리"가 아닌 "작은 조각"**:
- `useDirtyState(initial, current)` — 이미 utils에 `getDirtyStateSet` 있음.
- `useDiscardConfirm(dirty)` — 닫기 시 confirm 다이얼로그 패턴.
- `useFormState<T>(initial)` — 옅은 wrapper. ROI 미미해 굳이 안 만들어도 됨.

#### 생성/수정 hook 합치기 vs 분리

**기본 분리. 단, "두 hook"이 아니라 "두 빌더 함수 + 하나의 도메인 form hook(mode 분기)"**:

```ts
type Mode = { kind: "create" } | { kind: "update"; id: number; initial: ReadDto };

function useNftPassForm(mode: Mode) {
  const submit = async (form: FormState) => {
    if (mode.kind === "create") return api.createNftPass(buildCreatePayload(form));
    return api.updateNftPass(mode.id, buildUpdatePayload(form, mode.initial));
  };
}
```

판단 기준:
- 같은 form shape → mode 분기 hook 1개(정공법).
- shape가 다름(예: `news/_id`의 translations 머지) → hook 분리.
- `getDirtyStateSet`을 그대로 쓸 수 있으면 합치기, 필드별 patch 로직이 다르면 분리.

---

## 4. 위험 신호 3가지

1. **"필드 5개 이상이면 hook" 기준은 틀림** — 기준은 stateful 여부. 8개 number 필드라도 본질이 "필드별 캐스팅"이면 hook이 아닌 빌더 함수가 정답.
2. **"도메인 모달 구조가 동일"이라는 착시** — UI 구성과 payload contract는 별개. UI는 닮아도 타입·중첩 구조·검증 규칙이 다 다름.
3. **"공용인데 도메인별로 다르게"는 모순** — 그 시점 이미 도메인 hook. 멘탈 모델을 "공용 hook"에서 "**도메인 form hook + 공용 마이크로 hook**"으로 재정의 권장.

---

## 5. proposal-manage 적용 예시 (Before → After)

### 5-1. `index.tsx` — searchState 트랙

**Before**: 페이지 본문 ~290줄. `_initFetchFilters` / `_searchStatusItems` / `_searchSortItems` / `_searchByItems` / `searchState` useState / `handleFilter` 거대 분기 / `SearchStateBar` 9개 props / `TableSortFilter` 4개 props / `useFetchAdapter` / 컬럼 정의 / 모달·펍섭 결선 모두 한 파일.

**After**: `pages/dao/proposal-manage/hooks/useDaoProposalSearchState.ts`로 분리.

```ts
// hooks/useDaoProposalSearchState.ts
export const _initFetchFilters: GetDaoProposalsQueryDto = {
  page: 1, size: 10, sort: DAO_PROPOSAL_SORT.LATEST,
  category: undefined, search: undefined, by: "TITLE",
};

export function useDaoProposalSearchState(deps: { totalItemCount?: number; tabCount?: Record<string, number> }) {
  const { mui } = useLanguage();
  const [searchState, setSearchState] = useState<GetDaoProposalsQueryDto>(_initFetchFilters);

  const statusItems = useMemo(() => [/* ... */], [mui]);
  const sortItems   = useMemo(() => [/* ... */], [mui]);
  const byItems     = useMemo<{ label: string; value: DaoSearchBy }[]>(() => [
    { label: mui["_title"], value: "TITLE" },
    { label: mui["_dao_field_author"], value: "AUTHOR" },
  ], [mui]);

  const patch = (p: Partial<GetDaoProposalsQueryDto>) => setSearchState((s) => ({ ...s, ...p }));
  const reset = () => setSearchState(_initFetchFilters);

  const bar = {
    tabs: statusItems.map((item) => ({
      label: item.label, value: item.value,
      count: item.value === undefined ? (deps.totalItemCount ?? 0) : (deps.tabCount?.[item.value] ?? 0),
      active: searchState.status === item.value,
    })),
    keyword: searchState.search ?? "",
    searchByItems: byItems,
    searchByIndex: byItems.findIndex((i) => i.value === searchState.by),
    onTabChange: (value: DAO_PROPOSAL_STATUS | undefined) => patch({ page: 1, status: value }),
    onChangeKeyword: (v: string) => patch({ search: v || undefined }),
    onClearKeyword: () => patch({ search: undefined }),
    onSearchByChange: (idx: number) => patch({ by: byItems[idx]?.value }),
  };

  const sort = {
    sortItems, currentSort: searchState.sort,
    onSortChange: (value?: string) => patch({ sort: value as DAO_PROPOSAL_SORT }),
    onReset: reset,
  };

  return { searchState, patch, reset, bar, sort };
}
```

페이지 본체:
```tsx
const { searchState, bar, sort } = useDaoProposalSearchState({ totalItemCount, tabCount });

const { rows, isLoading, fetchedPagination, totalItemCount, tabCount, setRequestSearch }
  = useFetchAdapter({ searchState, fetchApi: api.dao.getDaoProposals, mapRow });

useEffect(() => setRequestSearch(true),
  [searchState.page, searchState.size, searchState.sort, searchState.category, searchState.status]);

<SearchStateBar
  title={mui["_dao_proposal_management"]}
  placeholder={mui["_dao_proposal_search_placeholder"]}
  onSubmit={(e) => { e.preventDefault(); setRequestSearch(true); }}
  onCreateClick={() => pubsub.publish("open-create-proposal-modal")}
  {...bar}
/>
<TableSortFilter title="" {...sort} />
```

**효과**: 페이지 290줄 → ~150줄. `SearchStateBar` props 11개 중 9개를 spread 1개로 축약. 쿼리 도메인 책임이 hook으로 분리.

**의도적 비포함**: hook 안에 `setRequestSearch`를 넣지 않음. fetch 트리거는 페이지가 보유.

### 5-2. `create/_id.modal.tsx` — payload 트랙

**Before**: 287줄. form state / images 별도 state / voteBehaviors / 카테고리 메뉴 / 4단계 검증 / 이미지 업로드 / API 호출 + 펍섭 + 다이얼로그 / JSX 모두 한 컴포넌트.

**After**: 3-layer 분리.

**(L1) 빌더·검증 — 순수 함수**
```ts
// create/model.ts
export type CreateProposalForm = CreateDaoProposalRequestDto;

export const _initCreateProposalForm: CreateProposalForm = {
  title: "", category: DAO_PROPOSAL_CATEGORY.POLICY, content: "",
  images: [], voteStartAt: "", voteEndAt: "",
};

export function validateCreateProposalForm(f: CreateProposalForm, mui: Mui): string | null {
  if (!f.title)    return mui["_msg_error_proposal_title_missing"];
  if (!f.content)  return mui["_msg_error_proposal_content_missing"];
  if (!f.category) return mui["_msg_error_proposal_category_missing"];
  return null;
}

export function buildCreateProposalPayload(f: CreateProposalForm, images: string[]): CreateDaoProposalRequestDto {
  return { ...f, images };
}
```

**(L2) 도메인 form hook — 상태/제출만**
```ts
// create/useCreateProposalForm.ts
export function useCreateProposalForm() {
  const { execute, api } = useApi();
  const { pubsub } = usePubSub();
  const Dialog = useDialog();
  const { mui } = useLanguage();

  const [formState, setFormState] = useState<CreateProposalForm>(_initCreateProposalForm);
  const [images, setImages] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const patch = (p: Partial<CreateProposalForm>) => setFormState((s) => ({ ...s, ...p }));
  const resetAll = () => { setFormState(_initCreateProposalForm); setImages([]); };

  const submit = (onDone: () => void) => {
    const err = validateCreateProposalForm(formState, mui);
    if (err) { Dialog.alert({ content: <p>{err}</p> }); return; }

    setIsLoading(true);
    execute(() => api.dao.createDaoProposal(buildCreateProposalPayload(formState, images)), {
      onSuccess: () => {
        Dialog.alert({ header: "Success", content: <p>{mui["_proposal_create_success"]}</p> });
        resetAll(); onDone();
        pubsub.publish("refresh-dao-proposals");
      },
      onError: console.error,
    });
    setIsLoading(false);
  };

  return { formState, patch, images, setImages, isLoading, submit, resetAll };
}
```

**(L3) 공용 마이크로 hook — 진짜 횡단인 것만**
- `useModalOpenSubscribe(topic)` — 펍섭 open/close (거의 모든 모달 공통)
- 기존 `useDaoProposalImageBridge` 재사용

**(L4) 컴포넌트 — JSX 결선만**
```tsx
export const CreateProposalModal = () => {
  const { mui } = useLanguage();
  const { pubsub } = usePubSub();
  const { isOpen, close } = useModalOpenSubscribe("open-create-proposal-modal");
  const { formState, patch, images, setImages, isLoading, submit, resetAll }
    = useCreateProposalForm();

  const voteBehaviors = useWeekFromClickBehavior({
    initialRange: { startDate: formState.voteStartAt, endDate: formState.voteEndAt },
    weekOffsetDays: 7, controls: true,
  });

  const handleClose = () => { close(); resetAll(); };
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => { e.preventDefault(); submit(close); };

  return (
    <SideModal open={isOpen} close={handleClose}>
      {isLoading && <Loading />}
      <form id="dao-proposal-create-modal" onSubmit={handleSubmit}>
        <TextInput value={formState.title} onChange={(e) => patch({ title: e.target.value })} ... />
        <Dropdown
          index={_categoryItems.findIndex((x) => x.value === formState.category)}
          onSelect={(_, i) => patch({ category: _categoryItems[i]?.value })} ...
        />
        <DateRangeField
          value={{ startDate: formState.voteStartAt, endDate: formState.voteEndAt }}
          onChange={({ startDate, endDate }) => patch({ voteStartAt: startDate, voteEndAt: endDate })}
          behaviors={voteBehaviors}
        />
        <TextArea value={formState.content} onChange={(e) => patch({ content: e.target.value })} />
        {/* 이미지 슬롯은 useDaoProposalImageBridge로 추가 정리 가능 */}
      </form>
    </SideModal>
  );
};
```

**효과**: 287줄 → 컴포넌트 ~120줄 + hook ~50줄 + model ~30줄. 검증·payload·API 호출이 컴포넌트에서 완전히 빠짐. `validateCreateProposalForm` / `buildCreateProposalPayload`는 순수 함수로 단독 테스트 가능.

### 5-3. proposal에서 create/update 합치기 판단

`detail/_id.modal.tsx`의 수정 form shape이 create와 동일하면:

```ts
type ProposalFormMode =
  | { kind: "create" }
  | { kind: "update"; proposalId: number; initial: CreateProposalForm };

export function useProposalForm(mode: ProposalFormMode) {
  const initial = mode.kind === "create" ? _initCreateProposalForm : mode.initial;
  // ...
  const submit = (onDone: () => void) => {
    const payload = buildCreateProposalPayload(formState, images);
    const call = mode.kind === "create"
      ? () => api.dao.createDaoProposal(payload)
      : () => api.dao.updateDaoProposal(mode.proposalId, payload);
    execute(call, { onSuccess: /* ... */ });
  };
}
```

**조건부**: detail이 read-only + 액션 버튼들이라면 합치지 말 것. 수정 form이 등장하는 시점에 분리 결정(YAGNI).

---

## 6. 핵심 정리

| 트랙 | 만드는 것 | 만들지 않는 것 |
|---|---|---|
| searchState | `useDaoProposalSearchState`(도메인 전용) | 공용 `useSearchState` |
| payload | 빌더 함수 + `useCreateProposalForm` + 펍섭 마이크로 hook | 공용 `useFormState` / `usePayload` |
| create/update | shape 같으면 mode 분기 hook 1개, 다르면 분리 | 무리한 generic 통합 |

---

## 7. 후속 액션 (보류)

- 본 토론은 문서화까지. 구현 착수는 별도 plan.md 승인 절차로 진행.
- 다음 결정 포인트:
  - `useModalOpenSubscribe` 도입 범위(전 모달 일괄 vs 점진).
  - `proposal-manage/detail` 수정 기능 유무 확인 후 `useProposalForm` 통합 여부 확정.
  - 다른 도메인(pass-management, admins, news)으로 동일 패턴 점진 적용 순서.
