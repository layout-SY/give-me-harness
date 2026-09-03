# 계획

## 요청 요약
- 설문조사 상세를 기존 CP 상세 패턴(page → controller → view)으로 정리하고 entity query/mutation에 결선한다.

## 작업 유형
- refactor

## 범위
- `src/pages/cp-survey/ui` 상세 화면만
- 기존 `useCpSurveyDetailQuery` / `useCpSurveyProcessMutation` 결선

## 제외 범위
- entity/MSW 재작성
- 목록 화면 재작업
- 공용 CP 상세 추상화 훅

## 섹션
1. 상세 process/controller/view/types/model

## 필요 에이전트
- Generator

## 필요 스킬
- policy/coding-convention, policy/hook-extraction, policy/type-definition
- policy/tanstack-query, recipe/data-fetch

## 리스크 / 가정
- 처리 payload의 기간은 ISO 날짜(`YYYY-MM-DD`)여야 하므로 화면 입력은 ISO로 정규화한다
- 저장 가능 필드는 status / periodFrom / periodTo / externalUrl이다

## 승인 요청
이 계획대로 진행할까요, 아니면 조정할 부분이 있나요?
