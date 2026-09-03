# 탐색 기록

## 대상 경로
- src/pages/cp-reward/ui
- src/entities/cp-reward
- src/features/cp-reward-pay
- src/pages/cp-board, src/pages/cp-survey (목록 검색·기간)
- src/shared/ui, src/widgets/admin-page-layout
- .codex/memory/reusable-assets.md

## 발견한 기존 재사용 자산
- 발견 항목: FilterBar/KpiStrip/MasterDetailLayout, Table, DateRangeField, RewardPayPopup, 설문 목록 기간 검색
- 재사용 제안: 게시판/설문 목록 search/data + 지급은 RewardPayPopup 확인 후 mutation
- 근거: 지급 목록은 마스터-디테일 조회 후 단건 지급 액션이다

## 재사용이 어려운 자산
- 자산: 게시판 process mutation, 공용 목록 컨트롤러
- 부적합 사유: 지급은 상태 칩 편집이 아니라 PENDING만 지급 가능하다
- 자산: 보상 정책 화면
- 부적합 사유: 이번 섹션은 지급 목록만 진행한다

## 신규 자산 필요성
- 필요 항목: cp-reward 목록 DTO/parser/query/MSW, 지급 목록 hook/model/ui
- 필요 이유: 엔티티 API가 구형 모듈이고 페이지가 fixture를 직접 그린다
