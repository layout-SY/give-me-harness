# 메뉴 API와 권한별 라우팅 인계

## 결론

`POST /auth/login`으로 access token을 받고 `localStorage`에 저장하는 로그인 작업은 완료했다. **후속 연결 지점은 `src/features/auth/use-auth.ts`의 `getAuthentication` 내부, `execute` 완료 및 취소 여부 확인 다음에 있는 `/menus` TODO 주석이다.** 현재 실제 메뉴 HTTP 요청은 없으며, 로그인 성공 후 기존 `/cp/dashboard` 이동을 유지한다.

사용자의 최신 지시: “/menus라는 path에 대해서 요청해야 한다는 주석만”, “실구현에 대해선 … 핸드오프 문서만”, “로그인 작업 진행”. 이 문서는 다른 worktree에서 수행할 메뉴·권한·라우팅 작업의 인계 자료이며, 미정 API 계약이나 Git 작업의 승인을 대신하지 않는다.

## 현재 Git 상태

- 종료된 문서 수정 도구의 잔여 기록은 복구 작업 `fb9ef79baa34480c98f4ca97ddfe918e`로 해소했다. 사용자 승인 후 종료 코드 0, `stage: done`을 확인했다.
- 사용자 재승인 후 로그인 커밋 작업 `9b2fce71fc2878dc8e19ddabe953ebea`가 종료 코드 0, `stage: done`으로 완료됐다. 커밋은 `a25745ccee1f2b822a6201a379e47c3dafe51a44` (`feat(auth): 관리자 로그인 API와 토큰 저장 연결`)다.
- 사용자는 토큰 저장 후 `/menus` 조회 TODO만 두고 실제 요청·권한·라우팅을 handoff로 전달하는 범위를 다시 확인했다. 소스에 이 범위가 반영돼 있다.
- 로그인 파일 10개만 커밋했고 해당 파일에 미커밋 변경이 없음을 확인했다. 함께 존재하는 아이템 카테고리 소스·테스트 변경 13개는 별도 작업이며 그대로 보존했다.

## 커밋 승인 후 실행 차단 이력

- 로그인 소스·테스트 10개 stage+commit은 사용자의 `명령 실행 승인`을 받았다. 메시지는 `feat(auth): 관리자 로그인 API와 토큰 저장 연결`이다.
- 보호 실행 작업 `9b2fce71fc2878dc8e19ddabe953ebea`가 Git 실행 전 중앙 잠금 파일 생성의 sandbox 권한 오류로 중단됐다.
- 권한 상승을 요청한 동일 명령 재시도는 이미 받은 승인을 다시 요구하는 PreToolUse에 차단됐고, `recover`는 시작된 완료 작업이 아니라는 이유로 거부됐다.
- 당시 `show` 결과는 `prepared`였고 HEAD와 index는 그대로였다. 이후 공식 복구 및 재승인으로 위 커밋을 완료했다.
- 후속 branch/worktree 생성과 병합은 아직 승인되지 않았다.
- “다시 이어서 작업 시작” 요청 후에도 동일 작업의 권한 상승 실행이 PreToolUse의 승인 재요구로 차단됐다. 재개 시점에도 변경 10개·빈 index·기존 HEAD와 `prepared` 상태를 확인했으며, 실제 Git 명령은 시작되지 않았다.
- 이후 권한 상승 실행으로 중앙 잠금 파일 권한 문제를 해소했다. 남아 있던 미확인 쓰기 기록 `388ea0d73ee22e79c8b42c41f2af83def0480ce4abf1ba842e2fcf58d353cef2`는 native 로그의 문서 `apply_patch` 종료 및 관련 프로세스 부재를 확인한 뒤 `write-recovery`로 해제했다. 상세 근거는 `final-summary.md`에 기록했다.

## 역할과 작업 공간

- 보내는 host·session·role: Codex / `admin-login-menu-handoff` / `logic`.
- `requested_roles`: 현재 로그인 Logic, 후속 메뉴·권한·라우팅 작업.
- `confirmed_roles`: 현재 세션의 `logic`.
- `completed_roles`: 로그인 API·세션·hook·오류 처리·검증·인계 문서화.
- `next_role`: 후속 API·상태·라우팅 연결은 Logic을 제안한다. 메뉴 표시 계약이나 레이아웃 변경이 필요하면 UI 역할을 별도 세션으로 연결한다.
- 받는 host·session·목적지 branch·worktree: 미정. 사용자가 별도 worktree에서 진행할 예정이라고 명시했다. 조회 시에는 아래 기본 checkout 한 곳만 존재한다.
- 후속 공간의 이름·절대 경로·직접 부모·생성 기준 commit은 후속 작업 시작 시 실제 상태와 사용자 결정으로 확정해야 한다. 이번 작업에서 branch/worktree를 생성하거나 이름을 예약하지 않았다.

### 보내는 위치: 로그인 작업 공간

- project: `asan-metaverse-admin-ui`.
- 저장소·worktree·명령 실행 디렉터리: `/Users/okand/SynologyDrive/asan-metaverse-admin-ui`.
- branch: `sy-main`.
- 시작 HEAD: `efccd76b10a89e49e2c3f7a5c8c59326e6b6c3f3`.
- 인계 기준 HEAD: `a25745ccee1f2b822a6201a379e47c3dafe51a44`.
- 직접 부모: 기준 브랜치이므로 이번 작업에서 별도 관계를 생성하지 않았다.
- 현재 작업 commit: `a25745c` (`feat(auth): 관리자 로그인 API와 토큰 저장 연결`).
- staged 변경: 없음.
- 커밋된 기존 파일 변경:
  - `src/entities/auth/api/auth.api.ts`, `auth.dto.ts`, `index.ts`: `/auth/login` 및 access-only 응답 계약.
  - `src/features/auth/model/auth-session.ts`: `commitSignInSession` 추가.
  - `src/features/auth/use-auth.ts`: 성공 여부 반환 및 `/menus` 연결 주석.
  - `src/pages/sign-in/hook/use-sign-in-controller.tsx`: 성공 여부 확인 후 이동, 오류 표시 함수 연결.
  - `tests/auth-api-contract.test.mjs`, `tests/auth-session.test.mjs`: 새 로그인 계약과 세션 검증.
- 커밋된 신규 파일:
  - `src/pages/sign-in/model/sign-in-error.ts`: 기존 오류 정규화를 사용하는 로그인 메시지 변환.
  - `tests/auth-login-flow.test.mjs`: 실제 hook·Axios interceptor·세션을 연결하는 Node 테스트.
- 자기 세션 산출물: `.codex/logs/sessions/admin-login-menu-handoff/{plan,final-summary,handoff}.md`. 소비자 로그 경로의 Git ignore 정책을 따른다.
- 이번 로그인 작업의 unstaged·untracked 변경은 없다. 다른 작업의 아이템 카테고리 소스·테스트 변경 13개가 남아 있으므로 후속 작업자는 이를 보존해야 한다.

### 인계 대상: 메뉴·권한 작업 공간

- 사용자가 요청한 방식: 같은 admin-ui 저장소의 별도 linked worktree.
- 목적: 메뉴 API 계약과 권한별 route/menu 구성을 독립적으로 구현·검증한다.
- 실제 경로·branch·HEAD·직접 부모: 아직 확정되지 않았다.
- 선행 조건: 로그인 완료 커밋 `a25745c`가 후속 공간의 기준 이력에 포함되는지 확인한다.
- 필요한 Git 작업: 로그인 파일 10개 commit은 완료됐다. 후속 branch/worktree 준비는 위치·명령·영향을 별도 보고하고 승인받는다.
- 진입 시 실제 HEAD·dirty 상태를 다시 확인한다. 이 문서의 HEAD로 복원하거나 다른 작업의 변경을 덮어쓰지 않는다.

## 현재 로그인 계약과 연결 위치

1. `src/pages/sign-in/hook/use-sign-in-controller.tsx`가 입력한 ID와 비밀번호로 `useAuth().getAuthentication`을 호출한다. 기존 ID trim, 비밀번호 원문 전달, 입력·제출 상태, 오류 시 비밀번호 초기화 흐름을 유지한다.
2. `src/entities/auth/api/auth.api.ts`는 `POST /auth/login`에 `{ loginId, password }`를 전달한다. 로그인 요청에 인증 헤더를 요구하지 않는다.
3. `src/entities/auth/api/auth.dto.ts`의 `parseSignInPayload`는 `{ code: "SUCCESS", message: string, data: { accessToken: string } }`를 검증한다. 토큰은 비어 있으면 거부한다. **권한 필드는 현재 DTO에 없으며 반환값에 포함되지 않는다.**
4. `src/features/auth/model/auth-session.ts`의 `commitSignInSession`이 `admin-access-token`을 저장하고 이전 refresh token·사용자 정보를 정리한 뒤 인증 여부와 revision을 갱신한다. 새 로그인 응답에 없는 profile·roles를 생성하지 않는다.
5. `getAuthentication`은 취소·오래된 요청이면 `false`, 성공 및 저장 완료이면 `true`, API·저장 실패이면 예외를 반환한다.
6. `/menus` TODO는 취소 검사 다음, `true` 반환 직전에 있다. 후속 메뉴 요청은 이 위치에서 순서대로 `await`할 수 있다. `useApi`의 `onSuccess`는 비동기 callback을 기다리는 계약이 아니므로 메뉴 초기화를 `async onSuccess`에 넣지 않는다.
7. 현재 컨트롤러는 `true`일 때 `/cp/dashboard`로 이동한다. 후속 작업에서는 메뉴 초기화와 권한별 최초 진입 경로 확정 후 이동하도록 연결해야 한다.

기존 `/v1/auth/token/reissue`와 `AuthPayloadDto`는 기존 refresh 경로를 위한 코드다. 새 로그인 응답은 `SignInPayloadDto`를 사용한다. 이번 API는 refresh token을 발급하지 않으므로 로그인 직후 refresh snapshot은 없으며 자동 갱신을 새로 연결하지 않았다.

## 사용자가 제시한 후속 기능 구조

아래는 사용자가 확정한 **구현 방향**이다. 예시 필드·값은 API 계약으로 확정되지 않았다.

1. 로그인 응답에서 권한을 받고 토큰 저장을 완료한다. 사용자가 든 `role: "vo"`는 권한 표현 예시다.
2. 즉시 해당 관리자의 메뉴 목록 API를 요청한다. `/menus?role=cp`는 요청 형태 예시이며 현재 코드에는 `/menus` 후속 요청 주석만 있다.
3. 메뉴 응답의 안정적인 식별자를 프런트엔드에 정의된 화면·경로와 연결한다. 사용자가 든 `proposal-detail`은 식별자 예시다.
4. 이 연결 결과로 왼쪽 메뉴 탭의 항목·표시 텍스트·클릭 이동을 구성한다.
5. 관리자의 권한에 허용된 영역과 화면만 앱에서 사용할 수 있게 하고 화면 코드를 lazy 로딩한다. VO 관리자에게 CP 경로로의 직접 접근이 발생하면 권한 밖 접근으로 거부한다.

전체 목표 순서: **로그인 응답 → 토큰 저장 → 메뉴 요청 및 응답 검증 → 메뉴·허용 라우트 연결 → 초기 화면 이동**.

## 실제 코드에서 재사용할 자산

| 경로 | 현재 내용 | 후속 연결 방향 |
| --- | --- | --- |
| `src/shared/api/axios-instance.ts`, `axios.interface.ts` | 저장된 access token을 `authRequired` 요청에 Bearer로 추가 | 확정된 메뉴 요청의 인증 설정에 재사용 |
| `src/shared/api/api-client.ts`, `common/response.dto.ts`, `with-abort-signal.ts` | 공통 응답·HTTP client·취소 신호 | 메뉴 전송·응답 파싱 계약에 맞춰 재사용 |
| `src/features/auth/use-auth.ts` | 로그인 결과와 세션 저장 후 TODO | 메뉴 초기화 순서 조율 |
| `src/features/auth/model/auth-session.ts`, `auth.store.ts` | 토큰·세션 revision·로그아웃·startup 복원 | 로그인 교체·로그아웃 이후 도착한 메뉴 응답 차단, 초기화 생명주기 연결 |
| `src/app/index.tsx` | `bootstrapAuthSession` 실행 | 새로고침·직접 URL 진입 시 저장된 토큰으로 메뉴를 다시 준비하는 흐름 검토 |
| `src/app/router/routes.tsx` | 모든 CP·VO 화면의 정적 import와 route 정의 | 확정된 메뉴 식별자와 로컬 route 정의를 연결하고 필요한 화면 import를 분리 |
| `src/app/router/private-route.tsx`, `role-based-route.tsx` | 기존 로그인·관리자 역할 검사 컴포넌트, 현재 CP·VO 라우트에는 미연결 | 로그인 여부와 확정된 CP·VO 권한 계약의 검사 경계로 확장 적합성 검토 |
| `src/app/router/cp-admin-shell.tsx`, `vo-admin-shell.tsx` | 고정 메뉴를 `Navigation`에 전달 | 메뉴 초기화 결과에서 화면용 items를 받아 전달 |
| `src/widgets/side-navigation/ui/navigation.tsx`, `model/navigation.dto.ts` | `items?: NavigationItem[][]`; icon·label·path·sublinks 표시 | 기존 items props와 메뉴 UI 재사용 |
| `src/widgets/side-navigation/lib/build-navigation-items.ts`, `model/_navigation5.ts`, `_navigation6.ts` | CP·VO의 기존 메뉴명·아이콘·경로 | 확정된 서버 식별자에 대응할 로컬 표시 자산 |

## 후속 설계에서 반드시 구분할 내용

- **권한 검사와 lazy 로딩:** lazy 자체는 권한을 검사하지 않는다. 권한 검사가 통과한 뒤에만 해당 화면의 import 함수가 호출되도록 설계한다. 단순히 import를 lazy로 교체하거나 메뉴에서 링크를 숨기는 것으로 접근 제한이 완성되지 않는다. React `lazy`는 최초 렌더 시점까지 컴포넌트 로딩을 미룬다. 참고: https://react.dev/reference/react/lazy .
- **로컬 route 정의:** 서버 식별자를 미리 정의한 route 매핑과 대조한다. 응답 문자열을 동적 import 경로로 직접 사용하지 않는다. 현재 실제 경로는 `routes.tsx`에 있으며 서버 식별자는 아직 확정되지 않았다.
- **표시 메뉴와 상세 접근 권한:** 왼쪽 메뉴에 표시되지 않는 상세 화면도 있다. 예를 들어 실제 제안 상세 경로는 `/cp/proposals/:proposalId`다. `proposal-detail`을 직접 메뉴 링크로 쓸지, 목록에서 이동하는 상세 권한으로 쓸지와 `proposalId` 출처는 계약이 필요하다.
- **첫 화면:** 현재 고정된 `/cp/dashboard`는 VO 전용 관리자 요구를 충족하지 않는다. 메뉴 응답이 준비된 뒤 허용된 첫 화면을 어떻게 선택할지 확정해야 한다. 첫 메뉴나 CP를 임의 기본값으로 선택하지 않는다.
- **새로고침·직접 URL:** localStorage에는 토큰만 있으므로 로그인 버튼을 누른 흐름 외에도 메뉴 초기화가 필요하다. 초기화 중·실패·완료 상태를 구분하고 완료 전에 이전 계정의 메뉴나 보호 화면을 표시하지 않도록 설계한다.
- **오래된 응답:** 메뉴 요청 중 로그아웃하거나 다른 계정으로 로그인하면 이전 응답을 폐기해야 한다. 기존 auth revision과 취소 경계를 활용한다.
- **메뉴 실패와 로그인 실패:** 메뉴 요청은 토큰 저장 후 발생한다. 메뉴 실패를 잘못된 비밀번호로 안내하거나 무조건 기존 대시보드로 이동하지 않도록 두 실패를 구분한다. 토큰 유지·로그아웃·재시도 정책은 후속 계약으로 확정한다.
- **서버 권한:** 화면 로딩과 메뉴 제어는 클라이언트 동작이다. API 접근 권한은 서버에서 토큰의 실제 권한으로 검증해야 하며, `role` query 값만으로 권한을 부여해서는 안 된다.

## 후속 구현 전에 확정할 계약

이번 로그인 구현을 막는 항목이 아니라, 다음 메뉴·권한 작업에서 확인할 항목이다.

- 로그인 권한 필드의 정확한 이름·타입·위치, 단일/복수 권한, 허용 값, 누락·알 수 없는 값의 처리.
- 메뉴 API method·실제 URL·권한 전달 방법 및 서버가 토큰에서 권한을 판단하는 방식.
- 메뉴 응답 envelope와 식별자·계층·순서·표시명·아이콘·이동 대상 필드, 필수 여부.
- 고정된 서버 메뉴 식별자와 로컬 route의 대응 목록. 사용자 예시 `proposal-detail`을 실제 값으로 사용할지는 미정.
- 상세 경로의 ID 등 parameter 출처, 표시하지 않는 상세 route의 권한 포함 규칙.
- CP·VO 복수 권한 시 메뉴 구성과 초기 화면, 빈 목록·중복·알 수 없는 식별자·권한 없는 메뉴 응답의 처리.
- 메뉴 초기화 실패·재시도·토큰 유지 정책, 접근 거부 표시 방식, `/meeting` 등 CP·VO 밖 경로의 적용 범위.
- 실제 인계 worktree의 경로·branch·기준 commit·직접 부모와 로그인 변경 전달 방법.

## 역할별 작업 및 순서

### Logic: 메뉴 API·상태·라우팅

1. 후속 공간에서 이 로그인 변경과 현재 API·라우터·메뉴 코드를 다시 확인한다.
2. 위 미정 계약을 확정하고 기존 API client·응답 파서·상태 구조의 재사용 또는 확장 방식을 결정한다.
3. 메뉴 전송·파싱·초기화 상태를 구현한다. 응답을 표시용 메뉴 모델과 허용 route에 연결하는 책임을 UI 밖에 둔다.
4. `useAuth`의 TODO 위치 및 startup 복원 경로에 메뉴 초기화를 연결한다.
5. `routes.tsx`의 정적 import를 허용 검사 후 로딩할 수 있도록 재구성한다. 현재 loader·lazy 실행 순서는 선택한 React Router 버전에서 확인한다.
6. `cp-admin-shell.tsx`·`vo-admin-shell.tsx`에 준비된 메뉴 items를 전달하고 초기 이동을 확정된 정책으로 교체한다.
7. 실패·취소·로그아웃·계정 전환을 검증하고 UI 표시 계약이 바뀌면 UI 세션에 인계한다.

### UI: 필요한 경우 메뉴 상태 표시 연결

- Logic의 메뉴 items·로딩·오류·재시도·접근 거부 계약이 확정된 다음 진행한다.
- 기존 `Navigation`과 공용 UI를 우선 사용한다. API 호출·token 처리·권한 판정은 UI에 넣지 않는다.
- 레이아웃 변경이 필요하면 해당 UI 역할 세션에서 범위를 확인한다. 이번 로그인 세션이 이 UI 변경까지 승인한 것으로 해석하지 않는다.

### 공유 파일·Git 순서

- 겹칠 가능성이 큰 경로: `use-auth.ts`, `auth-session.ts`, `routes.tsx`, CP·VO shell, 메뉴 props·model.
- 별도 worktree의 branch 관계와 통합 대상은 실제 공간 생성 시 정한다. 완료 통합은 승인된 자식에서 직접 부모 순서로 수행한다.
- 후속 작업 공간에 로그인 커밋 `a25745c`가 포함돼 있는지 확인한다. 이 세션의 ignored handoff 문서는 현재 경로에서 별도로 참조해야 한다.
- source 수정과 Git 실행을 조율하고 각 세션은 자기 로그만 수정한다. commit·branch 생성·merge는 각각 필요한 명령과 변경 범위를 별도 승인받는다.

## 검증 결과와 다음 완료 기준

현재 실행 결과:

- 수정 전 `TSX_TSCONFIG_PATH=tsconfig.app.json node --test tests/auth-api-contract.test.mjs`: 새 명세의 정상 응답이 refreshToken·profile·roles 누락으로 거부되는 실패 1건 재현.
- 공통 `formatting.py apply`: 수정한 소스·테스트의 실제 Prettier 포맷 완료.
- `TSX_TSCONFIG_PATH=tsconfig.app.json node --test --test-concurrency=1 tests/auth-api-contract.test.mjs tests/auth-session.test.mjs tests/auth-login-flow.test.mjs`: **16/16 통과**.
- `npm run lint`: 통과.
- `npm run build`: TypeScript 및 Vite build 통과. 큰 번들 및 `vite-tsconfig-paths` 안내 경고가 있다.
- `git diff --check`: 통과.
- 실서버 자격 증명 로그인·브라우저 자동화·메뉴 API 호출·후속 권한 검증은 수행하지 않았다. 독립 리뷰 에이전트는 호출하지 않았다.

후속 작업의 완료 기준:

- 로그인 token 저장보다 먼저 메뉴 요청이 실행되지 않고, 로그인 실패·취소 시 메뉴 요청이 없다.
- 확정된 메뉴 응답과 동일한 메뉴·허용 route를 구성한다.
- VO 관리자에게 CP 직접 URL을 요청했을 때 CP 화면의 import 함수와 화면 데이터 요청이 호출되지 않으며 확정된 접근 거부 상태를 표시한다. 반대 방향도 확인한다.
- 새로고침·직접 URL·로그아웃·다른 권한으로 재로그인했을 때 메뉴와 허용 경로가 현재 세션과 일치한다.
- 메뉴 실패·빈 목록·알 수 없는 식별자·동적 parameter를 계약대로 처리한다.
- 기존 인증 테스트, 새 메뉴·라우팅 테스트, 공통 포맷, lint·build를 실행한다. 테스트 프레임워크나 브라우저 캡처는 임의로 추가하지 않는다.

## 적용 정책

중앙 snapshot의 `task-role-routing`, `git-branch-strategy`, `coding-convention`, `data-fetch-layer`, `type-definition`, `validation`, `implementation-quality`, `documentation`, `abstraction-strategy`, `hook-use-auth`, `hook-use-api`를 참조했다. 후속 세션은 자신에게 바인딩된 정책과 실제 저장소 상태를 다시 확인한다. 다른 프로젝트를 조회할 필요는 없으며 사용자가 user-ui 비교를 제외했다.
