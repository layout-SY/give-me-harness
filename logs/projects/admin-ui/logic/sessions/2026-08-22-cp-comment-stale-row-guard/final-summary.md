# 최종 요약

## 상태
- `paused_after_generator`
- 구현과 정적·브라우저 검증은 완료했지만 Watcher `confirmed`가 없어 Closure 및 완료 처리하지 않는다.

## 무엇이 변경되었는가
- Comment data hook이 TanStack Query의 `isPlaceholderData`를 `isCurrentData` 계약으로 노출한다.
- placeholder 기간에는 process의 선택 행과 처리 상태를 비우고 행 선택·상태 변경·저장을 차단한다.
- controller는 현재 데이터일 때만 optional `onRowClick`을 제공한다.
- Comment table controller의 행 클릭 타입을 optional로 정렬했다.

## 왜 변경했는가
- query 전환 중 유지되는 이전 목록의 첫 행이 새 query의 처리 대상으로 노출될 수 있는 구간을 제거하기 위해서다.

## 재사용한 자산
- TanStack Query `isPlaceholderData`.
- Proposal/Vote/Discussion 목록의 `isCurrentData` 패턴.
- 공용 `Table.onRowClick` optional 계약과 기존 상세·처리 control disabled 계약.

## 영향받는 영역
- `src/pages/cp-comment/ui/use-cp-comment-list-data.tsx`
- `src/pages/cp-comment/ui/use-cp-comment-list-process.tsx`
- `src/pages/cp-comment/ui/use-cp-comment-list-controller.tsx`
- `src/pages/cp-comment/ui/cp-comment-list.types.ts`

## 검증
- 변경 파일 scoped ESLint 통과.
- `tsc -b`와 Vite production build 통과.
- scoped `git diff --check` 통과.
- 실제 브라우저에서 현재 데이터 행 선택·상세 전환·상태 변경 후 저장 활성화 확인.
- 15초 지연 query 전환에서 이전 행 9개 유지, 클릭 가능 행 0개, 선택 행 0개, click·Enter 무효, 처리·저장 비활성 확인.
- 최신 응답 후 첫 행 선택과 상호작용 복구 확인.
- 1391×1043 현재/placeholder 캡처의 독립 Visual QA Oracle 2회 `PASS`, 차단 0건.
- browser console error 0건, warning 0건.

## 남은 리스크
- TypeScript LSP 미설치, 전체 lint의 기존 오류, Watcher 미실행.
- 비활성 저장 버튼의 시각 표현은 기존 shared 스타일을 유지한다.

## 후속 제안
- Watcher `confirmed` 후 승인된 다음 섹션인 Vote·Discussion `resetKey` 작업으로 이동한다.
