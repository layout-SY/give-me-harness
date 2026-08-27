# 구현 로그

## 승인된 범위

`POST /auth/refresh`를 무인증 `{ refreshToken }`으로 호출하고, 1회용 토큰을 응답 값으로 교체한다. 재전송하지 않으며 실패 시 재로그인할 수 있게 세션을 지운다.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `src/features/auth/model/authSession.ts` | 전송 전 refresh 저장값 제거, in-flight 단일 호출, 실패 시 `clearAuthSession` | 같은 토큰을 두 번 보내지 않음. 실패하면 재로그인 |
| `src/features/auth/model/authSession.test.ts` | 단일 전송·실패 시 세션 삭제 테스트 | 1회용·재로그인 계약 고정 |
| DTO/API | 변경 없음 | 요청·응답이 제공된 스펙과 이미 같음 |

## 결정 사항

- 요청을 보내기 전에 `refresh-token`을 storage에서 뺀다. 겹치는 스케줄이 같은 값을 읽지 못한다.
- 응답이 오기 전에 재시도하지 않는다. 서버가 이미 소비했을 수 있기 때문이다.
- 실패하면 access/refresh/만료를 모두 지운다. 스펙상 재사용은 계정 토큰 전부 폐기이므로 클라이언트가 옛 토큰을 붙잡고 있지 않는다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| `npx vitest run src/features/auth` | 4 files / 9 tests passed |
| `npx eslint src/features/auth/model/authSession.ts src/features/auth/model/authSession.test.ts` | exit 0 |

## Watcher 인계

현재 변경은 세션 회전이다. UI 시각 QA는 수행하지 않았고, 검증은 테스트와 eslint다.
