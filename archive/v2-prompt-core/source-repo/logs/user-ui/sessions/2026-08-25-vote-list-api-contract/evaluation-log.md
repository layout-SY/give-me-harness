# 평가 로그

## 현재 판정과의 경계

여기서는 Watcher 판정을 다시 평가하지 않는다.

## 장기 관찰 사항

- 투표 상세가 목록과 같은 `startsAt`/`endsAt`·nullable 찬반 수를 받게 되면 `ContentDetailDto`와 fixture를 한 번에 맞춰야 한다. 지금은 목록만 새 계약이다.
- `/me/activity?content=vote` 응답이 목록과 같은 `{ items, total, page, size }`가 되면 `toVoteListItemFromContent` 경로를 목록 parser로 합칠 수 있다.
- 목록 page size는 클라이언트 10, OpenAPI 기본 20이다. 필터 UI가 생기면 size 기본값도 같이 확정하는 편이 낫다.
- MSW 목록 `startsAt`/`endsAt`이 `createdAt` 복사인 상태는 상세에 기간 필드가 없을 때의 임시값이다.

## 목록에 등록할 재사용 가능 자산

없음. 새 공용 UI/훅을 추가하지 않았다. `useVoteListQuery`는 투표 목록 전용이다.

## 기술 부채

- 투표 내 활동은 여전히 옛 content list DTO다. 목록과 토글 경로의 아이템 형태가 다르다.
- `useVoteListQuery` queryKey는 `lists(VOTE)`에 객체를 붙인 인라인이다. proposal의 `list()` 팩토리와 모양이 다르다.
- 전체 vitest의 시민참여 밖 실패는 이번 실행에서 다시 돌리지 않았다.

## 프로세스 개선 사항

배열 query(`status`, `sort`)는 Axios 기본 직렬화가 서버 `getAll`과 어긋날 수 있다. 확정 OpenAPI가 repeated key를 요구하면 처음부터 `URLSearchParams`를 계획에 적는 편이 재작업을 줄인다.

## 권고 사항

투표 내 활동과 상세 envelope가 확정되면 목록 매퍼의 이중 경로(`toVoteListItem` / `toVoteListItemFromContent`)와 상세 status 분기를 같은 DTO로 맞출 수 있다.
