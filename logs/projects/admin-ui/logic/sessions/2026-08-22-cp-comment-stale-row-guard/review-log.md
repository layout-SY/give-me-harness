# 리뷰 로그

## 리뷰 대상
- Comment 목록의 `placeholderData` freshness 전달과 stale 행 선택·처리·저장 차단.
- 기존 View·shared Table·entity query 계약을 변경하지 않는 최소 diff 범위.

## 결과
- `paused_after_generator`
- 프로젝트 정책상 Watcher를 실행하지 않았으므로 `pass` 또는 `confirmed`로 판정하지 않으며 Closure를 수행하지 않는다.

## 체크리스트 검토
- SKILL 준수: `policy-harness`, `policy-coding-convention`, `policy-refactoring`, `policy-hook-extraction`, `policy-data-fetch-layer`, `policy-tanstack-query`, `policy-type-definition`, `policy-documentation`, `policy-abstraction-strategy`, `recipe-data-fetch`, `component-table`, `programming`, `frontend`, `playwright`, `visual-qa`를 확인했다.
- 재사용 확인: Proposal/Vote/Discussion의 `isCurrentData` 패턴과 기존 optional `Table.onRowClick`을 재사용했다.
- 범위 확인: Comment data/process/controller/types 네 파일만 변경했으며 View, shared UI, entity, API, DTO, mutation, CSS는 변경하지 않았다.
- 타입 확인: `isCurrentData`와 optional `onRowClick` 계약이 `tsc -b`를 포함한 production build를 통과했다.
- 선택 방어: placeholder에서는 `selectedRow=null`, 공개 `selectedRowId=null`, `processState=null`이다.
- 입력 방어: controller가 `onRowClick`을 제공하지 않고 process의 `selectRow`도 early return한다.
- mutation 방어: `canSave=false`이며 `save`가 freshness를 다시 검사한다.
- 현재 데이터 보존: 첫 행 fallback, 명시적 행 선택, 상태 변경 후 저장 활성화가 기존대로 동작한다.
- background refetch 보존: `isFetching`이 아닌 `isPlaceholderData`만 freshness 기준으로 사용한다.
- 정적 검증: 변경 파일 scoped ESLint, production build, scoped `git diff --check` 통과.
- 브라우저 검증: stale 행 9개가 남은 상태에서 클릭 가능 행 0개, 선택 행 0개, direct click·Enter 무효, 처리·저장 버튼 비활성, 최신 응답 후 정상 복구를 확인했다.
- 시각 검증: 1391×1043 현재/placeholder 두 상태에서 레이아웃·CJK 회귀가 없었고 독립 Visual QA Oracle 2회가 모두 `PASS`했다.
- console 확인: error 0건, warning 0건.

## 위반 사항 / 차단
1. TypeScript LSP가 설치되지 않아 LSP diagnostics를 실행하지 못했다. `tsc -b`가 포함된 build로 대체했다.
2. 전체 `yarn lint`는 선행 audit에서 기존 73개 오류와 5개 경고가 확인돼 이번 범위에서는 변경 파일 scoped lint만 실행했다.
3. 구성된 Planner·Plan·Generator 실행 경로는 외부 provider credit 소진으로 시작하지 못해 동일 역할 계약의 독립 실행 경로를 사용했다.
4. Watcher API 비가용으로 실제 `confirmed` verdict가 없다.

## 필수 수정 사항
- 현재 구현 범위에서 추가 수정 사항은 발견되지 않았다.
- Closure 전 프로젝트 Watcher의 실제 `confirmed` 판정이 필요하다.

## 잔여 관찰
- 비활성 저장 버튼의 연한 파란색 표현은 기존 shared Button 스타일이며 DOM `disabled`와 동작 차단은 정상이다.
- stale 행은 이전 목록 유지 UX를 위해 일반 명암을 유지하지만 선택 강조·포커스·입력 계약은 제거된다.

## 반복 이슈
- false

## 에스컬레이션
- 외부 의존성 차단: 구성된 Planner·Plan·Generator 및 Watcher 실행 환경.
