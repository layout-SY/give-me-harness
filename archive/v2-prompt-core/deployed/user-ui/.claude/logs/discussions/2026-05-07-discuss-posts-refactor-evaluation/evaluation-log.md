# Discuss Posts Management — 도메인 리팩토링 평가

- 일자: 2026-05-07
- 평가자: evaluator 에이전트
- 분석 대상: `src/pages/dao/discuss-posts-management/` 전수 (9개 파일)

분석 대상(전수):
- `src/pages/dao/discuss-posts-management/index.tsx`
- `src/pages/dao/discuss-posts-management/index.css`
- `src/pages/dao/discuss-posts-management/config/discussion-status-label-key.ts`
- `src/pages/dao/discuss-posts-management/detail/_id.modal.tsx`
- `src/pages/dao/discuss-posts-management/detail/_id.modal.css`
- `src/pages/dao/discuss-posts-management/detail/commend/proposalPostDetailCommentWidget.tsx`
- `src/pages/dao/discuss-posts-management/detail/commend/proposalPostDetailCommentWidget.css`
- `src/pages/dao/discuss-posts-management/detail/commend/detail/_id.modal.tsx`
- `src/pages/dao/discuss-posts-management/detail/commend/detail/_id.modal.css`

---

## 1. 파일별 평가

### `discuss-posts-management/index.tsx`

- **요약**: 리스트 페이지. 검색/정렬/페이징 state, row grouping 변환, 컬럼 정의, pubsub 구독을 한 컴포넌트에서 모두 처리.
- **문제**:
  - 책임 혼재: searchState 관리(L31-38), groupedDiscussRows 변환(L64-86, 순수), columns 정의(L88-184, JSX 빌더), pubsub 구독(L198-203), 모달 placement(L207)가 한 함수 본문에 평면 배치.
  - `enum FILTER_TYPES`(L19-24)에 SORT/KEYWORD가 선언만 되어 있고 `handleFilter`(L186-196)는 PAGE/SIZE만 사용 → dead-enum + leaky 추상화. SORT/KEYWORD는 인라인 `setSearchState((prev) => ...)`로 직접 처리됨(L226, L234, L249).
  - `setRequestSearch(true)`가 5군데(L195, L231, L251, L255, L199)에 산재 → 검색 트리거가 로컬 규약. 백로그 BL-1(useSearchParamsState)로 흡수 가능.
  - `themeClassName` 빌드(L104)가 cell 인라인 → 같은 도메인의 다른 list/detail에서 동일한 색상 규약을 재사용할 때 grep 비용.
  - `proposalGroupIndex`, `proposalGroupSize`가 계산되지만 실제로는 `isProposalGroupHead`만 cell에서 소비됨(L108-118) → 미사용 데이터(YAGNI 위반).
- **근거**:
  - L19-24 `const enum FILTER_TYPES { SORT, KEYWORD, PAGE, SIZE }` + L186-196 `handleFilter`는 PAGE/SIZE만 분기 → SORT/KEYWORD는 dead.
  - L64-86 grouping 로직 21줄, 순수 변환이지만 컴포넌트 내부에 인라인.
  - L88-184 columns 96줄, JSX 셀 렌더러 4종(custom×4) 포함.
- **개선 방법**:
  1. `groupDiscussionRowsByProposal(rows)` 순수 함수를 `pages/dao/discuss-posts-management/model/group-rows.ts` (또는 FSD `entities/discussion-post/lib/`)로 이전. 컴포넌트는 `useMemo(() => groupDiscussionRowsByProposal(rows), [rows])`만 호출.
  2. `columns`를 `model/columns.tsx`(또는 `ui/DiscussionPostsTableColumns.tsx`)로 추출. mui와 pubsub publisher를 인자로 받는 `buildDiscussionPostColumns({ mui, onOpenDetail })` 시그니처. 셀 렌더러 4종(`PostIdCell`, `RelatedProposalCell`, `CommentCountCell`)을 명명된 컴포넌트로 분리.
  3. `enum FILTER_TYPES` 폐기 — PAGE 핸들러만 남으므로 `handlePageChange(page: number)`로 단순화. SORT/KEYWORD는 이미 인라인이므로 enum 자체를 제거.
  4. (BL-1과 결합) `useSearchParamsState<GetDaoDiscussionPostsQueryDto>(_initSearchState)`로 `searchState`/`setSearchState`/`setRequestSearch` 합성을 일원화.
- **우선순위**: P1
- **연계**: BL-1 (search state 공용 훅), 신규 항목 NEW-A (column builder 추출)

---

### `discuss-posts-management/index.css`

- **요약**: 리스트 테이블 스타일. 컬럼 너비 + `discuss-row` 모듈 스타일 + author badge 스타일.
- **문제**:
  - 토큰 부재: `#2f6bff`, `#22c55e`, `#ef4444`, `#c7cdd8`, `#f59e0b`, `#d1d5db`(L99-117) 등 5개 테마 컬러가 하드코딩. `getThemeColorKeyByNumericId`가 재사용 가능한 추상이라면 컬러 토큰도 같이 토큰화되어야 함.
  - `#dao-discuss-posts-management .col-number` (L11-14)가 정의되어 있으나 `index.tsx`에서 `col-number` 클래스 사용처 미확인 → dead rule 의심.
  - id selector 의존(`#dao-discuss-posts-management`) — FSD 관점 page 단위 격리는 가능하지만, `discuss-row__*`는 row UI primitive 성격이므로 page id에 묶일 이유가 없음(L65-176).
- **근거**: L11-14 `col-number` 미사용. L96-117 컬러 5종 반복. L119-122 `--same` 분기.
- **개선 방법**:
  1. `discuss-row` 블록을 `pages/dao/components/discuss-row/discuss-row.css`(or `entities/discussion-post/ui/DiscussRow/`)로 이전 + 컬러 토큰화(`--clr-row-accent-blue`).
  2. id selector 폐기, BEM 클래스 단독 사용. page 격리는 page wrapper에 BEM 네임스페이스로 충분.
  3. `col-number` rule 제거 (사용처 grep 후).
- **우선순위**: P2
- **연계**: 기존 backlog 없음 → 신규 NEW-B (DAO 컬러 토큰화)

---

### `discuss-posts-management/config/discussion-status-label-key.ts`

- **요약**: 상태 → i18n key 매핑 함수 2개.
- **문제**:
  - `DiscussionPostStatusLabelKey`/`DiscussionCommentStatusLabelKey`(L3-13) 두 union이 4개 멤버 중 3개가 동일(REPORTED, HIDDEN, NORMAL은 동일 또는 의미 동등) → 중복 선언이 유지비를 만든다.
  - `if-if-if-return` 사슬(L16-19, L23-26) → 매핑 객체로 표현 가능. 새로운 상태 추가 시 두 함수 모두 수정 필요.
  - 파일 위치(`config/`)가 FSD에서는 모호. label key는 view-layer 전용 매핑이지만 `entities/discussion-post/model/status.ts`로 옮겨 도메인 모델과 함께 두는 편이 정합.
  - i18n 키 일부(`_dao_discussion_exposure_post_hidden`)가 post/comment 양쪽에서 동일하게 재사용됨 → moderation 관련 key 일원화는 backlog F-01과 직결.
- **근거**: L7 vs L13 — 두 union이 `_dao_discussion_exposure_post_hidden`을 공유. L15-20 vs L22-27 — 분기 로직 1:1 동일.
- **개선 방법**:
  1. 매핑 record로 치환: `const POST_STATUS_LABEL_KEY: Record<DaoDiscussionStatus, DiscussionPostStatusLabelKey> = { ACTIVE: ..., DELETED: ..., REPORTED: ..., HIDDEN: ... }` + `getDiscussionPostStatusLabelKey = (s) => POST_STATUS_LABEL_KEY[s]`. 전체 case enumeration 강제.
  2. `entities/discussion-post/model/status.ts`로 이동 + `index.ts` 배럴 export. `config/`는 page-only 빌드/feature flag 등 진짜 설정에만 사용.
  3. 두 union을 단일 `DiscussionStatusLabelKey`로 통합하고, `target: "post" | "comment"` 인자로 분기.
- **우선순위**: P2
- **연계**: F-01 (moderation 키 분리). NEW-C (status mapping object 화).

---

### `discuss-posts-management/detail/_id.modal.tsx`

- **요약**: 상세 SideModal — 데이터 fetch, moderation(hide/restore), delete, ReasonPrompt 합성, JSX 표현이 전부 한 컴포넌트에 위치.
- **문제**:
  - **try/finally 안티패턴 (F-03 직격)**: `requestGet`(L49-62)과 `handleDeletePost`(L105-125)에서 `execute()`는 비동기 fire-and-forget인데 `finally`에서 즉시 `setIsLoading(false)` → `onSuccess` 실행 시점에는 이미 false. 인디케이터가 형식적.
  - **set/unset 비대칭**: `handlePostModerationRestore`(L83-92)는 `setIsLoading(true)`도 없음 → 사용자에게 진행 중 피드백 부재. `handlePostModeration`(L64-81)은 콜백 안에서 true만 설정하고 종료 처리 없음 → 영구 로딩 가능성.
  - **i18n 키 임시 재사용 (F-01)**: L67-69 `_dao_proposal_forceEndVote_reason_*` → 본 도메인의 게시글 숨김 의도와 의미 충돌. 해당 임시 차용은 logs에 기록되어 있음.
  - **모달 오케스트레이션 + form/검증 + 데이터 페칭이 단일 컴포넌트**: 모달 상태(L45-47), fetch(L49-62), 두 종 mutation(L64-92), delete(L105-125), pubsub 구독(L127-130), JSX(L132-217). FSD 관점에서 mutation은 `features/discussion-post-moderation/model/use-post-moderation.ts`로, fetch는 `features/discussion-post-detail/model/use-post-detail.ts`로 분해 가능.
  - **부모-자식 통신이 props 없는 pubsub**: `DiscussPostsManagementDetailModal`을 부모(`index.tsx`)에 단순 마운트하고(`<DiscussPostsManagementDetailModal />`) `pubsub.publish("open-discussion-post-detail-modal", ...)`로 여는 구조 → BL-9 영역.
  - **dead 초기값 패턴**: `_initState`에 `-1`을 sentinel로 사용(L21-36). 이후 `if (postId < 0) return`(L65, L84, L106) — sentinel 분산. `fetchedData: GetDaoDiscussionPostDetail | null`로 단순화 가능.
  - **action 영역 JSX 분기 복잡**: L163-184 — HIDDEN/!HIDDEN, !DELETED 두 축이 한 블록. `<PostActions status onHide onRestore onDelete>` 컴포넌트로 분리 가능.
- **근거**:
  - L49-62: `try { setIsLoading(true); execute(...); } catch ... finally { setIsLoading(false) }` — execute는 Promise를 반환해도 await 없음.
  - L83-92: 동일 패턴이지만 `setIsLoading` 자체가 없음 → 일관성 부재.
  - L107: `Dialog.confirm(...).then((yes) => { if (yes) { try { setIsLoading(true); execute(...); ... } finally { setIsLoading(false); } } })` — confirm Promise + execute Promise + finally가 동일 시점에 트리거.
  - L127-130: `useEffect(() => pubsub.subscribe(..., handleOpen), [])` — deps 빈 배열, handleOpen이 closure로 캡쳐된 `requestGet`을 가짐. 현재는 stable이지만 hook 추출 후 회귀 위험.
- **개선 방법**:
  1. `usePostDetail(postId)` hook 추출 — `{ data, isLoading, refetch }` 표준 인터페이스. 내부에서 `setIsLoading` 동기 종료 안티패턴 제거 (BL-5 패턴 재사용).
  2. `usePostModeration({ postId, onSuccess })` hook — `{ hide(reason), restore(), isPending }` 반환. `useReasonPrompt` 합성을 hook 내부로 흡수, 컴포넌트는 단일 호출 `moderation.hide()`.
  3. `usePostDelete({ postId, onSuccess })` hook — `Dialog.confirm` + delete 합성. fetched sentinel 의존 제거.
  4. `<PostHeaderActions status onHide onRestore onDelete />` 분리 (L163-184).
  5. `<PostMetaRow author createdAt viewCount />`, `<PostFooterStats likes reportCount />` UI 컴포넌트 분리.
  6. moderation i18n 키를 F-01에 따라 `_dao_post_hide_reason_*` 신설로 교체.
  7. `_initState` sentinel을 `null`로 단순화 + early return JSX guard.
- **우선순위**: P0 (안티패턴 + 버그 잠재 + 백로그 직접 매칭)
- **연계**: F-01, F-03, BL-5, BL-6, BL-9. 신규 NEW-D (모달-내부 hook 3분할 표준).

---

### `discuss-posts-management/detail/_id.modal.css`

- **요약**: 상세 모달 스타일 605줄. proposal banner / post card / comments table 셋의 스타일이 한 파일에 누적.
- **문제**:
  - **공동 책임 혼재**: L412-578 영역의 `dao-comment-table`/`dao-comment-row` 스타일이 본 파일에 정의되어 있으나, **실제 댓글 테이블은 `proposalPostDetailCommentWidget.tsx`가 렌더**한다. 즉 위젯 전용 스타일이 부모 모달 CSS에 밀착되어 결합.
  - **하드코딩 컬러 ~30+ 종**(L20, L73, L86, L99-101, L132, L167-170, L208 등) — 토큰 부재.
  - **상태 셀렉터에 한국어 데이터 속성**(L541, L546, L551): `[data-status="게시중"]`, `[data-status="신고접수"]`, `[data-status="삭제"]` → i18n 안티패턴. 일본어/영어 빌드 시 매칭 깨짐.
  - dead rule 의심: `dcdm-*`(comment detail modal) 스타일은 본 파일이 아니라 자식 modal css에 있어야 정상. (현재 본 파일에는 없음. OK)
  - 605줄은 단일 파일 한계에 근접.
- **근거**:
  - L541-554 한국어 data-status 매칭 셀렉터 3개.
  - L412-578 댓글 테이블 스타일이지만 본 파일이 아니라 widget css가 본가여야 함.
- **개선 방법**:
  1. `[data-status]` 셀렉터를 영문 enum 값(`ACTIVE`/`REPORTED`/`DELETED`)으로 교체. 컴포넌트 측 `data-status={row.status}`만 사용.
  2. L412-578 댓글 영역을 `proposalPostDetailCommentWidget.css`로 이동(또는 `entities/discussion-comment/ui/CommentTable.css` 신설). 부모 모달은 댓글 영역 layout만 담당.
  3. 컬러 토큰화 (NEW-B와 결합).
- **우선순위**: P1 (i18n 셀렉터 버그 잠재)
- **연계**: NEW-B, NEW-E (CSS i18n 셀렉터 정리)

---

### `discuss-posts-management/detail/commend/proposalPostDetailCommentWidget.tsx`

- **요약**: 댓글 검색/리스트 위젯. fetch + flatten + columns + delete + 자식 모달 placement.
- **문제**:
  - **폴더 오타**: `commend/` → `comment/` 의도. 도메인 용어 일치 깨짐. 임포트 경로 전체에 영향.
  - **버려지는 isLoading**: L37 `const [_, setIsLoading] = useState(false);` — getter 미사용, setter만 try/finally에 들어가 있음(L195, L206) → 효과 0. F-03 패턴 + dead state.
  - **try/finally 안티패턴 (F-03 재발)**: L194-208 `try { setIsLoading(true); execute(...) } catch... finally { setIsLoading(false); }` — `_id.modal.tsx`와 동일 패턴.
  - **pubsub 토픽 오타 의심**: L199 `pubsub.publish("refresh-dao-proposals-discussion-posts")` — 부모(`index.tsx` L199)는 `"refresh-dao-proposals-discussion-posts-list"`를 구독. **댓글 삭제 시 리스트 갱신 토픽 미스매치 → 리스트 totalItemCount 동기화 누락 가능**. 잠재 버그.
  - **자식 행렬 변환을 `useMemo`로 했지만(L74-93) 순수 함수**: `flattenDiscussionComments(rows)`로 추출 가능. 자식의 자식까지 재귀하지 않고 1단계만 처리하는 점이 명시적이지 않음(L80 `childComments: childComment.childComments` — 표시는 하지만 펼치진 않음).
  - **모달에 ad-hoc payload로 `rows` 전체와 `onDelete` 콜백을 보냄** (L155-161) — 자식 모달은 부모 rows를 가지고 다시 트리 검색(`detail/_id.modal.tsx` L34-51). 데이터 소스를 자식이 부모 메모리에서 끄집어내는 구조 → 결합 강. BL-9(Promise 모달)로 해소 가능 + `getDaoDiscussionCommentDetail(commentId)` 단건 API 도입이 정공법.
  - **search submit 시 page=1 reset 누락** (L212-215): keyword 변경 후 submit 하면 현재 page 유지 → empty page UX 우려.
  - **columns 정의 89줄(L95-184)** — `index.tsx`와 동일한 거대 columns 인라인 패턴.
  - **`SEARCH_BY_DROPDOWN_TYPE` 매직 문자열** (L19) — 해당 type이 글로벌 dropdown registry에 영향한다면 전역 충돌 위험.
- **근거**:
  - L37 `const [_, setIsLoading]` — getter discard.
  - L199 vs `index.tsx` L199 토픽 mismatch.
  - L74-93 flatten 로직 inline.
  - L155-161 `pubsub.publish("open-discussion-comment-detail-modal", { commentId, postTitle, rows, onDelete })`.
- **개선 방법**:
  1. **즉시**: L199 토픽을 `"refresh-dao-proposals-discussion-posts-list"`로 통일. (P0 버그)
  2. dead `setIsLoading` 제거 또는 정상 isLoading 노출(prop drill 또는 `useDeleteComment` hook의 isPending).
  3. 폴더 rename `commend/` → `comment/`. import 경로 업데이트.
  4. `flattenDiscussionComments(rows)` 순수 함수를 `entities/discussion-comment/lib/flatten.ts`로 추출.
  5. columns를 `model/columns.tsx`로 추출 + cell 컴포넌트 명명화.
  6. 자식 모달 결합 해소: `getDaoDiscussionComment(commentId)` 단건 API 도입 + 자식 모달은 commentId만 받음. 또는 BL-9 Promise 모달.
  7. `handleSubmit`에서 `page: 1` reset.
- **우선순위**: P0 (토픽 mismatch 버그) + P1 (구조)
- **연계**: F-03, BL-6, BL-9. NEW-F (commend→comment rename), NEW-G (flatten 추출), NEW-H (단건 댓글 API).

---

### `discuss-posts-management/detail/commend/proposalPostDetailCommentWidget.css` (111 lines)

- **요약**: 위젯 자체 스타일.
- **문제**:
  - 부모 모달 CSS와 책임 중첩 (`dao-comment-table`/`dao-comment-row`가 부모 css L412-578에도 존재) — 두 파일이 같은 클래스를 동시에 정의하면 cascade 충돌 위험.
  - 하드코딩 컬러/사이즈.
- **개선 방법**:
  1. 부모 모달의 댓글 관련 스타일을 본 파일로 흡수, 부모는 layout만.
  2. NEW-B 토큰화에 합류.
- **우선순위**: P2
- **연계**: NEW-B, NEW-I (CSS 책임 경계 정리)

---

### `discuss-posts-management/detail/commend/detail/_id.modal.tsx`

- **요약**: 댓글 단건 상세 모달. 부모로부터 `rows` 전체를 받아 재귀 검색으로 선택 댓글 추출, 삭제는 `onDeleteRef`(콜백 ref) 호출.
- **문제**:
  - **단건 API 부재 → 부모 메모리 의존**: L34-51 `findComment` 재귀 — 단건 fetch가 없어 부모 list cache를 트리 탐색. 부모 페이지 전환/검색 변경 시 race 발생 가능. 실질 anti-pattern.
  - **콜백 ref 패턴**: L32 `onDeleteRef`, L65 setter, L72 reset, L76 invoke — pubsub payload에 함수를 실어 전달하는 구조의 부산물. BL-9 Promise 모달로 자연 해소.
  - **selectedComment가 nullable** but 하단 JSX가 부분적으로만 가드 (L102 conditional + L106 `selectedComment?.content || "-"`). 댓글이 부모 rows에서 사라진 케이스(예: pagination)에서 빈 모달 노출.
  - **삭제 후 모달 닫힘은 즉시지만 부모 list 갱신은 위젯의 `setRequestSearch(true)`에 의존** — 삭제 직전 상태가 잠시 표시되는 stale window.
  - **`useEffect` deps에 `pubsub`만**(L83) — pubsub은 stable 객체라 OK이지만 handleOpen은 closure. 재구독 시점 위험은 낮으나 명시 deps 누락.
  - JSX 의미: `<dl>` 안의 자식이 `<dd>`만 두고 `<dt>` 누락(L99-107) → semantic 오류.
- **근거**:
  - L34-51 재귀 트리 검색 함수 inline.
  - L99-107 `<dl><div><div>...</div><dd>...</dd></div></dl>` — `<dt>` 빠짐.
- **개선 방법**:
  1. 단건 API `getDaoDiscussionComment(commentId)` 도입(NEW-H) + 자식 모달은 `commentId`만 받음. 부모 rows 의존 제거.
  2. BL-9: pubsub callback payload → Promise modal API. `Dialog.openCommentDetail({ commentId })` → resolve.
  3. selectedComment null 시 명시적 empty/error UI.
  4. `<dl>` semantic 정리.
- **우선순위**: P1
- **연계**: BL-9, NEW-H.

---

### `discuss-posts-management/detail/commend/detail/_id.modal.css` (183 lines)

- **요약**: 댓글 단건 모달 스타일.
- **문제**: 컬러 하드코딩 / `dcdm-*` BEM 일관 (양호). status 셀렉터에 영문 사용 가정 — 실제 컴포넌트가 `<StatusBadge>`를 쓰므로 부모 측 한국어 셀렉터 영향은 받지 않음(검증 필요).
- **개선 방법**: NEW-B 토큰화 합류.
- **우선순위**: P2

---

## 2. 도메인 공통 안티패턴

1. **try/finally setIsLoading**: `_id.modal.tsx` 2곳 + `proposalPostDetailCommentWidget.tsx` 1곳. F-03/BL-6에 직접 매칭. 본 도메인은 패턴 표준화의 대표 케이스로 활용 가능.
2. **enum FILTER_TYPES dead member**: `index.tsx`의 SORT/KEYWORD 미사용 — code-review 미스 신호.
3. **거대 columns 인라인**: list/widget 양쪽 모두 80~96줄 columns 정의를 컴포넌트 본문에 둠. column builder 추출 SKILL 필요.
4. **모달-pubsub 결합 + payload에 함수/배열 동봉**: `commend/detail/_id.modal.tsx` 결합도 최고. BL-9(Promise modal) PoC 후보 1순위.
5. **i18n 키 임시 재사용**: `_dao_proposal_forceEndVote_reason_*`를 게시글 숨김에 차용. F-01 직결.
6. **CSS 책임 침범**: `detail/_id.modal.css`(부모)가 댓글 위젯 스타일까지 정의 + 위젯 css와 클래스 중복. 클래스 충돌 가능.
7. **CSS i18n 데이터 속성 한국어**: `[data-status="게시중"]` 등 — 다국어 빌드에서 무력화. NEW-E.
8. **sentinel(-1) 초기값**: `_initState` 전역 분산. nullable로 통일 필요.
9. **상태 매핑 함수 if-사슬**: `config/discussion-status-label-key.ts` — Record로 단순화 가능.
10. **단건 API 부재**: 댓글 단건 모달이 부모 list memory에 의존 → race + 결합. NEW-H.
11. **폴더 명명 오타**: `commend/` (`comment` 의도). 도메인 용어 위반.
12. **pubsub 토픽 mismatch**: 댓글 삭제 → `"refresh-dao-proposals-discussion-posts"` (부모 구독은 `"-list"` 접미사). 잠재 버그.

---

## 3. 백로그 매핑 / 신규 항목

| 항목 | 매칭 백로그 | 비고 |
|---|---|---|
| `_id.modal.tsx`의 try/finally 3곳 | F-03, BL-6 | F-03이 1차로 명시 |
| moderation i18n 키 | F-01 | placeholder 새 키 도입 필요 |
| useSearchParamsState로 list 단순화 | BL-1 | dao/dao-logs PoC 완료 후 본 도메인 적용 |
| useReasonPrompt 합성 | (이미 적용) | usePostModeration hook으로 한 단계 더 추출 |
| pubsub modal Promise 전환 | BL-9 | 댓글 모달이 PoC 1순위 |
| commend/ 오타 rename | (신규) | NEW-F |
| flatten/group 순수 함수 추출 | (신규) | NEW-G |
| 단건 댓글 API + 자식 모달 결합 해소 | (신규) | NEW-H |
| 컬럼 빌더 추출 표준 | (신규) | NEW-A |
| DAO 컬러 토큰화 | (신규) | NEW-B |
| status mapping Record 화 | (신규) | NEW-C |
| moderation/detail hook 3분할 표준 | (신규) | NEW-D |
| CSS data-status 한국어 셀렉터 | (신규) | NEW-E |
| CSS 책임 경계(부모/위젯) 정리 | (신규) | NEW-I |

신규 후보 우선순위 추천: NEW-H (P0, 잠재 race) → NEW-F (P0, 즉시 가능) → NEW-D (P0, F-03 흡수) → NEW-A/G (P1) → NEW-C/E (P2) → NEW-B/I (P2).

**즉시 처리 권장 P0 버그/리스크**:
- pubsub 토픽 mismatch (`proposalPostDetailCommentWidget.tsx` L199) — 1줄 수정.
- `handlePostModerationRestore`의 isLoading 누락 (`detail/_id.modal.tsx` L83-92) — UX/일관성.
- F-03 try/finally 일괄 정리 (3곳).
- F-01 i18n 키 분리 (라벨 의미 충돌).

---

## 4. 권장 디렉터리 재구성

### 4-A. FSD 정확 적용본

```
src/
  entities/
    discussion-post/
      model/
        types.ts                     # GetDaoDiscussionPostDetail 등 도메인 타입 re-export
        status.ts                    # POST_STATUS_LABEL_KEY, getDiscussionPostStatusLabelKey
      lib/
        group-rows.ts                # groupDiscussionRowsByProposal (순수)
      ui/
        DiscussRow/
          DiscussRow.tsx
          DiscussRow.css
          theme-color.ts             # getThemeColorKeyByNumericId 이전
    discussion-comment/
      model/
        types.ts
        status.ts                    # COMMENT_STATUS_LABEL_KEY
      lib/
        flatten.ts                   # flattenDiscussionComments
      ui/
        CommentTable/                # 위젯 css + 행 스타일
  features/
    discussion-post-detail/
      model/
        use-post-detail.ts           # { data, isLoading, refetch }
    discussion-post-moderation/
      model/
        use-post-moderation.ts       # { hide(reason), restore() } + useReasonPrompt 흡수
        use-post-delete.ts
      ui/
        PostHeaderActions.tsx
    discussion-comment-list/
      model/
        use-comments-search.ts       # searchState + setRequestSearch 합성
        use-comment-delete.ts
      ui/
        CommentSearchBar.tsx
        CommentColumns.tsx           # buildDiscussionCommentColumns
    discussion-comment-detail/
      model/
        use-comment-detail.ts        # 단건 API + Promise modal API
      ui/
        CommentDetailModal.tsx
  pages/
    dao/
      discuss-posts-management/
        index.tsx                    # 표/페이지 레이아웃만 (~80 lines 목표)
        index.css                    # 페이지 그리드만
        detail/
          DiscussPostDetailModal.tsx # SideModal 레이아웃 + features 합성 (~120 lines)
          DiscussPostDetailModal.css
  shared/
    hooks/
      use-search-params-state.ts     # BL-1
      use-reason-prompt/             # 기 존재
    ui/
      modal-promise/                 # BL-9 산출물
```

### 4-B. 점진적 절충본 (현재 폴더 구조 유지하면서 책임만 분리)

```
src/pages/dao/discuss-posts-management/
  index.tsx                          # 컬럼 빌더/그룹핑 함수 분리 후 ~120 lines
  index.css
  config/
    discussion-status-label-key.ts   # Record 변환만 적용
  model/                             # NEW: 도메인 model 폴더
    columns.tsx                      # buildDiscussionPostColumns
    group-rows.ts                    # groupDiscussionRowsByProposal
  hooks/                             # NEW: 페이지 로컬 hook
    use-post-detail.ts
    use-post-moderation.ts
    use-post-delete.ts
  ui/                                # NEW: 페이지 로컬 UI 컴포넌트
    PostHeaderActions.tsx
    PostMetaRow.tsx
    DiscussRow.tsx
  detail/
    _id.modal.tsx                    # 합성만, ~150 lines
    _id.modal.css
    comment/                         # rename: commend → comment
      proposalPostDetailCommentWidget.tsx
      proposalPostDetailCommentWidget.css
      model/
        columns.tsx
        flatten.ts
      hooks/
        use-comments-search.ts
        use-comment-delete.ts
      detail/
        _id.modal.tsx                # 단건 API 적용 + commentId만 수용
        _id.modal.css
```

절충본 권장 순서:
1. F-01/F-03/토픽-mismatch 버그 fix (P0, 1 PR, 1일).
2. NEW-F (commend→comment rename) (P0, 1 PR, 30분).
3. NEW-G (flatten/group 추출) + NEW-A (columns 추출) (P1, 1 PR/도메인).
4. NEW-D (hook 3분할) — `_id.modal.tsx`만 먼저 (P1).
5. NEW-H (단건 댓글 API + 자식 모달 결합 해소) — 백엔드 협의 필요 (P1~P2).
6. NEW-C (status Record), NEW-E (CSS i18n 셀렉터), NEW-B (토큰화) (P2 묶음).
7. FSD 정확 적용본 마이그레이션은 BL-1/BL-9 PoC가 끝난 다음 단계.

---

## 5. 출력 포맷 (evaluator 헤더)

```yaml
summary: discuss-posts-management 도메인 9개 파일 전수 분석 — F-01/F-03/BL-1/BL-9와 강하게 매칭, P0 잠재 버그 2건(pubsub topic mismatch, restore isLoading 누락) 발견, 신규 백로그 9건 식별.
decision: recommendation_ready
diagnosis_report: |
  - index.tsx: dead enum + columns/grouping/모달placement/구독이 한 컴포넌트에 평면 배치
  - detail/_id.modal.tsx: try/finally setIsLoading 안티패턴 + i18n 키 임시 차용 + restore 비대칭 + 모달 오케스트레이션·fetch·mutation 혼재
  - commend/proposalPostDetailCommentWidget.tsx: pubsub 토픽 mismatch 잠재 버그, dead isLoading state, columns 89 lines 인라인, 자식 모달에 rows+onDelete 동봉
  - commend/detail/_id.modal.tsx: 단건 API 부재로 부모 list memory 트리 검색, callback ref 패턴, dl semantic 오류
  - config/discussion-status-label-key.ts: if-사슬, union 중복, FSD 위치 모호
  - CSS 전반: 한국어 data-status 셀렉터(i18n 깨짐), 컬러 토큰 부재, 부모/위젯 CSS 책임 침범
architectural_risks:
  - pubsub 모달 결합으로 props/타입 안전성 상실 (BL-9)
  - try/finally setIsLoading이 도메인 내 3곳, 코드베이스 표준화 누락 시 회귀 (BL-6)
  - 댓글 단건 API 부재 → 부모 캐시 의존 race
  - i18n CSS 셀렉터(한국어)로 다국어 빌드 시 사일런트 깨짐
  - DAO 컬러 토큰 부재로 테마 변경 비용 폭증
  - FSD entities/features 분리 부재로 columns/hook이 page에 종속, 재사용 불가
improvement_options:
  - hook 3분할 표준 도입 (use-post-detail / use-post-moderation / use-post-delete)
  - columns/그룹핑/flatten 순수 함수·빌더 추출 (model/ 신설)
  - status mapping Record 화 + entities/discussion-post/model로 이전
  - 단건 댓글 API 도입으로 자식 모달 결합 해소
  - DAO 컬러 토큰화 + CSS data-status 영문화
  - commend → comment 폴더 rename
  - BL-1 useSearchParamsState 본 도메인 적용
  - BL-9 Promise 모달 PoC 1순위로 댓글 모달 채택
recommended_backlog:
  - P0 BUG-1: pubsub 토픽 mismatch 1줄 수정 (proposalPostDetailCommentWidget.tsx L199)
  - P0 BUG-2: handlePostModerationRestore isLoading 누락 (detail/_id.modal.tsx L83-92)
  - P0 F-03: try/finally setIsLoading 3곳 정리 (본 도메인이 1차 케이스)
  - P0 F-01: moderation i18n 키 분리 + reason 라벨 본 도메인용 키 신설
  - P0 NEW-F: commend → comment 폴더 rename
  - P1 NEW-A: 컬럼 빌더 추출 (columns.tsx)
  - P1 NEW-D: detail 모달 hook 3분할 표준
  - P1 NEW-G: group-rows / flatten 순수 함수 추출
  - P1 NEW-H: 단건 댓글 API + 자식 모달 결합 해소
  - P1 BL-1 적용: useSearchParamsState로 list 페이지 단순화
  - P2 NEW-C: status mapping Record 변환 + entities로 이전
  - P2 NEW-E: CSS data-status 한국어 셀렉터 영문화
  - P2 NEW-B: DAO 컬러 토큰화
  - P2 NEW-I: 부모/위젯 CSS 책임 경계 정리
  - P2 BL-9 PoC: 댓글 모달 Promise API 전환
handoff_to_planner_optional: true
reasons:
  - P0 4건은 단순 수정이지만 잠재 버그 포함 → planner가 1개 세션으로 묶어 즉시 처리 권장
  - NEW-D/A/G/H는 본 도메인 한정 리팩토링 세션으로 묶어 plan 작성 가능
  - BL-1/BL-9는 도메인 횡단이므로 별도 PoC 세션 필요 (현 도메인 적용은 후행)
artifacts:
  - .claude/logs/sessions/2026-05-07-discuss-posts-refactor-evaluation/evaluation-log.md
next_action: planner에게 "P0 4건 fix 세션" + "본 도메인 구조 리팩토링 세션(NEW-A/D/G)" 두 갈래 plan 작성 의뢰
log:
  - 9개 파일 전수 read 완료
  - backlog.md 대조 완료 (F-01/F-03/BL-1/BL-5/BL-6/BL-9 매핑)
  - 신규 NEW-A ~ NEW-I 9건 식별
  - P0 잠재 버그 2건 식별 (BUG-1 토픽 mismatch, BUG-2 restore isLoading 누락)
status: recommendation_ready
```
