# Evaluation Log

## Context
- 일자: 2026-05-18
- 대상: `src/pages/dao/discuss-posts-management/` 전체 디렉터리
- 위임 에이전트: evaluator (`.claude/agents/evaluator.md`)
- 평가 범위 제외: pubsub 관련 영역
- 인벤토리:
  - `index.tsx`, `index.css`
  - `config/discussion-status-label-key.ts`
  - `utils/groupingSameDiscussRows.ts`
  - `model/tableRows.ts`
  - `ui/column/useDiscussPostTableColumns.tsx`
  - `detail/_id.modal.tsx`, `detail/_id.modal.css`
  - `detail/useDetailModal.ts`
  - `detail/hooks/useDiscussDetailFetch.tsx`
  - `detail/commend/proposalPostDetailCommentWidget.tsx`, `*.css`
  - `detail/commend/utils/mappingDIscussCommentRows.ts`
  - `detail/commend/ui/column/useDiscussPostCommentTableColumns.tsx`
  - `detail/commend/detail/_id.modal.tsx`, `*.css`

## Structural Risks
1. **R1 — Hook 규약 위반(PascalCase)**: `DiscussionPostTableColumns`, `DiscussionPostCommentTableColumns`가 내부에서 `useMemo` / `useLanguage`를 호출하지만 PascalCase로 명명되어 React Hook 호출 위치 제약을 시각적으로 잃음.
2. **R2 — Comment Columns hook의 상위 상태 캡쳐 + deps 누락**: `useDiscussPostCommentTableColumns`가 `postTitle`, `rows`, `handleDelete`를 캡쳐하지만 `useMemo` deps에 `[mui, pubsub]`만 포함 → stale closure로 삭제 핸들러가 옛 `commentId`/`rows`를 참조할 가능성.
3. **R3 — `useDiscussDetailFetch` God-hook**: 단일 hook이 fetch + 4개 도메인 액션 + Dialog + i18n까지 담당. 책임 4개 이상 → 액션 추가 시 변경/테스트 비용 급증.
4. **R4 — Post/Comment 액션 비대칭**: post는 action hook으로 격리됐지만 comment 삭제는 위젯 인라인(`const [_, setIsLoading]` 미사용, 비동기 의미상 무효한 try/catch).
5. **R5 — CommentDetail 모달의 의존 방향 역전**: `DiscussPostCommentDetailModal`이 `rows` 전체를 payload로 받아 자체 트리 탐색(`findComment`). 자식 모달이 부모 자료구조에 결합.
6. **R6 — 모델 소유권 모호**: comment 타입이 상위 `model/tableRows.ts`에 거주, 자식이 `../../`로 역참조.
7. **R7 — Status→label key 분기 복제**: `getDiscussionPostStatusLabelKey`/`Comment`가 동일 분기 구조를 두 함수에 복제.
8. **R8 — `useDetailModal` 선제 추상화 의심**: 단일 호출처에서 사용되는 4줄 disclosure hook. 추상화 4조건 미충족.
9. **R9 — 네이밍/오타**: 폴더 `commend` (→ `comment` 오타), 파일 `mappingDIscussCommentRows.ts` (CamelCase 위반).
10. **R10 — Display row 누수**: `DaoDiscussionCommentDisplayRow.childComments`가 평탄화 후에도 도메인 트리를 끌고 다님.

## Why This Matters
- R2/R5는 잠재 결함성(stale closure, 부모-자식 자료구조 결합) — 사용자 시나리오에서 삭제·재진입 시 오작동/캐시 깨짐 위험이 실재.
- R3/R4는 도메인 액션 확장(승급/이동/신고처리 등) 시 hook 폭증과 post/comment 비대칭으로 인한 규약 분기 비용 누적.
- R6/R9는 단기 통증은 적지만 디렉터리 이동·검색 비용에 누적 → FSD-style page-local 자기-완결성 훼손.
- R7/R10은 closed vocabulary 확장 시 누락 위험 및 표시-도메인 책임 경계 흐려짐.
- R1/R8은 컨벤션 일관성/YAGNI 항목 — 한 곳에서 어긋나면 다른 페이지로 전염되는 패턴.

## Improvement Options
1. **Option A — 도메인 분리 정리**: `model/tableRows.ts` 분할(`model/postRows.ts`, `detail/commend/model/commentRows.ts`), `commend/` → `comment/`, mapping 파일명 정상화. (R6/R9)
2. **Option B — Columns hook 규약 정상화**: 함수명 `use*`로 변경, `useDiscussPostCommentTableColumns`의 deps 전부 포함 또는 action을 row-단위 prop 콜백으로 위임해 캡쳐 범위 축소. (R1/R2)
3. **Option C — Detail/Action hook 책임 분리**: `useDiscussPostDetailQuery`(조회/리셋) + `useDiscussPostActions`(moderation/delete), 댓글도 `useDiscussCommentActions`로 격리. (R3/R4)
4. **Option D — CommentDetail 의존 방향 역전 해소**:
   - D1. 상세 API 존재 시 모달이 `commentId`만 받고 자체 fetch.
   - D2. 미존재 시 평탄화된 단일 객체만 payload로 전달, 모달의 트리 탐색 제거(선호). (R5)
5. **Option E — Status→label 매핑 통합(약한 추상화)**: `getDiscussionStatusLabelKey(status, kind)` 단일 함수 + 도메인별 반환 타입 유지. (R7)
6. **Option F — Display row 누수 제거**: `childComments` 제거, 트리 필요 시 별도 `commentIndex: Map<id, Row>`로 분리(D2와 결합). (R10)
7. **Option G — `useDetailModal` 결정**: 단일 호출처면 인라인 `useState`, 5+ 회 반복 시 `useDisclosure` 승급. (R8)

## Recommended Backlog
| 우선순위 | 항목 | 적용 옵션 | 근거 |
|---|---|---|---|
| P0 | Comment Columns hook deps 누락 / 상위 상태 캡쳐 수정 | B | stale closure 결함성 |
| P0 | CommentDetail 모달의 rows-payload 의존 역전 해소 | D2 + F | 부모-자식 결합 해소, 재진입 안정성 |
| P1 | `useDiscussDetailFetch` 책임 분리(query / actions) | C | 액션 확장성 |
| P1 | Comment 삭제 액션 hook 격리(위젯 인라인 제거) | C | post/comment 패턴 통일 |
| P2 | 도메인 모델 파일 분리 + 폴더/파일 리네이밍 | A | 소유권/검색성 |
| P2 | Columns 함수 → `use*` 규약 정상화 | B | Hook 규약 일관성 |
| P3 | Status→label 매핑 통합 함수 | E | 어휘 확장 시 누락 방지 |
| P3 | `useDetailModal` 인라인화 또는 공용화 결정 | G | YAGNI vs 일관성 |

## Suggested Next Step
- **P0 두 건(R2, R5)**: planner → refactorer 흐름으로 즉시 진행 권장.
- **P1~P2**: 한 세션의 리팩터 plan으로 묶어 처리.
- **P3**: `.claude/logs/backlog.md`에 적재.
- **선결 질의(역질문)**:
  1. Comment 상세 API 존재 여부 (Option D1 vs D2 분기).
  2. `useDetailModal` 패턴이 타 페이지에 반복되는지 (Option G 분기).
  3. `commend/` 폴더명이 오타인지 의도된 약어인지.
  4. Status label key union 확장 계획 유무 (Option E 우선순위 상향 여부).
