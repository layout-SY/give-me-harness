# 탐색 기록

## 대상 경로
- src/shared/ui/
- src/widgets/
- src/pages/cp-policy/ui
- src/pages/cp-vote/ui
- src/entities/cp-policy
- .agents/skills/reference/
- .codex/memory/reusable-assets.md

## 발견한 기존 재사용 자산
- 발견 항목: `useCpPolicyListQuery`, `useCpPolicyDetailQuery`, `useCpPolicyProcessMutation`, FilterBar, KpiStrip, MasterDetailLayout, Table, Dropdown, TextArea, TimelineList
- 재사용 제안: vote 목록/상세 controller-view 구조를 도메인 전용 훅으로 복제
- 근거: 공용 CP 목록 추상화 훅을 만들지 않기로 한 기존 결정과 동일하다

## 재사용이 어려운 자산
- 자산: 공용 목록 컨트롤러
- 부적합 사유: 정책반영은 stage/reflectionContent 처리와 KPI 라벨이 vote와 다르다

## 신규 자산 필요성
- 필요 항목: 정책반영 전용 search/data/process/controller/view
- 필요 이유: 페이지 fixture 직접 import를 제거하고 query/MSW 패턴에 맞춘다
