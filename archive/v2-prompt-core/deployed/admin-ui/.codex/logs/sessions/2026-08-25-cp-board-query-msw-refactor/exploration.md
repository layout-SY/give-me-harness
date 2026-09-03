# 탐색 기록

## 대상 경로
- src/shared/ui/
- src/widgets/
- src/pages/cp-board
- src/entities/cp-board
- src/pages/cp-comment, src/pages/cp-survey, src/pages/cp-policy
- .codex/memory/reusable-assets.md

## 발견한 기존 재사용 자산
- 발견 항목: FilterBar/KpiStrip/MasterDetailLayout/PageHeader, Table, ChoiceChipGroup, BulkHidePopup, Dialog
- 재사용 제안: 댓글 목록의 search/data/process 분리, 설문/정책의 detail query + process mutation + 조회 실패 다시 조회
- 근거: 게시판 목록도 마스터-디테일 + 처리 저장이고, 상세는 상태/유형 변경 저장이다

## 재사용이 어려운 자산
- 자산: 공용 CP 목록 컨트롤러
- 부적합 사유: 도메인별 필터·처리 필드가 다르고 공용 추상화 금지

## 신규 자산 필요성
- 필요 항목: cp-board DTO/parser/query/MSW, 페이지 hook/model/ui 분리
- 필요 이유: 엔티티 API가 구형 AxiosInstance 모듈이고 페이지가 fixture를 직접 그린다
