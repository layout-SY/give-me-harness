# 탐색 기록

## 대상 경로
- src/pages/cp-operation-policy/ui
- src/entities/cp-operation-policy
- src/features/cp-policy-apply
- src/pages/cp-reward (정책 저장/적용)
- src/shared/ui, src/widgets/admin-page-layout

## 발견한 기존 재사용 자산
- 발견 항목: PolicyApplyPopup, PageHeader/KpiStrip/ActionBar, ChoiceChipGroup, 보상 정책 save/apply
- 재사용 제안: 보상 정책 overview query + dirty save, 적용은 PolicyApplyPopup 확인 후 apply mutation
- 근거: 운영 정책도 조회 후 초안 편집·저장·적용이다

## 재사용이 어려운 자산
- 자산: 공용 정책 컨트롤러, 보상 정책 필드
- 부적합 사유: 허용/차단·기본 노출 vocabulary가 다르다
- 자산: 정책반영 관리 (`/v1/cp/policies`)
- 부적합 사유: 운영 정책 엔드포인트와 도메인이 다르다

## 신규 자산 필요성
- 필요 항목: 운영 정책 DTO/parser/query/save·apply mutation, 화면 hook/model/lib/ui
- 필요 이유: 엔티티 API가 구형 Axios 모듈이고 페이지가 fixture를 직접 그린다
