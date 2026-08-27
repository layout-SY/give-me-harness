# 계획

## 요청 요약
- 메인 노출 관리 화면을 fixture 직접 import에서 query hook + MSW 패턴으로 전환하고 controller-view로 분리한다.

## 작업 유형
- hybrid (feat + refactor)

## 범위
- `entities/cp-main-display`: DTO/parser/overview query/save·publish mutation
- `mocks/cp-main-display.handlers.ts`
- `pages/cp-main-display`: page → controller → process → view

## 제외 범위
- 보상, 운영 정책
- 공지 폼의 메인 노출 필드와 실시간 동기화
- 공용 CP 목록 컨트롤러 추출

## 섹션
1. 엔티티 API 계약과 query/mutation
2. MSW handler
3. 메인 노출 controller-view

## 필요 에이전트
- Generator

## 필요 스킬
- policy/tanstack-query, recipe/api-authoring, policy/hook-extraction, policy/coding-convention

## 리스크 / 가정
- 서버 계약은 MSW 임시 계약이다.
- 저장은 설정만 유지하고, 저장 및 반영은 동일 설정을 publish 엔드포인트로 보낸다.
