# 탐색

## 요청

시민 투표 댓글 조회 API의 요청·응답 DTO에 맞춰 관련 도메인을 수정한다.

## 대상 관련 사실

- 기존 `comment.dto.ts`는 `string id`, 필수 `likeCount/liked`, `pageSize/itemCount/pageCount`를 사용했다.
- 신규 vote 댓글 응답은 `number id`, `authorName/content/createdAt`, `total/page/size`만 제공한다.
- 기존 `useCitizenCommentsQuery`는 모든 콘텐츠를 `commentClient.getCommentList`로 조회했다.
- `CommentList`의 좋아요 필드는 이미 선택형 UI 계약이므로 정보가 없으면 제어를 렌더링하지 않는다.
- query key는 기존에 page만 포함해 size·sort가 다른 요청 사이의 충돌 가능성이 있었다.

## 불러온 스킬

- `skill-index`, `policy-index`, `recipe-index`, `reference-index`
- `reference-components`, `reference-custom-hooks`
- `recipe-api-authoring`, `recipe-data-dto`
- `policy-coding-convention`, `policy-type-definition`, `policy-data-fetch-layer`
- `policy-documentation`, `policy-harness`, `policy-portfolio`, `policy-review-checklist`
- `programming`, `git-master`
- 중앙 `policy-git-branch-strategy`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| `src/shared/ui/pagination/` | 제외 | 기존 상세 route가 댓글 페이지 UI를 노출하지 않아 API·도메인 수정만 필요하다. |
| 기존 citizen `CommentList` | 재사용 | `likeCount/liked`가 선택형이므로 vote 댓글의 필드 부재를 표현할 수 있다. |
| 신규 공용 UI | 제외 | 화면 구조 변경 요구가 없고 Claude Code 소유 production UI를 수정할 필요가 없다. |

## 제약 조건 및 미확인 사항

- 실제 backend 인증 환경은 제공되지 않아 Axios 표면은 MSW로 검증했다.
- TypeScript LSP server가 설치되지 않아 `lsp_diagnostics`는 실행 불가 상태를 반환했다.
- `bun`이 없어 programming 스킬의 no-excuse 전용 스크립트를 실행하지 못했다. `npm run lint`와 `npm run build`로 대체 검증했다.
- 현재 `sy-main`은 선행 `AGENTS.md`, `package.json` 변경이 있는 dirty worktree였다.

## 결론

vote 전용 transport DTO·API를 추가하고 parser에서 기존 댓글 화면 모델로 정규화하는 방식이 기존 UI와 다른 콘텐츠 댓글 계약을 보존하는 최소 변경이다.

## 추가 탐색 — 제안 목록이 표시되지 않는 문제

### 확인한 데이터 흐름

`Axios → ApiResult → unwrapApiResult → parseProposalList → React Query data → toProposalListItem → ProposalListPage` 순서로 추적했다.

### 비교한 가설

1. 실제 응답 shape가 Zod 목록 스키마와 달라 query가 error 상태가 된다.
2. `REJECTED` 상태가 presentation에서 제외되어 모든 항목이 사라진다.
3. `mine` 또는 page route state 때문에 서버가 빈 목록을 반환한다.
4. query error가 UI에서 정상 빈 결과로 은닉된다.

### 확정 원인

- 목록 스키마는 `author` 객체를 필수로 요구했지만 실제 응답의 `REJECTED` 항목은 `author: null`이었다.
- 목록 전체를 한 번에 parse하므로 한 항목의 nullable 작성자가 모든 항목을 무효화했다.
- 인라인 대조 실행에서 non-null 작성자만 있으면 성공했고, nullable 작성자를 섞으면 `items[1].author`, `expected object`로 실패했다.
- query error를 목록 route가 빈 배열로 대체하므로 사용자는 오류 대신 결과 없음 상태를 보게 된다.

### 최소 수정 결정

production UI는 수정하지 않고 API 경계의 nullable 계약과 presentation fallback만 고친다. 오류와 정상 빈 결과를 분리하는 UI 개선은 별도 production UI 작업으로 남긴다.
