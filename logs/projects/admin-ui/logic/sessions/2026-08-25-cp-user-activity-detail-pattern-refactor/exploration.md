# 탐색 기록

## 대상 경로
- `src/pages/cp-activity-log/ui/`
- `src/entities/cp-activity-log/`
- `src/pages/cp-vote/ui/` (상세 기준)
- `src/shared/ui/`, `src/widgets/admin-page-layout/`
- `.codex/memory/reusable-assets.md`

## 발견한 기존 재사용 자산
- 발견 항목: vote 상세의 `page → controller → view`, `useQuery` + 조회 실패 Dialog + Loading/`다시 조회`
- 레이아웃: `PageHeader`, `KpiStrip`, `ActionBar`, `SectionCard`, `DefinitionList`, `Table`, `StatusBadge`, `TimelineList`, `Loading`, `useDialog`
- 재사용 제안: 읽기 전용 상세이므로 process/mutation 훅은 두지 않는다. KPI·컬럼은 순수 config로 분리한다.
- 근거: 화면 주석이 읽기 전용·저장 버튼 없음을 명시한다.

## 재사용이 어려운 자산
- 자산: vote/survey의 process mutation, 목록 search/data 훅
- 부적합 사유: 사용자 활동 상세는 처리 저장이 없고, 이번 범위는 상세 페이지만이다.

## 신규 자산 필요성
- 필요 항목: `cp-activity-log`의 ApiClient 상세 조회, DTO/parser, query key, `useCpUserActivityDetailQuery`, MSW GET, 페이지 controller/view/config/types
- 필요 이유: entity가 레거시 axios 모듈 + fixture만 있어, 페이지를 나눠도 vote/survey와 같은 서버상태 패턴이 성립하지 않는다.
