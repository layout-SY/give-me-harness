# 포트폴리오 경험 기록

## 작업 개요
- 구현/수정 내용: 세 관리자 process mutation의 성공 lifecycle에 list prefix와 target exact detail cancellation을 추가해 stale query의 최신 cache 덮어쓰기를 차단했다.
- 구현 이유: 저장 성공 후 이전 GET 응답이 늦게 도착해 화면과 cache가 과거 상태로 되돌아가는 correctness 위험을 제거하기 위해서다.
- 작업 유형: correctness bug fix.
- 품질 상태: Generator 구현과 정적·브라우저 runtime 검증 완료, Watcher 대기 중인 `paused_after_generator`.

## 문제 상황
- 문제 출처: 구조적 race 분석과 deferred-query 런타임 시나리오.
- 대상 도메인·서비스: 시민제안·시민투표·시민토론 관리자 처리 mutation.
- 기존 문제와 영향: mutation response를 detail cache에 기록한 뒤 이전 detail GET 또는 inactive list prefetch가 늦게 완료되면 저장 성공 상태가 과거 값으로 되돌아갈 수 있었다.

## 요구사항 및 의사결정
- 사용자 요구·제안: 승인된 개선 순서에 따라 세 도메인의 mutation cache race 제거를 시작한다.
- 에이전트 제안: 실패 mutation의 조회 lifecycle을 유지하면서 성공 시 list prefix와 target exact detail만 취소한다.
- 최종 선택: 사용자가 `작업 시작`으로 권고안을 승인했다.

| 접근법 | 장점 | 단점 | 선택 여부와 이유 |
|---|---|---|---|
| 성공 시 list prefix + exact detail 취소 | active·inactive list와 target detail race 제거, 실패 의미론 유지 | 세 파일에 짧은 반복 | 선택: 가장 작은 correctness-complete 범위 |
| `onMutate` 선제 취소 | mutation 전 race 차단 | 실패 mutation도 조회 취소, rollback·refetch 정책 필요 | 미선택: 범위 확대 |
| invalidate-only | 구현 단순 | inactive in-flight query와 authoritative response 활용 문제 | 미선택: 부분 해결 |

## 사용 기술과 구체적 목적

| 기술/패턴/아키텍처 | 해결하려는 문제 | 적용 위치와 목적 | 미채택 대안/이유 |
|---|---|---|---|
| TanStack Query `cancelQueries` | 이전 GET의 late cache write | list prefix 전체와 target exact detail 취소 | detail/list invalidate-only는 in-flight inactive race 잔존 |
| async mutation `onSuccess` | cancellation·write·refetch 순서 보장 | cancellation 완료 후 cache write, invalidation 완료 후 callback | fire-and-forget은 surface가 먼저 진행 가능 |
| authoritative `setQueryData` | mutation 결과 즉시 반영 | 대상 exact detail cache | detail refetch는 네트워크·eventual consistency 의존 |
| MSW runtime handler + deferred QueryClient | 실제 browser stack에서 race 재현 | Vite·React·Axios·parser를 유지한 성공·실패 6개 시나리오 | API object monkeypatch는 HMR module identity로 불안정 |

## 적용 내용
- 각 process mutation hook에서 도메인 list prefix와 mutation variables 기반 exact detail key를 구성했다.
- 두 query 범위를 `Promise.all`로 취소하고, mutation detail을 기록한 뒤 list invalidation 완료를 기다린다.
- API, DTO, parser, query key factory, query hook, caller, UI, retry 정책은 변경하지 않았다.
- 공용 helper를 추가하지 않았다.

## 결과 및 성과
- before: 이전 list/detail 요청의 완료 순서에 따라 최신 mutation cache가 stale 값으로 되돌아갈 수 있었다.
- after: 세 도메인 모두 target list/detail 요청이 abort되고 늦은 stale resolve가 무시되며, sibling detail과 실패 mutation의 기존 조회 lifecycle은 유지됐다.
- 검증 결과: scoped ESLint, TypeScript production build, diff check 통과. 실제 브라우저에서 성공·실패 총 6개 process POST와 cache assertion 전체 통과. console error·warning 0건.
- 사용자 후속 피드백: 구현 후 추가 수정 요청은 확인되지 않았다.
- 잔여 리스크: 자동 테스트·LSP·Watcher가 없어 최종 Closure는 보류한다.

## 회고
- 잘된 판단: `invalidateQueries`의 active refetch 계약과 inactive in-flight query를 분리해 부분 수정이 아닌 list prefix cancellation까지 포함했다.
- 잘된 판단: 실패 의미론을 보존하기 위해 `onMutate`가 아닌 성공 lifecycle을 선택했다.
- 다시 한다면 바꿀 점: 브라우저 QA 시작부터 기존 MSW worker의 runtime handler를 사용해 API module HMR identity와 Service Worker route 우회 조사 시간을 줄일 것이다.
- 다음 작업에 적용할 인사이트: Vite+MSW 앱의 browser integration QA는 API object monkeypatch나 Playwright network route보다 앱이 실제 사용하는 worker module의 runtime handler가 더 안정적이다.
