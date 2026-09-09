# 계획

## 결론

`asan-metaverse-user-ui`의 전역 API 오류 처리와 token-presence 인증 기반을 현재 관리자 UI의 `ApiResult`, Zustand, Dialog, FSD 구조에 맞게 이식한다. typed failure 흐름, terminal reporting, 중앙 인증 세션 경계와 URL token bootstrap까지 구현하고 production 로그인 UI와 보호 route 활성화는 후속 작업으로 남긴다.

## 범위

- `src/shared/api/error/**`의 failure taxonomy, diagnostics, reporter, server error queue
- Axios, `useApi`, TanStack Query terminal error 연결
- 기존 Dialog를 재사용하는 app-level error bridge
- typed auth API parser와 `AbortSignal` 전달
- localStorage token 저장·삭제·URL bootstrap을 소유하는 auth session
- Zustand auth store의 token presence·revision 동기화
- startup 연결, Node 회귀 테스트 6파일, 현재 세션 문서 8종

## 제외 사항

- production `/sign-in` 마크업·CSS와 Header UI
- 보호 route와 `returnTo` 활성화
- 외부 SSO/native callback 및 user-ui 전용 도메인 코드
- package·lockfile 변경과 새 테스트 프레임워크
- 브라우저 자동화, screenshot, capture, 시각 QA

## 제약 조건

- 원본 `task/fix-loading-spinner-layout` worktree의 dirty UI 파일을 수정하지 않는다.
- `ApiResult`, `CustomException`, `useApi`의 기존 반환 계약과 silent-default를 보존한다.
- shared 계층은 auth store·route·Dialog를 직접 참조하지 않고 `reauthenticate` 이벤트까지만 생성한다.
- raw payload, token, authorization header, query variable을 diagnostics나 Dialog에 전달하지 않는다.
- Zustand 외 별도 인증 상태 store를 만들지 않는다.

## 실행 계획

1. `sy-main@ad687ac00c897163046d27b2f48bf9f2ae55d5b3`에서 격리 worktree와 작업 브랜치를 사용한다.
2. failure 정규화, queue, diagnostics·reporter를 구현한다.
3. Axios, `useApi`, TanStack Query와 기존 Dialog를 terminal 경계에 연결한다.
4. auth transport와 auth-session의 token presence·revision 흐름을 구현한다.
5. failing-first 테스트, build, targeted lint, 전체 suite로 검증한다.
6. Watcher·Evaluator·필수 문서를 완료한 뒤 사용자 병합 승인에 따라 atomic commit과 `--ff-only` 병합을 수행한다.

## 승인

- 구현 승인: 사용자의 `계획대로 진행`
- scope 추가 승인: `src/shared/lib/exceptions/custom.exception.ts`
- 브랜치 승인 식별자: `branch:task/admin-api-auth-foundation|parent:sy-main@ad687ac00c897163046d27b2f48bf9f2ae55d5b3|merge:sy-main`
- 병합 승인: 사용자의 `병합`
- 원격 작업: push 및 원격 브랜치 삭제 없음
