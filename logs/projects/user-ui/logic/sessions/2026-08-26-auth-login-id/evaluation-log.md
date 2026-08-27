# 평가 로그

## 현재 판정과의 경계

여기서는 Watcher 판정을 다시 평가하지 않는다.

## 장기 관찰 사항

- `POST /auth/refresh` 공식 본문·오류 코드가 오면 `{ refreshToken }` 가정을 서버 계약으로 교체해야 한다.
- 리프레시가 실패해도 세션을 지우지 않는다. 만료 후 보호 API는 401이 날 수 있다.
- 로그인 성공 시 `oasisapp://login`으로 이동한다. 웹 전용 흐름이면 이 딥링크를 재검토할 수 있다.
- `LoginPage.tsx`는 Claude Code 소유 경로인데, 아이디 필드 반영을 위해 이번 작업에서 수정했다.

## 목록에 등록할 재사용 가능 자산

`persistAuthSession` / `scheduleAuthSessionRefresh`는 로그인 성공과 앱 부팅이 같이 쓰는 인증 세션 헬퍼다.

## 기술 부채

- 회의 `meeting.api.test.ts` insecure 케이스 2건은 구현에서 해당 검증이 주석이라 기존 실패로 남는다.
- `handlers.test.ts`의 Invalid URL 20건은 이번 로그인 변경과 무관하며 단독 실행에서도 재현된다.

## 프로세스 개선 사항

인증 예외(로그인·리프레시)와 기본 Bearer 부착을 같은 인스턴스에 두면 스펙이 바뀔 때마다 충돌한다. 무인증 엔드포인트는 인터셉터 없는 클라이언트를 유지하는 편이 낫다.

## 권고 사항

refresh 요청/응답 OpenAPI가 확정되면 DTO만 맞추면 된다. 리프레시 실패 시 로그아웃할지 별도로 받으면 된다.
