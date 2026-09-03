# 구현 로그

## 작업 요약
- 신고 목록/상세를 fixture 직접 import에서 query hook + MSW로 전환하고, page → controller → view 구조로 분리했다.

## 재사용 자산
- 게시판 목록 search/data/process, 상세 query·process mutation, FilterBar/KpiStrip/MasterDetailLayout, ChoiceChipGroup, Table

## 신규 파일 / 수정 파일
- entities/cp-report: dto/parser, createCpReportApi, list/detail query, process mutation, query-keys, reasonType
- mocks/cp-report.handlers.ts 등록
- pages/cp-report: hook/model/ui 세그먼트, 목록·상세 view

## 핵심 로직
- 목록 필터는 검색 제출 시에만 query key에 반영한다.
- process는 변경된 status/exposureState/processMemo만 payload로 보낸다.
- 목록 처리는 상태·메모만 보내고, 콘텐츠 노출은 상세에서만 보낸다.
- 페이지는 fixture를 import하지 않는다.

## 검증 / 요청 처리
- yarn tsc --noEmit, yarn eslint 대상 경로 통과
- 브라우저: `/cp/reports` KPI 24건, RP-00182 검토중 저장 후 목록 반영(접수 5→4, 검토중 6→7)
- 상세에서 검토중·숨김 저장 후 이력·목록 반영, `/cp/reports/RP-00001` 조회 실패 + 다시 조회

## 리스크
- 서버 계약은 MSW 임시 계약이다.
- 닫힌 Dialog가 a11y 트리에 남는 현상은 기존 화면과 동일하게 보이며, 기능 버그로 단정하지 않았다.

## 핸드오프 메모
- 상태: `paused_after_generator`
- Watcher `confirmed` 전 Closure/portfolio 보류
