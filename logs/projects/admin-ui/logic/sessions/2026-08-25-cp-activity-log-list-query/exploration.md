# 탐색 기록

## 대상 경로
- src/shared/ui/
- src/widgets/
- src/pages/cp-vote/ui/
- src/pages/cp-survey/ui/
- src/entities/cp-vote/
- src/entities/cp-proposal/
- src/entities/cp-activity-log/
- src/mocks/
- .agents/skills/reference/
- .codex/memory/reusable-assets.md

## 발견한 기존 재사용 자산
- 발견 항목: `useCpVoteListQuery` / `cpVoteListQuerySchema` / `createCpVoteHandlers` 목록 GET, `FilterBar`·`KpiStrip`·`MasterDetailLayout`·`Table`, 설문 목록 search/data/controller/view 분해
- 재사용 제안: 활동 로그 목록도 동일 계약(query DTO + getList + Zod parser + query key params 전부 + MSW `searchParamsToRecord`)으로 결선. 공용 CP 목록 훅은 만들지 않고 도메인 전용 훅 복제
- 근거: vote/proposal이 이미 필터·페이지·placeholderData·조회 실패 Dialog 패턴을 갖고 있고, 목록은 읽기 전용이라 process/mutation만 제외하면 된다

## 재사용이 어려운 자산
- 자산: `useCpVoteListProcess` / `useCpSurveyListProcess`
- 부적합 사유: 활동 로그 목록은 처리 저장이 없고 행 선택만 필요하다

## 신규 자산 필요성
- 필요 항목: `GetCpActivityLogListQueryDto`, `getList`, 목록 MSW, `useCpActivityLogListQuery`, `use-cp-activity-log-list-selection`
- 필요 이유: 기존 목록 페이지가 fixture를 직접 렌더하고 FilterBar `onSubmit`이 없어 조회가 동작하지 않았다
