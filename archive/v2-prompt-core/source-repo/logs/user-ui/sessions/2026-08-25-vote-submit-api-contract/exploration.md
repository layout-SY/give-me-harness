# 탐색

## 요청

사용자는 투표하기 POST를 연결하라고 했다. 진행 중인 투표만 참여 가능하고 1인 1표이며, 불가 시 409 코드가 `ALREADY_VOTED`·`VOTE_NOT_STARTED`·`VOTE_CLOSED`·`VOTE_CANCELLED`로 갈린다. 요청 body는 `{ "choice": "AGREE" }`다.

## 대상 관련 사실

- `postVote`는 이미 `POST /v1/api/citizen-participation/votes/{voteId}/responses`와 `{ choice }` 및 `authRequired`를 쓴다.
- 성공 응답은 `{ id: string, completed, choice }`였고, 이번 요청에 200 JSON은 없다.
- MSW는 재투표만 `ALREADY_VOTED` 409였고, 종료·시작 전·중단 POST는 막지 않았다.
- `toServerResponse`가 `code`를 `toNumber`로 바꿔 문자열 409가 사라졌다.
- `VoteDetailRoute`는 `IN_PROGRESS`일 때만 mutate한다. `VoteDetailPage`에는 409 메시지 props가 없다.
- `src/shared/ui/`의 Button은 기존 투표하기 버튼이다.

## 불러온 스킬

- `.agents/skills/SKILL.md`
- `policy/harness`, `policy/coding-convention`, `policy/type-definition`, `policy/data-fetch-layer`, `policy/documentation`, `policy/portfolio`
- `recipe/api-authoring`, `recipe/data-dto`, `recipe/data-fetch`
- `reference/SKILL.md`, `reference/components`, `reference/custom-hooks`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| Button | 재사용 | 기존 투표하기 버튼 계약 유지 |
| Dialog | 제외 | 409 UI를 `VoteDetailPage`에 추가하지 않음 |

## 제약 조건 및 미확인 사항

- 200 `data` 형태는 미확정. 기존 submit 응답을 유지한다.
- POST URL의 `/responses` 여부는 이번 스펙에 path `voteId`만 있어 바꾸지 않는다.

## 결론

요청은 `{ choice }`만 보내고, 409는 투표 status·재투표로 가른다. 성공 응답은 확정될 때까지 기존 형태를 유지한다.
