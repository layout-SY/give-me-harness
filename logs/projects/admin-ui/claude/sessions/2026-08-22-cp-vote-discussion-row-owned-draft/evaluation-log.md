# 평가 로그

## 컨텍스트
- 승인된 `resetKey` 후속 섹션을 탐색하면서 동일한 소유권 누락이 공개 기준 draft에도 존재함을 확인해 사용자의 추가 승인을 받고 함께 수정했다.

## 구조적 리스크
1. 상태 draft는 공용 `useStatusTransition`이 소유권을 캡슐화하지만 공개 기준 draft는 각 도메인 process가 행 소유권을 직접 모델링한다.
2. 현재 공개 기준 선택지가 하나라 공개 기준 payload 위험이 일반 UI 입력만으로 드러나지 않아 향후 선택지 확대 시 회귀 가능성이 있다.
3. test runner와 TypeScript LSP 부재로 행 fallback 불변식을 자동화된 개발 피드백으로 고정하지 못했다.

## 왜 중요한가
- 선택형 관리자 목록에서 draft와 mutation 대상 ID의 소유권이 분리되면 UI는 새 행을 보여주면서 이전 행의 초안을 저장할 수 있다. 행 ID 귀속은 disabled 표현이 아니라 payload correctness 불변식이다.

## 개선 옵션
1. 현재처럼 각 process hook의 도메인 draft를 행 ID와 함께 저장한다.
2. 세 번째 동일 use case가 나타나고 입출력 계약이 동일할 때만 공용 row-owned draft helper를 검토한다.
3. test runner 도입 시 same-status fallback과 공개 기준 선택지 확대 시나리오를 우선 회귀 테스트로 추가한다.

## 권장 백로그
1. 프로젝트 테스트 인프라가 마련되면 Vote·Discussion same-query fallback 회귀를 자동화한다.
2. Vote 날짜 placeholder 줄바꿈과 실제 날짜 범위 검증은 승인된 별도 섹션에서 처리한다.
3. 다음 승인 섹션인 Proposal·Vote·Discussion cache race 제거는 현재 draft 귀속 계약을 보존해야 한다.

## 다음 단계 제안
- Watcher가 현재 변경을 `confirmed`한 뒤에만 다음 승인 섹션으로 이동한다.
