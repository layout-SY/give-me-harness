# 구현 로그

## 작업 요약
- 보상/포인트 정책 설정 화면을 fixture 직접 import에서 query hook + MSW로 전환하고, page → controller → process → view 구조로 분리했다.

## 재사용 자산
- 메인 노출 overview query와 dirty save, PolicyApplyPopup, PageHeader/KpiStrip/ActionBar

## 신규 파일 / 수정 파일
- entities/cp-reward: 정책 dto/parser, getPolicy/savePolicy/applyPolicy, query·save·apply mutation, query-keys.policy
- mocks/cp-reward.handlers.ts 정책 GET/save/apply
- pages/cp-reward: hook/model/lib/ui, 얇은 policy page
- PolicyApplyPopup: isConfirming 시 버튼 비활성

## 핵심 로직
- GET `/v1/cp/rewards/policy`로 정책을 조회한다.
- 저장은 변경분이 있을 때만 POST `/v1/cp/rewards/policy/save`를 보낸다.
- 적용은 현재 초안을 POST `/v1/cp/rewards/policy/apply`로 보낸다.
- payload는 참여 기준·지급 제한·변경 사유이며, 적용 범위/상태/기준일은 서버가 유지·갱신한다.
- 페이지는 fixture를 import하지 않는다.

## 검증 / 요청 처리
- yarn tsc --noEmit, yarn eslint 대상 경로 통과
- 브라우저 `/cp/rewards/policy`: KPI 적용중 / 2026.07.15, 변경 사유 입력 후 저장 Dialog, 적용 후 기준일 2026.08.25
- `/cp/rewards` 목록 KPI 8/16, `RW-00182` 유지

## 리스크
- 서버 계약은 MSW 임시 계약이다. 공용 ApiClient에 put이 없어 저장/적용은 POST로 정의했다.
- 지급 목록 포인트 라벨과는 실시간 동기화하지 않는다.

## 핸드오프 메모
- 상태: `paused_after_generator`
- Watcher `confirmed` 전 Closure/portfolio 보류
