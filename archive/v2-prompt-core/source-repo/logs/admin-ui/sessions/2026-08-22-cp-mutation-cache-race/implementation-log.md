# 구현 기록

## 상태
- `paused_after_generator`
- Generator 구현과 정적 검증을 완료했다.
- Watcher를 사용할 수 없으므로 Closure 및 완료 처리는 수행하지 않았다.

## 변경 파일
- `src/entities/cp-proposal/model/use-cp-proposal-process-mutation.ts`
- `src/entities/cp-vote/model/use-cp-vote-process-mutation.ts`
- `src/entities/cp-discussion/model/use-cp-discussion-process-mutation.ts`

## 구현 결과
- 세 process mutation hook의 hook-level `onSuccess`를 `async (detail, variables)`로 변경했다.
- 각 callback 내부에서 도메인별 `listQueryKey`와 mutation 대상 `detailQueryKey`를 로컬 상수로 구성했다.
- Proposal은 `variables.proposalId`, Vote는 `variables.voteId`, Discussion은 `variables.discussionId`를 exact detail key에 사용했다.
- list prefix cancellation과 exact detail cancellation을 `Promise.all`로 병렬 실행하고 모두 완료될 때까지 기다린다.
- cancellation 완료 후 authoritative mutation response를 exact detail cache에 기록한다.
- 기존 list prefix invalidation을 유지하고 완료될 때까지 기다린다.
- Proposal mutation variables의 기존 non-readonly 스타일은 변경하지 않았다.

## lifecycle 순서
1. mutation HTTP·envelope unwrap·detail parser 성공
2. list prefix와 mutation 대상 exact detail query cancellation 완료 대기
3. authoritative mutation response를 exact detail cache에 기록
4. list prefix invalidation 및 active list refetch 완료 대기
5. surface 호출별 lifecycle 진행

## key 범위
| 도메인 | list cancellation/invalidation | exact detail cancellation/write |
|---|---|---|
| Proposal | `cpProposalKeys.lists()` | `cpProposalKeys.detail(variables.proposalId)` |
| Vote | `cpVoteKeys.lists()` | `cpVoteKeys.detail(variables.voteId)` |
| Discussion | `cpDiscussionKeys.lists()` | `cpDiscussionKeys.detail(variables.discussionId)` |

## 보존한 계약
- API client, endpoint, DTO, parser를 변경하지 않았다.
- query key factory, query hook, caller, UI를 변경하지 않았다.
- mutation variables와 mutation 실패 동작을 변경하지 않았다.
- mutation 응답의 authoritative detail cache write와 기존 list invalidation을 유지했다.
- QueryClient 작업에 catch 또는 fallback을 추가하지 않았다.
- 공용 helper를 추출하지 않았다.

## 실패 의미론
- mutation HTTP·envelope·parser 실패 시 hook-level `onSuccess`에 진입하지 않는다.
- 따라서 실패 시 list/detail query cancellation, detail cache write, list invalidation이 실행되지 않는다.
- QueryClient cancellation 또는 invalidation 실패는 별도 catch 없이 기존 mutation lifecycle로 전파된다.

## 검증 결과
- TypeScript LSP diagnostics: 미실행. TypeScript LSP가 설치되지 않았고 사용자가 이전에 설치를 거절한 상태임을 도구가 보고했다.
- scoped ESLint: 통과.
- `yarn build` (`tsc -b && vite build`): 통과.
- scoped `git diff --check`: 통과.
- pure LOC: 세 source 파일 각각 27줄로 200줄 이하.
- 테스트: repository에 test runner script가 없어 추가·실행하지 않았다.
- 브라우저 deferred-query 회귀 검증: Proposal·Vote·Discussion의 성공·실패 시나리오가 모두 통과했다.
- 실제 Vite·React·TanStack Query·MSW·Axios·ApiResult unwrap·Zod parser 경로에서 세 mutation hook을 mount했다.
- 성공 시 active list, inactive list, target exact detail의 `AbortSignal`은 모두 abort됐고 sibling detail은 abort되지 않았다.
- cancellation 이후 늦게 stale query promise를 resolve해도 active list는 fresh 값, inactive list는 이전 값과 invalid 상태, target detail은 authoritative mutation 응답을 유지했다.
- active list queryFn은 각 도메인에서 2회 호출되어 cancellation 뒤 invalidation refetch가 실행됐고 inactive list는 `fetchStatus: idle`, `isInvalidated: true`로 남았다.
- hook-level lifecycle은 두 cancellation 완료 → detail `setQueryData` → list invalidation 완료 순서였고 호출별 callback은 `success → settled → mutateAsync resolved` 순서였다.
- 실패 mutation은 QueryClient lifecycle 0건, list/detail abort 0건, target detail cache 유지, 호출별 callback `error → settled → caught`를 확인했다.
- 브라우저 console error·warning 0건, QA harness DOM 0건, runtime MSW handler는 `resetHandlers()`로 원복했다.
- build는 기존 large chunk 경고와 `vite-tsconfig-paths` 안내를 출력했으나 성공했다.

## 잔여 위험과 다음 단계
- review-log, evaluation-log, final-summary, portfolio-entry는 `paused_after_generator` 증거 문서로 작성했다.
- Watcher `confirmed` 전에는 Closure 및 최종 완료 처리를 수행하지 않는다.
