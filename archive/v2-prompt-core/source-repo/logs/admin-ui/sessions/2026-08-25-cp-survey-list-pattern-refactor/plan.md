# 계획

## 요청 요약
- 설문조사 목록 페이지(`cp-survey-list-page.tsx`)가 fixture를 직접 쓰는 단일 파일 구조라, vote/proposal 등 다른 CP 도메인의 page/entity 사용 방식과 맞지 않는다.
- 이미 존재하는 `~/entities/cp-survey` query/mutation 계약을 목록 페이지가 소비하도록 구조를 맞춘다.

## 작업 유형
- hybrid (페이지 구조 리팩터 + 기존 entity 서버상태 결선)

## 범위
- `src/pages/cp-survey/ui/` 목록 화면만.
- 기준 패턴: `src/pages/cp-vote/ui/` 목록 세트 (search / data / process / controller / view / config / types).
- 재사용: `useCpSurveyListQuery`, `useCpSurveyProcessMutation`, `StatusTransitionField`, `FilterBar` 제출/초기화, `Table` 페이지네이션, `Loading`, `useDialog`.

## 제외 범위
- `cp-survey-detail-page.tsx` (상세도 fixture 직접 사용. 후속 섹션)
- `src/entities/cp-survey/**` API/DTO/parser/fixture 변경
- 공용 CP 목록 controller 추상화
- 행 선택 시 상세 query로 `externalUrl`을 채우는 동작

## 섹션
1. 설문 목록 페이지를 vote 목록 패턴으로 분해하고 entity query/mutation에 결선한다.
   - 유형: refactor (조립은 기존 CP 목록 recipe 복제)
   - 담당: Refactorer
   - 핵심 결정:
     - KPI/행은 `useCpSurveyListQuery` 결과에서 파생. 페이지에서 `CP_SURVEY_LIST_FIXTURE` import 금지.
     - 검색은 draft 상태 + `submit` 시에만 query 반영 (vote와 동일). 필터: 상태/제목/기간.
     - 처리 패널: `useStatusTransition` + `useCpSurveyProcessMutation`. 저장 성공/실패 Dialog는 process hook(surface)에서 처리.
     - 목록 아이템에 `externalUrl`이 없으므로 행 선택 시 입력은 빈 값으로 시작한다. 사용자가 유효한 URL을 입력했거나 상태가 바뀐 경우에만 저장 가능. 기존 하드코딩 `"Google Forms"`는 스키마(`http(s) URL`)와 맞지 않아 제거한다.
     - placeholderData 구간에는 행 클릭/저장 비활성 (`isCurrentData` 가드).
     - 초기 조회 실패 시 ActionBar 「다시 조회」.

## 필요 에이전트
- Planner (본 단계)
- Refactorer (섹션 1)
- Watcher: Claude Code API 비가용 → 실행하지 않음. Refactorer 완료 후 `paused_after_generator`

## 필요 스킬
- `policy-refactoring`
- `policy-coding-convention`
- `policy-hook-extraction`
- `policy-type-definition`
- `policy-tanstack-query`
- `policy-data-fetch-layer` (부수효과는 surface, query 함수에 Dialog 금지)
- `reference/components/table`
- `reference/components/loading`
- `recipe-api-authoring` (페이지는 entity hook만 호출, API 계층 수정 없음)

## 리스크 / 가정
- 목록 UI가 정적 fixture에서 서버 상태(로딩/재시도/페이지네이션/실제 저장)로 바뀐다. 요청 의도(다른 도메인 방식 정렬)에 포함되는 변경으로 본다.
- MSW/실서버가 survey list/process를 이미 제공한다고 가정한다. entity가 이미 그 계약을 갖고 있다.
- 상세 페이지는 이번 목록의 「상세처리 화면 열기」 내비게이션만 유지하고, 상세 데이터 결선은 후속 작업이다.

## 승인 요청
이 계획대로 진행할까요, 아니면 조정할 부분이 있나요?
