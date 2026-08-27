# 구현 로그

## 작업 요약
- 보상/포인트 지급 목록을 fixture 직접 import에서 query hook + MSW로 전환하고, page → controller → search/data/pay → view 구조로 분리했다.

## 재사용 자산
- 설문/게시판 목록 search-data 패턴, FilterBar/KpiStrip/MasterDetailLayout, DateRangeField, RewardPayPopup, ChoiceChipGroup(읽기 전용)

## 신규 파일 / 수정 파일
- entities/cp-reward: dto/parser, createCpRewardApi(getTargets/pay), target list query, pay mutation, query-keys
- mocks/cp-reward.handlers.ts 등록
- pages/cp-reward: 지급 목록 hook/model/view, 얇은 page
- RewardPayPopup: isConfirming 시 버튼 비활성

## 핵심 로직
- GET `/v1/cp/rewards/targets`로 지급 대상을 조회한다. 검색·기간은 제출 시에만 query key에 반영한다.
- POST `/v1/cp/rewards/targets/:targetId/pay`는 PENDING만 COMPLETED로 바꾼다.
- 포인트 수치는 협의 확정값 전제라 `pointLabel: "정책값"`, KPI `pendingPointLabel: "정책 기준"`만 둔다.
- 지급 상태 칩은 읽기 전용이고, PENDING일 때만 지급 팝업을 연다.
- 페이지는 fixture를 import하지 않는다.
- 목록 GET은 pathname 정규식으로 매칭한다. 문자열 `*` 경로는 한글 `user` query에서 unhandled가 되었다.

## 검증 / 요청 처리
- yarn tsc --noEmit, yarn eslint 대상 경로 통과
- 브라우저 `/cp/rewards`: KPI 지급대기 8건 / 지급완료 16건 / 대기 포인트 정책 기준, 1페이지 `RW-00182`, 2페이지 `RW-00172`, 사용자 「홍길동」 조회 후 대기 2건·완료 4건
- 지급 확인 클릭은 브라우저 승인 거절로 실행하지 않았다. PENDING 행에서 「보상 지급」 버튼은 활성 상태였다.

## 리스크
- 서버 계약은 MSW 임시 계약이다. 공용 ApiClient에 put이 없다.
- 정책 설정 화면은 이번 섹션 범위 밖이며 계속 fixture를 쓴다.
- 닫힌 RewardPayPopup 문구가 a11y 트리에 남는 현상은 기존과 같다.

## 핸드오프 메모
- 상태: `paused_after_generator`
- Watcher `confirmed` 전 Closure/portfolio 보류
