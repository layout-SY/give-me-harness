# 탐색 기록

## 대상 경로
- src/pages/cp-board/ui/cp-notice-form-page.tsx
- src/entities/cp-notice
- src/features/cp-notice-publish
- src/pages/cp-survey, src/pages/cp-board (상세 패턴)

## 발견한 기존 재사용 자산
- 발견 항목: NoticePublishPopup, PageHeader/ActionBar, ChoiceChipGroup, 설문 상세의 기간 검증 lib, 게시글 상세의 query 실패 다시 조회
- 재사용 제안: 상세 query + process hook + 조회 실패 Dialog, 게시는 기존 팝업 확인 후 mutation
- 근거: 공지 폼은 상세 조회 후 임시 저장/게시 액션이 있는 단건 화면이다

## 재사용이 어려운 자산
- 자산: 게시판 process mutation
- 부적합 사유: 공지는 draft/publish 엔드포인트와 필드가 다르다

## 신규 자산 필요성
- 필요 항목: cp-notice DTO/parser/query/MSW, 공지 폼 hook/model/lib/ui
- 필요 이유: 엔티티 API가 구형 모듈이고 페이지가 fixture를 직접 그린다
