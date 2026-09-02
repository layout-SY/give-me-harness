# 구현 로그

## 작업 요약
- 게시판 목록/상세를 fixture 직접 import에서 query hook + MSW로 전환하고, page → controller → view 구조로 분리했다.

## 재사용 자산
- 댓글 목록 search/data/process, 설문/정책 상세 query·process mutation, FilterBar/KpiStrip/MasterDetailLayout, BulkHidePopup, ChoiceChipGroup, Table

## 신규 파일 / 수정 파일
- entities/cp-board: dto/parser, createCpBoardApi, list/detail query, process/bulk-hide mutation, query-keys
- mocks/cp-board.handlers.ts 등록
- pages/cp-board: hook/model/ui 세그먼트, 목록·상세 view

## 핵심 로직
- 목록 필터는 검색 제출 시에만 query key에 반영한다.
- process는 변경된 state/type만 payload로 보낸다.
- 일괄 숨김은 다중 선택 UI 없이 현재 선택 행 1건을 대상으로 한다.
- 페이지는 fixture를 import하지 않는다.

## 검증 / 요청 처리
- yarn tsc --noEmit, yarn eslint 대상 경로 통과
- 브라우저: `/cp/boards` KPI·목록 렌더, BD-01002 숨김 저장 후 목록 반영, 상세에서 숨김 확인, `/cp/boards/BD-00001` 조회 실패 + 다시 조회

## 리스크
- 공지 등록/수정은 아직 fixture 화면이다.
- 서버 계약은 MSW 임시 계약이다.

## 핸드오프 메모
- 상태: `paused_after_generator`
- Watcher `confirmed` 전 Closure/portfolio 보류
