# 구현 로그

## 승인된 범위

액세스 토큰이 있으면 모든 API 요청에 `Authorization: Bearer`를 붙인다.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `src/shared/api/attach-access-token.ts` | `localStorage` 토큰을 Bearer로 붙이는 함수 | Axios 인스턴스가 같은 규칙을 재사용 |
| `src/shared/api/axios-instance.ts` | `authRequired` 가드 제거, 항상 attach | 시민참여 GET 포함 모든 공유 Axios 요청에 헤더 |
| `src/features/auth/api/auth.api.ts` | 같은 인터셉터 등록 | 로그인 인스턴스도 저장된 토큰을 보냄 |
| `src/features/meeting/api/http/meeting.api.ts` | 인자 토큰이 비면 storage 토큰 사용 | 회의 fetch도 저장된 토큰을 보냄 |
| 테스트 | attach 단위 테스트, 로그인 헤더 테스트 | 토큰 있음/없음 고정 |

## 결정 사항

- 요청마다 `customConfig`를 추가하지 않고 인터셉터에서 처리한다. 목록 GET이 빠져 있던 원인이 옵트인이기 때문이다.
- 토큰이 없으면 헤더를 넣지 않는다. 빈 `Bearer`를 보내지 않는다.
- 기존 API 파일의 `customConfig`는 제거하지 않았다. 인터셉터가 이미 헤더를 붙인다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| `npx vitest run src/shared/api/attach-access-token.test.ts src/features/auth/api/auth.api.test.ts` | 2 files / 4 tests passed |
| `npm run build` | `tsc -b && vite build` 성공 |
| `npm run lint` | exit 0 |

회의 `meeting.api.test.ts`의 insecure URL 2건 실패는 이번 파일에서 검증 코드가 주석 처리된 기존 상태이며 이번 헤더 변경으로 새로 생긴 실패가 아니다.

## Watcher 인계

현재 변경은 인증 헤더 부착이다. UI 시각 QA는 수행하지 않았고, 검증은 테스트·build·lint다.
