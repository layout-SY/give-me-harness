# 구현 로그

## 작업 요약
- 활동 로그 목록을 vote/survey와 같은 entity query + MSW + search/data/selection/controller/view로 결선했다. 페이지는 fixture를 직접 import하지 않는다.

## 재사용 자산
- `FilterBar`, `KpiStrip`, `MasterDetailLayout`, `Table`, `DateRangeField`, vote 목록 query/MSW 계약, comment `todayCount` count 필드

## 신규 파일 / 수정 파일
- 신규: `use-cp-activity-log-list-query.ts`, 목록 페이지 search/data/selection/controller/view/config/types
- 수정: `cp-activity-log.dto.ts` / `api.ts` / `parser.ts` / `query-keys.ts` / `index.ts`, `cp-activity-log.handlers.ts`, `cp-activity-log-page.tsx`, fixture에 `PROPOSAL` 샘플 1건

## 핵심 로직
- 요청: `GET /v1/cp/activity-logs` + `page/size/activityType/targetType/user/startDate/endDate`
- MSW는 targetType·user·기간으로 baseFiltered를 만든 뒤 activityType을 적용하고, tab count·todayCount는 baseFiltered 기준이다
- 기본 조회 기간은 `2026-07-01`~`2026-07-31`이다
- 목록은 읽기 전용이라 mutation 없이 행 선택만 한다. placeholder 구간에는 선택을 막는다

## 검증 / 요청 처리
- `yarn tsc --noEmit`, `yarn eslint` 변경 경로 통과
- 브라우저 `http://localhost:2426/cp/activity-logs`: 사용자 `홍길동` 조회, 대상유형 `제안` 조회, 초기화, `U-0091` 상세 회귀 확인

## 리스크
- 게시글 fixture 1건의 `targetScreen`이 제안 화면 문자열로 남아 있다. 이번 목록 결선 범위 밖이다

## 핸드오프 메모
- 상태: `paused_after_generator`. Watcher `confirmed` 전 Closure/portfolio는 보류한다
