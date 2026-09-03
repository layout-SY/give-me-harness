# 계획

## 요청 요약
- 활동 로그 목록 조회에 vote/proposal과 같은 요청 DTO·API·MSW·query를 추가하고, 필터 검색이 실제로 동작하게 한다.

## 작업 유형
- hybrid

## 범위
- `src/entities/cp-activity-log/` 목록 query DTO, getList, parser, list query hook
- `src/mocks/cp-activity-log.handlers.ts` 목록 GET + 필터
- `src/pages/cp-activity-log/ui/` 목록 페이지를 search/data/selection/controller/view로 분해

## 제외 범위
- 사용자 활동 상세의 조회 계약(이미 존재)
- 처리 저장 mutation (읽기 전용 목록)
- 공용 CP 목록 추상화 훅

## 섹션
1. entity 목록 계약
2. MSW 목록 GET
3. 목록 페이지 결선

## 필요 에이전트
- Generator

## 필요 스킬
- policy-tanstack-query, policy-data-fetch-layer, recipe-data-dto, policy-coding-convention, policy-documentation

## 리스크 / 가정
- 목록은 읽기 전용이므로 process/mutation 훅을 두지 않는다
- 기본 기간은 기존 UI의 7월 값과 맞춘다

## 승인 요청
사용자 요청에 작업 시작이 포함되어 실행한다.
