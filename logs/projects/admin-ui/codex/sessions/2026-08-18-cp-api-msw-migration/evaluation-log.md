# 평가 로그

## 평가

- MSW bootstrap 위에 첫 실제 CP 도메인 수직 슬라이스가 연결되었다.
- 서버 응답은 `unknown`에서 Zod parser를 통과하므로 TypeScript 선언만 신뢰하지 않는다.
- TanStack Query가 요청 취소, 캐시 유지, retry와 새로고침 상태를 소유하며 기존 `useApi` 화면과 병행한다.
- fixture는 MSW handler의 초기 데이터로만 남아 실제 HTTP 경계를 유지한다.
- `recipe-api-authoring`과 `policy-tanstack-query`가 후속 CP 도메인의 반복 계약을 명시한다.
- 전체 저장소 품질 게이트는 기존 TypeScript·lint 부채로 차단되지만 현재 변경 대상 검증은 통과했다.
- 1280px 관리자 화면은 정상이며 좁은 viewport의 기존 고정폭 부채는 별도 개선 대상이다.

## Evaluator 권고

- 지정 Evaluator는 최초 inactivity timeout 후 재시도에서 Anthropic API 크레딧 부족으로 실행되지 못했으며 독립 대체 Evaluator가 장기 평가를 수행했다.
- 다음 수직 슬라이스는 Dashboard와 인접하고 첫 mutation·최소 invalidation을 검증할 수 있는 `CP Main Display`가 적합하다.
- 이후 권장 순서는 `Proposal → Vote → Discussion → Survey → Policy → Comment → Report → Board → Activity Log → Reward → Operation Policy`다.
- Dashboard DTO와 도메인 모델이 동일 구조로 중복되므로 후속 도메인에서 schema 추론과 명시적 mapping 중 기준을 확정해야 한다.
- `mainDisplay.status`의 unrestricted `string`은 실제 backend vocabulary가 확정될 때 closed vocabulary로 좁힌다.
- CP handler 누락을 bypass가 숨기지 않도록 전환된 endpoint의 브라우저 네트워크 검증을 각 섹션에서 유지한다.
- mutation 도메인은 최소 query invalidation, 중복 제출 방지, 부분 실패와 감사 이력 정책을 먼저 정한다.
