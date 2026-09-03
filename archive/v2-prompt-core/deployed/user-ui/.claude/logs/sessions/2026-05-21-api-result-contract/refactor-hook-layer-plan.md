# PR-3.1 / Hook 계층 분리 — refactor-hook-layer-plan.md

> 세션: 2026-05-21-api-result-contract
> 작업 유형: refactor
> 결정 기준: 합의된 4계층 모델 (Option A — pass-through)
> 작성일: 2026-05-22

---

## 배경

PR-3에서 discussion 도메인을 ApiResult 계약으로 마이그레이션했으나, `useDiscussDetailFetch`가 여전히 surface 책임(Dialog.alert 성공 알림, pubsub.publish 리스트 갱신)을 보유하고 있다. 합의된 4계층 모델에 따라 이 책임을 `useDiscussDetailModal`로 이전한다. 아울러 PR-3에서 발견된 `useDiscussionCommentDelete` pubsub 이벤트명 typo도 함께 수정한다.

---

## 책임 재배치 표 (Before / After)

### useDiscussDetailFetch — Before

| 함수 | 현재 책임 |
|------|-----------|
| `fetchDetail` | API 호출, setFetchedData, boolean 반환 |
| `requestGet` | postId < 0 가드 후 fetchDetail 호출 |
| `runCurrentPostAction` | postId < 0 가드, execute(), **Dialog.alert(successMessage)**, **pubsub.publish("refresh-dao-proposals-discussion-posts-list")**, boolean 반환 |
| `requestDeletePost` | postId < 0 가드, **Dialog.confirm(삭제 확인)**, runCurrentPostAction 호출 |
| `requestPostModerationRestore` | runCurrentPostAction 위임 |
| `requestPostModerationHide` | runCurrentPostAction 위임 |
| `resetDetail` | fetchedData → _initState |

의존: `useApi`, `usePubSub`, `useLanguage`, `useDialog`

### useDiscussDetailFetch — After

| 함수 | 변경 후 책임 | 시그니처 변화 |
|------|-------------|--------------|
| `fetchDetail` | 변경 없음 | 없음 |
| `requestGet` | 변경 없음 | 없음 |
| `runCurrentPostAction` | postId < 0 가드, execute() 후 ApiResult passthrough 반환. Dialog.alert 제거, pubsub 제거. | `Promise<boolean>` → 유지 (실패 false, 성공 true) |
| `requestDeletePost` | Dialog.confirm 보존 (요청 전 게이트), runCurrentPostAction 호출 후 boolean passthrough | 없음 |
| `requestPostModerationRestore` | runCurrentPostAction passthrough | 없음 |
| `requestPostModerationHide` | runCurrentPostAction passthrough | 없음 |
| `resetDetail` | 변경 없음 | 없음 |

제거 의존: `usePubSub`, `useLanguage` (mui successMessage 파라미터가 사라지므로)
보존 의존: `useApi`, `useDialog` (confirm 게이트 때문에)

> 주의: `runCurrentPostAction`의 `CurrentPostActionParams` 타입에서 `successMessage` 필드를 제거한다.

### useDiscussDetailModal — Before

| 핸들러 | 현재 동작 |
|--------|-----------|
| `handleDeletePost` | ok 확인 후 handleModalClose() + discussPostListRefetch() (pubsub 구독하지 않고 prop으로 받은 refetch 직접 호출) |
| `handlePostModerationRestore` | ok 확인 후 resetDetail() |
| `postModerationHide` | ok 확인 후 handleModalClose() + resetDetail() |

성공 후 Dialog.alert / pubsub: **없음** (현재 useDiscussDetailFetch가 담당)

### useDiscussDetailModal — After

| 핸들러 | 변경 후 동작 |
|--------|-------------|
| `handleDeletePost` | ok 확인 후 **Dialog.alert(successMessage)** + **pubsub.publish("refresh-dao-proposals-discussion-posts-list")** + handleModalClose() |
| `handlePostModerationRestore` | ok 확인 후 **Dialog.alert(successMessage)** + **pubsub.publish("refresh-dao-proposals-discussion-posts-list")** + resetDetail() |
| `postModerationHide` | ok 확인 후 **Dialog.alert(successMessage)** + **pubsub.publish("refresh-dao-proposals-discussion-posts-list")** + handleModalClose() + resetDetail() |

추가 의존: `useDialog`, `usePubSub`, `useLanguage` (mui successMessage 가져오기 위해)

> `discussPostListRefetch` prop: `handleDeletePost`에서 직접 호출 부분을 pubsub으로 대체. prop은 제거하거나 유지 선택 필요.
> → **결정**: `discussPostListRefetch` prop 제거. 리스트 갱신은 pubsub을 통한 단일 경로로 통일. `index.tsx`에서 prop 전달 제거.

---

## 변경 파일 목록 및 패치 범위

| 파일 | 변경 종류 | 패치 범위 |
|------|----------|----------|
| `src/pages/dao/discuss-posts-management/detail/hooks/useDiscussDetailFetch.tsx` | 수정 | `CurrentPostActionParams`에서 `successMessage` 제거, `runCurrentPostAction`에서 `Dialog.alert` + `pubsub.publish` 제거, import `usePubSub` + `useLanguage` + `useDialog` 재검토 |
| `src/pages/dao/discuss-posts-management/detail/commend/hooks/useDiscussDetailModal.ts` | 수정 | 각 핸들러에 성공 후 `Dialog.alert` + `pubsub.publish` 흡수, `discussPostListRefetch` prop 제거, 신규 import 추가 |
| `src/pages/dao/discuss-posts-management/index.tsx` | 수정 | `DiscussPostsManagementDetailModal`에 전달하던 `discussPostListRefetch={refetch}` prop 제거 |
| `src/pages/dao/discuss-posts-management/detail/commend/hooks/useDiscussionCommentDelete.tsx` | 수정 | pubsub 이벤트명 `"refresh-dao-proposals-discussion-posts"` → `"refresh-dao-proposals-discussion-posts-list"` (typo 수정) |

> `useDiscussDetailFetch`에서 `useDialog`는 `requestDeletePost`의 `Dialog.confirm` 때문에 보존한다.
> `usePubSub` / `useLanguage` (mui) import는 successMessage 관련 코드 제거 후 사용처 없으면 제거.

---

## 시그니처 변화 요약

```ts
// useDiscussDetailFetch — CurrentPostActionParams (before)
type CurrentPostActionParams = {
  request: (postId: number) => Promise<ApiResult<void>>;
  successMessage: string; // ← 제거
};

// useDiscussDetailFetch — CurrentPostActionParams (after)
type CurrentPostActionParams = {
  request: (postId: number) => Promise<ApiResult<void>>;
};

// useDiscussDetailModal — hook 파라미터 (before)
export const useDiscussDetailModal = ({
  discussPostListRefetch,
}: { discussPostListRefetch: () => void })

// useDiscussDetailModal — hook 파라미터 (after)
export const useDiscussDetailModal = ()
// → discussPostListRefetch prop 제거. pubsub이 리스트 갱신을 담당.
```

---

## 검증 체크리스트

### 외부 동작 동등성

- [ ] 삭제 성공 시: Dialog.confirm(삭제 확인) → API 요청 → Dialog.alert(삭제 성공) → pubsub publish → 모달 닫힘 → 리스트 갱신
- [ ] 복원 성공 시: API 요청 → Dialog.alert(복원 성공) → pubsub publish → resetDetail
- [ ] 숨김 성공 시: reason prompt → API 요청 → Dialog.alert(숨김 성공) → pubsub publish → 모달 닫힘
- [ ] 실패 시: useApi의 silent:false 자동 Dialog → 모달 닫히지 않음 → 상태 오염 없음
- [ ] 취소(unmount/race): canceled passthrough → 아무 side effect 없음

### Silent failure 없음

- [ ] 모든 execute 호출에 `silent: false` 유지
- [ ] ok=false 분기에서 early return 보장 (Dialog.alert / pubsub 미실행)

### Modal hook이 진짜 오케스트레이터인지

- [ ] useDiscussDetailModal이 성공 후 Dialog.alert + pubsub.publish + modal close / resetDetail을 직접 조율
- [ ] useDiscussDetailFetch는 boolean 반환만 하고 surface side effect 미보유

### 이벤트명 버그 수정

- [ ] `useDiscussionCommentDelete`의 pubsub 이벤트명이 `"refresh-dao-proposals-discussion-posts-list"`로 수정됨
- [ ] `events.ts`의 `"refresh-dao-proposals-discussion-posts"` 이벤트가 미사용 상태가 됨 (이 이벤트를 subscribe하는 곳이 없으므로 실제 동작에 영향 없음 — 타입 레지스트리에서 제거는 별도 작업으로 분리)

### 타입 체크 / 린트

- [ ] `yarn tsc --noEmit` PASS (0 errors)
- [ ] `yarn lint` PASS (0 errors, 0 warnings)

---

## 리스크 / 롤백

| 리스크 | 수준 | 완화 방법 |
|--------|------|----------|
| `discussPostListRefetch` prop 제거 후 리스트 미갱신 | 중 | index.tsx의 pubsub subscribe 동작 확인 (이미 `"refresh-dao-proposals-discussion-posts-list"` 구독 중 — 라인 74) |
| successMessage를 modal hook에서 조립할 때 mui 키 오타 | 하 | tsc로 키 타입 검증 |
| useDiscussionCommentDelete 이벤트명 수정 후 subscriber 매칭 | 하 | `"refresh-dao-proposals-discussion-posts-list"` subscriber가 index.tsx에 존재 — 수정 후 정상 동작 |
| events.ts의 `"refresh-dao-proposals-discussion-posts"` 잔존 | 무시 가능 | 타입 레지스트리에서 미사용 키 잔존 — 런타임 영향 없음. 별도 cleanup PR로 분리 |

**롤백**: git revert 단일 커밋 가능 (모든 변경이 1 PR 범위)

---

## 작업 순서

1. `useDiscussDetailFetch.tsx` — successMessage 제거, pubsub/alert 제거, 불필요 import 정리
2. `useDiscussDetailModal.ts` — 성공 후 side effect 흡수, discussPostListRefetch prop 제거, 신규 import 추가
3. `index.tsx` — discussPostListRefetch prop 제거 (1줄)
4. `useDiscussionCommentDelete.tsx` — 이벤트명 typo 수정 (1줄)
5. tsc + lint 검증

