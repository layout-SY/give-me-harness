# Refactor Design — discuss-posts-management

선행: `evaluation-log.md` (R1~R10 / Option A~G / P0~P3). 구현 금지, 설계 문서. pubsub 영역 미언급.

---

## 1) 폴더 트리: Before → After

### Before
```
src/pages/dao/discuss-posts-management/
├── index.tsx
├── index.css
├── config/
│   └── discussion-status-label-key.ts
├── utils/
│   └── groupingSameDiscussRows.ts
├── model/
│   └── tableRows.ts                              # post + comment row 혼재
├── ui/column/
│   └── useDiscussPostTableColumns.tsx            # export 이름은 PascalCase
└── detail/
    ├── _id.modal.tsx
    ├── _id.modal.css
    ├── hooks/
    │   └── useDiscussDetailFetch.tsx             # fetch + 액션 4종 + Dialog 혼재
    └── commend/                                  # 오타 폴더
        ├── proposalPostDetailCommentWidget.tsx   # 인라인 handleDelete
        ├── proposalPostDetailCommentWidget.css
        ├── utils/
        │   └── mappingDIscussCommentRows.ts      # 파일명 카멜 위반
        ├── ui/column/
        │   └── useDiscussPostCommentTableColumns.tsx  # PascalCase export, deps 누락
        └── detail/
            ├── _id.modal.tsx                     # rows payload + findComment 트리탐색
            └── _id.modal.css
```

### After (Option A + B + C + D2 + F 반영)
```
src/pages/dao/discuss-posts-management/
├── index.tsx
├── index.css
├── config/
│   └── discussion-status-label-key.ts            # E 반영 시 통합 함수 추가
├── utils/
│   └── groupingSameDiscussRows.ts
├── model/
│   └── postRows.ts                               # post 전용 (R6)
├── ui/column/
│   └── useDiscussPostTableColumns.tsx            # use* 규약 (R1)
└── detail/
    ├── _id.modal.tsx                             # query/action hook 합성 (R3)
    ├── _id.modal.css
    ├── hooks/
    │   ├── useDiscussPostDetailQuery.ts          # 조회/리셋 (R3)
    │   └── useDiscussPostActions.ts              # 모더레이션/삭제 (R3)
    └── comment/                                  # 오타 교정 (R9)
        ├── proposalPostDetailCommentWidget.tsx   # 액션 hook 합성 (R4)
        ├── proposalPostDetailCommentWidget.css
        ├── model/
        │   └── commentRows.ts                    # comment 전용 (R6/R10)
        ├── hooks/
        │   └── useDiscussCommentActions.ts       # 삭제 격리 (R4)
        ├── utils/
        │   └── mappingDiscussCommentRows.ts      # 파일명 정상화 (R9)
        ├── ui/column/
        │   └── useDiscussPostCommentTableColumns.tsx  # use*, deps 정상화 (R1/R2)
        └── detail/
            ├── _id.modal.tsx                     # 평탄 단일 row payload (D2/F)
            └── _id.modal.css
```

---

## 2) 변경 의존성 그래프 (DAG)

```
A(모델 분리/리네이밍)
  └─▶ B(Columns use* 규약 + deps 정상화)
        └─▶ F(Display row 누수 제거: childComments 제거)
              └─▶ D2(CommentDetail payload 평탄화)
A ─▶ C-post(useDiscussPostDetailQuery + useDiscussPostActions)
A ─▶ C-comment(useDiscussCommentActions)
        └─▶ B(handleDelete prop으로 주입)
E(label key 통합) — 독립, 언제든 가능
G(useDetailModal 결정) — 독립
```

권장 순서: **A → (C-post, C-comment 병행) → B → F → D2 → E → G**.
P0 한정 빠른 경로: **C-comment(최소) → B(deps 수정) → F → D2**. (A 리네이밍 없이도 P0 결함 해소 가능.)

---

## 3) 항목별 상세 설계

### R2 — Comment Columns hook stale closure (P0 / Option B)

**Before** — `detail/commend/ui/column/useDiscussPostCommentTableColumns.tsx:10-14, 82-89, 112`
```ts
export const DiscussionPostCommentTableColumns = (postTitle, rows, handleDelete) => {
  ...
  return useMemo(..., [mui, pubsub]);   // postTitle/rows/handleDelete 캡쳐, deps 누락
};
```
`onOpenDetail`이 `rows`·`postTitle`·`handleDelete`를 캡쳐하면서 deps에는 없음 → stale.

**After**
```ts
// detail/comment/ui/column/useDiscussPostCommentTableColumns.tsx
type Args = {
  postTitle: string;
  onOpenCommentDetail: (row: DaoDiscussionCommentDisplayRow) => void; // 평탄 단일 row
  onDelete: (commentId: number) => void;
};
export const useDiscussPostCommentTableColumns = ({
  postTitle, onOpenCommentDetail, onDelete,
}: Args): TableColumnDef<DaoDiscussionCommentDisplayRow>[] => {
  const { mui } = useLanguage();
  return useMemo(
    () => [ /* ... */ ],
    [mui, postTitle, onOpenCommentDetail, onDelete],
  );
};
```
핵심: (1) 함수명 `use*`. (2) `rows` 인자 제거 — 트리 탐색은 호출처 책임이 아님. (3) 콜백을 prop으로 위임하여 캡쳐 범위를 인자로 한정. (4) deps 전부 포함.

**호출처 변경** (`proposalPostDetailCommentWidget.tsx`)
```ts
const handleOpenCommentDetail = useCallback((row: DaoDiscussionCommentDisplayRow) => {
  // pubsub 영역 — 본 문서 미언급
}, [postTitle]);

const columns = useDiscussPostCommentTableColumns({
  postTitle, onOpenCommentDetail: handleOpenCommentDetail, onDelete: handleDelete,
});
<Table columns={columns} rows={displayRows} ... />
```
`Table columns={DiscussionPostCommentTableColumns(postTitle, displayRows, handleDelete)}` 형태(매 렌더 호출)도 사라지고, 컬럼은 메모이즈된 단일 참조로 유지.

**파일 변동**
- 이동: `detail/commend/ui/column/useDiscussPostCommentTableColumns.tsx` → `detail/comment/ui/column/useDiscussPostCommentTableColumns.tsx`
- 수정: `proposalPostDetailCommentWidget.tsx` (호출 시그니처)

**회귀 위험**: 컬럼 prop 시그니처 breaking. 호출처 1곳뿐이라 국지적.

---

### R5 + R10 — CommentDetail 의존 역전 + display row 누수 (P0 / Option D2 + F)

**Before** — `detail/commend/detail/_id.modal.tsx:15-19, 34-51`
```ts
type CommentDetailModalPayload = { commentId; postTitle; rows: DaoDiscussionCommentTableRow[]; };
const selectedComment = useMemo(() => findComment(modalState.rows), ...);
```
`mappingDiscussCommentRows`가 `childComments`를 평탄화 후에도 유지 → 모달이 트리 재탐색.

**After (D2)** — 평탄 단일 객체 payload
```ts
// detail/comment/detail/_id.modal.tsx
type CommentDetailModalPayload = {
  comment: DaoDiscussionCommentDisplayRow; // childComments 없음 (F)
  postTitle: string;
  onDelete: () => void;
};
const INITIAL: CommentDetailModalPayload = { comment: EMPTY_DISPLAY_ROW, postTitle: "", onDelete: () => {} };
// findComment 제거. selectedComment = modalState.comment.
```

**After (F)** — `model/commentRows.ts` (신규)
```ts
export interface DaoDiscussionCommentTableRow {  // API 인입 형태 (childComments 보유)
  author: DaoAuthorDto;
  content: string;
  status: DaoDiscussionStatus;
  createdAt: string;
  deletedAt: string;
  reportCount: number;
  parentId: number;
  commentId: number;
  childComments: DaoDiscussionCommentTableRow[];  // 인입까지만 사용
}

export interface DaoDiscussionCommentDisplayRow {  // 평탄화 결과 — 트리 미보유
  author: DaoAuthorDto;
  content: string;
  status: DaoDiscussionStatus;
  createdAt: string;
  deletedAt: string;
  reportCount: number;
  parentId: number;
  commentId: number;
  isChild: boolean;
  rowKey: string;
}
```
`mappingDiscussCommentRows`도 `DaoDiscussionCommentDisplayRow`만 반환(childComments 미투영).

**파일 변동**
- 신규: `detail/comment/model/commentRows.ts`
- 수정: `detail/comment/utils/mappingDiscussCommentRows.ts` (childComments 제거, return 타입 좁힘)
- 수정: `detail/comment/detail/_id.modal.tsx` (payload·findComment 제거)
- 삭제: 상위 `model/tableRows.ts`의 `DaoDiscussionCommentTableRow` / `DaoDiscussionCommentDisplayRow` 항목

**호출처 변경**
- `proposalPostDetailCommentWidget.tsx`: 댓글 상세 진입 시 평탄 row를 그대로 전달.
- `useDiscussPostCommentTableColumns.tsx`: action 컬럼에서 row(평탄)만 위로 전달.

**회귀 위험**: payload 시그니처 breaking (구독자 1곳). 대댓글 표시는 `isChild` 플래그로 유지되어 UI 영향 없음.

---

### R3 — `useDiscussDetailFetch` God-hook 분리 (P1 / Option C)

**Before** — `detail/hooks/useDiscussDetailFetch.tsx:32-118`
단일 hook이 (1) detail fetch (2) restore (3) delete (4) hide(reason) (5) refetch 광장 (6) Dialog confirm을 모두 보유. 반환 6개.

**After** — 두 hook으로 분리
```ts
// detail/hooks/useDiscussPostDetailQuery.ts
export const useDiscussPostDetailQuery = () => {
  // fetchedData, isLoading, requestGet(postId), resetDetail, refetchDetail()
  return { fetchedData, isLoading, requestGet, refetchDetail, resetDetail };
};
```
```ts
// detail/hooks/useDiscussPostActions.ts
type Args = {
  postId: number;
  onAfterMutation?: (kind: "refetch" | "close") => void;
};
export const useDiscussPostActions = ({ postId, onAfterMutation }: Args) => {
  // requestPostModerationRestore, requestPostModeration(reason), requestDeletePost
  return { isLoading, requestPostModerationRestore, requestPostModeration, requestDeletePost };
};
```
- query hook은 상태(fetchedData) 보유, action hook은 무상태(postId를 인자로).
- 액션 성공 후처리는 콜백 주입으로 query↔action 분리. (delete 시 close, 그 외 refetch)
- Dialog confirm은 action hook 내부에 잔류(액션의 일부).

**호출처 변경** — `detail/_id.modal.tsx`
```ts
const { fetchedData, isLoading, requestGet, refetchDetail, resetDetail } = useDiscussPostDetailQuery();
const { requestPostModerationRestore, requestPostModeration, requestDeletePost } =
  useDiscussPostActions({
    postId: fetchedData.postId,
    onAfterMutation: (kind) => (kind === "refetch" ? refetchDetail() : handleClose()),
  });
```

**파일 변동**
- 신규: `detail/hooks/useDiscussPostDetailQuery.ts`, `detail/hooks/useDiscussPostActions.ts`
- 삭제: `detail/hooks/useDiscussDetailFetch.tsx`
- 수정: `detail/_id.modal.tsx`

**회귀 위험**: 모달 1곳만 영향. 액션 후 refetch 콜백 누락 시 화면 정체 가능 — 모달측에서 명시적으로 주입해야 함.

---

### R4 — Comment 삭제 액션 hook 격리 (P1 / Option C)

**Before** — `proposalPostDetailCommentWidget.tsx:44, 76-96`
```ts
const [_, setIsLoading] = useState(false);  // 미사용 변수
const handleDelete = (commentId) => {
  Dialog.confirm(...).then((yes) => {
    if (yes) {
      try {
        setIsLoading(true);
        execute(() => api.dao.deleteDaoDiscussionComment(commentId), { onSuccess: ... });
      } catch (e) { ... }  // execute는 throw 안 함 → 무효 try/catch
      finally { setIsLoading(false); }    // execute가 비동기 → 의미 깨짐
    }
  });
};
```

**After**
```ts
// detail/comment/hooks/useDiscussCommentActions.ts
type Args = { onAfterDelete?: () => void };
export const useDiscussCommentActions = ({ onAfterDelete }: Args = {}) => {
  const { api, execute } = useApi();
  const Dialog = useDialog();
  const { mui } = useLanguage();
  const { isLoading, runAsyncTask } = useAsyncTask();

  const requestDeleteComment = useCallback(async (commentId: number) => {
    if (commentId < 0) return;
    const yes = await Dialog.confirm({ content: <p>{mui["_dao_msg_delete_confirm"]}</p> });
    if (!yes) return;
    await runAsyncTask(async () => {
      await execute(() => api.dao.deleteDaoDiscussionComment(commentId), {
        onSuccess: () => {
          Dialog.alert({ content: <p>{mui["_dao_msg_delete_success"]}</p> });
          onAfterDelete?.();
        },
      });
    });
  }, [api.dao, Dialog, mui, onAfterDelete, runAsyncTask, execute]);

  return { isLoading, requestDeleteComment };
};
```
- `useAsyncTask`로 post 액션 패턴과 일치.
- 무효 try/catch 제거, 미사용 `setIsLoading` 제거.
- 새로고침 시그널은 콜백으로 위임.

**호출처 변경** — `proposalPostDetailCommentWidget.tsx`
```ts
const { requestDeleteComment } = useDiscussCommentActions({ onAfterDelete: refetch });
// columns 인자: onDelete={requestDeleteComment}
```

**파일 변동**
- 신규: `detail/comment/hooks/useDiscussCommentActions.ts`
- 수정: `proposalPostDetailCommentWidget.tsx`

**회귀 위험**: 사실상 동일 동작. 다만 액션 중 로딩 표시가 필요하면 `isLoading`을 위젯에서 소비해야 함(현재는 미사용).

---

### R6 + R9 — 모델 분리 + 폴더/파일 리네이밍 (P2 / Option A)

**파일 변동**
- 분리: `model/tableRows.ts` → 두 파일
  - `model/postRows.ts`: `DaoDiscussPostTableRow`, `DaoDiscussPostGroupedTableRow`
  - `detail/comment/model/commentRows.ts`: `DaoDiscussionCommentTableRow`, `DaoDiscussionCommentDisplayRow` (R10 형태)
- 리네이밍: `detail/commend/` → `detail/comment/`
- 리네이밍: `mappingDIscussCommentRows.ts` → `mappingDiscussCommentRows.ts` (현재 파일명은 이미 소문자 d로 존재, import 경로만 오타)

**호출처 변경**
- `index.tsx`, `utils/groupingSameDiscussRows.ts`, `ui/column/useDiscussPostTableColumns.tsx`: import `model/postRows`
- `detail/_id.modal.tsx`: `./comment/proposalPostDetailCommentWidget`
- `proposalPostDetailCommentWidget.tsx`: `./utils/mappingDiscussCommentRows`, `./model/commentRows`
- 컬럼/모달: `../../model/commentRows`

**회귀 위험**: 순수 경로 변경. git mv로 이력 보존 권장. 외부 페이지에서 댓글 row 타입을 import하는 곳이 없어야 함(현재 grep상 page 내부 한정).

---

### R1 — Columns export `use*` 규약 (P2 / Option B)

**Before**
```ts
// ui/column/useDiscussPostTableColumns.tsx
export const DiscussionPostTableColumns = () => { ... useMemo(...) };
// index.tsx
columns={DiscussionPostTableColumns()}
```

**After**
```ts
export const useDiscussPostTableColumns = (): TableColumnDef<DaoDiscussPostGroupedTableRow>[] => {
  const { mui } = useLanguage();
  return useMemo(() => [ /* ... */ ], [mui]);
};

// index.tsx
const columns = useDiscussPostTableColumns();
<Table columns={columns} ... />
```
- 함수 본문 변경 없이 export 명만 정상화 + 호출 위치를 컴포넌트 최상위로.
- `usePubSub` 의존은 pubsub 영역이라 본 문서에서 변경 권고 없음(기존 deps 유지).

**파일 변동**: import 경로 동일, named export만 교체. `index.tsx` 1곳 수정.

**회귀 위험**: 단순 리네이밍.

---

### R7 — Status→label 통합 (P3 / Option E)

**After** — `config/discussion-status-label-key.ts`
```ts
type DiscussionKind = "post" | "comment";
export type DiscussionStatusLabelKey = DiscussionPostStatusLabelKey | DiscussionCommentStatusLabelKey;

export const getDiscussionStatusLabelKey = (
  status: DaoDiscussionStatus, kind: DiscussionKind,
): DiscussionStatusLabelKey => {
  if (status === "DELETED") return kind === "post" ? "_dao_discussion_exposure_post_deleted" : "_dao_discussion_exposure_deleted";
  if (status === "REPORTED") return "_dao_discussion_exposure_reported";
  if (status === "HIDDEN") return "_dao_discussion_exposure_post_hidden";
  return "_dao_discussion_exposure_normal";
};
```
기존 두 함수는 본 함수 위임형 alias로 단기 유지하다 제거. 도메인별 좁은 반환 타입 보존을 원하면 alias를 영구 유지.

**호출처**: post column / post detail / comment column / comment detail 4곳.

**회귀 위험**: 분기 동일. union 확장 시 한 곳에서만 관리.

---

### R8 — `useDetailModal`(=`useModal`) 결정 (P3 / Option G)

현 상태: `src/hooks/use-modal/useModal.ts` 는 4줄짜리 disclosure이며 본 페이지의 `detail/_id.modal.tsx` 단 1곳만 import. evaluation §6 Q2 답에 따라 분기:

- **타 페이지 반복 없음** → `useModal` 제거, 모달에 `useState<boolean>` 인라인.
  - 변동: `detail/_id.modal.tsx` 인라인화, `src/hooks/use-modal/useModal.ts` 삭제.
- **5+ 회 반복 사용 예정** → 그대로 두되 명명 `useDisclosure`로 승급(전역 공용 표명).

**회귀 위험**: 단일 호출처라 국지적.

---

## 4) 미해결 의문 (역질문) — evaluation-log §6

1) **Comment 상세 단건 API 존재 여부 → Option D1 vs D2**
   - 코드 확인 결과 `getDaoDiscussion(Post)Comment(s)` 단건 조회는 `discussion.api.ts`에 부재(목록/삭제/모더레이션만).
   - 본 설계는 **D2(평탄 row payload 전달)** 가정으로 기술함.
   - 만약 추후 단건 API가 도입되면 → D1으로 분기: 모달 payload를 `{ commentId, postTitle, onDelete }`로 축소하고 모달 내부에서 `useDiscussCommentDetailQuery(commentId)` 호출. `displayRow` 의존이 사라져 R10도 자연히 해소.

2) **`useDetailModal`(useModal) 패턴 재사용성 → Option G**
   - 현 grep상 본 페이지 외 사용처 없음. **즉시 인라인 권장**.
   - 다른 모달이 곧 추가될 계획이면 → `useDisclosure`로 승급하고 `src/components/modal/hooks/`로 이전.

3) **`commend/` 폴더명 의도 → R9**
   - 영문 `comment`의 오타로 판단(파일 내부 식별자는 `Comment` 사용). **`comment/`로 교정**.
   - 만약 의도된 약어("commend = 추천")라면 → 폴더는 유지하되 README로 의미 명시. 단, 식별자 컨벤션과 충돌하므로 권장하지 않음.

4) **Status label key union 확장 계획 → Option E 우선순위**
   - 현재 상태 4종 고정. **P3 유지**.
   - `MUTED`/`PINNED` 등 신규 상태가 로드맵에 있다면 → P1으로 상향, 통합 함수 도입을 P0~P2 묶음과 함께 처리하여 두 곳 동시 수정 위험 차단.

---

## 5) 영향 범위 종합

| 영역 | 변경 파일 | breaking surface |
|---|---|---|
| index.tsx | 1 | columns 호출 표현식 |
| post detail modal | 1 | hook 분리에 따른 합성 |
| comment widget | 1 | 액션 hook + columns 시그니처 |
| comment columns | 1 | 함수명/시그니처/deps |
| comment detail modal | 1 | payload 평탄화 |
| 모델 | 분할 2 | import 경로 |
| 폴더/파일명 | git mv 다수 | import 경로 |
| 공용 hook | (옵션) `useModal` 제거 | 본 페이지 1곳 |

전 변경 모두 `src/pages/dao/discuss-posts-management/` 페이지 내부에 격리되며, 외부 페이지/공용 컴포넌트 API 변경 없음(Option G의 `useModal` 제거만 예외).
