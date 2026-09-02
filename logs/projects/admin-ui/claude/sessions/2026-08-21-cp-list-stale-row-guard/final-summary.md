# 최종 요약

## 상태
- `paused_after_generator`
- 구현과 정적·브라우저 검증은 완료했지만 Watcher confirmed가 없어 Closure 및 완료 처리하지 않는다.

## 무엇이 변경되었는가
- Proposal·Discussion·Vote 목록이 이전 `placeholderData`를 표시하는 동안 선택 행을 만들지 않는다.
- stale 기간에는 행 클릭, 처리 저장, 상세 화면 이동을 비활성화하고 handler에서도 mutation을 방어한다.
- Proposal 목록은 10줄 route page, search-state hook, controller hook, props 기반 view로 분리했다.
- Proposal 상태 변경 draft는 현재 상태와 선택 제안 ID에 귀속되어 다른 행으로 fallback될 때 즉시 초기화된다.
- Proposal controller를 data/process hooks와 별도 View contract로 추가 분리해 controller는 search orchestration과 navigation만 담당한다.

## 왜 변경했는가
- query key 변경 직후 이전 목록의 첫 행이 자동 선택되어 잘못된 도메인 항목을 처리할 수 있는 구간을 제거하기 위해서다.
- Proposal route page가 검색·서버 상태·처리 흐름·Dialog·navigation·JSX를 동시에 소유하던 책임 집중을 제거하기 위해서다.

## 재사용한 자산
- TanStack Query `isPlaceholderData`.
- 공용 `Table`, `Button`, `Dropdown`, `StatusTransitionField`의 기존 계약.

## 영향받는 영역
- `src/features/cp-status-transition/hook/useStatusTransition.ts`
- `src/pages/cp-proposal/ui/cp-proposal-list-page.tsx`
- `src/pages/cp-proposal/ui/use-cp-proposal-list-search-state.ts`
- `src/pages/cp-proposal/ui/use-cp-proposal-list-controller.tsx`
- `src/pages/cp-proposal/ui/use-cp-proposal-list-data.tsx`
- `src/pages/cp-proposal/ui/use-cp-proposal-list-process.tsx`
- `src/pages/cp-proposal/ui/cp-proposal-list.types.ts`
- `src/pages/cp-proposal/ui/cp-proposal-list-view.tsx`
- `src/pages/cp-discussion/ui/cp-discussion-list-page.tsx`
- `src/pages/cp-vote/ui/cp-vote-list-page.tsx`

## 검증
- 변경 파일 대상 ESLint 통과.
- production build 통과.
- Playwright stale/settled 기능 시나리오 세 페이지 통과.
- 3개 viewport × 3개 페이지의 독립 시각 QA 통과.
- Proposal 리팩터 후 초기 선택·행 선택·검색 stale/settled·상세 이동 시나리오와 console error 0건을 재확인했다.
- Proposal 375·768·1280px 기준 이미지 비교는 모두 100/100 유사도였다.
- 동일 상태 교차 행 회귀 시나리오에서 CP-001 draft가 CP-005에 남지 않고 저장 버튼이 비활성화되는 것을 확인했다.
- fresh-session console error 0건과 Oracle 재검토 차단 발견 0건을 확인했다.
- controller 세분화 후 대상 ESLint, production build, diff check를 재통과했다.
- 실제 상태 mutation·성공 Dialog·선택 유지·draft reset과 원상복구를 확인했다.
- fresh 3-viewport 시각 비교는 모두 100/100 유사도였고 독립 시각 검토 2회와 코드 품질 Oracle 모두 차단 발견 0건이었다.

## 남은 리스크
- 전체 lint의 기존 실패, TypeScript LSP 미설치, Watcher 미실행.
- 기존 모바일·태블릿 표 클리핑과 날짜 placeholder 줄바꿈.
- Discussion·Vote의 상태 draft ID 귀속은 각 controller 분리 단계에서 적용해야 한다.
- 동일 query의 행 제거·복원 시 내부 선택 ID가 다시 활성화될 수 있는 낮은 잠재 위험과 cached refetch 오류의 retry 미노출은 기존 동작으로 유지했다.

## 후속 제안
- Watcher confirmed 후 별도 승인으로 Vote 페이지의 search-state/controller/presentational 경계 분리를 다음 섹션으로 진행한다.
