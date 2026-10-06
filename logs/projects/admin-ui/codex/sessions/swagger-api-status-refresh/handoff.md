# 이용 내역 API·controller 인계

## 최신 상태: sy-main 병합 및 검증 완료 (2026-09-30)

- 사용자 터미널에서 생성한 병합 커밋 `987616b724273b63b1d8c7037679402ad26f7c87`을 기본 checkout의 `sy-main`에서 확인했다. 구현 `7ff8247`이 포함되어 있다.
- 해당 HEAD에서 관련 테스트 21개·lint·build를 재실행하여 모두 통과했고 Git 작업 트리는 깨끗하다.
- 이용 내역 branch·worktree는 그대로 보존했다. 이번 확인은 중앙 관계 완료 기록·push·정리를 수행하지 않았다.
- 후속 UI 연결은 미구현이다. 아래 커밋 전·병합 전 상태와 경로 목록은 과거 이력이며 재진입 시 실제 상태를 확인한다.

## 최신 상태: 커밋 완료

- `feature/usage-api-controller`의 현재 HEAD는 `7ff8247598322599c017208349d15ae85ba90b25`다. 메시지: `feat(usage): 이용 내역 API 계약 및 controller 구현`.
- 승인된 stage·commit 작업 `7e2d05453f625ae905730efa540ae1d5`는 done. 아래 나열한 변경 14개 파일이 모두 커밋됐고 staged·unstaged·untracked 변경은 없다.
- 작업 공간·직접 부모·공개 연결 계약은 그대로다. 아래 `c6ed8d3`와 미커밋 경로 목록은 구현 완료 당시의 기준·변경 이력이다.
- 병합·push·정리는 실행하지 않았다. 재진입 시 현재 HEAD와 status를 다시 확인한다.

## Assignment 이동과 역할 라우팅

- 보내는 host·session·role: Codex / swagger-api-status-refresh / Logic.
- 받는 host·session: 미정. 이 문서는 자동 구현·Git 승인이 아니다.
- requested_roles / confirmed_roles / completed_roles: Logic / Logic(inject) / 이용 내역 API·query·controller 구현 및 로컬 검증.
- next_role: UI 연결이 요청되면 UI. Git 처리만 요청되면 현재 작업을 읽어 별도 승인 흐름으로 진행한다.
- 사용자 확인: 별도 브랜치·워크트리, 화면 없는 controller까지, 날짜 입력 후 조회·역전 차단·검색 쌍 입력, 응답 필수·null 허용·objectName 보정, 이후 명시적 `진행` 승인.

## 목표 및 현재 상태

포인트·아이템 이용 내역 API의 저장된 Swagger 계약을 보정하고 UI 연결용 controller를 제공했다. 테스트 21개·lint·build·포맷·diff 검사 완료. 미커밋·미병합이며 화면은 구현하지 않았다.

## 완료된 작업과 결정

- GET `/admin/usage/point`, `/admin/usage/item`; 기존 공통 ApiClient·페이지 DTO/schema·query key/options/hook·취소 경계 재사용.
- 날짜 형식 YYYY-MM-DD, 필수 startDate/endDate, startDate ≤ endDate. 임의 기본 기간/최대 기간/시간대 변환 없음.
- 포인트 by: USER_ID/USER_NAME. 아이템 by: USER_ID/USER_NAME/ITEM_NAME. 검색 기준·검색어를 함께 입력하며 둘 다 없는 조회도 허용한다. controller는 검색어 양끝 공백을 제거한다.
- page/size 기본 1/20, 기존 반복 sort 형식 유지. 새 검색은 첫 페이지부터, 페이지 이동은 입력 중 초안이 아닌 적용 조건으로 요청한다.
- 행 필드는 필수·null 허용. objectName·명세 enum·정수를 검증하고 null·서버 순서·날짜 원문을 유지한다.
- 입력이 확정되기 전 query는 null/skipToken이며 가짜 날짜나 요청을 만들지 않는다.

## 보내는 작업의 위치와 변경 상태

- project·기본 저장소: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`.
- branch·HEAD: `feature/usage-api-controller@c6ed8d3c09fe3d4ecedd608f2c314795038d5b73`.
- worktree·실행 디렉터리: `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/usage-api-controller`.
- 확인 시점: 최종 구현·검증 후. 부모 sy-main은 `bc579b39278387f9b2e5b6f5bcce4a274249308c`로 진행했으며 기본 checkout은 깨끗했다.
- 완료한 기능 commit: 없음. staged: 없음.
- unstaged: `src/entities/usage/api/admin-usage.api.ts`, `admin-usage.dto.ts`, `api/index.ts`, `entities/usage/index.ts`, `hook/use-point-usage-list-query.ts`, `hook/use-item-usage-list-query.ts`, `model/admin-usage-query-keys.ts`, `model/admin-usage-query-options.ts`, `tests/usage-contract.test.mjs`, `tests/usage-query.test.mjs`.
- untracked: `src/pages/usage/index.ts`, `src/pages/usage/model/usage-controller.types.ts`, `src/pages/usage/hook/use-usage-controller.ts`, `tests/usage-controller.test.mjs`.
- ignored: 설치한 node_modules와 build dist, 세션 기록은 기본 checkout에 있다. 기존 다른 작업자의 파일은 변경하지 않았다.

## 인계 대상 작업 공간

### 작업 공간: usage-api-controller

- 목적지: 위 실재하는 동일 branch·worktree·실행 디렉터리. 생성 완료한 공간이므로 재생성하지 않는다.
- 직접 부모: sy-main. 승인된 관계 생성 작업 `7af0e8a93daa4b3992409c2217cf8796`의 done 결과로 확인했다.
- 기능: 이미 작성된 Logic 계약을 활용하는 순차 UI 연결 또는 별도 승인한 Git 처리.
- Logic → UI는 같은 공간에서 순차 작업을 제안한다. 실제 병렬 작업이 필요하면 별도 공간과 부모 관계를 먼저 확정한다.
- 진입 전 실제 HEAD·status·작업 중인 쓰기를 확인하고 위 미커밋/미추적 구현을 보존한다. 상태가 달라지면 변경 차이를 읽는다.
- 생성만 승인·완료. stage·commit·merge·push·정리는 미승인이다.

## 역할별 상세 작업: 후속 UI 연결

- 선행 구현: Logic. `controller <- UI` 방향으로 UI가 공개 계약에 맞춘다.
- 공개 진입: `~/pages/usage`의 `usePointUsageController`, `useItemUsageController`, `PointUsageController`, `ItemUsageController`, `UsageSearchFields`.
- 구현·타입: `src/pages/usage/hook/use-usage-controller.ts`, `src/pages/usage/model/usage-controller.types.ts`.
- `search`: startDate/endDate/by/keyword/sort, byOptions, canSubmit, validationMessage, onChange(Partial), onSubmit():boolean, onReset(). 초안 수정만으로 조회하지 않는다.
- `appliedQuery`: 현재 결과의 조회 조건 또는 null. 포인트/아이템별 요청 타입을 보존한다.
- `table`: rows, page/pageSize/pageCount/total, onPageChange(). 데이터가 없으면 메타는 undefined다. null 행 값을 임의 ID/0/빈 문자열로 치환하지 않는다.
- `hasSearched`는 입력 대기와 조회를 구분한다. `isEmpty`는 조회 성공 후 빈 배열에만 true다.
- `load`: isPending/isFetching/isFailed/errorMessage/onRetry(). 조회 전 재시도는 요청하지 않는다. 기존 전역 오류 reporter를 유지하며 UI에서 별도 중복 알림을 추가하지 않도록 확인한다.
- 필요한 UI: 기간 입력·검색·정렬·목록·페이지·오류/재시도·대기/빈 결과 표현. JSX·라우트·메뉴는 이번에 만들지 않았다. 화면 경로·메뉴 위치·표시 열·정렬 UI는 사용자에게 확정받아야 한다.
- 재사용 후보: shared UI 테이블·입력·검색·페이지 컴포넌트와 인접 inquiry/news 화면. UI 담당이 실제 props 적합성을 조사하고 ui-library 자산 계획을 작성한다. 이 Logic 작업에는 UI 선정 승인이 없다.
- 선행 조건/순서: 최신 코드·상태 확인 → UI 범위/자산/경로 승인 → 같은 공간에서 UI 구현 → API·controller 회귀 및 UI 검증 → 결과 인계.
- 겹침: entities/usage와 공개 controller의 계약을 임의 변경하지 않는다. 필요한 항목이 맞지 않으면 차이와 영향을 먼저 보고한다.

## 협업 순서와 Git 통합

- source 편집은 종료했다. 다음 작업자는 같은 공간의 미커밋 변경을 보존하고 순차 진행한다.
- 통합 대상은 직접 부모 sy-main. 부모가 분기 후 전진했으므로 통합 시 최신 변경·형제·계약·미커밋 상태를 다시 검토한다.
- source 검증 통과를 부모와의 병합 검증으로 해석하지 않는다. 안전한 정리도 별도 승인 범위를 확인한다.
- 산출물 책임: owner. 후속 세션은 자기 산출물을 작성하고 이 세션 문서는 읽기 전용으로 참조한다.

## 관련 경로와 스킬

- 명세: 기본 checkout의 `.codex/logs/sessions/swagger-api-coverage-audit/unknown/openapi.snapshot.json`, api-contracts.md, api-schema-catalog.md. ignored 기록이라 새 clone에 자동 포함되지 않는다.
- 사용 스킬: task-role-routing, git-branch-strategy, documentation, coding-convention, type-definition, data-fetch-layer, validation, implementation-quality, api-authoring 및 transport/query/controller 참조.
- UI 구현이 없으므로 UI 자산 선정 문서와 외부 UI 라이브러리 스킬 추가는 해당 없음.

## 명령어 및 결과

- 승인 관계 생성 execute: done.
- `npm ci --no-audit --no-fund`: 성공. package/lockfile 변경 없음.
- 중앙 `formatting.py apply`: 최종 변경 파일 실제 Prettier 실행 완료.
- `node --test tests/usage-contract.test.mjs tests/usage-query.test.mjs tests/usage-controller.test.mjs`: 21/21 통과.
- `npm run lint`, `npm run build`, `git diff --check`: exit 0.
- 기존 bundle 크기·vite-tsconfig-paths 안내는 남아 있으며 실패는 아니다.
- 중간 실패와 수정 근거는 final-summary.md에 기록했다.

## 실행하지 않은 검증과 다음 조치

원격 명세 재수집·실서버 업무 호출·실데이터·CORS·브라우저/시각 검증·별도 Watcher 에이전트 실행은 하지 않았다. 소스 구현과 로컬 검증은 완료했으며, 다음 기능/화면 구현이나 Git 변경은 사용자 요청에 따라 진행한다.
