# 구현 로그

## 작업 요약
- 메인 노출 관리 화면을 fixture 직접 import에서 query hook + MSW로 전환하고, page → controller → process → view 구조로 분리했다.

## 재사용 자산
- 대시보드 overview query, 게시판 process mutation, PageHeader/KpiStrip/ActionBar, ChoiceChipGroup

## 신규 파일 / 수정 파일
- entities/cp-main-display: dto/parser, createCpMainDisplayApi, overview query, save/publish mutation, query-keys
- mocks/cp-main-display.handlers.ts 등록
- pages/cp-main-display: hook/model/lib/ui, 페이지 전용 CSS를 view로 이동

## 핵심 로직
- GET `/v1/cp/main-display`로 overview를 조회한다.
- 저장은 변경분이 있을 때만 POST `/v1/cp/main-display/save`를 보낸다.
- 저장 및 반영은 현재 설정을 POST `/v1/cp/main-display/publish`로 보낸다.
- payload는 배너·주요 콘텐츠·공지 목록이며, 항목 ID/제목/순서는 유지하고 노출 상태만 바꾼다.
- 페이지는 fixture를 import하지 않는다.

## 검증 / 요청 처리
- yarn tsc --noEmit, yarn eslint 대상 경로 통과
- 브라우저 `/cp/main-display`: KPI 3/5/1, 배너 비노출 저장 Dialog, 저장 및 반영 Dialog

## 리스크
- 서버 계약은 MSW 임시 계약이다. 공용 ApiClient에 put이 없어 저장/반영은 POST로 정의했다.
- 공지 폼의 메인 노출 필드와는 실시간 동기화하지 않는다.

## 핸드오프 메모
- 상태: `paused_after_generator`
- Watcher `confirmed` 전 Closure/portfolio 보류
