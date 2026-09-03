# 탐색

## 요청

사용자는 제안 목록의 「내 활동 보기」버튼에서 말한 activity API를 요청하고 응답을 받아 표출하는 흐름까지 구현하라고 했다.

## 대상 관련 사실

- 토글 라벨은 `MyActivityToggle`의 `내 활동 보기`다. 메인 화면에도 같은 문구 버튼이 있으나 내 활동 페이지로 이동만 한다.
- 이전 작업에서 토글 on 시 `useMyActivityQuery`가 `/me/activity`를 쳤지만 응답은 옛 `ActivityListResponseDto`(`pageSize`/`authorName`/`summary`)로 파싱했다.
- 확정된 표출 가능한 목록 응답은 `{ items: [{ id, title, status, author.nickname, createdAt }], total, page, size }`다.
- `src/shared/ui/` Pagination, StatusBadge, NoResults는 기존 `ProposalListPage`가 이미 사용한다.

## 불러온 스킬

- policy/harness, coding-convention, data-fetch-layer, documentation, portfolio
- recipe/data-fetch, recipe-api-authoring

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| Pagination / StatusBadge / NoResults | 재사용 | 기존 제안 목록 카드 UI를 그대로 쓴다. |
| 새 목록 컴포넌트 | 제외 | 같은 페이지에 같은 카드로 그리면 된다. |

## 제약 조건 및 미확인 사항

- `/me/activity` 응답 스키마는 사용자가 따로 주지 않았다. 같은 목록 화면에 그리는 확정 proposal list 응답을 사용했다.
- vote 등 다른 타입 토글 응답은 이번에 바꾸지 않았다.

## 결론

`content=proposal` activity 응답을 `parseProposalList`로 읽고 `ProposalListPage`에 넣는다. 메인 「내 활동 보기」는 기존 내 활동 페이지 흐름을 유지하되, 제안 필터만 같은 목록 DTO를 쓰게 한다.
