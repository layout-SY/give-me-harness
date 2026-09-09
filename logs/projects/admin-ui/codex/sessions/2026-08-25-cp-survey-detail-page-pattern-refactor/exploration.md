# 탐색 기록

## 대상 경로
- src/shared/ui/
- src/widgets/
- src/pages/cp-survey/ui
- src/pages/cp-vote/ui
- src/entities/cp-survey
- .agents/skills/reference/
- .codex/memory/reusable-assets.md

## 발견한 기존 재사용 자산
- 발견 항목: `useCpSurveyDetailQuery`, `useCpSurveyProcessMutation`, `useStatusTransition`, `StatusTransitionField`, `FilterBar` 계열은 목록 전용, 상세는 `PageHeader`/`ActionBar`/`SectionCard`/`DefinitionList`/`TimelineList`/`TextInput`/`Button`/`Loading`
- 재사용 제안: vote 상세 controller-view와 survey 목록 process의 status/externalUrl 저장 규칙을 상세에 복제
- 근거: 공용 CP 상세 훅을 만들지 않기로 한 기존 결정과 동일하다

## 재사용이 어려운 자산
- 자산: `CP_SURVEY_DETAIL_FIXTURE` 페이지 직접 import
- 부적합 사유: fixture는 page/component에서 직접 import하지 않는다

## 신규 자산 필요성
- 필요 항목: 설문 상세 전용 process/controller/view/model
- 필요 이유: 조회 실패 재조회와 처리 저장 부수효과를 surface에 둔다
