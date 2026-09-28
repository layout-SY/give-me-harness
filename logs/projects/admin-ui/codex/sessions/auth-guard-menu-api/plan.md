# 로그인 가드와 메뉴 API 연결 계획

## 범위와 결정

기존 API 연결 패턴으로 `GET /menus`, `GET /me/menus`의 DTO·파서·요청 함수를 연결하고 인증 가드를 구현한다. 사용자가 메뉴 조회의 로그인 연결, 동적 메뉴와 권한별 라우팅은 계약 보강 후 진행하기로 확정했다.

- 역할: `logic`. 기존 PrivateRoute·인증 세션·JWT util·ApiClient·공통 응답 mapper·오류 큐를 재사용한다.
- 구현 작업 위치: `/private/tmp/asan-metaverse-admin-ui-auth-guard-menu-api`. 사용자 요청으로 구현·병합 후 워크트리 정리를 완료했다.
- 구현 branch: `feature/auth-guard-menu-api`, 직접 부모: `sy-main`. 로컬 branch 삭제를 완료했으며 기록은 기본 checkout의 같은 세션 경로에 보존한다.
- 시작 HEAD: `ed9d65bd6c74eabf3f8e5070c203135d2067264e`, 시작 미커밋 변경 없음.
- Git 생성 작업 `19eb26604d7f4cc6acbb16d441150442`와 stage·commit 작업 `359aa751dac4e5b0d40eeafab03f0395`는 사용자 승인 후 `done`이다. 후속 승인으로 부모 동기화와 `c739a91`의 `sy-main` 병합을 완료했다. 최종 정리 시점의 `sy-main`은 후속 commit을 포함한 `ea64f72`이며 clean이다. 원격 push는 실행하지 않았다.
- DAO 기존 코드를 유지한다. `customConfig` 객체와 기존 전달 구조는 유지하고 기본 인증 전환으로 불필요해진 `authRequired: true`만 제거한다.
- Axios의 저장된 access token 기본 부착, 명시한 Authorization 보존, 로그인·비밀번호 변경·메일 요청 제외, refresh token 및 meeting fetch의 기존 토큰 유지.

## 확인한 근거

- 기본 checkout의 `.claude/logs/sessions/로그인-리다이렉트-가드-인계/handoff.md`와 `.codex/logs/sessions/admin-login-menu-handoff/{handoff,plan,final-summary}.md`를 읽었다. 다른 세션 문서는 수정하지 않는다.
- `src/features/auth/model/auth-session.ts`, `use-auth.ts`: 토큰·revision·로그아웃·bootstrap과 로그인 취소 경계를 유지한다.
- `src/app/router/private-route.tsx`, `routes.tsx`: 기존 가드는 미연결이며 `/login`을 제외한 경로를 보호 layout 하위에 연결한다.
- `src/shared/api/common/response.dto.ts`, `api-client.ts`, `common/api-result/`: 공통 envelope 정규화를 재사용한다. 메뉴 DTO에는 내부 payload만 정의한다.
- `src/entities/items/api/`, `tests/auth-*.test.mjs`: API factory·parser 배치와 Node/Vite SSR 테스트 방식을 참조한다.
- `src/shared/api/error/server-error-queue.ts`: 진행 중인 재인증 팝업의 중복 차단이 이미 구현돼 있다.

## 수행과 검증

1. 이 worktree의 `entities/menus`에 명세 그대로 두 응답 형태와 요청을 연결한다. 문자열 children을 임의로 재귀 메뉴로 해석하지 않는다.
2. 인증 세션과 라우터에서 앱/보호 화면 진입 때 access token 만료를 검사하고, 확인 가능한 exp가 지난 경우만 세션을 정리한다. 타이머와 자동 refresh는 추가하지 않는다.
3. 로그인 화면 외 경로 보호, 안전한 내부 `state.from` 복원, 인증 상태의 로그인 화면 접근 차단을 연결한다. from이 없으면 기존 `/cp/dashboard`를 유지한다.
4. 401 팝업 확인 후 세션 정리와 원래 경로 복원이 연결되는지 검증한다. 팝업 문구는 유지한다. 기존 오류 처리 경계를 거치지 않는 API 호출은 조사 결과만 보고한다.
5. 요청 설정·토큰 헤더·메뉴 계약·만료·가드·복원 동작을 기존 Node 테스트 방식으로 검증한다. 바뀐 공통 인증 설정을 전제로 하던 테스트는 새 계약에 맞게 갱신하고 실제 Axios 헤더 검증으로 보완한다.
6. 공통 `formatting.py apply` 실행 후 `npm run lint`, `TSX_TSCONFIG_PATH=tsconfig.app.json node --test --test-concurrency=1 tests/*.test.mjs`, `npm run build`, `git diff --check` 결과를 기록한다.

## 제외와 한계

실서버 호출·브라우저 캡처·DAO 파일 수정·동적 메뉴·권한별 lazy 라우팅은 범위에 포함하지 않는다. 메뉴 필드 의미·route 매핑·실패 정책은 추가 계약이 필요하다. API 제공 예시와 공통 성공 envelope 규칙 이상의 계약을 임의로 만들지 않는다.

## 현재 실행 상태

브랜치와 워크트리 생성 후 사용자의 `진행`으로 소스 구현 승인이 기록됐다. 위 범위의 구현과 검증을 완료했다. `npm ci --offline --no-audit --no-fund`로 이 worktree에 의존성을 설치했으며 패키지 파일은 변경하지 않았다. 초기 구현에서 공통 포맷, 전체 Node 테스트 344/344, lint, TypeScript·Vite build와 `git diff --check`를 통과했다. 실제 변경·검증 한계와 후속 계약은 `final-summary.md`를 따른다.

사용자의 커밋 요청과 `명령 실행 승인`에 따라 소스·테스트 28개 파일을 `fe66897eee4e76fd787c1dfe53198040bfc61c49` (`feat(auth): 로그인 가드와 메뉴 API 연결`)로 커밋했다. 보호 실행기는 exit 0·`stage: done`을 반환했고 초기 커밋 시점의 작업 worktree는 clean이었다.

후속 병합 요청에 따라 최신 직접 부모 `sy-main`의 `c392709`을 이 worktree로 동기화했다. 승인된 merge 명령의 테스트 충돌 2개는 별도 `진행` 승인 후 해결했고, 승인된 stage 해제 후 필수 포맷을 완료했다. 통합 상태에서 lint·build·전체 Node 테스트 49파일 355/355·diff 공백 검증을 통과했다. 이후 승인된 stage·commit 작업으로 동기화 merge commit `c739a91`을 생성했고 기능 worktree는 clean이다.

2026-09-22에 사용자 승인 보호 작업 `6f3b0cb0ebd54d14933e1d701b87799b`로 기본 checkout의 `sy-main`을 `c392709`에서 `c739a91`로 ff-only 병합했다. 병합 후 lint·build가 통과했으며 source branch·worktree는 유지했다. 이전 이벤트 worktree 조회 문제는 외부에서 디렉터리와 등록을 제거한 뒤 해소된 것을 확인했다.

기본 checkout의 완료된 아이템·이벤트 변경 21개와 기존 PR 문서는 사용자 승인으로 두 stash에 임시 보관했다. 병합 후 보호 작업 `b6b500cb3f6711d598112e1e35605cfb`로 모두 복원하고 성공한 stash를 정리했다. 20파일의 diff와 PR 문서의 SHA-256은 원본과 일치하며, 겹친 `tests/items-contract.test.mjs`는 원래 enum 변경에 로그인 작업의 인증 기대값 한 줄만 함께 반영됐다. 원래 변경 21개는 unstaged, PR 문서는 untracked 상태로 남아 있다. 이 최종 조합에서 전체 Node 테스트 49파일 356/356, lint, TypeScript·Vite build와 diff 공백 검증을 통과했다. 원격 push와 기능 branch·worktree 삭제는 실행하지 않았다.

2026-09-22 후속 정리 완료: 위 복원 이후 별도 작업의 `e806132`, `ea64f72`가 추가됐고 기본 checkout은 clean이다. 이벤트 API 정리 `b8414c747e6d440eb84926b68f303482`와 로그인 정리 `174c6c5b8c3b4d91bba78865efce8182`가 모두 `cleaned`로 끝났다. 로그인 정리에서 현재 `sy-main`의 lint·build를 통과했고 HEAD `ea64f72`를 유지했다. 두 기능의 로컬 branch, worktree 등록 및 디렉터리 부재를 실제로 확인했다. 자기 기록은 `/Users/okand/SynologyDrive/asan-metaverse-admin-ui/.codex/logs/sessions/auth-guard-menu-api/`에 보존했다. 문의 타입·아이템 UI·이벤트 보상 UI의 다른 작업 공간과 원격은 변경하지 않았다.
