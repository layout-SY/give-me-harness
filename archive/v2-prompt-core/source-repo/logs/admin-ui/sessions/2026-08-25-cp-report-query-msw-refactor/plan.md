# 계획

## 요청 요약
- 신고 목록/상세를 fixture 직접 import에서 query hook + MSW 패턴으로 전환하고 controller-view로 분리한다.

## 작업 유형
- hybrid (feat + refactor)

## 범위
- `entities/cp-report`: DTO/parser/query/process mutation
- `mocks/cp-report.handlers.ts`
- `pages/cp-report`: 목록·상세 page → controller → process → view

## 제외 범위
- 메인 노출, 보상, 운영 정책
- 공용 CP 목록 컨트롤러 추출
- 신고 일괄 처리 UI 신설

## 섹션
1. 엔티티 API 계약과 query/mutation
2. MSW handler
3. 목록·상세 controller-view

## 필요 에이전트
- Generator

## 필요 스킬
- policy/tanstack-query, recipe/api-authoring, policy/hook-extraction, policy/coding-convention

## 리스크 / 가정
- 서버 계약은 MSW 임시 계약이다.
- 목록 처리 저장은 상태·메모만 보내고, 콘텐츠 노출은 상세에서만 보낸다.
