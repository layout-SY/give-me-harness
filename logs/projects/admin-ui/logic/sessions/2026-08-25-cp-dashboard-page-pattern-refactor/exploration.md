# 탐색 기록

## 대상 경로
- src/shared/ui/
- src/widgets/
- src/pages/cp-dashboard/
- src/pages/cp-activity-log/ui/ (읽기 전용 상세 패턴)
- src/entities/cp-dashboard/
- .agents/skills/reference/
- .codex/memory/reusable-assets.md

## 발견한 기존 재사용 자산
- 발견 항목: `useCpDashboardOverviewQuery`, `PageHeader`/`KpiStrip`/`ActionBar`/`SectionCard`/`DefinitionList`/`StatusBadge`/`Loading`/`Button`, 사용자 활동 상세의 page → controller → view
- 재사용 제안: 대시보드는 필터/목록이 없으므로 사용자 활동 상세와 같은 읽기 전용 controller/view로 분해. KPI 매핑은 `buildUserActivityKpiItems`처럼 config 순수 함수
- 근거: entity query와 MSW는 이미 있고, 페이지에 query·Dialog·navigate가 섞여 있다

## 재사용이 어려운 자산
- 자산: 목록 search/data/process 훅
- 부적합 사유: 대시보드는 페이지네이션·필터·처리 저장이 없다

## 신규 자산 필요성
- 필요 항목: `use-cp-dashboard-controller`, `cp-dashboard-view`, types, config
- 필요 이유: 페이지를 순수 진입점으로 만들고, 조회 부수효과와 마크업을 분리한다
