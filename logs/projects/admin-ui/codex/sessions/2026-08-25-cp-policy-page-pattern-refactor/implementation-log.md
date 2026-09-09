# 구현 로그

## 작업 요약
- 정책반영 목록/상세를 vote와 같은 page → controller → view로 분해하고, 기존 entity query/mutation/MSW에 결선했다.

## 재사용 자산
- `useCpPolicyListQuery`, `useCpPolicyDetailQuery`, `useCpPolicyProcessMutation`
- `FilterBar`, `KpiStrip`, `MasterDetailLayout`, `Table`, `Dropdown`, `TextArea`, `TimelineList`

## 신규 파일 / 수정 파일
- 목록: search/data/process/controller/view/config/types
- 상세: process/controller/view/config/types
- 페이지 진입점은 얇게 유지

## 핵심 로직
- 목록 필터는 status/department/title/stage이며, KPI tab count는 status 적용 전 집합 기준이다
- 처리 저장은 단계 또는 반영내용이 바뀐 경우에만 mutation을 보낸다

## 검증 / 요청 처리
- `yarn tsc --noEmit`, `yarn eslint src/pages/cp-policy` 통과
- 브라우저(`http://localhost:2426/cp/policies`)에서 제목 검색·초기화, 처리 단계 저장, PL-001 상세 이동, 목록 복귀, 2페이지 이동을 확인했다

## 리스크
- 처리단계 드롭다운 재선택은 index -1이 될 수 있어 음수 index는 무시한다

## 핸드오프 메모
- 상태: `paused_after_generator`
