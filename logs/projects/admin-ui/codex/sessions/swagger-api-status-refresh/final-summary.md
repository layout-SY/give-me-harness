# Swagger 작업 현황 갱신 결과

## 최신 상태: 수동 병합 확인 및 통합 검증 완료 (2026-09-30)

사용자의 터미널 실행 후 `sy-main@987616b724273b63b1d8c7037679402ad26f7c87`에서 병합을 확인했다. 부모는 `bc579b3`와 이용 내역 구현 `7ff8247`이며 구현 커밋의 포함 관계를 확인했다. 병합 후 기본 checkout에서 관련 테스트 21/21, lint, build를 다시 실행해 모두 exit 0으로 통과했다. 기존 Vite 플러그인 전환 안내·번들 크기 경고는 유지된다. 검증 후 Git 작업 트리는 깨끗하며 이용 내역 branch·worktree는 보존되어 있다. 이번 확인에서 Git 변경·push·중앙 관계 완료 기록은 실행하지 않았다. 아래 미병합 표기는 이전 시점의 이력이다.

## 커밋 완료

사용자 승인 후 보호 작업 `7e2d05453f625ae905730efa540ae1d5`를 한 번 실행하여 `feature/usage-api-controller`에 `7ff8247598322599c017208349d15ae85ba90b25` (`feat(usage): 이용 내역 API 계약 및 controller 구현`)를 생성했다. 14개 파일, 575줄 추가·110줄 삭제이며 커밋 후 staged·unstaged·untracked 변경이 없다. 검증한 코드에서 추가 소스 변경 없이 커밋했으며 기존 테스트 21개·lint·build 통과 결과가 적용된다. 병합·push는 실행하지 않았다. 아래 미커밋·승인 대기 표기는 각 시점의 이력이다.

## 최신 결과: 이용 내역 API·controller 구현 완료

사용자가 승인한 별도 작업 공간에서 포인트·아이템 이용 내역 API 계약을 보정하고 UI 없는 controller를 구현했다. **최종 관련 테스트 21/21, lint, build, git diff --check 통과.** 소스 변경은 아직 커밋·병합하지 않았다. 아래 이전 문서 갱신·승인 대기 기록은 이력이다.

- source: `feature/usage-api-controller@c6ed8d3c09fe3d4ecedd608f2c314795038d5b73` + 미커밋 변경.
- worktree: `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/usage-api-controller`.
- 문서 위치: 기본 checkout의 `.codex/logs/sessions/swagger-api-status-refresh/`. 논리적 세션 경로를 유지했다.
- 상세 인계: [handoff.md](./handoff.md).

### 실제 변경

1. 기존 `entities/usage` API·query를 재사용하여 `/admin/usage/point`, `/admin/usage/item`을 포인트·아이템별 요청 타입/schema로 연결했다. 날짜 필수·유효 달력일·역전 차단, 검색 기준 enum·검색어 쌍 입력, 반복 sort를 검증한다. 날짜 기본값이나 임의 최대 기간은 넣지 않았다. 페이지 기본값은 Swagger의 1·20이다.
2. 응답 필드 `itemName`을 명세 `objectName`으로 보정했다. 사용자 확정대로 모든 행 필드는 필수·null 허용이며 명세 enum·정수 형식을 적용한다. 공통 페이지 schema와 기존 parser를 재사용하고 서버 정렬·날짜·null 값을 보존한다.
3. query는 null 조건에 skipToken을 사용해 조회 전 요청을 만들지 않는다. 실제 요청에는 기존 ApiClient·인증·AbortSignal·평탄한 query·반복 sort 직렬화를 사용한다.
4. `src/pages/usage/`에 `usePointUsageController`, `useItemUsageController`와 공개 타입을 추가했다. 입력과 적용 조건 분리, 검색·초기화·페이지 이동·재시도, 조회 전·로딩·빈 결과·오류를 제공한다. 포인트/아이템의 appliedQuery 타입도 각각 구분한다. 기존 maintenance/inquiry/news controller 패턴을 참조했다.
5. 기존 contract/query 테스트를 확정 계약에 맞춰 갱신하고 controller 테스트 6개·미조회 query 테스트 1개를 추가했다. 예전 날짜 생략·검색 단독 입력·size 10·임의 enum/소수 기대값은 명세와 사용자 확정 계약에 맞춘 검증으로 교체했다. 새로운 테스트 프레임워크는 추가하지 않았다.

### 최종 검증

- `formatting.py apply`: 수정한 소스·테스트 14개 파일에 실제 중앙 Prettier 실행 완료, 최종 타입 보완 파일도 재포맷 완료.
- `node --test tests/usage-contract.test.mjs tests/usage-query.test.mjs tests/usage-controller.test.mjs`: 21/21 통과, exit 0.
- `npm run lint`: exit 0.
- `npm run build`: 타입 검증·Vite build exit 0. 기존 vite-tsconfig-paths 전환 안내와 500 kB 초과 번들 경고는 남아 있다.
- `git diff --check`: exit 0. 제거한 이전 요청 타입/schema 이름의 src/tests 참조 없음.
- 중간 실패: 신규 테스트 괄호 오류를 수정했다. SSR Probe에는 Query effect/구독이 없어 2개가 실패했으며, 최종 렌더의 실제 QueryObserver에 옵션 적용·구독을 수행하도록 테스트 lifecycle을 보완한 뒤 21개 모두 통과했다. 운영 코드에서 요청을 강제로 발생시키는 우회는 하지 않았다.
- 변경 검토: 두 endpoint·enum·응답 필드·공통 page 재사용, 조회 전 요청 없음, 취소·캐시·오류 계약을 코드와 실행 결과로 확인했다. 별도 리뷰 에이전트는 호출하지 않았다.

### 미완료·범위 밖

- UI 마크업·라우트·메뉴와 레거시 `/v1/usage`는 변경하지 않았다. 후속 UI는 `~/pages/usage`의 controller를 사용한다.
- 실제 서버 재조회·실데이터·CORS·브라우저 동작은 미검증이다. 로컬 테스트는 확인된 계약의 MSW 응답을 사용한다.
- 작업 commit·merge·push는 실행하지 않았다. 부모 sy-main은 작업 중 `bc579b39278387f9b2e5b6f5bcce4a274249308c`로 진행했다. 이번 검증은 source worktree의 코드 기준이며 최신 부모와의 통합 검증은 아니다.

## 이전 문서 갱신 기록

기존 Swagger 감사 이후의 커밋과 현재 코드를 대조하여 [API 작업 현황](./unknown/api-work-items.md)을 갱신했다. 원본 OpenAPI와 다른 세션 기록은 보존했다.

- 위치: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`, `sy-main@84d47a87f032ec5cc106f4fad8ec3a9709e901e1`.
- 요청/역할: 문서 갱신과 남은 작업 보고, Logic owner. 기능 구현이나 Git 변경은 수행하지 않았다.
- T01: 시민제안·투표 연결 sy-main 반영 완료.
- T07: 7개 API·controller 반영 완료, 화면 소비는 별도.
- T05: controller 반영 완료. UI 커밋 `b785adf`는 `feature/inquiry-ui`에만 있고 병합되지 않았다. 빈 성공 응답 parser 계약 확인이 남아 있다.
- T02~T13의 잔여 계약·연결·제품 결정과 권장 순서를 전체 목록으로 기록했다.
- 근거: 기존 기준 `4b0b7db` 이후 diff/log, 실제 DTO/API/controller, 같은 저장소의 문의 UI worktree 조회, 저장된 OpenAPI.
- 검증: 원본 JSON의 75 paths / 106 operations / 196 schemas 재확인. 작성한 문서 3개의 로컬 링크 10개 모두 유효하고 T01~T13 누락이 없다. `git diff --check` 통과, 기본 checkout의 Git status는 깨끗하다.
- 소스 변경 없는 문서 작업이므로 포맷 트리거·앱 테스트·lint·build는 실행하지 않았다. 기존 세션의 테스트 결과는 과거 기록으로 구분했다.
- 조사 중 와일드카드가 포함된 조회 명령 하나는 프로젝트 경로 확인 guard에서 차단됐다. 대상을 명시한 저장소 내부 파일 읽기로 확인했다. 문의 UI worktree에는 `docs/admin-routes.md`가 없어 해당 경로 검색은 실패했으며 실제 router와 커밋으로 대신 확인했다.
- 남은 작업: 사용자에게 후속 후보를 보고한다. 선택되지 않은 기능 구현, 서버 재조회, 통합·정리는 시작하지 않는다.

## 후속 이용 내역 작업 상태

- 사용자가 포인트·아이템 이용 내역 API 보정과 UI 없는 controller 구현, 날짜 입력 후 조회·역전 차단·검색 쌍 입력, 응답 필수·null 허용을 확정했다.
- 승인 생성 작업 `7af0e8a93daa4b3992409c2217cf8796`은 done이다. `feature/usage-api-controller`와 `/Users/okand/SynologyDrive/asan-worktrees/asan-metaverse-admin-ui-worktree/usage-api-controller`가 `c6ed8d3` 기준으로 생성됐다.
- `npm ci --no-audit --no-fund`: 성공, 341개 패키지 설치. package/lockfile 변경 없음.
- 현재 첫 소스 수정 도구가 `소스 구현 준비가 필요합니다: 사용자 구현 승인`으로 차단됐다. 기존 진행 지시가 자동 검사에서 승인으로 인정되지 않은 상태이며 우회하거나 같은 수정을 반복하지 않았다.
- 소스 diff 없음. 구현·포맷·테스트·lint·build 미실행. 세부 재사용·변경·검증 계획은 plan.md의 후속 승인 구간에 기록했다.
