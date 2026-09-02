# 계획

## 요청 요약
- 운영 대시보드 페이지를 vote/사용자 활동 상세와 같은 page → controller → view 패턴으로 분해한다.

## 작업 유형
- hybrid (구조 리팩터, 조회 계약은 유지)

## 범위
- `src/pages/cp-dashboard/ui/` 를 page/controller/view/types/config로 분해
- 기존 `useCpDashboardOverviewQuery`를 controller에서만 사용
- 페이지에서 query/Dialog/navigate를 제거

## 제외 범위
- entity API/DTO/query/MSW 재작성 (이미 결선됨)
- `src/entities/dashboard/` 레거시 모듈
- 메인 노출·정책반영 등 다른 도메인
- 공용 대시보드 추상화 훅
- process/mutation (읽기 전용)

## 섹션
1. 대시보드 페이지 패턴 분해

## 필요 에이전트
- Generator

## 필요 스킬
- policy-publishing, policy-hook-extraction, policy-tanstack-query, policy-coding-convention, policy-type-definition, policy-documentation

## 리스크 / 가정
- 화면 동작(KPI, 요약 카드, 새로고침, 바로가기)은 유지한다
- 조회 실패 Dialog와 빈 데이터 재조회는 사용자 활동 상세와 같은 empty/retry UI로 맞춘다

## 승인 요청
이 계획대로 진행할까요, 아니면 조정할 부분이 있나요?
