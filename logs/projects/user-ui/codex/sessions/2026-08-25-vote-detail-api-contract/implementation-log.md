# 구현 로그

## 승인된 범위

투표 상세 응답 DTO를 확정 구조로 추가하고, 인증 없는 조회·임시저장 404·`myChoice` null·CLOSED만 찬반 수·재투표 409를 맞춘다. `VoteListPage`/`VoteDetailPage` 마크업은 바꾸지 않는다.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `src/features/citizen-participation/model/constants.ts` | `VOTE_STATUS`에 `UPCOMING`/`CANCELLED`, `VOTE_LIST_STATUS` 추가 | 목록 필터와 상세 status가 분리됨 |
| `src/features/citizen-participation/api/vote/vote.dto.ts` | `GetVoteDetailResponseDto`와 schema | 확정 JSON과 같은 상세 계약 |
| `src/features/citizen-participation/api/vote/vote.api.ts` | `getVoteDetail` 반환 타입 변경 | 공용 `ContentDetailDto`에 의존하지 않음 |
| `src/features/citizen-participation/api/http/citizenParticipation.parser.ts` | `parseVoteDetail` 추가 | 알 수 없는 상세 값을 좁힘 |
| `src/features/citizen-participation/hook/useCitizenParticipationQueries.ts` | `useVoteDetailQuery` 분리, vote를 공용 detail에서 제외 | 목록 훅과 같은 전용 경로 |
| `src/pages/citizen-participation/model/presentation.ts` | `toVoteDetail(GetVoteDetailResponseDto)` | agenda·기간·불가 사유·CLOSED 비율 매핑 |
| `src/pages/citizen-participation/ui/CitizenParticipationDetailRoutes.tsx` | `useVoteDetailQuery`, `myChoice === null` 분기 | 미투표를 제출 완료로 보지 않음 |
| `src/features/citizen-participation/mocks/fixtures.ts` / `handlers.ts` | SUCCESS envelope, 상세 전용 UPCOMING/CANCELLED, draft 404, 재투표 409 | 로컬이 확정 계약을 재현 |
| `src/features/citizen-participation/index.ts` | 훅·parser·DTO 타입 export | barrel이 새 계약을 노출 |

## 결정 사항

- 목록 아이템/`status` query는 `VOTE_LIST_STATUS`만 허용한다.
- 시작 전·중단 fixture는 `voteDetailOnlyFixtures`로 두어 내 활동 건수에 넣지 않는다.
- UI `state`는 `IN_PROGRESS`만 `ongoing`, 나머지(시작 전·중단·완료)는 `closed`. 시작 전·중단 이유는 `period` 접두사다.
- 댓글 API 경로는 변경하지 않았다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| `npx vitest run src/features/citizen-participation src/pages/citizen-participation` | 12 files / 66 tests passed |
| `npx tsc -p tsconfig.app.json --noEmit` | exit 0 |
| `npm run lint && npm run build` | exit 0 |

구현 중 수정한 실패:

- 시작 전·중단 투표를 `contentFixtures`에 넣자 내 활동이 `전체 8건` 대신 `전체 10건`을 표시했다 → 상세 전용 fixture로 분리

## Watcher 인계

현재 변경은 투표 상세 요청/응답 계약과 상세 사용처 연결이다. UI 시각 QA는 수행하지 않았고, 검증은 테스트·build·lint다. `VoteDetailPage` 마크업은 변경하지 않았다.
