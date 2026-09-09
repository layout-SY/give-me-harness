# 평가 로그

## 컨텍스트
- process mutation의 authoritative detail cache가 이전에 시작된 list/detail 응답으로 되돌아갈 수 있는 race를 세 도메인의 공통 lifecycle로 제거했다.

## 구조적 리스크
1. 세 mutation hook에 동일한 짧은 lifecycle이 반복되지만 도메인별 key factory와 ID 계약이 달라 현재는 로컬 구현이 더 명확하다.
2. 서버 list read-after-write가 eventual consistency로 바뀌면 active list refetch가 mutation 직후 이전 값을 받을 수 있으며 별도 write-through 정책이 필요하다.
3. test runner와 TypeScript LSP 부재로 cancellation·late resolve 불변식을 자동 개발 피드백으로 고정하지 못했다.

## 왜 중요한가
- mutation 성공 응답은 authoritative하지만, 이전 GET의 완료 순서가 늦다는 이유만으로 관리자 화면이 과거 상태로 돌아가면 저장 성공과 표시 상태가 모순된다.

## 개선 옵션
1. 현재처럼 성공 시 list prefix와 target exact detail만 취소하고 authoritative detail을 기록한다.
2. 세 번째 이상의 다른 도메인이 같은 key·ID·failure 계약까지 공유할 때만 mutation lifecycle helper를 검토한다.
3. 테스트 인프라 도입 시 abort signal, late stale resolve, inactive invalid 상태, 실패 no-op을 브라우저 또는 integration test로 고정한다.

## 권장 백로그
1. 프로젝트 test runner 도입 후 세 도메인의 cache race 시나리오를 자동화한다.
2. 서버 consistency 계약이 바뀌면 list cache write-through 또는 지연 refetch 정책을 별도 설계한다.
3. TypeScript LSP와 Watcher 실행 환경을 복구한다.

## 다음 단계 제안
- Watcher `confirmed` 후에만 Closure로 이동하고, 이후 승인 순서인 Vote·Discussion 날짜 검증을 별도 섹션으로 시작한다.
