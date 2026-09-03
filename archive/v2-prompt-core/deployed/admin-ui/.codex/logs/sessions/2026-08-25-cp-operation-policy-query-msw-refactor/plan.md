# 계획

## 요청 요약
- 운영 정책 설정 화면을 fixture 직접 import에서 query hook + MSW 패턴으로 전환하고 controller-view로 분리한다.

## 작업 유형
- hybrid (feat + refactor)

## 범위
- `entities/cp-operation-policy`: 정책 조회 DTO/parser/query, save/apply mutation
- `mocks/cp-operation-policy.handlers.ts`
- `pages/cp-operation-policy`: page → controller → process → view

## 제외 범위
- 보상/포인트 정책
- 정책반영 관리
- 공용 정책 컨트롤러 추출

## 섹션
1. 엔티티 API 계약과 query/mutation
2. MSW handler
3. 운영 정책 화면 controller-view

## 필요 에이전트
- Generator

## 필요 스킬
- policy/tanstack-query, recipe/api-authoring, policy/hook-extraction, policy/coding-convention

## 리스크 / 가정
- 서버 계약은 MSW 임시 계약이다. 공용 ApiClient에 put이 없어 저장은 POST `/save`로 정의한다.
