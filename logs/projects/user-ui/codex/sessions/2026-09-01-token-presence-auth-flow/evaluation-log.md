# 평가 로그

## 현재 판정과의 경계

여기서는 Watcher 판정을 다시 평가하지 않는다. 현재 구현의 완료 판정은 `review-log.md`의 PASS를 따른다.

## 장기 관찰 사항

- 기존 authSession revision store를 재사용해 인증 상태 정본을 늘리지 않았다.
- profile query와 credential presence가 분리되어 API timing이 댓글 권한처럼 보이는 문제를 제거했다.
- client expiry metadata는 refresh 예약에만 남고 보호 route 차단은 backend 401이 담당한다.
- `returnTo` 보안 검증을 새로 구현하지 않고 기존 sanitizer를 공유했다.

## 목록에 등록할 재사용 가능 자산

- `src/features/auth/hook/useAuthTokenPresence.ts`: auth credential presence가 필요한 다른 기능에서 재사용 가능하다.
- `bootstrapAuthTokensFromLocation()`: native/web callback query를 session으로 이관하는 auth bootstrap 경계다.

## 기술 부채

- `authSession.test.ts` pure LOC 235로 warning band다. 다음 기능 추가 전 presence/bootstrap과 refresh lifecycle 분리를 검토한다.
- `AuthRouteBoundary.reauthentication.test.tsx`와 `ApiErrorDialogBridge.test.tsx`의 일부 integration fixture가 중첩된다.
- 다른 탭 localStorage 변경은 현재 external revision listener에 자동 반영되지 않는다.

## 프로세스 개선 사항

- URL credential을 다루는 startup 변경은 비동기 mock·analytics보다 먼저 실행되는지 Watcher 질문에 포함한다.
- UI_COMPLETE 후 handoff의 상태·대기 작업·검증 표를 즉시 갱신해 코드와 문서 불일치를 막는다.
- no-excuse checker는 프로젝트 환경에 Bun이 없으므로 향후 정책 toolchain과 저장소 runtime의 실행 경로를 정렬할 필요가 있다.

## 권고 사항

- 다중 탭 인증 동기화 요구가 생길 때만 `storage` event 구독을 추가한다.
- 테스트 파일이 250 pure LOC에 근접하면 기능 추가 전에 책임별로 분리한다.
- 현재 범위에서는 Zustand 도입, 401 자동 refresh retry, bundle 분할을 추가하지 않는다.
