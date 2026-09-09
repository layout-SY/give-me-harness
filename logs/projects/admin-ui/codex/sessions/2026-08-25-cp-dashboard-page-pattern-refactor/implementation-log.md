# 구현 로그

## 작업 요약
- 운영 대시보드를 사용자 활동 상세와 같은 page → controller → view로 분해했다. 조회 계약은 기존 `useCpDashboardOverviewQuery`를 유지한다.

## 재사용 자산
- `PageHeader`, `KpiStrip`, `ActionBar`, `SectionCard`, `DefinitionList`, `StatusBadge`, `Loading`, `Button`
- 읽기 전용 controller 패턴: `use-cp-user-activity-detail-controller`

## 신규 파일 / 수정 파일
- 신규: `cp-dashboard.config.ts`, `cp-dashboard.types.ts`, `use-cp-dashboard-controller.tsx`, `cp-dashboard-view.tsx`
- 수정: `cp-dashboard-page.tsx`를 얇은 진입점으로 축소

## 핵심 로직
- controller가 query 오류 Dialog와 바로가기 navigate를 담당한다
- view는 pending / 빈 데이터 새로고침 / KPI·요약 카드·바로가기만 렌더한다
- KPI·바로가기 경로는 config 순수 데이터다

## 검증 / 요청 처리
- `yarn tsc --noEmit`, `yarn eslint src/pages/cp-dashboard` 통과
- 브라우저 `http://localhost:2426/cp/dashboard`: KPI 214/31/186/18, 요약 카드, `댓글 관리` 바로가기 `/cp/comments` 이동 확인

## 리스크
- 조회 실패 empty 상태는 MSW가 항상 성공 응답을 주므로 이번 브라우저에서 재현하지 못했다

## 핸드오프 메모
- 상태: `paused_after_generator`. Watcher `confirmed` 전 Closure/portfolio는 보류한다
