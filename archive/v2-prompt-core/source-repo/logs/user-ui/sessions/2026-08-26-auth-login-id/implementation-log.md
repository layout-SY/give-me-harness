# 구현 로그

## 승인된 범위

로그인 입력을 `loginId` 문자열로 바꾸고, 인증 없이 `POST /auth/login`으로 토큰을 받은 뒤 `expiresIn` 전에 `POST /auth/refresh`로 갱신한다.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `src/features/auth/api/auth.dto.ts` | `{ loginId, password }`, SUCCESS envelope, `tokenType`/`expiresIn` | 이메일·프로필 필드 제거 |
| `src/features/auth/api/auth.api.ts` | `/auth/login`, `/auth/refresh`, 인터셉터 없음 | 인증 없이 호출, 저장된 토큰도 안 붙음 |
| `src/features/auth/api/client.ts` | `postAuthLogin`, `postAuthRefresh` | 런타임 클라이언트가 새 계약 사용 |
| `src/features/auth/model/authSession.ts` | 토큰·만료 시각 저장, 30초 전 refresh | 부팅과 로그인 성공 후 스케줄 |
| `src/features/auth/hook/useSignInMutation.ts` | 세션 persist 후 기존 딥링크 | access/refresh 모두 저장 |
| `src/features/auth/ui/LoginPage.tsx` | 아이디 필드, `loginId` props | 이메일이 아닌 일반 문자열 |
| `src/features/auth/testing/LoginTestPage.tsx` | `loginId` 제출, 공통 실패 문구 | 아이디/비밀번호를 구분하지 않음 |
| `src/shared/config/constants.ts` | refresh·expires-at 키 | 세션 저장 키 고정 |
| `src/main.tsx` | 부팅 시 `scheduleAuthSessionRefresh` | 새로고침 후에도 만료 전 갱신 |
| 테스트 | API·세션·mutation·폼 | loginId 계약과 무인증·refresh 고정 |

## 결정 사항

- 인증 Axios에는 Bearer 인터셉터를 두지 않는다. 로그인·리프레시는 스펙상 인증 없이 호출한다. 시민참여 등 공유 Axios는 기존처럼 액세스 토큰을 붙인다.
- 만료는 JWT `exp`가 아니라 응답 `expiresIn`으로 계산한다.
- 리프레시 본문은 `{ refreshToken }`이다. 사용자가 스키마를 주지 않아 이 형태로 전송한다.
- 아이디 없음과 비밀번호 틀림을 클라이언트가 나누지 않는다. 실패 문구는 둘 다 아이디와 비밀번호 확인이다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| `npx vitest run src/features/auth` | 4 files / 7 tests passed |
| `npm run build` | `tsc -b && vite build` 성공 |
| `npm run lint` | exit 0 |

전체 `npx vitest run`에서 `meeting.api.test.ts` insecure 2건과 `handlers.test.ts` Invalid URL 20건은 이번 auth 파일과 무관한 기존 실패다. `handlers.test.ts`는 이 파일만 단독 실행해도 같은 Invalid URL이 난다.

## Watcher 인계

현재 변경은 로그인 계약과 토큰 갱신이다. 이미지 캡처 시각 QA는 수행하지 않았고, 검증은 테스트·build·lint다.
