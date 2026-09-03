# 탐색 기록

## 대상 경로
- src/pages/cp-report/ui
- src/entities/cp-report
- src/pages/cp-board (목록·상세 query 패턴)
- src/shared/ui, src/widgets/admin-page-layout
- .codex/memory/reusable-assets.md

## 발견한 기존 재사용 자산
- 발견 항목: FilterBar/KpiStrip/MasterDetailLayout, ChoiceChipGroup, Table, 게시판 search/data/process/controller
- 재사용 제안: 게시판과 동일한 목록 검색 제출·process mutation·조회 실패 다시 조회
- 근거: 신고도 목록 마스터-디테일 + 단건 상세 처리 화면이다

## 재사용이 어려운 자산
- 자산: 게시판 bulk-hide, 공지 draft/publish
- 부적합 사유: 신고는 단건 처리 저장만 있고 엔드포인트·필드가 다르다
- 자산: 공용 CP 목록 컨트롤러
- 부적합 사유: 도메인 필터·처리 필드가 달라 공용 추상화를 만들지 않는다

## 신규 자산 필요성
- 필요 항목: cp-report DTO/parser/query/MSW, 목록·상세 hook/model/ui
- 필요 이유: 엔티티 API가 구형 모듈이고 페이지가 fixture를 직접 그린다
