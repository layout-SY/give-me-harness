# 구현 로그

## 승인된 범위

투표 목록 요청/응답 DTO를 확정 구조로 추가하고, `page`/`size`를 항상 보내며 `status`/`sort`는 있을 때만 전송한다. 목록 훅·매퍼·MSW·상세 제출 가드를 `IN_PROGRESS`/`CLOSED`에 맞춘다. `VoteListPage` 마크업과 내 활동 activity 응답은 바꾸지 않는다.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `src/features/citizen-participation/model/constants.ts` | `VOTE_STATUS` `{ IN_PROGRESS, CLOSED }` 추가 | 투표 status가 참여형 `scheduled`/`open`/`closed`와 분리됨 |
| `src/features/citizen-participation/api/vote/vote.dto.ts` | 목록 query/item/response 타입과 Zod schema | 확정 JSON과 같은 목록 계약. 타입은 `z.infer`가 아님 |
| `src/features/citizen-participation/api/vote/vote.api.ts` | `URLSearchParams`로 `status`/`sort` 반복 키 전송 | Axios `status[]` 직렬화를 피함 |
| `src/features/citizen-participation/api/http/citizenParticipation.parser.ts` | `parseVoteList` 추가 | 알 수 없는 목록 값을 좁힘 |
| `src/features/citizen-participation/hook/useCitizenParticipationQueries.ts` | `useVoteListQuery` 분리, vote를 공용 list에서 제외 | 목록과 내 활동이 다른 query를 사용 |
| `src/pages/citizen-participation/model/presentation.ts` | `toVoteListItem` / `toVoteListItemFromContent` | 목록 DTO와 activity content DTO를 각각 매핑 |
| `src/pages/citizen-participation/ui/CitizenListRoutes.tsx` | `VoteListRoute`가 전용 훅 사용 | 첫 화면은 `{ page, size }`만 전달 |
| `src/pages/citizen-participation/ui/CitizenParticipationDetailRoutes.tsx` | 제출 가드를 `VOTE_STATUS.IN_PROGRESS`로 변경 | 진행 중이 아니면 투표 제출하지 않음 |
| `src/features/citizen-participation/mocks/fixtures.ts` / `handlers.ts` | 숫자 id, SUCCESS envelope, status OR 필터 | 로컬이 확정 계약을 재현 |
| `src/features/citizen-participation/index.ts` | 훅·parser·`VOTE_STATUS`·DTO 타입 export | barrel이 새 계약을 노출 |

## 결정 사항

- 새 목록 DTO를 다시 `ContentListResponseDto`로 되돌리지 않았다.
- 내 활동 토글은 `useMyActivityQuery("vote")`와 `toVoteListItemFromContent`를 유지했다.
- `useVoteListQuery`의 queryKey는 새 `voteList()` 팩토리 대신 `lists(VOTE)` + 명시 객체다. 이전 작업에서 새 key 팩토리가 IDE에서 unresolved로 보였다.
- 진행 중 투표 fixture는 `agreeCount`/`disagreeCount`를 `null`로 둔다. 상세 테스트 기대값을 이에 맞췄다.
- `toVoteListItemFromContent`의 optional 필드는 `exactOptionalPropertyTypes` 때문에 조건 spread로 넣었다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| `npx vitest run src/features/citizen-participation src/pages/citizen-participation` | 12 files / 61 tests passed |
| `npm run lint && npm run build` | exit 0. `tsc -b && vite build` 성공 |
| `npx tsc -p tsconfig.app.json --noEmit` | 구현 중 exit 0 |

구현 중 수정한 실패:

- Axios가 배열을 `status[]`로 보내 `getAll("status")`가 비었다 → `URLSearchParams.append`로 변경
- `author: string | undefined`를 optional prop에 넣어 tsc가 실패 → 조건 spread
- 진행 중 상세 테스트가 `agreeCount: 72`를 기대 → fixture와 기대를 `IN_PROGRESS` + `commentCount`로 맞춤

샌드박스에서 `handlers.test.ts` 14건이 `Invalid URL`로 실패한 실행은 있었고, `required_permissions: all`로 다시 돌리면 통과했다. 계약 결함으로 보지 않는다.

## Watcher 인계

현재 변경은 투표 목록 요청/응답 계약과 목록 사용처 연결이다. UI 시각 QA는 수행하지 않았고, 검증은 테스트·build·lint다. `VoteListPage` 마크업은 변경하지 않았다.
