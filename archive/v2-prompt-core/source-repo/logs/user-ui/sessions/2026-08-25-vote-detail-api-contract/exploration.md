# 탐색

## 요청

사용자는 투표 상세 조회가 인증 없이 가능하고, 관리자 임시저장은 404이며, 목록과 달리 시작 전·중단된 투표도 조회된다고 확정했다. 응답 `data`는 숫자 `id`, `title`, `agenda`, `status`, `startsAt`/`endsAt`, nullable 찬반 수, `myChoice`, `createdAt`/`updatedAt`이다. 의견 목록은 이 응답에 없고 별도 comments API다. 구현 승인은 `작업 진행`이다.

## 대상 관련 사실

- 기존 `getVoteDetail`은 공용 `ContentDetailDto`와 `useCitizenContentDetailQuery("vote")`를 썼다. 필드가 `body`/`period`/`authorName`/`commentCount`/`myVoteChoice?`였다.
- 확정 아이템은 `agenda`, ISO 기간, `myChoice: AGREE|DISAGREE|null`이며 댓글 수는 없다.
- `VoteDetailPage`는 `state: "ongoing" | "closed"`만 받는다. 시작 전·중단 전용 뱃지 계약은 없다.
- 댓글은 이미 `GET /v1/api/citizen-participation/votes/{id}/comments`로 분리되어 있다.
- 목록 작업에서 `UPCOMING`/`CANCELLED`는 목록 필터 400 값으로 확인됐다. 상세 성공 예시는 `IN_PROGRESS`만 주어졌다.
- `src/shared/ui/`의 StatusBadge, Button, Pagination은 기존 상세 UI가 이미 사용 중이다.

## 불러온 스킬

- `.agents/skills/SKILL.md`
- `policy/harness`, `policy/coding-convention`, `policy/type-definition`, `policy/data-fetch-layer`, `policy/documentation`, `policy/portfolio`, `policy/hook-extraction`
- `recipe/api-authoring`, `recipe/data-dto`, `recipe/data-fetch`
- `reference/SKILL.md`, `reference/custom-hooks`, `reference/components`

## `src/shared/ui/`의 재사용 가능 자산

| 후보 | 결정 | 근거 |
| --- | --- | --- |
| StatusBadge | 재사용 | 기존 상세 뱃지 계약을 유지한다. 새 상태 뱃지는 UI 파일 변경이 필요하다. |
| Button / BottomActionBar | 재사용 | 투표하기 비활성은 기존 `closed`/`hasSubmitted` 계약이다. |
| Table / useFetchAdapter | 제외 | 상세 화면 계약이 아니다. |
| useApi | 제외 | 이미 TanStack Query + `ApiClient` 경로가 있다. |

## 제약 조건 및 미확인 사항

- 시작 전·중단의 정확한 enum 문자열은 이번 JSON 예시에 없다. 이전 목록 계약의 `UPCOMING`/`CANCELLED`를 사용한다.
- `VoteDetailPage`는 예정/중단 전용 상태를 렌더하지 않는다. 이유 문구는 presentation `period`로 넣는다.
- 댓글 경로의 OpenAPI 표기 `/citizen/votes/{voteId}/comments`는 기존 시민참여 prefix와 다르며 이번 범위에서 URL을 바꾸지 않는다.

## 결론

투표 상세는 목록과 같이 전용 DTO가 단일 계약이어야 하고, 목록 필터 enum과 상세 status enum을 나눈다. 댓글은 기존 분리 요청을 유지한다.
