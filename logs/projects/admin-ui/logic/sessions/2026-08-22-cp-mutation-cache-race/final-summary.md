# 최종 요약

## 상태
- `paused_after_generator`
- 구현과 정적·브라우저 검증은 완료했지만 Watcher `confirmed`가 없어 Closure 및 완료 처리하지 않는다.

## 무엇이 변경되었는가
- Proposal·Vote·Discussion process mutation 성공 시 list prefix와 mutation 대상 exact detail query를 먼저 취소한다.
- cancellation 완료 후 authoritative mutation detail을 exact cache에 기록한다.
- list prefix invalidation과 active list refetch 완료를 기다린 뒤 surface callback으로 진행한다.

## 왜 변경했는가
- mutation 성공보다 먼저 시작된 stale list/detail GET이 늦게 완료되어 최신 cache를 과거 값으로 덮어쓰는 경쟁 조건을 제거하기 위해서다.

## 재사용한 자산
- `cpProposalKeys`, `cpVoteKeys`, `cpDiscussionKeys`.
- 기존 QueryClient, mutation response parser, detail cache write, list invalidation 계약.
- 기존 API·DTO·caller·UI 계약.

## 영향받는 영역
- `src/entities/cp-proposal/model/use-cp-proposal-process-mutation.ts`
- `src/entities/cp-vote/model/use-cp-vote-process-mutation.ts`
- `src/entities/cp-discussion/model/use-cp-discussion-process-mutation.ts`

## 검증
- 세 파일 scoped ESLint 통과.
- `tsc -b`와 Vite production build 통과.
- scoped `git diff --check` 통과.
- 브라우저에서 세 실제 hook의 성공·실패 총 6개 mutation 경로 통과.
- 성공: active/inactive list와 target detail abort, sibling detail 비취소, active fresh refetch, inactive invalid 유지, late stale overwrite 차단.
- 실패: QueryClient side effect와 abort 0건, 기존 cache·in-flight query 유지.
- callback 순서, MSW handler 원복, QA DOM 제거, console error·warning 0건 확인.

## 남은 리스크
- TypeScript LSP와 Bun 미설치, test runner 부재, Watcher 미실행.
- 서버가 read-after-write 대신 eventual consistency를 제공하면 별도 list 동기화 정책이 필요하다.

## 후속 제안
- Watcher `confirmed` 후 Closure하고 다음 승인 섹션인 Vote·Discussion 날짜 검증으로 이동한다.
