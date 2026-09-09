# 구현 로그

## 승인된 범위

`GET /citizen/proposals`에 `mine`·`sort`를 넣고, 제안 목록 「내활동만 보기」가 같은 목록 API를 쓰게 한다. 목록 응답에는 본문 4필드가 없다.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `src/features/citizen-participation/api/proposal/proposal.dto.ts` | `PROPOSAL_LIST_SORT`, `mine?`, `sort?` | 허용 sort와 선택 `mine`이 DTO에 고정됨 |
| `src/features/citizen-participation/api/proposal/proposal.api.ts` | `toProposalListParams` | 기본 `sort=createdAt,desc`, `mine===true`일 때만 `mine=true`와 `customConfig` |
| `src/features/citizen-participation/model/queryKeys.ts` | `proposalList`에 `mine`/`sort` | 필터가 다른 캐시 키를 만든다 |
| `src/features/citizen-participation/hook/useCitizenParticipationQueries.ts` | `useProposalListQuery` 키에 기본 sort와 `mine` | 목록 훅이 확정 query를 반영한다 |
| `src/pages/citizen-participation/ui/CitizenListRoutes.tsx` | `ProposalListRoute`가 단일 list query | `/me/activity` 분기를 제안 목록에서 제거 |
| `src/features/citizen-participation/ui/layout/MyActivityToggle.tsx` | optional `label` | 제안만 다른 문구를 쓸 수 있다 |
| `src/features/citizen-participation/ui/proposal/ProposalListPage.tsx` | `label="내활동만 보기"` | 요청한 필터 문구 |
| `src/features/citizen-participation/mocks/handlers.ts` | `mine=true`면 `item.mine === true` | MSW가 서버 필터를 재현 |
| `src/features/citizen-participation/index.ts` | `PROPOSAL_LIST_SORT`, `ProposalListSort` export | 허용 sort를 barrel에서 재사용 |

## 결정 사항

- `mine=false`는 query에 넣지 않는다. 기본값이 false이기 때문이다.
- 제안 목록은 `useMyProposalActivityQuery`를 쓰지 않는다. 내 활동 페이지는 그대로 둔다.
- 정렬 UI는 추가하지 않고 전송 기본값만 맞춘다.
- 목록 본문 4필드는 스키마에 넣지 않았다. 상세 스키마에만 있다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| `npx vitest run src/pages/citizen-participation/ui/CitizenDataRoutes.test.tsx src/features/citizen-participation src/pages/citizen-participation/model` | 9 files / 62 tests passed |
| `npm run build` | `tsc -b && vite build` 성공 |
| `npm run lint` | exit 0 |

## Watcher 인계

현재 변경은 proposal list의 `mine`/`sort` 전송과 목록 필터 연결이다. UI 시각 QA는 수행하지 않았고, 검증은 테스트·build·lint다.
