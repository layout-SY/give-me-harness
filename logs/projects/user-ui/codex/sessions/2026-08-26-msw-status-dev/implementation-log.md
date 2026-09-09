# 구현 로그

## 승인된 범위

브라우저 MSW는 `VITE_API_BASE_URL_STATUS`가 `dev`일 때만 시작한다.

## 변경 사항

| 경로 | 변경 사항 | 결과 |
| --- | --- | --- |
| `src/app/mocks/startMocks.ts` | status를 trim한 뒤 `dev`일 때만 worker 시작 | DEV 기본 켜짐과 `VITE_ENABLE_MSW` 제거 |
| `src/app/mocks/startMocks.test.ts` | `dev` / 공백 / 빈 값 / `prod` 케이스 | 새 계약을 고정 |
| `src/features/meeting/config/vite-env.d.ts` | `VITE_API_BASE_URL_STATUS` 추가, `VITE_ENABLE_MSW` 삭제 | env 타입이 실제 스위치와 같음 |
| `.env` | `VITE_API_BASE_URL_STATUS=dev` | 로컬에서 모의를 켤 수 있음 (gitignore) |

## 결정 사항

- `dev`만 허용한다. 대소문자를 바꾸지 않는다.
- `.env`의 `VITE_API_BASE_URL= https://...`처럼 공백이 있을 수 있어 status는 trim한다.
- 테스트용 node MSW는 그대로 둔다.

## 검증 근거

| 명령어 | 결과 |
| --- | --- |
| `npx vitest run src/app/mocks/startMocks.test.ts` | 1 file / 4 tests passed |
| `npm run build` | `tsc -b && vite build` 성공 |
| `npm run lint` | exit 0 |

## Watcher 인계

현재 변경은 모의 서버 시작 조건이다. UI 시각 QA는 수행하지 않았고, 검증은 테스트·build·lint다.
