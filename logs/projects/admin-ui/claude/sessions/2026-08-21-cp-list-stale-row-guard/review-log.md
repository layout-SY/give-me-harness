# 리뷰 로그

## 리뷰 대상
- Proposal·Discussion·Vote 목록의 stale `placeholderData` 처리 방어.
- Proposal 목록의 thin route page, search-state hook, controller hook, presentational view 책임 분리.
- Proposal controller의 data/process 책임 추가 분리와 View 계약 독립.

## 결과
- `paused_after_generator`
- 프로젝트 정책상 Claude Code API가 비가용하여 Watcher를 실행하지 않았다. 따라서 pass/confirmed 및 Closure로 처리하지 않는다.

## 체크리스트 검토
- SKILL 준수: `policy-harness`, `policy-coding-convention`, `policy-tanstack-query`, `policy-refactoring`, `policy-hook-extraction`, `policy-type-definition`, `programming`, `frontend`, `playwright`, `visual-qa` 확인.
- 재사용 확인: 기존 `isPlaceholderData`, `Table.onRowClick`, disabled 계약만 재사용했다.
- 검증 확인: 대상 ESLint·build·Playwright 기능 QA·9개 viewport 캡처의 독립 시각 QA 통과.
- Payload 완결성: API payload를 변경하지 않았다.
- 성능 우려: query 실행 횟수와 cache 정책을 변경하지 않았다.
- 중복 코드 우려: 세 도메인의 기존 page-local 결선에 동일 불변식을 명시했으며 범용 helper는 추가하지 않았다.
- 책임 분리 확인: Proposal route page는 controller와 view 결선만 수행하며 직접 state·query·mutation·router·Dialog 의존이 없다.
- 타입 계약 확인: controller 반환 계약은 interface, query·transition 같은 데이터 형태는 기존 type을 유지했다.
- 동작 보존 확인: 검색·행 선택·stale/settled 전환·상세 이동과 console error 0건을 실제 브라우저에서 확인했다.
- 시각 회귀 확인: 3개 viewport가 리팩터 전 기준 이미지와 모두 100/100 유사도였다.
- 상태 draft 귀속 확인: `useStatusTransition`은 `currentStatus`와 선택적 `resetKey`를 독립 추적하며 Proposal은 `selectedRow.id`를 전달한다.
- handler/payload 확인: 선택 ID 또는 현재 상태가 바뀌는 렌더에는 활성 `nextStatus`가 `null`이고 `canSaveProcess`와 mutation payload도 같은 값을 사용한다.
- data 책임 확인: entity query가 cache owner로 유지되고 page data hook은 오류 dedupe·stale 의미·KPI·pagination·retry만 파생한다.
- process 책임 확인: 선택·fallback·상태/부서 draft·mutation·저장 Dialog가 한 hook에 응집돼 reset 불변식이 controller로 누출되지 않는다.
- controller 확인: 72줄에서 search/data/process 조합, coordinated reset, contract 조립, navigation만 담당한다.
- 의존 방향 확인: View와 controller는 별도 contract를 공유하며 data/process/entity/shared에서 controller 또는 View로 역참조하지 않는다.
- 실제 mutation 확인: CP-002 상태 저장, 성공 Dialog, 선택 유지, draft reset, query invalidation 후 row 갱신을 브라우저에서 확인했다.
- 시각 검토 확인: 3개 viewport의 fresh reference/actual 비교와 독립 Oracle 2회 모두 PASS, 차단 0건이다.
- 코드 검토 확인: Oracle no-blocking. 서버 상태 복제·순환 의존·과분할이 없다.

## 자체 검토 이력
1. Oracle 1차: 같은 상태의 다른 제안으로 fallback될 때 이전 상태 draft가 남을 수 있는 차단 결함 1건 발견.
2. 수정: `useStatusTransition.resetKey` 추가와 Proposal `selectedRow.id` 결선.
3. 실제 회귀 QA: CP-001에서 CP-005로 같은 상태 fallback 시 draft 초기화·저장 비활성 확인.
4. Oracle 2차: 기존 `currentStatus` 초기화 보존, ID 초기화 추가, 저장/payload 게이트 확인. 차단 발견 0건.

## 위반 사항 / 차단
1. TypeScript LSP 미설치 상태로 diagnostics를 실행하지 못했다.
2. 전체 lint는 기존 73개 오류와 5개 경고로 실패했다. 이번 변경 대상 파일의 ESLint는 통과했다.
3. Planner·Generator 하위 에이전트는 외부 Anthropic 크레딧 차단으로 실행되지 않았다.
4. Watcher API 비가용으로 confirmed verdict가 없다.

## 필수 수정 사항
1. 현재 구현 범위의 추가 수정 사항은 발견되지 않았다.
2. Closure 전 실제 Watcher `confirmed` 판정이 필요하다.

## 잔여 관찰
- 375px Proposal 화면의 테이블·페이지네이션 우측 클리핑과 접힌 사이드바 폭은 기존 동작이며 별도 UI 개선 범위다.
- Discussion·Vote는 현재 `useStatusTransition.resetKey`를 전달하지 않으므로 controller 분리 시 선택 행 ID 귀속을 함께 적용해야 한다.
- process 내부 ID가 사라진 행을 기억한 채 UI는 첫 행으로 fallback하므로 같은 query에서 해당 ID가 다시 나타나면 선택이 복원될 수 있다. 현재 검색·페이지·mutation 경로는 reset돼 비차단 잠재 위험이다.
- 캐시가 있는 background refetch 실패에서는 오류 Dialog는 표시되지만 retry ActionBar는 노출되지 않는다. 기존 `data === undefined` 계약을 보존한 결과이며 UX 변경이 필요하면 별도 범위다.

## 반복 이슈
- false

## 에스컬레이션
- 외부 의존성 차단: Planner·Generator·Refactorer·Watcher 실행 환경.
