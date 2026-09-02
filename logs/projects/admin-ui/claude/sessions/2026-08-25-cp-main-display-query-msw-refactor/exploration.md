# 탐색 기록

## 대상 경로
- src/pages/cp-main-display/ui
- src/entities/cp-main-display
- src/pages/cp-dashboard (overview query)
- src/pages/cp-board (process mutation, 조회 실패)
- src/shared/ui, src/widgets/admin-page-layout
- .codex/memory/reusable-assets.md

## 발견한 기존 재사용 자산
- 발견 항목: PageHeader/KpiStrip/ActionBar, ChoiceChipGroup, 대시보드 overview query, 게시판 process mutation
- 재사용 제안: overview query + 선택 항목 draft process + 조회 실패 다시 조회
- 근거: 단건 overview를 조회한 뒤 항목 노출 상태를 저장/반영하는 화면이다

## 재사용이 어려운 자산
- 자산: 게시판/신고 목록 컨트롤러
- 부적합 사유: 메인 노출은 테이블 목록이 아니라 배너·콘텐츠·공지 섹션 overview다
- 자산: 공지 draft/publish payload
- 부적합 사유: 필드와 엔드포인트가 다르다

## 신규 자산 필요성
- 필요 항목: cp-main-display DTO/parser/query/MSW, 페이지 hook/model/lib/ui
- 필요 이유: 엔티티 API가 구형 모듈이고 페이지가 fixture를 직접 그린다
