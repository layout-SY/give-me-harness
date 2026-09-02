# 계획

## 요청 요약
- 게시판 목록/상세를 fixture 직접 import에서 기존 CP 도메인과 같은 query hook + MSW 패턴으로 전환하고, controller-view + FSD 세그먼트로 리팩터한다.

## 작업 유형
- hybrid (feat + refactor)

## 범위
- `entities/cp-board`: DTO/parser/`createCpBoardApi`/list·detail query/process mutation
- `mocks/cp-board.handlers.ts` 등록
- `pages/cp-board` 목록·상세: page → controller → search/data/process → view

## 제외 범위
- 공지 등록/수정 (`cp-notice`, `/cp/boards/notices/:noticeId/edit`)
- 신고/메인 노출/보상/운영 정책
- 공용 CP 목록 추상화 훅
- 다중 선택 UI 신설 (일괄 숨김은 선택 행 1건 기준)

## 섹션
1. 엔티티 API 계약과 query/mutation
2. MSW handler
3. 목록 controller-view
4. 상세 controller-view

## 필요 에이전트
- Generator

## 필요 스킬
- policy/data-fetch-layer, policy/tanstack-query, recipe/api-authoring, recipe/data-dto
- policy/coding-convention, policy/hook-extraction, policy/type-definition

## 리스크 / 가정
- 서버 계약은 MSW 임시 계약이며 `/v1/cp/boards`를 유지한다.
- 목록 처리와 상세 처리는 동일 process mutation을 쓴다.
