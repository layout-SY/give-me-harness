# 리뷰 로그

## 리뷰 대상
- Proposal·Vote·Discussion process mutation 성공과 기존 list/detail query의 cache race.
- list prefix, target exact detail, sibling detail의 cancellation 범위와 실패 의미론.

## 결과
- `paused_after_generator`
- 구현, 정적 검증, 실제 브라우저 runtime 회귀는 통과했지만 Watcher를 실행하지 못해 `confirmed` 또는 Closure로 처리하지 않는다.

## 체크리스트 검토
- SKILL 준수: `policy-harness`, `policy-coding-convention`, `policy-tanstack-query`, `policy-data-fetch-layer`, `policy-refactoring`, `policy-abstraction-strategy`, `policy-type-definition`, `policy-documentation`, `policy-review-checklist`, `recipe-api-authoring`, `programming`, `playwright`, `debugging` 확인.
- 재사용 확인: 기존 도메인 query key factory, QueryClient, authoritative mutation response, list invalidation 계약을 재사용했다.
- 범위 확인: source 변경은 세 entity process mutation hook으로 제한했다. API, DTO, parser, query hook, caller, UI는 변경하지 않았다.
- cancellation: list prefix 전체와 mutation 대상 exact detail을 `Promise.all`로 병렬 취소하고 모두 완료될 때까지 기다린다.
- cache write: cancellation 완료 후 mutation parser를 통과한 detail을 exact key에 기록한다.
- invalidation: list prefix만 invalidate하고 active refetch 완료를 hook-level lifecycle에서 기다린다.
- exact 범위: sibling detail은 abort되지 않고 늦은 응답을 정상 반영했다.
- inactive list: abort 후 이전 cache를 유지하고 invalid 상태·idle fetch 상태로 남았다.
- 실패 의미론: 실패 mutation에서 cancellation, cache write, invalidation은 모두 0건이었다.
- surface callback: 성공 `success → settled → resolved`, 실패 `error → settled → caught` 순서를 확인했다.
- 정적 검증: scoped ESLint, `yarn build`, scoped diff check 통과.
- 브라우저 검증: 세 도메인 성공·실패 총 6개 process POST가 MSW runtime handler를 통과했고 모든 assertion이 통과했다.
- cleanup: runtime handler reset, QA DOM 0건, console error·warning 0건 확인.
- 성능·중복: cancellation 두 건은 병렬이며 각 파일 34줄로 공용 helper 추출 조건을 충족하지 않는다.

## 위반 사항 / 차단
1. TypeScript LSP가 설치되지 않아 LSP diagnostics를 실행하지 못했다.
2. Bun이 설치되지 않아 programming no-excuse script를 실행하지 못했다.
3. 프로젝트 test runner script가 없어 자동 회귀 테스트가 없다.
4. 구성된 Generator는 외부 provider credit 소진으로 시작하지 못해 동일 역할 계약의 독립 실행 경로를 사용했다.
5. Watcher API 비가용으로 실제 `confirmed` verdict가 없다.

## 필수 수정 사항
- 현재 승인 범위에서 추가 수정 사항은 발견되지 않았다.
- Closure 전 프로젝트 Watcher의 실제 `confirmed` 판정이 필요하다.

## 반복 이슈
- false

## 에스컬레이션
- 외부 의존성 차단: 구성된 Generator·Watcher 실행 환경.
