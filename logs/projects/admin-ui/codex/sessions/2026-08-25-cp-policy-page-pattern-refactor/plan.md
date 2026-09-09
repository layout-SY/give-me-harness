# 계획

## 요청 요약
- 기존 CP 목록/상세 패턴으로 정책반영 페이지를 정리한다.

## 작업 유형
- refactor

## 범위
- `src/pages/cp-policy/ui` 목록·상세 page → controller → view 분해
- 기존 `useCpPolicyListQuery` / `useCpPolicyDetailQuery` / `useCpPolicyProcessMutation` 결선

## 제외 범위
- entity/MSW 재작성
- 공용 CP 목록 추상화 훅
- 설문 상세·게시판·신고·보상 등 다른 fixture 화면

## 섹션
1. 목록 search/data/process/controller/view
2. 상세 process/controller/view

## 필요 에이전트
- Generator

## 필요 스킬
- policy/coding-convention, policy/hook-extraction, policy/data-fetch-layer
- recipe/data-fetch, policy/tanstack-query
- reference/table, search-state-bar(FilterBar)

## 리스크 / 가정
- 처리 단계 드롭다운 재선택 index -1은 무시한다
- 목록 처리 저장은 stage 또는 reflectionContent가 바뀐 경우에만 활성화한다

## 승인 요청
이 계획대로 진행할까요, 아니면 조정할 부분이 있나요?
