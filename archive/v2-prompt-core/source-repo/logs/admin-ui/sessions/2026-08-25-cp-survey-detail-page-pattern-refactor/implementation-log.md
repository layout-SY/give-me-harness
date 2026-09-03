# 구현 로그

## 작업 요약
- 설문조사 상세를 vote와 같은 page → controller → view로 분해하고, 기존 entity query/mutation에 결선했다.

## 재사용 자산
- `useCpSurveyDetailQuery`, `useCpSurveyProcessMutation`, `useStatusTransition`, `StatusTransitionField`, `PageHeader`, `ActionBar`, `SectionCard`, `DefinitionList`, `TimelineList`, `TextInput`

## 신규 파일 / 수정 파일
- 상세: model/types/process/controller/view
- `cp-survey-detail-page.tsx`는 얇은 진입점으로 축소

## 핵심 로직
- 조회 실패 시 Dialog와 「다시 조회」를 surface에서 처리한다
- 처리 저장은 상태·기간·외부 URL 변경분만 보내고, 기간은 ISO 날짜로 정규화한다

## 검증 / 요청 처리
- `yarn tsc --noEmit`, `yarn eslint src/pages/cp-survey` 통과
- 브라우저에서 목록 → `SV-001` 상세 → 마감 저장 → 목록 상태 반영, `SV-999` 빈 화면/재조회를 확인했다

## 리스크
- 기간 입력이 ISO가 아니거나 시작일이 종료일보다 늦으면 저장 버튼이 비활성이다

## 핸드오프 메모
- 상태: `paused_after_generator`
