# 평가 로그

## 컨텍스트
- 비교 감사에서 확인된 Comment 목록 stale-row correctness 위험을 첫 번째 승인 섹션으로 수정했다.

## 구조적 리스크
1. Comment, Proposal, Vote, Discussion이 동일한 freshness 불변식을 page-local로 각각 표현한다.
2. 범용 추상화를 추가하지 않은 만큼 향후 각 도메인 변경 시 동일 불변식이 누락될 수 있다.
3. 프로젝트 전체 lint 기존 오류와 TypeScript LSP 미설치가 변경 범위 밖 품질 신호를 제한한다.

## 왜 중요한가
- placeholder 목록 표시와 처리 가능성은 서로 다른 책임이다. freshness를 data/process/controller 경계에 명시해야 이전 응답을 잘못된 mutation 대상으로 사용하는 경쟁 조건을 막을 수 있다.

## 개선 옵션
1. 현재처럼 도메인별 data/process/controller 계약을 명시적으로 유지한다.
2. 세 개 이상 도메인의 입력·출력 계약이 완전히 같아질 때만 공용 helper 추출을 재평가한다.
3. 전체 lint와 LSP 환경은 별도 품질 인프라 섹션으로 해결한다.

## 권장 백로그
1. 승인된 다음 섹션인 Vote·Discussion `resetKey` 적용 시 같은 stale/draft 귀속 회귀를 함께 검증한다.
2. Proposal·Vote·Discussion cache race 제거를 별도 섹션으로 수행한다.
3. 전역 freshness 추상화는 현재 4조건이 충족되지 않으므로 보류한다.

## 다음 단계 제안
- Watcher가 현재 Comment 변경을 `confirmed`한 뒤에만 사용자 승인 순서의 다음 섹션으로 이동한다.
