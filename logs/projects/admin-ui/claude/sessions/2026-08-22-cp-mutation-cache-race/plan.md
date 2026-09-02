# 계획

## 상태
- `paused_after_generator`
- 사용자가 `작업 시작`으로 승인한 범위를 구현하고 정적·브라우저 검증을 완료했다.
- Watcher를 사용할 수 없어 `confirmed` 및 Closure 처리는 보류한다.

## 요청 요약
- Proposal·Vote·Discussion process mutation 성공과 동시에 진행 중인 list/detail query가 최신 mutation cache를 오래된 응답으로 덮어쓰는 경쟁 조건을 제거한다.

## 작업 유형
- correctness bug fix

## 변경 범위
1. `src/entities/cp-proposal/model/use-cp-proposal-process-mutation.ts`
2. `src/entities/cp-vote/model/use-cp-vote-process-mutation.ts`
3. `src/entities/cp-discussion/model/use-cp-discussion-process-mutation.ts`

## 권고 구현
각 mutation hook의 `onSuccess`를 async callback으로 변경한다.

```ts
onSuccess: async (detail, variables) => {
  const listQueryKey = domainKeys.lists();
  const detailQueryKey = domainKeys.detail(variables.domainId);

  await Promise.all([
    queryClient.cancelQueries({ queryKey: listQueryKey }),
    queryClient.cancelQueries({ queryKey: detailQueryKey, exact: true }),
  ]);

  queryClient.setQueryData(detailQueryKey, detail);
  await queryClient.invalidateQueries({ queryKey: listQueryKey });
},
```

도메인별 ID는 다음을 사용한다.
- Proposal: `variables.proposalId`
- Vote: `variables.voteId`
- Discussion: `variables.discussionId`

## 순서 불변식
1. cancellation 완료 전에 authoritative detail을 쓰지 않는다.
2. list prefix는 모든 필터·검색·페이지 variant를 취소한다.
3. detail은 mutation 대상 ID의 exact key만 취소한다.
4. mutation 응답 detail을 exact cache에 기록한다.
5. list prefix만 invalidate해 active list를 최신 서버 값으로 재조회한다.
6. inactive list는 취소 후 invalid 상태로 남아 다음 mount에서 재조회한다.
7. hook-level async lifecycle 완료 후 surface 호출별 `onSuccess`·`onSettled`가 실행된다.

## 실패 의미론
- mutation HTTP 실패, envelope 실패, parser 실패 시 hook-level `onSuccess`에 진입하지 않는다.
- 따라서 list/detail query를 취소하거나 cache를 수정하지 않는다.
- 기존 surface `onError`, Dialog, mutation guard 해제 흐름을 유지한다.

## 대안
### A. 권고안: 성공 시 list prefix + exact detail 취소
- active·inactive list와 exact detail race를 모두 제거한다.
- 실패 mutation의 조회 lifecycle을 유지한다.
- mutation response cache write와 기존 list invalidation을 보존한다.

### B. `onMutate` 선제 취소
- mutation 전 race를 넓게 차단하지만 실패 mutation도 조회를 취소한다.
- 실패 시 재조회·rollback 정책이 추가로 필요해 범위를 확대하므로 제외한다.

### C. detail/list invalidate-only
- authoritative mutation 응답을 활용하지 않고 네트워크 재조회에 의존한다.
- UI 반영이 느려지고 eventual consistency 위험이 생겨 제외한다.

### D. exact detail만 취소
- inactive in-flight list variant가 오래된 응답을 기록하는 경로가 남아 부분 해결이므로 제외한다.

## 비목표
- API client, endpoint, DTO, schema, parser 변경
- query key 구조 또는 list/detail query hook 변경
- optimistic update, rollback snapshot, mutation retry 정책 추가
- detail invalidate/refetch 추가
- surface caller, Dialog, draft, UI, 사용자 노출 문자열 변경
- 공용 mutation helper/factory 추출
- Policy, Survey, Comment 등 다른 도메인 확장

## 검증 계획
### 정적 검증
- 변경한 세 파일 LSP diagnostics. LSP 미설치 시 제약 기록.
- 세 파일 scoped ESLint.
- `yarn build`로 TypeScript project build와 Vite production build 확인.
- scoped `git diff --check`.
- Bun no-excuse 도구가 계속 미설치면 대체 검증 근거 기록.

### 브라우저 deferred-query 회귀
각 Proposal·Vote·Discussion에서 반복한다.

1. 실제 QueryClient에 변경 전 값을 반환하는 deferred exact detail query를 시작한다.
2. observer 없는 별도 list variant를 deferred prefetch로 시작한다.
3. 현재 active list에도 변경 전 in-flight 요청이 존재하도록 제어한다.
4. UI에서 process mutation을 실행하고 authoritative 변경 후 detail을 먼저 받는다.
5. detail, active list, inactive list의 `AbortSignal`이 모두 abort되는지 확인한다.
6. mutation 대상이 아닌 다른 detail query는 취소되지 않는지 확인한다.
7. 오래된 deferred 응답을 늦게 resolve해도 exact detail cache가 mutation 응답에서 되돌아가지 않는지 확인한다.
8. active list는 invalidation 후 최신 값으로 refetch되고 inactive list는 invalid 상태로 남는지 확인한다.
9. mutation 실패 주입 시 deferred list/detail 요청이 취소되지 않고 cache도 변경되지 않는지 확인한다.
10. surface 성공 Dialog·draft reset·mutation guard 해제와 browser console error·warning 0건을 확인한다.

## 필요 에이전트
- Planner: lifecycle·key 범위·실패 의미론 확정
- Generator: 승인된 entity mutation hook 세 파일 구현
- Watcher: API 복구 후 최종 판정
- Closure: Watcher `confirmed` 후에만 실행

## 필요 스킬
- `policy-harness`
- `policy-coding-convention`
- `policy-tanstack-query`
- `policy-data-fetch-layer`
- `policy-refactoring`
- `policy-abstraction-strategy`
- `policy-type-definition`
- `policy-documentation`
- `policy-review-checklist`
- `recipe-api-authoring`
- `programming`
- `playwright`

## 승인 결과
- 사용자가 `작업 시작`으로 계획을 승인했다.
