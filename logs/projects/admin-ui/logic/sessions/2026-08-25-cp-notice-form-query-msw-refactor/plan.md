# 계획

## 요청 요약
- 공지 등록/수정 화면을 fixture 직접 import에서 query hook + MSW 패턴으로 전환하고 controller-view로 분리한다.

## 작업 유형
- hybrid (feat + refactor)

## 범위
- `entities/cp-notice`: DTO/parser/query/draft·publish mutation
- `mocks/cp-notice.handlers.ts`
- `pages/cp-board` 공지 폼: page → controller → process → view

## 제외 범위
- 공지 목록 화면 신설
- 게시판 목록에서 공지 폼으로의 진입 버튼 추가
- 신고/메인 노출/보상/운영 정책

## 섹션
1. 엔티티 API 계약과 query/mutation
2. MSW handler
3. 공지 폼 controller-view

## 필요 에이전트
- Generator

## 필요 스킬
- policy/tanstack-query, recipe/api-authoring, policy/hook-extraction, policy/coding-convention
