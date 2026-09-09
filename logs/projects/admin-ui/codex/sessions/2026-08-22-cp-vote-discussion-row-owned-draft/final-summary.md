# 최종 요약

## 상태
- `paused_after_generator`
- 구현과 정적·브라우저 검증은 완료했지만 Watcher `confirmed`가 없어 Closure 및 완료 처리하지 않는다.

## 무엇이 변경되었는가
- Vote·Discussion 목록이 `useStatusTransition.resetKey`로 상태 draft를 선택 행 ID에 귀속한다.
- 공개 기준 draft도 `{ voteId, index }` 또는 `{ discussionId, index }`로 소유 행을 명시한다.
- 현재 선택 행과 소유 ID가 일치하는 draft만 UI, `canSave`, mutation payload에 참여한다.
- reset, 명시적 행 선택, mutation 성공 시 공개 기준 draft를 제거한다.

## 왜 변경했는가
- same-query refetch로 기존 선택 행이 사라지고 같은 상태의 다른 행이 fallback될 때 이전 행의 상태·공개 기준 draft가 새 행의 저장 payload에 결합될 수 있는 경로를 제거하기 위해서다.

## 재사용한 자산
- `useStatusTransition.resetKey`.
- Proposal process의 행 소유 selection 패턴.
- 기존 Vote·Discussion controller/View/API/mutation 계약.

## 영향받는 영역
- `src/pages/cp-vote/ui/use-cp-vote-list-process.tsx`
- `src/pages/cp-discussion/ui/use-cp-discussion-list-process.tsx`

## 검증
- 변경 파일 scoped ESLint 통과.
- `tsc -b`와 Vite production build 통과.
- scoped `git diff --check` 통과.
- Vote: VT-001 draft 생성 후 외부 상태 변경과 same-query refetch로 VT-002 fallback, 이전 draft 제거·persisted 공개 기준 복구·저장 비활성 확인.
- Discussion: DS-001 draft 생성 후 DS-002 fallback, 이전 draft 제거·persisted 공개 기준 복구·저장 비활성 확인.
- 최종 browser console error 0건, warning 0건.
- 1391×1043 두 페이지 fresh 캡처의 독립 Visual QA Oracle 2회 `PASS`, 차단 0건.

## 남은 리스크
- TypeScript LSP와 Bun 미설치, test runner 부재, Watcher 미실행.
- Vote 날짜 placeholder 줄바꿈과 날짜 유효성 검증은 기존 별도 backlog다.

## 후속 제안
- Watcher `confirmed` 후 승인된 다음 섹션인 Proposal·Vote·Discussion mutation cache race 제거로 이동한다.
