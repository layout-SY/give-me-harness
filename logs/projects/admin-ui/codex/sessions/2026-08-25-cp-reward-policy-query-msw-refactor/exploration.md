# 탐색 기록

## 대상 경로
- src/pages/cp-reward/ui/cp-reward-policy-page.tsx
- src/entities/cp-reward
- src/features/cp-policy-apply
- src/pages/cp-main-display, src/pages/cp-board (저장/반영)
- src/shared/ui, src/widgets/admin-page-layout

## 발견한 기존 재사용 자산
- 발견 항목: PageHeader/KpiStrip/ActionBar, SectionCard, PolicyApplyPopup, 메인 노출 save/publish mutation
- 재사용 제안: 메인 노출 overview query + dirty save, 적용은 PolicyApplyPopup 확인 후 apply mutation
- 근거: 정책 화면은 조회 후 초안 편집·저장·적용이다

## 재사용이 어려운 자산
- 자산: 공용 정책 컨트롤러, 운영 정책 화면
- 부적합 사유: 운영 정책은 다음 섹션이고, 보상 정책 필드(참여 기준/지급 제한)가 다르다
- 자산: 지급 목록 query
- 부적합 사유: 목록 KPI 포인트 라벨은 정책 수치를 노출하지 않는다

## 신규 자산 필요성
- 필요 항목: 정책 DTO/parser/query/save·apply mutation, 정책 화면 hook/model/lib/ui
- 필요 이유: 엔티티 API가 목록만 있고 페이지가 fixture를 직접 그린다
