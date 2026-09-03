# 구현 기록

## 상태
- `paused_after_generator`
- 사유: 승인된 Generator 범위 구현을 완료했으며 Watcher는 외부 provider credit 소진으로 비가용하다.

## 변경 파일
- `src/pages/cp-comment/ui/use-cp-comment-list-data.tsx`
- `src/pages/cp-comment/ui/use-cp-comment-list-process.tsx`
- `src/pages/cp-comment/ui/use-cp-comment-list-controller.tsx`
- `src/pages/cp-comment/ui/cp-comment-list.types.ts`

## 구현 결론
- query의 `isPlaceholderData`를 화면 계약 `isCurrentData`로 변환했다.
- stale data에서는 process의 `selectedRow`를 `null`로 강제하고 직접 선택과 저장을 방어했다.
- `canSave`에 freshness를 포함했으며 `changeState`는 `selectedRow` 불변식을 그대로 재사용했다.
- controller는 현재 데이터일 때만 optional `onRowClick`을 제공한다.

## 재사용 자산
- Proposal/Vote/Discussion 목록의 `isCurrentData: !isPlaceholderData` 전달 패턴
- Proposal process의 stale selection/save guard 패턴
- `src/shared/ui/table/table.tsx`의 optional `onRowClick` 계약

## 범위 준수
- View, shared Table, entities, API, DTO, query key, mutation, CSS, markup, tests 및 다른 도메인은 수정하지 않았다.
- 신규 공용 추상화 없이 Comment 전용 네 파일만 최소 diff로 변경했다.

## 검증
- 변경 파일 diagnostics: TypeScript LSP가 설치되지 않았고 사용자 설치 거절 상태라 실행 불가. 네 파일 모두 동일한 `LSP server 'typescript' ... is NOT INSTALLED; user previously declined installation` 결과를 확인했다.
- 대체 compiler diagnostics + build: `yarn build` 통과 (`tsc -b && vite build`, 4,034 modules transformed). 기존 Vite tsconfig-paths 안내와 500 kB 초과 chunk 경고만 발생했다.
- scoped lint: `yarn eslint src/pages/cp-comment/ui/use-cp-comment-list-data.tsx src/pages/cp-comment/ui/use-cp-comment-list-process.tsx src/pages/cp-comment/ui/use-cp-comment-list-controller.tsx src/pages/cp-comment/ui/cp-comment-list.types.ts` 통과.
- 대상 source·session 산출물 `git diff --check` 통과.
- pure LOC: data 49, process 79, controller 67, types 49. 네 파일 모두 200 LOC 이하이다.
- 실제 브라우저 현재 데이터 상태에서 첫 행 자동 선택, 두 번째 행 클릭에 따른 상세 전환, 처리 상태 변경 후 저장 버튼 활성화를 확인했다.
- Comment 목록 GET을 15초 지연한 탭 전환에서 이전 행 9개는 유지됐지만 클릭 가능 행 0개, 선택 행 0개, 첫 행 `tabindex` 없음으로 확인됐다.
- stale 행을 직접 클릭하고 Enter를 입력해도 선택되지 않았고 상세는 `목록에서 댓글을 선택하세요.`를 유지했으며 처리 상태·저장 버튼은 모두 비활성 상태였다.
- 최신 응답 후 첫 행 선택, 행 클릭·키보드 계약, 상세 패널과 처리 상태 버튼이 복구됐다.
- 1391×1043 현재/placeholder 캡처에서 레이아웃·한글 표시 회귀가 없었고 fresh 독립 Visual QA Oracle 2회가 모두 `PASS`, 차단 0건을 반환했다.
- 브라우저 console error와 warning은 0건이었다.

## 실행 경로
- 구성된 Planner와 일반 Plan 에이전트는 외부 provider credit 소진으로 시작하지 못했다.
- 독립 planning 실행 경로가 승인 범위·비목표·검증 기준을 확정했고 해당 결과를 `plan.md`와 `exploration.md`에 기록했다.
- 구성된 Generator도 같은 외부 provider 차단으로 시작하지 못해 독립 Generator 실행 경로가 동일 역할 계약으로 네 파일만 구현했다.
- Oracle 시각 검토는 Watcher를 대체하지 않으며 브라우저 evidence의 독립 교차 검토로만 사용했다.

## 후속 게이트
- browser QA와 독립 시각 검토를 완료했다.
- 프로젝트 Watcher는 정책에 따라 호출하지 않았으며 실제 `confirmed` 판정이 남아 있다.
- Watcher의 `confirmed` 전에는 Closure와 완료 처리를 수행하지 않는다.
