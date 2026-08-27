# Evaluation Log

## Context
- 일자: 2026-05-20
- 대상: `src/pages/dao/discuss-posts-management/` 전체
- 위임 에이전트: evaluator (`.claude/agents/evaluator.md`)
- 적용 정책: `.claude/skills/policy/abstraction-strategy/SKILL.md`, `.claude/skills/policy/refactoring/SKILL.md`
- 평가 범위 제외: pubsub 관련 영역(언급/진단 제외)
- 평가 방식: 이전(2026-05-18) 평가 결과를 참조하지 않고 현재 코드 상태를 재독.

## Inventory (현재 상태)
- `index.tsx` (138 LOC) — 페이지 컨테이너
- `index.css` (216 LOC)
- `config/discussion-status-label-key.ts` — status → i18n key 매퍼 2종
- `model/tableRows.ts` — Post/Comment row 타입(평탄/표시)
- `model/tableRowMappers.ts` — DTO → row 매퍼 2종
- `utils/groupingSameDiscussRows.ts` — proposalId 그룹 헤더 부여
- `ui/column/useDiscussPostTableColumns.tsx` — 게시글 테이블 컬럼 hook
- `hooks/` — 빈 디렉터리
- `detail/_id.modal.tsx` (139 LOC) — 게시글 상세 SideModal
- `detail/_id.modal.css` (605 LOC)
- `detail/hooks/useDiscussDetailFetch.tsx` — 상세 조회 + 모더레이션/삭제 액션 통합 hook
- `detail/commend/proposalPostDetailCommentWidget.tsx` (142 LOC)
- `detail/commend/proposalPostDetailCommentWidget.css` (111 LOC)
- `detail/commend/utils/mappingDiscussCommentRows.ts` — 1-depth 평탄화
- `detail/commend/ui/column/useDiscussPostCommentTableColumns.tsx`
- `detail/commend/hooks/useDiscussionCommentDelete.tsx` — 댓글 삭제 hook
- `detail/commend/detail/_id.modal.tsx` (146 LOC)
- `detail/commend/detail/_id.modal.css` (183 LOC)

## 추상화 비용/목적 진단
- 약한 추상화 위주 구조. `model/config/utils/hooks/ui` 슬라이스 분리가 명확.
- 목적 뚜렷성: 컬럼 hook·매퍼·그룹핑 유틸은 호출처 1곳이지만 단일 책임이 명확해 ROI 인정 (policy-abstraction-strategy §2-4 통과).
- 과추상화 의심:
  1. `mapDaoDiscussionCommentTableRow`는 사실상 identity. 추상화 4조건 미충족(YAGNI).
  2. `model/tableRowMappers.ts`에 Post/Comment 매퍼가 공존하나, Comment 매퍼/모델은 `detail/commend/` 소유가 자연스러움(스코프 누설).
- 부족 추상화:
  1. `getDiscussionPostStatusLabelKey`와 `getDiscussionCommentStatusLabelKey`가 동일 분기 구조를 복제(키 한 자리만 다름).
  2. Post는 fetch+actions가 단일 hook, Comment는 fetch는 위젯·delete만 hook → 비대칭.

## 아키텍처 진단 (FSD 관점)
- 페이지-로컬 자기-완결형 구조(준-FSD). 컨벤션 대체로 준수.
- 양호한 패턴:
  - Container/Presenter 분리 (`index.tsx` ↔ `ui/column` ↔ `utils`).
  - Adapter 패턴 (`useFetchAdapter`).
  - 약한 추상화 helper hook (`useDiscussionCommentDelete`).
- 어긋남:
  1. 폴더 오타 `commend` → 의미상 `comment`.
  2. Comment 도메인 타입이 페이지 루트 `model/`에 거주, `detail/commend`에서 `../../`로 역참조.
  3. 빈 `hooks/` — 죽은 구조.
  4. `detail/_id.modal.css`(605 LOC) 비대화.

## 의존관계 추적/책임 분리 평가
- 흐름:
  - `index.tsx` → `useDaoKeywordSortQueryState`, `useFetchAdapter`, `useDiscussionPostTableColumns`, `groupingSameDiscussRows`, `DiscussPostsManagementDetailModal`
  - `DiscussPostsManagementDetailModal` → `useModal`, `useDiscussDetailFetch`, `ProposalPostDetailCommentsWidget`, `useReasonPrompt`
  - `ProposalPostDetailCommentsWidget` → `useDaoKeywordSortQueryState`, `useFetchAdapter`, `useDiscussionPostCommentTableColumns`, `mappingDiscussCommentRows`, `useDiscussionCommentDelete`, `DiscussPostCommentDetailModal`
  - `DiscussPostCommentDetailModal` ← payload `{commentId, postTitle, rows, onDelete}` ← 위젯
- 타당:
  - 컬럼 hook → 페이지 모델/config 단방향, 응집도 양호.
  - `useDiscussionCommentDelete`는 콜백 주입으로 위젯과 약한 결합.
- 의심:
  1. `useDiscussionCommentDelete`가 `setIsLoading`을 외부에서 주입받음 → hook이 외부 loading state 직접 제어, 캡슐화 누수.
  2. 위젯의 `onSuccess: refetch` 콜백과 hook 내부의 별도 refresh 트리거가 **두 경로 동시 존재** → 부수효과 중복(메커니즘 자체는 평가 제외 영역이라 사실관계만 진단).
  3. `DiscussPostCommentDetailModal`이 `rows` 트리 + `findComment` 재귀 → 자식 모달이 부모 자료구조에 결합(의존 역전).
  4. `useDiscussDetailFetch`가 fetch + 3액션 + Dialog + i18n 결합(God-hook).
  5. `handleOpenCommentDetail` deps에 `rows`가 들어가 매 fetch마다 콜백/컬럼 재생성.

## 기술 부채 표
| ID | 항목 | 카테고리 | 심각도 | 근거 |
|---|---|---|---|---|
| D1 | `commend/` 폴더 오타 | 네이밍/검색성 | 중 | FSD-segment 이름 오용 |
| D2 | Comment 모델/매퍼가 페이지 루트 `model/` 소유 | 경계 누설 | 중 | `detail/commend`만 사용 |
| D3 | identity 매퍼(`mapDaoDiscussionCommentTableRow`) | YAGNI | 낮 | 호출처1·구현0 |
| D4 | `useDiscussDetailFetch` God-hook | 책임 분리 | 중 | 4책임 결합 |
| D5 | CommentDetail이 `rows` 트리 의존 | 의존 역전 | 높 | 자식이 부모 자료구조 재귀 탐색 |
| D6 | Comment 삭제 hook이 외부 `setIsLoading` 수신 | 캡슐화 누수 | 중 | hook 자기 책임으로 흡수 권장 |
| D7 | refetch 경로 이중 트리거(콜백+이벤트) | 부수효과 중복 | 중 | 동일 효과 2경로 |
| D8 | Status→label 분기 함수 2개 중복 | 약한 추상화 부족 | 낮 | 단일 함수+scope로 통합 가능 |
| D9 | 빈 `hooks/` 디렉터리 | 죽은 구조 | 낮 | 의도 불명 |
| D10 | CSS 비대화(`detail/_id.modal.css` 605 LOC 등) | UI 응집 | 중 | 슬라이스 분할 여지 |
| D11 | `DaoDiscussionCommentDisplayRow.childComments` 보존 | 표시-도메인 누수 | 중 | 평탄화 후 트리 동반 |
| D12 | 컬럼 콜백 deps에 `rows` 포함 | 렌더 비용 | 낮 | 매 fetch마다 columns 재생성 |

## Improvement Options
- **A. CommentDetail 의존 역전 해소(D5/D11)**: A1 `commentId`만 받고 자체 fetch / A2 평탄 1건만 payload + `childComments` 제거, 필요 시 `Map<id, Row>` 인덱스.
- **B. Detail hook 책임 분리(D4)**: `useDiscussPostDetailQuery` + `useDiscussPostActions`.
- **C. Comment 삭제 hook 캡슐화(D6)**: hook 자체 `isPending` 노출, 외부 `setIsLoading` 제거.
- **D. Refetch 단일 경로(D7)**: 콜백/이벤트 중 하나 선정.
- **E. 도메인 경계 재정렬(D1/D2)**: `commend`→`comment`, comment 모델·매퍼 `detail/comment/model/`로 이동.
- **F. Status 매핑 약한 통합(D8)**: `getDiscussionStatusLabelKey(status, scope)` 단일 함수, scope별 반환 union 유지.
- **G. Identity 매퍼 제거(D3)**.
- **H. CSS 슬라이스 분할(D10)**: `dao-post-card`, `dao-comments-card`, `dao-proposal-banner` 등 블록 단위 분리.
- **I. 빈 `hooks/` 정리(D9)**.
- **J. 컬럼 콜백 deps 안정화(D12)**: A2 적용 시 자연 해소.

## Recommended Backlog
| 우선순위 | 항목 | 옵션 | 근거 |
|---|---|---|---|
| P0 | CommentDetail 의존 역전 + DisplayRow 누수 제거 | A2 (+J 동반) | 자식이 부모 자료구조 재귀 탐색 — 재진입/캐시 무결성 위험 최상위 |
| P0 | refetch 이중 트리거 단일화 | D | 부수효과 2경로(레이스/멱등성 위험) |
| P1 | useDiscussDetailFetch 책임 분리 | B | 액션 확장 비용 |
| P1 | Comment 삭제 hook 캡슐화 | C | 캡슐화 누수, post/comment 패턴 통일 |
| P2 | 폴더/모델 소유권 재정렬 | E | FSD 경계, 검색성 |
| P2 | Status 매핑 약한 통합 | F | closed vocabulary 누락 방지 |
| P3 | identity 매퍼 제거 / 빈 hooks 정리 | G + I | YAGNI/죽은 구조 |
| P3 | CSS 슬라이스 분할 | H | 장기 유지보수 |

## Architectural Risks (요약)
- R1 부모-자식 의존 역전(D5/D11)
- R2 부수효과 이중 트리거(D7)
- R3 God-hook(D4)
- R4 캡슐화 누수(D6)
- R5 도메인 경계 누설(D1/D2)
- R6 closed vocabulary 분기 복제(D8)
- R7 죽은 구조/YAGNI(D3/D9)
- R8 UI 응집 비대화(D10)

## 이전 평가(2026-05-18) 대비 변화
- 해결됨:
  - Comment 삭제 액션이 `detail/commend/hooks/useDiscussionCommentDelete.tsx`로 분리(이전 R4 해소, 단 캡슐화 누수 D6는 잔존).
  - 컬럼 hook이 `use*` 규약 충족(이전 R1 해소).
  - 댓글 컬럼 hook deps가 `[mui, onDelete, onOpenDetail]`로 정정 → stale closure 핵심 결함성 해소(이전 R2).
  - `detail/useDetailModal.ts` 제거되고 공용 `~/hooks/use-modal/useModal`로 대체(이전 R8 해소).
  - 매퍼 파일명 오타(`mappingDIscussCommentRows.ts`) 정정(이전 R9 일부 해소).
- 잔존:
  - `useDiscussDetailFetch` God-hook (R3 → D4).
  - CommentDetail 모달 `rows` 트리 의존 + 재귀 탐색 (R5 → D5, 최우선 잔여 결함성).
  - Comment 모델이 페이지 루트 `model/` 소유 (R6 → D2).
  - Status→label 분기 함수 중복 (R7 → D8).
  - `DaoDiscussionCommentDisplayRow.childComments` 누수 (R10 → D11).
  - `commend` 폴더 오타 (R9 잔여 → D1).
- 신규:
  - `useDiscussionCommentDelete`가 외부 `setIsLoading`을 주입받음 — 캡슐화 누수(D6).
  - refetch 이중 트리거 경로(D7).
  - 빈 `hooks/` 디렉터리(D9) — 분할 잔재 추정.
  - identity 매퍼 가시화(D3).
  - 컬럼 콜백 deps에 `rows` 포함(D12) — D5 해결 시 자연 소멸.

## 역질문 (사용자 확인 필요)
1. 댓글 상세 전용 API가 백엔드에 존재합니까? (A1 vs A2)
2. refetch 이중 트리거 중 의도된 단일 경로는 어디입니까? (D 방향)
3. `commend` 폴더는 오타입니까, 의도된 약어입니까? (E 적용 여부)
4. `useDiscussDetailFetch`에 추가될 액션이 더 있습니까? (B 우선순위)
5. 빈 `hooks/`는 향후 사용 계획이 있습니까? (I 처리 방향)
6. Status union 확장 계획이 있습니까? (F 우선순위)

## Decision
- 상태: recommendation_ready
- 다음 단계: P0 2건(A2, D)을 planner로 이관해 단일 리팩터 plan으로 묶고, P1은 후속 단계로 편성. P2~P3는 backlog 적재.
- 직접 구현 금지(evaluator 범위 준수).
