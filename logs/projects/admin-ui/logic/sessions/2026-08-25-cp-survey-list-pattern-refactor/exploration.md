# 탐색 기록

## 대상 경로
- `src/shared/ui/`
- `src/widgets/`
- `src/features/`
- `src/pages/cp-survey/`
- `src/pages/cp-vote/ui/`
- `src/pages/cp-proposal/ui/`
- `src/pages/cp-discussion/ui/`
- `src/entities/cp-survey/`
- `.agents/skills/reference/`
- `.codex/memory/reusable-assets.md`

## 발견한 기존 재사용 자산
- 발견 항목:
  - CP 목록 페이지 조립 패턴: `page → controller → view`, 하위에 `search` / `data` / `process` 분리 (`cp-vote`, `cp-proposal`, `cp-discussion` 동일)
  - `~/entities/cp-survey`에 이미 vote/proposal과 같은 entity 계층이 존재함 (`api` / parser / DTO / query keys / `useCpSurveyListQuery` / `useCpSurveyProcessMutation`)
  - 레이아웃: `PageHeader`, `KpiStrip`, `FilterBar`, `MasterDetailLayout`, `ActionBar` (`~/widgets/admin-page-layout`)
  - 프리미티브: `Table`, `SectionCard`, `DefinitionList`, `Dropdown`, `TextInput`, `Button`, `Loading`, `useDialog`
  - 처리 패널: `StatusTransitionField` + `~/features/cp-status-transition`의 `useStatusTransition`
  - 기간 필터: `DateRangeField` (`~/features/calendar-picker`)
- 재사용 제안:
  - 설문 목록 페이지를 vote 목록과 같은 파일 분해·controller 계약으로 맞춘다.
  - 페이지에서 fixture를 직접 import하지 않고 `useCpSurveyListQuery` / `useCpSurveyProcessMutation`만 사용한다 (`policy-tanstack-query`).
  - 운영상태 Dropdown을 `StatusTransitionField`로 교체한다.
  - 조회 실패 Dialog, placeholderData 기준 행 선택 가드, FilterBar 제출/초기화, 테이블 페이지네이션, 저장 mutation 부수효과는 vote `use-cp-vote-list-*`를 도메인 필드만 바꿔 복제한다.
- 근거:
  - `src/pages/cp-survey/ui/cp-survey-list-page.tsx`는 단일 파일에 검색/선택/KPI/컬럼/처리 UI가 모두 있고 `CP_SURVEY_LIST_FIXTURE`를 직접 읽는다.
  - vote/proposal/discussion 목록은 이미 같은 계약을 공유한다. 공용 추상화 훅을 새로 만들 조건(소비자 2곳 이상 + 제네릭 가능)은 충족하지만, 기존 CP 도메인은 도메인 전용 hook을 복제하는 약한 추상화를 선택했다 (`policy-abstraction-strategy`, `policy-hook-extraction`).

## 재사용이 어려운 자산
- 자산: vote의 작성자 필터·결과공개, proposal의 작성자 필터·담당부서
- 부적합 사유: 설문 목록 DTO(`CpSurveyListItem`)에는 `authorName` / `disclosureRule` / `department`가 없고, 필터 계약은 `status` / `title` / `startDate` / `endDate`다. 설문 전용 필드(대상, 외부URL)만 유지한다.

## 신규 자산 필요성
- 필요 항목: `src/pages/cp-survey/ui/` 아래 목록 전용 파일 세트 (config / types / search / data / process / controller / view). entity·shared·widget 신규 자산은 없음.
- 필요 이유: 다른 CP 목록과 동일한 책임 분리. 공용 `useCpListController` 추상화는 사용처마다 필드가 달라 제네릭 폭발 위험이 있어 이번 범위에서 만들지 않는다.
