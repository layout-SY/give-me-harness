# 구현 로그

## 작업 요약
- 설문조사 목록 페이지를 vote 목록과 같은 page/controller/view + search/data/process 구조로 분해했다.
- 페이지는 `CP_SURVEY_LIST_FIXTURE`를 직접 읽지 않고 `useCpSurveyListQuery` / `useCpSurveyProcessMutation`만 사용한다.

## 재사용 자산
- `~/entities/cp-survey` query·mutation
- `PageHeader`, `KpiStrip`, `FilterBar`, `MasterDetailLayout`, `ActionBar`
- `Table`, `SectionCard`, `DefinitionList`, `Dropdown`, `TextInput`, `Button`, `Loading`, `useDialog`
- `StatusTransitionField` + `useStatusTransition`
- `DateRangeField`

## 신규 파일 / 수정 파일
- 신규: `cp-survey-list.config.ts`, `cp-survey-list.types.ts`, `cp-survey-list-view.tsx`, `use-cp-survey-list-search.tsx`, `use-cp-survey-list-data.tsx`, `use-cp-survey-list-process.tsx`, `use-cp-survey-list-controller.tsx`
- 수정: `cp-survey-list-page.tsx` (controller 결선만 남김)

## 핵심 로직
- search: draft 필터는 `submit` 시에만 query에 반영. 페이지 변경은 query.page만 갱신.
- data: list query 결과로 KPI/행/페이지네이션 파생. 조회 오류는 Dialog. 초기 데이터 없으면 「다시 조회」.
- process: `isCurrentData`가 아니면 선택/저장 불가. 상태 전이 또는 비어 있지 않은 외부URL이 있을 때만 저장. 성공/실패 Dialog는 process hook에서 처리.
- 목록 DTO에 URL이 없어 행 선택 시 외부URL 입력은 빈 값으로 시작한다.

## 검증 / 요청 처리
- `yarn tsc --noEmit` 통과
- `yarn eslint src/pages/cp-survey/ui` 통과
- 브라우저(`/cp/surveys`): 목록·KPI 조회, 제목 검색, 초기화, 상태 변경 저장(성공 Dialog·KPI 갱신), 상세 화면 내비게이션 확인
- 상세 페이지는 이번 범위 밖이라 여전히 fixture를 표시한다

## 리스크
- 외부URL은 목록 아이템에 없어 현재 값을 목록 패널에서 보여 주지 못한다. 잘못된 URL은 MSW/서버 400으로 실패 Dialog가 난다.

## 핸드오프 메모
- Watcher는 Claude Code API 비가용으로 실행하지 않음. 상태: `paused_after_generator`
- Closure / portfolio / final-summary는 Watcher `confirmed` 전까지 보류
