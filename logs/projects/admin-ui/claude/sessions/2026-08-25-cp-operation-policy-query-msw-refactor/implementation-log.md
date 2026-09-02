# 구현 로그

## 작업 요약
- 시민참여 운영 정책 설정 화면을 fixture 직접 import에서 query hook + MSW로 전환하고, page → controller → process → view 구조로 분리했다.

## 재사용 자산
- 보상 정책 overview query와 dirty save/apply, PolicyApplyPopup, PageHeader/KpiStrip/ActionBar, ChoiceChipGroup

## 신규 파일 / 수정 파일
- entities/cp-operation-policy: dto/parser, createCpOperationPolicyApi, query·save·apply mutation, query-keys
- mocks/cp-operation-policy.handlers.ts, handlers.ts 등록
- pages/cp-operation-policy: hook/model/lib/ui, 얇은 page

## 핵심 로직
- GET `/v1/cp/operation-policy`로 정책을 조회한다. pathname 정규식으로 매칭한다.
- 저장은 변경분이 있을 때만 POST `/v1/cp/operation-policy/save`를 보낸다.
- 적용은 현재 초안을 POST `/v1/cp/operation-policy/apply`로 보낸다.
- payload는 postPermission/commentPermission/reportPermission/defaultExposure/changeReason이며, postLimitLabel·적용 상태는 서버가 유지·갱신한다.
- 페이지는 fixture를 import하지 않는다.

## 검증 / 요청 처리
- yarn tsc --noEmit, yarn eslint 대상 경로 통과
- 브라우저 `/cp/operation-policy`: KPI 적용중 / 2026.07.15, 변경 사유 입력 후 저장 Dialog, 적용 후 마지막 적용 2026.08.25

## 리스크
- 서버 계약은 MSW 임시 계약이다. 공용 ApiClient에 put이 없어 저장/적용은 POST로 정의했다.
- 닫힌 Popup 문구가 a11y 트리에 남는 현상은 기존과 동일하다.

## 핸드오프 메모
- 상태: `paused_after_generator`
- Watcher `confirmed` 전 Closure/portfolio 보류
- 시민참여 fixture 전환 화면은 이 섹션으로 소진됐다.
