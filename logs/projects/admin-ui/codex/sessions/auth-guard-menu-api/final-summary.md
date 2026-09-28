# 로그인 가드와 메뉴 API 연결 결과

## 결과

사용자가 확정한 범위의 메뉴 API 기반, 로그인 가드와 기본 인증 헤더 처리를 구현하고 `fe66897`로 커밋했다. 이후 최신 `sy-main`을 기능 worktree에 동기화해 테스트 충돌 2건을 해결한 `c739a91`을 만들었고, 2026-09-22에 사용자 승인으로 이 commit을 `sy-main`에 ff-only 병합했다. 기본 checkout의 기존 아이템·이벤트 변경 21개와 PR 문서도 임시 보관 후 원래 미커밋 상태로 모두 복원했다. 당시 조합에서 전체 테스트 356/356, lint, TypeScript·Vite build 및 diff 공백 검증을 통과했다. 후속 사용자 요청에 따라 이벤트 API·로그인 로컬 branch와 worktree 정리까지 완료했다. 최종 정리 시점의 `sy-main`은 `ea64f72`로 clean이며 lint·build를 통과했다. 원격 push는 실행하지 않았다.

- 구현 작업 위치: `/private/tmp/asan-metaverse-admin-ui-auth-guard-menu-api`였으며 정리 후 디렉터리와 Git 등록이 없다.
- 구현 branch: `feature/auth-guard-menu-api`, 직접 부모: `sy-main`. 로컬 branch 삭제를 완료했다.
- 시작 기준 HEAD: `ed9d65bd6c74eabf3f8e5070c203135d2067264e`.
- 기능의 최종 HEAD: `c739a91fef5a687123bf4851419224720068830b`. 현재 `sy-main`에 포함돼 있다.
- 기본 checkout `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`의 현재 `sy-main`은 `ea64f72f6ede900d34e9ba8f8d5a37ca8a5e08f0`이며 staged·unstaged·untracked 변경과 미해결 충돌이 없다. 앞서 복원한 21개 변경은 별도 작업의 후속 commit으로 반영됐고 PR 문서의 외부 제거를 확인했다.
- Git 생성 작업 `19eb26604d7f4cc6acbb16d441150442`와 초기 stage·commit 작업 `359aa751dac4e5b0d40eeafab03f0395`는 `done`이다. 최종 병합 작업 `6f3b0cb0ebd54d14933e1d701b87799b`는 `verification_passed: true`, source를 유지하는 `retained` 상태다. 복원 작업 `b6b500cb3f6711d598112e1e35605cfb`는 `done`이다. push는 실행하지 않았다.
- 역할: `logic`. 독립 하위 에이전트·브라우저 자동화는 호출하지 않았다.

## 실제 구현

### 메뉴 API

`src/entities/menus/api/{menus.api,menus.dto,menus.parser,index}.ts`와 entity barrel을 추가했다.

- `menusApi.getList({ signal? })`: `GET /menus`, `ApiResult<GetMenuListResponseDto>`.
- `menusApi.getMyList({ signal? })`: `GET /me/menus`, `ApiResult<GetMyMenuListResponseDto>`.
- 기존 `ApiClient`·공통 envelope mapper·`ApiResult`·`withAbortSignal`·`customConfig`를 재사용한다. 응답 제네릭은 내부 payload이며 도메인 envelope를 중복 정의하지 않는다.
- 성공 payload를 파서에서 한 번 검증한다. `/menus`의 `children: string[]`와 `/me/menus`의 객체 children을 구분하고 응답 순서·visible을 임의로 바꾸지 않는다.
- 빈 배열은 정상이며 잘못된 성공 payload, 업무 실패, HTTP 실패, 취소를 구분한다. role query 등 명세에 없는 인자를 보내지 않는다.
- 로그인 뒤 실제 조회, 메뉴 캐시·상태, 동적 메뉴와 권한별 라우팅에는 아직 연결하지 않았다. 사용자가 후속 명세 보강 후 진행하기로 확정한 범위다.

### 로그인·라우트

- `src/app/router/routes.tsx`: `/login`만 로그인 전용 가드에 두고 `/`, `/cp`, `/vo`, `/manage`, `/events`, `/meeting`을 기존 `PrivateRoute` 하위에 둔다.
- `private-route.tsx`: 인증 store와 만료 판정을 구독한다. 보호 화면을 렌더하기 전에 차단하고 `state.from`에 현재 경로를 넣어 `/login`으로 replace 이동한다.
- 신규 `login-route.tsx`: 인증된 사용자의 로그인 화면 접근을 막고 복귀 경로 또는 기존 `/cp/dashboard`로 보낸다.
- `src/features/auth/use-auth-route-session.ts`: 두 가드가 인증 상태와 만료 판정을 공유한다. 만료된 경우 해당 렌더에서 보호 화면을 차단하고 effect에서 세션을 동기화한다. revision 비교로 이전 렌더의 정리가 새 세션을 덮어쓰지 않게 한다.
- `auth-session.ts`, `token.util.ts`: bootstrap·화면 진입에서 숫자 exp가 현재와 같거나 지난 토큰을 정리한다. exp 0도 만료로 판정한다. 디코드 실패·exp 누락·잘못된 타입은 만료로 간주하지 않는다. 타이머나 자동 refresh는 추가하지 않았다.
- `auth-redirect.ts`, `use-sign-in-controller.tsx`: pathname·search·hash를 보존한 내부 복귀 경로를 공용화했다. 외부 주소·역슬래시·인코딩된 로그인 루프 등은 기본 경로로 돌린다.
- 기존 `ApiErrorDialogBridge`의 알림 확인 → `clearAuthSession()`과 가드의 store 구독이 연결된다. bridge·팝업 문구·이미 있는 재인증 이벤트 중복 억제는 유지했다.

### 인증 헤더·기존 코드 유지

- `axios-instance.ts`: 저장된 access token을 기본 포함한다. `authRequired: false`이면 자동 부착을 생략하고 명시된 Authorization은 대소문자와 관계없이 보존한다.
- `axios.interface.ts`: `customConfig` 객체와 타입·export를 유지하고 `authRequired: true` 기본 항목만 제거했다. 각 도메인의 기존 전달 구조도 유지한다. 추가 공통 헤더가 메뉴 API까지 전달되는지 테스트했다.
- `auth.api.ts`: 로그인·비밀번호 변경·메일 요청은 토큰 자동 부착을 명시적으로 제외한다. 재발급은 기존 refresh token 헤더를 사용한다.
- DAO 파일은 수정하지 않았다. 기존 잘못된 POST 인자 위치도 사용자 요청대로 그대로 둔다. 공통 interceptor 변경은 이 인스턴스를 공유하는 DAO 요청에도 적용되지만 DAO 소스·업무 동작을 별도로 수정하지 않았다.
- `/meeting` fetch의 기존 화면 입력 토큰은 유지했다.

## 초기 구현 검증 근거

| 검증 | 결과 |
| --- | --- |
| 공통 `formatting.py apply` | 수정 소스·테스트 28개에 실제 Prettier 적용, 이후 테스트 보완분도 재실행 완료 |
| 전체 Node 테스트 48파일 | 344/344 통과, exit 0 |
| `npm run lint` | 마지막 테스트 수정 후 재실행 포함 통과 |
| `npm run build` | TypeScript·Vite 통과 |
| `git diff --check` | 통과 |
| DAO diff | 없음 |
| 기본 checkout 상태 | 구현 검증 시 `sy-main` `ed9d65b`, 커밋 후 확인 시 `2b9ca35`, 모두 clean |

실제 테스트 명령은 `TSX_TSCONFIG_PATH=tsconfig.app.json node --test --test-concurrency=1 --test-reporter=spec` 뒤에 `rg --files tests -g '*.test.mjs'`에서 얻은 48개 경로를 정렬하여 각각 명시했다. 하네스가 와일드카드 경로를 거부해 실제 파일 경로로 실행했다. package.json에는 `test` script가 없다.

신규 `tests/menus-contract.test.mjs`는 실제 Axios interceptor와 공통 ApiClient를 통해 두 메뉴 계약·추가 공통 헤더·토큰·취소·오류를 확인한다. `auth-login-flow.test.mjs`는 기본 토큰 부착·명시 헤더 보존·인증 예외를 추가 검증한다. 기존 도메인 테스트의 `authRequired: true` 기대값은 기본 인증 계약에 맞게 갱신했으며 요청 내용·취소·응답 검증을 유지했다. 자동 포맷 때문에 일부 수정 테스트 파일에서 줄 배치도 변경됐다.

`auth-route-guard.test.mjs`는 실제 가드와 MemoryRouter의 SSR 렌더로 보호 화면 미렌더링, 원래 경로, 로그인 차단, 세션 정리 이후 복귀를 확인한다. Zustand의 SSR 초기 snapshot을 테스트의 현재 인증 상태로 공급한다. 실제 route 정의도 실행하여 `/login` 외 라우트가 보호 가드 아래인지 검증한다. 첫 테스트에서 SSR snapshot·ESM 모듈 대체 문제를 수정했고, 별도 VM 컨텍스트 사용 시의 프로세스 종료 실패는 동일 컨텍스트 실행으로 해소했다. 동일 구조 검증을 유지한 최종 전체 실행에서 344/344 및 exit 0을 확인했다.

한계: 실서버 로그인·메뉴 호출과 브라우저 렌더·effect·실제 뒤로가기 조작은 실행하지 않았다. 가드 SSR 테스트는 렌더 차단·이동 props·세션 경계를 검증하며 브라우저의 실제 effect 실행 검증을 대신한다고 주장하지 않는다. build에는 기존 `vite-tsconfig-paths` 안내와 500 kB 초과 청크 경고가 있다. 전체 테스트에는 기존 MockTimers 실험 API 안내가 있다.

## 공통 401 경계 밖의 확인된 호출

조사 경로는 `src/shared/api`, `src/entities/**/api`, `src/features`, `src/pages`, `src/widgets`의 Axios 인스턴스·API 호출 사용처다. 인증과 이미지 upload/delete는 useApi, 확인한 이벤트 조회는 QueryClient 경계를 통과한다.

`src/features/meeting/api/meeting.api.ts`의 `createMeeting`, `joinMeetingByInviteCode`, `joinMeetingByRtcToken`은 별도 fetch를 사용한다. HTTP 실패를 일반 Error로 변환하고 `src/features/meeting/ui/MeetingPage.tsx` 및 `useAgoraMeeting.ts`에서 화면 오류로 처리한다. 이 세 호출의 401은 공통 재인증 알림·세션 정리로 연결되지 않는다. 사용자 승인 없이 임의 수정하지 않고 후속 확인 대상으로 남긴다.

## 후속 메뉴 연결 계약

다음 작업은 사용할 branch·worktree의 현재 HEAD와 변경 상태를 먼저 확인한 뒤 이어갈 수 있다. 이번 구현의 초기 commit은 `fe66897eee4e76fd787c1dfe53198040bfc61c49`이며 부모 동기화를 포함한 `c739a91`이 `sy-main`에 통합돼 있다. 원래 기능 worktree는 정리됐고, 최종 확인 당시 기본 checkout은 clean이다.

아직 필요한 계약: 두 API의 실제 용도·호출 시점, key와 route의 대응, 상세 경로 parameter·권한 관계, 복수 권한과 첫 화면, 빈 목록·알 수 없는 key 처리, 메뉴 실패·재시도·토큰 유지 정책. 로그인 후 연결 지점은 기존 `src/features/auth/use-auth.ts`의 TODO이며 API 함수만 준비돼 있다. 새 메뉴 초기화는 bootstrap·로그아웃·계정 전환과 revision·취소 경계도 함께 연결해야 한다.

## 커밋 결과

- 커밋: `fe66897eee4e76fd787c1dfe53198040bfc61c49`.
- 메시지: `feat(auth): 로그인 가드와 메뉴 API 연결`.
- 범위: 승인된 소스·테스트 28개 파일, 950줄 추가·235줄 삭제.
- 보호 실행 작업 `359aa751dac4e5b0d40eeafab03f0395`: exit 0, `stage: done`.
- 커밋 후 `git status --short --branch`에서 작업 branch의 staged·unstaged·untracked 변경이 없음을 확인했다. 세션 산출물은 ignore 대상이라 커밋에 포함하지 않았다.
- 초기 커밋 당시 merge·push·branch 및 worktree 정리는 실행하지 않았다.

## 최신 부모 동기화와 충돌 해결

- 사용자 요청: 기능 branch를 `sy-main`에 병합. 진행 중이던 형제 문의 타입 작업과 기본 checkout의 페이지네이션 변경이 커밋된 후 다시 검토했다.
- 동기화 source: 직접 부모 `sy-main`의 `c3927095a58bc7814f28348b8ae94e11228a4627`.
- 동기화 target: 이 기능 worktree의 `feature/auth-guard-menu-api`, HEAD `fe66897eee4e76fd787c1dfe53198040bfc61c49`.
- 승인된 보호 작업 `ef3741168edfd96ca0311aff528a2d79`가 `git merge --no-ff sy-main`을 실제 실행했다. 테스트 2개에서 내용 충돌이 발생해 종료됐고 당시 MERGE_HEAD는 `c3927095a58bc7814f28348b8ae94e11228a4627`이었다. 실패한 merge 명령은 반복하지 않았다.
- 사용자의 별도 `진행` 승인 후 `tests/logic-api-contract.test.mjs`는 새 페이지 응답·deepEqual 검증과 기본 인증 요청 설정을 함께 유지했다. `tests/news-contract.test.mjs`는 최신 `total/page/size` 응답 계약과 기본 인증 기대값을 유지했다.
- 자동 포맷이 미해결 index 항목을 staged 파일로 판정해 중단됐다. 사용자 승인 보호 작업 `8545edfe714d6e51a03423cb50464419`로 테스트 2개만 stage에서 해제했고 파일 내용과 나머지 자동 병합 결과를 보존했다. 이 작업은 exit 0·`done`이다.
- 필수 `formatting.py apply`가 수정 테스트 2개에 실제 Prettier를 적용하고 exit 0으로 완료됐다.
- 통합 상태 검증: `npm run lint` 통과, `npm run build` 통과, 전체 Node 테스트 49파일 355/355 통과(exit 0), `git diff --check` 통과. `git diff --name-only --diff-filter=U`는 비어 있다.
- 전체 테스트는 `TSX_TSCONFIG_PATH=tsconfig.app.json node --test --test-concurrency=1 --test-reporter=spec` 뒤에 현재 `tests/*.test.mjs`에 해당하는 49개 실제 파일명을 각각 명시하여 실행했다. 부모의 새 `global-pagination-msw.test.mjs`도 포함했다.
- 최신 `sy-main` 대비 전체 기능 diff는 28파일, 775줄 추가·182줄 삭제다. DAO diff는 없으며 부모가 이미 커밋한 DAO·페이지네이션·이벤트·배포 변경을 그대로 보존했다.
- 사용자 승인 보호 작업 `124f2c4b7257225b8f4acb0ffce44a6b`가 테스트 2개를 stage하고 동기화 merge commit `c739a91fef5a687123bf4851419224720068830b`를 생성했다. 메시지는 `merge: sy-main 변경을 로그인 가드 브랜치에 반영`, 부모는 `fe66897`과 `c392709`다. 작업은 exit 0·`done`이며 기능 worktree의 staged·unstaged·untracked 변경은 없다.
- 동기화 완료 당시 기본 checkout은 `sy-main`의 `c3927095a58bc7814f28348b8ae94e11228a4627`이었다. 해당 commit이 기능 branch의 조상임을 확인해 최종 병합을 ff-only로 준비했다.
- 최초 최종 보호 `review`는 `/private/tmp/asan-metaverse-admin-ui-event-api`의 사라진 `.git` 파일과 남은 worktree 등록 때문에 exit 2로 중단됐다. 당시 남아 있던 로컬 파일을 이 세션에서 직접 삭제하지 않았다.
- 보호 경로의 `git worktree prune --expire now --verbose`와 `git worktree repair /private/tmp/asan-metaverse-admin-ui-event-api`도 PreToolUse에서 거부돼 실제 실행되지 않았다. 이후 사용자 설명으로 복구 후 취소 경위를 확인했고, 외부에서 이벤트 worktree 디렉터리와 등록이 제거된 것을 조회해 이 차단이 해소됐음을 확인했다. 이벤트 기능 commit은 이미 `sy-main`에 포함돼 있었다. 중앙 정책 변경이나 raw Git 우회는 하지 않았다.
- 형제 문의 타입 branch `7db04d9`와 다른 worktree를 보존했다. 기존 PR 문서는 아래 최종 병합 단계에서 승인된 임시 보관·복원을 거쳤으며 내용은 동일하다. 원격 push와 로그인 branch·worktree 정리는 범위 밖이다.

## sy-main 병합과 기존 변경 복원

- 병합 대상: 기본 checkout의 `sy-main`, `c392709` → `c739a91`. source는 `/private/tmp/asan-metaverse-admin-ui-auth-guard-menu-api`의 `feature/auth-guard-menu-api`다. 최종 형제 검토 `b9d4fda70b6b48238fc78c892d3d1eb4`에서 직접 부모 관계, 미처리 자식 없음, ff-only 가능과 두 worktree clean을 확인했다.
- 기본 checkout의 별도 아이템·이벤트 작업이 끝날 때까지 사용자 요청으로 병합을 대기했다. 완료된 21개 변경이 미커밋 상태로 남았고, 보호 완료 실행기가 target의 미커밋 변경을 허용하지 않아 실제 병합 전에 중단됐다. 사용자의 추가 승인으로 모든 기존 변경을 임시 보관했다.
- 첫 stash `53650c70d159c5725cf2d16f09dde3add16e6649`는 겹치는 `tests/items-contract.test.mjs` 한 파일을 보관했다. 두 번째 stash `7f097b6048c53f280fc54de7ead247f39d719da3`는 나머지 20파일과 untracked PR 문서를 보관했다. 관련 보호 작업 `5f3219da5848e8965d0efbbde048b18f`, `6857ebb60be2da2addafd79bb4e954eb`는 모두 승인 후 `done`이다.
- 사용자 승인 병합 작업 `6f3b0cb0ebd54d14933e1d701b87799b`는 exit 0으로 끝났고 결과 commit `c739a91`, 병합 후 lint·build 성공을 기록했다. cleanup을 요청하지 않아 source branch·worktree를 유지하는 `retained` 상태다.
- 사용자 승인 복원 작업 `b6b500cb3f6711d598112e1e35605cfb`가 두 stash를 최근 항목부터 순서대로 pop했다. 첫 복원은 20파일·PR 문서를, 두 번째 복원은 items 계약 테스트를 복구했다. 모두 exit 0이며 실제 Git 충돌 없이 성공한 stash 두 개가 정리됐다.
- 보존 검증: 나머지 20파일의 binary diff는 보관 전과 정확히 일치한다. items 계약 테스트의 전체 내용은 보관한 원본에 로그인 작업의 `authRequired` 기대값 `true` → `undefined` 한 줄만 반영한 결과와 일치한다. PR 문서의 SHA-256은 보관 전후 `251edf03e7b0a7dd68a554aa282945dbe88e8403839a90f485df55bc83c36c28`로 동일하다. 기존 21파일은 unstaged, PR 문서는 untracked 상태이며 stash ref는 없다.
- 복원 후 기본 checkout 검증: 전체 Node 테스트 49파일 **356/356 통과**, 실패·취소·skip 0, exit 0. `npm run lint`, `npm run build`, `git diff --check`도 통과했다. 테스트는 기존에 사용한 명령 뒤에 실제 49개 파일 경로를 명시해 실행했다. 별도 작업의 확정 enum 계약과 로그인·메뉴 API 변경을 함께 검증한 결과다.
- 원격 push, 로그인 branch·worktree 삭제, 별도 아이템·이벤트 변경의 stage·commit은 실행하지 않았다. 실서버·브라우저 검증과 후속 메뉴 명세 보강은 앞서 기록한 한계로 유지한다.

## 로컬 브랜치·워크트리 정리 완료

- 사용자 요청으로 이벤트 API와 로그인 작업의 로컬 branch·worktree를 정리했다. 이벤트 작업 `b8414c747e6d440eb84926b68f303482`, 로그인 작업 `174c6c5b8c3b4d91bba78865efce8182`는 모두 `cleaned`이며 관계 기록의 검증 결과는 `passed`다.
- 로그인 작업 기록 두 파일을 기본 checkout의 동일 세션 경로에 복사한 후 원본과 SHA-256 일치를 확인했다. 빌드 메타파일도 기본 checkout에 동일 사본이 있어 보존했다. 승인된 Git clean `4672b65528b350f5fe83179e771ca29f`로 source의 빈 자기 세션 폴더와 중복 `tsconfig.tsbuildinfo`만 제거했다.
- 이전 정리 재개 `f315ad6d8e01428ba8792aa8b62b27bb`는 부모의 후속 commit으로 실제 병합 결과 비교에 실패했다. 현재 부모 `ea64f72`를 기준으로 검토를 갱신하고 사용자 승인을 받은 로그인 정리 작업에서 lint·build를 통과한 후 삭제했다.
- 사후 `git worktree list --porcelain`, `git for-each-ref` 및 디렉터리 조회로 `feature/event-attendance-roulette-api`, `feature/auth-guard-menu-api`의 로컬 ref와 두 worktree가 모두 없음을 확인했다. `sy-main` HEAD는 `ea64f72f6ede900d34e9ba8f8d5a37ca8a5e08f0`로 유지됐고 clean이다.
- 문의 타입·아이템 UI·별도 이벤트 보상 UI 작업 공간은 보존했다. 원격 push·원격 branch 삭제는 실행하지 않았다. 자기 기록의 현재 위치는 `/Users/okand/SynologyDrive/asan-metaverse-admin-ui/.codex/logs/sessions/auth-guard-menu-api/`다.
- 이번 정리에서 전체 테스트는 재실행하지 않았다. 후속 `ea64f72`의 `items-query-mutation.test.mjs`에서 같은 `mainCategoryId` 존재를 true와 false로 연속 검사하는 상충 단언을 확인했으며, 별도 작업 변경이므로 수정하지 않았다. 앞서 기록한 전체 테스트 356/356은 이 후속 commit 이전 조합의 결과다.

## 정책·실행 기록

필수 스킬·인접 구현을 읽고 사용자에게 범위와 재사용 방식을 확인했다. Git 생성 승인과 구현 `진행`이 각각 기록된 후 작업했다. 중앙 기록 파일에 대한 sandbox 권한 오류는 동일 보호 명령·포맷 명령의 권한 상승 경로로 처리했으며 정책 파일이나 상태를 직접 수정하지 않았다. 사용자 요청대로 다른 프로젝트 조회, raw Git 우회, DAO 수정, customConfig 삭제는 하지 않았다.
