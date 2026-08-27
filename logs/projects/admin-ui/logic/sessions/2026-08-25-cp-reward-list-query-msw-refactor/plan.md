# 계획

## 요청 요약
- 보상/포인트 지급 목록을 fixture 직접 import에서 query hook + MSW 패턴으로 전환하고 controller-view로 분리한다.

## 작업 유형
- hybrid (feat + refactor)

## 범위
- `entities/cp-reward`: 지급 대상 목록 DTO/parser/query/pay mutation
- `mocks/cp-reward.handlers.ts`
- `pages/cp-reward` 지급 목록: page → controller → search/data/pay → view
- `RewardPayPopup` 확인 후 실제 pay mutation 연결

## 제외 범위
- 보상/포인트 정책 설정 화면
- 운영 정책
- 공용 CP 목록 컨트롤러 추출

## 섹션
1. 엔티티 API 계약과 query/mutation
2. MSW handler
3. 지급 목록 controller-view

## 필요 에이전트
- Generator

## 필요 스킬
- policy/tanstack-query, recipe/api-authoring, policy/hook-extraction, policy/coding-convention

## 리스크 / 가정
- 서버 계약은 MSW 임시 계약이다.
- 포인트 수치는 협의 확정값 전제라 임의 숫자를 두지 않는다.
