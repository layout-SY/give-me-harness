# 구현 로그

## 작업 요약
- 공지 등록/수정 화면을 fixture 직접 import에서 query hook + MSW로 전환하고, page → controller → process → view 구조로 분리했다.

## 재사용 자산
- 설문 상세 query·기간 검증, 게시글 상세 조회 실패 다시 조회, NoticePublishPopup, PageHeader/ActionBar, ChoiceChipGroup

## 신규 파일 / 수정 파일
- entities/cp-notice: dto/parser, createCpNoticeApi, detail query, draft/publish mutation, query-keys
- mocks/cp-notice.handlers.ts 등록
- pages/cp-board: 공지 폼 hook/model/lib/ui, 얇은 page 진입점

## 핵심 로직
- GET `/v1/cp/notices/:noticeId`로 단건 조회한다.
- 임시 저장은 필수값·기간 유효·변경분이 있을 때만 POST `/v1/cp/notices/draft`를 보낸다.
- 게시는 동일 조건에서 NoticePublishPopup 확인 후 POST `/v1/cp/notices/:noticeId/publish`를 보낸다.
- 게시 상태 칩은 서버 `detail.state` 읽기 전용이고, 메인 노출만 편집한다.
- 페이지는 fixture를 import하지 않는다.

## 검증 / 요청 처리
- yarn tsc --noEmit, yarn eslint 대상 경로 통과
- 브라우저 `/cp/boards/notices/NT-00043/edit`: 제목 수정 후 임시 저장 Dialog, 공지 게시 확인 후 `PUBLISHED` 칩·「공지가 게시되었습니다.」
- `/cp/boards/notices/NT-00001/edit`: 조회 실패 Dialog + 「다시 조회」

## 리스크
- 닫힌 Popup의 확인 문구가 a11y 트리에 남는 현상은 게시판 일괄숨김과 동일하게 보이며, 기능 버그로 단정하지 않았다.
- 서버 계약은 MSW 임시 계약이다.

## 핸드오프 메모
- 상태: `paused_after_generator`
- Watcher `confirmed` 전 Closure/portfolio 보류
