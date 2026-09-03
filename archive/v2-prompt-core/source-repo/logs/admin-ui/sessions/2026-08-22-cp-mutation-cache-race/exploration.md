# 탐색 기록

## 상태
- `paused_after_generator`
- 탐색 후 승인된 lifecycle을 세 process mutation hook에 구현했다.
- Watcher를 사용할 수 없어 Closure는 수행하지 않는다.

## 스킬·문서 확인
- `policy-tanstack-query`
- `policy-data-fetch-layer`
- `recipe-api-authoring`
- `policy-harness`
- `policy-refactoring`
- `policy-abstraction-strategy`
- `policy-documentation`
- TanStack Query v5 공식 `QueryClient`, mutation lifecycle, mutation response cache update 문서
- `.codex/memory/reusable-assets.md`

## 탐색 범위
- `src/shared/ui/`: 이번 entity mutation lifecycle 변경에 필요한 UI 자산 없음.
- `src/widgets/`: 이번 entity mutation lifecycle 변경에 필요한 widget 없음.
- `src/entities/cp-proposal/model/`
- `src/entities/cp-vote/model/`
- `src/entities/cp-discussion/model/`
- 각 도메인의 list/detail process 호출부와 query hook.

## 현재 mutation 계약
- Proposal·Vote·Discussion process mutation은 모두 API 결과를 unwrap하고 detail parser를 통과한 authoritative detail을 반환한다.
- hook-level `onSuccess`에서 exact detail cache에 mutation 응답을 기록한 뒤 list prefix를 무효화한다.
- 같은 mutation hook이 각 도메인의 list surface와 detail surface에서 함께 사용된다.
- list/detail queryFn은 TanStack Query의 `AbortSignal`을 실제 Axios 요청까지 전달한다.

## query key 구조

| 도메인 | list prefix | exact detail |
|---|---|---|
| Proposal | `cpProposalKeys.lists()` → `["cp-proposals", "list"]` | `cpProposalKeys.detail(proposalId)` |
| Vote | `cpVoteKeys.lists()` → `["cp-votes", "list"]` | `cpVoteKeys.detail(voteId)` |
| Discussion | `cpDiscussionKeys.lists()` → `["cp-discussions", "list"]` | `cpDiscussionKeys.detail(discussionId)` |

## 확인된 경쟁 조건
### detail
1. 기존 detail GET이 변경 전 값을 요청한다.
2. process mutation이 성공해 authoritative detail을 `setQueryData`한다.
3. 기존 detail GET이 늦게 완료돼 같은 exact key를 변경 전 값으로 덮어쓸 수 있다.
4. 현재 list invalidation은 detail key에 영향을 주지 않는다.

### list
1. `invalidateQueries(lists())`는 모든 matching list를 invalid 처리한다.
2. 기본 `refetchType`은 `active`이므로 active list만 refetch 대상으로 선택된다.
3. `cancelRefetch: true`도 선택된 active refetch에만 적용된다.
4. observer가 없는 inactive prefetch list가 이미 fetch 중이면 invalidation만으로는 해당 요청을 취소하지 못한다.
5. 오래된 inactive 응답이 mutation 성공 후 cache에 기록될 수 있으므로 list prefix의 explicit cancellation이 필요하다.

## TanStack Query 공식 계약
- `cancelQueries`는 active 여부와 무관하게 matching query 전체를 취소하고 기본 `revert: true`를 적용한다.
- `invalidateQueries`는 모든 matching query를 invalid 처리하지만 기본으로 active query만 refetch한다.
- `refetchQueries`는 선택된 query에 대해 `cancelRefetch: true`를 기본 적용한다.
- async hook-level `onSuccess`는 반환 Promise를 기다리므로 cancellation → cache write → list refetch 순서를 mutation lifecycle 안에 둘 수 있다.

## 접근안 비교

| 접근안 | active/inactive list | exact detail | 실패 의미론 | 판단 |
|---|---|---|---|---|
| 성공 시 list prefix + exact detail 취소 후 cache write | 모두 취소 | 대상만 취소 | 유지 | 권고 |
| `onMutate`에서 선제 취소 | 모두 취소 | 대상만 취소 | 실패 mutation도 조회 취소 | 비권고 |
| detail/list invalidate 후 재조회 | refetch 의존 | refetch 의존 | 유지 | authoritative 응답 미활용·네트워크 증가 |
| exact detail만 취소 | inactive list 잔존 | 대상 취소 | 유지 | 부분 해결 |

## 권고 lifecycle
1. mutationFn 성공 및 detail parser 완료.
2. hook-level async `onSuccess(detail, variables)` 진입.
3. list prefix와 mutation variables가 가리키는 exact detail key를 `Promise.all`로 취소하고 완료를 기다린다.
4. exact detail cache에 authoritative mutation 응답을 기록한다.
5. list prefix를 invalidate하고 active list refetch 완료를 기다린다.
6. 이후 surface의 호출별 `onSuccess`와 `onSettled`가 실행된다.

## 재사용·추상화 결정
- 각 entity의 기존 query key factory와 `QueryClient`를 직접 재사용한다.
- 추가 로직은 파일별로 짧고 도메인별 ID·key factory가 달라 공용 mutation helper를 만들지 않는다.
- API, DTO, parser, query hook, caller, UI 계약을 변경하지 않는다.

## 가정·제약
- process mutation endpoint는 요청 ID와 동일한 ID의 authoritative detail을 반환한다.
- 서버는 mutation 성공 후 list GET에 변경된 상태가 보이는 read-after-write 계약을 제공한다.
- eventual consistency가 존재한다면 별도 list write-through 전략이 필요하며 이번 범위에는 포함하지 않는다.
- 사용자 승인 전 source 구현을 시작하지 않는다.
