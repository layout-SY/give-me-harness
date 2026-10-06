# Maintenance API·Controller 구현 완료

Swagger의 maintenance API 7개를 기존 공통 ApiClient·TanStack Query 패턴으로 교체하고, 사용자 추가 요청에 따라 UI–Logic controller와 데이터·입력·상태·콜백 계약을 구현했다. **최종 자동 포맷, 테스트 27개, lint, build, diff 검사 모두 통과했다.** 작업 위치는 `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`, 브랜치는 `sy-main`, HEAD는 `4b0b7db45aa9d15bf918a1a084370594e138a124`다.

## Controller 추가 결과와 UI 연결 계약

- 근거: 공지사항·아이템·출석 이벤트의 `model` 타입, `lib` mapper, controller hook 및 View 소비 구조. 사용자 `그럼 일단 이 패턴대로 controller 구현해봐`로 구현 승인.
- 공개 경로: `~/pages/maintenance`. `useMaintenanceController()`는 `list`와 `actions`를 함께 제공한다. `useMaintenanceListController()`, `useMaintenanceItemController(key)`, `useMaintenanceActionsController()`를 개별 조합할 수도 있다.
- `model/maintenance-controller.types.ts`: 조회 5개 필드, 로딩·오류·빈 목록·재조회 계약, 설정/버전/시간 입력, 마지막 제출 종류·진행·성공·오류 상태와 콜백을 정의했다.
- `lib/maintenance-controller.model.ts`: 응답의 허용 필드만 UI 모델로 옮긴다. 요청은 UI 입력에서 DTO를 명시적으로 구성하고 기존 schema로 검증한다. 문자열·날짜 원문·빈 문자열·optional을 유지하며 null을 허용하지 않는다.
- `actions.onSaveConfigs([{ key, value }])`, `onSaveVersion({ version })`, `onSaveTime({ start?, end? })`, `onTurnOn()`, `onTurnOff()`가 API 5종으로 연결된다. UI는 입력을 보관하고 콜백에 전달한다. Promise 완료만으로 성공을 판정하지 않고 `operation`, `isSuccess`, `errorMessage`를 소비한다. `onReset`은 제출 결과를 초기화하며 요청 중에는 적용하지 않는다.
- 설정별 boolean 변환, 전용 변경 API와 설정 키의 내부 관계, 기본값·시간대·버전 형식·폼 배치를 새로 추측하지 않았다. 조회 값은 string이며 미조회 단건만 undefined다.
- 단건 입력 key가 비면 조회 hook을 비활성화하고 controller에서 입력 오류를 제공한다. 정상 key의 캐시 구조는 유지한다.
- 기존 mutation의 공통 성공 판정과 캐시 취소·무효화를 재사용한다. controller는 같은 렌더의 연속 제출을 잠그고 unmount 시 AbortSignal을 취소하며 이후 UI 상태 갱신을 막는다. 로딩 상태는 TanStack Query/Mutation에서 파생한다.
- 화면·라우트·CSS는 추가하지 않았다. 실제 UI 소비 및 실서버 검증은 수행하지 않았다.

신규 `tests/maintenance-controller.test.mjs`의 11개 테스트는 기존 React SSR/Vite/MSW 방식으로 응답/입력 mapper, 빈 값·null·형식, 대기/빈 목록/실패, 단건 key 분리, 재조회, 실제 5개 변경 요청·캐시 갱신, 입력 오류 상태·초기화, 업무/HTTP 실패·재시도, 연속 제출 차단을 확인했다. 기존 타입 검증에는 UI 입력 필수/null/transport wrapper 차단 및 읽기 전용 응답 경계를 추가했다. 브라우저의 실제 mount/unmount 수명 검증은 실행하지 않았으며 unmount 취소는 코드 경로와 기존 API signal 테스트로 확인했다.

## 검증 결과

| 검증 | 결과 |
| --- | --- |
| 중앙 `formatting.py apply` | 최초 API 14개 파일, controller 추가 후 수정한 소스·테스트 12개 파일 포맷 완료 |
| 중앙 `formatting.py check` | `Prettier 확인 완료`, exit code 0 |
| `node --test tests/maintenance-controller.test.mjs tests/maintenance-contract.test.mjs tests/maintenance-query-mutation.test.mjs tests/logic-api-types.test.mjs` | 27개 통과, 실패·취소·skip 없음 |
| `npm run lint` | exit code 0 |
| `npm run build` | TypeScript·Vite 빌드 성공, exit code 0 |
| `git diff --check` | 통과 |

최종 diff에서 승인된 7개 method/path, 한 번의 일괄 PATCH, 필수·non-null 조회 응답, 공통 envelope 재사용, 캐시 입력 전 단일 parser, 성공 후 maintenance 범위 조회 취소·무효화를 확인했다. 테스트는 실제 Axios 표면을 MSW로 가로채 인증·query/body 직렬화·업무/HTTP/전송 실패·취소·기존 캐시 보존·활성 조회 재요청을 확인했다.

빌드에는 `vite-tsconfig-paths`의 Vite 내장 기능 안내와 500 kB 초과 청크 경고가 남는다. 이 작업에서 빌드 구성·청크 구조는 변경하지 않았다.

## 실제 변경

- `src/entities/maintenance/api/maintenance.api.ts`: 공통 ApiClient factory, `/maintenance`의 GET/PATCH 및 `/one`, `/version`, `/time`, `/on`, `/off` 연결. 경로 override를 제거하고 일괄 PATCH를 한 요청으로 교체했다.
- `maintenance.dto.ts`, `maintenance.parser.ts`: 사용자 확정 조회 필드 필수·null 금지, 기존 8개 키, Swagger 요청 길이·시간 형식, unknown 조회 payload 검증.
- `api/index.ts`, slice `index.ts`, `hook/`, `model/`: 공개 API, 조회 2개와 mutation 5개, 단건 key 캐시 분리, 성공 후 maintenance 조회 취소·무효화. PATCH data는 공통 mapper의 null→undefined와 unwrap을 사용한다.
- `tests/logic-api-types.test.mjs`: 새 필드·필수/null·void 계약으로 기존 타입 검증 갱신.
- `tests/maintenance-contract.test.mjs`, `tests/maintenance-query-mutation.test.mjs`: DTO, 7개 요청, 인증, 일괄 PATCH, null 성공, 실패/취소, 캐시 보존·재조회를 확인하는 테스트 작성·실행 완료.

## 구현 중 차단과 복구 이력 — 현재 해소됨

- `git diff --check`: 통과. 소스 파일 반영을 실제 조회로 확인했다.
- 중앙 `formatting.py apply`: `결과 미확인 코드 쓰기를 먼저 확인한 뒤 포맷하세요`로 차단.
- `formatting.py check`: maintenance API 4개 파일의 최초 실패 패치 기록을 보고했다.
- 최초 apply_patch는 동일 파일 Delete/Add 중복으로 `verification failed: invalid patch: multiple operations target ...maintenance.dto.ts`를 반환했다. 이후 정상 Update/Add 패치로 전체 소스가 작성되었다.
- 미확인 기록: `0d4a105a5389632c103ad67533ca839ecb03fc2e22c7f0402cdd559cd1496fe1`, native session `01a0e5fa-52b7-7aa1-811b-022d709bfbbf`, call `exec-c1222d41-ddd5-407a-9fbd-7d1b4f611779`.
- 승인된 `ps -Ao pid,ppid,comm` 조회에서 실행 중인 apply_patch·Python·Prettier 프로세스가 없음을 확인했다.
- `write-recovery` 작업 `3405f07f02084b528b28626e03d6a8de`를 준비했다. 중앙 상태 디렉터리 권한 오류 후 승인된 escalation으로 준비 성공했다.
- 사용자가 비동기 질문에 `명령 실행 승인`으로 답했지만 당시 execute 재호출은 같은 승인 요구로 차단되었다. 이후 일반 채팅 승인을 받고 아래 복구 절차로 해소했다.
- 동일 worktree의 다른 native session 미확인 기록 `9a2972b169d5adeb0bc53314261978f19a38734c9b886d1be6314bafce79d662`도 조회되어 아래 종료 근거로 정리했다.

## 완료 범위와 제한

승인된 API·DTO·parser·조회/변경 훅과 UI–Logic controller 구현 및 로컬 검증은 완료했다. API 계층은 `~/entities/maintenance`, UI 연결 계약은 `~/pages/maintenance`에서 가져온다. 조회 응답 5개 필드는 사용자 확정대로 모두 필수·non-null이며, 요청 optional과 길이·시간 형식은 Swagger를 유지한다.

브랜치 변경·실서버 호출·UI 화면 연결은 수행하지 않았다. 검증은 로컬 명세와 사용자 계약 기반 테스트이며 실서버 운영 결과를 보장하는 기록이 아니다. 별도 리뷰 에이전트는 실행하지 않았다. 다른 작업의 미추적 `docs/admin-routes.md`를 그대로 보존했다.

## 최종 커밋 결과

사용자의 커밋 요청과 `명령 실행 승인` 후 `sy-main`에 `b5c35a8` (`feat: maintenance API 및 controller 구현`)을 생성했다. 보호 실행 작업 `d4f29d350430d1e373f0183a8edb068f`는 stage done, exit code 0으로 완료되었다. maintenance API·controller 및 테스트 22개 파일이 포함되었다. 커밋 후 `git status --short`에는 이번 작업과 무관한 `?? docs/admin-routes.md`만 남았고 stage된 변경은 없다. push는 수행하지 않았다.

최초 승인 실행은 중앙 잠금 파일 쓰기 권한 오류로 Git 실행 전에 실패했다. 권한 확장 재시도에서 훅이 승인을 다시 요구해 사용자 재승인을 받았으며, 동일 작업을 권한 확장으로 한 번 실행해 완료했다. 최종 커밋 대상은 테스트 27개·lint·build가 통과한 소스와 같으며 커밋 전 Prettier check도 통과했다.

## 일반 채팅 승인 후 상태 재확인 이력

- 사용자 일반 채팅 `명령 실행 승인`은 훅에 인식되었다. 그러나 실행 직전 `종료 확인 후 도구 기록 또는 변경이 달라졌습니다`라는 이유로 기존 복구가 차단되었다.
- HEAD 및 maintenance 소스·테스트 14개 파일 SHA-256은 준비 시점과 모두 같다. 새 미추적 파일 `docs/admin-routes.md`가 추가되었고 이 파일은 이번 작업과 무관하므로 그대로 보존한다.
- 현재 파일 상태로 같은 미확인 쓰기 ID에 대한 복구 작업 `40281d96c00244048d2cd6e08b3d3740`을 준비했다. 재승인 후 완료했고 이전 복구 작업은 실행되지 않았다. 관련 없는 파일을 지워 이전 snapshot에 맞추지 않았다.

## 자체 기록과 외부 세션 기록 복구 결과

- 일반 채팅 승인 후 복구 `40281d96c00244048d2cd6e08b3d3740`은 stage done, exit code 0으로 완료되었다. 최초 실패 패치 기록은 정리되었다.
- 후속 formatter는 같은 worktree의 다른 미확인 쓰기 예약 때문에 차단되었다.
- 남은 기록 `9a2972b169d5adeb0bc53314261978f19a38734c9b886d1be6314bafce79d662`의 native session rollout ordinal 592를 확인했다. `exec-34e82d88-8faa-4804-ba5f-221a31d933fd`는 citizen-proposal-vote-api 연결 worktree의 `npm ci --no-audit --no-fund`였으며 `2026-09-28T03:05:31.801Z`에 completed, exit code 0으로 종료했다. 실제 실행 위치와 달리 기본 checkout에 예약 기록이 남아 있었다.
- 그 종료 근거로 복구 `ba0d3bd11a2d423b8e2881da74e474c5`를 준비하고 일반 채팅 승인 후 stage done, exit code 0으로 완료했다. 소스·의존성·Git 변경 없이 오래된 예약만 정리했다.
- 이후 inquiry-ui 연결 worktree의 성공 종료한 npm ci 기록 `90f254c8004d132296a1f4db5a7ff9210f9141dd5acedb200b83e8849d122b92`가 기본 checkout에 남아 포맷을 막았다. rollout ordinal 239의 completed/exit code 0을 확인하고 복구 `5d92ffb7f1f44f65a076eec40cafac6c`를 준비했지만, 실행 전에 외부에서 원래 예약이 해소되어 실행하지 않았다. 남은 예약은 inquiry-ui worktree 대상임을 확인했다.
- 기본 checkout의 차단 해소 후 정상 formatter로 14개 파일을 포맷하고 위 테스트·lint·build·최종 포맷 검사를 완료했다. 미완료 실행을 성공으로 처리하거나 정책/중앙 기록을 직접 수정하지 않았다.
